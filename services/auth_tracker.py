"""
Authentication Tracking Wrapper
Clean integration layer for visitor tracking without modifying core auth.py

This module wraps existing authentication functions to add GDPR-compliant tracking
"""

import logging
import uuid
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any
from services.visitor_tracker import get_visitor_tracker, VisitorEventType
from services.auth import authenticate as _auth_authenticate, create_user as _auth_create_user

logger = logging.getLogger(__name__)

def get_client_ip_from_streamlit() -> str:
    """
    Get client IP address from Streamlit context
    Falls back to 'unknown' if not available
    
    Returns:
        str: Client IP address (will be anonymized by VisitorTracker)
    """
    try:
        import streamlit as st
        
        # Try to get from X-Forwarded-For header (if behind proxy)
        if hasattr(st, 'context') and hasattr(st.context, 'headers'):
            forwarded_for = st.context.headers.get('X-Forwarded-For')
            if forwarded_for:
                # Get first IP in chain
                return forwarded_for.split(',')[0].strip()
            
            # Try to get from X-Real-IP header
            real_ip = st.context.headers.get('X-Real-IP')
            if real_ip:
                return real_ip
            
            # Fallback to remote address
            remote_addr = st.context.headers.get('Remote-Addr')
            if remote_addr:
                return remote_addr
        
        return 'unknown'
        
    except Exception as e:
        logger.debug(f"Could not get client IP: {e}")
        return 'unknown'

def get_session_id() -> str:
    """
    Get or create session ID for visitor tracking
    
    Returns:
        str: Session ID
    """
    try:
        import streamlit as st
        
        if 'visitor_session_id' not in st.session_state:
            st.session_state.visitor_session_id = str(uuid.uuid4())
        
        return st.session_state.visitor_session_id
    except Exception:
        return str(uuid.uuid4())

def authenticate_with_tracking(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate user and track the attempt (success or failure)
    
    This is a wrapper around services.auth.authenticate() that adds tracking
    
    Args:
        username: Username or email
        password: Password
        
    Returns:
        User dict if successful, None if failed
    """
    tracker = get_visitor_tracker()
    session_id = get_session_id()
    ip_address = get_client_ip_from_streamlit()
    
    try:
        # Attempt authentication using original function
        user = _auth_authenticate(username, password)
        
        if user:
            # Track successful login - NO PII in details (GDPR-compliant)
            tracker.track_event(
                session_id=session_id,
                event_type=VisitorEventType.LOGIN_SUCCESS,
                page_path="/login",
                ip_address=ip_address,
                user_id=hashlib.sha256(str(user.get('user_id', '')).encode()).hexdigest()[:16],  # Anonymized user_id
                username=None,  # Don't store username in events table
                details={
                    'method': 'password',
                    'role': user.get('role', 'unknown'),
                    'timestamp': datetime.now().isoformat()
                },
                success=True
            )
            logger.info(f"✅ Login successful: {username}")
            return user
        else:
            # Track failed login - NO PII (GDPR-compliant)
            tracker.track_event(
                session_id=session_id,
                event_type=VisitorEventType.LOGIN_FAILURE,
                page_path="/login",
                ip_address=ip_address,
                details={
                    'method': 'password',
                    'attempt_time': datetime.now().isoformat()
                },
                success=False,
                error_message="Invalid credentials"
            )
            logger.warning(f"❌ Login failed: {username}")
            return None
            
    except Exception as e:
        # Track failed login due to error - NO PII (GDPR-compliant)
        tracker.track_event(
            session_id=session_id,
            event_type=VisitorEventType.LOGIN_FAILURE,
            page_path="/login",
            ip_address=ip_address,
            details={
                'method': 'password',
                'error_type': type(e).__name__
            },
            success=False,
            error_message="Authentication error"
        )
        logger.error(f"❌ Login error for {username}: {e}")
        return None

def create_user_with_tracking(username: str, password: str, role: str, 
                             email: str) -> tuple:
    """
    Create user and track the attempt (success or failure)
    
    This is a wrapper around services.auth.create_user() that adds tracking
    Maintains the original signature: (username, password, role, email) -> Tuple[bool, str]
    
    Args:
        username: Username
        password: Password
        role: User role
        email: Email address
        
    Returns:
        Tuple of (success, message)
    """
    tracker = get_visitor_tracker()
    session_id = get_session_id()
    ip_address = get_client_ip_from_streamlit()
    
    try:
        # Track registration started - NO PII in details (GDPR-compliant)
        tracker.track_event(
            session_id=session_id,
            event_type=VisitorEventType.REGISTRATION_STARTED,
            page_path="/register",
            ip_address=ip_address,
            details={
                'role': role,
                'method': 'signup_form',
                'timestamp': datetime.now().isoformat()
            },
            success=True
        )
        
        # Attempt user creation using original function
        success, message = _auth_create_user(username, password, role, email)
        
        if success:
            # Track successful registration - NO PII (GDPR-compliant)
            tracker.track_event(
                session_id=session_id,
                event_type=VisitorEventType.REGISTRATION_SUCCESS,
                page_path="/register",
                ip_address=ip_address,
                user_id=None,  # Don't store user_id for registration events
                username=None,  # Don't store username
                details={
                    'role': role,
                    'method': 'signup_form',
                    'timestamp': datetime.now().isoformat()
                },
                success=True
            )
            logger.info(f"✅ User registered successfully: {username}")
            return (True, message)
        else:
            # Track failed registration - NO PII (GDPR-compliant)
            tracker.track_event(
                session_id=session_id,
                event_type=VisitorEventType.REGISTRATION_FAILURE,
                page_path="/register",
                ip_address=ip_address,
                details={
                    'role': role,
                    'method': 'signup_form',
                    'failure_reason': 'validation_error'
                },
                success=False,
                error_message="Registration validation failed"
            )
            logger.warning(f"❌ User registration failed: {username}")
            return (False, message)
            
    except Exception as e:
        # Track failed registration due to error - NO PII (GDPR-compliant)
        tracker.track_event(
            session_id=session_id,
            event_type=VisitorEventType.REGISTRATION_FAILURE,
            page_path="/register",
            ip_address=ip_address,
            details={
                'role': role,
                'error_type': type(e).__name__
            },
            success=False,
            error_message="Registration system error"
        )
        logger.error(f"❌ User registration error for {username}: {e}")
        return (False, str(e))

def track_page_view(page_path: str = "/", referrer: Optional[str] = None):
    """
    Track anonymous page view (GDPR-compliant)
    
    Args:
        page_path: URL path being viewed
        referrer: HTTP referrer (optional)
    """
    try:
        tracker = get_visitor_tracker()
        session_id = get_session_id()
        ip_address = get_client_ip_from_streamlit()
        
        tracker.track_event(
            session_id=session_id,
            event_type=VisitorEventType.PAGE_VIEW,
            page_path=page_path,
            ip_address=ip_address,
            referrer=referrer,
            success=True
        )
        
    except Exception as e:
        logger.debug(f"Failed to track page view: {e}")

def track_logout(user_id: str, username: str):
    """
    Track user logout event (GDPR-compliant, no PII stored)
    
    Args:
        user_id: User ID (will be hashed before storage)
        username: Username (used for logging only, NOT stored)
    """
    try:
        tracker = get_visitor_tracker()
        session_id = get_session_id()
        ip_address = get_client_ip_from_streamlit()
        
        # Hash user_id for anonymization (GDPR compliance)
        hashed_user_id = hashlib.sha256(str(user_id).encode()).hexdigest()[:16]
        
        tracker.track_event(
            session_id=session_id,
            event_type=VisitorEventType.LOGOUT,
            page_path="/logout",
            ip_address=ip_address,
            user_id=hashed_user_id,  # Hashed, not raw user_id
            username=None,  # Never store username (GDPR)
            details={
                'method': 'manual_logout',
                'timestamp': datetime.now().isoformat()
            },
            success=True
        )
        
        logger.info(f"👋 User logged out: {username}")
        
    except Exception as e:
        logger.debug(f"Failed to track logout: {e}")

def track_session_start():
    """Track session start event"""
    try:
        tracker = get_visitor_tracker()
        session_id = get_session_id()
        ip_address = get_client_ip_from_streamlit()
        
        tracker.track_event(
            session_id=session_id,
            event_type=VisitorEventType.SESSION_START,
            page_path="/",
            ip_address=ip_address,
            success=True
        )
        
    except Exception as e:
        logger.debug(f"Failed to track session start: {e}")
