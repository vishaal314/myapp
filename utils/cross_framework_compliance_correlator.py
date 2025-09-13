"""
Cross-Framework Compliance Correlation Engine

This module provides correlation capabilities across GDPR, AI Act, UAVG, SOC2 Security, 
and Sustainability frameworks, connecting previously isolated scanner findings into 
a unified compliance assessment while preserving core design functionalities.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

# Import centralized logging
try:
    from utils.centralized_logger import get_scanner_logger
    logger = get_scanner_logger("cross_framework_correlator")
except ImportError:
    logger = logging.getLogger(__name__)


class ComplianceFramework(Enum):
    GDPR = "gdpr"
    AI_ACT = "ai_act"
    UAVG = "uavg"
    SOC2 = "soc2"
    SUSTAINABILITY = "sustainability"


@dataclass
class ComplianceMapping:
    """Maps findings across compliance frameworks"""
    framework_source: ComplianceFramework
    framework_target: ComplianceFramework
    source_finding: str
    target_requirement: str
    correlation_strength: float  # 0.0 to 1.0
    explanation: str


@dataclass
class UnifiedCompliance:
    """Unified compliance assessment across all frameworks"""
    scan_id: str
    timestamp: str
    frameworks_analyzed: List[ComplianceFramework]
    overall_compliance_score: float
    framework_scores: Dict[str, float]
    cross_framework_findings: List[Dict[str, Any]]
    compliance_gaps: List[Dict[str, Any]]
    unified_recommendations: List[Dict[str, Any]]
    coverage_matrix: Dict[str, Dict[str, float]]


class CrossFrameworkComplianceCorrelator:
    """
    Correlates compliance findings across multiple regulatory frameworks,
    identifying overlaps, gaps, and providing unified recommendations.
    """
    
    def __init__(self, region: str = "Netherlands"):
        self.region = region
        self.correlation_id = str(uuid.uuid4())
        
        # Framework correlation mappings
        self.framework_correlations = self._initialize_framework_correlations()
        
        # Regional compliance multipliers
        self.regional_multipliers = self._get_regional_multipliers()
        
        logger.info(f"Initialized Cross-Framework Correlator for region: {region}")
    
    def _initialize_framework_correlations(self) -> List[ComplianceMapping]:
        """Initialize correlation mappings between frameworks"""
        mappings = [
            # GDPR ↔ AI Act correlations
            ComplianceMapping(
                ComplianceFramework.GDPR, ComplianceFramework.AI_ACT,
                "Personal data processing", "High-risk AI system assessment",
                0.9, "AI systems processing personal data fall under both GDPR and AI Act"
            ),
            ComplianceMapping(
                ComplianceFramework.GDPR, ComplianceFramework.AI_ACT,
                "Automated decision-making (Art. 22)", "Prohibited AI practices",
                0.95, "GDPR automated decisions directly map to AI Act prohibitions"
            ),
            
            # GDPR ↔ UAVG correlations
            ComplianceMapping(
                ComplianceFramework.GDPR, ComplianceFramework.UAVG,
                "Special category data (Art. 9)", "BSN processing requirements",
                0.85, "Netherlands BSN falls under GDPR special categories"
            ),
            ComplianceMapping(
                ComplianceFramework.GDPR, ComplianceFramework.UAVG,
                "Data subject rights (Art. 15-22)", "Netherlands AP Guidelines",
                0.9, "UAVG implements GDPR rights with Netherlands specifics"
            ),
            
            # GDPR ↔ SOC2 correlations
            ComplianceMapping(
                ComplianceFramework.GDPR, ComplianceFramework.SOC2,
                "Security of processing (Art. 32)", "Security TSC criteria",
                0.8, "GDPR security requirements align with SOC2 Security criteria"
            ),
            ComplianceMapping(
                ComplianceFramework.GDPR, ComplianceFramework.SOC2,
                "Privacy by design (Art. 25)", "Processing Integrity TSC",
                0.7, "Privacy by design principles complement SOC2 integrity controls"
            ),
            
            # AI Act ↔ SOC2 correlations
            ComplianceMapping(
                ComplianceFramework.AI_ACT, ComplianceFramework.SOC2,
                "AI system security requirements", "Security TSC criteria",
                0.75, "AI system security aligns with SOC2 security controls"
            ),
            
            # Sustainability correlations
            ComplianceMapping(
                ComplianceFramework.SUSTAINABILITY, ComplianceFramework.AI_ACT,
                "Energy efficiency requirements", "AI system environmental impact",
                0.6, "EU Green Deal requirements apply to AI systems"
            ),
            
            # SOC2 ↔ Sustainability
            ComplianceMapping(
                ComplianceFramework.SOC2, ComplianceFramework.SUSTAINABILITY,
                "Availability TSC criteria", "Resource optimization",
                0.5, "System availability affects environmental efficiency"
            )
        ]
        
        return mappings
    
    def _get_regional_multipliers(self) -> Dict[str, float]:
        """Get regional compliance multipliers for Netherlands/EU"""
        if self.region.lower() in ['netherlands', 'nl']:
            return {
                'gdpr': 1.2,  # Netherlands AP more strict
                'uavg': 1.0,  # Native Netherlands law  
                'ai_act': 1.1,  # EU member state
                'soc2': 0.9,  # US standard, less emphasis
                'sustainability': 1.3  # EU Green Deal priority
            }
        else:
            return {framework.value: 1.0 for framework in ComplianceFramework}
    
    def correlate_scanner_findings(self, scanner_results: Dict[str, Dict[str, Any]]) -> UnifiedCompliance:
        """
        Correlate findings from multiple scanner results into unified compliance assessment.
        
        Args:
            scanner_results: Dictionary mapping scanner_type -> scan_results
                           e.g., {'code': code_results, 'ai_model': ai_results, ...}
        
        Returns:
            UnifiedCompliance assessment across all frameworks
        """
        correlation_start = datetime.now()
        logger.info(f"Starting cross-framework correlation for {len(scanner_results)} scanners")
        
        # Initialize unified assessment
        unified = UnifiedCompliance(
            scan_id=str(uuid.uuid4()),
            timestamp=correlation_start.isoformat(),
            frameworks_analyzed=[],
            overall_compliance_score=0.0,
            framework_scores={},
            cross_framework_findings=[],
            compliance_gaps=[],
            unified_recommendations=[],
            coverage_matrix={}
        )
        
        # Analyze each scanner's compliance coverage
        framework_findings = {}
        for scanner_type, results in scanner_results.items():
            framework_coverage = self._analyze_scanner_framework_coverage(scanner_type, results)
            framework_findings[scanner_type] = framework_coverage
            
            # Update frameworks analyzed
            for framework in framework_coverage.keys():
                if framework not in [f.value for f in unified.frameworks_analyzed]:
                    unified.frameworks_analyzed.append(ComplianceFramework(framework))
        
        # Calculate framework scores with regional multipliers
        for framework in ComplianceFramework:
            framework_key = framework.value
            total_score = 0.0
            scanner_count = 0
            
            for scanner_type, coverage in framework_findings.items():
                if framework_key in coverage:
                    multiplier = self.regional_multipliers.get(framework_key, 1.0)
                    total_score += coverage[framework_key]['score'] * multiplier
                    scanner_count += 1
            
            if scanner_count > 0:
                unified.framework_scores[framework_key] = total_score / scanner_count
        
        # Identify cross-framework correlations
        unified.cross_framework_findings = self._identify_cross_framework_correlations(framework_findings)
        
        # Identify compliance gaps
        unified.compliance_gaps = self._identify_compliance_gaps(framework_findings)
        
        # Generate unified recommendations
        unified.unified_recommendations = self._generate_unified_recommendations(
            unified.framework_scores, unified.compliance_gaps
        )
        
        # Build coverage matrix
        unified.coverage_matrix = self._build_coverage_matrix(framework_findings)
        
        # Calculate overall compliance score
        if unified.framework_scores:
            unified.overall_compliance_score = sum(unified.framework_scores.values()) / len(unified.framework_scores)
        
        logger.info(f"Completed cross-framework correlation: {unified.overall_compliance_score:.1f}% overall compliance")
        return unified
    
    def _analyze_scanner_framework_coverage(self, scanner_type: str, results: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Analyze which frameworks a scanner covers and how well"""
        coverage = {}
        
        # Code Scanner coverage
        if scanner_type == 'code':
            coverage['gdpr'] = {
                'score': self._calculate_gdpr_score_from_code(results),
                'findings': results.get('gdpr_violations', []),
                'articles_covered': results.get('gdpr_articles_validated', 0)
            }
            coverage['uavg'] = {
                'score': self._calculate_uavg_score_from_code(results),
                'findings': results.get('netherlands_violations', []),
                'bsn_detected': results.get('bsn_patterns_found', 0)
            }
            if 'ai_related_secrets' in results:
                coverage['ai_act'] = {
                    'score': 30.0,  # Basic AI Act coverage via secrets
                    'findings': results.get('ai_related_secrets', [])
                }
        
        # AI Model Scanner coverage
        elif scanner_type == 'ai_model':
            coverage['ai_act'] = {
                'score': self._calculate_ai_act_score(results),
                'findings': results.get('ai_violations', []),
                'prohibited_practices': results.get('prohibited_practices_detected', 0)
            }
            coverage['gdpr'] = {
                'score': 40.0,  # Basic GDPR coverage
                'findings': results.get('pii_in_models', [])
            }
        
        # Website Scanner coverage
        elif scanner_type == 'website':
            coverage['gdpr'] = {
                'score': self._calculate_gdpr_score_from_website(results),
                'findings': results.get('cookie_violations', []),
                'consent_detected': results.get('consent_mechanisms', [])
            }
            coverage['uavg'] = {
                'score': 75.0 if results.get('netherlands_cookie_compliance') else 25.0,
                'findings': results.get('netherlands_specific_issues', [])
            }
        
        # SOC2 Scanner coverage
        elif scanner_type == 'soc2':
            coverage['soc2'] = {
                'score': results.get('compliance_score', 0),
                'findings': results.get('findings', []),
                'tsc_coverage': results.get('tsc_criteria', {})
            }
            # SOC2 has some GDPR overlap
            coverage['gdpr'] = {
                'score': 45.0 if results.get('privacy_controls_passed', False) else 15.0,
                'findings': []
            }
        
        # Database Scanner coverage  
        elif scanner_type == 'database':
            coverage['gdpr'] = {
                'score': self._calculate_gdpr_score_from_db(results),
                'findings': results.get('pii_findings', []),
                'data_classification': results.get('classified_data', {})
            }
            coverage['uavg'] = {
                'score': 70.0 if results.get('bsn_detected') else 30.0,
                'findings': results.get('netherlands_data_residency_issues', [])
            }
        
        # Sustainability Scanner coverage
        elif scanner_type == 'sustainability':
            coverage['sustainability'] = {
                'score': results.get('efficiency_score', 0),
                'findings': results.get('optimization_opportunities', []),
                'co2_reduction': results.get('co2_savings_tons', 0)
            }
        
        return coverage
    
    def _calculate_gdpr_score_from_code(self, results: Dict[str, Any]) -> float:
        """Calculate GDPR compliance score from code scan results"""
        base_score = 90.0  # Assume high baseline
        violations = len(results.get('gdpr_violations', []))
        secrets_found = len(results.get('secrets_found', []))
        
        # Reduce score based on violations
        score = base_score - (violations * 5) - (secrets_found * 3)
        return max(0.0, min(100.0, score))
    
    def _calculate_uavg_score_from_code(self, results: Dict[str, Any]) -> float:
        """Calculate UAVG compliance score from code scan results"""
        base_score = 85.0
        bsn_violations = len([v for v in results.get('netherlands_violations', []) if 'bsn' in v.get('type', '').lower()])
        
        score = base_score - (bsn_violations * 10)
        return max(0.0, min(100.0, score))
    
    def _calculate_ai_act_score(self, results: Dict[str, Any]) -> float:
        """Calculate AI Act compliance score"""
        base_score = 95.0
        prohibited_practices = len(results.get('prohibited_practices_detected', []))
        high_risk_issues = len(results.get('high_risk_ai_violations', []))
        
        score = base_score - (prohibited_practices * 20) - (high_risk_issues * 10)
        return max(0.0, min(100.0, score))
    
    def _calculate_gdpr_score_from_website(self, results: Dict[str, Any]) -> float:
        """Calculate GDPR compliance score from website scan"""
        base_score = 80.0
        cookie_violations = len(results.get('cookie_violations', []))
        tracking_violations = len(results.get('tracking_violations', []))
        
        score = base_score - (cookie_violations * 8) - (tracking_violations * 6)
        return max(0.0, min(100.0, score))
    
    def _calculate_gdpr_score_from_db(self, results: Dict[str, Any]) -> float:
        """Calculate GDPR compliance score from database scan"""
        base_score = 85.0
        pii_exposures = len(results.get('pii_findings', []))
        data_classification_score = results.get('data_classification_score', 50.0)
        
        score = (base_score - (pii_exposures * 7)) * (data_classification_score / 100.0)
        return max(0.0, min(100.0, score))
    
    def _identify_cross_framework_correlations(self, framework_findings: Dict[str, Dict[str, Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Identify correlations between framework findings"""
        correlations = []
        
        for mapping in self.framework_correlations:
            source_key = mapping.framework_source.value
            target_key = mapping.framework_target.value
            
            # Check if both frameworks have findings
            source_scanners = [s for s, findings in framework_findings.items() if source_key in findings]
            target_scanners = [s for s, findings in framework_findings.items() if target_key in findings]
            
            if source_scanners and target_scanners:
                correlations.append({
                    'source_framework': source_key,
                    'target_framework': target_key,
                    'correlation_strength': mapping.correlation_strength,
                    'explanation': mapping.explanation,
                    'source_scanners': source_scanners,
                    'target_scanners': target_scanners,
                    'recommendation': f"Align {mapping.source_finding} with {mapping.target_requirement}"
                })
        
        return correlations
    
    def _identify_compliance_gaps(self, framework_findings: Dict[str, Dict[str, Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Identify gaps in cross-framework compliance coverage"""
        gaps = []
        
        all_frameworks = [f.value for f in ComplianceFramework]
        covered_frameworks = set()
        
        for scanner_findings in framework_findings.values():
            covered_frameworks.update(scanner_findings.keys())
        
        # Identify missing frameworks
        missing_frameworks = set(all_frameworks) - covered_frameworks
        for framework in missing_frameworks:
            gaps.append({
                'type': 'missing_framework',
                'framework': framework,
                'severity': 'high',
                'description': f"No scanner coverage for {framework} compliance",
                'recommendation': f"Integrate {framework} compliance detection across existing scanners"
            })
        
        # Identify weak coverage
        for framework, scanners in [(f, [s for s, findings in framework_findings.items() if f in findings]) 
                                   for f in covered_frameworks]:
            if len(scanners) == 1:
                gaps.append({
                    'type': 'single_scanner_coverage',
                    'framework': framework,
                    'severity': 'medium',
                    'scanner': scanners[0],
                    'description': f"{framework} compliance depends on single scanner: {scanners[0]}",
                    'recommendation': f"Add {framework} detection to additional scanners for redundancy"
                })
        
        return gaps
    
    def _generate_unified_recommendations(self, framework_scores: Dict[str, float], gaps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate unified recommendations across all frameworks"""
        recommendations = []
        
        # Priority recommendations based on framework scores
        for framework, score in framework_scores.items():
            if score < 70.0:
                recommendations.append({
                    'type': 'improve_framework_score',
                    'framework': framework,
                    'priority': 'high' if score < 50.0 else 'medium',
                    'current_score': score,
                    'target_score': 85.0,
                    'recommendation': f"Improve {framework} compliance from {score:.1f}% to 85%+",
                    'estimated_effort': 'medium' if score > 40.0 else 'high'
                })
        
        # Gap-based recommendations
        for gap in gaps:
            if gap['severity'] == 'high':
                recommendations.append({
                    'type': 'address_compliance_gap',
                    'framework': gap['framework'],
                    'priority': 'high',
                    'recommendation': gap['recommendation'],
                    'estimated_effort': 'high'
                })
        
        # Cross-framework optimization
        if len(framework_scores) >= 3:
            recommendations.append({
                'type': 'cross_framework_optimization',
                'priority': 'medium',
                'recommendation': "Implement unified compliance dashboard for cross-framework correlation",
                'estimated_effort': 'medium',
                'frameworks_involved': list(framework_scores.keys())
            })
        
        return sorted(recommendations, key=lambda x: {'high': 3, 'medium': 2, 'low': 1}[x['priority']], reverse=True)
    
    def _build_coverage_matrix(self, framework_findings: Dict[str, Dict[str, Dict[str, Any]]]) -> Dict[str, Dict[str, float]]:
        """Build coverage matrix showing framework coverage by scanner"""
        matrix = {}
        
        for scanner_type in framework_findings.keys():
            matrix[scanner_type] = {}
            for framework in ComplianceFramework:
                framework_key = framework.value
                if framework_key in framework_findings[scanner_type]:
                    matrix[scanner_type][framework_key] = framework_findings[scanner_type][framework_key]['score']
                else:
                    matrix[scanner_type][framework_key] = 0.0
        
        return matrix
    
    def generate_correlation_report(self, unified_compliance: UnifiedCompliance) -> Dict[str, Any]:
        """Generate comprehensive correlation report"""
        return {
            'correlation_id': self.correlation_id,
            'region': self.region,
            'scan_summary': {
                'scan_id': unified_compliance.scan_id,
                'timestamp': unified_compliance.timestamp,
                'frameworks_analyzed': [f.value for f in unified_compliance.frameworks_analyzed],
                'overall_score': unified_compliance.overall_compliance_score
            },
            'framework_scores': unified_compliance.framework_scores,
            'coverage_matrix': unified_compliance.coverage_matrix,
            'cross_framework_analysis': {
                'correlations_found': len(unified_compliance.cross_framework_findings),
                'compliance_gaps': len(unified_compliance.compliance_gaps),
                'unified_recommendations': len(unified_compliance.unified_recommendations)
            },
            'detailed_findings': {
                'cross_framework_correlations': unified_compliance.cross_framework_findings,
                'compliance_gaps': unified_compliance.compliance_gaps,
                'unified_recommendations': unified_compliance.unified_recommendations
            },
            'regional_analysis': {
                'region': self.region,
                'multipliers_applied': self.regional_multipliers,
                'netherlands_specific_analysis': self.region.lower() in ['netherlands', 'nl']
            }
        }