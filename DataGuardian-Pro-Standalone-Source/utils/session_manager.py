"""
Session State Manager for Multi-User Isolation

This module provides user-specific session state management to prevent
data conflicts between concurrent users in DataGuardian Pro.
"""

import streamlit as st
import uuid
import hashlib
from typing import Any, Optional, Dict
from datetime import datetime, timedelta

class SessionManager:
    """
    Manages user-specific session state to prevent conflicts between concurrent users.
    Each user gets isolated session data identified by user_id or session_id.
    """
    
    @staticmethod
    def get_user_id() -> str:
        """
        Get or generate a unique user identifier for this session.
        Uses authenticated user ID if available, otherwise generates session-based ID.
        """
        # Try to get authenticated user ID first
        if 'username' in st.session_state and st.session_state.username:
            return st.session_state.username
        
        # Generate session-based ID if no authenticated user
        if 'session_user_id' not in st.session_state:
            # Create deterministic ID based on session info
            session_info = f"{st.session_state.get('session_id', str(uuid.uuid4()))}"
            st.session_state.session_user_id = hashlib.md5(session_info.encode()).hexdigest()[:12]
        
        return st.session_state.session_user_id
    
    @staticmethod
    def get_user_session_key(key: str) -> str:
        """
        Generate user-specific session key to prevent conflicts.
        
        Args:
            key: Base session key
            
        Returns:
            User-specific session key
        """
        user_id = SessionManager.get_user_id()
        return f"user_{user_id}_{key}"
    
    @staticmethod
    def set_user_data(key: str, value: Any) -> None:
        """
        Set user-specific session data.
        
        Args:
            key: Session key
            value: Value to store
        """
        user_key = SessionManager.get_user_session_key(key)
        st.session_state[user_key] = value
    
    @staticmethod
    def get_user_data(key: str, default: Any = None) -> Any:
        """
        Get user-specific session data.
        
        Args:
            key: Session key
            default: Default value if key not found
            
        Returns:
            User-specific session data or default
        """
        user_key = SessionManager.get_user_session_key(key)
        return st.session_state.get(user_key, default)
    
    @staticmethod
    def delete_user_data(key: str) -> None:
        """
        Delete user-specific session data.
        
        Args:
            key: Session key to delete
        """
        user_key = SessionManager.get_user_session_key(key)
        if user_key in st.session_state:
            del st.session_state[user_key]
    
    @staticmethod
    def clear_user_session() -> None:
        """
        Clear all user-specific session data while preserving global session data.
        """
        user_id = SessionManager.get_user_id()
        user_prefix = f"user_{user_id}_"
        
        # Find all user-specific keys
        keys_to_delete = [key for key in st.session_state.keys() if key.startswith(user_prefix)]
        
        # Delete user-specific data
        for key in keys_to_delete:
            del st.session_state[key]
    
    @staticmethod
    def get_scan_results(scan_type: str) -> Optional[Dict]:
        """
        Get scan results for specific scan type and user.
        
        Args:
            scan_type: Type of scan (code, document, image, etc.)
            
        Returns:
            Scan results or None
        """
        return SessionManager.get_user_data(f"scan_results_{scan_type}")
    
    @staticmethod
    def set_scan_results(scan_type: str, results: Dict) -> None:
        """
        Set scan results for specific scan type and user.
        
        Args:
            scan_type: Type of scan
            results: Scan results to store
        """
        SessionManager.set_user_data(f"scan_results_{scan_type}", results)
        SessionManager.set_user_data(f"scan_timestamp_{scan_type}", datetime.now())
    
    @staticmethod
    def get_payment_data() -> Optional[Dict]:
        """
        Get user-specific payment data.
        
        Returns:
            Payment data or None
        """
        return SessionManager.get_user_data("payment_data")
    
    @staticmethod
    def set_payment_data(payment_data: Dict) -> None:
        """
        Set user-specific payment data.
        
        Args:
            payment_data: Payment information to store
        """
        SessionManager.set_user_data("payment_data", payment_data)
    
    @staticmethod
    def get_db_config() -> Optional[Dict]:
        """
        Get user-specific database configuration.
        
        Returns:
            Database configuration or None
        """
        return SessionManager.get_user_data("db_config")
    
    @staticmethod
    def set_db_config(db_config: Dict) -> None:
        """
        Set user-specific database configuration.
        
        Args:
            db_config: Database configuration to store
        """
        SessionManager.set_user_data("db_config", db_config)
    
    @staticmethod
    def get_upload_files(scan_type: str) -> Optional[list]:
        """
        Get user-specific uploaded files for scan type.
        
        Args:
            scan_type: Type of scan
            
        Returns:
            List of uploaded files or None
        """
        return SessionManager.get_user_data(f"uploaded_files_{scan_type}")
    
    @staticmethod
    def set_upload_files(scan_type: str, files: list) -> None:
        """
        Set user-specific uploaded files for scan type.
        
        Args:
            scan_type: Type of scan
            files: List of uploaded files
        """
        SessionManager.set_user_data(f"uploaded_files_{scan_type}", files)
    
    @staticmethod
    def is_scan_complete(scan_type: str) -> bool:
        """
        Check if scan is complete for user and scan type.
        
        Args:
            scan_type: Type of scan
            
        Returns:
            True if scan is complete
        """
        return SessionManager.get_user_data(f"scan_complete_{scan_type}", False)
    
    @staticmethod
    def set_scan_complete(scan_type: str, complete: bool = True) -> None:
        """
        Set scan completion status for user and scan type.
        
        Args:
            scan_type: Type of scan
            complete: Completion status
        """
        SessionManager.set_user_data(f"scan_complete_{scan_type}", complete)
    
    @staticmethod
    def get_scan_progress(scan_type: str) -> Dict:
        """
        Get scan progress information for user and scan type.
        
        Args:
            scan_type: Type of scan
            
        Returns:
            Progress information dictionary
        """
        return SessionManager.get_user_data(f"scan_progress_{scan_type}", {
            "current": 0,
            "total": 100,
            "status": "Not started"
        })
    
    @staticmethod
    def set_scan_progress(scan_type: str, current: int, total: int, status: str) -> None:
        """
        Set scan progress for user and scan type.
        
        Args:
            scan_type: Type of scan
            current: Current progress
            total: Total progress
            status: Status message
        """
        SessionManager.set_user_data(f"scan_progress_{scan_type}", {
            "current": current,
            "total": total,
            "status": status,
            "timestamp": datetime.now()
        })
    
    @staticmethod
    def cleanup_old_sessions() -> None:
        """
        Cleanup old session data to prevent memory leaks.
        This should be called periodically to remove stale session data.
        """
        current_time = datetime.now()
        cleanup_threshold = timedelta(hours=24)  # Remove data older than 24 hours
        
        # Find all timestamp keys
        timestamp_keys = [key for key in st.session_state.keys() if "timestamp" in key]
        
        for key in timestamp_keys:
            try:
                timestamp = st.session_state.get(key)
                if timestamp and isinstance(timestamp, datetime):
                    if current_time - timestamp > cleanup_threshold:
                        # Extract user_id and base_key from timestamp key
                        # Format: user_{user_id}_scan_timestamp_{scan_type}
                        parts = key.split("_")
                        if len(parts) >= 4:
                            user_id = parts[1]
                            base_key = "_".join(parts[2:-1])  # Remove timestamp suffix
                            
                            # Delete related session data
                            related_key = f"user_{user_id}_{base_key}"
                            if related_key in st.session_state:
                                del st.session_state[related_key]
                            del st.session_state[key]
            except Exception:
                # If cleanup fails for any key, continue with others
                pass
    
    @staticmethod
    def get_active_users_count() -> int:
        """
        Get count of active users based on session data.
        
        Returns:
            Number of active users
        """
        user_ids = set()
        
        # Extract user IDs from all user-specific keys
        for key in st.session_state.keys():
            if key.startswith("user_") and "_" in key:
                parts = key.split("_")
                if len(parts) >= 2:
                    user_ids.add(parts[1])
        
        return len(user_ids)
    
    @staticmethod
    def get_debug_info() -> Dict:
        """
        Get debug information about session state for monitoring.
        
        Returns:
            Debug information dictionary
        """
        user_id = SessionManager.get_user_id()
        user_keys = [key for key in st.session_state.keys() if key.startswith(f"user_{user_id}_")]
        
        return {
            "user_id": user_id,
            "user_keys_count": len(user_keys),
            "active_users": SessionManager.get_active_users_count(),
            "total_session_keys": len(st.session_state.keys()),
            "user_specific_keys": user_keys[:10],  # Show first 10 keys for debugging
            "session_size_estimate": len(str(st.session_state))
        }

# Convenience functions for common operations
def get_user_scan_results(scan_type: str) -> Optional[Dict]:
    """Convenience function to get user scan results"""
    return SessionManager.get_scan_results(scan_type)

def set_user_scan_results(scan_type: str, results: Dict) -> None:
    """Convenience function to set user scan results"""
    SessionManager.set_scan_results(scan_type, results)

def get_user_payment_data() -> Optional[Dict]:
    """Convenience function to get user payment data"""
    return SessionManager.get_payment_data()

def set_user_payment_data(payment_data: Dict) -> None:
    """Convenience function to set user payment data"""
    SessionManager.set_payment_data(payment_data)

def clear_user_data() -> None:
    """Convenience function to clear user session data"""
    SessionManager.clear_user_session()