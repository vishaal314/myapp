"""
System Capacity Monitoring for DataGuardian Pro

This module monitors system capacity, concurrent users, and resource utilization
to provide real-time capacity metrics and alerts.
"""

import time
import psutil
import streamlit as st
from typing import Dict, Any, List
from datetime import datetime, timedelta
from utils.session_manager import SessionManager
from utils.async_scan_manager import async_scan_manager
from utils.database_manager import DatabaseManager

class CapacityMonitor:
    """
    Monitors system capacity and provides real-time metrics for concurrent usage.
    """
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.scan_manager = async_scan_manager
        
        # Capacity thresholds
        self.max_concurrent_users = 10  # Target limit with optimizations
        self.memory_warning_threshold = 85  # %
        self.memory_critical_threshold = 95  # %
        self.db_connection_warning_threshold = 80  # % of pool
        self.scan_duration_warning_multiplier = 2.0  # 2x normal duration
        
        # Expected scan durations (in seconds)
        self.expected_scan_durations = {
            "code": 75,      # 30-120s average
            "document": 37,   # 15-60s average  
            "image": 112,     # 45-180s average
            "database": 180,  # 60-300s average
            "website": 60,    # 30-90s average
            "ai_model": 360,  # 120-600s average
            "api": 54,        # 30-90s average
            "soc2": 150       # 60-240s average
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive system metrics for capacity monitoring.
        
        Returns:
            Dictionary containing system metrics
        """
        try:
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Database connection metrics
            db_stats = self._get_database_stats()
            
            # Scan metrics
            scan_stats = self._get_scan_stats()
            
            # User metrics
            user_stats = self._get_user_stats()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_percent": memory.percent,
                    "status": self._get_memory_status(memory.percent)
                },
                "cpu": {
                    "usage_percent": cpu_percent,
                    "status": self._get_cpu_status(cpu_percent)
                },
                "database": db_stats,
                "scans": scan_stats,
                "users": user_stats,
                "capacity": self._calculate_capacity_metrics()
            }
        except Exception as e:
            return {
                "error": f"Failed to collect metrics: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_database_stats(self) -> Dict[str, Any]:
        """Get database connection pool statistics."""
        try:
            pool = self.db_manager._connection_pool
            if pool:
                # For ThreadedConnectionPool
                total_connections = pool.maxconn
                used_connections = len(pool._used) if hasattr(pool, '_used') else 0
                available_connections = total_connections - used_connections
                usage_percent = (used_connections / total_connections) * 100
                
                return {
                    "total_connections": total_connections,
                    "used_connections": used_connections,
                    "available_connections": available_connections,
                    "usage_percent": round(usage_percent, 1),
                    "status": self._get_db_status(usage_percent)
                }
            else:
                return {
                    "status": "unavailable",
                    "error": "Database pool not initialized"
                }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Database stats error: {str(e)}"
            }
    
    def _get_scan_stats(self) -> Dict[str, Any]:
        """Get active scan statistics."""
        try:
            stats = self.scan_manager.get_system_stats()
            
            # Ensure stats is a dict (handle None or invalid return values)
            if not isinstance(stats, dict):
                stats = {"active_tasks": 0, "queued_tasks": 0, "completed_tasks": 0}
            
            # Add scan duration analysis
            long_running_scans = 0
            for task in self.scan_manager.tasks.values():
                if (task.status == "running" and 
                    task.started_at and 
                    task.scan_type in self.expected_scan_durations):
                    
                    duration = (datetime.now() - task.started_at).total_seconds()
                    expected = self.expected_scan_durations[task.scan_type]
                    
                    if duration > (expected * self.scan_duration_warning_multiplier):
                        long_running_scans += 1
            
            stats["long_running_scans"] = long_running_scans
            stats["status"] = self._get_scan_status(stats.get("active_tasks", 0))
            
            return stats
        except Exception as e:
            return {
                "status": "error",
                "error": f"Scan stats error: {str(e)}"
            }
    
    def _get_user_stats(self) -> Dict[str, Any]:
        """Get user activity statistics."""
        try:
            active_users = SessionManager.get_active_users_count()
            
            # Get active scan users
            scan_users = set()
            for task in self.scan_manager.tasks.values():
                if task.status in ["queued", "submitted", "running"]:
                    scan_users.add(task.user_id)
            
            return {
                "total_active_users": active_users,
                "users_with_active_scans": len(scan_users),
                "concurrent_capacity_used_percent": round((active_users / self.max_concurrent_users) * 100, 1),
                "status": self._get_user_status(active_users)
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"User stats error: {str(e)}"
            }
    
    def _calculate_capacity_metrics(self) -> Dict[str, Any]:
        """Calculate overall system capacity metrics."""
        try:
            # Get individual metrics
            memory = psutil.virtual_memory()
            active_users = SessionManager.get_active_users_count()
            active_scans = len([task for task in self.scan_manager.tasks.values() 
                              if task.status in ["queued", "submitted", "running"]])
            
            # Calculate capacity scores (0-100)
            memory_score = 100 - memory.percent
            user_score = max(0, 100 - ((active_users / self.max_concurrent_users) * 100))
            scan_score = max(0, 100 - (active_scans * 12.5))  # Assume max 8 concurrent scans
            
            # Overall capacity (weighted average)
            overall_capacity = (memory_score * 0.4 + user_score * 0.4 + scan_score * 0.2)
            
            return {
                "overall_capacity_percent": round(overall_capacity, 1),
                "memory_capacity_percent": round(memory_score, 1),
                "user_capacity_percent": round(user_score, 1),
                "scan_capacity_percent": round(scan_score, 1),
                "status": self._get_overall_status(overall_capacity),
                "recommendations": self._get_capacity_recommendations(overall_capacity, memory.percent, active_users, active_scans)
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Capacity calculation error: {str(e)}"
            }
    
    def _get_memory_status(self, usage_percent: float) -> str:
        """Get memory status based on usage."""
        if usage_percent >= self.memory_critical_threshold:
            return "critical"
        elif usage_percent >= self.memory_warning_threshold:
            return "warning"
        else:
            return "good"
    
    def _get_cpu_status(self, usage_percent: float) -> str:
        """Get CPU status based on usage."""
        if usage_percent >= 90:
            return "critical"
        elif usage_percent >= 75:
            return "warning"
        else:
            return "good"
    
    def _get_db_status(self, usage_percent: float) -> str:
        """Get database status based on connection usage."""
        if usage_percent >= 95:
            return "critical"
        elif usage_percent >= self.db_connection_warning_threshold:
            return "warning"
        else:
            return "good"
    
    def _get_scan_status(self, active_scans: int) -> str:
        """Get scan status based on active scans."""
        if active_scans >= 8:
            return "critical"
        elif active_scans >= 5:
            return "warning"
        else:
            return "good"
    
    def _get_user_status(self, active_users: int) -> str:
        """Get user status based on active users."""
        if active_users >= self.max_concurrent_users:
            return "critical"
        elif active_users >= (self.max_concurrent_users * 0.8):
            return "warning"
        else:
            return "good"
    
    def _get_overall_status(self, capacity_percent: float) -> str:
        """Get overall system status."""
        if capacity_percent >= 70:
            return "good"
        elif capacity_percent >= 40:
            return "warning"
        else:
            return "critical"
    
    def _get_capacity_recommendations(self, capacity: float, memory_percent: float, 
                                    active_users: int, active_scans: int) -> List[str]:
        """Get capacity improvement recommendations."""
        recommendations = []
        
        if capacity < 40:
            recommendations.append("🚨 System at critical capacity - immediate action required")
        
        if memory_percent > self.memory_critical_threshold:
            recommendations.append("🔴 Memory usage critical - restart application or upgrade server")
        elif memory_percent > self.memory_warning_threshold:
            recommendations.append("⚠️ High memory usage - monitor closely")
        
        if active_users >= self.max_concurrent_users:
            recommendations.append("👥 Maximum user capacity reached - queue new users")
        elif active_users >= (self.max_concurrent_users * 0.8):
            recommendations.append("👥 Approaching user capacity limit")
        
        if active_scans >= 6:
            recommendations.append("⚡ High scan load - consider scan queuing")
        
        if not recommendations:
            recommendations.append("✅ System operating within normal capacity")
        
        return recommendations
    
    def display_capacity_dashboard(self):
        """Display capacity monitoring dashboard in Streamlit."""
        try:
            metrics = self.get_system_metrics()
            
            if "error" in metrics:
                st.error(f"Capacity monitoring error: {metrics['error']}")
                return
            
            # Overall status
            capacity = metrics["capacity"]
            overall_status = capacity["status"]
            overall_capacity = capacity["overall_capacity_percent"]
            
            # Status color mapping
            status_colors = {
                "good": "🟢",
                "warning": "🟡", 
                "critical": "🔴"
            }
            
            st.subheader(f"System Capacity: {status_colors.get(overall_status, '⚪')} {overall_capacity}%")
            
            # Metrics columns
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Memory", 
                    f"{metrics['memory']['used_percent']:.1f}%",
                    delta=f"{metrics['memory']['available_gb']:.1f}GB free"
                )
            
            with col2:
                st.metric(
                    "Active Users", 
                    metrics['users']['total_active_users'],
                    delta=f"{self.max_concurrent_users - metrics['users']['total_active_users']} capacity left"
                )
            
            with col3:
                st.metric(
                    "Active Scans", 
                    metrics['scans']['active_tasks'],
                    delta=f"{metrics['scans']['completed_tasks']} completed"
                )
            
            with col4:
                st.metric(
                    "DB Connections", 
                    f"{metrics['database'].get('used_connections', 0)}/{metrics['database'].get('total_connections', 25)}",
                    delta=f"{metrics['database'].get('usage_percent', 0):.1f}% used"
                )
            
            # Recommendations
            if capacity["recommendations"]:
                st.subheader("Recommendations")
                for rec in capacity["recommendations"]:
                    if "🚨" in rec or "🔴" in rec:
                        st.error(rec)
                    elif "⚠️" in rec or "👥" in rec:
                        st.warning(rec)
                    else:
                        st.info(rec)
            
            # Detailed metrics in expander
            with st.expander("Detailed Metrics"):
                st.json(metrics)
                
        except Exception as e:
            st.error(f"Failed to display capacity dashboard: {str(e)}")
    
    def get_user_scan_status(self, user_id: str = None) -> Dict[str, Any]:
        """
        Get scan status for a specific user.
        
        Args:
            user_id: User ID (defaults to current user)
        
        Returns:
            User-specific scan status
        """
        if not user_id:
            user_id = SessionManager.get_user_id()
        
        try:
            user_tasks = self.scan_manager.get_user_tasks(user_id)
            active_tasks = [task for task in user_tasks if task["status"] in ["queued", "submitted", "running"]]
            
            return {
                "user_id": user_id,
                "total_scans": len(user_tasks),
                "active_scans": len(active_tasks),
                "max_concurrent_allowed": self.scan_manager.max_tasks_per_user,
                "can_start_new_scan": len(active_tasks) < self.scan_manager.max_tasks_per_user,
                "active_scan_details": active_tasks
            }
        except Exception as e:
            return {
                "error": f"Failed to get user scan status: {str(e)}"
            }

# Global instance
capacity_monitor = CapacityMonitor()

# Convenience functions
def get_system_capacity() -> Dict[str, Any]:
    """Get current system capacity metrics."""
    return capacity_monitor.get_system_metrics()

def display_capacity_status():
    """Display capacity status in Streamlit sidebar."""
    try:
        metrics = capacity_monitor.get_system_metrics()
        if "error" not in metrics:
            capacity = metrics["capacity"]["overall_capacity_percent"]
            status = metrics["capacity"]["status"]
            
            status_icons = {"good": "🟢", "warning": "🟡", "critical": "🔴"}
            st.metric("System Capacity", f"{capacity:.0f}%", delta=status_icons.get(status, "⚪"))
            
            # Show active users
            active_users = metrics["users"]["total_active_users"]
            st.metric("Active Users", active_users, delta=f"/{capacity_monitor.max_concurrent_users}")
    except Exception:
        pass  # Fail silently in sidebar

def check_capacity_before_scan() -> bool:
    """
    Check if system has capacity for a new scan.
    
    Returns:
        True if capacity available, False otherwise
    """
    try:
        metrics = capacity_monitor.get_system_metrics()
        capacity = metrics["capacity"]["overall_capacity_percent"]
        
        # Don't allow new scans if system is critically low on capacity
        if capacity < 20:
            st.error("🚨 System capacity critical - please wait for current scans to complete")
            return False
        
        # Check user-specific limits
        user_status = capacity_monitor.get_user_scan_status()
        if not user_status.get("can_start_new_scan", False):
            st.warning(f"⚠️ You have reached the maximum concurrent scan limit ({capacity_monitor.scan_manager.max_tasks_per_user})")
            return False
        
        return True
        
    except Exception:
        # If capacity check fails, allow scan but warn
        st.warning("⚠️ Unable to check system capacity - proceeding with scan")
        return True