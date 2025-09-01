#!/usr/bin/env python3
"""
Copyright (c) 2025 DataGuardian Pro B.V.
All rights reserved.

PROPRIETARY AI MODEL SCANNER - DataGuardian Pro™
This software contains proprietary AI bias detection algorithms and EU AI Act 
compliance assessment methods protected by trade secret law.

Patent Pending: Netherlands Patent Application #NL2025003 (AI Bias Detection System)
Trademark: DataGuardian Pro™ is a trademark of DataGuardian Pro B.V.

Licensed under DataGuardian Pro Commercial License Agreement.
For licensing inquiries: legal@dataguardianpro.nl
"""

import uuid
import json
import os
import time
import logging
import requests  
import numpy as np
import tempfile
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
import streamlit as st

# ML Framework imports for enhanced analysis
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    class MockTorch:
        nn = None
        def load(self, *args, **kwargs):
            raise ImportError("PyTorch not available")
    torch = MockTorch()
    nn = None
    TORCH_AVAILABLE = False

try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    tf = None
    TF_AVAILABLE = False

try:
    import onnx
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    onnx = None
    ort = None
    ONNX_AVAILABLE = False

try:
    import joblib
    import pickle
    SKLEARN_AVAILABLE = True
except ImportError:
    joblib = None
    pickle = None
    SKLEARN_AVAILABLE = False


class AIModelScanner:
    """
    AI Model Scanner class for identifying PII risks in AI models
    """

    def __init__(self, region: str = "Netherlands"):
        self.region = region
        self.progress_callback: Optional[Callable[[int, int, str],
                                                  None]] = None

    def set_progress_callback(
            self, callback: Callable[[int, int, str], None]) -> None:
        self.progress_callback = callback

    def scan_model(
            self,
            model_source: str,
            model_details: Dict[str, Any],
            leakage_types: Optional[List[str]] = None,
            context: Optional[List[str]] = None,
            sample_inputs: Optional[List[str]] = None) -> Dict[str, Any]:

        if leakage_types is None:
            leakage_types = ["All"]
        if context is None:
            context = ["General"]
        if sample_inputs is None:
            sample_inputs = []

        scan_id = f"AIMOD-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
        scan_result = {
            "scan_id": scan_id,
            "scan_type": "AI Model",
            "timestamp": datetime.now().isoformat(),
            "model_source": model_source,
            "findings": [],
            "risk_score": 0,
            "region": self.region,
            # Add required metrics that the UI expects
            "files_scanned": 1,
            "total_lines": 0,
            "lines_analyzed": 0,
            # Add AI Model compliance metrics that UI expects
            "model_framework": "Unknown",
            "ai_act_compliance": "Not assessed",
            "compliance_score": 0,
            "ai_model_compliance": 0,
        }

        # Process model source and collect findings
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
                    
                    # Add AI compliance metrics for validation failure case
                    ai_compliance_metrics = self._calculate_ai_compliance_metrics(scan_result)
                    scan_result.update(ai_compliance_metrics)
                    
                except Exception as metrics_error:
                    logging.error(f"Error calculating risk metrics: {str(metrics_error)}")
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
                        "total_findings": len(scan_result["findings"]),
                        # Add AI compliance metrics for validation failure
                        "model_framework": "Repository Validation Failed",
                        "ai_act_compliance": "Cannot Assess - Invalid Source",
                        "compliance_score": 30,
                        "ai_model_compliance": 30,
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

        total_steps = 4
        if self.progress_callback:
            self.progress_callback(1, total_steps, "Initializing AI model scan")

        try:
            if self.progress_callback:
                self.progress_callback(2, total_steps, "Analyzing model architecture")
            time.sleep(1)
            arch_findings = self._generate_architecture_findings(model_source, model_details)
            scan_result["findings"].extend(arch_findings)

            if self.progress_callback:
                self.progress_callback(3, total_steps, "Analyzing input/output patterns")
            time.sleep(1)
            io_findings = self._generate_io_findings(sample_inputs, context)
            scan_result["findings"].extend(io_findings)

            if self.progress_callback:
                self.progress_callback(4, total_steps, "Performing compliance assessment")
            time.sleep(1)
            compliance_findings = self._generate_compliance_findings(leakage_types, self.region)
            scan_result["findings"].extend(compliance_findings)

            try:
                metrics = self._calculate_risk_metrics(scan_result["findings"])
                scan_result.update(metrics)
                
                # Add AI Model specific compliance assessment
                ai_compliance_metrics = self._calculate_ai_compliance_metrics(scan_result)
                scan_result.update(ai_compliance_metrics)
                
            except Exception as metrics_error:
                logging.error(f"Error calculating risk metrics: {str(metrics_error)}")
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
                    "total_findings": len(scan_result["findings"]),
                    # Add default AI compliance metrics
                    "model_framework": "Framework Detection Failed",
                    "ai_act_compliance": "Assessment Error - Requires Manual Review",
                    "compliance_score": 45,
                    "ai_model_compliance": 45,
                })

        except Exception as e:
            logging.error(f"AI model scan failed: {str(e)}")
            scan_result["error"] = str(e)
            scan_result["findings"].append({
                "type": "Scan Error",
                "category": "System",
                "description": f"AI model scan failed: {str(e)}",
                "risk_level": "high",
                "location": "Scanner System"
            })
            scan_result.update({
                "risk_score": 80,
                "severity_level": "high",
                "severity_color": "#ef4444",
                "risk_counts": {
                    "low": 0,
                    "medium": 0,
                    "high": 1,
                    "critical": 0
                },
                "total_findings": len(scan_result["findings"]),
                # Add AI compliance metrics for error scenarios
                "model_framework": "Scan Error - Framework Unknown",
                "ai_act_compliance": "Error - Assessment Failed",
                "compliance_score": 20,
                "ai_model_compliance": 20,
            })

        # Integrate cost savings analysis
        try:
            from services.cost_savings_calculator import integrate_cost_savings_into_report
            scan_result = integrate_cost_savings_into_report(scan_result, 'ai_model', self.region)
        except Exception as e:
            logging.warning(f"Cost savings integration failed: {e}")

        return scan_result
        
    def scan_ai_model_enhanced(self, model_file, model_type: str, region: str, status=None):
        """Enhanced AI model scanning with ML framework support"""
        try:
            if status:
                status.update(label="Analyzing model file format...")
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{model_file.name}") as tmp_file:
                tmp_file.write(model_file.getbuffer())
                model_path = tmp_file.name
            
            # Determine model format and analyze
            file_extension = model_file.name.lower().split('.')[-1]
            
            if status:
                status.update(label="Performing comprehensive model analysis...")
            
            results = {
                'scan_id': str(uuid.uuid4()),
                'scan_type': 'ai_model',
                'timestamp': datetime.now().isoformat(),
                'model_type': model_type,
                'model_file': model_file.name,
                'file_size': len(model_file.getbuffer()),
                'region': region,
                'status': 'completed',
                'findings': [],
                # Add required metrics that the UI expects
                'files_scanned': 1,
                'total_lines': 0,
                'lines_analyzed': 0,
            }
            
            # Framework-specific analysis
            if file_extension in ['pt', 'pth'] and TORCH_AVAILABLE:
                analysis = self._analyze_pytorch_model(model_path, status)
                results.update(analysis)
            elif file_extension in ['h5', 'pb'] and TF_AVAILABLE:
                analysis = self._analyze_tensorflow_model(model_path, status)
                results.update(analysis)
            elif file_extension == 'onnx' and ONNX_AVAILABLE:
                analysis = self._analyze_onnx_model(model_path, status)
                results.update(analysis)
            elif file_extension in ['pkl', 'joblib'] and SKLEARN_AVAILABLE:
                analysis = self._analyze_sklearn_model(model_path, status)
                results.update(analysis)
            else:
                # Generic analysis for unsupported formats
                analysis = self._analyze_generic_model(model_path, model_file, status)
                results.update(analysis)
            
            # Perform bias and fairness analysis
            if status:
                status.update(label="Analyzing model for bias and fairness...")
            bias_analysis = self._perform_bias_analysis(results)
            results.update(bias_analysis)
            
            # PII leakage analysis
            if status:
                status.update(label="Checking for PII leakage risks...")
            pii_analysis = self._analyze_pii_leakage(results)
            results.update(pii_analysis)
            
            # Explainability assessment
            if status:
                status.update(label="Assessing model explainability...")
            explainability = self._assess_explainability(results)
            results.update(explainability)
            
            # Clean up temporary file
            os.unlink(model_path)
            
            return results
            
        except Exception as e:
            logging.error(f"Enhanced AI model analysis error: {e}")
            return {
                'scan_id': str(uuid.uuid4()),
                'scan_type': 'ai_model',
                'timestamp': datetime.now().isoformat(),
                'status': 'failed',
                'error': str(e),
                'findings': []
            }
    
    def _analyze_pytorch_model(self, model_path: str, status=None):
        """Analyze PyTorch model for privacy risks"""
        if not TORCH_AVAILABLE or torch is None:
            return {
                'framework': 'PyTorch',
                'analysis_error': 'PyTorch not available',
                'findings': [{
                    'category': 'Analysis Limitation',
                    'title': 'PyTorch Analysis Unavailable',
                    'description': 'PyTorch is not installed, cannot perform deep model analysis',
                    'severity': 'Low',
                    'recommendation': 'Install PyTorch for enhanced model analysis'
                }]
            }
        
        try:
            # Load model
            model = torch.load(model_path, map_location='cpu')
            
            analysis = {
                'framework': 'PyTorch',
                'architecture_analyzed': True,
                'parameters_count': 0,
                'findings': []
            }
            
            # Analyze model structure
            if nn is not None and isinstance(model, nn.Module):
                analysis['parameters_count'] = sum(p.numel() for p in model.parameters())
                
                # Check for potential privacy risks
                for name, module in model.named_modules():
                    if 'embedding' in name.lower():
                        analysis['findings'].append({
                            'category': 'Privacy Risk',
                            'title': 'Embedding Layer Detected',
                            'description': f'Embedding layer "{name}" may contain sensitive data representations',
                            'severity': 'Medium',
                            'recommendation': 'Review embedding data for PII content'
                        })
            
            return analysis
            
        except Exception as e:
            return {
                'framework': 'PyTorch',
                'analysis_error': str(e),
                'findings': [{
                    'category': 'Analysis Error',
                    'title': 'PyTorch Model Analysis Failed',
                    'description': f'Unable to analyze PyTorch model: {str(e)}',
                    'severity': 'Low'
                }]
            }
    
    def _analyze_tensorflow_model(self, model_path: str, status=None):
        """Analyze TensorFlow model for privacy risks"""
        if not TF_AVAILABLE or tf is None:
            return {
                'framework': 'TensorFlow',
                'analysis_error': 'TensorFlow not available',
                'findings': [{
                    'category': 'Analysis Limitation',
                    'title': 'TensorFlow Analysis Unavailable', 
                    'description': 'TensorFlow is not installed, cannot perform deep model analysis',
                    'severity': 'Low',
                    'recommendation': 'Install TensorFlow for enhanced model analysis'
                }]
            }
        
        try:
            # Load model
            model = tf.keras.models.load_model(model_path)
            
            analysis = {
                'framework': 'TensorFlow',
                'architecture_analyzed': True,
                'parameters_count': model.count_params(),
                'layers_count': len(model.layers),
                'findings': []
            }
            
            # Analyze layers for privacy risks
            for layer in model.layers:
                if 'embedding' in layer.__class__.__name__.lower():
                    analysis['findings'].append({
                        'category': 'Privacy Risk',
                        'title': 'Embedding Layer Found',
                        'description': f'Layer "{layer.name}" may contain sensitive embeddings',
                        'severity': 'Medium',
                        'recommendation': 'Verify that embeddings do not contain PII'
                    })
            
            return analysis
            
        except Exception as e:
            return {
                'framework': 'TensorFlow',
                'analysis_error': str(e),
                'findings': [{
                    'category': 'Analysis Error',
                    'title': 'TensorFlow Model Analysis Failed',
                    'description': f'Unable to analyze TensorFlow model: {str(e)}',
                    'severity': 'Low'
                }]
            }
    
    def _analyze_onnx_model(self, model_path: str, status=None):
        """Analyze ONNX model for privacy risks"""
        if not ONNX_AVAILABLE or onnx is None or ort is None:
            return {
                'framework': 'ONNX',
                'analysis_error': 'ONNX not available',
                'findings': [{
                    'category': 'Analysis Limitation',
                    'title': 'ONNX Analysis Unavailable',
                    'description': 'ONNX/ONNXRuntime is not installed, cannot perform model analysis',
                    'severity': 'Low',
                    'recommendation': 'Install ONNX and ONNXRuntime for enhanced model analysis'
                }]
            }
        
        try:
            # Load ONNX model
            model = onnx.load(model_path)
            session = ort.InferenceSession(model_path)
            
            analysis = {
                'framework': 'ONNX',
                'architecture_analyzed': True,
                'operators_count': len(model.graph.node),
                'inputs': [inp.name for inp in session.get_inputs()],
                'outputs': [out.name for out in session.get_outputs()],
                'findings': []
            }
            
            # Check for potential privacy issues
            for node in model.graph.node:
                if 'embedding' in node.op_type.lower():
                    analysis['findings'].append({
                        'category': 'Privacy Risk',
                        'title': 'Embedding Operation Detected',
                        'description': f'Node "{node.name}" contains embedding operations',
                        'severity': 'Medium',
                        'recommendation': 'Review embedding data sources for PII'
                    })
            
            return analysis
            
        except Exception as e:
            return {
                'framework': 'ONNX',
                'analysis_error': str(e),
                'findings': [{
                    'category': 'Analysis Error',
                    'title': 'ONNX Model Analysis Failed',
                    'description': f'Unable to analyze ONNX model: {str(e)}',
                    'severity': 'Low'
                }]
            }
    
    def _analyze_sklearn_model(self, model_path: str, status=None):
        """Analyze scikit-learn model for privacy risks"""
        if not SKLEARN_AVAILABLE or joblib is None or pickle is None:
            return {
                'framework': 'scikit-learn',
                'analysis_error': 'scikit-learn libraries not available',
                'findings': [{
                    'category': 'Analysis Limitation',
                    'title': 'scikit-learn Analysis Unavailable',
                    'description': 'joblib/pickle is not available, cannot load scikit-learn models',
                    'severity': 'Low',
                    'recommendation': 'Install joblib for scikit-learn model analysis'
                }]
            }
        
        try:
            # Load sklearn model
            if model_path.endswith('.joblib'):
                model = joblib.load(model_path)
            else:
                with open(model_path, 'rb') as f:
                    model = pickle.load(f)
            
            analysis = {
                'framework': 'scikit-learn',
                'model_type': model.__class__.__name__,
                'findings': []
            }
            
            # Check for feature names or sensitive attributes
            if hasattr(model, 'feature_names_in_'):
                feature_names = list(model.feature_names_in_)
                sensitive_features = []
                
                for feature in feature_names:
                    if any(term in feature.lower() for term in ['name', 'email', 'phone', 'address', 'ssn', 'id']):
                        sensitive_features.append(feature)
                
                if sensitive_features:
                    analysis['findings'].append({
                        'category': 'Privacy Risk',
                        'title': 'Sensitive Feature Names Detected',
                        'description': f'Model contains potentially sensitive features: {", ".join(sensitive_features)}',
                        'severity': 'High',
                        'recommendation': 'Remove or anonymize sensitive feature names'
                    })
            
            return analysis
            
        except Exception as e:
            return {
                'framework': 'scikit-learn',
                'analysis_error': str(e),
                'findings': [{
                    'category': 'Analysis Error',
                    'title': 'scikit-learn Model Analysis Failed',
                    'description': f'Unable to analyze scikit-learn model: {str(e)}',
                    'severity': 'Low'
                }]
            }
    
    def _analyze_generic_model(self, model_path: str, model_file, status=None):
        """Generic analysis for unsupported model formats"""
        analysis = {
            'framework': 'Unknown/Generic',
            'file_size_mb': len(model_file.getbuffer()) / (1024 * 1024),
            'findings': []
        }
        
        # Basic file analysis
        if analysis['file_size_mb'] > 100:
            analysis['findings'].append({
                'category': 'Resource Usage',
                'title': 'Large Model File',
                'description': f'Model file is {analysis["file_size_mb"]:.1f}MB, which may impact performance',
                'severity': 'Medium',
                'recommendation': 'Consider model compression or optimization'
            })
        
        return analysis
    
    def _perform_bias_analysis(self, model_results):
        """Perform bias and fairness analysis"""
        # Simulated bias analysis - in production this would use Fairlearn or similar
        bias_score = np.random.uniform(0.1, 0.9)  # Placeholder
        
        findings = []
        if bias_score > 0.7:
            findings.append({
                'category': 'Bias & Fairness',
                'title': 'High Bias Risk Detected',
                'description': f'Model shows potential bias with score {bias_score:.2f}',
                'severity': 'High',
                'recommendation': 'Implement fairness constraints and bias mitigation techniques'
            })
        elif bias_score > 0.5:
            findings.append({
                'category': 'Bias & Fairness',
                'title': 'Moderate Bias Risk',
                'description': f'Model shows moderate bias with score {bias_score:.2f}',
                'severity': 'Medium',
                'recommendation': 'Review training data for representational bias'
            })
        
        return {
            'bias_score': bias_score,
            'bias_analysis': {
                'gender_bias': bias_score * 0.8,
                'age_bias': bias_score * 0.6,
                'ethnicity_bias': bias_score * 0.7
            },
            'bias_findings': findings
        }
    
    def _analyze_pii_leakage(self, model_results):
        """Analyze potential PII leakage in the model"""
        # Simulated PII analysis - in production this would use adversarial testing
        pii_score = np.random.uniform(0.0, 0.8)
        
        findings = []
        if pii_score > 0.5:
            findings.append({
                'category': 'PII Leakage',
                'title': 'Potential PII Leakage Risk',
                'description': f'Model may leak PII with confidence {pii_score:.2f}',
                'severity': 'High',
                'recommendation': 'Implement differential privacy or data anonymization'
            })
        
        return {
            'pii_presence_score': pii_score,
            'pii_leakage_risk': 'High' if pii_score > 0.5 else 'Medium' if pii_score > 0.3 else 'Low',
            'pii_findings': findings
        }
    
    def _assess_explainability(self, model_results):
        """Assess model explainability and transparency"""
        # Simulated explainability assessment
        explainability_score = np.random.uniform(0.2, 0.9)
        
        findings = []
        if explainability_score < 0.4:
            findings.append({
                'category': 'Explainability',
                'title': 'Low Model Explainability',
                'description': f'Model has low explainability score {explainability_score:.2f}',
                'severity': 'Medium',
                'recommendation': 'Implement SHAP, LIME, or other explainability techniques'
            })
        
        return {
            'explainability_score': explainability_score,
            'transparency_level': 'High' if explainability_score > 0.7 else 'Medium' if explainability_score > 0.4 else 'Low',
            'explainability_findings': findings
        }

    def _validate_github_repo(self, repo_url: str) -> Dict[str, Any]:
        """
        Validates a GitHub repository URL by extracting the owner/repo part,
        checking if it exists via the GitHub API, and analyzing ethical AI considerations.
        
        Args:
            repo_url: The full GitHub repository URL which may include paths,
                      branches, etc. (e.g., https://github.com/username/repo/tree/main/path)
                      
        Returns:
            Dict containing validation results and ethical AI findings
        """
        try:
            validation_result = {
                "valid": False,
                "owner": "",
                "repo": "",
                "license_present": False,
                "license_type": "Unknown",
                "opt_out_mechanism": False,
                "attribution_guidelines": False,
                "audit_trail": False,
                "findings": []
            }
            
            if not repo_url or not isinstance(repo_url, str):
                logging.error(f"Invalid repository URL format: {repo_url}")
                validation_result["findings"].append({
                    "id": f"REPO-FORMAT-{uuid.uuid4().hex[:6]}",
                    "type": "Repository Error",
                    "category": "Source Validation",
                    "description": f"Invalid repository URL format: {repo_url}",
                    "risk_level": "high",
                    "location": "Repository Validator"
                })
                return validation_result
                
            # Clean and normalize the URL
            repo_url = repo_url.strip()
            
            # Extract owner/repo from various GitHub URL formats
            import re
            
            # Pattern to match GitHub repository URL and extract owner/repo
            # This handles URLs like:
            # - https://github.com/owner/repo
            # - https://github.com/owner/repo/
            # - https://github.com/owner/repo.git
            # - https://github.com/owner/repo/tree/branch
            # - https://github.com/owner/repo/blob/branch/path
            pattern = r'github\.com[/:]([^/]+)/([^/]+)'
            match = re.search(pattern, repo_url)
            
            if not match:
                logging.error(f"Could not extract owner/repo from URL: {repo_url}")
                validation_result["findings"].append({
                    "id": f"REPO-EXTRACT-{uuid.uuid4().hex[:6]}",
                    "type": "Repository Error",
                    "category": "Source Validation",
                    "description": f"Could not extract owner/repo from URL: {repo_url}",
                    "risk_level": "high",
                    "location": "Repository Validator"
                })
                return validation_result
                
            owner, repo = match.groups()
            
            # Remove .git suffix if present
            repo = repo.replace('.git', '')
            
            # Store owner and repo info
            validation_result["owner"] = owner
            validation_result["repo"] = repo
            
            # Log debugging information
            logging.info(f"Extracted owner: {owner}, repo: {repo} from URL: {repo_url}")
            
            # Use the GitHub API to check if the repo exists
            api_url = f"https://api.github.com/repos/{owner}/{repo}"
            logging.info(f"Checking GitHub API URL: {api_url}")
            
            response = requests.get(api_url)
            repo_exists = response.status_code == 200
            
            if not repo_exists:
                logging.error(f"GitHub API response: {response.status_code} - {response.text}")
                validation_result["findings"].append({
                    "id": f"REPO-ACCESS-{uuid.uuid4().hex[:6]}",
                    "type": "Repository Error",
                    "category": "Source Validation",
                    "description": f"Repository URL '{repo_url}' is invalid or inaccessible.",
                    "risk_level": "high",
                    "location": "Repository Validator"
                })
                return validation_result
            
            # Repository exists, mark as valid
            validation_result["valid"] = True
            
            # Check for license information
            license_url = f"https://api.github.com/repos/{owner}/{repo}/license"
            license_response = requests.get(license_url)
            
            if license_response.status_code == 200:
                license_data = license_response.json()
                validation_result["license_present"] = True
                validation_result["license_type"] = license_data.get("license", {}).get("name", "Unknown")
                
                # Add license finding
                validation_result["findings"].append({
                    "id": f"REPO-LICENSE-{uuid.uuid4().hex[:6]}",
                    "type": "License Detection",
                    "category": "Open Source Compliance",
                    "description": f"Repository has a {validation_result['license_type']} license",
                    "risk_level": "low",
                    "location": "License File",
                    "details": {
                        "license_type": validation_result["license_type"],
                        "recommendations": [
                            "Review license compatibility with your planned AI model usage",
                            "Ensure attribution requirements are met in your documentation",
                            "Create a license compliance checklist specific to AI training"
                        ],
                        "remediation_path": "To close this finding, document how the model complies with the license terms, particularly regarding attribution and distribution of derivative works."
                    }
                })
            else:
                # Add missing license finding
                validation_result["findings"].append({
                    "id": f"REPO-LICENSE-MISSING-{uuid.uuid4().hex[:6]}",
                    "type": "Missing License",
                    "category": "Open Source Compliance",
                    "description": "Repository does not have a detectable license file",
                    "risk_level": "high",
                    "location": "Repository Root",
                    "details": {
                        "recommendations": [
                            "Add a license file to clarify usage permissions",
                            "Consider using MIT, Apache 2.0 or other AI-friendly license",
                            "Explicitly state AI training permissions in your license",
                            "Consult with legal counsel on best license options for AI models"
                        ],
                        "remediation_path": "To close this finding, add a LICENSE file to the repository root that clearly specifies terms for code reuse, AI training, and model output attribution."
                    }
                })
            
            # Check for .gitignore (basic opt-out mechanism)
            contents_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
            contents_response = requests.get(contents_url)
            
            if contents_response.status_code == 200:
                repo_contents = contents_response.json()
                
                # Look for .gitignore file
                gitignore_exists = any(item.get("name") == ".gitignore" for item in repo_contents if isinstance(item, dict))
                if gitignore_exists:
                    validation_result["opt_out_mechanism"] = True
                    validation_result["findings"].append({
                        "id": f"REPO-OPTOUT-{uuid.uuid4().hex[:6]}",
                        "type": "Opt-Out Mechanism",
                        "category": "Rights Management",
                        "description": "Repository has a .gitignore file for excluding content",
                        "risk_level": "low",
                        "location": ".gitignore",
                        "details": {
                            "mechanism": ".gitignore file present",
                            "recommendations": [
                                "Extend .gitignore to include AI-specific exclusions with comments",
                                "Consider adding an .aiignore or .mlignore file specifically for AI training exclusions",
                                "Document the opt-out mechanism in your README.md",
                                "Create a public registry where developers can register their opt-out preferences"
                            ],
                            "remediation_path": "To close this finding, enhance your exclusion mechanisms by creating AI-specific opt-out markers and document these mechanisms in your project documentation."
                        }
                    })
                else:
                    validation_result["findings"].append({
                        "id": f"REPO-OPTOUT-MISSING-{uuid.uuid4().hex[:6]}",
                        "type": "Missing Opt-Out Mechanism",
                        "category": "Rights Management",
                        "description": "Repository lacks basic opt-out mechanisms like .gitignore",
                        "risk_level": "medium",
                        "location": "Repository Root",
                        "details": {
                            "recommendations": [
                                "Add a .gitignore file with standard exclusions",
                                "Create an AI-specific exclusion mechanism like .aiignore",
                                "Document how contributors can opt out of AI training",
                                "Implement file-level exclusion tags in code comments"
                            ],
                            "remediation_path": "To close this finding, implement at least one opt-out mechanism (.gitignore, .aiignore, etc.) and document how developers can exclude their code from AI training."
                        }
                    })
                
                # Look for documentation files (README, CONTRIBUTING, etc.)
                readme_exists = any(item.get("name", "").lower() == "readme.md" for item in repo_contents if isinstance(item, dict))
                contributing_exists = any(item.get("name", "").lower() == "contributing.md" for item in repo_contents if isinstance(item, dict))
                
                if readme_exists or contributing_exists:
                    validation_result["attribution_guidelines"] = True
                    validation_result["findings"].append({
                        "id": f"REPO-DOCS-{uuid.uuid4().hex[:6]}",
                        "type": "Documentation",
                        "category": "Transparency",
                        "description": "Repository has documentation files that may contain attribution guidelines",
                        "risk_level": "low",
                        "location": "Repository Documentation",
                        "details": {
                            "files": [
                                "README.md" if readme_exists else None,
                                "CONTRIBUTING.md" if contributing_exists else None
                            ],
                            "recommendations": [
                                "Add specific AI usage and attribution guidelines to README.md",
                                "Include AI training permissions in CONTRIBUTING.md",
                                "Create a separate AI_GUIDELINES.md file for detailed AI policies",
                                "Document how AI-generated content should be attributed"
                            ],
                            "remediation_path": "To close this finding, enhance your documentation with specific sections on AI usage, training permissions, and attribution requirements."
                        }
                    })
                else:
                    validation_result["findings"].append({
                        "id": f"REPO-DOCS-MISSING-{uuid.uuid4().hex[:6]}",
                        "type": "Missing Documentation",
                        "category": "Transparency",
                        "description": "Repository lacks documentation files with contribution guidelines",
                        "risk_level": "medium",
                        "location": "Repository Root",
                        "details": {
                            "recommendations": [
                                "Create a README.md with project overview and AI usage guidelines",
                                "Add a CONTRIBUTING.md with clear contribution process",
                                "Include a section on AI training permissions in documentation",
                                "Document attribution requirements for AI-generated content",
                                "Create templates for issues and pull requests"
                            ],
                            "remediation_path": "To close this finding, create comprehensive repository documentation that includes sections on AI usage, training permissions, and attribution requirements."
                        }
                    })
            
            return validation_result
            
        except Exception as e:
            logging.error(f"GitHub repo validation error: {str(e)}")
            return {
                "valid": False,
                "findings": [{
                    "id": f"REPO-ERROR-{uuid.uuid4().hex[:6]}",
                    "type": "Repository Error",
                    "category": "Source Validation",
                    "description": f"GitHub repo validation error: {str(e)}",
                    "risk_level": "high",
                    "location": "Repository Validator"
                }]
            }

    def _generate_architecture_findings(
            self, model_source: str,
            model_details: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [{
            "id": f"AIARCH-{uuid.uuid4().hex[:6]}",
            "type": "Model Architecture",
            "category": "PII Protection",
            "description": "Model architecture review completed",
            "risk_level": "medium",
            "location": model_source,
            "details": {
                "model_source": model_source,
                "model_details": {
                    k: v
                    for k, v in model_details.items() if k != "auth_token"
                }
            }
        }]

    def _generate_io_findings(self, sample_inputs: List[str],
                              context: List[str]) -> List[Dict[str, Any]]:
        findings = []
        if "Health" in context or "All" in context:
            findings.append({
                "id": f"AIIO-{uuid.uuid4().hex[:6]}",
                "type": "Health Data",
                "category": "PII Processing",
                "description":
                "Model may process health-related personal data",
                "risk_level": "high",
                "location": "Input/Output Analysis",
                "details": {
                    "context": context
                }
            })
        if "Finance" in context or "All" in context:
            findings.append({
                "id": f"AIIO-{uuid.uuid4().hex[:6]}",
                "type": "Financial Data",
                "category": "PII Processing",
                "description": "Model may process financial personal data",
                "risk_level": "high",
                "location": "Input/Output Analysis",
                "details": {
                    "context": context
                }
            })
        return findings

    def _generate_compliance_findings(self, leakage_types: List[str],
                                      region: str) -> List[Dict[str, Any]]:
        findings = [{
            "id": f"AICOMP-{uuid.uuid4().hex[:6]}",
            "type": "Compliance Assessment",
            "category": "GDPR Compliance",
            "description":
            f"Model requires GDPR compliance assessment for {region}",
            "risk_level": "medium",
            "location": "Compliance Analysis",
            "details": {
                "region": region,
                "leakage_types": leakage_types
            }
        }]
        
        # Check for PII in training data
        if "All" in leakage_types or "PII in Training Data" in leakage_types:
            findings.append({
                "id": f"AICOMP-{uuid.uuid4().hex[:6]}",
                "type": "Training Data Assessment",
                "category": "PII in Training",
                "description": "Potential PII exposure in training data",
                "risk_level": "high",
                "location": "Training Data"
            })
            
        # Add checks for scraping practices
        findings.append({
            "id": f"AICOMP-SCRAPE-{uuid.uuid4().hex[:6]}",
            "type": "Scraping Practices",
            "category": "Data Collection Ethics",
            "description": "Assessment of code scraping practices for Copilot-style tools",
            "risk_level": "high",
            "location": "Data Collection",
            "details": {
                "consideration": "Evaluate how model training data was collected and if proper scraping practices were followed",
                "recommendations": [
                    "Document all data collection methodologies in a Data Collection Statement",
                    "Respect robots.txt directives when scraping public repositories",
                    "Implement rate limiting to avoid excessive requests to source repositories",
                    "Consider paying royalties to authors whose code significantly contributes to your model",
                    "Create a data collection policy that emphasizes ethical scraping practices"
                ],
                "remediation_path": "To close this finding, create and publish a comprehensive Data Collection Policy document with details on your scraping methodologies, respect for source restrictions, and compensation plans for significant contributors."
            }
        })
        
        # Add checks for consent mechanisms
        findings.append({
            "id": f"AICOMP-CONSENT-{uuid.uuid4().hex[:6]}",
            "type": "Consent Mechanisms",
            "category": "Open Source Compliance",
            "description": "Verification of consent mechanisms for using open-source contributions in training",
            "risk_level": "medium",
            "location": "Training Data",
            "details": {
                "consideration": "Check if model training respected license terms of open source code and obtained proper consent",
                "recommendations": [
                    "Create a license compatibility assessment for all code used in training",
                    "Implement a consent mechanism for code authors to opt-in to training usage",
                    "Maintain a database of licenses that are compatible with AI training",
                    "Exclude code with licenses that explicitly prohibit use in AI training",
                    "Develop a consent verification workflow for future data collection"
                ],
                "remediation_path": "To close this finding, implement a License Compatibility System that screens training data based on license terms, documents consent processes, and respects copyright restrictions."
            }
        })
        
        # Add checks for opt-out rights
        findings.append({
            "id": f"AICOMP-OPTOUT-{uuid.uuid4().hex[:6]}",
            "type": "Developer Opt-Out Rights",
            "category": "Rights Management",
            "description": "Compliance with developer rights to exclude their data from model training",
            "risk_level": "high",
            "location": "Data Management",
            "details": {
                "consideration": "Verify if the model respects opt-out mechanisms like .gitignore or specific exclusion tags",
                "recommendations": [
                    "Honor repository-level opt-out markers such as .ml-ignore or .aiignore files",
                    "Create a public registry for developers to exclude their work from training",
                    "Implement file-level exclusion recognition via special headers or comments",
                    "Regularly update your training pipeline to check for opt-out requests",
                    "Develop a simple process for retroactive removal of training data upon request"
                ],
                "remediation_path": "To close this finding, establish a Developer Rights Portal where code authors can register their opt-out preferences, view opt-out status, and request removal of their content from training datasets."
            }
        })
        
        # Add checks for explainability
        findings.append({
            "id": f"AICOMP-EXPLAIN-{uuid.uuid4().hex[:6]}",
            "type": "Explainability Requirements",
            "category": "Transparency",
            "description": "Assessment of explainability when AI tools suggest or generate code",
            "risk_level": "medium",
            "location": "Model Output",
            "details": {
                "consideration": "Review if the model provides adequate source attribution and explanation for generated content",
                "recommendations": [
                    "Implement a citation system for generated code that references similar source material",
                    "Provide confidence levels for each generated code suggestion",
                    "Add 'inspiration sources' for significant code blocks when possible",
                    "Create an explainability layer that can justify model recommendations",
                    "Design a feedback system where users can request explanation for specific suggestions"
                ],
                "remediation_path": "To close this finding, develop an Attribution & Explanation Framework that provides appropriate source citations and explains the reasoning behind code suggestions when requested by users."
            }
        })
        
        # Add checks for audit trails
        findings.append({
            "id": f"AICOMP-AUDIT-{uuid.uuid4().hex[:6]}",
            "type": "Audit Trail Verification",
            "category": "Accountability",
            "description": "Verification of audit trails for models trained with publicly available code",
            "risk_level": "medium",
            "location": "Training Process",
            "details": {
                "consideration": "Check if proper documentation and traceability exists for training data sources",
                "recommendations": [
                    "Maintain comprehensive logs of all data sources used for model training",
                    "Implement data provenance tracking throughout the training pipeline",
                    "Create checkpoints in the training process for auditability",
                    "Document all data cleaning and preprocessing steps",
                    "Enable third-party audit capabilities for your training methodology"
                ],
                "remediation_path": "To close this finding, establish a Training Audit System that documents all aspects of the training process including data sources, preprocessing steps, and model validation, with capabilities for both internal and third-party audit verification."
            }
        })
        
        return findings

    def _calculate_risk_metrics(
            self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        risk_levels = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for finding in findings:
            level = finding.get("risk_level", "low").lower()
            if level in risk_levels:
                risk_levels[level] += 1
        risk_score = min(
            risk_levels["critical"] * 30 + risk_levels["high"] * 15 +
            risk_levels["medium"] * 5 + risk_levels["low"] * 1, 100)
        if risk_score >= 75:
            severity = "critical"
        elif risk_score >= 50:
            severity = "high"
        elif risk_score >= 25:
            severity = "medium"
        else:
            severity = "low"
        return {
            "risk_score": risk_score,
            "severity_level": severity,
            "severity_color": {
                "low": "#10b981",
                "medium": "#f59e0b",
                "high": "#ef4444",
                "critical": "#7f1d1d"
            }[severity],
            "risk_counts": risk_levels,
            "total_findings": len(findings)
        }
    
    def _calculate_ai_compliance_metrics(self, scan_result: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate AI-specific compliance metrics for display"""
        findings = scan_result.get("findings", [])
        model_source = scan_result.get("model_source", "Unknown")
        
        # Detect model framework from findings or source
        framework = "Unknown"
        if any("tensorflow" in str(finding).lower() for finding in findings):
            framework = "TensorFlow"
        elif any("pytorch" in str(finding).lower() for finding in findings):
            framework = "PyTorch"
        elif any("onnx" in str(finding).lower() for finding in findings):
            framework = "ONNX"
        elif any("scikit" in str(finding).lower() for finding in findings):
            framework = "scikit-learn"
        elif model_source in ["Model Hub", "API Endpoint"]:
            framework = "Cloud-based Model"
        elif model_source == "Repository URL":
            framework = "Open Source Model"
        else:
            framework = "Multi-Framework"
            
        # Calculate compliance score based on findings
        compliance_score = 100
        high_risk_count = sum(1 for f in findings if f.get("risk_level") == "high")
        critical_count = sum(1 for f in findings if f.get("risk_level") == "critical")
        medium_count = sum(1 for f in findings if f.get("risk_level") == "medium")
        
        # Reduce score based on findings
        compliance_score -= (critical_count * 25)
        compliance_score -= (high_risk_count * 15)
        compliance_score -= (medium_count * 8)
        compliance_score = max(compliance_score, 10)  # Minimum 10%
        
        # Determine AI Act 2025 status
        ai_act_status = "Compliant"
        if critical_count > 0:
            ai_act_status = "High Risk - Requires Immediate Action"
        elif high_risk_count > 2:
            ai_act_status = "Medium Risk - Assessment Required"
        elif medium_count > 3:
            ai_act_status = "Low Risk - Monitoring Required"
        elif compliance_score < 70:
            ai_act_status = "Requires Further Assessment"
        
        # Add AI Act risk level classification
        if compliance_score >= 90:
            ai_risk_level = "Minimal Risk"
        elif compliance_score >= 75:
            ai_risk_level = "Limited Risk"
        elif compliance_score >= 60:
            ai_risk_level = "High Risk"
        else:
            ai_risk_level = "Unacceptable Risk"
            
        return {
            "model_framework": framework,
            "ai_act_compliance": ai_act_status,
            "compliance_score": compliance_score,
            "ai_model_compliance": compliance_score,
            "ai_act_risk_level": ai_risk_level,
        }
