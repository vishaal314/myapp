"""
Enhanced Signup Flow for DataGuardian Pro

This module provides a complete end-to-end signup experience including:
- User registration with email validation
- Free trial option
- Proper payment method selection (VISA/iDEAL)
- Subscription plan activation
"""

import streamlit as st
import re
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple, Optional, List

# Import billing components
from billing.plans_config import SUBSCRIPTION_PLANS
from billing.stripe_integration import (
    create_stripe_customer,
    create_checkout_session
)

# File paths
USERS_FILE = "users.json"

def load_users() -> Dict[str, Any]:
    """Load users data from JSON file"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users: Dict[str, Any]) -> None:
    """Save users data to JSON file"""
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def validate_email(email: str) -> bool:
    """Validate email format using regex"""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password strength
    Returns: (is_valid, message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    
    return True, "Password is strong"

def user_exists(username: str, email: str) -> Tuple[bool, str]:
    """Check if user already exists"""
    users = load_users()
    
    if username in users:
        return True, "Username already taken"
    
    for user, data in users.items():
        if data.get("email") == email:
            return True, "Email already registered"
    
    return False, ""

def create_user(
    username: str, 
    password: str, 
    email: str, 
    first_name: str,
    last_name: str,
    role: str = "user", 
    subscription_tier: str = "basic",
    free_trial: bool = True
) -> Tuple[bool, str]:
    """
    Create a new user with optional free trial
    Returns: (success, message)
    """
    users = load_users()
    
    # Check if user exists
    exists, message = user_exists(username, email)
    if exists:
        return False, message
    
    # Create Stripe customer
    customer_id = create_stripe_customer({
        "email": email,
        "name": f"{first_name} {last_name}",
        "metadata": {
            "username": username,
            "subscription_tier": subscription_tier
        }
    })
    
    # Trial end date (14 days from now)
    trial_end = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
    
    # Create user data
    users[username] = {
        "password": password,  # In a real app, this would be hashed
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "role": role,
        "subscription_tier": subscription_tier,
        "subscription_active": True,  # Active during free trial
        "subscription_renewal_date": trial_end,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "last_login": None,
        "stripe_customer_id": customer_id,
        "free_trial": free_trial,
        "free_trial_end": trial_end if free_trial else None,
        "payment_method": None,
        "has_payment_method": False
    }
    
    save_users(users)
    return True, "User created successfully"

def render_signup_page():
    """Render the enhanced signup page with free trial option"""
    st.title("Create Your DataGuardian Pro Account")
    
    # Custom CSS for better presentation
    st.markdown("""
    <style>
    .signup-container {
        background: white;
        border-radius: 16px;
        padding: 35px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        max-width: 800px;
        margin: 0 auto;
    }
    
    .plan-card {
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 20px;
        height: 100%;
        background-color: white;
    }
    
    .plan-card.selected {
        border: 2px solid #4f46e5;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
    }
    
    .google-signup-button {
        background-color: white;
        border: 1px solid #e2e8f0;
        color: #333333;
        padding: 14px 24px;
        border-radius: 12px;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin: 15px 0;
        width: 100%;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        font-size: 1rem;
    }
    
    .google-signup-button:hover {
        background-color: #f8f9fa;
        border-color: #c1c7cd;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }
    
    .form-header {
        text-align: center;
        color: #1a202c;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 20px;
    }
    
    .divider {
        display: flex;
        align-items: center;
        text-align: center;
        margin: 30px 0;
    }
    
    .divider::before,
    .divider::after {
        content: '';
        flex: 1;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .divider-text {
        padding: 0 10px;
        color: #a0aec0;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Signup container
    st.markdown('<div class="signup-container">', unsafe_allow_html=True)
    
    # Google signup button
    st.markdown("""
    <h2 class="form-header">Create your account</h2>
    
    <button class="google-signup-button">
        <img src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg" 
             style="height: 20px; margin-right: 12px; vertical-align: middle;"> 
        Sign up with Google
    </button>
    
    <div class="divider"><span class="divider-text">OR SIGN UP WITH EMAIL</span></div>
    """, unsafe_allow_html=True)
    
    # Email registration form
    with st.form("signup_form"):
        # Personal information
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name", key="first_name", placeholder="Enter your first name")
        with col2:
            last_name = st.text_input("Last Name", key="last_name", placeholder="Enter your last name")
        
        email = st.text_input("Email Address", key="email", placeholder="Enter your email address")
        
        # Account credentials
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("Username", key="username", placeholder="Choose a username")
        with col2:
            password = st.text_input("Password", type="password", key="password", placeholder="Choose a strong password")
        
        # Confirm password with strength indicator
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password", placeholder="Re-enter your password")
        
        # Subscription plan selection
        st.markdown("### Choose Your Plan")
        plan_tier = st.selectbox(
            "Select Plan",
            list(SUBSCRIPTION_PLANS.keys()),
            format_func=lambda k: f"{SUBSCRIPTION_PLANS[k]['name']} (€{SUBSCRIPTION_PLANS[k]['price']})",
            index=0
        )
        
        selected_plan = SUBSCRIPTION_PLANS[plan_tier]
        
        # Display selected plan details
        st.markdown(f"""
        <div class="plan-card selected">
            <div style="text-align:center; margin-bottom:10px;">
                <span style="font-size:24px;">{selected_plan.get('icon', '✨')}</span>
            </div>
            <h3 style="text-align:center; margin:5px 0; font-size:18px;">
                {selected_plan.get('name', 'Basic')} Plan
            </h3>
            <div style="text-align:center; font-size:24px; font-weight:bold; margin:15px 0;">
                €{selected_plan.get('price', 0)}
                <span style="font-size:14px; font-weight:normal; color:#718096;">
                    /{selected_plan.get('unit', 'month')}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Free trial option
        free_trial = st.checkbox("Start with 14-day free trial", value=True)
        
        # Terms and conditions
        terms_agreed = st.checkbox("I agree to the Terms of Service and Privacy Policy")
        
        # Marketing consent
        marketing_consent = st.checkbox("I want to receive emails about product updates and promotions")
        
        # Submit button
        submit_button = st.form_submit_button("Create Account", use_container_width=True)
        
        if submit_button:
            # Validate inputs
            if not first_name or not last_name or not email or not username or not password or not confirm_password:
                st.error("Please fill in all required fields.")
            elif not validate_email(email):
                st.error("Please enter a valid email address.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            elif not terms_agreed:
                st.error("You must agree to the Terms of Service and Privacy Policy.")
            else:
                # Validate password strength
                password_valid, password_message = validate_password(password)
                if not password_valid:
                    st.error(password_message)
                else:
                    # Create user
                    success, message = create_user(
                        username=username,
                        password=password,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        subscription_tier=plan_tier,
                        free_trial=free_trial
                    )
                    
                    if success:
                        st.session_state.signup_success = True
                        st.session_state.new_username = username
                        st.session_state.new_email = email
                        st.session_state.selected_plan = plan_tier
                        st.success("Account created successfully! Your 14-day free trial has started.")
                        
                        # Show what happens next
                        st.markdown("""
                        ### What happens next?
                        
                        1. You can now log in with your new account
                        2. Explore DataGuardian Pro during your free trial
                        3. Before your trial expires, you'll be prompted to add a payment method
                        """)
                        
                        # Login button
                        if st.button("Log in now"):
                            st.session_state.current_view = "login"
                            st.rerun()
                    else:
                        st.error(message)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_trial_expiry_notice():
    """Render notice when free trial is about to expire"""
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        return
    
    # Check if user is on free trial
    username = st.session_state.get("username", "")
    if not username:
        return
        
    users = load_users()
    if username not in users:
        return
    
    user_data = users[username]
    if not user_data.get("free_trial", False):
        return
    
    # Check if trial is about to expire
    trial_end = user_data.get("free_trial_end")
    if not trial_end:
        return
    
    trial_end_date = datetime.strptime(trial_end, "%Y-%m-%d")
    days_left = (trial_end_date - datetime.now()).days
    
    if days_left <= 3 and days_left >= 0:
        st.warning(f"""
        ### Your free trial expires in {days_left} days
        
        Add a payment method now to continue your subscription without interruption.
        """)
        
        if st.button("Add Payment Method"):
            st.session_state.current_view = "payment_method"
            st.rerun()
    elif days_left < 0 and not user_data.get("has_payment_method", False):
        st.error("""
        ### Your free trial has expired
        
        Add a payment method now to continue using DataGuardian Pro.
        """)
        
        if st.button("Add Payment Method Now"):
            st.session_state.current_view = "payment_method"
            st.rerun()

def render_payment_method_selection():
    """Render payment method selection for a specific plan"""
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.warning("Please log in to add a payment method.")
        return
    
    username = st.session_state.get("username", "")
    if not username:
        st.error("Username not found in session")
        return
        
    users = load_users()
    if username not in users:
        st.error("User not found")
        return
    
    user_data = users[username]
    
    st.title("Add Payment Method")
    
    # Plan information
    plan_tier = user_data.get("subscription_tier", "basic")
    plan = SUBSCRIPTION_PLANS.get(plan_tier, SUBSCRIPTION_PLANS["basic"])
    
    st.markdown(f"""
    ### {plan.get('name', 'Basic')} Plan - €{plan.get('price', 0)}/{plan.get('unit', 'month')}
    
    Please select your preferred payment method:
    """)
    
    # Payment method selection
    payment_method = st.radio(
        "Payment Method",
        ["Credit Card (VISA)", "iDEAL (Netherlands)"],
        horizontal=True
    )
    
    payment_methods = []
    if payment_method == "Credit Card (VISA)":
        payment_methods = ["card"]
        st.info("You'll be redirected to our secure payment processor to enter your credit card details.")
    else:  # iDEAL
        payment_methods = ["ideal"]
        st.info("You'll be redirected to your bank's iDEAL payment page to complete the subscription.")
    
    # Get stripe customer ID
    customer_id = user_data.get("stripe_customer_id", "")
    if not customer_id:
        st.error("Error retrieving customer information. Please contact support.")
        return
    
    # Get price ID for the selected plan
    price_id = plan.get("stripe_price_id", "")
    if not price_id:
        st.error("Error retrieving plan information. Please contact support.")
        return
    
    # Create checkout button
    if st.button("Continue to Payment", type="primary"):
        # Get currency from plan data
        currency = plan.get("currency", "EUR")
        
        checkout_url = create_checkout_session(
            customer_id, 
            price_id, 
            payment_methods=payment_methods,
            currency=currency.lower()  # Stripe prefers lowercase currency codes
        )
        
        if checkout_url:
            st.markdown(f"[Click here to complete your payment]({checkout_url})")
            st.info("You'll be redirected to our secure payment processor.")
            
            # Update user data
            users[username]["payment_method"] = payment_method
            save_users(users)
        else:
            st.error("Error creating checkout session. Please try again or contact support.")