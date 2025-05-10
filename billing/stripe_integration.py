"""
Stripe Integration Module for DataGuardian Pro

This module handles all Stripe-related functionality including:
- Customer creation and management
- Subscription handling and checkout flows
- Webhook processing
- Payment history retrieval
"""

import os
import json
import stripe
import streamlit as st
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import uuid
import hmac
import hashlib

# Initialize Stripe with API keys from environment variables
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
stripe_publishable_key = os.environ.get('STRIPE_PUBLISHABLE_KEY')
webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')

# Import the plans configuration
from billing.plans_config import (
    SUBSCRIPTION_PLANS, 
    get_plan_by_tier, 
    get_plan_by_price_id
)

# URL for webhook and success/cancel redirects
BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")
SUCCESS_URL = f"{BASE_URL}/?checkout=success"
CANCEL_URL = f"{BASE_URL}/?checkout=cancel"
WEBHOOK_URL = f"{BASE_URL}/stripe-webhook"

def create_stripe_customer(user_data: Dict[str, Any]) -> Optional[str]:
    """
    Create a new Stripe customer for a user
    
    Args:
        user_data: Dictionary containing user information
        
    Returns:
        Stripe customer ID if successful, None otherwise
    """
    try:
        customer = stripe.Customer.create(
            email=user_data.get("email"),
            name=user_data.get("username"),
            metadata={
                "user_id": user_data.get("user_id", str(uuid.uuid4())),
                "role": user_data.get("role", "user")
            }
        )
        return customer.id
    except stripe.error.StripeError as e:
        st.error(f"Error creating Stripe customer: {str(e)}")
        return None

def get_customer_subscription_data(customer_id: str) -> Dict[str, Any]:
    """
    Get subscription data for a Stripe customer
    
    Args:
        customer_id: Stripe customer ID
        
    Returns:
        Dictionary with subscription details
    """
    try:
        # Get active subscriptions for the customer
        subscriptions = stripe.Subscription.list(
            customer=customer_id,
            status='active',
            expand=['data.default_payment_method']
        )
        
        if not subscriptions.data:
            return {
                "has_subscription": False,
                "subscription_id": None,
                "plan_tier": "basic",  # Default to basic for customers without subscriptions
                "plan_name": "Basic",
                "renewal_date": None,
                "payment_method": None
            }
        
        subscription = subscriptions.data[0]
        price_id = subscription.items.data[0].price.id
        
        # Get the plan tier based on the price ID
        tier, plan = get_plan_by_price_id(price_id)
        
        # Get renewal date (current_period_end is a Unix timestamp)
        renewal_timestamp = subscription.current_period_end
        renewal_date = datetime.fromtimestamp(renewal_timestamp).strftime("%Y-%m-%d")
        
        # Get payment method details if available
        payment_method = None
        if subscription.default_payment_method:
            card = subscription.default_payment_method.card
            payment_method = {
                "brand": card.brand,
                "last4": card.last4,
                "exp_month": card.exp_month,
                "exp_year": card.exp_year
            }
        
        return {
            "has_subscription": True,
            "subscription_id": subscription.id,
            "plan_tier": tier,
            "plan_name": plan["name"],
            "renewal_date": renewal_date,
            "payment_method": payment_method
        }
    except stripe.error.StripeError as e:
        st.error(f"Error getting customer subscription: {str(e)}")
        return {
            "has_subscription": False,
            "subscription_id": None,
            "plan_tier": "basic",
            "plan_name": "Basic",
            "renewal_date": None,
            "payment_method": None,
            "error": str(e)
        }

def create_checkout_session(
    customer_id: str, 
    price_id: str, 
    mode: str = 'subscription'
) -> Optional[str]:
    """
    Create a Stripe Checkout session
    
    Args:
        customer_id: Stripe customer ID
        price_id: Stripe price ID for the selected plan
        mode: Checkout mode ('subscription' or 'payment')
        
    Returns:
        Checkout session URL if successful, None otherwise
    """
    try:
        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode=mode,
            success_url=SUCCESS_URL,
            cancel_url=CANCEL_URL,
        )
        return checkout_session.url
    except stripe.error.StripeError as e:
        st.error(f"Error creating checkout session: {str(e)}")
        return None

def create_customer_portal_session(customer_id: str) -> Optional[str]:
    """
    Create a Stripe Customer Portal session
    
    Args:
        customer_id: Stripe customer ID
        
    Returns:
        Portal session URL if successful, None otherwise
    """
    try:
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=BASE_URL,
        )
        return session.url
    except stripe.error.StripeError as e:
        st.error(f"Error creating customer portal session: {str(e)}")
        return None

def get_invoice_history(customer_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get invoice history for a Stripe customer
    
    Args:
        customer_id: Stripe customer ID
        limit: Maximum number of invoices to return
        
    Returns:
        List of invoice details
    """
    try:
        invoices = stripe.Invoice.list(
            customer=customer_id,
            limit=limit,
            status='paid'
        )
        
        invoice_list = []
        for invoice in invoices.data:
            # Format invoice data
            invoice_date = datetime.fromtimestamp(invoice.created).strftime("%Y-%m-%d")
            amount = invoice.amount_paid / 100  # Convert cents to dollars
            
            invoice_list.append({
                "invoice_id": invoice.id,
                "date": invoice_date,
                "amount": amount,
                "currency": invoice.currency.upper(),
                "status": invoice.status,
                "pdf_url": invoice.invoice_pdf
            })
            
        return invoice_list
    except stripe.error.StripeError as e:
        st.error(f"Error retrieving invoice history: {str(e)}")
        return []

def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """
    Verify the signature of a Stripe webhook
    
    Args:
        payload: Request body as bytes
        signature: Stripe signature from request headers
        
    Returns:
        True if signature is valid, False otherwise
    """
    if not webhook_secret:
        st.warning("Webhook secret not configured")
        return False
        
    try:
        # Verify the signature using the webhook secret
        stripe.Webhook.construct_event(
            payload, signature, webhook_secret
        )
        return True
    except (ValueError, stripe.error.SignatureVerificationError):
        return False

def process_webhook_event(payload: bytes, signature: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Process a Stripe webhook event
    
    Args:
        payload: Request body as bytes
        signature: Stripe signature from request headers
        
    Returns:
        Tuple of (success, event_data)
    """
    # First verify the webhook signature
    if not verify_webhook_signature(payload, signature):
        return False, {"error": "Invalid webhook signature"}
    
    try:
        # Parse the event
        event_json = json.loads(payload)
        event_type = event_json.get("type")
        event_data = event_json.get("data", {}).get("object", {})
        
        # Process different event types
        if event_type == "customer.subscription.created":
            # New subscription created
            customer_id = event_data.get("customer")
            subscription_id = event_data.get("id")
            
            # Get the price ID to determine the plan tier
            if event_data.get("items", {}).get("data"):
                price_id = event_data["items"]["data"][0]["price"]["id"]
                tier, _ = get_plan_by_price_id(price_id)
                
                return True, {
                    "event": "subscription_created",
                    "customer_id": customer_id,
                    "subscription_id": subscription_id,
                    "plan_tier": tier
                }
        
        elif event_type == "customer.subscription.updated":
            # Subscription updated (upgrade/downgrade)
            customer_id = event_data.get("customer")
            subscription_id = event_data.get("id")
            
            # Get the price ID to determine the new plan tier
            if event_data.get("items", {}).get("data"):
                price_id = event_data["items"]["data"][0]["price"]["id"]
                tier, _ = get_plan_by_price_id(price_id)
                
                return True, {
                    "event": "subscription_updated",
                    "customer_id": customer_id,
                    "subscription_id": subscription_id,
                    "plan_tier": tier
                }
                
        elif event_type == "customer.subscription.deleted":
            # Subscription canceled
            customer_id = event_data.get("customer")
            subscription_id = event_data.get("id")
            
            return True, {
                "event": "subscription_deleted",
                "customer_id": customer_id,
                "subscription_id": subscription_id
            }
            
        elif event_type == "invoice.paid":
            # Payment succeeded
            customer_id = event_data.get("customer")
            invoice_id = event_data.get("id")
            amount_paid = event_data.get("amount_paid", 0) / 100  # Convert cents to dollars
            
            return True, {
                "event": "payment_succeeded",
                "customer_id": customer_id,
                "invoice_id": invoice_id,
                "amount": amount_paid
            }
            
        # Return success for unhandled event types
        return True, {
            "event": "unhandled",
            "type": event_type
        }
        
    except Exception as e:
        return False, {"error": f"Error processing webhook: {str(e)}"}

def update_user_subscription(user_data: Dict[str, Any], subscription_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update user data with subscription information
    
    Args:
        user_data: Current user data
        subscription_data: Subscription data from webhook
        
    Returns:
        Updated user data
    """
    event = subscription_data.get("event")
    
    # Make a copy to avoid modifying the original
    updated_user = user_data.copy()
    
    if event == "subscription_created" or event == "subscription_updated":
        # Update plan tier and subscription details
        updated_user["subscription_tier"] = subscription_data.get("plan_tier", "basic")
        updated_user["subscription_id"] = subscription_data.get("subscription_id")
        updated_user["subscription_active"] = True
        
    elif event == "subscription_deleted":
        # Reset to basic tier when subscription is canceled
        updated_user["subscription_tier"] = "basic"
        updated_user["subscription_id"] = None
        updated_user["subscription_active"] = False
        
    # Return the updated user data
    return updated_user