"""
Netherlands GDPR (UAVG) Compliance Module

This module provides specialized detection for Netherlands-specific GDPR requirements
under the Dutch UAVG implementation without modifying existing scanner logic.
"""

import re
from typing import Dict, List, Any, Optional


def detect_nl_violations(content: str) -> List[Dict[str, Any]]:
    """
    Detect Netherlands-specific GDPR violations in content.
    This is a non-intrusive addition to existing scanners.
    
    Args:
        content: The text content to scan
        
    Returns:
        List of Netherlands-specific findings
    """
    findings = []
    
    # Add BSN detection
    findings.extend(_find_bsn_numbers(content))
    
    # Add minor consent detection
    findings.extend(_detect_minor_consent(content))
    
    # Add medical data detection
    findings.extend(_detect_medical_data(content))
    
    return findings


def _find_bsn_numbers(text: str) -> List[Dict[str, Any]]:
    """
    Find Dutch BSN numbers with improved context awareness.
    Looks for BSN numbers and validates them with the official "11 test".
    """
    # More specific BSN context patterns
    bsn_contexts = [
        r'\b(?:BSN|Burgerservicenummer|sofi[-\s]?nummer)(?:[:\s-]+)?(\d{9})\b',
        r'\b(?:BSN|Burgerservicenummer|sofi[-\s]?nummer)(?:[:\s-]+)?(\d{3}[-\s]\d{3}[-\s]\d{3})\b',
        # More generalized 9-digit pattern but with higher validation requirements
        r'\b(\d{9})\b'
    ]
    
    found = []
    
    for pattern in bsn_contexts:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            bsn = match.group(1) if match.lastindex else match.group(0)
            # Remove non-digits
            bsn = re.sub(r'\D', '', bsn)
            
            # Apply the "11 test" validation
            if _is_valid_bsn(bsn):
                # Determine context - higher risk when near identifying markers
                context_text = text[max(0, match.start()-50):min(len(text), match.end()+50)]
                is_high_risk = any(term in context_text.lower() for term in 
                              ['patient', 'klant', 'persoons', 'burger', 'client'])
                
                found.append({
                    'type': 'BSN',
                    'value': bsn,
                    'risk_level': 'High' if is_high_risk else 'Medium',
                    'gdpr_principle': 'netherlands_specific',
                    'description': 'Dutch Citizen Service Number (BSN) detected - special handling required under UAVG'
                })
    
    return found


def _is_valid_bsn(bsn: str) -> bool:
    """Check if a number passes the BSN validation ("11 test")."""
    if not bsn.isdigit() or len(bsn) != 9:
        return False
    
    # Apply the "11 test" for BSN
    total = 0
    for i in range(9):
        if i == 8:
            total -= int(bsn[i]) * i
        else:
            total += int(bsn[i]) * (9 - i)
    
    return total % 11 == 0


def _detect_minor_consent(text: str) -> List[Dict[str, Any]]:
    """
    Detect references to consent mechanisms specifically for Dutch minors.
    Under Dutch UAVG, parental consent is required for children under 16.
    """
    findings = []
    
    # Look for mentions of age verification with Dutch minor age context
    minor_patterns = [
        r'\b(?:leeftijd(?:s)?verificatie|leeftijd(?:s)?check)\b',
        r'\b(?:onder|jonger\s+dan)\s+(?:16|zestien)\s+jaar\b',
        r'\b(?:ouderlijke\s+toestemming|toestemming\s+van\s+ouders)\b',
        r'\b(?:parental\s+consent|age\s+verification)\b'
    ]
    
    for pattern in minor_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            findings.append({
                'type': 'MINOR_CONSENT',
                'value': 'Dutch minor consent references found',
                'risk_level': 'Medium',
                'gdpr_principle': 'netherlands_specific',
                'description': 'References to age verification/parental consent needed for users under 16 (Dutch UAVG)'
            })
            # One finding is enough
            break
    
    return findings


def _detect_medical_data(text: str) -> List[Dict[str, Any]]:
    """
    Detect Dutch medical data references that require special protection under UAVG.
    """
    findings = []
    
    # Dutch medical terms
    medical_terms = [
        r'\b(?:medisch(?:e)?|patiënt(?:en)?|diagnos(?:e|tisch)|behandeling|gezondheid(?:s)?)\b',
        r'\b(?:ziekenhuis|huisarts|specialist|UMC|zorg(?:verlener)?)\b',
        r'\b(?:elektronisch\s+patiëntendossier|EPD)\b'
    ]
    
    for pattern in medical_terms:
        if re.search(pattern, text, re.IGNORECASE):
            context_text = text[:min(500, len(text))]
            # Check if it's in a healthcare context
            is_high_risk = any(term in context_text.lower() for term in 
                          ['privacy', 'persoonlijk', 'vertrouwelijk', 'dossier'])
            
            findings.append({
                'type': 'MEDICAL_DATA',
                'value': 'Dutch healthcare data references found',
                'risk_level': 'High' if is_high_risk else 'Medium',
                'gdpr_principle': 'netherlands_specific',
                'description': 'Healthcare data requires additional safeguards under UAVG Article 30'
            })
            # One finding is enough
            break
    
    return findings


def validate_nl_compliance(findings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate a Netherlands compliance summary from findings.
    
    Args:
        findings: List of all findings
        
    Returns:
        Netherlands compliance summary
    """
    # Extract Netherlands-specific findings
    nl_findings = []
    
    for finding in findings:
        if finding.get('gdpr_principle') == 'netherlands_specific' or finding.get('type') in ['BSN', 'MEDICAL_DATA', 'MINOR_CONSENT']:
            nl_findings.append(finding)
    
    # Count high-risk findings
    high_risk_count = sum(1 for f in nl_findings if f.get('risk_level', '').lower() == 'high')
    
    # Generate appropriate recommendations based on findings
    recommendations = []
    
    if any(f.get('type') == 'BSN' for f in nl_findings):
        recommendations.append("Verify all BSN usage is explicitly authorized by law (UAVG Article 46)")
    
    if any(f.get('type') == 'MINOR_CONSENT' for f in nl_findings):
        recommendations.append("Implement proper age verification for users under 16 years (UAVG Article 5)")
    
    if any(f.get('type') == 'MEDICAL_DATA' for f in nl_findings):
        recommendations.append("Ensure medical data has additional safeguards per UAVG Article 30")
    
    if nl_findings:
        recommendations.append("Document legal basis for all Netherlands-specific personal data processing")
    
    return {
        'issues_found': len(nl_findings) > 0,
        'issue_count': len(nl_findings),
        'high_risk_count': high_risk_count,
        'findings': nl_findings,
        'recommendations': recommendations
    }


def test_netherlands_detection():
    """
    Simple unit test function for Netherlands detection logic.
    """
    # Test case 1: Valid BSN with context
    test_text_1 = "Patient met BSN 123456782 moet worden geregistreerd."
    findings_1 = detect_nl_violations(test_text_1)
    assert len(findings_1) > 0, "Should detect BSN in medical context"
    
    # Test case 2: Medical data
    test_text_2 = "Het elektronisch patiëntendossier bevat vertrouwelijke medische gegevens."
    findings_2 = detect_nl_violations(test_text_2)
    assert len(findings_2) > 0, "Should detect medical data references"
    
    # Test case 3: Minor consent
    test_text_3 = "Voor gebruikers jonger dan 16 jaar is ouderlijke toestemming vereist."
    findings_3 = detect_nl_violations(test_text_3)
    assert len(findings_3) > 0, "Should detect minor consent references"
    
    # Test case 4: No violations
    test_text_4 = "Dit is een normale tekst zonder speciale gegevens."
    findings_4 = detect_nl_violations(test_text_4)
    assert len(findings_4) == 0, "Should not detect violations in normal text"
    
    print("All Netherlands detection tests passed!")
    
    return True