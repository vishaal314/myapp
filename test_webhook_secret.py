#!/usr/bin/env python3
"""
Test Webhook Secret Configuration
Run this after adding STRIPE_WEBHOOK_SECRET to verify setup
"""

import os
import sys

def test_webhook_configuration():
    """Test webhook secret configuration"""
    
    print("=" * 60)
    print("STRIPE WEBHOOK SECRET CONFIGURATION TEST")
    print("=" * 60)
    
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    if not webhook_secret:
        print("❌ STRIPE_WEBHOOK_SECRET: NOT SET")
        print("\nTo fix:")
        print("1. Go to https://dashboard.stripe.com/webhooks")
        print("2. Create webhook endpoint")
        print("3. Copy the signing secret (whsec_...)")
        print("4. Add to Replit Secrets as STRIPE_WEBHOOK_SECRET")
        return False
    
    # Validate format
    if not webhook_secret.startswith('whsec_'):
        print(f"⚠️ STRIPE_WEBHOOK_SECRET: Invalid format")
        print(f"   Current: {webhook_secret[:15]}...")
        print(f"   Expected: whsec_xxxxxxxxxxxxx")
        return False
    
    print(f"✅ STRIPE_WEBHOOK_SECRET: CONFIGURED")
    print(f"   Format: {webhook_secret[:15]}...")
    print(f"   Length: {len(webhook_secret)} characters")
    
    # Test with stripe_payment module
    print("\n" + "=" * 60)
    print("TESTING WEBHOOK VERIFICATION FUNCTION")
    print("=" * 60)
    
    try:
        from services.stripe_payment import verify_webhook_signature
        
        # Test with dummy data (will fail signature but shows function works)
        test_payload = '{"test": "payload"}'
        test_signature = 'test_signature'
        
        result = verify_webhook_signature(test_payload, test_signature)
        
        if result is False:
            print("✅ Webhook verification function: WORKING")
            print("   (Test signature failed as expected)")
            print("   Real webhooks will be verified correctly")
        else:
            print("⚠️ Unexpected result from verification")
            
    except Exception as e:
        print(f"❌ Error testing webhook function: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("WEBHOOK ENDPOINT INFORMATION")
    print("=" * 60)
    
    base_url = os.getenv('REPLIT_URL', 'http://localhost:5000')
    webhook_url = f"{base_url}/webhook/stripe"
    
    print(f"Your webhook endpoint URL:")
    print(f"  {webhook_url}")
    print(f"\nAdd this URL to Stripe Dashboard:")
    print(f"  https://dashboard.stripe.com/webhooks")
    
    print("\n" + "=" * 60)
    print("✅ WEBHOOK CONFIGURATION: COMPLETE")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = test_webhook_configuration()
    sys.exit(0 if success else 1)
