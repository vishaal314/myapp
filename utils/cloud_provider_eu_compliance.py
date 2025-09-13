"""
Cloud Provider EU-Compliance Validation
Validates cloud provider EU residency and compliance requirements
"""

import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib

class CloudProviderType(Enum):
    """Types of cloud providers"""
    HYPERSCALER = "hyperscaler"        # AWS, Azure, Google Cloud
    EU_NATIVE = "eu_native"           # OVH, Scaleway, Hetzner
    SPECIALIZED = "specialized"        # AI/ML focused providers
    HYBRID = "hybrid"                 # Multi-cloud setups
    UNKNOWN = "unknown"

class ComplianceStatus(Enum):
    """Compliance status levels"""
    FULLY_COMPLIANT = "fully_compliant"
    MOSTLY_COMPLIANT = "mostly_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    UNKNOWN = "unknown"

@dataclass
class CloudProviderProfile:
    """Cloud provider compliance profile"""
    provider_name: str
    provider_type: CloudProviderType
    headquarters_country: str
    eu_data_centers: List[str]
    non_eu_access_controls: Dict[str, Any]
    operational_team_location: List[str]
    compliance_certifications: List[str]
    data_sovereignty_guarantees: Dict[str, Any]
    audit_frequency: str
    last_audit_date: Optional[datetime]
    compliance_score: float
    risk_assessment: Dict[str, Any]

@dataclass
class DataResidencyRequirement:
    """Data residency requirement specification"""
    requirement_id: str
    jurisdiction: str
    data_types: List[str]
    processing_location: str
    access_restrictions: List[str]
    audit_requirements: Dict[str, Any]
    compliance_evidence: List[str]

class CloudProviderEUComplianceValidator:
    """
    Validates cloud provider EU compliance and data sovereignty requirements
    """
    
    def __init__(self, region: str = "Netherlands"):
        self.region = region
        self.provider_database = self._load_provider_database()
        self.compliance_rules = self._load_compliance_rules()
        self.audit_requirements = self._load_audit_requirements()
        
    def _load_provider_database(self) -> Dict[str, CloudProviderProfile]:
        """Load known cloud provider compliance profiles"""
        return {
            "aws": CloudProviderProfile(
                provider_name="Amazon Web Services",
                provider_type=CloudProviderType.HYPERSCALER,
                headquarters_country="United States",
                eu_data_centers=["eu-west-1", "eu-west-2", "eu-west-3", "eu-central-1", "eu-north-1"],
                non_eu_access_controls={
                    "us_access_possible": True,
                    "government_access_risk": "High",
                    "legal_framework": "US CLOUD Act applies",
                    "mitigation_measures": ["AWS Europe Sovereign Cloud (planned)"]
                },
                operational_team_location=["United States", "Ireland", "Germany"],
                compliance_certifications=["ISO 27001", "SOC 2", "GDPR", "EU-US DPF"],
                data_sovereignty_guarantees={
                    "data_residency": "Configurable per region",
                    "encryption_keys": "Customer managed possible",
                    "access_logging": "CloudTrail available",
                    "eu_only_processing": "Not guaranteed"
                },
                audit_frequency="Annual",
                last_audit_date=datetime(2024, 6, 15),
                compliance_score=75.0,
                risk_assessment={
                    "sovereignty_risk": "Medium-High",
                    "third_country_access": "Possible under US law",
                    "mitigation_available": True
                }
            ),
            "azure": CloudProviderProfile(
                provider_name="Microsoft Azure",
                provider_type=CloudProviderType.HYPERSCALER,
                headquarters_country="United States",
                eu_data_centers=["West Europe", "North Europe", "France Central", "Germany West Central"],
                non_eu_access_controls={
                    "us_access_possible": True,
                    "government_access_risk": "High",
                    "legal_framework": "US CLOUD Act applies",
                    "mitigation_measures": ["EU Data Boundary", "Customer Lockbox"]
                },
                operational_team_location=["United States", "Ireland", "Netherlands"],
                compliance_certifications=["ISO 27001", "SOC 2", "GDPR", "EU-US DPF"],
                data_sovereignty_guarantees={
                    "data_residency": "EU Data Boundary available",
                    "encryption_keys": "Customer Key available",
                    "access_logging": "Comprehensive audit logs",
                    "eu_only_processing": "With EU Data Boundary"
                },
                audit_frequency="Bi-annual",
                last_audit_date=datetime(2024, 8, 20),
                compliance_score=78.0,
                risk_assessment={
                    "sovereignty_risk": "Medium",
                    "third_country_access": "Limited with EU Data Boundary",
                    "mitigation_available": True
                }
            ),
            "google_cloud": CloudProviderProfile(
                provider_name="Google Cloud Platform",
                provider_type=CloudProviderType.HYPERSCALER,
                headquarters_country="United States",
                eu_data_centers=["europe-west1", "europe-west2", "europe-west3", "europe-west4"],
                non_eu_access_controls={
                    "us_access_possible": True,
                    "government_access_risk": "High",
                    "legal_framework": "US CLOUD Act applies",
                    "mitigation_measures": ["Google Cloud Europe (planned)"]
                },
                operational_team_location=["United States", "Ireland", "Finland"],
                compliance_certifications=["ISO 27001", "SOC 2", "GDPR", "EU-US DPF"],
                data_sovereignty_guarantees={
                    "data_residency": "Regional data residency",
                    "encryption_keys": "Customer-managed encryption keys",
                    "access_logging": "Cloud Audit Logs",
                    "eu_only_processing": "Not guaranteed"
                },
                audit_frequency="Annual",
                last_audit_date=datetime(2024, 5, 10),
                compliance_score=73.0,
                risk_assessment={
                    "sovereignty_risk": "Medium-High",
                    "third_country_access": "Possible under US law",
                    "mitigation_available": "Limited"
                }
            ),
            "ovh": CloudProviderProfile(
                provider_name="OVHcloud",
                provider_type=CloudProviderType.EU_NATIVE,
                headquarters_country="France",
                eu_data_centers=["GRA", "SBG", "RBX", "WAW", "DE", "UK"],
                non_eu_access_controls={
                    "us_access_possible": False,
                    "government_access_risk": "Low",
                    "legal_framework": "EU law only",
                    "mitigation_measures": ["EU-only operations"]
                },
                operational_team_location=["France", "Poland", "Germany"],
                compliance_certifications=["ISO 27001", "SOC 2", "GDPR", "SecNumCloud", "ANSSI"],
                data_sovereignty_guarantees={
                    "data_residency": "Guaranteed EU-only",
                    "encryption_keys": "EU-managed keys",
                    "access_logging": "Full transparency",
                    "eu_only_processing": "Guaranteed"
                },
                audit_frequency="Bi-annual",
                last_audit_date=datetime(2024, 9, 1),
                compliance_score=95.0,
                risk_assessment={
                    "sovereignty_risk": "Very Low",
                    "third_country_access": "Not possible",
                    "mitigation_available": "Not needed"
                }
            ),
            "hetzner": CloudProviderProfile(
                provider_name="Hetzner Cloud",
                provider_type=CloudProviderType.EU_NATIVE,
                headquarters_country="Germany",
                eu_data_centers=["nbg1", "fsn1", "hel1", "ash"],
                non_eu_access_controls={
                    "us_access_possible": False,
                    "government_access_risk": "Very Low",
                    "legal_framework": "German/EU law only",
                    "mitigation_measures": ["German operations only"]
                },
                operational_team_location=["Germany"],
                compliance_certifications=["ISO 27001", "GDPR", "BSI C5"],
                data_sovereignty_guarantees={
                    "data_residency": "Germany/EU only",
                    "encryption_keys": "EU-managed",
                    "access_logging": "German standards",
                    "eu_only_processing": "Guaranteed"
                },
                audit_frequency="Annual",
                last_audit_date=datetime(2024, 7, 15),
                compliance_score=92.0,
                risk_assessment={
                    "sovereignty_risk": "Very Low",
                    "third_country_access": "Not possible",
                    "mitigation_available": "Not needed"
                }
            ),
            "scaleway": CloudProviderProfile(
                provider_name="Scaleway",
                provider_type=CloudProviderType.EU_NATIVE,
                headquarters_country="France",
                eu_data_centers=["par1", "par2", "ams1", "war1"],
                non_eu_access_controls={
                    "us_access_possible": False,
                    "government_access_risk": "Low",
                    "legal_framework": "French/EU law only",
                    "mitigation_measures": ["EU-only operations"]
                },
                operational_team_location=["France", "Netherlands"],
                compliance_certifications=["ISO 27001", "GDPR", "SecNumCloud"],
                data_sovereignty_guarantees={
                    "data_residency": "EU-only guaranteed",
                    "encryption_keys": "EU-managed",
                    "access_logging": "Full audit trail",
                    "eu_only_processing": "Guaranteed"
                },
                audit_frequency="Bi-annual",
                last_audit_date=datetime(2024, 8, 5),
                compliance_score=90.0,
                risk_assessment={
                    "sovereignty_risk": "Very Low",
                    "third_country_access": "Not possible",
                    "mitigation_available": "Not needed"
                }
            )
        }
    
    def _load_compliance_rules(self) -> Dict[str, Any]:
        """Load EU compliance rules for cloud providers"""
        return {
            "data_sovereignty_requirements": {
                "netherlands": {
                    "data_residency": "EU/EEA only",
                    "processing_teams": "EU residents preferred",
                    "government_access": "EU legal framework only",
                    "audit_frequency": "Minimum annual",
                    "encryption_requirements": "AES-256 minimum",
                    "key_management": "Customer or EU-based escrow"
                },
                "germany": {
                    "data_residency": "EU/EEA mandatory for sensitive data",
                    "processing_teams": "EU residents for sensitive operations",
                    "government_access": "German court orders only",
                    "audit_frequency": "Bi-annual for critical systems",
                    "encryption_requirements": "BSI approved algorithms",
                    "key_management": "German/EU key escrow required"
                }
            },
            "third_country_access_restrictions": {
                "us_providers": {
                    "cloud_act_risk": "High",
                    "government_access": "Possible under US law",
                    "mitigation_required": True,
                    "acceptable_mitigations": [
                        "EU-only data processing guarantees",
                        "Customer-managed encryption keys",
                        "EU sovereign cloud offerings",
                        "Contractual data sovereignty guarantees"
                    ]
                },
                "china_providers": {
                    "access_risk": "Very High",
                    "government_access": "Highly likely",
                    "mitigation_available": False,
                    "recommendation": "Avoid for EU operations"
                }
            },
            "operational_requirements": {
                "team_residency": {
                    "critical_operations": "EU residents only",
                    "support_teams": "EU preferred",
                    "management_oversight": "EU-based required",
                    "security_teams": "EU residents mandatory"
                },
                "audit_requirements": {
                    "frequency": "Minimum annual",
                    "scope": "Full infrastructure and operations",
                    "auditor_requirements": "EU-based auditors preferred",
                    "reporting": "Transparent audit reports required"
                }
            }
        }
    
    def _load_audit_requirements(self) -> Dict[str, Any]:
        """Load audit and monitoring requirements"""
        return {
            "bi_annual_requirements": [
                "Data sovereignty compliance verification",
                "Third-country access controls validation",
                "Operational team residency confirmation",
                "Encryption and key management review",
                "Incident response capability assessment",
                "Legal framework compliance check"
            ],
            "continuous_monitoring": [
                "Data location tracking",
                "Access attempt monitoring",
                "Operational team changes",
                "Certification status updates",
                "Legal framework changes",
                "Provider service changes"
            ],
            "documentation_requirements": [
                "Data processing locations",
                "Team member residency status",
                "Access control mechanisms",
                "Audit trail completeness",
                "Incident response procedures",
                "Legal compliance evidence"
            ]
        }
    
    def detect_cloud_provider_usage(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Detect cloud provider usage and assess EU compliance
        
        Args:
            content: Content to analyze for cloud provider references
            metadata: Additional metadata about the system
            
        Returns:
            List of cloud provider compliance findings
        """
        findings = []
        metadata = metadata or {}
        
        # Detect cloud providers
        detected_providers = self._identify_cloud_providers(content)
        
        for provider_name, usage_context in detected_providers.items():
            provider_profile = self.provider_database.get(provider_name.lower())
            
            if provider_profile:
                # Assess compliance for known provider
                compliance_assessment = self._assess_provider_compliance(
                    provider_profile, usage_context, metadata
                )
                findings.extend(compliance_assessment)
            else:
                # Unknown provider - flag for review
                findings.append({
                    'type': 'UNKNOWN_CLOUD_PROVIDER',
                    'category': 'Cloud Provider Compliance',
                    'provider_name': provider_name,
                    'usage_context': usage_context,
                    'risk_level': 'High',
                    'description': f'Unknown cloud provider "{provider_name}" requires compliance assessment',
                    'remediation': 'Assess EU compliance status of cloud provider',
                    'regulation': 'GDPR Article 28 + Netherlands UAVG'
                })
        
        # Check for data residency requirements
        findings.extend(self._check_data_residency_compliance(content, detected_providers))
        
        # Check for team residency requirements
        findings.extend(self._check_operational_team_compliance(content))
        
        # Check for audit scheduling
        findings.extend(self._check_audit_compliance(detected_providers))
        
        return findings
    
    def _identify_cloud_providers(self, content: str) -> Dict[str, List[str]]:
        """Identify cloud providers mentioned in content"""
        provider_patterns = {
            "aws": [
                r"\b(?:amazon\s+web\s+services|aws)\b",
                r"\b(?:ec2|s3|lambda|rds|dynamodb)\b",
                r"\b(?:us-east-1|eu-west-1|eu-central-1)\b"
            ],
            "azure": [
                r"\b(?:microsoft\s+azure|azure)\b",
                r"\b(?:azure\s+functions|azure\s+storage|azure\s+sql)\b",
                r"\b(?:westeurope|northeurope)\b"
            ],
            "google_cloud": [
                r"\b(?:google\s+cloud|gcp|google\s+compute)\b",
                r"\b(?:cloud\s+functions|cloud\s+storage|bigquery)\b",
                r"\b(?:europe-west|us-central)\b"
            ],
            "ovh": [
                r"\b(?:ovh|ovhcloud)\b",
                r"\b(?:gra|sbg|rbx|wav)\b"
            ],
            "hetzner": [
                r"\b(?:hetzner|hetzner\s+cloud)\b",
                r"\b(?:nbg1|fsn1|hel1)\b"
            ],
            "scaleway": [
                r"\b(?:scaleway)\b",
                r"\b(?:par1|par2|ams1)\b"
            ]
        }
        
        detected = {}
        for provider, patterns in provider_patterns.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, content, re.IGNORECASE)
                matches.extend(found)
            
            if matches:
                detected[provider] = matches
        
        return detected
    
    def _assess_provider_compliance(self, provider_profile: CloudProviderProfile, 
                                  usage_context: List[str], metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Assess compliance of a specific cloud provider"""
        findings = []
        
        # Check data sovereignty compliance
        sovereignty_risk = provider_profile.risk_assessment.get("sovereignty_risk", "Unknown")
        
        if sovereignty_risk in ["High", "Medium-High"]:
            findings.append({
                'type': 'DATA_SOVEREIGNTY_RISK',
                'category': 'Cloud Provider Data Sovereignty',
                'provider_name': provider_profile.provider_name,
                'provider_type': provider_profile.provider_type.value,
                'risk_level': sovereignty_risk,
                'description': f'{provider_profile.provider_name} poses data sovereignty risks',
                'sovereignty_concerns': [
                    f"Headquarters: {provider_profile.headquarters_country}",
                    f"Third-country access: {provider_profile.risk_assessment.get('third_country_access', 'Unknown')}",
                    f"Operational teams: {', '.join(provider_profile.operational_team_location)}"
                ],
                'mitigation_available': provider_profile.risk_assessment.get("mitigation_available", False),
                'mitigation_measures': provider_profile.non_eu_access_controls.get("mitigation_measures", []),
                'remediation': 'Implement data sovereignty safeguards or consider EU-native alternatives',
                'regulation': 'GDPR Article 44-49 + Netherlands UAVG data residency'
            })
        
        # Check operational team compliance
        non_eu_teams = [loc for loc in provider_profile.operational_team_location 
                       if loc not in ["Netherlands", "Germany", "France", "Ireland", "Poland", "Finland"]]
        
        if non_eu_teams:
            findings.append({
                'type': 'NON_EU_OPERATIONAL_TEAMS',
                'category': 'Cloud Provider Team Residency',
                'provider_name': provider_profile.provider_name,
                'risk_level': 'Medium',
                'description': f'{provider_profile.provider_name} has non-EU operational teams',
                'non_eu_locations': non_eu_teams,
                'compliance_risk': 'Data processing by non-EU residents',
                'remediation': 'Request EU-only team assignment or implement additional safeguards',
                'regulation': 'Netherlands UAVG operational requirements'
            })
        
        # Check audit compliance
        if provider_profile.last_audit_date:
            days_since_audit = (datetime.now() - provider_profile.last_audit_date).days
            required_frequency = 365 if provider_profile.audit_frequency == "Annual" else 182
            
            if days_since_audit > required_frequency:
                findings.append({
                    'type': 'AUDIT_OVERDUE',
                    'category': 'Cloud Provider Audit Compliance',
                    'provider_name': provider_profile.provider_name,
                    'risk_level': 'Medium',
                    'description': f'Cloud provider audit overdue by {days_since_audit - required_frequency} days',
                    'last_audit': provider_profile.last_audit_date.strftime("%Y-%m-%d"),
                    'required_frequency': provider_profile.audit_frequency,
                    'remediation': 'Schedule bi-annual compliance audit',
                    'regulation': 'GDPR Article 28 processor audit requirements'
                })
        
        # Check compliance score
        if provider_profile.compliance_score < 80:
            findings.append({
                'type': 'LOW_COMPLIANCE_SCORE',
                'category': 'Cloud Provider Overall Compliance',
                'provider_name': provider_profile.provider_name,
                'compliance_score': provider_profile.compliance_score,
                'risk_level': 'High' if provider_profile.compliance_score < 60 else 'Medium',
                'description': f'Cloud provider compliance score below threshold: {provider_profile.compliance_score}%',
                'remediation': 'Consider alternative providers with higher compliance scores',
                'regulation': 'GDPR Article 28 + Netherlands UAVG standards'
            })
        
        return findings
    
    def _check_data_residency_compliance(self, content: str, detected_providers: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Check data residency compliance requirements"""
        findings = []
        
        # Look for data residency indicators
        residency_patterns = [
            r"\b(?:data\s+residency|data\s+location|data\s+sovereignty)\b",
            r"\b(?:us-east|us-west|ap-south|ap-northeast)\b",  # Non-EU regions
            r"\b(?:china|singapore|japan|australia)\s+(?:region|datacenter)\b"
        ]
        
        non_eu_indicators = []
        for pattern in residency_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            non_eu_indicators.extend(matches)
        
        if non_eu_indicators:
            findings.append({
                'type': 'NON_EU_DATA_RESIDENCY',
                'category': 'Data Residency Compliance',
                'risk_level': 'Critical',
                'description': 'Data processing outside EU detected',
                'non_eu_indicators': non_eu_indicators,
                'detected_providers': list(detected_providers.keys()),
                'compliance_requirement': 'EU/EEA data residency required for personal data',
                'remediation': 'Configure EU-only data residency or implement adequate safeguards',
                'regulation': 'GDPR Articles 44-49 + Netherlands UAVG Article 26'
            })
        
        return findings
    
    def _check_operational_team_compliance(self, content: str) -> List[Dict[str, Any]]:
        """Check operational team residency compliance"""
        findings = []
        
        team_patterns = [
            r"\b(?:support\s+team|operations\s+team|dev\s+team)\s+(?:in|located)\s+([^.\n]+)\b",
            r"\b(?:managed\s+by|operated\s+by|staffed\s+by)\s+([^.\n]+)\b",
            r"\b(?:24/7\s+support|round.*clock)\s+(?:from|in)\s+([^.\n]+)\b"
        ]
        
        non_eu_teams = []
        for pattern in team_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                location = match.group(1).strip()
                if any(country in location.lower() for country in ["usa", "united states", "india", "china", "singapore"]):
                    non_eu_teams.append(location)
        
        if non_eu_teams:
            findings.append({
                'type': 'NON_EU_OPERATIONAL_TEAMS',
                'category': 'Operational Team Compliance',
                'risk_level': 'High',
                'description': 'Non-EU operational teams detected',
                'non_eu_team_locations': non_eu_teams,
                'compliance_risk': 'Data access by non-EU residents',
                'remediation': 'Request EU-resident teams for sensitive data operations',
                'regulation': 'Netherlands UAVG operational security requirements'
            })
        
        return findings
    
    def _check_audit_compliance(self, detected_providers: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Check audit scheduling compliance"""
        findings = []
        
        for provider_name in detected_providers.keys():
            provider_profile = self.provider_database.get(provider_name.lower())
            if provider_profile:
                # Check if bi-annual audit is due
                if provider_profile.last_audit_date:
                    next_audit_due = provider_profile.last_audit_date + timedelta(days=182)  # 6 months
                    days_until_audit = (next_audit_due - datetime.now()).days
                    
                    if days_until_audit <= 30:  # Audit due within 30 days
                        findings.append({
                            'type': 'AUDIT_DUE_SOON',
                            'category': 'Cloud Provider Audit Scheduling',
                            'provider_name': provider_profile.provider_name,
                            'risk_level': 'Medium',
                            'description': f'Bi-annual audit due within {days_until_audit} days',
                            'next_audit_due': next_audit_due.strftime("%Y-%m-%d"),
                            'audit_scope': self.audit_requirements["bi_annual_requirements"],
                            'remediation': 'Schedule bi-annual compliance audit with EU-based auditors',
                            'regulation': 'GDPR Article 28 + Netherlands UAVG audit requirements'
                        })
        
        return findings
    
    def generate_cloud_compliance_report(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive cloud provider compliance report"""
        if not findings:
            return {
                'overall_compliance': 'NO_CLOUD_USAGE_DETECTED',
                'sovereignty_status': 'NOT_APPLICABLE',
                'risk_level': 'Unknown'
            }
        
        # Categorize findings by severity
        critical_count = len([f for f in findings if f.get('risk_level') == 'Critical'])
        high_count = len([f for f in findings if f.get('risk_level') == 'High'])
        medium_count = len([f for f in findings if f.get('risk_level') == 'Medium'])
        
        # Determine overall compliance
        if critical_count > 0:
            overall_compliance = 'NON_COMPLIANT'
            sovereignty_status = 'HIGH_RISK'
            risk_level = 'Critical'
        elif high_count > 0:
            overall_compliance = 'PARTIALLY_COMPLIANT'
            sovereignty_status = 'MEDIUM_RISK'
            risk_level = 'High'
        elif medium_count > 2:
            overall_compliance = 'MOSTLY_COMPLIANT'
            sovereignty_status = 'LOW_RISK'
            risk_level = 'Medium'
        else:
            overall_compliance = 'COMPLIANT'
            sovereignty_status = 'COMPLIANT'
            risk_level = 'Low'
        
        # Extract provider information
        detected_providers = list(set(f.get('provider_name', 'Unknown') for f in findings if 'provider_name' in f))
        
        # Generate recommendations
        recommendations = []
        finding_types = set(f.get('type') for f in findings)
        
        if 'DATA_SOVEREIGNTY_RISK' in finding_types:
            recommendations.append("🏛️ Consider EU-native cloud providers for data sovereignty")
            
        if 'NON_EU_OPERATIONAL_TEAMS' in finding_types:
            recommendations.append("👥 Request EU-resident operational teams")
            
        if 'AUDIT_OVERDUE' in finding_types or 'AUDIT_DUE_SOON' in finding_types:
            recommendations.append("📅 Schedule bi-annual compliance audits")
            
        if 'NON_EU_DATA_RESIDENCY' in finding_types:
            recommendations.append("🌍 Configure EU-only data residency")
            
        recommendations.extend([
            "📋 Implement comprehensive cloud provider assessment",
            "🔒 Validate data sovereignty guarantees",
            "📊 Monitor compliance status continuously"
        ])
        
        return {
            'overall_compliance': overall_compliance,
            'sovereignty_status': sovereignty_status,
            'risk_level': risk_level,
            'total_findings': len(findings),
            'critical_findings': critical_count,
            'high_risk_findings': high_count,
            'medium_risk_findings': medium_count,
            'detected_providers': detected_providers,
            'recommendations': recommendations,
            'next_audit_due': self._calculate_next_audit_due(detected_providers),
            'compliance_score': max(0, 100 - (critical_count * 30 + high_count * 20 + medium_count * 10)),
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_next_audit_due(self, detected_providers: List[str]) -> str:
        """Calculate next audit due date"""
        next_audits = []
        
        for provider_name in detected_providers:
            provider_key = provider_name.lower().replace(" ", "_")
            provider_profile = self.provider_database.get(provider_key)
            
            if provider_profile and provider_profile.last_audit_date:
                next_audit = provider_profile.last_audit_date + timedelta(days=182)
                next_audits.append(next_audit)
        
        if next_audits:
            return min(next_audits).strftime("%Y-%m-%d")
        else:
            return "Schedule initial audit"
    
    def assess_provider_alternatives(self, current_provider: str, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Assess alternative cloud providers that meet EU compliance requirements"""
        alternatives = []
        
        for provider_key, profile in self.provider_database.items():
            if provider_key == current_provider.lower():
                continue
                
            # Score provider against requirements
            score = self._score_provider_fit(profile, requirements)
            
            alternatives.append({
                'provider_name': profile.provider_name,
                'provider_type': profile.provider_type.value,
                'compliance_score': profile.compliance_score,
                'sovereignty_risk': profile.risk_assessment.get('sovereignty_risk', 'Unknown'),
                'fit_score': score,
                'key_benefits': self._get_provider_benefits(profile),
                'migration_complexity': self._assess_migration_complexity(current_provider, provider_key),
                'cost_impact': self._estimate_cost_impact(profile)
            })
        
        # Sort by fit score and compliance
        alternatives.sort(key=lambda x: (x['fit_score'], x['compliance_score']), reverse=True)
        
        return alternatives[:5]  # Top 5 alternatives
    
    def _score_provider_fit(self, profile: CloudProviderProfile, requirements: Dict[str, Any]) -> float:
        """Score how well a provider fits the requirements"""
        score = 0.0
        
        # Data sovereignty requirement (40% weight)
        if requirements.get('data_sovereignty_required', False):
            if profile.risk_assessment.get('sovereignty_risk') in ['Very Low', 'Low']:
                score += 40
            elif profile.risk_assessment.get('sovereignty_risk') == 'Medium':
                score += 20
        
        # EU operational teams (20% weight)
        eu_team_ratio = len([loc for loc in profile.operational_team_location 
                           if loc in ['Netherlands', 'Germany', 'France', 'Ireland']]) / len(profile.operational_team_location)
        score += eu_team_ratio * 20
        
        # Compliance certifications (20% weight)
        required_certs = requirements.get('required_certifications', [])
        if required_certs:
            cert_match_ratio = len(set(required_certs) & set(profile.compliance_certifications)) / len(required_certs)
            score += cert_match_ratio * 20
        else:
            score += 20  # Full score if no specific requirements
        
        # Audit frequency (10% weight)
        if profile.audit_frequency == "Bi-annual":
            score += 10
        elif profile.audit_frequency == "Annual":
            score += 5
        
        # Overall compliance score (10% weight)
        score += (profile.compliance_score / 100) * 10
        
        return round(score, 1)
    
    def _get_provider_benefits(self, profile: CloudProviderProfile) -> List[str]:
        """Get key benefits of a cloud provider"""
        benefits = []
        
        if profile.risk_assessment.get('sovereignty_risk') in ['Very Low', 'Low']:
            benefits.append("Strong data sovereignty guarantees")
            
        if profile.provider_type == CloudProviderType.EU_NATIVE:
            benefits.append("EU-native provider with local expertise")
            
        if "SecNumCloud" in profile.compliance_certifications:
            benefits.append("French SecNumCloud certification")
            
        if profile.audit_frequency == "Bi-annual":
            benefits.append("Frequent compliance audits")
            
        if profile.compliance_score >= 90:
            benefits.append("Excellent compliance track record")
            
        return benefits
    
    def _assess_migration_complexity(self, current_provider: str, target_provider: str) -> str:
        """Assess migration complexity between providers"""
        hyperscalers = ["aws", "azure", "google_cloud"]
        eu_native = ["ovh", "hetzner", "scaleway"]
        
        if current_provider in hyperscalers and target_provider in hyperscalers:
            return "Medium - Similar services but different APIs"
        elif current_provider in hyperscalers and target_provider in eu_native:
            return "High - Significant architectural changes required"
        elif current_provider in eu_native and target_provider in hyperscalers:
            return "High - Feature set differences"
        else:
            return "Medium - Similar EU-native providers"
    
    def _estimate_cost_impact(self, profile: CloudProviderProfile) -> str:
        """Estimate cost impact of using this provider"""
        if profile.provider_type == CloudProviderType.EU_NATIVE:
            return "Potentially lower costs with better compliance"
        elif profile.provider_type == CloudProviderType.HYPERSCALER:
            return "Standard market rates with premium compliance features"
        else:
            return "Variable - depends on specific requirements"