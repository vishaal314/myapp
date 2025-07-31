"""
Unit Tests for License System - Comprehensive test coverage for production deployment.
"""

import unittest
import tempfile
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.license_manager import (
    LicenseManager, LicenseType, UsageLimitType, LicenseConfig, UsageLimit
)
from services.usage_analytics import UsageAnalytics, UsageEventType

class TestLicenseManager(unittest.TestCase):
    """Test suite for license manager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary license file
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file.close()
        
        self.license_manager = LicenseManager(
            license_file=self.temp_file.name,
            encrypt_license=False
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_license_generation_trial(self):
        """Test trial license generation."""
        license_config = self.license_manager.generate_license(
            license_type=LicenseType.TRIAL,
            customer_id="TEST001",
            customer_name="Test User",
            company_name="Test Company",
            email="test@example.com",
            validity_days=30
        )
        
        self.assertEqual(license_config.license_type, LicenseType.TRIAL)
        self.assertEqual(license_config.customer_id, "TEST001")
        self.assertEqual(len(license_config.usage_limits), 4)  # Trial has 4 limits
        
        # Check specific trial limits
        scan_limit = next(
            (limit for limit in license_config.usage_limits 
             if limit.limit_type == UsageLimitType.SCANS_PER_MONTH), None
        )
        self.assertIsNotNone(scan_limit)
        if scan_limit:
            self.assertEqual(scan_limit.limit_value, 5)  # Updated to 5 scans for trial
    
    def test_license_generation_enterprise(self):
        """Test enterprise license generation."""
        license_config = self.license_manager.generate_license(
            license_type=LicenseType.ENTERPRISE,
            customer_id="ENT001",
            customer_name="Enterprise User", 
            company_name="Enterprise Corp",
            email="enterprise@example.com",
            validity_days=365
        )
        
        self.assertEqual(license_config.license_type, LicenseType.ENTERPRISE)
        
        # Check enterprise scan limits (updated for new pricing)
        scan_limit = next(
            (limit for limit in license_config.usage_limits 
             if limit.limit_type == UsageLimitType.SCANS_PER_MONTH), None
        )
        self.assertIsNotNone(scan_limit)
        if scan_limit:
            self.assertEqual(scan_limit.limit_value, 200)  # Updated enterprise limit
    
    def test_license_validation_valid(self):
        """Test license validation for valid license."""
        # Generate and save a valid license
        license_config = self.license_manager.generate_license(
            license_type=LicenseType.BASIC,
            customer_id="BASIC001",
            customer_name="Basic User",
            company_name="Basic Company",
            email="basic@example.com",
            validity_days=30
        )
        
        self.license_manager.save_license(license_config)
        
        # Validate license
        is_valid, message = self.license_manager.validate_license()
        self.assertTrue(is_valid)
        self.assertIn("valid", message.lower())
    
    def test_license_validation_expired(self):
        """Test license validation for expired license."""
        # Generate expired license
        license_config = self.license_manager.generate_license(
            license_type=LicenseType.BASIC,
            customer_id="EXPIRED001",
            customer_name="Expired User",
            company_name="Expired Company",
            email="expired@example.com",
            validity_days=-1  # Already expired
        )
        
        self.license_manager.save_license(license_config)
        
        # Validate license
        is_valid, message = self.license_manager.validate_license()
        self.assertFalse(is_valid)
        self.assertIn("expired", message.lower())
    
    def test_usage_limit_checking(self):
        """Test usage limit checking functionality."""
        # Generate license with known limits
        license_config = self.license_manager.generate_license(
            license_type=LicenseType.TRIAL,
            customer_id="USAGE001",
            customer_name="Usage Test",
            company_name="Usage Company",
            email="usage@example.com",
            validity_days=30
        )
        
        self.license_manager.save_license(license_config)
        
        # Check initial usage
        allowed, current, limit = self.license_manager.check_usage_limit(
            UsageLimitType.SCANS_PER_MONTH
        )
        self.assertTrue(allowed)
        self.assertEqual(current, 0)
        self.assertEqual(limit, 5)  # Updated trial limit
    
    def test_usage_increment(self):
        """Test usage increment functionality."""
        # Generate and save license
        license_config = self.license_manager.generate_license(
            license_type=LicenseType.TRIAL,
            customer_id="INCREMENT001",
            customer_name="Increment Test",
            company_name="Increment Company",
            email="increment@example.com",
            validity_days=30
        )
        
        self.license_manager.save_license(license_config)
        
        # Increment usage (only 1 since trial limit is now 5)
        success = self.license_manager.increment_usage(
            UsageLimitType.SCANS_PER_MONTH, 1
        )
        self.assertTrue(success)
        
        # Check updated usage
        allowed, current, limit = self.license_manager.check_usage_limit(
            UsageLimitType.SCANS_PER_MONTH
        )
        self.assertEqual(current, 1)
    
    def test_feature_access_checking(self):
        """Test feature access checking."""
        # Generate trial license
        license_config = self.license_manager.generate_license(
            license_type=LicenseType.TRIAL,
            customer_id="FEATURE001",
            customer_name="Feature Test",
            company_name="Feature Company",
            email="feature@example.com",
            validity_days=30
        )
        
        self.license_manager.save_license(license_config)
        
        # Check allowed feature
        has_access = self.license_manager.check_feature_access("code_scanner")
        self.assertTrue(has_access)
        
        # Check restricted feature (trial doesn't have white_label)
        has_access = self.license_manager.check_feature_access("white_label")
        self.assertFalse(has_access)
    
    def test_session_tracking(self):
        """Test concurrent session tracking."""
        # Generate license with 2 concurrent user limit
        license_config = self.license_manager.generate_license(
            license_type=LicenseType.TRIAL,
            customer_id="SESSION001",
            customer_name="Session Test",
            company_name="Session Company",
            email="session@example.com",
            validity_days=30
        )
        
        self.license_manager.save_license(license_config)
        
        # Track first user
        success1 = self.license_manager.track_session("user1")
        self.assertTrue(success1)
        
        # Track second user (trial now has only 1 user limit, so this should fail)
        success2 = self.license_manager.track_session("user2")
        self.assertFalse(success2)  # Trial limit is now 1 user
        
        # Try to track third user (should fail for trial license with 1 user limit)
        success3 = self.license_manager.track_session("user3")
        self.assertFalse(success3)  # Trial now has 1 user limit
    
    def test_premium_tier_enterprise_plus(self):
        """Test Enterprise Plus premium tier features."""
        license_config = self.license_manager.generate_license(
            license_type=LicenseType.ENTERPRISE_PLUS,
            customer_id="EP001",
            customer_name="Enterprise Plus Customer",
            company_name="Large Corp",
            email="ep@largecorp.com",
            validity_days=365
        )
        
        self.assertEqual(license_config.license_type, LicenseType.ENTERPRISE_PLUS)
        
        # Check unlimited scans
        scan_limit = next(
            (limit for limit in license_config.usage_limits 
             if limit.limit_type == UsageLimitType.SCANS_PER_MONTH), None
        )
        self.assertIsNotNone(scan_limit)
        if scan_limit:
            self.assertEqual(scan_limit.limit_value, 999999)  # Unlimited
        
        # Check high concurrent user limit
        self.assertEqual(license_config.max_concurrent_users, 50)
        
        # Check all features available
        self.assertGreaterEqual(len(license_config.allowed_features), 16)
        self.assertIn("white_label", license_config.allowed_features)
        
    def test_premium_tier_consultancy(self):
        """Test Consultancy premium tier features."""
        license_config = self.license_manager.generate_license(
            license_type=LicenseType.CONSULTANCY,
            customer_id="CONS001",
            customer_name="Privacy Consultancy",
            company_name="GDPR Experts BV",
            email="contact@gdprexperts.nl",
            validity_days=365
        )
        
        self.assertEqual(license_config.license_type, LicenseType.CONSULTANCY)
        
        # Check 500 scans for client work
        scan_limit = next(
            (limit for limit in license_config.usage_limits 
             if limit.limit_type == UsageLimitType.SCANS_PER_MONTH), None
        )
        self.assertIsNotNone(scan_limit)
        if scan_limit:
            self.assertEqual(scan_limit.limit_value, 500)
        
        # Check 25 concurrent users for team
        self.assertEqual(license_config.max_concurrent_users, 25)
        
        # Check white-label access
        self.assertIn("white_label", license_config.allowed_features)
        
    def test_premium_tier_ai_compliance(self):
        """Test AI Compliance premium tier features."""
        license_config = self.license_manager.generate_license(
            license_type=LicenseType.AI_COMPLIANCE,
            customer_id="AI001",
            customer_name="AI Startup",
            company_name="AI Tech Inc",
            email="ai@techstartup.com",
            validity_days=365
        )
        
        self.assertEqual(license_config.license_type, LicenseType.AI_COMPLIANCE)
        
        # Check unlimited AI scans
        scan_limit = next(
            (limit for limit in license_config.usage_limits 
             if limit.limit_type == UsageLimitType.SCANS_PER_MONTH), None
        )
        self.assertIsNotNone(scan_limit)
        if scan_limit:
            self.assertEqual(scan_limit.limit_value, 999999)  # Unlimited for AI
        
        # Check AI-focused concurrent users
        self.assertEqual(license_config.max_concurrent_users, 20)
        
        # Check AI model scanner access
        self.assertIn("ai_model", license_config.allowed_scanners)


class TestUsageAnalytics(unittest.TestCase):
    """Test suite for usage analytics functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        self.analytics = UsageAnalytics(db_file=self.temp_db.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_event_tracking(self):
        """Test basic event tracking."""
        success = self.analytics.track_event(
            event_type=UsageEventType.SCAN_STARTED,
            user_id="test_user",
            session_id="test_session",
            scanner_type="code",
            success=True
        )
        
        self.assertTrue(success)
    
    def test_event_tracking_with_details(self):
        """Test event tracking with additional details."""
        details = {
            "files_scanned": 10,
            "findings_count": 5
        }
        
        success = self.analytics.track_event(
            event_type=UsageEventType.SCAN_COMPLETED,
            user_id="test_user",
            session_id="test_session",
            scanner_type="code",
            details=details,
            duration_ms=1500,
            success=True
        )
        
        self.assertTrue(success)
    
    def test_failed_event_tracking(self):
        """Test tracking of failed events."""
        success = self.analytics.track_event(
            event_type=UsageEventType.SCAN_FAILED,
            user_id="test_user",
            session_id="test_session",
            scanner_type="database",
            success=False,
            error_message="Connection timeout"
        )
        
        self.assertTrue(success)


class TestLicenseIntegration(unittest.TestCase):
    """Test suite for license integration functionality."""
    
    def test_convenience_functions(self):
        """Test convenience functions work correctly."""
        from services.license_manager import check_license, check_feature
        
        # These should not crash even without a license
        is_valid, message = check_license()
        # Result can be True or False depending on license file presence
        self.assertIsInstance(is_valid, bool)
        self.assertIsInstance(message, str)
        
        # Feature check should return boolean
        has_feature = check_feature("code_scanner")
        self.assertIsInstance(has_feature, bool)


if __name__ == '__main__':
    # Run specific test groups
    print("Running License System Tests...")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestLicenseManager))
    suite.addTests(loader.loadTestsFromTestCase(TestUsageAnalytics))
    suite.addTests(loader.loadTestsFromTestCase(TestLicenseIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total_tests - failures - errors
    
    print(f"\n{'='*60}")
    print(f"LICENSE SYSTEM TEST RESULTS")
    print(f"{'='*60}")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed}")
    print(f"Failed: {failures}")
    print(f"Errors: {errors}")
    print(f"Success Rate: {(passed/total_tests)*100:.1f}%")
    
    if failures == 0 and errors == 0:
        print("✅ ALL TESTS PASSED - PRODUCTION READY")
    else:
        print("❌ TESTS FAILED - NEEDS FIXES")
        
    print(f"{'='*60}")