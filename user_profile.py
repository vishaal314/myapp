"""
User Profile for DataGuardian Pro

This module provides the user profile for the application, including:
- User information display
- Permission information
- Role information
"""

import streamlit as st
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import RBAC components
from access_control import (
    ROLES,
    get_user_permissions,
    render_permission_ui
)

def render_user_profile_page():
    """
    Render the user profile page
    """
    # Check if user is logged in
    if not st.session_state.get("logged_in", False):
        st.warning("Please log in to view your profile.")
        return
    
    st.title("Your Profile")
    
    # User information
    username = st.session_state.get("username", "Unknown")
    email = st.session_state.get("email", "")
    role = st.session_state.get("role", "viewer")
    subscription_tier = st.session_state.get("subscription_tier", "basic")
    
    # Display user information
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Display avatar
        initial = username[0].upper() if username else "?"
        st.markdown(f"""
        <div style="background-color:#3b82f6; color:white; width:100px; height:100px; 
                 border-radius:50%; display:flex; align-items:center; justify-content:center; 
                 font-weight:bold; font-size:36px; margin-bottom:20px;">
            {initial}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"### {username}")
        st.markdown(f"**Email:** {email}")
        
        # Role information
        role_info = ROLES.get(role, {"name": role.title(), "description": "User role"})
        st.markdown(f"**Role:** {role_info['name']}")
        st.markdown(f"**Role Description:** {role_info['description']}")
        
        # Subscription information
        st.markdown(f"**Subscription:** {subscription_tier.title()}")
        
        # Show renewal date if available
        renewal_date = st.session_state.get("subscription_renewal_date")
        if renewal_date:
            st.markdown(f"**Renewal Date:** {renewal_date}")
    
    # Tabs for different profile sections
    tabs = st.tabs(["Permissions", "Activity", "Settings"])
    
    with tabs[0]:
        # Permissions
        render_permission_ui()
    
    with tabs[1]:
        # Activity
        st.subheader("Recent Activity")
        
        # In a real app, this would be fetched from a database
        # For demonstration, show some fake activity
        activities = [
            {
                "type": "Scan",
                "description": "Repository scan completed",
                "timestamp": (datetime.now().strftime("%Y-%m-%d %H:%M")),
                "details": "5 issues found"
            },
            {
                "type": "Login",
                "description": "Successful login",
                "timestamp": ((datetime.now().strftime("%Y-%m-%d %H:%M"))),
                "details": ""
            },
            {
                "type": "Report",
                "description": "Downloaded compliance report",
                "timestamp": ((datetime.now().strftime("%Y-%m-%d %H:%M"))),
                "details": "PDF format"
            }
        ]
        
        for activity in activities:
            st.markdown(f"""
            <div style="border:1px solid #e2e8f0; border-radius:8px; padding:12px; margin-bottom:12px;">
                <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                    <span style="font-weight:500;">{activity['type']}</span>
                    <span style="color:#64748b; font-size:14px;">{activity['timestamp']}</span>
                </div>
                <div style="margin-bottom:4px;">{activity['description']}</div>
                {f'<div style="font-size:12px; color:#64748b;">{activity["details"]}</div>' if activity['details'] else ''}
            </div>
            """, unsafe_allow_html=True)
    
    with tabs[2]:
        # Settings
        st.subheader("Profile Settings")
        
        with st.form("profile_settings_form"):
            # Personal information
            new_email = st.text_input("Email", value=email)
            
            # Password change
            st.markdown("### Change Password")
            change_password = st.checkbox("Change my password")
            
            current_password = None
            new_password = None
            confirm_password = None
            
            if change_password:
                current_password = st.text_input("Current Password", type="password")
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm New Password", type="password")
            
            # Notification settings
            st.markdown("### Notification Settings")
            
            email_notifications = st.checkbox("Email Notifications", value=True)
            scan_completion = st.checkbox("Scan Completion Notifications", value=True)
            security_alerts = st.checkbox("Security Alerts", value=True)
            
            # Save button
            save_settings = st.form_submit_button("Save Settings")
            
            if save_settings:
                if new_email != email:
                    # Update email logic would go here
                    st.success(f"Email updated to {new_email}")
                
                if change_password:
                    if not current_password or not new_password or not confirm_password:
                        st.error("Please fill in all password fields.")
                    elif new_password != confirm_password:
                        st.error("New passwords do not match.")
                    else:
                        # Update password logic would go here
                        st.success("Password updated successfully.")
                
                # In a real app, notification settings would be saved to a database
                st.success("Settings saved successfully!")