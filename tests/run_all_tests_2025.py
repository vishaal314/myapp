#!/usr/bin/env python3
"""
Test Runner for 2025 EU AI Act Compliance Test Suite
Runs all unit tests and provides comprehensive report
"""

import unittest
import sys
import os
import time
from io import StringIO

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_test_suite():
    """Run all 2025 compliance tests and return results"""
    
    # Discover and load all tests
    test_modules = [
        'test_ai_model_scanner_2025',
        'test_dutch_reports_2025', 
        'test_penalty_calculations_2025',
        'test_certificate_generation_2025',
        'test_performance_2025'
    ]
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    print("🧪 DataGuardian Pro 2025 EU AI Act Compliance Test Suite")
    print("=" * 60)
    
    # Load tests from each module
    for module_name in test_modules:
        try:
            module = __import__(module_name)
            module_suite = loader.loadTestsFromModule(module)
            suite.addTest(module_suite)
            print(f"✅ Loaded tests from {module_name}")
        except ImportError as e:
            print(f"⚠️  Could not load {module_name}: {e}")
    
    print("\n🚀 Running tests...")
    print("-" * 40)
    
    # Run tests with detailed output
    stream = StringIO()
    runner = unittest.TextTestRunner(
        stream=stream,
        verbosity=2,
        buffer=True
    )
    
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    # Print results
    print(f"\n📊 Test Results Summary")
    print("=" * 40)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / max(result.testsRun, 1) * 100):.1f}%")
    print(f"Execution time: {end_time - start_time:.2f} seconds")
    
    # Print detailed output
    print(f"\n📝 Detailed Output:")
    print("-" * 40)
    print(stream.getvalue())
    
    # Print failures and errors
    if result.failures:
        print(f"\n❌ Failures ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"  • {test}: {traceback.split('AssertionError:')[-1].strip() if 'AssertionError:' in traceback else 'See details above'}")
    
    if result.errors:
        print(f"\n🚨 Errors ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"  • {test}: {traceback.split('Exception:')[-1].strip() if 'Exception:' in traceback else 'See details above'}")
    
    # Overall status
    if result.failures or result.errors:
        print(f"\n🔴 TESTS FAILED - Issues found that need attention")
        return False
    else:
        print(f"\n🟢 ALL TESTS PASSED - 2025 EU AI Act compliance verified!")
        return True

if __name__ == '__main__':
    success = run_test_suite()
    sys.exit(0 if success else 1)