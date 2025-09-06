#!/usr/bin/env python3
"""
Comprehensive Unit Tests for Scanner Log Dashboard
DataGuardian Pro - Scanner Logs Dashboard Testing Suite
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.scanner_log_dashboard import ScannerLogAnalyzer, ScannerLogDashboard
except ImportError as e:
    print(f"Warning: Could not import scanner dashboard modules: {e}")
    ScannerLogAnalyzer = None
    ScannerLogDashboard = None

class TestScannerLogAnalyzer(unittest.TestCase):
    """Test cases for ScannerLogAnalyzer functionality"""
    
    def setUp(self):
        """Set up test environment with temporary log directory"""
        if ScannerLogAnalyzer is None:
            self.skipTest("Scanner dashboard modules not available")
            
        self.temp_dir = tempfile.mkdtemp()
        self.analyzer = ScannerLogAnalyzer(logs_dir=self.temp_dir)
        self.sample_logs = self._create_sample_log_data()
        
    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def _create_sample_log_data(self):
        """Create realistic sample log data for testing"""
        now = datetime.utcnow()
        
        return [
            # Recent successful scan
            {
                "timestamp": (now - timedelta(hours=1)).isoformat() + "Z",
                "level": "INFO",
                "category": "scanner",
                "scanner_type": "code_scanner",
                "message": "Scan completed successfully",
                "execution_time": 5.2,
                "memory_usage": 128.5,
                "findings_count": 15
            },
            # Recent error
            {
                "timestamp": (now - timedelta(hours=2)).isoformat() + "Z",
                "level": "ERROR", 
                "category": "scanner",
                "scanner_type": "ai_model_scanner",
                "message": "Connection timeout during model analysis",
                "execution_time": 0,
                "memory_usage": 0,
                "error_code": "TIMEOUT"
            },
            # Warning from blob scanner
            {
                "timestamp": (now - timedelta(hours=3)).isoformat() + "Z",
                "level": "WARNING",
                "category": "scanner", 
                "scanner_type": "blob_scanner",
                "message": "Large file detected, may impact performance",
                "execution_time": 12.8,
                "memory_usage": 512.1,
                "file_size": "1.2GB"
            },
            # Old successful scan (outside 24h window)
            {
                "timestamp": (now - timedelta(hours=30)).isoformat() + "Z",
                "level": "INFO",
                "category": "scanner",
                "scanner_type": "website_scanner", 
                "message": "Website scan completed",
                "execution_time": 8.5,
                "memory_usage": 256.0
            },
            # Non-scanner log (should be filtered out)
            {
                "timestamp": (now - timedelta(hours=1)).isoformat() + "Z",
                "level": "INFO",
                "category": "system",
                "message": "System startup completed"
            }
        ]
    
    def _write_test_log_file(self, filename, log_entries):
        """Write test log entries to a file"""
        log_path = Path(self.temp_dir) / filename
        with open(log_path, 'w') as f:
            for entry in log_entries:
                f.write(json.dumps(entry) + '\n')
        return log_path
    
    def test_empty_logs_directory(self):
        """Test Case 1: Dashboard behavior with empty logs directory"""
        # Test with no log files
        scanner_types = self.analyzer.get_scanner_types()
        self.assertEqual(scanner_types, [])
        
        logs = self.analyzer.get_scanner_logs(hours=24)
        self.assertEqual(logs, [])
        
        summary = self.analyzer.get_scanner_activity_summary(hours=24)
        expected_summary = {
            'scanner_stats': {},
            'total_operations': 0,
            'total_errors': 0,
            'activity_timeline': [],
            'active_scanners': 0
        }
        self.assertEqual(summary, expected_summary)
    
    def test_mixed_data_scenarios(self):
        """Test Case 2: Dashboard with mixed successful/failed operations"""
        # Write mixed log data
        self._write_test_log_file("dataguardian_scanner.log", self.sample_logs)
        
        # Test scanner type detection
        scanner_types = self.analyzer.get_scanner_types()
        expected_types = ['ai_model_scanner', 'blob_scanner', 'code_scanner', 'website_scanner']
        self.assertEqual(sorted(scanner_types), sorted(expected_types))
        
        # Test log filtering by time (24 hours)
        logs_24h = self.analyzer.get_scanner_logs(hours=24)
        self.assertEqual(len(logs_24h), 3)  # Should exclude 30-hour old entry and non-scanner entry
        
        # Test activity summary
        summary = self.analyzer.get_scanner_activity_summary(hours=24)
        self.assertEqual(summary['total_operations'], 3)
        self.assertEqual(summary['total_errors'], 1)
        self.assertEqual(summary['active_scanners'], 3)
        
        # Verify scanner-specific stats
        scanner_stats = summary['scanner_stats']
        self.assertIn('code_scanner', scanner_stats)
        self.assertEqual(scanner_stats['code_scanner']['total_operations'], 1)
        self.assertEqual(scanner_stats['code_scanner']['errors'], 0)
        
        self.assertIn('ai_model_scanner', scanner_stats)
        self.assertEqual(scanner_stats['ai_model_scanner']['errors'], 1)
    
    def test_large_dataset_performance(self):
        """Test Case 3: Dashboard performance with large datasets"""
        # Generate large dataset (1000 entries)
        large_dataset = []
        base_time = datetime.utcnow()
        
        scanner_types = ['code_scanner', 'blob_scanner', 'ai_model_scanner', 'website_scanner', 'db_scanner']
        levels = ['INFO', 'WARNING', 'ERROR']
        
        for i in range(1000):
            entry = {
                "timestamp": (base_time - timedelta(minutes=i)).isoformat() + "Z",
                "level": levels[i % 3],
                "category": "scanner",
                "scanner_type": scanner_types[i % 5],
                "message": f"Operation {i} completed",
                "execution_time": (i % 20) + 1.0,
                "memory_usage": (i % 100) + 50.0
            }
            large_dataset.append(entry)
        
        # Write large dataset
        self._write_test_log_file("large_scanner.log", large_dataset)
        
        # Test performance with large dataset
        import time
        start_time = time.time()
        
        scanner_types = self.analyzer.get_scanner_types()
        logs = self.analyzer.get_scanner_logs(hours=24)
        summary = self.analyzer.get_scanner_activity_summary(hours=24)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Performance assertions
        self.assertLess(processing_time, 5.0, "Processing should complete within 5 seconds")
        self.assertEqual(len(scanner_types), 5)
        self.assertEqual(len(logs), 1000)  # All entries within 24h window
        self.assertEqual(summary['total_operations'], 1000)
        
        # Verify memory usage calculations
        for scanner, stats in summary['scanner_stats'].items():
            self.assertGreater(stats['avg_memory_usage'], 0)
            self.assertGreater(stats['avg_execution_time'], 0)
    
    def test_error_conditions_and_edge_cases(self):
        """Test Case 4: Error conditions and edge cases"""
        # Test with corrupted JSON log file
        corrupted_logs = [
            json.dumps(self.sample_logs[0]),  # Valid entry
            "{ invalid json }",  # Invalid JSON
            "",  # Empty line
            json.dumps(self.sample_logs[1])  # Valid entry
        ]
        
        log_path = Path(self.temp_dir) / "corrupted_scanner.log"
        with open(log_path, 'w') as f:
            for line in corrupted_logs:
                f.write(line + '\n')
        
        # Should handle corrupted data gracefully
        logs = self.analyzer.get_scanner_logs(hours=24)
        self.assertEqual(len(logs), 2)  # Should get 2 valid entries
        
        # Test with missing timestamp
        logs_no_timestamp = [{
            "level": "INFO",
            "category": "scanner",
            "scanner_type": "test_scanner",
            "message": "No timestamp entry"
        }]
        self._write_test_log_file("no_timestamp.log", logs_no_timestamp)
        
        # Should handle missing timestamps gracefully
        summary = self.analyzer.get_scanner_activity_summary(hours=24)
        self.assertGreaterEqual(summary['total_operations'], 2)
        
        # Test filtering with non-existent scanner type
        filtered_logs = self.analyzer.get_scanner_logs(hours=24, scanner_type="non_existent_scanner")
        self.assertEqual(len(filtered_logs), 0)
        
        # Test with very short time window
        recent_logs = self.analyzer.get_scanner_logs(hours=0.1)  # 6 minutes
        # Should return limited results
        self.assertLessEqual(len(recent_logs), len(logs))
    
    def test_filtering_and_search_functionality(self):
        """Test Case 5: Advanced filtering and search functionality"""
        # Create diverse test data for filtering
        filter_test_logs = [
            {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "level": "ERROR",
                "category": "scanner", 
                "scanner_type": "code_scanner",
                "message": "Critical error in authentication module"
            },
            {
                "timestamp": datetime.utcnow().isoformat() + "Z", 
                "level": "WARNING",
                "category": "scanner",
                "scanner_type": "code_scanner", 
                "message": "Deprecated API usage detected"
            },
            {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "level": "INFO",
                "category": "scanner",
                "scanner_type": "blob_scanner",
                "message": "File processing completed successfully"
            },
            {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "level": "ERROR", 
                "category": "scanner",
                "scanner_type": "blob_scanner",
                "message": "Failed to access storage container"
            }
        ]
        
        self._write_test_log_file("filter_test.log", filter_test_logs)
        
        # Test scanner type filtering
        code_logs = self.analyzer.get_scanner_logs(hours=24, scanner_type="code_scanner")
        self.assertEqual(len(code_logs), 2)
        for log in code_logs:
            self.assertEqual(log['scanner_type'], 'code_scanner')
        
        blob_logs = self.analyzer.get_scanner_logs(hours=24, scanner_type="blob_scanner") 
        self.assertEqual(len(blob_logs), 2)
        for log in blob_logs:
            self.assertEqual(log['scanner_type'], 'blob_scanner')
        
        # Test level filtering
        error_logs = self.analyzer.get_scanner_logs(hours=24, level="ERROR")
        self.assertEqual(len(error_logs), 2)
        for log in error_logs:
            self.assertEqual(log['level'], 'ERROR')
        
        warning_logs = self.analyzer.get_scanner_logs(hours=24, level="WARNING")
        self.assertEqual(len(warning_logs), 1)
        self.assertEqual(warning_logs[0]['level'], 'WARNING')
        
        # Test combined filtering
        code_errors = self.analyzer.get_scanner_logs(hours=24, scanner_type="code_scanner", level="ERROR")
        self.assertEqual(len(code_errors), 1)
        self.assertEqual(code_errors[0]['scanner_type'], 'code_scanner')
        self.assertEqual(code_errors[0]['level'], 'ERROR')
        
        # Test case-insensitive filtering
        case_test_logs = self.analyzer.get_scanner_logs(hours=24, scanner_type="CODE_SCANNER")
        self.assertEqual(len(case_test_logs), 2)  # Should still match despite case difference


class TestScannerLogDashboard(unittest.TestCase):
    """Test cases for ScannerLogDashboard UI components"""
    
    def setUp(self):
        """Set up test environment for dashboard testing"""
        if ScannerLogDashboard is None:
            self.skipTest("Scanner dashboard modules not available")
            
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock streamlit to avoid GUI dependencies in tests
        self.mock_st = Mock()
        self.mock_st.title = Mock()
        self.mock_st.markdown = Mock()
        self.mock_st.selectbox = Mock()
        self.mock_st.columns = Mock(return_value=[Mock(), Mock(), Mock(), Mock()])
        self.mock_st.metric = Mock()
        self.mock_st.info = Mock()
        self.mock_st.error = Mock()
        self.mock_st.session_state = {'log_hours': 24, 'log_scanner_filter': 'All', 'log_level_filter': 'All'}
        
    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('streamlit.title')
    @patch('streamlit.markdown') 
    @patch('streamlit.session_state')
    def test_dashboard_initialization(self, mock_session_state, mock_markdown, mock_title):
        """Test dashboard initialization without errors"""
        mock_session_state.__getitem__ = Mock(side_effect={'log_hours': 24, 'log_scanner_filter': 'All', 'log_level_filter': 'All'}.get)
        mock_session_state.get = Mock(side_effect=lambda key, default: {'log_hours': 24, 'log_scanner_filter': 'All', 'log_level_filter': 'All'}.get(key, default))
        
        dashboard = ScannerLogDashboard()
        
        # Test that dashboard initializes without exceptions
        self.assertIsNotNone(dashboard)
        self.assertIsNotNone(dashboard.analyzer)
    
    def test_analyzer_integration(self):
        """Test dashboard integration with analyzer"""
        dashboard = ScannerLogDashboard()
        
        # Test analyzer accessibility
        self.assertIsInstance(dashboard.analyzer, ScannerLogAnalyzer)
        
        # Test that analyzer methods are accessible through dashboard
        scanner_types = dashboard.analyzer.get_scanner_types()
        self.assertIsInstance(scanner_types, list)
        
        logs = dashboard.analyzer.get_scanner_logs(hours=24)
        self.assertIsInstance(logs, list)
        
        summary = dashboard.analyzer.get_scanner_activity_summary(hours=24)
        self.assertIsInstance(summary, dict)
        self.assertIn('total_operations', summary)
        self.assertIn('active_scanners', summary)


if __name__ == '__main__':
    # Configure test logging
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    loader = unittest.TestLoader()
    suite.addTest(loader.loadTestsFromTestCase(TestScannerLogAnalyzer))
    suite.addTest(loader.loadTestsFromTestCase(TestScannerLogDashboard))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Scanner Log Dashboard Test Summary")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%" if result.testsRun > 0 else "N/A")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print(f"\nErrors:")  
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")