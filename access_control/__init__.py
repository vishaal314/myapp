"""
Role-Based Access Control (RBAC) for DataGuardian Pro

This module provides role-based access control for the application, including:
- Permission definitions and checks
- Role-based function decorators
- User management
"""

from access_control.rbac import (
    requires_permission,
    requires_role,
    check_permission,
    check_role,
    render_access_denied,
    get_user_permissions,
    render_permission_ui
)

from access_control.roles_config import (
    ROLES,
    PERMISSIONS,
    ROLE_PERMISSIONS,
    SUBSCRIPTION_FEATURES,
    TIER_REQUIRED_FEATURES,
    get_role_info,
    get_role_permissions,
    get_subscription_features,
    has_permission,
    get_effective_permissions
)

from access_control.user_management import (
    load_users,
    save_users,
    create_user,
    update_user,
    delete_user,
    change_user_role,
    change_user_subscription,
    render_user_management,
    authenticate_user,
    get_permissions_for_role
)