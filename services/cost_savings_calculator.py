"""
Cost Savings Calculator for DataGuardian Pro
Calculates monetary value of compliance findings across all scanner types
"""

import logging
from typing import Dict, List, Any, Tuple
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class ComplianceViolationType(Enum):
    """Types of compliance violations with associated costs"""
    GDPR_PERSONAL_DATA = "gdpr_personal_data"
    GDPR_SENSITIVE_DATA = "gdpr_sensitive_data"
    GDPR_CONSENT_VIOLATION = "gdpr_consent_violation"
    GDPR_DATA_BREACH = "gdpr_data_breach"
    GDPR_RIGHT_TO_ERASURE = "gdpr_right_to_erasure"
    GDPR_DATA_PORTABILITY = "gdpr_data_portability"
    BSN_EXPOSURE = "bsn_exposure"
    COOKIE_CONSENT_VIOLATION = "cookie_consent_violation"
    DARK_PATTERN_DETECTION = "dark_pattern_detection"
    AI_BIAS_VIOLATION = "ai_bias_violation"
    AI_TRANSPARENCY_VIOLATION = "ai_transparency_violation"
    SOC2_SECURITY_CONTROL = "soc2_security_control"
    DATA_MINIMIZATION = "data_minimization"
    UNAUTHORIZED_TRACKING = "unauthorized_tracking"
    CROSS_BORDER_TRANSFER = "cross_border_transfer"
    SUSTAINABILITY_VIOLATION = "sustainability_violation"

class CostSavingsCalculator:
    """Calculate cost savings from compliance findings"""
    
    def __init__(self, region: str = "Netherlands"):
        self.region = region
        self.base_penalties = self._initialize_base_penalties()
        self.implementation_costs = self._initialize_implementation_costs()
        self.operational_costs = self._initialize_operational_costs()
    
    def _initialize_base_penalties(self) -> Dict[ComplianceViolationType, Dict[str, Dict[str, float]]]:
        """Initialize base penalty amounts by region and violation type"""
        return {
            ComplianceViolationType.GDPR_PERSONAL_DATA: {
                "Netherlands": {"min": 50000, "max": 20000000, "avg": 2500000},
                "Germany": {"min": 75000, "max": 20000000, "avg": 3000000},
                "France": {"min": 60000, "max": 20000000, "avg": 2800000},
                "Belgium": {"min": 45000, "max": 20000000, "avg": 2200000},
                "Europe": {"min": 50000, "max": 20000000, "avg": 2500000}
            },
            ComplianceViolationType.GDPR_SENSITIVE_DATA: {
                "Netherlands": {"min": 100000, "max": 20000000, "avg": 4000000},
                "Germany": {"min": 150000, "max": 20000000, "avg": 5000000},
                "France": {"min": 120000, "max": 20000000, "avg": 4500000},
                "Belgium": {"min": 90000, "max": 20000000, "avg": 3500000},
                "Europe": {"min": 100000, "max": 20000000, "avg": 4000000}
            },
            ComplianceViolationType.GDPR_CONSENT_VIOLATION: {
                "Netherlands": {"min": 25000, "max": 10000000, "avg": 1200000},
                "Germany": {"min": 35000, "max": 10000000, "avg": 1500000},
                "France": {"min": 30000, "max": 10000000, "avg": 1350000},
                "Belgium": {"min": 20000, "max": 10000000, "avg": 1000000},
                "Europe": {"min": 25000, "max": 10000000, "avg": 1200000}
            },
            ComplianceViolationType.BSN_EXPOSURE: {
                "Netherlands": {"min": 150000, "max": 25000000, "avg": 5000000},
                "Germany": {"min": 0, "max": 0, "avg": 0},  # BSN specific to Netherlands
                "France": {"min": 0, "max": 0, "avg": 0},
                "Belgium": {"min": 0, "max": 0, "avg": 0},
                "Europe": {"min": 50000, "max": 5000000, "avg": 1000000}
            },
            ComplianceViolationType.COOKIE_CONSENT_VIOLATION: {
                "Netherlands": {"min": 15000, "max": 5000000, "avg": 750000},
                "Germany": {"min": 20000, "max": 5000000, "avg": 900000},
                "France": {"min": 18000, "max": 5000000, "avg": 850000},
                "Belgium": {"min": 12000, "max": 5000000, "avg": 650000},
                "Europe": {"min": 15000, "max": 5000000, "avg": 750000}
            },
            ComplianceViolationType.AI_BIAS_VIOLATION: {
                "Netherlands": {"min": 200000, "max": 35000000, "avg": 7500000},
                "Germany": {"min": 300000, "max": 35000000, "avg": 10000000},
                "France": {"min": 250000, "max": 35000000, "avg": 8500000},
                "Belgium": {"min": 180000, "max": 35000000, "avg": 6500000},
                "Europe": {"min": 200000, "max": 35000000, "avg": 7500000}
            },
            ComplianceViolationType.SOC2_SECURITY_CONTROL: {
                "Netherlands": {"min": 75000, "max": 15000000, "avg": 3000000},
                "Germany": {"min": 100000, "max": 15000000, "avg": 3500000},
                "France": {"min": 85000, "max": 15000000, "avg": 3250000},
                "Belgium": {"min": 65000, "max": 15000000, "avg": 2750000},
                "Europe": {"min": 75000, "max": 15000000, "avg": 3000000}
            },
            ComplianceViolationType.SUSTAINABILITY_VIOLATION: {
                "Netherlands": {"min": 50000, "max": 10000000, "avg": 2000000},
                "Germany": {"min": 75000, "max": 12000000, "avg": 2500000},
                "France": {"min": 60000, "max": 11000000, "avg": 2250000},
                "Belgium": {"min": 45000, "max": 9000000, "avg": 1750000},
                "Europe": {"min": 50000, "max": 10000000, "avg": 2000000}
            }
        }
    
    def _initialize_implementation_costs(self) -> Dict[str, float]:
        """Initialize implementation costs by finding type"""
        return {
            "data_encryption": 25000,
            "access_control": 35000,
            "consent_management": 45000,
            "data_anonymization": 40000,
            "audit_logging": 20000,
            "staff_training": 15000,
            "policy_development": 30000,
            "technical_remediation": 50000,
            "legal_consultation": 75000,
            "security_implementation": 60000,
            "ai_bias_mitigation": 100000,
            "sustainability_optimization": 80000,
            "cookie_consent_system": 25000,
            "data_subject_rights": 55000,
            "cross_border_compliance": 65000
        }
    
    def _initialize_operational_costs(self) -> Dict[str, float]:
        """Initialize ongoing operational costs"""
        return {
            "compliance_monitoring": 120000,  # Annual
            "staff_overhead": 180000,        # Annual
            "audit_costs": 50000,           # Annual
            "legal_fees": 100000,           # Annual
            "system_maintenance": 80000,     # Annual
            "training_updates": 25000,       # Annual
            "certification_renewal": 40000,  # Annual
            "consultant_fees": 150000,      # Annual
            "technology_updates": 60000,     # Annual
            "incident_response": 200000      # Per incident
        }
    
    def calculate_finding_cost_savings(self, finding: Dict[str, Any], scanner_type: str) -> Dict[str, Any]:
        """Calculate cost savings for a specific finding"""
        
        violation_type = self._map_finding_to_violation_type(finding, scanner_type)
        severity = finding.get('severity', 'medium').lower()
        
        # Base penalty calculation
        penalty_data = self.base_penalties.get(violation_type, {}).get(self.region, {"min": 10000.0, "max": 1000000.0, "avg": 250000.0})
        
        # Adjust penalty based on severity
        severity_multipliers = {
            "critical": 1.0,
            "high": 0.7,
            "medium": 0.4,
            "low": 0.2
        }
        
        multiplier = severity_multipliers.get(severity, 0.4)
        potential_penalty = float(penalty_data["avg"]) * multiplier
        
        # Implementation cost to fix
        implementation_cost = self._calculate_implementation_cost(finding, scanner_type)
        
        # Operational cost savings (annual)
        operational_savings = self._calculate_operational_savings(finding, scanner_type)
        
        # Net savings calculation
        immediate_savings = potential_penalty - implementation_cost
        annual_savings = operational_savings
        three_year_savings = immediate_savings + (operational_savings * 3)
        
        return {
            "potential_penalty": potential_penalty,
            "implementation_cost": implementation_cost,
            "immediate_savings": max(0, immediate_savings),
            "annual_operational_savings": operational_savings,
            "three_year_total_savings": max(0, three_year_savings),
            "roi_percentage": ((three_year_savings / max(implementation_cost, 1)) * 100) if implementation_cost > 0 else 0,
            "payback_period_months": max(1, implementation_cost / max(operational_savings / 12, 1)) if operational_savings > 0 else 999,
            "severity_adjusted": True,
            "violation_type": violation_type.value,
            "currency": "EUR"
        }
    
    def _map_finding_to_violation_type(self, finding: Dict[str, Any], scanner_type: str) -> ComplianceViolationType:
        """Map scanner finding to compliance violation type"""
        
        finding_type = finding.get('type', '').lower()
        finding_pattern = finding.get('pattern', '').lower()
        finding_title = finding.get('title', '').lower()
        
        # Scanner-specific mapping
        if scanner_type == 'code':
            if 'bsn' in finding_pattern or 'burgerservicenummer' in finding_title:
                return ComplianceViolationType.BSN_EXPOSURE
            elif any(pattern in finding_pattern for pattern in ['email', 'phone', 'address']):
                return ComplianceViolationType.GDPR_PERSONAL_DATA
            elif any(pattern in finding_pattern for pattern in ['credit_card', 'passport', 'ssn']):
                return ComplianceViolationType.GDPR_SENSITIVE_DATA
            else:
                return ComplianceViolationType.GDPR_PERSONAL_DATA
        
        elif scanner_type == 'website':
            if 'cookie' in finding_title or 'tracking' in finding_title:
                return ComplianceViolationType.COOKIE_CONSENT_VIOLATION
            elif 'dark_pattern' in finding_title:
                return ComplianceViolationType.DARK_PATTERN_DETECTION
            elif 'consent' in finding_title:
                return ComplianceViolationType.GDPR_CONSENT_VIOLATION
            else:
                return ComplianceViolationType.UNAUTHORIZED_TRACKING
        
        elif scanner_type == 'ai_model':
            if 'bias' in finding_title:
                return ComplianceViolationType.AI_BIAS_VIOLATION
            elif 'transparency' in finding_title or 'explainability' in finding_title:
                return ComplianceViolationType.AI_TRANSPARENCY_VIOLATION
            else:
                return ComplianceViolationType.AI_BIAS_VIOLATION
        
        elif scanner_type == 'soc2':
            return ComplianceViolationType.SOC2_SECURITY_CONTROL
        
        elif scanner_type == 'sustainability':
            return ComplianceViolationType.SUSTAINABILITY_VIOLATION
        
        elif scanner_type in ['database', 'document', 'image']:
            if 'sensitive' in finding_title or 'confidential' in finding_title:
                return ComplianceViolationType.GDPR_SENSITIVE_DATA
            else:
                return ComplianceViolationType.GDPR_PERSONAL_DATA
        
        elif scanner_type == 'api':
            return ComplianceViolationType.GDPR_DATA_BREACH
        
        else:
            return ComplianceViolationType.GDPR_PERSONAL_DATA
    
    def _calculate_implementation_cost(self, finding: Dict[str, Any], scanner_type: str) -> float:
        """Calculate implementation cost to remediate the finding"""
        
        base_costs = {
            'code': 15000,
            'website': 10000,
            'ai_model': 50000,
            'soc2': 25000,
            'database': 20000,
            'document': 8000,
            'image': 12000,
            'api': 18000,
            'dpia': 30000,
            'sustainability': 35000
        }
        
        base_cost = base_costs.get(scanner_type, 15000)
        
        # Severity adjustment
        severity = finding.get('severity', 'medium').lower()
        severity_multipliers = {
            'critical': 2.0,
            'high': 1.5,
            'medium': 1.0,
            'low': 0.5
        }
        
        return base_cost * severity_multipliers.get(severity, 1.0)
    
    def _calculate_operational_savings(self, finding: Dict[str, Any], scanner_type: str) -> float:
        """Calculate annual operational cost savings"""
        
        base_savings = {
            'code': 50000,
            'website': 30000,
            'ai_model': 150000,
            'soc2': 80000,
            'database': 60000,
            'document': 25000,
            'image': 35000,
            'api': 45000,
            'dpia': 100000,
            'sustainability': 120000
        }
        
        return base_savings.get(scanner_type, 40000)
    
    def calculate_total_scan_savings(self, scan_results: Dict[str, Any], scanner_type: str) -> Dict[str, Any]:
        """Calculate total cost savings for entire scan"""
        
        findings = scan_results.get('findings', [])
        
        if not findings:
            return {
                "total_potential_penalties": 0,
                "total_implementation_costs": 0,
                "total_immediate_savings": 0,
                "total_annual_savings": 0,
                "total_three_year_savings": 0,
                "findings_count": 0,
                "average_roi": 0,
                "currency": "EUR"
            }
        
        total_penalties = 0
        total_implementation = 0
        total_immediate = 0
        total_annual = 0
        total_three_year = 0
        roi_values = []
        
        for finding in findings:
            savings = self.calculate_finding_cost_savings(finding, scanner_type)
            
            total_penalties += savings["potential_penalty"]
            total_implementation += savings["implementation_cost"]
            total_immediate += savings["immediate_savings"]
            total_annual += savings["annual_operational_savings"]
            total_three_year += savings["three_year_total_savings"]
            
            if savings["roi_percentage"] > 0:
                roi_values.append(savings["roi_percentage"])
        
        return {
            "total_potential_penalties": total_penalties,
            "total_implementation_costs": total_implementation,
            "total_immediate_savings": total_immediate,
            "total_annual_savings": total_annual,
            "total_three_year_savings": total_three_year,
            "findings_count": len(findings),
            "average_roi": sum(roi_values) / len(roi_values) if roi_values else 0,
            "currency": "EUR",
            "region": self.region,
            "scanner_type": scanner_type
        }
    
    def format_cost_savings_summary(self, savings: Dict[str, Any]) -> str:
        """Format cost savings summary for reports"""
        
        if savings["findings_count"] == 0:
            return "No compliance findings detected - system appears compliant."
        
        return f"""
💰 COST SAVINGS ANALYSIS
        
Total Potential GDPR Penalties Avoided: €{savings['total_potential_penalties']:,.2f}
Implementation Investment Required: €{savings['total_implementation_costs']:,.2f}
        
IMMEDIATE SAVINGS: €{savings['total_immediate_savings']:,.2f}
Annual Operational Savings: €{savings['total_annual_savings']:,.2f}
3-Year Total Value: €{savings['total_three_year_savings']:,.2f}
        
Return on Investment: {savings['average_roi']:.1f}%
Findings Addressed: {savings['findings_count']} compliance issues
        
💡 DataGuardian Pro identifies compliance issues that could result in 
€{savings['total_potential_penalties']:,.0f} in penalties. Early remediation 
provides €{savings['total_three_year_savings']:,.0f} in total value over 3 years.
        """
    
    def get_cost_comparison_oneTrust(self, scanner_type: str, findings_count: int) -> Dict[str, Any]:
        """Compare costs with OneTrust implementation"""
        
        # OneTrust typical costs
        onetrust_costs = {
            "annual_license": 240000,    # €20K/month average
            "implementation": 150000,    # One-time setup
            "consulting": 200000,        # Annual consulting
            "training": 50000,          # Annual training
            "maintenance": 80000        # Annual maintenance
        }
        
        onetrust_three_year = (onetrust_costs["annual_license"] * 3 + 
                              onetrust_costs["implementation"] +
                              onetrust_costs["consulting"] * 3 +
                              onetrust_costs["training"] * 3 +
                              onetrust_costs["maintenance"] * 3)
        
        # DataGuardian Pro costs (from pricing tiers)
        dataguardian_annual = 3000  # €250/month average
        dataguardian_three_year = dataguardian_annual * 3
        
        cost_savings = onetrust_three_year - dataguardian_three_year
        savings_percentage = (cost_savings / onetrust_three_year) * 100
        
        return {
            "onetrust_three_year": onetrust_three_year,
            "dataguardian_three_year": dataguardian_three_year,
            "absolute_savings": cost_savings,
            "savings_percentage": savings_percentage,
            "currency": "EUR"
        }

def integrate_cost_savings_into_report(scan_results: Dict[str, Any], scanner_type: str, region: str = "Netherlands") -> Dict[str, Any]:
    """Integrate cost savings analysis into scan report"""
    
    calculator = CostSavingsCalculator(region)
    
    # Calculate cost savings
    cost_savings = calculator.calculate_total_scan_savings(scan_results, scanner_type)
    
    # Add individual finding cost analysis
    enhanced_findings = []
    for finding in scan_results.get('findings', []):
        finding_savings = calculator.calculate_finding_cost_savings(finding, scanner_type)
        enhanced_finding = finding.copy()
        enhanced_finding['cost_savings'] = finding_savings
        enhanced_findings.append(enhanced_finding)
    
    # Get OneTrust comparison
    onetrust_comparison = calculator.get_cost_comparison_oneTrust(
        scanner_type, 
        len(scan_results.get('findings', []))
    )
    
    # Enhance scan results
    enhanced_results = scan_results.copy()
    enhanced_results['findings'] = enhanced_findings
    enhanced_results['cost_savings_analysis'] = cost_savings
    enhanced_results['cost_savings_summary'] = calculator.format_cost_savings_summary(cost_savings)
    enhanced_results['onetrust_comparison'] = onetrust_comparison
    enhanced_results['generated_with_cost_analysis'] = True
    enhanced_results['cost_analysis_timestamp'] = datetime.now().isoformat()
    
    return enhanced_results