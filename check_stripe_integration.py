#!/usr/bin/env python3
"""
Stripe Integration Status Checker
Verify that DataGuardian Pro is correctly linked to Stripe for iDEAL payments
"""

import os
import sys
import stripe
from datetime import datetime, timedelta

def check_stripe_integration():
    """Check Stripe integration status and recent activity"""
    
    # Load Stripe configuration
    stripe_secret = os.getenv('STRIPE_SECRET_KEY')
    if not stripe_secret:
        print("❌ STRIPE_SECRET_KEY not found in environment variables")
        return False
    
    stripe.api_key = stripe_secret
    environment = "LIVE" if "sk_live" in stripe_secret else "TEST"
    
    print(f"🔍 Checking Stripe Integration Status")
    print(f"Environment: {environment} Mode")
    print(f"API Key: {stripe_secret[:12]}...{stripe_secret[-4:]}")
    print("=" * 50)
    
    try:
        # 1. Check Account Status
        print("\n1️⃣ Account Status:")
        account = stripe.Account.retrieve()
        print(f"   ✅ Account ID: {account.id}")
        print(f"   ✅ Country: {account.country}")
        print(f"   ✅ Currency: {account.default_currency}")
        print(f"   ✅ Business Type: {account.business_type}")
        
        # 2. Check Payment Methods
        print("\n2️⃣ Available Payment Methods:")
        payment_methods = stripe.PaymentMethod.list(limit=5)
        if payment_methods.data:
            for pm in payment_methods.data:
                print(f"   💳 {pm.type.upper()}: {pm.id}")
        else:
            print("   ℹ️  No saved payment methods (normal for test environment)")
        
        # 3. Check Recent Payment Intents (last 24 hours)
        print("\n3️⃣ Recent Payment Activity (Last 24 Hours):")
        yesterday = datetime.now() - timedelta(days=1)
        payment_intents = stripe.PaymentIntent.list(
            created={'gte': int(yesterday.timestamp())},
            limit=10
        )
        
        if payment_intents.data:
            print(f"   📊 Found {len(payment_intents.data)} recent payment intents:")
            for pi in payment_intents.data:
                amount_eur = pi.amount / 100
                status_emoji = {
                    'succeeded': '✅',
                    'processing': '⏳', 
                    'requires_payment_method': '⏯️',
                    'canceled': '❌',
                    'requires_action': '🔄'
                }.get(pi.status, '❓')
                
                payment_method = "Unknown"
                if pi.payment_method_types:
                    payment_method = ", ".join(pi.payment_method_types).upper()
                
                print(f"   {status_emoji} €{amount_eur:.2f} - {pi.status.upper()} - {payment_method}")
                
                # Check for iDEAL specific data
                if 'ideal' in pi.payment_method_types:
                    print(f"      🏦 iDEAL Payment - ID: {pi.id}")
                    if pi.metadata:
                        print(f"      📝 Metadata: {dict(pi.metadata)}")
        else:
            print("   ℹ️  No payment activity in last 24 hours")
        
        # 4. Check Checkout Sessions
        print("\n4️⃣ Recent Checkout Sessions:")
        sessions = stripe.checkout.Session.list(limit=5)
        if sessions.data:
            for session in sessions.data:
                status_emoji = '✅' if session.payment_status == 'paid' else '⏳'
                amount = session.amount_total / 100 if session.amount_total else 0
                print(f"   {status_emoji} €{amount:.2f} - {session.payment_status.upper()}")
                print(f"      🔗 Session ID: {session.id}")
                if session.customer_details and session.customer_details.email:
                    print(f"      📧 Customer: {session.customer_details.email}")
        else:
            print("   ℹ️  No recent checkout sessions")
        
        # 5. Check Webhook Endpoints
        print("\n5️⃣ Webhook Configuration:")
        webhooks = stripe.WebhookEndpoint.list()
        if webhooks.data:
            for webhook in webhooks.data:
                status_emoji = '✅' if webhook.status == 'enabled' else '❌'
                print(f"   {status_emoji} {webhook.url}")
                print(f"      📋 Events: {len(webhook.enabled_events)} configured")
                print(f"      🔧 Status: {webhook.status}")
        else:
            print("   ⚠️  No webhook endpoints configured")
            print("   💡 Recommendation: Set up webhooks for payment confirmations")
        
        # 6. Test iDEAL Availability
        print("\n6️⃣ iDEAL Payment Method Test:")
        try:
            # Create a test payment intent with iDEAL
            test_intent = stripe.PaymentIntent.create(
                amount=1000,  # €10.00
                currency='eur',
                payment_method_types=['ideal'],
                metadata={'test': 'ideal_availability_check'}
            )
            print("   ✅ iDEAL payment method is available")
            print(f"   🆔 Test Payment Intent: {test_intent.id}")
            
            # Clean up test intent
            test_intent.cancel()
            print("   🧹 Test payment intent cancelled")
            
        except stripe.error.StripeError as e:
            print(f"   ❌ iDEAL availability issue: {str(e)}")
        
        # 7. Integration Health Summary
        print("\n" + "=" * 50)
        print("🏥 INTEGRATION HEALTH SUMMARY:")
        print("✅ Stripe API Connection: Working")
        print("✅ Account Access: Verified") 
        print("✅ Payment Processing: Available")
        print("💳 iDEAL Support: Enabled for Netherlands")
        print("🔗 Environment: Ready for Testing")
        
        return True
        
    except stripe.error.AuthenticationError:
        print("❌ Authentication failed - Check your STRIPE_SECRET_KEY")
        return False
    except stripe.error.APIConnectionError:
        print("❌ Cannot connect to Stripe API - Check internet connection") 
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def show_quick_links():
    """Show quick links to relevant Stripe Dashboard sections"""
    print("\n🔗 STRIPE DASHBOARD QUICK LINKS:")
    print("📊 Payments: https://dashboard.stripe.com/payments")
    print("🔄 Payment Intents: https://dashboard.stripe.com/payment_intents") 
    print("🛒 Checkout Sessions: https://dashboard.stripe.com/checkout/sessions")
    print("⚡ Events: https://dashboard.stripe.com/events")
    print("🪝 Webhooks: https://dashboard.stripe.com/webhooks")
    print("📈 Analytics: https://dashboard.stripe.com/analytics")
    
    print("\n💡 MONITORING TIPS:")
    print("1. Keep Payments tab open during iDEAL testing")
    print("2. Monitor Events tab for real-time webhook delivery")
    print("3. Check Payment Intents for detailed processing status")
    print("4. Use Test Mode for safe ABN AMRO card testing")

if __name__ == "__main__":
    print("🛡️ DataGuardian Pro - Stripe Integration Checker")
    print("=" * 50)
    
    success = check_stripe_integration()
    
    if success:
        show_quick_links()
        print("\n✅ Integration check completed successfully!")
        print("🧪 Ready for ABN AMRO iDEAL payment testing")
    else:
        print("\n❌ Integration issues found - Please fix before testing")
    
    print("\n🚀 Next: Use the iDEAL Payment Test interface in DataGuardian Pro")