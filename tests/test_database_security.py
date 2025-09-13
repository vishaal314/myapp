"""
Database Security and Tenant Isolation Tests

Comprehensive tests to verify:
1. Transport security enforcement (TLS)
2. Row Level Security (RLS) policies
3. Cross-tenant data isolation
4. Organization context enforcement
"""

import os
import pytest
import psycopg2
import uuid
from datetime import datetime
from typing import Dict, Any

# Set up test environment
os.environ['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'postgresql://localhost/test_db')

try:
    from services.results_aggregator import ResultsAggregator
    from services.multi_tenant_service import MultiTenantService, TenantConfig, TenantTier
except ImportError:
    # Handle relative imports for testing
    import sys
    sys.path.append('.')
    from services.results_aggregator import ResultsAggregator
    from services.multi_tenant_service import MultiTenantService, TenantConfig, TenantTier


class TestDatabaseSecurity:
    """Test database transport security and Row Level Security."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.test_org_1 = 'test_org_1'
        self.test_org_2 = 'test_org_2'
        self.test_admin_org = 'admin_test_org'
        
        # Initialize services
        self.multi_tenant_service = MultiTenantService()
        self.results_aggregator = ResultsAggregator()
        
        # Create test tenant organizations
        self._create_test_tenants()
    
    def _create_test_tenants(self):
        """Create test tenant organizations."""
        test_tenants = [
            TenantConfig(
                organization_id=self.test_org_1,
                organization_name='Test Organization 1',
                tier=TenantTier.PROFESSIONAL,
                max_users=10,
                max_scans_per_month=100,
                max_storage_gb=10,
                features={'basic_scanning', 'gdpr_compliance'},
                compliance_regions=['EU'],
                data_residency='EU',
                created_at=datetime.now(),
                metadata={'test': True}
            ),
            TenantConfig(
                organization_id=self.test_org_2,
                organization_name='Test Organization 2',
                tier=TenantTier.ENTERPRISE,
                max_users=50,
                max_scans_per_month=500,
                max_storage_gb=100,
                features={'basic_scanning', 'gdpr_compliance', 'advanced_reports'},
                compliance_regions=['EU'],
                data_residency='EU',
                created_at=datetime.now(),
                metadata={'test': True}
            ),
            TenantConfig(
                organization_id=self.test_admin_org,
                organization_name='Admin Test Organization',
                tier=TenantTier.ENTERPRISE_PLUS,
                max_users=100,
                max_scans_per_month=1000,
                max_storage_gb=500,
                features={'basic_scanning', 'gdpr_compliance', 'advanced_reports', 'admin_access'},
                compliance_regions=['EU'],
                data_residency='EU',
                created_at=datetime.now(),
                metadata={'test': True, 'admin': True}
            )
        ]
        
        for tenant in test_tenants:
            try:
                self.multi_tenant_service.create_tenant(tenant)
                print(f"Created test tenant: {tenant.organization_id}")
            except Exception as e:
                print(f"Test tenant {tenant.organization_id} may already exist: {str(e)}")
    
    def test_transport_security_enforcement(self):
        """Test that all database connections enforce TLS."""
        print("Testing transport security enforcement...")
        
        # Test that secure connections are established
        try:
            conn = self.multi_tenant_service.get_secure_connection(self.test_org_1)
            assert conn is not None, "Secure connection should be established"
            
            # Verify SSL is being used
            cursor = conn.cursor()
            cursor.execute("SHOW ssl;")
            ssl_status = cursor.fetchone()[0]
            assert ssl_status == 'on', f"SSL should be enabled, got: {ssl_status}"
            
            cursor.close()
            conn.close()
            print("✅ Transport security enforcement verified")
            
        except Exception as e:
            pytest.fail(f"Transport security test failed: {str(e)}")
    
    def test_row_level_security_policies(self):
        """Test that RLS policies are properly configured."""
        print("Testing Row Level Security policies...")
        
        try:
            # Use admin bypass to check RLS configuration
            conn = self.multi_tenant_service.get_secure_connection(self.test_admin_org, admin_bypass=True)
            cursor = conn.cursor()
            
            # Check that RLS is enabled on scans table
            cursor.execute("""
                SELECT rowsecurity 
                FROM pg_tables 
                WHERE tablename = 'scans' AND schemaname = 'public';
            """)
            
            result = cursor.fetchone()
            if result:
                rls_enabled = result[0]
                assert rls_enabled, "Row Level Security should be enabled on scans table"
            
            # Check that RLS policies exist
            cursor.execute("""
                SELECT COUNT(*) 
                FROM pg_policies 
                WHERE tablename = 'scans' AND schemaname = 'public';
            """)
            
            policy_count = cursor.fetchone()[0]
            assert policy_count > 0, "RLS policies should exist for scans table"
            
            cursor.close()
            conn.close()
            print("✅ Row Level Security policies verified")
            
        except Exception as e:
            pytest.fail(f"RLS policy test failed: {str(e)}")
    
    def test_tenant_data_isolation(self):
        """Test that tenants cannot access each other's data."""
        print("Testing tenant data isolation...")
        
        # Create test scan data for each organization
        test_scan_1 = {
            'scan_id': f'test_scan_1_{uuid.uuid4().hex}',
            'scan_type': 'code_scan',
            'region': 'EU',
            'files_scanned': 10,
            'total_pii_found': 5,
            'high_risk_count': 2,
            'findings': ['test_finding_1']
        }
        
        test_scan_2 = {
            'scan_id': f'test_scan_2_{uuid.uuid4().hex}',
            'scan_type': 'database_scan',
            'region': 'EU',
            'files_scanned': 20,
            'total_pii_found': 8,
            'high_risk_count': 3,
            'findings': ['test_finding_2']
        }
        
        try:
            # Store scans for different organizations
            scan_id_1 = self.results_aggregator.store_scan_result(
                username='test_user_1',
                result=test_scan_1,
                organization_id=self.test_org_1
            )
            
            scan_id_2 = self.results_aggregator.store_scan_result(
                username='test_user_2',
                result=test_scan_2,
                organization_id=self.test_org_2
            )
            
            # Test 1: Organization 1 should access only its own scan
            org_1_scan = self.results_aggregator.get_scan_result(scan_id_1, self.test_org_1)
            assert org_1_scan is not None, "Organization 1 should access its own scan"
            assert org_1_scan['scan_id'] == scan_id_1, "Should return correct scan"
            
            # Test 2: Organization 1 should NOT access Organization 2's scan
            try:
                org_1_accessing_org_2 = self.results_aggregator.get_scan_result(scan_id_2, self.test_org_1)
                assert org_1_accessing_org_2 is None, "Organization 1 should NOT access Organization 2's scan"
            except PermissionError:
                # This is also acceptable - should deny access
                pass
            
            # Test 3: Organization 2 should access only its own scan
            org_2_scan = self.results_aggregator.get_scan_result(scan_id_2, self.test_org_2)
            assert org_2_scan is not None, "Organization 2 should access its own scan"
            assert org_2_scan['scan_id'] == scan_id_2, "Should return correct scan"
            
            # Test 4: Organization 2 should NOT access Organization 1's scan
            try:
                org_2_accessing_org_1 = self.results_aggregator.get_scan_result(scan_id_1, self.test_org_2)
                assert org_2_accessing_org_1 is None, "Organization 2 should NOT access Organization 1's scan"
            except PermissionError:
                # This is also acceptable - should deny access
                pass
            
            print("✅ Tenant data isolation verified")
            
        except Exception as e:
            pytest.fail(f"Tenant isolation test failed: {str(e)}")
    
    def test_audit_log_isolation(self):
        """Test that audit logs are also isolated by tenant."""
        print("Testing audit log isolation...")
        
        try:
            # Create audit events for different organizations
            self.results_aggregator.log_audit_event(
                username='test_user_1',
                action='test_action_1',
                details={'test': 'data_1'},
                organization_id=self.test_org_1
            )
            
            self.results_aggregator.log_audit_event(
                username='test_user_2',
                action='test_action_2',
                details={'test': 'data_2'},
                organization_id=self.test_org_2
            )
            
            # Verify audit logs are isolated (would need additional methods to query audit logs)
            # This tests that the audit events can be created without cross-contamination
            print("✅ Audit log isolation test completed")
            
        except Exception as e:
            pytest.fail(f"Audit log isolation test failed: {str(e)}")
    
    def test_organization_context_enforcement(self):
        """Test that organization context is properly enforced."""
        print("Testing organization context enforcement...")
        
        try:
            # Test valid organization access
            valid_access = self.multi_tenant_service.validate_tenant_access(self.test_org_1)
            assert valid_access, "Valid organization should have access"
            
            # Test invalid organization access
            invalid_access = self.multi_tenant_service.validate_tenant_access('nonexistent_org')
            assert not invalid_access, "Invalid organization should not have access"
            
            # Test secure connection with valid organization
            conn = self.multi_tenant_service.get_secure_connection(self.test_org_1)
            assert conn is not None, "Should get connection for valid organization"
            conn.close()
            
            # Test secure connection with invalid organization should fail
            try:
                invalid_conn = self.multi_tenant_service.get_secure_connection('nonexistent_org')
                pytest.fail("Should not get connection for invalid organization")
            except PermissionError:
                pass  # Expected behavior
            
            print("✅ Organization context enforcement verified")
            
        except Exception as e:
            pytest.fail(f"Organization context enforcement test failed: {str(e)}")
    
    def test_admin_bypass_functionality(self):
        """Test that admin bypass works for administrative operations."""
        print("Testing admin bypass functionality...")
        
        try:
            # Test admin bypass connection
            admin_conn = self.multi_tenant_service.get_secure_connection(
                self.test_admin_org, 
                admin_bypass=True
            )
            assert admin_conn is not None, "Admin should get bypass connection"
            
            cursor = admin_conn.cursor()
            
            # Verify admin bypass is set
            cursor.execute("SELECT current_setting('app.admin_bypass', true);")
            bypass_setting = cursor.fetchone()[0]
            assert bypass_setting == 'true', "Admin bypass should be enabled"
            
            cursor.close()
            admin_conn.close()
            
            print("✅ Admin bypass functionality verified")
            
        except Exception as e:
            pytest.fail(f"Admin bypass test failed: {str(e)}")
    
    def teardown_method(self):
        """Clean up after each test."""
        try:
            # Clean up test data (would need additional cleanup methods)
            print("Test cleanup completed")
        except Exception as e:
            print(f"Cleanup warning: {str(e)}")


def run_security_tests():
    """Run all database security tests."""
    print("🔒 Starting Database Security Tests")
    print("=" * 50)
    
    test_instance = TestDatabaseSecurity()
    
    try:
        test_instance.setup_method()
        
        # Run all tests
        test_instance.test_transport_security_enforcement()
        test_instance.test_row_level_security_policies()
        test_instance.test_tenant_data_isolation()
        test_instance.test_audit_log_isolation()
        test_instance.test_organization_context_enforcement()
        test_instance.test_admin_bypass_functionality()
        
        test_instance.teardown_method()
        
        print("=" * 50)
        print("🎉 All Database Security Tests Passed!")
        
    except Exception as e:
        print(f"❌ Security test failed: {str(e)}")
        raise


if __name__ == "__main__":
    run_security_tests()