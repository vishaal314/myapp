"""
Stripe Integration for DataGuardian Pro

This module provides the Stripe integration for payment processing including:
- Customer management
- Payment method handling
- Subscription management
- Invoice generation and retrieval
"""

import os
import json
import stripe
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Initialize Stripe with the API key
def init_stripe():
    """Initialize Stripe with the API key from environment variables"""
    # Get API key from environment, or use a mock key for testing
    stripe_secret_key = os.environ.get("STRIPE_SECRET_KEY", "sk_test_mock")
    
    # In a real app, we would use the actual Stripe API
    # For this demo, we'll mock the API calls
    return stripe_secret_key

def _add_payment_method_to_storage(customer_id: str, payment_method: Dict[str, Any]) -> None:
    """
    Helper function to save a payment method to persistent storage
    
    Args:
        customer_id: Stripe customer ID
        payment_method: Payment method object to save
    """
    import os
    import json
    
    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    os.makedirs(data_dir, exist_ok=True)
    
    # Path to store customer payment methods
    storage_path = os.path.join(data_dir, f"payment_methods_{customer_id}.json")
    
    # Load existing payment methods
    payment_methods = []
    if os.path.exists(storage_path):
        try:
            with open(storage_path, 'r') as f:
                payment_methods = json.load(f)
        except Exception as e:
            print(f"Error loading payment methods: {e}")
    
    # Check if payment method with same ID already exists
    exists = False
    pm_id = payment_method.get("id", "")
    
    for i, pm in enumerate(payment_methods):
        if pm.get("id") == pm_id:
            # Update existing payment method
            payment_methods[i] = payment_method
            exists = True
            print(f"Updating existing payment method {pm_id}")
            break
    
    # Set new payment method as default if specified
    if payment_method.get("is_default", False):
        for pm in payment_methods:
            pm["is_default"] = False
    
    # Add the new payment method if it doesn't exist
    if not exists:
        payment_methods.append(payment_method)
        print(f"Adding new payment method {pm_id}")
    
    # Save updated payment methods
    try:
        with open(storage_path, 'w') as f:
            json.dump(payment_methods, f)
        print(f"Saved payment method {payment_method['id']} for customer {customer_id}")
    except Exception as e:
        print(f"Error saving payment methods: {e}")

def create_stripe_customer(customer_data: Dict[str, Any]) -> str:
    """
    Create a new customer in Stripe
    
    Args:
        customer_data: Dictionary with customer details
        
    Returns:
        Stripe customer ID
    """
    # In a real app, we would call the Stripe API
    # For this demo, we'll return a mock customer ID
    return f"cus_{hashlib.md5(str(customer_data).encode()).hexdigest()[:16]}"

def create_payment_method(customer_id: str, **kwargs) -> Dict[str, Any]:
    """
    Create a new payment method for a customer
    
    Args:
        customer_id: Stripe customer ID
        **kwargs: Payment method details (card_number, exp_month, etc.)
        
    Returns:
        Payment method details
    """
    # In a real app, we would call the Stripe API
    # For this demo, we'll create a mock payment method and store it
    import os
    import json
    
    payment_type = kwargs.get("payment_type", "card")
    
    if payment_type == "card":
        # Create a mock card payment method
        card_number = kwargs.get("card_number", "4242424242424242")
        exp_month = kwargs.get("exp_month", "12")
        exp_year = kwargs.get("exp_year", "25")
        cardholder_name = kwargs.get("cardholder_name", "Test User")
        
        # Basic validation
        if not card_number.isdigit() or len(card_number) < 13 or len(card_number) > 19:
            raise ValueError("Invalid card number")
        
        # Create unique id with timestamp to prevent duplicates
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        created_date = now.strftime("%d/%m/%Y %H:%M")
        unique_id = f"pm_card_{timestamp}_{hashlib.md5((card_number + cardholder_name).encode()).hexdigest()[:12]}"
        
        # Create new payment method object
        payment_method = {
            "id": unique_id,
            "type": "card",
            "card_brand": _get_card_brand(card_number),
            "last4": card_number[-4:],
            "exp_month": exp_month,
            "exp_year": exp_year,
            "cardholder_name": cardholder_name,
            "created_at": created_date,
            "is_default": True  # Set as default if it's the first one
        }
        
        # Add the payment method to the customer's saved payment methods
        _add_payment_method_to_storage(customer_id, payment_method)
        
        return payment_method
    
    elif payment_type == "ideal":
        # Create a mock iDEAL payment method
        bank = kwargs.get("bank", "ing")
        account_name = kwargs.get("account_name", "Test User")
        
        # Create unique id with timestamp to prevent duplicates
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        created_date = now.strftime("%d/%m/%Y %H:%M")
        unique_id = f"pm_ideal_{timestamp}_{hashlib.md5((bank + account_name).encode()).hexdigest()[:12]}"
        
        # Create new payment method object
        payment_method = {
            "id": unique_id,
            "type": "ideal",
            "card_brand": f"iDEAL ({bank})",
            "last4": "Bank", 
            "exp_month": "NA",
            "exp_year": "NA",
            "cardholder_name": account_name,
            "created_at": created_date,
            "is_default": True  # Set as default if it's the first one
        }
        
        # Add the payment method to the customer's saved payment methods
        _add_payment_method_to_storage(customer_id, payment_method)
        
        return payment_method
    
    else:
        raise ValueError(f"Unsupported payment type: {payment_type}")

def list_payment_methods(customer_id: Optional[str]) -> List[Dict[str, Any]]:
    """
    List all payment methods for a customer
    
    Args:
        customer_id: Stripe customer ID
        
    Returns:
        List of payment method details
    """
    # In a real app, we would call the Stripe API
    # For this demo, we'll use our storage system for persistence
    
    if not customer_id:
        return []
    
    import os
    import json
    
    # Define storage path
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    os.makedirs(data_dir, exist_ok=True)
    storage_path = os.path.join(data_dir, f"payment_methods_{customer_id}.json")
    
    # Try to load saved payment methods
    if os.path.exists(storage_path):
        try:
            with open(storage_path, 'r') as f:
                saved_methods = json.load(f)
                if saved_methods:
                    print(f"Loaded {len(saved_methods)} payment methods for customer {customer_id}")
                    return saved_methods
        except Exception as e:
            print(f"Error loading payment methods: {e}")
    
    # If no saved methods exist, generate some mock ones
    print(f"No saved payment methods found for {customer_id}, generating mock data")
    
    # Generate a deterministic but "random-looking" number of payment methods
    num_methods = int(hashlib.md5(str(customer_id).encode()).hexdigest()[-1], 16) % 2
    
    # Always return at least one payment method for customers with subscription
    if customer_id.startswith("cus_") and num_methods == 0:
        num_methods = 1
    
    payment_methods = []
    
    for i in range(num_methods):
        # Generate mock card details
        card_types = ["Visa", "Mastercard", "American Express"]
        card_brand = card_types[i % len(card_types)]
        
        # Create unique ID with index and timestamp
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        created_date = now.strftime("%d/%m/%Y %H:%M")
        unique_id = f"pm_mock_{timestamp}_{i}_{hashlib.md5((customer_id + str(i)).encode()).hexdigest()[:8]}"
        
        payment_methods.append({
            "id": unique_id,
            "type": "card",
            "card_brand": card_brand,
            "last4": f"{1000 + i}",
            "exp_month": "12",
            "exp_year": "2025",
            "cardholder_name": "Test User",
            "created_at": created_date,
            "is_default": i == 0  # First one is default
        })
    
    # Save these initial methods to storage
    if payment_methods:
        try:
            with open(storage_path, 'w') as f:
                json.dump(payment_methods, f)
            print(f"Saved {len(payment_methods)} initial payment methods for customer {customer_id}")
        except Exception as e:
            print(f"Error saving initial payment methods: {e}")
    
    return payment_methods

def update_default_payment_method(customer_id: str, payment_method_id: str) -> bool:
    """
    Set a payment method as default for a customer
    
    Args:
        customer_id: Stripe customer ID
        payment_method_id: Payment method ID
        
    Returns:
        Success flag
    """
    # In a real app, we would call the Stripe API
    # For this demo, we'll use our storage system
    
    import os
    import json
    
    # Define storage path
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    storage_path = os.path.join(data_dir, f"payment_methods_{customer_id}.json")
    
    # Check if file exists
    if not os.path.exists(storage_path):
        print(f"No payment methods found for customer {customer_id}")
        return False
    
    # Load payment methods
    try:
        with open(storage_path, 'r') as f:
            payment_methods = json.load(f)
    except Exception as e:
        print(f"Error loading payment methods: {e}")
        return False
    
    # Find the payment method to set as default
    found = False
    for pm in payment_methods:
        if pm.get("id") == payment_method_id:
            pm["is_default"] = True
            found = True
        else:
            pm["is_default"] = False
    
    if not found:
        print(f"Payment method {payment_method_id} not found for customer {customer_id}")
        return False
    
    # Save updated payment methods
    try:
        with open(storage_path, 'w') as f:
            json.dump(payment_methods, f)
        print(f"Updated default payment method to {payment_method_id} for customer {customer_id}")
        return True
    except Exception as e:
        print(f"Error saving payment methods: {e}")
        return False

def delete_payment_method(customer_id: str, payment_method_id: str) -> bool:
    """
    Delete a payment method for a customer
    
    Args:
        customer_id: Stripe customer ID
        payment_method_id: Payment method ID
        
    Returns:
        Success flag
    """
    # In a real app, we would call the Stripe API
    # For this demo, we'll use our storage system
    
    import os
    import json
    
    # Define storage path
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    storage_path = os.path.join(data_dir, f"payment_methods_{customer_id}.json")
    
    # Check if file exists
    if not os.path.exists(storage_path):
        print(f"No payment methods found for customer {customer_id}")
        return False
    
    # Load payment methods
    try:
        with open(storage_path, 'r') as f:
            payment_methods = json.load(f)
    except Exception as e:
        print(f"Error loading payment methods: {e}")
        return False
    
    # Find the payment method to delete
    was_default = False
    new_payment_methods = []
    for pm in payment_methods:
        if pm.get("id") == payment_method_id:
            was_default = pm.get("is_default", False)
            continue  # Skip this payment method (delete it)
        new_payment_methods.append(pm)
    
    if len(new_payment_methods) == len(payment_methods):
        print(f"Payment method {payment_method_id} not found for customer {customer_id}")
        return False
    
    # If the deleted payment method was the default, set the first remaining one as default
    if was_default and new_payment_methods:
        new_payment_methods[0]["is_default"] = True
    
    # Save updated payment methods
    try:
        with open(storage_path, 'w') as f:
            json.dump(new_payment_methods, f)
        print(f"Deleted payment method {payment_method_id} for customer {customer_id}")
        return True
    except Exception as e:
        print(f"Error saving payment methods: {e}")
        return False

def get_subscription_details(customer_id: Optional[str]) -> Optional[Dict[str, Any]]:
    """
    Get subscription details for a customer
    
    Args:
        customer_id: Stripe customer ID
        
    Returns:
        Subscription details or None
    """
    # In a real app, we would call the Stripe API
    # For this demo, we'll return mock subscription details
    
    if not customer_id:
        return None
    
    # Calculate a deterministic but "random-looking" subscription status
    sub_hash = hashlib.md5(str(customer_id).encode()).hexdigest()
    
    # Determine if customer has a subscription
    has_subscription = int(sub_hash[-2], 16) % 5 != 0  # 80% chance of having a subscription
    
    if not has_subscription:
        return None
    
    # Determine subscription details
    tiers = ["basic", "professional", "enterprise"]
    tier_index = int(sub_hash[-3], 16) % len(tiers)
    
    # Calculate next billing date
    days_to_next = int(sub_hash[-4:], 16) % 30 + 1
    next_billing = (datetime.now() + timedelta(days=days_to_next)).strftime("%Y-%m-%d")
    
    return {
        "id": f"sub_{hashlib.md5(str(customer_id).encode()).hexdigest()[:16]}",
        "status": "active",
        "tier": tiers[tier_index],
        "current_period_end": next_billing,
        "cancel_at_period_end": False
    }

def create_checkout_session(customer_id: str, price_id: str, success_url: str, cancel_url: str) -> Dict[str, Any]:
    """
    Create a Stripe Checkout session for subscription
    
    Args:
        customer_id: Stripe customer ID
        price_id: Stripe price ID
        success_url: URL to redirect to on success
        cancel_url: URL to redirect to on cancel
        
    Returns:
        Checkout session details
    """
    # In a real app, we would call the Stripe API
    # For this demo, we'll return a mock checkout session
    
    # Mock response
    return {
        "id": f"cs_{hashlib.md5(f'{customer_id}_{price_id}'.encode()).hexdigest()[:16]}",
        "url": success_url,  # For demo, always "succeed"
        "payment_status": "paid",
        "subscription": f"sub_{hashlib.md5(str(customer_id).encode()).hexdigest()[:16]}"
    }

def _get_card_brand(card_number: str) -> str:
    """
    Determine the card brand based on the first few digits
    
    Args:
        card_number: Card number
        
    Returns:
        Card brand name
    """
    first_digit = card_number[0] if card_number else ""
    first_two = card_number[:2] if len(card_number) >= 2 else ""
    
    if first_digit == "4":
        return "Visa"
    elif first_two in ["51", "52", "53", "54", "55"]:
        return "Mastercard"
    elif first_two in ["34", "37"]:
        return "American Express"
    elif first_two == "62":
        return "UnionPay"
    elif first_two == "35":
        return "JCB"
    else:
        return "Unknown"