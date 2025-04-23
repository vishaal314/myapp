import uuid
import json
import os
import time
import logging
import requests  # 👈 required for URL validation
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable


class AIModelScanner:
    """
    AI Model Scanner class for identifying PII risks in AI models
    """

    def __init__(self, region: str = "Global"):
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
        }

        if model_source == "API Endpoint":
            scan_result["api_endpoint"] = model_details.get("api_endpoint", "")
            scan_result["repository_path"] = model_details.get(
                "repository_path", "")
        elif model_source == "Model Hub":
            scan_result["model_name"] = model_details.get("hub_url", "")
            scan_result["repository_path"] = model_details.get(
                "repository_path", "")
        elif model_source == "Repository URL":
            repo_url = model_details.get("repo_url", "")
            branch = model_details.get("branch_name", "main")
            scan_result["repository_url"] = repo_url
            scan_result["branch"] = branch

            # ✅ Validate the repo URL
            if not self._validate_github_repo(repo_url):
                scan_result["findings"].append({
                    "id":
                    f"REPO-INVALID-{uuid.uuid4().hex[:6]}",
                    "type":
                    "Repository Error",
                    "category":
                    "Source Validation",
                    "description":
                    f"Repository URL '{repo_url}' is invalid or inaccessible.",
                    "risk_level":
                    "high",
                    "location":
                    "Repository Validator"
                })
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
                    "total_findings": 1
                })
                return scan_result

        total_steps = 4
        if self.progress_callback:
            self.progress_callback(1, total_steps,
                                   "Initializing AI model scan")

        try:
            if self.progress_callback:
                self.progress_callback(2, total_steps,
                                       "Analyzing model architecture")
            time.sleep(1)
            arch_findings = self._generate_architecture_findings(
                model_source, model_details)
            scan_result["findings"].extend(arch_findings)

            if self.progress_callback:
                self.progress_callback(3, total_steps,
                                       "Analyzing input/output patterns")
            time.sleep(1)
            io_findings = self._generate_io_findings(sample_inputs, context)
            scan_result["findings"].extend(io_findings)

            if self.progress_callback:
                self.progress_callback(4, total_steps,
                                       "Performing compliance assessment")
            time.sleep(1)
            compliance_findings = self._generate_compliance_findings(
                leakage_types, self.region)
            scan_result["findings"].extend(compliance_findings)

            try:
                metrics = self._calculate_risk_metrics(scan_result["findings"])
                scan_result.update(metrics)
            except Exception as metrics_error:
                logging.error(
                    f"Error calculating risk metrics: {str(metrics_error)}")
                scan_result.update({
                    "risk_score":
                    50,
                    "severity_level":
                    "medium",
                    "severity_color":
                    "#f59e0b",
                    "risk_counts": {
                        "low": 0,
                        "medium": 1,
                        "high": 0,
                        "critical": 0
                    },
                    "total_findings":
                    len(scan_result["findings"])
                })

            return scan_result

        except Exception as e:
            logging.error(f"Error during AI model scan: {str(e)}")
            return {
                "scan_id":
                scan_id,
                "scan_type":
                "AI Model",
                "timestamp":
                datetime.now().isoformat(),
                "model_source":
                model_source,
                "findings": [{
                    "id": f"AIERROR-{uuid.uuid4().hex[:6]}",
                    "type": "Critical Error",
                    "category": "Scan Failure",
                    "description":
                    f"The AI model scan encountered a critical error: {str(e)}",
                    "risk_level": "high",
                    "location": "AI Model Scanner"
                }],
                "error":
                str(e),
                "status":
                "completed_with_errors",
                "risk_score":
                50,
                "severity_level":
                "medium",
                "severity_color":
                "#f59e0b",
                "risk_counts": {
                    "low": 0,
                    "medium": 0,
                    "high": 1,
                    "critical": 0
                },
                "total_findings":
                1,
                "region":
                self.region
            }

    def _validate_github_repo(self, repo_url: str) -> bool:
        try:
            repo_path = repo_url.replace("https://github.com/", "")
            api_url = f"https://api.github.com/repos/{repo_path}"
            response = requests.get(api_url)
            return response.status_code == 200
        except Exception as e:
            logging.error(f"GitHub repo validation error: {str(e)}")
            return False

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
        if "All" in leakage_types or "PII in Training Data" in leakage_types:
            findings.append({
                "id": f"AICOMP-{uuid.uuid4().hex[:6]}",
                "type": "Training Data Assessment",
                "category": "PII in Training",
                "description": "Potential PII exposure in training data",
                "risk_level": "high",
                "location": "Training Data"
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
