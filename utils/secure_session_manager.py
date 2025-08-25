"""
Secure Session Manager for DataGuardian Pro
Enhanced session security with encryption and monitoring
"""

import streamlit as st
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from utils.security_hardening import get_security_hardening, secure_log

class SecureSessionManager:
    """Enhanced session management with security features"""
    
    def __init__(self):
        self.security = get_security_hardening()
        self.max_session_age = timedelta(hours=8)
        self.session_timeout = timedelta(minutes=30)
    
    def initialize_secure_session(self, username: str) -> str:
        """Initialize a secure session with proper security measures"""
        try:
            # Generate secure session token
            session_token = self.security.generate_secure_session_token()
            
            # Set session security parameters
            st.session_state.update({
                'session_token': session_token,
                'session_start': datetime.now().isoformat(),
                'last_activity': datetime.now().isoformat(),
                'username': username,
                'user_id': username,  # For backwards compatibility
                'session_id': session_token[:16],  # Shorter ID for logs
                'security_validated': True,
                'login_ip': self.security.get_client_ip(),
            })
            
            secure_log("session_created", f"Secure session initialized for user: {username}", username)
            return session_token
            
        except Exception as e:
            secure_log("session_error", f"Failed to initialize session: {str(e)[:50]}...", username)
            raise
    
    def validate_session(self) -> bool:
        """Validate current session security"""
        try:
            if not st.session_state.get('session_token'):
                return False
            
            # Check session age
            session_start = st.session_state.get('session_start')
            if session_start:
                session_age = datetime.now() - datetime.fromisoformat(session_start)
                if session_age > self.max_session_age:
                    secure_log("session_expired", "Session expired due to maximum age")
                    self.terminate_session()
                    return False
            
            # Check session timeout
            last_activity = st.session_state.get('last_activity')
            if last_activity:
                inactivity = datetime.now() - datetime.fromisoformat(last_activity)
                if inactivity > self.session_timeout:
                    secure_log("session_timeout", "Session expired due to inactivity")
                    self.terminate_session()
                    return False
            
            # Update last activity
            st.session_state['last_activity'] = datetime.now().isoformat()
            
            # Perform additional security validation
            return self.security.validate_session_security()
            
        except Exception as e:
            secure_log("session_validation_error", f"Session validation failed: {str(e)[:50]}...")
            return False
    
    def terminate_session(self):
        """Securely terminate current session"""
        username = st.session_state.get('username', 'unknown')
        secure_log("session_terminated", f"Session terminated for user: {username}", username)
        
        # Clear sensitive session data
        sensitive_keys = [
            'session_token', 'username', 'user_id', 'session_id',
            'security_validated', 'login_ip', 'permissions',
            'role', 'session_start', 'last_activity'
        ]
        
        for key in sensitive_keys:
            if key in st.session_state:
                del st.session_state[key]
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get safe session information for display"""
        if not self.validate_session():
            return {}
        
        return {
            'username': st.session_state.get('username', 'unknown'),
            'session_age': self._get_session_age(),
            'last_activity': st.session_state.get('last_activity'),
            'role': st.session_state.get('role', 'user'),
            'session_id': st.session_state.get('session_id', 'unknown')[:8],
        }
    
    def _get_session_age(self) -> str:
        """Get human-readable session age"""
        session_start = st.session_state.get('session_start')
        if not session_start:
            return 'unknown'
        
        age = datetime.now() - datetime.fromisoformat(session_start)
        hours = int(age.total_seconds() // 3600)
        minutes = int((age.total_seconds() % 3600) // 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"

# Global secure session manager
_secure_session_manager = None

def get_secure_session_manager() -> SecureSessionManager:
    """Get global secure session manager instance"""
    global _secure_session_manager
    if _secure_session_manager is None:
        _secure_session_manager = SecureSessionManager()
    return _secure_session_manager