"""
Unit tests for GDPR risk categorization functionality

These tests verify the correctness of risk level mapping, scoring,
and aggregation functions.
"""

import unittest
from services.gdpr_risk_categories import (
    RiskLevel, SeverityLevel, RemediationPriority,
    map_severity_to_risk_level, map_severity_to_priority,
    validate_risk_level, calculate_compliance_score,
    determine_compliance_status, normalize_risk_counts,
    merge_risk_counts
)

class TestRiskCategorization(unittest.TestCase):
    """Test suite for GDPR risk categorization functionality"""
    
    def test_map_severity_to_risk_level(self):
        """Test mapping severity levels to risk levels"""
        # Test all standard severity levels
        self.assertEqual(map_severity_to_risk_level("high"), RiskLevel.HIGH.value)
        self.assertEqual(map_severity_to_risk_level("medium"), RiskLevel.MEDIUM.value)
        self.assertEqual(map_severity_to_risk_level("low"), RiskLevel.LOW.value)
        self.assertEqual(map_severity_to_risk_level("none"), RiskLevel.NONE.value)
        
        # Test case insensitivity
        self.assertEqual(map_severity_to_risk_level("HIGH"), RiskLevel.HIGH.value)
        self.assertEqual(map_severity_to_risk_level("Medium"), RiskLevel.MEDIUM.value)
        
        # Test default for unknown severity
        self.assertEqual(map_severity_to_risk_level("unknown"), RiskLevel.MEDIUM.value)
    
    def test_map_severity_to_priority(self):
        """Test mapping severity levels to remediation priorities"""
        # Test all standard severity levels
        self.assertEqual(map_severity_to_priority("high"), RemediationPriority.HIGH.value)
        self.assertEqual(map_severity_to_priority("medium"), RemediationPriority.MEDIUM.value)
        self.assertEqual(map_severity_to_priority("low"), RemediationPriority.LOW.value)
        self.assertEqual(map_severity_to_priority("none"), RemediationPriority.NONE.value)
        
        # Test case insensitivity
        self.assertEqual(map_severity_to_priority("HIGH"), RemediationPriority.HIGH.value)
        self.assertEqual(map_severity_to_priority("Medium"), RemediationPriority.MEDIUM.value)
        
        # Test default for unknown severity
        self.assertEqual(map_severity_to_priority("unknown"), RemediationPriority.MEDIUM.value)
    
    def test_validate_risk_level(self):
        """Test validation of risk level strings"""
        # Test valid risk levels
        self.assertEqual(validate_risk_level("High"), RiskLevel.HIGH.value)
        self.assertEqual(validate_risk_level("Medium"), RiskLevel.MEDIUM.value)
        self.assertEqual(validate_risk_level("Low"), RiskLevel.LOW.value)
        self.assertEqual(validate_risk_level("None"), RiskLevel.NONE.value)
        
        # Test case normalization
        self.assertEqual(validate_risk_level("high"), RiskLevel.HIGH.value)
        self.assertEqual(validate_risk_level("HIGH"), RiskLevel.HIGH.value)
        self.assertEqual(validate_risk_level("  Low  "), RiskLevel.LOW.value)
        
        # Test invalid risk levels
        with self.assertRaises(ValueError):
            validate_risk_level("Critical")
        with self.assertRaises(ValueError):
            validate_risk_level("Warning")
        with self.assertRaises(ValueError):
            validate_risk_level("")
    
    def test_calculate_compliance_score(self):
        """Test calculation of compliance score based on risk counts"""
        # Test with no findings
        self.assertEqual(calculate_compliance_score({}), 100)
        self.assertEqual(calculate_compliance_score({"High": 0, "Medium": 0, "Low": 0}), 100)
        
        # Test with single risk level
        self.assertEqual(calculate_compliance_score({"High": 1, "Medium": 0, "Low": 0}), 95)
        self.assertEqual(calculate_compliance_score({"High": 0, "Medium": 1, "Low": 0}), 97)
        self.assertEqual(calculate_compliance_score({"High": 0, "Medium": 0, "Low": 1}), 99)
        
        # Test with multiple risk levels
        self.assertEqual(calculate_compliance_score({"High": 1, "Medium": 1, "Low": 1}), 92)
        self.assertEqual(calculate_compliance_score({"High": 2, "Medium": 3, "Low": 5}), 80)
        
        # Test with maximum point threshold (should cap at 0)
        self.assertEqual(calculate_compliance_score({"High": 50, "Medium": 0, "Low": 0}), 0)
    
    def test_determine_compliance_status(self):
        """Test determination of compliance status based on score"""
        # Test different score ranges
        self.assertEqual(determine_compliance_status(95), "Compliant")
        self.assertEqual(determine_compliance_status(90), "Compliant")
        self.assertEqual(determine_compliance_status(89), "Largely Compliant")
        self.assertEqual(determine_compliance_status(75), "Largely Compliant")
        self.assertEqual(determine_compliance_status(70), "Largely Compliant")
        self.assertEqual(determine_compliance_status(69), "Needs Improvement")
        self.assertEqual(determine_compliance_status(55), "Needs Improvement")
        self.assertEqual(determine_compliance_status(50), "Needs Improvement")
        self.assertEqual(determine_compliance_status(49), "Non-Compliant")
        self.assertEqual(determine_compliance_status(25), "Non-Compliant")
        self.assertEqual(determine_compliance_status(0), "Non-Compliant")
    
    def test_normalize_risk_counts(self):
        """Test normalization of risk counts"""
        # Test with empty dictionary
        self.assertEqual(
            normalize_risk_counts({}),
            {RiskLevel.HIGH.value: 0, RiskLevel.MEDIUM.value: 0, RiskLevel.LOW.value: 0}
        )
        
        # Test with partial dictionary
        self.assertEqual(
            normalize_risk_counts({"High": 5}),
            {RiskLevel.HIGH.value: 5, RiskLevel.MEDIUM.value: 0, RiskLevel.LOW.value: 0}
        )
        
        # Test with complete dictionary
        self.assertEqual(
            normalize_risk_counts({"High": 1, "Medium": 2, "Low": 3}),
            {RiskLevel.HIGH.value: 1, RiskLevel.MEDIUM.value: 2, RiskLevel.LOW.value: 3}
        )
        
        # Test with extra entries
        self.assertEqual(
            normalize_risk_counts({"High": 1, "Medium": 2, "Low": 3, "Critical": 4}),
            {RiskLevel.HIGH.value: 1, RiskLevel.MEDIUM.value: 2, RiskLevel.LOW.value: 3}
        )
    
    def test_merge_risk_counts(self):
        """Test merging of risk counts from multiple sources"""
        # Test with empty dictionaries
        self.assertEqual(
            merge_risk_counts({}, {}),
            {RiskLevel.HIGH.value: 0, RiskLevel.MEDIUM.value: 0, RiskLevel.LOW.value: 0}
        )
        
        # Test with one-sided dictionaries
        self.assertEqual(
            merge_risk_counts({"High": 5, "Medium": 3, "Low": 1}, {}),
            {RiskLevel.HIGH.value: 5, RiskLevel.MEDIUM.value: 3, RiskLevel.LOW.value: 1}
        )
        self.assertEqual(
            merge_risk_counts({}, {"High": 2, "Medium": 4, "Low": 6}),
            {RiskLevel.HIGH.value: 2, RiskLevel.MEDIUM.value: 4, RiskLevel.LOW.value: 6}
        )
        
        # Test with partial dictionaries
        self.assertEqual(
            merge_risk_counts({"High": 5}, {"Medium": 4}),
            {RiskLevel.HIGH.value: 5, RiskLevel.MEDIUM.value: 4, RiskLevel.LOW.value: 0}
        )
        
        # Test with overlapping dictionaries
        self.assertEqual(
            merge_risk_counts({"High": 1, "Medium": 2, "Low": 3}, {"High": 4, "Medium": 5, "Low": 6}),
            {RiskLevel.HIGH.value: 5, RiskLevel.MEDIUM.value: 7, RiskLevel.LOW.value: 9}
        )
        
        # Test with extra entries
        self.assertEqual(
            merge_risk_counts({"High": 1, "Critical": 10}, {"Medium": 2, "Warning": 20}),
            {RiskLevel.HIGH.value: 1, RiskLevel.MEDIUM.value: 2, RiskLevel.LOW.value: 0}
        )

if __name__ == "__main__":
    unittest.main()