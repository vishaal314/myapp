"""
Comprehensive GDPR Validator

This module provides comprehensive validation of all GDPR principles including
the core principles, rights, and obligations under the regulation.
"""

import re
from typing import Dict, List, Any, Set
from datetime import datetime, timedelta

# GDPR Core Principles (Article 5)
GDPR_PRINCIPLES = {
    "lawfulness": {
        "description": "Processing must have a lawful basis",
        "patterns": [
            r"\b(?:consent|contract|legal\s+obligation|vital\s+interest|public\s+task|legitimate\s+interest)\b",
            r"\b(?:lawful\s+basis|legal\s+basis|processing\s+purpose)\b"
        ],
        "violations": [
            r"\b(?:unlawful\s+processing|no\s+legal\s+basis|unauthorized\s+collection)\b"
        ]
    },
    "fairness": {
        "description": "Processing must be fair and transparent",
        "patterns": [
            r"\b(?:fair\s+processing|transparent|privacy\s+notice|data\s+subject\s+rights)\b"
        ],
        "violations": [
            r"\b(?:unfair\s+processing|hidden\s+collection|deceptive\s+practice)\b"
        ]
    },
    "transparency": {
        "description": "Data subjects must be informed about processing",
        "patterns": [
            r"\b(?:privacy\s+policy|privacy\s+notice|data\s+protection\s+notice|information\s+provided)\b"
        ],
        "violations": [
            r"\b(?:hidden\s+processing|no\s+notice|undisclosed\s+use)\b"
        ]
    },
    "purpose_limitation": {
        "description": "Data must be collected for specified, explicit and legitimate purposes",
        "patterns": [
            r"\b(?:specified\s+purpose|explicit\s+purpose|legitimate\s+purpose|purpose\s+statement)\b"
        ],
        "violations": [
            r"\b(?:purpose\s+creep|secondary\s+use|incompatible\s+purpose|function\s+creep)\b"
        ]
    },
    "data_minimisation": {
        "description": "Data must be adequate, relevant and limited to what is necessary",
        "patterns": [
            r"\b(?:data\s+minimisation|necessary\s+data|adequate\s+data|relevant\s+data)\b"
        ],
        "violations": [
            r"\b(?:excessive\s+data|unnecessary\s+collection|data\s+hoarding|over-collection)\b"
        ]
    },
    "accuracy": {
        "description": "Data must be accurate and kept up to date",
        "patterns": [
            r"\b(?:data\s+accuracy|data\s+quality|data\s+validation|data\s+verification)\b"
        ],
        "violations": [
            r"\b(?:inaccurate\s+data|outdated\s+data|data\s+quality\s+issues)\b"
        ]
    },
    "storage_limitation": {
        "description": "Data must be kept only as long as necessary",
        "patterns": [
            r"\b(?:retention\s+period|storage\s+limitation|data\s+retention|deletion\s+schedule)\b"
        ],
        "violations": [
            r"\b(?:indefinite\s+storage|excessive\s+retention|no\s+deletion\s+policy)\b"
        ]
    },
    "integrity_confidentiality": {
        "description": "Data must be processed securely",
        "patterns": [
            r"\b(?:data\s+security|encryption|access\s+control|security\s+measures)\b"
        ],
        "violations": [
            r"\b(?:data\s+breach|security\s+incident|unauthorized\s+access|data\s+leak)\b"
        ]
    },
    "accountability": {
        "description": "Controller must demonstrate compliance",
        "patterns": [
            r"\b(?:accountability|compliance\s+demonstration|data\s+protection\s+record|processing\s+record)\b"
        ],
        "violations": [
            r"\b(?:no\s+documentation|compliance\s+failure|inadequate\s+records)\b"
        ]
    }
}

# GDPR Data Subject Rights (Chapter III)
DATA_SUBJECT_RIGHTS = {
    "right_to_information": {
        "articles": ["Article 13", "Article 14"],
        "description": "Right to be informed about data processing",
        "patterns": [
            r"\b(?:right\s+to\s+(?:be\s+)?inform|information\s+provided|transparency\s+information)\b"
        ]
    },
    "right_of_access": {
        "articles": ["Article 15"],
        "description": "Right to access personal data",
        "patterns": [
            r"\b(?:right\s+of\s+access|subject\s+access\s+request|data\s+access|copy\s+of\s+data)\b"
        ]
    },
    "right_to_rectification": {
        "articles": ["Article 16"],
        "description": "Right to rectify inaccurate data",
        "patterns": [
            r"\b(?:right\s+to\s+rectification|data\s+correction|amend\s+data|update\s+data)\b"
        ]
    },
    "right_to_erasure": {
        "articles": ["Article 17"],
        "description": "Right to erasure (right to be forgotten)",
        "patterns": [
            r"\b(?:right\s+to\s+erasure|right\s+to\s+be\s+forgotten|delete\s+data|data\s+deletion)\b"
        ]
    },
    "right_to_restrict_processing": {
        "articles": ["Article 18"],
        "description": "Right to restrict processing",
        "patterns": [
            r"\b(?:restrict\s+processing|processing\s+restriction|limit\s+processing)\b"
        ]
    },
    "right_to_data_portability": {
        "articles": ["Article 20"],
        "description": "Right to data portability",
        "patterns": [
            r"\b(?:data\s+portability|export\s+data|transfer\s+data|data\s+migration)\b"
        ]
    },
    "right_to_object": {
        "articles": ["Article 21"],
        "description": "Right to object to processing",
        "patterns": [
            r"\b(?:right\s+to\s+object|object\s+to\s+processing|opt-?out|withdraw\s+consent)\b"
        ]
    },
    "rights_related_to_automated_decision_making": {
        "articles": ["Article 22"],
        "description": "Rights related to automated decision-making and profiling",
        "patterns": [
            r"\b(?:automated\s+decision|profiling|algorithmic\s+decision|human\s+intervention)\b"
        ]
    }
}

def validate_comprehensive_gdpr_compliance(content: str, region: str = "Netherlands") -> Dict[str, Any]:
    """
    Perform comprehensive GDPR compliance validation.
    
    Args:
        content: Document content to analyze
        region: Region for specific requirements
        
    Returns:
        Comprehensive GDPR compliance assessment
    """
    findings = []
    
    # Validate core GDPR principles
    principle_compliance = _validate_gdpr_principles(content)
    findings.extend(principle_compliance['findings'])
    
    # Validate data subject rights
    rights_compliance = _validate_data_subject_rights(content)
    findings.extend(rights_compliance['findings'])
    
    # Validate special categories of data
    special_data_compliance = _validate_special_categories(content)
    findings.extend(special_data_compliance['findings'])
    
    # Validate international transfers
    transfer_compliance = _validate_international_transfers(content)
    findings.extend(transfer_compliance['findings'])
    
    # Validate breach notification requirements
    breach_compliance = _validate_breach_notification(content)
    findings.extend(breach_compliance['findings'])
    
    # Calculate overall compliance score
    compliance_score = _calculate_compliance_score(findings)
    
    return {
        'assessment_date': datetime.now().isoformat(),
        'region': region,
        'total_findings': len(findings),
        'principle_compliance': principle_compliance['scores'],
        'rights_compliance': rights_compliance['scores'],
        'special_data_compliance': special_data_compliance['score'],
        'transfer_compliance': transfer_compliance['score'],
        'breach_compliance': breach_compliance['score'],
        'overall_compliance_score': compliance_score,
        'compliance_status': _get_compliance_status(compliance_score),
        'findings': findings,
        'recommendations': _generate_comprehensive_recommendations(findings),
        'next_review_date': (datetime.now() + timedelta(days=90)).isoformat()
    }

def _validate_gdpr_principles(content: str) -> Dict[str, Any]:
    """Validate adherence to GDPR core principles."""
    findings = []
    scores = {}
    
    for principle, config in GDPR_PRINCIPLES.items():
        principle_score = 100
        principle_findings = []
        
        # Check for positive indicators
        has_compliance_indicators = any(
            re.search(pattern, content, re.IGNORECASE) 
            for pattern in config['patterns']
        )
        
        # Check for violations
        violation_matches = []
        for violation_pattern in config.get('violations', []):
            matches = list(re.finditer(violation_pattern, content, re.IGNORECASE))
            violation_matches.extend(matches)
        
        if violation_matches:
            principle_score -= len(violation_matches) * 20
            for match in violation_matches:
                principle_findings.append({
                    'type': 'GDPR_PRINCIPLE_VIOLATION',
                    'principle': principle,
                    'category': config['description'],
                    'value': match.group(),
                    'risk_level': 'High',
                    'regulation': 'GDPR Article 5',
                    'description': f"Violation of {principle.replace('_', ' ')} principle",
                    'location': f"Position {match.start()}-{match.end()}"
                })
        
        if not has_compliance_indicators and principle in ['transparency', 'lawfulness']:
            principle_score -= 30
            principle_findings.append({
                'type': 'GDPR_PRINCIPLE_MISSING',
                'principle': principle,
                'category': config['description'],
                'value': f"Missing {principle} indicators",
                'risk_level': 'Medium',
                'regulation': 'GDPR Article 5',
                'description': f"No evidence of {principle.replace('_', ' ')} compliance"
            })
        
        scores[principle] = max(0, principle_score)
        findings.extend(principle_findings)
    
    return {
        'scores': scores,
        'findings': findings,
        'average_score': sum(scores.values()) / len(scores) if scores else 0
    }

def _validate_data_subject_rights(content: str) -> Dict[str, Any]:
    """Validate implementation of data subject rights."""
    findings = []
    scores = {}
    
    for right, config in DATA_SUBJECT_RIGHTS.items():
        right_score = 100
        
        # Check if the right is mentioned or implemented
        has_right_implementation = any(
            re.search(pattern, content, re.IGNORECASE) 
            for pattern in config['patterns']
        )
        
        if not has_right_implementation:
            right_score = 50  # Partial compliance - right not explicitly mentioned
            findings.append({
                'type': 'DATA_SUBJECT_RIGHT_MISSING',
                'right': right,
                'category': config['description'],
                'value': f"No evidence of {right.replace('_', ' ')} implementation",
                'risk_level': 'Medium',
                'regulation': ', '.join(config['articles']),
                'description': f"Data subject right not explicitly addressed: {config['description']}"
            })
        
        scores[right] = right_score
    
    return {
        'scores': scores,
        'findings': findings,
        'average_score': sum(scores.values()) / len(scores) if scores else 0
    }

def _validate_special_categories(content: str) -> Dict[str, Any]:
    """Validate processing of special categories of personal data (Article 9)."""
    findings = []
    
    special_categories = {
        'health_data': [
            r"\b(?:health\s+data|medical\s+data|patient\s+data|health\s+record)\b",
            r"\b(?:diagnosis|treatment|medication|medical\s+condition)\b"
        ],
        'genetic_data': [
            r"\b(?:genetic\s+data|dna|genome|genetic\s+information)\b"
        ],
        'biometric_data': [
            r"\b(?:biometric\s+data|fingerprint|facial\s+recognition|biometric\s+identification)\b"
        ],
        'racial_ethnic_origin': [
            r"\b(?:racial\s+origin|ethnic\s+origin|ethnicity|race)\b"
        ],
        'political_opinions': [
            r"\b(?:political\s+opinion|political\s+affiliation|political\s+view)\b"
        ],
        'religious_beliefs': [
            r"\b(?:religious\s+belief|religion|faith|spiritual\s+belief)\b"
        ],
        'trade_union_membership': [
            r"\b(?:trade\s+union|union\s+membership|labor\s+union)\b"
        ],
        'sexual_orientation': [
            r"\b(?:sexual\s+orientation|sexual\s+preference|gender\s+identity)\b"
        ]
    }
    
    detected_categories = []
    for category, patterns in special_categories.items():
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                detected_categories.append(category)
                break
    
    if detected_categories:
        # Check for explicit consent or other Article 9 legal basis
        consent_patterns = [
            r"\b(?:explicit\s+consent|specific\s+consent|clear\s+consent)\b",
            r"\b(?:employment\s+law|social\s+security\s+law|collective\s+agreement)\b",
            r"\b(?:vital\s+interest|life\s+or\s+death|medical\s+emergency)\b",
            r"\b(?:public\s+interest|substantial\s+public\s+interest)\b"
        ]
        
        has_legal_basis = any(
            re.search(pattern, content, re.IGNORECASE) 
            for pattern in consent_patterns
        )
        
        if not has_legal_basis:
            findings.append({
                'type': 'SPECIAL_CATEGORY_VIOLATION',
                'category': 'Special Categories Processing',
                'value': ', '.join(detected_categories),
                'risk_level': 'Critical',
                'regulation': 'GDPR Article 9',
                'description': f"Special categories of data detected without explicit legal basis: {', '.join(detected_categories)}",
                'remediation': "Obtain explicit consent or establish other Article 9 legal basis"
            })
    
    score = 100 if not detected_categories or (detected_categories and has_legal_basis) else 30
    
    return {
        'score': score,
        'findings': findings,
        'detected_categories': detected_categories
    }

def _validate_international_transfers(content: str) -> Dict[str, Any]:
    """Validate international data transfers (Chapter V)."""
    findings = []
    
    transfer_patterns = [
        r"\b(?:international\s+transfer|cross-?border\s+transfer|third\s+country\s+transfer)\b",
        r"\b(?:adequacy\s+decision|standard\s+contractual\s+clauses|scc)\b",
        r"\b(?:binding\s+corporate\s+rules|bcr|certification\s+mechanism)\b",
        r"\b(?:usa|united\s+states|china|russia|india|non-?eu\s+country)\b"
    ]
    
    has_international_transfer = any(
        re.search(pattern, content, re.IGNORECASE) 
        for pattern in transfer_patterns
    )
    
    if has_international_transfer:
        # Check for appropriate safeguards
        safeguard_patterns = [
            r"\b(?:adequacy\s+decision|appropriate\s+safeguard|suitable\s+safeguard)\b",
            r"\b(?:standard\s+contractual\s+clauses|binding\s+corporate\s+rules)\b",
            r"\b(?:certification|transfer\s+impact\s+assessment|tia)\b"
        ]
        
        has_safeguards = any(
            re.search(pattern, content, re.IGNORECASE) 
            for pattern in safeguard_patterns
        )
        
        if not has_safeguards:
            findings.append({
                'type': 'INTERNATIONAL_TRANSFER_VIOLATION',
                'category': 'International Transfers',
                'value': 'Transfer without adequate safeguards',
                'risk_level': 'High',
                'regulation': 'GDPR Chapter V',
                'description': "International data transfer detected without appropriate safeguards",
                'remediation': "Implement appropriate safeguards (adequacy decision, SCCs, BCRs, etc.)"
            })
    
    score = 100 if not has_international_transfer or has_safeguards else 40
    
    return {
        'score': score,
        'findings': findings
    }

def _validate_breach_notification(content: str) -> Dict[str, Any]:
    """Validate breach notification procedures (Articles 33-34)."""
    findings = []
    
    breach_patterns = [
        r"\b(?:data\s+breach|security\s+incident|privacy\s+breach)\b",
        r"\b(?:unauthorized\s+access|data\s+leak|cyber\s+attack)\b"
    ]
    
    has_breach_reference = any(
        re.search(pattern, content, re.IGNORECASE) 
        for pattern in breach_patterns
    )
    
    if has_breach_reference:
        # Check for notification procedures
        notification_patterns = [
            r"\b(?:72\s+hour|breach\s+notification|notify\s+(?:supervisory\s+)?authority)\b",
            r"\b(?:notify\s+data\s+subject|individual\s+notification|breach\s+communication)\b",
            r"\b(?:incident\s+response|breach\s+procedure|notification\s+process)\b"
        ]
        
        has_notification_procedure = any(
            re.search(pattern, content, re.IGNORECASE) 
            for pattern in notification_patterns
        )
        
        if not has_notification_procedure:
            findings.append({
                'type': 'BREACH_NOTIFICATION_MISSING',
                'category': 'Breach Notification',
                'value': 'Missing notification procedures',
                'risk_level': 'High',
                'regulation': 'GDPR Articles 33-34',
                'description': "Data breach references found without proper notification procedures",
                'remediation': "Implement 72-hour authority notification and data subject notification procedures"
            })
    
    score = 100 if not has_breach_reference or has_notification_procedure else 50
    
    return {
        'score': score,
        'findings': findings
    }

def _calculate_compliance_score(findings: List[Dict[str, Any]]) -> int:
    """Calculate overall GDPR compliance score."""
    if not findings:
        return 100
    
    critical_count = len([f for f in findings if f.get('risk_level') == 'Critical'])
    high_count = len([f for f in findings if f.get('risk_level') == 'High'])
    medium_count = len([f for f in findings if f.get('risk_level') == 'Medium'])
    
    score_deduction = (critical_count * 30) + (high_count * 15) + (medium_count * 5)
    
    return max(0, 100 - score_deduction)

def _get_compliance_status(score: int) -> str:
    """Determine compliance status based on score."""
    if score >= 90:
        return "Fully Compliant"
    elif score >= 70:
        return "Mostly Compliant"
    elif score >= 50:
        return "Partially Compliant"
    else:
        return "Non-Compliant"

def _generate_comprehensive_recommendations(findings: List[Dict[str, Any]]) -> List[str]:
    """Generate comprehensive recommendations based on findings."""
    recommendations = set()
    
    finding_types = [f.get('type', '') for f in findings]
    
    if any('PRINCIPLE_VIOLATION' in ft for ft in finding_types):
        recommendations.add("Review and update data processing activities to ensure compliance with GDPR principles")
    
    if any('DATA_SUBJECT_RIGHT' in ft for ft in finding_types):
        recommendations.add("Implement comprehensive data subject rights management system")
    
    if any('SPECIAL_CATEGORY' in ft for ft in finding_types):
        recommendations.add("Establish explicit consent mechanisms for special categories of personal data")
    
    if any('INTERNATIONAL_TRANSFER' in ft for ft in finding_types):
        recommendations.add("Implement appropriate safeguards for international data transfers")
    
    if any('BREACH_NOTIFICATION' in ft for ft in finding_types):
        recommendations.add("Develop and test incident response and breach notification procedures")
    
    # Always include these general recommendations
    recommendations.update([
        "Conduct regular GDPR compliance assessments",
        "Provide ongoing GDPR training for all staff",
        "Maintain comprehensive records of processing activities",
        "Implement privacy by design and default principles"
    ])
    
    return list(recommendations)