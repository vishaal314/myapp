"""
Infrastructure-as-Code (IaC) Scanner

This module provides capability to scan Infrastructure-as-Code files (Terraform, 
CloudFormation, etc.) for security and compliance issues. It focuses on finding 
issues relevant to PCI DSS requirements for secure infrastructure deployment.
"""

import os
import re
import json
import logging
import subprocess
from typing import Dict, List, Any, Optional

# Set up logging
logger = logging.getLogger("iac_scanner")

class IaCScanner:
    """
    Scans Infrastructure-as-Code files for security and compliance issues.
    """
    
    def __init__(self):
        """Initialize the IaC Scanner."""
        # Define patterns for different types of IaC security issues
        self.terraform_patterns = {
            "unencrypted_storage": [
                r'resource\s*"aws_s3_bucket".*\n(?:(?!\s*server_side_encryption_configuration\s*{)[\s\S])*?\n\s*}',
                r'resource\s*"aws_ebs_volume".*\n(?:(?!\s*encrypted\s*=.*true)[\s\S])*?\n\s*}'
            ],
            "public_access": [
                r'resource\s*"aws_s3_bucket_public_access_block".*\n(?:(?!\s*block_public_acls\s*=\s*true)[\s\S])*?\n\s*}',
                r'resource\s*"aws_s3_bucket".*\n(?:(?!\s*acl\s*=\s*"private")[\s\S])*?\n\s*}'
            ],
            "open_security_groups": [
                r'resource\s*"aws_security_group_rule".*\n(?:.*\n)*?.*cidr_blocks\s*=\s*\[\s*"0\.0\.0\.0/0"\s*\]',
                r'ingress\s*{[^}]*from_port\s*=\s*0[^}]*to_port\s*=\s*0[^}]*protocol\s*=\s*"-1"[^}]*}'
            ],
            "weak_tls": [
                r'resource\s*"aws_alb_listener".*\n(?:(?!\s*ssl_policy\s*=\s*"ELBSecurityPolicy-FS-1-2")[\s\S])*?\n\s*}',
                r'minimum_protocol_version\s*=\s*"TLSv1"'
            ],
            "plaintext_secrets": [
                r'variable\s*"[^"]*password[^"]*"\s*{[^}]*default\s*=\s*"[^}]*}',
                r'variable\s*"[^"]*secret[^"]*"\s*{[^}]*default\s*=\s*"[^}]*}'
            ],
            "logging_disabled": [
                r'resource\s*"aws_s3_bucket".*\n(?:(?!\s*logging\s*{)[\s\S])*?\n\s*}',
                r'resource\s*"aws_cloudtrail".*\n(?:(?!\s*enable_logging\s*=\s*true)[\s\S])*?\n\s*}'
            ],
            "insecure_cors": [
                r'cors_rule\s*{[^}]*allowed_origin\s*=\s*"\*"[^}]*}',
                r'allowed_origins\s*=\s*\[\s*"\*"\s*\]'
            ]
        }
        
        self.cloudformation_patterns = {
            "unencrypted_storage": [
                r'Type\s*:\s*AWS::S3::Bucket[^}]*(?!Properties[^}]*SSEAlgorithm)[^}]*',
                r'Type\s*:\s*AWS::EBS::Volume[^}]*(?!Encrypted[^}]*true)[^}]*'
            ],
            "public_access": [
                r'Type\s*:\s*AWS::S3::Bucket[^}]*PublicAccessBlockConfiguration[^}]*(?!BlockPublicAcls[^}]*true)[^}]*',
                r'Type\s*:\s*AWS::S3::Bucket[^}]*(?!AccessControl[^}]*Private)[^}]*'
            ],
            "open_security_groups": [
                r'Type\s*:\s*AWS::EC2::SecurityGroup[^}]*SecurityGroupIngress[^}]*CidrIp\s*:\s*0\.0\.0\.0/0[^}]*',
                r'Type\s*:\s*AWS::EC2::SecurityGroupIngress[^}]*CidrIp\s*:\s*0\.0\.0\.0/0[^}]*FromPort\s*:\s*0[^}]*ToPort\s*:\s*65535[^}]*'
            ],
            "weak_tls": [
                r'Type\s*:\s*AWS::ElasticLoadBalancingV2::Listener[^}]*(?!SslPolicy[^}]*ELBSecurityPolicy-FS-1-2)[^}]*',
                r'SecurityPolicy\s*:\s*"TLSv1"'
            ],
            "plaintext_secrets": [
                r'Type\s*:\s*AWS::SecretsManager::Secret[^}]*SecretString\s*:\s*[\'"][^\'"+][^}]*',
                r'Type\s*:\s*AWS::RDS::DBInstance[^}]*MasterUserPassword\s*:\s*[\'"][^\'"+][^}]*'
            ],
            "logging_disabled": [
                r'Type\s*:\s*AWS::S3::Bucket[^}]*(?!LoggingConfiguration)[^}]*',
                r'Type\s*:\s*AWS::CloudTrail::Trail[^}]*(?!IsLogging[^}]*true)[^}]*'
            ],
            "insecure_cors": [
                r'Type\s*:\s*AWS::S3::Bucket[^}]*CorsRule[^}]*AllowedOrigin\s*:\s*\'\*\'[^}]*',
                r'Type\s*:\s*AWS::ApiGateway::RestApi[^}]*CorsConfiguration[^}]*AllowOrigins\s*:\s*\[\s*\'\*\'\s*\][^}]*'
            ]
        }
        
        self.kubernetes_patterns = {
            "privileged_containers": [
                r'privileged:\s*true',
                r'allowPrivilegeEscalation:\s*true'
            ],
            "host_network_access": [
                r'hostNetwork:\s*true',
                r'hostPID:\s*true',
                r'hostIPC:\s*true'
            ],
            "run_as_root": [
                r'runAsUser:\s*0',
                r'runAsNonRoot:\s*false'
            ],
            "insecure_capabilities": [
                r'capabilities:\s*(?=.*add:\s*\[\s*(?=.*"ALL"|.*SYS_ADMIN).*\])',
                r'capabilities:\s*(?=.*add:\s*\[\s*(?=.*NET_ADMIN|.*SYS_PTRACE).*\])'
            ],
            "secret_as_env_var": [
                r'env:\s*\n(?:.*\n)*?.*name:\s*\w*(?:secret|password|key|token|credential).*\n(?:.*\n)*?.*value:',
                r'env:\s*\n(?:.*\n)*?.*name:\s*\w*(?:api[_-]?key|access[_-]?key).*\n(?:.*\n)*?.*value:'
            ],
            "insecure_workload": [
                r'kind:\s*(?:Deployment|StatefulSet|DaemonSet)[^}]*(?!securityContext|readOnlyRootFilesystem:\s*true)[^}]*',
                r'kind:\s*Pod[^}]*(?!securityContext|readOnlyRootFilesystem:\s*true)[^}]*'
            ]
        }
        
        # File extensions to scan
        self.iac_file_extensions = {
            '.tf': 'terraform',
            '.tfvars': 'terraform',
            '.hcl': 'terraform',
            '.yaml': 'kubernetes',
            '.yml': 'kubernetes',
            '.json': 'cloudformation',
            '.template': 'cloudformation'
        }
        
        logger.info("IaC Scanner initialized with security patterns")
    
    def analyze(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        Analyze IaC files in the given directory for security issues.
        
        Args:
            directory_path: Path to the directory containing IaC files
            
        Returns:
            List of security findings
        """
        findings = []
        
        # Try to use specialized IaC security tools if available
        try:
            # Try to use Checkov if available
            checkov_findings = self._run_checkov(directory_path)
            if checkov_findings:
                findings.extend(checkov_findings)
                logger.info(f"Found {len(checkov_findings)} issues with Checkov")
                
                # If Checkov worked, we can return early as it's more comprehensive
                if len(checkov_findings) > 0:
                    return findings
        except Exception as e:
            logger.info(f"Checkov not available or failed, using built-in detection: {str(e)}")
        
        # Try to use TFSec if available
        try:
            # For Terraform-specific scanning
            tfsec_findings = self._run_tfsec(directory_path)
            if tfsec_findings:
                findings.extend(tfsec_findings)
                logger.info(f"Found {len(tfsec_findings)} issues with TFSec")
                
                # Continue with other scan methods even if TFSec worked
        except Exception as e:
            logger.info(f"TFSec not available or failed: {str(e)}")
        
        # Fall back to built-in detection
        logger.info("Using built-in IaC security patterns")
        
        # Find all IaC files
        iac_files = []
        for root, _, files in os.walk(directory_path):
            # Skip .git directory
            if '.git' in root:
                continue
                
            for file in files:
                file_path = os.path.join(root, file)
                _, ext = os.path.splitext(file_path)
                
                if ext.lower() in self.iac_file_extensions:
                    iac_files.append((file_path, self.iac_file_extensions[ext.lower()]))
                    
                # Check for CloudFormation templates with different extensions
                elif file.lower().endswith('.cloudformation.json') or file.lower().endswith('.cf.json'):
                    iac_files.append((file_path, 'cloudformation'))
                elif file.lower().endswith('.cloudformation.yaml') or file.lower().endswith('.cf.yaml'):
                    iac_files.append((file_path, 'cloudformation'))
        
        # Scan each file
        for file_path, iac_type in iac_files:
            # Get relative path for reporting
            rel_path = os.path.relpath(file_path, directory_path)
            
            # Read file content
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception as e:
                logger.warning(f"Error reading file {file_path}: {str(e)}")
                continue
                
            # Scan using appropriate patterns
            if iac_type == 'terraform':
                file_findings = self._scan_terraform(content, rel_path)
            elif iac_type == 'cloudformation':
                file_findings = self._scan_cloudformation(content, rel_path)
            elif iac_type == 'kubernetes':
                file_findings = self._scan_kubernetes(content, rel_path)
            else:
                file_findings = []
                
            findings.extend(file_findings)
        
        logger.info(f"Found {len(findings)} IaC security issues with built-in patterns")
        return findings
    
    def _scan_terraform(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Scan Terraform content for security issues.
        
        Args:
            content: The file content
            file_path: The file path for reporting
            
        Returns:
            List of security findings
        """
        findings = []
        
        # Scan for each issue type
        for issue_type, patterns in self.terraform_patterns.items():
            for pattern in patterns:
                try:
                    for match in re.finditer(pattern, content, re.MULTILINE):
                        # Find line number by counting newlines before match
                        line_number = content[:match.start()].count('\n') + 1
                        
                        # Get issue details
                        details = self._get_issue_details(issue_type, 'terraform')
                        
                        # Create finding
                        finding = {
                            "type": f"Insecure IaC Configuration: {details['title']}",
                            "value": match.group(0)[:100] + "..." if len(match.group(0)) > 100 else match.group(0),
                            "location": f"{file_path}:{line_number}",
                            "file_name": file_path,
                            "line_number": line_number,
                            "risk_level": details["risk_level"],
                            "pci_requirement": details["pci_requirement"],
                            "reason": details["reason"],
                            "remediation": details["remediation"]
                        }
                        
                        findings.append(finding)
                except Exception as e:
                    logger.warning(f"Error scanning for {issue_type} in {file_path}: {str(e)}")
        
        return findings
    
    def _scan_cloudformation(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Scan CloudFormation content for security issues.
        
        Args:
            content: The file content
            file_path: The file path for reporting
            
        Returns:
            List of security findings
        """
        findings = []
        
        # Scan for each issue type
        for issue_type, patterns in self.cloudformation_patterns.items():
            for pattern in patterns:
                try:
                    for match in re.finditer(pattern, content, re.MULTILINE):
                        # Find line number by counting newlines before match
                        line_number = content[:match.start()].count('\n') + 1
                        
                        # Get issue details
                        details = self._get_issue_details(issue_type, 'cloudformation')
                        
                        # Create finding
                        finding = {
                            "type": f"Insecure IaC Configuration: {details['title']}",
                            "value": match.group(0)[:100] + "..." if len(match.group(0)) > 100 else match.group(0),
                            "location": f"{file_path}:{line_number}",
                            "file_name": file_path,
                            "line_number": line_number,
                            "risk_level": details["risk_level"],
                            "pci_requirement": details["pci_requirement"],
                            "reason": details["reason"],
                            "remediation": details["remediation"]
                        }
                        
                        findings.append(finding)
                except Exception as e:
                    logger.warning(f"Error scanning for {issue_type} in {file_path}: {str(e)}")
        
        return findings
    
    def _scan_kubernetes(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Scan Kubernetes content for security issues.
        
        Args:
            content: The file content
            file_path: The file path for reporting
            
        Returns:
            List of security findings
        """
        findings = []
        
        # Scan for each issue type
        for issue_type, patterns in self.kubernetes_patterns.items():
            for pattern in patterns:
                try:
                    for match in re.finditer(pattern, content, re.MULTILINE):
                        # Find line number by counting newlines before match
                        line_number = content[:match.start()].count('\n') + 1
                        
                        # Get issue details
                        details = self._get_issue_details(issue_type, 'kubernetes')
                        
                        # Create finding
                        finding = {
                            "type": f"Insecure IaC Configuration: {details['title']}",
                            "value": match.group(0)[:100] + "..." if len(match.group(0)) > 100 else match.group(0),
                            "location": f"{file_path}:{line_number}",
                            "file_name": file_path,
                            "line_number": line_number,
                            "risk_level": details["risk_level"],
                            "pci_requirement": details["pci_requirement"],
                            "reason": details["reason"],
                            "remediation": details["remediation"]
                        }
                        
                        findings.append(finding)
                except Exception as e:
                    logger.warning(f"Error scanning for {issue_type} in {file_path}: {str(e)}")
        
        return findings
    
    def _get_issue_details(self, issue_type: str, iac_type: str) -> Dict[str, str]:
        """
        Get details for an issue type.
        
        Args:
            issue_type: The type of issue
            iac_type: The type of IaC (terraform, cloudformation, kubernetes)
            
        Returns:
            Dictionary with issue details
        """
        # Define issue details
        details = {
            "unencrypted_storage": {
                "title": "Unencrypted Storage",
                "risk_level": "High",
                "pci_requirement": "3.4, 3.5, 4.1",
                "reason": "Storage resource defined without encryption. PCI DSS requires encryption for stored cardholder data.",
                "remediation": "Enable encryption for all storage resources that may contain sensitive data."
            },
            "public_access": {
                "title": "Public Access",
                "risk_level": "High",
                "pci_requirement": "1.2.1, 1.3.1, 1.3.2",
                "reason": "Resource is publicly accessible. PCI DSS requires limiting public access to systems in the cardholder data environment.",
                "remediation": "Restrict access to private networks only and implement proper access controls."
            },
            "open_security_groups": {
                "title": "Overly Permissive Security Group",
                "risk_level": "High",
                "pci_requirement": "1.2.1, 1.3.4",
                "reason": "Security group allows unrestricted access (0.0.0.0/0). PCI DSS requires restricting access to only necessary services.",
                "remediation": "Limit security group rules to specific IP ranges and necessary ports only."
            },
            "weak_tls": {
                "title": "Weak TLS Configuration",
                "risk_level": "Medium",
                "pci_requirement": "4.1",
                "reason": "TLS configuration uses older or insecure protocols. PCI DSS requires strong cryptography for data transmission.",
                "remediation": "Use TLS 1.2 or higher with secure cipher suites."
            },
            "plaintext_secrets": {
                "title": "Plaintext Secrets",
                "risk_level": "High",
                "pci_requirement": "3.3.3, 3.6.1, 3.6.3",
                "reason": "Secrets or credentials defined in plaintext. PCI DSS prohibits storing plaintext credentials.",
                "remediation": "Use a secrets management service or environment variables instead of hardcoded values."
            },
            "logging_disabled": {
                "title": "Logging Disabled",
                "risk_level": "Medium",
                "pci_requirement": "10.1, 10.2",
                "reason": "Resource defined without logging enabled. PCI DSS requires logging of all access to network resources and cardholder data.",
                "remediation": "Enable logging for all resources and ensure logs are stored securely."
            },
            "insecure_cors": {
                "title": "Insecure CORS Configuration",
                "risk_level": "Medium",
                "pci_requirement": "6.5.9",
                "reason": "CORS configuration allows access from any origin (*). This may allow cross-site scripting attacks.",
                "remediation": "Restrict CORS to specific, trusted origins only."
            },
            "privileged_containers": {
                "title": "Privileged Containers",
                "risk_level": "High",
                "pci_requirement": "2.2.4, 2.2.5",
                "reason": "Container runs with privileged access, which bypasses container security controls.",
                "remediation": "Remove privileged mode and use more specific capabilities if needed."
            },
            "host_network_access": {
                "title": "Host Network Access",
                "risk_level": "High",
                "pci_requirement": "1.2.1, 2.2.1",
                "reason": "Container has access to host network, PID, or IPC namespace, which weakens isolation.",
                "remediation": "Remove host network access and use proper network policies."
            },
            "run_as_root": {
                "title": "Container Running as Root",
                "risk_level": "Medium",
                "pci_requirement": "7.1.2, 7.1.3",
                "reason": "Container runs as root user, which may allow privilege escalation if compromised.",
                "remediation": "Use non-root users and set runAsNonRoot: true."
            },
            "insecure_capabilities": {
                "title": "Insecure Container Capabilities",
                "risk_level": "High",
                "pci_requirement": "2.2.4, 7.1.1",
                "reason": "Container has dangerous Linux capabilities that could allow privilege escalation.",
                "remediation": "Remove unnecessary capabilities and apply principle of least privilege."
            },
            "secret_as_env_var": {
                "title": "Secret as Environment Variable",
                "risk_level": "Medium",
                "pci_requirement": "3.3.3, 3.6.1",
                "reason": "Secret or credential passed as environment variable in plaintext.",
                "remediation": "Use Kubernetes Secrets or other secret management tools to securely inject credentials."
            },
            "insecure_workload": {
                "title": "Insecure Workload Configuration",
                "risk_level": "Medium",
                "pci_requirement": "6.5, 6.6",
                "reason": "Workload defined without security context or other security controls.",
                "remediation": "Add security context with proper constraints (readOnlyRootFilesystem, runAsNonRoot, etc.)."
            }
        }
        
        return details.get(issue_type, {
            "title": "Misconfiguration",
            "risk_level": "Medium",
            "pci_requirement": "6.3.3, 6.3.4",
            "reason": "Infrastructure misconfiguration that may lead to security vulnerabilities.",
            "remediation": "Review and secure the infrastructure configuration according to security best practices."
        })
    
    def _run_checkov(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        Run Checkov for IaC security scanning if available.
        
        Args:
            directory_path: Path to the directory to scan
            
        Returns:
            List of security findings
        """
        findings = []
        
        try:
            # Run Checkov
            result = subprocess.run(
                ["checkov", "--directory", directory_path, "--output", "json", "--quiet"],
                capture_output=True,
                text=True,
                check=False  # Don't raise an exception on non-zero exit code
            )
            
            # Parse Checkov output
            try:
                output = json.loads(result.stdout)
                results = output.get("results", {})
                
                # Process failed checks
                for check_type, details in results.items():
                    if "failed_checks" in details:
                        for check in details["failed_checks"]:
                            # Get file path
                            file_path = check.get("file_path", "Unknown")
                            
                            # Make file path relative
                            if directory_path in file_path:
                                file_path = file_path.replace(directory_path, "").lstrip("/")
                            
                            # Get check details
                            check_id = check.get("check_id", "Unknown")
                            check_name = check.get("check_name", "Unknown")
                            line_number = check.get("file_line_range", [0])[0]
                            
                            # Map Checkov category to PCI requirement
                            category = check.get("check_class", "").lower()
                            pci_requirement = "6.3.3, 6.3.4"  # Default
                            
                            if "encryption" in category or "kms" in category:
                                pci_requirement = "3.4, 3.5, 4.1"
                            elif "network" in category or "security_group" in category:
                                pci_requirement = "1.2.1, 1.3.4"
                            elif "iam" in category or "permissions" in category:
                                pci_requirement = "7.1.1, 7.1.2"
                            elif "logging" in category or "monitoring" in category:
                                pci_requirement = "10.1, 10.2"
                            
                            # Create finding
                            finding = {
                                "type": f"IaC Security Issue: {check_name}",
                                "value": check.get("resource", "Unknown resource"),
                                "location": f"{file_path}:{line_number}",
                                "file_name": file_path,
                                "line_number": line_number,
                                "risk_level": self._map_checkov_severity(check.get("severity", "MEDIUM")),
                                "pci_requirement": pci_requirement,
                                "reason": check.get("guideline", "Infrastructure security misconfiguration"),
                                "remediation": "Fix the issue according to the guideline: " + check.get("guideline", "Follow security best practices")
                            }
                            
                            findings.append(finding)
            except json.JSONDecodeError:
                logger.warning("Failed to parse Checkov JSON output")
        except Exception as e:
            raise Exception(f"Failed to run Checkov: {str(e)}")
            
        return findings
    
    def _run_tfsec(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        Run TFSec for Terraform security scanning if available.
        
        Args:
            directory_path: Path to the directory to scan
            
        Returns:
            List of security findings
        """
        findings = []
        
        try:
            # Run TFSec
            result = subprocess.run(
                ["tfsec", directory_path, "--format", "json"],
                capture_output=True,
                text=True,
                check=False  # Don't raise an exception on non-zero exit code
            )
            
            # Parse TFSec output
            try:
                output = json.loads(result.stdout)
                results = output.get("results", [])
                
                for result in results:
                    # Get file path
                    file_path = result.get("location", {}).get("filename", "Unknown")
                    
                    # Make file path relative
                    if directory_path in file_path:
                        file_path = file_path.replace(directory_path, "").lstrip("/")
                    
                    # Get result details
                    rule_id = result.get("rule_id", "Unknown")
                    rule_description = result.get("rule_description", "Unknown")
                    line_number = result.get("location", {}).get("start_line", 0)
                    
                    # Get remediation
                    resolution = result.get("resolution", "Fix according to security best practices")
                    
                    # Map TFSec severity to risk level
                    severity = result.get("severity", "MEDIUM")
                    risk_level = "Medium"
                    if severity == "HIGH" or severity == "CRITICAL":
                        risk_level = "High"
                    elif severity == "LOW":
                        risk_level = "Low"
                    
                    # Map TFSec categories to PCI requirements
                    rule_provider = result.get("rule_provider", "").lower()
                    pci_requirement = "6.3.3, 6.3.4"  # Default
                    
                    if "encrypt" in rule_id.lower() or "kms" in rule_id.lower():
                        pci_requirement = "3.4, 3.5, 4.1"
                    elif "network" in rule_id.lower() or "firewall" in rule_id.lower() or "public" in rule_id.lower():
                        pci_requirement = "1.2.1, 1.3.4"
                    elif "iam" in rule_id.lower() or "permission" in rule_id.lower() or "privilege" in rule_id.lower():
                        pci_requirement = "7.1.1, 7.1.2"
                    elif "log" in rule_id.lower() or "monitor" in rule_id.lower():
                        pci_requirement = "10.1, 10.2"
                    
                    # Create finding
                    finding = {
                        "type": f"Terraform Security Issue: {rule_description}",
                        "value": result.get("description", "Security issue detected"),
                        "location": f"{file_path}:{line_number}",
                        "file_name": file_path,
                        "line_number": line_number,
                        "risk_level": risk_level,
                        "pci_requirement": pci_requirement,
                        "reason": result.get("impact", "Infrastructure security misconfiguration"),
                        "remediation": resolution
                    }
                    
                    findings.append(finding)
            except json.JSONDecodeError:
                logger.warning("Failed to parse TFSec JSON output")
        except Exception as e:
            raise Exception(f"Failed to run TFSec: {str(e)}")
            
        return findings
    
    def _map_checkov_severity(self, severity: str) -> str:
        """
        Map Checkov severity to risk level.
        
        Args:
            severity: Checkov severity string
            
        Returns:
            Risk level string
        """
        mapping = {
            "CRITICAL": "High",
            "HIGH": "High",
            "MEDIUM": "Medium",
            "LOW": "Low",
            "INFO": "Low"
        }
        
        return mapping.get(severity.upper(), "Medium")