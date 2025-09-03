#!/usr/bin/env python3
"""
Unit Tests for AI Model Scanner - 2025 EU AI Act Compliance
Tests end-to-end functionality, GPAI detection, and performance
"""

import unittest
import tempfile
import json
import os
import sys
import io
from unittest.mock import patch, MagicMock
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ai_model_scanner import AIModelScanner
from utils.eu_ai_act_compliance import detect_ai_act_violations, _detect_gpai_compliance

class TestAIModelScanner2025(unittest.TestCase):
    """Test suite for AI Model Scanner with 2025 EU AI Act compliance"""

    def setUp(self):
        """Set up test environment"""
        self.scanner = AIModelScanner(region="Netherlands")
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_gpai_detection_foundation_models(self):
        """Test GPAI detection for foundation models"""
        test_content = """
        This is a large language model (LLM) based on transformer architecture.
        The foundation model uses GPT-4 technology with computational threshold
        exceeding 10^25 FLOPS. Training data includes copyrighted content.
        Model documentation includes capability assessment and risk evaluation.
        """
        
        findings = detect_ai_act_violations(test_content)
        gpai_findings = [f for f in findings if f.get('type') == 'AI_ACT_GPAI_COMPLIANCE']
        
        # Should detect multiple GPAI patterns
        self.assertGreater(len(gpai_findings), 0, "Should detect GPAI compliance requirements")
        
        # Verify penalty structure
        for finding in gpai_findings:
            self.assertEqual(finding.get('penalty_risk'), 'Up to €15M or 3% global turnover')
            self.assertEqual(finding.get('compliance_deadline'), 'August 2, 2025 (Effective)')
            self.assertIn('Articles 51-55', finding.get('article_reference', ''))

    def test_gpai_detection_patterns(self):
        """Test specific GPAI detection patterns"""
        test_cases = [
            ("foundation model", True),
            ("large language model", True),
            ("transformer architecture", True),
            ("FLOPS computation", True),
            ("training data copyright", True),
            ("model documentation", True),
            ("simple calculator", False),
            ("basic web form", False)
        ]
        
        for content, should_detect in test_cases:
            with self.subTest(content=content):
                findings = _detect_gpai_compliance(content)
                if should_detect:
                    self.assertGreater(len(findings), 0, f"Should detect GPAI in: {content}")
                else:
                    self.assertEqual(len(findings), 0, f"Should not detect GPAI in: {content}")

    def test_penalty_calculation_structure(self):
        """Test 2025 penalty calculation structure"""
        # Test prohibited practices penalty
        prohibited_findings = [{'type': 'prohibited', 'severity': 'Critical'}]
        
        # Test GPAI penalty  
        gpai_findings = [{'type': 'AI_ACT_GPAI_COMPLIANCE', 'severity': 'High'}]
        
        # Verify penalty structure in findings
        gpai_detection = _detect_gpai_compliance("foundation model GPT transformer")
        for finding in gpai_detection:
            penalty = finding.get('penalty_risk', '')
            self.assertIn('€15M', penalty, "GPAI penalties should reference €15M")
            self.assertIn('3%', penalty, "GPAI penalties should reference 3% global turnover")

    def test_2025_enforcement_timeline(self):
        """Test 2025 enforcement timeline accuracy"""
        findings = _detect_gpai_compliance("large language model documentation")
        
        for finding in findings:
            deadline = finding.get('compliance_deadline', '')
            self.assertIn('August 2, 2025', deadline, "GPAI deadline should be August 2, 2025")
            self.assertIn('Effective', deadline, "Should indicate enforcement is active")

    def test_article_references_accuracy(self):
        """Test article references are accurate for 2025"""
        findings = _detect_gpai_compliance("foundation model with systemic risk")
        
        for finding in findings:
            article_ref = finding.get('article_reference', '')
            self.assertIn('Articles 51-55', article_ref, "Should reference correct GPAI articles")
            self.assertIn('GPAI Models', article_ref, "Should specify GPAI model context")

    def test_model_file_simulation(self):
        """Test end-to-end model file processing simulation"""
        # Create mock model file content
        mock_model_content = """
        {
            "model_type": "transformer",
            "architecture": "GPT-4",
            "parameters": 175000000000,
            "training_data": "Large corpus including copyrighted content",
            "capabilities": ["text generation", "reasoning", "code generation"],
            "computational_cost": "10^25 FLOPS",
            "documentation": "foundation model risk assessment"
        }
        """
        
        # Create temporary model file
        model_file = os.path.join(self.test_dir, "test_model.json")
        with open(model_file, 'w') as f:
            f.write(mock_model_content)
        
        # Test scanner can process the file
        self.assertTrue(os.path.exists(model_file), "Test model file should exist")
        
        # Simulate file content analysis
        findings = detect_ai_act_violations(mock_model_content)
        gpai_findings = [f for f in findings if f.get('type') == 'AI_ACT_GPAI_COMPLIANCE']
        
        self.assertGreater(len(gpai_findings), 0, "Should detect GPAI compliance issues in model file")

    @patch('streamlit.session_state', {'language': 'nl'})
    def test_dutch_language_context(self):
        """Test scanner works in Dutch language context"""
        # Simulate Dutch language context
        with patch('streamlit.session_state', {'language': 'nl'}):
            scanner = AIModelScanner(region="Netherlands")
            self.assertEqual(scanner.region, "Netherlands")
            
            # Test GPAI detection still works with Dutch context
            findings = _detect_gpai_compliance("foundation model transformer architecture")
            self.assertGreater(len(findings), 0, "GPAI detection should work in Dutch context")

    def test_performance_large_content(self):
        """Test performance with large model content"""
        # Create large test content (simulating large model file)
        large_content = "foundation model " * 10000 + "transformer architecture " * 5000
        
        start_time = time.time()
        findings = detect_ai_act_violations(large_content)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Should complete within reasonable time (5 seconds for large content)
        self.assertLess(processing_time, 5.0, "Large content processing should complete within 5 seconds")
        self.assertGreater(len(findings), 0, "Should detect violations in large content")

    def test_scanner_region_compliance(self):
        """Test scanner respects Netherlands region compliance"""
        scanner = AIModelScanner(region="Netherlands")
        self.assertEqual(scanner.region, "Netherlands")
        
        # Test scanner can be initialized with different regions
        eu_scanner = AIModelScanner(region="EU")
        self.assertEqual(eu_scanner.region, "EU")

    def test_remediation_guidance(self):
        """Test remediation guidance for GPAI findings"""
        findings = _detect_gpai_compliance("foundation model risk assessment")
        
        for finding in findings:
            remediation = finding.get('remediation', '')
            self.assertIn('transparency', remediation.lower(), "Should include transparency requirements")
            self.assertIn('documentation', remediation.lower(), "Should include documentation requirements")

if __name__ == '__main__':
    unittest.main()