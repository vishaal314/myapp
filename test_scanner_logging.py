#!/usr/bin/env python3
"""
DataGuardian Pro - Scanner Logging Integration Test
Test centralized logging across all scanner types
"""

import sys
import time
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.append('.')

def test_scanner_logging():
    """Test logging integration across different scanner types"""
    
    print("🔍 DataGuardian Pro - Scanner Logging Integration Test")
    print("=" * 60)
    
    try:
        # Import centralized logging
        from utils.centralized_logger import (
            get_scanner_logger, 
            get_license_logger, 
            get_performance_logger,
            get_security_logger
        )
        print("✅ Successfully imported centralized logging")
        
        # Test 1: Code Scanner Logging
        print("\n1. Testing Code Scanner Logging...")
        code_logger = get_scanner_logger("code_scanner")
        code_logger.scan_started("code_scan", "/path/to/code", "admin_001")
        code_logger.scan_progress("code_scan", 25.0, "Scanning Python files")
        code_logger.pii_found("email", "config.py:42", confidence=0.95)
        code_logger.scan_completed("code_scan", 15, 3.45)
        print("   ✅ Code scanner logging successful")
        
        # Test 2: Blob Scanner Logging
        print("\n2. Testing Blob Scanner Logging...")
        blob_logger = get_scanner_logger("blob_scanner")
        blob_logger.scan_started("blob_scan", "/path/to/documents", "admin_001")
        blob_logger.pii_found("phone", "document.pdf:page_2", confidence=0.87)
        blob_logger.scan_completed("blob_scan", 8, 2.12)
        print("   ✅ Blob scanner logging successful")
        
        # Test 3: AI Model Scanner Logging
        print("\n3. Testing AI Model Scanner Logging...")
        ai_logger = get_scanner_logger("ai_model_scanner")
        ai_logger.scan_started("ai_scan", "/models/classifier.pkl", "admin_001")
        ai_logger.scan_progress("ai_scan", 75.0, "Analyzing bias patterns")
        ai_logger.scan_completed("ai_scan", 3, 1.89)
        print("   ✅ AI Model scanner logging successful")
        
        # Test 4: SOC2 Scanner Logging
        print("\n4. Testing SOC2 Scanner Logging...")
        soc2_logger = get_scanner_logger("soc2_scanner")
        soc2_logger.scan_started("soc2_scan", "github.com/example/repo", "admin_001")
        soc2_logger.scan_completed("soc2_scan", 12, 5.67)
        print("   ✅ SOC2 scanner logging successful")
        
        # Test 5: License System Logging
        print("\n5. Testing License System Logging...")
        license_logger = get_license_logger()
        license_logger.license_loaded("DGP-ENT-2025-001", "Enterprise Ultimate", "admin_001")
        license_logger.scanner_access_denied("premium_scanner", "demo_user", "License tier insufficient")
        print("   ✅ License system logging successful")
        
        # Test 6: Performance Logging
        print("\n6. Testing Performance Logging...")
        perf_logger = get_performance_logger()
        perf_logger.execution_time("full_scan", 12.34)
        perf_logger.memory_usage("full_scan", 156.8)
        perf_logger.performance_warning("slow_operation", "Exceeded 10s threshold")
        print("   ✅ Performance logging successful")
        
        # Test 7: Security Logging
        print("\n7. Testing Security Logging...")
        security_logger = get_security_logger()
        security_logger.login_attempt("admin_001", True, "192.168.1.100")
        security_logger.login_attempt("hacker", False, "10.0.0.254")
        security_logger.unauthorized_access("demo_user", "enterprise_scanner", "192.168.1.200")
        print("   ✅ Security logging successful")
        
        # Test 8: Error Handling
        print("\n8. Testing Error Handling...")
        try:
            raise ValueError("Test error for logging")
        except Exception as e:
            code_logger.error("Test error occurred", exception=e)
        print("   ✅ Error logging successful")
        
        # Verify log files
        print("\n9. Verifying Log Files...")
        log_dir = Path("logs")
        log_files = list(log_dir.glob("dataguardian_*.log"))
        
        print(f"   📁 Found {len(log_files)} log files:")
        for log_file in log_files:
            size = log_file.stat().st_size
            print(f"      - {log_file.name}: {size} bytes")
        
        print("\n✅ All scanner logging tests completed successfully!")
        print(f"📊 Log files created in: {log_dir.absolute()}")
        print("🎯 Ready for production use!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_scanner_logging()
    sys.exit(0 if success else 1)