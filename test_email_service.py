#!/usr/bin/env python3
"""
Email Service Configuration Test
Tests SMTP/SendGrid/Resend email setup
"""

import os
import sys

def test_email_configuration():
    """Test email service configuration"""
    
    print("=" * 70)
    print("EMAIL SERVICE CONFIGURATION TEST")
    print("=" * 70)
    
    # Check for different email service configurations
    email_username = os.getenv('EMAIL_USERNAME') or os.getenv('SMTP_USERNAME')
    email_password = os.getenv('EMAIL_PASSWORD') or os.getenv('SMTP_PASSWORD')
    sendgrid_key = os.getenv('SENDGRID_API_KEY')
    resend_key = os.getenv('RESEND_API_KEY')
    
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = os.getenv('SMTP_PORT', '587')
    from_email = os.getenv('FROM_EMAIL')
    
    configured_services = []
    
    print("\n1. CHECKING SMTP CONFIGURATION")
    print("-" * 70)
    
    if email_username and email_password:
        print(f"✅ SMTP Credentials: CONFIGURED")
        print(f"   Username: {email_username}")
        print(f"   Password: {'*' * 10}{email_password[-4:] if len(email_password) > 4 else '****'}")
        print(f"   Server: {smtp_server}")
        print(f"   Port: {smtp_port}")
        configured_services.append('SMTP')
    else:
        print(f"❌ SMTP Credentials: NOT CONFIGURED")
        if not email_username:
            print(f"   Missing: EMAIL_USERNAME or SMTP_USERNAME")
        if not email_password:
            print(f"   Missing: EMAIL_PASSWORD or SMTP_PASSWORD")
    
    print("\n2. CHECKING SENDGRID CONFIGURATION")
    print("-" * 70)
    
    if sendgrid_key:
        print(f"✅ SendGrid API Key: CONFIGURED")
        print(f"   Key: {sendgrid_key[:15]}...{sendgrid_key[-4:]}")
        configured_services.append('SendGrid')
    else:
        print(f"❌ SendGrid API Key: NOT CONFIGURED")
        print(f"   Missing: SENDGRID_API_KEY")
    
    print("\n3. CHECKING RESEND CONFIGURATION")
    print("-" * 70)
    
    if resend_key:
        print(f"✅ Resend API Key: CONFIGURED")
        print(f"   Key: {resend_key[:15]}...{resend_key[-4:]}")
        configured_services.append('Resend')
    else:
        print(f"❌ Resend API Key: NOT CONFIGURED")
        print(f"   Missing: RESEND_API_KEY")
    
    print("\n4. CHECKING SENDER CONFIGURATION")
    print("-" * 70)
    
    if from_email:
        print(f"✅ FROM_EMAIL: {from_email}")
    else:
        print(f"⚠️ FROM_EMAIL: NOT SET (using default)")
        print(f"   Default: billing@dataguardian.pro")
    
    # Summary
    print("\n" + "=" * 70)
    print("CONFIGURATION SUMMARY")
    print("=" * 70)
    
    if configured_services:
        print(f"\n✅ Email Services Configured: {', '.join(configured_services)}")
        
        # Test the email service
        print("\n5. TESTING EMAIL SERVICE")
        print("-" * 70)
        
        try:
            from services.email_service import email_service
            
            if email_service.enabled:
                print("✅ Email Service: ENABLED")
                print(f"   SMTP Server: {email_service.smtp_server}")
                print(f"   SMTP Port: {email_service.smtp_port}")
                print(f"   From Email: {email_service.from_email}")
                
                # Test email configuration
                print("\n6. TESTING SMTP CONNECTION (Optional)")
                print("-" * 70)
                
                if email_username and email_password:
                    import smtplib
                    
                    try:
                        print(f"Connecting to {smtp_server}:{smtp_port}...")
                        server = smtplib.SMTP(smtp_server, int(smtp_port))
                        server.starttls()
                        print("✅ TLS connection established")
                        
                        print(f"Authenticating as {email_username}...")
                        server.login(email_username, email_password)
                        print("✅ Authentication successful")
                        
                        server.quit()
                        print("✅ SMTP connection test: PASSED")
                        
                        print("\n" + "=" * 70)
                        print("✅ EMAIL SERVICE: FULLY OPERATIONAL")
                        print("=" * 70)
                        print("\nYou can now:")
                        print("1. Send payment confirmations")
                        print("2. Deliver invoices via email")
                        print("3. Send subscription notifications")
                        
                        return True
                        
                    except smtplib.SMTPAuthenticationError:
                        print("❌ SMTP Authentication failed")
                        print("\nPossible issues:")
                        print("- Wrong password (use App Password for Gmail)")
                        print("- 2FA not enabled (required for Gmail App Passwords)")
                        print("- Account locked/suspended")
                        return False
                        
                    except Exception as e:
                        print(f"❌ SMTP connection failed: {e}")
                        return False
                else:
                    print("ℹ️ SMTP credentials not set, skipping connection test")
                    return True
                    
            else:
                print("❌ Email Service: DISABLED")
                print("   Reason: No credentials configured")
                return False
                
        except ImportError as e:
            print(f"❌ Cannot import email service: {e}")
            return False
    else:
        print("\n❌ No email services configured")
        print("\nTo configure email, choose one:")
        print("\n1. Gmail SMTP (Quick):")
        print("   - Set EMAIL_USERNAME to your Gmail")
        print("   - Set EMAIL_PASSWORD to Gmail App Password")
        print("   - Set SMTP_SERVER to smtp.gmail.com")
        print("   - Set SMTP_PORT to 587")
        print("\n2. SendGrid (Professional):")
        print("   - Get API key from https://sendgrid.com")
        print("   - Set SENDGRID_API_KEY")
        print("\n3. Resend (Modern):")
        print("   - Get API key from https://resend.com")
        print("   - Set RESEND_API_KEY")
        
        return False

if __name__ == "__main__":
    success = test_email_configuration()
    sys.exit(0 if success else 1)
