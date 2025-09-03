"""
EU AI Act 2025 Compliance Module

This module provides detection and validation for EU AI Act compliance requirements
including high-risk AI systems, prohibited practices, GPAI model obligations, and transparency requirements.

Timeline Compliance:
- Prohibited practices: Enforced since February 2, 2025
- GPAI model rules: Enforced since August 2, 2025  
- High-risk systems: Full enforcement by August 2, 2027
- Maximum penalties: €35M or 7% of global turnover
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime

# EU AI Act Risk Categories
AI_RISK_CATEGORIES = {
    "prohibited": [
        "subliminal techniques",
        "social scoring", 
        "real-time biometric identification",
        "emotion recognition in workplace",
        "biometric categorisation", 
        "indiscriminate facial recognition",
        "manipulative ai targeting vulnerable groups",
        "deceptive ai practices",
        "exploitative ai systems"
    ],
    "gpai_models": [
        "general purpose ai models",
        "foundation models",
        "large language models", 
        "multimodal ai systems",
        "systemic risk models",
        "computational threshold models"
    ],
    "high_risk": [
        "biometric identification",
        "critical infrastructure",
        "education and vocational training",
        "employment and worker management",
        "access to essential services",
        "law enforcement",
        "migration and border control",
        "justice and democratic processes"
    ],
    "limited_risk": [
        "chatbots",
        "ai systems that interact with humans",
        "emotion recognition systems",
        "biometric categorisation systems",
        "ai systems that generate content"
    ]
}

def detect_ai_act_violations(content: str, document_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Detect EU AI Act compliance violations in document content.
    
    Args:
        content: Document content to analyze
        document_metadata: Additional metadata about the document
        
    Returns:
        List of AI Act compliance findings
    """
    findings = []
    
    # Check for prohibited AI practices
    findings.extend(_detect_prohibited_practices(content))
    
    # Check for high-risk AI systems
    findings.extend(_detect_high_risk_systems(content))
    
    # Check for transparency obligations
    findings.extend(_detect_transparency_violations(content))
    
    # Check for fundamental rights impact
    findings.extend(_detect_fundamental_rights_impact(content))
    
    # Check for algorithmic accountability
    findings.extend(_detect_algorithmic_accountability(content))
    
    # Check for GPAI model compliance (August 2025 requirements)
    findings.extend(_detect_gpai_compliance(content))
    
    return findings

def _detect_prohibited_practices(content: str) -> List[Dict[str, Any]]:
    """Detect prohibited AI practices under EU AI Act Article 5."""
    findings = []
    
    prohibited_patterns = {
        "subliminal_techniques": r"\b(?:subliminal|subconscious|unconscious)\s+(?:influence|manipulation|techniques)\b",
        "social_scoring": r"\b(?:social\s+scor|citizen\s+scor|behavioral\s+scor|reputation\s+system)\b",
        "biometric_mass_surveillance": r"\b(?:mass\s+surveillance|indiscriminate\s+monitoring|bulk\s+biometric)\b",
        "emotion_manipulation": r"\b(?:emotion(?:al)?\s+(?:manipulation|exploit|influence)|psychological\s+manipulation)\b"
    }
    
    for violation_type, pattern in prohibited_patterns.items():
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            findings.append({
                'type': 'AI_ACT_PROHIBITED',
                'category': violation_type.replace('_', ' ').title(),
                'value': match.group(),
                'risk_level': 'Critical',
                'regulation': 'EU AI Act Article 5',
                'description': f"Prohibited AI practice detected: {violation_type.replace('_', ' ')}",
                'location': f"Position {match.start()}-{match.end()}",
                'remediation': "Remove or modify system to eliminate prohibited practices"
            })
    
    return findings

def _detect_high_risk_systems(content: str) -> List[Dict[str, Any]]:
    """Detect high-risk AI systems under EU AI Act Annex III."""
    findings = []
    
    high_risk_patterns = {
        "biometric_identification": r"\b(?:facial\s+recognition|biometric\s+identification|fingerprint\s+matching)\b",
        "employment_ai": r"\b(?:recruitment\s+ai|hiring\s+algorithm|cv\s+screening|employee\s+monitoring)\b",
        "education_ai": r"\b(?:educational\s+ai|student\s+assessment|learning\s+analytics|academic\s+scoring)\b",
        "credit_scoring": r"\b(?:credit\s+scoring|loan\s+assessment|financial\s+risk\s+model)\b",
        "healthcare_ai": r"\b(?:medical\s+diagnosis|healthcare\s+ai|clinical\s+decision|patient\s+risk)\b"
    }
    
    for system_type, pattern in high_risk_patterns.items():
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            findings.append({
                'type': 'AI_ACT_HIGH_RISK',
                'category': system_type.replace('_', ' ').title(),
                'value': match.group(),
                'risk_level': 'High',
                'regulation': 'EU AI Act Annex III',
                'description': f"High-risk AI system detected: {system_type.replace('_', ' ')}",
                'location': f"Position {match.start()}-{match.end()}",
                'compliance_requirements': [
                    "Risk management system required",
                    "High-quality training data needed",
                    "Transparency and documentation required",
                    "Human oversight mandatory",
                    "Accuracy and robustness testing required"
                ]
            })
    
    return findings

def _detect_transparency_violations(content: str) -> List[Dict[str, Any]]:
    """Detect transparency obligation violations under EU AI Act Article 13."""
    findings = []
    
    # Check for AI systems interacting with humans without disclosure
    interaction_patterns = [
        r"\b(?:chatbot|virtual\s+assistant|ai\s+agent)\b",
        r"\b(?:automated\s+(?:response|system|decision))\b",
        r"\b(?:machine\s+learning|artificial\s+intelligence)\b"
    ]
    
    transparency_indicators = [
        r"\b(?:this\s+is\s+an?\s+ai|powered\s+by\s+ai|ai\s+system|automated\s+system)\b",
        r"\b(?:human\s+oversight|human\s+review|manual\s+verification)\b"
    ]
    
    has_ai_system = any(re.search(pattern, content, re.IGNORECASE) for pattern in interaction_patterns)
    has_transparency_notice = any(re.search(pattern, content, re.IGNORECASE) for pattern in transparency_indicators)
    
    if has_ai_system and not has_transparency_notice:
        findings.append({
            'type': 'AI_ACT_TRANSPARENCY',
            'category': 'Transparency Obligation',
            'value': 'AI system without disclosure',
            'risk_level': 'Medium',
            'regulation': 'EU AI Act Article 13',
            'description': "AI system detected without proper transparency disclosure",
            'remediation': "Add clear disclosure that users are interacting with an AI system"
        })
    
    return findings

def _detect_fundamental_rights_impact(content: str) -> List[Dict[str, Any]]:
    """Detect potential fundamental rights impacts under EU AI Act."""
    findings = []
    
    rights_impact_patterns = {
        "privacy_invasion": r"\b(?:privacy\s+violation|data\s+mining|behavioral\s+tracking)\b",
        "discrimination": r"\b(?:discriminat|bias|unfair\s+treatment|algorithmic\s+bias)\b",
        "freedom_expression": r"\b(?:content\s+moderation|speech\s+filtering|censorship)\b",
        "due_process": r"\b(?:automated\s+decision|algorithmic\s+justice|due\s+process)\b"
    }
    
    for impact_type, pattern in rights_impact_patterns.items():
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            findings.append({
                'type': 'AI_ACT_FUNDAMENTAL_RIGHTS',
                'category': impact_type.replace('_', ' ').title(),
                'value': match.group(),
                'risk_level': 'High',
                'regulation': 'EU AI Act Article 29',
                'description': f"Potential fundamental rights impact: {impact_type.replace('_', ' ')}",
                'location': f"Position {match.start()}-{match.end()}",
                'requirements': [
                    "Fundamental rights impact assessment required",
                    "Safeguards and mitigation measures needed",
                    "Regular monitoring and evaluation required"
                ]
            })
    
    return findings

def _detect_algorithmic_accountability(content: str) -> List[Dict[str, Any]]:
    """Detect algorithmic accountability requirements."""
    findings = []
    
    accountability_patterns = {
        "decision_making": r"\b(?:algorithmic\s+decision|automated\s+decision|ai\s+decision)\b",
        "model_governance": r"\b(?:model\s+governance|ai\s+governance|algorithm\s+oversight)\b",
        "audit_trail": r"\b(?:audit\s+trail|decision\s+log|traceability)\b",
        "explainability": r"\b(?:explainable\s+ai|interpretable|model\s+explanation)\b"
    }
    
    has_decision_making = bool(re.search(accountability_patterns["decision_making"], content, re.IGNORECASE))
    has_governance = any(re.search(pattern, content, re.IGNORECASE) 
                        for pattern in list(accountability_patterns.values())[1:])
    
    if has_decision_making and not has_governance:
        findings.append({
            'type': 'AI_ACT_ACCOUNTABILITY',
            'category': 'Algorithmic Accountability',
            'value': 'Decision-making without governance',
            'risk_level': 'Medium',
            'regulation': 'EU AI Act Article 14-15',
            'description': "Algorithmic decision-making detected without adequate governance framework",
            'requirements': [
                "Establish algorithmic governance framework",
                "Implement decision audit trails",
                "Ensure explainability mechanisms",
                "Regular algorithmic impact assessments"
            ]
        })
    
    return findings

def generate_ai_act_compliance_report(findings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate a comprehensive AI Act compliance report."""
    
    if not findings:
        findings = []
    
    risk_distribution = {
        'Critical': len([f for f in findings if f.get('risk_level') == 'Critical']),
        'High': len([f for f in findings if f.get('risk_level') == 'High']),
        'Medium': len([f for f in findings if f.get('risk_level') == 'Medium']),
        'Low': len([f for f in findings if f.get('risk_level') == 'Low'])
    }
    
    # Calculate compliance score
    total_findings = len(findings)
    critical_findings = risk_distribution['Critical']
    high_findings = risk_distribution['High']
    
    if total_findings == 0:
        compliance_score = 100
    else:
        # Severe penalty for critical/prohibited practices
        score_deduction = (critical_findings * 40) + (high_findings * 20) + (risk_distribution['Medium'] * 10)
        compliance_score = max(0, 100 - score_deduction)
    
    recommendations = []
    if critical_findings > 0:
        recommendations.append("Immediately address prohibited AI practices identified")
    if high_findings > 0:
        recommendations.append("Implement required safeguards for high-risk AI systems")
    if risk_distribution['Medium'] > 0:
        recommendations.append("Enhance transparency and accountability measures")
    
    recommendations.extend([
        "Conduct regular AI Act compliance assessments",
        "Establish AI governance framework with clear responsibilities",
        "Implement continuous monitoring of AI systems",
        "Train staff on EU AI Act requirements"
    ])
    
    return {
        'assessment_date': datetime.now().isoformat(),
        'total_findings': total_findings,
        'risk_distribution': risk_distribution,
        'compliance_score': compliance_score,
        'compliance_status': 'Non-Compliant' if critical_findings > 0 else 
                           'Needs Review' if high_findings > 0 else 'Compliant',
        'findings': findings,
        'recommendations': recommendations,
        'next_assessment_due': (datetime.now().replace(day=1, month=datetime.now().month + 3 if datetime.now().month <= 9 else datetime.now().month - 9, year=datetime.now().year + 1 if datetime.now().month > 9 else datetime.now().year)).isoformat()
    }

def _detect_gpai_compliance(content: str) -> List[Dict[str, Any]]:
    """Detect General-Purpose AI model compliance issues (August 2025 requirements)."""
    findings = []
    
    gpai_patterns = {
        "foundation_model": r"foundation\s+model|general\s+purpose|large\s+language\s+model|llm|gpt|bert|transformer",
        "computational_threshold": r"flops|compute|training\s+cost|parameter\s+count|model\s+size",
        "systemic_risk": r"systemic\s+risk|high\s+impact|widespread\s+deployment|capability\s+evaluation",
        "copyright_disclosure": r"training\s+data|copyrighted\s+content|intellectual\s+property|data\s+sources",
        "transparency_requirements": r"model\s+documentation|technical\s+specification|capability\s+assessment|risk\s+evaluation"
    }
    
    for pattern_name, pattern in gpai_patterns.items():
        matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            finding = {
                'type': 'AI_ACT_GPAI_COMPLIANCE',
                'category': 'GPAI Model Requirements',
                'severity': 'High',
                'title': f'GPAI Model Compliance Assessment Required',
                'description': f'General-Purpose AI model detected requiring compliance with August 2025 requirements: {pattern_name.replace("_", " ").title()}',
                'location': f'Position {match.start()}-{match.end()}',
                'matched_text': match.group(),
                'article_reference': 'EU AI Act Articles 51-55 (GPAI Models)',
                'compliance_deadline': 'August 2, 2025 (Effective)',
                'penalty_risk': 'Up to €15M or 3% global turnover',
                'remediation': 'Implement GPAI transparency, documentation, and risk assessment requirements'
            }
            findings.append(finding)
    
    return findings