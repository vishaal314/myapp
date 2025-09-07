"""
Unit Test Cases for Cloud Database Scanner Connectors
Tests Azure, AWS, and Google Cloud database connectivity functionality, performance, and security.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import time
import threading
from datetime import datetime
import re
import sys
import os

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.db_scanner import DBScanner


class TestCloudDatabaseConnectors(unittest.TestCase):
    """Test suite for cloud database connectors."""
    
    def setUp(self):
        """Set up test environment."""
        self.scanner = DBScanner(region="Netherlands")
        
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self.scanner, 'connection') and self.scanner.connection:
            try:
                self.scanner.connection.close()
            except:
                pass


class TestAzureDatabaseConnectors(TestCloudDatabaseConnectors):
    """Test Azure Database connectivity and functionality."""
    
    def test_azure_mysql_flexible_connection_string_parsing(self):
        """Test Azure MySQL Flexible Server connection string parsing."""
        connection_string = (
            "Server=testserver.mysql.database.azure.com;"
            "Port=3306;"
            "Database=testdb;"
            "Uid=testuser;"
            "Pwd=testpass123!;"
            "SslMode=Required;"
        )
        
        parsed = self.scanner._parse_azure_connection_string(connection_string)
        
        self.assertEqual(parsed['server'], 'testserver.mysql.database.azure.com')
        self.assertEqual(parsed['port'], 3306)
        self.assertEqual(parsed['database'], 'testdb')
        self.assertEqual(parsed['username'], 'testuser')
        self.assertEqual(parsed['password'], 'testpass123!')
        self.assertEqual(parsed['ssl_mode'], 'Required')
        
    def test_azure_mysql_legacy_connection_string_parsing(self):
        """Test Azure MySQL Single Server (Legacy) connection string parsing."""
        connection_string = (
            "Server=legacyserver.mysql.database.azure.com;"
            "Port=3306;"
            "Database=legacydb;"
            "Uid=testuser@legacyserver;"
            "Pwd=legacypass123!;"
            "SslMode=Required;"
        )
        
        parsed = self.scanner._parse_azure_connection_string(connection_string)
        
        self.assertEqual(parsed['server'], 'legacyserver.mysql.database.azure.com')
        self.assertEqual(parsed['username'], 'testuser@legacyserver')
        self.assertTrue(parsed['ssl_mode'] in ['Required', 'require'])
        
    def test_azure_postgresql_connection_string_parsing(self):
        """Test Azure PostgreSQL connection string parsing."""
        connection_string = (
            "postgresql://testuser:testpass@pgserver.postgres.database.azure.com:5432/testdb?sslmode=require"
        )
        
        parsed = self.scanner._parse_connection_string(connection_string)
        
        self.assertEqual(parsed['host'], 'pgserver.postgres.database.azure.com')
        self.assertEqual(parsed['port'], 5432)
        self.assertEqual(parsed['database'], 'testdb')
        self.assertEqual(parsed['username'], 'testuser')
        self.assertTrue('ssl' in parsed or 'sslmode' in parsed)
        
    def test_azure_sql_database_connection_string_parsing(self):
        """Test Azure SQL Database connection string parsing."""
        connection_string = (
            "Server=tcp:sqlserver.database.windows.net,1433;"
            "Initial Catalog=sqldb;"
            "Persist Security Info=False;"
            "User ID=sqladmin;"
            "Password=SqlPass123!;"
            "MultipleActiveResultSets=False;"
            "Encrypt=True;"
            "TrustServerCertificate=False;"
        )
        
        parsed = self.scanner._parse_azure_connection_string(connection_string)
        
        self.assertIn('sqlserver.database.windows.net', parsed['server'])
        self.assertEqual(parsed['database'], 'sqldb')
        self.assertEqual(parsed['username'], 'sqladmin')
        self.assertEqual(parsed['ssl_mode'], 'True')  # Encrypt=True
        
    @patch('services.db_scanner.mysql.connector.connect')
    def test_azure_mysql_ssl_enforcement(self, mock_connect):
        """Test SSL enforcement for Azure MySQL connections."""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        connection_string = (
            "Server=secure.mysql.database.azure.com;"
            "Port=3306;"
            "Database=securedb;"
            "Uid=secureuser;"
            "Pwd=SecurePass123!;"
            "SslMode=Required;"
        )
        
        result = self.scanner.connect_from_string(connection_string)
        
        # Verify SSL was enforced in connection call
        mock_connect.assert_called_once()
        call_args = mock_connect.call_args[1]
        self.assertTrue(call_args.get('ssl_disabled', True) == False)
        self.assertTrue('ssl_mode' in str(call_args) or 'ssl' in str(call_args))
        
    def test_azure_cloud_detection(self):
        """Test automatic Azure cloud provider detection."""
        azure_hostnames = [
            'test.mysql.database.azure.com',
            'test.postgres.database.azure.com',
            'test.database.windows.net'
        ]
        
        for hostname in azure_hostnames:
            is_azure = self.scanner._is_azure_cloud_database(hostname)
            self.assertTrue(is_azure, f"Failed to detect Azure for {hostname}")
            
    def test_azure_connection_performance(self):
        """Test Azure connection establishment performance."""
        connection_string = (
            "Server=perf-test.mysql.database.azure.com;"
            "Port=3306;"
            "Database=perfdb;"
            "Uid=perfuser;"
            "Pwd=PerfPass123!;"
            "SslMode=Required;"
        )
        
        with patch('services.db_scanner.mysql.connector.connect') as mock_connect:
            mock_connect.return_value = Mock()
            
            start_time = time.time()
            self.scanner.connect_from_string(connection_string)
            connection_time = time.time() - start_time
            
            # Connection should be fast (under 5 seconds for mocked connection)
            self.assertLess(connection_time, 5.0)
            
    def test_azure_connection_security_validation(self):
        """Test security validation for Azure connections."""
        # Test weak password rejection
        weak_connection_string = (
            "Server=test.mysql.database.azure.com;"
            "Port=3306;"
            "Database=testdb;"
            "Uid=testuser;"
            "Pwd=123;"  # Weak password
            "SslMode=Required;"
        )
        
        security_issues = self.scanner._validate_connection_security(weak_connection_string)
        self.assertTrue(len(security_issues) > 0)
        self.assertTrue(any('password' in issue.lower() for issue in security_issues))
        
    def test_azure_pii_detection_functionality(self):
        """Test PII detection in Azure database schemas."""
        mock_schema = {
            'tables': ['users', 'user_profiles', 'payment_info'],
            'table_details': {
                'users': {
                    'columns': ['user_id', 'email_address', 'phone_number', 'created_at']
                },
                'payment_info': {
                    'columns': ['payment_id', 'credit_card_number', 'cvv', 'billing_address']
                }
            }
        }
        
        findings = self.scanner._scan_schema_for_pii(mock_schema)
        
        # Should detect email, phone, credit card
        pii_types_found = [f['type'] for f in findings]
        self.assertIn('EMAIL', pii_types_found)
        self.assertIn('PHONE', pii_types_found) 
        self.assertIn('CREDIT_CARD', pii_types_found)
        
        # Should have high confidence for clear column names
        email_findings = [f for f in findings if f['type'] == 'EMAIL']
        self.assertTrue(any(f['confidence'] >= 0.8 for f in email_findings))


class TestAWSRDSConnectors(TestCloudDatabaseConnectors):
    """Test AWS RDS connectivity and functionality."""
    
    def test_aws_rds_mysql_connection_string_parsing(self):
        """Test AWS RDS MySQL connection string parsing."""
        connection_string = (
            "mysql://dbuser:dbpass123@myinstance.abc123.us-east-1.rds.amazonaws.com:3306/proddb?ssl-mode=REQUIRED"
        )
        
        parsed = self.scanner._parse_connection_string(connection_string)
        
        self.assertEqual(parsed['host'], 'myinstance.abc123.us-east-1.rds.amazonaws.com')
        self.assertEqual(parsed['port'], 3306)
        self.assertEqual(parsed['database'], 'proddb')
        self.assertEqual(parsed['username'], 'dbuser')
        self.assertIn('ssl', str(parsed).lower())
        
    def test_aws_aurora_cluster_connection_string_parsing(self):
        """Test AWS Aurora cluster connection string parsing."""
        connection_string = (
            "mysql://aurora_user:aurora_pass@mycluster.cluster-abc123.us-west-2.rds.amazonaws.com:3306/auroradb?ssl-mode=REQUIRED"
        )
        
        parsed = self.scanner._parse_connection_string(connection_string)
        
        self.assertIn('cluster', parsed['host'])
        self.assertIn('rds.amazonaws.com', parsed['host'])
        self.assertEqual(parsed['username'], 'aurora_user')
        
    def test_aws_rds_postgresql_connection_string_parsing(self):
        """Test AWS RDS PostgreSQL connection string parsing."""
        connection_string = (
            "postgresql://pguser:pgpass123@pginstance.xyz789.eu-west-1.rds.amazonaws.com:5432/pgdb?sslmode=require"
        )
        
        parsed = self.scanner._parse_connection_string(connection_string)
        
        self.assertEqual(parsed['host'], 'pginstance.xyz789.eu-west-1.rds.amazonaws.com')
        self.assertEqual(parsed['database'], 'pgdb')
        self.assertTrue('ssl' in str(parsed).lower())
        
    def test_aws_rds_sql_server_connection_string_parsing(self):
        """Test AWS RDS SQL Server connection string parsing."""
        connection_string = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=sqlinstance.def456.us-east-1.rds.amazonaws.com,1433;"
            "DATABASE=sqldb;"
            "UID=sqluser;"
            "PWD=SqlPass123!;"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
        )
        
        parsed = self.scanner._parse_odbc_connection_string(connection_string)
        
        self.assertIn('rds.amazonaws.com', parsed['server'])
        self.assertEqual(parsed['database'], 'sqldb')
        self.assertEqual(parsed['username'], 'sqluser')
        self.assertTrue(parsed.get('encrypt', '').lower() == 'yes')
        
    def test_aws_cloud_detection(self):
        """Test automatic AWS cloud provider detection."""
        aws_hostnames = [
            'instance.abc123.us-east-1.rds.amazonaws.com',
            'cluster.cluster-xyz789.us-west-2.rds.amazonaws.com',
            'aurora.cluster-def456.eu-west-1.rds.amazonaws.com'
        ]
        
        for hostname in aws_hostnames:
            is_aws = self.scanner._is_aws_cloud_database(hostname)
            self.assertTrue(is_aws, f"Failed to detect AWS RDS for {hostname}")
            
    @patch('services.db_scanner.mysql.connector.connect')
    def test_aws_rds_ssl_enforcement(self, mock_connect):
        """Test SSL enforcement for AWS RDS connections."""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        connection_string = (
            "mysql://secureuser:securepass@secure.abc123.us-east-1.rds.amazonaws.com:3306/securedb?ssl-mode=REQUIRED"
        )
        
        result = self.scanner.connect_from_string(connection_string)
        
        # Verify SSL was enforced
        mock_connect.assert_called_once()
        call_args = mock_connect.call_args[1]
        self.assertTrue('ssl' in str(call_args).lower())
        
    def test_aws_connection_performance_with_timeout(self):
        """Test AWS connection performance with proper timeouts."""
        connection_string = (
            "mysql://testuser:testpass@slow.abc123.us-east-1.rds.amazonaws.com:3306/testdb?ssl-mode=REQUIRED"
        )
        
        with patch('services.db_scanner.mysql.connector.connect') as mock_connect:
            # Simulate slow connection
            def slow_connect(*args, **kwargs):
                time.sleep(0.1)  # Simulate network delay
                return Mock()
            
            mock_connect.side_effect = slow_connect
            
            start_time = time.time()
            result = self.scanner.connect_from_string(connection_string)
            connection_time = time.time() - start_time
            
            # Should complete within reasonable time
            self.assertLess(connection_time, 10.0)
            
    def test_aws_region_specific_compliance(self):
        """Test AWS region-specific compliance features."""
        # Test different AWS regions for compliance
        regions = ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1']
        
        for region in regions:
            hostname = f"instance.abc123.{region}.rds.amazonaws.com"
            compliance_rules = self.scanner._get_region_compliance_rules(hostname)
            
            if 'eu-' in region:
                # EU regions should have GDPR compliance
                self.assertIn('GDPR', str(compliance_rules))
            
    def test_aws_aurora_cluster_failover_detection(self):
        """Test detection of Aurora cluster endpoints vs individual instances."""
        cluster_endpoint = "mycluster.cluster-abc123.us-west-2.rds.amazonaws.com"
        reader_endpoint = "mycluster.cluster-ro-abc123.us-west-2.rds.amazonaws.com"
        instance_endpoint = "myinstance.abc123.us-west-2.rds.amazonaws.com"
        
        self.assertTrue(self.scanner._is_aurora_cluster_endpoint(cluster_endpoint))
        self.assertTrue(self.scanner._is_aurora_reader_endpoint(reader_endpoint))
        self.assertFalse(self.scanner._is_aurora_cluster_endpoint(instance_endpoint))


class TestGoogleCloudSQLConnectors(TestCloudDatabaseConnectors):
    """Test Google Cloud SQL connectivity and functionality."""
    
    def test_gcp_mysql_connection_string_parsing(self):
        """Test Google Cloud SQL MySQL connection string parsing."""
        connection_string = (
            "mysql://gcpuser:gcppass123@35.202.123.456:3306/gcpdb?ssl-mode=REQUIRED"
        )
        
        parsed = self.scanner._parse_connection_string(connection_string)
        
        self.assertEqual(parsed['host'], '35.202.123.456')
        self.assertEqual(parsed['port'], 3306)
        self.assertEqual(parsed['database'], 'gcpdb')
        self.assertEqual(parsed['username'], 'gcpuser')
        
    def test_gcp_postgresql_connection_string_parsing(self):
        """Test Google Cloud SQL PostgreSQL connection string parsing."""
        connection_string = (
            "postgresql://pguser:pgpass@10.1.2.3:5432/postgresdb?sslmode=require"
        )
        
        parsed = self.scanner._parse_connection_string(connection_string)
        
        self.assertEqual(parsed['host'], '10.1.2.3')
        self.assertEqual(parsed['database'], 'postgresdb')
        self.assertTrue('ssl' in str(parsed).lower())
        
    def test_gcp_unix_socket_connection_parsing(self):
        """Test Google Cloud SQL Unix socket connection parsing."""
        connection_string = (
            "mysql://socketuser:socketpass@localhost:3306/socketdb?unix_socket=/cloudsql/myproject:us-central1:myinstance"
        )
        
        parsed = self.scanner._parse_connection_string(connection_string)
        
        self.assertEqual(parsed['host'], 'localhost')
        self.assertIn('/cloudsql/', str(parsed))
        self.assertIn('myproject:us-central1:myinstance', str(parsed))
        
    def test_gcp_sql_server_connection_string_parsing(self):
        """Test Google Cloud SQL Server connection string parsing.""" 
        connection_string = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=203.0.113.1,1433;"
            "DATABASE=gcpsqldb;"
            "UID=gcpsqluser;"
            "PWD=GcpSqlPass123!;"
            "Encrypt=yes;"
        )
        
        parsed = self.scanner._parse_odbc_connection_string(connection_string)
        
        self.assertEqual(parsed['server'], '203.0.113.1,1433')
        self.assertEqual(parsed['database'], 'gcpsqldb')
        self.assertTrue(parsed.get('encrypt', '').lower() == 'yes')
        
    def test_gcp_cloud_detection(self):
        """Test automatic Google Cloud SQL detection."""
        gcp_indicators = [
            '/cloudsql/',
            '.sql.goog',
            'googleusercontent.com',
            'compute.internal'
        ]
        
        for indicator in gcp_indicators:
            test_string = f"mysql://user:pass@host{indicator}:3306/db"
            is_gcp = self.scanner._is_gcp_cloud_database(test_string)
            self.assertTrue(is_gcp, f"Failed to detect GCP for {indicator}")
            
    @patch('services.db_scanner.mysql.connector.connect')
    def test_gcp_ssl_enforcement(self, mock_connect):
        """Test SSL enforcement for Google Cloud SQL connections."""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        connection_string = (
            "mysql://secure:pass@secure-ip:3306/securedb?ssl-mode=REQUIRED"
        )
        
        result = self.scanner.connect_from_string(connection_string)
        
        mock_connect.assert_called_once()
        call_args = mock_connect.call_args[1]
        # GCP should enforce SSL
        self.assertTrue('ssl' in str(call_args).lower() or call_args.get('ssl_disabled') == False)
        
    def test_gcp_private_ip_vs_public_ip_detection(self):
        """Test detection of private vs public IP addresses for GCP."""
        private_ips = ['10.1.1.1', '192.168.1.100', '172.16.0.50']
        public_ips = ['8.8.8.8', '35.202.123.456', '203.0.113.1']
        
        for private_ip in private_ips:
            self.assertTrue(self.scanner._is_private_ip(private_ip))
            
        for public_ip in public_ips:
            self.assertFalse(self.scanner._is_private_ip(public_ip))
            
    def test_gcp_connection_name_parsing(self):
        """Test parsing of GCP connection names."""
        connection_name = "myproject:us-central1:myinstance"
        
        parsed = self.scanner._parse_gcp_connection_name(connection_name)
        
        self.assertEqual(parsed['project'], 'myproject')
        self.assertEqual(parsed['region'], 'us-central1')
        self.assertEqual(parsed['instance'], 'myinstance')
        
    def test_gcp_performance_with_connection_pooling(self):
        """Test GCP connection performance with pooling."""
        with patch('services.db_scanner.mysql.connector.pooling.MySQLConnectionPool') as mock_pool:
            mock_pool.return_value.get_connection.return_value = Mock()
            
            start_time = time.time()
            
            # Simulate multiple connections
            for i in range(5):
                self.scanner._get_pooled_connection('mysql://user:pass@host:3306/db')
                
            pool_time = time.time() - start_time
            
            # Pooled connections should be fast
            self.assertLess(pool_time, 1.0)


class TestCrossCloudSecurityFeatures(TestCloudDatabaseConnectors):
    """Test security features across all cloud providers."""
    
    def test_password_strength_validation(self):
        """Test password strength validation across providers."""
        weak_passwords = ['123', 'password', 'abc123', 'admin']
        strong_passwords = ['MyStr0ng!Pass', 'Secure#Pass123', 'C0mpl3x$P@ssw0rd']
        
        for weak in weak_passwords:
            self.assertFalse(self.scanner._is_strong_password(weak))
            
        for strong in strong_passwords:
            self.assertTrue(self.scanner._is_strong_password(strong))
            
    def test_connection_string_sanitization(self):
        """Test connection string sanitization for logging."""
        connection_string = "mysql://user:secret123@host:3306/db"
        
        sanitized = self.scanner._sanitize_connection_string_for_logging(connection_string)
        
        # Password should be masked
        self.assertNotIn('secret123', sanitized)
        self.assertIn('***', sanitized)
        
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention in queries."""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'; DELETE FROM logs; --"
        ]
        
        for malicious_input in malicious_inputs:
            sanitized = self.scanner._escape_identifier(malicious_input)
            # Should not contain dangerous SQL characters
            self.assertNotIn(';', sanitized)
            self.assertNotIn('--', sanitized)
            self.assertNotIn('DROP', sanitized.upper())
            
    def test_ssl_certificate_validation(self):
        """Test SSL certificate validation."""
        # Mock SSL context
        with patch('ssl.create_default_context') as mock_ssl:
            mock_context = Mock()
            mock_ssl.return_value = mock_context
            
            self.scanner._create_ssl_context(verify_cert=True)
            
            # Should create context with cert verification
            mock_ssl.assert_called_once()
            self.assertTrue(mock_context.check_hostname)
            
    def test_connection_timeout_enforcement(self):
        """Test connection timeout enforcement."""
        with patch('services.db_scanner.mysql.connector.connect') as mock_connect:
            def timeout_connect(*args, **kwargs):
                if kwargs.get('connection_timeout', 30) < 5:
                    raise Exception("Connection timeout too short")
                return Mock()
                
            mock_connect.side_effect = timeout_connect
            
            # Should enforce minimum timeout
            result = self.scanner._connect_with_timeout("mysql://user:pass@host:3306/db", timeout=1)
            
            # Should have used reasonable timeout
            mock_connect.assert_called_once()
            call_kwargs = mock_connect.call_args[1]
            self.assertGreaterEqual(call_kwargs.get('connection_timeout', 30), 5)


class TestPerformanceBenchmarks(TestCloudDatabaseConnectors):
    """Test performance benchmarks for cloud connectors."""
    
    def test_connection_establishment_speed(self):
        """Test connection establishment speed across providers."""
        providers = {
            'Azure': 'Server=test.mysql.database.azure.com;Database=test;Uid=test;Pwd=test;',
            'AWS': 'mysql://test:test@test.us-east-1.rds.amazonaws.com:3306/test',
            'GCP': 'mysql://test:test@127.0.0.1:3306/test?unix_socket=/cloudsql/project:region:instance'
        }
        
        with patch('services.db_scanner.mysql.connector.connect') as mock_connect:
            mock_connect.return_value = Mock()
            
            performance_results = {}
            
            for provider, connection_string in providers.items():
                start_time = time.time()
                self.scanner.connect_from_string(connection_string)
                end_time = time.time()
                
                performance_results[provider] = end_time - start_time
                
            # All connections should be reasonably fast (under 1 second for mocked)
            for provider, duration in performance_results.items():
                self.assertLess(duration, 1.0, f"{provider} connection too slow: {duration}s")
                
    def test_concurrent_connection_handling(self):
        """Test handling of concurrent connections."""
        def create_connection(provider_name):
            connection_string = f"mysql://test:test@{provider_name}.example.com:3306/test"
            with patch('services.db_scanner.mysql.connector.connect'):
                return self.scanner.connect_from_string(connection_string)
                
        # Test concurrent connections
        threads = []
        results = {}
        
        providers = ['azure', 'aws', 'gcp']
        
        for provider in providers:
            thread = threading.Thread(target=lambda p=provider: results.update({p: create_connection(p)}))
            threads.append(thread)
            thread.start()
            
        # Wait for all threads
        for thread in threads:
            thread.join(timeout=5.0)
            
        # All connections should complete
        self.assertEqual(len(results), len(providers))
        
    def test_memory_usage_optimization(self):
        """Test memory usage during connection operations."""
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Create multiple connections
        with patch('services.db_scanner.mysql.connector.connect') as mock_connect:
            mock_connect.return_value = Mock()
            
            connections = []
            for i in range(10):
                conn = self.scanner.connect_from_string(f"mysql://test{i}:test@host{i}:3306/db{i}")
                connections.append(conn)
                
        # Force garbage collection
        gc.collect()
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB)
        self.assertLess(memory_increase, 50 * 1024 * 1024)


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestAzureDatabaseConnectors,
        TestAWSRDSConnectors, 
        TestGoogleCloudSQLConnectors,
        TestCrossCloudSecurityFeatures,
        TestPerformanceBenchmarks
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
            
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")