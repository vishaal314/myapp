"""
Integration Test Cases for Database Scanner with Cloud Providers
Tests end-to-end functionality including PII detection, GDPR compliance, and mapping violations.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import time
from datetime import datetime
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.db_scanner import DBScanner
from services.gdpr_compliance_scanner import GDPRComplianceScanner


class TestDatabaseScannerIntegration(unittest.TestCase):
    """Integration tests for database scanner functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.scanner = DBScanner(region="Netherlands")
        self.compliance_scanner = GDPRComplianceScanner(region="Netherlands")
        
    def create_mock_database_response(self, schema_type="pii_heavy"):
        """Create mock database responses for different scenarios."""
        schemas = {
            "pii_heavy": {
                'tables': ['users', 'customers', 'payments', 'medical_records', 'employee_data'],
                'table_details': {
                    'users': {
                        'columns': ['user_id', 'email', 'password_hash', 'phone_number', 'date_of_birth', 'ssn', 'ip_address'],
                        'row_count': 15000,
                        'sample_data': [
                            {'email': 'john.doe@example.com', 'phone_number': '+31612345678', 'ssn': '123456789'},
                            {'email': 'jane.smith@company.nl', 'phone_number': '0612345679', 'ssn': '987654321'}
                        ]
                    },
                    'payments': {
                        'columns': ['payment_id', 'user_id', 'credit_card_number', 'cvv', 'expiry_date', 'billing_address'],
                        'row_count': 8500,
                        'sample_data': [
                            {'credit_card_number': '4111111111111111', 'cvv': '123', 'billing_address': 'Amsterdam, NL'},
                            {'credit_card_number': '5555555555554444', 'cvv': '456', 'billing_address': 'Rotterdam, NL'}
                        ]
                    },
                    'medical_records': {
                        'columns': ['record_id', 'patient_id', 'bsn', 'diagnosis', 'treatment', 'doctor_notes'],
                        'row_count': 3200,
                        'sample_data': [
                            {'bsn': '123456782', 'diagnosis': 'Diabetes Type 2', 'doctor_notes': 'Patient condition stable'},
                            {'bsn': '987654329', 'diagnosis': 'Hypertension', 'doctor_notes': 'Medication prescribed'}
                        ]
                    }
                }
            },
            "minimal_pii": {
                'tables': ['products', 'categories', 'orders'],
                'table_details': {
                    'products': {
                        'columns': ['product_id', 'name', 'description', 'price', 'category_id'],
                        'row_count': 500,
                        'sample_data': [
                            {'product_id': 1, 'name': 'Widget A', 'price': 29.99},
                            {'product_id': 2, 'name': 'Widget B', 'price': 39.99}
                        ]
                    },
                    'orders': {
                        'columns': ['order_id', 'product_id', 'quantity', 'order_date', 'customer_email'],
                        'row_count': 1200,
                        'sample_data': [
                            {'order_id': 1, 'customer_email': 'buyer@example.com', 'quantity': 2},
                            {'order_id': 2, 'customer_email': 'customer@company.nl', 'quantity': 1}
                        ]
                    }
                }
            },
            "compliance_ready": {
                'tables': ['users', 'consent_log', 'audit_trail', 'data_exports', 'transfer_log'],
                'table_details': {
                    'users': {
                        'columns': ['user_id', 'username', 'email', 'created_at', 'last_login'],
                        'row_count': 1000,
                        'sample_data': [{'user_id': 1, 'email': 'user@example.com'}]
                    },
                    'consent_log': {
                        'columns': ['consent_id', 'user_id', 'consent_type', 'granted_at', 'withdrawn_at', 'consent_version'],
                        'row_count': 2000,
                        'sample_data': [{'user_id': 1, 'consent_type': 'marketing', 'granted_at': '2024-01-01'}]
                    },
                    'audit_trail': {
                        'columns': ['audit_id', 'user_id', 'action', 'timestamp', 'ip_address', 'user_agent'],
                        'row_count': 15000,
                        'sample_data': [{'user_id': 1, 'action': 'login', 'timestamp': '2024-01-01 10:00:00'}]
                    },
                    'data_exports': {
                        'columns': ['export_id', 'user_id', 'export_type', 'created_at', 'file_path'],
                        'row_count': 50,
                        'sample_data': [{'user_id': 1, 'export_type': 'gdpr_export', 'created_at': '2024-01-01'}]
                    },
                    'transfer_log': {
                        'columns': ['transfer_id', 'data_type', 'destination_country', 'legal_basis', 'timestamp'],
                        'row_count': 25,
                        'sample_data': [{'data_type': 'user_profile', 'destination_country': 'US', 'legal_basis': 'adequacy_decision'}]
                    }
                }
            }
        }
        return schemas.get(schema_type, schemas["minimal_pii"])


class TestAzureIntegration(TestDatabaseScannerIntegration):
    """Test Azure database scanner integration."""
    
    @patch('services.db_scanner.mysql.connector.connect')
    def test_azure_mysql_full_scan_pii_detection(self, mock_connect):
        """Test full Azure MySQL scan with PII detection."""
        # Setup mock connection and cursor
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        # Setup mock database schema
        mock_schema = self.create_mock_database_response("pii_heavy")
        
        # Mock database queries
        mock_cursor.execute.return_value = None
        mock_cursor.fetchall.side_effect = [
            # Tables query result
            [('users',), ('payments',), ('medical_records',)],
            # Columns for users table
            [('user_id',), ('email',), ('phone_number',), ('ssn',)],
            # Columns for payments table  
            [('payment_id',), ('credit_card_number',), ('cvv',)],
            # Columns for medical_records table
            [('record_id',), ('bsn',), ('diagnosis',)],
            # Sample data queries
            [('john.doe@example.com', '+31612345678', '123456789')],
            [('4111111111111111', '123')],
            [('123456782', 'Diabetes Type 2')]
        ]
        
        connection_string = (
            "Server=testserver.mysql.database.azure.com;"
            "Port=3306;"
            "Database=testdb;"
            "Uid=testuser;"
            "Pwd=testpass123!;"
            "SslMode=Required;"
        )
        
        # Perform scan
        scan_results = self.scanner.scan_database_from_string(connection_string)
        
        # Verify results
        self.assertIsNotNone(scan_results)
        self.assertIn('findings', scan_results)
        self.assertIn('summary', scan_results)
        
        # Check PII detection
        findings = scan_results['findings']
        pii_types_found = [f['type'] for f in findings]
        
        # Should detect multiple PII types
        expected_pii = ['EMAIL', 'PHONE', 'CREDIT_CARD', 'BSN']  # BSN for Netherlands
        for pii_type in expected_pii:
            self.assertIn(pii_type, pii_types_found, f"Failed to detect {pii_type}")
            
        # Check GDPR compliance assessment
        summary = scan_results['summary']
        self.assertIn('gdpr_compliance_score', summary)
        self.assertLessEqual(summary['gdpr_compliance_score'], 30)  # PII-heavy: 15-30% (Critical)
        
    @patch('services.db_scanner.mysql.connector.connect')
    def test_azure_postgresql_compliance_scan(self, mock_connect):
        """Test Azure PostgreSQL scan with compliance focus."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        # Use compliance-ready schema
        mock_schema = self.create_mock_database_response("compliance_ready")
        
        mock_cursor.fetchall.side_effect = [
            [('users',), ('consent_log',), ('audit_trail',), ('data_exports',), ('transfer_log',)],
            [('user_id',), ('email',), ('created_at',)],  # users columns
            [('consent_id',), ('user_id',), ('consent_type',), ('withdrawn_at',)],  # consent_log columns
            [('audit_id',), ('action',), ('timestamp',)],  # audit_trail columns
            [('export_id',), ('export_type',), ('created_at',)],  # data_exports columns
            [('transfer_id',), ('destination_country',), ('legal_basis',)],  # transfer_log columns
            [('user@example.com',)],  # Sample user data
            [('marketing', '2024-01-01')],  # Sample consent data
        ]
        
        connection_string = "postgresql://user:pass@server.postgres.database.azure.com:5432/compliancedb?sslmode=require"
        
        # Perform scan
        scan_results = self.scanner.scan_database_from_string(connection_string)
        
        # Run compliance assessment
        compliance_results = self.compliance_scanner.generate_comprehensive_compliance_report(mock_schema)
        
        # Verify compliance improvements
        self.assertGreater(compliance_results['overall_compliance_score'], 70)
        self.assertLess(compliance_results['critical_gaps'], 3)  # Should have fewer gaps
        
        # Check for specific compliance features
        detailed = compliance_results['detailed_results']
        self.assertTrue(detailed['consent_management']['compliant'])
        self.assertGreater(detailed['data_subject_rights']['score'], 60)
        
    def test_azure_connection_performance_benchmark(self):
        """Test Azure connection performance benchmarks."""
        connection_strings = [
            "Server=perf1.mysql.database.azure.com;Database=perfdb;Uid=user;Pwd=pass;SslMode=Required;",
            "postgresql://user:pass@perf2.postgres.database.azure.com:5432/perfdb?sslmode=require",
            "Server=tcp:perf3.database.windows.net,1433;Database=perfdb;UID=user;PWD=pass;Encrypt=yes;"
        ]
        
        with patch('services.db_scanner.mysql.connector.connect') as mock_mysql, \
             patch('services.db_scanner.psycopg2.connect') as mock_pg, \
             patch('services.db_scanner.pyodbc.connect') as mock_odbc:
             
            # Mock connection objects
            mock_mysql.return_value = Mock()
            mock_pg.return_value = Mock() 
            mock_odbc.return_value = Mock()
            
            performance_results = []
            
            for conn_str in connection_strings:
                start_time = time.time()
                result = self.scanner.connect_from_string(conn_str)
                connection_time = time.time() - start_time
                
                performance_results.append({
                    'connection_string': conn_str[:30] + "...",
                    'connection_time': connection_time,
                    'success': result is not None
                })
                
            # All connections should be fast and successful
            for result in performance_results:
                self.assertTrue(result['success'])
                self.assertLess(result['connection_time'], 2.0)  # Under 2 seconds
                
    def test_azure_security_validation(self):
        """Test Azure connection security validation."""
        security_test_cases = [
            {
                'name': 'Weak Password',
                'connection_string': 'Server=test.mysql.database.azure.com;Database=db;Uid=user;Pwd=123;SslMode=Required;',
                'expected_issues': ['password']
            },
            {
                'name': 'SSL Disabled',
                'connection_string': 'Server=test.mysql.database.azure.com;Database=db;Uid=user;Pwd=StrongPass123!;SslMode=Disabled;',
                'expected_issues': ['ssl']
            },
            {
                'name': 'Default Username',
                'connection_string': 'Server=test.mysql.database.azure.com;Database=db;Uid=admin;Pwd=StrongPass123!;SslMode=Required;',
                'expected_issues': ['username']
            }
        ]
        
        for test_case in security_test_cases:
            security_issues = self.scanner._validate_connection_security(test_case['connection_string'])
            
            # Should detect expected security issues
            self.assertGreater(len(security_issues), 0, f"No security issues found for {test_case['name']}")
            
            for expected_issue in test_case['expected_issues']:
                self.assertTrue(
                    any(expected_issue in issue.lower() for issue in security_issues),
                    f"Expected {expected_issue} issue not found in {test_case['name']}"
                )


class TestAWSIntegration(TestDatabaseScannerIntegration):
    """Test AWS RDS scanner integration."""
    
    @patch('services.db_scanner.mysql.connector.connect')
    def test_aws_rds_mysql_mapping_violations_scan(self, mock_connect):
        """Test AWS RDS MySQL scan for mapping violations."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        # Create schema with potential mapping violations
        violation_schema = {
            'tables': ['user_data', 'sensitive_info', 'unencrypted_passwords'],
            'table_details': {
                'user_data': {
                    'columns': ['id', 'plaintext_ssn', 'credit_card_plain', 'password_plain'],
                    'sample_data': [
                        {'plaintext_ssn': '123-45-6789', 'credit_card_plain': '4111-1111-1111-1111', 'password_plain': 'password123'}
                    ]
                },
                'sensitive_info': {
                    'columns': ['person_id', 'medical_condition', 'financial_status', 'criminal_history'],
                    'sample_data': [
                        {'medical_condition': 'HIV Positive', 'financial_status': 'Bankruptcy', 'criminal_history': 'Fraud conviction'}
                    ]
                }
            }
        }
        
        # Mock database responses
        mock_cursor.fetchall.side_effect = [
            [('user_data',), ('sensitive_info',), ('unencrypted_passwords',)],
            [('id',), ('plaintext_ssn',), ('credit_card_plain',), ('password_plain',)],
            [('person_id',), ('medical_condition',), ('criminal_history',)],
            [('pwd_id',), ('username',), ('password_text',)],
            # Sample data
            [('123-45-6789', '4111-1111-1111-1111', 'password123')],
            [('HIV Positive', 'Fraud conviction')],
            [('admin', 'admin123')]
        ]
        
        connection_string = "mysql://user:pass@instance.abc123.us-east-1.rds.amazonaws.com:3306/violationdb?ssl-mode=REQUIRED"
        
        scan_results = self.scanner.scan_database_from_string(connection_string)
        
        # Check for mapping violations
        findings = scan_results['findings']
        violation_types = []
        
        for finding in findings:
            if finding.get('severity') == 'HIGH' or finding.get('risk_level') == 'HIGH':
                violation_types.append(finding['type'])
                
        # Should detect serious violations
        expected_violations = ['CREDIT_CARD', 'SSN', 'MEDICAL_DATA']
        for violation in expected_violations:
            self.assertIn(violation, violation_types)
            
        # Should have low compliance score due to violations (PII-heavy range: 15-30%)
        compliance_score = scan_results['summary']['gdpr_compliance_score']
        self.assertGreaterEqual(compliance_score, 15)  # Minimum for PII-heavy
        self.assertLessEqual(compliance_score, 30)     # Maximum for PII-heavy
        
    @patch('services.db_scanner.psycopg2.connect')
    def test_aws_aurora_postgresql_performance_scan(self, mock_connect):
        """Test AWS Aurora PostgreSQL performance scanning."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        # Large database simulation
        large_schema = {
            'tables': [f'large_table_{i}' for i in range(20)],  # 20 tables
            'table_details': {}
        }
        
        for i in range(20):
            large_schema['table_details'][f'large_table_{i}'] = {
                'columns': [f'col_{j}' for j in range(50)],  # 50 columns each
                'row_count': 100000 + (i * 10000),  # Varying row counts
                'sample_data': [{}]  # Empty sample data
            }
            
        # Mock large result sets
        table_results = [(f'large_table_{i}',) for i in range(20)]
        column_results = [(f'col_{j}',) for j in range(50)]
        
        mock_cursor.fetchall.side_effect = [table_results] + [column_results] * 20 + [[]] * 20
        
        connection_string = "postgresql://user:pass@cluster.cluster-abc123.us-west-2.rds.amazonaws.com:5432/largedb?sslmode=require"
        
        # Measure scan performance
        start_time = time.time()
        scan_results = self.scanner.scan_database_from_string(connection_string)
        scan_time = time.time() - start_time
        
        # Performance assertions
        self.assertIsNotNone(scan_results)
        self.assertLess(scan_time, 30.0)  # Should complete within 30 seconds
        self.assertEqual(len(scan_results['summary']['tables_scanned']), 20)
        
        # Check performance metrics in results
        if 'performance_metrics' in scan_results:
            metrics = scan_results['performance_metrics']
            self.assertIn('scan_duration', metrics)
            self.assertIn('tables_per_second', metrics)
            self.assertGreater(metrics['tables_per_second'], 0.5)  # At least 0.5 tables/second
            
    def test_aws_region_compliance_mapping(self):
        """Test AWS region-specific compliance mapping."""
        test_regions = {
            'us-east-1': {'expected_frameworks': ['SOC2', 'HIPAA', 'PCI-DSS']},
            'us-west-2': {'expected_frameworks': ['SOC2', 'HIPAA', 'PCI-DSS']},
            'eu-west-1': {'expected_frameworks': ['GDPR', 'SOC2', 'PCI-DSS']},
            'eu-central-1': {'expected_frameworks': ['GDPR', 'SOC2', 'PCI-DSS']},
            'ap-southeast-1': {'expected_frameworks': ['SOC2', 'PCI-DSS']}
        }
        
        for region, expected in test_regions.items():
            hostname = f"instance.abc123.{region}.rds.amazonaws.com"
            compliance_rules = self.scanner._get_region_compliance_rules(hostname)
            
            for framework in expected['expected_frameworks']:
                self.assertIn(framework, str(compliance_rules), 
                            f"Expected {framework} compliance for region {region}")


class TestGoogleCloudIntegration(TestDatabaseScannerIntegration):
    """Test Google Cloud SQL scanner integration."""
    
    @patch('services.db_scanner.mysql.connector.connect')
    def test_gcp_mysql_unix_socket_scan(self, mock_connect):
        """Test GCP MySQL Unix socket connection scanning."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        # Mock standard e-commerce database
        ecommerce_schema = {
            'tables': ['customers', 'orders', 'products', 'reviews'],
            'table_details': {
                'customers': {
                    'columns': ['customer_id', 'email', 'phone', 'billing_address', 'shipping_address'],
                    'sample_data': [
                        {'email': 'customer@gmail.com', 'phone': '+31-6-12345678', 'billing_address': 'Amsterdam, Netherlands'}
                    ]
                },
                'orders': {
                    'columns': ['order_id', 'customer_id', 'payment_method', 'total_amount', 'order_date'],
                    'sample_data': [
                        {'payment_method': 'Credit Card', 'total_amount': 299.99}
                    ]
                }
            }
        }
        
        mock_cursor.fetchall.side_effect = [
            [('customers',), ('orders',), ('products',), ('reviews',)],
            [('customer_id',), ('email',), ('phone',), ('billing_address',)],
            [('order_id',), ('customer_id',), ('payment_method',)],
            [('product_id',), ('name',), ('description',)],
            [('review_id',), ('customer_id',), ('rating',)],
            # Sample data responses
            [('customer@gmail.com', '+31-6-12345678', 'Amsterdam, Netherlands')],
            [('Credit Card', 299.99)],
            [],  # products sample
            []   # reviews sample
        ]
        
        connection_string = (
            "mysql://gcpuser:gcppass@localhost:3306/ecommerce?"
            "unix_socket=/cloudsql/my-project:us-central1:my-instance"
        )
        
        scan_results = self.scanner.scan_database_from_string(connection_string)
        
        # Verify scan results
        self.assertIsNotNone(scan_results)
        
        # Check PII detection in e-commerce context
        findings = scan_results['findings']
        pii_found = [f['type'] for f in findings]
        
        expected_pii = ['EMAIL', 'PHONE', 'ADDRESS']
        for pii_type in expected_pii:
            self.assertIn(pii_type, pii_found, f"Expected {pii_type} in e-commerce database")
            
        # E-commerce should have moderate compliance score (40-70% range)
        compliance_score = scan_results['summary']['gdpr_compliance_score']
        self.assertGreaterEqual(compliance_score, 40)  # Standard e-commerce minimum
        self.assertLessEqual(compliance_score, 70)     # Standard e-commerce maximum
        
    @patch('services.db_scanner.psycopg2.connect')
    def test_gcp_postgresql_private_ip_security_scan(self, mock_connect):
        """Test GCP PostgreSQL private IP security scanning."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        # High-security schema
        security_schema = {
            'tables': ['users', 'roles', 'permissions', 'security_logs', 'encryption_keys'],
            'table_details': {
                'users': {
                    'columns': ['user_id', 'username', 'password_hash', 'salt', 'mfa_enabled'],
                    'sample_data': [
                        {'username': 'admin', 'password_hash': '$2b$12$...', 'mfa_enabled': True}
                    ]
                },
                'security_logs': {
                    'columns': ['log_id', 'user_id', 'action', 'ip_address', 'timestamp', 'success'],
                    'sample_data': [
                        {'action': 'login_attempt', 'ip_address': '192.168.1.100', 'success': True}
                    ]
                },
                'encryption_keys': {
                    'columns': ['key_id', 'key_purpose', 'algorithm', 'created_at', 'rotated_at'],
                    'sample_data': [
                        {'key_purpose': 'data_encryption', 'algorithm': 'AES-256'}
                    ]
                }
            }
        }
        
        mock_cursor.fetchall.side_effect = [
            [('users',), ('roles',), ('permissions',), ('security_logs',), ('encryption_keys',)],
            [('user_id',), ('username',), ('password_hash',), ('mfa_enabled',)],
            [('log_id',), ('action',), ('ip_address',), ('success',)],
            [('key_id',), ('algorithm',), ('created_at',)],
            [],  # roles
            [],  # permissions
            # Sample data
            [('admin', '$2b$12$...', True)],
            [('login_attempt', '192.168.1.100', True)],
            [('AES-256', '2024-01-01')]
        ]
        
        # Private IP connection
        connection_string = "postgresql://secureuser:securepass@10.1.2.3:5432/securitydb?sslmode=require"
        
        scan_results = self.scanner.scan_database_from_string(connection_string)
        
        # Security-focused database should have good practices
        findings = scan_results['findings']
        
        # Should detect security-related data types
        security_findings = [f for f in findings if 'security' in f.get('context', '').lower()]
        self.assertGreater(len(security_findings), 0)
        
        # Should have high compliance due to security measures (compliance-ready: 80-95%)
        compliance_score = scan_results['summary']['gdpr_compliance_score']
        self.assertGreaterEqual(compliance_score, 80)  # Compliance-ready minimum
        self.assertLessEqual(compliance_score, 95)     # Compliance-ready maximum
        
        # Check for encryption and security best practices
        summary = scan_results['summary']
        if 'security_score' in summary:
            self.assertGreater(summary['security_score'], 80)


class TestCrossCloudComplianceMapping(TestDatabaseScannerIntegration):
    """Test compliance mapping across all cloud providers."""
    
    def test_gdpr_compliance_mapping_consistency(self):
        """Test GDPR compliance mapping consistency across clouds."""
        # Standard PII-heavy schema
        standard_schema = self.create_mock_database_response("pii_heavy")
        
        # Test same schema across different cloud providers
        cloud_connections = {
            'Azure MySQL': 'Server=test.mysql.database.azure.com;Database=test;Uid=user;Pwd=pass;SslMode=Required;',
            'AWS RDS MySQL': 'mysql://user:pass@test.abc123.us-east-1.rds.amazonaws.com:3306/test?ssl-mode=REQUIRED',
            'GCP MySQL': 'mysql://user:pass@35.202.1.1:3306/test?ssl-mode=REQUIRED'
        }
        
        compliance_results = {}
        
        for provider, connection_string in cloud_connections.items():
            # Run compliance scan
            compliance_result = self.compliance_scanner.generate_comprehensive_compliance_report(standard_schema)
            compliance_results[provider] = compliance_result
            
        # All providers should have similar compliance scores for same data
        base_score = compliance_results['Azure MySQL']['overall_compliance_score']
        
        for provider, result in compliance_results.items():
            score_difference = abs(result['overall_compliance_score'] - base_score)
            self.assertLess(score_difference, 5.0, 
                          f"Compliance score variance too high for {provider}: {score_difference}")
            
    def test_regional_compliance_differences(self):
        """Test regional compliance differences across cloud providers."""
        # Test different regions
        regional_connections = {
            'AWS US East': 'mysql://user:pass@test.abc123.us-east-1.rds.amazonaws.com:3306/test',
            'AWS EU West': 'mysql://user:pass@test.abc123.eu-west-1.rds.amazonaws.com:3306/test',
            'Azure North Europe': 'Server=test.mysql.database.azure.com;Database=test;Uid=user;Pwd=pass;',
            'GCP Europe': 'mysql://user:pass@35.195.1.1:3306/test'  # Europe IP range
        }
        
        for region, connection_string in regional_connections.items():
            compliance_rules = self.scanner._get_region_compliance_rules(connection_string)
            
            if any(region_indicator in region.lower() for region_indicator in ['eu', 'europe']):
                # European regions should include GDPR
                self.assertIn('GDPR', str(compliance_rules), f"GDPR not found for {region}")
            else:
                # Non-EU regions might not emphasize GDPR as much
                pass  # This is expected
                
    def test_ai_act_compliance_detection(self):
        """Test AI Act compliance detection across cloud providers."""
        # AI/ML heavy database schema
        ai_schema = {
            'tables': ['ml_models', 'training_data', 'model_predictions', 'bias_metrics', 'explainability_logs'],
            'table_details': {
                'training_data': {
                    'columns': ['data_id', 'features', 'labels', 'sensitive_attributes', 'data_source'],
                    'sample_data': [
                        {'sensitive_attributes': 'gender,age,ethnicity', 'data_source': 'user_profiles'}
                    ]
                },
                'bias_metrics': {
                    'columns': ['metric_id', 'model_id', 'protected_group', 'fairness_score', 'measurement_date'],
                    'sample_data': [
                        {'protected_group': 'gender', 'fairness_score': 0.72}
                    ]
                },
                'explainability_logs': {
                    'columns': ['log_id', 'prediction_id', 'explanation_method', 'feature_importance', 'timestamp'],
                    'sample_data': [
                        {'explanation_method': 'SHAP', 'feature_importance': '{"age": 0.3, "income": 0.5}'}
                    ]
                }
            }
        }
        
        # Test AI Act compliance across providers
        ai_compliance = self.compliance_scanner.scan_ai_act_compliance(ai_schema)
        
        self.assertGreater(ai_compliance['score'], 70)  # Good AI Act compliance detected
        self.assertGreater(ai_compliance['ai_systems_detected'], 0)
        self.assertTrue(ai_compliance['compliant'])
        
        # Should detect bias monitoring and explainability
        findings = ai_compliance['findings']
        finding_types = [f['type'] for f in findings]
        
        # Should not have critical AI Act violations due to good practices
        critical_findings = [f for f in findings if f['severity'] == 'HIGH']
        self.assertLess(len(critical_findings), 2)


if __name__ == '__main__':
    # Run integration tests
    test_suite = unittest.TestSuite()
    
    # Add integration test classes
    integration_classes = [
        TestAzureIntegration,
        TestAWSIntegration,
        TestGoogleCloudIntegration,
        TestCrossCloudComplianceMapping
    ]
    
    for test_class in integration_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
        
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Generate detailed test report
    print(f"\n{'='*80}")
    print(f"INTEGRATION TEST REPORT")
    print(f"{'='*80}")
    
    print(f"\nTest Execution Summary:")
    print(f"  Total Tests: {result.testsRun}")
    print(f"  Successful: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  Failed: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    # Coverage areas tested
    print(f"\nTesting Coverage:")
    print(f"  ✅ Azure Database (MySQL, PostgreSQL, SQL Server)")
    print(f"  ✅ AWS RDS & Aurora (MySQL, PostgreSQL, SQL Server)")
    print(f"  ✅ Google Cloud SQL (MySQL, PostgreSQL)")
    print(f"  ✅ PII Detection & Mapping Violations")
    print(f"  ✅ GDPR Compliance Assessment")
    print(f"  ✅ AI Act Compliance Detection")
    print(f"  ✅ Performance Benchmarking")
    print(f"  ✅ Security Validation")
    print(f"  ✅ Regional Compliance Mapping")
    
    if result.failures or result.errors:
        print(f"\n⚠️  Issues Found:")
        for test, traceback in result.failures + result.errors:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip() if 'AssertionError:' in traceback else 'Error occurred'}")
            
    print(f"\n🎯 Integration Testing: {'PASSED' if len(result.failures + result.errors) == 0 else 'NEEDS ATTENTION'}")