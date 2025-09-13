"""
Privacy-Enhancing Technology Validation
Detects and validates privacy-preserving techniques in AI systems
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

class PETType(Enum):
    """Privacy-enhancing technology types"""
    FEDERATED_LEARNING = "federated_learning"
    DIFFERENTIAL_PRIVACY = "differential_privacy"
    SYNTHETIC_DATA = "synthetic_data"
    HOMOMORPHIC_ENCRYPTION = "homomorphic_encryption"
    SECURE_MULTIPARTY = "secure_multiparty"
    ANONYMIZATION = "anonymization"
    PSEUDONYMIZATION = "pseudonymization"

class ComplianceLevel(Enum):
    """Compliance levels for PET implementation"""
    COMPLIANT = "compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    NOT_IMPLEMENTED = "not_implemented"

@dataclass
class PETValidationResult:
    """Result of PET validation"""
    pet_type: PETType
    detected: bool
    compliance_level: ComplianceLevel
    implementation_quality: float  # 0-100
    findings: List[Dict[str, Any]]
    recommendations: List[str]
    regulatory_impact: Dict[str, str]

class PrivacyEnhancingTechValidator:
    """
    Validates privacy-enhancing technologies in AI systems
    for GDPR and AI Act compliance
    """
    
    def __init__(self, region: str = "Netherlands"):
        self.region = region
        self.pet_patterns = self._load_pet_patterns()
        self.compliance_rules = self._load_compliance_rules()
        
    def _load_pet_patterns(self) -> Dict[str, Any]:
        """Load detection patterns for privacy-enhancing technologies"""
        return {
            "federated_learning": {
                "detection_patterns": [
                    r"\b(?:federated\s+learning|fl\s+training|distributed\s+training)\b",
                    r"\b(?:client.*server|parameter\s+aggregation|model\s+aggregation)\b",
                    r"\b(?:flower|tensorflow.*federated|fed.*avg|federated.*averaging)\b",
                    r"\b(?:local\s+training|on.*device\s+training|edge\s+learning)\b"
                ],
                "implementation_indicators": [
                    r"\b(?:secure\s+aggregation|differential\s+privacy|client\s+selection)\b",
                    r"\b(?:communication\s+rounds|federated\s+optimization)\b",
                    r"\b(?:horizontal\s+federated|vertical\s+federated)\b"
                ],
                "quality_indicators": [
                    r"\b(?:privacy\s+budget|epsilon.*delta|noise\s+addition)\b",
                    r"\b(?:byzantine\s+robust|poisoning\s+defense)\b",
                    r"\b(?:convergence\s+guarantee|theoretical\s+analysis)\b"
                ]
            },
            "differential_privacy": {
                "detection_patterns": [
                    r"\b(?:differential\s+privacy|dp\s+mechanism|epsilon.*delta)\b",
                    r"\b(?:laplace\s+noise|gaussian\s+noise|privacy\s+budget)\b",
                    r"\b(?:global\s+sensitivity|local\s+sensitivity)\b",
                    r"\b(?:composition\s+theorem|privacy\s+accountant)\b"
                ],
                "implementation_indicators": [
                    r"\b(?:noise\s+addition|randomized\s+response|exponential\s+mechanism)\b",
                    r"\b(?:private\s+aggregation|histogram\s+release)\b",
                    r"\b(?:renyi\s+dp|concentrated\s+dp|approximate\s+dp)\b"
                ],
                "quality_indicators": [
                    r"epsilon\s*[=<>]\s*\d+\.?\d*",  # Epsilon values
                    r"delta\s*[=<>]\s*\d+\.?\d*",    # Delta values
                    r"\b(?:formal\s+privacy\s+proof|privacy\s+analysis)\b"
                ]
            },
            "synthetic_data": {
                "detection_patterns": [
                    r"\b(?:synthetic\s+data|data\s+synthesis|artificial\s+data)\b",
                    r"\b(?:gan\s+training|variational\s+autoencoder|vae)\b",
                    r"\b(?:data\s+generation|generative\s+model)\b",
                    r"\b(?:synthetic\s+dataset|simulated\s+data)\b"
                ],
                "implementation_indicators": [
                    r"\b(?:tabular\s+gan|ctgan|copulagan|pategan)\b",
                    r"\b(?:privacy\s+preserving\s+gan|dp.*gan)\b",
                    r"\b(?:conditional\s+generation|attribute\s+preservation)\b"
                ],
                "quality_indicators": [
                    r"\b(?:utility\s+preservation|statistical\s+fidelity)\b",
                    r"\b(?:membership\s+inference|privacy\s+attack)\b",
                    r"\b(?:synthetic\s+validation|realism\s+test)\b"
                ]
            },
            "homomorphic_encryption": {
                "detection_patterns": [
                    r"\b(?:homomorphic\s+encryption|he\s+scheme|fhe)\b",
                    r"\b(?:fully\s+homomorphic|somewhat\s+homomorphic|partial\s+homomorphic)\b",
                    r"\b(?:encrypted\s+computation|secure\s+computation)\b",
                    r"\b(?:seal|helib|palisade|concrete)\b"  # HE libraries
                ],
                "implementation_indicators": [
                    r"\b(?:bootstrapping|noise\s+management|parameter\s+selection)\b",
                    r"\b(?:bgv|bfv|ckks|tfhe)\s+scheme\b",
                    r"\b(?:ciphertext\s+operations|encrypted\s+inference)\b"
                ],
                "quality_indicators": [
                    r"\b(?:security\s+parameter|multiplicative\s+depth)\b",
                    r"\b(?:performance\s+optimization|batching\s+technique)\b",
                    r"\b(?:correctness\s+proof|security\s+analysis)\b"
                ]
            },
            "secure_multiparty": {
                "detection_patterns": [
                    r"\b(?:secure\s+multiparty|mpc|multi.*party\s+computation)\b",
                    r"\b(?:secret\s+sharing|garbled\s+circuits)\b",
                    r"\b(?:oblivious\s+transfer|private\s+set\s+intersection)\b",
                    r"\b(?:shamir\s+secret|additive\s+sharing)\b"
                ],
                "implementation_indicators": [
                    r"\b(?:honest\s+majority|dishonest\s+majority)\b",
                    r"\b(?:semi.*honest|malicious\s+adversary)\b",
                    r"\b(?:communication\s+rounds|circuit\s+evaluation)\b"
                ],
                "quality_indicators": [
                    r"\b(?:security\s+proof|privacy\s+guarantee)\b",
                    r"\b(?:protocol\s+efficiency|round\s+complexity)\b",
                    r"\b(?:fault\s+tolerance|robustness\s+analysis)\b"
                ]
            },
            "anonymization": {
                "detection_patterns": [
                    r"\b(?:anonymization|k.*anonymity|l.*diversity)\b",
                    r"\b(?:t.*closeness|m.*invariance|personalization)\b",
                    r"\b(?:quasi.*identifier|sensitive\s+attribute)\b",
                    r"\b(?:generalization|suppression|perturbation)\b"
                ],
                "implementation_indicators": [
                    r"\b(?:hierarchy\s+tree|taxonomy\s+tree)\b",
                    r"\b(?:equivalence\s+class|anonymity\s+group)\b",
                    r"\b(?:information\s+loss|utility\s+metric)\b"
                ],
                "quality_indicators": [
                    r"k\s*[=<>]\s*\d+",  # k-anonymity values
                    r"l\s*[=<>]\s*\d+",  # l-diversity values  
                    r"\b(?:re.*identification\s+risk|linkage\s+attack)\b"
                ]
            },
            "pseudonymization": {
                "detection_patterns": [
                    r"\b(?:pseudonymization|pseudonym|tokenization)\b",
                    r"\b(?:hash\s+function|cryptographic\s+hash)\b",
                    r"\b(?:identifier\s+replacement|data\s+masking)\b",
                    r"\b(?:reversible\s+pseudonym|irreversible\s+pseudonym)\b"
                ],
                "implementation_indicators": [
                    r"\b(?:salt\s+value|key\s+management|deterministic\s+hash)\b",
                    r"\b(?:format\s+preserving|referential\s+integrity)\b",
                    r"\b(?:lookup\s+table|mapping\s+function)\b"
                ],
                "quality_indicators": [
                    r"\b(?:collision\s+resistance|preimage\s+resistance)\b",
                    r"\b(?:key\s+rotation|cryptographic\s+strength)\b",
                    r"\b(?:unlinkability|untraceability)\b"
                ]
            }
        }
    
    def _load_compliance_rules(self) -> Dict[str, Any]:
        """Load compliance rules for PET implementations"""
        return {
            "gdpr_requirements": {
                "pseudonymization": {
                    "article": "Article 4(5), Article 25",
                    "requirements": [
                        "Technical and organizational measures",
                        "Appropriate safeguards for data subjects",
                        "Reversibility controls where applicable"
                    ]
                },
                "anonymization": {
                    "article": "Recital 26",
                    "requirements": [
                        "No re-identification possibility",
                        "Reasonable means assessment",
                        "Technical and legal context consideration"
                    ]
                },
                "data_minimization": {
                    "article": "Article 5(1)(c)",
                    "requirements": [
                        "Adequate and relevant data only",
                        "Limited to necessary purposes",
                        "Proportionate processing"
                    ]
                }
            },
            "ai_act_requirements": {
                "high_risk_systems": {
                    "article": "Article 10",
                    "requirements": [
                        "Data governance and management practices",
                        "Training data quality and representativeness",
                        "Bias detection and correction measures"
                    ]
                },
                "transparency": {
                    "article": "Article 13",
                    "requirements": [
                        "Clear information about AI system capabilities",
                        "Appropriate level of transparency",
                        "Human oversight possibilities"
                    ]
                }
            }
        }
    
    def validate_privacy_technologies(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> List[PETValidationResult]:
        """
        Validate privacy-enhancing technologies in content
        
        Args:
            content: Content to analyze
            metadata: Additional metadata about the system
            
        Returns:
            List of PET validation results
        """
        results = []
        metadata = metadata or {}
        
        for pet_name, pet_config in self.pet_patterns.items():
            pet_type = PETType(pet_name)
            
            # Detect PET implementation
            detected = self._detect_pet_implementation(content, pet_config)
            
            if detected:
                # Validate implementation quality
                compliance_level, quality_score, findings = self._validate_pet_quality(
                    content, pet_type, pet_config
                )
                
                # Generate recommendations
                recommendations = self._generate_pet_recommendations(
                    pet_type, compliance_level, quality_score, findings
                )
                
                # Assess regulatory impact
                regulatory_impact = self._assess_regulatory_impact(pet_type, compliance_level)
                
                results.append(PETValidationResult(
                    pet_type=pet_type,
                    detected=True,
                    compliance_level=compliance_level,
                    implementation_quality=quality_score,
                    findings=findings,
                    recommendations=recommendations,
                    regulatory_impact=regulatory_impact
                ))
            else:
                # PET not detected - check if it should be implemented
                should_implement = self._assess_pet_necessity(pet_type, metadata)
                if should_implement:
                    results.append(PETValidationResult(
                        pet_type=pet_type,
                        detected=False,
                        compliance_level=ComplianceLevel.NOT_IMPLEMENTED,
                        implementation_quality=0.0,
                        findings=[{
                            'type': 'MISSING_PET',
                            'description': f'{pet_type.value} not implemented but may be beneficial',
                            'severity': 'medium'
                        }],
                        recommendations=[f"Consider implementing {pet_type.value} for enhanced privacy protection"],
                        regulatory_impact=self._assess_regulatory_impact(pet_type, ComplianceLevel.NOT_IMPLEMENTED)
                    ))
        
        return results
    
    def _detect_pet_implementation(self, content: str, pet_config: Dict[str, Any]) -> bool:
        """Detect if a PET is implemented in the content"""
        detection_patterns = pet_config.get("detection_patterns", [])
        
        # Need at least one detection pattern match
        for pattern in detection_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False
    
    def _validate_pet_quality(self, content: str, pet_type: PETType, 
                             pet_config: Dict[str, Any]) -> Tuple[ComplianceLevel, float, List[Dict[str, Any]]]:
        """Validate the quality of PET implementation"""
        findings = []
        quality_score = 0.0
        
        implementation_patterns = pet_config.get("implementation_indicators", [])
        quality_patterns = pet_config.get("quality_indicators", [])
        
        # Check implementation indicators (40% of score)
        impl_matches = 0
        for pattern in implementation_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                impl_matches += 1
        
        impl_score = min(40, (impl_matches / len(implementation_patterns)) * 40) if implementation_patterns else 20
        
        # Check quality indicators (60% of score)
        quality_matches = 0
        for pattern in quality_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                quality_matches += 1
                findings.append({
                    'type': 'QUALITY_INDICATOR',
                    'description': f'Quality indicator found: {pattern}',
                    'severity': 'info',
                    'pattern': pattern
                })
        
        quality_indicator_score = min(60, (quality_matches / len(quality_patterns)) * 60) if quality_patterns else 30
        
        quality_score = impl_score + quality_indicator_score
        
        # Determine compliance level
        if quality_score >= 80:
            compliance_level = ComplianceLevel.COMPLIANT
        elif quality_score >= 50:
            compliance_level = ComplianceLevel.PARTIALLY_COMPLIANT
            findings.append({
                'type': 'PARTIAL_IMPLEMENTATION',
                'description': f'{pet_type.value} partially implemented - consider enhancements',
                'severity': 'medium'
            })
        else:
            compliance_level = ComplianceLevel.NON_COMPLIANT
            findings.append({
                'type': 'POOR_IMPLEMENTATION',
                'description': f'{pet_type.value} implementation lacks key quality indicators',
                'severity': 'high'
            })
        
        return compliance_level, quality_score, findings
    
    def _assess_pet_necessity(self, pet_type: PETType, metadata: Dict[str, Any]) -> bool:
        """Assess if a PET should be implemented based on system metadata"""
        data_sensitivity = metadata.get('data_sensitivity', 'medium').lower()
        system_type = metadata.get('system_type', '').lower()
        use_case = metadata.get('use_case', '').lower()
        
        necessity_rules = {
            PETType.FEDERATED_LEARNING: [
                data_sensitivity in ['high', 'very_high'],
                'distributed' in system_type,
                'multi_party' in use_case
            ],
            PETType.DIFFERENTIAL_PRIVACY: [
                data_sensitivity in ['high', 'very_high'],
                'statistical' in use_case,
                'analytics' in system_type
            ],
            PETType.SYNTHETIC_DATA: [
                data_sensitivity in ['medium', 'high', 'very_high'],
                'training' in use_case,
                'machine_learning' in system_type
            ],
            PETType.HOMOMORPHIC_ENCRYPTION: [
                data_sensitivity == 'very_high',
                'computation' in use_case,
                'cloud' in system_type
            ],
            PETType.ANONYMIZATION: [
                data_sensitivity in ['medium', 'high'],
                'personal_data' in use_case,
                'research' in system_type
            ],
            PETType.PSEUDONYMIZATION: [
                data_sensitivity in ['medium', 'high', 'very_high'],
                'personal_data' in use_case,
                True  # Generally recommended
            ]
        }
        
        rules = necessity_rules.get(pet_type, [False])
        return any(rules)
    
    def _generate_pet_recommendations(self, pet_type: PETType, compliance_level: ComplianceLevel,
                                    quality_score: float, findings: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations for PET implementation"""
        recommendations = []
        
        if compliance_level == ComplianceLevel.NOT_IMPLEMENTED:
            recommendations.append(f"📚 Research {pet_type.value} implementation best practices")
            recommendations.append(f"🔧 Consider implementing {pet_type.value} for enhanced privacy protection")
            
        elif compliance_level == ComplianceLevel.NON_COMPLIANT:
            recommendations.append(f"🚨 Improve {pet_type.value} implementation - current quality: {quality_score:.1f}%")
            recommendations.append(f"📋 Review implementation against industry standards")
            
        elif compliance_level == ComplianceLevel.PARTIALLY_COMPLIANT:
            recommendations.append(f"⚡ Enhance {pet_type.value} implementation - current quality: {quality_score:.1f}%")
            recommendations.append(f"🔍 Add missing quality indicators for full compliance")
            
        else:  # COMPLIANT
            recommendations.append(f"✅ {pet_type.value} implementation meets standards - quality: {quality_score:.1f}%")
            recommendations.append(f"📊 Monitor implementation performance and maintain quality")
        
        # Type-specific recommendations
        type_specific = {
            PETType.FEDERATED_LEARNING: [
                "Implement secure aggregation protocols",
                "Add differential privacy to federated updates",
                "Monitor client selection fairness"
            ],
            PETType.DIFFERENTIAL_PRIVACY: [
                "Optimize privacy budget allocation",
                "Implement privacy accountant",
                "Validate noise calibration"
            ],
            PETType.SYNTHETIC_DATA: [
                "Validate synthetic data utility",
                "Test against membership inference attacks",
                "Ensure attribute preservation"
            ],
            PETType.HOMOMORPHIC_ENCRYPTION: [
                "Optimize bootstrapping operations",
                "Implement batching for efficiency",
                "Validate security parameters"
            ]
        }
        
        recommendations.extend(type_specific.get(pet_type, []))
        
        return recommendations
    
    def _assess_regulatory_impact(self, pet_type: PETType, compliance_level: ComplianceLevel) -> Dict[str, str]:
        """Assess regulatory compliance impact of PET implementation"""
        impact = {
            'gdpr_compliance': 'neutral',
            'ai_act_compliance': 'neutral',
            'overall_risk': 'medium'
        }
        
        if compliance_level == ComplianceLevel.COMPLIANT:
            impact.update({
                'gdpr_compliance': 'positive',
                'ai_act_compliance': 'positive', 
                'overall_risk': 'low',
                'benefit': f'{pet_type.value} enhances privacy protection and regulatory compliance'
            })
        elif compliance_level == ComplianceLevel.PARTIALLY_COMPLIANT:
            impact.update({
                'gdpr_compliance': 'neutral',
                'ai_act_compliance': 'neutral',
                'overall_risk': 'medium',
                'concern': f'{pet_type.value} implementation may not provide full privacy protection'
            })
        elif compliance_level == ComplianceLevel.NON_COMPLIANT:
            impact.update({
                'gdpr_compliance': 'negative',
                'ai_act_compliance': 'negative',
                'overall_risk': 'high',
                'risk': f'Poor {pet_type.value} implementation may create privacy vulnerabilities'
            })
        else:  # NOT_IMPLEMENTED
            if pet_type in [PETType.PSEUDONYMIZATION, PETType.ANONYMIZATION]:
                impact.update({
                    'gdpr_compliance': 'negative',
                    'overall_risk': 'high',
                    'risk': f'Missing {pet_type.value} may violate GDPR privacy protection requirements'
                })
        
        return impact
    
    def generate_pet_compliance_report(self, validation_results: List[PETValidationResult]) -> Dict[str, Any]:
        """Generate comprehensive PET compliance report"""
        if not validation_results:
            return {
                'overall_compliance': 'NO_PETS_DETECTED',
                'privacy_protection_level': 'MINIMAL',
                'recommendations': ['Consider implementing privacy-enhancing technologies']
            }
        
        # Calculate overall scores
        implemented_pets = [r for r in validation_results if r.detected]
        compliant_pets = [r for r in implemented_pets if r.compliance_level == ComplianceLevel.COMPLIANT]
        
        implementation_rate = len(implemented_pets) / len(validation_results) * 100
        compliance_rate = len(compliant_pets) / len(implemented_pets) * 100 if implemented_pets else 0
        
        avg_quality = sum(r.implementation_quality for r in implemented_pets) / len(implemented_pets) if implemented_pets else 0
        
        # Determine overall compliance level
        if compliance_rate >= 80 and avg_quality >= 75:
            overall_compliance = 'HIGHLY_COMPLIANT'
            privacy_level = 'STRONG'
        elif compliance_rate >= 60 and avg_quality >= 50:
            overall_compliance = 'MOSTLY_COMPLIANT'
            privacy_level = 'ADEQUATE'
        elif implementation_rate >= 30:
            overall_compliance = 'PARTIALLY_COMPLIANT'
            privacy_level = 'WEAK'
        else:
            overall_compliance = 'NON_COMPLIANT'
            privacy_level = 'MINIMAL'
        
        # Aggregate recommendations
        all_recommendations = []
        for result in validation_results:
            all_recommendations.extend(result.recommendations)
        
        # Get regulatory impacts
        positive_impacts = [r for r in validation_results if r.regulatory_impact.get('gdpr_compliance') == 'positive']
        negative_impacts = [r for r in validation_results if r.regulatory_impact.get('overall_risk') == 'high']
        
        return {
            'overall_compliance': overall_compliance,
            'privacy_protection_level': privacy_level,
            'implementation_rate': round(implementation_rate, 1),
            'compliance_rate': round(compliance_rate, 1),
            'average_quality_score': round(avg_quality, 1),
            'pets_detected': len(implemented_pets),
            'pets_compliant': len(compliant_pets),
            'total_pets_assessed': len(validation_results),
            'positive_regulatory_impacts': len(positive_impacts),
            'negative_regulatory_impacts': len(negative_impacts),
            'key_recommendations': list(set(all_recommendations))[:10],  # Top 10 unique recommendations
            'detailed_results': [
                {
                    'pet_type': r.pet_type.value,
                    'detected': r.detected,
                    'compliance_level': r.compliance_level.value,
                    'quality_score': r.implementation_quality,
                    'regulatory_impact': r.regulatory_impact
                }
                for r in validation_results
            ],
            'timestamp': datetime.now().isoformat()
        }