"""
Session Optimization Module for DataGuardian Pro
Handles concurrent user sessions with improved performance
"""

import streamlit as st
import threading
import time
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
from collections import defaultdict
import psutil
import os

logger = logging.getLogger(__name__)

class SessionOptimizer:
    """Optimized session manager for concurrent users"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
        self.user_sessions: Dict[str, List[str]] = defaultdict(list)
        self.session_lock = threading.RLock()
        self.cleanup_thread = None
        self.running = True
        self.stats = {
            'total_sessions': 0,
            'active_sessions': 0,
            'expired_sessions': 0,
            'concurrent_users': 0,
            'peak_concurrent': 0,
            'session_duration_avg': 0.0
        }
        
        # Configuration
        self.session_timeout = 3600  # 1 hour
        self.max_sessions_per_user = 5
        self.cleanup_interval = 300  # 5 minutes
        
        # Start cleanup thread
        self.start_cleanup_thread()
    
    def start_cleanup_thread(self):
        """Start background cleanup thread"""
        def cleanup_loop():
            while self.running:
                try:
                    self.cleanup_expired_sessions()
                    time.sleep(self.cleanup_interval)
                except Exception as e:
                    logger.error(f"Session cleanup error: {e}")
        
        self.cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        self.cleanup_thread.start()
        logger.info("Session cleanup thread started")
    
    def create_session(self, user_id: str, user_data: Dict) -> str:
        """Create optimized user session"""
        with self.session_lock:
            session_id = str(uuid.uuid4())
            current_time = datetime.now()
            
            # Limit sessions per user
            if len(self.user_sessions[user_id]) >= self.max_sessions_per_user:
                oldest_session = self.user_sessions[user_id].pop(0)
                self.remove_session(oldest_session)
            
            # Create session
            session_data = {
                'session_id': session_id,
                'user_id': user_id,
                'user_data': user_data,
                'created_at': current_time,
                'last_activity': current_time,
                'ip_address': self._get_client_ip(),
                'user_agent': self._get_user_agent(),
                'scan_count': 0,
                'cache_data': {},
                'preferences': {},
                'activity_log': []
            }
            
            self.sessions[session_id] = session_data
            self.user_sessions[user_id].append(session_id)
            
            # Update statistics
            self.stats['total_sessions'] += 1
            self.stats['active_sessions'] = len(self.sessions)
            self.stats['concurrent_users'] = len(self.user_sessions)
            
            if self.stats['concurrent_users'] > self.stats['peak_concurrent']:
                self.stats['peak_concurrent'] = self.stats['concurrent_users']
            
            logger.info(f"Created session {session_id} for user {user_id}")
            return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data with activity tracking"""
        with self.session_lock:
            if session_id not in self.sessions:
                return None
            
            session = self.sessions[session_id]
            
            # Check if session expired
            if self._is_session_expired(session):
                self.remove_session(session_id)
                return None
            
            # Update last activity
            session['last_activity'] = datetime.now()
            
            return session.copy()
    
    def update_session(self, session_id: str, updates: Dict) -> bool:
        """Update session data efficiently"""
        with self.session_lock:
            if session_id not in self.sessions:
                return False
            
            session = self.sessions[session_id]
            
            # Check if session expired
            if self._is_session_expired(session):
                self.remove_session(session_id)
                return False
            
            # Update session data
            for key, value in updates.items():
                if key not in ['session_id', 'user_id', 'created_at']:
                    session[key] = value
            
            session['last_activity'] = datetime.now()
            
            return True
    
    def remove_session(self, session_id: str) -> bool:
        """Remove session efficiently"""
        with self.session_lock:
            if session_id not in self.sessions:
                return False
            
            session = self.sessions[session_id]
            user_id = session['user_id']
            
            # Remove from sessions
            del self.sessions[session_id]
            
            # Remove from user sessions
            if user_id in self.user_sessions:
                try:
                    self.user_sessions[user_id].remove(session_id)
                    if not self.user_sessions[user_id]:
                        del self.user_sessions[user_id]
                except ValueError:
                    pass
            
            # Update statistics
            self.stats['active_sessions'] = len(self.sessions)
            self.stats['concurrent_users'] = len(self.user_sessions)
            
            logger.info(f"Removed session {session_id}")
            return True
    
    def get_user_sessions(self, user_id: str) -> List[Dict]:
        """Get all sessions for a user"""
        with self.session_lock:
            if user_id not in self.user_sessions:
                return []
            
            user_session_data = []
            for session_id in self.user_sessions[user_id]:
                if session_id in self.sessions:
                    session = self.sessions[session_id]
                    if not self._is_session_expired(session):
                        user_session_data.append(session.copy())
            
            return user_session_data
    
    def track_activity(self, session_id: str, activity: str, details: Dict = None) -> bool:
        """Track user activity in session"""
        with self.session_lock:
            if session_id not in self.sessions:
                return False
            
            session = self.sessions[session_id]
            
            activity_entry = {
                'timestamp': datetime.now().isoformat(),
                'activity': activity,
                'details': details or {}
            }
            
            # Add to activity log
            session['activity_log'].append(activity_entry)
            
            # Keep only last 100 activities
            if len(session['activity_log']) > 100:
                session['activity_log'] = session['activity_log'][-100:]
            
            # Update scan count if it's a scan activity
            if activity.startswith('scan_'):
                session['scan_count'] += 1
            
            session['last_activity'] = datetime.now()
            
            return True
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        with self.session_lock:
            expired_sessions = []
            
            for session_id, session in self.sessions.items():
                if self._is_session_expired(session):
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                self.remove_session(session_id)
            
            if expired_sessions:
                self.stats['expired_sessions'] += len(expired_sessions)
                logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    def _is_session_expired(self, session: Dict) -> bool:
        """Check if session is expired"""
        last_activity = session.get('last_activity', datetime.now())
        return datetime.now() - last_activity > timedelta(seconds=self.session_timeout)
    
    def _get_client_ip(self) -> str:
        """Get client IP address"""
        try:
            # Try to get from Streamlit headers
            return st.context.headers.get('X-Forwarded-For', '127.0.0.1')
        except:
            return '127.0.0.1'
    
    def _get_user_agent(self) -> str:
        """Get user agent string"""
        try:
            return st.context.headers.get('User-Agent', 'Unknown')
        except:
            return 'Unknown'
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        with self.session_lock:
            # Calculate average session duration
            if self.sessions:
                total_duration = 0
                for session in self.sessions.values():
                    created_at = session.get('created_at', datetime.now())
                    duration = (datetime.now() - created_at).total_seconds()
                    total_duration += duration
                
                self.stats['session_duration_avg'] = total_duration / len(self.sessions)
            
            return {
                **self.stats,
                'memory_usage': self._get_memory_usage(),
                'system_resources': self._get_system_resources()
            }
    
    def _get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,
            'vms_mb': memory_info.vms / 1024 / 1024,
            'percent': process.memory_percent()
        }
    
    def _get_system_resources(self) -> Dict[str, Any]:
        """Get system resource usage"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
        }
    
    def optimize_for_concurrent_users(self, expected_users: int):
        """Optimize session management for expected concurrent users"""
        # Adjust session timeout based on expected load
        if expected_users > 100:
            self.session_timeout = 1800  # 30 minutes for high load
            self.cleanup_interval = 120  # 2 minutes
        elif expected_users > 50:
            self.session_timeout = 2400  # 40 minutes for medium load
            self.cleanup_interval = 180  # 3 minutes
        else:
            self.session_timeout = 3600  # 1 hour for low load
            self.cleanup_interval = 300  # 5 minutes
        
        # Adjust max sessions per user
        self.max_sessions_per_user = max(3, min(10, expected_users // 10))
        
        logger.info(f"Optimized for {expected_users} concurrent users")
    
    def shutdown(self):
        """Shutdown session manager"""
        self.running = False
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=5)
        logger.info("Session optimizer shutdown complete")

# Integration with Streamlit session state
class StreamlitSessionIntegration:
    """Integration layer for Streamlit session state"""
    
    def __init__(self, optimizer: SessionOptimizer):
        self.optimizer = optimizer
    
    def init_session(self, user_id: str, user_data: Dict):
        """Initialize Streamlit session with optimizer"""
        if 'session_id' not in st.session_state:
            session_id = self.optimizer.create_session(user_id, user_data)
            st.session_state.session_id = session_id
            st.session_state.user_id = user_id
            st.session_state.optimized = True
        
        # Update session activity
        self.optimizer.track_activity(
            st.session_state.session_id,
            'page_view',
            {'page': st.get_option('browser.gatherUsageStats')}
        )
    
    def get_session_data(self) -> Optional[Dict]:
        """Get current session data"""
        if 'session_id' in st.session_state:
            return self.optimizer.get_session(st.session_state.session_id)
        return None
    
    def update_session_data(self, updates: Dict) -> bool:
        """Update current session data"""
        if 'session_id' in st.session_state:
            return self.optimizer.update_session(st.session_state.session_id, updates)
        return False
    
    def track_scan_activity(self, scan_type: str, scan_data: Dict):
        """Track scan activity"""
        if 'session_id' in st.session_state:
            self.optimizer.track_activity(
                st.session_state.session_id,
                f'scan_{scan_type}',
                scan_data
            )
    
    def cleanup_on_logout(self):
        """Clean up session on logout"""
        if 'session_id' in st.session_state:
            self.optimizer.remove_session(st.session_state.session_id)
            # Clear Streamlit session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]

# Global session optimizer
session_optimizer = SessionOptimizer()
streamlit_session = StreamlitSessionIntegration(session_optimizer)

def get_session_optimizer():
    """Get the session optimizer instance"""
    return session_optimizer

def get_streamlit_session():
    """Get the Streamlit session integration"""
    return streamlit_session