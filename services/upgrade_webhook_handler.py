"""
Upgrade Webhook Handler for DataGuardian Pro
Processes Stripe webhooks for license upgrade payments
"""

import os
import stripe
import logging
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify
from services.license_upgrade_payment import license_upgrade_payment_manager

logger = logging.getLogger(__name__)

# Initialize Flask app for webhooks
webhook_app = Flask(__name__)

# Stripe webhook endpoint secret
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

@webhook_app.route('/webhooks/stripe/upgrade', methods=['POST'])
def handle_stripe_upgrade_webhook():
    """Handle Stripe webhooks for upgrade payments"""
    
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    if not STRIPE_WEBHOOK_SECRET:
        logger.error("Stripe webhook secret not configured")
        return jsonify({'error': 'Webhook not configured'}), 500
    
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Check if this is an upgrade payment
        metadata = session.get('metadata', {})
        if metadata.get('upgrade_type') == 'license_tier':
            success = license_upgrade_payment_manager.process_successful_upgrade(session['id'])
            
            if success:
                logger.info(f"Successfully processed upgrade for session {session['id']}")
                return jsonify({'status': 'success'}), 200
            else:
                logger.error(f"Failed to process upgrade for session {session['id']}")
                return jsonify({'error': 'Processing failed'}), 500
    
    elif event['type'] == 'payment_intent.succeeded':
        # Additional confirmation for payment success
        payment_intent = event['data']['object']
        logger.info(f"Payment succeeded: {payment_intent['id']}")
    
    elif event['type'] == 'payment_intent.payment_failed':
        # Handle failed payments
        payment_intent = event['data']['object']
        logger.warning(f"Payment failed: {payment_intent['id']}")
    
    return jsonify({'status': 'received'}), 200

@webhook_app.route('/upgrade-success')
def upgrade_success_page():
    """Redirect page after successful upgrade payment"""
    
    session_id = request.args.get('session_id')
    
    if session_id:
        # Process the upgrade
        success = license_upgrade_payment_manager.process_successful_upgrade(session_id)
        
        if success:
            # In a full web app, this would redirect to the success page
            return f"""
            <html>
            <head>
                <title>Upgrade Successful - DataGuardian Pro</title>
                <meta http-equiv="refresh" content="3;url=/">
            </head>
            <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                <h1>🎉 Upgrade Successful!</h1>
                <p>Your DataGuardian Pro license has been upgraded successfully.</p>
                <p>You will be redirected to your dashboard in 3 seconds...</p>
                <a href="/">Return to Dashboard</a>
            </body>
            </html>
            """
        else:
            return f"""
            <html>
            <head>
                <title>Upgrade Processing - DataGuardian Pro</title>
            </head>
            <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                <h1>⏳ Processing Your Upgrade</h1>
                <p>We're processing your upgrade. This may take a few moments.</p>
                <p>Please check your email for confirmation or contact support if you have questions.</p>
                <a href="/">Return to Dashboard</a>
            </body>
            </html>
            """
    
    return "Invalid session", 400

def start_webhook_server(port: int = 5001):
    """Start the webhook server"""
    logger.info(f"Starting upgrade webhook server on port {port}")
    webhook_app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    start_webhook_server()