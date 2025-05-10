"""
Usage Tracker Module for DataGuardian Pro

This module tracks and manages usage limits for subscription plans, including:
- Scans per month tracking
- Repository limits
- Usage analytics
- Quota enforcement
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import streamlit as st

# Import plan configuration
from billing.plans_config import get_plan_by_tier, get_limit

# Path to store usage data
USAGE_DATA_PATH = "data/usage_data.json"

# Ensure the data directory exists
os.makedirs(os.path.dirname(USAGE_DATA_PATH), exist_ok=True)

def _load_usage_data() -> Dict[str, Any]:
    """
    Load usage data from file
    
    Returns:
        Dictionary with usage data for all users
    """
    try:
        if os.path.exists(USAGE_DATA_PATH):
            with open(USAGE_DATA_PATH, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        st.error(f"Error loading usage data: {str(e)}")
        return {}

def _save_usage_data(usage_data: Dict[str, Any]) -> bool:
    """
    Save usage data to file
    
    Args:
        usage_data: Dictionary with usage data for all users
        
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        with open(USAGE_DATA_PATH, 'w') as f:
            json.dump(usage_data, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving usage data: {str(e)}")
        return False

def _get_current_period() -> str:
    """
    Get the current billing period (YYYY-MM)
    
    Returns:
        String representing the current month in YYYY-MM format
    """
    return datetime.now().strftime("%Y-%m")

def get_user_usage(username: str) -> Dict[str, Any]:
    """
    Get usage statistics for a user
    
    Args:
        username: Username to get usage for
        
    Returns:
        Dictionary with usage metrics
    """
    usage_data = _load_usage_data()
    
    # Get or create user entry
    if username not in usage_data:
        usage_data[username] = {
            "scans": {},
            "repositories": set(),
            "last_updated": datetime.now().isoformat()
        }
        _save_usage_data(usage_data)
    
    user_data = usage_data[username]
    current_period = _get_current_period()
    
    # Ensure current period exists
    if current_period not in user_data.get("scans", {}):
        user_data["scans"][current_period] = {
            "total": 0,
            "by_type": {}
        }
    
    # Convert repositories from list to set and back (for JSON serialization)
    if "repositories" in user_data and isinstance(user_data["repositories"], list):
        user_data["repositories"] = set(user_data["repositories"])
    
    return user_data

def track_scan(username: str, scan_type: str, repository_url: Optional[str] = None) -> Tuple[bool, str]:
    """
    Track a scan for usage limits
    
    Args:
        username: Username performing the scan
        scan_type: Type of scan being performed
        repository_url: Optional repository URL being scanned
        
    Returns:
        Tuple of (allowed, message) indicating if scan is allowed and reason
    """
    usage_data = _load_usage_data()
    user_usage = get_user_usage(username)
    current_period = _get_current_period()
    
    # Get user's subscription tier
    subscription_tier = st.session_state.get("subscription_tier", "basic")
    
    # Check repository limit
    if repository_url and repository_url not in user_usage["repositories"]:
        repositories = user_usage["repositories"]
        if isinstance(repositories, list):
            repositories = set(repositories)
        
        repo_limit = get_limit(subscription_tier, "repositories")
        if repo_limit != float('inf') and len(repositories) >= repo_limit:
            return False, f"Repository limit reached ({repo_limit}). Please upgrade your plan to add more repositories."
    
    # Check scan limit
    scans_this_month = user_usage["scans"].get(current_period, {}).get("total", 0)
    scan_limit = get_limit(subscription_tier, "scans_per_month")
    
    if scan_limit != float('inf') and scans_this_month >= scan_limit:
        return False, f"Monthly scan limit reached ({scan_limit}). Please upgrade your plan for more scans."
    
    # Track the scan
    if current_period not in user_usage["scans"]:
        user_usage["scans"][current_period] = {"total": 0, "by_type": {}}
    
    user_usage["scans"][current_period]["total"] += 1
    
    # Track by scan type
    if scan_type not in user_usage["scans"][current_period]["by_type"]:
        user_usage["scans"][current_period]["by_type"][scan_type] = 0
    user_usage["scans"][current_period]["by_type"][scan_type] += 1
    
    # Track repository
    if repository_url:
        if isinstance(user_usage["repositories"], set):
            user_usage["repositories"].add(repository_url)
        else:
            user_usage["repositories"] = set([repository_url])
    
    # Convert sets to lists for JSON serialization
    user_usage["repositories"] = list(user_usage["repositories"])
    
    # Update last updated timestamp
    user_usage["last_updated"] = datetime.now().isoformat()
    
    # Save updated usage data
    usage_data[username] = user_usage
    _save_usage_data(usage_data)
    
    return True, "Scan tracked successfully"

def get_usage_metrics(username: str) -> Dict[str, Any]:
    """
    Get usage metrics for display in the dashboard
    
    Args:
        username: Username to get metrics for
        
    Returns:
        Dictionary with formatted usage metrics
    """
    user_usage = get_user_usage(username)
    current_period = _get_current_period()
    
    # Get subscription tier
    subscription_tier = st.session_state.get("subscription_tier", "basic")
    
    # Get limits from the plan
    scan_limit = get_limit(subscription_tier, "scans_per_month")
    repo_limit = get_limit(subscription_tier, "repositories")
    
    # Format repository limit for display
    if repo_limit == float('inf'):
        repo_limit_display = "Unlimited"
    else:
        repo_limit_display = str(repo_limit)
    
    # Format scan limit for display
    if scan_limit == float('inf'):
        scan_limit_display = "Unlimited"
    else:
        scan_limit_display = str(scan_limit)
    
    # Count repositories
    repositories = user_usage.get("repositories", [])
    if isinstance(repositories, set):
        repo_count = len(repositories)
    else:
        repo_count = len(set(repositories))
    
    # Count scans this month
    scans_this_month = user_usage.get("scans", {}).get(current_period, {}).get("total", 0)
    
    # Breakdown by scan type
    scan_types = user_usage.get("scans", {}).get(current_period, {}).get("by_type", {})
    
    # Calculate percentages
    scan_percentage = 0
    if scan_limit != float('inf') and scan_limit > 0:
        scan_percentage = min(100, int((scans_this_month / scan_limit) * 100))
    
    repo_percentage = 0
    if repo_limit != float('inf') and repo_limit > 0:
        repo_percentage = min(100, int((repo_count / repo_limit) * 100))
    
    return {
        "scans_used": scans_this_month,
        "scans_limit": scan_limit_display,
        "scan_percentage": scan_percentage,
        "repositories_used": repo_count,
        "repositories_limit": repo_limit_display,
        "repository_percentage": repo_percentage,
        "scan_types": scan_types,
        "current_period": current_period,
        "period_start": datetime.now().replace(day=1).strftime("%Y-%m-%d"),
        "period_end": (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1, hour=0, minute=0, second=0, microsecond=0).strftime("%Y-%m-%d")
    }

def reset_usage(username: str) -> bool:
    """
    Reset usage statistics for a user (admin function)
    
    Args:
        username: Username to reset usage for
        
    Returns:
        True if reset successfully, False otherwise
    """
    try:
        usage_data = _load_usage_data()
        
        if username in usage_data:
            current_period = _get_current_period()
            
            # Reset scans for current period
            if current_period in usage_data[username].get("scans", {}):
                usage_data[username]["scans"][current_period] = {
                    "total": 0,
                    "by_type": {}
                }
            
            # Save updated usage data
            _save_usage_data(usage_data)
            
        return True
    except Exception as e:
        st.error(f"Error resetting usage data: {str(e)}")
        return False