#!/usr/bin/env python3
"""
DataGuardian Pro - Scanner Logging Example
Demonstration of how to integrate centralized logging into scanners
"""

import time
import random
from utils.centralized_logger import (
    get_scanner_logger, 
    get_license_logger, 
    get_performance_logger,
    get_security_logger
)

def demonstrate_scanner_logging():
    """Demonstrate scanner logging features"""
    
    # Initialize specialized loggers
    scanner_logger = get_scanner_logger("demo_scanner")
    license_logger = get_license_logger()
    perf_logger = get_performance_logger()
    security_logger = get_security_logger()
    
    print("🚀 Starting DataGuardian Pro Logging Demonstration...")
    
    # Simulate license validation
    license_logger.license_loaded("DGP-ENT-2025-001", "Enterprise Ultimate", "admin_001")
    
    # Simulate scanner startup
    scanner_logger.scan_started("demo_scan", "/path/to/target", user_id="admin_001")
    
    # Simulate scan progress
    for progress in [10, 25, 50, 75, 90, 100]:
        scanner_logger.scan_progress("demo_scan", progress, f"Processing files... {progress}%")
        time.sleep(0.5)  # Simulate work
    
    # Simulate PII detection
    scanner_logger.pii_found("email", "config/settings.py:42", confidence=0.95)
    scanner_logger.pii_found("phone", "data/contacts.csv:156", confidence=0.89)
    scanner_logger.pii_found("credit_card", "logs/payment.log:78", confidence=0.97)
    
    # Simulate performance metrics
    execution_time = random.uniform(2.5, 8.3)
    memory_usage = random.uniform(45.2, 127.8)
    
    perf_logger.execution_time("demo_scan", execution_time)
    perf_logger.memory_usage("demo_scan", memory_usage)
    
    # Simulate scan completion
    findings_count = random.randint(8, 24)
    scanner_logger.scan_completed("demo_scan", findings_count, execution_time)
    
    # Simulate security events
    security_logger.login_attempt("admin_001", True, "192.168.1.100")
    security_logger.login_attempt("unknown_user", False, "10.0.0.254")
    
    # Simulate error scenarios
    try:
        # Intentional error for demonstration
        raise ValueError("Simulated scanner configuration error")
    except Exception as e:
        scanner_logger.scan_failed("demo_scan", "Configuration validation failed", exception=e)
    
    # Simulate license access control
    license_logger.scanner_access_denied("premium_scanner", "demo_user", "License tier insufficient")
    
    print("✅ Logging demonstration completed! Check logs/ directory for output files.")
    print("📊 View the log dashboard in DataGuardian Pro for real-time monitoring.")

if __name__ == "__main__":
    demonstrate_scanner_logging()