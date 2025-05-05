"""
Static Application Security Testing (SAST) Analyzer

This module provides a SAST capability to detect common security vulnerabilities
in source code without executing it. It focuses on finding issues that are
relevant to PCI DSS requirement 6.3.2 for secure coding practices.
"""

import os
import re
import subprocess
import logging
import json
from typing import Dict, List, Any, Optional, Tuple, Set

# Set up logging
logger = logging.getLogger("sast_analyzer")

class SASTAnalyzer:
    """
    Performs static application security testing to detect common security
    vulnerabilities in source code.
    """
    
    def __init__(self):
        """Initialize the SAST Analyzer."""
        # Define vulnerability patterns by language
        self.vulnerability_patterns = {
            # SQL Injection patterns
            "python": {
                "sql_injection": [
                    r'cursor\.execute\(\s*[\'"].*%s.*[\'"]',
                    r'cursor\.execute\(\s*[\'"].*\+.*[\'"]',
                    r'cursor\.execute\(\s*f[\'"].*\{.*\}',
                    r'cursor\.executemany\(\s*[\'"].*\+.*[\'"]',
                    r'execute\(\s*[\'"].*\+.*[\'"]',
                ],
                "command_injection": [
                    r'os\.system\(.*\)',
                    r'subprocess\.call\(.*shell\s*=\s*True.*\)',
                    r'subprocess\.Popen\(.*shell\s*=\s*True.*\)',
                    r'eval\(.*\)',
                    r'exec\(.*\)'
                ],
                "xss": [
                    r'render_template\(.*\+.*\)',
                    r'Response\(.*\+.*\)',
                    r'\.html\(.*\+.*\)',
                    r'.*\.write\(.*\+.*\)'
                ],
                "path_traversal": [
                    r'open\(.*\+.*\)',
                    r'os\.path\.join\(.*\+.*\)'
                ],
                "weak_crypto": [
                    r'md5\(',
                    r'hashlib\.md5\(',
                    r'hashlib\.sha1\(',
                    r'crypto\.Cipher\.DES',
                    r'crypto\.Cipher\.Blowfish',
                    r'random\.randrange\('
                ]
            },
            "java": {
                "sql_injection": [
                    r'Statement\.executeQuery\(\s*[\'"].*\+.*[\'"]',
                    r'Statement\.executeUpdate\(\s*[\'"].*\+.*[\'"]',
                    r'createStatement\(\).*execute',
                    r'prepareStatement\(\s*[\'"].*\+.*[\'"]'
                ],
                "command_injection": [
                    r'Runtime\.getRuntime\(\)\.exec\(',
                    r'ProcessBuilder\(',
                    r'new\s+ProcessBuilder\('
                ],
                "xss": [
                    r'response\.getWriter\(\)\.print',
                    r'response\.getWriter\(\)\.write',
                    r'out\.print',
                    r'out\.println'
                ],
                "path_traversal": [
                    r'new\s+File\(.*\+.*\)',
                    r'new\s+FileInputStream\(.*\+.*\)',
                    r'new\s+FileOutputStream\(.*\+.*\)'
                ],
                "weak_crypto": [
                    r'MessageDigest\.getInstance\([\'"]MD5[\'"]\)',
                    r'MessageDigest\.getInstance\([\'"]SHA-1[\'"]\)',
                    r'Cipher\.getInstance\([\'"]DES[\'"]\)',
                    r'Cipher\.getInstance\([\'"]AES/ECB[\'"]\)',
                    r'new\s+SecureRandom\(.*\)'
                ]
            },
            "javascript": {
                "sql_injection": [
                    r'connection\.query\(\s*[\'"].*\+.*[\'"]',
                    r'db\.query\(\s*[\'"].*\+.*[\'"]',
                    r'sequelize\.query\(\s*[\'"].*\+.*[\'"]',
                    r'mongoose\.exec\(\s*[\'"].*\+.*[\'"]'
                ],
                "command_injection": [
                    r'child_process\.exec\(',
                    r'child_process\.spawn\(',
                    r'child_process\.execSync\(',
                    r'eval\(',
                    r'Function\([\'"].*[\'"]\)'
                ],
                "xss": [
                    r'innerHTML\s*=',
                    r'document\.write\(',
                    r'element\.outerHTML\s*=',
                    r'dangerouslySetInnerHTML',
                    r'\.html\('
                ],
                "path_traversal": [
                    r'fs\.readFile\(.*\+.*\)',
                    r'fs\.readFileSync\(.*\+.*\)',
                    r'fs\.writeFile\(.*\+.*\)',
                    r'fs\.writeFileSync\(.*\+.*\)',
                    r'path\.join\(.*\+.*\)'
                ],
                "weak_crypto": [
                    r'crypto\.createHash\([\'"]md5[\'"]\)',
                    r'crypto\.createHash\([\'"]sha1[\'"]\)',
                    r'crypto\.createCipher\(',
                    r'Math\.random\(\)',
                    r'new\s+Date\(\)\.getTime\(\)'
                ]
            },
            "csharp": {
                "sql_injection": [
                    r'SqlCommand\(.*\+.*\)',
                    r'ExecuteReader\(.*\+.*\)',
                    r'ExecuteNonQuery\(.*\+.*\)',
                    r'ExecuteScalar\(.*\+.*\)',
                    r'new\s+SqlCommand\(.*\+.*\)'
                ],
                "command_injection": [
                    r'Process\.Start\(',
                    r'ProcessStartInfo',
                    r'System\.Diagnostics\.Process',
                    r'cmd\.exe',
                    r'powershell\.exe'
                ],
                "xss": [
                    r'Response\.Write\(',
                    r'<%=.*%>',
                    r'HttpUtility\.HtmlDecode\(',
                    r'@Html\.Raw\('
                ],
                "path_traversal": [
                    r'File\.ReadAllText\(.*\+.*\)',
                    r'File\.WriteAllText\(.*\+.*\)',
                    r'File\.Open\(.*\+.*\)',
                    r'StreamReader\(.*\+.*\)',
                    r'StreamWriter\(.*\+.*\)'
                ],
                "weak_crypto": [
                    r'MD5CryptoServiceProvider',
                    r'SHA1CryptoServiceProvider',
                    r'new\s+Random\(',
                    r'DESCryptoServiceProvider',
                    r'DateTime\.Now\.Ticks'
                ]
            },
            "php": {
                "sql_injection": [
                    r'mysql_query\(\s*[\'"].*\$.*[\'"]',
                    r'mysqli_query\(\s*[\'"].*\$.*[\'"]',
                    r'->query\(\s*[\'"].*\$.*[\'"]',
                    r'->exec\(\s*[\'"].*\$.*[\'"]',
                    r'->prepare\(\s*[\'"].*\$.*[\'"]'
                ],
                "command_injection": [
                    r'exec\(\s*\$.*\)',
                    r'shell_exec\(\s*\$.*\)',
                    r'system\(\s*\$.*\)',
                    r'passthru\(\s*\$.*\)',
                    r'eval\(\s*\$.*\)'
                ],
                "xss": [
                    r'echo\s+\$.*',
                    r'print\s+\$.*',
                    r'<\?=\s*\$.*\?>',
                    r'\.html\(\s*\$.*\)',
                    r'innerHTML\s*=\s*\$.*'
                ],
                "path_traversal": [
                    r'file_get_contents\(\s*\$.*\)',
                    r'file_put_contents\(\s*\$.*\)',
                    r'fopen\(\s*\$.*\)',
                    r'readfile\(\s*\$.*\)',
                    r'include\(\s*\$.*\)'
                ],
                "weak_crypto": [
                    r'md5\(',
                    r'sha1\(',
                    r'crypt\(',
                    r'mt_rand\(',
                    r'rand\('
                ]
            },
            # Generic patterns for configuration files
            "config": {
                "insecure_configuration": [
                    r'(password|secret|key|token|credential)[\'"]\s*:\s*[\'"][^\'"]+[\'"]',
                    r'(allowOrigin|cors)[\'"]\s*:\s*[\'"][*][\'"]',
                    r'(debug|development|test)[\'"]\s*:\s*[\'"]?true[\'"]?',
                    r'(ssl|https|secure)[\'"]\s*:\s*[\'"]?false[\'"]?',
                    r'(auth|authentication|authorization)[\'"]\s*:\s*[\'"]?false[\'"]?'
                ]
            }
        }
        
        # Map file extensions to language
        self.extension_map = {
            ".py": "python",
            ".java": "java",
            ".jsp": "java",
            ".js": "javascript",
            ".ts": "javascript",
            ".jsx": "javascript",
            ".tsx": "javascript",
            ".cs": "csharp",
            ".php": "php",
            ".json": "config",
            ".yaml": "config",
            ".yml": "config",
            ".xml": "config",
            ".properties": "config",
            ".ini": "config",
            ".conf": "config",
            ".cfg": "config",
            ".config": "config"
        }
        
        logger.info("SAST Analyzer initialized with vulnerability pattern databases")
        
    def analyze(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        Analyze source code in the given directory for security vulnerabilities.
        
        Args:
            directory_path: Path to the directory containing source code
            
        Returns:
            List of vulnerability findings
        """
        findings = []
        
        # Try to use semgrep if available for more advanced analysis
        try:
            semgrep_findings = self._run_semgrep(directory_path)
            if semgrep_findings:
                findings.extend(semgrep_findings)
                logger.info(f"Found {len(semgrep_findings)} issues with semgrep")
                # If semgrep worked, we can return early as it's more comprehensive
                if len(semgrep_findings) > 0:
                    return findings
        except Exception as e:
            logger.info(f"Semgrep not available or failed, using pattern-based scanning: {str(e)}")
        
        # Fall back to pattern-based scanning
        logger.info("Performing pattern-based SAST analysis")
        
        # Walk through directory and scan each file
        for root, _, files in os.walk(directory_path):
            # Skip .git directory
            if '.git' in root:
                continue
                
            for file in files:
                # Skip hidden files
                if file.startswith('.'):
                    continue
                    
                file_path = os.path.join(root, file)
                _, ext = os.path.splitext(file_path)
                
                # Get the appropriate language for this file
                language = self.extension_map.get(ext.lower())
                if not language:
                    continue
                    
                # Read file content
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception as e:
                    logger.warning(f"Error reading file {file_path}: {str(e)}")
                    continue
                    
                # Get relative path for reporting
                rel_path = os.path.relpath(file_path, directory_path)
                
                # Scan for vulnerabilities
                file_findings = self._scan_content(content, language, rel_path)
                findings.extend(file_findings)
        
        logger.info(f"Found {len(findings)} vulnerabilities through pattern-based scanning")
        return findings
    
    def _scan_content(self, content: str, language: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Scan file content for vulnerabilities based on language patterns.
        
        Args:
            content: The file content
            language: The programming language
            file_path: The file path for reporting
            
        Returns:
            List of vulnerability findings
        """
        findings = []
        
        # Skip if we don't have patterns for this language
        if language not in self.vulnerability_patterns:
            return findings
            
        # Get vulnerability patterns for this language
        patterns = self.vulnerability_patterns[language]
        
        # Split content into lines for better reporting
        lines = content.split('\n')
        
        # Scan for each vulnerability type
        for vuln_type, regexes in patterns.items():
            for regex_pattern in regexes:
                try:
                    # Search for pattern in content
                    for match in re.finditer(regex_pattern, content, re.IGNORECASE | re.MULTILINE):
                        # Find line number by counting newlines before match
                        line_number = content[:match.start()].count('\n') + 1
                        
                        # Get the matched line for context
                        line_content = lines[line_number - 1] if line_number <= len(lines) else "Context not available"
                        
                        # Create finding
                        finding = {
                            "type": self._normalize_vulnerability_type(vuln_type),
                            "value": line_content.strip(),
                            "location": f"{file_path}:{line_number}",
                            "file_name": file_path,
                            "line_number": line_number,
                            "pci_requirement": self._get_pci_requirement(vuln_type),
                            "risk_level": self._get_risk_level(vuln_type),
                            "remediation": self._get_remediation(vuln_type)
                        }
                        
                        findings.append(finding)
                except Exception as e:
                    logger.warning(f"Error scanning for {vuln_type} in {file_path}: {str(e)}")
        
        return findings
    
    def _run_semgrep(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        Run semgrep for more advanced static analysis if available.
        
        Args:
            directory_path: Path to the directory containing source code
            
        Returns:
            List of vulnerability findings from semgrep
        """
        findings = []
        
        try:
            # Try to run semgrep with p/owasp-top-ten ruleset
            result = subprocess.run(
                ["semgrep", "--config=p/owasp-top-ten", "--json", directory_path],
                capture_output=True,
                text=True,
                check=False  # Don't raise exception on non-zero exit
            )
            
            # Parse JSON output
            if result.stdout:
                try:
                    output = json.loads(result.stdout)
                    results = output.get("results", [])
                    
                    # Convert semgrep findings to our format
                    for result in results:
                        try:
                            finding = {
                                "type": self._normalize_vulnerability_type(result.get("check_id", "Unknown")),
                                "value": result.get("extra", {}).get("lines", "Context not available"),
                                "location": f"{result.get('path', 'Unknown')}:{result.get('start', {}).get('line', 0)}",
                                "file_name": result.get("path", "Unknown"),
                                "line_number": result.get("start", {}).get("line", 0),
                                "pci_requirement": self._get_pci_requirement_from_semgrep(result.get("check_id", "")),
                                "risk_level": self._get_risk_level_from_semgrep(result.get("severity", "")),
                                "remediation": result.get("extra", {}).get("message", "Fix this security issue")
                            }
                            findings.append(finding)
                        except Exception as e:
                            logger.warning(f"Error processing semgrep result: {str(e)}")
                except json.JSONDecodeError:
                    logger.warning("Failed to parse semgrep JSON output")
        except Exception as e:
            logger.warning(f"Failed to run semgrep: {str(e)}")
            raise
            
        return findings
    
    def _normalize_vulnerability_type(self, vuln_type: str) -> str:
        """
        Normalize vulnerability type to a readable form.
        
        Args:
            vuln_type: The raw vulnerability type
            
        Returns:
            Normalized vulnerability type
        """
        # Remove prefixes from semgrep rules
        if vuln_type.startswith("java."):
            vuln_type = vuln_type[5:]
        elif vuln_type.startswith("python."):
            vuln_type = vuln_type[7:]
        elif vuln_type.startswith("javascript."):
            vuln_type = vuln_type[11:]
        elif vuln_type.startswith("owasp."):
            vuln_type = vuln_type[6:]
        
        # Replace underscores and hyphens with spaces
        vuln_type = vuln_type.replace("_", " ").replace("-", " ")
        
        # Common normalization mappings
        normalization_map = {
            "sql injection": "SQL Injection",
            "sqli": "SQL Injection",
            "command injection": "Command Injection",
            "cmdi": "Command Injection",
            "xss": "Cross-Site Scripting (XSS)",
            "cross site scripting": "Cross-Site Scripting (XSS)",
            "csrf": "Cross-Site Request Forgery (CSRF)",
            "cross site request forgery": "Cross-Site Request Forgery (CSRF)",
            "path traversal": "Path Traversal",
            "weak crypto": "Weak Cryptography",
            "insecure configuration": "Insecure Configuration",
            "insecure deserialization": "Insecure Deserialization",
            "insecure random": "Insecure Randomness",
            "insecure hashing": "Insecure Hashing Algorithm",
            "xxe": "XML External Entity (XXE)",
            "ssrf": "Server-Side Request Forgery (SSRF)"
        }
        
        # Get normalized type or capitalize words
        lower_type = vuln_type.lower()
        for key, value in normalization_map.items():
            if key in lower_type:
                return value
                
        # If no match, capitalize each word
        return " ".join(word.capitalize() for word in vuln_type.split())
    
    def _get_pci_requirement(self, vuln_type: str) -> str:
        """
        Get the relevant PCI DSS requirement for a vulnerability type.
        
        Args:
            vuln_type: The vulnerability type
            
        Returns:
            PCI DSS requirement string
        """
        # Map vulnerability types to PCI DSS requirements
        mapping = {
            "sql_injection": "6.3.2, 6.3.3",
            "command_injection": "6.3.2, 6.3.3",
            "xss": "6.3.2, 6.3.3",
            "path_traversal": "6.3.2",
            "weak_crypto": "3.6.1, 4.1",
            "insecure_configuration": "2.2.1, 2.2.4, 6.3.3"
        }
        
        return mapping.get(vuln_type, "6.3.2")
    
    def _get_pci_requirement_from_semgrep(self, check_id: str) -> str:
        """
        Map semgrep check ID to PCI DSS requirement.
        
        Args:
            check_id: The semgrep check ID
            
        Returns:
            PCI DSS requirement string
        """
        if "injection" in check_id.lower() or "sqli" in check_id.lower():
            return "6.3.2, 6.3.3"
        elif "xss" in check_id.lower():
            return "6.3.2, 6.3.3"
        elif "csrf" in check_id.lower():
            return "6.3.2, 6.3.3"
        elif "path-traversal" in check_id.lower():
            return "6.3.2"
        elif "crypto" in check_id.lower() or "hash" in check_id.lower():
            return "3.6.1, 4.1"
        elif "config" in check_id.lower():
            return "2.2.1, 2.2.4, 6.3.3"
        elif "auth" in check_id.lower() or "password" in check_id.lower():
            return "8.2.3, 8.3.1"
        else:
            return "6.3.2"
    
    def _get_risk_level(self, vuln_type: str) -> str:
        """
        Determine risk level based on vulnerability type.
        
        Args:
            vuln_type: The vulnerability type
            
        Returns:
            Risk level as "High", "Medium", or "Low"
        """
        high_risk = ["sql_injection", "command_injection", "insecure_deserialization"]
        medium_risk = ["xss", "path_traversal", "weak_crypto"]
        
        if vuln_type in high_risk:
            return "High"
        elif vuln_type in medium_risk:
            return "Medium"
        else:
            return "Low"
    
    def _get_risk_level_from_semgrep(self, severity: str) -> str:
        """
        Convert semgrep severity to our risk level format.
        
        Args:
            severity: Semgrep severity
            
        Returns:
            Risk level as "High", "Medium", or "Low"
        """
        mapping = {
            "ERROR": "High",
            "WARNING": "Medium",
            "INFO": "Low"
        }
        
        return mapping.get(severity.upper(), "Medium")
    
    def _get_remediation(self, vuln_type: str) -> str:
        """
        Get remediation guidance for a vulnerability type.
        
        Args:
            vuln_type: The vulnerability type
            
        Returns:
            Remediation guidance
        """
        remediation_map = {
            "sql_injection": "Use parameterized queries, prepared statements, or ORM frameworks instead of string concatenation for SQL queries",
            "command_injection": "Use safe APIs for system commands, validate and sanitize user input, avoid directly passing user input to command execution functions",
            "xss": "Use proper output encoding appropriate for the context, implement Content Security Policy (CSP), and validate user input",
            "path_traversal": "Use secure file access APIs, validate and normalize file paths, restrict file access to specific directories",
            "weak_crypto": "Use strong cryptographic algorithms (AES-256, SHA-256, etc.) and securely manage encryption keys",
            "insecure_configuration": "Remove hardcoded credentials, implement proper access controls, and follow security configuration best practices"
        }
        
        return remediation_map.get(vuln_type, "Follow secure coding practices and address this vulnerability according to OWASP guidelines")