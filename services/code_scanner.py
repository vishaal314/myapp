import os
import re
import json
import math
import hashlib
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set
from utils.pii_detection import identify_pii_in_text
from utils.gdpr_rules import get_region_rules, evaluate_risk_level

class CodeScanner:
    """
    An advanced scanner that detects PII, secrets, and sensitive information in code files.
    Supports multiple languages and regulatory frameworks.
    """
    
    def __init__(self, extensions: Optional[List[str]] = None, include_comments: bool = True, 
                 region: str = "Netherlands", use_entropy: bool = True, 
                 use_git_metadata: bool = False, include_article_refs: bool = True):
        """
        Initialize the code scanner with advanced detection capabilities.
        
        Args:
            extensions: List of file extensions to scan (e.g., ['.py', '.js'])
            include_comments: Whether to include comments in the scan
            region: The region for which to apply GDPR rules
            use_entropy: Whether to use entropy analysis for secret detection
            use_git_metadata: Whether to collect Git metadata for findings
            include_article_refs: Whether to include regulatory article references
        """
        # Support for multiple languages
        self.extensions = extensions or [
            # Core programming languages
            '.py', '.pyw', '.pyx', '.pyi',  # Python
            '.js', '.jsx', '.mjs',          # JavaScript
            '.ts', '.tsx',                  # TypeScript
            '.java', '.jsp', '.jav',        # Java
            '.php', '.phtml',               # PHP
            '.rb', '.rhtml', '.erb',        # Ruby
            '.cs', '.cshtml', '.csx',       # C#
            '.go',                          # Go
            '.rs',                          # Rust
            '.c', '.cpp', '.cc', '.h',      # C/C++
            '.kt', '.kts',                  # Kotlin
            '.swift',                       # Swift
            
            # Infrastructure as Code
            '.tf', '.tfvars',               # Terraform
            '.yml', '.yaml',                # YAML
            '.json',                        # JSON
            '.xml',                         # XML
            
            # Web
            '.html', '.htm', '.xhtml',      # HTML
            '.css', '.scss', '.sass',       # CSS
            
            # Other
            '.sql',                         # SQL
            '.sh', '.bash',                 # Bash
            '.ps1', '.psm1',                # PowerShell
            '.env',                         # Environment files
            '.properties', '.conf', '.ini', # Config files
            '.md', '.txt'                   # Documentation
        ]
        
        self.include_comments = include_comments
        self.region = region
        self.region_rules = get_region_rules(region)
        self.use_entropy = use_entropy
        self.use_git_metadata = use_git_metadata
        self.include_article_refs = include_article_refs
        
        # Enhanced regex patterns for secrets and PII detection by provider
        self.secret_patterns = {
            # General API keys and tokens
            'api_key': r'(?i)(api[_-]?key|apikey)[^\w\n]*?[\'"=:]+[^\w\n]*?([\w\-]{20,64})',
            'auth_token': r'(?i)(auth[_-]token|oauth|bearer|jwt)[^\w\n]*?[\'"=:]+[^\w\n]*?([^\s;,]{30,64})',
            'generic_secret': r'(?i)(secret|key|token)[^\w\n]*?[\'"=:]+[^\w\n]*?([^\s;,]{16,64})',
            
            # AWS
            'aws_access_key': r'(?i)(AWS|AKIA)[^\w\n]*?(ACCESS|SECRET)[^\w\n]*?(KEY)[^\w\n]*?[\'"=:]+[^\w\n]*?([A-Za-z0-9/+=]{16,40})',
            'aws_key_id': r'(?i)(AKIA[0-9A-Z]{16})',
            'aws_secret': r'(?i)(aws[^\w\n]*?([\'"]?(?:access|secret)[_-]?key[\'"]?)[^\w\n]*?[\'"=:]+[^\w\n]*?([A-Za-z0-9/+=]{40}))',
            
            # Azure
            'azure_key': r'(?i)(azure[^\w\n]*?(key|token|secret))[^\w\n]*?[\'"=:]+[^\w\n]*?([A-Za-z0-9+/=]{44})',
            'azure_connection': r'(?i)(DefaultEndpointsProtocol=https)(.*?)(AccountKey=[A-Za-z0-9+/=]{88})',
            'azure_storage': r'(?i)(BlobEndpoint|QueueEndpoint|TableEndpoint|FileEndpoint)(=https://[a-z0-9]+\.)(blob|queue|table|file)(\.core\.windows\.net/)',
            
            # Google Cloud
            'gcp_api_key': r'(?i)(AIza[0-9A-Za-z\-_]{35})',
            'gcp_service_account': r'(?i)("type": "service_account"[.\s\S]*?"private_key": "[^"]*")',
            
            # Payment processors
            'stripe_key': r'(?i)(sk_live_|pk_live_)([a-zA-Z0-9]{24})',
            'stripe_test_key': r'(?i)(sk_test_|pk_test_)([a-zA-Z0-9]{24})',
            'paypal_key': r'(?i)(access_token\$production\$[0-9a-z]{16}\$[0-9a-f]{32})',
            'braintree_key': r'(?i)(access_token\$sandbox\$[0-9a-z]{16}\$[0-9a-f]{32})',
            
            # Database
            'connection_string': r'(?i)(mongodb|mysql|postgresql|jdbc|sqlserver|oracle|redis)(://|:|@)([^\s;,]*:[^\s;,]*@)([a-zA-Z0-9.-]+)(:[0-9]+)?',
            'mongodb_uri': r'(?i)(mongodb(?:\+srv)?://[^:]+:[^@]+@[^/]+)',
            'mysql_conn': r'(?i)(mysql://[^:]+:[^@]+@[^/]+)',
            'postgres_conn': r'(?i)(postgres(?:ql)?://[^:]+:[^@]+@[^/]+)',
            
            # Social media
            'twitter_key': r'(?i)(twitter[^\w\n]*?(api|secret|token)[^\w\n]*?key)[^\w\n]*?[\'"=:]+[^\w\n]*?([a-zA-Z0-9]{35,44})',
            'facebook_key': r'(?i)(facebook[^\w\n]*?(api|secret|app|client)[^\w\n]*?(key|id|token))[^\w\n]*?[\'"=:]+[^\w\n]*?([a-zA-Z0-9]{32,40})',
            'github_token': r'(?i)(gh[pousr]_[a-zA-Z0-9_]{36})',
            
            # Passwords
            'password': r'(?i)(password|passwd|pwd)[^\w\n]*?[\'"=:]+[^\w\n]*?([^\s;,]{8,32})',
            'passwd_assignment': r'(?i)(password|passwd|pwd)\s*(=|:=|:)\s*["\']([^"\']{8,32})["\']'
        }
        
        # Map of file extensions to language-specific comment patterns
        self.comment_patterns = {
            # Python
            '.py': [r'#.*?$', r'""".*?"""', r"'''.*?'''"],
            '.pyw': [r'#.*?$', r'""".*?"""', r"'''.*?'''"],
            '.pyx': [r'#.*?$', r'""".*?"""', r"'''.*?'''"],
            '.pyi': [r'#.*?$', r'""".*?"""', r"'''.*?'''"],
            
            # JavaScript/TypeScript
            '.js': [r'//.*?$', r'/\*.*?\*/', r'<!--.*?-->'],
            '.jsx': [r'//.*?$', r'/\*.*?\*/', r'<!--.*?-->'],
            '.mjs': [r'//.*?$', r'/\*.*?\*/'],
            '.ts': [r'//.*?$', r'/\*.*?\*/'],
            '.tsx': [r'//.*?$', r'/\*.*?\*/', r'<!--.*?-->'],
            
            # Java
            '.java': [r'//.*?$', r'/\*.*?\*/'],
            '.jsp': [r'//.*?$', r'/\*.*?\*/', r'<!--.*?-->', r'<%--.*?--%>'],
            '.jav': [r'//.*?$', r'/\*.*?\*/'],
            
            # PHP
            '.php': [r'//.*?$', r'/\*.*?\*/', r'#.*?$', r'<!--.*?-->'],
            '.phtml': [r'//.*?$', r'/\*.*?\*/', r'#.*?$', r'<!--.*?-->'],
            
            # Ruby
            '.rb': [r'#.*?$', r'=begin.*?=end'],
            '.rhtml': [r'#.*?$', r'<!--.*?-->'],
            '.erb': [r'#.*?$', r'<%#.*?%>', r'<!--.*?-->'],
            
            # C#
            '.cs': [r'//.*?$', r'/\*.*?\*/'],
            '.cshtml': [r'//.*?$', r'/\*.*?\*/', r'<!--.*?-->'],
            '.csx': [r'//.*?$', r'/\*.*?\*/'],
            
            # Go
            '.go': [r'//.*?$', r'/\*.*?\*/'],
            
            # Rust
            '.rs': [r'//.*?$', r'/\*.*?\*/'],
            
            # C/C++
            '.c': [r'//.*?$', r'/\*.*?\*/'],
            '.cpp': [r'//.*?$', r'/\*.*?\*/'],
            '.cc': [r'//.*?$', r'/\*.*?\*/'],
            '.h': [r'//.*?$', r'/\*.*?\*/'],
            '.hpp': [r'//.*?$', r'/\*.*?\*/'],
            
            # Kotlin
            '.kt': [r'//.*?$', r'/\*.*?\*/'],
            '.kts': [r'//.*?$', r'/\*.*?\*/'],
            
            # Swift
            '.swift': [r'//.*?$', r'/\*.*?\*/'],
            
            # Terraform
            '.tf': [r'#.*?$', r'/\*.*?\*/'],
            '.tfvars': [r'#.*?$', r'/\*.*?\*/'],
            
            # YAML
            '.yml': [r'#.*?$'],
            '.yaml': [r'#.*?$'],
            
            # HTML/CSS
            '.html': [r'<!--.*?-->'],
            '.htm': [r'<!--.*?-->'],
            '.xhtml': [r'<!--.*?-->'],
            '.css': [r'/\*.*?\*/'],
            '.scss': [r'/\*.*?\*/', r'//.*?$'],
            '.sass': [r'/\*.*?\*/', r'//.*?$'],
            
            # SQL
            '.sql': [r'--.*?$', r'/\*.*?\*/'],
            
            # Bash
            '.sh': [r'#.*?$'],
            '.bash': [r'#.*?$'],
            
            # PowerShell
            '.ps1': [r'#.*?$', r'<#.*?#>'],
            '.psm1': [r'#.*?$', r'<#.*?#>'],
            
            # Config files
            '.env': [r'#.*?$'],
            '.properties': [r'#.*?$'],
            '.conf': [r'#.*?$'],
            '.ini': [r';.*?$'],
            
            # Documentation
            '.md': [r'<!--.*?-->'],
            '.txt': []
        }
        
        # Regulatory frameworks mapped to article references
        self.regulatory_refs = {
            "GDPR (EU)": {
                "PII": "Art. 4(1)",
                "Sensitive Data": "Art. 9",
                "Data Processing": "Art. 6",
                "Children's Data": "Art. 8",
                "Data Subject Rights": "Art. 15-22",
                "Security": "Art. 32",
                "Consent": "Art. 7"
            },
            "UAVG (NL)": {
                "BSN": "Art. 46",
                "Criminal Data": "Art. 31-33",
                "Health Data": "Art. 30",
                "Data for Research": "Art. 43-47",
                "Special Categories": "Art. 22-30"
            },
            "BDSG (DE)": {
                "Employee Data": "§26",
                "Credit Scoring": "§31",
                "Video Surveillance": "§4",
                "Special Categories": "§22",
                "Automated Decisions": "§37"
            },
            "CNIL (FR)": {
                "Health Data": "Articles L1111-7 and L1111-8 of the Public Health Code",
                "Biometric Data": "Deliberation No. 2019-001",
                "Financial Data": "Deliberation No. 2018-303"
            },
            "DPA (UK)": {
                "PII": "Section 3",
                "Special Categories": "Section 10",
                "Criminal Data": "Section 11",
                "Automated Decisions": "Section 14"
            }
        }
        
        # Known providers patterns for API keys and secrets
        self.known_providers = {
            "AWS": [
                r'AKIA[0-9A-Z]{16}',
                r'aws_access_key_id',
                r'aws_secret_access_key'
            ],
            "Azure": [
                r'DefaultEndpointsProtocol=https',
                r'AccountKey=',
                r'StorageAccountKey=',
                r'azure_storage_key',
                r'azure_connection_string'
            ],
            "GCP": [
                r'AIza[0-9A-Za-z\-_]{35}',
                r'"type": "service_account"',
                r'GOOG[0-9A-Za-z\-_]{32}'
            ],
            "Stripe": [
                r'sk_live_[0-9a-zA-Z]{24}',
                r'pk_live_[0-9a-zA-Z]{24}',
                r'sk_test_[0-9a-zA-Z]{24}',
                r'pk_test_[0-9a-zA-Z]{24}'
            ],
            "GitHub": [
                r'gh[pousr]_[a-zA-Z0-9_]{36}',
                r'github_token',
                r'GITHUB_TOKEN'
            ],
            "Twilio": [
                r'SK[0-9a-fA-F]{32}',
                r'AC[a-zA-Z0-9]{32}',
                r'twilio_account_sid',
                r'twilio_auth_token'
            ],
            "SendGrid": [
                r'SG\.[0-9A-Za-z\-_]{22}\.[0-9A-Za-z\-_]{43}',
                r'sendgrid_api_key'
            ],
            "MailChimp": [
                r'[0-9a-f]{32}-us[0-9]{1,2}',
                r'mailchimp_api_key'
            ],
            "Slack": [
                r'xox[baprs]-[0-9]{12}-[0-9]{12}-[0-9a-zA-Z]{24}',
                r'slack_token',
                r'slack_api_token'
            ],
            "NPM": [
                r'npm_[0-9a-zA-Z]{36}',
                r'NPM_TOKEN'
            ],
            "Heroku": [
                r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}',
                r'heroku_api_key'
            ],
            "Facebook": [
                r'EAACEdEose0cBA[0-9A-Za-z]+',
                r'[A-Za-z0-9]{30,}',
                r'facebook_client_secret'
            ]
        }
        
    def scan_file(self, file_path: str) -> Dict[str, Any]:
        """
        Scan a single file for PII and secrets using advanced detection techniques.
        
        Args:
            file_path: Path to the file to scan
            
        Returns:
            Dictionary containing scan results with detailed metadata
        """
        if not os.path.isfile(file_path):
            return {
                'file_name': os.path.basename(file_path),
                'status': 'error',
                'error': 'File not found',
                'pii_found': []
            }
        
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in self.extensions:
            return {
                'file_name': os.path.basename(file_path),
                'status': 'skipped',
                'reason': f'File extension {ext} not in scan list',
                'pii_found': []
            }
        
        try:
            # Get file metadata including Git info if available
            file_metadata = self._get_file_metadata(file_path)
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # First, extract code and comments separately
            code_content = content
            comments = []
            
            if not self.include_comments:
                # Remove comments from code if not including them
                for ext_pattern in self.comment_patterns.keys():
                    if ext.lower().endswith(ext_pattern):
                        for pattern in self.comment_patterns[ext_pattern]:
                            # Extract comments before removing them
                            if ext_pattern in self.comment_patterns:
                                # For languages with multiline comments
                                comment_matches = re.finditer(pattern, code_content, re.DOTALL | re.MULTILINE)
                                for match in comment_matches:
                                    comments.append(match.group(0))
                            
                            # Remove comments from code content
                            code_content = re.sub(pattern, '', code_content, flags=re.DOTALL | re.MULTILINE)
            
            # Find PII in code
            pii_in_code = self._scan_content(code_content, "code", file_path)
            
            # Find PII in comments if included
            pii_in_comments = []
            if self.include_comments and comments:
                comments_text = '\n'.join(comments)
                pii_in_comments = self._scan_content(comments_text, "comment", file_path)
            
            # Combine results
            all_pii = pii_in_code + pii_in_comments
            
            # Scan for secrets using regex patterns
            for secret_type, pattern in self.secret_patterns.items():
                for match in re.finditer(pattern, content, re.MULTILINE | re.DOTALL):
                    if len(match.groups()) >= 2:
                        # Variable name is in group 1, value in group 2
                        var_name = match.group(1)
                        value = match.group(2)
                        
                        # Find line number
                        line_no = content[:match.start()].count('\n') + 1
                        
                        # Identify provider if possible
                        provider = self._identify_provider(var_name, value)
                        
                        # Calculate entropy if enabled
                        entropy_score = None
                        if self.use_entropy:
                            entropy_score = self._calculate_entropy(value)
                            if len(value) < 8 or entropy_score < 3.5:  # Low entropy threshold
                                continue  # Skip if entropy is too low (likely not a secret)
                        
                        # Add regulatory references if enabled
                        reg_refs = {}
                        if self.include_article_refs:
                            reg_refs = self._get_regulation_references("Secret")
                        
                        # Add to PII findings with enriched metadata
                        finding = {
                            'type': f'Secret ({secret_type})',
                            'value': f'{var_name}: {value[:3]}***{value[-3:]}',  # Mask the actual value
                            'location': f'Line {line_no}',
                            'risk_level': 'High',
                            'reason': f'Hardcoded {secret_type} found'
                        }
                        
                        # Add additional metadata if available
                        if provider:
                            finding['provider'] = provider
                        if entropy_score is not None:
                            finding['entropy'] = str(round(entropy_score, 2))
                        if reg_refs:
                            finding['regulatory_references'] = json.dumps(reg_refs)
                        if file_metadata.get('git'):
                            finding['git_metadata'] = json.dumps(file_metadata['git'])
                        
                        all_pii.append(finding)
            
            # Use entropy analysis for additional secret detection
            if self.use_entropy:
                entropy_findings = self._detect_high_entropy_strings(content, file_path)
                all_pii.extend(entropy_findings)
            
            # Create results with detailed metadata
            result = {
                'file_name': os.path.basename(file_path),
                'file_path': file_path,
                'status': 'scanned',
                'file_size': os.path.getsize(file_path),
                'file_type': ext.lower(),
                'scan_timestamp': datetime.now().isoformat(),
                'pii_found': all_pii,
                'pii_count': len(all_pii),
                'metadata': file_metadata
            }
            
            # Group findings by type for easier reporting
            risk_levels = {'High': 0, 'Medium': 0, 'Low': 0}
            pii_types = {}
            
            for pii in all_pii:
                # Count risk levels
                if 'risk_level' in pii and pii['risk_level'] in risk_levels:
                    risk_levels[pii['risk_level']] += 1
                
                # Count PII types
                pii_type = pii['type']
                if pii_type in pii_types:
                    pii_types[pii_type] += 1
                else:
                    pii_types[pii_type] = 1
            
            result['risk_summary'] = risk_levels
            result['pii_types_summary'] = pii_types
            
            # Add CI/CD compatibility fields
            result['ci_cd'] = {
                'has_critical_findings': risk_levels['High'] > 0,
                'exit_code': 1 if risk_levels['High'] > 0 else 0,
                'scan_id': hashlib.md5(f"{file_path}:{datetime.now().isoformat()}".encode()).hexdigest()[:10]
            }
            
            return result
            
        except Exception as e:
            return {
                'file_name': os.path.basename(file_path),
                'status': 'error',
                'error': str(e),
                'pii_found': []
            }
    
    def _get_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Get detailed file metadata, including Git information if available.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file metadata
        """
        metadata = {
            'last_modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
            'created': datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
            'size_bytes': os.path.getsize(file_path),
            'extension': os.path.splitext(file_path)[1].lower()
        }
        
        # Get Git metadata if enabled and the file is in a Git repository
        if self.use_git_metadata:
            try:
                git_data = {}
                
                # Get the file's Git history
                result = subprocess.run(
                    ['git', 'log', '-n', '1', '--pretty=format:%H|%an|%ae|%ad|%s', '--', file_path],
                    capture_output=True, text=True, check=False
                )
                
                if result.returncode == 0 and result.stdout:
                    parts = result.stdout.split('|')
                    if len(parts) >= 5:
                        git_data['commit_hash'] = parts[0]
                        git_data['author_name'] = parts[1]
                        git_data['author_email'] = parts[2]
                        git_data['commit_date'] = parts[3]
                        git_data['commit_message'] = parts[4]
                
                # Get Git blame info
                result = subprocess.run(
                    ['git', 'blame', '--porcelain', file_path],
                    capture_output=True, text=True, check=False
                )
                
                if result.returncode == 0 and result.stdout:
                    # Parse blame output to get line-by-line author info
                    blame_data = {}
                    lines = result.stdout.split('\n')
                    current_commit = None
                    line_number = 0
                    
                    for line in lines:
                        if line.startswith('author '):
                            author = line[7:]
                            if current_commit and current_commit not in blame_data:
                                blame_data[current_commit] = {
                                    'author': author,
                                    'lines': [line_number]
                                }
                            elif current_commit:
                                blame_data[current_commit]['lines'].append(line_number)
                        elif line and not line.startswith('\t'):
                            parts = line.split(' ')
                            if len(parts) > 0:
                                current_commit = parts[0]
                                line_number = int(parts[2]) if len(parts) > 2 else 0
                    
                    # Add line count per author summary
                    authors = {}
                    for commit, data in blame_data.items():
                        author = data['author']
                        if author in authors:
                            authors[author] += len(data['lines'])
                        else:
                            authors[author] = len(data['lines'])
                    
                    git_data['blame_summary'] = {
                        'authors': authors,
                        'total_lines': sum(authors.values())
                    }
                
                metadata['git'] = git_data
            except Exception as e:
                # Git metadata collection failed, but we don't want to fail the whole scan
                metadata['git_error'] = str(e)
        
        return metadata
    
    def _calculate_entropy(self, string: str) -> float:
        """
        Calculate Shannon entropy of a string.
        Higher values indicate more randomness (higher likelihood of being a secret).
        
        Args:
            string: The string to calculate entropy for
            
        Returns:
            Entropy value (typically 3.5+ for secrets, 5+ for strong secrets)
        """
        if not string:
            return 0.0
        
        # Count character frequencies
        freq = {}
        for c in string:
            if c in freq:
                freq[c] += 1
            else:
                freq[c] = 1
        
        # Calculate entropy
        length = len(string)
        entropy = 0.0
        
        for count in freq.values():
            probability = count / length
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    def _detect_high_entropy_strings(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Detect high entropy strings that might be secrets but weren't caught by regex patterns.
        
        Args:
            content: The file content
            file_path: Path to the file for reference
            
        Returns:
            List of findings with high entropy strings
        """
        findings = []
        
        # Look for string literals in the code
        # This is a simplified approach - each language has different string literal syntax
        string_patterns = [
            r'"([^"\\]*(\\.[^"\\]*)*)"',    # Double-quoted strings
            r"'([^'\\]*(\\.[^'\\]*)*)'",    # Single-quoted strings
            r"`([^`\\]*(\\.[^`\\]*)*)`"     # Backtick strings (JavaScript)
        ]
        
        for pattern in string_patterns:
            for match in re.finditer(pattern, content, re.MULTILINE | re.DOTALL):
                string_value = match.group(1)
                
                # Only analyze strings that might be secrets (8+ chars, alphanumeric+symbols)
                if len(string_value) >= 8 and re.search(r'[A-Za-z0-9]', string_value) and re.search(r'[^A-Za-z0-9]', string_value):
                    entropy = self._calculate_entropy(string_value)
                    
                    # High entropy threshold (adjust as needed)
                    if entropy > 4.0:
                        line_no = content[:match.start()].count('\n') + 1
                        entropy_formatted = str(round(entropy, 2))
                        
                        # Add to findings
                        findings.append({
                            'type': 'High Entropy String',
                            'value': f'{string_value[:3]}***{string_value[-3:]}',  # Mask the value
                            'location': f'Line {line_no}',
                            'risk_level': 'Medium',
                            'reason': f'String with high entropy (randomness) detected. Entropy: {entropy_formatted}',
                            'entropy': entropy_formatted
                        })
        
        return findings
    
    def _identify_provider(self, var_name: str, value: str) -> Optional[str]:
        """
        Identify the provider/service based on key patterns.
        
        Args:
            var_name: Variable name or key
            value: The secret value
            
        Returns:
            Provider name if identified, None otherwise
        """
        combined = f"{var_name} {value}".lower()
        
        for provider, patterns in self.known_providers.items():
            for pattern in patterns:
                if re.search(pattern, combined, re.IGNORECASE):
                    return provider
        
        return None
    
    def _get_regulation_references(self, finding_type: str) -> Dict[str, str]:
        """
        Get relevant regulatory references for a finding type.
        
        Args:
            finding_type: The type of finding
            
        Returns:
            Dictionary mapping regulation names to article references
        """
        references = {}
        
        finding_type = finding_type.lower()
        
        # Map finding types to regulatory categories
        category_map = {
            'secret': 'Security',
            'api key': 'Security',
            'token': 'Security',
            'password': 'Security',
            'email': 'PII',
            'name': 'PII',
            'address': 'PII',
            'phone': 'PII',
            'ip': 'PII',
            'credit card': 'Financial Data',
            'bank': 'Financial Data',
            'passport': 'Special Categories',
            'medical': 'Health Data',
            'health': 'Health Data',
            'ethnic': 'Special Categories',
            'biometric': 'Special Categories'
        }
        
        # Determine which category this finding falls into
        matched_category = None
        for key, category in category_map.items():
            if key in finding_type:
                matched_category = category
                break
        
        if not matched_category:
            matched_category = 'PII'  # Default category
        
        # Add references from each regulatory framework
        for regulation, ref_map in self.regulatory_refs.items():
            for ref_category, article in ref_map.items():
                if matched_category in ref_category or ref_category in matched_category:
                    references[regulation] = article
                    break
            
            # Add general reference if no specific one was found
            if regulation not in references and 'PII' in ref_map:
                references[regulation] = ref_map['PII']
        
        return references
    
    def _scan_content(self, content: str, content_type: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Scan content (code or comments) for PII.
        
        Args:
            content: The text content to scan
            content_type: Either "code" or "comment"
            file_path: Original file path for reference
            
        Returns:
            List of PII findings
        """
        pii_found = []
        
        # Split into lines for better location reporting
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line_num = i + 1
            
            # Use PII detection utility
            pii_items = identify_pii_in_text(line, self.region)
            
            for pii_item in pii_items:
                pii_type = pii_item['type']
                
                # Evaluate risk level
                risk_level = evaluate_risk_level(pii_type, self.region_rules)
                
                # Create finding entry
                finding = {
                    'type': pii_type,
                    'value': pii_item['value'],
                    'location': f'Line {line_num} ({content_type})',
                    'risk_level': risk_level,
                    'reason': self._get_reason(pii_type, risk_level)
                }
                
                pii_found.append(finding)
        
        return pii_found
    
    def _get_reason(self, pii_type: str, risk_level: str) -> str:
        """
        Get a reason explanation for the PII finding.
        
        Args:
            pii_type: The type of PII found
            risk_level: The risk level (Low, Medium, High)
            
        Returns:
            A string explaining why this PII is a concern
        """
        reasons = {
            'BSN': 'Dutch citizen service number (BSN) is highly sensitive personal data under GDPR and UAVG',
            'Email': 'Email addresses are personal data under GDPR',
            'Phone': 'Phone numbers are personal data under GDPR',
            'Address': 'Physical addresses are personal data under GDPR',
            'Name': 'Personal names are personal data under GDPR',
            'Credit Card': 'Payment information is highly sensitive under GDPR',
            'IP Address': 'IP addresses are considered personal data under GDPR',
            'Date of Birth': 'Birth dates are personal data and can be used for identity theft',
            'Passport Number': 'Passport numbers are highly sensitive personal data under GDPR',
            'Medical Data': 'Medical data is special category data under GDPR Article 9',
            'Financial Data': 'Financial information is sensitive personal data under GDPR',
            'Username': 'Usernames may be personal data under GDPR',
            'Password': 'Password storage should follow strict security guidelines under GDPR',
        }
        
        # Default reason if specific one not found
        default_reason = f"{pii_type} is potentially personal data under GDPR"
        
        return reasons.get(pii_type, default_reason)
