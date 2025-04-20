import hashlib
import json
import os
import re
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List, Set

# Simple user store (in a real app, this would be a database)
# For demo purposes, we'll store users in a JSON file
USERS_FILE = "users.json"

# Define permission structure
# Each permission is a string like 'scan:create' or 'user:delete'
# Format: resource:action
PERMISSIONS = {
    # Scan permissions
    'scan:create': 'Ability to create new scans',
    'scan:view': 'Ability to view scan results',
    'scan:export': 'Ability to export scan results',
    'scan:delete': 'Ability to delete scan results',
    'scan:premium': 'Ability to use premium scan features',
    'scan:configure': 'Ability to configure scan settings',
    
    # User management permissions
    'user:create': 'Ability to create new users',
    'user:view': 'Ability to view user information',
    'user:update': 'Ability to update user information',
    'user:delete': 'Ability to delete users',
    
    # Report permissions
    'report:create': 'Ability to create reports',
    'report:view': 'Ability to view reports',
    'report:export': 'Ability to export reports',
    
    # System permissions
    'system:settings': 'Ability to modify system settings',
    'system:logs': 'Ability to view system logs',
    'system:backup': 'Ability to backup system data',
    'system:restore': 'Ability to restore system data',
    
    # Admin permissions
    'admin:manage_users': 'Ability to manage users',
    'admin:manage_roles': 'Ability to manage roles',
    'admin:view_metrics': 'Ability to view system metrics',
    
    # Payment management
    'payment:manage': 'Ability to manage payment settings',
    'payment:view': 'Ability to view payment history',
    
    # Audit permissions
    'audit:view': 'Ability to view audit logs',
    'audit:export': 'Ability to export audit logs',
    
    # View permissions
    'dashboard:view': 'Ability to view the dashboard',
    'history:view': 'Ability to view scan history',
    
    # API permissions
    'api:access': 'Ability to access API endpoints',
    'api:manage_keys': 'Ability to manage API keys',
    
    # Advanced scanning features
    'scan:website': 'Ability to scan websites',
    'scan:code': 'Ability to scan code repositories',
    'scan:document': 'Ability to scan documents',
    'scan:database': 'Ability to scan databases',
    'scan:api': 'Ability to scan APIs',
}

# Define roles and their permissions
ROLE_PERMISSIONS = {
    'admin': {
        'description': 'Full system access with all permissions',
        'permissions': [
            # Scan permissions
            'scan:create', 'scan:view', 'scan:export', 'scan:delete', 'scan:premium', 'scan:configure',
            'scan:website', 'scan:code', 'scan:document', 'scan:database', 'scan:api',
            
            # User management
            'user:create', 'user:view', 'user:update', 'user:delete',
            
            # Report permissions
            'report:create', 'report:view', 'report:export',
            
            # System management
            'system:settings', 'system:logs', 'system:backup', 'system:restore',
            
            # Admin permissions
            'admin:manage_users', 'admin:manage_roles', 'admin:view_metrics',
            
            # Payment management
            'payment:manage', 'payment:view',
            
            # Audit permissions
            'audit:view', 'audit:export',
            
            # View permissions
            'dashboard:view', 'history:view',
            
            # API permissions
            'api:access', 'api:manage_keys'
        ]
    },
    'analyst': {
        'description': 'Can create and analyze scans, generate reports',
        'permissions': [
            # Scan permissions
            'scan:create', 'scan:view', 'scan:export', 'scan:premium', 'scan:configure',
            'scan:website', 'scan:code', 'scan:document', 'scan:database', 'scan:api',
            
            # Report permissions
            'report:create', 'report:view', 'report:export',
            
            # Limited user access
            'user:view',
            
            # Audit access
            'audit:view',
            
            # View permissions
            'dashboard:view', 'history:view',
            
            # API access
            'api:access'
        ]
    },
    'viewer': {
        'description': 'Read-only access to scans and reports',
        'permissions': [
            # Limited scan access
            'scan:view',
            
            # Limited report access
            'report:view',
            
            # View permissions
            'dashboard:view', 'history:view'
        ]
    },
    'security_officer': {
        'description': 'Focused on security compliance and auditing',
        'permissions': [
            # Scan permissions
            'scan:create', 'scan:view', 'scan:export', 'scan:configure',
            'scan:website', 'scan:code', 'scan:document',
            
            # Report access
            'report:view', 'report:export', 'report:create',
            
            # System monitoring
            'system:logs',
            
            # Audit access
            'audit:view', 'audit:export',
            
            # View permissions
            'dashboard:view', 'history:view'
        ]
    },
    'data_protection_officer': {
        'description': 'Focused on data protection and compliance reporting',
        'permissions': [
            # Limited scan access
            'scan:view', 'scan:export',
            
            # Report access
            'report:view', 'report:export', 'report:create',
            
            # Audit access
            'audit:view',
            
            # View permissions
            'dashboard:view', 'history:view'
        ]
    },
    'developer': {
        'description': 'Technical role for API integration and development',
        'permissions': [
            # Scan access
            'scan:create', 'scan:view', 'scan:export',
            'scan:website', 'scan:code', 'scan:api',
            
            # Limited report access
            'report:view',
            
            # API access
            'api:access', 'api:manage_keys',
            
            # View permissions
            'dashboard:view', 'history:view'
        ]
    },
    'manager': {
        'description': 'Oversees operations with metric visibility',
        'permissions': [
            # Limited scan access
            'scan:view', 'scan:export',
            
            # Report access
            'report:view', 'report:export',
            
            # Limited admin access
            'admin:view_metrics',
            
            # Limited payment access
            'payment:view',
            
            # Audit access
            'audit:view',
            
            # View permissions
            'dashboard:view', 'history:view'
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
        "permissions": ROLE_PERMISSIONS["admin"]["permissions"],
        "created_at": datetime.now().isoformat()
    },
    {
        "username": "analyst",
        "password_hash": hashlib.sha256("analyst123".encode()).hexdigest(),
        "role": "analyst",
        "email": "analyst@example.com",
        "permissions": ROLE_PERMISSIONS["analyst"]["permissions"],
        "created_at": datetime.now().isoformat()
    },
    {
        "username": "viewer",
        "password_hash": hashlib.sha256("viewer123".encode()).hexdigest(),
        "role": "viewer",
        "email": "viewer@example.com",
        "permissions": ROLE_PERMISSIONS["viewer"]["permissions"],
        "created_at": datetime.now().isoformat()
    },
    {
        "username": "security",
        "password_hash": hashlib.sha256("security123".encode()).hexdigest(),
        "role": "security_officer",
        "email": "security@example.com",
        "permissions": ROLE_PERMISSIONS["security_officer"]["permissions"],
        "created_at": datetime.now().isoformat()
    },
    {
        "username": "dpo",
        "password_hash": hashlib.sha256("dpo123".encode()).hexdigest(),
        "role": "data_protection_officer",
        "email": "dpo@example.com",
        "permissions": ROLE_PERMISSIONS["data_protection_officer"]["permissions"],
        "created_at": datetime.now().isoformat()
    },
    {
        "username": "developer",
        "password_hash": hashlib.sha256("developer123".encode()).hexdigest(),
        "role": "developer",
        "email": "developer@example.com",
        "permissions": ROLE_PERMISSIONS["developer"]["permissions"],
        "created_at": datetime.now().isoformat()
    },
    {
        "username": "manager",
        "password_hash": hashlib.sha256("manager123".encode()).hexdigest(),
        "role": "manager",
        "email": "manager@example.com",
        "permissions": ROLE_PERMISSIONS["manager"]["permissions"],
        "created_at": datetime.now().isoformat()
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
        "permissions": ROLE_PERMISSIONS[role]["permissions"],
        "created_at": datetime.now().isoformat()
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
    Preserves language preference.
    """
    import streamlit as st
    
    # Save the current language setting
    current_language = st.session_state.get("language", "en")
    
    # Clear authentication-related session state
    for key in ["logged_in", "username", "role", "permissions"]:
        if key in st.session_state:
            del st.session_state[key]
    
    # Restore language setting
    st.session_state["language"] = current_language

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

def remove_custom_permissions(username: str, permissions: List[str]) -> bool:
    """
    Remove custom permissions from a user.
    
    Args:
        username: The username to remove permissions from
        permissions: List of permissions to remove
        
    Returns:
        True if permissions were removed, False if user doesn't exist
    """
    users = _load_users()
    
    if username not in users:
        return False
    
    # Get current permissions
    current_permissions = users[username].get("permissions", [])
    
    # Get the base permissions for the user's role
    role = users[username].get("role")
    if role not in ROLE_PERMISSIONS:
        return False
        
    base_permissions = ROLE_PERMISSIONS[role]["permissions"]
    
    # Remove permissions if they're not in the base role permissions
    for permission in permissions:
        if permission in current_permissions and permission not in base_permissions:
            current_permissions.remove(permission)
    
    # Update user
    users[username]["permissions"] = current_permissions
    _save_users(users)
    
    return True

def reset_user_permissions(username: str) -> bool:
    """
    Reset a user's permissions to their role's default permissions.
    
    Args:
        username: The username to reset permissions for
        
    Returns:
        True if permissions were reset, False if user doesn't exist or role is invalid
    """
    users = _load_users()
    
    if username not in users:
        return False
    
    # Get the user's role
    role = users[username].get("role")
    if role not in ROLE_PERMISSIONS:
        return False
    
    # Reset permissions to role default
    users[username]["permissions"] = ROLE_PERMISSIONS[role]["permissions"].copy()
    _save_users(users)
    
    return True

def change_user_role(username: str, new_role: str) -> bool:
    """
    Change a user's role and update their permissions accordingly.
    
    Args:
        username: The username to change role for
        new_role: The new role to assign
        
    Returns:
        True if role was changed, False if user doesn't exist or role is invalid
    """
    users = _load_users()
    
    if username not in users:
        return False
    
    # Validate role
    if new_role not in ROLE_PERMISSIONS:
        return False
    
    # Update role and permissions
    users[username]["role"] = new_role
    users[username]["permissions"] = ROLE_PERMISSIONS[new_role]["permissions"].copy()
    _save_users(users)
    
    return True

def get_user_role_details(username: str) -> Optional[Dict[str, Any]]:
    """
    Get details about a user's role and permissions.
    
    Args:
        username: The username to get role details for
        
    Returns:
        Dictionary with role details or None if user doesn't exist
    """
    user_data = get_user(username)
    if not user_data:
        return None
    
    role = user_data.get("role")
    if not role or role not in ROLE_PERMISSIONS:
        return None
    
    role_data = ROLE_PERMISSIONS[role].copy()
    
    # Get custom permissions (permissions not in the role)
    user_permissions = set(user_data.get("permissions", []))
    role_permissions = set(role_data.get("permissions", []))
    
    custom_permissions = list(user_permissions - role_permissions)
    missing_permissions = list(role_permissions - user_permissions)
    
    return {
        "role": role,
        "role_description": role_data.get("description", ""),
        "custom_permissions": custom_permissions,
        "missing_permissions": missing_permissions,
        "total_permissions": len(user_permissions)
    }

def create_custom_role(role_name: str, description: str, permissions: List[str]) -> Tuple[bool, str]:
    """
    Create a new custom role with specified permissions.
    
    Args:
        role_name: Name for the new role (must be unique)
        description: Description of the role
        permissions: List of permission strings to assign to this role
        
    Returns:
        Tuple of (success, message) where success is True if role was created, 
        False otherwise, and message provides details
    """
    global ROLE_PERMISSIONS
    
    # Validate inputs
    if not role_name or not role_name.strip():
        return False, "Role name cannot be empty"
    
    # Clean role name (alphanumeric + underscores only)
    role_name = role_name.strip().lower().replace(' ', '_')
    
    # Check if role already exists
    if role_name in ROLE_PERMISSIONS:
        return False, f"Role '{role_name}' already exists"
    
    # Validate permissions
    valid_permissions = []
    for perm in permissions:
        if perm in PERMISSIONS:
            valid_permissions.append(perm)
    
    # Create the new role
    ROLE_PERMISSIONS[role_name] = {
        "description": description,
        "permissions": valid_permissions,
        "custom": True  # Flag to identify custom roles
    }
    
    # Return success
    return True, f"Role '{role_name}' created successfully with {len(valid_permissions)} permissions"

def update_role(role_name: str, updates: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Update an existing role.
    
    Args:
        role_name: The name of the role to update
        updates: Dictionary of fields to update (description, permissions)
        
    Returns:
        Tuple of (success, message) where success is True if role was updated, 
        False otherwise, and message provides details
    """
    global ROLE_PERMISSIONS
    
    # Check if role exists
    if role_name not in ROLE_PERMISSIONS:
        return False, f"Role '{role_name}' does not exist"
    
    # Check if it's a system role (only custom roles can be updated)
    if not ROLE_PERMISSIONS[role_name].get('custom', False):
        return False, f"Cannot update system role '{role_name}'"
    
    # Update description if provided
    if 'description' in updates:
        ROLE_PERMISSIONS[role_name]['description'] = updates['description']
    
    # Update permissions if provided
    if 'permissions' in updates:
        valid_permissions = []
        for perm in updates['permissions']:
            if perm in PERMISSIONS:
                valid_permissions.append(perm)
        
        ROLE_PERMISSIONS[role_name]['permissions'] = valid_permissions
    
    # Update other fields
    for key, value in updates.items():
        if key not in ['description', 'permissions', 'custom']:
            ROLE_PERMISSIONS[role_name][key] = value
    
    # Return success
    return True, f"Role '{role_name}' updated successfully"

def delete_role(role_name: str) -> Tuple[bool, str]:
    """
    Delete a custom role.
    
    Args:
        role_name: The name of the role to delete
        
    Returns:
        Tuple of (success, message) where success is True if role was deleted, 
        False otherwise, and message provides details
    """
    global ROLE_PERMISSIONS
    
    # Check if role exists
    if role_name not in ROLE_PERMISSIONS:
        return False, f"Role '{role_name}' does not exist"
    
    # Check if it's a system role (only custom roles can be deleted)
    if not ROLE_PERMISSIONS[role_name].get('custom', False):
        return False, f"Cannot delete system role '{role_name}'"
    
    # Check if any users have this role (optional - requires loading all users)
    try:
        users = _load_users()
        role_users = [username for username, data in users.items() if data.get('role') == role_name]
        if role_users:
            return False, f"Cannot delete role '{role_name}' because it is assigned to {len(role_users)} users"
    except:
        # If we can't load users, continue with deletion
        pass
    
    # Delete the role
    del ROLE_PERMISSIONS[role_name]
    
    # Return success
    return True, f"Role '{role_name}' deleted successfully"
