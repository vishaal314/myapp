"""
Enhanced Signup Flow for DataGuardian Pro

This module provides a complete end-to-end signup experience including:
- Google authentication integration
- Traditional email signup option
- Free trial option
- Payment method selection (VISA/iDEAL)
- Subscription plan selection
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

# Import user management functions
from access_control.user_management import (
    load_users, 
    save_users, 
    create_user,
    hash_password
)

# Import Google authentication
from access_control.google_auth import (
    signup_with_google,
    get_google_auth_url
)

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

def render_enhanced_signup_page():
    """Render the enhanced signup page with Google authentication and free trial"""
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
    
    .google-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 12px 16px;
        background-color: white;
        color: #333;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        width: 100%;
        text-decoration: none;
        font-weight: 500;
        transition: all 0.2s ease;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    .google-btn:hover {
        background-color: #f8f9fa;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    .google-btn img {
        height: 24px;
        margin-right: 12px;
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
    
    # Header
    st.markdown('<h2 class="form-header">Create your account</h2>', unsafe_allow_html=True)
    
    # Step indicator - steps to complete signup
    steps = ["Choose Plan", "Create Account", "Payment Details"]
    current_step = st.session_state.get("signup_step", 1)
    
    # Render the step indicator
    cols = st.columns(len(steps))
    for i, step in enumerate(steps, 1):
        with cols[i-1]:
            if i < current_step:
                st.markdown(f"<div style='text-align:center;'><strong style='color:#4f46e5;'>✓ {step}</strong></div>", unsafe_allow_html=True)
            elif i == current_step:
                st.markdown(f"<div style='text-align:center;'><strong style='color:#4f46e5;'>{step}</strong></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align:center; color:#a0aec0;'>{step}</div>", unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # STEP 1: Choose Plan
    if current_step == 1:
        st.subheader("Select Your Plan")
        
        # Create 3 columns for the 3 plans
        cols = st.columns(3)
        
        # Store all plan tiers in a list
        plan_tiers = list(SUBSCRIPTION_PLANS.keys())
        
        # Default selected plan
        if "selected_plan_tier" not in st.session_state:
            st.session_state.selected_plan_tier = plan_tiers[1]  # Default to second plan (professional)
        
        # Display each plan with options to select
        for i, plan_tier in enumerate(plan_tiers):
            plan = SUBSCRIPTION_PLANS[plan_tier]
            with cols[i]:
                # Create a card for each plan
                is_selected = st.session_state.selected_plan_tier == plan_tier
                card_class = "plan-card selected" if is_selected else "plan-card"
                
                st.markdown(f"""
                <div class="{card_class}">
                    <div style="text-align:center; margin-bottom:10px;">
                        <span style="font-size:24px;">{plan.get('icon', '✨')}</span>
                    </div>
                    <h3 style="text-align:center; margin:5px 0; font-size:18px;">{plan.get('name', 'Basic')} Plan</h3>
                    <div style="text-align:center; font-size:24px; font-weight:bold; margin:15px 0;">
                        €{plan.get('price', 0)}
                        <span style="font-size:14px; font-weight:normal; color:#718096;">/{plan.get('unit', 'month')}</span>
                    </div>
                    <div style="margin-top:15px; margin-bottom:20px;">
                        <ul style="padding-left:20px; margin-top:0px;">
                """, unsafe_allow_html=True)
                
                # List features
                for feature in plan.get('features', []):
                    st.markdown(f'<li style="margin-bottom:8px; font-size:14px;">{feature}</li>', unsafe_allow_html=True)
                
                st.markdown('</ul></div>', unsafe_allow_html=True)
                
                # Add a select button
                select_button_text = "Selected" if is_selected else "Select Plan"
                select_button_style = "primary" if is_selected else "secondary"
                
                if is_selected:
                    st.button(select_button_text, key=f"select_plan_{plan_tier}", disabled=True, use_container_width=True)
                else:
                    if st.button(select_button_text, key=f"select_plan_{plan_tier}", use_container_width=True):
                        st.session_state.selected_plan_tier = plan_tier
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Free trial option
        st.markdown("<div style='margin-top:20px;'>", unsafe_allow_html=True)
        if "free_trial" not in st.session_state:
            st.session_state.free_trial = True
            
        st.session_state.free_trial = st.checkbox("Start with 14-day free trial", value=st.session_state.free_trial)
        
        # Continue button
        if st.button("Continue to Account Creation", use_container_width=True, type="primary"):
            st.session_state.signup_step = 2
            st.rerun()
    
    # STEP 2: Create Account
    elif current_step == 2:
        st.subheader("Create Your Account")
        
        # Check if Google OAuth is configured
        import os
        google_oauth_configured = bool(os.environ.get("GOOGLE_CLIENT_ID") and os.environ.get("GOOGLE_CLIENT_SECRET"))
        
        if google_oauth_configured:
            # Google signup button with OAuth available
            google_auth_url = get_google_auth_url()
            st.markdown(f"""
            <a href="{google_auth_url}" class="google-btn">
                <img src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg" 
                     alt="Google logo"> 
                Sign up with Google
            </a>
            
            <div class="divider"><span class="divider-text">OR SIGN UP WITH EMAIL</span></div>
            """, unsafe_allow_html=True)
        else:
            # Show a simplified header for email signup
            st.markdown("""
            <div style="text-align: center; margin-bottom: 20px;">
                <h3 style="font-size: 1.1rem; color: #4a5568;">Create your account with email</h3>
            </div>
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
            
            # Selected plan display
            selected_plan_tier = st.session_state.get("selected_plan_tier", "basic")
            selected_plan = SUBSCRIPTION_PLANS[selected_plan_tier]
            
            st.markdown(f"""
            <div style="margin-top: 20px; padding: 15px; border-radius: 8px; background-color: #f7fafc; border: 1px solid #e2e8f0;">
                <h4 style="margin-top: 0px;">Selected Plan: {selected_plan.get('name', 'Basic')}</h4>
                <p style="margin-bottom: 10px;">€{selected_plan.get('price', 0)}/{selected_plan.get('unit', 'month')}</p>
                <p style="margin-bottom: 0px; font-size: 14px; color: #4a5568;">
                    {f"Includes a 14-day free trial." if st.session_state.get("free_trial", True) else ""}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
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
                            email=email,
                            password=password,
                            first_name=first_name,
                            last_name=last_name,
                            subscription_tier=selected_plan_tier,
                            free_trial=st.session_state.get("free_trial", True)
                        )
                        
                        if success:
                            st.session_state.signup_success = True
                            st.session_state.new_username = username
                            st.session_state.new_email = email
                            st.session_state.signup_step = 3
                            st.success("Account created successfully!")
                            st.rerun()
                        else:
                            st.error(message)
                            
        # Add "Forgot Password" link below the form
        st.markdown("""
        <div style="text-align: center; margin-top: 20px;">
            <p style="font-size: 14px; color: #4a5568;">
                Already have an account but <a href="#forgot_password" style="color: #4f46e5; text-decoration: none;">forgot your password?</a>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Check if the "Forgot password?" link was clicked
        if "forgot_password" in st.query_params:
            st.session_state.current_view = "password_reset"
            st.rerun()
        
        # Back button to return to Plan Selection
        if st.button("Back to Plan Selection"):
            st.session_state.signup_step = 1
            st.rerun()
    
    # STEP 3: Payment Details
    elif current_step == 3:
        st.subheader("Add Payment Method")
        
        # Show selected plan again
        selected_plan_tier = st.session_state.get("selected_plan_tier", "basic")
        selected_plan = SUBSCRIPTION_PLANS[selected_plan_tier]
        
        st.markdown(f"""
        <div style="margin-bottom: 25px; padding: 15px; border-radius: 8px; background-color: #f7fafc; border: 1px solid #e2e8f0;">
            <h4 style="margin-top: 0px;">Selected Plan: {selected_plan.get('name', 'Basic')}</h4>
            <p style="margin-bottom: 10px;">€{selected_plan.get('price', 0)}/{selected_plan.get('unit', 'month')}</p>
            <p style="margin-bottom: 0px; font-size: 14px; color: #4a5568;">
                {f"Your 14-day free trial has started. You won't be charged until the trial ends." if st.session_state.get("free_trial", True) else ""}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Payment method selection
        st.markdown("### Select Payment Method")
        
        payment_method = st.radio(
            "Payment Method",
            ["Credit Card (VISA)", "iDEAL (Netherlands)"],
            horizontal=True
        )
        
        # Show appropriate payment form
        if payment_method == "Credit Card (VISA)":
            st.info("You'll be redirected to our secure payment processor to enter your credit card details.")
            payment_methods = ["card"]
        else:  # iDEAL
            st.info("You'll be redirected to your bank's iDEAL payment page to complete the subscription.")
            payment_methods = ["ideal"]
        
        # Process payment button
        username = st.session_state.get("new_username")
        
        if username:
            users = load_users()
            if username in users:
                user_data = users[username]
                
                # Get stripe customer ID
                customer_id = user_data.get("stripe_customer_id", "")
                if not customer_id:
                    st.error("Error retrieving customer information. Please contact support.")
                else:
                    # Get price ID for the selected plan
                    price_id = selected_plan.get("stripe_price_id", "")
                    if not price_id:
                        st.error("Error retrieving plan information. Please contact support.")
                    else:
                        # Create checkout button
                        if st.button("Continue to Payment", type="primary", use_container_width=True):
                            # Get currency from plan data
                            currency = selected_plan.get("currency", "EUR")
                            
                            from billing.stripe_integration import create_checkout_session
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
                                
                                # Success notification for completing entire flow
                                st.success("Your account has been created successfully and your free trial has started!")
                                
                                # Offer option to go to dashboard
                                if st.button("Go to Dashboard"):
                                    # Log the user in
                                    st.session_state.logged_in = True
                                    st.session_state.username = username
                                    st.session_state.user_data = user_data
                                    st.session_state.current_view = "dashboard"
                                    
                                    # Reset signup flow
                                    if "signup_step" in st.session_state:
                                        del st.session_state.signup_step
                                    if "selected_plan_tier" in st.session_state:
                                        del st.session_state.selected_plan_tier
                                    
                                    st.rerun()
                            else:
                                st.error("Error creating checkout session. Please try again or contact support.")
                                
        # Skip payment option during free trial
        if st.session_state.get("free_trial", True):
            st.markdown("<p style='text-align:center; margin-top:20px;'>or</p>", unsafe_allow_html=True)
            if st.button("Skip for now (Add payment method later)", use_container_width=True):
                # Load users again to make sure we have the latest data
                users = load_users()
                if username and username in users:
                    # Log the user in
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.user_data = users[username]
                    st.session_state.current_view = "dashboard"
                else:
                    st.error("Error retrieving user information. Please try again.")
                
                # Reset signup flow
                if "signup_step" in st.session_state:
                    del st.session_state.signup_step
                if "selected_plan_tier" in st.session_state:
                    del st.session_state.selected_plan_tier
                
                st.rerun()
        
        # Back button to return to Account Creation
        if st.button("Back to Account Creation"):
            st.session_state.signup_step = 2
            st.rerun()
    
    # Close container div
    st.markdown('</div>', unsafe_allow_html=True)

def render_login_page():
    """Render the login page with Google authentication option"""
    st.title("Log In to DataGuardian Pro")
    
    # Custom CSS for better presentation
    st.markdown("""
    <style>
    .login-container {
        background: white;
        border-radius: 16px;
        padding: 35px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        max-width: 500px;
        margin: 0 auto;
    }
    
    .google-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 12px 16px;
        background-color: white;
        color: #333;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        width: 100%;
        text-decoration: none;
        font-weight: 500;
        transition: all 0.2s ease;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    .google-btn:hover {
        background-color: #f8f9fa;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    .google-btn img {
        height: 24px;
        margin-right: 12px;
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
    
    # Login container
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Header
    st.markdown('<h2 class="form-header">Log in to your account</h2>', unsafe_allow_html=True)
    
    # Google login button
    google_auth_url = get_google_auth_url()
    st.markdown(f"""
    <a href="{google_auth_url}" class="google-btn">
        <img src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg" 
             alt="Google logo"> 
        Log in with Google
    </a>
    
    <div class="divider"><span class="divider-text">OR LOG IN WITH EMAIL</span></div>
    """, unsafe_allow_html=True)
    
    # Traditional login form
    with st.form("login_form"):
        username = st.text_input("Username or Email", placeholder="Enter your username or email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        # Remember me checkbox
        remember_me = st.checkbox("Remember me")
        
        # Submit button
        submit_button = st.form_submit_button("Log In", use_container_width=True)
        
        if submit_button:
            if not username or not password:
                st.error("Please enter both username and email.")
            else:
                # Authenticate user
                from access_control.user_management import authenticate_user, get_permissions_for_role
                
                try:
                    success, user_data = authenticate_user(username, password)
                    
                    if success and user_data:
                        # Set login session state
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.user_data = user_data
                        
                        # Set role and permissions
                        role = user_data.get("role", "user")
                        permissions = get_permissions_for_role(role)
                        st.session_state.user_role = role
                        st.session_state.user_permissions = permissions
                        
                        first_name = user_data.get('first_name', username)
                        st.success(f"Welcome back, {first_name}!")
                        
                        # Redirect to dashboard only if login successful
                        st.session_state.current_view = "dashboard"
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
                except Exception as e:
                    st.error(f"An error occurred during login: {str(e)}")
    
    # Password reset and signup links
    st.markdown("""
    <div style="display: flex; justify-content: space-between; margin-top: 15px;">
        <a href="#" style="color: #4f46e5; text-decoration: none; font-size: 14px;">Forgot password?</a>
        <span style="font-size: 14px;">
            Don't have an account? <a href="#" id="signup-link" style="color: #4f46e5; text-decoration: none;">Sign up</a>
        </span>
    </div>
    
    <script>
        document.getElementById('signup-link').addEventListener('click', function(e) {
            e.preventDefault();
            window.location.hash = 'signup';
        });
    </script>
    """, unsafe_allow_html=True)
    
    # "Sign up" button handler
    if st.button("Create new account"):
        st.session_state.current_view = "signup"
        if "signup_step" in st.session_state:
            del st.session_state.signup_step
        st.rerun()
    
    # Close container div
    st.markdown('</div>', unsafe_allow_html=True)