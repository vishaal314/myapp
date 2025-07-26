#!/usr/bin/env python3
"""
DataGuardian Pro - Comprehensive Test Suite Runner
Executes all scanner tests and generates comprehensive reports.
"""

import sys
import os
import unittest
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_comprehensive_test_suite() -> Dict[str, Any]:
    """Run comprehensive test suite for all scanners"""
    test_results = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'error_tests': 0,
        'total_time': 0,
        'scanner_results': {},
        'overall_grade': 'F',
        'production_ready': False
    }
    
    # Define all scanner test modules
    scanner_test_modules = [
        ('Code Scanner', 'test_code_scanner'),
        ('Website Scanner', 'test_website_scanner'),
        ('Image Scanner', 'test_image_scanner'),
        ('AI Model Scanner', 'test_ai_model_scanner'),
        ('DPIA Scanner', 'test_dpia_scanner'),
        ('Sustainability Scanner', 'test_sustainability_scanner')
    ]
    
    print("🧪 DataGuardian Pro - Comprehensive Test Suite")
    print("=" * 60)
    print(f"Starting automated testing at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Testing {len(scanner_test_modules)} scanner types...")
    print()
    
    start_time = time.time()
    
    for scanner_name, module_name in scanner_test_modules:
        print(f"🔍 Testing {scanner_name}...")
        module_start_time = time.time()
        
        try:
            # Import test module
            test_module = __import__(f'tests.{module_name}', fromlist=[module_name])
            
            # Create test suite
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(test_module)
            
            # Run tests with custom result collector
            stream = unittest.StringIO()
            runner = unittest.TextTestRunner(stream=stream, verbosity=2)
            result = runner.run(suite)
            
            # Calculate timing
            module_time = time.time() - module_start_time
            
            # Calculate success metrics
            tests_run = result.testsRun
            failures = len(result.failures)
            errors = len(result.errors)
            passed = tests_run - failures - errors
            success_rate = (passed / tests_run * 100) if tests_run > 0 else 0
            
            # Determine grade based on success rate
            if success_rate >= 95:
                grade = 'A+'
            elif success_rate >= 90:
                grade = 'A'
            elif success_rate >= 85:
                grade = 'A-'
            elif success_rate >= 80:
                grade = 'B+'
            elif success_rate >= 75:
                grade = 'B'
            elif success_rate >= 70:
                grade = 'B-'
            elif success_rate >= 60:
                grade = 'C'
            else:
                grade = 'F'
            
            # Record results
            test_results['scanner_results'][scanner_name] = {
                'tests_run': tests_run,
                'passed': passed,
                'failures': failures,
                'errors': errors,
                'success_rate': success_rate,
                'grade': grade,
                'execution_time': module_time,
                'production_ready': success_rate >= 85,
                'test_output': stream.getvalue()
            }
            
            # Update totals
            test_results['total_tests'] += tests_run
            test_results['passed_tests'] += passed
            test_results['failed_tests'] += failures
            test_results['error_tests'] += errors
            test_results['total_time'] += module_time
            
            # Print results
            status_emoji = "✅" if success_rate >= 85 else "⚠️" if success_rate >= 70 else "❌"
            print(f"   {status_emoji} {scanner_name}: {passed}/{tests_run} tests passed ({success_rate:.1f}%) - Grade: {grade}")
            print(f"      Time: {module_time:.2f}s")
            
            if failures > 0:
                print(f"      ⚠️ {failures} test failures")
            if errors > 0:
                print(f"      ❌ {errors} test errors")
            
        except Exception as e:
            print(f"   ❌ {scanner_name}: Test execution failed - {str(e)}")
            test_results['scanner_results'][scanner_name] = {
                'error': str(e),
                'execution_time': time.time() - module_start_time,
                'production_ready': False
            }
        
        print()
    
    # Calculate overall results
    end_time = time.time()
    test_results['total_time'] = end_time - start_time
    
    if test_results['total_tests'] > 0:
        overall_success_rate = (test_results['passed_tests'] / test_results['total_tests']) * 100
        test_results['overall_success_rate'] = overall_success_rate
        
        # Calculate overall grade
        if overall_success_rate >= 95:
            test_results['overall_grade'] = 'A+'
        elif overall_success_rate >= 90:
            test_results['overall_grade'] = 'A'
        elif overall_success_rate >= 85:
            test_results['overall_grade'] = 'A-'
        elif overall_success_rate >= 80:
            test_results['overall_grade'] = 'B+'
        elif overall_success_rate >= 75:
            test_results['overall_grade'] = 'B'
        elif overall_success_rate >= 70:
            test_results['overall_grade'] = 'B-'
        elif overall_success_rate >= 60:
            test_results['overall_grade'] = 'C'
        else:
            test_results['overall_grade'] = 'F'
        
        # Determine production readiness
        production_ready_scanners = sum(1 for result in test_results['scanner_results'].values() 
                                       if result.get('production_ready', False))
        test_results['production_ready'] = (production_ready_scanners >= len(scanner_test_modules) * 0.8)
    
    return test_results

def print_summary_report(results: Dict[str, Any]):
    """Print comprehensive summary report"""
    print("📊 TEST SUITE SUMMARY REPORT")
    print("=" * 60)
    print(f"Overall Grade: {results['overall_grade']}")
    print(f"Production Ready: {'✅ YES' if results['production_ready'] else '❌ NO'}")
    print(f"Total Execution Time: {results['total_time']:.2f} seconds")
    print()
    
    print(f"📈 Test Statistics:")
    print(f"   Total Tests: {results['total_tests']}")
    print(f"   Passed: {results['passed_tests']} ({results.get('overall_success_rate', 0):.1f}%)")
    print(f"   Failed: {results['failed_tests']}")
    print(f"   Errors: {results['error_tests']}")
    print()
    
    print("🔍 Scanner Results:")
    for scanner_name, scanner_result in results['scanner_results'].items():
        if 'error' in scanner_result:
            print(f"   ❌ {scanner_name}: ERROR - {scanner_result['error']}")
        else:
            success_rate = scanner_result.get('success_rate', 0)
            grade = scanner_result.get('grade', 'F')
            ready = "✅" if scanner_result.get('production_ready', False) else "❌"
            print(f"   {ready} {scanner_name}: {success_rate:.1f}% (Grade: {grade})")
    
    print()
    
    # Production readiness assessment
    print("🚀 Production Readiness Assessment:")
    ready_scanners = [name for name, result in results['scanner_results'].items() 
                     if result.get('production_ready', False)]
    not_ready_scanners = [name for name, result in results['scanner_results'].items() 
                         if not result.get('production_ready', False)]
    
    print(f"   ✅ Ready: {len(ready_scanners)}/{len(results['scanner_results'])}")
    for scanner in ready_scanners:
        print(f"      • {scanner}")
    
    if not_ready_scanners:
        print(f"   ❌ Needs Work: {len(not_ready_scanners)}")
        for scanner in not_ready_scanners:
            print(f"      • {scanner}")
    
    print()
    
    # Recommendations
    print("💡 Recommendations:")
    if results['overall_grade'] in ['A+', 'A', 'A-']:
        print("   🎉 Excellent! System is ready for production deployment.")
        print("   🚀 Proceed with confidence to Netherlands market launch.")
    elif results['overall_grade'] in ['B+', 'B', 'B-']:
        print("   ⚠️ Good performance with minor issues to address.")
        print("   🔧 Fix failing tests before production deployment.")
    else:
        print("   ❌ Significant issues detected. Address before deployment.")
        print("   🔧 Review failing tests and implement fixes.")
    
    print()

def save_detailed_report(results: Dict[str, Any], filename: str = "test_results.json"):
    """Save detailed test results to JSON file"""
    try:
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"📄 Detailed results saved to: {filename}")
    except Exception as e:
        print(f"❌ Failed to save results: {e}")

def main():
    """Main test runner function"""
    print("🔥 Starting DataGuardian Pro Test Suite...")
    print()
    
    # Run comprehensive tests
    results = run_comprehensive_test_suite()
    
    # Print summary
    print_summary_report(results)
    
    # Save detailed results
    save_detailed_report(results)
    
    # Exit with appropriate code
    if results['production_ready'] and results['overall_grade'] in ['A+', 'A', 'A-']:
        print("✅ All tests completed successfully! System ready for deployment.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Review and fix issues before deployment.")
        sys.exit(1)

if __name__ == '__main__':
    main()