"""
Stripe Webhook Handler for DataGuardian Pro
Handles real-time payment confirmations and subscription events
"""

import os
import json
import hashlib
import hmac
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import stripe
import streamlit as st

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebhookHandler:
    """Handle Stripe webhook events with security and reliability"""
    
    def __init__(self):
        self.stripe_api_key = os.getenv('STRIPE_SECRET_KEY')
        self.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        
        if self.stripe_api_key:
            stripe.api_key = self.stripe_api_key
        
        if not self.webhook_secret:
            logger.warning("STRIPE_WEBHOOK_SECRET not configured - webhook signature verification disabled")
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify Stripe webhook signature for security
        
        Args:
            payload: Raw request payload as bytes
            signature: Stripe signature header
            
        Returns:
            True if signature is valid
        """
        if not self.webhook_secret:
            logger.warning("Webhook signature verification skipped - no secret configured")
            return True
        
        try:
            stripe.Webhook.construct_event(payload, signature, self.webhook_secret)
            return True
        except stripe.SignatureVerificationError:
            logger.error("Invalid webhook signature")
            return False
        except Exception as e:
            logger.error(f"Webhook verification error: {str(e)}")
            return False
    
    def process_webhook_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process webhook event and return response
        
        Args:
            event: Stripe webhook event data
            
        Returns:
            Processing result dictionary
        """
        event_type = event.get('type', 'unknown')
        event_id = event.get('id', 'unknown')
        
        logger.info(f"Processing webhook event: {event_type} ({event_id})")
        
        try:
            # Route event to appropriate handler
            if event_type.startswith('checkout.session.'):
                return self._handle_checkout_event(event)
            elif event_type.startswith('payment_intent.'):
                return self._handle_payment_intent_event(event)
            elif event_type.startswith('invoice.'):
                return self._handle_invoice_event(event)
            elif event_type.startswith('customer.subscription.'):
                return self._handle_subscription_event(event)
            else:
                logger.info(f"Unhandled event type: {event_type}")
                return {'status': 'ignored', 'message': f'Event type {event_type} not handled'}
                
        except Exception as e:
            logger.error(f"Error processing webhook event {event_id}: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def _handle_checkout_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle checkout session events"""
        event_type = event['type']
        session = event['data']['object']
        
        if event_type == 'checkout.session.completed':
            return self._handle_checkout_completed(session)
        elif event_type == 'checkout.session.expired':
            return self._handle_checkout_expired(session)
        
        return {'status': 'ignored', 'message': f'Checkout event {event_type} not handled'}
    
    def _handle_checkout_completed(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful checkout completion"""
        session_id = session.get('id')
        customer_email = session.get('customer_email')
        amount_total = session.get('amount_total', 0)
        metadata = session.get('metadata', {})
        
        logger.info(f"Checkout completed: {session_id} for {customer_email}")
        
        # Extract scan details from metadata
        scan_type = metadata.get('scan_type', 'Unknown')
        country_code = metadata.get('country_code', 'NL')
        
        # Log payment completion
        payment_record = {
            'session_id': session_id,
            'customer_email': customer_email,
            'amount': amount_total / 100,  # Convert from cents
            'currency': session.get('currency', 'eur'),
            'scan_type': scan_type,
            'country_code': country_code,
            'status': 'completed',
            'timestamp': datetime.utcnow().isoformat(),
            'payment_method': session.get('payment_method_types', ['unknown'])[0]
        }
        
        # Store payment record (in production, save to database)
        self._store_payment_record(payment_record)
        
        # Trigger scan processing
        self._trigger_scan_processing(payment_record)
        
        # Send confirmation email
        self._send_payment_confirmation(payment_record)
        
        return {
            'status': 'success',
            'message': f'Payment processed for {scan_type}',
            'payment_id': session_id
        }
    
    def _handle_checkout_expired(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Handle expired checkout sessions"""
        session_id = session.get('id')
        customer_email = session.get('customer_email')
        
        logger.info(f"Checkout expired: {session_id} for {customer_email}")
        
        # Log abandoned checkout for analytics
        abandoned_record = {
            'session_id': session_id,
            'customer_email': customer_email,
            'status': 'expired',
            'timestamp': datetime.utcnow().isoformat(),
            'metadata': session.get('metadata', {})
        }
        
        self._store_abandoned_checkout(abandoned_record)
        
        return {
            'status': 'success',
            'message': 'Expired checkout logged',
            'session_id': session_id
        }
    
    def _handle_payment_intent_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment intent events"""
        event_type = event['type']
        payment_intent = event['data']['object']
        
        if event_type == 'payment_intent.succeeded':
            return self._handle_payment_succeeded(payment_intent)
        elif event_type == 'payment_intent.payment_failed':
            return self._handle_payment_failed(payment_intent)
        
        return {'status': 'ignored', 'message': f'Payment intent event {event_type} not handled'}
    
    def _handle_payment_succeeded(self, payment_intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful payment"""
        payment_id = payment_intent.get('id')
        amount = payment_intent.get('amount', 0)
        
        logger.info(f"Payment succeeded: {payment_id} for €{amount/100:.2f}")
        
        # Update payment status in database
        if payment_id:
            self._update_payment_status(payment_id, 'succeeded')
        
        return {
            'status': 'success',
            'message': 'Payment success recorded',
            'payment_id': payment_id
        }
    
    def _handle_payment_failed(self, payment_intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle failed payment"""
        payment_id = payment_intent.get('id')
        failure_reason = payment_intent.get('last_payment_error', {}).get('message', 'Unknown error')
        
        logger.warning(f"Payment failed: {payment_id} - {failure_reason}")
        
        # Update payment status and log failure
        if payment_id:
            self._update_payment_status(payment_id, 'failed', failure_reason)
        
        return {
            'status': 'success',
            'message': 'Payment failure recorded',
            'payment_id': payment_id
        }
    
    def _handle_invoice_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle invoice events for subscriptions"""
        event_type = event['type']
        invoice = event['data']['object']
        
        if event_type == 'invoice.payment_succeeded':
            return self._handle_invoice_paid(invoice)
        elif event_type == 'invoice.payment_failed':
            return self._handle_invoice_failed(invoice)
        
        return {'status': 'ignored', 'message': f'Invoice event {event_type} not handled'}
    
    def _handle_invoice_paid(self, invoice: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful subscription payment"""
        invoice_id = invoice.get('id')
        customer_id = invoice.get('customer')
        amount_paid = invoice.get('amount_paid', 0)
        
        logger.info(f"Subscription payment succeeded: {invoice_id} for €{amount_paid/100:.2f}")
        
        # Update subscription status
        if customer_id:
            self._update_subscription_status(customer_id, 'active')
        
        return {
            'status': 'success',
            'message': 'Subscription payment recorded',
            'invoice_id': invoice_id
        }
    
    def _handle_invoice_failed(self, invoice: Dict[str, Any]) -> Dict[str, Any]:
        """Handle failed subscription payment"""
        invoice_id = invoice.get('id')
        customer_id = invoice.get('customer')
        
        logger.warning(f"Subscription payment failed: {invoice_id}")
        
        # Handle failed payment (retry logic, notifications, etc.)
        if customer_id and invoice_id:
            self._handle_subscription_payment_failure(customer_id, invoice_id)
        
        return {
            'status': 'success',
            'message': 'Subscription payment failure handled',
            'invoice_id': invoice_id
        }
    
    def _handle_subscription_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription lifecycle events"""
        event_type = event['type']
        subscription = event['data']['object']
        
        if event_type == 'customer.subscription.created':
            return self._handle_subscription_created(subscription)
        elif event_type == 'customer.subscription.updated':
            return self._handle_subscription_updated(subscription)
        elif event_type == 'customer.subscription.deleted':
            return self._handle_subscription_cancelled(subscription)
        
        return {'status': 'ignored', 'message': f'Subscription event {event_type} not handled'}
    
    def _handle_subscription_created(self, subscription: Dict[str, Any]) -> Dict[str, Any]:
        """Handle new subscription creation"""
        subscription_id = subscription.get('id')
        customer_id = subscription.get('customer')
        
        logger.info(f"New subscription created: {subscription_id}")
        
        # Set up subscription in database
        self._create_subscription_record(subscription)
        
        return {
            'status': 'success',
            'message': 'Subscription created',
            'subscription_id': subscription_id
        }
    
    def _handle_subscription_updated(self, subscription: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription updates"""
        subscription_id = subscription.get('id')
        status = subscription.get('status')
        
        logger.info(f"Subscription updated: {subscription_id} status: {status}")
        
        # Update subscription in database
        self._update_subscription_record(subscription)
        
        return {
            'status': 'success',
            'message': 'Subscription updated',
            'subscription_id': subscription_id
        }
    
    def _handle_subscription_cancelled(self, subscription: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription cancellation"""
        subscription_id = subscription.get('id')
        customer_id = subscription.get('customer')
        
        logger.info(f"Subscription cancelled: {subscription_id}")
        
        # Update subscription status and handle cleanup
        if subscription_id:
            self._cancel_subscription_record(subscription_id)
        
        return {
            'status': 'success',
            'message': 'Subscription cancelled',
            'subscription_id': subscription_id
        }
    
    # Helper methods for database operations (implement based on your database)
    def _store_payment_record(self, payment_record: Dict[str, Any]) -> None:
        """Store payment record in database"""
        # TODO: Implement database storage
        logger.info(f"Storing payment record: {payment_record['session_id']}")
        pass
    
    def _store_abandoned_checkout(self, abandoned_record: Dict[str, Any]) -> None:
        """Store abandoned checkout for analytics"""
        # TODO: Implement analytics storage
        logger.info(f"Storing abandoned checkout: {abandoned_record['session_id']}")
        pass
    
    def _trigger_scan_processing(self, payment_record: Dict[str, Any]) -> None:
        """Trigger automatic scan processing after payment"""
        # TODO: Implement scan queue processing
        logger.info(f"Triggering scan processing for: {payment_record['scan_type']}")
        pass
    
    def _send_payment_confirmation(self, payment_record: Dict[str, Any]) -> None:
        """Send payment confirmation email"""
        # TODO: Implement email service
        logger.info(f"Sending confirmation email to: {payment_record['customer_email']}")
        pass
    
    def _update_payment_status(self, payment_id: str, status: str, error_message: Optional[str] = None) -> None:
        """Update payment status in database"""
        # TODO: Implement database update
        logger.info(f"Updating payment {payment_id} status: {status}")
        pass
    
    def _update_subscription_status(self, customer_id: str, status: str) -> None:
        """Update subscription status"""
        # TODO: Implement database update
        logger.info(f"Updating subscription status for customer {customer_id}: {status}")
        pass
    
    def _handle_subscription_payment_failure(self, customer_id: str, invoice_id: str) -> None:
        """Handle subscription payment failure"""
        # TODO: Implement retry logic and notifications
        logger.warning(f"Handling subscription payment failure for customer {customer_id}")
        pass
    
    def _create_subscription_record(self, subscription: Dict[str, Any]) -> None:
        """Create subscription record in database"""
        # TODO: Implement database creation
        logger.info(f"Creating subscription record: {subscription.get('id')}")
        pass
    
    def _update_subscription_record(self, subscription: Dict[str, Any]) -> None:
        """Update subscription record in database"""
        # TODO: Implement database update
        logger.info(f"Updating subscription record: {subscription.get('id')}")
        pass
    
    def _cancel_subscription_record(self, subscription_id: str) -> None:
        """Cancel subscription record"""
        # TODO: Implement database update
        logger.info(f"Cancelling subscription record: {subscription_id}")
        pass

# Global webhook handler instance
webhook_handler = WebhookHandler()

def process_stripe_webhook(payload: bytes, signature: str) -> Dict[str, Any]:
    """
    Process incoming Stripe webhook
    
    Args:
        payload: Raw request payload as bytes
        signature: Stripe signature header
        
    Returns:
        Processing result dictionary
    """
    # Verify signature
    if not webhook_handler.verify_webhook_signature(payload, signature):
        return {'status': 'error', 'message': 'Invalid signature'}
    
    try:
        # Parse event data
        event = json.loads(payload.decode('utf-8'))
        
        # Process event
        return webhook_handler.process_webhook_event(event)
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook payload")
        return {'status': 'error', 'message': 'Invalid JSON payload'}
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        return {'status': 'error', 'message': 'Internal processing error'}