"""
Netherlands UAVG Compliance Module

Enhanced detection for Netherlands-specific GDPR implementation (UAVG)
including AP Guidelines 2024-2025, BSN processing rules, and cookie consent validation.
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

def detect_uavg_compliance_gaps(content: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Comprehensive Netherlands UAVG compliance detection addressing identified gaps.
    """
    findings = []
    
    # AP Guidelines 2024-2025 updates
    findings.extend(_check_ap_guidelines_2024_2025(content, metadata or {}))
    
    # Enhanced BSN processing rules
    findings.extend(_check_enhanced_bsn_processing(content, metadata or {}))
    
    # Real-time cookie consent validation
    findings.extend(_check_real_time_cookie_consent(content, metadata or {}))
    
    # 72-hour data breach notification automation
    findings.extend(_check_breach_notification_timeline(content, metadata or {}))
    
    # Netherlands-specific privacy requirements
    findings.extend(_check_netherlands_privacy_requirements(content, metadata or {}))
    
    return findings

def _check_ap_guidelines_2024_2025(content: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Check compliance with latest Netherlands AP (Autoriteit Persoonsgegevens) guidelines."""
    findings = []
    
    # AP 2024-2025 specific requirements
    ap_requirements = {
        "ai_decision_making": r"\b(?:ai.*decision|automated.*decision|algorithmic.*decision|machine.*learning.*decision)\b",
        "children_data_protection": r"\b(?:children.*data|minor.*data|under.*16|parental.*consent|child.*protection)\b",
        "biometric_processing": r"\b(?:biometric.*process|fingerprint|facial.*recognition|iris.*scan|voice.*print)\b",
        "health_data_special": r"\b(?:health.*data|medical.*data|patient.*data|healthcare.*information)\b",
        "workplace_monitoring": r"\b(?:workplace.*monitor|employee.*surveillance|staff.*tracking|worker.*monitoring)\b",
        "cookie_consent_2024": r"\b(?:cookie.*consent|tracking.*consent|analytics.*consent|marketing.*cookie)\b",
        "data_minimization_principle": r"\b(?:data.*minimi|necessary.*data|proportional.*processing|excessive.*data)\b",
        "purpose_limitation_strict": r"\b(?:purpose.*limitation|processing.*purpose|secondary.*use|function.*creep)\b"
    }
    
    ap_violations = []
    for requirement, pattern in ap_requirements.items():
        if re.search(pattern, content, re.IGNORECASE):
            ap_violations.append(requirement)
    
    # Check for AP-specific compliance indicators
    ap_compliance_indicators = [
        r"\b(?:ap.*guideline|autoriteit.*persoonsgegevens|dutch.*dpa)\b",
        r"\b(?:netherlands.*gdpr|uavg.*compliance|dutch.*privacy.*law)\b"
    ]
    
    has_ap_compliance = any(re.search(pattern, content, re.IGNORECASE) for pattern in ap_compliance_indicators)
    
    if ap_violations and not has_ap_compliance:
        findings.append({
            'type': 'UAVG_AP_GUIDELINES_2024_2025_GAP',
            'category': 'Netherlands AP Guidelines',
            'severity': 'High',
            'title': 'Netherlands AP Guidelines 2024-2025 Compliance Gap',
            'description': f'Processing activities requiring AP Guidelines compliance detected: {", ".join(ap_violations)}',
            'article_reference': 'Netherlands UAVG + AP Guidelines 2024-2025',
            'detected_activities': ap_violations,
            'compliance_deadline': 'Immediate - AP Guidelines Effective',
            'penalty_risk': 'Up to €890K or 2% turnover (Netherlands)',
            'ap_website': 'https://autoriteitpersoonsgegevens.nl',
            'remediation': 'Implement Netherlands AP Guidelines 2024-2025 specific requirements'
        })
    
    return findings

def _check_enhanced_bsn_processing(content: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Enhanced validation for BSN (Burgerservicenummer) processing rules."""
    findings = []
    
    # BSN detection patterns (Dutch social security numbers)
    bsn_patterns = [
        r"\b(?:bsn|burgerservicenummer|social.*security.*number)\b",
        r"\b\d{9}\b",  # 9-digit BSN format
        r"\b(?:citizen.*service.*number|national.*id.*number)\b"
    ]
    
    # BSN-specific use cases and restrictions
    bsn_use_cases = {
        "government_services": r"\b(?:government.*service|public.*administration|municipal.*service|tax.*administration)\b",
        "healthcare_providers": r"\b(?:healthcare.*provider|hospital|medical.*practice|gp.*practice)\b",
        "educational_institutions": r"\b(?:school|university|educational.*institution|student.*administration)\b",
        "financial_institutions": r"\b(?:bank|financial.*institution|insurance.*company|pension.*fund)\b",
        "employment_services": r"\b(?:employment.*agency|hr.*department|payroll.*service|uwv)\b"
    }
    
    has_bsn = any(re.search(pattern, content, re.IGNORECASE) for pattern in bsn_patterns)
    
    if has_bsn:
        # Check for legitimate BSN use cases
        legitimate_uses = []
        for use_case, pattern in bsn_use_cases.items():
            if re.search(pattern, content, re.IGNORECASE):
                legitimate_uses.append(use_case)
        
        # Check for BSN protection measures
        bsn_protection_patterns = [
            r"\b(?:encrypted.*bsn|protected.*bsn|secured.*bsn|masked.*bsn)\b",
            r"\b(?:bsn.*encryption|bsn.*protection|bsn.*security)\b"
        ]
        
        has_bsn_protection = any(re.search(pattern, content, re.IGNORECASE) for pattern in bsn_protection_patterns)
        
        if not legitimate_uses:
            findings.append({
                'type': 'UAVG_BSN_UNAUTHORIZED_USE',
                'category': 'BSN Processing Rules',
                'severity': 'Critical',
                'title': 'Unauthorized BSN Processing Detected',
                'description': 'BSN processing without legitimate legal basis under Dutch law',
                'article_reference': 'Netherlands UAVG Article 46 + BSN Act',
                'legal_basis_required': 'Wbp/UAVG Article 6 + specific BSN legislation',
                'penalty_risk': 'Up to €890K or 2% turnover + criminal liability',
                'remediation': 'Remove BSN processing or establish legitimate legal basis under Dutch law'
            })
        
        if legitimate_uses and not has_bsn_protection:
            findings.append({
                'type': 'UAVG_BSN_INSUFFICIENT_PROTECTION',
                'category': 'BSN Processing Rules',
                'severity': 'High',
                'title': 'Insufficient BSN Protection Measures',
                'description': f'BSN processing in {", ".join(legitimate_uses)} without adequate protection',
                'article_reference': 'Netherlands UAVG Article 32 + BSN Guidelines',
                'detected_use_cases': legitimate_uses,
                'penalty_risk': 'Up to €890K or 2% turnover',
                'remediation': 'Implement encryption, access controls, and audit logging for BSN processing'
            })
    
    return findings

def _check_real_time_cookie_consent(content: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Real-time cookie consent validation per Netherlands AP requirements."""
    findings = []
    
    # Cookie and tracking technology patterns
    cookie_patterns = [
        r"\b(?:cookie|tracking.*pixel|web.*beacon|local.*storage)\b",
        r"\b(?:analytics|google.*analytics|facebook.*pixel|tracking.*code)\b",
        r"\b(?:third.*party.*cookie|advertising.*cookie|marketing.*cookie)\b"
    ]
    
    # Consent mechanisms
    consent_patterns = {
        "explicit_consent": r"\b(?:explicit.*consent|clear.*consent|unambiguous.*consent)\b",
        "opt_in_mechanism": r"\b(?:opt.*in|active.*choice|user.*choice|consent.*banner)\b",
        "granular_consent": r"\b(?:granular.*consent|specific.*consent|category.*consent)\b",
        "withdraw_consent": r"\b(?:withdraw.*consent|revoke.*consent|opt.*out|consent.*withdrawal)\b"
    }
    
    has_cookies = any(re.search(pattern, content, re.IGNORECASE) for pattern in cookie_patterns)
    
    if has_cookies:
        # Check consent implementation
        consent_gaps = []
        for consent_type, pattern in consent_patterns.items():
            if not re.search(pattern, content, re.IGNORECASE):
                consent_gaps.append(consent_type)
        
        # Check for pre-ticked boxes (forbidden)
        dark_patterns = [
            r"\b(?:pre.*ticked|pre.*selected|default.*accept|automatically.*accept)\b",
            r"\b(?:nudging|dark.*pattern|deceptive.*design|misleading.*consent)\b"
        ]
        
        has_dark_patterns = any(re.search(pattern, content, re.IGNORECASE) for pattern in dark_patterns)
        
        if len(consent_gaps) >= 2:
            findings.append({
                'type': 'UAVG_COOKIE_CONSENT_INSUFFICIENT',
                'category': 'Cookie Consent Validation',
                'severity': 'High',
                'title': 'Insufficient Cookie Consent Implementation',
                'description': f'Missing {len(consent_gaps)} required consent mechanisms',
                'article_reference': 'Netherlands UAVG Article 6 + Telecommunications Act Article 11.7a',
                'missing_mechanisms': consent_gaps,
                'penalty_risk': 'Up to €890K or 2% turnover',
                'ap_guidance': 'https://autoriteitpersoonsgegevens.nl/themas/internet-telefoon-tv-en-post/cookies',
                'remediation': 'Implement compliant cookie consent banner with explicit opt-in'
            })
        
        if has_dark_patterns:
            findings.append({
                'type': 'UAVG_COOKIE_DARK_PATTERNS',
                'category': 'Cookie Consent Validation',
                'severity': 'High',
                'title': 'Prohibited Cookie Consent Dark Patterns',
                'description': 'Deceptive design patterns in cookie consent implementation',
                'article_reference': 'Netherlands UAVG Article 7 + AP Guidelines',
                'penalty_risk': 'Up to €890K or 2% turnover',
                'remediation': 'Remove dark patterns, ensure genuine free choice in cookie consent'
            })
    
    return findings

def _check_breach_notification_timeline(content: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """72-hour timeline validation for data breach notifications."""
    findings = []
    
    # Data breach indicators
    breach_patterns = [
        r"\b(?:data.*breach|security.*incident|privacy.*breach|cyber.*attack)\b",
        r"\b(?:unauthorized.*access|data.*leak|system.*compromise|hacking.*incident)\b"
    ]
    
    # Notification timeline patterns
    timeline_patterns = {
        "72_hour_notification": r"\b(?:72.*hour|three.*day|ap.*notification|supervisory.*authority)\b",
        "breach_register": r"\b(?:breach.*register|incident.*log|breach.*documentation)\b",
        "impact_assessment": r"\b(?:impact.*assessment|risk.*evaluation|breach.*analysis)\b",
        "data_subject_notification": r"\b(?:data.*subject.*notification|individual.*notification|person.*affected)\b"
    }
    
    has_breach_reference = any(re.search(pattern, content, re.IGNORECASE) for pattern in breach_patterns)
    
    if has_breach_reference:
        # Check notification procedures
        missing_procedures = []
        for procedure, pattern in timeline_patterns.items():
            if not re.search(pattern, content, re.IGNORECASE):
                missing_procedures.append(procedure)
        
        # Check for automated notification systems
        automation_patterns = [
            r"\b(?:automated.*notification|automatic.*breach.*reporting|incident.*response.*system)\b",
            r"\b(?:breach.*detection.*system|monitoring.*system|alert.*system)\b"
        ]
        
        has_automation = any(re.search(pattern, content, re.IGNORECASE) for pattern in automation_patterns)
        
        if len(missing_procedures) >= 2:
            findings.append({
                'type': 'UAVG_BREACH_NOTIFICATION_INCOMPLETE',
                'category': 'Data Breach Notification',
                'severity': 'High',
                'title': '72-Hour Breach Notification Requirements Incomplete',
                'description': f'Missing {len(missing_procedures)} required breach notification procedures',
                'article_reference': 'Netherlands UAVG Articles 33-34',
                'missing_procedures': missing_procedures,
                'ap_contact': 'datalek@autoriteitpersoonsgegevens.nl',
                'timeline_requirement': '72 hours to AP, without undue delay to data subjects',
                'penalty_risk': 'Up to €890K or 2% turnover',
                'remediation': 'Implement complete 72-hour breach notification procedures'
            })
        
        if not has_automation:
            findings.append({
                'type': 'UAVG_BREACH_NOTIFICATION_MANUAL',
                'category': 'Data Breach Notification',
                'severity': 'Medium',
                'title': 'Manual Breach Notification Process Risk',
                'description': 'No automated breach detection/notification system detected',
                'article_reference': 'Netherlands UAVG Article 33',
                'timeline_risk': '72-hour deadline may be missed with manual processes',
                'penalty_risk': 'Up to €890K or 2% turnover for late notification',
                'recommendation': 'Consider automated breach detection and notification systems'
            })
    
    return findings

def _check_netherlands_privacy_requirements(content: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Check Netherlands-specific privacy law requirements beyond GDPR."""
    findings = []
    
    # Netherlands-specific privacy laws
    dutch_privacy_laws = {
        "telecommunications_act": r"\b(?:telecommunicatiewet|telecommunications.*act|telecom.*law)\b",
        "electronic_communications": r"\b(?:electronic.*communication|e.*communication|digital.*communication)\b",
        "consumer_protection": r"\b(?:consumer.*protection|consumentenbescherming|acm.*guidelines)\b",
        "media_law": r"\b(?:media.*law|mediawet|broadcasting.*law)\b"
    }
    
    # Dutch language requirements
    dutch_language_patterns = [
        r"\b(?:privacyverklaring|privacybeleid|gegevensbescherming|toestemming)\b",
        r"\b(?:persoonsgegevens|verwerkingsverantwoordelijke|betroffene)\b"
    ]
    
    # Data residency requirements
    data_residency_patterns = [
        r"\b(?:data.*residency|eu.*hosting|netherlands.*hosting|european.*server)\b",
        r"\b(?:data.*sovereignty|local.*storage|eu.*cloud|dutch.*datacenter)\b"
    ]
    
    applicable_laws = []
    for law, pattern in dutch_privacy_laws.items():
        if re.search(pattern, content, re.IGNORECASE):
            applicable_laws.append(law)
    
    has_dutch_language = any(re.search(pattern, content, re.IGNORECASE) for pattern in dutch_language_patterns)
    has_data_residency = any(re.search(pattern, content, re.IGNORECASE) for pattern in data_residency_patterns)
    
    if applicable_laws and not has_dutch_language:
        findings.append({
            'type': 'UAVG_DUTCH_LANGUAGE_REQUIREMENT',
            'category': 'Netherlands Privacy Requirements',
            'severity': 'Medium',
            'title': 'Dutch Language Privacy Notice Requirement',
            'description': f'Processing under {", ".join(applicable_laws)} may require Dutch language privacy notice',
            'article_reference': 'Netherlands UAVG Article 12 + Consumer Protection',
            'applicable_laws': applicable_laws,
            'recommendation': 'Provide privacy notices in Dutch for Netherlands consumers'
        })
    
    if not has_data_residency and re.search(r'\b(?:personal.*data|sensitive.*data|eu.*citizen)\b', content, re.IGNORECASE):
        findings.append({
            'type': 'UAVG_DATA_RESIDENCY_CONCERN',
            'category': 'Netherlands Privacy Requirements',
            'severity': 'Medium',
            'title': 'Netherlands Data Residency Consideration',
            'description': 'EU/Netherlands data residency not explicitly mentioned',
            'article_reference': 'Netherlands UAVG Articles 44-49',
            'market_preference': 'Netherlands organizations prefer EU/Netherlands data residency',
            'recommendation': 'Consider explicitly stating EU/Netherlands data residency'
        })
    
    return findings