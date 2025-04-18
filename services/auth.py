import hashlib
import json
import os
import re
from typing import Dict, Any, Optional, Tuple, List, Set

# Simple user store (in a real app, this would be a database)
# For demo purposes, we'll store users in a JSON file
USERS_FILE = "users.json"

# Define permission structure
# Each permission is a string like 'scan:create' or 'user:delete'
# Format: resource:action
PERMISSIONS = {
    'scan:create': 'Ability to create new scans',
    'scan:view': 'Ability to view scan results',
    'scan:export': 'Ability to export scan results',
    'scan:delete': 'Ability to delete scan results',
    'scan:premium': 'Ability to use premium scan features',
    'user:create': 'Ability to create new users',
    'user:view': 'Ability to view user information',
    'user:update': 'Ability to update user information',
    'user:delete': 'Ability to delete users',
    'report:create': 'Ability to create reports',
    'report:view': 'Ability to view reports',
    'report:export': 'Ability to export reports',
    'system:settings': 'Ability to modify system settings',
    'system:logs': 'Ability to view system logs',
    'payment:manage': 'Ability to manage payment settings',
    'audit:view': 'Ability to view audit logs',
}

# Define roles and their permissions
ROLE_PERMISSIONS = {
    'admin': {
        'description': 'Full system access',
        'permissions': [
            'scan:create', 'scan:view', 'scan:export', 'scan:delete', 'scan:premium',
            'user:create', 'user:view', 'user:update', 'user:delete',
            'report:create', 'report:view', 'report:export',
            'system:settings', 'system:logs',
            'payment:manage',
            'audit:view',
        ]
    },
    'analyst': {
        'description': 'Can create and analyze scans',
        'permissions': [
            'scan:create', 'scan:view', 'scan:export', 'scan:premium',
            'report:create', 'report:view', 'report:export',
            'user:view',
            'audit:view',
        ]
    },
    'viewer': {
        'description': 'Read-only access to scans and reports',
        'permissions': [
            'scan:view',
            'report:view',
        ]
    },
    'security_officer': {
        'description': 'Focused on security compliance',
        'permissions': [
            'scan:create', 'scan:view', 'scan:export',
            'report:view', 'report:export',
            'audit:view',
            'system:logs',
        ]
    },
    'data_protection_officer': {
        'description': 'Focused on data protection',
        'permissions': [
            'scan:view', 'scan:export',
            'report:view', 'report:export',
            'audit:view',
        ]
    }
}

# Default users to create if the file doesn't exist
DEFAULT_USERS = [
    {
        "username": "admin",
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "admin",
        "email": "admin@example.com",
        "permissions": ROLE_PERMISSIONS["admin"]["permissions"]
    },
    {
        "username": "analyst",
        "password_hash": hashlib.sha256("analyst123".encode()).hexdigest(),
        "role": "analyst",
        "email": "analyst@example.com",
        "permissions": ROLE_PERMISSIONS["analyst"]["permissions"]
    },
    {
        "username": "viewer",
        "password_hash": hashlib.sha256("viewer123".encode()).hexdigest(),
        "role": "viewer",
        "email": "viewer@example.com",
        "permissions": ROLE_PERMISSIONS["viewer"]["permissions"]
    },
    {
        "username": "security",
        "password_hash": hashlib.sha256("security123".encode()).hexdigest(),
        "role": "security_officer",
        "email": "security@example.com",
        "permissions": ROLE_PERMISSIONS["security_officer"]["permissions"]
    },
    {
        "username": "dpo",
        "password_hash": hashlib.sha256("dpo123".encode()).hexdigest(),
        "role": "data_protection_officer",
        "email": "dpo@example.com",
        "permissions": ROLE_PERMISSIONS["data_protection_officer"]["permissions"]
    }
]

def _load_users() -> Dict[str, Dict[str, Any]]:
    """
    Load users from file, creating with defaults if it doesn't exist.
    
    Returns:
        Dictionary of users indexed by username
    """
    if not os.path.exists(USERS_FILE):
        # Create default users file
        users = {user["username"]: user for user in DEFAULT_USERS}
        _save_users(users)
        return users
    
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        # If file is corrupted, create a new one with defaults
        users = {user["username"]: user for user in DEFAULT_USERS}
        _save_users(users)
        return users

def _save_users(users: Dict[str, Dict[str, Any]]) -> None:
    """
    Save users to file.
    
    Args:
        users: Dictionary of users indexed by username
    """
    try:
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        print(f"Error saving users: {str(e)}")

def validate_email(email: str) -> bool:
    """
    Validates if a string is a proper email address.
    
    Args:
        email: Email string to validate
        
    Returns:
        True if valid email format, False otherwise
    """
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))

def authenticate(username_or_email: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate a user with username/email and password.
    
    Args:
        username_or_email: The username or email to authenticate
        password: The password to check
        
    Returns:
        User data dictionary if authentication is successful, None otherwise
    """
    users = _load_users()
    
    # Check if direct username match
    if username_or_email in users:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if users[username_or_email]["password_hash"] == password_hash:
            # Return user data without password hash
            user_data = users[username_or_email].copy()
            user_data.pop("password_hash", None)
            return user_data
    
    # Check if email match
    is_email = validate_email(username_or_email)
    if is_email:
        for username, user_data in users.items():
            if user_data.get("email") == username_or_email:
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                if user_data["password_hash"] == password_hash:
                    # Return user data without password hash
                    result = user_data.copy()
                    result.pop("password_hash", None)
                    return result
    
    return None

def get_user(username: str) -> Optional[Dict[str, Any]]:
    """
    Get user data by username.
    
    Args:
        username: The username to look up
        
    Returns:
        User data dictionary if found, None otherwise
    """
    users = _load_users()
    
    if username in users:
        # Return user data without password hash
        user_data = users[username].copy()
        user_data.pop("password_hash", None)
        return user_data
    
    return None

def create_user(username: str, password: str, role: str, email: str) -> Tuple[bool, str]:
    """
    Create a new user with validation.
    
    Args:
        username: The username for the new user
        password: The password for the new user
        role: The role for the new user
        email: The email for the new user
        
    Returns:
        Tuple of (success, message) where success is True if user was created, 
        False otherwise, and message provides details
    """
    users = _load_users()
    
    # Validate username
    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    # Check if username exists
    if username in users:
        return False, "Username already exists"
    
    # Check for email format
    if not validate_email(email):
        return False, "Invalid email format"
    
    # Check if email is already used
    for existing_user in users.values():
        if existing_user.get("email") == email:
            return False, "Email address is already registered"
    
    # Validate password
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    # Validate role
    if role not in ROLE_PERMISSIONS:
        return False, f"Invalid role. Valid roles are: {', '.join(ROLE_PERMISSIONS.keys())}"
    
    # Create user
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    users[username] = {
        "username": username,
        "password_hash": password_hash,
        "role": role,
        "email": email,
        "permissions": ROLE_PERMISSIONS[role]["permissions"]
    }
    
    _save_users(users)
    return True, "User created successfully"

def update_user(username: str, updates: Dict[str, Any]) -> bool:
    """
    Update an existing user.
    
    Args:
        username: The username of the user to update
        updates: Dictionary of fields to update
        
    Returns:
        True if user was updated, False if user doesn't exist
    """
    users = _load_users()
    
    if username not in users:
        return False
    
    # Update password if provided
    if "password" in updates:
        updates["password_hash"] = hashlib.sha256(updates.pop("password").encode()).hexdigest()
    
    # Update other fields
    for key, value in updates.items():
        if key != "username" and key != "password":  # Don't allow username changes
            users[username][key] = value
    
    _save_users(users)
    return True

def delete_user(username: str) -> bool:
    """
    Delete a user.
    
    Args:
        username: The username of the user to delete
        
    Returns:
        True if user was deleted, False if user doesn't exist
    """
    users = _load_users()
    
    if username not in users:
        return False
    
    del users[username]
    _save_users(users)
    return True

def is_authenticated() -> bool:
    """
    Check if user is authenticated in the current Streamlit session.
    
    Returns:
        True if authenticated, False otherwise
    """
    import streamlit as st
    return st.session_state.get("logged_in", False)

def logout() -> None:
    """
    Log out the current user by clearing session state.
    """
    import streamlit as st
    for key in ["logged_in", "username", "role", "permissions"]:
        if key in st.session_state:
            del st.session_state[key]

def has_permission(permission: str) -> bool:
    """
    Check if the current user has a specific permission.
    
    Args:
        permission: The permission to check (e.g., 'scan:create')
        
    Returns:
        True if the user has the permission, False otherwise
    """
    import streamlit as st
    
    # Admin bypass - admins have all permissions
    if st.session_state.get("role") == "admin":
        return True
    
    # Check if user has explicit permission
    user_permissions = st.session_state.get("permissions", [])
    return permission in user_permissions

def require_permission(permission: str) -> bool:
    """
    Check if the user has the required permission and show an error if not.
    
    Args:
        permission: The permission to check
        
    Returns:
        True if the user has the permission, False otherwise
    """
    import streamlit as st
    
    if not is_authenticated():
        st.error("You must be logged in to access this feature.")
        return False
        
    if not has_permission(permission):
        st.error(f"You don't have permission to access this feature ({permission}).")
        return False
        
    return True
    
def get_user_permissions(username: str = None) -> List[str]:
    """
    Get permissions for a specific user or the current user.
    
    Args:
        username: Optional username to get permissions for.
                 If None, returns permissions for the current user.
                 
    Returns:
        List of permission strings
    """
    import streamlit as st
    
    if username is None:
        # Get current user's permissions from session
        return st.session_state.get("permissions", [])
    
    # Get specific user's permissions
    user_data = get_user(username)
    if user_data and "permissions" in user_data:
        return user_data["permissions"]
    
    # If role exists but no permissions, derive from role
    if user_data and "role" in user_data and user_data["role"] in ROLE_PERMISSIONS:
        return ROLE_PERMISSIONS[user_data["role"]]["permissions"]
    
    return []

def get_all_permissions() -> Dict[str, str]:
    """
    Get all available permissions with descriptions.
    
    Returns:
        Dictionary of permission keys to descriptions
    """
    return PERMISSIONS

def get_all_roles() -> Dict[str, Dict[str, Any]]:
    """
    Get all available roles with descriptions and permissions.
    
    Returns:
        Dictionary of roles with their descriptions and permissions
    """
    return ROLE_PERMISSIONS

def add_custom_permissions(username: str, permissions: List[str]) -> bool:
    """
    Add custom permissions to a user beyond their role.
    
    Args:
        username: The username to add permissions to
        permissions: List of permissions to add
        
    Returns:
        True if permissions were added, False if user doesn't exist
    """
    users = _load_users()
    
    if username not in users:
        return False
    
    # Get current permissions
    current_permissions = users[username].get("permissions", [])
    
    # Add new permissions
    for permission in permissions:
        if permission in PERMISSIONS and permission not in current_permissions:
            current_permissions.append(permission)
    
    # Update user
    users[username]["permissions"] = current_permissions
    _save_users(users)
    
    return True
