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
    
    # Validate international transfers (Articles 44-49)
    transfer_compliance = _validate_international_transfers(content)
    findings.extend(transfer_compliance['findings'])
    
    # Validate breach notification requirements
    breach_compliance = _validate_breach_notification(content)
    findings.extend(breach_compliance['findings'])
    
    # Validate Data Protection by Design and by Default (Article 25)
    design_compliance = _validate_data_protection_by_design(content)
    findings.extend(design_compliance['findings'])
    
    # Validate Processor obligations (Article 28)
    processor_compliance = _validate_processor_obligations(content)
    findings.extend(processor_compliance['findings'])
    
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
        'design_compliance': design_compliance['score'],
        'processor_compliance': processor_compliance['score'],
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
    
    has_legal_basis = False  # Initialize variable
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
    """Validate international transfer safeguards (Articles 44-49)."""
    findings = []
    
    # Enhanced detection patterns for international transfers
    transfer_patterns = [
        r"\b(?:international\s+transfer|cross-?border\s+transfer|third\s+country\s+transfer)\b",
        r"\b(?:data\s+export|overseas\s+processing|global\s+processing)\b",
        r"\b(?:us\s+cloud|american\s+server|chinese\s+server|non-?eu\s+server)\b"
    ]
    
    # Specific third countries and regions
    third_country_patterns = [
        r"\b(?:usa|united\s+states|america|us\s+server)\b",
        r"\b(?:china|chinese\s+server|hong\s+kong)\b", 
        r"\b(?:india|singapore|australia|japan|south\s+korea)\b",
        r"\b(?:canada|brazil|mexico|argentina)\b",
        r"\b(?:russia|ukraine|turkey|israel)\b",
        r"\b(?:uk|united\s+kingdom|britain|post-?brexit)\b"
    ]
    
    # Cloud providers that may involve transfers
    cloud_provider_patterns = [
        r"\b(?:amazon\s+web\s+services|aws|s3\.amazonaws\.com)\b",
        r"\b(?:google\s+cloud|gcp|firebase|app\s+engine)\b",
        r"\b(?:microsoft\s+azure|azure\.com|office\s+365)\b",
        r"\b(?:alibaba\s+cloud|tencent\s+cloud|baidu\s+cloud)\b"
    ]
    
    has_international_transfer = (
        any(re.search(pattern, content, re.IGNORECASE) for pattern in transfer_patterns) or
        any(re.search(pattern, content, re.IGNORECASE) for pattern in third_country_patterns) or
        any(re.search(pattern, content, re.IGNORECASE) for pattern in cloud_provider_patterns)
    )
    
    if has_international_transfer:
        # Article 45: Adequacy decisions
        adequacy_patterns = [
            r"\b(?:adequacy\s+decision|adequate\s+level\s+of\s+protection)\b",
            r"\b(?:andorra|argentina|canada|faroe\s+islands|guernsey|isle\s+of\s+man|israel|japan|jersey|new\s+zealand|switzerland|uruguay|uk\s+gdpr)\b"
        ]
        
        has_adequacy = any(re.search(pattern, content, re.IGNORECASE) for pattern in adequacy_patterns)
        
        # Article 46: Appropriate safeguards  
        safeguard_patterns = [
            r"\b(?:standard\s+contractual\s+clauses|scc|model\s+clauses)\b",
            r"\b(?:binding\s+corporate\s+rules|bcr|intra-?group\s+agreement)\b",
            r"\b(?:certification\s+mechanism|approved\s+code\s+of\s+conduct)\b",
            r"\b(?:transfer\s+impact\s+assessment|tia|supplementary\s+measures)\b"
        ]
        
        has_safeguards = any(re.search(pattern, content, re.IGNORECASE) for pattern in safeguard_patterns)
        
        # Article 47: Binding corporate rules
        bcr_patterns = [
            r"\b(?:binding\s+corporate\s+rules|bcr\s+approval|supervisory\s+authority\s+approval)\b",
            r"\b(?:multinational\s+group|corporate\s+group\s+policy|intra-?group\s+transfer)\b"
        ]
        
        has_bcr = any(re.search(pattern, content, re.IGNORECASE) for pattern in bcr_patterns)
        
        # Article 49: Derogations for specific situations
        derogation_patterns = [
            r"\b(?:explicit\s+consent\s+for\s+transfer|informed\s+consent\s+to\s+transfer)\b",
            r"\b(?:contract\s+performance|pre-?contractual\s+measures)\b",
            r"\b(?:public\s+interest|vital\s+interest|legal\s+claim)\b",
            r"\b(?:legitimate\s+interest.*compelling|occasional\s+transfer)\b"
        ]
        
        has_derogation = any(re.search(pattern, content, re.IGNORECASE) for pattern in derogation_patterns)
        
        # Check for Schrems II compliance (supplementary measures)
        schrems_patterns = [
            r"\b(?:schrems\s+ii|surveillance\s+laws|government\s+access)\b",
            r"\b(?:supplementary\s+measures|additional\s+safeguards|encryption\s+in\s+transit)\b",
            r"\b(?:end-?to-?end\s+encryption|pseudonymization\s+before\s+transfer)\b"
        ]
        
        has_schrems_compliance = any(re.search(pattern, content, re.IGNORECASE) for pattern in schrems_patterns)
        
        # Evaluate transfer compliance
        legal_basis_found = has_adequacy or has_safeguards or has_bcr or has_derogation
        
        if not legal_basis_found:
            findings.append({
                'type': 'INTERNATIONAL_TRANSFER_NO_LEGAL_BASIS',
                'category': 'International Transfers',
                'value': 'Transfer without legal basis',
                'risk_level': 'Critical',
                'regulation': 'GDPR Articles 44-49',
                'description': "International data transfer detected without adequate legal basis (no adequacy decision, appropriate safeguards, or valid derogation)",
                'remediation': "Establish legal basis: adequacy decision (Art. 45), appropriate safeguards (Art. 46), BCRs (Art. 47), or valid derogation (Art. 49)"
            })
        
        # Check for US transfers requiring Schrems II compliance
        us_transfer_patterns = [r"\b(?:usa|united\s+states|us\s+server|american\s+cloud)\b"]
        has_us_transfer = any(re.search(pattern, content, re.IGNORECASE) for pattern in us_transfer_patterns)
        
        if has_us_transfer and not has_schrems_compliance and not has_adequacy:
            findings.append({
                'type': 'SCHREMS_II_COMPLIANCE_MISSING',
                'category': 'International Transfers', 
                'value': 'US transfer without Schrems II compliance',
                'risk_level': 'High',
                'regulation': 'GDPR Article 46 + Schrems II',
                'description': "Transfer to US detected without supplementary measures required post-Schrems II",
                'remediation': "Implement supplementary measures: end-to-end encryption, pseudonymization, contractual guarantees against surveillance"
            })
        
        # Check for prohibited transfers under Article 46
        prohibited_patterns = [
            r"\b(?:mass\s+surveillance|government\s+backdoor|unencrypted\s+transfer)\b",
            r"\b(?:no\s+data\s+protection|weak\s+privacy\s+laws|unrestricted\s+access)\b"
        ]
        
        has_prohibited_transfer = any(re.search(pattern, content, re.IGNORECASE) for pattern in prohibited_patterns)
        
        if has_prohibited_transfer:
            findings.append({
                'type': 'PROHIBITED_TRANSFER_METHOD',
                'category': 'International Transfers',
                'value': 'Prohibited transfer method detected',
                'risk_level': 'Critical', 
                'regulation': 'GDPR Article 46',
                'description': "Transfer using methods that do not provide adequate protection (mass surveillance, unencrypted, unrestricted government access)",
                'remediation': "Cease prohibited transfer methods, implement appropriate safeguards with supplementary measures"
            })
    
    # Calculate comprehensive score
    score = 100
    if has_international_transfer:
        critical_violations = len([f for f in findings if f.get('risk_level') == 'Critical'])
        high_violations = len([f for f in findings if f.get('risk_level') == 'High'])
        
        if critical_violations > 0:
            score = 20
        elif high_violations > 0:
            score = 50
        elif not any([has_adequacy, has_safeguards, has_bcr, has_derogation]):
            score = 60
    
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
    
    has_notification_procedure = False  # Initialize variable
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

def _validate_data_protection_by_design(content: str) -> Dict[str, Any]:
    """Validate Data Protection by Design and by Default (Article 25)."""
    findings = []
    
    # Check for privacy by design indicators
    design_patterns = [
        r"\b(?:privacy\s+by\s+design|data\s+protection\s+by\s+design)\b",
        r"\b(?:privacy\s+by\s+default|data\s+protection\s+by\s+default)\b",
        r"\b(?:built-?in\s+privacy|privacy\s+engineering|privacy\s+architecture)\b",
        r"\b(?:data\s+minimization\s+by\s+design|purpose\s+limitation\s+by\s+design)\b"
    ]
    
    # Check for privacy engineering practices
    engineering_patterns = [
        r"\b(?:pseudonymization|anonymization|encryption\s+by\s+default)\b",
        r"\b(?:access\s+controls?\s+by\s+design|role-?based\s+access\s+by\s+design)\b",
        r"\b(?:audit\s+logging\s+by\s+design|monitoring\s+by\s+design)\b",
        r"\b(?:consent\s+management\s+by\s+design|opt-?out\s+by\s+default)\b"
    ]
    
    has_design_principles = any(
        re.search(pattern, content, re.IGNORECASE) 
        for pattern in design_patterns
    )
    
    has_engineering_practices = any(
        re.search(pattern, content, re.IGNORECASE) 
        for pattern in engineering_patterns
    )
    
    # Check for violations (systems without privacy considerations)
    violation_patterns = [
        r"\b(?:collect\s+all\s+data|store\s+everything|maximum\s+data\s+collection)\b",
        r"\b(?:no\s+privacy\s+controls|privacy\s+not\s+considered|privacy\s+afterthought)\b",
        r"\b(?:opt-?in\s+by\s+default|sharing\s+by\s+default|public\s+by\s+default)\b"
    ]
    
    has_violations = any(
        re.search(pattern, content, re.IGNORECASE) 
        for pattern in violation_patterns
    )
    
    # Evaluate compliance
    if has_violations:
        findings.append({
            'type': 'DATA_PROTECTION_BY_DESIGN_VIOLATION',
            'category': 'Privacy by Design',
            'value': 'Privacy by design principles not implemented',
            'risk_level': 'High',
            'regulation': 'GDPR Article 25',
            'description': "System design violates data protection by design and by default principles",
            'remediation': "Implement privacy by design: data minimization, pseudonymization, privacy-friendly defaults"
        })
    
    if not has_design_principles and not has_engineering_practices:
        findings.append({
            'type': 'DATA_PROTECTION_BY_DESIGN_MISSING',
            'category': 'Privacy by Design',
            'value': 'No privacy by design indicators found',
            'risk_level': 'Medium',
            'regulation': 'GDPR Article 25',
            'description': "No evidence of data protection by design and by default implementation",
            'remediation': "Integrate privacy considerations into system design and implement privacy by default settings"
        })
    
    # Calculate score
    score = 100
    if has_violations:
        score -= 40
    if not has_design_principles:
        score -= 20
    if not has_engineering_practices:
        score -= 15
    
    return {
        'score': max(0, score),
        'findings': findings
    }

def _validate_processor_obligations(content: str) -> Dict[str, Any]:
    """Validate Processor obligations (Article 28)."""
    findings = []
    
    # Check for processor relationship indicators
    processor_patterns = [
        r"\b(?:data\s+processor|processing\s+agreement|processor\s+contract)\b",
        r"\b(?:sub-?processor|third\s+party\s+processor|service\s+provider)\b",
        r"\b(?:cloud\s+provider|hosting\s+provider|saas\s+provider)\b"
    ]
    
    has_processor_relationship = any(
        re.search(pattern, content, re.IGNORECASE) 
        for pattern in processor_patterns
    )
    
    if has_processor_relationship:
        # Check for required contractual elements
        contract_patterns = [
            r"\b(?:processing\s+instructions|written\s+authorization|documented\s+instructions)\b",
            r"\b(?:confidentiality\s+obligation|staff\s+confidentiality|employee\s+confidentiality)\b",
            r"\b(?:security\s+measures|technical\s+safeguards|organizational\s+measures)\b",
            r"\b(?:sub-?processor\s+authorization|sub-?contractor\s+approval)\b",
            r"\b(?:data\s+subject\s+rights|assist\s+controller|support\s+controller)\b",
            r"\b(?:data\s+return|data\s+deletion|end\s+of\s+processing)\b",
            r"\b(?:audit\s+rights|inspection\s+rights|compliance\s+monitoring)\b"
        ]
        
        missing_elements = []
        contract_element_names = [
            "processing instructions",
            "confidentiality obligations", 
            "security measures",
            "sub-processor authorization",
            "data subject rights assistance",
            "data return/deletion",
            "audit rights"
        ]
        
        for i, pattern in enumerate(contract_patterns):
            if not re.search(pattern, content, re.IGNORECASE):
                missing_elements.append(contract_element_names[i])
        
        if missing_elements:
            findings.append({
                'type': 'PROCESSOR_CONTRACT_INCOMPLETE',
                'category': 'Processor Obligations',
                'value': f'Missing contract elements: {", ".join(missing_elements[:3])}...' if len(missing_elements) > 3 else f'Missing: {", ".join(missing_elements)}',
                'risk_level': 'High',
                'regulation': 'GDPR Article 28',
                'description': f"Data processing agreement missing required elements: {', '.join(missing_elements)}",
                'remediation': "Update processor contracts to include all Article 28 requirements: instructions, confidentiality, security, sub-processors, rights assistance, data return, audits"
            })
        
        # Check for prohibited processing
        prohibited_patterns = [
            r"\b(?:unauthorized\s+processing|processing\s+without\s+instructions)\b",
            r"\b(?:use\s+data\s+for\s+own\s+purposes|secondary\s+use\s+of\s+data)\b",
            r"\b(?:retain\s+data\s+after\s+contract|keep\s+data\s+permanently)\b"
        ]
        
        has_prohibited_activities = any(
            re.search(pattern, content, re.IGNORECASE) 
            for pattern in prohibited_patterns
        )
        
        if has_prohibited_activities:
            findings.append({
                'type': 'PROCESSOR_PROHIBITED_ACTIVITY',
                'category': 'Processor Obligations',
                'value': 'Prohibited processor activities detected',
                'risk_level': 'Critical',
                'regulation': 'GDPR Article 28',
                'description': "Processor engaging in prohibited activities (unauthorized processing, secondary use, retention)",
                'remediation': "Cease unauthorized processing, implement strict instruction compliance, ensure data deletion after contract termination"
            })
    
    # Calculate score
    score = 100
    if has_processor_relationship:
        if any(f.get('risk_level') == 'Critical' for f in findings):
            score = 20
        elif any(f.get('risk_level') == 'High' for f in findings):
            score = 60
    
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
        recommendations.add("Implement appropriate safeguards for international data transfers including Schrems II compliance")
    
    if any('BREACH_NOTIFICATION' in ft for ft in finding_types):
        recommendations.add("Develop and test incident response and breach notification procedures")
    
    if any('DATA_PROTECTION_BY_DESIGN' in ft for ft in finding_types):
        recommendations.add("Integrate privacy by design and by default into all system development processes")
    
    if any('PROCESSOR' in ft for ft in finding_types):
        recommendations.add("Review and update all data processing agreements to ensure Article 28 compliance")
    
    if any('SCHREMS_II' in ft for ft in finding_types):
        recommendations.add("Implement supplementary measures for US data transfers post-Schrems II ruling")
    
    # Always include these general recommendations
    recommendations.update([
        "Conduct regular GDPR compliance assessments",
        "Provide ongoing GDPR training for all staff",
        "Maintain comprehensive records of processing activities",
        "Implement privacy by design and default principles",
        "Review all third-party processor contracts annually",
        "Conduct Transfer Impact Assessments for international data flows"
    ])
    
    return list(recommendations)