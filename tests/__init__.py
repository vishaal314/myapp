"""
Test Suite for DataGuardian Pro Scanner Ecosystem
Comprehensive automated testing for all 10 scanner types.
Enterprise Connector Tests for Quality, Performance, Scalability, and Security
"""

__version__ = "1.0.0"
__author__ = "DataGuardian Pro"

# Test configuration
TEST_CONFIG = {
    'timeout': 30,
    'max_retries': 3,
    'verbose_logging': False,
    'mock_external_apis': True,
    'enterprise_endpoints': {
        'microsoft365': 'https://graph.microsoft.com',
        'google_workspace': 'https://www.googleapis.com',
        'exact_online': 'https://start.exactonline.nl',
        'sap': 'https://sap-test-server'
    }
}

# Import test classes for easy access (when available)
try:
    from .test_enterprise_connectors import (
        TestMicrosoft365Connector,
        TestGoogleWorkspaceConnector,
        TestExactOnlineConnector,
        TestSAPConnector,
        TestPerformanceMetrics
    )
    
    __all__ = [
        'TestMicrosoft365Connector',
        'TestGoogleWorkspaceConnector', 
        'TestExactOnlineConnector',
        'TestSAPConnector',
        'TestPerformanceMetrics',
        'TEST_CONFIG'
    ]
except ImportError:
    # Enterprise connector tests not available
    __all__ = ['TEST_CONFIG']