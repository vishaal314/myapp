"""
PCI DSS Scanner

This module provides a comprehensive PCI DSS-focused code scanning capability
that combines multiple analysis engines to detect compliance issues across:
- Source Code (SAST)
- Configuration Files
- Infrastructure-as-Code (IaC)
- Dependencies (SCA)
- Secrets and Keys

It maps findings to specific PCI DSS requirements and provides detailed
remediation guidance.
"""

import os
import re
import json
import logging
import time
import subprocess
from typing import Dict, List, Any, Tuple, Optional, Callable, Union
from datetime import datetime

# Import the analyzer modules
from services.sast_analyzer import SASTAnalyzer
from services.sca_analyzer import SCAAnalyzer
from services.secrets_detector import SecretsDetector
from services.iac_scanner import IaCScanner
from utils.pci_compliance import map_finding_to_pci_requirement

# Set up logging
logger = logging.getLogger("pcidss_scanner")

class PCIDSSScanner:
    """
    Comprehensive PCI DSS-focused scanner that combines multiple analysis engines
    to provide a complete view of compliance issues in code repositories.
    """
    
    def __init__(self, region: str = "Global", progress_callback: Optional[Callable] = None):
        """
        Initialize the PCI DSS Scanner with all required analyzer modules.
        
        Args:
            region: Geographic region for compliance context (default: "Global")
            progress_callback: Optional callback function to report progress
        """
        self.region = region
        self.progress_callback = progress_callback
        
        # Initialize analyzer components
        self.sast_analyzer = SASTAnalyzer()
        self.sca_analyzer = SCAAnalyzer()
        self.secrets_detector = SecretsDetector()
        self.iac_scanner = IaCScanner()
        
        logger.info("PCI DSS Scanner initialized with all analyzer modules")
        
    def set_progress_callback(self, callback_fn: Callable[[int, int, str], None]) -> None:
        """
        Set the progress callback function.
        
        Args:
            callback_fn: Function to be called to report progress
                         Parameters: (current_step, total_steps, status_message)
        """
        self.progress_callback = callback_fn
        logger.info("Progress callback set for PCI DSS Scanner")
        
    def _update_progress(self, current: int, total: int, message: str) -> None:
        """
        Update scan progress using the callback if provided.
        
        Args:
            current: Current step
            total: Total steps
            message: Status message
        """
        if self.progress_callback:
            self.progress_callback(current, total, message)
            
    def scan_repository(self, 
                       repo_path: str, 
                       branch: str = "main",
                       scan_dependencies: bool = True,
                       scan_iac: bool = True,
                       scan_secrets: bool = True,
                       pci_requirements_filter: Union[List[str], None] = None) -> Dict[str, Any]:
        """
        Scans a repository for PCI DSS compliance issues.
        Uses the region specified during initialization or by the scan method.
        
        Args:
            repo_path: Path or URL to the repository
            branch: Branch to scan (default: "main")
            scan_dependencies: Whether to scan dependencies
            scan_iac: Whether to scan infrastructure-as-code
            scan_secrets: Whether to scan for secrets
            pci_requirements_filter: List of PCI DSS requirements to focus on
            
        Returns:
            Dictionary containing scan results, findings, and metadata
        """
        # Log region to provide context for scan
        logger.info(f"Scanning repository for PCI DSS compliance with regional context: {self.region}")
        """
        Scan a Git repository for PCI DSS compliance issues.
        
        Args:
            repo_path: Path to the Git repository or repository URL
            branch: Branch to scan (default: "main")
            scan_dependencies: Whether to scan dependencies (default: True)
            scan_iac: Whether to scan Infrastructure-as-Code files (default: True)
            scan_secrets: Whether to scan for secrets (default: True)
            pci_requirements_filter: Optional list of PCI DSS requirements to focus on
                                    (e.g., ["6.3.2", "6.3.3"])
        
        Returns:
            Dictionary containing scan results, findings, and metadata
        """
        start_time = time.time()
        logger.info(f"Starting PCI DSS scan of repository: {repo_path}, branch: {branch}")
        
        # Clone repository if it's a URL rather than a local path
        is_remote = repo_path.startswith(("http://", "https://", "git://"))
        local_repo_path = repo_path
        clone_time = 0
        
        if is_remote:
            clone_start = time.time()
            self._update_progress(1, 10, f"Cloning repository {repo_path}")
            
            temp_dir = os.path.join(os.getcwd(), "temp_" + datetime.now().strftime("%Y%m%d%H%M%S"))
            os.makedirs(temp_dir, exist_ok=True)
            
            try:
                subprocess.run(
                    ["git", "clone", "--depth", "1", "--branch", branch, repo_path, temp_dir],
                    check=True,
                    capture_output=True,
                    text=True
                )
                local_repo_path = temp_dir
                clone_time = time.time() - clone_start
                logger.info(f"Repository cloned successfully in {clone_time:.2f} seconds")
            except subprocess.CalledProcessError as e:
                # If specified branch doesn't exist, try default branch
                logger.warning(f"Branch {branch} not found. Attempting to clone default branch.")
                try:
                    subprocess.run(
                        ["git", "clone", "--depth", "1", repo_path, temp_dir],
                        check=True,
                        capture_output=True,
                        text=True
                    )
                    local_repo_path = temp_dir
                    clone_time = time.time() - clone_start
                    # Try to determine what branch was actually cloned
                    try:
                        result = subprocess.run(
                            ["git", "-C", temp_dir, "branch", "--show-current"],
                            check=True,
                            capture_output=True,
                            text=True
                        )
                        actual_branch = result.stdout.strip()
                        branch = actual_branch if actual_branch else "default branch"
                    except:
                        branch = "default branch"
                except Exception as clone_error:
                    logger.error(f"Failed to clone repository: {str(clone_error)}")
                    return {
                        "status": "error",
                        "error": f"Failed to clone repository: {str(clone_error)}",
                        "findings": []
                    }
        
        # Get repository size and stats
        repo_stats = self._get_repo_stats(local_repo_path)
        total_files = repo_stats.get("total_files", 0)
        
        # Set the total number of steps based on enabled scanners
        total_steps = 1  # SAST is always included
        if scan_dependencies:
            total_steps += 1
        if scan_iac:
            total_steps += 1
        if scan_secrets:
            total_steps += 1
            
        current_step = 1
        findings = []
        
        # Step 1: Perform SAST analysis
        self._update_progress(current_step, total_steps, "Performing Static Application Security Testing (SAST)")
        sast_findings = self.sast_analyzer.analyze(local_repo_path)
        findings.extend(sast_findings)
        current_step += 1
        
        # Step 2: Scan dependencies if enabled
        if scan_dependencies:
            self._update_progress(current_step, total_steps, "Analyzing dependencies for vulnerabilities (SCA)")
            sca_findings = self.sca_analyzer.analyze(local_repo_path)
            findings.extend(sca_findings)
            current_step += 1
        
        # Step 3: Scan Infrastructure-as-Code if enabled
        if scan_iac:
            self._update_progress(current_step, total_steps, "Scanning Infrastructure-as-Code files (IaC)")
            iac_findings = self.iac_scanner.analyze(local_repo_path)
            findings.extend(iac_findings)
            current_step += 1
        
        # Step 4: Scan for secrets if enabled
        if scan_secrets:
            self._update_progress(current_step, total_steps, "Detecting hardcoded secrets and credentials")
            secrets_findings = self.secrets_detector.detect(local_repo_path)
            findings.extend(secrets_findings)
            
        # Apply PCI requirements filter if specified
        if pci_requirements_filter:
            filtered_findings = []
            for finding in findings:
                pci_req = finding.get("pci_requirement", "")
                if any(req in pci_req for req in pci_requirements_filter):
                    filtered_findings.append(finding)
            findings = filtered_findings
            
        # Map findings to PCI DSS requirements and add contextual information
        enhanced_findings = []
        for finding in findings:
            if "pci_requirement" not in finding:
                # Map finding to PCI requirement if not already mapped
                pci_req = map_finding_to_pci_requirement(finding["type"])
                finding["pci_requirement"] = pci_req
            
            # Ensure all required fields are present
            if "risk_level" not in finding:
                finding["risk_level"] = self._determine_risk_level(finding)
                
            enhanced_findings.append(finding)
            
        # Calculate risk metrics
        high_risk = sum(1 for f in enhanced_findings if f.get("risk_level", "").lower() == "high")
        medium_risk = sum(1 for f in enhanced_findings if f.get("risk_level", "").lower() == "medium")
        low_risk = sum(1 for f in enhanced_findings if f.get("risk_level", "").lower() == "low")
        total_findings = len(enhanced_findings)
        
        # Generate compliance score (100-based score where higher is better)
        # Formula: 100 - (high_risk * 10 + medium_risk * 3 + low_risk)
        penalty = (high_risk * 10) + (medium_risk * 3) + (low_risk)
        compliance_score = max(0, min(100, 100 - penalty))
        
        # Generate recommendations
        recommendations = self._generate_recommendations(enhanced_findings)
        
        # Cleanup if remote repository
        if is_remote and os.path.exists(local_repo_path):
            try:
                import shutil
                shutil.rmtree(local_repo_path)
            except Exception as e:
                logger.warning(f"Failed to clean up temporary directory: {str(e)}")
                
        # Finalize and return results
        scan_time = time.time() - start_time - clone_time
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "scan_type": "PCI DSS",
            "repository": repo_path,
            "branch": branch,
            "findings": enhanced_findings,
            "high_risk_count": high_risk,
            "medium_risk_count": medium_risk,
            "low_risk_count": low_risk,
            "total_pii_found": total_findings,  # For consistency with other scanners
            "compliance_score": compliance_score,
            "performance": {
                "clone_time": round(clone_time, 2),
                "scan_time": round(scan_time, 2),
                "total_time": round(time.time() - start_time, 2)
            },
            "repository_stats": repo_stats,
            "recommendations": recommendations,
            "region": self.region  # Include the region in the results
        }
    
    def _get_repo_stats(self, repo_path: str) -> Dict[str, Any]:
        """
        Get statistics about the repository.
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            Dictionary containing repository statistics
        """
        stats = {
            "total_files": 0,
            "file_extensions": {},
            "file_types": {
                "code": 0,
                "configuration": 0,
                "iac": 0,
                "dependency": 0,
                "other": 0
            },
            "languages": {}
        }
        
        # List of extensions by type
        code_exts = ['.py', '.js', '.ts', '.java', '.cs', '.go', '.php', '.rb', '.cpp', '.c', '.h', '.swift']
        config_exts = ['.yml', '.yaml', '.json', '.xml', '.ini', '.cfg', '.conf', '.env', '.properties']
        iac_exts = ['.tf', '.hcl', '.template', '.cf.json', '.cf.yaml', '.bicep', '.arm.json']
        dependency_files = ['package.json', 'requirements.txt', 'pom.xml', 'build.gradle', 'Gemfile', 'Cargo.toml']
        
        # Walk the repository directory
        for root, _, files in os.walk(repo_path):
            # Skip .git directory
            if '.git' in root:
                continue
                
            for file in files:
                # Skip hidden files
                if file.startswith('.'):
                    continue
                    
                file_path = os.path.join(root, file)
                _, ext = os.path.splitext(file)
                
                # Count total files
                stats["total_files"] += 1
                
                # Count by extension
                if ext in stats["file_extensions"]:
                    stats["file_extensions"][ext] += 1
                else:
                    stats["file_extensions"][ext] = 1
                    
                # Count by file type
                if ext in code_exts:
                    stats["file_types"]["code"] += 1
                elif ext in config_exts:
                    stats["file_types"]["configuration"] += 1
                elif ext in iac_exts:
                    stats["file_types"]["iac"] += 1
                elif file in dependency_files:
                    stats["file_types"]["dependency"] += 1
                else:
                    stats["file_types"]["other"] += 1
                    
                # Try to determine language based on extension
                language = self._extension_to_language(ext)
                if language:
                    if language in stats["languages"]:
                        stats["languages"][language] += 1
                    else:
                        stats["languages"][language] = 1
        
        return stats
    
    def _extension_to_language(self, ext: str) -> Optional[str]:
        """
        Convert file extension to programming language.
        
        Args:
            ext: File extension
            
        Returns:
            Programming language name or None
        """
        mapping = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cs': 'C#',
            '.go': 'Go',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.cpp': 'C++',
            '.c': 'C',
            '.h': 'C/C++ Header',
            '.swift': 'Swift',
            '.tf': 'Terraform',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.json': 'JSON',
            '.xml': 'XML'
        }
        return mapping.get(ext.lower())
    
    def _determine_risk_level(self, finding: Dict[str, Any]) -> str:
        """
        Determine the risk level for a finding based on its type and context.
        
        Args:
            finding: The finding dictionary
            
        Returns:
            Risk level string ("High", "Medium", or "Low")
        """
        finding_type = finding.get("type", "").lower()
        
        # High risk vulnerabilities
        high_risk_types = [
            "sql injection", 
            "remote code execution", 
            "command injection",
            "insecure deserialization",
            "xxe",
            "ssrf",
            "path traversal", 
            "credential",
            "api key",
            "password",
            "secret",
            "token",
            "cvss:9",
            "cvss:10"
        ]
        
        # Medium risk vulnerabilities
        medium_risk_types = [
            "xss",
            "cross-site scripting",
            "csrf",
            "open redirect",
            "information disclosure",
            "weak authentication",
            "insecure configuration",
            "insecure s3 bucket",
            "cvss:6",
            "cvss:7",
            "cvss:8"
        ]
        
        # Determine risk level based on type
        if any(risk_type in finding_type for risk_type in high_risk_types):
            return "High"
        elif any(risk_type in finding_type for risk_type in medium_risk_types):
            return "Medium"
        else:
            return "Low"
    def scan(self, **kwargs) -> Dict[str, Any]:
        """
        Main scan method that handles different scan modes and sources.
        This is the primary interface for scanning in the PCIDSSScanner class.
        
        Args:
            **kwargs: Keyword arguments include:
                - repo_url: GitHub repository URL (for GitHub repo scanning)
                - branch: Branch to scan (default: "main")
                - token: GitHub access token for private repos
                - uploaded_files: List of files uploaded by the user (for local scanning)
                - scan_scope: List of scan components to include
                - requirements: Dictionary mapping PCI DSS requirements to boolean flags
                - output_formats: List of desired output formats
                - region: Geographic region for compliance context (default: "Global")
                
        Returns:
            Dictionary containing scan results, findings, and metadata
        """
        # Extract parameters
        repo_url = kwargs.get('repo_url')
        branch = kwargs.get('branch', 'main')
        token = kwargs.get('token')
        uploaded_files = kwargs.get('uploaded_files', [])
        scan_scope = kwargs.get('scan_scope', [])
        requirements = kwargs.get('requirements', {})
        output_formats = kwargs.get('output_formats', ['PDF'])
        
        # Allow region override from scan parameters
        region = kwargs.get('region')
        if region:
            self.region = region
            
        logger.info(f"Starting PCI DSS scan with region context: {self.region}")
        
        # Determine scan mode based on inputs
        if repo_url:
            # For GitHub repository scanning
            # Add token to URL if provided
            if token and 'github.com' in repo_url:
                # Format: https://{token}@github.com/...
                if 'https://' in repo_url:
                    repo_url = repo_url.replace('https://', f'https://{token}@')
                else:
                    repo_url = f'https://{token}@github.com/{repo_url.replace("github.com/", "")}'
            
            # Convert requirements dict to list of PCI DSS requirement strings
            pci_requirements_filter = []
            for req_name, include in requirements.items():
                if include:
                    # Convert req1, req2, etc. to 1, 2, etc.
                    req_num = req_name.replace('req', '')
                    pci_requirements_filter.append(req_num)
            
            # Determine which scan components to include
            scan_dependencies = "SCA (Software Composition Analysis)" in scan_scope
            scan_iac = "IaC (Infrastructure-as-Code) Scanning" in scan_scope
            scan_secrets = "Secrets Detection" in scan_scope
            
            # Perform the repository scan
            results = self.scan_repository(
                repo_path=repo_url,
                branch=branch,
                scan_dependencies=scan_dependencies,
                scan_iac=scan_iac,
                scan_secrets=scan_secrets,
                pci_requirements_filter=pci_requirements_filter
            )
            
            # Add repo URL to results for display
            results['repo_url'] = repo_url
            
        elif uploaded_files:
            # For local file uploads
            # Create a temporary directory to store uploaded files
            import tempfile
            import os
            import shutil
            
            temp_dir = tempfile.mkdtemp()
            try:
                # Save uploaded files to temp directory
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(file_path, 'wb') as f:
                        f.write(uploaded_file.getbuffer())
                
                # Convert requirements dict to list of PCI DSS requirement strings
                pci_requirements_filter = []
                for req_name, include in requirements.items():
                    if include:
                        req_num = req_name.replace('req', '')
                        pci_requirements_filter.append(req_num)
                
                # Determine which scan components to include
                scan_dependencies = "SCA (Software Composition Analysis)" in scan_scope
                scan_iac = "IaC (Infrastructure-as-Code) Scanning" in scan_scope
                scan_secrets = "Secrets Detection" in scan_scope
                
                # Scan the local directory
                results = self.scan_repository(
                    repo_path=temp_dir,
                    scan_dependencies=scan_dependencies,
                    scan_iac=scan_iac,
                    scan_secrets=scan_secrets,
                    pci_requirements_filter=pci_requirements_filter
                )
                
                # Add source info to results
                results['source'] = 'Local Upload'
                results['file_count'] = len(uploaded_files)
                
            except Exception as e:
                logger.error(f"Error processing uploaded files: {str(e)}")
                results = {
                    "status": "error",
                    "error": f"Error processing uploaded files: {str(e)}",
                    "findings": []
                }
            finally:
                # Clean up temp directory
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary directory: {str(e)}")
        else:
            # No valid scan source provided
            results = {
                "status": "error",
                "error": "No valid scan source provided",
                "findings": []
            }
        
        # Add PCI DSS categories for reporting
        results['pci_categories'] = self._count_findings_by_pci_category(results.get('findings', []))
        
        return results
        
    def _count_findings_by_pci_category(self, findings: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Count findings by PCI DSS requirement category.
        
        Args:
            findings: List of finding dictionaries
            
        Returns:
            Dictionary mapping PCI DSS requirements to counts
        """
        categories = {
            "Req 1": 0,  # Network Security
            "Req 2": 0,  # Secure Configurations
            "Req 3": 0,  # Cardholder Data Protection
            "Req 4": 0,  # Transmission Security
            "Req 5": 0,  # Malware Protection
            "Req 6": 0,  # Secure Systems
            "Req 7": 0,  # Access Control
            "Req 8": 0,  # Authentication
            "Req 9": 0,  # Physical Access
            "Req 10": 0, # System Monitoring
            "Req 11": 0, # Security Testing
            "Req 12": 0  # Security Policy
        }
        
        for finding in findings:
            pci_req = finding.get('pci_requirement', '')
            if not pci_req:
                continue
                
            # Extract the primary requirement number (e.g., "6.5.1" -> "6")
            parts = pci_req.split('.')
            if parts and parts[0].isdigit():
                req_key = f"Req {parts[0]}"
                if req_key in categories:
                    categories[req_key] += 1
        
        return categories
    
    def _generate_recommendations(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate prioritized recommendations based on findings.
        
        Args:
            findings: List of findings
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        # Group findings by PCI DSS requirement
        pci_req_groups = {}
        for finding in findings:
            pci_req = finding.get("pci_requirement", "Unknown")
            if pci_req not in pci_req_groups:
                pci_req_groups[pci_req] = []
            pci_req_groups[pci_req].append(finding)
        
        # Generate recommendations for each PCI DSS requirement group
        for pci_req, req_findings in pci_req_groups.items():
            # Count risk levels
            high_count = sum(1 for f in req_findings if f.get("risk_level") == "High")
            medium_count = sum(1 for f in req_findings if f.get("risk_level") == "Medium")
            
            # Determine severity based on findings
            if high_count > 0:
                severity = "High"
            elif medium_count > 0:
                severity = "Medium"
            else:
                severity = "Low"
                
            # Create recommendation description
            if "6.3.2" in pci_req:
                description = f"Review and fix {len(req_findings)} secure coding issues that violate PCI DSS 6.3.2 requiring secure coding practices"
                remediation = "Implement input validation, parameterized queries, and proper error handling according to OWASP Top 10"
            elif "6.3.3" in pci_req:
                description = f"Address {len(req_findings)} vulnerabilities related to PCI DSS 6.3.3 requiring security vulnerability identification"
                remediation = "Implement regular code reviews and automated security scanning in your development pipeline"
            elif "6.3.4" in pci_req:
                description = f"Update {len(req_findings)} vulnerable dependencies to comply with PCI DSS 6.3.4 requiring patches and security updates"
                remediation = "Establish a process for regular dependency updates and vulnerability patching"
            elif "3.3.3" in pci_req:
                description = f"Remove {len(req_findings)} hardcoded secrets to comply with PCI DSS 3.3.3 requiring secure storage of credentials"
                remediation = "Store secrets in a secure vault and use environment variables or a secrets manager to reference them"
            elif "1.2.7" in pci_req:
                description = f"Fix {len(req_findings)} insecure cloud configurations to comply with PCI DSS 1.2.7 requiring network security controls"
                remediation = "Implement proper network security groups, encryption, and access controls for cloud resources"
            else:
                description = f"Address {len(req_findings)} issues related to PCI DSS requirement {pci_req}"
                remediation = "Review and remediate identified issues according to PCI DSS guidance"
                
            # Add to recommendations list
            recommendations.append({
                "category": f"PCI DSS {pci_req}",
                "description": description,
                "severity": severity,
                "remediation": remediation,
                "issues_count": len(req_findings)
            })
        
        # Sort recommendations by severity
        severity_order = {"High": 0, "Medium": 1, "Low": 2}
        recommendations.sort(key=lambda x: severity_order.get(x["severity"], 3))
        
        return recommendations