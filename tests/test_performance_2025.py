#!/usr/bin/env python3
"""
Unit Tests for Performance Testing - Large Model Files
Tests scanner handles large model files without issues
"""

import unittest
import sys
import os
import tempfile
import time
import json
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ai_model_scanner import AIModelScanner
from utils.eu_ai_act_compliance import detect_ai_act_violations

class TestPerformance2025(unittest.TestCase):
    """Test suite for performance with large model files"""

    def setUp(self):
        """Set up test environment"""
        self.scanner = AIModelScanner(region="Netherlands")
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_large_content_processing_speed(self):
        """Test processing speed with large content"""
        # Create large content (10,000 repetitions)
        large_content = (
            "foundation model transformer architecture GPT-4 "
            "computational threshold FLOPS training data copyright "
            "model documentation risk assessment "
        ) * 10000
        
        start_time = time.time()
        findings = detect_ai_act_violations(large_content)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Should complete within 10 seconds for very large content
        self.assertLess(processing_time, 10.0, 
                       f"Large content processing took {processing_time:.2f}s, should be under 10s")
        
        # Should still detect violations
        self.assertGreater(len(findings), 0, "Should detect violations in large content")

    def test_memory_usage_large_files(self):
        """Test memory usage doesn't grow excessively with large files"""
        try:
            import psutil
            process = psutil.Process()
            
            # Get initial memory usage
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Process large content multiple times
            large_content = "foundation model " * 50000
            
            for i in range(5):
                findings = detect_ai_act_violations(large_content)
                self.assertGreater(len(findings), 0)
            
            # Get final memory usage
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # Memory increase should be reasonable (less than 500MB)
            self.assertLess(memory_increase, 500, 
                           f"Memory increased by {memory_increase:.1f}MB, should be under 500MB")
            
        except ImportError:
            self.skipTest("psutil not available for memory testing")

    def test_concurrent_processing_simulation(self):
        """Test simulated concurrent processing"""
        import threading
        import queue
        
        results_queue = queue.Queue()
        
        def process_content(content, result_queue):
            try:
                findings = detect_ai_act_violations(content)
                result_queue.put(('success', len(findings)))
            except Exception as e:
                result_queue.put(('error', str(e)))
        
        # Create multiple threads processing different content
        threads = []
        test_contents = [
            "foundation model GPT transformer" * 1000,
            "large language model FLOPS computation" * 1000,
            "GPAI model documentation risk assessment" * 1000
        ]
        
        start_time = time.time()
        
        for content in test_contents:
            thread = threading.Thread(target=process_content, args=(content, results_queue))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join(timeout=30)  # 30 second timeout
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete within reasonable time
        self.assertLess(total_time, 30.0, "Concurrent processing should complete within 30s")
        
        # Check results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        
        # All should succeed
        self.assertEqual(len(results), len(test_contents))
        for status, result in results:
            self.assertEqual(status, 'success')
            self.assertGreater(result, 0)  # Should find violations

    def test_large_json_model_file(self):
        """Test processing large JSON model files"""
        # Create large mock model file
        large_model_data = {
            "model_type": "transformer",
            "architecture": "GPT-4",
            "parameters": 175000000000,
            "layers": [
                {
                    "layer_id": i,
                    "type": "transformer_block",
                    "weights": [0.1] * 1000,  # Large weight arrays
                    "training_data_source": f"foundation model corpus section {i}",
                    "computational_cost": "high FLOPS requirement"
                }
                for i in range(1000)  # 1000 layers
            ],
            "training_metadata": {
                "copyright_sources": ["copyrighted content"] * 100,
                "documentation": "GPAI model risk assessment" * 100
            }
        }
        
        # Write to temp file
        model_file = os.path.join(self.temp_dir, "large_model.json")
        with open(model_file, 'w') as f:
            json.dump(large_model_data, f)
        
        # Verify file size
        file_size = os.path.getsize(model_file)
        self.assertGreater(file_size, 1000000, "Test file should be over 1MB")  # >1MB
        
        # Test processing
        start_time = time.time()
        
        with open(model_file, 'r') as f:
            content = f.read()
        
        findings = detect_ai_act_violations(content)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should complete within reasonable time
        self.assertLess(processing_time, 15.0, 
                       f"Large JSON processing took {processing_time:.2f}s, should be under 15s")
        
        # Should detect GPAI violations
        gpai_findings = [f for f in findings if f.get('type') == 'AI_ACT_GPAI_COMPLIANCE']
        self.assertGreater(len(gpai_findings), 0, "Should detect GPAI compliance issues")

    def test_stress_test_repeated_scans(self):
        """Test stress testing with repeated scans"""
        test_content = "foundation model transformer GPAI documentation"
        
        start_time = time.time()
        
        # Run 100 scans
        for i in range(100):
            findings = detect_ai_act_violations(test_content)
            self.assertGreater(len(findings), 0, f"Scan {i} should find violations")
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_scan = total_time / 100
        
        # Average time per scan should be reasonable
        self.assertLess(avg_time_per_scan, 0.1, 
                       f"Average scan time {avg_time_per_scan:.3f}s should be under 0.1s")

    def test_regex_performance_optimization(self):
        """Test regex patterns perform well on large content"""
        # Create content designed to test regex performance
        test_patterns = [
            "foundation model " * 1000,
            "transformer architecture " * 1000,
            "FLOPS computational threshold " * 1000,
            "copyright training data " * 1000
        ]
        
        for pattern_content in test_patterns:
            with self.subTest(pattern=pattern_content[:50]):
                start_time = time.time()
                findings = detect_ai_act_violations(pattern_content)
                end_time = time.time()
                
                processing_time = end_time - start_time
                
                # Each pattern should process quickly
                self.assertLess(processing_time, 2.0, 
                               f"Pattern processing took {processing_time:.2f}s, should be under 2s")
                self.assertGreater(len(findings), 0, "Should detect violations")

    def test_file_size_limits(self):
        """Test scanner handles various file sizes appropriately"""
        test_sizes = [
            ("small", "foundation model", 100),      # ~1KB
            ("medium", "foundation model", 10000),   # ~100KB  
            ("large", "foundation model", 100000),   # ~1MB
        ]
        
        for size_name, base_content, repetitions in test_sizes:
            with self.subTest(size=size_name):
                content = (base_content + " ") * repetitions
                
                start_time = time.time()
                findings = detect_ai_act_violations(content)
                end_time = time.time()
                
                processing_time = end_time - start_time
                
                # Processing time should scale reasonably
                max_time = {
                    "small": 1.0,
                    "medium": 5.0, 
                    "large": 15.0
                }[size_name]
                
                self.assertLess(processing_time, max_time, 
                               f"{size_name} file took {processing_time:.2f}s, should be under {max_time}s")
                
                self.assertGreater(len(findings), 0, f"Should detect violations in {size_name} file")

if __name__ == '__main__':
    unittest.main()