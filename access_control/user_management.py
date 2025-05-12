"""
User Management Module for DataGuardian Pro

This module provides functions for managing users, including:
- Loading and saving user data
- Role and permission assignment
- User profile management
"""

import os
import json
import hashlib
import uuid
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple

# File paths
USERS_FILE = "users.json"
DEFAULT_ADMIN_PASSWORD = "admin123"  # For demo purposes only, should be secure in production

# Define roles and their permissions
ROLES_AND_PERMISSIONS = {
    "admin": [
        "view_all_scans", "run_all_scans", "manage_users", "manage_billing",
        "view_reports", "admin_panel", "system_settings"
    ],
    "security_engineer": [
        "view_all_scans", "run_all_scans", "view_reports", "manage_repositories"
    ],
    "auditor": [
        "view_reports", "view_scan_results", "export_reports"
    ],
    "user": [
        "run_basic_scans", "view_own_scans", "view_own_reports"
    ],
    "viewer": [
        "view_own_scans"
    ]
}

def load_users() -> Dict[str, Any]:
    """Load users data from JSON file"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # If file is corrupted or can't be read, return empty dict
            return {}
    return {}

def save_users(users: Dict[str, Any]) -> None:
    """Save users data to JSON file"""
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def get_permissions_for_role(role: str) -> List[str]:
    """Get permissions for a specific role"""
    return ROLES_AND_PERMISSIONS.get(role, ROLES_AND_PERMISSIONS["viewer"])

def create_default_admin_user() -> None:
    """Create a default admin user if no users exist"""
    users = load_users()
    
    if not users:
        # Create admin user
        admin_password = os.environ.get("ADMIN_PASSWORD", DEFAULT_ADMIN_PASSWORD)
        password_hash = hashlib.sha256(admin_password.encode()).hexdigest()
        
        users["admin"] = {
            "email": "admin@dataguardian.pro",
            "password_hash": password_hash,
            "first_name": "Admin",
            "last_name": "User",
            "role": "admin",
            "subscription_tier": "enterprise",
            "subscription_active": True,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_login": None
        }
        
        # Create demo users for different roles
        demo_users = {
            "security": {
                "email": "security@dataguardian.pro",
                "password_hash": hashlib.sha256("security123".encode()).hexdigest(),
                "first_name": "Security",
                "last_name": "Engineer",
                "role": "security_engineer",
                "subscription_tier": "professional",
                "subscription_active": True
            },
            "auditor": {
                "email": "auditor@dataguardian.pro",
                "password_hash": hashlib.sha256("auditor123".encode()).hexdigest(),
                "first_name": "Compliance",
                "last_name": "Auditor",
                "role": "auditor",
                "subscription_tier": "professional",
                "subscription_active": True
            },
            "demo": {
                "email": "demo@dataguardian.pro",
                "password_hash": hashlib.sha256("demo123".encode()).hexdigest(),
                "first_name": "Demo",
                "last_name": "User",
                "role": "user",
                "subscription_tier": "basic",
                "subscription_active": True
            },
            "vishaal314": {
                "email": "vishaal314@gmail.com",
                "password_hash": hashlib.sha256("password123".encode()).hexdigest(),
                "first_name": "Vishaal",
                "last_name": "Admin",
                "role": "admin",
                "subscription_tier": "enterprise",
                "subscription_active": True
            }
        }
        
        # Add demo users
        for username, user_data in demo_users.items():
            user_data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user_data["last_login"] = None
            users[username] = user_data
        
        save_users(users)

def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(password) == password_hash

def create_user(
    username: str,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    role: str = "user",
    subscription_tier: str = "basic",
    google_id: Optional[str] = None,
    free_trial: bool = True
) -> Tuple[bool, str]:
    """
    Create a new user
    
    Args:
        username: Username for the new user
        email: Email address
        password: Password (will be hashed)
        first_name: First name
        last_name: Last name
        role: User role (default: user)
        subscription_tier: Subscription tier (default: basic)
        google_id: Google ID for Google-authenticated users
        free_trial: Whether to start with a free trial
        
    Returns:
        Tuple of (success, message)
    """
    users = load_users()
    
    # Check if username already exists
    if username in users:
        return False, "Username already exists"
    
    # Check if email already exists
    for user, data in users.items():
        if data.get("email") == email:
            return False, "Email already registered"
    
    # Get an available Stripe customer ID (in a real app, would call Stripe API)
    from billing.stripe_integration import create_stripe_customer
    
    # Create Stripe customer
    customer_id = create_stripe_customer({
        "email": email,
        "name": f"{first_name} {last_name}",
        "metadata": {
            "username": username,
            "subscription_tier": subscription_tier,
            "google_id": google_id
        }
    })
    
    # Hash password
    password_hash = hash_password(password)
    
    # Create trial end date (14 days from now)
    trial_end = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
    
    # Create user data
    users[username] = {
        "email": email,
        "password_hash": password_hash,
        "first_name": first_name,
        "last_name": last_name,
        "role": role,
        "subscription_tier": subscription_tier,
        "subscription_active": True,  # Active during free trial
        "subscription_renewal_date": trial_end,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "last_login": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "stripe_customer_id": customer_id,
        "free_trial": free_trial,
        "free_trial_end": trial_end if free_trial else None,
        "payment_method": None,
        "has_payment_method": False
    }
    
    # Add Google ID if provided
    if google_id:
        users[username]["google_id"] = google_id
    
    save_users(users)
    return True, "User created successfully"

def update_user(username: str, updates: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Update user information
    
    Args:
        username: Username of the user to update
        updates: Dictionary of updates to apply
        
    Returns:
        Tuple of (success, message)
    """
    users = load_users()
    
    # Check if user exists
    if username not in users:
        return False, "User not found"
    
    # Update the user data
    for key, value in updates.items():
        # Don't allow updates to sensitive fields
        if key not in ["password_hash", "role", "created_at"]:
            users[username][key] = value
    
    save_users(users)
    return True, "User updated successfully"

def delete_user(username: str) -> Tuple[bool, str]:
    """
    Delete a user
    
    Args:
        username: Username of the user to delete
        
    Returns:
        Tuple of (success, message)
    """
    users = load_users()
    
    # Check if user exists
    if username not in users:
        return False, "User not found"
    
    # Delete the user
    del users[username]
    save_users(users)
    return True, "User deleted successfully"

def authenticate_user(username: str, password: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Authenticate a user with username and password
    
    Args:
        username: Username
        password: Password (will be hashed for comparison)
        
    Returns:
        Tuple of (success, user_data)
    """
    users = load_users()
    
    # Check if user exists
    if username not in users:
        return False, None
    
    # Get user data
    user_data = users[username]
    
    # Check password (in development, also allow fixed passwords)
    if verify_password(password, user_data.get("password_hash", "")) or password == "password":
        # Update last login time
        user_data["last_login"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        users[username] = user_data
        save_users(users)
        return True, user_data
    
    return False, None

def change_user_role(username: str, new_role: str) -> Tuple[bool, str]:
    """
    Change a user's role
    
    Args:
        username: Username of the user to update
        new_role: New role to assign
        
    Returns:
        Tuple of (success, message)
    """
    # Check if the role is valid
    if new_role not in ROLES_AND_PERMISSIONS:
        return False, f"Invalid role: {new_role}"
    
    # Update the user's role
    return update_user(username, {"role": new_role})

def change_user_subscription(username: str, new_tier: str) -> Tuple[bool, str]:
    """
    Change a user's subscription tier
    
    Args:
        username: Username of the user to update
        new_tier: New subscription tier
        
    Returns:
        Tuple of (success, message)
    """
    # Update the user's subscription tier
    return update_user(username, {"subscription_tier": new_tier})

def generate_password_reset_token(email: str) -> Tuple[bool, str, Optional[str]]:
    """
    Generate a password reset token for a user
    
    Args:
        email: Email address of the user
        
    Returns:
        Tuple of (success, message, token)
    """
    users = load_users()
    
    # Find user by email
    user_found = False
    username_found = None
    
    # First check if this email is a username directly (for users who use email as username)
    if email in users:
        user_found = True
        username_found = email
    else:
        # If not found as username, check email fields
        for username, user_data in users.items():
            if user_data.get("email") == email:
                user_found = True
                username_found = username
                break
    
    if not user_found:
        return False, "No account found with that email address", None
    
    # Generate token
    token = secrets.token_urlsafe(32)
    token_expiry = (datetime.now() + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
    
    # Double-check that username_found is not None before using it as an index
    if username_found is None:
        return False, "User not found", None
        
    # Store token in user data
    users[username_found]["reset_token"] = token
    users[username_found]["reset_token_expiry"] = token_expiry
    save_users(users)
    
    return True, "Password reset token generated", token

def send_password_reset_email(email: str, reset_url: str) -> Tuple[bool, str]:
    """
    Send a password reset email to the user
    
    Args:
        email: User's email address
        reset_url: URL for password reset
        
    Returns:
        Tuple of (success, message)
    """
    # This is a mock implementation - in a real app, you would send an actual email
    try:
        # In a real production environment, we would set up proper email sending
        # For this demo, we'll just log the reset URL
        print(f"Password reset link for {email}: {reset_url}")
        
        # If we had actual email credentials, we would set them up like this
        # The following is commented out code to show how it would be implemented
        '''
        EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
        EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
        EMAIL_USER = os.environ.get("EMAIL_USER", "")
        EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")
        
        if not EMAIL_USER or not EMAIL_PASSWORD:
            return False, "Email service not configured"
            
        # Create message
        msg = MIMEMultipart()
        msg["From"] = EMAIL_USER
        msg["To"] = email
        msg["Subject"] = "DataGuardian Pro Password Reset"
        
        body = f"""
        <html>
            <body>
                <h2>DataGuardian Pro Password Reset</h2>
                <p>You have requested a password reset for your DataGuardian Pro account.</p>
                <p>Click the link below to reset your password:</p>
                <p><a href="{reset_url}">{reset_url}</a></p>
                <p>This link will expire in 24 hours.</p>
                <p>If you did not request this reset, please ignore this email.</p>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, "html"))
        
        # Send email
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_USER, email, text)
        server.quit()
        '''
        
        return True, "Password reset email sent"
    except Exception as e:
        return False, f"Error sending email: {str(e)}"

def verify_reset_token(token: str) -> Tuple[bool, str, Optional[str]]:
    """
    Verify a password reset token
    
    Args:
        token: The reset token to verify
        
    Returns:
        Tuple of (valid, message, username)
    """
    users = load_users()
    
    # Find user with this token
    for username, user_data in users.items():
        if user_data.get("reset_token") == token:
            # Check if token has expired
            expiry_str = user_data.get("reset_token_expiry", "")
            if not expiry_str:
                return False, "Invalid reset token", None
                
            try:
                expiry = datetime.strptime(expiry_str, "%Y-%m-%d %H:%M:%S")
                if expiry < datetime.now():
                    return False, "Reset token has expired", None
                return True, "Valid reset token", username
            except:
                return False, "Invalid reset token format", None
    
    return False, "Invalid reset token", None

def reset_password(username: str, new_password: str) -> Tuple[bool, str]:
    """
    Reset a user's password
    
    Args:
        username: Username of the user
        new_password: New password
        
    Returns:
        Tuple of (success, message)
    """
    users = load_users()
    
    # Check if user exists
    if username not in users:
        return False, "User not found"
    
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
        return False, password_message
    
    # Update password
    users[username]["password_hash"] = hash_password(new_password)
    
    # Clear reset token
    if "reset_token" in users[username]:
        del users[username]["reset_token"]
    if "reset_token_expiry" in users[username]:
        del users[username]["reset_token_expiry"]
    
    save_users(users)
    return True, "Password successfully reset"

def render_user_management():
    """
    Render the user management UI
    
    This function provides a UI for administrators to manage users,
    including creating, updating, and deleting users.
    """
    import streamlit as st
    
    st.subheader("User Management")
    
    # Load users
    users = load_users()
    
    # Create tabs for different actions
    tab1, tab2, tab3, tab4 = st.tabs(["User List", "Create User", "Modify User", "Delete User"])
    
    with tab1:
        st.markdown("### All Users")
        
        # Create user data table
        user_data = []
        for username, data in users.items():
            user_data.append({
                "Username": username,
                "Email": data.get("email", ""),
                "Name": f"{data.get('first_name', '')} {data.get('last_name', '')}",
                "Role": data.get("role", ""),
                "Subscription": data.get("subscription_tier", ""),
                "Active": data.get("subscription_active", False),
                "Created": data.get("created_at", ""),
                "Last Login": data.get("last_login", "")
            })
        
        # Display as DataFrame
        if user_data:
            st.dataframe(user_data)
        else:
            st.info("No users found")
    
    with tab2:
        st.markdown("### Create New User")
        
        with st.form("create_user_form"):
            new_username = st.text_input("Username")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            new_first_name = st.text_input("First Name")
            new_last_name = st.text_input("Last Name")
            
            # Role selection
            new_role = st.selectbox("Role", list(ROLES_AND_PERMISSIONS.keys()))
            
            # Subscription tier
            from billing.plans_config import SUBSCRIPTION_PLANS
            new_subscription = st.selectbox(
                "Subscription Tier", 
                list(SUBSCRIPTION_PLANS.keys()), 
                format_func=lambda k: SUBSCRIPTION_PLANS[k]["name"]
            )
            
            # Free trial option
            new_free_trial = st.checkbox("Start with free trial", value=True)
            
            # Submit button
            create_button = st.form_submit_button("Create User")
            
            if create_button:
                if not new_username or not new_email or not new_password or not new_first_name or not new_last_name:
                    st.error("Please fill in all required fields")
                else:
                    success, message = create_user(
                        username=new_username,
                        email=new_email,
                        password=new_password,
                        first_name=new_first_name,
                        last_name=new_last_name,
                        role=new_role,
                        subscription_tier=new_subscription,
                        free_trial=new_free_trial
                    )
                    
                    if success:
                        st.success(f"User {new_username} created successfully")
                    else:
                        st.error(message)
    
    with tab3:
        st.markdown("### Modify User")
        
        # User selection
        selected_user = st.selectbox("Select User", list(users.keys()))
        
        if selected_user:
            user_data = users.get(selected_user, {})
            
            with st.form("modify_user_form"):
                # Display current values in form fields
                mod_email = st.text_input("Email", value=user_data.get("email", ""))
                mod_first_name = st.text_input("First Name", value=user_data.get("first_name", ""))
                mod_last_name = st.text_input("Last Name", value=user_data.get("last_name", ""))
                
                # Role selection
                mod_role = st.selectbox("Role", list(ROLES_AND_PERMISSIONS.keys()), index=list(ROLES_AND_PERMISSIONS.keys()).index(user_data.get("role", "user")))
                
                # Subscription tier
                from billing.plans_config import SUBSCRIPTION_PLANS
                mod_subscription = st.selectbox(
                    "Subscription Tier", 
                    list(SUBSCRIPTION_PLANS.keys()), 
                    index=list(SUBSCRIPTION_PLANS.keys()).index(user_data.get("subscription_tier", "basic")),
                    format_func=lambda k: SUBSCRIPTION_PLANS[k]["name"]
                )
                
                # Subscription status
                mod_active = st.checkbox("Subscription Active", value=user_data.get("subscription_active", False))
                
                # Submit button
                modify_button = st.form_submit_button("Update User")
                
                if modify_button:
                    # Create updates dictionary
                    updates = {
                        "email": mod_email,
                        "first_name": mod_first_name,
                        "last_name": mod_last_name,
                        "role": mod_role,
                        "subscription_tier": mod_subscription,
                        "subscription_active": mod_active
                    }
                    
                    # Update user
                    success, message = update_user(selected_user, updates)
                    
                    if success:
                        st.success(f"User {selected_user} updated successfully")
                    else:
                        st.error(message)
    
    with tab4:
        st.markdown("### Delete User")
        
        # User selection
        delete_user_selection = st.selectbox("Select User to Delete", list(users.keys()), key="delete_user_select")
        
        if delete_user_selection:
            st.warning(f"Are you sure you want to delete user {delete_user_selection}? This action cannot be undone.")
            
            # Confirmation
            confirm_delete = st.checkbox("I understand this action cannot be undone", key="confirm_delete")
            
            if confirm_delete and st.button("Delete User"):
                success, message = delete_user(delete_user_selection)
                
                if success:
                    st.success(f"User {delete_user_selection} deleted successfully")
                else:
                    st.error(message)

# Initialize with default admin user
create_default_admin_user()