"""
Secrets Detector

This module provides capability to detect hardcoded secrets, credentials, API keys,
and other sensitive information in source code. It focuses on finding issues
relevant to PCI DSS requirement 3.3.3 for securing credentials.
"""

import os
import re
import subprocess
import json
import logging
import math
from typing import Dict, List, Any, Tuple, Optional

# Set up logging
logger = logging.getLogger("secrets_detector")

class SecretsDetector:
    """
    Detects hardcoded secrets, credentials, API keys, and other sensitive
    information in source code.
    """
    
    def __init__(self):
        """Initialize the Secrets Detector."""
        # Define patterns for different types of secrets
        self.secret_patterns = {
            "AWS_ACCESS_KEY": r"(?i)(ACCESS_KEY|AWS_ACCESS|AKIA)[A-Z0-9]{16,24}",
            "AWS_SECRET_KEY": r"(?i)(SECRET_KEY|AWS_SECRET)[A-Za-z0-9/+]{40}",
            "AWS_MWS_KEY": r"(?i)amzn\.mws\.[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            "API_KEY": r"(?i)(api_key|apikey|api token)[\"'= ]+[A-Za-z0-9_\-]{32,45}[\"']*",
            "AZURE_CONNECTION_STRING": r"(?i)AccountKey=[A-Za-z0-9+/=]{88}",
            "AZURE_SERVICE_KEY": r"(?i)serviceApiKey[ \"':=]+[A-Za-z0-9_\-]{32,45}[\"']*",
            "DATABASE_URI": r"(?i)(mongodb|mysql|postgresql|redis|jdbc|db|database)://[A-Za-z0-9:_\-\/\?\.=&%]+@[A-Za-z0-9:_\-\/\?\.=&%]+",
            "EMAIL_PASSWORD": r"(?i)(email|mail|smtp)_?password[ \"':=]+[A-Za-z0-9_\-\.\+\*\$\#]{6,30}[\"']*",
            "GENERIC_SECRET": r"(?i)(secret|token|key|credential|password)[ \"':=]+[A-Za-z0-9_\-\.\+\*\$\#\!]{8,45}[\"']*",
            "GENERIC_PASSWORD": r"(?i)(pass|pwd|passwd|password)[ \"':=]+[A-Za-z0-9_\-\.\+\*\$\#\!]{8,45}[\"']*",
            "GITHUB_PAT": r"(?i)gh[pousr]_[A-Za-z0-9_]{36,255}",
            "GOOGLE_API_KEY": r"(?i)AIza[0-9A-Za-z\-_]{35}",
            "GOOGLE_OAUTH_TOKEN": r"(?i)ya29\.[0-9A-Za-z\-_]+",
            "HEROKU_API_KEY": r"(?i)[hH][eE][rR][oO][kK][uU].*[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}",
            "JWT_TOKEN": r"(?i)eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*",
            "MAILCHIMP_API_KEY": r"(?i)[0-9a-f]{32}-us[0-9]{1,2}",
            "PGP_PRIVATE_KEY": r"(?i)-{5}BEGIN PGP PRIVATE KEY BLOCK-{5}[A-Za-z0-9/\n+=]*-{5}END PGP PRIVATE KEY BLOCK-{5}",
            "PRIVATE_KEY": r"(?i)-{5}BEGIN (RSA|OPENSSH|DSA|EC) PRIVATE KEY-{5}[A-Za-z0-9/\n+=]*-{5}END (RSA|OPENSSH|DSA|EC) PRIVATE KEY-{5}",
            "SLACK_TOKEN": r"(?i)xox[baprs]-[0-9]{12}-[0-9]{12}-[0-9]{12}-[a-z0-9]{32}",
            "SLACK_WEBHOOK": r"(?i)https://hooks.slack.com/services/T[a-zA-Z0-9_]{8}/B[a-zA-Z0-9_]{8}/[a-zA-Z0-9_]{24}",
            "SQUARE_ACCESS_TOKEN": r"(?i)sq0atp-[0-9A-Za-z\-_]{22}",
            "SQUARE_OAUTH_SECRET": r"(?i)sq0csp-[0-9A-Za-z\-_]{43}",
            "STRIPE_API_KEY": r"(?i)sk_live_[0-9a-zA-Z]{24}",
            "STRIPE_PUBLISHABLE_KEY": r"(?i)pk_live_[0-9a-zA-Z]{24}",
            "TWILIO_API_KEY": r"(?i)SK[0-9a-fA-F]{32}",
            "TWITTER_ACCESS_TOKEN": r"(?i)[1-9][0-9]+-[0-9a-zA-Z]{40}"
        }
        
        # Define environment variable patterns
        self.env_var_patterns = [
            r'(?i)os\.environ\[[\'"](.*?)[\'"]\]',  # Python
            r'(?i)process\.env\.(.*?)[;\s]',        # JavaScript/Node.js
            r'(?i)System\.getenv\([\'"](.+?)[\'"]\)',  # Java
            r'(?i)getenv\([\'"](.+?)[\'"]\)',       # PHP, C
            r'(?i)ENV\[[\'"](.+?)[\'"]\]',          # Ruby
            r'(?i)Environment\.GetEnvironmentVariable\([\'"](.+?)[\'"]\)'  # C#
        ]
        
        # Files to exclude from scanning
        self.exclude_patterns = [
            r'.*\.git/.*',
            r'.*node_modules/.*',
            r'.*\.venv/.*',
            r'.*venv/.*',
            r'.*\.env\.example',
            r'.*\.env\.sample',
            r'.*\.env\.template',
            r'.*test/.*',
            r'.*example/.*',
            r'.*vendor/.*',
            r'.*dist/.*',
            r'.*build/.*',
            r'.*LICENSE',
            r'.*README\.md'
        ]
        
        # Mappings of file extensions to language
        self.extension_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cs': 'C#',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.go': 'Go',
            '.rs': 'Rust',
            '.sh': 'Shell',
            '.json': 'JSON',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.xml': 'XML',
            '.properties': 'Properties',
            '.env': 'Environment Variables',
            '.ini': 'INI',
            '.conf': 'Configuration',
            '.tf': 'Terraform',
            '.tfvars': 'Terraform Variables'
        }
        
        logger.info("Secrets Detector initialized with pattern databases")
    
    def detect(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        Detect secrets in the given directory.
        
        Args:
            directory_path: Path to the directory to scan
            
        Returns:
            List of secret findings
        """
        findings = []
        
        # Try to use specialized tools if available
        try:
            # Try to use TruffleHog if available
            trufflehog_findings = self._run_trufflehog(directory_path)
            if trufflehog_findings:
                findings.extend(trufflehog_findings)
                logger.info(f"Found {len(trufflehog_findings)} secrets with TruffleHog")
                
                # If TruffleHog worked, we can return early as it's more comprehensive
                if len(trufflehog_findings) > 0:
                    return findings
        except Exception as e:
            logger.info(f"TruffleHog not available or failed, using built-in detection: {str(e)}")
        
        # Fall back to built-in detection
        logger.info("Using built-in secrets detection")
        
        # Walk through directory
        for root, _, files in os.walk(directory_path):
            # Check if this directory should be excluded
            if self._should_exclude(root):
                continue
                
            for file in files:
                file_path = os.path.join(root, file)
                
                # Check if this file should be excluded
                if self._should_exclude(file_path):
                    continue
                    
                # Get file extension
                _, ext = os.path.splitext(file_path)
                
                # Skip binary files
                if self._is_binary_file(file_path):
                    continue
                    
                # Get relative path for reporting
                rel_path = os.path.relpath(file_path, directory_path)
                
                # Read file content
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception as e:
                    logger.warning(f"Error reading file {file_path}: {str(e)}")
                    continue
                
                # Get the language for this file
                language = self.extension_map.get(ext.lower(), 'Unknown')
                
                # Scan for secrets
                file_findings = self._scan_content_for_secrets(content, rel_path, language)
                
                # Add entropy analysis for additional detections
                entropy_findings = self._detect_high_entropy_strings(content, rel_path)
                
                # Combine findings
                findings.extend(file_findings)
                findings.extend(entropy_findings)
        
        # Check for exposed environment variables
        env_findings = self._check_environment_variables(directory_path)
        findings.extend(env_findings)
        
        logger.info(f"Found {len(findings)} secrets using built-in detection")
        return findings
    
    def _scan_content_for_secrets(self, content: str, file_path: str, language: str) -> List[Dict[str, Any]]:
        """
        Scan file content for secrets using regex patterns.
        
        Args:
            content: The file content
            file_path: The file path for reporting
            language: The programming language
            
        Returns:
            List of secret findings
        """
        findings = []
        
        # Split content into lines for better reporting
        lines = content.split('\n')
        
        # Scan for each secret type
        for secret_type, pattern in self.secret_patterns.items():
            try:
                for match in re.finditer(pattern, content, re.MULTILINE):
                    # Find line number by counting newlines before match
                    line_number = content[:match.start()].count('\n') + 1
                    
                    # Get the matched line for context
                    line_content = lines[line_number - 1] if line_number <= len(lines) else "Context not available"
                    
                    # Extract the matched string
                    matched_string = match.group(0)
                    
                    # Skip if it looks like an environment variable reference
                    if self._is_env_var_reference(matched_string, language):
                        continue
                    
                    # Mask the secret value for reporting (show first 3 and last 3 chars only)
                    masked_value = self._mask_secret(matched_string)
                    
                    # Create finding
                    finding = {
                        "type": f"Hardcoded Secret: {secret_type}",
                        "value": masked_value,
                        "location": f"{file_path}:{line_number}",
                        "file_name": file_path,
                        "line_number": line_number,
                        "risk_level": "High",
                        "pci_requirement": "3.3.3, 6.3.2",
                        "reason": f"Hardcoded {secret_type} found in source code. This violates PCI DSS 3.3.3 which requires strong cryptography for stored credentials.",
                        "remediation": "Store this secret in an environment variable or a secure secrets management system like AWS Secrets Manager or HashiCorp Vault."
                    }
                    
                    findings.append(finding)
            except Exception as e:
                logger.warning(f"Error scanning for {secret_type} in {file_path}: {str(e)}")
        
        return findings
    
    def _detect_high_entropy_strings(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Detect strings with high entropy that may be secrets.
        
        Args:
            content: The file content
            file_path: The file path for reporting
            
        Returns:
            List of high entropy findings
        """
        findings = []
        
        # Split content into lines for analysis
        lines = content.split('\n')
        
        # Patterns to extract strings that might be secrets
        string_patterns = [
            r'"([A-Za-z0-9+/=_\-\.]{16,64})"',  # Double-quoted strings
            r"'([A-Za-z0-9+/=_\-\.]{16,64})'",  # Single-quoted strings
            r"`([A-Za-z0-9+/=_\-\.]{16,64})`"   # Backtick quoted strings
        ]
        
        # Analyze each line
        for line_number, line in enumerate(lines, 1):
            # Skip short lines
            if len(line.strip()) < 20:
                continue
                
            # Skip common code patterns that are unlikely to be secrets
            if "import " in line or "require(" in line or "return " in line:
                continue
                
            # Extract potential strings
            for pattern in string_patterns:
                for match in re.finditer(pattern, line):
                    string_value = match.group(1)
                    
                    # Skip short strings
                    if len(string_value) < 16:
                        continue
                        
                    # Calculate entropy
                    entropy = self._calculate_shannon_entropy(string_value)
                    
                    # High entropy suggests possible secret
                    if entropy > 4.0:
                        # Skip if it's a URL, file path, or known non-secret pattern
                        if self._is_false_positive(string_value):
                            continue
                            
                        # Mask the value for reporting
                        masked_value = self._mask_secret(string_value)
                        
                        # Create finding
                        finding = {
                            "type": "High Entropy String (Possible Secret)",
                            "value": masked_value,
                            "location": f"{file_path}:{line_number}",
                            "file_name": file_path,
                            "line_number": line_number,
                            "risk_level": "Medium",
                            "pci_requirement": "3.3.3",
                            "reason": f"String with high entropy (randomness) detected (entropy: {entropy:.2f}). This may be a hardcoded secret or credential.",
                            "remediation": "Verify if this is a secret. If so, store it in an environment variable or a secure secrets management system."
                        }
                        
                        findings.append(finding)
        
        return findings
    
    def _calculate_shannon_entropy(self, string: str) -> float:
        """
        Calculate the Shannon entropy of a string (measure of randomness).
        
        Args:
            string: The string to analyze
            
        Returns:
            Entropy value (higher values indicate more randomness)
        """
        # Count frequency of each character
        char_count = {}
        for char in string:
            if char in char_count:
                char_count[char] += 1
            else:
                char_count[char] = 1
        
        # Calculate entropy
        entropy = 0.0
        for count in char_count.values():
            freq = count / len(string)
            entropy -= freq * math.log2(freq)
        
        return entropy
    
    def _check_environment_variables(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        Check for environment variables that should be used instead of hardcoded secrets.
        
        Args:
            directory_path: Path to the directory to scan
            
        Returns:
            List of findings for missing environment variables
        """
        findings = []
        env_vars = set()
        
        # Walk through directory to find references to environment variables
        for root, _, files in os.walk(directory_path):
            # Skip excluded directories
            if self._should_exclude(root):
                continue
                
            for file in files:
                file_path = os.path.join(root, file)
                
                # Skip if excluded or binary
                if self._should_exclude(file_path) or self._is_binary_file(file_path):
                    continue
                    
                # Read file content
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception as e:
                    continue
                
                # Get relative path for reporting
                rel_path = os.path.relpath(file_path, directory_path)
                
                # Look for environment variable references
                for pattern in self.env_var_patterns:
                    for match in re.finditer(pattern, content):
                        var_name = match.group(1)
                        
                        # Skip common non-secret env vars
                        if var_name.lower() in ["port", "host", "debug", "env", "path", "lang", "home", "user"]:
                            continue
                            
                        # Add to set of environment variables
                        env_vars.add(var_name)
        
        # Check for environment file
        env_files = [".env", ".env.local", ".env.development", ".env.production"]
        env_file_path = None
        
        for env_file in env_files:
            path = os.path.join(directory_path, env_file)
            if os.path.exists(path):
                env_file_path = path
                break
        
        # If an .env file was found, check if it's excluded from version control
        if env_file_path:
            # Get relative path for reporting
            rel_path = os.path.relpath(env_file_path, directory_path)
            
            # Check if .env file is committed (it shouldn't be)
            gitignore_path = os.path.join(directory_path, ".gitignore")
            if os.path.exists(gitignore_path):
                try:
                    with open(gitignore_path, 'r', encoding='utf-8') as f:
                        gitignore_content = f.read()
                        
                    # Check if .env is excluded
                    env_excluded = False
                    for line in gitignore_content.split('\n'):
                        line = line.strip()
                        if line == ".env" or line == "*.env" or line.startswith(".env"):
                            env_excluded = True
                            break
                            
                    if not env_excluded:
                        # Create finding for .env not being excluded from version control
                        finding = {
                            "type": "Environment File Not Excluded",
                            "value": ".env file may be committed to version control",
                            "location": ".gitignore",
                            "file_name": ".gitignore",
                            "risk_level": "High",
                            "pci_requirement": "3.3.3",
                            "reason": ".env file containing secrets is not excluded from version control in .gitignore",
                            "remediation": "Add '.env' to your .gitignore file to prevent committing secrets to version control"
                        }
                        findings.append(finding)
                except Exception as e:
                    logger.warning(f"Error reading .gitignore: {str(e)}")
            
            # Read the .env file to see if it contains real secrets or just examples
            try:
                with open(env_file_path, 'r', encoding='utf-8') as f:
                    env_content = f.read()
                    
                # Check if this is a real .env file or an example
                if "example" not in env_file_path.lower() and "sample" not in env_file_path.lower():
                    # Create finding for committed secrets in .env file
                    finding = {
                        "type": "Committed Environment File",
                        "value": f"{rel_path} may contain secrets",
                        "location": rel_path,
                        "file_name": rel_path,
                        "risk_level": "High",
                        "pci_requirement": "3.3.3",
                        "reason": f"{rel_path} file may contain secrets and should not be committed to version control",
                        "remediation": f"Remove {rel_path} from version control, add it to .gitignore, and provide a template file instead"
                    }
                    findings.append(finding)
            except Exception as e:
                logger.warning(f"Error reading .env file: {str(e)}")
        
        return findings
    
    def _is_binary_file(self, file_path: str) -> bool:
        """
        Check if a file is binary.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file is binary, False otherwise
        """
        # Check file extension for common binary formats
        binary_extensions = [
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.zip', '.tar', '.gz', '.tgz', '.rar', '.7z',
            '.exe', '.dll', '.so', '.dylib', '.bin', '.dat',
            '.mp3', '.mp4', '.avi', '.mov', '.flv', '.wav'
        ]
        
        _, ext = os.path.splitext(file_path)
        if ext.lower() in binary_extensions:
            return True
            
        # Check file content
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                if b'\0' in chunk:  # Binary files often contain null bytes
                    return True
                    
                # Check if file is mostly non-ASCII
                text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x7F)))
                return bool(chunk.translate(None, text_chars))
        except Exception:
            # If we can't read the file, assume it's not binary
            return False
            
        return False
    
    def _should_exclude(self, path: str) -> bool:
        """
        Check if a path should be excluded from scanning.
        
        Args:
            path: The path to check
            
        Returns:
            True if the path should be excluded, False otherwise
        """
        for pattern in self.exclude_patterns:
            if re.match(pattern, path):
                return True
                
        return False
    
    def _is_env_var_reference(self, string: str, language: str) -> bool:
        """
        Check if a string is a reference to an environment variable.
        
        Args:
            string: The string to check
            language: The programming language
            
        Returns:
            True if the string is an environment variable reference, False otherwise
        """
        # Python environment variable reference
        if language == "Python" and ("os.environ" in string or "os.getenv" in string):
            return True
            
        # Node.js environment variable reference
        if language in ["JavaScript", "TypeScript"] and "process.env" in string:
            return True
            
        # Java environment variable reference
        if language == "Java" and "System.getenv" in string:
            return True
            
        # C# environment variable reference
        if language == "C#" and "Environment.GetEnvironmentVariable" in string:
            return True
            
        # PHP environment variable reference
        if language == "PHP" and ("getenv" in string or "$_ENV" in string):
            return True
            
        # Ruby environment variable reference
        if language == "Ruby" and "ENV[" in string:
            return True
            
        return False
    
    def _is_false_positive(self, string: str) -> bool:
        """
        Check if a string is likely to be a false positive.
        
        Args:
            string: The string to check
            
        Returns:
            True if the string is likely a false positive, False otherwise
        """
        # Check if it's a URL
        if string.startswith(("http://", "https://", "ftp://", "file://")):
            return True
            
        # Check if it's a file path
        if "/" in string and "." in string:
            if re.match(r'^[\/\w\.\-]+$', string):
                return True
                
        # Check if it's a base64-encoded image
        if string.startswith(("data:image/", "data:application/")):
            return True
            
        # Check for UUID pattern
        if re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', string.lower()):
            return True
            
        # Check for HTML/XML content
        if "<" in string and ">" in string:
            return True
            
        return False
    
    def _mask_secret(self, secret: str) -> str:
        """
        Mask a secret for reporting.
        
        Args:
            secret: The secret to mask
            
        Returns:
            Masked secret
        """
        if len(secret) <= 6:
            return "******"
            
        return secret[:3] + "****" + secret[-3:]
    
    def _run_trufflehog(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        Run TruffleHog tool for secret detection if available.
        
        Args:
            directory_path: Path to the directory to scan
            
        Returns:
            List of secret findings
        """
        findings = []
        
        try:
            # Run TruffleHog
            result = subprocess.run(
                ["trufflehog", "filesystem", "--json", directory_path],
                capture_output=True,
                text=True,
                check=False  # Don't raise an exception on non-zero exit code
            )
            
            # Parse TruffleHog output
            for line in result.stdout.splitlines():
                if not line.strip():
                    continue
                    
                try:
                    finding_json = json.loads(line)
                    
                    # Extract information from TruffleHog finding
                    secret_type = finding_json.get("DetectorType", "Unknown Secret")
                    file_path = finding_json.get("SourceMetadata", {}).get("Data", {}).get("Filesystem", {}).get("file", "Unknown")
                    line_number = finding_json.get("SourceMetadata", {}).get("Data", {}).get("Filesystem", {}).get("line", 0)
                    
                    # Get relative path if directory_path is provided
                    if os.path.isabs(file_path) and directory_path:
                        try:
                            file_path = os.path.relpath(file_path, directory_path)
                        except ValueError:
                            # Keep the absolute path if relpath fails
                            pass
                    
                    # Mask the secret for reporting
                    secret_value = finding_json.get("Raw", "")
                    masked_value = self._mask_secret(secret_value) if secret_value else "********"
                    
                    # Create finding
                    finding = {
                        "type": f"Hardcoded Secret: {secret_type}",
                        "value": masked_value,
                        "location": f"{file_path}:{line_number}" if line_number else file_path,
                        "file_name": file_path,
                        "line_number": line_number if line_number else 0,
                        "risk_level": "High",
                        "pci_requirement": "3.3.3, 6.3.2",
                        "reason": f"Hardcoded {secret_type} found with TruffleHog scanner. This violates PCI DSS 3.3.3 which requires strong cryptography for stored credentials.",
                        "remediation": "Store this secret in an environment variable or a secure secrets management system like AWS Secrets Manager or HashiCorp Vault."
                    }
                    
                    findings.append(finding)
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            raise Exception(f"Failed to run TruffleHog: {str(e)}")
            
        return findings