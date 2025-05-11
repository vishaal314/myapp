"""
Role-Based Access Control (RBAC) for DataGuardian Pro

This module provides functions and decorators to implement RBAC in the application.
It includes utilities for checking permissions and protecting features based on roles.
"""

import functools
import streamlit as st
from typing import Callable, List, Any, Optional, Set, Dict, Union

# Import the roles configuration
from access_control.roles_config import (
    has_permission, 
    get_effective_permissions,
    PERMISSIONS
)

def requires_permission(permission: str, message: Optional[str] = None) -> Callable:
    """
    Decorator to protect a function based on a required permission.
    
    Args:
        permission: The permission identifier required
        message: Optional custom message to display when access is denied
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check if user is logged in
            if not st.session_state.get("logged_in", False):
                st.error("Please log in to access this feature.")
                return None
            
            # Get user role and subscription tier
            user_role = st.session_state.get("role", "viewer")
            subscription_tier = st.session_state.get("subscription_tier", "basic")
            
            # Check permission
            if has_permission(user_role, permission, subscription_tier):
                return func(*args, **kwargs)
            else:
                # Display access denied message
                display_message = message or f"Access denied: You don't have the required permission ({permission})."
                
                # Check if this is a tier restriction
                from access_control.roles_config import TIER_REQUIRED_FEATURES
                
                if permission in TIER_REQUIRED_FEATURES:
                    required_tier = TIER_REQUIRED_FEATURES[permission]
                    if required_tier == "premium":
                        display_message = f"This feature requires a Premium subscription. Please upgrade to access it."
                    elif required_tier == "gold":
                        display_message = f"This feature requires a Gold subscription. Please upgrade to access it."
                
                st.error(display_message)
                return None
                
        return wrapper
    return decorator

def requires_role(role: str, message: Optional[str] = None) -> Callable:
    """
    Decorator to protect a function based on a required role.
    
    Args:
        role: The role identifier required
        message: Optional custom message to display when access is denied
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check if user is logged in
            if not st.session_state.get("logged_in", False):
                st.error("Please log in to access this feature.")
                return None
            
            # Get user role
            user_role = st.session_state.get("role", "viewer")
            
            # Check role
            from access_control.roles_config import ROLES
            
            role_priority = ROLES.get(user_role, {}).get("priority", 0)
            required_priority = ROLES.get(role, {}).get("priority", 100)
            
            if role_priority >= required_priority:
                return func(*args, **kwargs)
            else:
                # Display access denied message
                display_message = message or f"Access denied: You need to be a {ROLES.get(role, {}).get('name', role)} to access this feature."
                st.error(display_message)
                return None
                
        return wrapper
    return decorator

def check_permission(permission: str) -> bool:
    """
    Check if the current user has a specific permission
    
    Args:
        permission: The permission identifier to check
        
    Returns:
        True if the user has the permission, False otherwise
    """
    # Check if user is logged in
    if not st.session_state.get("logged_in", False):
        return False
        
    # Get user role and subscription tier
    user_role = st.session_state.get("role", "viewer")
    subscription_tier = st.session_state.get("subscription_tier", "basic")
    
    # Admin users have all permissions automatically
    if user_role == "admin":
        return True
    
    # Check permission for other roles
    return has_permission(user_role, permission, subscription_tier)

def check_role(role: str) -> bool:
    """
    Check if the current user has a specific role or higher
    
    Args:
        role: The role identifier to check
        
    Returns:
        True if the user has the role or higher, False otherwise
    """
    # Check if user is logged in
    if not st.session_state.get("logged_in", False):
        return False
        
    # Get user role
    user_role = st.session_state.get("role", "viewer")
    
    # Check role priority
    from access_control.roles_config import ROLES
    
    role_priority = ROLES.get(user_role, {}).get("priority", 0)
    required_priority = ROLES.get(role, {}).get("priority", 100)
    
    return role_priority >= required_priority

def render_access_denied(permission: str = "", role: str = "") -> None:
    """
    Render an access denied message
    
    Args:
        permission: Optional permission that was denied
        role: Optional role that was required
    """
    if permission and permission != "":
        from access_control.roles_config import PERMISSIONS, TIER_REQUIRED_FEATURES
        
        permission_name = PERMISSIONS.get(permission, permission)
        
        if permission in TIER_REQUIRED_FEATURES:
            required_tier = TIER_REQUIRED_FEATURES[permission]
            st.error(f"Access denied: This feature requires a {required_tier.title()} subscription.")
            
            # Show upgrade button
            if st.button("Upgrade Subscription"):
                # Set session state to show billing page
                st.session_state.active_tab = "billing"
                st.rerun()
        else:
            st.error(f"Access denied: You don't have the required permission ({permission_name}).")
    elif role and role != "":
        from access_control.roles_config import ROLES
        
        role_name = ROLES.get(role, {}).get("name", role)
        st.error(f"Access denied: You need to be a {role_name} to access this feature.")
    else:
        st.error("Access denied: You don't have permission to access this feature.")

def get_user_permissions() -> List[str]:
    """
    Get all permissions for the current user
    
    Returns:
        List of permission identifiers the user has
    """
    # Check if user is logged in
    if not st.session_state.get("logged_in", False):
        return []
        
    # Get user role and subscription tier
    user_role = st.session_state.get("role", "viewer")
    subscription_tier = st.session_state.get("subscription_tier", "basic")
    
    # Get effective permissions
    return get_effective_permissions(user_role, subscription_tier)

def render_permission_ui() -> None:
    """
    Render a UI component showing the current user's permissions
    """
    # Check if user is logged in
    if not st.session_state.get("logged_in", False):
        st.warning("Please log in to view permissions.")
        return
        
    # Get user role and subscription tier
    user_role = st.session_state.get("role", "viewer")
    subscription_tier = st.session_state.get("subscription_tier", "basic")
    
    # Get effective permissions
    permissions = get_effective_permissions(user_role, subscription_tier)
    
    st.markdown("### Your Permissions")
    
    # Group permissions by category
    categories = {}
    for perm in permissions:
        category = perm.split(":")[0] if ":" in perm else "other"
        if category not in categories:
            categories[category] = []
        categories[category].append(perm)
    
    # Display permissions by category
    for category, perms in categories.items():
        st.markdown(f"**{category.title()}**")
        
        for perm in perms:
            perm_name = PERMISSIONS.get(perm, perm)
            st.markdown(f"- {perm_name}")
    
    # Show role and subscription info
    from access_control.roles_config import ROLES
    
    role_name = ROLES.get(user_role, {}).get("name", user_role)
    
    st.markdown("---")
    st.markdown(f"**Role:** {role_name}")
    st.markdown(f"**Subscription:** {subscription_tier.title()}")