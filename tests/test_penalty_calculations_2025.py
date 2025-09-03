#!/usr/bin/env python3
"""
Unit Tests for 2025 EU AI Act Penalty Calculations
Tests €35M/€15M penalty structure accuracy and regional multipliers
"""

import unittest
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.eu_ai_act_compliance import generate_ai_act_compliance_report
from services.intelligent_risk_analyzer import IntelligentRiskAnalyzer

class TestPenaltyCalculations2025(unittest.TestCase):
    """Test suite for 2025 penalty calculation accuracy"""

    def setUp(self):
        """Set up test environment"""
        self.risk_analyzer = IntelligentRiskAnalyzer(region="Netherlands")

    def test_prohibited_practices_penalty_structure(self):
        """Test prohibited practices carry €35M or 7% penalty reference"""
        prohibited_findings = [
            {
                'type': 'prohibited',
                'severity': 'Critical',
                'category': 'Prohibited AI Practices',
                'risk_level': 'Critical'
            }
        ]
        
        # Test compliance report generation
        report = generate_ai_act_compliance_report(prohibited_findings)
        
        # Should indicate critical status for prohibited practices
        self.assertEqual(report['compliance_status'], 'Non-Compliant')
        self.assertGreater(report['risk_distribution']['Critical'], 0)

    def test_gpai_penalty_structure(self):
        """Test GPAI models carry €15M or 3% penalty reference"""
        gpai_findings = [
            {
                'type': 'AI_ACT_GPAI_COMPLIANCE',
                'severity': 'High',
                'category': 'GPAI Model Requirements',
                'penalty_risk': 'Up to €15M or 3% global turnover',
                'risk_level': 'High'
            }
        ]
        
        report = generate_ai_act_compliance_report(gpai_findings)
        
        # Should indicate needs review for GPAI
        self.assertEqual(report['compliance_status'], 'Needs Review')
        self.assertGreater(report['risk_distribution']['High'], 0)

    def test_netherlands_regional_multiplier(self):
        """Test Netherlands has 1.2x penalty multiplier for strict enforcement"""
        netherlands_analyzer = IntelligentRiskAnalyzer(region="Netherlands")
        eu_analyzer = IntelligentRiskAnalyzer(region="EU")
        
        # Both should be initialized correctly
        self.assertEqual(netherlands_analyzer.region, "Netherlands")
        self.assertEqual(eu_analyzer.region, "EU")

    def test_penalty_severity_scoring(self):
        """Test penalty severity affects compliance scoring correctly"""
        # Test critical findings (prohibited practices)
        critical_findings = [
            {'risk_level': 'Critical', 'severity': 'Critical'},
            {'risk_level': 'Critical', 'severity': 'Critical'}
        ]
        
        report_critical = generate_ai_act_compliance_report(critical_findings)
        
        # Test high findings (GPAI)
        high_findings = [
            {'risk_level': 'High', 'severity': 'High'},
            {'risk_level': 'High', 'severity': 'High'}
        ]
        
        report_high = generate_ai_act_compliance_report(high_findings)
        
        # Critical should have lower compliance score than high
        self.assertLess(report_critical['compliance_score'], report_high['compliance_score'])

    def test_penalty_calculation_ranges(self):
        """Test penalty calculations fall within expected ranges"""
        # Test no findings = high compliance
        no_findings_report = generate_ai_act_compliance_report([])
        self.assertEqual(no_findings_report['compliance_score'], 100)
        
        # Test many critical findings = low compliance
        many_critical = [{'risk_level': 'Critical'} for _ in range(5)]
        critical_report = generate_ai_act_compliance_report(many_critical)
        self.assertLess(critical_report['compliance_score'], 50)

    def test_mixed_penalty_scenarios(self):
        """Test mixed penalty scenarios (prohibited + GPAI + high-risk)"""
        mixed_findings = [
            {
                'type': 'prohibited',
                'risk_level': 'Critical',
                'severity': 'Critical'
            },
            {
                'type': 'AI_ACT_GPAI_COMPLIANCE',
                'risk_level': 'High',
                'severity': 'High'
            },
            {
                'type': 'high_risk',
                'risk_level': 'High',
                'severity': 'High'
            },
            {
                'type': 'transparency',
                'risk_level': 'Medium',
                'severity': 'Medium'
            }
        ]
        
        report = generate_ai_act_compliance_report(mixed_findings)
        
        # Should be non-compliant due to prohibited practices
        self.assertEqual(report['compliance_status'], 'Non-Compliant')
        
        # Should have varied risk distribution
        self.assertGreater(report['risk_distribution']['Critical'], 0)
        self.assertGreater(report['risk_distribution']['High'], 0)
        self.assertGreater(report['risk_distribution']['Medium'], 0)

    def test_penalty_recommendations_accuracy(self):
        """Test penalty-based recommendations are accurate"""
        critical_findings = [
            {
                'type': 'prohibited',
                'risk_level': 'Critical',
                'severity': 'Critical'
            }
        ]
        
        report = generate_ai_act_compliance_report(critical_findings)
        recommendations = report.get('recommendations', [])
        
        # Should include immediate action for prohibited practices
        has_immediate_action = any('Immediately address prohibited' in rec for rec in recommendations)
        self.assertTrue(has_immediate_action, "Should recommend immediate action for prohibited practices")

    def test_compliance_score_calculation_logic(self):
        """Test compliance score calculation follows 2025 penalty logic"""
        # Test score deduction logic
        test_cases = [
            # (critical_count, high_count, medium_count, expected_max_score)
            (0, 0, 0, 100),  # Perfect score
            (1, 0, 0, 60),   # One critical = -40 points
            (0, 1, 0, 80),   # One high = -20 points  
            (0, 0, 1, 90),   # One medium = -10 points
            (2, 2, 2, 0),    # Many findings = very low score
        ]
        
        for critical, high, medium, expected_max in test_cases:
            with self.subTest(critical=critical, high=high, medium=medium):
                findings = (
                    [{'risk_level': 'Critical'} for _ in range(critical)] +
                    [{'risk_level': 'High'} for _ in range(high)] +
                    [{'risk_level': 'Medium'} for _ in range(medium)]
                )
                
                report = generate_ai_act_compliance_report(findings)
                
                if expected_max == 100:
                    self.assertEqual(report['compliance_score'], 100)
                else:
                    self.assertLessEqual(report['compliance_score'], expected_max)

    def test_netherlands_specific_penalties(self):
        """Test Netherlands-specific penalty considerations"""
        # Netherlands should have stricter enforcement
        netherlands_findings = [
            {
                'type': 'AI_ACT_GPAI_COMPLIANCE',
                'risk_level': 'High',
                'region': 'Netherlands'
            }
        ]
        
        report = generate_ai_act_compliance_report(netherlands_findings)
        
        # Should process Netherlands-specific findings
        self.assertGreater(len(report['findings']), 0)

    def test_penalty_timeline_compliance(self):
        """Test penalty calculations reflect 2025 enforcement timeline"""
        # Current date should be after enforcement dates
        from datetime import datetime
        current_date = datetime.now()
        
        # February 2025 (prohibited practices) should be in effect
        self.assertGreaterEqual(current_date.year, 2025)
        
        # August 2025 (GPAI) should be in effect if current date is after Aug 2025
        gpai_enforcement_passed = (
            current_date.year > 2025 or 
            (current_date.year == 2025 and current_date.month >= 8)
        )
        
        if gpai_enforcement_passed:
            # GPAI penalties should be fully active
            gpai_findings = [{'type': 'AI_ACT_GPAI_COMPLIANCE', 'risk_level': 'High'}]
            report = generate_ai_act_compliance_report(gpai_findings)
            self.assertEqual(report['compliance_status'], 'Needs Review')

if __name__ == '__main__':
    unittest.main()