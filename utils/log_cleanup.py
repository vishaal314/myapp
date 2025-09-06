#!/usr/bin/env python3
"""
DataGuardian Pro - Log Cleanup Utility
Automated log management and cleanup
"""

import os
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List
import schedule
import time

class LogCleaner:
    """Automated log cleanup and archiving"""
    
    def __init__(self, logs_dir: str = "logs", archive_dir: str = "logs/archive"):
        self.logs_dir = Path(logs_dir)
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
    
    def compress_old_logs(self, days_old: int = 7):
        """Compress logs older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        for log_file in self.logs_dir.glob("*.log"):
            if log_file.stat().st_mtime < cutoff_date.timestamp():
                self._compress_file(log_file)
    
    def _compress_file(self, file_path: Path):
        """Compress a single log file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        compressed_name = f"{file_path.stem}_{timestamp}.log.gz"
        compressed_path = self.archive_dir / compressed_name
        
        with open(file_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        file_path.unlink()  # Remove original
        print(f"Compressed {file_path} -> {compressed_path}")
    
    def delete_old_archives(self, days_old: int = 30):
        """Delete compressed logs older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        for archive_file in self.archive_dir.glob("*.gz"):
            if archive_file.stat().st_mtime < cutoff_date.timestamp():
                archive_file.unlink()
                print(f"Deleted old archive: {archive_file}")
    
    def cleanup_empty_logs(self):
        """Remove empty log files"""
        for log_file in self.logs_dir.glob("*.log"):
            if log_file.stat().st_size == 0:
                log_file.unlink()
                print(f"Removed empty log: {log_file}")
    
    def run_cleanup(self):
        """Run complete cleanup process"""
        print(f"Starting log cleanup at {datetime.now()}")
        self.cleanup_empty_logs()
        self.compress_old_logs(days_old=7)
        self.delete_old_archives(days_old=30)
        print("Log cleanup completed")

def setup_automated_cleanup():
    """Setup automated log cleanup schedule"""
    cleaner = LogCleaner()
    
    # Schedule daily cleanup at 2 AM
    schedule.every().day.at("02:00").do(cleaner.run_cleanup)
    
    # Schedule weekly deep cleanup on Sunday at 3 AM
    schedule.every().sunday.at("03:00").do(lambda: cleaner.delete_old_archives(days_old=14))
    
    print("Automated log cleanup scheduled")
    
    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    # Run cleanup immediately
    cleaner = LogCleaner()
    cleaner.run_cleanup()