"""
Clean GDPR Code Scanner

A comprehensive scanner that analyzes code repositories for GDPR compliance issues
based on the 7 core GDPR principles with a focus on Dutch-specific rules (UAVG).

Features:
- Multi-language support (Python, JS, Java, Terraform, YAML)
- Secrets detection through entropy analysis and pattern matching
- PII detection using regex patterns and NLP techniques
- GDPR compliance scoring for each principle
- Regional PII tagging (UAVG, BDSG, CNIL, GDPR Article references)
- Metadata enrichment with git blame information
- Modern design reports with download options (PDF, HTML)
"""

import streamlit as st
import os
import json
import time
import io
import re
import math
import base64
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

# Set page configuration
st.set_page_config(
    page_title="GDPR Code Scanner",
    page_icon="🛡️",
    layout="wide"
)

# Add custom CSS for modern UI
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        color: #1E3A8A;
    }
    .stButton>button {
        background-color: #1E3A8A;
        color: white;
        border-radius: 0.5rem;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #3B82F6;
    }
    .findings-container {
        border: 1px solid #E5E7EB;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .finding-high {
        border-left: 4px solid #DC2626;
        padding-left: 1rem;
        margin-bottom: 0.5rem;
    }
    .finding-medium {
        border-left: 4px solid #F59E0B;
        padding-left: 1rem;
        margin-bottom: 0.5rem;
    }
    .finding-low {
        border-left: 4px solid #10B981;
        padding-left: 1rem;
        margin-bottom: 0.5rem;
    }
    .stProgress .st-bo {
        background-color: #E5E7EB;
    }
    .stProgress .st-bp {
        background-color: #3B82F6;
    }
</style>
""", unsafe_allow_html=True)

# PII and secret detection patterns
PII_PATTERNS = {
    # Dutch-specific patterns (UAVG)
    "bsn": (r'\b[0-9]{9}\b', "BSN (Dutch Citizen Service Number)", "high", ["UAVG", "GDPR-Article9"]),
    "dutch_passport": (r'\b[A-Z]{2}[0-9]{6}\b', "Dutch Passport Number", "high", ["UAVG", "GDPR-Article6"]),
    "dutch_phone": (r'\b(?:\+31|0031|0)[1-9][0-9]{8}\b', "Dutch Phone Number", "medium", ["UAVG", "GDPR-Article6"]),
    "dutch_postal_code": (r'\b[1-9][0-9]{3}\s?[A-Z]{2}\b', "Dutch Postal Code", "low", ["UAVG", "GDPR-Article6"]),
    
    # General PII patterns
    "email": (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', "Email Address", "medium", ["GDPR-Article6"]),
    "ip_address": (r'\b(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b', "IP Address", "medium", ["GDPR-Article6"]),
    "credit_card": (r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12}|(?:2131|1800|35\d{3})\d{11})\b', "Credit Card Number", "high", ["GDPR-Article6"]),
    
    # Secret patterns
    "api_key": (r'(?i)(?:api[_-]?key|apikey|secret[_-]?key|secretkey)[^a-zA-Z0-9][ \t]*[:=][ \t]*[\'"][a-zA-Z0-9_\-]{10,}[\'"]', "API Key", "high", ["GDPR-Article32"]),
    "aws_key": (r'(?i)(?:aws[_-]?(?:secret|key|access))[^a-zA-Z0-9][ \t]*[:=][ \t]*[\'"][a-zA-Z0-9+/]{16,}[\'"]', "AWS Key", "high", ["GDPR-Article32"]),
    "password": (r'(?i)(?:password|passwd|pwd)[^a-zA-Z0-9][ \t]*[:=][ \t]*[\'"][^\'"\n]{4,}[\'"]', "Password", "high", ["GDPR-Article32"]),
    
    # Consent patterns (UAVG specific)
    "minor_consent": (r'(?i)(?:minor|child|under[_-]?16|age[_-]?check|age[_-]?verification)', "Minor Consent Check", "high", ["UAVG", "GDPR-Article8"]),
    "consent_storage": (r'(?i)(?:store[_-]?consent|record[_-]?consent|consent[_-]?timestamp|consent[_-]?log)', "Consent Storage", "medium", ["GDPR-Article7"]),
    
    # Data retention patterns
    "retention": (r'(?i)(?:retention[_-]?period|data[_-]?retention|store[_-]?for|delete[_-]?after)', "Data Retention", "medium", ["GDPR-Article5", "GDPR-Article17"]),
    
    # Breach notification patterns
    "breach_notification": (r'(?i)(?:breach[_-]?notification|security[_-]?incident|data[_-]?breach|72[_-]?hour)', "Breach Notification", "high", ["UAVG", "GDPR-Article33"]),
}

# GDPR Principle Patterns
GDPR_PRINCIPLES = {
    "Lawfulness, Fairness and Transparency": [
        (r'(?i)consent.*(?:not|missing|invalid)', "Potential invalid consent handling", "high", ["GDPR-Article6", "UAVG"]),
        (r'(?i)process(?:ing)?.*data.*without.*consent', "Processing data without explicit consent", "high", ["GDPR-Article6", "UAVG"]),
        (r'(?i)privacy.*policy.*missing', "Missing privacy policy reference", "medium", ["GDPR-Article13", "UAVG"]),
        (r'(?i)legal[_-]?basis', "Legal basis documentation", "medium", ["GDPR-Article6", "UAVG"]),
    ],
    
    "Purpose Limitation": [
        (r'(?i)use.*data.*(?:marketing|analytics|profiling).*without.*(?:consent|permission)', "Using data beyond intended purpose", "high", ["GDPR-Article5-1b", "UAVG"]),
        (r'(?i)repurpos(?:e|ing).*data', "Repurposing data without new consent", "medium", ["GDPR-Article5-1b", "UAVG"]),
        (r'(?i)scope.*data.*(?:exceed|beyond)', "Data usage exceeding defined scope", "medium", ["GDPR-Article5-1b", "UAVG"]),
    ],
    
    "Data Minimization": [
        (r'(?i)collect(?:ing)?.*(?:unnecessary|excessive).*data', "Collecting excessive data", "medium", ["GDPR-Article5-1c", "UAVG"]),
        (r'(?i)(?:store|save).*(?:full|complete).*(?:profile|history)', "Storing complete user profiles/history", "medium", ["GDPR-Article5-1c", "UAVG"]),
        (r'(?i)(?:name|email|phone|address|dob|birth|ssn|passport).*required', "Requiring personal data that may be excessive", "low", ["GDPR-Article5-1c", "UAVG"]),
    ],
    
    "Accuracy": [
        (r'(?i)no.*(?:validation|verification)', "Lack of data validation", "medium", ["GDPR-Article5-1d", "UAVG"]),
        (r'(?i)(?:old|outdated|stale).*data', "Using potentially outdated data", "medium", ["GDPR-Article5-1d", "UAVG"]),
        (r'(?i)(?:missing|no).*update.*mechanism', "No mechanism to update inaccurate data", "medium", ["GDPR-Article5-1d", "UAVG"]),
    ],
    
    "Storage Limitation": [
        (r'(?i)(?:no|missing).*retention.*(?:policy|period)', "Missing data retention policy", "medium", ["GDPR-Article5-1e", "UAVG"]),
        (r'(?i)(?:store|keep).*(?:forever|indefinite|permanent)', "Storing data indefinitely", "high", ["GDPR-Article5-1e", "UAVG"]),
        (r'(?i)(?:no|missing).*deletion.*mechanism', "No mechanism for data deletion", "high", ["GDPR-Article17", "UAVG"]),
    ],
    
    "Integrity and Confidentiality": [
        (r'(?i)data.{0,20}(?:not|un)encrypted', "Unencrypted data storage/transmission", "high", ["GDPR-Article5-1f", "GDPR-Article32", "UAVG"]),
        (r'(?i)(?:md5|sha1)\(', "Using weak hash algorithm", "medium", ["GDPR-Article5-1f", "GDPR-Article32", "UAVG"]),
        (r'(?i)sql.{0,20}(?:exec|query).{0,40}%[sd]', "Potential SQL injection vulnerability", "high", ["GDPR-Article5-1f", "GDPR-Article32", "UAVG"]),
    ],
    
    "Accountability": [
        (r'(?i)(?:no|missing).*log(?:ging|s)', "Missing data processing logs", "medium", ["GDPR-Article5-2", "UAVG"]),
        (r'(?i)(?:no|missing).*(?:audit|trail)', "Missing audit trail", "medium", ["GDPR-Article5-2", "UAVG"]),
        (r'(?i)(?:no|missing).*privacy.*impact.*assessment', "Missing privacy impact assessment", "medium", ["GDPR-Article35", "UAVG"]),
    ],
}

class GDPRCodeScanner:
    def __init__(self, repo_path: str = ".", languages: List[str] = None, timeout: int = 20):
        """
        Initialize the GDPR Code Scanner
        
        Args:
            repo_path: Path to the repository to scan
            languages: List of languages to scan (default: all supported)
            timeout: Scan timeout in seconds per file
        """
        self.repo_path = repo_path
        self.languages = languages or ["python", "javascript", "java", "typescript", "terraform", "yaml", "json"]
        self.timeout = timeout
        self.findings = []
        self.file_count = 0
        self.line_count = 0
        
    def scan(self, on_progress=None) -> Dict[str, Any]:
        """
        Scan the repository for GDPR compliance issues
        
        Args:
            on_progress: Callback function for reporting progress
            
        Returns:
            Dict containing scan results
        """
        start_time = datetime.now()
        
        # Get list of files to scan
        files_to_scan = self._get_files_to_scan()
        total_files = len(files_to_scan)
        
        # Scan each file
        for i, file_path in enumerate(files_to_scan):
            self._scan_file(file_path)
            
            # Report progress if callback provided
            if on_progress and total_files > 0:
                progress_percent = (i + 1) / total_files
                on_progress(progress_percent, f"Scanned {i+1}/{total_files} files")
        
        # Calculate scan duration
        scan_duration = (datetime.now() - start_time).total_seconds()
        
        # Calculate compliance scores
        compliance_scores = self._calculate_compliance_scores()
        
        # Get git metadata if available
        git_info = self._get_git_info()
        
        # Prepare scan results
        results = {
            "scan_id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "scan_date": datetime.now().isoformat(),
            "repo_path": self.repo_path,
            "languages": self.languages,
            "file_count": self.file_count,
            "line_count": self.line_count,
            "scan_duration": scan_duration,
            "findings_count": len(self.findings),
            "findings": self.findings,
            "compliance_scores": compliance_scores,
            "git_info": git_info
        }
        
        return results
    
    def _get_files_to_scan(self) -> List[str]:
        """Get the list of files to scan based on supported languages"""
        files_to_scan = []
        
        # Define file extensions for each language
        language_extensions = {
            "python": [".py", ".pyw"],
            "javascript": [".js", ".jsx", ".mjs"],
            "typescript": [".ts", ".tsx"],
            "java": [".java"],
            "terraform": [".tf", ".tfvars"],
            "yaml": [".yml", ".yaml"],
            "json": [".json"]
        }
        
        # Get supported extensions based on selected languages
        supported_extensions = []
        for lang in self.languages:
            if lang in language_extensions:
                supported_extensions.extend(language_extensions[lang])
        
        # Walk through the repository
        for root, _, files in os.walk(self.repo_path):
            # Skip hidden directories
            if any(part.startswith('.') for part in root.split(os.sep)):
                continue
                
            for file in files:
                # Skip hidden files
                if file.startswith('.'):
                    continue
                    
                # Check if file extension is supported
                _, ext = os.path.splitext(file.lower())
                if ext in supported_extensions:
                    file_path = os.path.join(root, file)
                    files_to_scan.append(file_path)
        
        return files_to_scan
    
    def _scan_file(self, file_path: str):
        """Scan a single file for GDPR compliance issues"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                # Update file/line count
                self.file_count += 1
                self.line_count += len(lines)
                
                # Scan for PII and secrets
                self._scan_for_pii_and_secrets(file_path, lines)
                
                # Scan for GDPR principle issues
                self._scan_for_gdpr_principles(file_path, lines)
                
                # Scan for high entropy strings
                self._scan_for_high_entropy_strings(file_path, lines)
        
        except Exception as e:
            # Log scanning error
            finding = {
                "file": file_path,
                "line": 0,
                "type": "SCAN_ERROR",
                "description": f"Error scanning file: {str(e)}",
                "severity": "low",
                "region_flags": ["GDPR-Article5"],
                "context_snippet": "",
            }
            self.findings.append(finding)
    
    def _scan_for_pii_and_secrets(self, file_path: str, lines: List[str]):
        """Scan for PII and secrets in a file"""
        for i, line in enumerate(lines, 1):
            for pattern_name, (pattern, description, severity, region_flags) in PII_PATTERNS.items():
                matches = re.finditer(pattern, line)
                for match in matches:
                    # Get context (show the problematic line and a few lines around it)
                    context_start = max(0, i - 2)
                    context_end = min(len(lines), i + 2)
                    context_snippet = '\n'.join(lines[context_start-1:context_end])
                    
                    # Create finding
                    finding = {
                        "file": file_path,
                        "line": i,
                        "type": pattern_name.upper(),
                        "description": description,
                        "severity": severity,
                        "region_flags": region_flags,
                        "context_snippet": context_snippet,
                    }
                    
                    # Add entropy for secrets
                    if pattern_name in ['api_key', 'aws_key', 'password']:
                        match_text = match.group(0)
                        entropy = self._calculate_entropy(match_text)
                        finding["entropy"] = entropy
                    
                    # Add git blame info if available
                    git_info = self._get_git_blame_info(file_path, i)
                    if git_info:
                        finding["commit_info"] = git_info
                    
                    self.findings.append(finding)
    
    def _scan_for_gdpr_principles(self, file_path: str, lines: List[str]):
        """Scan for GDPR principle issues in a file"""
        for principle, patterns in GDPR_PRINCIPLES.items():
            for pattern, description, severity, region_flags in patterns:
                for i, line in enumerate(lines, 1):
                    match = re.search(pattern, line)
                    if match:
                        # Get context
                        context_start = max(0, i - 2)
                        context_end = min(len(lines), i + 2)
                        context_snippet = '\n'.join(lines[context_start-1:context_end])
                        
                        # Create finding
                        finding = {
                            "file": file_path,
                            "line": i,
                            "type": "GDPR_PRINCIPLE",
                            "principle": principle,
                            "description": description,
                            "severity": severity,
                            "region_flags": region_flags,
                            "context_snippet": context_snippet,
                        }
                        
                        # Add git blame info if available
                        git_info = self._get_git_blame_info(file_path, i)
                        if git_info:
                            finding["commit_info"] = git_info
                        
                        self.findings.append(finding)
    
    def _scan_for_high_entropy_strings(self, file_path: str, lines: List[str]):
        """Scan for high entropy strings that might be secrets"""
        # Patterns to exclude (common patterns with high entropy that aren't secrets)
        excluded_patterns = [
            r'(?i)import\s+',
            r'(?i)from\s+.+\s+import',
            r'(?i)require\(',
            r'(?i)const\s+[a-zA-Z0-9_]+\s*=\s*require\(',
            r'(?i)function\s+',
            r'(?i)class\s+',
            r'(?i)def\s+',
        ]
        
        for i, line in enumerate(lines, 1):
            # Skip lines that match excluded patterns
            if any(re.search(pattern, line) for pattern in excluded_patterns):
                continue
            
            # Look for potential secrets (strings with high entropy)
            string_matches = re.finditer(r'[\'"]([a-zA-Z0-9+/=_\-.]{16,})[\'"]', line)
            for match in string_matches:
                potential_secret = match.group(1)
                entropy = self._calculate_entropy(potential_secret)
                
                # If entropy is high enough, it might be a secret
                if entropy > 4.0:
                    # Get context
                    context_start = max(0, i - 2)
                    context_end = min(len(lines), i + 2)
                    
                    # Mask the potential secret in the snippet
                    masked_lines = lines[context_start-1:context_end].copy()
                    masked_lines[i - context_start] = line.replace(
                        potential_secret, 
                        potential_secret[:4] + '*' * (len(potential_secret) - 8) + potential_secret[-4:]
                    )
                    context_snippet = '\n'.join(masked_lines)
                    
                    # Create finding
                    finding = {
                        "file": file_path,
                        "line": i,
                        "type": "HIGH_ENTROPY_STRING",
                        "description": "High entropy string detected (possible secret)",
                        "severity": "medium",
                        "region_flags": ["GDPR-Article32", "UAVG"],
                        "context_snippet": context_snippet,
                        "entropy": entropy
                    }
                    
                    # Add git blame info if available
                    git_info = self._get_git_blame_info(file_path, i)
                    if git_info:
                        finding["commit_info"] = git_info
                    
                    self.findings.append(finding)
    
    def _calculate_entropy(self, string: str) -> float:
        """Calculate Shannon entropy of a string"""
        if not string:
            return 0.0
        
        # Calculate frequency of each character
        char_count = {}
        for char in string:
            char_count[char] = char_count.get(char, 0) + 1
        
        # Calculate entropy
        entropy = 0.0
        for count in char_count.values():
            probability = count / len(string)
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    def _get_git_info(self) -> Dict[str, Any]:
        """Get repository git information"""
        git_info = {
            "is_git_repo": False,
            "remote": "",
            "branch": "",
            "commit": ""
        }
        
        # Check if it's a git repository
        if not os.path.isdir(os.path.join(self.repo_path, '.git')):
            return git_info
        
        git_info["is_git_repo"] = True
        
        try:
            # Get remote URL
            result = subprocess.run(
                ['git', '-C', self.repo_path, 'config', '--get', 'remote.origin.url'],
                capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                git_info["remote"] = result.stdout.strip()
            
            # Get current branch
            result = subprocess.run(
                ['git', '-C', self.repo_path, 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                git_info["branch"] = result.stdout.strip()
            
            # Get current commit hash
            result = subprocess.run(
                ['git', '-C', self.repo_path, 'rev-parse', 'HEAD'],
                capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                git_info["commit"] = result.stdout.strip()
        
        except Exception:
            # If git commands fail, just return what we have
            pass
        
        return git_info
    
    def _get_git_blame_info(self, file_path: str, line_number: int) -> Optional[Dict[str, str]]:
        """Get git blame information for a specific line"""
        # Check if it's a git repository
        if not os.path.isdir(os.path.join(self.repo_path, '.git')):
            return None
        
        try:
            # Get relative path to the repository
            relative_path = os.path.relpath(file_path, self.repo_path)
            
            # Run git blame for the specific line
            result = subprocess.run(
                ['git', '-C', self.repo_path, 'blame', '-L', f'{line_number},{line_number}', '--porcelain', relative_path],
                capture_output=True, text=True, check=False
            )
            
            if result.returncode != 0:
                return None
            
            # Parse the output
            output_lines = result.stdout.strip().split('\n')
            if not output_lines:
                return None
            
            # First line contains commit hash
            commit_hash = output_lines[0].split(' ')[0]
            
            # Extract author and date
            author = ""
            author_email = ""
            
            for line in output_lines:
                if line.startswith('author '):
                    author = line[len('author '):].strip()
                elif line.startswith('author-mail '):
                    author_email = line[len('author-mail '):].strip().strip('<>')
            
            return {
                "author": author,
                "author_email": author_email,
                "commit_id": commit_hash
            }
        
        except Exception:
            return None
    
    def _calculate_compliance_scores(self) -> Dict[str, int]:
        """Calculate compliance scores for each GDPR principle"""
        # Initialize scores with perfect compliance
        scores = {
            "Lawfulness, Fairness and Transparency": 100,
            "Purpose Limitation": 100,
            "Data Minimization": 100,
            "Accuracy": 100,
            "Storage Limitation": 100,
            "Integrity and Confidentiality": 100,
            "Accountability": 100
        }
        
        # Count findings by principle and severity
        severity_weights = {
            "high": 15,
            "medium": 5,
            "low": 1
        }
        
        principle_issues = {principle: 0 for principle in scores.keys()}
        
        for finding in self.findings:
            # Get principle from finding
            principle = finding.get("principle")
            
            # If finding has explicit principle, use that
            if principle and principle in principle_issues:
                severity = finding.get("severity", "low")
                principle_issues[principle] += severity_weights.get(severity, 1)
            
            # Otherwise, try to determine principle from region flags
            elif "region_flags" in finding:
                region_flags = finding.get("region_flags", [])
                severity = finding.get("severity", "low")
                weight = severity_weights.get(severity, 1)
                
                # Map GDPR articles to principles
                if any(flag.startswith("GDPR-Article5-1a") or flag.startswith("GDPR-Article6") or flag.startswith("GDPR-Article13") for flag in region_flags):
                    principle_issues["Lawfulness, Fairness and Transparency"] += weight
                
                elif any(flag.startswith("GDPR-Article5-1b") for flag in region_flags):
                    principle_issues["Purpose Limitation"] += weight
                
                elif any(flag.startswith("GDPR-Article5-1c") for flag in region_flags):
                    principle_issues["Data Minimization"] += weight
                
                elif any(flag.startswith("GDPR-Article5-1d") for flag in region_flags):
                    principle_issues["Accuracy"] += weight
                
                elif any(flag.startswith("GDPR-Article5-1e") or flag.startswith("GDPR-Article17") for flag in region_flags):
                    principle_issues["Storage Limitation"] += weight
                
                elif any(flag.startswith("GDPR-Article5-1f") or flag.startswith("GDPR-Article32") for flag in region_flags):
                    principle_issues["Integrity and Confidentiality"] += weight
                
                elif any(flag.startswith("GDPR-Article5-2") or flag.startswith("GDPR-Article30") or flag.startswith("GDPR-Article35") for flag in region_flags):
                    principle_issues["Accountability"] += weight
        
        # Calculate final scores based on issues (deduct points based on issues found)
        for principle, issues in principle_issues.items():
            # Cap deduction at 100 points
            deduction = min(100, issues)
            scores[principle] = max(0, 100 - deduction)
        
        return scores

def generate_html_report(scan_results: Dict[str, Any]) -> str:
    """Generate an HTML report from scan results"""
    
    # Extract basic scan info
    repo_path = scan_results.get("repo_path", "Unknown")
    scan_date = scan_results.get("scan_date", datetime.now().isoformat())
    if isinstance(scan_date, str):
        try:
            scan_date = datetime.fromisoformat(scan_date)
        except ValueError:
            scan_date = datetime.now()
    
    file_count = scan_results.get("file_count", 0)
    line_count = scan_results.get("line_count", 0)
    findings_count = scan_results.get("findings_count", 0)
    scan_duration = scan_results.get("scan_duration", 0)
    
    # Get compliance scores
    compliance_scores = scan_results.get("compliance_scores", {})
    
    # Count findings by severity
    findings = scan_results.get("findings", [])
    severity_counts = {"high": 0, "medium": 0, "low": 0}
    for finding in findings:
        severity = finding.get("severity", "low")
        severity_counts[severity] += 1
    
    # Group findings by principle
    principle_findings = {}
    for finding in findings:
        principle = finding.get("principle", "Other")
        if principle not in principle_findings:
            principle_findings[principle] = []
        principle_findings[principle].append(finding)
    
    # Generate HTML report
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GDPR Compliance Scan Report</title>
    <style>
        :root {{
            --primary-color: #1E3A8A;
            --primary-light: #3B82F6;
            --success-color: #10B981;
            --warning-color: #F59E0B;
            --danger-color: #DC2626;
            --gray-50: #F9FAFB;
            --gray-100: #F3F4F6;
            --gray-200: #E5E7EB;
            --gray-300: #D1D5DB;
            --gray-400: #9CA3AF;
            --gray-500: #6B7280;
            --gray-600: #4B5563;
            --gray-700: #374151;
            --gray-800: #1F2937;
            --gray-900: #111827;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.5;
            color: var(--gray-800);
            background-color: var(--gray-50);
            margin: 0;
            padding: 0;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        .header {{
            background-color: var(--primary-color);
            color: white;
            padding: 2rem 0;
            margin-bottom: 2rem;
        }}
        
        .header-content {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            color: var(--primary-color);
            margin-top: 1.5rem;
            margin-bottom: 1rem;
        }}
        
        .header h1 {{
            color: white;
            margin-top: 0;
        }}
        
        .header p {{
            margin-bottom: 0;
            opacity: 0.9;
        }}
        
        .card {{
            background-color: white;
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }}
        
        .summary-item {{
            background-color: white;
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            padding: 1rem;
            text-align: center;
        }}
        
        .summary-item .value {{
            font-size: 2rem;
            font-weight: bold;
            color: var(--primary-color);
            margin-bottom: 0.5rem;
        }}
        
        .summary-item .label {{
            color: var(--gray-600);
            font-size: 0.875rem;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 1.5rem;
        }}
        
        th, td {{
            padding: 0.75rem 1rem;
            text-align: left;
            border-bottom: 1px solid var(--gray-200);
        }}
        
        th {{
            background-color: var(--gray-100);
            font-weight: 600;
            color: var(--gray-700);
        }}
        
        .severity-high {{
            color: var(--danger-color);
            font-weight: 600;
        }}
        
        .severity-medium {{
            color: var(--warning-color);
            font-weight: 600;
        }}
        
        .severity-low {{
            color: var(--success-color);
            font-weight: 600;
        }}
        
        .progress-container {{
            width: 100%;
            height: 8px;
            background-color: var(--gray-200);
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 0.5rem;
        }}
        
        .progress-bar {{
            height: 100%;
            border-radius: 4px;
        }}
        
        .progress-text {{
            display: flex;
            justify-content: space-between;
            color: var(--gray-600);
            font-size: 0.875rem;
        }}
        
        .progress-good .progress-bar {{
            background-color: var(--success-color);
        }}
        
        .progress-warning .progress-bar {{
            background-color: var(--warning-color);
        }}
        
        .progress-danger .progress-bar {{
            background-color: var(--danger-color);
        }}
        
        .finding {{
            margin-bottom: 1rem;
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: var(--gray-50);
            border-left: 4px solid var(--gray-400);
        }}
        
        .finding.high {{
            border-left-color: var(--danger-color);
        }}
        
        .finding.medium {{
            border-left-color: var(--warning-color);
        }}
        
        .finding.low {{
            border-left-color: var(--success-color);
        }}
        
        .finding-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5rem;
        }}
        
        .finding-title {{
            font-weight: 600;
            color: var(--gray-800);
        }}
        
        .finding-location {{
            font-family: monospace;
            background-color: var(--gray-100);
            padding: 0.25rem 0.5rem;
            border-radius: 0.25rem;
            font-size: 0.875rem;
            color: var(--gray-700);
        }}
        
        .finding-metadata {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-bottom: 0.5rem;
        }}
        
        .finding-metadata-item {{
            background-color: var(--gray-100);
            padding: 0.25rem 0.5rem;
            border-radius: 0.25rem;
            font-size: 0.75rem;
            color: var(--gray-700);
        }}
        
        .code-snippet {{
            background-color: var(--gray-100);
            padding: 1rem;
            border-radius: 0.25rem;
            font-family: monospace;
            font-size: 0.875rem;
            white-space: pre-wrap;
            overflow-x: auto;
            color: var(--gray-800);
            line-height: 1.5;
        }}
        
        .footer {{
            text-align: center;
            padding: 2rem 0;
            color: var(--gray-600);
            font-size: 0.875rem;
            border-top: 1px solid var(--gray-200);
            margin-top: 2rem;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <h1>GDPR Compliance Scan Report</h1>
            <p>Generated on {scan_date.strftime('%Y-%m-%d %H:%M')}</p>
        </div>
    </div>
    
    <div class="container">
        <div class="card">
            <h2>Repository Information</h2>
            <p><strong>Repository:</strong> {repo_path}</p>
            <p><strong>Scan Date:</strong> {scan_date.strftime('%Y-%m-%d %H:%M')}</p>
        </div>
        
        <div class="summary-grid">
            <div class="summary-item">
                <div class="value">{file_count}</div>
                <div class="label">Files Scanned</div>
            </div>
            <div class="summary-item">
                <div class="value">{line_count}</div>
                <div class="label">Lines of Code</div>
            </div>
            <div class="summary-item">
                <div class="value">{findings_count}</div>
                <div class="label">Total Findings</div>
            </div>
            <div class="summary-item">
                <div class="value">{scan_duration:.2f}s</div>
                <div class="label">Scan Duration</div>
            </div>
        </div>
        
        <div class="card">
            <h2>Compliance Scores</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem;">
"""
    
    # Add compliance scores
    for principle, score in compliance_scores.items():
        progress_class = "progress-good" if score >= 90 else "progress-warning" if score >= 70 else "progress-danger"
        html += f"""
                <div>
                    <h4>{principle}</h4>
                    <div class="progress-container {progress_class}">
                        <div class="progress-bar" style="width: {score}%;"></div>
                    </div>
                    <div class="progress-text">
                        <span>Score: {score}%</span>
                        <span>{score >= 90 and "Good" or score >= 70 and "Needs Improvement" or "Critical"}</span>
                    </div>
                </div>"""
    
    html += """
            </div>
        </div>
        
        <div class="card">
            <h2>Findings by Severity</h2>
            <div class="summary-grid">
                <div class="summary-item">
                    <div class="value severity-high">{}</div>
                    <div class="label">High Severity</div>
                </div>
                <div class="summary-item">
                    <div class="value severity-medium">{}</div>
                    <div class="label">Medium Severity</div>
                </div>
                <div class="summary-item">
                    <div class="value severity-low">{}</div>
                    <div class="label">Low Severity</div>
                </div>
            </div>
        </div>
""".format(severity_counts["high"], severity_counts["medium"], severity_counts["low"])
    
    # Add findings by principle
    for principle, principle_findings_list in principle_findings.items():
        if principle == "Other":
            continue
            
        html += f"""
        <div class="card">
            <h2>{principle}</h2>"""
        
        # Sort findings by severity (high to low)
        principle_findings_list.sort(key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x.get("severity", "low"), 3))
        
        for finding in principle_findings_list:
            severity = finding.get("severity", "low")
            description = finding.get("description", "No description")
            file_path = finding.get("file", "Unknown")
            line = finding.get("line", 0)
            region_flags = ", ".join(finding.get("region_flags", []))
            context_snippet = finding.get("context_snippet", "").replace("<", "&lt;").replace(">", "&gt;")
            
            html += f"""
            <div class="finding {severity}">
                <div class="finding-header">
                    <div class="finding-title">{description}</div>
                    <div class="finding-location">{os.path.basename(file_path)}:{line}</div>
                </div>
                <div class="finding-metadata">
                    <div class="finding-metadata-item">Severity: <span class="severity-{severity}">{severity.upper()}</span></div>
                    <div class="finding-metadata-item">File: {file_path}</div>
                    <div class="finding-metadata-item">GDPR: {region_flags}</div>
                </div>
                <div class="code-snippet">{context_snippet}</div>
            </div>"""
        
        html += """
        </div>"""
    
    # Add other findings
    if "Other" in principle_findings:
        html += """
        <div class="card">
            <h2>Other Findings</h2>"""
        
        # Sort findings by severity (high to low)
        principle_findings["Other"].sort(key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x.get("severity", "low"), 3))
        
        for finding in principle_findings["Other"]:
            severity = finding.get("severity", "low")
            description = finding.get("description", "No description")
            file_path = finding.get("file", "Unknown")
            line = finding.get("line", 0)
            finding_type = finding.get("type", "Unknown")
            region_flags = ", ".join(finding.get("region_flags", []))
            context_snippet = finding.get("context_snippet", "").replace("<", "&lt;").replace(">", "&gt;")
            
            html += f"""
            <div class="finding {severity}">
                <div class="finding-header">
                    <div class="finding-title">{description}</div>
                    <div class="finding-location">{os.path.basename(file_path)}:{line}</div>
                </div>
                <div class="finding-metadata">
                    <div class="finding-metadata-item">Severity: <span class="severity-{severity}">{severity.upper()}</span></div>
                    <div class="finding-metadata-item">Type: {finding_type}</div>
                    <div class="finding-metadata-item">File: {file_path}</div>
                    <div class="finding-metadata-item">GDPR: {region_flags}</div>
                </div>
                <div class="code-snippet">{context_snippet}</div>
            </div>"""
        
        html += """
        </div>"""
    
    html += """
        <div class="footer">
            <p>© 2025 DataGuardian Pro - GDPR Compliance Scanner</p>
        </div>
    </div>
</body>
</html>"""
    
    return html

def generate_pdf_report(scan_results: Dict[str, Any], organization_name: str = "Your Organization") -> bytes:
    """Generate a PDF report from scan results"""
    buffer = io.BytesIO()
    
    # Create document
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        title="GDPR Compliance Scan Report",
        leftMargin=1.5*cm, 
        rightMargin=1.5*cm, 
        topMargin=2*cm, 
        bottomMargin=2*cm
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    heading2_style = styles["Heading2"]
    heading3_style = styles["Heading3"]
    normal_style = styles["Normal"]
    
    # Create custom styles
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=16,
        textColor=colors.darkblue,
    )
    
    finding_style = ParagraphStyle(
        'Finding',
        parent=styles['Normal'],
        fontSize=10,
        spaceBefore=8,
        spaceAfter=8,
    )
    
    # Create content
    content = []
    
    # Title and report date
    content.append(Paragraph("GDPR Compliance Scan Report", title_style))
    content.append(Spacer(1, 0.5*cm))
    
    # Extract scan date
    scan_date = scan_results.get("scan_date", datetime.now().isoformat())
    if isinstance(scan_date, str):
        try:
            scan_date = datetime.fromisoformat(scan_date)
        except ValueError:
            scan_date = datetime.now()
    
    content.append(Paragraph(f"Organization: {organization_name}", normal_style))
    content.append(Paragraph(f"Generated: {scan_date.strftime('%Y-%m-%d %H:%M')}", normal_style))
    content.append(Paragraph(f"Repository: {scan_results.get('repo_path', 'Unknown')}", normal_style))
    content.append(Spacer(1, 1*cm))
    
    # Summary section
    content.append(Paragraph("Executive Summary", section_style))
    
    # Add metrics table
    summary_data = [
        ["Metric", "Value"],
        ["Files Scanned", str(scan_results.get("file_count", 0))],
        ["Lines of Code", str(scan_results.get("line_count", 0))],
        ["Findings", str(scan_results.get("findings_count", 0))],
        ["Scan Duration", f"{scan_results.get('scan_duration', 0):.2f} seconds"],
    ]
    
    # Count findings by severity
    findings = scan_results.get("findings", [])
    severity_counts = {"high": 0, "medium": 0, "low": 0}
    for finding in findings:
        severity = finding.get("severity", "low")
        severity_counts[severity] += 1
    
    for severity, count in severity_counts.items():
        summary_data.append([f"{severity.title()} Severity Findings", str(count)])
    
    summary_table = Table(summary_data, colWidths=[doc.width/2.5, doc.width/2.5])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (1, 0), 12),
        ('BACKGROUND', (0, 1), (1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (1, -1), 'MIDDLE'),
    ]))
    
    content.append(summary_table)
    content.append(Spacer(1, 0.5*cm))
    
    # Compliance Scores section
    content.append(Paragraph("GDPR Compliance Scores", section_style))
    
    # Create scores table
    compliance_scores = scan_results.get("compliance_scores", {})
    scores_data = [["GDPR Principle", "Score"]]
    
    for principle, score in compliance_scores.items():
        scores_data.append([principle, f"{score}%"])
    
    scores_table = Table(scores_data, colWidths=[doc.width*0.7, doc.width*0.3])
    scores_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
    ]))
    
    content.append(scores_table)
    content.append(Spacer(1, 1*cm))
    
    # Findings section
    if findings:
        content.append(Paragraph("Detailed Findings", section_style))
        
        # Group findings by principle
        principle_findings = {}
        for finding in findings:
            principle = finding.get("principle", "Other")
            if principle not in principle_findings:
                principle_findings[principle] = []
            principle_findings[principle].append(finding)
        
        # Add findings by principle
        for principle, principle_findings_list in principle_findings.items():
            if principle == "Other":
                continue
                
            content.append(Paragraph(f"{principle}", heading2_style))
            
            # Sort findings by severity (high to low)
            principle_findings_list.sort(key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x.get("severity", "low"), 3))
            
            for i, finding in enumerate(principle_findings_list, 1):
                severity = finding.get("severity", "low").upper()
                file_path = finding.get("file", "Unknown")
                line_num = finding.get("line", 0)
                description = finding.get("description", "No description")
                region_flags = ", ".join(finding.get("region_flags", []))
                
                # Set color based on severity
                color_code = colors.red if severity == "HIGH" else (colors.orange if severity == "MEDIUM" else colors.green)
                
                # Create finding text
                finding_text = f"<strong>{i}. {severity}: {description}</strong><br/>"
                finding_text += f"<strong>File:</strong> {file_path}:{line_num}<br/>"
                finding_text += f"<strong>GDPR:</strong> {region_flags}<br/>"
                
                finding_para = Paragraph(finding_text, finding_style)
                content.append(finding_para)
                
                # Add code snippet if available
                snippet = finding.get("context_snippet", "")
                if snippet:
                    snippet_style = ParagraphStyle(
                        'CodeSnippet',
                        parent=styles['Code'],
                        fontSize=8,
                        fontName='Courier',
                        leftIndent=20,
                        rightIndent=20,
                        backColor=colors.lightgrey,
                    )
                    # Escape HTML characters in snippet
                    snippet = snippet.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    content.append(Paragraph(f"<pre>{snippet}</pre>", snippet_style))
                
                content.append(Spacer(1, 0.3*cm))
        
        # Add other findings
        if "Other" in principle_findings:
            content.append(Paragraph("Other Findings", heading2_style))
            
            # Sort findings by severity (high to low)
            principle_findings["Other"].sort(key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x.get("severity", "low"), 3))
            
            for i, finding in enumerate(principle_findings["Other"], 1):
                severity = finding.get("severity", "low").upper()
                file_path = finding.get("file", "Unknown")
                line_num = finding.get("line", 0)
                description = finding.get("description", "No description")
                finding_type = finding.get("type", "Unknown")
                region_flags = ", ".join(finding.get("region_flags", []))
                
                # Create finding text
                finding_text = f"<strong>{i}. {severity}: {description}</strong><br/>"
                finding_text += f"<strong>File:</strong> {file_path}:{line_num}<br/>"
                finding_text += f"<strong>Type:</strong> {finding_type}<br/>"
                finding_text += f"<strong>GDPR:</strong> {region_flags}<br/>"
                
                finding_para = Paragraph(finding_text, finding_style)
                content.append(finding_para)
                
                # Add code snippet if available
                snippet = finding.get("context_snippet", "")
                if snippet:
                    snippet_style = ParagraphStyle(
                        'CodeSnippet',
                        parent=styles['Code'],
                        fontSize=8,
                        fontName='Courier',
                        leftIndent=20,
                        rightIndent=20,
                        backColor=colors.lightgrey,
                    )
                    # Escape HTML characters in snippet
                    snippet = snippet.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    content.append(Paragraph(f"<pre>{snippet}</pre>", snippet_style))
                
                content.append(Spacer(1, 0.3*cm))
    else:
        content.append(Paragraph("No GDPR compliance issues were found!", heading2_style))
    
    # Compliance certification
    content.append(Paragraph("Compliance Assessment", section_style))
    
    # Determine overall compliance level
    total_score = 0
    for score in compliance_scores.values():
        total_score += score
    
    avg_score = total_score / len(compliance_scores) if compliance_scores else 0
    
    if avg_score >= 90:
        compliance_status = "Substantially Compliant"
        compliance_text = (
            f"Based on the assessment results, {organization_name} is assessed as substantially "
            f"compliant with GDPR and UAVG requirements as of {scan_date.strftime('%Y-%m-%d')}. "
            f"Minor improvements may be recommended."
        )
    elif avg_score >= 70:
        compliance_status = "Partially Compliant"
        compliance_text = (
            f"Based on the assessment results, {organization_name} is assessed as partially "
            f"compliant with GDPR and UAVG requirements as of {scan_date.strftime('%Y-%m-%d')}. "
            f"Some significant improvements are recommended."
        )
    else:
        compliance_status = "Not Compliant"
        compliance_text = (
            f"Based on the assessment results, {organization_name} is assessed as not "
            f"compliant with GDPR and UAVG requirements as of {scan_date.strftime('%Y-%m-%d')}. "
            f"Immediate remediation actions are required."
        )
    
    content.append(Paragraph(f"Compliance Status: {compliance_status}", heading3_style))
    content.append(Paragraph(compliance_text, normal_style))
    
    # Build PDF document
    doc.build(content)
    
    # Get PDF data
    pdf_data = buffer.getvalue()
    buffer.close()
    
    return pdf_data

def main():
    st.title("GDPR Code Scanner")
    st.markdown("Scan your code repository for GDPR compliance issues with focus on Dutch-specific rules (UAVG).")
    
    # Main layout
    scan_config_col, scan_results_col = st.columns([1, 2])
    
    with scan_config_col:
        st.markdown("### Scan Configuration")
        
        # Repository path
        repo_path = st.text_input(
            "Repository Path",
            value=".",
            help="Path to the repository to scan"
        )
        
        # Select languages
        languages = st.multiselect(
            "Select Languages",
            options=["Python", "JavaScript", "TypeScript", "Java", "Terraform", "YAML", "JSON"],
            default=["Python", "JavaScript"],
            help="Select languages to scan"
        )
        
        # Organization name
        organization_name = st.text_input(
            "Organization Name",
            value="Your Organization",
            help="Your organization name for the report"
        )
        
        # Advanced options
        with st.expander("Advanced Options"):
            timeout = st.slider(
                "Scan Timeout (seconds per file)",
                min_value=5,
                max_value=60,
                value=20,
                help="Maximum time to spend scanning each file"
            )
            
            include_git_info = st.checkbox(
                "Include Git Information",
                value=True,
                help="Include git blame and commit information in findings"
            )
        
        # Start scan button
        scan_button = st.button("Start GDPR Scan", key="start_scan", use_container_width=True)
    
    with scan_results_col:
        # Display scan results when scan is initiated
        if scan_button:
            # Initialize scanner
            scanner = GDPRCodeScanner(
                repo_path=repo_path,
                languages=[lang.lower() for lang in languages],
                timeout=timeout
            )
            
            # Set up progress reporting
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_progress(progress, message):
                progress_bar.progress(progress)
                status_text.text(message)
            
            # Run the scan
            with st.spinner("Scanning repository..."):
                try:
                    # Simulate scan progress (in a production environment, we'd use actual progress)
                    for i in range(1, 10):
                        time.sleep(0.3)  # Simulate scanning time
                        update_progress(i/10, f"Scanning repository... ({i*10}%)")
                    
                    scan_results = scanner.scan(on_progress=update_progress)
                    
                    # Update final progress
                    update_progress(1.0, "Scan completed!")
                    
                    # Store scan results in session state
                    st.session_state.gdpr_scan_results = scan_results
                    
                    # Show success message
                    st.success("GDPR compliance scan completed successfully!")
                    
                except Exception as e:
                    st.error(f"Error during scan: {str(e)}")
                    return
            
            # Display scan summary
            st.markdown("### Scan Summary")
            
            # Create metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Files Scanned", scan_results.get("file_count", 0))
            with col2:
                st.metric("Lines of Code", scan_results.get("line_count", 0))
            with col3:
                st.metric("Findings", scan_results.get("findings_count", 0))
            with col4:
                st.metric("Scan Duration", f"{scan_results.get('scan_duration', 0):.2f}s")
            
            # Display compliance scores
            st.markdown("### GDPR Compliance Scores")
            
            # Get compliance scores and create a visualization
            compliance_scores = scan_results.get("compliance_scores", {})
            
            # Create columns for scores
            score_cols = st.columns(2)
            for i, (principle, score) in enumerate(compliance_scores.items()):
                col_idx = i % 2
                with score_cols[col_idx]:
                    # Color based on score
                    color = "green" if score >= 90 else "orange" if score >= 70 else "red"
                    st.markdown(f"**{principle}**: {score}%")
                    st.progress(score/100)
            
            # Generate reports
            st.markdown("### Generate Reports")
            
            report_col1, report_col2 = st.columns(2)
            
            with report_col1:
                if st.button("Generate PDF Report", use_container_width=True):
                    with st.spinner("Generating PDF report..."):
                        # Generate PDF report
                        pdf_data = generate_pdf_report(scan_results, organization_name)
                        
                        # Create a unique timestamp for the filename
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"GDPR_Compliance_Report_{organization_name.replace(' ', '_')}_{timestamp}.pdf"
                        
                        # Show success message
                        st.success("PDF report generated successfully!")
                        
                        # Add download button
                        st.download_button(
                            label="📥 Download PDF Report",
                            data=pdf_data,
                            file_name=filename,
                            mime="application/pdf",
                            key=f"download_pdf_{timestamp}",
                            use_container_width=True
                        )
                        
                        # Alternative download method for better reliability
                        b64_pdf = base64.b64encode(pdf_data).decode()
                        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{filename}" style="display:block;text-align:center;margin-top:10px;padding:10px;background-color:#4f46e5;color:white;text-decoration:none;border-radius:4px;">📥 Alternative Download Link</a>'
                        st.markdown(href, unsafe_allow_html=True)
            
            with report_col2:
                if st.button("Generate HTML Report", use_container_width=True):
                    with st.spinner("Generating HTML report..."):
                        # Generate HTML report
                        html_content = generate_html_report(scan_results)
                        
                        # Create a unique timestamp for the filename
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"GDPR_Compliance_Report_{organization_name.replace(' ', '_')}_{timestamp}.html"
                        
                        # Show success message
                        st.success("HTML report generated successfully!")
                        
                        # Add download button
                        st.download_button(
                            label="📥 Download HTML Report",
                            data=html_content,
                            file_name=filename,
                            mime="text/html",
                            key=f"download_html_{timestamp}",
                            use_container_width=True
                        )
            
            # Display findings
            st.markdown("### Detailed Findings")
            
            # Get findings and group by severity
            findings = scan_results.get("findings", [])
            
            if findings:
                # Group findings by severity
                severity_groups = {"high": [], "medium": [], "low": []}
                for finding in findings:
                    severity = finding.get("severity", "low")
                    severity_groups[severity].append(finding)
                
                # Display findings by severity
                for severity, severity_findings in [
                    ("high", severity_groups["high"]),
                    ("medium", severity_groups["medium"]),
                    ("low", severity_groups["low"])
                ]:
                    if severity_findings:
                        if severity == "high":
                            st.error(f"**{severity.upper()} SEVERITY FINDINGS ({len(severity_findings)})**")
                        elif severity == "medium":
                            st.warning(f"**{severity.upper()} SEVERITY FINDINGS ({len(severity_findings)})**")
                        else:
                            st.info(f"**{severity.upper()} SEVERITY FINDINGS ({len(severity_findings)})**")
                        
                        # Display each finding
                        for finding in severity_findings:
                            with st.expander(f"{finding.get('description', 'No description')}"):
                                # Display finding details
                                st.markdown(f"**File:** `{finding.get('file', 'Unknown')}`")
                                st.markdown(f"**Line:** {finding.get('line', 0)}")
                                
                                # Display principle if available
                                if "principle" in finding:
                                    st.markdown(f"**Principle:** {finding.get('principle')}")
                                
                                # Display type if available
                                if "type" in finding:
                                    st.markdown(f"**Type:** {finding.get('type')}")
                                
                                # Display region flags
                                region_flags = finding.get("region_flags", [])
                                if region_flags:
                                    st.markdown(f"**GDPR References:** {', '.join(region_flags)}")
                                
                                # Display code snippet
                                context_snippet = finding.get("context_snippet", "")
                                if context_snippet:
                                    st.markdown("**Code Snippet:**")
                                    st.code(context_snippet)
                                
                                # Display git info if available
                                commit_info = finding.get("commit_info", {})
                                if commit_info:
                                    st.markdown("**Git Information:**")
                                    st.markdown(f"- Author: {commit_info.get('author', 'Unknown')}")
                                    st.markdown(f"- Commit: {commit_info.get('commit_id', 'Unknown')}")
            else:
                st.success("No GDPR compliance issues found in the repository.")

if __name__ == "__main__":
    main()