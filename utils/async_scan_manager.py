"""
Async Scan Manager for Concurrent Processing

This module provides asynchronous scan processing capabilities to handle
multiple concurrent scans without blocking the main Streamlit thread.
"""

import asyncio
import threading
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
from concurrent.futures import ThreadPoolExecutor, Future
import streamlit as st
from utils.session_manager import SessionManager

class ScanTask:
    """Represents a single scan task with status tracking."""
    
    def __init__(self, task_id: str, user_id: str, scan_type: str, scan_function: Callable, 
                 scan_args: tuple, scan_kwargs: dict):
        self.task_id = task_id
        self.user_id = user_id
        self.scan_type = scan_type
        self.scan_function = scan_function
        self.scan_args = scan_args
        self.scan_kwargs = scan_kwargs
        self.status = "queued"
        self.progress = 0
        self.total = 100
        self.result = None
        self.error = None
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.future: Optional[Future] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for serialization."""
        return {
            "task_id": self.task_id,
            "user_id": self.user_id,
            "scan_type": self.scan_type,
            "status": self.status,
            "progress": self.progress,
            "total": self.total,
            "error": str(self.error) if self.error else None,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration": (self.completed_at - self.started_at).total_seconds() 
                       if self.started_at and self.completed_at else None
        }

class AsyncScanManager:
    """
    Manages asynchronous scan execution with progress tracking and user isolation.
    Prevents blocking operations and enables concurrent scan processing.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(AsyncScanManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.executor = ThreadPoolExecutor(max_workers=8)  # Support up to 8 concurrent scans
            self.tasks: Dict[str, ScanTask] = {}
            self.user_tasks: Dict[str, List[str]] = {}  # user_id -> list of task_ids
            self.max_tasks_per_user = 3  # Limit concurrent scans per user
            self.initialized = True
    
    def submit_scan(self, user_id: str, scan_type: str, scan_function: Callable, 
                   *args, **kwargs) -> str:
        """
        Submit a scan task for asynchronous execution.
        
        Args:
            user_id: User identifier
            scan_type: Type of scan (code, document, etc.)
            scan_function: Function to execute
            *args: Arguments for scan function
            **kwargs: Keyword arguments for scan function
        
        Returns:
            Task ID for tracking
        """
        # Check user task limit
        user_task_count = len(self.get_user_active_tasks(user_id))
        if user_task_count >= self.max_tasks_per_user:
            raise Exception(f"User has reached maximum concurrent scan limit ({self.max_tasks_per_user})")
        
        # Create task
        task_id = f"scan_{uuid.uuid4().hex[:12]}"
        task = ScanTask(task_id, user_id, scan_type, scan_function, args, kwargs)
        
        # Add progress callback wrapper
        def progress_callback(current: int, total: int, status: str = ""):
            self.update_task_progress(task_id, current, total, status)
        
        # Inject progress callback if scan function supports it
        if 'progress_callback' in kwargs:
            kwargs['progress_callback'] = progress_callback
        
        # Submit to thread pool
        task.future = self.executor.submit(self._execute_scan_task, task)
        task.status = "submitted"
        
        # Store task
        self.tasks[task_id] = task
        if user_id not in self.user_tasks:
            self.user_tasks[user_id] = []
        self.user_tasks[user_id].append(task_id)
        
        return task_id
    
    def _execute_scan_task(self, task: ScanTask) -> Any:
        """
        Execute a scan task with error handling and progress tracking.
        
        Args:
            task: Scan task to execute
        
        Returns:
            Scan result
        """
        try:
            task.status = "running"
            task.started_at = datetime.now()
            
            # Execute the scan function
            result = task.scan_function(*task.scan_args, **task.scan_kwargs)
            
            task.result = result
            task.status = "completed"
            task.progress = 100
            task.completed_at = datetime.now()
            
            # Store result in user session
            SessionManager.set_scan_results(task.scan_type, result)
            SessionManager.set_scan_complete(task.scan_type, True)
            
            return result
            
        except Exception as e:
            task.error = e
            task.status = "failed"
            task.completed_at = datetime.now()
            
            # Log error for debugging
            print(f"Scan task {task.task_id} failed: {str(e)}")
            raise e
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a specific task.
        
        Args:
            task_id: Task identifier
        
        Returns:
            Task status dictionary or None
        """
        task = self.tasks.get(task_id)
        return task.to_dict() if task else None
    
    def get_user_tasks(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all tasks for a specific user.
        
        Args:
            user_id: User identifier
        
        Returns:
            List of task status dictionaries
        """
        user_task_ids = self.user_tasks.get(user_id, [])
        return [self.tasks[task_id].to_dict() for task_id in user_task_ids if task_id in self.tasks]
    
    def get_user_active_tasks(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get active (queued, submitted, running) tasks for a user.
        
        Args:
            user_id: User identifier
        
        Returns:
            List of active task status dictionaries
        """
        user_tasks = self.get_user_tasks(user_id)
        return [task for task in user_tasks if task["status"] in ["queued", "submitted", "running"]]
    
    def update_task_progress(self, task_id: str, current: int, total: int, status: str = "") -> None:
        """
        Update progress for a specific task.
        
        Args:
            task_id: Task identifier
            current: Current progress
            total: Total progress
            status: Status message
        """
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.progress = current
            task.total = total
            
            # Update session state for real-time UI updates
            SessionManager.set_scan_progress(task.scan_type, current, total, status)
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a specific task.
        
        Args:
            task_id: Task identifier
        
        Returns:
            True if cancelled successfully
        """
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if task.future and not task.future.done():
                cancelled = task.future.cancel()
                if cancelled:
                    task.status = "cancelled"
                    task.completed_at = datetime.now()
                return cancelled
        return False
    
    def cancel_user_tasks(self, user_id: str) -> int:
        """
        Cancel all active tasks for a user.
        
        Args:
            user_id: User identifier
        
        Returns:
            Number of tasks cancelled
        """
        user_task_ids = self.user_tasks.get(user_id, [])
        cancelled_count = 0
        
        for task_id in user_task_ids:
            if self.cancel_task(task_id):
                cancelled_count += 1
        
        return cancelled_count
    
    def cleanup_completed_tasks(self, max_age_hours: int = 24) -> int:
        """
        Clean up completed tasks older than specified age.
        
        Args:
            max_age_hours: Maximum age in hours for completed tasks
        
        Returns:
            Number of tasks cleaned up
        """
        current_time = datetime.now()
        cleanup_threshold = current_time.timestamp() - (max_age_hours * 3600)
        
        tasks_to_remove = []
        for task_id, task in self.tasks.items():
            if (task.status in ["completed", "failed", "cancelled"] and 
                task.completed_at and 
                task.completed_at.timestamp() < cleanup_threshold):
                tasks_to_remove.append(task_id)
        
        # Remove old tasks
        for task_id in tasks_to_remove:
            task = self.tasks[task_id]
            # Remove from user tasks list
            if task.user_id in self.user_tasks:
                self.user_tasks[task.user_id] = [
                    tid for tid in self.user_tasks[task.user_id] if tid != task_id
                ]
            # Remove from tasks dictionary
            del self.tasks[task_id]
        
        return len(tasks_to_remove)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get system statistics for monitoring.
        
        Returns:
            System statistics dictionary
        """
        active_tasks = sum(1 for task in self.tasks.values() 
                          if task.status in ["queued", "submitted", "running"])
        completed_tasks = sum(1 for task in self.tasks.values() 
                             if task.status == "completed")
        failed_tasks = sum(1 for task in self.tasks.values() 
                          if task.status == "failed")
        
        return {
            "total_tasks": len(self.tasks),
            "active_tasks": active_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "active_users": len([user_id for user_id, tasks in self.user_tasks.items() 
                               if any(self.tasks[tid].status in ["queued", "submitted", "running"] 
                                     for tid in tasks if tid in self.tasks)]),
            "executor_workers": self.executor._max_workers,
            "memory_usage_mb": len(str(self.tasks)) / 1024 / 1024
        }
    
    def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> Optional[Any]:
        """
        Wait for a task to complete and return the result.
        
        Args:
            task_id: Task identifier
            timeout: Maximum time to wait in seconds
        
        Returns:
            Task result or None if timeout/error
        """
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        if task.future:
            try:
                return task.future.result(timeout=timeout)
            except Exception as e:
                print(f"Error waiting for task {task_id}: {str(e)}")
                return None
        
        return task.result
    
    def shutdown(self):
        """Shutdown the async scan manager and cleanup resources."""
        self.executor.shutdown(wait=True)
        self.tasks.clear()
        self.user_tasks.clear()

# Global instance
async_scan_manager = AsyncScanManager()

# Convenience functions
def submit_async_scan(scan_type: str, scan_function: Callable, *args, **kwargs) -> str:
    """
    Submit an async scan for the current user.
    
    Args:
        scan_type: Type of scan
        scan_function: Function to execute
        *args: Arguments for scan function
        **kwargs: Keyword arguments for scan function
    
    Returns:
        Task ID for tracking
    """
    user_id = SessionManager.get_user_id()
    return async_scan_manager.submit_scan(user_id, scan_type, scan_function, *args, **kwargs)

def get_user_scan_status(task_id: str) -> Optional[Dict[str, Any]]:
    """Get status of a user's scan task."""
    return async_scan_manager.get_task_status(task_id)

def get_user_active_scans() -> List[Dict[str, Any]]:
    """Get all active scans for the current user."""
    user_id = SessionManager.get_user_id()
    return async_scan_manager.get_user_active_tasks(user_id)

def cancel_user_scans() -> int:
    """Cancel all active scans for the current user."""
    user_id = SessionManager.get_user_id()
    return async_scan_manager.cancel_user_tasks(user_id)