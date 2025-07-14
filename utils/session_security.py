"""
Session Security Manager
Handles secure session management with JWT tokens and session validation
"""
import streamlit as st
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SessionSecurityManager:
    """Manages secure session with JWT token validation"""
    
    def __init__(self):
        self.session_timeout = 24 * 60 * 60  # 24 hours in seconds
        
    def create_secure_session(self, auth_result) -> None:
        """Create secure session with JWT token"""
        if not auth_result.success:
            return
            
        # Store secure session data
        st.session_state.authenticated = True
        st.session_state.username = auth_result.username
        st.session_state.user_role = auth_result.role
        st.session_state.user_id = auth_result.user_id
        st.session_state.auth_token = auth_result.token
        st.session_state.login_time = datetime.utcnow().isoformat()
        st.session_state.expires_at = auth_result.expires_at.isoformat() if auth_result.expires_at else None
        
        logger.info(f"Secure session created for user: {auth_result.username}")
    
    def validate_session(self) -> bool:
        """Validate current session and JWT token"""
        if not st.session_state.get('authenticated', False):
            return False
            
        token = st.session_state.get('auth_token')
        if not token:
            logger.warning("No auth token found in session")
            self.clear_session()
            return False
            
        try:
            from utils.secure_auth_enhanced import validate_token
            auth_result = validate_token(token)
            
            if auth_result.success:
                # Update session with fresh data
                st.session_state.username = auth_result.username
                st.session_state.user_role = auth_result.role
                st.session_state.user_id = auth_result.user_id
                return True
            else:
                logger.warning(f"Token validation failed: {auth_result.message}")
                self.clear_session()
                return False
                
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            self.clear_session()
            return False
    
    def clear_session(self) -> None:
        """Clear all session data"""
        keys_to_clear = [
            'authenticated', 'username', 'user_role', 'user_id', 
            'auth_token', 'login_time', 'expires_at'
        ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
                
        logger.info("Session cleared")
    
    def get_session_info(self) -> Optional[Dict[str, Any]]:
        """Get current session information"""
        if not st.session_state.get('authenticated', False):
            return None
            
        return {
            'username': st.session_state.get('username'),
            'user_role': st.session_state.get('user_role'),
            'user_id': st.session_state.get('user_id'),
            'login_time': st.session_state.get('login_time'),
            'expires_at': st.session_state.get('expires_at')
        }
    
    def logout(self) -> None:
        """Logout user and clear session"""
        username = st.session_state.get('username', 'unknown')
        self.clear_session()
        logger.info(f"User {username} logged out")

# Global instance
_session_manager = None

def get_session_manager() -> SessionSecurityManager:
    """Get global session manager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionSecurityManager()
    return _session_manager

def validate_current_session() -> bool:
    """Validate current session"""
    return get_session_manager().validate_session()

def logout_user() -> None:
    """Logout current user"""
    get_session_manager().logout()

def get_current_user() -> Optional[Dict[str, Any]]:
    """Get current user session info"""
    return get_session_manager().get_session_info()