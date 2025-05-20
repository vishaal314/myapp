"""
Test Suite for Netherlands GDPR (UAVG) Detection

This file contains unit and integration tests for the Netherlands-specific
GDPR detection functionality.
"""

import sys
import os
import unittest

# Add the project root to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.netherlands_gdpr import (
    detect_nl_violations,
    _find_bsn_numbers,
    _detect_minor_consent,
    _detect_medical_data,
    _is_valid_bsn,
    validate_nl_compliance
)


class TestNLBSNDetection(unittest.TestCase):
    """Tests for BSN (Dutch Citizen Service Number) detection"""
    
    def test_valid_bsn(self):
        """Test BSN validation logic with valid BSNs"""
        # These are valid BSNs that pass the "11 test"
        valid_bsns = ['123456782', '111222333']
        for bsn in valid_bsns:
            self.assertTrue(_is_valid_bsn(bsn), f"BSN {bsn} should be valid")
    
    def test_invalid_bsn(self):
        """Test BSN validation logic with invalid BSNs"""
        # These are invalid BSNs that fail the "11 test"
        invalid_bsns = ['123456789', '987654321']
        for bsn in invalid_bsns:
            self.assertFalse(_is_valid_bsn(bsn), f"BSN {bsn} should be invalid")
    
    def test_bsn_detection(self):
        """Test BSN detection in different contexts"""
        # Test with explicit BSN identification
        text_with_explicit_bsn = "Patient data: BSN: 123456782"
        findings = _find_bsn_numbers(text_with_explicit_bsn)
        self.assertTrue(findings, "Should detect BSN with explicit identifier")
        
        # Test with formatted BSN
        text_with_formatted_bsn = "Burgerservicenummer 123-456-782"
        findings = _find_bsn_numbers(text_with_formatted_bsn)
        self.assertTrue(findings, "Should detect formatted BSN")
        
        # Test with standalone valid BSN (should be detected, but validation matters)
        text_with_standalone_bsn = "The number 123456782 appears alone with no context"
        findings = _find_bsn_numbers(text_with_standalone_bsn)
        self.assertTrue(findings, "Should detect standalone valid BSN with validation")
        
        # Test with invalid BSN (should not be detected as it fails the "11 test")
        text_with_invalid_bsn = "The number 123456789 is not a valid BSN"
        findings = _find_bsn_numbers(text_with_invalid_bsn)
        self.assertFalse(findings, "Should not detect invalid BSN")


class TestNLMinorConsent(unittest.TestCase):
    """Tests for Dutch minor consent detection"""
    
    def test_minor_consent_detection(self):
        """Test detection of minor consent references"""
        # Test with Dutch minor consent terms
        text_with_dutch_minor = "Voor gebruikers jonger dan 16 jaar is ouderlijke toestemming vereist."
        findings = _detect_minor_consent(text_with_dutch_minor)
        self.assertTrue(findings, "Should detect Dutch minor consent references")
        
        # Test with English minor consent terms but Dutch age
        text_with_english_minor = "For users under 16 years, parental consent is required."
        findings = _detect_minor_consent(text_with_english_minor)
        self.assertTrue(findings, "Should detect English minor consent with Dutch age")
        
        # Test with no minor consent references
        text_without_minor = "All users must accept the terms and conditions."
        findings = _detect_minor_consent(text_without_minor)
        self.assertFalse(findings, "Should not detect minor consent in unrelated text")


class TestNLMedicalData(unittest.TestCase):
    """Tests for Dutch medical data detection"""
    
    def test_medical_data_detection(self):
        """Test detection of Dutch medical data references"""
        # Test with Dutch healthcare terms
        text_with_medical = "Het medisch dossier bevat vertrouwelijke patiëntgegevens."
        findings = _detect_medical_data(text_with_medical)
        self.assertTrue(findings, "Should detect Dutch medical data references")
        
        # Test with healthcare institution
        text_with_hospital = "UMC Utrecht is een academisch ziekenhuis."
        findings = _detect_medical_data(text_with_hospital)
        self.assertTrue(findings, "Should detect Dutch healthcare institution")
        
        # Test with no medical references
        text_without_medical = "Dit document bevat algemene bedrijfsinformatie."
        findings = _detect_medical_data(text_without_medical)
        self.assertFalse(findings, "Should not detect medical data in unrelated text")


class TestNLViolationsIntegration(unittest.TestCase):
    """Integration tests for the Netherlands violations detection"""
    
    def test_nl_violations_detection(self):
        """Test full Netherlands violations detection pipeline"""
        # Test with mixed Netherlands-specific issues
        test_text = """
        Dit document bevat gevoelige informatie.
        
        Patiëntgegevens:
        - Naam: Jan de Vries
        - BSN: 123456782
        - Geboortedatum: 12-05-1980
        
        Voor gebruikers jonger dan 16 jaar is ouderlijke toestemming vereist.
        """
        
        findings = detect_nl_violations(test_text)
        
        # Should detect BSN, medical data, and minor consent
        finding_types = [f.get('type') for f in findings]
        
        self.assertIn('BSN', finding_types, "Should detect BSN")
        self.assertIn('MEDICAL_DATA', finding_types, "Should detect medical data")
        self.assertIn('MINOR_CONSENT', finding_types, "Should detect minor consent")
        
        # Test compliance validation
        compliance = validate_nl_compliance(findings)
        self.assertTrue(compliance['issues_found'], "Should identify compliance issues")
        self.assertTrue(compliance['recommendations'], "Should generate recommendations")


class TestMixedEuropeanData(unittest.TestCase):
    """Edge case tests with mixed European data"""
    
    def test_mixed_language_detection(self):
        """Test detection with mixed European languages"""
        # Test with mixed Dutch, German, and English content
        mixed_text = """
        Patient information:
        - BSN: 123456782 (Netherlands)
        - Versicherungsnummer: DE123456789 (Germany)
        - Numéro de sécurité sociale: 187090100100141 (France)
        
        Medical data includes diagnostische Informationen and medisch dossier.
        
        For users under 16 years in the Netherlands, parental consent is required.
        """
        
        findings = detect_nl_violations(mixed_text)
        
        # Should only detect Netherlands-specific issues (BSN, medical, consent)
        nl_finding_types = [f.get('type') for f in findings]
        
        self.assertIn('BSN', nl_finding_types, "Should detect Dutch BSN")
        self.assertTrue(any(t == 'MEDICAL_DATA' for t in nl_finding_types), 
                       "Should detect medical data with Dutch terms")
        self.assertIn('MINOR_CONSENT', nl_finding_types, "Should detect Dutch minor consent age")


if __name__ == '__main__':
    # Run all tests
    unittest.main()