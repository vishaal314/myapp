"""
Google OAuth Authentication Module for DataGuardian Pro

This module provides Google Sign-In functionality for the application, including:
- OAuth 2.0 flow implementation
- User profile retrieval from Google
- Account linking with existing users
- Creation of new accounts with Google profiles
"""

import os
import json
import requests
import uuid
import hashlib
import time
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple

# Import user management functions
from access_control.user_management import load_users, save_users, get_permissions_for_role

# Import billing components
from billing.stripe_integration import create_stripe_customer

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("REDIRECT_URI", "http://localhost:5000/")

# OAuth endpoints
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

def get_google_auth_url() -> str:
    """
    Generate the Google OAuth authorization URL
    
    Returns:
        Google authorization URL
    """
    if not GOOGLE_CLIENT_ID:
        st.error("Google OAuth is not configured. Please set GOOGLE_CLIENT_ID in environment variables.")
        return "#"
        
    # Generate a state parameter to prevent CSRF attacks
    state = hashlib.sha256(f"{uuid.uuid4()}{time.time()}".encode()).hexdigest()
    st.session_state.oauth_state = state
    
    # Generate authorization URL
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "prompt": "select_account"  # Always show account selector
    }
    
    # Build the URL with query parameters
    auth_url = f"{GOOGLE_AUTH_URL}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
    return auth_url

def exchange_code_for_token(code: str) -> Optional[Dict[str, Any]]:
    """
    Exchange authorization code for access token
    
    Args:
        code: Authorization code from Google
        
    Returns:
        Token response dictionary or None if failed
    """
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        st.error("Google OAuth is not fully configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.")
        return None
        
    try:
        # Prepare token request
        token_params = {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI
        }
        
        # Make token request
        response = requests.post(GOOGLE_TOKEN_URL, data=token_params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error exchanging authorization code: {str(e)}")
        return None

def get_user_info(access_token: str) -> Optional[Dict[str, Any]]:
    """
    Get user information from Google using access token
    
    Args:
        access_token: Google OAuth access token
        
    Returns:
        User information dictionary or None if failed
    """
    try:
        # Make user info request
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(GOOGLE_USER_INFO_URL, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error getting user information: {str(e)}")
        return None

def find_user_by_google_id(google_id: Optional[str]) -> Optional[Tuple[str, Dict[str, Any]]]:
    """
    Find a user by their Google ID
    
    Args:
        google_id: Google user ID
        
    Returns:
        Tuple of (username, user_data) if found, None otherwise
    """
    if not google_id:
        return None
        
    users = load_users()
    
    for username, user_data in users.items():
        if user_data.get("google_id") == google_id:
            return username, user_data
    
    return None

def find_user_by_email(email: str) -> Optional[Tuple[str, Dict[str, Any]]]:
    """
    Find a user by their email
    
    Args:
        email: User email
        
    Returns:
        Tuple of (username, user_data) if found, None otherwise
    """
    users = load_users()
    
    for username, user_data in users.items():
        if user_data.get("email") == email:
            return username, user_data
    
    return None

def create_user_from_google(
    user_info: Dict[str, Any],
    subscription_tier: str = "basic",
    free_trial: bool = True
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Create a new user from Google profile information
    
    Args:
        user_info: Google user information
        subscription_tier: Subscription tier for the new user
        free_trial: Whether to start with a free trial
        
    Returns:
        Tuple of (success, message, user_data)
    """
    users = load_users()
    
    # Extract user information from Google profile
    google_id = user_info.get("sub")
    email = user_info.get("email")
    
    if not google_id or not email:
        return False, "Incomplete user information from Google", None
    
    # Check if user with this Google ID already exists
    existing_user = find_user_by_google_id(google_id)
    if existing_user:
        username, user_data = existing_user
        return False, f"User with this Google account already exists as {username}", user_data
    
    # Check if user with this email already exists
    existing_email = find_user_by_email(email)
    if existing_email:
        username, user_data = existing_email
        # Link Google ID to existing account
        users[username]["google_id"] = google_id
        users[username]["google_profile"] = {
            "name": user_info.get("name"),
            "given_name": user_info.get("given_name"),
            "family_name": user_info.get("family_name"),
            "picture": user_info.get("picture")
        }
        save_users(users)
        return True, f"Google account linked to existing user {username}", users[username]
    
    # Create a new username from email
    base_username = email.split("@")[0].lower()
    username = base_username
    
    # Make sure username is unique
    suffix = 1
    while username in users:
        username = f"{base_username}{suffix}"
        suffix += 1
    
    # Create Stripe customer
    first_name = user_info.get("given_name", "")
    last_name = user_info.get("family_name", "")
    full_name = user_info.get("name", f"{first_name} {last_name}")
    
    customer_id = create_stripe_customer({
        "email": email,
        "name": full_name,
        "metadata": {
            "username": username,
            "subscription_tier": subscription_tier,
            "google_id": google_id
        }
    })
    
    # Create random password for Google users (they'll login via Google)
    random_password = hashlib.sha256(f"{uuid.uuid4()}".encode()).hexdigest()
    password_hash = hashlib.sha256(random_password.encode()).hexdigest()
    
    # Prepare new user data
    from datetime import datetime, timedelta
    trial_end = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
    
    users[username] = {
        "email": email,
        "password_hash": password_hash,  # Random password for fallback login
        "first_name": first_name,
        "last_name": last_name,
        "role": "user",
        "subscription_tier": subscription_tier,
        "subscription_active": True,  # Active during free trial
        "subscription_renewal_date": trial_end,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "last_login": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "stripe_customer_id": customer_id,
        "free_trial": free_trial,
        "free_trial_end": trial_end if free_trial else None,
        "payment_method": None,
        "has_payment_method": False,
        "google_id": google_id,
        "google_profile": {
            "name": user_info.get("name"),
            "given_name": user_info.get("given_name"),
            "family_name": user_info.get("family_name"),
            "picture": user_info.get("picture")
        }
    }
    
    save_users(users)
    return True, f"New user {username} created from Google profile", users[username]

def handle_google_callback(code: str, state: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Handle Google OAuth callback
    
    Args:
        code: Authorization code from Google
        state: State parameter for CSRF protection
        
    Returns:
        Tuple of (success, message, user_data)
    """
    # Verify state parameter to prevent CSRF attacks
    if "oauth_state" not in st.session_state or st.session_state.oauth_state != state:
        return False, "Invalid state parameter", None
    
    # Exchange code for token
    token_data = exchange_code_for_token(code)
    if not token_data or "access_token" not in token_data:
        return False, "Failed to get access token", None
    
    # Get user information
    access_token = token_data["access_token"]
    user_info = get_user_info(access_token)
    if not user_info:
        return False, "Failed to get user information", None
    
    # Check if user with this Google ID exists
    google_id = user_info.get("sub")
    # Make sure google_id is a string or None
    google_id_str = str(google_id) if google_id is not None else None
    existing_user = find_user_by_google_id(google_id_str)
    
    if existing_user:
        username, user_data = existing_user
        # Update last login time
        users = load_users()
        users[username]["last_login"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_users(users)
        return True, f"Logged in as {username}", users[username]
    
    # Check if we're in a signup flow
    if "signup_with_google" in st.session_state and st.session_state.signup_with_google:
        # Get plan tier from session if available
        plan_tier = st.session_state.get("selected_plan_tier", "basic")
        free_trial = st.session_state.get("free_trial", True)
        
        # Create new user
        success, message, user_data = create_user_from_google(
            user_info,
            subscription_tier=plan_tier,
            free_trial=free_trial
        )
        
        # Clear signup state
        st.session_state.signup_with_google = False
        
        return success, message, user_data
    
    # If not in signup flow, create a basic account
    return create_user_from_google(user_info)

def login_with_google() -> Dict[str, Any]:
    """
    Login button and OAuth flow for Google authentication
    
    Returns:
        Dictionary with rendered elements
    """
    auth_url = get_google_auth_url()
    
    # Check for authentication code in query parameters
    query_params = st.experimental_get_query_params()
    if "code" in query_params and "state" in query_params:
        code = query_params["code"][0]
        state = query_params["state"][0]
        
        with st.spinner("Authenticating with Google..."):
            success, message, user_data = handle_google_callback(code, state)
            
            # Clear query parameters
            st.experimental_set_query_params()
            
            if success and user_data:
                # Set login session state
                st.session_state.logged_in = True
                st.session_state.username = list(user_data.keys())[0]  # Get username
                st.session_state.user_data = user_data
                
                # Set role and permissions
                role = user_data.get("role", "user")
                permissions = get_permissions_for_role(role)
                st.session_state.user_role = role
                st.session_state.user_permissions = permissions
                
                st.success(f"Successfully logged in as {st.session_state.username}")
                time.sleep(1)
                st.rerun()
            else:
                st.error(message)
    
    # Render button with proper authentication URL
    markup = f'<a href="{auth_url}" class="google-btn">Sign in with Google</a>'
    return {"auth_url": auth_url, "markup": markup}

def signup_with_google(plan_tier: str = "basic", free_trial: bool = True) -> Dict[str, Any]:
    """
    Signup button and OAuth flow for Google authentication
    
    Args:
        plan_tier: Subscription tier for the new user
        free_trial: Whether to start with a free trial
        
    Returns:
        Dictionary with rendered elements
    """
    # Store signup information in session
    st.session_state.signup_with_google = True
    st.session_state.selected_plan_tier = plan_tier
    st.session_state.free_trial = free_trial
    
    # Get authentication URL
    auth_url = get_google_auth_url()
    
    # Render button with proper authentication URL
    markup = f'<a href="{auth_url}" class="google-btn">Sign up with Google</a>'
    return {"auth_url": auth_url, "markup": markup}