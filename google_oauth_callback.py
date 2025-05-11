"""
Google OAuth Callback Handler

This script handles OAuth callbacks from Google authentication.
It parses the authorization code from the URL and processes the
OAuth flow to retrieve user information and create/authenticate users.
"""

import streamlit as st
from urllib.parse import urlparse, parse_qs

from access_control.google_auth import (
    handle_google_callback,
    get_permissions_for_role
)

def process_google_oauth_callback():
    """
    Process Google OAuth callback parameters from URL

    This function extracts the authorization code and state from the URL
    and completes the OAuth flow.

    Returns:
        True if successful authentication, False otherwise
    """
    # Get current URL parameters
    query_params = st.experimental_get_query_params()
    
    # Check if we have a code and state from Google OAuth
    code = query_params.get("code", [None])[0]
    state = query_params.get("state", [None])[0]
    
    if not code or not state:
        st.warning("Missing authentication parameters. Please try again.")
        return False
    
    # Process the Google callback
    success, message, user_data = handle_google_callback(code, state)
    
    if success and user_data:
        # Set session state for authenticated user
        st.session_state.logged_in = True
        st.session_state.username = user_data.get("username")
        st.session_state.user_data = user_data
        
        # Set user role and permissions
        role = user_data.get("role", "user")
        permissions = get_permissions_for_role(role)
        st.session_state.user_role = role
        st.session_state.user_permissions = permissions
        
        # Add subscription data to session state
        st.session_state.subscription_tier = user_data.get("subscription_tier", "basic")
        st.session_state.subscription_active = user_data.get("subscription_active", True)
        st.session_state.stripe_customer_id = user_data.get("stripe_customer_id")
        st.session_state.subscription_id = user_data.get("subscription_id")
        st.session_state.user_id = user_data.get("user_id")
        st.session_state.subscription_renewal_date = user_data.get("subscription_renewal_date")
        
        # Redirect to dashboard
        st.session_state.current_view = "dashboard"
        st.success(f"Welcome, {user_data.get('first_name', user_data.get('username'))}!")
        
        # If this is a new user, consider redirecting to a welcome page or tutorial
        if user_data.get("is_new_user", False):
            st.session_state.show_welcome = True
        
        return True
    else:
        st.error(f"Authentication failed: {message}")
        return False