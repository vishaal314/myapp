"""
Comprehensive Unit Tests for Visitor Tracking System
Tests both functional and non-functional scenarios including GDPR compliance
"""

import unittest
import hashlib
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.visitor_tracker import VisitorTracker, VisitorEventType
from services.auth_tracker import (
    authenticate_with_tracking,
    create_user_with_tracking,
    track_logout,
    track_page_view
)


class TestVisitorTrackerFunctional(unittest.TestCase):
    """Functional tests for visitor tracking system"""
    
    def setUp(self):
        """Setup test environment"""
        self.tracker = VisitorTracker()
        self.test_session_id = "test_session_123"
        self.test_ip = "192.168.1.100"
    
    def test_track_page_view_anonymous(self):
        """Test anonymous page view tracking"""
        event_id = self.tracker.track_event(
            session_id=self.test_session_id,
            event_type=VisitorEventType.PAGE_VIEW,
            page_path="/dashboard",
            ip_address=self.test_ip,
            referrer="https://google.com"
        )
        
        self.assertIsNotNone(event_id)
        self.assertEqual(len(self.tracker.events), 1)
        
        event = self.tracker.events[0]
        self.assertEqual(event.event_type, VisitorEventType.PAGE_VIEW)
        self.assertEqual(event.page_path, "/dashboard")
        self.assertEqual(event.referrer, "https://google.com")
        self.assertIsNone(event.user_id)
        self.assertIsNone(event.username)
    
    def test_track_login_success(self):
        """Test successful login tracking"""
        test_user_id = "user123"
        
        event_id = self.tracker.track_event(
            session_id=self.test_session_id,
            event_type=VisitorEventType.LOGIN_SUCCESS,
            page_path="/login",
            ip_address=self.test_ip,
            user_id=test_user_id,
            details={"method": "password", "role": "user"},
            success=True
        )
        
        self.assertIsNotNone(event_id)
        event = self.tracker.events[0]
        
        # Verify user_id is hashed (unconditional hashing)
        self.assertNotEqual(event.user_id, test_user_id)
        self.assertEqual(len(event.user_id), 16)  # Truncated SHA-256
        
        # Verify username is always None (GDPR enforcement)
        self.assertIsNone(event.username)
        
        # Verify details contains only metadata
        self.assertEqual(event.details["method"], "password")
        self.assertEqual(event.details["role"], "user")
    
    def test_track_login_failure(self):
        """Test failed login tracking"""
        event_id = self.tracker.track_event(
            session_id=self.test_session_id,
            event_type=VisitorEventType.LOGIN_FAILURE,
            page_path="/login",
            ip_address=self.test_ip,
            details={"method": "password"},
            success=False,
            error_message="Invalid credentials"
        )
        
        self.assertIsNotNone(event_id)
        event = self.tracker.events[0]
        
        self.assertEqual(event.event_type, VisitorEventType.LOGIN_FAILURE)
        self.assertFalse(event.success)
        self.assertEqual(event.error_message, "Invalid credentials")
        self.assertIsNone(event.user_id)
        self.assertIsNone(event.username)
    
    def test_track_registration_success(self):
        """Test user registration tracking"""
        event_id = self.tracker.track_event(
            session_id=self.test_session_id,
            event_type=VisitorEventType.REGISTRATION_SUCCESS,
            page_path="/register",
            ip_address=self.test_ip,
            details={"role": "analyst", "method": "signup_form"},
            success=True
        )
        
        self.assertIsNotNone(event_id)
        event = self.tracker.events[0]
        
        self.assertEqual(event.event_type, VisitorEventType.REGISTRATION_SUCCESS)
        self.assertTrue(event.success)
        self.assertEqual(event.details["role"], "analyst")
        self.assertIsNone(event.user_id)
        self.assertIsNone(event.username)
    
    def test_track_logout(self):
        """Test user logout tracking"""
        test_user_id = "user456"
        
        event_id = self.tracker.track_event(
            session_id=self.test_session_id,
            event_type=VisitorEventType.LOGOUT,
            page_path="/logout",
            ip_address=self.test_ip,
            user_id=test_user_id,
            details={"method": "manual_logout"},
            success=True
        )
        
        self.assertIsNotNone(event_id)
        event = self.tracker.events[0]
        
        # Verify user_id is hashed
        self.assertNotEqual(event.user_id, test_user_id)
        self.assertEqual(len(event.user_id), 16)
        
        # Verify username is None
        self.assertIsNone(event.username)
    
    def test_multiple_events_tracking(self):
        """Test tracking multiple events in sequence"""
        # Track 5 different events
        for i in range(5):
            self.tracker.track_event(
                session_id=f"session_{i}",
                event_type=VisitorEventType.PAGE_VIEW,
                page_path=f"/page_{i}",
                ip_address=self.test_ip
            )
        
        self.assertEqual(len(self.tracker.events), 5)
        
        # Verify all events have unique IDs
        event_ids = [e.event_id for e in self.tracker.events]
        self.assertEqual(len(event_ids), len(set(event_ids)))


class TestVisitorTrackerGDPRCompliance(unittest.TestCase):
    """Non-functional tests for GDPR compliance"""
    
    def setUp(self):
        """Setup test environment"""
        self.tracker = VisitorTracker()
        self.test_session_id = "test_session_gdpr"
        self.test_ip = "192.168.1.100"
    
    def test_username_always_none(self):
        """Test that username is ALWAYS None regardless of input"""
        # Try to pass a username (should be blocked by backend)
        event_id = self.tracker.track_event(
            session_id=self.test_session_id,
            event_type=VisitorEventType.LOGIN_SUCCESS,
            page_path="/login",
            ip_address=self.test_ip,
            user_id="user123",
            username="john@example.com",  # Attempt to pass username
            details={"method": "password"}
        )
        
        event = self.tracker.events[0]
        
        # CRITICAL: Username must ALWAYS be None (GDPR enforcement)
        self.assertIsNone(event.username, "Username must ALWAYS be None for GDPR compliance")
    
    def test_user_id_unconditional_hashing(self):
        """Test that user_id is ALWAYS hashed, no exceptions"""
        test_cases = [
            "user123",  # Regular user ID
            "1234567890123456",  # 16-digit numeric
            "abcdef1234567890",  # 16-char hex (could bypass old logic)
            "12345",  # Short ID
        ]
        
        for test_user_id in test_cases:
            self.tracker.events = []  # Clear events
            
            event_id = self.tracker.track_event(
                session_id=self.test_session_id,
                event_type=VisitorEventType.LOGIN_SUCCESS,
                page_path="/login",
                ip_address=self.test_ip,
                user_id=test_user_id
            )
            
            event = self.tracker.events[0]
            
            # CRITICAL: user_id must be hashed (16-char hex)
            self.assertIsNotNone(event.user_id)
            self.assertEqual(len(event.user_id), 16, f"User ID must be 16-char hash for {test_user_id}")
            self.assertNotEqual(event.user_id, test_user_id, f"Raw user_id must not be stored: {test_user_id}")
            
            # Verify it's a valid hex string
            try:
                int(event.user_id, 16)
            except ValueError:
                self.fail(f"user_id must be valid hex string: {event.user_id}")
    
    def test_details_field_sanitization(self):
        """Test that PII fields are blocked from details"""
        pii_fields = {
            "username": "john@example.com",
            "email": "user@example.com",
            "attempted_username": "admin",
            "user_email": "test@test.com",
            "name": "John Doe",
            "password": "secret123"
        }
        
        # Add some safe fields
        safe_fields = {
            "method": "password",
            "role": "user",
            "timestamp": "2025-11-17T22:00:00"
        }
        
        all_fields = {**pii_fields, **safe_fields}
        
        event_id = self.tracker.track_event(
            session_id=self.test_session_id,
            event_type=VisitorEventType.LOGIN_SUCCESS,
            page_path="/login",
            ip_address=self.test_ip,
            details=all_fields
        )
        
        event = self.tracker.events[0]
        
        # CRITICAL: PII fields must be blocked
        for pii_key in pii_fields.keys():
            self.assertNotIn(pii_key, event.details, f"PII field '{pii_key}' must be blocked")
        
        # Safe fields should be present
        for safe_key in safe_fields.keys():
            self.assertIn(safe_key, event.details, f"Safe field '{safe_key}' should be allowed")
    
    def test_ip_anonymization(self):
        """Test that IP addresses are anonymized"""
        test_ips = [
            ("192.168.1.100", True),   # IPv4
            ("2001:db8::1", True),     # IPv6
            (None, False),             # No IP
        ]
        
        for ip, should_anonymize in test_ips:
            self.tracker.events = []  # Clear events
            
            event_id = self.tracker.track_event(
                session_id=self.test_session_id,
                event_type=VisitorEventType.PAGE_VIEW,
                page_path="/",
                ip_address=ip
            )
            
            event = self.tracker.events[0]
            
            if should_anonymize:
                # IP should be hashed (16-char hex or "unknown")
                self.assertIsNotNone(event.anonymized_ip)
                self.assertNotEqual(event.anonymized_ip, ip, f"Raw IP must not be stored: {ip}")
                
                if event.anonymized_ip != "unknown":
                    self.assertEqual(len(event.anonymized_ip), 16, "Anonymized IP must be 16-char hash")
            else:
                self.assertEqual(event.anonymized_ip, "unknown")
    
    def test_no_pii_in_any_field(self):
        """Comprehensive test: NO PII should exist anywhere in event"""
        # Attempt to inject PII everywhere
        event_id = self.tracker.track_event(
            session_id=self.test_session_id,
            event_type=VisitorEventType.REGISTRATION_SUCCESS,
            page_path="/register",
            ip_address="192.168.1.100",
            user_id="user_john@example.com",  # Attempt raw email as user_id
            username="john_doe_admin",  # Attempt username
            details={
                "username": "john@example.com",
                "email": "john@example.com",
                "role": "admin"  # Safe field
            }
        )
        
        event = self.tracker.events[0]
        
        # Convert event to dict for comprehensive check
        event_dict = {
            "user_id": event.user_id,
            "username": event.username,
            "details": json.dumps(event.details) if event.details else "{}"
        }
        
        # Check for common PII patterns
        pii_patterns = [
            "@example.com",
            "john",
            "doe",
            "admin" # Should not appear except in safe 'role' field
        ]
        
        # Username must be None
        self.assertIsNone(event.username, "Username must be None")
        
        # User_id must be hashed (not contain email patterns)
        self.assertNotIn("@", event.user_id or "", "User_id must not contain email")
        
        # Details must not contain PII
        details_str = json.dumps(event.details)
        self.assertNotIn("username", details_str.lower(), "Details must not contain 'username' key")
        self.assertNotIn("email", details_str, "Details must not contain 'email' key")


class TestVisitorTrackerPerformance(unittest.TestCase):
    """Non-functional tests for performance and scalability"""
    
    def setUp(self):
        """Setup test environment"""
        self.tracker = VisitorTracker()
    
    def test_in_memory_limit_enforcement(self):
        """Test that in-memory storage respects 10,000 event limit"""
        # Track 10,500 events
        for i in range(10500):
            self.tracker.track_event(
                session_id=f"session_{i}",
                event_type=VisitorEventType.PAGE_VIEW,
                page_path=f"/page_{i}",
                ip_address="192.168.1.1"
            )
        
        # Should be limited to 10,000 events
        self.assertEqual(len(self.tracker.events), 10000, "In-memory limit must be 10,000 events")
    
    def test_hashing_performance(self):
        """Test that SHA-256 hashing is fast"""
        import time
        
        start_time = time.time()
        
        # Hash 1000 user IDs
        for i in range(1000):
            self.tracker.track_event(
                session_id=f"session_{i}",
                event_type=VisitorEventType.LOGIN_SUCCESS,
                page_path="/login",
                ip_address="192.168.1.1",
                user_id=f"user_{i}"
            )
        
        elapsed = time.time() - start_time
        
        # Should complete in under 2 seconds (very generous)
        self.assertLess(elapsed, 2.0, "Hashing 1000 events should take <2 seconds")
    
    def test_event_uniqueness(self):
        """Test that all events have unique IDs"""
        # Create 100 events rapidly
        for i in range(100):
            self.tracker.track_event(
                session_id=f"session_{i}",
                event_type=VisitorEventType.PAGE_VIEW,
                page_path="/",
                ip_address="192.168.1.1"
            )
        
        event_ids = [e.event_id for e in self.tracker.events]
        
        # All IDs must be unique
        self.assertEqual(len(event_ids), len(set(event_ids)), "All event IDs must be unique")


class TestAuthTrackerIntegration(unittest.TestCase):
    """Integration tests for auth_tracker wrapper functions"""
    
    @patch('services.auth_tracker.get_visitor_tracker')
    @patch('services.auth_tracker.get_session_id')
    def test_track_page_view_integration(self, mock_session, mock_tracker):
        """Test page view tracking wrapper"""
        mock_tracker_instance = Mock()
        mock_tracker.return_value = mock_tracker_instance
        mock_session.return_value = "test_session"
        
        track_page_view("/dashboard", "https://google.com")
        
        # Verify tracker was called
        mock_tracker_instance.track_event.assert_called_once()
        call_args = mock_tracker_instance.track_event.call_args
        
        self.assertEqual(call_args[1]['event_type'], VisitorEventType.PAGE_VIEW)
        self.assertEqual(call_args[1]['page_path'], "/dashboard")
        self.assertEqual(call_args[1]['referrer'], "https://google.com")
    
    @patch('services.auth_tracker.get_visitor_tracker')
    @patch('services.auth_tracker.get_session_id')
    def test_track_logout_gdpr_compliance(self, mock_session, mock_tracker):
        """Test logout tracking enforces GDPR compliance"""
        mock_tracker_instance = Mock()
        mock_tracker.return_value = mock_tracker_instance
        mock_session.return_value = "test_session"
        
        # Call track_logout with user_id
        track_logout("user123", "john@example.com")
        
        # Verify tracker was called
        mock_tracker_instance.track_event.assert_called_once()
        call_args = mock_tracker_instance.track_event.call_args
        
        # CRITICAL: username must be None
        self.assertIsNone(call_args[1]['username'], "Logout must not store username")
        
        # CRITICAL: user_id must be hashed
        stored_user_id = call_args[1]['user_id']
        self.assertIsNotNone(stored_user_id)
        self.assertEqual(len(stored_user_id), 16, "User_id must be 16-char hash")
        self.assertNotEqual(stored_user_id, "user123", "Raw user_id must not be passed")


class TestErrorHandling(unittest.TestCase):
    """Non-functional tests for error handling and resilience"""
    
    def setUp(self):
        """Setup test environment"""
        self.tracker = VisitorTracker()
    
    def test_handle_none_session_id(self):
        """Test graceful handling of None session_id"""
        # Should not crash
        try:
            event_id = self.tracker.track_event(
                session_id=None,
                event_type=VisitorEventType.PAGE_VIEW,
                page_path="/",
                ip_address="192.168.1.1"
            )
            # If it doesn't crash, that's acceptable
        except Exception as e:
            self.fail(f"Should handle None session_id gracefully: {e}")
    
    def test_handle_invalid_details(self):
        """Test handling of various details field inputs"""
        test_cases = [
            None,           # None details
            {},             # Empty dict
            {"key": None},  # Dict with None value
        ]
        
        for details in test_cases:
            try:
                event_id = self.tracker.track_event(
                    session_id="test_session",
                    event_type=VisitorEventType.PAGE_VIEW,
                    page_path="/",
                    ip_address="192.168.1.1",
                    details=details
                )
                # Should not crash
            except Exception as e:
                self.fail(f"Should handle details={details} gracefully: {e}")
    
    def test_handle_empty_strings(self):
        """Test handling of empty string inputs"""
        event_id = self.tracker.track_event(
            session_id="test_session",
            event_type=VisitorEventType.PAGE_VIEW,
            page_path="",  # Empty page path
            ip_address="",  # Empty IP
            user_agent="",  # Empty user agent
            referrer=""     # Empty referrer
        )
        
        self.assertIsNotNone(event_id)
        event = self.tracker.events[0]
        
        # Empty strings should be stored as-is (not None)
        self.assertEqual(event.page_path, "")
        self.assertEqual(event.user_agent, "")
        self.assertEqual(event.referrer, "")


def generate_test_report():
    """Generate comprehensive test report"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestVisitorTrackerFunctional))
    suite.addTests(loader.loadTestsFromTestCase(TestVisitorTrackerGDPRCompliance))
    suite.addTests(loader.loadTestsFromTestCase(TestVisitorTrackerPerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestAuthTrackerIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    print("=" * 80)
    print("VISITOR TRACKING SYSTEM - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print()
    
    result = generate_test_report()
    
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("=" * 80)
    
    sys.exit(0 if result.wasSuccessful() else 1)
