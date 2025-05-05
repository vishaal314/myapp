"""
Integration tests for GDPR scanning and risk categorization

These tests verify the correct integration between the enhanced scanner,
risk categorization system, and result formatting.
"""

import unittest
import os
import tempfile
from services.enhanced_gdpr_repo_scanner import GDPRArticleScanner, scan_repository_for_gdpr_compliance
from services.advanced_repo_scan_connector import run_enhanced_gdpr_scan, _format_enhanced_results
from services.repo_scanner_integration import enhance_repo_scan_results, _merge_scan_results
from services.gdpr_risk_categories import RiskLevel, SeverityLevel

class TestGDPRIntegration(unittest.TestCase):
    """Integration test suite for GDPR scanning and risk categorization"""
    
    def setUp(self):
        """Set up test environment with sample repository"""
        # Create a temporary directory for test repository
        self.repo_dir = tempfile.mkdtemp()
        
        # Create sample files with various GDPR issues
        self._create_test_files()
    
    def tearDown(self):
        """Clean up test environment"""
        self._cleanup_repo_dir()
    
    def _create_test_files(self):
        """Create test files with known GDPR issues"""
        # File with high risk issue
        high_risk_file = os.path.join(self.repo_dir, "high_risk.py")
        with open(high_risk_file, "w") as f:
            f.write("""
            # This file contains a high risk issue (hardcoded API key)
            
            def authenticate():
                api_key = "sk_test_1234567890abcdef"
                return api_key
            """)
        
        # File with medium risk issue
        medium_risk_file = os.path.join(self.repo_dir, "medium_risk.py")
        with open(medium_risk_file, "w") as f:
            f.write("""
            # This file contains a medium risk issue (data storage without retention)
            
            class User:
                def save(self):
                    # Save user data without retention period
                    db.save(self)
            """)
        
        # File with low risk issue
        low_risk_file = os.path.join(self.repo_dir, "low_risk.py")
        with open(low_risk_file, "w") as f:
            f.write("""
            # This file contains a low risk issue (privacy policy display)
            
            def show_privacy_policy():
                privacy_policy.display()
            """)
    
    def _cleanup_repo_dir(self):
        """Clean up the test repository directory"""
        for root, dirs, files in os.walk(self.repo_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        
        os.rmdir(self.repo_dir)
    
    def test_scanner_risk_categorization(self):
        """Test that scanner correctly categorizes risks"""
        # Run scanner on test repository
        scanner = GDPRArticleScanner(self.repo_dir)
        results = scanner.scan_repository()
        
        # Check that findings were found
        self.assertIn("findings", results)
        self.assertIn("statistics", results)
        
        # Check risk categorization in statistics
        statistics = results["statistics"]
        self.assertIn("severity_counts", statistics)
        
        severity_counts = statistics["severity_counts"]
        self.assertGreaterEqual(severity_counts.get(SeverityLevel.HIGH.value, 0), 1)
        self.assertGreaterEqual(severity_counts.get(SeverityLevel.MEDIUM.value, 0), 1)
        self.assertGreaterEqual(severity_counts.get(SeverityLevel.LOW.value, 0), 1)
        
        # Check compliance score calculation
        self.assertIn("compliance_score", statistics)
        self.assertLess(statistics["compliance_score"], 100)  # Should be less than 100 due to findings
        
        # Check compliance status
        self.assertIn("compliance_status", statistics)
        self.assertIn(statistics["compliance_status"], 
                     ["Compliant", "Largely Compliant", "Needs Improvement", "Non-Compliant"])
    
    def test_connector_formatting(self):
        """Test that connector correctly formats scanner results"""
        # Get scanner results
        scanner_results = scan_repository_for_gdpr_compliance(self.repo_dir)
        
        # Format the results
        formatted_results = _format_enhanced_results(scanner_results)
        
        # Check key result sections
        self.assertIn("findings", formatted_results)
        self.assertIn("statistics", formatted_results)
        self.assertIn("risk_summary", formatted_results)
        self.assertIn("gdpr_compliance", formatted_results)
        
        # Check risk summary structure
        risk_summary = formatted_results["risk_summary"]
        self.assertIn(RiskLevel.HIGH.value, risk_summary)
        self.assertIn(RiskLevel.MEDIUM.value, risk_summary)
        self.assertIn(RiskLevel.LOW.value, risk_summary)
        
        # Check gdpr_compliance structure
        gdpr_compliance = formatted_results["gdpr_compliance"]
        self.assertIn("compliance_score", gdpr_compliance)
        self.assertIn("compliance_status", gdpr_compliance)
        self.assertIn("risk_breakdown", gdpr_compliance)
        self.assertIn("remediation_priorities", gdpr_compliance)
        
        # Check risk breakdown structure
        risk_breakdown = gdpr_compliance["risk_breakdown"]
        for category in ["pii", "dsar", "consent", "security", "principle", "nl_uavg", "other"]:
            self.assertIn(category, risk_breakdown)
            self.assertIsInstance(risk_breakdown[category], float)
        
        # Check remediation priorities structure
        remediation_priorities = gdpr_compliance["remediation_priorities"]
        self.assertIn("high", remediation_priorities)
        self.assertIn("medium", remediation_priorities)
        self.assertIn("low", remediation_priorities)
    
    def test_result_merging(self):
        """Test that scan results are correctly merged"""
        # Create two sample scan results
        original_results = {
            "findings": [{"id": 1, "risk_level": "High", "type": "security"}],
            "risk_summary": {"High": 1, "Medium": 0, "Low": 0},
            "gdpr_compliance": {
                "compliance_score": 80,
                "compliance_status": "Largely Compliant",
                "risk_breakdown": {"security": 5.0, "principle": 0.0},
                "remediation_priorities": {"high": 1, "medium": 0, "low": 0}
            },
            "statistics": {
                "total_files_scanned": 10,
                "total_findings": 1,
                "scan_duration": 1.5
            }
        }
        
        enhanced_results = {
            "findings": [{"id": 2, "risk_level": "Medium", "type": "principle"}],
            "risk_summary": {"High": 0, "Medium": 1, "Low": 0},
            "gdpr_compliance": {
                "compliance_score": 90,
                "compliance_status": "Compliant",
                "risk_breakdown": {"security": 0.0, "principle": 3.0},
                "remediation_priorities": {"high": 0, "medium": 1, "low": 0}
            },
            "statistics": {
                "total_files_scanned": 10,
                "total_findings": 1,
                "scan_duration": 0.5
            }
        }
        
        # Merge the results
        merged_results = _merge_scan_results(original_results, enhanced_results)
        
        # Check merged findings
        self.assertEqual(len(merged_results["findings"]), 2)
        
        # Check merged risk summary
        self.assertEqual(merged_results["risk_summary"]["High"], 1)
        self.assertEqual(merged_results["risk_summary"]["Medium"], 1)
        self.assertEqual(merged_results["risk_summary"]["Low"], 0)
        
        # Check merged compliance information
        gdpr_compliance = merged_results["gdpr_compliance"]
        
        # Compliance score should be weighted average (70/30)
        expected_score = int(80 * 0.7 + 90 * 0.3)
        self.assertEqual(gdpr_compliance["compliance_score"], expected_score)
        
        # Check merged risk breakdown
        risk_breakdown = gdpr_compliance["risk_breakdown"]
        self.assertEqual(risk_breakdown["security"], 5.0)
        self.assertEqual(risk_breakdown["principle"], 3.0)
        
        # Check merged remediation priorities
        remediation_priorities = gdpr_compliance["remediation_priorities"]
        self.assertEqual(remediation_priorities["high"], 1)
        self.assertEqual(remediation_priorities["medium"], 1)
        self.assertEqual(remediation_priorities["low"], 0)
        
        # Check merged statistics
        statistics = merged_results["statistics"]
        self.assertEqual(statistics["total_files_scanned"], 10)  # Max of the two
        self.assertEqual(statistics["total_findings"], 2)  # Sum of the two
        self.assertEqual(statistics["scan_duration"], 2.0)  # Sum of the two
    
    def test_end_to_end_workflow(self):
        """Test the end-to-end scanning workflow"""
        # Create a simple original scan result
        original_scan_result = {
            "findings": [{"id": 1, "type": "privacy", "risk_level": "Medium"}],
            "risk_summary": {"High": 0, "Medium": 1, "Low": 0},
            "gdpr_compliance": {
                "compliance_score": 85,
                "compliance_status": "Largely Compliant",
                "risk_breakdown": {"privacy": 3.0},
                "remediation_priorities": {"high": 0, "medium": 1, "low": 0}
            },
            "statistics": {
                "total_files_scanned": 5,
                "total_findings": 1
            }
        }
        
        # Enhance the scan results with our scanner
        enhanced_results = enhance_repo_scan_results(original_scan_result, self.repo_dir)
        
        # Check that enhanced results contain original findings plus new ones
        self.assertGreater(len(enhanced_results["findings"]), 1)
        
        # Check that risk levels are correctly merged
        self.assertIn("risk_summary", enhanced_results)
        
        # Check that compliance information is merged
        self.assertIn("gdpr_compliance", enhanced_results)
        gdpr_compliance = enhanced_results["gdpr_compliance"]
        self.assertIn("compliance_score", gdpr_compliance)
        self.assertIn("compliance_status", gdpr_compliance)
        self.assertIn("risk_breakdown", gdpr_compliance)
        
        # Verify that the compliance score is reasonable
        self.assertGreaterEqual(gdpr_compliance["compliance_score"], 0)
        self.assertLessEqual(gdpr_compliance["compliance_score"], 100)
        
        # Verify that statistics are present
        self.assertIn("statistics", enhanced_results)
        statistics = enhanced_results["statistics"]
        self.assertIn("total_files_scanned", statistics)
        self.assertIn("total_findings", statistics)

if __name__ == "__main__":
    unittest.main()