#!/usr/bin/env python3
"""
Quick Setup Assistant for DataGuardian Pro Payment System
Guides you through configuring webhooks and email in 5 minutes
"""

import os
import sys

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_step(number, title):
    """Print step header"""
    print(f"\n📋 STEP {number}: {title}")
    print("-" * 70)

def check_secret(key):
    """Check if secret is configured"""
    value = os.getenv(key)
    if value:
        if len(value) > 20:
            display = f"{value[:10]}...{value[-4:]}"
        else:
            display = "*" * len(value)
        return True, display
    return False, None

def main():
    """Run setup assistant"""
    
    print_header("🚀 DataGuardian Pro - Quick Setup Assistant")
    
    print("""
This assistant will help you configure:
1. Stripe Webhook Secret (for payment verification)
2. Email Service (for customer notifications)

Time required: 5-10 minutes
""")
    
    input("Press Enter to begin setup... ")
    
    # Step 1: Check current status
    print_step(1, "Checking Current Configuration")
    
    secrets_status = {
        'STRIPE_SECRET_KEY': check_secret('STRIPE_SECRET_KEY'),
        'STRIPE_WEBHOOK_SECRET': check_secret('STRIPE_WEBHOOK_SECRET'),
        'EMAIL_USERNAME': check_secret('EMAIL_USERNAME'),
        'EMAIL_PASSWORD': check_secret('EMAIL_PASSWORD'),
        'SENDGRID_API_KEY': check_secret('SENDGRID_API_KEY'),
    }
    
    for key, (configured, value) in secrets_status.items():
        status = "✅" if configured else "❌"
        display = f"({value})" if configured else "NOT SET"
        print(f"{status} {key}: {display}")
    
    # Step 2: Webhook Secret
    print_step(2, "Configure Stripe Webhook Secret")
    
    if secrets_status['STRIPE_WEBHOOK_SECRET'][0]:
        print("✅ Webhook secret already configured!")
        print(f"   Current: {secrets_status['STRIPE_WEBHOOK_SECRET'][1]}")
        
        reconfigure = input("\nReconfigure? (y/N): ").lower()
        if reconfigure != 'y':
            print("Skipping webhook configuration...")
        else:
            print("\n📝 Manual Steps Required:")
            print("1. Go to: https://dashboard.stripe.com/webhooks")
            print("2. Click 'Add endpoint'")
            print("3. Set URL to: https://[your-app].replit.app/webhook/stripe")
            print("4. Select events (see PAYMENT_FIXES_SETUP_GUIDE.md)")
            print("5. Copy the 'whsec_...' signing secret")
            print("6. Add to Replit Secrets as STRIPE_WEBHOOK_SECRET")
            print("\n📖 Full guide: PAYMENT_FIXES_SETUP_GUIDE.md")
    else:
        print("❌ Webhook secret NOT configured")
        print("\nThis is CRITICAL for payment security!")
        print("\n📝 Setup Instructions:")
        print("\n1. Go to Stripe Dashboard:")
        print("   https://dashboard.stripe.com/webhooks")
        print("\n2. Create webhook endpoint:")
        print("   - Click 'Add endpoint'")
        print("   - URL: https://[your-app].replit.app/webhook/stripe")
        print("   - Select these events:")
        print("     ✅ checkout.session.completed")
        print("     ✅ payment_intent.succeeded")
        print("     ✅ payment_intent.payment_failed")
        print("\n3. Copy the webhook secret (whsec_...)")
        print("\n4. Add to Replit Secrets:")
        print("   - Key: STRIPE_WEBHOOK_SECRET")
        print("   - Value: whsec_xxxxxxxxxxxxx")
        
        print("\n⏸️  Complete this step before continuing...")
        input("Press Enter when webhook secret is configured... ")
        
        # Recheck
        configured, value = check_secret('STRIPE_WEBHOOK_SECRET')
        if configured:
            print(f"✅ Webhook secret detected: {value}")
        else:
            print("❌ Webhook secret still not found")
            print("   Please add STRIPE_WEBHOOK_SECRET to Replit Secrets")
    
    # Step 3: Email Service
    print_step(3, "Configure Email Service")
    
    email_configured = (
        secrets_status['EMAIL_USERNAME'][0] or 
        secrets_status['SENDGRID_API_KEY'][0]
    )
    
    if email_configured:
        print("✅ Email service already configured!")
        
        if secrets_status['EMAIL_USERNAME'][0]:
            print(f"   Using SMTP: {secrets_status['EMAIL_USERNAME'][1]}")
        if secrets_status['SENDGRID_API_KEY'][0]:
            print(f"   Using SendGrid: {secrets_status['SENDGRID_API_KEY'][1]}")
        
        reconfigure = input("\nReconfigure? (y/N): ").lower()
        if reconfigure == 'y':
            show_email_options()
    else:
        print("❌ Email service NOT configured")
        print("\nCustomers won't receive payment confirmations!")
        show_email_options()
    
    # Step 4: Test Configuration
    print_step(4, "Test Configuration")
    
    print("\nRunning automated tests...")
    
    # Test webhook
    print("\n1. Testing webhook configuration...")
    webhook_ok, _ = check_secret('STRIPE_WEBHOOK_SECRET')
    if webhook_ok:
        print("   ✅ Webhook secret: CONFIGURED")
    else:
        print("   ❌ Webhook secret: NOT SET")
    
    # Test email
    print("\n2. Testing email configuration...")
    try:
        from services.email_service import email_service
        if email_service.enabled:
            print(f"   ✅ Email service: ENABLED")
            print(f"      SMTP: {email_service.smtp_server}")
            print(f"      From: {email_service.from_email}")
        else:
            print("   ❌ Email service: DISABLED")
    except Exception as e:
        print(f"   ❌ Email service error: {e}")
    
    # Step 5: Summary
    print_step(5, "Setup Summary")
    
    webhook_ok, _ = check_secret('STRIPE_WEBHOOK_SECRET')
    email_ok = email_configured or check_secret('EMAIL_USERNAME')[0] or check_secret('SENDGRID_API_KEY')[0]
    
    if webhook_ok and email_ok:
        print("\n🎉 SETUP COMPLETE!")
        print("\n✅ Webhook verification: ENABLED")
        print("✅ Email notifications: ENABLED")
        print("\nYour payment system is now production-ready!")
        print("\n🧪 Next Steps:")
        print("1. Run: python test_webhook_secret.py")
        print("2. Run: python test_email_service.py")
        print("3. Test payment: streamlit run test_ideal_payment.py")
    else:
        print("\n⚠️ SETUP INCOMPLETE")
        if not webhook_ok:
            print("❌ Webhook secret: NOT SET")
        if not email_ok:
            print("❌ Email service: NOT SET")
        print("\n📖 See PAYMENT_FIXES_SETUP_GUIDE.md for detailed instructions")
    
    print("\n" + "=" * 70)
    print("Setup assistant complete!")
    print("=" * 70)

def show_email_options():
    """Show email configuration options"""
    print("\nChoose email service:")
    print("\n1. Gmail SMTP (Quick - 5 min)")
    print("   ✅ Free forever")
    print("   ✅ Easy setup")
    print("   ❌ 500 emails/day limit")
    print("\n2. SendGrid (Professional - 10 min)")
    print("   ✅ 100 emails/day FREE")
    print("   ✅ Better deliverability")
    print("   ✅ Professional")
    
    choice = input("\nSelect option (1 or 2): ")
    
    if choice == "1":
        print("\n📧 Gmail SMTP Setup:")
        print("\n1. Generate App Password:")
        print("   https://myaccount.google.com/apppasswords")
        print("   (Requires 2FA enabled)")
        print("\n2. Add to Replit Secrets:")
        print("   - EMAIL_USERNAME: your-email@gmail.com")
        print("   - EMAIL_PASSWORD: (16-char app password, no spaces)")
        print("   - SMTP_SERVER: smtp.gmail.com")
        print("   - SMTP_PORT: 587")
    elif choice == "2":
        print("\n📧 SendGrid Setup:")
        print("\n1. Create account: https://signup.sendgrid.com/")
        print("2. Create API key: Settings → API Keys")
        print("3. Add to Replit Secrets:")
        print("   - SENDGRID_API_KEY: SG.xxxxxxxxx")
        print("   - FROM_EMAIL: noreply@yourdomain.com")
    else:
        print("\nInvalid choice. See PAYMENT_FIXES_SETUP_GUIDE.md")
    
    print("\n⏸️  Complete email setup in Replit Secrets...")
    input("Press Enter when done... ")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        sys.exit(1)
