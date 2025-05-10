"""
Stripe Webhook Handler for DataGuardian Pro

This module processes Stripe webhook events to update user subscriptions, 
track payments, and maintain billing state.
"""

import json
import os
import streamlit as st
from typing import Dict, Any, Tuple

# Import Stripe integration
from billing.stripe_integration import process_webhook_event

def load_users() -> Dict[str, Any]:
    """
    Load users from users.json file
    
    Returns:
        Dictionary with user data
    """
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading users: {str(e)}")
        return {}

def save_users(users: Dict[str, Any]) -> bool:
    """
    Save users to users.json file
    
    Args:
        users: Dictionary with user data
        
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        with open("users.json", "w") as f:
            json.dump(users, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving users: {str(e)}")
        return False

def find_user_by_stripe_customer(customer_id: str) -> Tuple[str, Dict[str, Any]]:
    """
    Find a user by Stripe customer ID
    
    Args:
        customer_id: Stripe customer ID
        
    Returns:
        Tuple of (username, user_data) if found, or (None, {}) if not found
    """
    users = load_users()
    
    for username, user_data in users.items():
        if user_data.get("stripe_customer_id") == customer_id:
            return username, user_data
    
    return None, {}

def handle_webhook(payload: bytes, signature: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Handle a Stripe webhook event
    
    Args:
        payload: Raw request body
        signature: Stripe signature header
        
    Returns:
        Tuple of (success, response_data)
    """
    # Process the webhook event
    success, event_data = process_webhook_event(payload, signature)
    
    if not success:
        return False, event_data
    
    # Get the event type and customer ID
    event = event_data.get("event")
    customer_id = event_data.get("customer_id")
    
    if not customer_id:
        return False, {"error": "No customer ID in webhook event"}
    
    # Find the user associated with this customer
    username, user_data = find_user_by_stripe_customer(customer_id)
    
    if not username:
        return False, {"error": "No user found for customer ID"}
    
    # Load all users
    users = load_users()
    
    # Update user based on event type
    if event == "subscription_created" or event == "subscription_updated":
        # Update subscription plan
        plan_tier = event_data.get("plan_tier", "basic")
        
        # Update user data
        users[username]["subscription_tier"] = plan_tier
        users[username]["subscription_id"] = event_data.get("subscription_id")
        users[username]["subscription_active"] = True
        
    elif event == "subscription_deleted":
        # Reset to basic plan
        users[username]["subscription_tier"] = "basic"
        users[username]["subscription_id"] = None
        users[username]["subscription_active"] = False
    
    # Save updated user data
    if not save_users(users):
        return False, {"error": "Failed to save user data"}
    
    return True, {
        "success": True,
        "event": event,
        "username": username,
        "message": f"User {username} subscription updated"
    }