"""
Comprehensive Test Suite for AI Model Scanner
6 automated tests covering functional and performance validation.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch
from typing import Dict, Any

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_mock_scanners import MockAIModelScanner as AIModelScanner
from tests.test_framework import ScannerTestSuite, BaseScanner

class TestAIModelScanner(ScannerTestSuite):
    """Comprehensive test suite for AI Model Scanner functionality and performance"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.scanner = AIModelScanner(region="Netherlands")
        cls.base_tester = BaseScanner("AIModelScanner")
    
    def test_1_functional_repository_analysis(self):
        """Test 1: Functional - AI Model Repository Analysis"""
        model_details = {
            "repo_url": "https://github.com/example/ai-model",
            "branch_name": "main"
        }
        
        # Mock repository validation response
        mock_validation = {
            "valid": True,
            "findings": [
                {
                    "type": "Bias Risk",
                    "severity": "Medium",
                    "description": "Model training data may contain demographic bias",
                    "risk_level": "medium"
                },
                {
                    "type": "Privacy Leakage",
                    "severity": "High", 
                    "description": "Training data contains PII patterns",
                    "risk_level": "high"
                }
            ]
        }
        
        with patch.object(self.scanner, '_validate_github_repo', return_value=mock_validation):
            performance_data = self.base_tester.measure_performance(
                self.scanner.scan_model,
                "Repository URL",
                model_details,
                ["Bias Detection", "Privacy Leakage"],
                ["Machine Learning"],
                []
            )
            result = performance_data['result']
            
            # Validate structure
            self.assert_scan_structure(result)
            
            # Check AI-specific fields
            self.assertEqual(result['scan_type'], 'AI Model')
            self.assertIn('repository_url', result)
            self.assertGreater(len(result['findings']), 0)
            
            # Check bias detection
            bias_findings = [f for f in result['findings'] if 'bias' in str(f).lower()]
            self.assertGreater(len(bias_findings), 0, "Should detect bias risks")
            
            # Validate performance
            self.assert_performance_within_limits(performance_data)
            
            print(f"✓ Test 1 PASSED: Repository analysis with {len(result['findings'])} findings in {performance_data['execution_time']:.2f}s")
    
    def test_2_functional_eu_ai_act_compliance(self):
        """Test 2: Functional - EU AI Act 2025 Compliance Assessment"""
        model_details = {
            "api_endpoint": "https://api.example.com/model",
            "model_type": "high_risk_ai_system"
        }
        
        # Mock AI Act compliance analysis
        mock_ai_act_findings = [
            {
                "type": "AI Act Violation",
                "severity": "Critical",
                "description": "High-risk AI system lacks required risk assessment documentation",
                "article": "Article 9 - Risk Management System",
                "risk_level": "critical"
            },
            {
                "type": "Documentation Gap",
                "severity": "High",
                "description": "Missing CE marking for high-risk AI system",
                "article": "Article 43 - CE Marking",
                "risk_level": "high"
            }
        ]
        
        with patch.object(self.scanner, '_analyze_ai_act_compliance') as mock_ai_act:
            mock_ai_act.return_value = mock_ai_act_findings
            
            performance_data = self.base_tester.measure_performance(
                self.scanner.scan_model,
                "API Endpoint",
                model_details,
                ["EU AI Act Compliance"],
                ["High-Risk AI System"],
                []
            )
            result = performance_data['result']
            
            # Validate structure
            self.assert_scan_structure(result)
            
            # Check EU AI Act compliance
            ai_act_findings = [f for f in result.get('findings', []) 
                              if 'ai act' in str(f).lower() or 'article' in str(f).lower()]
            
            # Netherlands-specific EU AI Act compliance
            self.assertEqual(result.get('region'), 'Netherlands')
            
            # Validate performance
            self.assert_performance_within_limits(performance_data)
            
            print(f"✓ Test 2 PASSED: EU AI Act compliance analysis in {performance_data['execution_time']:.2f}s")
    
    def test_3_functional_bias_fairness_analysis(self):
        """Test 3: Functional - Bias and Fairness Assessment"""
        model_details = {
            "hub_url": "https://huggingface.co/example/model",
            "model_type": "classification"
        }
        
        sample_inputs = [
            "Analyze this resume for job suitability",
            "Evaluate loan application risk",
            "Assess medical diagnosis probability"
        ]
        
        # Mock bias analysis
        mock_bias_analysis = {
            "demographic_bias": True,
            "affected_groups": ["gender", "age", "ethnicity"],
            "fairness_metrics": {
                "equal_opportunity": 0.65,
                "demographic_parity": 0.70,
                "calibration": 0.80
            },
            "recommendations": [
                "Implement bias mitigation techniques",
                "Increase training data diversity",
                "Regular fairness auditing"
            ]
        }
        
        with patch.object(self.scanner, '_analyze_bias_fairness', return_value=mock_bias_analysis):
            performance_data = self.base_tester.measure_performance(
                self.scanner.scan_model,
                "Model Hub",
                model_details,
                ["Bias Detection", "Fairness Analysis"],
                ["Hiring", "Finance", "Healthcare"],
                sample_inputs
            )
            result = performance_data['result']
            
            # Validate structure
            self.assert_scan_structure(result)
            
            # Check bias analysis results
            bias_findings = [f for f in result.get('findings', []) 
                            if any(keyword in str(f).lower() for keyword in ['bias', 'fairness', 'demographic'])]
            self.assertGreater(len(bias_findings), 0, "Should detect bias issues")
            
            # Validate performance
            self.assert_performance_within_limits(performance_data)
            
            print(f"✓ Test 3 PASSED: Bias analysis with {len(bias_findings)} findings in {performance_data['execution_time']:.2f}s")
    
    def test_4_performance_large_model_analysis(self):
        """Test 4: Performance - Large Model Repository Scanning"""
        model_details = {
            "repo_url": "https://github.com/large-org/massive-model",
            "branch_name": "main"
        }
        
        # Mock large repository with many files
        mock_validation = {
            "valid": True,
            "findings": [
                {
                    "type": "PII Exposure",
                    "severity": "High",
                    "description": f"Training data file {i} contains email addresses",
                    "risk_level": "high"
                } for i in range(50)  # Simulate many findings
            ] + [
                {
                    "type": "Model Bias",
                    "severity": "Medium", 
                    "description": f"Bias detected in model component {i}",
                    "risk_level": "medium"
                } for i in range(30)  # More findings
            ]
        }
        
        with patch.object(self.scanner, '_validate_github_repo', return_value=mock_validation):
            performance_data = self.base_tester.measure_performance(
                self.scanner.scan_model,
                "Repository URL",
                model_details,
                ["All"],
                ["General"],
                []
            )
            result = performance_data['result']
            
            # Validate structure
            self.assert_scan_structure(result)
            
            # Performance requirements for large models
            self.assertLess(performance_data['execution_time'], 30.0,
                           "Large model analysis should complete within 30 seconds")
            self.assertLess(performance_data['memory_used'], 250.0,
                           "Memory usage should stay under 250MB for large models")
            
            # Check that many findings were processed
            self.assertGreater(len(result['findings']), 50, "Should process many findings efficiently")
            
            print(f"✓ Test 4 PASSED: Large model analysis ({len(result['findings'])} findings) in {performance_data['execution_time']:.2f}s")
    
    def test_5_performance_multiple_model_formats(self):
        """Test 5: Performance - Multiple AI Model Formats"""
        model_scenarios = [
            ("API Endpoint", {"api_endpoint": "https://api.openai.com/v1/models"}),
            ("Model Hub", {"hub_url": "https://huggingface.co/bert-base"}),
            ("Repository URL", {"repo_url": "https://github.com/pytorch/vision"}),
            ("Local Model", {"model_path": "/path/to/model.pkl"})
        ]
        
        total_scans = 0
        total_time = 0
        
        for source_type, details in model_scenarios:
            # Mock appropriate responses for each type
            if source_type == "Repository URL":
                mock_validation = {"valid": True, "findings": [
                    {"type": "Test", "severity": "Low", "description": "Test finding", "risk_level": "low"}
                ]}
                with patch.object(self.scanner, '_validate_github_repo', return_value=mock_validation):
                    performance_data = self.base_tester.measure_performance(
                        self.scanner.scan_model,
                        source_type,
                        details,
                        ["Basic Analysis"],
                        ["General"],
                        []
                    )
            else:
                performance_data = self.base_tester.measure_performance(
                    self.scanner.scan_model,
                    source_type,
                    details,
                    ["Basic Analysis"],
                    ["General"],
                    []
                )
            
            result = performance_data['result']
            
            # Validate each result
            self.assert_scan_structure(result)
            total_scans += 1
            total_time += performance_data['execution_time']
        
        # Performance validation
        avg_time_per_scan = total_time / total_scans
        self.assertLess(avg_time_per_scan, 8.0,
                       "Average scan time per model format should be under 8 seconds")
        
        print(f"✓ Test 5 PASSED: {total_scans} model formats scanned in {total_time:.2f}s (avg: {avg_time_per_scan:.2f}s)")
    
    def test_6_functional_netherlands_ai_governance(self):
        """Test 6: Functional - Netherlands AI Governance and Ethics"""
        model_details = {
            "repo_url": "https://github.com/dutch-org/ai-model",
            "branch_name": "main",
            "deployment_region": "Netherlands"
        }
        
        # Mock Netherlands-specific AI governance findings
        mock_validation = {
            "valid": True,
            "findings": [
                {
                    "type": "Dutch AI Ethics Violation",
                    "severity": "High",
                    "description": "AI system lacks transparency required by Dutch AI principles",
                    "risk_level": "high",
                    "regulation": "Netherlands AI Framework"
                },
                {
                    "type": "GDPR-AI Integration",
                    "severity": "Medium",
                    "description": "Automated decision-making requires explicit consent under UAVG",
                    "risk_level": "medium",
                    "regulation": "UAVG Article 22"
                },
                {
                    "type": "Algorithmic Transparency",
                    "severity": "High",
                    "description": "Public sector AI use requires algorithmic impact assessment",
                    "risk_level": "high",
                    "regulation": "Dutch Algorithm Register"
                }
            ]
        }
        
        with patch.object(self.scanner, '_validate_github_repo', return_value=mock_validation):
            performance_data = self.base_tester.measure_performance(
                self.scanner.scan_model,
                "Repository URL",
                model_details,
                ["Netherlands AI Governance"],
                ["Public Sector", "Automated Decision Making"],
                []
            )
            result = performance_data['result']
            
            # Validate structure
            self.assert_scan_structure(result)
            
            # Check Netherlands-specific compliance
            self.assertEqual(result.get('region'), 'Netherlands')
            
            # Check for Netherlands AI governance findings
            nl_ai_findings = [f for f in result.get('findings', []) 
                             if any(keyword in str(f).lower() for keyword in 
                                   ['dutch', 'netherlands', 'uavg', 'algorithm register'])]
            self.assertGreater(len(nl_ai_findings), 0, 
                              "Should detect Netherlands AI governance issues")
            
            # Validate performance
            self.assert_performance_within_limits(performance_data)
            
            print(f"✓ Test 6 PASSED: Netherlands AI governance analysis in {performance_data['execution_time']:.2f}s")

if __name__ == '__main__':
    unittest.main(verbosity=2)