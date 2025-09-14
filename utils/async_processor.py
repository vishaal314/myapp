"""
Async Processing Module for DataGuardian Pro
Provides concurrent scanning capabilities for improved performance
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from datetime import datetime, timedelta
import threading

logger = logging.getLogger(__name__)

class AsyncProcessor:
    """Handles async processing for concurrent scans"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_tasks = {}
        self.task_results = {}
        self._lock = threading.RLock()  # Use RLock to avoid deadlock in nested calls
        
    def submit_scan_task(self, task_id: str, scan_function: Callable, *args, **kwargs) -> Optional[str]:
        """Submit a scan task for async processing"""
        try:
            with self._lock:
                if task_id in self.active_tasks:
                    logger.warning(f"Task {task_id} already exists, skipping")
                    return task_id
                
                # Submit task to executor
                future = self.executor.submit(scan_function, *args, **kwargs)
                self.active_tasks[task_id] = {
                    'future': future,
                    'submitted_at': datetime.now(),
                    'status': 'running'
                }
                
                logger.info(f"Submitted async task: {task_id}")
                return task_id
                
        except Exception as e:
            logger.error(f"Failed to submit task {task_id}: {e}")
            return None
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a specific task"""
        with self._lock:
            if task_id not in self.active_tasks:
                if task_id in self.task_results:
                    return {
                        'status': 'completed',
                        'result': self.task_results[task_id],
                        'completed_at': self.task_results[task_id].get('completed_at')
                    }
                return {'status': 'not_found'}
            
            task = self.active_tasks[task_id]
            future = task['future']
            
            if future.done():
                try:
                    result = future.result()
                    # Move to results and clean up
                    self.task_results[task_id] = {
                        'result': result,
                        'completed_at': datetime.now(),
                        'success': True
                    }
                    del self.active_tasks[task_id]
                    
                    return {
                        'status': 'completed',
                        'result': result,
                        'completed_at': self.task_results[task_id]['completed_at']
                    }
                except Exception as e:
                    # Handle task failure
                    self.task_results[task_id] = {
                        'error': str(e),
                        'completed_at': datetime.now(),
                        'success': False
                    }
                    del self.active_tasks[task_id]
                    
                    return {
                        'status': 'failed',
                        'error': str(e),
                        'completed_at': self.task_results[task_id]['completed_at']
                    }
            else:
                return {
                    'status': 'running',
                    'submitted_at': task['submitted_at']
                }
    
    def get_all_task_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all tasks - avoiding deadlock by not calling get_task_status under lock"""
        statuses = {}
        
        # Get snapshots under lock, then process without lock
        with self._lock:
            active_task_ids = list(self.active_tasks.keys())
            completed_results = dict(self.task_results)
        
        # Process active tasks without holding the lock
        for task_id in active_task_ids:
            statuses[task_id] = self.get_task_status(task_id)
        
        # Add completed tasks
        for task_id, result in completed_results.items():
            if task_id not in statuses:
                statuses[task_id] = {
                    'status': 'completed' if result.get('success') else 'failed',
                    'result': result.get('result'),
                    'error': result.get('error'),
                    'completed_at': result.get('completed_at')
                }
        
        return statuses
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        with self._lock:
            if task_id not in self.active_tasks:
                return False
            
            future = self.active_tasks[task_id]['future']
            if future.cancel():
                del self.active_tasks[task_id]
                logger.info(f"Cancelled task: {task_id}")
                return True
            
            return False
    
    def cleanup_completed_tasks(self, max_age_hours: int = 24):
        """Clean up old completed tasks"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        with self._lock:
            to_remove = []
            for task_id, result in self.task_results.items():
                if result.get('completed_at', datetime.now()) < cutoff_time:
                    to_remove.append(task_id)
            
            for task_id in to_remove:
                del self.task_results[task_id]
                logger.debug(f"Cleaned up old task: {task_id}")
    
    def shutdown(self):
        """Shutdown the executor"""
        self.executor.shutdown(wait=True)
        logger.info("Async processor shut down")

# Global instance for application use
async_processor = AsyncProcessor(max_workers=4)

def get_async_processor() -> AsyncProcessor:
    """Get the global async processor instance"""
    return async_processor

# Convenience functions for common async operations
def submit_concurrent_scan(scan_type: str, scan_function: Callable, *args, **kwargs) -> Optional[str]:
    """Submit a scan for async processing"""
    task_id = f"{scan_type}_{int(time.time() * 1000)}"
    return async_processor.submit_scan_task(task_id, scan_function, *args, **kwargs)

def get_scan_progress(task_id: str) -> Dict[str, Any]:
    """Get progress of a scan task"""
    return async_processor.get_task_status(task_id)

def get_all_scan_progress() -> Dict[str, Dict[str, Any]]:
    """Get progress of all scan tasks"""
    return async_processor.get_all_task_statuses()