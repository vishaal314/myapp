"""
Session Manager - Memory leak prevention and session cleanup

Handles session state management, cleanup, and prevents memory accumulation
that causes performance issues in the main application.
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class SessionManager:
    """Manages session state with automatic cleanup and memory leak prevention"""
    
    # Keys that should be preserved during cleanup
    PERSISTENT_KEYS = {
        'language', '_persistent_language', 'pre_login_language', 
        'backup_language', 'authenticated', 'username', 'user_email', 
        'user_role', 'premium_member'
    }
    
    # Keys that should be cleaned up regularly
    TEMP_KEYS_PATTERNS = [
        'scan_', 'dpia_', 'simple_dpia_', 'temp_', 'upload_',
        'progress_', 'results_', 'report_', 'form_'
    ]
    
    # Session timeout (30 minutes of inactivity)
    SESSION_TIMEOUT = timedelta(minutes=30)
    
    @staticmethod
    def initialize_session():
        """Initialize session with proper defaults"""
        # Set session start time
        if 'session_start_time' not in st.session_state:
            st.session_state.session_start_time = datetime.now()
        
        # Set last activity time
        st.session_state.last_activity = datetime.now()
        
        # Initialize language if not set
        if 'language' not in st.session_state:
            st.session_state.language = 'en'
            st.session_state._persistent_language = 'en'
            st.session_state.backup_language = 'en'
        
        # Initialize authentication state
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
    
    @staticmethod
    def update_activity():
        """Update last activity timestamp"""
        st.session_state.last_activity = datetime.now()
    
    @staticmethod
    def check_session_timeout() -> bool:
        """Check if session has timed out"""
        if 'last_activity' not in st.session_state:
            return False
        
        last_activity = st.session_state.last_activity
        if datetime.now() - last_activity > SessionManager.SESSION_TIMEOUT:
            SessionManager.cleanup_expired_session()
            return True
        
        return False
    
    @staticmethod
    def cleanup_expired_session():
        """Clean up expired session while preserving essential data"""
        logger.info("Cleaning up expired session")
        
        # Preserve essential data
        preserved_data = {}
        for key in SessionManager.PERSISTENT_KEYS:
            if key in st.session_state:
                preserved_data[key] = st.session_state[key]
        
        # Clear all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        # Restore essential data
        for key, value in preserved_data.items():
            st.session_state[key] = value
        
        # Mark as logged out due to timeout
        st.session_state.authenticated = False
        st.session_state.session_expired = True
    
    @staticmethod
    def cleanup_temporary_data():
        """Clean up temporary session data to prevent memory leaks"""
        cleanup_count = 0
        
        for key in list(st.session_state.keys()):
            # Skip persistent keys
            if key in SessionManager.PERSISTENT_KEYS:
                continue
            
            # Check if key matches temporary patterns
            should_cleanup = any(
                str(key).startswith(pattern) for pattern in SessionManager.TEMP_KEYS_PATTERNS
            )
            
            if should_cleanup:
                try:
                    del st.session_state[key]
                    cleanup_count += 1
                except Exception as e:
                    logger.warning(f"Error cleaning up session key {key}: {e}")
        
        logger.info(f"Cleaned up {cleanup_count} temporary session keys")
        return cleanup_count
    
    @staticmethod
    def get_session_info() -> Dict[str, Any]:
        """Get session information for debugging"""
        session_info = {
            'total_keys': len(st.session_state.keys()),
            'session_start': st.session_state.get('session_start_time'),
            'last_activity': st.session_state.get('last_activity'),
            'authenticated': st.session_state.get('authenticated', False),
            'language': st.session_state.get('language', 'en'),
            'temp_keys': []
        }
        
        # Count temporary keys
        for key in st.session_state.keys():
            if any(str(key).startswith(pattern) for pattern in SessionManager.TEMP_KEYS_PATTERNS):
                session_info['temp_keys'].append(key)
        
        session_info['temp_key_count'] = len(session_info['temp_keys'])
        
        return session_info
    
    @staticmethod
    def reset_session():
        """Complete session reset (for logout)"""
        # Preserve language settings
        language = st.session_state.get('language', 'en')
        persistent_language = st.session_state.get('_persistent_language', 'en')
        
        # Clear all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        # Restore language and reinitialize
        st.session_state.language = language
        st.session_state._persistent_language = persistent_language
        st.session_state.backup_language = language
        st.session_state.force_language_after_login = language
        
        SessionManager.initialize_session()
    
    @staticmethod
    def preserve_language_and_reset():
        """Reset session while preserving language settings"""
        # Get current language settings
        language_settings = {
            'language': st.session_state.get('language', 'en'),
            '_persistent_language': st.session_state.get('_persistent_language', 'en'),
            'pre_login_language': st.session_state.get('pre_login_language', 'en'),
            'backup_language': st.session_state.get('backup_language', 'en')
        }
        
        # Clear non-language session state
        keys_to_remove = []
        for key in st.session_state.keys():
            if key not in language_settings:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            try:
                del st.session_state[key]
            except Exception as e:
                logger.warning(f"Error removing session key {key}: {e}")
        
        # Ensure language settings are preserved
        for key, value in language_settings.items():
            st.session_state[key] = value
        
        # Reinitialize session
        SessionManager.initialize_session()


def fix_variable_scoping():
    """Fix common variable scoping issues by ensuring proper initialization"""
    
    # Language variables
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    
    current_language = st.session_state.get('language', 'en')
    
    # Navigation variables
    navigation_defaults = {
        'selected_nav': 'Dashboard',
        'scan_title': 'Scan',
        'dashboard_title': 'Dashboard', 
        'history_title': 'History',
        'results_title': 'Results',
        'report_title': 'Report'
    }
    
    for key, default_value in navigation_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    # Authentication variables
    auth_defaults = {
        'authenticated': False,
        'username': '',
        'user_email': '',
        'user_role': 'user',
        'premium_member': False
    }
    
    for key, default_value in auth_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    # Membership variables
    membership_defaults = {
        'membership_details': {},
        'free_trial_active': False,
        'free_trial_days_left': 0
    }
    
    for key, default_value in membership_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    return current_language


def get_safe_session_value(key: str, default: Any = None) -> Any:
    """Safely get session state value with default"""
    return st.session_state.get(key, default)


def set_safe_session_value(key: str, value: Any) -> None:
    """Safely set session state value"""
    try:
        st.session_state[key] = value
    except Exception as e:
        logger.warning(f"Error setting session key {key}: {e}")


# Session middleware for automatic management
def session_middleware():
    """Middleware to be called on every page load"""
    SessionManager.initialize_session()
    SessionManager.update_activity()
    
    # Check for session timeout
    if SessionManager.check_session_timeout():
        st.warning("Your session has expired due to inactivity. Please log in again.")
        return False
    
    # Periodic cleanup (every 50 page loads to prevent memory buildup)
    if 'cleanup_counter' not in st.session_state:
        st.session_state.cleanup_counter = 0
    
    st.session_state.cleanup_counter += 1
    
    if st.session_state.cleanup_counter >= 50:
        SessionManager.cleanup_temporary_data()
        st.session_state.cleanup_counter = 0
    
    # Fix variable scoping issues
    fix_variable_scoping()
    
    return True