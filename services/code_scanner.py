import os
import re
import json
from typing import Dict, List, Any, Optional
from utils.pii_detection import identify_pii_in_text
from utils.gdpr_rules import get_region_rules, evaluate_risk_level

class CodeScanner:
    """
    A scanner that detects PII in code files.
    """
    
    def __init__(self, extensions: List[str] = None, include_comments: bool = True, region: str = "Netherlands"):
        """
        Initialize the code scanner.
        
        Args:
            extensions: List of file extensions to scan (e.g., ['.py', '.js'])
            include_comments: Whether to include comments in the scan
            region: The region for which to apply GDPR rules
        """
        self.extensions = extensions or ['.py', '.js', '.java', '.php', '.html', '.css', '.ts', '.go', '.rb']
        self.include_comments = include_comments
        self.region = region
        self.region_rules = get_region_rules(region)
        
        # Regex patterns for common secrets and PII
        self.secret_patterns = {
            'api_key': r'(?i)(api[_-]?key|apikey)[^\w\n]*?[\'"=:]+[^\w\n]*?([\w\-]{20,64})',
            'aws_key': r'(?i)aws[^\w\n]*?([\'"]?(?:access|secret)[_-]?key[\'"]?)[^\w\n]*?[\'"=:]+[^\w\n]*?([\w\/+]{20,40})',
            'password': r'(?i)(password|passwd|pwd)[^\w\n]*?[\'"=:]+[^\w\n]*?([^\s;,]{8,32})',
            'connection_string': r'(?i)(mongodb|mysql|postgresql|jdbc)[^\n]{3,100}([\w]+:[\w]+@)',
            'token': r'(?i)(auth[_-]token|oauth|bearer|jwt)[^\w\n]*?[\'"=:]+[^\w\n]*?([^\s;,]{30,64})'
        }
        
        # Comment patterns by language
        self.comment_patterns = {
            '.py': [r'#.*?$', r'""".*?"""', r"'''.*?'''"],
            '.js': [r'//.*?$', r'/\*.*?\*/', r'<!--.*?-->'],
            '.java': [r'//.*?$', r'/\*.*?\*/'],
            '.php': [r'//.*?$', r'/\*.*?\*/', r'#.*?$'],
            '.html': [r'<!--.*?-->'],
            '.css': [r'/\*.*?\*/'],
            '.ts': [r'//.*?$', r'/\*.*?\*/'],
            '.go': [r'//.*?$', r'/\*.*?\*/'],
            '.rb': [r'#.*?$', r'=begin.*?=end']
        }
        
    def scan_file(self, file_path: str) -> Dict[str, Any]:
        """
        Scan a single file for PII.
        
        Args:
            file_path: Path to the file to scan
            
        Returns:
            Dictionary containing scan results
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
                            if ext_pattern in ['.py', '.js', '.java', '.php', '.ts', '.go', '.rb']:
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
                        
                        # Add to PII findings
                        all_pii.append({
                            'type': f'Secret ({secret_type})',
                            'value': f'{var_name}: {value[:3]}***{value[-3:]}', # Mask the actual value
                            'location': f'Line {line_no}',
                            'risk_level': 'High',
                            'reason': f'Hardcoded {secret_type} found'
                        })
            
            # Create results
            result = {
                'file_name': os.path.basename(file_path),
                'status': 'scanned',
                'pii_found': all_pii,
                'pii_count': len(all_pii)
            }
            
            return result
            
        except Exception as e:
            return {
                'file_name': os.path.basename(file_path),
                'status': 'error',
                'error': str(e),
                'pii_found': []
            }
    
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
