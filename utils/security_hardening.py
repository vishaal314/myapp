"""
Security Hardening Module for DataGuardian Pro
Implements additional security measures including encryption, secure logging, and session protection
"""

import os
import logging
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from cryptography.fernet import Fernet
import streamlit as st

# Security audit logger
security_logger = logging.getLogger('security_audit')
security_handler = logging.FileHandler('logs/security_audit.log')
security_handler.setFormatter(logging.Formatter(
    '%(asctime)s - SECURITY - %(levelname)s - [IP:%(ip)s] - %(message)s'
))
security_logger.addHandler(security_handler)
security_logger.setLevel(logging.INFO)

class SecurityHardening:
    """Enhanced security measures for DataGuardian Pro"""
    
    def __init__(self):
        self.encryption_key = self._get_or_create_encryption_key()
        self.fernet = Fernet(self.encryption_key)
        self.failed_attempts = {}  # IP -> failed attempts tracking
        self.session_tokens = {}   # Active session tokens
        
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for sensitive data"""
        key_file = 'security/encryption.key'
        os.makedirs('security', exist_ok=True)
        
        try:
            if os.path.exists(key_file):
                with open(key_file, 'rb') as f:
                    return f.read()
            else:
                # Generate new key
                key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(key)
                # Set restrictive permissions
                os.chmod(key_file, 0o600)
                self.log_security_event("encryption_key_created", "New encryption key generated")
                return key
        except Exception as e:
            self.log_security_event("encryption_key_error", f"Failed to manage encryption key: {str(e)[:50]}...")
            raise
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data before storage"""
        try:
            return self.fernet.encrypt(data.encode()).decode()
        except Exception as e:
            self.log_security_event("encryption_error", f"Failed to encrypt data: {str(e)[:30]}...")
            raise
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data after retrieval"""
        try:
            return self.fernet.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            self.log_security_event("decryption_error", f"Failed to decrypt data: {str(e)[:30]}...")
            raise
    
    def log_security_event(self, event_type: str, message: str, username: Optional[str] = None):
        """Log security events with proper sanitization"""
        # Get client IP safely
        client_ip = self.get_client_ip()
        
        # Sanitize message to prevent log injection
        sanitized_message = self.sanitize_log_message(message)
        
        # Create security log entry
        extra = {'ip': client_ip}
        security_logger.info(
            f"[{event_type.upper()}] User: {username or 'anonymous'} - {sanitized_message}",
            extra=extra
        )
    
    def get_client_ip(self) -> str:
        """Get client IP address safely"""
        try:
            # In Streamlit, we can't easily get real IP, so use session ID as identifier
            return st.session_state.get('session_id', 'unknown')[:8]
        except:
            return 'unknown'
    
    def sanitize_log_message(self, message: str) -> str:
        """Sanitize log messages to prevent injection attacks"""
        if not message:
            return "empty_message"
        
        # Remove potential log injection characters
        sanitized = message.replace('\n', '').replace('\r', '').replace('\t', ' ')
        # Limit length to prevent log flooding
        return sanitized[:200] if len(sanitized) > 200 else sanitized
    
    def check_rate_limiting(self, identifier: str, max_attempts: int = 5, window_minutes: int = 15) -> bool:
        """Check if user/IP is rate limited"""
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)
        
        if identifier in self.failed_attempts:
            # Clean old attempts
            self.failed_attempts[identifier] = [
                attempt for attempt in self.failed_attempts[identifier]
                if attempt > window_start
            ]
            
            if len(self.failed_attempts[identifier]) >= max_attempts:
                self.log_security_event("rate_limit_exceeded", f"Rate limit exceeded for {identifier}")
                return False
        
        return True
    
    def record_failed_attempt(self, identifier: str):
        """Record failed authentication attempt"""
        if identifier not in self.failed_attempts:
            self.failed_attempts[identifier] = []
        
        self.failed_attempts[identifier].append(datetime.now())
        self.log_security_event("auth_failed", f"Failed authentication attempt: {identifier}")
    
    def generate_secure_session_token(self) -> str:
        """Generate cryptographically secure session token"""
        return secrets.token_urlsafe(32)
    
    def validate_session_security(self) -> bool:
        """Validate current session security parameters"""
        try:
            # Check session age
            session_start = st.session_state.get('session_start')
            if session_start:
                session_age = datetime.now() - datetime.fromisoformat(session_start)
                if session_age.total_seconds() > 28800:  # 8 hours max session
                    self.log_security_event("session_expired", "Session expired due to age")
                    return False
            
            # Check for session hijacking indicators
            current_user_agent = st.session_state.get('user_agent')
            stored_user_agent = st.session_state.get('initial_user_agent')
            
            if stored_user_agent and current_user_agent != stored_user_agent:
                self.log_security_event("session_hijack_attempt", "User agent mismatch detected")
                return False
            
            return True
        except Exception as e:
            self.log_security_event("session_validation_error", f"Session validation failed: {str(e)[:50]}...")
            return False
    
    def secure_error_handler(self, error: Exception, context: str = "") -> str:
        """Handle errors securely without information leakage"""
        # Generate error ID for tracking
        error_id = secrets.token_hex(8)
        
        # Log detailed error internally
        self.log_security_event(
            "application_error", 
            f"Error ID: {error_id} - Context: {context} - Error: {str(error)[:100]}..."
        )
        
        # Return sanitized error message to user
        return f"An error occurred. Reference ID: {error_id}. Please contact support if the issue persists."
    
    def sanitize_user_input(self, user_input: str, max_length: int = 1000) -> str:
        """Sanitize user input to prevent various injection attacks"""
        if not user_input:
            return ""
        
        # Limit length
        sanitized = user_input[:max_length]
        
        # Remove potential script injections
        dangerous_patterns = ['<script', 'javascript:', 'onload=', 'onerror=', 'eval(']
        for pattern in dangerous_patterns:
            sanitized = sanitized.replace(pattern.lower(), '').replace(pattern.upper(), '')
        
        return sanitized.strip()

# Global security instance
_security_hardening = None

def get_security_hardening() -> SecurityHardening:
    """Get global security hardening instance"""
    global _security_hardening
    if _security_hardening is None:
        _security_hardening = SecurityHardening()
    return _security_hardening

def secure_log(event_type: str, message: str, username: Optional[str] = None):
    """Convenience function for secure logging"""
    security = get_security_hardening()
    security.log_security_event(event_type, message, username)

def validate_session():
    """Convenience function for session validation"""
    security = get_security_hardening()
    return security.validate_session_security()

def handle_error_securely(error: Exception, context: str = "") -> str:
    """Convenience function for secure error handling"""
    security = get_security_hardening()
    return security.secure_error_handler(error, context)