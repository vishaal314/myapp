"""
Test Framework for DataGuardian Pro Scanner Testing
Provides base classes and utilities for comprehensive scanner testing.
"""

import unittest
import time
import json
import tempfile
import os
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test configuration
class TestConfig:
    """Configuration settings for test suite"""
    PERFORMANCE_TIMEOUT = 30  # seconds
    FUNCTIONAL_TIMEOUT = 10   # seconds
    MIN_FINDINGS_THRESHOLD = 1
    MAX_RESPONSE_TIME = 5.0   # seconds
    MEMORY_LIMIT_MB = 100     # MB
    
    # Test data paths
    TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data')
    
    # Expected result thresholds
    EXPECTED_COMPLIANCE_SCORE_MIN = 0
    EXPECTED_COMPLIANCE_SCORE_MAX = 100

class BaseScanner:
    """Base class for scanner testing with common functionality"""
    
    def __init__(self, scanner_name: str):
        self.scanner_name = scanner_name
        self.test_results = []
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging for test execution"""
        logging.basicConfig(
            level=logging.INFO,
            format=f'%(asctime)s - {self.scanner_name} - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.scanner_name)
    
    def measure_performance(self, func, *args, **kwargs):
        """Measure function execution time and memory usage"""
        import psutil
        process = psutil.Process()
        
        # Measure initial state
        start_time = time.time()
        start_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Execute function
        result = func(*args, **kwargs)
        
        # Measure final state
        end_time = time.time()
        end_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        execution_time = end_time - start_time
        memory_used = end_memory - start_memory
        
        return {
            'result': result,
            'execution_time': execution_time,
            'memory_used': memory_used,
            'within_timeout': execution_time <= TestConfig.PERFORMANCE_TIMEOUT,
            'within_memory_limit': memory_used <= TestConfig.MEMORY_LIMIT_MB
        }
    
    def validate_scan_result(self, result: Dict[str, Any]) -> Dict[str, bool]:
        """Validate common scan result structure"""
        validations = {
            'has_scan_id': 'scan_id' in result,
            'has_scan_type': 'scan_type' in result,
            'has_timestamp': 'timestamp' in result,
            'has_findings': 'findings' in result and isinstance(result['findings'], list),
            'has_region': 'region' in result,
            'valid_compliance_score': (
                'compliance_score' in result and 
                TestConfig.EXPECTED_COMPLIANCE_SCORE_MIN <= 
                result.get('compliance_score', 0) <= 
                TestConfig.EXPECTED_COMPLIANCE_SCORE_MAX
            )
        }
        return validations
    
    def create_test_report(self, test_name: str, passed: bool, details: Dict[str, Any]):
        """Create standardized test report"""
        report = {
            'scanner': self.scanner_name,
            'test_name': test_name,
            'timestamp': datetime.now().isoformat(),
            'passed': passed,
            'details': details
        }
        self.test_results.append(report)
        return report

class ScannerTestSuite(unittest.TestCase):
    """Base test suite for scanner testing"""
    
    @classmethod
    def setUpClass(cls):
        """Setup test environment"""
        cls.test_config = TestConfig()
        
        # Create test data directory if it doesn't exist
        os.makedirs(cls.test_config.TEST_DATA_DIR, exist_ok=True)
    
    def create_temp_file(self, content: str, extension: str = '.txt') -> str:
        """Create temporary file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix=extension, delete=False) as f:
            f.write(content)
            return f.name
    
    def cleanup_temp_file(self, filepath: str):
        """Clean up temporary test file"""
        try:
            os.unlink(filepath)
        except OSError:
            pass
    
    def assert_scan_structure(self, result: Dict[str, Any]):
        """Assert that scan result has required structure"""
        self.assertIn('scan_id', result)
        self.assertIn('scan_type', result)
        self.assertIn('timestamp', result)
        self.assertIn('findings', result)
        self.assertIsInstance(result['findings'], list)
    
    def assert_performance_within_limits(self, performance_data: Dict[str, Any]):
        """Assert that performance is within acceptable limits"""
        self.assertTrue(
            performance_data['within_timeout'],
            f"Execution time {performance_data['execution_time']:.2f}s exceeds timeout {TestConfig.PERFORMANCE_TIMEOUT}s"
        )
        self.assertTrue(
            performance_data['within_memory_limit'],
            f"Memory usage {performance_data['memory_used']:.2f}MB exceeds limit {TestConfig.MEMORY_LIMIT_MB}MB"
        )

def run_comprehensive_test_suite():
    """Run comprehensive test suite for all scanners"""
    test_results = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'scanner_results': {}
    }
    
    scanner_modules = [
        'test_code_scanner',
        'test_website_scanner', 
        'test_image_scanner',
        'test_ai_model_scanner',
        'test_database_scanner',
        'test_document_scanner',
        'test_api_scanner',
        'test_soc2_scanner',
        'test_dpia_scanner',
        'test_sustainability_scanner'
    ]
    
    for module_name in scanner_modules:
        try:
            # Import and run tests for each scanner
            module = __import__(f'tests.{module_name}', fromlist=[module_name])
            
            # Run tests and collect results
            suite = unittest.TestLoader().loadTestsFromModule(module)
            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)
            
            # Record results
            scanner_name = module_name.replace('test_', '')
            test_results['scanner_results'][scanner_name] = {
                'tests_run': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors),
                'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
            }
            
            test_results['total_tests'] += result.testsRun
            test_results['passed_tests'] += result.testsRun - len(result.failures) - len(result.errors)
            test_results['failed_tests'] += len(result.failures) + len(result.errors)
            
        except Exception as e:
            print(f"Error testing {module_name}: {e}")
            test_results['scanner_results'][module_name.replace('test_', '')] = {
                'error': str(e)
            }
    
    # Calculate overall success rate
    if test_results['total_tests'] > 0:
        test_results['overall_success_rate'] = (test_results['passed_tests'] / test_results['total_tests']) * 100
    else:
        test_results['overall_success_rate'] = 0
    
    return test_results

if __name__ == '__main__':
    results = run_comprehensive_test_suite()
    print(json.dumps(results, indent=2))