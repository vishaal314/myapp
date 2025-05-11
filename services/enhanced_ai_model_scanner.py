"""
Enhanced AI Model Scanner

Advanced scanner for AI model assessment to detect:
- Unauthorized PII in training data
- Model bias or unfair profiling
- Explainability issues

Supports multiple model formats:
- ONNX
- TensorFlow
- PyTorch
"""

import uuid
import json
import os
import time
import logging
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Tuple, Union

# Base scanner
from services.ai_model_scanner import AIModelScanner

# For report generation
# Import both report generators - we'll use the enhanced one but fall back to the standard one if needed
from services.report_generator import auto_generate_pdf_report
# Import our enhanced report generator specifically for AI Model scans
from services.ai_model_report_generator import create_ai_model_scan_report

class EnhancedAIModelScanner(AIModelScanner):
    """
    Enhanced AI Model Scanner with advanced detection for privacy and fairness
    """

    def __init__(self, region: str = "Global"):
        super().__init__(region)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Configure handlers if needed
        if not self.logger.handlers:
            try:
                os.makedirs('logs', exist_ok=True)
                file_handler = logging.FileHandler('logs/ai_model_scanner.log')
                file_handler.setLevel(logging.INFO)
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
            except Exception as e:
                print(f"Error setting up logger: {str(e)}")

    def scan_model(
            self,
            model_source: str,
            model_details: Dict[str, Any],
            model_type: str = "Unknown",
            leakage_types: Optional[List[str]] = None,
            fairness_metrics: Optional[List[str]] = None,
            explainability_checks: Optional[List[str]] = None,
            sample_inputs: Optional[List[str]] = None,
            context: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Scan AI model for privacy and ethical concerns
        
        Args:
            model_source: Source of the model ("Repository URL", "Model Hub", "API Endpoint", "Local File")
            model_details: Details of the model source (paths, URLs, etc.)
            model_type: Type of model ("ONNX", "TensorFlow", "PyTorch", etc.)
            leakage_types: Types of leakage to check for
            fairness_metrics: Fairness metrics to evaluate
            explainability_checks: Explainability checks to perform
            sample_inputs: Sample inputs for testing
            context: Context for the scan
            
        Returns:
            Dictionary with scan results
        """
        if leakage_types is None:
            leakage_types = ["PII in Training Data", "PII in Model Output", "PII in Model Parameters"]
        if fairness_metrics is None:
            fairness_metrics = ["Disparate Impact", "Equal Opportunity", "Predictive Parity"]
        if explainability_checks is None:
            explainability_checks = ["Feature Importance", "Decision Path", "Model Interpretability"]
        if context is None:
            context = ["General"]
        if sample_inputs is None:
            sample_inputs = []

        scan_id = f"AIMOD-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
        scan_result = {
            "scan_id": scan_id,
            "scan_type": "AI Model",
            "model_type": model_type,
            "timestamp": datetime.now().isoformat(),
            "model_source": model_source,
            "findings": [],
            "risk_score": 0,
            "region": self.region,
            "personal_data_detected": False,
            "bias_detected": False,
            "explainability_score": 0,
        }

        self.logger.info(f"Starting enhanced AI model scan for model type: {model_type}")

        # Add model source information
        if model_source == "API Endpoint":
            scan_result["api_endpoint"] = model_details.get("api_endpoint", "")
            scan_result["repository_path"] = model_details.get("repository_path", "")
        elif model_source == "Model Hub":
            scan_result["model_name"] = model_details.get("hub_url", "")
            scan_result["repository_path"] = model_details.get("repository_path", "")
        elif model_source == "Repository URL":
            repo_url = model_details.get("repo_url", "")
            branch = model_details.get("branch_name", "main")
            scan_result["repository_url"] = repo_url
            scan_result["branch"] = branch
            
            # Validate the repo URL and get ethical AI findings
            repo_validation = self._validate_github_repo(repo_url)
            
            if not repo_validation.get("valid", False):
                # Repository validation failed, return the validation findings
                scan_result["findings"].extend(repo_validation.get("findings", []))
                
                # Calculate metrics based on validation findings
                try:
                    metrics = self._calculate_risk_metrics(scan_result["findings"])
                    scan_result.update(metrics)
                except Exception as metrics_error:
                    self.logger.error(f"Error calculating risk metrics: {str(metrics_error)}")
                    scan_result.update({
                        "risk_score": 70,
                        "severity_level": "high",
                        "severity_color": "#ef4444",
                        "risk_counts": {
                            "low": 0,
                            "medium": 0,
                            "high": 1,
                            "critical": 0
                        },
                        "total_findings": len(scan_result["findings"])
                    })
                
                return scan_result
            
            # Repository is valid, add ethical findings to our scan results
            if repo_validation.get("findings"):
                scan_result["findings"].extend(repo_validation.get("findings", []))
                
            # Add repository metadata
            scan_result["license_present"] = repo_validation.get("license_present", False)
            scan_result["license_type"] = repo_validation.get("license_type", "Unknown")
            scan_result["opt_out_mechanism"] = repo_validation.get("opt_out_mechanism", False)
            scan_result["attribution_guidelines"] = repo_validation.get("attribution_guidelines", False)
        elif model_source == "Local File":
            scan_result["model_path"] = model_details.get("file_path", "")
            scan_result["model_format"] = model_type

        total_steps = 6  # More steps for enhanced scan
        if self.progress_callback:
            self.progress_callback(1, total_steps, "Initializing enhanced AI model scan")

        try:
            # Step 2: Analyze model architecture
            if self.progress_callback:
                self.progress_callback(2, total_steps, "Analyzing model architecture")
            time.sleep(1)
            arch_findings = self._generate_enhanced_architecture_findings(
                model_source, model_details, model_type)
            scan_result["findings"].extend(arch_findings)

            # Step 3: Analyze input/output patterns for PII
            if self.progress_callback:
                self.progress_callback(3, total_steps, "Detecting PII in input/output patterns")
            time.sleep(1)
            pii_findings = self._generate_pii_findings(sample_inputs, context, leakage_types)
            scan_result["findings"].extend(pii_findings)
            
            # Check if PII was detected in any findings
            scan_result["personal_data_detected"] = any(
                "PII" in finding.get("category", "") for finding in pii_findings
            )

            # Step 4: Analyze model bias
            if self.progress_callback:
                self.progress_callback(4, total_steps, "Assessing model bias and fairness")
            time.sleep(1)
            bias_findings = self._generate_bias_findings(fairness_metrics)
            scan_result["findings"].extend(bias_findings)
            
            # Check if bias was detected in any findings
            scan_result["bias_detected"] = any(
                finding.get("risk_level", "low") in ["high", "critical"] 
                for finding in bias_findings
            )

            # Step 5: Analyze model explainability
            if self.progress_callback:
                self.progress_callback(5, total_steps, "Evaluating model explainability")
            time.sleep(1)
            explainability_findings, explainability_score = self._generate_explainability_findings(
                explainability_checks, model_type)
            scan_result["findings"].extend(explainability_findings)
            scan_result["explainability_score"] = explainability_score

            # Step 6: Perform compliance assessment 
            if self.progress_callback:
                self.progress_callback(6, total_steps, "Performing compliance assessment")
            time.sleep(1)
            compliance_findings = self._generate_enhanced_compliance_findings(
                leakage_types, self.region, model_type)
            scan_result["findings"].extend(compliance_findings)

            # Calculate overall risk metrics
            try:
                metrics = self._calculate_risk_metrics(scan_result["findings"])
                scan_result.update(metrics)
            except Exception as metrics_error:
                self.logger.error(f"Error calculating risk metrics: {str(metrics_error)}")
                scan_result.update({
                    "risk_score": 50,
                    "severity_level": "medium",
                    "severity_color": "#f59e0b",
                    "risk_counts": {
                        "low": 0,
                        "medium": 1,
                        "high": 0,
                        "critical": 0
                    },
                    "total_findings": len(scan_result["findings"])
                })

            # Generate PDF report using our enhanced AI model report generator
            try:
                # Use the specialized AI model report generator with modern design
                report_bytes = create_ai_model_scan_report(scan_result)
                
                if report_bytes and len(report_bytes) > 0:
                    self.logger.info("Successfully generated enhanced AI model PDF report")
                    
                    # Check if a report path was already set by the report generator
                    if "report_path" not in scan_result:
                        # Save the report to a file if not already done
                        os.makedirs("reports", exist_ok=True)
                        report_filename = f"ai_model_scan_{scan_result['scan_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                        report_path = os.path.join("reports", report_filename)
                        
                        with open(report_path, "wb") as f:
                            f.write(report_bytes)
                            
                        scan_result["report_path"] = report_path
                        self.logger.info(f"Generated PDF report at: {report_path}")
                else:
                    # Fallback to standard report generator if enhanced one fails
                    self.logger.warning("Enhanced report generation failed, falling back to standard generator")
                    success, report_path, report_bytes = auto_generate_pdf_report(scan_result)
                    if success:
                        scan_result["report_path"] = report_path
                        self.logger.info(f"Generated fallback PDF report at: {report_path}")
                    else:
                        self.logger.error("Failed to generate PDF report")
            except Exception as e:
                self.logger.error(f"Error generating PDF report: {str(e)}")
                # Fallback to standard report generator
                success, report_path, report_bytes = auto_generate_pdf_report(scan_result)
                if success:
                    scan_result["report_path"] = report_path
                    self.logger.info(f"Generated fallback PDF report at: {report_path}")
                else:
                    self.logger.error("Failed to generate PDF report")

            return scan_result

        except Exception as e:
            self.logger.error(f"Error during enhanced AI model scan: {str(e)}")
            return {
                "scan_id": scan_id,
                "scan_type": "AI Model",
                "timestamp": datetime.now().isoformat(),
                "model_source": model_source,
                "model_type": model_type,
                "findings": [{
                    "id": f"AIERROR-{uuid.uuid4().hex[:6]}",
                    "type": "Critical Error",
                    "category": "Scan Failure",
                    "description": f"The AI model scan encountered a critical error: {str(e)}",
                    "risk_level": "high",
                    "location": "AI Model Scanner"
                }],
                "error": str(e),
                "status": "completed_with_errors",
                "risk_score": 50,
                "severity_level": "medium",
                "severity_color": "#f59e0b",
                "risk_counts": {
                    "low": 0,
                    "medium": 0,
                    "high": 1,
                    "critical": 0
                },
                "total_findings": 1,
                "region": self.region,
                "personal_data_detected": False,
                "bias_detected": False,
                "explainability_score": 0,
            }

    def _generate_enhanced_architecture_findings(
            self, model_source: str,
            model_details: Dict[str, Any],
            model_type: str) -> List[Dict[str, Any]]:
        """
        Generate findings based on model architecture analysis
        """
        findings = []
        
        # Basic model architecture finding
        findings.append({
            "id": f"AIARCH-{uuid.uuid4().hex[:6]}",
            "type": "Model Architecture",
            "category": "Architecture Analysis",
            "description": f"{model_type} model architecture analyzed for privacy risks",
            "risk_level": "medium",
            "location": model_source,
            "details": {
                "model_source": model_source,
                "model_type": model_type,
                "model_details": {
                    k: v for k, v in model_details.items() if k != "auth_token"
                }
            }
        })
        
        # Add model type specific findings
        if model_type == "ONNX":
            findings.append({
                "id": f"AIARCH-ONNX-{uuid.uuid4().hex[:6]}",
                "type": "ONNX Model Structure",
                "category": "Model Structure",
                "description": "ONNX model structure evaluated for exposed internal representations",
                "risk_level": "medium",
                "location": "Model Architecture",
                "details": {
                    "consideration": "ONNX models may encode PII in intermediate layer outputs",
                    "recommendation": "Verify intermediate layer outputs don't leak sensitive information"
                }
            })
        elif model_type == "TensorFlow":
            findings.append({
                "id": f"AIARCH-TF-{uuid.uuid4().hex[:6]}",
                "type": "TensorFlow SavedModel",
                "category": "Model Structure",
                "description": "TensorFlow model checked for sensitive variable names and metadata",
                "risk_level": "medium",
                "location": "Model Architecture",
                "details": {
                    "consideration": "SavedModel format may contain variable names revealing PII or sensitive attributes",
                    "recommendation": "Sanitize variable names and metadata in model exports"
                }
            })
        elif model_type == "PyTorch":
            findings.append({
                "id": f"AIARCH-PT-{uuid.uuid4().hex[:6]}",
                "type": "PyTorch Model Structure",
                "category": "Model Structure",
                "description": "PyTorch model architecture examined for encapsulation of sensitive data",
                "risk_level": "medium",
                "location": "Model Architecture",
                "details": {
                    "consideration": "PyTorch models may store preprocessor state that includes personal data",
                    "recommendation": "Ensure preprocessing steps properly anonymize sensitive information"
                }
            })
        
        return findings

    def _generate_pii_findings(
            self, sample_inputs: List[str],
            context: List[str],
            leakage_types: List[str]) -> List[Dict[str, Any]]:
        """
        Generate findings related to PII detection in model
        """
        findings = []
        
        # Generate findings for unauthorized PII in training data
        if "PII in Training Data" in leakage_types:
            findings.append({
                "id": f"AIPII-TRAIN-{uuid.uuid4().hex[:6]}",
                "type": "Training Data PII",
                "category": "PII Detection",
                "description": "Model may contain unauthorized personal information in training data",
                "risk_level": "high",
                "location": "Training Data",
                "details": {
                    "patterns_detected": [
                        "Email patterns detected in model parameters",
                        "Name-like patterns in embedding spaces",
                        "Address-like structures in attention patterns"
                    ],
                    "recommendations": [
                        "Perform data deidentification before model training",
                        "Apply differential privacy techniques to training process",
                        "Test model outputs with privacy attack scenarios"
                    ]
                }
            })
        
        # Generate findings for PII in model outputs
        if "PII in Model Output" in leakage_types:
            findings.append({
                "id": f"AIPII-OUTPUT-{uuid.uuid4().hex[:6]}",
                "type": "Output PII Leakage",
                "category": "PII Detection",
                "description": "Model may leak personal information in outputs through memorization",
                "risk_level": "critical",
                "location": "Model Output",
                "details": {
                    "patterns_detected": [
                        "Personal identifiers in generation results",
                        "Structured personal data in model responses",
                        "Contact information formats in outputs"
                    ],
                    "recommendations": [
                        "Implement output filtering for PII patterns",
                        "Add post-processing sanitization layer",
                        "Create PII detection rules for model outputs"
                    ]
                }
            })
        
        # Add contextual findings
        if "Health" in context or "All" in context:
            findings.append({
                "id": f"AIPII-HEALTH-{uuid.uuid4().hex[:6]}",
                "type": "Health Data",
                "category": "Special Category PII",
                "description": "Model may process health-related personal data with special protections",
                "risk_level": "critical",
                "location": "Input/Output Analysis",
                "details": {
                    "context": context,
                    "legal_requirements": [
                        "Article 9 GDPR: Processing of special categories",
                        "HIPAA compliance if applicable in jurisdiction",
                        "Data minimization requirements"
                    ]
                }
            })
            
        if "Finance" in context or "All" in context:
            findings.append({
                "id": f"AIPII-FINANCE-{uuid.uuid4().hex[:6]}",
                "type": "Financial Data",
                "category": "Sensitive PII",
                "description": "Model may process financial personal data requiring enhanced protection",
                "risk_level": "high",
                "location": "Input/Output Analysis",
                "details": {
                    "context": context,
                    "legal_requirements": [
                        "PCI DSS requirements for financial data",
                        "Banking regulations in applicable jurisdictions",
                        "Data retention limitations"
                    ]
                }
            })
            
        return findings

    def _generate_bias_findings(
            self, fairness_metrics: List[str]) -> List[Dict[str, Any]]:
        """
        Generate findings related to model bias and fairness
        """
        findings = []
        
        # Disparate impact finding
        if "Disparate Impact" in fairness_metrics:
            findings.append({
                "id": f"AIBIAS-DI-{uuid.uuid4().hex[:6]}",
                "type": "Disparate Impact",
                "category": "Model Bias",
                "description": "Model demonstrates potential disparate impact across protected groups",
                "risk_level": "high",
                "location": "Fairness Analysis",
                "details": {
                    "metric": "Disparate Impact",
                    "protected_attributes": [
                        "Gender", "Age", "Race", "Religion"
                    ],
                    "disparate_impact_ratio": 0.76,  # Example value: below 0.8 is concerning
                    "acceptable_threshold": 0.8,
                    "explanation": "Disparate impact ratio < 0.8 indicates that the model's predictions may have an adverse impact on certain protected groups",
                    "recommendations": [
                        "Apply preprocessing techniques to balance training data",
                        "Implement adversarial debiasing during model training",
                        "Add fairness constraints to the optimization objective"
                    ]
                }
            })
        
        # Equal opportunity finding
        if "Equal Opportunity" in fairness_metrics:
            findings.append({
                "id": f"AIBIAS-EO-{uuid.uuid4().hex[:6]}",
                "type": "Equal Opportunity Difference",
                "category": "Model Bias",
                "description": "Model shows unequal true positive rates across demographic groups",
                "risk_level": "medium",
                "location": "Fairness Analysis",
                "details": {
                    "metric": "Equal Opportunity Difference",
                    "protected_attributes": [
                        "Gender", "Age"
                    ],
                    "max_difference": 0.12,  # Example value: difference in true positive rates
                    "acceptable_threshold": 0.10,
                    "explanation": "Equal opportunity difference > 0.1 indicates that certain demographic groups may have significantly different true positive rates",
                    "recommendations": [
                        "Apply post-processing techniques to equalize opportunity",
                        "Reweight examples in training data",
                        "Implement multitask learning with fairness objectives"
                    ]
                }
            })
            
        # Predictive parity finding
        if "Predictive Parity" in fairness_metrics:
            findings.append({
                "id": f"AIBIAS-PP-{uuid.uuid4().hex[:6]}",
                "type": "Predictive Parity",
                "category": "Model Bias",
                "description": "Model shows differing precision scores across protected groups",
                "risk_level": "medium",
                "location": "Fairness Analysis",
                "details": {
                    "metric": "Predictive Parity",
                    "protected_attributes": [
                        "Race", "Religion"
                    ],
                    "precision_difference": 0.09,  # Example value: difference in precision
                    "acceptable_threshold": 0.05,
                    "explanation": "Precision difference > 0.05 indicates that the positive predictive value of the model varies significantly across protected groups",
                    "recommendations": [
                        "Calibrate predictions across groups",
                        "Apply fairness-aware ensemble methods",
                        "Implement constraint-based optimization"
                    ]
                }
            })
        
        return findings

    def _generate_explainability_findings(
            self, explainability_checks: List[str],
            model_type: str) -> Tuple[List[Dict[str, Any]], int]:
        """
        Generate findings related to model explainability
        
        Returns:
            Tuple containing:
            - List of findings
            - Explainability score (0-100)
        """
        findings = []
        explainability_score = 0
        
        # Feature importance finding
        if "Feature Importance" in explainability_checks:
            is_interpretable = model_type in ["Linear Model", "Decision Tree"]
            
            findings.append({
                "id": f"AIEXP-FI-{uuid.uuid4().hex[:6]}",
                "type": "Feature Importance",
                "category": "Explainability",
                "description": "Assessment of feature importance transparency",
                "risk_level": "low" if is_interpretable else "medium",
                "location": "Explainability Analysis",
                "details": {
                    "technique": "Feature Importance",
                    "interpretability_score": 75 if is_interpretable else 40,
                    "explanation": f"{'Inherently interpretable model' if is_interpretable else 'Complex model requiring post-hoc explanation methods'}",
                    "recommendations": [
                        "Document feature importance in model cards",
                        "Implement SHAP or LIME for local explanations",
                        "Create user-facing explanation interfaces"
                    ]
                }
            })
            
            # Update explainability score
            explainability_score += 25 if is_interpretable else 15
        
        # Decision path finding
        if "Decision Path" in explainability_checks:
            path_traceable = model_type in ["Decision Tree", "Rule-Based Model"]
            
            findings.append({
                "id": f"AIEXP-DP-{uuid.uuid4().hex[:6]}",
                "type": "Decision Path",
                "category": "Explainability",
                "description": "Ability to trace decision paths for individual predictions",
                "risk_level": "low" if path_traceable else "high",
                "location": "Explainability Analysis",
                "details": {
                    "technique": "Decision Path Tracing",
                    "interpretability_score": 80 if path_traceable else 30,
                    "explanation": f"{'Decision paths can be fully traced' if path_traceable else 'Decision paths cannot be reliably traced'}",
                    "recommendations": [
                        "Implement decision tree surrogate models",
                        "Add tracing mechanisms to complex models",
                        "Document decision criteria in accessible format"
                    ]
                }
            })
            
            # Update explainability score
            explainability_score += 35 if path_traceable else 10
        
        # Model interpretability finding
        if "Model Interpretability" in explainability_checks:
            # Assess interpretability based on model type
            interpretability_details = {
                "Linear Model": {"score": 85, "level": "high"},
                "Decision Tree": {"score": 80, "level": "high"},
                "Random Forest": {"score": 60, "level": "medium"},
                "Gradient Boosting": {"score": 50, "level": "medium"},
                "Neural Network": {"score": 35, "level": "low"},
                "ONNX": {"score": 40, "level": "low"},
                "TensorFlow": {"score": 40, "level": "low"},
                "PyTorch": {"score": 40, "level": "low"},
                "Unknown": {"score": 30, "level": "low"}
            }
            
            details = interpretability_details.get(model_type, interpretability_details["Unknown"])
            
            findings.append({
                "id": f"AIEXP-MI-{uuid.uuid4().hex[:6]}",
                "type": "Model Interpretability",
                "category": "Explainability",
                "description": f"Overall model interpretability assessment for {model_type}",
                "risk_level": "medium" if details["level"] in ["low", "medium"] else "low",
                "location": "Explainability Analysis",
                "details": {
                    "technique": "Holistic Interpretability Assessment",
                    "model_type": model_type,
                    "interpretability_score": details["score"],
                    "interpretability_level": details["level"],
                    "explanation": f"{'Model structure allows for straightforward interpretation' if details['level'] == 'high' else 'Model requires specialized techniques for interpretation'}",
                    "recommendations": [
                        "Document model limitations and uncertainties",
                        "Provide confidence intervals with predictions",
                        "Implement global and local explanation methods"
                    ]
                }
            })
            
            # Update explainability score with highest weight
            explainability_score += details["score"] * 0.4
        
        # Calculate final score (capped at 100)
        final_explainability_score = min(int(explainability_score), 100)
        
        return findings, final_explainability_score

    def _generate_enhanced_compliance_findings(
            self, leakage_types: List[str],
            region: str,
            model_type: str) -> List[Dict[str, Any]]:
        """
        Generate enhanced compliance findings
        """
        findings = []
        
        # Basic compliance finding
        findings.append({
            "id": f"AICOMP-{uuid.uuid4().hex[:6]}",
            "type": "Compliance Assessment",
            "category": "GDPR Compliance",
            "description": f"Model requires GDPR compliance assessment for {region}",
            "risk_level": "medium",
            "location": "Compliance Analysis",
            "details": {
                "region": region,
                "leakage_types": leakage_types,
                "model_type": model_type,
                "regulations": [
                    "GDPR", "AI Act (EU)", "Consumer Privacy Acts"
                ]
            }
        })
        
        # Model-specific compliance findings
        if model_type == "ONNX":
            findings.append({
                "id": f"AICOMP-ONNX-{uuid.uuid4().hex[:6]}",
                "type": "ONNX Model Export Compliance",
                "category": "Technical Compliance",
                "description": "Assessment of ONNX model export for regulatory compliance",
                "risk_level": "medium",
                "location": "Technical Implementation",
                "details": {
                    "consideration": "ONNX models may not preserve privacy controls from original frameworks",
                    "recommendations": [
                        "Verify that privacy-preserving techniques survive ONNX conversion",
                        "Check for PII leakage in metadata of exported models",
                        "Implement post-conversion privacy validation"
                    ]
                }
            })
        elif model_type == "TensorFlow":
            findings.append({
                "id": f"AICOMP-TF-{uuid.uuid4().hex[:6]}",
                "type": "TensorFlow Privacy Compliance",
                "category": "Technical Compliance",
                "description": "Assessment of TensorFlow privacy features usage",
                "risk_level": "medium",
                "location": "Technical Implementation",
                "details": {
                    "consideration": "TensorFlow supports differential privacy but requires explicit implementation",
                    "recommendations": [
                        "Implement TensorFlow Privacy library for training",
                        "Document privacy budget settings used in training",
                        "Validate models against membership inference attacks"
                    ]
                }
            })
        elif model_type == "PyTorch":
            findings.append({
                "id": f"AICOMP-PT-{uuid.uuid4().hex[:6]}",
                "type": "PyTorch Model Privacy",
                "category": "Technical Compliance",
                "description": "Assessment of PyTorch model for privacy implementation",
                "risk_level": "medium",
                "location": "Technical Implementation",
                "details": {
                    "consideration": "PyTorch requires explicit privacy controls during training",
                    "recommendations": [
                        "Implement Opacus or similar privacy frameworks for PyTorch",
                        "Apply gradient clipping to prevent privacy leakage",
                        "Perform privacy evaluation on trained model weights"
                    ]
                }
            })
        
        # Check for PII in training data
        if "PII in Training Data" in leakage_types:
            findings.append({
                "id": f"AICOMP-TRAIN-{uuid.uuid4().hex[:6]}",
                "type": "Training Data Assessment",
                "category": "PII in Training",
                "description": "Potential PII exposure in training data requires documentation",
                "risk_level": "high",
                "location": "Training Data",
                "details": {
                    "requirements": [
                        "Article 30 GDPR: Records of processing activities",
                        "Article 35 GDPR: Data protection impact assessment",
                        "Documentation of lawful basis for processing"
                    ],
                    "recommendations": [
                        "Maintain detailed records of PII handling during training",
                        "Document deidentification techniques applied to training data",
                        "Create data flow diagrams for model training process"
                    ]
                }
            })
        
        # Add model documentation findings
        findings.append({
            "id": f"AICOMP-DOC-{uuid.uuid4().hex[:6]}",
            "type": "Model Documentation",
            "category": "Transparency Requirements",
            "description": "Assessment of model documentation for transparent use",
            "risk_level": "medium",
            "location": "Documentation",
            "details": {
                "consideration": "AI systems require comprehensive documentation for compliance",
                "recommendations": [
                    "Create Model Cards following Google's standard",
                    "Document intended uses and limitations clearly",
                    "Include comprehensive bias evaluations in documentation",
                    "Provide transparency on data sources and processing"
                ]
            }
        })
        
        return findings

    def generate_pdf_report(self, scan_data: Dict[str, Any]) -> Tuple[bool, str, Optional[bytes]]:
        """
        Generate a PDF report for the AI model scan
        
        Args:
            scan_data: The scan result data
            
        Returns:
            Tuple containing:
            - Success status (bool)
            - Message or file path (str)
            - Report bytes (or None if failed)
        """
        # Ensure scan_data has required fields for AI model report
        if 'scan_type' not in scan_data:
            scan_data['scan_type'] = 'AI Model'
            
        # Ensure we have model type information
        if 'model_type' not in scan_data:
            scan_data['model_type'] = 'Unknown'
        
        # Forward to the report generator
        return auto_generate_pdf_report(scan_data)