#!/usr/bin/env python3
"""
Run tests for GDPR risk categorization

This script runs the unit and integration tests for the GDPR risk categorization system.
"""

import unittest
import sys
import os

def run_tests():
    """Run the tests for GDPR risk categorization"""
    # Ensure services module is in path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # Discover and run tests
    loader = unittest.TestLoader()
    
    # Run unit tests
    unit_tests = loader.discover("tests", pattern="test_gdpr_risk_categories.py")
    
    # Run integration tests
    integration_tests = loader.discover("tests", pattern="test_gdpr_integration.py")
    
    # Create test suite
    test_suite = unittest.TestSuite()
    test_suite.addTests(unit_tests)
    test_suite.addTests(integration_tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_tests())