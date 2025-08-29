#!/usr/bin/env python3
"""
Test script for DataGuardian Pro webhook endpoint
"""

import json
import requests
import os
from datetime import datetime

def test_webhook_endpoint():
    """Test the webhook endpoint with a sample Stripe event"""
    
    # Test webhook URL (adjust based on your setup)
    webhook_url = "http://localhost:5001/webhook/stripe"
    
    # Sample Stripe checkout.session.completed event
    test_event = {
        "id": "evt_test_webhook_" + str(int(datetime.now().timestamp())),
        "object": "event",
        "api_version": "2020-08-27",
        "created": int(datetime.now().timestamp()),
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_a1b2c3d4e5f6g7h8i9j0",
                "object": "checkout.session",
                "amount_total": 2783,  # €27.83 with VAT
                "currency": "eur",
                "customer_email": "test@dataguardian.nl",
                "payment_status": "paid",
                "payment_method_types": ["card", "ideal"],
                "metadata": {
                    "scan_type": "Code Scan",
                    "user_email": "test@dataguardian.nl",
                    "country_code": "NL",
                    "vat_rate": "0.21"
                }
            }
        }
    }
    
    try:
        # Test health check first
        health_response = requests.get("http://localhost:5001/webhook/health")
        print(f"✅ Health check: {health_response.status_code} - {health_response.json()}")
        
        # Test webhook processing (without signature for testing)
        headers = {
            'Content-Type': 'application/json',
            'Stripe-Signature': 'test_signature_12345'  # This would normally be real
        }
        
        response = requests.post(
            webhook_url,
            headers=headers,
            data=json.dumps(test_event)
        )
        
        print(f"\n🧪 Webhook Test Results:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Webhook endpoint is working!")
        else:
            print("❌ Webhook endpoint returned an error")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to webhook server. Make sure it's running on port 5001")
        print("Start with: python services/webhook_server.py")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

def start_webhook_server():
    """Instructions to start the webhook server"""
    print("🚀 DataGuardian Pro Webhook Server Setup")
    print("=" * 50)
    print()
    print("1. Start the webhook server:")
    print("   python services/webhook_server.py")
    print()
    print("2. Test the webhook endpoint:")
    print("   python webhook_test.py")
    print()
    print("3. Configure Stripe webhook endpoint:")
    print("   - Go to Stripe Dashboard > Webhooks")
    print("   - Add endpoint: https://yourdomain.com/webhook/stripe")
    print("   - Select events: checkout.session.completed, payment_intent.succeeded")
    print("   - Copy webhook secret to STRIPE_WEBHOOK_SECRET environment variable")
    print()
    print("4. For local testing, use ngrok:")
    print("   ngrok http 5001")
    print("   Use the ngrok URL in Stripe webhook configuration")

if __name__ == "__main__":
    print("🧪 Testing DataGuardian Pro Webhook Endpoint")
    print("=" * 50)
    
    # Check if webhook server is likely running
    try:
        response = requests.get("http://localhost:5001/webhook/health", timeout=2)
        test_webhook_endpoint()
    except:
        start_webhook_server()