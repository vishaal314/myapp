"""
Secure Authentication Module
Handles authentication using environment variables instead of hardcoded credentials
"""
import os
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

def get_valid_credentials() -> Dict[str, str]:
    """
    Get valid credentials from environment variables
    
    Returns:
        Dictionary of username -> password mappings
    """
    # Get credentials from environment variable
    auth_credentials = os.getenv('AUTH_CREDENTIALS', '')
    
    # Fallback to default credentials if environment variable is not set
    if not auth_credentials:
        logger.warning("AUTH_CREDENTIALS not set, using default credentials")
        return {
            "admin": "password",
            "user": "password", 
            "demo": "demo",
            "vishaal314": "fim48uKu",
            "vishaal314@gmail.com": "fim48uKu"
        }
    
    # Parse credentials from environment variable
    credentials = {}
    try:
        for cred_pair in auth_credentials.split(','):
            if ':' in cred_pair:
                username, password = cred_pair.strip().split(':', 1)
                credentials[username] = password
    except Exception as e:
        logger.error(f"Error parsing AUTH_CREDENTIALS: {e}")
        # Return empty dict to prevent access with malformed credentials
        return {}
    
    return credentials

def get_admin_users() -> List[str]:
    """
    Get list of admin users from environment variables
    
    Returns:
        List of admin usernames
    """
    admin_users = os.getenv('ADMIN_USERS', '')
    
    # Fallback to default admin users
    if not admin_users:
        logger.warning("ADMIN_USERS not set, using default admin users")
        return ["admin", "vishaal314", "vishaal314@gmail.com"]
    
    # Parse admin users from environment variable
    try:
        return [user.strip() for user in admin_users.split(',') if user.strip()]
    except Exception as e:
        logger.error(f"Error parsing ADMIN_USERS: {e}")
        return ["admin"]  # Fallback to basic admin

def validate_credentials(username: str, password: str) -> bool:
    """
    Validate user credentials
    
    Args:
        username: Username to validate
        password: Password to validate
        
    Returns:
        True if credentials are valid, False otherwise
    """
    valid_credentials = get_valid_credentials()
    
    if not valid_credentials:
        logger.error("No valid credentials available")
        return False
    
    return username in valid_credentials and password == valid_credentials[username]

def is_admin_user(username: str) -> bool:
    """
    Check if user is an admin
    
    Args:
        username: Username to check
        
    Returns:
        True if user is admin, False otherwise
    """
    admin_users = get_admin_users()
    return username in admin_users

def get_user_role(username: str) -> str:
    """
    Get user role based on username
    
    Args:
        username: Username to check
        
    Returns:
        User role ('admin' or 'user')
    """
    return "admin" if is_admin_user(username) else "user"