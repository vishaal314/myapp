"""
Sample test file for DataGuardian Pro CI/CD pipeline
"""

import unittest
import os
import sys

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Try importing our utilities
try:
    from utils.i18n import get_text
    from utils.error_handler import show_error_message, DataGuardianError
except ImportError:
    print("Warning: Unable to import some modules. Tests may fail.")

class SampleTest(unittest.TestCase):
    """Sample test class to ensure CI pipeline is working"""
    
    def test_simple_assertion(self):
        """Test that basic assertions work"""
        self.assertEqual(1, 1)
        self.assertTrue(True)
        self.assertFalse(False)
    
    def test_error_handler_class(self):
        """Test the DataGuardianError exception class"""
        try:
            # Import the error class dynamically in case it wasn't imported above
            from utils.error_handler import DataGuardianError
            
            # Create a sample error
            error = DataGuardianError(
                error_code="test_error",
                custom_message="This is a test error"
            )
            
            # Check error properties
            self.assertEqual(error.error_code, "test_error")
            self.assertEqual(error.custom_message, "This is a test error")
            
        except ImportError:
            # Skip test if module isn't available
            self.skipTest("Error handler module not available")

if __name__ == '__main__':
    unittest.main()