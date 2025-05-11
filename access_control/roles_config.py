"""
Role-Based Access Control Configuration for DataGuardian Pro

This module defines the roles, permissions, and access levels for the application.
It provides the core configuration for the RBAC system.
"""

from typing import Dict, List, Set, Any, Optional

# Define the available roles
ROLES = {
    "admin": {
        "name": "Administrator",
        "description": "Complete system access with all permissions",
        "priority": 100
    },
    "security_engineer": {
        "name": "Security Engineer",
        "description": "Configure and manage security settings and scans",
        "priority": 80
    },
    "auditor": {
        "name": "Compliance Auditor",
        "description": "View and audit compliance findings",
        "priority": 60
    },
    "team_manager": {
        "name": "Team Manager",
        "description": "Manage team members and view reports",
        "priority": 40
    },
    "viewer": {
        "name": "Basic User",
        "description": "View basic reports and run assigned scans",
        "priority": 20
    }
}

# Define permissions by category
PERMISSIONS = {
    # Scan permissions
    "scan:run_any": "Run any scan type",
    "scan:run_basic": "Run basic scans only",
    "scan:view_all": "View all scan results",
    "scan:view_own": "View own scan results only",
    "scan:delete": "Delete scan results",
    "scan:configure": "Configure scan settings",
    
    # Report permissions
    "report:view_all": "View all reports",
    "report:view_own": "View own reports only",
    "report:export": "Export reports",
    "report:generate": "Generate custom reports",
    "report:delete": "Delete reports",
    
    # Admin permissions
    "admin:users": "Manage users",
    "admin:roles": "Manage roles",
    "admin:settings": "Manage system settings",
    "admin:billing": "Manage billing and subscriptions",
    "admin:api_keys": "Manage API keys",
    
    # Feature permissions
    "feature:advanced_analytics": "Access advanced analytics",
    "feature:custom_policies": "Create custom compliance policies",
    "feature:integrations": "Configure third-party integrations",
    "feature:api_access": "API access",
    "feature:soc2": "SOC2 scanner access",
    "feature:sustainability": "Sustainability scanner access",
    
    # Team permissions
    "team:view": "View team members",
    "team:invite": "Invite team members",
    "team:remove": "Remove team members",
    "team:assign_role": "Assign roles to team members"
}

# Define role permissions (which permissions each role has)
ROLE_PERMISSIONS = {
    "admin": list(PERMISSIONS.keys()),  # Admin has all permissions
    
    "security_engineer": [
        "scan:run_any", "scan:view_all", "scan:delete", "scan:configure",
        "report:view_all", "report:export", "report:generate",
        "admin:settings", "admin:api_keys",
        "feature:advanced_analytics", "feature:custom_policies", "feature:integrations", 
        "feature:api_access", "feature:soc2", "feature:sustainability",
        "team:view"
    ],
    
    "auditor": [
        "scan:view_all",
        "report:view_all", "report:export", "report:generate",
        "feature:advanced_analytics",
        "team:view"
    ],
    
    "team_manager": [
        "scan:run_basic", "scan:view_all", 
        "report:view_all", "report:export",
        "team:view", "team:invite", "team:remove"
    ],
    
    "viewer": [
        "scan:run_basic", "scan:view_own",
        "report:view_own", "report:export",
        "feature:sustainability"  # Everyone can use sustainability scanner
    ]
}

# Define feature access based on subscription tiers
SUBSCRIPTION_FEATURES = {
    "basic": [
        "scan:run_basic", "scan:view_own",
        "report:view_own", "report:export",
        "feature:sustainability"
    ],
    
    "premium": [
        "scan:run_any", "scan:view_all", "scan:configure",
        "report:view_all", "report:export", "report:generate",
        "feature:advanced_analytics", "feature:soc2", "feature:sustainability",
        "team:view", "team:invite"
    ],
    
    "gold": list(PERMISSIONS.keys())  # Gold tier has access to all features
}

# Features that require a certain subscription tier
TIER_REQUIRED_FEATURES = {
    "feature:advanced_analytics": "premium",
    "feature:custom_policies": "gold",
    "feature:integrations": "premium",
    "feature:api_access": "gold",
    "feature:soc2": "premium",
    "admin:api_keys": "premium",
    "team:invite": "premium",
    "team:remove": "premium",
    "team:assign_role": "gold"
}

def get_role_info(role: str) -> Dict[str, Any]:
    """
    Get information about a specific role
    
    Args:
        role: Role identifier
        
    Returns:
        Dictionary with role information
    """
    return ROLES.get(role, ROLES["viewer"])

def get_role_permissions(role: str) -> List[str]:
    """
    Get permissions for a specific role
    
    Args:
        role: Role identifier
        
    Returns:
        List of permission identifiers
    """
    return ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS["viewer"])

def get_subscription_features(tier: str) -> List[str]:
    """
    Get features available for a specific subscription tier
    
    Args:
        tier: Subscription tier identifier
        
    Returns:
        List of feature identifiers
    """
    return SUBSCRIPTION_FEATURES.get(tier, SUBSCRIPTION_FEATURES["basic"])

def has_permission(user_role: str, permission: str, subscription_tier: str = "basic") -> bool:
    """
    Check if a user has a specific permission based on role and subscription tier
    
    Args:
        user_role: User's role
        permission: Permission to check
        subscription_tier: User's subscription tier
        
    Returns:
        True if the user has the permission, False otherwise
    """
    # Get permissions for the user's role
    role_permissions = get_role_permissions(user_role)
    
    # Get features for the user's subscription tier
    subscription_features = get_subscription_features(subscription_tier)
    
    # Check if permission is in role permissions
    has_role_permission = permission in role_permissions
    
    # If this feature requires a specific tier, check if user's tier is sufficient
    if permission in TIER_REQUIRED_FEATURES:
        required_tier = TIER_REQUIRED_FEATURES[permission]
        tier_priority = {
            "basic": 1,
            "premium": 2,
            "gold": 3
        }
        
        has_tier_permission = tier_priority.get(subscription_tier, 0) >= tier_priority.get(required_tier, 0)
    else:
        has_tier_permission = True
    
    # User needs both role permission and subscription tier
    return has_role_permission and has_tier_permission

def get_effective_permissions(user_role: str, subscription_tier: str = "basic") -> List[str]:
    """
    Get all effective permissions for a user based on role and subscription tier
    
    Args:
        user_role: User's role
        subscription_tier: User's subscription tier
        
    Returns:
        List of all permissions the user has
    """
    # Get permissions for the user's role
    role_permissions = get_role_permissions(user_role)
    
    # Filter based on subscription tier
    effective_permissions = []
    for permission in role_permissions:
        if permission in TIER_REQUIRED_FEATURES:
            required_tier = TIER_REQUIRED_FEATURES[permission]
            tier_priority = {
                "basic": 1,
                "premium": 2,
                "gold": 3
            }
            
            if tier_priority.get(subscription_tier, 0) >= tier_priority.get(required_tier, 0):
                effective_permissions.append(permission)
        else:
            effective_permissions.append(permission)
    
    return effective_permissions