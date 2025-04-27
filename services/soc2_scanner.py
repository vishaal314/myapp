"""
SOC2 Compliance Scanner for IaC Code

This module provides functionality to scan infrastructure-as-code (IaC) repositories
for SOC2 compliance issues. It focuses on common security and compliance issues
in Terraform, CloudFormation, Ansible, and other IaC tools.
"""

import os
import re
import json
import logging
from typing import Dict, List, Any, Tuple, Optional, Set
import tempfile
import glob
import shutil
import subprocess
from datetime import datetime
import traceback

logger = logging.getLogger(__name__)

# SOC2 Compliance categories
SOC2_CATEGORIES = {
    "security": "Security",
    "availability": "Availability",
    "processing_integrity": "Processing Integrity",
    "confidentiality": "Confidentiality",
    "privacy": "Privacy"
}

# SOC2 Compliance risk levels
RISK_LEVELS = ["high", "medium", "low"]

# IaC file patterns to identify
IaC_FILE_PATTERNS = {
    "terraform": [r"\.tf$", r"\.tfvars$", r"terraform\..*\.json$"],
    "cloudformation": [r"\.yaml$", r"\.yml$", r"\.json$"],
    "ansible": [r"\.ya?ml$", r"playbook\..*\.ya?ml$", r"inventory\..*"],
    "kubernetes": [r"\.ya?ml$", r"kustomization\.ya?ml$"],
    "docker": [r"Dockerfile$", r"docker-compose\.ya?ml$"],
    "pulumi": [r"\.ts$", r"\.js$", r"\.py$", r"Pulumi\.yaml$"],
    "chef": [r"\.rb$", r"Berksfile$", r"metadata\.rb$"],
    "puppet": [r"\.pp$", r"Puppetfile$"]
}

# Risk patterns for each IaC tool
# Format: {pattern: (description, severity, recommendation, category)}
TERRAFORM_RISK_PATTERNS = {
    r"provider\s+\"aws\"": (
        "AWS provider without version constraint",
        "medium",
        "Specify provider version constraints for better stability and security",
        "security"
    ),
    r"access_key.*=": (
        "Hard-coded AWS access keys",
        "high",
        "Use environment variables, instance profiles, or secret management tools instead of hard-coded credentials",
        "security"
    ),
    r"secret.*=": (
        "Possible hard-coded secrets",
        "high",
        "Store secrets in a dedicated secret management service",
        "security"
    ),
    r"password.*=": (
        "Possible hard-coded password",
        "high", 
        "Use secrets manager instead of hard-coded passwords",
        "security"
    ),
    r"ingress\s+{[^}]*0\.0\.0\.0/0": (
        "Security group with unrestricted ingress",
        "high",
        "Restrict ingress traffic to known IP ranges or specific sources",
        "security"
    ),
    r"acl\s*=\s*\"public-read\"": (
        "S3 bucket with public read access",
        "high",
        "Restrict S3 bucket access to only required principals",
        "confidentiality"
    ),
    r"encrypted\s*=\s*false": (
        "Resource with encryption disabled",
        "high",
        "Enable encryption for data protection",
        "confidentiality"
    ),
    r"logging[^}]*=\s*\{\s*\}": (
        "Resource without logging configured",
        "medium",
        "Enable logging for audit and compliance purposes",
        "processing_integrity"
    ),
    r"backup[^}]*=\s*false": (
        "Resource with backups disabled",
        "medium",
        "Enable backup for data protection and availability",
        "availability"
    ),
    r"disable_api_termination\s*=\s*false": (
        "EC2 instance without termination protection",
        "low",
        "Enable termination protection for critical resources",
        "availability"
    ),
    r"versioning[^}]*=\s*\{\s*enabled\s*=\s*false": (
        "S3 bucket without versioning",
        "medium", 
        "Enable versioning for data protection and recovery",
        "availability"
    ),
    r"monitoring\s*=\s*false": (
        "Resource with monitoring disabled",
        "medium",
        "Enable monitoring for effective operational oversight",
        "availability"
    ),
}

CLOUDFORMATION_RISK_PATTERNS = {
    r"Effect\"\s*:\s*\"Allow\"[^{]*\"\*\"": (
        "IAM policy with unrestricted access",
        "high",
        "Follow the principle of least privilege by limiting permissions",
        "security"
    ),
    r"\"CidrIp\"\s*:\s*\"0\.0\.0\.0/0\"": (
        "Security group with unrestricted access",
        "high",
        "Restrict access to specific IP ranges or security groups",
        "security"
    ),
    r"\"AccessControl\"\s*:\s*\"PublicRead\"": (
        "S3 bucket with public read access",
        "high",
        "Restrict S3 bucket access to only required principals",
        "confidentiality"
    ),
    r"\"DeletionPolicy\"\s*:\s*\"Delete\"": (
        "Resource without deletion protection",
        "medium",
        "Use 'Retain' for critical resources to prevent accidental deletion",
        "availability"
    ),
    r"\"Encrypted\"\s*:\s*false": (
        "Resource with encryption disabled",
        "high",
        "Enable encryption for data protection",
        "confidentiality"
    ),
}

KUBERNETES_RISK_PATTERNS = {
    r"privileged:\s*true": (
        "Container running in privileged mode",
        "high",
        "Avoid running containers in privileged mode",
        "security"
    ),
    r"hostPath:": (
        "Pod using hostPath volume",
        "high",
        "Avoid using hostPath as it allows access to host filesystem",
        "security"
    ),
    r"readOnlyRootFilesystem:\s*false": (
        "Container without read-only root filesystem",
        "medium",
        "Enable readOnlyRootFilesystem for better security",
        "security"
    ),
    r"runAsNonRoot:\s*false": (
        "Container not running as non-root user",
        "medium",
        "Run containers as non-root users",
        "security"
    ),
    r"allowPrivilegeEscalation:\s*true": (
        "Container allowed to escalate privileges",
        "high",
        "Disable privilege escalation for containers",
        "security"
    ),
    r"namespace:\s*default": (
        "Resources in default namespace",
        "low",
        "Use dedicated namespaces for better isolation",
        "security"
    ),
}

DOCKER_RISK_PATTERNS = {
    r"FROM\s+.*latest": (
        "Using 'latest' tag for base image",
        "medium",
        "Use specific version tags for base images",
        "processing_integrity"
    ),
    r"ADD\s+http": (
        "Using ADD with HTTP source",
        "medium",
        "Use COPY instead of ADD and download files in a separate step",
        "security"
    ),
    r"ENV\s+AWS_SECRET": (
        "AWS secrets in environment variables",
        "high",
        "Don't store secrets in Docker environment variables",
        "security"
    ),
    r"USER\s+root": (
        "Running container as root",
        "high",
        "Create and use non-root users in containers",
        "security"
    ),
    r"RUN\s+.*curl.*(sh|bash)": (
        "Executing scripts directly from URLs",
        "high",
        "Download scripts first and verify before executing",
        "security"
    ),
}

# Combine all patterns for use in scanning
IaC_RISK_PATTERNS = {
    "terraform": TERRAFORM_RISK_PATTERNS,
    "cloudformation": CLOUDFORMATION_RISK_PATTERNS,
    "kubernetes": KUBERNETES_RISK_PATTERNS,
    "docker": DOCKER_RISK_PATTERNS,
    # Add more as needed
}

def identify_iac_technology(file_path: str) -> Optional[str]:
    """
    Identify the IaC technology used in the given file.
    
    Args:
        file_path: Path to the file to analyze
        
    Returns:
        String identifying the IaC technology or None if not identified
    """
    if not os.path.isfile(file_path):
        return None
        
    file_name = os.path.basename(file_path)
    file_content = None
    
    # First try to identify by filename pattern
    for tech, patterns in IaC_FILE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, file_name, re.IGNORECASE):
                # For ambiguous patterns (like .yaml), check content
                if tech in ["cloudformation", "kubernetes", "ansible"] and file_name.endswith((".yaml", ".yml")):
                    # Load content if not already loaded
                    if file_content is None:
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                file_content = f.read()
                        except:
                            return None
                                
                    # Additional checks for specific technologies
                    if tech == "cloudformation" and ("AWSTemplateFormatVersion" in file_content or "Resources" in file_content):
                        return "cloudformation"
                    elif tech == "kubernetes" and ("apiVersion" in file_content and "kind" in file_content):
                        return "kubernetes"
                    elif tech == "ansible" and ("hosts:" in file_content or "tasks:" in file_content):
                        return "ansible"
                else:
                    return tech
    
    # If not identified by name, try content-based identification
    if file_content is None:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
        except:
            return None
            
    # Content-based checks
    if "resource" in file_content and "provider" in file_content:
        return "terraform"
    elif "AWSTemplateFormatVersion" in file_content or "Resources" in file_content:
        return "cloudformation"
    elif "apiVersion" in file_content and "kind" in file_content:
        return "kubernetes"
    elif "FROM" in file_content and ("RUN" in file_content or "CMD" in file_content):
        return "docker"
            
    return None

def scan_iac_file(file_path: str, tech: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Scan an IaC file for compliance issues.
    
    Args:
        file_path: Path to the file to scan
        tech: Optional technology identifier. If None, it will be detected
        
    Returns:
        List of findings, each a dictionary with issue details
    """
    findings = []
    
    # Identify technology if not provided
    if tech is None:
        tech = identify_iac_technology(file_path)
        
    if tech is None or tech not in IaC_RISK_PATTERNS:
        return findings
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Get risk patterns for this technology
        risk_patterns = IaC_RISK_PATTERNS[tech]
        
        # Check each pattern
        for pattern, (description, severity, recommendation, category) in risk_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                context_start = max(0, content.rfind('\n', 0, match.start()) + 1)
                context_end = content.find('\n', match.end())
                if context_end == -1:
                    context_end = len(content)
                    
                code_snippet = content[context_start:context_end].strip()
                
                finding = {
                    "file": file_path,
                    "line": line_num,
                    "description": description,
                    "risk_level": severity,
                    "recommendation": recommendation,
                    "category": category,
                    "location": f"{os.path.basename(file_path)}:{line_num}",
                    "code_snippet": code_snippet,
                    "technology": tech
                }
                
                findings.append(finding)
    except Exception as e:
        logger.error(f"Error scanning file {file_path}: {str(e)}")
        traceback.print_exc()
        
    return findings

def scan_github_repo_for_soc2(repo_url: str, branch: Optional[str] = None, token: Optional[str] = None) -> Dict[str, Any]:
    """
    Scan a GitHub repository for SOC2 compliance issues in IaC code.
    
    Args:
        repo_url: GitHub repository URL
        branch: Optional branch name
        token: Optional GitHub access token for private repos
        
    Returns:
        Dictionary with scan results
    """
    # Initialize results
    results = {
        "scan_type": "soc2",
        "timestamp": datetime.now().isoformat(),
        "repo_url": repo_url,
        "branch": branch or "main",
        "findings": [],
        "summary": {
            "security": {"high": 0, "medium": 0, "low": 0},
            "availability": {"high": 0, "medium": 0, "low": 0},
            "processing_integrity": {"high": 0, "medium": 0, "low": 0},
            "confidentiality": {"high": 0, "medium": 0, "low": 0},
            "privacy": {"high": 0, "medium": 0, "low": 0}
        },
        "scan_status": "failed",
        "technologies_detected": set(),
        "total_files_scanned": 0,
        "iac_files_found": 0,
        "high_risk_count": 0,
        "medium_risk_count": 0,
        "low_risk_count": 0,
    }
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    clone_successful = False
    
    try:
        # Prepare clone command
        if token:
            # Use token for authentication
            auth_repo_url = repo_url.replace("https://", f"https://{token}@")
        else:
            auth_repo_url = repo_url
            
        # Add branch parameter if provided
        branch_param = []
        if branch:
            branch_param = ["-b", branch]
            
        # Clone repository
        logger.info(f"Cloning repository {repo_url}...")
        process = subprocess.run(
            ["git", "clone", "--depth", "1"] + branch_param + [auth_repo_url, temp_dir],
            capture_output=True,
            text=True
        )
        
        if process.returncode != 0:
            error_msg = process.stderr.strip()
            logger.error(f"Failed to clone repo: {error_msg}")
            results["error"] = f"Failed to clone repository: {error_msg}"
            return results
            
        clone_successful = True
        
        # Scan all files in the repository
        logger.info("Scanning repository files...")
        
        # Find all files recursively
        all_files = []
        for root, dirs, files in os.walk(temp_dir):
            # Skip .git directory
            if '.git' in dirs:
                dirs.remove('.git')
                
            for file in files:
                file_path = os.path.join(root, file)
                all_files.append(file_path)
        
        results["total_files_scanned"] = len(all_files)
        
        # Scan each file
        for file_path in all_files:
            tech = identify_iac_technology(file_path)
            if tech:
                results["iac_files_found"] += 1
                results["technologies_detected"].add(tech)
                
                file_findings = scan_iac_file(file_path, tech)
                
                # Make file paths relative to repo
                for finding in file_findings:
                    finding["file"] = os.path.relpath(finding["file"], temp_dir)
                    
                    # Update summary counts
                    category = finding["category"]
                    risk_level = finding["risk_level"]
                    
                    if category in results["summary"]:
                        if risk_level in results["summary"][category]:
                            results["summary"][category][risk_level] += 1
                            
                    # Update risk counts
                    if risk_level == "high":
                        results["high_risk_count"] += 1
                    elif risk_level == "medium":
                        results["medium_risk_count"] += 1
                    elif risk_level == "low":
                        results["low_risk_count"] += 1
                
                # Add findings
                results["findings"].extend(file_findings)
        
        # Convert technologies_detected from set to list for JSON serialization
        results["technologies_detected"] = list(results["technologies_detected"])
        
        # Calculate compliance score based on findings
        total_findings = len(results["findings"])
        high_risk = results["high_risk_count"]
        medium_risk = results["medium_risk_count"]
        low_risk = results["low_risk_count"]
        
        # Base score is 100, deduct points based on findings
        base_score = 100
        if total_findings > 0:
            # Calculate weighted impact of findings
            weighted_impact = (high_risk * 10 + medium_risk * 5 + low_risk * 2) / (results["iac_files_found"] or 1)
            # Cap the impact to ensure score doesn't go below 0
            weighted_impact = min(95, weighted_impact)
            compliance_score = base_score - weighted_impact
        else:
            compliance_score = base_score
            
        results["compliance_score"] = max(5, int(compliance_score))
        
        # Update scan status
        results["scan_status"] = "completed"
        
        # Add recommendations
        results["recommendations"] = generate_recommendations(results)
        
    except Exception as e:
        logger.error(f"Error scanning repository: {str(e)}")
        traceback.print_exc()
        results["error"] = f"Error scanning repository: {str(e)}"
    finally:
        # Clean up temp directory
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except:
                logger.warning(f"Failed to clean up temp directory: {temp_dir}")
    
    return results

def generate_recommendations(scan_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate recommendations based on scan results.
    
    Args:
        scan_results: Scan results dictionary
        
    Returns:
        List of recommendation dictionaries
    """
    recommendations = []
    
    # Extract unique recommendations to avoid duplication
    unique_recs = {}
    for finding in scan_results.get("findings", []):
        rec_key = (finding["recommendation"], finding["category"], finding["risk_level"])
        if rec_key not in unique_recs:
            unique_recs[rec_key] = {
                "description": f"SOC2 {finding['category'].capitalize()} - {finding['recommendation']}",
                "severity": finding["risk_level"],
                "impact": "High" if finding["risk_level"] == "high" else "Medium" if finding["risk_level"] == "medium" else "Low",
                "category": finding["category"],
                "steps": [],
                "affected_files": []
            }
        
        # Add file to affected files if not already there
        file_info = f"{finding['file']}:{finding['line']}"
        if file_info not in unique_recs[rec_key]["affected_files"]:
            unique_recs[rec_key]["affected_files"].append(file_info)
    
    # Create recommendations list
    for rec_data in unique_recs.values():
        # Create steps based on category and severity
        if rec_data["category"] == "security":
            if rec_data["severity"] == "high":
                rec_data["steps"] = [
                    "Review and remove hard-coded credentials and secrets",
                    "Implement proper secret management",
                    "Update security configurations to follow least privilege principle",
                    f"Focus on files: {', '.join(rec_data['affected_files'][:3])}" + ("..." if len(rec_data["affected_files"]) > 3 else "")
                ]
            else:
                rec_data["steps"] = [
                    "Update security configurations to follow best practices",
                    "Implement proper access controls",
                    f"Focus on files: {', '.join(rec_data['affected_files'][:3])}" + ("..." if len(rec_data["affected_files"]) > 3 else "")
                ]
        elif rec_data["category"] == "availability":
            rec_data["steps"] = [
                "Enable backup and disaster recovery features",
                "Implement proper redundancy and failover mechanisms",
                f"Focus on files: {', '.join(rec_data['affected_files'][:3])}" + ("..." if len(rec_data["affected_files"]) > 3 else "")
            ]
        elif rec_data["category"] == "confidentiality":
            rec_data["steps"] = [
                "Enable encryption for data at rest and in transit",
                "Review and update access controls",
                f"Focus on files: {', '.join(rec_data['affected_files'][:3])}" + ("..." if len(rec_data["affected_files"]) > 3 else "")
            ]
        elif rec_data["category"] == "processing_integrity":
            rec_data["steps"] = [
                "Implement proper logging and monitoring",
                "Enable version control for infrastructure changes",
                f"Focus on files: {', '.join(rec_data['affected_files'][:3])}" + ("..." if len(rec_data["affected_files"]) > 3 else "")
            ]
        elif rec_data["category"] == "privacy":
            rec_data["steps"] = [
                "Review data collection and storage practices",
                "Implement data minimization principles",
                f"Focus on files: {', '.join(rec_data['affected_files'][:3])}" + ("..." if len(rec_data["affected_files"]) > 3 else "")
            ]
        
        # Remove affected_files before adding to recommendations
        affected_files = rec_data.pop("affected_files")
        recommendations.append(rec_data)
    
    # Sort recommendations by severity (high -> medium -> low)
    severity_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda x: severity_order.get(x["severity"], 3))
    
    return recommendations