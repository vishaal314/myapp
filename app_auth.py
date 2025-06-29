"""
Authentication Module - Extracted from main app.py

Handles all authentication, registration, and user management functionality
to reduce complexity in the main application file.
"""

import streamlit as st
import hashlib
import json
import os
from datetime import datetime
from services.auth import authenticate, is_authenticated, logout, create_user, validate_email, get_user_permissions
from utils.i18n import get_text, set_language

def _(key, default=None):
    """Translation function"""
    return get_text(key, default)

def show_login_page():
    """Display login page"""
    st.markdown("### Login")
    
    # Create login form
    with st.form("login_form"):
        username_or_email = st.text_input("Username or Email")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")
        
        if login_button:
            if username_or_email and password:
                user_data = authenticate(username_or_email, password)
                if user_data:
                    st.session_state.authenticated = True
                    st.session_state.username = user_data['username']
                    st.session_state.user_email = user_data['email']
                    st.session_state.user_role = user_data.get('role', 'user')
                    
                    # Set premium status based on role
                    st.session_state.premium_member = user_data.get('role') in ['premium_user', 'enterprise_user', 'admin']
                    
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username/email or password")
            else:
                st.error("Please enter both username/email and password")

def show_registration_page():
    """Display registration page"""
    st.markdown("### Register")
    
    # Define role options
    role_options = {
        'user': 'Standard User - Basic scanning capabilities',
        'premium_user': 'Premium User - Advanced features and unlimited scans',
        'compliance_officer': 'Compliance Officer - Full compliance management',
        'privacy_officer': 'Privacy Officer - Complete privacy assessment tools',
        'enterprise_user': 'Enterprise User - Full enterprise features',
        'consultant': 'Privacy Consultant - Professional consulting tools',
        'admin': 'Administrator - Full system access'
    }
    
    with st.form("registration_form"):
        new_username = st.text_input("Username")
        new_email = st.text_input("Email")
        new_password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        new_role = st.selectbox("Role", options=list(role_options.keys()), 
                               format_func=lambda x: role_options[x])
        terms = st.checkbox("I agree to the Terms and Conditions")
        register_button = st.form_submit_button("Register")
        
        if register_button:
            if new_username and new_email and new_password and new_password == confirm_password and terms:
                success, message = create_user(new_username, new_password, new_role, new_email)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.error("Please fill all fields correctly and accept terms")

def show_password_reset_page():
    """Display password reset page"""
    st.markdown("### Reset Password")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Request Reset")
        reset_email = st.text_input("Email", key="reset_email_input")
        new_password = st.text_input("New Password", type="password", key="new_password_input")
        confirm_password = st.text_input("Confirm New Password", type="password", key="confirm_password_input")
        
        if st.button("Reset Password"):
            if reset_email and new_password and new_password == confirm_password:
                # Simple password reset (in production, this would require email verification)
                success, message = reset_user_password(reset_email, new_password)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.error("Please fill all fields correctly")
    
    with col2:
        st.markdown("#### Help")
        st.info("For security reasons, please contact your administrator if you cannot reset your password.")

def reset_user_password(email, new_password):
    """Reset user password (simplified version)"""
    try:
        # In production, this would require proper email verification
        # For demo purposes, we'll implement a basic reset
        
        # Load users
        users_file = "users.json"
        if os.path.exists(users_file):
            with open(users_file, 'r') as f:
                users = json.load(f)
        else:
            return False, "User database not found"
        
        # Find user by email
        user_found = False
        for username, user_data in users.items():
            if user_data.get('email') == email:
                # Hash the new password
                password_hash = hashlib.sha256(new_password.encode()).hexdigest()
                users[username]['password'] = password_hash
                user_found = True
                break
        
        if not user_found:
            return False, "Email not found"
        
        # Save updated users
        with open(users_file, 'w') as f:
            json.dump(users, f, indent=2)
        
        return True, "Password reset successfully"
        
    except Exception as e:
        return False, f"Error resetting password: {str(e)}"

def show_user_profile():
    """Display user profile information"""
    if not st.session_state.get('authenticated', False):
        st.error("Please login to view your profile")
        return
    
    st.markdown("### User Profile")
    
    current_user = st.session_state.get('username', 'Unknown')
    user_email = st.session_state.get('user_email', 'Unknown')
    user_role = st.session_state.get('user_role', 'user')
    
    # Display user information
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Account Information")
        st.write(f"**Username:** {current_user}")
        st.write(f"**Email:** {user_email}")
        st.write(f"**Role:** {user_role.replace('_', ' ').title()}")
    
    with col2:
        st.markdown("#### Role Permissions")
        user_permissions = get_user_permissions(user_role)
        if user_permissions:
            permissions_by_category = {}
            for perm in user_permissions:
                category = perm.split(':')[0]
                if category not in permissions_by_category:
                    permissions_by_category[category] = []
                permissions_by_category[category].append(perm)
            
            for category, perms in permissions_by_category.items():
                st.write(f"**{category.title()}:**")
                for perm in perms:
                    st.write(f"  • {perm}")

def handle_authentication():
    """Main authentication handler"""
    if not st.session_state.get('authenticated', False):
        # Show authentication interface
        auth_tabs = st.tabs(["Login", "Register", "Reset Password"])
        
        with auth_tabs[0]:
            show_login_page()
        
        with auth_tabs[1]:
            show_registration_page()
        
        with auth_tabs[2]:
            show_password_reset_page()
        
        return False
    
    return True

def cleanup_session_state():
    """Clean up session state on logout"""
    # Preserve language settings
    preserved_language = st.session_state.get('language', 'en')
    
    # Clear authentication-related session state
    auth_keys = ['authenticated', 'username', 'user_email', 'user_role', 'premium_member']
    for key in auth_keys:
        if key in st.session_state:
            del st.session_state[key]
    
    # Clear scan-related session state
    scan_keys = [key for key in st.session_state.keys() if key.startswith(('scan_', 'dpia_', 'simple_dpia_'))]
    for key in scan_keys:
        del st.session_state[key]
    
    # Restore language
    st.session_state['language'] = preserved_language
    st.session_state['force_language_after_login'] = preserved_language

def show_logout_option():
    """Show logout option in sidebar"""
    if st.session_state.get('authenticated', False):
        if st.sidebar.button("Logout", key="logout_button"):
            cleanup_session_state()
            st.success("Logged out successfully")
            st.rerun()