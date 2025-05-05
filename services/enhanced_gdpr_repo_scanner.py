"""
Enhanced GDPR Repository Scanner

This module enhances the repository scanner with comprehensive GDPR article-specific detection capabilities.
It provides advanced pattern recognition for identifying compliance issues directly in code repositories.
"""

import os
import re
import json
import logging
import tempfile
import time
from typing import Dict, List, Any, Tuple, Optional, Set
import subprocess
from pathlib import Path

from services.gdpr_risk_categories import (
    RiskLevel, SeverityLevel, RemediationPriority,
    calculate_compliance_score, determine_compliance_status,
    normalize_risk_counts
)

# Configure logging
logger = logging.getLogger(__name__)

class GDPRArticleScanner:
    """
    A scanner that analyzes code repositories for GDPR compliance issues, with specific
    detection capabilities for each relevant GDPR article.
    """
    
    def __init__(self, repo_path: str):
        """
        Initialize the GDPR Article Scanner with a repository path.
        
        Args:
            repo_path: Path to the repository directory
        """
        self.repo_path = repo_path
        self.findings = []
        self.article_mappings = self._load_article_mappings()
        self.pattern_rules = self._load_pattern_rules()
        
    def _load_article_mappings(self) -> Dict[str, Dict[str, Any]]:
        """
        Load GDPR article mappings and their descriptions.
        
        Returns:
            Dictionary mapping article IDs to their descriptions and requirements
        """
        # This would typically load from a JSON file, but for demonstration we'll hardcode
        return {
            "article_5": {
                "title": "Principles Relating to Processing of Personal Data",
                "principles": [
                    "Lawfulness, Fairness, and Transparency",
                    "Purpose Limitation",
                    "Data Minimization",
                    "Accuracy",
                    "Storage Limitation",
                    "Integrity and Confidentiality",
                    "Accountability"
                ],
                "keywords": [
                    "personal data", "processing", "purpose", "retention", 
                    "accuracy", "security", "accountability"
                ]
            },
            "article_6": {
                "title": "Lawfulness of Processing",
                "principles": [
                    "Consent",
                    "Contract Performance",
                    "Legal Obligation",
                    "Vital Interests",
                    "Public Interest",
                    "Legitimate Interests"
                ],
                "keywords": [
                    "consent", "legal basis", "processing", "legitimate interest",
                    "contract", "legal obligation"
                ]
            },
            "article_7": {
                "title": "Conditions for Consent",
                "principles": [
                    "Demonstrable Consent",
                    "Clear Request",
                    "Right to Withdraw",
                    "Freely Given"
                ],
                "keywords": [
                    "consent", "withdraw", "opt-in", "explicit consent",
                    "checkbox", "agreement"
                ]
            },
            "article_12_15": {
                "title": "Transparency and Data Subject Rights",
                "principles": [
                    "Transparent Information",
                    "Access to Data",
                    "Processing Information",
                    "Recipients Disclosure"
                ],
                "keywords": [
                    "privacy policy", "information", "access request", 
                    "data subject", "transparent", "retrieve personal data"
                ]
            },
            "article_16_17": {
                "title": "Right to Rectification and Erasure",
                "principles": [
                    "Rectification of Inaccurate Data",
                    "Completion of Incomplete Data",
                    "Erasure (Right to be Forgotten)",
                    "Data Deletion"
                ],
                "keywords": [
                    "correction", "update", "delete", "remove", "erasure",
                    "forget", "deletion", "rectify"
                ]
            },
            "article_25": {
                "title": "Data Protection by Design and by Default",
                "principles": [
                    "Privacy by Design",
                    "Privacy by Default",
                    "Data Minimization",
                    "Pseudonymization"
                ],
                "keywords": [
                    "default settings", "privacy settings", "data minimization",
                    "pseudonymization", "privacy-enhancing", "design"
                ]
            },
            "article_30": {
                "title": "Records of Processing Activities",
                "principles": [
                    "Processing Records",
                    "Purpose Documentation",
                    "Categories Documentation",
                    "Recipient Documentation"
                ],
                "keywords": [
                    "processing record", "documentation", "processing activity",
                    "record keeping", "processing log"
                ]
            },
            "article_32": {
                "title": "Security of Processing",
                "principles": [
                    "Encryption",
                    "Confidentiality",
                    "Integrity",
                    "Availability",
                    "Resilience",
                    "Testing",
                    "Risk Assessment"
                ],
                "keywords": [
                    "encryption", "security", "secure", "hash", "protection",
                    "confidentiality", "integrity", "backup", "restore"
                ]
            },
            "article_44_49": {
                "title": "Transfers of Personal Data to Third Countries or International Organizations",
                "principles": [
                    "Adequacy Decision",
                    "Appropriate Safeguards",
                    "Binding Corporate Rules",
                    "Standard Contractual Clauses",
                    "Explicit Consent for Transfer"
                ],
                "keywords": [
                    "international transfer", "cross-border", "third country",
                    "transfer mechanism", "standard contractual clauses",
                    "adequacy", "safeguards"
                ]
            }
        }
    
    def _load_pattern_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Load pattern detection rules for each GDPR article.
        
        Returns:
            Dictionary mapping article IDs to lists of pattern rules
        """
        # This would typically load from rule files, but for demonstration we'll define inline
        return {
            "article_5": [
                # Lawfulness, Fairness, Transparency
                {
                    "pattern": r"api_key\s*=\s*['\"]([a-zA-Z0-9_\-\.]+)['\"]",
                    "message": "Hardcoded API key found. This could expose sensitive credentials.",
                    "severity": "high",
                    "principle": "Integrity and Confidentiality",
                    "remediation": "Store API keys in environment variables or a secure vault."
                },
                # Data Minimization
                {
                    "pattern": r"collect(UserData|PersonalInfo|UserInfo)",
                    "message": "Potential broad data collection function identified. Verify data minimization.",
                    "severity": "medium",
                    "principle": "Data Minimization",
                    "remediation": "Ensure only necessary data is collected for the specified purpose."
                },
                # Storage Limitation
                {
                    "pattern": r"(user|profile|customer|client|data)\.(create|save|store|insert)",
                    "message": "Data storage operation without visible retention period.",
                    "severity": "medium",
                    "principle": "Storage Limitation",
                    "remediation": "Implement data retention policies and automatic deletion mechanisms."
                },
            ],
            "article_6": [
                # Legal Basis
                {
                    "pattern": r"(process|handle|collect|store)(UserData|PersonalData|PersonalInfo)",
                    "message": "Data processing function without clear legal basis check.",
                    "severity": "high",
                    "principle": "Lawfulness of Processing",
                    "remediation": "Ensure a legal basis check (e.g., consent verification) before processing data."
                },
                # Consent Verification
                {
                    "pattern": r"(send|submit|process).*data(?!.*consent)",
                    "message": "Data submission without visible consent verification.",
                    "severity": "high",
                    "principle": "Consent",
                    "remediation": "Implement consent verification before data submission."
                },
            ],
            "article_7": [
                # Consent Management
                {
                    "pattern": r"(opt|check).*in.*=.*true",
                    "message": "Potential pre-checked consent option detected.",
                    "severity": "high",
                    "principle": "Freely Given Consent",
                    "remediation": "Ensure consent is opt-in by default (not pre-checked)."
                },
                # Consent Records
                {
                    "pattern": r"(user|customer|client)\.setConsent\(.*\)(?!.*timestamp)",
                    "message": "Consent setting without timestamp recording.",
                    "severity": "medium",
                    "principle": "Demonstrable Consent",
                    "remediation": "Record timestamps with consent to demonstrate when it was given."
                },
            ],
            "article_12_15": [
                # Information Provision
                {
                    "pattern": r"(privacy_policy|terms_of_service|data_policy)\.(display|show|present)",
                    "message": "Privacy information display function identified. Verify compliance with transparency requirements.",
                    "severity": "low",
                    "principle": "Transparent Information",
                    "remediation": "Ensure privacy information is clear, concise, and easily accessible."
                },
                # Data Subject Access
                {
                    "pattern": r"(export|download|retrieve)(UserData|PersonalData)",
                    "message": "Data access functionality identified. Verify completeness of provided data.",
                    "severity": "medium",
                    "principle": "Access to Data",
                    "remediation": "Ensure all user data is included in access request responses."
                },
            ],
            "article_16_17": [
                # Rectification
                {
                    "pattern": r"(update|modify|change)(UserData|PersonalData|Profile)",
                    "message": "Data modification function identified. Verify support for rectification rights.",
                    "severity": "medium",
                    "principle": "Rectification of Inaccurate Data",
                    "remediation": "Ensure users can easily correct all their personal data."
                },
                # Erasure
                {
                    "pattern": r"(delete|remove|destroy)(User|Account|Profile)(?!.*cascade)",
                    "message": "User deletion without clear cascade deletion of associated data.",
                    "severity": "high",
                    "principle": "Erasure (Right to be Forgotten)",
                    "remediation": "Implement cascade deletion to ensure all user data is removed."
                },
            ],
            "article_25": [
                # Privacy by Design
                {
                    "pattern": r"privacy_level\s*=\s*['\"]?(low|basic|standard)['\"]?",
                    "message": "Non-restrictive default privacy setting detected.",
                    "severity": "medium",
                    "principle": "Privacy by Default",
                    "remediation": "Set privacy settings to the most protective level by default."
                },
                # Data Minimization in Design
                {
                    "pattern": r"class\s+([A-Za-z0-9_]+User[A-Za-z0-9_]*|[A-Za-z0-9_]+Profile[A-Za-z0-9_]*)",
                    "message": "User/Profile class detected. Verify data minimization in design.",
                    "severity": "low",
                    "principle": "Data Minimization",
                    "remediation": "Review class attributes to ensure only necessary data is collected."
                },
            ],
            "article_30": [
                # Processing Records
                {
                    "pattern": r"(log|record|track)(Processing|DataAccess|DataUse)",
                    "message": "Data processing logging function identified. Verify completeness of records.",
                    "severity": "medium",
                    "principle": "Processing Records",
                    "remediation": "Ensure processing records include all required information (purpose, categories, etc.)."
                },
                # Documentation
                {
                    "pattern": r"\/\*\s*Processing purpose:.*\*\/|#\s*Processing purpose:.*|\/\/\s*Processing purpose:.*",
                    "message": "Processing purpose documentation identified. Verify completeness.",
                    "severity": "low",
                    "principle": "Purpose Documentation",
                    "remediation": "Ensure all processing activities have documented purposes."
                },
            ],
            "article_32": [
                # Encryption
                {
                    "pattern": r"(password|secret|key|token).*=.*((?!encrypt|hash|bcrypt|scrypt|argon2).)*$",
                    "message": "Potential storage of sensitive data without encryption.",
                    "severity": "high",
                    "principle": "Encryption",
                    "remediation": "Implement encryption for all sensitive data storage."
                },
                # Secure Communication
                {
                    "pattern": r"http://(?!localhost)",
                    "message": "Non-secure HTTP URL detected (not using HTTPS).",
                    "severity": "high",
                    "principle": "Confidentiality",
                    "remediation": "Use HTTPS for all external communications."
                },
                # Authentication
                {
                    "pattern": r"(authenticate|login|signin).*\((?!.*password).*\)",
                    "message": "Authentication function without password parameter.",
                    "severity": "high",
                    "principle": "Confidentiality",
                    "remediation": "Ensure proper authentication mechanisms are in place."
                },
            ],
            "article_44_49": [
                # Cross-border Transfers
                {
                    "pattern": r"(api\.|endpoint\.|url\.).*(\.com|\.io|\.net|\.org)",
                    "message": "Potential external API call that may transfer data internationally.",
                    "severity": "medium",
                    "principle": "International Transfers",
                    "remediation": "Ensure appropriate safeguards for international data transfers."
                },
                # Transfer Safeguards
                {
                    "pattern": r"(transfer|send|transmit)(Data|PersonalData).*To.*(External|ThirdParty|Partner)",
                    "message": "Data transfer to external party without visible safeguards.",
                    "severity": "high",
                    "principle": "Appropriate Safeguards",
                    "remediation": "Implement and document appropriate safeguards for data transfers."
                },
            ],
        }
    
    def scan_repository(self) -> List[Dict[str, Any]]:
        """
        Scan the repository for GDPR compliance issues.
        
        Returns:
            List of findings with GDPR article mappings
        """
        logger.info(f"Starting enhanced GDPR scan on repository: {self.repo_path}")
        
        # Execute pattern-based scanning for each GDPR article
        for article_id, rules in self.pattern_rules.items():
            article_findings = self._scan_patterns_for_article(article_id, rules)
            self.findings.extend(article_findings)
        
        # Perform specialized analysis
        self._analyze_data_protection_by_design()
        self._analyze_consent_flows()
        self._analyze_data_retention()
        self._detect_special_category_data()
        self._analyze_cross_border_transfers()
        
        logger.info(f"GDPR scan completed. Found {len(self.findings)} potential issues.")
        return self.findings
    
    def _scan_patterns_for_article(self, article_id: str, rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Scan repository for patterns related to a specific GDPR article.
        
        Args:
            article_id: ID of the GDPR article
            rules: List of pattern rules for the article
            
        Returns:
            List of findings related to the article
        """
        article_findings = []
        
        # Get all relevant files (exclude binaries, images, etc.)
        code_files = self._get_code_files()
        
        for file_path in code_files:
            try:
                # Read file content
                with open(os.path.join(self.repo_path, file_path), 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Apply each pattern rule
                for rule in rules:
                    pattern = rule["pattern"]
                    matches = re.finditer(pattern, content)
                    
                    for match in matches:
                        # Create a finding
                        finding = {
                            "article_id": article_id,
                            "article_title": self.article_mappings[article_id]["title"],
                            "principle": rule["principle"],
                            "pattern": pattern,
                            "message": rule["message"],
                            "severity": rule["severity"],
                            "file_path": file_path,
                            "line_number": content[:match.start()].count('\n') + 1,
                            "snippet": self._get_context_snippet(content, match.start()),
                            "remediation": rule["remediation"]
                        }
                        
                        article_findings.append(finding)
            
            except Exception as e:
                logger.warning(f"Error scanning file {file_path}: {str(e)}")
        
        return article_findings
    
    def _get_code_files(self) -> List[str]:
        """
        Get all code files in the repository.
        
        Returns:
            List of file paths relative to repository root
        """
        code_files = []
        exclude_dirs = ['.git', 'node_modules', '__pycache__', 'dist', 'build', 'venv']
        exclude_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.pdf', '.zip', '.tar', '.gz', '.exe', '.bin']
        
        for root, dirs, files in os.walk(self.repo_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                # Skip excluded file types
                if any(file.endswith(ext) for ext in exclude_extensions):
                    continue
                
                # Get path relative to repository root
                rel_path = os.path.relpath(os.path.join(root, file), self.repo_path)
                code_files.append(rel_path)
        
        return code_files
    
    def _get_context_snippet(self, content: str, match_pos: int, context_lines: int = 2) -> str:
        """
        Get a snippet of code around the match position with context lines.
        
        Args:
            content: File content
            match_pos: Position of the match in the content
            context_lines: Number of context lines before and after the match
            
        Returns:
            Code snippet with context
        """
        # Find line start and end positions
        line_start = content.rfind('\n', 0, match_pos) + 1
        if line_start == 0:  # If no newline found before match
            line_start = 0
            
        line_end = content.find('\n', match_pos)
        if line_end == -1:  # If no newline found after match
            line_end = len(content)
            
        # Extract the line with the match
        match_line = content[line_start:line_end]
        
        # Find context lines before
        context_before = []
        pos = line_start
        for _ in range(context_lines):
            if pos <= 0:
                break
                
            prev_line_end = pos - 1
            prev_line_start = content.rfind('\n', 0, prev_line_end) + 1
            if prev_line_start == 0:  # If no newline found
                prev_line_start = 0
                
            context_before.insert(0, content[prev_line_start:prev_line_end])
            pos = prev_line_start
        
        # Find context lines after
        context_after = []
        pos = line_end
        for _ in range(context_lines):
            if pos >= len(content):
                break
                
            next_line_start = pos + 1
            next_line_end = content.find('\n', next_line_start)
            if next_line_end == -1:  # If no newline found
                next_line_end = len(content)
                
            context_after.append(content[next_line_start:next_line_end])
            pos = next_line_end
        
        # Combine context and match line
        snippet = "\n".join(context_before + [match_line] + context_after)
        return snippet
    
    def _analyze_data_protection_by_design(self):
        """
        Analyze the repository for data protection by design issues.
        This includes checking for default privacy settings and data minimization.
        """
        # Implementation would include:
        # 1. Analysis of configuration files for default settings
        # 2. Examination of data models for minimization
        # 3. Check for privacy enhancing technologies
        pass
    
    def _analyze_consent_flows(self):
        """
        Analyze the repository for consent flow issues.
        This traces user journey from data collection to processing.
        """
        # Implementation would include:
        # 1. Identification of data collection points
        # 2. Tracking of consent collection and verification
        # 3. Analysis of consent storage and withdrawal mechanisms
        pass
    
    def _analyze_data_retention(self):
        """
        Analyze the repository for data retention issues.
        This looks for retention policies and deletion mechanisms.
        """
        # Implementation would include:
        # 1. Identification of data storage mechanisms
        # 2. Check for TTL (time to live) fields
        # 3. Search for data archiving and deletion functionality
        pass
    
    def _detect_special_category_data(self):
        """
        Detect processing of special category data.
        This identifies fields that might contain sensitive data.
        """
        # Implementation would include:
        # 1. Search for indicators of health, biometric, genetic data
        # 2. Identification of fields for race, ethnicity, political opinions, etc.
        # 3. Check for appropriate safeguards for such data
        pass
    
    def _analyze_cross_border_transfers(self):
        """
        Analyze the repository for cross-border transfer issues.
        This detects data flows to external services or international recipients.
        """
        # Implementation would include:
        # 1. Identification of API calls to external services
        # 2. Detection of cloud storage configuration
        # 3. Analysis of data transfer mechanisms
        pass

def scan_repository_for_gdpr_compliance(repo_path: str) -> Dict[str, Any]:
    """
    Scan a repository for GDPR compliance issues using the enhanced scanner.
    
    Args:
        repo_path: Path to the repository directory
        
    Returns:
        Dictionary with scan results including findings and statistics
    """
    scanner = GDPRArticleScanner(repo_path)
    findings = scanner.scan_repository()
    
    # Group findings by GDPR article
    findings_by_article = {}
    for finding in findings:
        article_id = finding["article_id"]
        if article_id not in findings_by_article:
            findings_by_article[article_id] = []
        findings_by_article[article_id].append(finding)
    
    # Count findings by severity
    severity_counts = {"high": 0, "medium": 0, "low": 0}
    for finding in findings:
        severity = finding["severity"]
        if severity in severity_counts:
            severity_counts[severity] += 1
    
    # Calculate compliance score (basic algorithm - would be enhanced in production)
    # High issues count 5 points, medium 3 points, low 1 point
    # Maximum score is 100
    issue_points = severity_counts["high"] * 5 + severity_counts["medium"] * 3 + severity_counts["low"] * 1
    max_points = 100
    compliance_score = max(0, 100 - min(issue_points, max_points))
    
    # Prepare the results
    results = {
        "findings": findings,
        "findings_by_article": findings_by_article,
        "severity_counts": severity_counts,
        "compliance_score": compliance_score,
        "total_findings": len(findings),
        "scanned_files": len(scanner._get_code_files())
    }
    
    return results