import hashlib
import json
import os
from typing import Dict, Any, Optional

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

def authenticate(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate a user with username and password.
    
    Args:
        username: The username to authenticate
        password: The password to check
        
    Returns:
        User data dictionary if authentication is successful, None otherwise
    """
    users = _load_users()
    
    if username in users:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if users[username]["password_hash"] == password_hash:
            # Return user data without password hash
            user_data = users[username].copy()
            user_data.pop("password_hash", None)
            return user_data
    
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

def create_user(username: str, password: str, role: str, email: str) -> bool:
    """
    Create a new user.
    
    Args:
        username: The username for the new user
        password: The password for the new user
        role: The role for the new user
        email: The email for the new user
        
    Returns:
        True if user was created, False if username already exists
    """
    users = _load_users()
    
    if username in users:
        return False
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    users[username] = {
        "username": username,
        "password_hash": password_hash,
        "role": role,
        "email": email
    }
    
    _save_users(users)
    return True

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
