"""
Advanced AI Scanner - Enhanced AI model analysis with EU AI Act 2025 compliance,
bias detection, explainability assessment, and model governance features
"""

import json
import numpy as np
import pickle
# Optional joblib import - not required for core functionality
try:
    import joblib
except ImportError:
    joblib = None
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import hashlib
import tempfile
import os
import logging

# Import centralized logging
try:
    from utils.centralized_logger import get_scanner_logger
    logger = get_scanner_logger("advanced_ai_scanner")
except ImportError:
    # Fallback to standard logging if centralized logger not available
    logger = logging.getLogger(__name__)

class AIRiskCategory(Enum):
    PROHIBITED = "Prohibited AI System"
    HIGH_RISK = "High-Risk AI System"
    LIMITED_RISK = "Limited Risk AI System"
    MINIMAL_RISK = "Minimal Risk AI System"
    GENERAL_PURPOSE = "General Purpose AI Model"

class AIActCompliance(Enum):
    COMPLIANT = "Compliant"
    NON_COMPLIANT = "Non-Compliant"
    REQUIRES_ASSESSMENT = "Requires Assessment"
    NOT_APPLICABLE = "Not Applicable"

@dataclass
class BiasAssessment:
    overall_bias_score: float
    demographic_parity: float
    equalized_odds: float
    calibration_score: float
    fairness_through_awareness: float
    affected_groups: List[str]
    mitigation_recommendations: List[str]

@dataclass
class ExplainabilityAssessment:
    interpretability_score: float
    model_transparency: str
    feature_importance_available: bool
    decision_explanations: str
    audit_trail_quality: str
    user_understanding_level: str

@dataclass
class AIGovernanceAssessment:
    risk_management_system: bool
    human_oversight_implemented: bool
    data_governance_score: float
    documentation_completeness: float
    testing_validation_score: float
    monitoring_systems: bool
    incident_response_plan: bool

class AdvancedAIScanner:
    """
    Advanced AI scanner with comprehensive EU AI Act 2025 compliance assessment,
    bias detection, explainability analysis, and governance evaluation.
    """
    
    def __init__(self, region: str = "Netherlands"):
        self.region = region
        self.ai_act_rules = self._load_ai_act_2025_rules()
        self.bias_detection_algorithms = self._initialize_bias_detectors()
        self.explainability_framework = self._load_explainability_framework()
        
    def _load_ai_act_2025_rules(self) -> Dict[str, Any]:
        """Load EU AI Act 2025 compliance rules and requirements"""
        return {
            "prohibited_practices": [
                "subliminal_techniques",
                "exploiting_vulnerabilities", 
                "social_scoring",
                "real_time_biometric_identification",
                "predictive_policing_individuals"
            ],
            "high_risk_systems": {
                "biometric_identification": {
                    "requirements": ["conformity_assessment", "risk_management", "data_governance", "transparency", "human_oversight"],
                    "max_error_rates": {"far": 0.001, "frr": 0.01},
                    "documentation_required": ["eu_declaration", "technical_documentation", "instructions_use"]
                },
                "critical_infrastructure": {
                    "requirements": ["safety_components", "risk_assessment", "quality_management"],
                    "sectors": ["transport", "energy", "water", "health"]
                },
                "education_training": {
                    "requirements": ["transparency", "human_oversight", "accuracy_requirements"],
                    "prohibited": ["behavior_analysis", "personality_assessment"]
                },
                "employment": {
                    "requirements": ["transparency", "human_oversight", "non_discrimination"],
                    "prohibited": ["cv_filtering_personality", "performance_monitoring_emotions"]
                },
                "law_enforcement": {
                    "requirements": ["fundamental_rights_assessment", "human_oversight", "accuracy"],
                    "special_conditions": ["judicial_authorization", "proportionality_assessment"]
                }
            },
            "general_purpose_models": {
                "thresholds": {
                    "compute_threshold": 10**25,  # FLOPs
                    "systemic_risk_threshold": 10**26
                },
                "requirements": ["model_evaluation", "adversarial_testing", "systemic_risk_assessment"]
            },
            "penalties": {
                "prohibited_practices": {"amount": 35000000, "percentage": 0.07},
                "high_risk_non_compliance": {"amount": 15000000, "percentage": 0.03},
                "information_obligations": {"amount": 7500000, "percentage": 0.015}
            }
        }
    
    def _initialize_bias_detectors(self) -> Dict[str, Any]:
        """Initialize bias detection algorithms"""
        return {
            "demographic_parity": {
                "threshold": 0.8,
                "description": "Statistical parity across protected groups",
                "formula": "P(Y=1|A=0) ≈ P(Y=1|A=1)"
            },
            "equalized_odds": {
                "threshold": 0.8,
                "description": "Equal true positive and false positive rates",
                "formula": "TPR_A=0 ≈ TPR_A=1 AND FPR_A=0 ≈ FPR_A=1"
            },
            "calibration": {
                "threshold": 0.1,
                "description": "Prediction calibration across groups",
                "formula": "P(Y=1|Score=s,A=0) ≈ P(Y=1|Score=s,A=1)"
            },
            "individual_fairness": {
                "threshold": 0.9,
                "description": "Similar individuals receive similar outcomes",
                "formula": "d(f(x1),f(x2)) ≤ L*d(x1,x2)"
            }
        }
    
    def _load_explainability_framework(self) -> Dict[str, Any]:
        """Load explainability assessment framework"""
        return {
            "transparency_levels": {
                "black_box": {"score": 0.1, "description": "No interpretability"},
                "glass_box": {"score": 0.9, "description": "Fully interpretable"},
                "gray_box": {"score": 0.6, "description": "Partially interpretable"}
            },
            "explanation_methods": {
                "feature_importance": {"weight": 0.25, "techniques": ["SHAP", "LIME", "permutation"]},
                "counterfactual": {"weight": 0.2, "techniques": ["counterfactual_examples", "contrastive"]},
                "example_based": {"weight": 0.15, "techniques": ["prototypes", "criticisms", "nearest_neighbors"]},
                "attention_based": {"weight": 0.2, "techniques": ["attention_maps", "gradient_cam"]},
                "rule_based": {"weight": 0.2, "techniques": ["decision_trees", "rules_extraction"]}
            },
            "user_categories": {
                "data_subjects": {"explanation_level": "simple", "rights": ["explanation_request"]},
                "operators": {"explanation_level": "detailed", "rights": ["operational_insights"]},
                "auditors": {"explanation_level": "technical", "rights": ["full_documentation"]},
                "regulators": {"explanation_level": "comprehensive", "rights": ["compliance_evidence"]}
            }
        }
    
    def scan_ai_model_comprehensive(self, model_file: Any, model_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform comprehensive AI model analysis including EU AI Act compliance,
        bias assessment, explainability evaluation, and governance review.
        
        Args:
            model_file: AI model file or object
            model_metadata: Additional metadata about the model
            
        Returns:
            Comprehensive AI analysis results
        """
        if model_metadata is None:
            model_metadata = {}
        
        # Basic model analysis
        basic_analysis = self._analyze_model_structure(model_file, model_metadata)
        
        # EU AI Act 2025 compliance assessment
        ai_act_compliance = self._assess_ai_act_compliance(basic_analysis, model_metadata)
        
        # Bias and fairness assessment
        bias_assessment = self._assess_model_bias(model_file, model_metadata)
        
        # Explainability assessment
        explainability_assessment = self._assess_model_explainability(model_file, model_metadata)
        
        # Governance assessment
        governance_assessment = self._assess_ai_governance(model_metadata)
        
        # Generate comprehensive findings
        findings = self._generate_ai_findings(
            ai_act_compliance, bias_assessment, explainability_assessment, governance_assessment
        )
        
        # Calculate overall risk score
        overall_risk_score = self._calculate_ai_risk_score(
            ai_act_compliance, bias_assessment, explainability_assessment, governance_assessment
        )
        
        return {
            'scan_type': 'Advanced AI Model Analysis',
            'scan_id': hashlib.md5(f"ai_scan_{datetime.now().isoformat()}".encode()).hexdigest()[:10],
            'timestamp': datetime.now().isoformat(),
            'region': self.region,
            'model_analysis': basic_analysis,
            'ai_act_compliance': ai_act_compliance,
            'bias_assessment': bias_assessment.__dict__ if isinstance(bias_assessment, BiasAssessment) else bias_assessment,
            'explainability_assessment': explainability_assessment.__dict__ if isinstance(explainability_assessment, ExplainabilityAssessment) else explainability_assessment,
            'governance_assessment': governance_assessment.__dict__ if isinstance(governance_assessment, AIGovernanceAssessment) else governance_assessment,
            'findings': findings,
            'overall_risk_score': overall_risk_score,
            'recommendations': self._generate_ai_recommendations(ai_act_compliance, bias_assessment, governance_assessment),
            'compliance_score': max(0, 100 - overall_risk_score),
            'metadata': {
                'files_scanned': 1,
                'model_framework': basic_analysis.get('framework', 'Unknown'),
                'risk_category': ai_act_compliance.get('risk_category', 'Unknown')
            }
        }
    
    def _analyze_model_structure(self, model_file: Any, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze basic model structure and properties"""
        analysis = {
            'framework': 'Unknown',
            'model_type': 'Unknown',
            'parameters_count': 0,
            'input_shape': None,
            'output_shape': None,
            'model_size_mb': 0,
            'architecture_complexity': 'Unknown'
        }
        
        try:
            # Determine model framework and type
            if hasattr(model_file, 'read'):
                model_content = model_file.read()
                model_file.seek(0)  # Reset file pointer
                
                # Check for common ML frameworks
                if b'tensorflow' in model_content or b'keras' in model_content:
                    analysis['framework'] = 'TensorFlow/Keras'
                elif b'pytorch' in model_content or b'torch' in model_content:
                    analysis['framework'] = 'PyTorch'
                elif b'onnx' in model_content:
                    analysis['framework'] = 'ONNX'
                elif b'sklearn' in model_content or b'joblib' in model_content:
                    analysis['framework'] = 'scikit-learn'
                
                analysis['model_size_mb'] = len(model_content) / (1024 * 1024)
            
            # Try to load and analyze the model
            if analysis['framework'] == 'scikit-learn':
                try:
                    model = joblib.load(model_file) if joblib and hasattr(model_file, 'read') else model_file
                    analysis['model_type'] = model.__class__.__name__
                    
                    if hasattr(model, 'n_features_in_'):
                        analysis['input_shape'] = (model.n_features_in_,)
                    
                    # Estimate parameter count for sklearn models
                    param_count = 0
                    for param_name, param_value in model.get_params().items():
                        if isinstance(param_value, (int, float)):
                            param_count += 1
                        elif hasattr(param_value, '__len__'):
                            param_count += len(param_value)
                    
                    analysis['parameters_count'] = param_count
                    
                except Exception:
                    pass
            
            # Determine architecture complexity
            if analysis['model_size_mb'] > 1000:
                analysis['architecture_complexity'] = 'Very High (Large Language Model)'
            elif analysis['model_size_mb'] > 100:
                analysis['architecture_complexity'] = 'High (Deep Neural Network)'
            elif analysis['model_size_mb'] > 10:
                analysis['architecture_complexity'] = 'Medium (Complex Model)'
            else:
                analysis['architecture_complexity'] = 'Low (Simple Model)'
            
        except Exception as e:
            analysis['analysis_error'] = str(e)
        
        return analysis
    
    def _assess_ai_act_compliance(self, model_analysis: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Assess EU AI Act 2025 compliance"""
        
        # Determine AI system category
        risk_category = self._classify_ai_risk_category(model_analysis, metadata)
        
        # Check for prohibited practices
        prohibited_violations = self._check_prohibited_practices(metadata)
        
        # Assess high-risk system requirements
        high_risk_compliance = {}
        if risk_category == AIRiskCategory.HIGH_RISK:
            high_risk_compliance = self._assess_high_risk_requirements(model_analysis, metadata)
        
        # Check general purpose model requirements
        gp_compliance = {}
        if risk_category == AIRiskCategory.GENERAL_PURPOSE:
            gp_compliance = self._assess_general_purpose_requirements(model_analysis, metadata)
        
        # Calculate compliance score
        compliance_status = self._determine_compliance_status(
            risk_category, prohibited_violations, high_risk_compliance, gp_compliance
        )
        
        # Estimate potential penalties
        penalty_assessment = self._assess_potential_penalties(
            compliance_status, prohibited_violations, high_risk_compliance
        )
        
        return {
            'risk_category': risk_category.value,
            'compliance_status': compliance_status.value,
            'prohibited_violations': prohibited_violations,
            'high_risk_compliance': high_risk_compliance,
            'general_purpose_compliance': gp_compliance,
            'penalty_assessment': penalty_assessment,
            'certification_required': risk_category in [AIRiskCategory.HIGH_RISK, AIRiskCategory.GENERAL_PURPOSE],
            'conformity_assessment_needed': risk_category == AIRiskCategory.HIGH_RISK,
            'transparency_obligations': risk_category != AIRiskCategory.MINIMAL_RISK,
            'human_oversight_required': risk_category == AIRiskCategory.HIGH_RISK
        }
    
    def _classify_ai_risk_category(self, model_analysis: Dict[str, Any], metadata: Dict[str, Any]) -> AIRiskCategory:
        """Classify AI system according to EU AI Act risk categories"""
        
        # Check for prohibited systems
        use_case = metadata.get('use_case', '').lower()
        application_domain = metadata.get('application_domain', '').lower()
        
        prohibited_keywords = ['social scoring', 'manipulation', 'subliminal', 'exploit vulnerabilities']
        if any(keyword in use_case or keyword in application_domain for keyword in prohibited_keywords):
            return AIRiskCategory.PROHIBITED
        
        # Check for high-risk systems
        high_risk_domains = ['biometric', 'critical infrastructure', 'education', 'employment', 'law enforcement', 'healthcare']
        if any(domain in application_domain for domain in high_risk_domains):
            return AIRiskCategory.HIGH_RISK
        
        # Check for general purpose models (large models)
        model_size_mb = model_analysis.get('model_size_mb', 0)
        parameters_count = model_analysis.get('parameters_count', 0)
        
        # Thresholds for general purpose models (simplified)
        if model_size_mb > 1000 or parameters_count > 1000000:  # Large models
            return AIRiskCategory.GENERAL_PURPOSE
        
        # Check for limited risk (user interaction)
        if 'chatbot' in use_case or 'user interaction' in use_case:
            return AIRiskCategory.LIMITED_RISK
        
        # Default to minimal risk
        return AIRiskCategory.MINIMAL_RISK
    
    def _check_prohibited_practices(self, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for prohibited AI practices under EU AI Act"""
        violations = []
        
        use_case = metadata.get('use_case', '').lower()
        processing_activities = metadata.get('processing_activities', [])
        
        # Check each prohibited practice
        if 'social scoring' in use_case:
            violations.append({
                'violation': 'Social Scoring System',
                'article': 'Article 5(1)(c)',
                'description': 'AI systems for social scoring by public authorities',
                'penalty_risk': 'Up to €35M or 7% of annual turnover'
            })
        
        if any('manipulation' in activity for activity in processing_activities):
            violations.append({
                'violation': 'Subliminal Manipulation',
                'article': 'Article 5(1)(a)',
                'description': 'AI systems using subliminal techniques',
                'penalty_risk': 'Up to €35M or 7% of annual turnover'
            })
        
        if 'real-time biometric identification' in use_case and 'public space' in use_case:
            violations.append({
                'violation': 'Real-time Biometric Identification',
                'article': 'Article 5(1)(d)',
                'description': 'Real-time remote biometric identification in public spaces',
                'penalty_risk': 'Up to €35M or 7% of annual turnover'
            })
        
        return violations
    
    def _assess_high_risk_requirements(self, model_analysis: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Assess high-risk AI system requirements compliance"""
        
        requirements_status = {
            'risk_management_system': metadata.get('risk_management_system', False),
            'data_governance': metadata.get('data_governance_implemented', False),
            'technical_documentation': metadata.get('technical_documentation_complete', False),
            'record_keeping': metadata.get('automatic_logging', False),
            'transparency_obligations': metadata.get('transparency_implemented', False),
            'human_oversight': metadata.get('human_oversight', False),
            'accuracy_robustness': metadata.get('accuracy_tested', False),
            'cybersecurity': metadata.get('cybersecurity_measures', False)
        }
        
        # Calculate compliance percentage
        total_requirements = len(requirements_status)
        met_requirements = sum(requirements_status.values())
        compliance_percentage = (met_requirements / total_requirements) * 100
        
        # Generate specific recommendations
        missing_requirements = [req for req, status in requirements_status.items() if not status]
        
        return {
            'requirements_status': requirements_status,
            'compliance_percentage': compliance_percentage,
            'missing_requirements': missing_requirements,
            'conformity_assessment_needed': compliance_percentage < 100,
            'ce_marking_eligible': compliance_percentage == 100
        }
    
    def _assess_general_purpose_requirements(self, model_analysis: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Assess general purpose AI model requirements"""
        
        model_size_mb = model_analysis.get('model_size_mb', 0)
        
        # Determine if systemic risk threshold is exceeded
        systemic_risk = model_size_mb > 10000  # Simplified threshold
        
        requirements = {
            'model_evaluation': metadata.get('model_evaluation_completed', False),
            'adversarial_testing': metadata.get('adversarial_testing', False),
            'model_documentation': metadata.get('model_card_available', False),
            'risk_assessment': metadata.get('systemic_risk_assessment', False) if systemic_risk else True
        }
        
        compliance_percentage = (sum(requirements.values()) / len(requirements)) * 100
        
        return {
            'systemic_risk_model': systemic_risk,
            'requirements': requirements,
            'compliance_percentage': compliance_percentage,
            'additional_obligations': systemic_risk
        }
    
    def _validate_bias_test_data(self, test_data: Dict[str, Any]) -> Dict[str, bool]:
        """
        Validate schema of bias_test_data before metric execution.
        
        Returns dict of which metrics can be safely calculated.
        """
        validation = {
            'demographic_parity': False,
            'equalized_odds': False,
            'calibration': False,
            'individual_fairness': False
        }
        
        # Check for demographic parity requirements
        if 'predictions' in test_data and 'sensitive_attributes' in test_data:
            validation['demographic_parity'] = True
        
        # Check for equalized odds requirements
        if ('predictions' in test_data and 
            'ground_truth' in test_data and 
            'sensitive_attributes' in test_data):
            validation['equalized_odds'] = True
        
        # Check for calibration requirements
        if ('probabilities' in test_data and 
            'ground_truth' in test_data and 
            'sensitive_attributes' in test_data):
            validation['calibration'] = True
        elif validation['demographic_parity']:
            # Can fallback to demographic parity
            validation['calibration'] = True
        
        # Check for individual fairness requirements
        if 'features' in test_data and 'predictions' in test_data:
            validation['individual_fairness'] = True
        elif validation['demographic_parity']:
            # Can fallback to demographic parity
            validation['individual_fairness'] = True
        
        return validation
    
    def _assess_model_bias(self, model_file: Any, metadata: Dict[str, Any]) -> BiasAssessment:
        """
        Assess model bias and fairness using real fairness calculations.
        
        Implements three approaches:
        1. If metadata contains bias test results → Use those (most accurate)
        2. If bias_test_data provided → Calculate real fairness metrics
        3. Otherwise → Use static analysis based on model characteristics
        """
        
        # Approach 1: Use pre-computed bias metrics from metadata (if available)
        if metadata and metadata.get('bias_test_results'):
            bias_results = metadata['bias_test_results']
            demographic_parity = bias_results.get('demographic_parity', 0.5)
            equalized_odds = bias_results.get('equalized_odds', 0.5)
            calibration_score = bias_results.get('calibration', 0.5)
            fairness_through_awareness = bias_results.get('individual_fairness', 0.5)
            logger.info("Using pre-computed bias test results from metadata")
            
        # Approach 2: Calculate real metrics from provided test data
        elif metadata and metadata.get('bias_test_data'):
            test_data = metadata['bias_test_data']
            
            # Validate test data schema before processing
            validation = self._validate_bias_test_data(test_data)
            logger.info(f"Bias test data validation: {validation}")
            
            # Calculate each metric if valid, fallback to static analysis if not
            if validation['demographic_parity']:
                try:
                    demographic_parity = self._calculate_demographic_parity(test_data)
                except Exception as e:
                    logger.error(f"Demographic parity calculation failed: {e}, using static analysis")
                    demographic_parity = self._estimate_bias_from_model_characteristics(metadata)['demographic_parity']
            else:
                logger.warning("Demographic parity: Missing required fields (predictions, sensitive_attributes)")
                demographic_parity = self._estimate_bias_from_model_characteristics(metadata)['demographic_parity']
            
            if validation['equalized_odds']:
                try:
                    equalized_odds = self._calculate_equalized_odds(test_data)
                except Exception as e:
                    logger.error(f"Equalized odds calculation failed: {e}, using static analysis")
                    equalized_odds = self._estimate_bias_from_model_characteristics(metadata)['equalized_odds']
            else:
                logger.warning("Equalized odds: Missing required fields (predictions, ground_truth, sensitive_attributes)")
                equalized_odds = self._estimate_bias_from_model_characteristics(metadata)['equalized_odds']
            
            if validation['calibration']:
                try:
                    calibration_score = self._calculate_calibration_score(test_data)
                except Exception as e:
                    logger.error(f"Calibration calculation failed: {e}, using static analysis")
                    calibration_score = self._estimate_bias_from_model_characteristics(metadata)['calibration']
            else:
                logger.warning("Calibration: Missing required fields")
                calibration_score = self._estimate_bias_from_model_characteristics(metadata)['calibration']
            
            if validation['individual_fairness']:
                try:
                    fairness_through_awareness = self._calculate_individual_fairness(test_data)
                except Exception as e:
                    logger.error(f"Individual fairness calculation failed: {e}, using static analysis")
                    fairness_through_awareness = self._estimate_bias_from_model_characteristics(metadata)['individual_fairness']
            else:
                logger.warning("Individual fairness: Missing required fields (features, predictions)")
                fairness_through_awareness = self._estimate_bias_from_model_characteristics(metadata)['individual_fairness']
            
        # Approach 3: Static analysis based on model characteristics
        else:
            logger.info("Using static analysis for bias estimation (no test data provided)")
            bias_metrics = self._estimate_bias_from_model_characteristics(metadata)
            demographic_parity = bias_metrics['demographic_parity']
            equalized_odds = bias_metrics['equalized_odds']
            calibration_score = bias_metrics['calibration']
            fairness_through_awareness = bias_metrics['individual_fairness']
        
        # Calculate overall bias score (higher is better, 1.0 = perfect fairness)
        overall_bias_score = (demographic_parity + equalized_odds + calibration_score + fairness_through_awareness) / 4
        
        # Identify potentially affected groups based on fairness thresholds
        affected_groups = []
        if demographic_parity < 0.8:
            affected_groups.extend(['Gender', 'Age groups'])
        if equalized_odds < 0.7:
            affected_groups.extend(['Ethnic minorities', 'Socioeconomic groups'])
        if calibration_score < 0.7:
            affected_groups.extend(['Religious groups', 'Disability status'])
        if fairness_through_awareness < 0.7:
            affected_groups.extend(['LGBTQ+', 'Geographic regions'])
        
        # Generate evidence-based mitigation recommendations
        mitigation_recommendations = []
        if demographic_parity < 0.8:
            mitigation_recommendations.append('Re-balance training dataset across protected attributes')
        if equalized_odds < 0.7:
            mitigation_recommendations.append('Apply equalized odds post-processing correction')
        if calibration_score < 0.7:
            mitigation_recommendations.append('Implement calibration techniques (Platt scaling, isotonic regression)')
        if fairness_through_awareness < 0.7:
            mitigation_recommendations.append('Add fairness constraints during model training')
        if overall_bias_score < 0.6:
            mitigation_recommendations.append('Conduct comprehensive bias audit with domain experts')
            mitigation_recommendations.append('Establish ongoing bias monitoring system')
        
        return BiasAssessment(
            overall_bias_score=overall_bias_score,
            demographic_parity=demographic_parity,
            equalized_odds=equalized_odds,
            calibration_score=calibration_score,
            fairness_through_awareness=fairness_through_awareness,
            affected_groups=list(set(affected_groups)),
            mitigation_recommendations=mitigation_recommendations
        )
    
    def _calculate_demographic_parity(self, test_data: Dict[str, Any]) -> float:
        """
        Calculate real Demographic Parity fairness metric.
        
        Formula: P(Y=1|A=0) ≈ P(Y=1|A=1)
        Returns ratio (0-1, where 1.0 = perfect parity)
        
        Args:
            test_data: Dict containing 'predictions', 'sensitive_attributes'
        """
        try:
            y_pred = np.array(test_data['predictions'])
            sensitive_attr = np.array(test_data['sensitive_attributes'])
            
            # Get unique groups
            unique_groups = np.unique(sensitive_attr)
            if len(unique_groups) < 2:
                logger.info("Demographic parity: Only one group found, returning default score")
                return 0.8  # Default if only one group
            
            # Calculate positive prediction rate for each group
            rates = []
            for group in unique_groups:
                mask = sensitive_attr == group
                group_size = np.sum(mask)
                if group_size > 0:
                    positive_rate = float(np.mean(y_pred[mask] == 1))
                    rates.append(positive_rate)
                    logger.debug(f"Group {group}: positive rate = {positive_rate:.3f} (n={group_size})")
            
            # Edge case: insufficient valid groups
            if len(rates) < 2:
                logger.warning("Demographic parity: Less than 2 groups with data")
                return 0.7
            
            # Edge case: all predictions are negative (max rate = 0)
            if max(rates) == 0:
                logger.info("Demographic parity: All predictions negative across all groups (perfect parity)")
                return 1.0  # Perfect parity if all groups have 0% positive rate
            
            # Edge case: all predictions are positive (min rate = 1.0)
            if min(rates) == 1.0:
                logger.info("Demographic parity: All predictions positive across all groups (perfect parity)")
                return 1.0  # Perfect parity if all groups have 100% positive rate
            
            # Calculate demographic parity ratio
            parity_ratio = min(rates) / max(rates)
            return float(parity_ratio)
                
        except (KeyError, ValueError, ZeroDivisionError) as e:
            logger.warning(f"Could not calculate demographic parity from test data: {e}")
            return 0.7  # Conservative default
    
    def _calculate_equalized_odds(self, test_data: Dict[str, Any]) -> float:
        """
        Calculate real Equalized Odds fairness metric.
        
        Formula: TPR_A=0 ≈ TPR_A=1 AND FPR_A=0 ≈ FPR_A=1
        Returns average ratio (0-1, where 1.0 = perfect equality)
        
        Args:
            test_data: Dict containing 'predictions', 'ground_truth', 'sensitive_attributes'
        """
        try:
            y_pred = np.array(test_data['predictions'])
            y_true = np.array(test_data['ground_truth'])
            sensitive_attr = np.array(test_data['sensitive_attributes'])
            
            unique_groups = np.unique(sensitive_attr)
            if len(unique_groups) < 2:
                logger.info("Equalized odds: Only one group found, returning default score")
                return 0.7  # Default
            
            tpr_list = []
            fpr_list = []
            valid_groups = 0
            
            for group in unique_groups:
                mask = sensitive_attr == group
                y_pred_group = y_pred[mask]
                y_true_group = y_true[mask]
                
                # True Positive Rate
                true_positives = int(np.sum((y_pred_group == 1) & (y_true_group == 1)))
                actual_positives = int(np.sum(y_true_group == 1))
                
                # False Positive Rate
                false_positives = int(np.sum((y_pred_group == 1) & (y_true_group == 0)))
                actual_negatives = int(np.sum(y_true_group == 0))
                
                # Skip groups that lack either positive or negative labels
                if actual_positives == 0 or actual_negatives == 0:
                    logger.warning(f"Equalized odds: Group {group} lacks positive or negative labels "
                                 f"(pos={actual_positives}, neg={actual_negatives}), skipping")
                    continue
                
                tpr = true_positives / actual_positives
                fpr = false_positives / actual_negatives
                tpr_list.append(float(tpr))
                fpr_list.append(float(fpr))
                valid_groups += 1
                
                logger.debug(f"Group {group}: TPR={tpr:.3f}, FPR={fpr:.3f}")
            
            # Edge case: insufficient valid groups after filtering
            if valid_groups < 2:
                logger.warning(f"Equalized odds: Only {valid_groups} valid groups after filtering, need at least 2")
                return 0.6  # Penalize datasets with class imbalance
            
            # Edge case: all TPRs are 0 (no true positives in any group)
            if max(tpr_list) == 0:
                logger.info("Equalized odds: All TPRs are 0 (no true positives), using FPR only")
                tpr_ratio = 1.0  # Perfect TPR equality (all zero)
            else:
                tpr_ratio = min(tpr_list) / max(tpr_list)
            
            # Edge case: all FPRs are 0 (no false positives in any group)
            if max(fpr_list) == 0:
                logger.info("Equalized odds: All FPRs are 0 (no false positives), using TPR only")
                fpr_ratio = 1.0  # Perfect FPR equality (all zero)
            else:
                fpr_ratio = min(fpr_list) / max(fpr_list)
            
            # Average of TPR and FPR equality
            result = (tpr_ratio + fpr_ratio) / 2
            return float(result)
            
        except (KeyError, ValueError, ZeroDivisionError) as e:
            logger.warning(f"Could not calculate equalized odds from test data: {e}")
            return 0.6  # Conservative default
    
    def _calculate_calibration_score(self, test_data: Dict[str, Any]) -> float:
        """
        Calculate real Calibration Score fairness metric.
        
        Formula: P(Y=1|Score=s,A=0) ≈ P(Y=1|Score=s,A=1)
        Returns calibration quality (0-1, where 1.0 = perfect calibration)
        
        Args:
            test_data: Dict containing 'probabilities', 'ground_truth', 'sensitive_attributes'
        """
        try:
            if 'probabilities' not in test_data:
                # If no probabilities, fallback to demographic parity
                logger.info("Calibration: No probabilities provided, using demographic parity instead")
                return self._calculate_demographic_parity(test_data)
            
            y_prob = np.array(test_data['probabilities'], dtype=float)
            y_true = np.array(test_data['ground_truth'])
            sensitive_attr = np.array(test_data['sensitive_attributes'])
            
            # Validate data
            if len(y_prob) != len(y_true) or len(y_prob) != len(sensitive_attr):
                logger.warning("Calibration: Mismatched array lengths")
                return 0.65
            
            unique_groups = np.unique(sensitive_attr)
            if len(unique_groups) < 2:
                logger.info("Calibration: Only one group found, returning default score")
                return 0.7
            
            # Bin probabilities into 10 bins
            bins = np.linspace(0, 1, 11)
            calibration_errors = []
            bins_processed = 0
            
            for group in unique_groups:
                mask = sensitive_attr == group
                y_prob_group = y_prob[mask]
                y_true_group = y_true[mask]
                
                if len(y_prob_group) < 10:
                    logger.warning(f"Calibration: Group {group} has only {len(y_prob_group)} samples, skipping")
                    continue
                
                # Calculate calibration error per bin
                for i in range(len(bins) - 1):
                    bin_mask = (y_prob_group >= bins[i]) & (y_prob_group < bins[i+1])
                    bin_count = np.sum(bin_mask)
                    
                    if bin_count >= 5:  # At least 5 samples per bin
                        predicted_prob = float(np.mean(y_prob_group[bin_mask]))
                        actual_prob = float(np.mean(y_true_group[bin_mask]))
                        
                        # Check for NaN values
                        if np.isnan(predicted_prob) or np.isnan(actual_prob):
                            logger.warning(f"Calibration: NaN detected in bin {i} for group {group}, skipping")
                            continue
                        
                        error = abs(predicted_prob - actual_prob)
                        calibration_errors.append(error)
                        bins_processed += 1
                        logger.debug(f"Group {group}, Bin {i}: pred={predicted_prob:.3f}, actual={actual_prob:.3f}, error={error:.3f}")
            
            # Edge case: no valid bins processed
            if len(calibration_errors) == 0:
                logger.warning("Calibration: No valid bins processed, data too sparse")
                return 0.6  # Penalize sparse data
            
            # Edge case: very few bins (< 5 total across all groups)
            if bins_processed < 5:
                logger.warning(f"Calibration: Only {bins_processed} bins processed, results may be unreliable")
            
            # Calculate average calibration error (filter out any NaNs)
            valid_errors = [e for e in calibration_errors if not np.isnan(e)]
            if len(valid_errors) == 0:
                logger.warning("Calibration: All errors are NaN")
                return 0.6
            
            avg_calibration_error = float(np.mean(valid_errors))
            calibration_score = max(0.0, 1.0 - avg_calibration_error)
            
            logger.debug(f"Calibration: {bins_processed} bins, avg error={avg_calibration_error:.3f}, score={calibration_score:.3f}")
            return calibration_score
                
        except (KeyError, ValueError, TypeError) as e:
            logger.warning(f"Could not calculate calibration score from test data: {e}")
            return 0.65  # Conservative default
    
    def _calculate_individual_fairness(self, test_data: Dict[str, Any]) -> float:
        """
        Calculate Individual Fairness metric (Lipschitz continuity).
        
        Formula: d(f(x1),f(x2)) ≤ L*d(x1,x2)
        Returns fairness score (0-1, where 1.0 = perfect individual fairness)
        
        Args:
            test_data: Dict containing 'features', 'predictions'
        """
        try:
            if 'features' not in test_data or 'predictions' not in test_data:
                # Fallback to demographic parity if features unavailable
                return self._calculate_demographic_parity(test_data)
            
            X = np.array(test_data['features'])
            y_pred = np.array(test_data['predictions'])
            
            # Sample pairs of similar individuals (within 10% feature distance)
            n_samples = min(100, len(X))  # Limit for performance
            lipschitz_violations = 0
            total_comparisons = 0
            
            for _ in range(n_samples):
                # Randomly sample two individuals
                idx1, idx2 = np.random.choice(len(X), 2, replace=False)
                x1, x2 = X[idx1], X[idx2]
                pred1, pred2 = y_pred[idx1], y_pred[idx2]
                
                # Calculate feature distance (normalized Euclidean)
                feature_distance = np.linalg.norm(x1 - x2) / np.sqrt(len(x1))
                
                # Calculate prediction distance
                pred_distance = abs(pred1 - pred2)
                
                # Check Lipschitz constraint with L=1.0
                # Similar individuals should get similar predictions
                if feature_distance < 0.1:  # Similar individuals
                    total_comparisons += 1
                    if pred_distance > feature_distance * 1.5:  # Lipschitz constant = 1.5
                        lipschitz_violations += 1
            
            if total_comparisons > 0:
                fairness_score = 1.0 - (lipschitz_violations / total_comparisons)
                return max(0, fairness_score)
            else:
                return 0.7
                
        except (KeyError, ValueError):
            logger.warning("Could not calculate individual fairness from test data")
            return 0.65  # Conservative default
    
    def _estimate_bias_from_model_characteristics(self, metadata: Dict[str, Any]) -> Dict[str, float]:
        """
        Estimate bias risk from model characteristics when test data unavailable.
        
        Uses static analysis of model properties to provide informed estimates
        (much better than random values).
        
        Args:
            metadata: Model metadata including training info, data sources, etc.
        """
        # Base fairness scores (neutral starting point)
        demographic_parity = 0.75
        equalized_odds = 0.70
        calibration = 0.72
        individual_fairness = 0.68
        
        # Adjust based on model characteristics
        if metadata:
            # Model complexity (simpler models = less bias potential)
            model_type = metadata.get('model_type', '').lower()
            if 'linear' in model_type or 'logistic' in model_type:
                demographic_parity += 0.10
                equalized_odds += 0.08
            elif 'tree' in model_type or 'forest' in model_type:
                demographic_parity += 0.05
                equalized_odds += 0.05
            elif 'neural' in model_type or 'deep' in model_type:
                demographic_parity -= 0.05  # More complex = higher bias risk
                equalized_odds -= 0.05
            
            # Training data quality indicators
            if metadata.get('balanced_dataset', False):
                demographic_parity += 0.08
                equalized_odds += 0.07
            
            if metadata.get('diverse_training_data', False):
                demographic_parity += 0.05
                calibration += 0.05
            
            # Fairness constraints during training
            if metadata.get('fairness_constraints_applied', False):
                demographic_parity += 0.10
                equalized_odds += 0.10
                individual_fairness += 0.12
            
            # Bias testing performed
            if metadata.get('bias_testing_conducted', False):
                calibration += 0.08
                individual_fairness += 0.08
            
            # Model size (larger models = more capacity for bias)
            model_size_mb = metadata.get('model_size_mb', 0)
            if model_size_mb > 1000:  # Large model
                demographic_parity -= 0.03
                equalized_odds -= 0.03
            elif model_size_mb < 10:  # Small model
                demographic_parity += 0.03
                individual_fairness += 0.03
            
            # Industry/domain risk factors
            use_case = metadata.get('use_case', '').lower()
            high_risk_domains = ['hiring', 'lending', 'criminal', 'healthcare', 'insurance']
            if any(domain in use_case for domain in high_risk_domains):
                # High-risk domains require more scrutiny
                demographic_parity -= 0.08
                equalized_odds -= 0.08
                logger.warning(f"High-risk domain detected: {use_case} - requires bias testing")
        
        # Clamp values to [0.5, 0.95] range
        return {
            'demographic_parity': max(0.5, min(0.95, demographic_parity)),
            'equalized_odds': max(0.5, min(0.95, equalized_odds)),
            'calibration': max(0.5, min(0.95, calibration)),
            'individual_fairness': max(0.5, min(0.95, individual_fairness))
        }
    
    def _assess_model_explainability(self, model_file: Any, metadata: Dict[str, Any]) -> ExplainabilityAssessment:
        """Assess model explainability and interpretability"""
        
        # Determine model transparency level
        framework = metadata.get('framework', 'Unknown')
        model_type = metadata.get('model_type', 'Unknown')
        
        if 'tree' in model_type.lower() or 'linear' in model_type.lower():
            transparency = 'glass_box'
            interpretability_score = 0.9
        elif 'neural' in model_type.lower() or 'deep' in framework.lower():
            transparency = 'black_box'
            interpretability_score = 0.2
        else:
            transparency = 'gray_box'
            interpretability_score = 0.6
        
        # Assess explanation capabilities
        feature_importance_available = metadata.get('feature_importance', False)
        decision_explanations = metadata.get('explanation_method', 'Not Available')
        audit_trail_quality = 'Good' if metadata.get('audit_logging', False) else 'Limited'
        user_understanding_level = 'Technical' if interpretability_score > 0.7 else 'Limited'
        
        return ExplainabilityAssessment(
            interpretability_score=interpretability_score,
            model_transparency=transparency,
            feature_importance_available=feature_importance_available,
            decision_explanations=decision_explanations,
            audit_trail_quality=audit_trail_quality,
            user_understanding_level=user_understanding_level
        )
    
    def _assess_ai_governance(self, metadata: Dict[str, Any]) -> AIGovernanceAssessment:
        """Assess AI governance and risk management practices"""
        
        return AIGovernanceAssessment(
            risk_management_system=metadata.get('risk_management_system', False),
            human_oversight_implemented=metadata.get('human_oversight', False),
            data_governance_score=metadata.get('data_governance_score', 0.0),
            documentation_completeness=metadata.get('documentation_completeness', 0.0),
            testing_validation_score=metadata.get('testing_validation_score', 0.0),
            monitoring_systems=metadata.get('monitoring_systems', False),
            incident_response_plan=metadata.get('incident_response_plan', False)
        )
    
    def _generate_ai_findings(self, ai_act_compliance: Dict[str, Any], 
                            bias_assessment: BiasAssessment,
                            explainability_assessment: ExplainabilityAssessment,
                            governance_assessment: AIGovernanceAssessment) -> List[Dict[str, Any]]:
        """Generate comprehensive AI findings"""
        findings = []
        
        # AI Act compliance findings
        if ai_act_compliance['prohibited_violations']:
            for violation in ai_act_compliance['prohibited_violations']:
                findings.append({
                    'type': 'ai_act_prohibited',
                    'category': 'AI Act Violation',
                    'severity': 'Critical',
                    'title': f"Prohibited AI Practice: {violation['violation']}",
                    'description': violation['description'],
                    'location': violation['article'],
                    'impact': violation['penalty_risk'],
                    'recommendation': 'Immediately discontinue prohibited AI practice'
                })
        
        # High-risk system compliance findings
        if ai_act_compliance['risk_category'] == 'High-Risk AI System':
            high_risk_compliance = ai_act_compliance['high_risk_compliance']
            if high_risk_compliance['compliance_percentage'] < 100:
                findings.append({
                    'type': 'ai_act_high_risk',
                    'category': 'AI Act Compliance',
                    'severity': 'High',
                    'title': 'High-Risk AI System Non-Compliance',
                    'description': f"High-risk AI system meets only {high_risk_compliance['compliance_percentage']:.0f}% of requirements",
                    'location': 'AI Act Articles 8-15',
                    'impact': 'Up to €15M or 3% of annual turnover',
                    'missing_requirements': high_risk_compliance['missing_requirements']
                })
        
        # Bias and fairness findings
        if bias_assessment.overall_bias_score < 0.7:
            findings.append({
                'type': 'ai_bias',
                'category': 'Fairness & Bias',
                'severity': 'High' if bias_assessment.overall_bias_score < 0.5 else 'Medium',
                'title': 'AI Model Bias Detected',
                'description': f"Model shows bias with overall fairness score of {bias_assessment.overall_bias_score:.2f}",
                'location': 'Model Output Analysis',
                'affected_groups': bias_assessment.affected_groups,
                'recommendations': bias_assessment.mitigation_recommendations
            })
        
        # Explainability findings
        if explainability_assessment.interpretability_score < 0.5:
            findings.append({
                'type': 'ai_explainability',
                'category': 'Transparency & Explainability',
                'severity': 'Medium',
                'title': 'Limited Model Explainability',
                'description': f"Model has low interpretability score ({explainability_assessment.interpretability_score:.2f})",
                'location': 'Model Architecture',
                'impact': 'May not meet transparency obligations for high-risk systems',
                'recommendation': 'Implement explanation methods (SHAP, LIME) or use interpretable models'
            })
        
        # Governance findings
        governance_issues = []
        if not governance_assessment.risk_management_system:
            governance_issues.append('Risk management system not implemented')
        if not governance_assessment.human_oversight_implemented:
            governance_issues.append('Human oversight not implemented')
        if governance_assessment.data_governance_score < 0.7:
            governance_issues.append('Inadequate data governance practices')
        
        if governance_issues:
            findings.append({
                'type': 'ai_governance',
                'category': 'AI Governance',
                'severity': 'Medium',
                'title': 'AI Governance Gaps',
                'description': f"AI governance deficiencies identified: {', '.join(governance_issues)}",
                'location': 'AI System Management',
                'impact': 'Increased operational and compliance risks',
                'recommendations': [
                    'Implement comprehensive AI governance framework',
                    'Establish risk management procedures',
                    'Add human oversight mechanisms'
                ]
            })
        
        return findings
    
    def _calculate_ai_risk_score(self, ai_act_compliance: Dict[str, Any],
                                bias_assessment: BiasAssessment,
                                explainability_assessment: ExplainabilityAssessment,
                                governance_assessment: AIGovernanceAssessment) -> float:
        """Calculate overall AI risk score"""
        
        risk_components = []
        
        # AI Act compliance risk (40% weight)
        if ai_act_compliance['prohibited_violations']:
            risk_components.append(100 * 0.4)  # Maximum risk for prohibited practices
        elif ai_act_compliance['risk_category'] == 'High-Risk AI System':
            high_risk_compliance = ai_act_compliance['high_risk_compliance']
            compliance_risk = (100 - high_risk_compliance['compliance_percentage']) * 0.4
            risk_components.append(compliance_risk)
        else:
            risk_components.append(20 * 0.4)  # Base risk for other categories
        
        # Bias risk (25% weight)
        bias_risk = (1 - bias_assessment.overall_bias_score) * 100 * 0.25
        risk_components.append(bias_risk)
        
        # Explainability risk (20% weight)
        explainability_risk = (1 - explainability_assessment.interpretability_score) * 100 * 0.2
        risk_components.append(explainability_risk)
        
        # Governance risk (15% weight)
        governance_score = (
            governance_assessment.data_governance_score +
            governance_assessment.documentation_completeness +
            governance_assessment.testing_validation_score
        ) / 3
        governance_risk = (1 - governance_score) * 100 * 0.15
        risk_components.append(governance_risk)
        
        return min(100, sum(risk_components))
    
    def _generate_ai_recommendations(self, ai_act_compliance: Dict[str, Any],
                                   bias_assessment: BiasAssessment,
                                   governance_assessment: AIGovernanceAssessment) -> List[Dict[str, Any]]:
        """Generate AI-specific recommendations"""
        recommendations = []
        
        # AI Act compliance recommendations
        if ai_act_compliance['risk_category'] == 'High-Risk AI System':
            recommendations.append({
                'priority': 'Critical',
                'category': 'AI Act Compliance',
                'action': 'Implement High-Risk AI System Requirements',
                'description': 'Ensure compliance with all EU AI Act requirements for high-risk systems',
                'effort_estimate': '3-6 months',
                'cost_estimate': '€50,000-€200,000'
            })
        
        # Bias mitigation recommendations
        if bias_assessment.overall_bias_score < 0.7:
            recommendations.append({
                'priority': 'High',
                'category': 'Fairness & Bias',
                'action': 'Implement Bias Mitigation Strategy',
                'description': 'Address identified bias issues through data, algorithmic, and post-processing interventions',
                'effort_estimate': '2-4 months',
                'cost_estimate': '€20,000-€75,000'
            })
        
        # Governance recommendations
        if not governance_assessment.risk_management_system:
            recommendations.append({
                'priority': 'Medium',
                'category': 'AI Governance',
                'action': 'Establish AI Risk Management System',
                'description': 'Implement comprehensive AI risk management framework and procedures',
                'effort_estimate': '1-3 months',
                'cost_estimate': '€15,000-€50,000'
            })
        
        return recommendations
    
    def _determine_compliance_status(self, risk_category: AIRiskCategory,
                                   prohibited_violations: List[Dict[str, Any]],
                                   high_risk_compliance: Dict[str, Any],
                                   gp_compliance: Dict[str, Any]) -> AIActCompliance:
        """Determine overall AI Act compliance status"""
        
        if prohibited_violations:
            return AIActCompliance.NON_COMPLIANT
        
        if risk_category == AIRiskCategory.HIGH_RISK:
            if high_risk_compliance.get('compliance_percentage', 0) < 80:
                return AIActCompliance.NON_COMPLIANT
            elif high_risk_compliance.get('compliance_percentage', 0) < 100:
                return AIActCompliance.REQUIRES_ASSESSMENT
            else:
                return AIActCompliance.COMPLIANT
        
        if risk_category == AIRiskCategory.GENERAL_PURPOSE:
            if gp_compliance.get('compliance_percentage', 0) < 100:
                return AIActCompliance.REQUIRES_ASSESSMENT
            else:
                return AIActCompliance.COMPLIANT
        
        return AIActCompliance.COMPLIANT
    
    def _assess_potential_penalties(self, compliance_status: AIActCompliance,
                                  prohibited_violations: List[Dict[str, Any]],
                                  high_risk_compliance: Dict[str, Any]) -> Dict[str, Any]:
        """Assess potential AI Act penalties"""
        
        if prohibited_violations:
            return {
                'risk_level': 'Critical',
                'max_fine_eur': 35_000_000,
                'max_fine_percentage': 7.0,
                'description': 'Maximum penalties for prohibited AI practices'
            }
        
        if compliance_status == AIActCompliance.NON_COMPLIANT and high_risk_compliance:
            return {
                'risk_level': 'High',
                'max_fine_eur': 15_000_000,
                'max_fine_percentage': 3.0,
                'description': 'Penalties for high-risk AI system non-compliance'
            }
        
        if compliance_status == AIActCompliance.REQUIRES_ASSESSMENT:
            return {
                'risk_level': 'Medium',
                'max_fine_eur': 7_500_000,
                'max_fine_percentage': 1.5,
                'description': 'Penalties for information obligation violations'
            }
        
        return {
            'risk_level': 'Low',
            'max_fine_eur': 0,
            'max_fine_percentage': 0.0,
            'description': 'No significant penalty risk identified'
        }

def scan_ai_model_advanced(model_file: Any, model_metadata: Optional[Dict[str, Any]] = None, 
                          region: str = "Netherlands") -> Dict[str, Any]:
    """
    Convenience function for advanced AI model scanning.
    
    Args:
        model_file: AI model file or object to scan
        model_metadata: Additional metadata about the model
        region: Regulatory region for compliance assessment
        
    Returns:
        Comprehensive AI model analysis results
    """
    scanner = AdvancedAIScanner(region=region)
    return scanner.scan_ai_model_comprehensive(model_file, model_metadata or {})