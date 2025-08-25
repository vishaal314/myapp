"""
Secure Error Handler for DataGuardian Pro
Prevents information leakage through error messages
"""

import streamlit as st
import secrets
import traceback
from typing import Optional, Any
from utils.security_hardening import get_security_hardening, secure_log

class SecureErrorHandler:
    """Handle errors without leaking sensitive information"""
    
    def __init__(self):
        self.security = get_security_hardening()
        self.debug_mode = False  # Set to True only for development
    
    def handle_exception(self, e: Exception, context: str = "", user_message: str = None) -> str:
        """Handle exceptions securely"""
        # Generate unique error ID for tracking
        error_id = secrets.token_hex(8)
        
        # Get user context safely
        username = st.session_state.get('username', 'anonymous')
        
        # Log detailed error for debugging (internal only)
        secure_log(
            "application_error",
            f"Error ID: {error_id} | Context: {context} | Error: {str(e)[:100]}...",
            username
        )
        
        # Log full traceback in debug mode only
        if self.debug_mode:
            secure_log(
                "debug_traceback",
                f"Error ID: {error_id} | Traceback: {traceback.format_exc()[:500]}...",
                username
            )
        
        # Return sanitized error message
        if user_message:
            return f"{user_message} (Error ID: {error_id})"
        else:
            return f"An error occurred while processing your request. Error ID: {error_id}"
    
    def handle_authentication_error(self, username: str = "unknown") -> str:
        """Handle authentication errors securely"""
        # Record failed attempt for rate limiting
        client_ip = self.security.get_client_ip()
        self.security.record_failed_attempt(client_ip)
        
        secure_log("auth_failed", f"Authentication failed for user: {username}")
        
        return "Invalid credentials. Please check your username and password."
    
    def handle_permission_error(self, required_permission: str, username: str = "unknown") -> str:
        """Handle permission errors securely"""
        secure_log("permission_denied", f"Access denied for user: {username} | Required: {required_permission}")
        
        return "You don't have permission to access this feature. Please contact your administrator."
    
    def handle_rate_limit_error(self, identifier: str) -> str:
        """Handle rate limiting errors"""
        secure_log("rate_limit_hit", f"Rate limit exceeded for: {identifier}")
        
        return "Too many requests. Please wait a few minutes before trying again."
    
    def handle_validation_error(self, field_name: str, username: str = "unknown") -> str:
        """Handle input validation errors securely"""
        secure_log("validation_error", f"Invalid input in field: {field_name} | User: {username}")
        
        return f"Invalid input provided for {field_name}. Please check your input and try again."
    
    def handle_scanner_error(self, scanner_type: str, error: Exception, username: str = "unknown") -> str:
        """Handle scanner-specific errors securely"""
        error_id = secrets.token_hex(6)
        
        secure_log(
            "scanner_error",
            f"Scanner: {scanner_type} | Error ID: {error_id} | Error: {str(error)[:50]}...",
            username
        )
        
        return f"{scanner_type} scan failed. Error ID: {error_id}. Please try again or contact support."
    
    def create_safe_error_display(self, error_message: str, show_details: bool = False):
        """Create safe error display in Streamlit"""
        st.error(error_message)
        
        if show_details and self.debug_mode:
            with st.expander("Debug Information (Development Only)"):
                st.code("Enable debug mode to see detailed error information")
    
    def sanitize_user_data(self, data: Any) -> str:
        """Sanitize user data for safe display"""
        if data is None:
            return "None"
        
        # Convert to string and sanitize
        str_data = str(data)
        sanitized = self.security.sanitize_user_input(str_data, max_length=200)
        
        return sanitized

# Global secure error handler
_secure_error_handler = None

def get_secure_error_handler() -> SecureErrorHandler:
    """Get global secure error handler instance"""
    global _secure_error_handler
    if _secure_error_handler is None:
        _secure_error_handler = SecureErrorHandler()
    return _secure_error_handler

def handle_error(e: Exception, context: str = "", user_message: str = None) -> str:
    """Convenience function for secure error handling"""
    handler = get_secure_error_handler()
    return handler.handle_exception(e, context, user_message)

def show_secure_error(error_message: str, show_details: bool = False):
    """Convenience function for secure error display"""
    handler = get_secure_error_handler()
    handler.create_safe_error_display(error_message, show_details)