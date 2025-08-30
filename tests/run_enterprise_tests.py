#!/usr/bin/env python3
"""
Enterprise Connector Test Runner
Automated test execution for DataGuardian Pro Enterprise Connectors

Usage:
    python tests/run_enterprise_tests.py [options]
    
Options:
    --connector TYPE    Run tests for specific connector (microsoft365, google_workspace, exact_online, sap)
    --category TYPE     Run specific test category (quality, performance, scalability, security)
    --verbose          Enable verbose output
    --coverage         Generate coverage report
"""

import sys
import os
import unittest
import argparse
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def setup_test_environment():
    """Setup test environment and dependencies"""
    # Mock environment variables for testing
    test_env = {
        'SALESFORCE_TIMEOUT': '10',
        'SAP_SSL_VERIFY': 'false',  # For testing only
        'SAP_REQUEST_TIMEOUT': '10',
        'TESTING_MODE': 'true'
    }
    
    for key, value in test_env.items():
        os.environ.setdefault(key, value)
    
    # Ensure logs directory exists
    logs_dir = project_root / 'logs'
    logs_dir.mkdir(exist_ok=True)

def run_connector_tests(connector_type=None, test_category=None, verbose=False):
    """Run enterprise connector tests with filtering options"""
    from test_enterprise_connectors import (
        TestMicrosoft365Connector,
        TestGoogleWorkspaceConnector, 
        TestExactOnlineConnector,
        TestSAPConnector,
        TestPerformanceMetrics
    )
    
    # Map connector types to test classes
    connector_tests = {
        'microsoft365': TestMicrosoft365Connector,
        'google_workspace': TestGoogleWorkspaceConnector,
        'exact_online': TestExactOnlineConnector,
        'sap': TestSAPConnector,
        'performance': TestPerformanceMetrics
    }
    
    # Build test suite
    test_suite = unittest.TestSuite()
    
    if connector_type and connector_type in connector_tests:
        # Run specific connector tests
        test_class = connector_tests[connector_type]
        if test_category:
            # Filter by category (quality, performance, scalability, security)
            for test_name in unittest.TestLoader().getTestCaseNames(test_class):
                if test_category.lower() in test_name.lower():
                    test_suite.addTest(test_class(test_name))
        else:
            # Run all tests for connector
            tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
            test_suite.addTests(tests)
    else:
        # Run all connector tests
        for test_class in connector_tests.values():
            if test_category:
                # Filter by category across all connectors
                for test_name in unittest.TestLoader().getTestCaseNames(test_class):
                    if test_category.lower() in test_name.lower():
                        test_suite.addTest(test_class(test_name))
            else:
                tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
                test_suite.addTests(tests)
    
    # Configure test runner
    verbosity = 2 if verbose else 1
    runner = unittest.TextTestRunner(
        verbosity=verbosity,
        stream=sys.stdout,
        buffer=True
    )
    
    # Run tests
    print(f"{'='*80}")
    print("DATAGUARDIAN PRO ENTERPRISE CONNECTOR TEST SUITE")
    print(f"{'='*80}")
    
    if connector_type:
        print(f"Testing: {connector_type.upper()} Connector")
    if test_category:
        print(f"Category: {test_category.upper()}")
    
    print(f"Test Count: {test_suite.countTestCases()}")
    print(f"{'='*80}")
    
    start_time = time.time()
    result = runner.run(test_suite)
    end_time = time.time()
    
    # Generate test report
    generate_test_report(result, end_time - start_time, connector_type, test_category)
    
    return result.wasSuccessful()

def generate_test_report(result, execution_time, connector_type=None, test_category=None):
    """Generate comprehensive test report"""
    print(f"\n{'='*80}")
    print("TEST EXECUTION SUMMARY")
    print(f"{'='*80}")
    
    # Basic metrics
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    success_count = total_tests - failures - errors
    success_rate = (success_count / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests Run: {total_tests}")
    print(f"Successful: {success_count}")
    print(f"Failures: {failures}")
    print(f"Errors: {errors}")
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"Execution Time: {execution_time:.2f} seconds")
    
    # Performance metrics
    if total_tests > 0:
        avg_time_per_test = execution_time / total_tests
        print(f"Average Time Per Test: {avg_time_per_test:.3f} seconds")
    
    # Category breakdown
    if not connector_type and not test_category:
        print(f"\n{'='*40}")
        print("CONNECTOR BREAKDOWN")
        print(f"{'='*40}")
        
        connectors = ['microsoft365', 'google_workspace', 'exact_online', 'sap']
        for connector in connectors:
            connector_tests = [test for test in result.testsRun if connector in str(test)]
            print(f"{connector.upper()}: Tests available")
    
    # Detailed failure/error report
    if failures or errors:
        print(f"\n{'='*40}")
        print("DETAILED ISSUE REPORT")
        print(f"{'='*40}")
        
        if failures:
            print("\nFAILURES:")
            for i, (test, traceback) in enumerate(result.failures, 1):
                print(f"{i}. {test}")
                print(f"   Error: {traceback.split('AssertionError:')[-1].strip()}")
        
        if errors:
            print("\nERRORS:")
            for i, (test, traceback) in enumerate(result.errors, 1):
                print(f"{i}. {test}")
                print(f"   Error: {traceback.split('Exception:')[-1].strip()}")
    
    # Recommendations
    print(f"\n{'='*40}")
    print("RECOMMENDATIONS")
    print(f"{'='*40}")
    
    if success_rate >= 95:
        print("✅ Excellent: Enterprise connectors are production-ready")
    elif success_rate >= 90:
        print("✅ Good: Minor issues to address before production")
    elif success_rate >= 80:
        print("⚠️  Warning: Several issues need attention")
    else:
        print("❌ Critical: Major issues must be resolved")
    
    if avg_time_per_test > 2.0:
        print("⚠️  Performance: Consider optimizing slow tests")
    
    print(f"{'='*80}")

def main():
    """Main test runner entry point"""
    parser = argparse.ArgumentParser(
        description="DataGuardian Pro Enterprise Connector Test Suite"
    )
    
    parser.add_argument(
        '--connector',
        choices=['microsoft365', 'google_workspace', 'exact_online', 'sap', 'performance'],
        help='Run tests for specific connector'
    )
    
    parser.add_argument(
        '--category',
        choices=['quality', 'performance', 'scalability', 'security'],
        help='Run specific test category'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--list-tests',
        action='store_true',
        help='List available tests without running them'
    )
    
    args = parser.parse_args()
    
    # Setup test environment
    setup_test_environment()
    
    # List tests if requested
    if args.list_tests:
        list_available_tests()
        return True
    
    # Run tests
    try:
        success = run_connector_tests(
            connector_type=args.connector,
            test_category=args.category,
            verbose=args.verbose
        )
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\nTest execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nTest execution failed: {e}")
        sys.exit(1)

def list_available_tests():
    """List all available tests"""
    from test_enterprise_connectors import (
        TestMicrosoft365Connector,
        TestGoogleWorkspaceConnector,
        TestExactOnlineConnector,
        TestSAPConnector,
        TestPerformanceMetrics
    )
    
    test_classes = {
        'Microsoft 365': TestMicrosoft365Connector,
        'Google Workspace': TestGoogleWorkspaceConnector,
        'Exact Online': TestExactOnlineConnector,
        'SAP': TestSAPConnector,
        'Performance': TestPerformanceMetrics
    }
    
    print("AVAILABLE ENTERPRISE CONNECTOR TESTS")
    print("="*50)
    
    for connector_name, test_class in test_classes.items():
        print(f"\n{connector_name} Connector:")
        test_names = unittest.TestLoader().getTestCaseNames(test_class)
        for test_name in test_names:
            # Extract test category and description
            if 'quality' in test_name:
                category = "Quality"
            elif 'performance' in test_name:
                category = "Performance"  
            elif 'scalability' in test_name:
                category = "Scalability"
            elif 'security' in test_name:
                category = "Security"
            else:
                category = "General"
            
            print(f"  [{category}] {test_name}")

if __name__ == '__main__':
    main()