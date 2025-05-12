"""
Password Reset Flow for DataGuardian Pro

This module provides a complete workflow for password reset:
- Request password reset by email
- Validate reset token
- Set new password
"""

import streamlit as st
import re
from typing import Dict, Any, Optional

# Import user management functions
from access_control.user_management import (
    generate_password_reset_token,
    send_password_reset_email,
    verify_reset_token,
    reset_password,
    get_permissions_for_role
)

def run_password_reset_flow():
    """
    Main entry point for the password reset flow
    """
    # Initialize session state variables if they don't exist
    if "reset_step" not in st.session_state:
        st.session_state.reset_step = 1  # 1=Request, 2=Verify, 3=Reset
    
    # Check for token in URL query parameters
    if "token" in st.query_params and st.session_state.reset_step == 1:
        token = st.query_params["token"]
        st.session_state.reset_token = token
        st.session_state.reset_step = 2
    
    # Custom CSS for better presentation
    st.markdown("""
    <style>
    .reset-container {
        background: white;
        border-radius: 16px;
        padding: 35px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        max-width: 600px;
        margin: 0 auto;
    }
    
    .form-header {
        text-align: center;
        color: #1a202c;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 20px;
    }
    
    /* Additional styles for the password reset UI */
    .back-link {
        display: block;
        text-align: center;
        margin-top: 20px;
        font-size: 14px;
        color: #4a5568;
        text-decoration: none;
    }
    
    .back-link:hover {
        color: #4f46e5;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Show appropriate step based on the session state
    if st.session_state.reset_step == 1:
        show_request_reset_form()
    elif st.session_state.reset_step == 2:
        show_verify_token_form()
    elif st.session_state.reset_step == 3:
        show_reset_password_form()
    elif st.session_state.reset_step == 4:
        show_reset_confirmation()

def show_request_reset_form():
    """Show the form to request a password reset"""
    st.markdown('<div class="reset-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="form-header">Reset Your Password</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; margin-bottom: 30px;">Enter your email address to receive a password reset link.</p>', unsafe_allow_html=True)
    
    # Email input form
    with st.form("reset_request_form"):
        email = st.text_input("Email Address", key="reset_email", placeholder="Enter your registered email address")
        submit_button = st.form_submit_button("Send Reset Link", use_container_width=True)
        
        if submit_button:
            if not email:
                st.error("Please enter your email address.")
            else:
                # Validate email format
                email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_regex, email):
                    st.error("Please enter a valid email address.")
                else:
                    # Generate reset token
                    success, message, token = generate_password_reset_token(email)
                    
                    if success and token:
                        # Create reset URL
                        # In production, this would be a proper URL, but for demo we use the current page with a token parameter
                        reset_url = f"http://localhost:5000/?token={token}"
                        
                        # Send email
                        email_sent, email_message = send_password_reset_email(email, reset_url)
                        
                        if email_sent:
                            st.session_state.reset_email = email
                            st.success("Password reset link has been sent to your email address. Please check your inbox.")
                            
                            # Display the link for demo purposes only
                            st.info(f"Since this is a demo, here's your reset link: [Reset Password]({reset_url})", icon="ℹ️")
                        else:
                            st.error(f"Failed to send email: {email_message}")
                    else:
                        st.error(message)
    
    # Back to login link
    st.markdown('<a href="/" class="back-link">Back to Login</a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def show_verify_token_form():
    """Show the form to verify the reset token"""
    token = st.session_state.get("reset_token", "")
    
    if not token:
        st.error("No reset token provided.")
        st.session_state.reset_step = 1
        st.rerun()
    
    # Verify token
    valid, message, username = verify_reset_token(token)
    
    st.markdown('<div class="reset-container">', unsafe_allow_html=True)
    
    if valid and username:
        st.markdown('<h2 class="form-header">Reset Your Password</h2>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; margin-bottom: 30px;">Your reset link is valid. Please set a new password.</p>', unsafe_allow_html=True)
        
        # Store username for the reset step
        st.session_state.reset_username = username
        
        # Move to reset password form
        st.session_state.reset_step = 3
        st.rerun()
    else:
        st.markdown('<h2 class="form-header">Invalid Reset Link</h2>', unsafe_allow_html=True)
        st.error(message)
        st.markdown('<p style="text-align: center; margin-top: 20px;">Please request a new password reset link.</p>', unsafe_allow_html=True)
        
        # Add button to go back to request form
        if st.button("Request New Reset Link", type="primary", use_container_width=True):
            st.session_state.reset_step = 1
            st.rerun()
    
    # Back to login link
    st.markdown('<a href="/" class="back-link">Back to Login</a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def show_reset_password_form():
    """Show the form to reset the password"""
    username = st.session_state.get("reset_username", "")
    
    if not username:
        st.error("No user information found. Please start the reset process again.")
        st.session_state.reset_step = 1
        st.rerun()
    
    st.markdown('<div class="reset-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="form-header">Set New Password</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; margin-bottom: 30px;">Please enter and confirm your new password.</p>', unsafe_allow_html=True)
    
    # Password reset form
    with st.form("reset_password_form"):
        new_password = st.text_input("New Password", type="password", key="new_password", placeholder="Enter your new password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password", placeholder="Re-enter your new password")
        
        # Password requirements
        st.markdown("""
        <div style="margin-top: 10px; font-size: 12px; color: #4a5568;">
            <p>Password should:</p>
            <ul>
                <li>Be at least 8 characters long</li>
                <li>Include at least one uppercase letter</li>
                <li>Include at least one number</li>
                <li>Include at least one special character</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        submit_button = st.form_submit_button("Reset Password", use_container_width=True)
        
        if submit_button:
            if not new_password or not confirm_password:
                st.error("Please fill in all fields.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                # Validate password strength
                password_valid = True
                password_message = ""
                
                # Basic validation
                if len(new_password) < 8:
                    password_valid = False
                    password_message = "Password must be at least 8 characters long"
                elif not any(c.isupper() for c in new_password):
                    password_valid = False
                    password_message = "Password must contain at least one uppercase letter"
                elif not any(c.isdigit() for c in new_password):
                    password_valid = False
                    password_message = "Password must contain at least one number"
                elif not any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?/`~" for c in new_password):
                    password_valid = False
                    password_message = "Password must contain at least one special character"
                
                if not password_valid:
                    st.error(password_message)
                else:
                    # Reset password
                    success, message = reset_password(username, new_password)
                    
                    if success:
                        st.session_state.reset_step = 4
                        st.rerun()
                    else:
                        st.error(message)
    
    # Back to login link
    st.markdown('<a href="/" class="back-link">Back to Login</a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def show_reset_confirmation():
    """Show the confirmation message after successful password reset"""
    st.markdown('<div class="reset-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="form-header">Password Reset Successful</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; margin-bottom: 30px;">Your password has been reset successfully.</p>', unsafe_allow_html=True)
    
    # Success message
    st.success("You can now log in with your new password.")
    
    # Login button
    if st.button("Go to Login", type="primary", use_container_width=True):
        # Reset the reset flow
        if "reset_step" in st.session_state:
            del st.session_state.reset_step
        if "reset_token" in st.session_state:
            del st.session_state.reset_token
        if "reset_username" in st.session_state:
            del st.session_state.reset_username
        
        # Redirect to login
        st.query_params.clear()
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    run_password_reset_flow()