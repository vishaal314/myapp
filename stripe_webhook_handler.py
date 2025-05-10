"""
Stripe Webhook Handler for DataGuardian Pro

This is a standalone script that can be run to handle Stripe webhook events.
It should be configured as the webhook endpoint in your Stripe Dashboard.

In a production environment, this would typically be a separate API endpoint
in a web framework like Flask or FastAPI, but for Streamlit we'll use a simpler approach.
"""

import os
import sys
import json
from typing import Dict, Any
import hmac
import hashlib

# Import the webhook handler
from billing.stripe_webhooks import handle_webhook

def main():
    """
    Process a webhook request from Stripe
    """
    # Read input from stdin (for testing)
    if len(sys.argv) > 1 and sys.argv[1] == "--stdin":
        payload = sys.stdin.buffer.read()
        signature = os.environ.get("STRIPE_WEBHOOK_SIGNATURE", "")
    else:
        # For testing, you can pass JSON file and signature
        if len(sys.argv) != 3:
            print("Usage: python stripe_webhook_handler.py <payload_file> <signature>")
            print("   or: echo '{...}' | python stripe_webhook_handler.py --stdin")
            sys.exit(1)
            
        payload_file = sys.argv[1]
        signature = sys.argv[2]
        
        with open(payload_file, "rb") as f:
            payload = f.read()
    
    # Process the webhook
    success, response = handle_webhook(payload, signature)
    
    # Print the response
    print(json.dumps(response, indent=2))
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()