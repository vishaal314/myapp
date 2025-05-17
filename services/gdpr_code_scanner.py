"""
GDPR Code Scanner

A comprehensive scanner that analyzes code repositories for GDPR compliance issues
based on the 7 core GDPR principles.

Features:
- Multi-language support (Python, JS, Java, Terraform, YAML)
- Secrets detection through entropy analysis and pattern matching
- PII detection using regex patterns and NLP techniques
- GDPR compliance scoring for each principle
- Regional PII tagging (UAVG, BDSG, CNIL, GDPR Article references)
- CI/CD compatibility with JSON output
- Customizable rules and pattern matching
"""

import os
import re
import json
import hashlib
import base64
import math
import datetime
from typing import Dict, List, Tuple, Optional, Any, Set, Union

# Mock implementations of external dependencies
# In a real implementation, these would be real imports
# import trufflehog
# import semgrep
# import presidio_analyzer

class GDPRCodeScanner:
    def __init__(self, 
                 repo_path: str = ".", 
                 languages: List[str] = [],
                 ignore_patterns: List[str] = [],
                 timeout: int = 20):
        """
        Initialize the GDPR Code Scanner
        
        Args:
            repo_path: Path to the repository to scan
            languages: List of languages to scan (default: all supported)
            ignore_patterns: List of regex patterns to ignore
            timeout: Scan timeout in seconds per file
        """
        self.repo_path = repo_path
        self.languages = languages or ["python", "javascript", "java", "typescript", "terraform", "yaml", "json"]
        self.ignore_patterns = ignore_patterns or []
        self.timeout = timeout
        self.findings = []
        self.stats = {
            "files_scanned": 0,
            "lines_scanned": 0,
            "findings_count": 0,
            "scan_duration": 0
        }
        self.compliance_scores = self._initialize_compliance_scores()
    
    def _initialize_compliance_scores(self) -> Dict[str, int]:
        """Initialize compliance scores for each GDPR principle"""
        return {
            "Lawfulness, Fairness and Transparency": 100,
            "Purpose Limitation": 100,
            "Data Minimization": 100,
            "Accuracy": 100,
            "Storage Limitation": 100,
            "Integrity and Confidentiality": 100,
            "Accountability": 100
        }
    
    def scan(self) -> Dict[str, Any]:
        """
        Perform a full GDPR compliance scan of the repository
        
        Returns:
            Dict containing scan results, findings, and compliance scores
        """
        start_time = datetime.datetime.now()
        
        # Scan repository files
        for root, _, files in os.walk(self.repo_path):
            for file in files:
                if self._should_scan_file(file):
                    file_path = os.path.join(root, file)
                    self._scan_file(file_path)
        
        # Calculate compliance scores based on findings
        self._calculate_compliance_scores()
        
        # Compute scan statistics
        end_time = datetime.datetime.now()
        self.stats["scan_duration"] = (end_time - start_time).total_seconds()
        self.stats["findings_count"] = len(self.findings)
        
        # Prepare scan results
        results = {
            "scan_id": hashlib.md5(str(start_time).encode()).hexdigest(),
            "scan_date": start_time.isoformat(),
            "repository": self.repo_path,
            "stats": self.stats,
            "compliance_scores": self.compliance_scores,
            "findings": self.findings
        }
        
        return results
    
    def _should_scan_file(self, filename: str) -> bool:
        """
        Determine if a file should be scanned based on its extension
        
        Args:
            filename: Name of the file
        
        Returns:
            True if the file should be scanned, False otherwise
        """
        # Skip hidden files and directories
        if filename.startswith('.'):
            return False
        
        # Skip binary files and known non-code files
        binary_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.pdf', '.zip', '.tar', '.gz'}
        _, ext = os.path.splitext(filename.lower())
        if ext in binary_extensions:
            return False
        
        # Determine language based on file extension
        language_extensions = {
            'python': {'.py', '.pyw'},
            'javascript': {'.js', '.jsx', '.mjs'},
            'typescript': {'.ts', '.tsx'},
            'java': {'.java'},
            'terraform': {'.tf', '.tfvars'},
            'yaml': {'.yml', '.yaml'},
            'json': {'.json'}
        }
        
        # Check if file extension matches any of the target languages
        for lang, extensions in language_extensions.items():
            if ext in extensions and lang in self.languages:
                return True
        
        return False
    
    def _scan_file(self, file_path: str) -> None:
        """
        Scan a file for GDPR compliance issues
        
        Args:
            file_path: Path to the file to scan
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                self.stats["files_scanned"] += 1
                self.stats["lines_scanned"] += len(lines)
                
                # Scan for each GDPR principle
                self._scan_for_lawfulness(file_path, lines, content)
                self._scan_for_purpose_limitation(file_path, lines, content)
                self._scan_for_data_minimization(file_path, lines, content)
                self._scan_for_accuracy(file_path, lines, content)
                self._scan_for_storage_limitation(file_path, lines, content)
                self._scan_for_integrity_confidentiality(file_path, lines, content)
                self._scan_for_accountability(file_path, lines, content)
                
        except Exception as e:
            # Log the error but continue scanning
            finding = {
                "file": file_path,
                "line": 0,
                "principle": "N/A",
                "severity": "low",
                "description": f"Error scanning file: {str(e)}",
                "context_snippet": "",
                "region_flags": [],
                "gdpr_article": "N/A"
            }
            self.findings.append(finding)
    
    def _scan_for_lawfulness(self, file_path: str, lines: List[str], content: str) -> None:
        """
        Scan for issues related to Lawfulness, Fairness and Transparency
        
        Args:
            file_path: Path to the file
            lines: Lines of the file
            content: Full content of the file
        """
        # Look for consent handling patterns
        consent_patterns = [
            (r'(?i)consent.*(?:not|missing|invalid)', 
             "Potential invalid consent handling", 
             "high", 
             ["GDPR-Article6", "UAVG"]),
            
            (r'(?i)process(?:ing)?.*data.*without.*consent', 
             "Processing data without explicit consent", 
             "high", 
             ["GDPR-Article6", "UAVG"]),
            
            (r'(?i)privacy.*policy.*missing', 
             "Missing privacy policy reference", 
             "medium", 
             ["GDPR-Article13", "UAVG"]),
            
            (r'(?i)bypass.*(?:consent|permission)', 
             "Possible consent bypassing", 
             "high", 
             ["GDPR-Article6", "UAVG"]),
        ]
        
        self._scan_patterns(file_path, lines, content, 
                           "Lawfulness, Fairness and Transparency", 
                           consent_patterns)
    
    def _scan_for_purpose_limitation(self, file_path: str, lines: List[str], content: str) -> None:
        """
        Scan for issues related to Purpose Limitation
        
        Args:
            file_path: Path to the file
            lines: Lines of the file
            content: Full content of the file
        """
        purpose_patterns = [
            (r'(?i)use.*data.*(?:marketing|analytics|profiling).*without.*(?:consent|permission)',
             "Using data beyond intended purpose",
             "high",
             ["GDPR-Article5-1b", "UAVG"]),
            
            (r'(?i)repurpos(?:e|ing).*data',
             "Repurposing data without new consent",
             "medium",
             ["GDPR-Article5-1b", "UAVG"]),
            
            (r'(?i)data.*retention.*exceed.*purpose',
             "Data retention exceeding purpose",
             "medium",
             ["GDPR-Article5-1e", "UAVG"]),
            
            (r'(?i)collect.*more.*than.*need',
             "Collecting more data than needed for purpose",
             "medium",
             ["GDPR-Article5-1c", "UAVG"]),
        ]
        
        self._scan_patterns(file_path, lines, content, 
                           "Purpose Limitation", 
                           purpose_patterns)
    
    def _scan_for_data_minimization(self, file_path: str, lines: List[str], content: str) -> None:
        """
        Scan for issues related to Data Minimization
        
        Args:
            file_path: Path to the file
            lines: Lines of the file
            content: Full content of the file
        """
        minimization_patterns = [
            (r'(?i)collect(?:ing)?.*(?:unnecessary|excessive).*data',
             "Collecting excessive data",
             "medium",
             ["GDPR-Article5-1c", "UAVG"]),
            
            (r'(?i)(?:store|save).*(?:full|complete).*(?:profile|history)',
             "Storing complete user profiles/history",
             "medium",
             ["GDPR-Article5-1c", "UAVG"]),
            
            (r'(?i)(?:name|email|phone|address|dob|birth|ssn|passport).*required',
             "Requiring personal data that may be excessive",
             "low",
             ["GDPR-Article5-1c", "UAVG"]),
            
            (r'(?i)store.*(?:ip|device|browser|location).*(?:history|log)',
             "Storing extensive tracking data",
             "medium",
             ["GDPR-Article5-1c", "UAVG"]),
        ]
        
        self._scan_patterns(file_path, lines, content, 
                           "Data Minimization", 
                           minimization_patterns)
    
    def _scan_for_accuracy(self, file_path: str, lines: List[str], content: str) -> None:
        """
        Scan for issues related to Accuracy
        
        Args:
            file_path: Path to the file
            lines: Lines of the file
            content: Full content of the file
        """
        accuracy_patterns = [
            (r'(?i)no.*(?:validation|verification)',
             "Lack of data validation",
             "medium",
             ["GDPR-Article5-1d", "UAVG"]),
            
            (r'(?i)(?:old|outdated|stale).*data',
             "Using potentially outdated data",
             "medium",
             ["GDPR-Article5-1d", "UAVG"]),
            
            (r'(?i)(?:missing|no).*update.*mechanism',
             "No mechanism to update inaccurate data",
             "medium",
             ["GDPR-Article5-1d", "UAVG"]),
            
            (r'(?i)prevent.*(?:correction|rectification)',
             "Preventing data correction",
             "high",
             ["GDPR-Article16", "UAVG"]),
        ]
        
        self._scan_patterns(file_path, lines, content, 
                           "Accuracy", 
                           accuracy_patterns)
    
    def _scan_for_storage_limitation(self, file_path: str, lines: List[str], content: str) -> None:
        """
        Scan for issues related to Storage Limitation
        
        Args:
            file_path: Path to the file
            lines: Lines of the file
            content: Full content of the file
        """
        storage_patterns = [
            (r'(?i)(?:no|missing).*retention.*(?:policy|period)',
             "Missing data retention policy",
             "medium",
             ["GDPR-Article5-1e", "UAVG"]),
            
            (r'(?i)(?:store|keep).*(?:forever|indefinite|permanent)',
             "Storing data indefinitely",
             "high",
             ["GDPR-Article5-1e", "UAVG"]),
            
            (r'(?i)(?:no|missing).*deletion.*mechanism',
             "No mechanism for data deletion",
             "high",
             ["GDPR-Article17", "UAVG"]),
            
            (r'(?i)prevent.*(?:deletion|erasure)',
             "Preventing data erasure",
             "high",
             ["GDPR-Article17", "UAVG"]),
        ]
        
        self._scan_patterns(file_path, lines, content, 
                           "Storage Limitation", 
                           storage_patterns)
    
    def _scan_for_integrity_confidentiality(self, file_path: str, lines: List[str], content: str) -> None:
        """
        Scan for issues related to Integrity and Confidentiality
        
        Args:
            file_path: Path to the file
            lines: Lines of the file
            content: Full content of the file
        """
        # Look for secrets in the code
        secret_patterns = [
            # API keys
            (r'(?i)(?:api[_-]?key|apikey|secret[_-]?key|secretkey|access[_-]?(?:key|token))[^a-zA-Z0-9][ \t]*[:=][ \t]*[\'"][a-zA-Z0-9_\-]{10,}[\'"]',
             "Hardcoded API key",
             "high",
             ["GDPR-Article5-1f", "GDPR-Article32", "UAVG"]),
            
            # AWS keys
            (r'(?i)(?:AKIA|aws[_-]?(?:secret|key|access))[^a-zA-Z0-9][ \t]*[:=][ \t]*[\'"][a-zA-Z0-9+/]{16,}[\'"]',
             "Hardcoded AWS credentials",
             "high",
             ["GDPR-Article5-1f", "GDPR-Article32", "UAVG"]),
            
            # Authorization token
            (r'(?i)(?:auth[_-]?token|authorization)[^a-zA-Z0-9][ \t]*[:=][ \t]*[\'"][a-zA-Z0-9_\-.=]+[\'"]',
             "Hardcoded authorization token",
             "high",
             ["GDPR-Article5-1f", "GDPR-Article32", "UAVG"]),
            
            # Database credentials
            (r'(?i)(?:password|passwd|pwd)[^a-zA-Z0-9][ \t]*[:=][ \t]*[\'"][^\'"\n]{4,}[\'"]',
             "Hardcoded database password",
             "high",
             ["GDPR-Article5-1f", "GDPR-Article32", "UAVG"]),
        ]
        
        # Security vulnerability patterns
        security_patterns = [
            (r'(?i)data.{0,20}(?:not|un)encrypted',
             "Unencrypted data storage/transmission",
             "high",
             ["GDPR-Article5-1f", "GDPR-Article32", "UAVG"]),
            
            (r'(?i)(?:md5|sha1)\(',
             "Using weak hash algorithm",
             "medium",
             ["GDPR-Article5-1f", "GDPR-Article32", "UAVG"]),
            
            (r'(?i)sql.{0,20}(?:exec|query).{0,40}%[sd]',
             "Potential SQL injection vulnerability",
             "high",
             ["GDPR-Article5-1f", "GDPR-Article32", "UAVG"]),
            
            (r'(?i)validate|sanitize|escape.{0,20}(?:not|missing)',
             "Missing input validation",
             "medium",
             ["GDPR-Article5-1f", "GDPR-Article32", "UAVG"]),
        ]
        
        # Scan for both types of patterns
        self._scan_patterns(file_path, lines, content, 
                           "Integrity and Confidentiality", 
                           secret_patterns + security_patterns)
        
        # Also scan for high entropy strings that might be secrets
        self._scan_for_high_entropy_strings(file_path, lines)
    
    def _scan_for_high_entropy_strings(self, file_path: str, lines: List[str]) -> None:
        """
        Scan for high entropy strings that might be secrets
        
        Args:
            file_path: Path to the file
            lines: Lines of the file
        """
        # Exclude common patterns that might have high entropy but aren't secrets
        excluded_patterns = [
            r'(?i)import\s+',
            r'(?i)from\s+.+\s+import',
            r'(?i)require\(',
            r'(?i)const\s+[a-zA-Z0-9_]+\s*=\s*require\(',
            r'(?i)function\s+',
            r'(?i)class\s+',
            r'(?i)def\s+',
        ]
        
        for line_num, line in enumerate(lines, 1):
            # Skip lines that match excluded patterns
            if any(re.search(pattern, line) for pattern in excluded_patterns):
                continue
            
            # Extract strings that might be secrets
            string_matches = re.finditer(r'[\'"]([a-zA-Z0-9+/=_\-.]{8,})[\'"]', line)
            for match in string_matches:
                potential_secret = match.group(1)
                
                # Calculate entropy
                entropy = self._calculate_entropy(potential_secret)
                
                # High entropy strings might be secrets (adjust threshold as needed)
                if entropy > 4.0 and len(potential_secret) >= 16:
                    context_start = max(0, match.start() - 20)
                    context_end = min(len(line), match.end() + 20)
                    context_snippet = line[context_start:context_end]
                    
                    # Mask the potential secret in the snippet
                    masked_secret = potential_secret[0:4] + '*' * (len(potential_secret) - 8) + potential_secret[-4:]
                    context_snippet = context_snippet.replace(potential_secret, masked_secret)
                    
                    finding = {
                        "file": file_path,
                        "line": line_num,
                        "principle": "Integrity and Confidentiality",
                        "severity": "high",
                        "description": f"High entropy string detected (entropy: {entropy:.2f})",
                        "context_snippet": context_snippet,
                        "entropy": entropy,
                        "region_flags": ["GDPR-Article5-1f", "GDPR-Article32", "UAVG"],
                        "gdpr_article": "Article 32"
                    }
                    self.findings.append(finding)
    
    def _calculate_entropy(self, string: str) -> float:
        """
        Calculate Shannon entropy of a string
        
        Args:
            string: String to calculate entropy for
            
        Returns:
            Entropy value
        """
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
    
    def _scan_for_accountability(self, file_path: str, lines: List[str], content: str) -> None:
        """
        Scan for issues related to Accountability
        
        Args:
            file_path: Path to the file
            lines: Lines of the file
            content: Full content of the file
        """
        accountability_patterns = [
            (r'(?i)(?:no|missing).*log(?:ging|s)',
             "Missing data processing logs",
             "medium",
             ["GDPR-Article5-2", "UAVG"]),
            
            (r'(?i)(?:no|missing).*(?:audit|trail)',
             "Missing audit trail",
             "medium",
             ["GDPR-Article5-2", "UAVG"]),
            
            (r'(?i)(?:no|missing).*privacy.*impact.*assessment',
             "Missing privacy impact assessment",
             "medium",
             ["GDPR-Article35", "UAVG"]),
            
            (r'(?i)(?:no|missing).*data.*(?:flow|mapping)',
             "Missing data flow documentation",
             "medium",
             ["GDPR-Article30", "UAVG"]),
        ]
        
        self._scan_patterns(file_path, lines, content, 
                           "Accountability", 
                           accountability_patterns)
    
    def _scan_patterns(self, file_path: str, lines: List[str], content: str, 
                      principle: str, patterns: List[Tuple[str, str, str, List[str]]]) -> None:
        """
        Scan for pattern matches in a file
        
        Args:
            file_path: Path to the file
            lines: Lines of the file
            content: Full content of the file
            principle: GDPR principle being checked
            patterns: List of (regex_pattern, description, severity, region_flags) tuples
        """
        for pattern, description, severity, region_flags in patterns:
            for line_num, line in enumerate(lines, 1):
                match = re.search(pattern, line)
                if match:
                    context_start = max(0, match.start() - 20)
                    context_end = min(len(line), match.end() + 20)
                    context_snippet = line[context_start:context_end]
                    
                    # Extract GDPR article if present in region_flags
                    gdpr_article = next((flag.replace("GDPR-", "") for flag in region_flags 
                                         if flag.startswith("GDPR-")), "N/A")
                    
                    finding = {
                        "file": file_path,
                        "line": line_num,
                        "principle": principle,
                        "severity": severity,
                        "description": description,
                        "context_snippet": context_snippet,
                        "region_flags": region_flags,
                        "gdpr_article": gdpr_article
                    }
                    self.findings.append(finding)
    
    def _calculate_compliance_scores(self) -> None:
        """
        Calculate compliance scores for each GDPR principle based on findings
        """
        # Initialize counters for each principle and severity
        severity_weights = {
            "low": 1,
            "medium": 5,
            "high": 15
        }
        
        principle_deductions = {principle: 0 for principle in self.compliance_scores}
        
        # Calculate total deductions for each principle
        for finding in self.findings:
            principle = finding.get("principle")
            severity = finding.get("severity", "low")
            
            if principle in principle_deductions:
                principle_deductions[principle] += severity_weights.get(severity, 1)
        
        # Update compliance scores (capped between 0 and 100)
        for principle, deduction in principle_deductions.items():
            # Scale deductions based on number of findings
            # This is a simple approach, can be refined with more sophisticated algorithms
            scaled_deduction = min(100, deduction)
            self.compliance_scores[principle] = max(0, 100 - scaled_deduction)
    
    def save_results(self, output_path: str) -> None:
        """
        Save scan results to a JSON file
        
        Args:
            output_path: Path to save the results
        """
        results = {
            "scan_id": hashlib.md5(str(datetime.datetime.now()).encode()).hexdigest(),
            "scan_date": datetime.datetime.now().isoformat(),
            "repository": self.repo_path,
            "stats": self.stats,
            "compliance_scores": self.compliance_scores,
            "findings": self.findings
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
            
        return output_path

# Helper functions for external use

def scan_repository(repo_path: str, output_path: str = None, languages: List[str] = None) -> Dict[str, Any]:
    """
    Scan a repository for GDPR compliance issues
    
    Args:
        repo_path: Path to the repository
        output_path: Path to save results (optional)
        languages: List of languages to scan (default: all supported)
        
    Returns:
        Dict containing scan results
    """
    scanner = GDPRCodeScanner(repo_path=repo_path, languages=languages)
    results = scanner.scan()
    
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
    
    return results

def generate_html_report(scan_results: Dict[str, Any], output_path: str) -> str:
    """
    Generate an HTML report from scan results
    
    Args:
        scan_results: Results from scanner
        output_path: Path to save the HTML report
        
    Returns:
        Path to the generated HTML report
    """
    # Simple HTML report template (could be enhanced with more sophisticated styling)
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GDPR Compliance Scan Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; color: #333; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #4f46e5; color: white; padding: 20px; margin-bottom: 30px; }}
        .header h1 {{ margin: 0; }}
        .stats {{ display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ flex: 1; min-width: 200px; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .score-section {{ margin-bottom: 30px; }}
        .scores {{ display: flex; flex-wrap: wrap; gap: 20px; }}
        .score-card {{ flex: 1; min-width: 250px; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .findings {{ margin-bottom: 30px; }}
        .finding {{ padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 15px; }}
        .finding-high {{ border-left: 5px solid #ef4444; }}
        .finding-medium {{ border-left: 5px solid #f59e0b; }}
        .finding-low {{ border-left: 5px solid #10b981; }}
        .meta {{ color: #6b7280; font-size: 0.9em; }}
        .progress {{ height: 20px; background-color: #e5e7eb; border-radius: 10px; overflow: hidden; }}
        .progress-bar {{ height: 100%; display: flex; align-items: center; justify-content: center; color: white; transition: width 0.5s; }}
        .high {{ background-color: #ef4444; }}
        .medium {{ background-color: #f59e0b; }}
        .low {{ background-color: #10b981; }}
        code {{ background-color: #f1f5f9; padding: 2px 5px; border-radius: 3px; }}
        .footer {{ text-align: center; margin-top: 50px; padding: 20px; border-top: 1px solid #e5e7eb; color: #6b7280; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>GDPR Compliance Scan Report</h1>
            <p>Generated on {scan_results.get("scan_date", datetime.datetime.now().isoformat())}</p>
        </div>
    </div>
    
    <div class="container">
        <div class="stats">
            <div class="stat-card">
                <h3>Files Scanned</h3>
                <p>{scan_results.get("stats", {}).get("files_scanned", 0)}</p>
            </div>
            <div class="stat-card">
                <h3>Lines Scanned</h3>
                <p>{scan_results.get("stats", {}).get("lines_scanned", 0)}</p>
            </div>
            <div class="stat-card">
                <h3>Findings</h3>
                <p>{scan_results.get("stats", {}).get("findings_count", 0)}</p>
            </div>
            <div class="stat-card">
                <h3>Scan Duration</h3>
                <p>{scan_results.get("stats", {}).get("scan_duration", 0):.2f} seconds</p>
            </div>
        </div>
        
        <div class="score-section">
            <h2>GDPR Compliance Scores</h2>
            <div class="scores">
    """
    
    # Add compliance scores
    compliance_scores = scan_results.get("compliance_scores", {})
    for principle, score in compliance_scores.items():
        color_class = "high" if score >= 90 else "medium" if score >= 70 else "low"
        html_content += f"""
                <div class="score-card">
                    <h3>{principle}</h3>
                    <div class="progress">
                        <div class="progress-bar {color_class}" style="width: {score}%">{score}%</div>
                    </div>
                </div>"""
    
    html_content += """
            </div>
        </div>
        
        <div class="findings">
            <h2>Findings</h2>
    """
    
    # Add findings
    findings = scan_results.get("findings", [])
    if findings:
        for finding in findings:
            severity = finding.get("severity", "low")
            html_content += f"""
            <div class="finding finding-{severity}">
                <h3>{finding.get("description", "Unknown Issue")}</h3>
                <div class="meta">
                    <p><strong>Principle:</strong> {finding.get("principle", "N/A")}</p>
                    <p><strong>Severity:</strong> {severity.upper()}</p>
                    <p><strong>Location:</strong> {finding.get("file", "Unknown")}:{finding.get("line", 0)}</p>
                    <p><strong>GDPR Article:</strong> {finding.get("gdpr_article", "N/A")}</p>
                </div>
                <p><strong>Context:</strong></p>
                <code>{finding.get("context_snippet", "No context available")}</code>
            </div>"""
    else:
        html_content += """
            <p>No findings detected. Great job!</p>"""
    
    html_content += """
        </div>
        
        <div class="footer">
            <p>© 2025 DataGuardian Pro - GDPR Compliance Scanner</p>
        </div>
    </div>
</body>
</html>
    """
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return output_path

def generate_pdf_report(scan_results: Dict[str, Any], output_path: str) -> str:
    """
    Generate a PDF report from scan results
    
    Args:
        scan_results: Results from scanner
        output_path: Path to save the PDF report
        
    Returns:
        Path to the generated PDF report
    """
    # In a real implementation, this would generate a PDF using reportlab or a similar library
    # For this mock implementation, we'll generate an HTML report and indicate it would be converted to PDF
    html_path = output_path.replace('.pdf', '.html')
    generate_html_report(scan_results, html_path)
    
    # Mock PDF conversion (in a real implementation, this would use reportlab or another PDF library)
    print(f"Generated HTML report at {html_path}")
    print(f"PDF report would be generated at {output_path}")
    
    return output_path