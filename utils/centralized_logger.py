#!/usr/bin/env python3
"""
DataGuardian Pro - Centralized Logging System
Professional logging configuration for all scanners and services
"""

import logging
import logging.handlers
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union
from enum import Enum
import traceback

class LogLevel(Enum):
    """Log level enumeration"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

class LogCategory(Enum):
    """Log category enumeration for filtering"""
    SCANNER = "scanner"
    LICENSE = "license"
    AUTH = "auth"
    PAYMENT = "payment"
    SECURITY = "security"
    PERFORMANCE = "performance"
    API = "api"
    DATABASE = "database"
    SYSTEM = "system"
    USER = "user"

class CustomJSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "process": record.process
        }
        
        # Add extra fields if present
        if hasattr(record, 'category'):
            log_entry['category'] = record.category
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'scanner_type'):
            log_entry['scanner_type'] = record.scanner_type
        if hasattr(record, 'execution_time'):
            log_entry['execution_time'] = record.execution_time
        if hasattr(record, 'memory_usage'):
            log_entry['memory_usage'] = record.memory_usage
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        return json.dumps(log_entry)

class DataGuardianLogger:
    """Centralized logger for DataGuardian Pro"""
    
    def __init__(self, name: str, category: LogCategory = LogCategory.SYSTEM):
        self.name = name
        self.category = category
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup logger with appropriate handlers"""
        if self.logger.handlers:
            return  # Already configured
        
        self.logger.setLevel(self._get_log_level())
        
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Console handler (for development)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # File handler (structured JSON logs)
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_dir / f"dataguardian_{self.category.value}.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(CustomJSONFormatter())
        
        # Error file handler (errors only)
        error_handler = logging.handlers.RotatingFileHandler(
            filename=log_dir / "dataguardian_errors.log",
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(CustomJSONFormatter())
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        
        # Prevent duplicate logs
        self.logger.propagate = False
    
    def _get_log_level(self) -> int:
        """Get log level from environment or default"""
        level_str = os.getenv('LOG_LEVEL', 'INFO').upper()
        return getattr(logging, level_str, logging.INFO)
    
    def _add_context(self, extra: Dict[str, Any]) -> Dict[str, Any]:
        """Add category and common context"""
        context = {"category": self.category.value}
        context.update(extra or {})
        return context
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, extra=self._add_context(kwargs))
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, extra=self._add_context(kwargs))
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, extra=self._add_context(kwargs))
    
    def error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log error message"""
        if exception:
            self.logger.error(message, exc_info=exception, extra=self._add_context(kwargs))
        else:
            self.logger.error(message, extra=self._add_context(kwargs))
    
    def critical(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log critical message"""
        if exception:
            self.logger.critical(message, exc_info=exception, extra=self._add_context(kwargs))
        else:
            self.logger.critical(message, extra=self._add_context(kwargs))

class ScannerLogger(DataGuardianLogger):
    """Specialized logger for scanners"""
    
    def __init__(self, scanner_name: str):
        super().__init__(f"scanner.{scanner_name}", LogCategory.SCANNER)
    
    def scan_started(self, scan_type: str, target: str, user_id: str = None, **kwargs):
        """Log scan start"""
        self.info(
            f"Scan started: {scan_type} on {target}",
            scanner_type=scan_type,
            target=target,
            user_id=user_id,
            **kwargs
        )
    
    def scan_progress(self, scan_type: str, progress: float, message: str = "", **kwargs):
        """Log scan progress"""
        self.info(
            f"Scan progress: {progress:.1f}% - {message}",
            scanner_type=scan_type,
            progress=progress,
            **kwargs
        )
    
    def scan_completed(self, scan_type: str, results_count: int, execution_time: float, **kwargs):
        """Log scan completion"""
        self.info(
            f"Scan completed: {scan_type} - {results_count} findings in {execution_time:.2f}s",
            scanner_type=scan_type,
            results_count=results_count,
            execution_time=execution_time,
            **kwargs
        )
    
    def scan_failed(self, scan_type: str, error_message: str, exception: Exception = None, **kwargs):
        """Log scan failure"""
        self.error(
            f"Scan failed: {scan_type} - {error_message}",
            exception=exception,
            scanner_type=scan_type,
            **kwargs
        )
    
    def pii_found(self, pii_type: str, location: str, confidence: float, **kwargs):
        """Log PII detection"""
        self.warning(
            f"PII detected: {pii_type} at {location} (confidence: {confidence:.2f})",
            pii_type=pii_type,
            location=location,
            confidence=confidence,
            **kwargs
        )

class LicenseLogger(DataGuardianLogger):
    """Specialized logger for license operations"""
    
    def __init__(self):
        super().__init__("license", LogCategory.LICENSE)
    
    def license_loaded(self, license_id: str, license_type: str, user_id: str = None):
        """Log license loading"""
        self.info(
            f"License loaded: {license_id} (type: {license_type})",
            license_id=license_id,
            license_type=license_type,
            user_id=user_id
        )
    
    def license_validation_failed(self, reason: str, user_id: str = None):
        """Log license validation failure"""
        self.error(
            f"License validation failed: {reason}",
            user_id=user_id,
            validation_failure=True
        )
    
    def scanner_access_denied(self, scanner_type: str, user_id: str, reason: str):
        """Log scanner access denial"""
        self.warning(
            f"Scanner access denied: {scanner_type} for user {user_id} - {reason}",
            scanner_type=scanner_type,
            user_id=user_id,
            access_denied=True
        )

class PerformanceLogger(DataGuardianLogger):
    """Specialized logger for performance monitoring"""
    
    def __init__(self):
        super().__init__("performance", LogCategory.PERFORMANCE)
    
    def execution_time(self, operation: str, duration: float, **kwargs):
        """Log execution time"""
        self.info(
            f"Operation '{operation}' completed in {duration:.3f}s",
            operation=operation,
            execution_time=duration,
            **kwargs
        )
    
    def memory_usage(self, operation: str, memory_mb: float, **kwargs):
        """Log memory usage"""
        self.info(
            f"Operation '{operation}' used {memory_mb:.1f}MB memory",
            operation=operation,
            memory_usage=memory_mb,
            **kwargs
        )
    
    def performance_warning(self, operation: str, threshold_exceeded: str, **kwargs):
        """Log performance warning"""
        self.warning(
            f"Performance warning: {operation} - {threshold_exceeded}",
            operation=operation,
            performance_issue=True,
            **kwargs
        )

class SecurityLogger(DataGuardianLogger):
    """Specialized logger for security events"""
    
    def __init__(self):
        super().__init__("security", LogCategory.SECURITY)
    
    def login_attempt(self, user_id: str, success: bool, ip_address: str = None):
        """Log login attempt"""
        if success:
            self.info(
                f"Successful login: {user_id}",
                user_id=user_id,
                login_success=True,
                ip_address=ip_address
            )
        else:
            self.warning(
                f"Failed login attempt: {user_id}",
                user_id=user_id,
                login_failure=True,
                ip_address=ip_address
            )
    
    def unauthorized_access(self, user_id: str, resource: str, ip_address: str = None):
        """Log unauthorized access attempt"""
        self.error(
            f"Unauthorized access attempt: {user_id} tried to access {resource}",
            user_id=user_id,
            resource=resource,
            unauthorized_access=True,
            ip_address=ip_address
        )

# Convenience functions for getting loggers
def get_scanner_logger(scanner_name: str) -> ScannerLogger:
    """Get scanner logger instance"""
    return ScannerLogger(scanner_name)

def get_license_logger() -> LicenseLogger:
    """Get license logger instance"""
    return LicenseLogger()

def get_performance_logger() -> PerformanceLogger:
    """Get performance logger instance"""
    return PerformanceLogger()

def get_security_logger() -> SecurityLogger:
    """Get security logger instance"""
    return SecurityLogger()

def get_logger(name: str, category: LogCategory = LogCategory.SYSTEM) -> DataGuardianLogger:
    """Get general logger instance"""
    return DataGuardianLogger(name, category)

# Initialize root logger
def setup_root_logger():
    """Setup root logger configuration"""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Silence noisy third-party loggers
    logging.getLogger('stripe').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('streamlit').setLevel(logging.WARNING)

# Auto-setup on import
setup_root_logger()