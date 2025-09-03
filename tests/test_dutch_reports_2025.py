#!/usr/bin/env python3
"""
Unit Tests for Dutch Language Reports - 2025 EU AI Act Timeline
Tests HTML reports display correctly in Dutch with updated enforcement dates
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.eu_ai_act_html_reporter import generate_eu_ai_act_html_report
from translations.translation_manager import get_translator

class TestDutchReports2025(unittest.TestCase):
    """Test suite for Dutch language reports with 2025 timeline"""

    def setUp(self):
        """Set up test environment with Dutch language"""
        self.mock_scan_results = {
            'scan_id': 'test-scan-2025',
            'ai_system_name': 'Test AI Model',
            'findings': [
                {
                    'type': 'AI_ACT_GPAI_COMPLIANCE',
                    'category': 'GPAI Model Requirements',
                    'severity': 'High',
                    'title': 'GPAI Model Compliance Assessment Required',
                    'penalty_risk': 'Up to €15M or 3% global turnover',
                    'compliance_deadline': 'August 2, 2025 (Effective)'
                }
            ],
            'compliance_score': 75,
            'region': 'Netherlands'
        }

    def test_dutch_regulatory_status_text(self):
        """Test Dutch regulatory status contains 2025 timeline"""
        # Test Dutch translator initialization
        dutch_translator = get_translator('nl')
        self.assertIsNotNone(dutch_translator, "Dutch translator should be available")
        
        # Generate Dutch report
        with patch('streamlit.session_state', {'language': 'nl'}):
            html_report = generate_eu_ai_act_html_report(
                self.mock_scan_results,
                language='nl'
            )
        
        # Verify Dutch regulatory status contains 2025 timeline
        self.assertIn('Verboden praktijken: Gehandhaafd sinds 2 februari 2025', html_report)
        self.assertIn('GPAI modelregels: Gehandhaafd sinds 2 augustus 2025', html_report)
        self.assertIn('Hoog-risico systemen: Volledige handhaving tegen 2 augustus 2027', html_report)
        self.assertIn('Maximale boetes: €35M of 7% mondiale omzet', html_report)

    def test_dutch_penalty_structure_display(self):
        """Test Dutch penalty structure displays correctly"""
        with patch('streamlit.session_state', {'language': 'nl'}):
            html_report = generate_eu_ai_act_html_report(
                self.mock_scan_results,
                language='nl'
            )
        
        # Verify penalty structure in Dutch
        self.assertIn('€35M', html_report, "Should display €35M penalty")
        self.assertIn('€15M', html_report, "Should display €15M penalty for GPAI")
        self.assertIn('mondiale omzet', html_report, "Should use Dutch term for global turnover")

    def test_dutch_enforcement_authority_reference(self):
        """Test Dutch enforcement authority is referenced correctly"""
        with patch('streamlit.session_state', {'language': 'nl'}):
            html_report = generate_eu_ai_act_html_report(
                self.mock_scan_results,
                language='nl'
            )
        
        # Should reference Dutch/EU enforcement authorities in Dutch
        self.assertIn('Nationale toezichthoudende autoriteiten', html_report)

    def test_dutch_gpai_terminology(self):
        """Test GPAI terminology appears correctly in Dutch"""
        gpai_findings = [{
            'type': 'AI_ACT_GPAI_COMPLIANCE',
            'category': 'GPAI Model Requirements',
            'title': 'GPAI Model Compliance Assessment Required'
        }]
        
        scan_results_with_gpai = {
            **self.mock_scan_results,
            'findings': gpai_findings
        }
        
        with patch('streamlit.session_state', {'language': 'nl'}):
            html_report = generate_eu_ai_act_html_report(
                scan_results_with_gpai,
                language='nl'
            )
        
        # GPAI should be handled correctly in Dutch context
        self.assertIn('GPAI', html_report, "GPAI acronym should appear in Dutch report")

    def test_dutch_compliance_score_display(self):
        """Test compliance score displays correctly in Dutch"""
        with patch('streamlit.session_state', {'language': 'nl'}):
            html_report = generate_eu_ai_act_html_report(
                self.mock_scan_results,
                language='nl'
            )
        
        # Should display compliance score
        self.assertIn('75', html_report, "Should display compliance score")

    def test_dutch_certificate_seal_language(self):
        """Test certificate seal uses correct Dutch language"""
        with patch('streamlit.session_state', {'language': 'nl'}):
            html_report = generate_eu_ai_act_html_report(
                self.mock_scan_results,
                language='nl'
            )
        
        # Certificate seal should indicate 2025 compliance
        self.assertIn('AI ACT 2025', html_report, "Should show AI ACT 2025 certification")

    def test_dutch_timestamp_format(self):
        """Test timestamp formatting in Dutch reports"""
        with patch('streamlit.session_state', {'language': 'nl'}):
            html_report = generate_eu_ai_act_html_report(
                self.mock_scan_results,
                language='nl'
            )
        
        # Should contain timestamp
        self.assertIn('2025', html_report, "Should contain current year in timestamp")

    def test_dutch_article_references(self):
        """Test article references appear correctly in Dutch"""
        findings_with_articles = [{
            'type': 'AI_ACT_GPAI_COMPLIANCE',
            'article_reference': 'EU AI Act Articles 51-55 (GPAI Models)',
            'category': 'GPAI Model Requirements'
        }]
        
        scan_results_with_articles = {
            **self.mock_scan_results,
            'findings': findings_with_articles
        }
        
        with patch('streamlit.session_state', {'language': 'nl'}):
            html_report = generate_eu_ai_act_html_report(
                scan_results_with_articles,
                language='nl'
            )
        
        # Article references should appear
        self.assertIn('Articles 51-55', html_report, "Should contain article references")

    def test_dutch_report_structure_completeness(self):
        """Test Dutch report contains all required sections"""
        with patch('streamlit.session_state', {'language': 'nl'}):
            html_report = generate_eu_ai_act_html_report(
                self.mock_scan_results,
                language='nl'
            )
        
        # Key sections should be present
        required_sections = [
            '<html',  # Valid HTML structure
            '<head',  # Header section
            '<title', # Title
            '<body',  # Body content
            'EU AI Act', # Main heading content
            '2025',   # Timeline reference
            '</html>' # Proper closure
        ]
        
        for section in required_sections:
            self.assertIn(section, html_report, f"Dutch report should contain {section}")

    def test_dutch_error_handling(self):
        """Test Dutch report generation handles errors gracefully"""
        # Test with minimal/malformed data
        minimal_data = {
            'scan_id': 'minimal-test',
            'findings': []
        }
        
        try:
            with patch('streamlit.session_state', {'language': 'nl'}):
                html_report = generate_eu_ai_act_html_report(
                    minimal_data,
                    language='nl'
                )
            # Should generate report even with minimal data
            self.assertIsInstance(html_report, str)
            self.assertGreater(len(html_report), 0)
        except Exception as e:
            self.fail(f"Dutch report generation should handle minimal data gracefully: {e}")

if __name__ == '__main__':
    unittest.main()