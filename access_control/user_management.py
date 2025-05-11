"""
User Management for DataGuardian Pro

This module provides user management functions for administrators, including:
- Creating and updating users
- Assigning roles and permissions
- Managing user accounts
"""

import streamlit as st
import json
import hashlib
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Import role configuration
from access_control.roles_config import ROLES, ROLE_PERMISSIONS
from access_control.rbac import requires_permission, check_permission

def load_users() -> Dict[str, Any]:
    """
    Load users from the users.json file
    
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
    Save users to the users.json file
    
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

def create_user(
    username: str,
    password: str,
    email: str,
    role: str = "viewer",
    subscription_tier: str = "basic",
    **kwargs
) -> Tuple[bool, str]:
    """
    Create a new user
    
    Args:
        username: Username for the new user
        password: Password for the new user
        email: Email address for the new user
        role: Role for the new user
        subscription_tier: Subscription tier for the new user
        **kwargs: Additional user data
        
    Returns:
        Tuple of (success, message)
    """
    # Hash the password
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # Load existing users
    users = load_users()
    
    # Check if username already exists
    if username in users:
        return False, f"User '{username}' already exists."
    
    # Create user object
    user_data = {
        "username": username,
        "password_hash": password_hash,
        "email": email,
        "role": role,
        "subscription_tier": subscription_tier,
        "subscription_active": True,
        "stripe_customer_id": kwargs.get("stripe_customer_id"),
        "subscription_id": kwargs.get("subscription_id"),
        "user_id": kwargs.get("user_id", f"usr_{uuid.uuid4().hex[:8]}"),
        "subscription_renewal_date": kwargs.get("subscription_renewal_date"),
        "created_at": datetime.now().isoformat(),
        "last_login": None
    }
    
    # Add additional data
    for key, value in kwargs.items():
        if key not in user_data:
            user_data[key] = value
    
    # Add user to users dictionary
    users[username] = user_data
    
    # Save users
    if save_users(users):
        return True, f"User '{username}' created successfully."
    else:
        return False, "Error saving users."

def update_user(
    username: str,
    **kwargs
) -> Tuple[bool, str]:
    """
    Update an existing user
    
    Args:
        username: Username of the user to update
        **kwargs: User data to update
        
    Returns:
        Tuple of (success, message)
    """
    # Load existing users
    users = load_users()
    
    # Check if username exists
    if username not in users:
        return False, f"User '{username}' does not exist."
    
    # Update user data
    for key, value in kwargs.items():
        # Handle password separately
        if key == "password":
            # Hash the password
            users[username]["password_hash"] = hashlib.sha256(value.encode()).hexdigest()
        else:
            users[username][key] = value
    
    # Save users
    if save_users(users):
        return True, f"User '{username}' updated successfully."
    else:
        return False, "Error saving users."

def delete_user(username: str) -> Tuple[bool, str]:
    """
    Delete a user
    
    Args:
        username: Username of the user to delete
        
    Returns:
        Tuple of (success, message)
    """
    # Load existing users
    users = load_users()
    
    # Check if username exists
    if username not in users:
        return False, f"User '{username}' does not exist."
    
    # Delete user
    del users[username]
    
    # Save users
    if save_users(users):
        return True, f"User '{username}' deleted successfully."
    else:
        return False, "Error saving users."

def change_user_role(username: str, new_role: str) -> Tuple[bool, str]:
    """
    Change a user's role
    
    Args:
        username: Username of the user to update
        new_role: New role for the user
        
    Returns:
        Tuple of (success, message)
    """
    # Check if role exists
    if new_role not in ROLES:
        return False, f"Role '{new_role}' does not exist."
    
    # Update user
    return update_user(username, role=new_role)

def change_user_subscription(username: str, new_tier: str) -> Tuple[bool, str]:
    """
    Change a user's subscription tier
    
    Args:
        username: Username of the user to update
        new_tier: New subscription tier for the user
        
    Returns:
        Tuple of (success, message)
    """
    # Check if tier exists
    valid_tiers = ["basic", "premium", "gold"]
    if new_tier not in valid_tiers:
        return False, f"Subscription tier '{new_tier}' does not exist."
    
    # Update user
    return update_user(username, subscription_tier=new_tier)

@requires_permission("admin:users")
def render_user_management():
    """
    Render the user management UI for administrators
    """
    st.title("User Management")
    
    # Load users
    users = load_users()
    
    # Create tabs for different management functions
    tabs = st.tabs(["User List", "Create User", "Edit User", "Delete User"])
    
    with tabs[0]:
        # User list
        st.subheader("User List")
        
        if not users:
            st.info("No users found.")
        else:
            # Convert to list for table display
            user_list = []
            for username, data in users.items():
                user_list.append({
                    "Username": username,
                    "Email": data.get("email", ""),
                    "Role": data.get("role", "viewer"),
                    "Subscription": data.get("subscription_tier", "basic").title(),
                    "Active": "Yes" if data.get("subscription_active", True) else "No"
                })
            
            # Display as table
            st.dataframe(user_list)
            
            # Display detailed user information
            selected_user = st.selectbox("Select user for details", list(users.keys()))
            
            if selected_user:
                user_data = users[selected_user]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### User Details")
                    st.markdown(f"**Username:** {selected_user}")
                    st.markdown(f"**Email:** {user_data.get('email', '')}")
                    st.markdown(f"**Role:** {user_data.get('role', 'viewer')}")
                    st.markdown(f"**Subscription:** {user_data.get('subscription_tier', 'basic').title()}")
                    st.markdown(f"**Active:** {'Yes' if user_data.get('subscription_active', True) else 'No'}")
                    
                    if "created_at" in user_data:
                        st.markdown(f"**Created:** {user_data['created_at']}")
                    
                    if "last_login" in user_data and user_data["last_login"]:
                        st.markdown(f"**Last Login:** {user_data['last_login']}")
                
                with col2:
                    st.markdown("#### Subscription Details")
                    st.markdown(f"**Subscription ID:** {user_data.get('subscription_id', 'N/A')}")
                    st.markdown(f"**Customer ID:** {user_data.get('stripe_customer_id', 'N/A')}")
                    st.markdown(f"**Renewal Date:** {user_data.get('subscription_renewal_date', 'N/A')}")
    
    with tabs[1]:
        # Create user
        st.subheader("Create New User")
        
        # User form
        with st.form("create_user_form"):
            username = st.text_input("Username", key="create_username")
            email = st.text_input("Email", key="create_email")
            password = st.text_input("Password", type="password", key="create_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="create_confirm_password")
            
            role = st.selectbox("Role", list(ROLES.keys()), format_func=lambda x: ROLES[x]["name"])
            subscription_tier = st.selectbox("Subscription Tier", ["basic", "premium", "gold"], format_func=lambda x: x.title())
            
            submit_button = st.form_submit_button("Create User")
            
            if submit_button:
                if not username or not email or not password:
                    st.error("Please fill in all fields.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    success, message = create_user(
                        username=username,
                        password=password,
                        email=email,
                        role=role,
                        subscription_tier=subscription_tier
                    )
                    
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
    
    with tabs[2]:
        # Edit user
        st.subheader("Edit User")
        
        # Select user to edit
        edit_username = st.selectbox("Select User to Edit", list(users.keys()), key="edit_user_select")
        
        if edit_username:
            user_data = users[edit_username]
            
            with st.form("edit_user_form"):
                edit_email = st.text_input("Email", value=user_data.get("email", ""))
                change_password = st.checkbox("Change Password")
                
                edit_password = None
                edit_confirm_password = None
                
                if change_password:
                    edit_password = st.text_input("New Password", type="password")
                    edit_confirm_password = st.text_input("Confirm New Password", type="password")
                
                edit_role = st.selectbox(
                    "Role", 
                    list(ROLES.keys()), 
                    index=list(ROLES.keys()).index(user_data.get("role", "viewer")),
                    format_func=lambda x: ROLES[x]["name"]
                )
                
                edit_subscription = st.selectbox(
                    "Subscription Tier", 
                    ["basic", "premium", "gold"], 
                    index=["basic", "premium", "gold"].index(user_data.get("subscription_tier", "basic")),
                    format_func=lambda x: x.title()
                )
                
                edit_active = st.checkbox("Subscription Active", value=user_data.get("subscription_active", True))
                
                submit_edit = st.form_submit_button("Update User")
                
                if submit_edit:
                    update_data = {
                        "email": edit_email,
                        "role": edit_role,
                        "subscription_tier": edit_subscription,
                        "subscription_active": edit_active
                    }
                    
                    if change_password:
                        if not edit_password:
                            st.error("Please enter a new password.")
                            st.stop()
                        elif edit_password != edit_confirm_password:
                            st.error("Passwords do not match.")
                            st.stop()
                        else:
                            update_data["password"] = edit_password
                    
                    success, message = update_user(edit_username, **update_data)
                    
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
    
    with tabs[3]:
        # Delete user
        st.subheader("Delete User")
        
        st.warning("Deleting a user is permanent and cannot be undone.")
        
        # Select user to delete
        delete_username = st.selectbox("Select User to Delete", list(users.keys()), key="delete_user_select")
        
        if delete_username:
            st.write(f"Are you sure you want to delete user '{delete_username}'?")
            
            # Confirm delete
            confirm_delete = st.checkbox("I confirm I want to delete this user", key="confirm_delete")
            
            if confirm_delete:
                if st.button("Delete User", key="delete_user_button"):
                    success, message = delete_user(delete_username)
                    
                    if success:
                        st.success(message)
                        st.rerun()  # Refresh the page
                    else:
                        st.error(message)