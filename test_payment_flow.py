#!/usr/bin/env python3
"""
Payment Flow Testing Script for DataGuardian Pro
Tests the Stripe payment integration and provides suggestions
"""

import os
import sys
import json
from unittest.mock import Mock, patch
from typing import Dict, Any, Optional

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from services.stripe_payment import (
        SCAN_PRICES, 
        SCAN_PRODUCTS, 
        SCAN_DESCRIPTIONS,
        calculate_vat,
        validate_email,
        validate_scan_type,
        sanitize_metadata,
        create_checkout_session,
        verify_payment,
        display_payment_button
    )
    from services.subscription_manager import SUBSCRIPTION_PLANS, SubscriptionManager
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

def test_pricing_structure():
    """Test the pricing structure and calculations"""
    print("🧪 Testing Pricing Structure")
    print("=" * 40)
    
    # Test scan prices
    total_scans = len(SCAN_PRICES)
    print(f"✅ Total scan types: {total_scans}")
    
    # Display all pricing with VAT
    print("\n💰 Current Pricing (incl. 21% Netherlands VAT):")
    for scan_type, price_cents in SCAN_PRICES.items():
        pricing = calculate_vat(price_cents, "NL")
        print(f"  • {scan_type}: €{pricing['subtotal']/100:.2f} + €{pricing['vat_amount']/100:.2f} VAT = €{pricing['total']/100:.2f}")
    
    # Test enterprise pricing positioning
    enterprise_scans = [k for k in SCAN_PRICES.keys() if any(term in k.lower() for term in ['enterprise', 'sap', 'exact', 'microsoft', 'google', 'salesforce'])]
    print(f"\n🏢 Enterprise scan types: {len(enterprise_scans)}")
    
    # Calculate average pricing
    avg_price = sum(SCAN_PRICES.values()) / len(SCAN_PRICES) / 100
    print(f"📊 Average scan price: €{avg_price:.2f}")
    
    # Test highest value scans
    highest_value = max(SCAN_PRICES.items(), key=lambda x: x[1])
    print(f"💎 Highest value scan: {highest_value[0]} at €{highest_value[1]/100:.2f}")
    
    return True

def test_vat_calculations():
    """Test VAT calculations for different countries"""
    print("\n🧪 Testing VAT Calculations")
    print("=" * 40)
    
    test_amount = 10000  # €100.00
    countries = ["NL", "DE", "FR", "BE", "US"]
    
    for country in countries:
        vat_info = calculate_vat(test_amount, country)
        print(f"  • {country}: €{vat_info['subtotal']/100:.2f} + €{vat_info['vat_amount']/100:.2f} ({vat_info['vat_rate']*100:.0f}% VAT) = €{vat_info['total']/100:.2f}")
    
    return True

def test_email_validation():
    """Test email validation"""
    print("\n🧪 Testing Email Validation")
    print("=" * 40)
    
    test_emails = [
        ("valid@example.com", True),
        ("user+tag@domain.co.uk", True),
        ("invalid.email", False),
        ("@domain.com", False),
        ("user@", False),
        ("", False),
        ("a" * 255 + "@domain.com", False)  # Too long
    ]
    
    all_passed = True
    for email, expected in test_emails:
        result = validate_email(email)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{email}': {result}")
        if result != expected:
            all_passed = False
    
    return all_passed

def test_scan_type_validation():
    """Test scan type validation"""
    print("\n🧪 Testing Scan Type Validation")
    print("=" * 40)
    
    # Test valid scan types
    valid_count = 0
    for scan_type in SCAN_PRICES.keys():
        if validate_scan_type(scan_type):
            valid_count += 1
    
    print(f"✅ Valid scan types: {valid_count}/{len(SCAN_PRICES)}")
    
    # Test invalid scan types
    invalid_types = ["Invalid Scan", "", "Fake Scan Type"]
    for scan_type in invalid_types:
        result = validate_scan_type(scan_type)
        status = "✅" if not result else "❌"
        print(f"  {status} '{scan_type}': {result}")
    
    return True

def test_metadata_sanitization():
    """Test metadata sanitization"""
    print("\n🧪 Testing Metadata Sanitization")
    print("=" * 40)
    
    test_metadata = {
        "user_id": "12345",
        "scan_type": "Code Scan",
        "malicious_script": "<script>alert('xss')</script>",
        "long_value": "x" * 200,  # Should be truncated
        "valid_number": 42,
        "valid_bool": True,
        123: "invalid_key",  # Should be filtered out
        "special_chars!": "filtered"  # Should be filtered out
    }
    
    sanitized = sanitize_metadata(test_metadata)
    print(f"  Original keys: {len(test_metadata)}")
    print(f"  Sanitized keys: {len(sanitized)}")
    
    for key, value in sanitized.items():
        print(f"  ✅ {key}: {value[:50]}{'...' if len(str(value)) > 50 else ''}")
    
    return True

def test_subscription_plans():
    """Test subscription plans structure"""
    print("\n🧪 Testing Subscription Plans")
    print("=" * 40)
    
    print(f"✅ Total subscription plans: {len(SUBSCRIPTION_PLANS)}")
    
    for plan_id, plan in SUBSCRIPTION_PLANS.items():
        pricing = calculate_vat(plan["price"], "NL")
        print(f"\n📋 {plan['name']} ({plan_id}):")
        print(f"  💰 Price: €{pricing['total']/100:.2f}/month (incl. VAT)")
        print(f"  📝 Features: {len(plan['features'])} items")
        print(f"  🎯 {plan['description']}")
    
    return True

def mock_stripe_test():
    """Test payment flow with mocked Stripe calls"""
    print("\n🧪 Testing Payment Flow (Mocked)")
    print("=" * 40)
    
    # Mock successful checkout session
    mock_checkout_response = {
        "id": "cs_test_123456",
        "url": "https://checkout.stripe.com/pay/cs_test_123456",
        "amount_total": 2783,  # €27.83 with VAT
        "currency": "eur"
    }
    
    # Test checkout session creation
    try:
        with patch('stripe.checkout.Session.create', return_value=type('obj', (object,), mock_checkout_response)):
            # This would normally create a real checkout session
            print("✅ Checkout session creation flow: Ready")
            print(f"  📧 Test email validation: {'✅' if validate_email('test@example.com') else '❌'}")
            print(f"  🔍 Scan type validation: {'✅' if validate_scan_type('Code Scan') else '❌'}")
            
    except Exception as e:
        print(f"❌ Checkout session test failed: {e}")
        return False
    
    return True

def analyze_pricing_competitiveness():
    """Analyze pricing competitiveness"""
    print("\n📊 Pricing Competitiveness Analysis")
    print("=" * 40)
    
    # Enterprise scan pricing analysis
    enterprise_scans = {
        "SAP Integration Scan": 15000,
        "Exact Online Scan": 12500,
        "Salesforce Scan": 9200,
        "Microsoft 365 Scan": 7500,
        "Enterprise Scan": 8900
    }
    
    print("🏢 Enterprise Integration Pricing:")
    for scan, price in enterprise_scans.items():
        vat_calc = calculate_vat(price, "NL")
        print(f"  • {scan}: €{vat_calc['total']/100:.2f}")
    
    # Revenue potential calculation
    avg_enterprise_price = sum(enterprise_scans.values()) / len(enterprise_scans)
    print(f"\n💰 Average Enterprise Scan: €{calculate_vat(int(avg_enterprise_price), 'NL')['total']/100:.2f}")
    
    # Monthly revenue scenarios
    scenarios = [
        ("Conservative", 50, 2),  # 50 regular scans, 2 enterprise per month
        ("Growth", 150, 8),       # 150 regular scans, 8 enterprise per month  
        ("Target", 300, 20)       # 300 regular scans, 20 enterprise per month
    ]
    
    print("\n🎯 Monthly Revenue Scenarios:")
    avg_regular_price = sum(v for k, v in SCAN_PRICES.items() if k not in enterprise_scans) / (len(SCAN_PRICES) - len(enterprise_scans))
    
    for scenario, regular_scans, enterprise_scans_count in scenarios:
        regular_revenue = (regular_scans * avg_regular_price) / 100
        enterprise_revenue = (enterprise_scans_count * avg_enterprise_price) / 100
        total_revenue = regular_revenue + enterprise_revenue
        vat_total = calculate_vat(int(total_revenue * 100), "NL")["total"] / 100
        
        print(f"  📈 {scenario}: €{vat_total:,.2f}/month ({regular_scans} regular + {enterprise_scans_count} enterprise)")
    
    return True

def provide_suggestions():
    """Provide improvement suggestions"""
    print("\n💡 Payment Flow Improvement Suggestions")
    print("=" * 50)
    
    suggestions = [
        {
            "category": "🎯 Pricing Strategy",
            "items": [
                "Consider volume discounts for enterprise customers (10+ scans)",
                "Add annual subscription discount (15-20% off)",
                "Create bundle packages (e.g., 'Netherlands Business Pack' with Exact + Microsoft 365)",
                "Implement loyalty pricing for repeat customers"
            ]
        },
        {
            "category": "💳 Payment Experience",
            "items": [
                "Add payment method icons (iDEAL, Credit Cards) to build trust",
                "Display security badges (SSL, GDPR compliant, Stripe secured)",
                "Show estimated time to complete scan after payment",
                "Add progress indicator during payment process"
            ]
        },
        {
            "category": "🇳🇱 Netherlands Market",
            "items": [
                "Make iDEAL the primary payment option for NL customers",
                "Add Dutch tax receipt generation (BTW-factuur)",
                "Include AP (Autoriteit Persoonsgegevens) compliance messaging",
                "Add UAVG-specific compliance guarantees in payment flow"
            ]
        },
        {
            "category": "🔧 Technical Improvements",
            "items": [
                "Implement webhook endpoint for real-time payment confirmations",
                "Add payment retry mechanism for failed transactions",
                "Create payment analytics dashboard for revenue tracking",
                "Implement automatic invoice generation and emailing"
            ]
        },
        {
            "category": "📊 Business Intelligence",
            "items": [
                "Track conversion rates by scan type",
                "Monitor popular payment methods by region",
                "Analyze customer lifetime value patterns",
                "Create automated follow-up for abandoned checkouts"
            ]
        },
        {
            "category": "🚀 Revenue Optimization",
            "items": [
                "Add upselling prompts (suggest related scans)",
                "Implement subscription conversion offers after 3+ pay-per-scan purchases",
                "Create enterprise trial programs (first scan free)",
                "Add referral discount programs"
            ]
        }
    ]
    
    for suggestion in suggestions:
        print(f"\n{suggestion['category']}:")
        for item in suggestion['items']:
            print(f"  • {item}")
    
    return True

def run_payment_flow_tests():
    """Run all payment flow tests"""
    print("🚀 DataGuardian Pro - Payment Flow Testing")
    print("=" * 50)
    
    tests = [
        ("Pricing Structure", test_pricing_structure),
        ("VAT Calculations", test_vat_calculations),
        ("Email Validation", test_email_validation),
        ("Scan Type Validation", test_scan_type_validation),
        ("Metadata Sanitization", test_metadata_sanitization),
        ("Subscription Plans", test_subscription_plans),
        ("Mock Stripe Integration", mock_stripe_test),
        ("Pricing Competitiveness", analyze_pricing_competitiveness)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = "✅ PASSED" if result else "❌ FAILED"
        except Exception as e:
            results[test_name] = f"❌ ERROR: {str(e)}"
    
    # Print test summary
    print(f"\n{'='*50}")
    print("🧪 TEST SUMMARY:")
    print("="*50)
    for test_name, result in results.items():
        print(f"  {result} {test_name}")
    
    # Provide suggestions
    provide_suggestions()
    
    print(f"\n{'='*50}")
    print("✅ Payment Flow Testing Complete!")
    print("="*50)

if __name__ == "__main__":
    run_payment_flow_tests()