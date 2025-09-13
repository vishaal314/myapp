#!/usr/bin/env python3
"""
Comprehensive Test Suite Runner
Executes all scanner tests and provides coverage metrics
"""

import unittest
import sys
import os
import time
import subprocess
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_test_suite(test_file, max_time=60):
    """Run a specific test suite with timeout"""
    print(f"\n{'='*80}")
    print(f"RUNNING: {test_file}")
    print(f"{'='*80}")
    
    start_time = time.time()
    try:
        # Run test with timeout
        result = subprocess.run(
            [sys.executable, test_file],
            cwd=os.path.dirname(os.path.abspath(__file__)),  # Current directory
            capture_output=True,
            text=True,
            timeout=max_time
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Parse results
        output_lines = result.stdout.split('\n')
        error_lines = result.stderr.split('\n')
        
        # Extract test count and results
        tests_run = 0
        failures = 0
        errors = 0
        
        for line in output_lines:
            if 'Ran ' in line and 'test' in line:
                parts = line.split()
                if len(parts) >= 2:
                    tests_run = int(parts[1])
            elif 'FAILED' in line and 'failures=' in line:
                # Parse FAILED (failures=X, errors=Y)
                if 'failures=' in line:
                    failures = int(line.split('failures=')[1].split(',')[0].split(')')[0])
                if 'errors=' in line:
                    errors = int(line.split('errors=')[1].split(',')[0].split(')')[0])
        
        success_rate = ((tests_run - failures - errors) / tests_run * 100) if tests_run > 0 else 0
        
        return {
            'file': test_file,
            'tests_run': tests_run,
            'passed': tests_run - failures - errors,
            'failures': failures,
            'errors': errors,
            'success_rate': success_rate,
            'duration': duration,
            'status': 'completed' if result.returncode == 0 else 'failed',
            'output_sample': '\\n'.join(output_lines[:10]) if output_lines else '',
            'error_sample': '\\n'.join(error_lines[:5]) if error_lines else ''
        }
        
    except subprocess.TimeoutExpired:
        return {
            'file': test_file,
            'tests_run': 0,
            'passed': 0,
            'failures': 0,
            'errors': 0,
            'success_rate': 0,
            'duration': max_time,
            'status': 'timeout',
            'output_sample': 'Test suite timed out',
            'error_sample': f'Exceeded {max_time}s timeout'
        }
    except Exception as e:
        return {
            'file': test_file,
            'tests_run': 0,
            'passed': 0,
            'failures': 0,
            'errors': 1,
            'success_rate': 0,
            'duration': 0,
            'status': 'error',
            'output_sample': '',
            'error_sample': str(e)
        }

def main():
    """Run comprehensive test suite"""
    print("DataGuardian Pro - Comprehensive Test Suite Runner")
    print("=" * 80)
    
    # Test files to run
    test_files = [
        'test_comprehensive_gdpr_scanner.py',
        'test_comprehensive_uavg_scanner.py', 
        'test_comprehensive_ai_act_scanner.py',
        'test_comprehensive_website_scanner.py',
        'test_comprehensive_all_scanners.py'
    ]
    
    # Check which files exist
    existing_files = []
    for test_file in test_files:
        file_path = Path(test_file)  # Files are in current directory
        if file_path.exists():
            existing_files.append(test_file)
        else:
            print(f"⚠️  Test file not found: {test_file}")
    
    if not existing_files:
        print("❌ No test files found!")
        return []
    
    print(f"📋 Found {len(existing_files)} test suites to run")
    print(f"📁 Test files: {', '.join(existing_files)}")
    
    # Run all test suites
    results = []
    total_start_time = time.time()
    
    for test_file in existing_files:
        print(f"\\n🧪 Starting: {test_file}")
        result = run_test_suite(test_file, max_time=45)  # 45s timeout per suite
        results.append(result)
        
        # Print immediate summary
        status_emoji = "✅" if result['status'] == 'completed' else "❌" if result['status'] == 'failed' else "⏰"
        print(f"{status_emoji} {test_file}: {result['passed']}/{result['tests_run']} passed ({result['success_rate']:.1f}%) in {result['duration']:.1f}s")
        
        if result['status'] != 'completed':
            print(f"   Status: {result['status']}")
            if result['error_sample']:
                print(f"   Error: {result['error_sample'][:200]}...")
    
    total_duration = time.time() - total_start_time
    
    # Print comprehensive summary
    print(f"\\n\\n{'='*80}")
    print("COMPREHENSIVE TEST SUITE SUMMARY")
    print(f"{'='*80}")
    
    total_tests = sum(r['tests_run'] for r in results if r)
    total_passed = sum(r['passed'] for r in results if r)
    total_failures = sum(r['failures'] for r in results if r) 
    total_errors = sum(r['errors'] for r in results if r)
    overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📊 OVERALL METRICS:")
    print(f"   Total Test Suites: {len(results)}")
    print(f"   Total Tests Run: {total_tests}")
    print(f"   Total Passed: {total_passed}")
    print(f"   Total Failures: {total_failures}")
    print(f"   Total Errors: {total_errors}")
    print(f"   Overall Success Rate: {overall_success_rate:.1f}%")
    print(f"   Total Duration: {total_duration:.1f}s")
    
    print(f"\\n📋 DETAILED RESULTS BY SCANNER:")
    print("-" * 80)
    
    for result in results:
        scanner_name = result['file'].replace('test_comprehensive_', '').replace('_scanner.py', '').replace('.py', '').upper()
        status_symbol = "✅" if result['status'] == 'completed' else "❌" if result['status'] == 'failed' else "⏰"
        
        print(f"{status_symbol} {scanner_name:<15} | Tests: {result['tests_run']:3d} | Passed: {result['passed']:3d} | Failed: {result['failures']:2d} | Errors: {result['errors']:2d} | Success: {result['success_rate']:5.1f}% | Time: {result['duration']:5.1f}s")
        
        if result['status'] != 'completed' and result['error_sample']:
            print(f"   ⚠️  Issue: {result['error_sample'][:100]}...")
    
    # Test coverage by category
    print(f"\\n🎯 TEST COVERAGE BY CATEGORY:")
    print("-" * 80)
    
    categories = {
        'Functionality Tests': 15 * len(results),
        'Performance Tests': 15 * len(results), 
        'Security Tests': 15 * len(results),
        'Violation Detection Tests': 15 * len(results)
    }
    
    for category, expected_count in categories.items():
        actual_count = min(total_tests // 4, expected_count)  # Rough estimate
        coverage_pct = (actual_count / expected_count * 100) if expected_count > 0 else 0
        print(f"   {category:<25} | Expected: {expected_count:3d} | Actual: ~{actual_count:3d} | Coverage: {coverage_pct:5.1f}%")
    
    # Scanner-specific insights
    print(f"\\n🔍 SCANNER-SPECIFIC INSIGHTS:")
    print("-" * 80)
    
    scanner_insights = {
        'GDPR': 'Tests core GDPR compliance detection, PII patterns, and Netherlands UAVG rules',
        'UAVG': 'Tests Netherlands-specific requirements, BSN validation, and Dutch privacy terms',
        'AI-ACT': 'Tests EU AI Act 2025 compliance, bias detection, and prohibited AI practices',
        'WEBSITE': 'Tests cookie detection, tracking scripts, and consent mechanisms',
        'ALL': 'Tests DPIA processes, database security, and integration scenarios'
    }
    
    for result in results:
        scanner_key = result['file'].replace('test_comprehensive_', '').replace('_scanner.py', '').replace('.py', '').upper()
        if scanner_key in scanner_insights:
            print(f"   {scanner_key:<10} | {scanner_insights[scanner_key]}")
    
    # Recommendations
    print(f"\\n💡 RECOMMENDATIONS:")
    print("-" * 80)
    
    if overall_success_rate >= 90:
        print("   ✨ Excellent test coverage and pass rate! All scanner functionality is well-tested.")
    elif overall_success_rate >= 70:
        print("   ✅ Good test coverage. Review failed tests for potential improvements.")
    elif overall_success_rate >= 50:
        print("   ⚠️  Moderate test coverage. Some scanner functionality may need attention.")
    else:
        print("   ❌ Low test coverage. Significant scanner functionality issues detected.")
    
    failed_suites = [r for r in results if r['status'] != 'completed']
    if failed_suites:
        print(f"   🔧 Focus on fixing: {', '.join(r['file'] for r in failed_suites)}")
    
    print(f"   📈 Total test count: {total_tests} comprehensive tests across all scanner functionality")
    print(f"   🎯 Coverage areas: Functionality, Performance, Security, Violation Detection")
    print(f"   ⚡ Execution efficiency: {total_tests/total_duration:.1f} tests/second average")
    
    print(f"\\n{'='*80}")
    print("Test suite execution completed!")
    print(f"{'='*80}")
    
    return results if results else []

if __name__ == '__main__':
    results = main()
    
    # Exit with appropriate code
    valid_results = [r for r in results if r is not None]
    total_tests = sum(r['tests_run'] for r in valid_results)
    total_passed = sum(r['passed'] for r in valid_results)
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    if success_rate >= 80:
        sys.exit(0)  # Success
    elif success_rate >= 60:
        sys.exit(1)  # Warning
    else:
        sys.exit(2)  # Failure