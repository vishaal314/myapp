import hashlib
import json
import os
import re
from typing import Dict, Any, Optional, Tuple

# Simple user store (in a real app, this would be a database)
# For demo purposes, we'll store users in a JSON file
USERS_FILE = "users.json"

# Default users to create if the file doesn't exist
DEFAULT_USERS = [
    {
        "username": "admin",
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "admin",
        "email": "admin@example.com"
    },
    {
        "username": "analyst",
        "password_hash": hashlib.sha256("analyst123".encode()).hexdigest(),
        "role": "analyst",
        "email": "analyst@example.com"
    },
    {
        "username": "viewer",
        "password_hash": hashlib.sha256("viewer123".encode()).hexdigest(),
        "role": "viewer",
        "email": "viewer@example.com"
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
    
    # Create user
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    users[username] = {
        "username": username,
        "password_hash": password_hash,
        "role": role,
        "email": email
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
    for key in ["logged_in", "username", "role"]:
        if key in st.session_state:
            del st.session_state[key]
