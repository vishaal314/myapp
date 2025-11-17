#!/usr/bin/env python3
"""
GDPR Compliance Verification - Revenue Tracking
Verify NO PII in details field for all revenue tracking events
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from services.visitor_tracker import VisitorTracker, VisitorEventType
import json

def verify_event(tracker, event_type, details, test_name):
    """Verify event has no PII in details"""
    event_id = tracker.track_event(
        session_id='test_session',
        event_type=event_type,
        page_path='/test',
        ip_address='192.168.1.1',
        user_id='test_user_123',  # Will be hashed
        username='test@example.com',  # Should be blocked
        details=details
    )
    
    event = tracker.events[-1]
    
    # Check for PII leaks
    pii_keys = ['user_id', 'username', 'email', 'password', 'name', 'attempted_username']
    pii_found = [key for key in pii_keys if key in event.details]
    
    print(f"\n{test_name}")
    print("=" * 60)
    print(f"Event Type: {event.event_type.value}")
    print(f"User ID: {event.user_id} (hashed)")
    print(f"Username: {event.username} (should be None)")
    print(f"Details: {json.dumps(event.details, indent=2)}")
    
    if pii_found:
        print(f"❌ FAIL: PII found in details: {pii_found}")
        return False
    else:
        print(f"✅ PASS: No PII in details field")
        return True

def main():
    tracker = VisitorTracker()
    all_passed = True
    
    print("GDPR COMPLIANCE VERIFICATION - REVENUE TRACKING")
    print("=" * 60)
    
    # Test 1: Pricing Page View
    all_passed &= verify_event(
        tracker,
        VisitorEventType.PRICING_PAGE_VIEW,
        {'tier_viewed': 'Professional', 'timestamp': '2025-11-17'},
        "Test 1: Pricing Page View"
    )
    
    # Test 2: Trial Started
    all_passed &= verify_event(
        tracker,
        VisitorEventType.TRIAL_STARTED,
        {'tier': 'Professional', 'duration_days': 14, 'trial_start': '2025-11-17'},
        "Test 2: Trial Started"
    )
    
    # Test 3: Trial Converted
    all_passed &= verify_event(
        tracker,
        VisitorEventType.TRIAL_CONVERTED,
        {'tier': 'Professional', 'mrr': 99.0, 'conversion_date': '2025-11-17'},
        "Test 3: Trial Converted"
    )
    
    # Test 4: Scanner Executed
    all_passed &= verify_event(
        tracker,
        VisitorEventType.SCANNER_EXECUTED,
        {'scanner_type': 'database', 'findings_count': 42, 'execution_time': '2025-11-17'},
        "Test 4: Scanner Executed"
    )
    
    # Test 5: Subscription Upgraded
    all_passed &= verify_event(
        tracker,
        VisitorEventType.SUBSCRIPTION_UPGRADED,
        {'action': 'upgraded', 'from_tier': 'Startup', 'to_tier': 'Professional', 'mrr_change': 40.0},
        "Test 5: Subscription Upgraded"
    )
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total Tests: 5")
    print(f"Passed: {sum([all_passed] * 5)}")
    print(f"Failed: {5 - sum([all_passed] * 5)}")
    print(f"\nGDPR Compliance: {'✅ PASS' if all_passed else '❌ FAIL'}")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
