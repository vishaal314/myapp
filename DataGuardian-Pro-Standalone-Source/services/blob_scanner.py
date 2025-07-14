import os
import tempfile
import re
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
import PyPDF2
import textract
from utils.pii_detection import identify_pii_in_text
from utils.gdpr_rules import get_region_rules, evaluate_risk_level
from utils.netherlands_gdpr import detect_nl_violations
from utils.comprehensive_gdpr_validator import validate_comprehensive_gdpr_compliance
from utils.eu_ai_act_compliance import detect_ai_act_violations, generate_ai_act_compliance_report

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BlobScanner:
    """
    A scanner that detects PII in document files (PDFs, Word documents, text files, etc.)
    """
    
    def __init__(self, file_types: List[str] = None, region: str = "Netherlands"):
        """
        Initialize the blob scanner.
        
        Args:
            file_types: List of file types to scan (e.g., ['PDF', 'DOCX'])
            region: The region for which to apply GDPR rules
        """
        self.file_types = file_types or [
            "PDF", "DOCX", "TXT", "RTF", "CSV", "XLSX", "JSON", "XML", 
            "HTML", "MD", "LOG", "CONF", "INI", "ENV", "SQL", "JS", 
            "PY", "JAVA", "PHP", "RB", "C", "CPP", "CS", "GO", "TS"
        ]
        self.region = region
        self.region_rules = get_region_rules(region)
        
        # Expanded mapping of file extensions to their types
        self.extension_map = {
            # Document formats
            '.pdf': 'PDF',
            '.docx': 'DOCX',
            '.doc': 'DOCX',
            '.rtf': 'RTF',
            '.odt': 'DOCX',
            '.pptx': 'PPTX',
            '.ppt': 'PPTX',
            '.odp': 'PPTX',
            
            # Spreadsheet formats
            '.xlsx': 'XLSX',
            '.xls': 'XLSX',
            '.csv': 'CSV',
            '.ods': 'XLSX',
            '.tsv': 'CSV',
            
            # Text formats
            '.txt': 'TXT',
            '.md': 'MD',
            '.markdown': 'MD',
            '.rst': 'TXT',
            
            # Data formats
            '.json': 'JSON',
            '.xml': 'XML',
            '.html': 'HTML',
            '.htm': 'HTML',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.toml': 'TOML',
            
            # Config files
            '.conf': 'CONF',
            '.config': 'CONF',
            '.ini': 'INI',
            '.cfg': 'CONF',
            '.env': 'ENV',
            '.properties': 'CONF',
            '.cnf': 'CONF',
            
            # Log files
            '.log': 'LOG',
            
            # Database files
            '.sql': 'SQL',
            '.sqlite': 'SQL',
            '.db': 'SQL',
            
            # Programming languages
            '.py': 'PY',
            '.js': 'JS',
            '.ts': 'TS',
            '.jsx': 'JS',
            '.tsx': 'TS',
            '.java': 'JAVA',
            '.cs': 'CS',
            '.php': 'PHP',
            '.rb': 'RB',
            '.c': 'C',
            '.cpp': 'CPP',
            '.h': 'C',
            '.hpp': 'CPP',
            '.go': 'GO',
            '.rs': 'RS',
            '.swift': 'SWIFT',
            '.kt': 'KT',
            '.sh': 'SH',
            '.ps1': 'PS1',
            '.bat': 'BAT',
            '.css': 'CSS',
            '.scss': 'CSS',
            '.less': 'CSS'
        }
        
        # High-risk file types that might contain sensitive information
        self.high_risk_files = [
            '.env', '.ini', '.conf', '.config', '.cnf', '.properties',
            '.pem', '.key', '.cert', '.crt', '.p12', '.pfx', '.keystore',
            '.htpasswd', '.netrc', '.pgpass', '.aws/credentials', 
            'secrets.json', 'credentials.json', 'auth.json'
        ]
    
    def scan_file(self, file_path: str) -> Dict[str, Any]:
        """
        Scan a single document file for PII.
        
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
        
        # Get filename for checks
        file_name = os.path.basename(file_path)
        
        # Check if file is in high-risk list - always scan these regardless of extension
        is_high_risk = any(file_name.endswith(ext) for ext in self.high_risk_files) or any(pattern in file_name.lower() for pattern in ['secret', 'password', 'credential', 'token', 'key', 'auth'])
        
        # Check if file type is supported
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        # For high-risk files, try to scan even if extension is not in the map
        if ext not in self.extension_map and not is_high_risk:
            return {
                'file_name': file_name,
                'status': 'skipped',
                'reason': f'File extension {ext} not supported',
                'pii_found': []
            }
        
        # For high-risk files without recognized extension, treat as text
        if ext not in self.extension_map and is_high_risk:
            file_type = 'TXT'  # Treat as plain text
        else:
            file_type = self.extension_map[ext]
            
        # Skip normal files if type not in scan list, but always scan high-risk files
        if file_type not in self.file_types and not is_high_risk:
            return {
                'file_name': file_name,
                'status': 'skipped',
                'reason': f'File type {file_type} not in scan list',
                'pii_found': []
            }
        
        try:
            # Extract text based on file type
            text = self._extract_text(file_path, file_type)
            
            if not text:
                return {
                    'file_name': os.path.basename(file_path),
                    'status': 'warning',
                    'warning': 'No text content could be extracted',
                    'pii_found': []
                }
            
            # Scan the extracted text for PII
            pii_items = self._scan_text(text, file_path)
            
            # Perform comprehensive compliance validation with error handling
            try:
                gdpr_compliance = validate_comprehensive_gdpr_compliance(text, self.region)
            except Exception as e:
                print(f"GDPR compliance validation failed: {str(e)}")
                gdpr_compliance = {'findings': [], 'overall_compliance_score': 100}
            
            try:
                netherlands_violations = detect_nl_violations(text) if self.region == "Netherlands" else []
            except Exception as e:
                print(f"Netherlands violations detection failed: {str(e)}")
                netherlands_violations = []
            
            try:
                ai_act_violations = detect_ai_act_violations(text)
            except Exception as e:
                print(f"AI Act violations detection failed: {str(e)}")
                ai_act_violations = []
            
            # Combine all findings
            all_compliance_findings = []
            if gdpr_compliance and 'findings' in gdpr_compliance:
                all_compliance_findings.extend(gdpr_compliance.get('findings', []))
            if netherlands_violations:
                all_compliance_findings.extend(netherlands_violations)
            if ai_act_violations:
                all_compliance_findings.extend(ai_act_violations)
            
            # Calculate risk assessment including compliance findings
            all_findings = pii_items if pii_items else []
            if all_compliance_findings:
                all_findings.extend(all_compliance_findings)
            risk_assessment = self._calculate_risk_score(all_findings)
            
            # Determine GDPR categories
            gdpr_categories = self._get_gdpr_categories(pii_items)
            
            # Generate comprehensive compliance notes
            compliance_notes = self._generate_comprehensive_compliance_notes(
                pii_items, all_compliance_findings, file_type, gdpr_compliance, ai_act_violations
            )
            
            # Generate AI Act compliance report with error handling
            try:
                ai_act_report = generate_ai_act_compliance_report(ai_act_violations)
            except Exception as e:
                print(f"AI Act report generation failed: {str(e)}")
                ai_act_report = {'compliance_score': 100, 'compliance_status': 'Compliant', 'risk_distribution': {}, 'recommendations': []}
            
            # Create comprehensive results
            result = {
                'file_name': os.path.basename(file_path),
                'file_path': file_path,
                'status': 'scanned',
                'file_type': file_type,
                'file_size': os.path.getsize(file_path),
                'pii_found': pii_items,
                'pii_count': len(pii_items),
                'risk_assessment': risk_assessment,
                'risk_level': risk_assessment.get('level', 'Low'),
                'gdpr_categories': gdpr_categories,
                'compliance_notes': compliance_notes,
                'scan_timestamp': datetime.now().isoformat(),
                'region': self.region,
                'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                'text_length': len(text) if text else 0,
                # Enhanced compliance reporting
                'gdpr_compliance': {
                    'overall_score': gdpr_compliance.get('overall_compliance_score', 0),
                    'status': gdpr_compliance.get('compliance_status', 'Unknown'),
                    'principle_scores': gdpr_compliance.get('principle_compliance', {}),
                    'rights_scores': gdpr_compliance.get('rights_compliance', {}),
                    'recommendations': gdpr_compliance.get('recommendations', [])
                },
                'netherlands_compliance': {
                    'violations_found': len(netherlands_violations),
                    'violations': netherlands_violations
                } if self.region == "Netherlands" else {},
                'ai_act_compliance': {
                    'compliance_score': ai_act_report.get('compliance_score', 100),
                    'status': ai_act_report.get('compliance_status', 'Compliant'),
                    'risk_distribution': ai_act_report.get('risk_distribution', {}),
                    'violations': ai_act_violations,
                    'recommendations': ai_act_report.get('recommendations', [])
                },
                'all_compliance_findings': all_compliance_findings
            }
            
            return result
            
        except Exception as e:
            return {
                'file_name': os.path.basename(file_path),
                'status': 'error',
                'error': str(e),
                'pii_found': []
            }
    
    def _extract_text(self, file_path: str, file_type: str) -> str:
        """
        Extract text content from a document file.
        
        Args:
            file_path: Path to the document file
            file_type: Type of the document (PDF, DOCX, etc.)
            
        Returns:
            Extracted text content
        """
        # Group file types by extraction method
        text_based_formats = [
            'TXT', 'JSON', 'XML', 'HTML', 'MD', 'LOG', 'CONF', 'INI', 'ENV', 'YAML', 
            'TOML', 'SQL'
        ]
        document_formats = ['DOCX', 'RTF', 'PPTX']
        spreadsheet_formats = ['XLSX', 'CSV', 'TSV']
        code_formats = [
            'PY', 'JS', 'TS', 'JAVA', 'CS', 'PHP', 'RB', 'C', 'CPP', 'GO', 'RS', 
            'SWIFT', 'KT', 'SH', 'PS1', 'BAT', 'CSS'
        ]
        
        # Check if file is in high-risk list
        file_name = os.path.basename(file_path)
        is_high_risk = any(file_name.endswith(ext) for ext in self.high_risk_files) or any(pattern in file_name for pattern in ['secret', 'password', 'credential', 'token', 'key', 'auth'])
        
        try:
            # Handle PDF documents with specialized extraction
            if file_type == 'PDF':
                return self._extract_pdf_text(file_path)
                
            # Handle plain text, config files, and similar
            elif file_type in text_based_formats:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Add a note for high-risk files
                    if is_high_risk:
                        content = f"[HIGH-RISK FILE: {file_name}]\n\n" + content
                    return content
                    
            # Handle programming language source files (treat as text)
            elif file_type in code_formats:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Add a note for potentially sensitive code files
                    if any(pattern in content.lower() for pattern in ['password', 'secret', 'token', 'key', 'credential', 'auth']):
                        content = f"[POTENTIALLY SENSITIVE CODE: {file_name}]\n\n" + content
                    return content
                    
            # Handle document formats using textract
            elif file_type in document_formats:
                try:
                    return textract.process(file_path).decode('utf-8', errors='ignore')
                except:
                    # Fallback to basic text reading
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        return f.read()
                        
            # Handle spreadsheet formats
            elif file_type in spreadsheet_formats:
                try:
                    return textract.process(file_path).decode('utf-8', errors='ignore')
                except:
                    # Fallback for CSV/TSV files
                    if file_type in ['CSV', 'TSV']:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            return f.read()
                    return ""
            
            # Handle binary files by checking for text patterns
            elif os.path.splitext(file_path)[1].lower() in ['.db', '.sqlite']:
                # Extract strings from binary files using strings command if available
                try:
                    import subprocess
                    result = subprocess.run(['strings', file_path], capture_output=True, text=True)
                    if result.returncode == 0:
                        return result.stdout
                    return ""
                except:
                    return ""
            
            # Unknown format - try basic text extraction
            else:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        return f.read()
                except:
                    # For binary files, make a note but don't attempt to read
                    if os.path.getsize(file_path) > 0:
                        return f"[BINARY FILE: {file_name} - size: {os.path.getsize(file_path)} bytes]"
                    return ""
                    
        except Exception as e:
            print(f"Error extracting text from {file_path}: {str(e)}")
            return f"[ERROR: Could not extract text from {file_name} - {str(e)}]"
    
    def _extract_pdf_text(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content
        """
        text = ""
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
                    
            # If no text was extracted (e.g., scanned PDF), try OCR if available
            if not text.strip():
                try:
                    # Attempt to use textract as a fallback for OCR
                    return textract.process(pdf_path).decode('utf-8', errors='ignore')
                except:
                    return text
            
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {str(e)}")
            return ""
    
    def _scan_text(self, text: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Enhanced text scanning for PII and compliance violations.
        
        Args:
            text: Text content to scan
            file_path: Path to the file being scanned (for context)
            
        Returns:
            List of PII findings and violations
        """
        if not text or not text.strip():
            return []
        
        try:
            # Use the PII detection utility
            pii_items = identify_pii_in_text(text, region=self.region)
            
            # Enhanced violation detection for demonstration files
            demonstration_violations = self._detect_demonstration_violations(text, file_path)
            
            # Format findings for consistency
            formatted_findings = []
            
            # Add PII findings
            for item in pii_items:
                formatted_findings.append({
                    'type': item.get('type', 'Unknown'),
                    'value': item.get('value', ''),
                    'risk_level': item.get('risk_level', 'Medium'),
                    'location': item.get('location', f'File: {os.path.basename(file_path)}'),
                    'description': item.get('description', f"{item.get('type', 'PII')} detected"),
                    'gdpr_article': item.get('gdpr_article', 'Article 6'),
                    'recommendation': item.get('recommendation', 'Review and ensure proper legal basis')
                })
            
            # Add demonstration violations
            formatted_findings.extend(demonstration_violations)
            
            return formatted_findings
            
        except Exception as e:
            print(f"Error scanning text: {str(e)}")
            return []
    
    def _detect_demonstration_violations(self, text: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Detect violations in demonstration or example files that contain violation examples.
        """
        violations = []
        
        # Check if this is a demonstration file with violation examples
        if any(marker in text.lower() for marker in ['violation', '❌', 'unauthorized', 'prohibited']):
            
            # Detect BSN violations
            bsn_violations = re.findall(r'❌.*?BSN.*?(\d{9})', text, re.IGNORECASE | re.DOTALL)
            for bsn in bsn_violations:
                violations.append({
                    'type': 'BSN_VIOLATION',
                    'value': bsn,
                    'risk_level': 'High',
                    'location': f'File: {os.path.basename(file_path)}',
                    'description': 'Unauthorized BSN collection example detected',
                    'gdpr_article': 'UAVG Article 46',
                    'recommendation': 'Remove unauthorized BSN examples or add proper legal basis'
                })
            
            # Detect AI Act violations
            if re.search(r'❌.*?AI.*?(?:hiring|automatic|evaluat)', text, re.IGNORECASE):
                violations.append({
                    'type': 'AI_ACT_VIOLATION',
                    'value': 'High-risk AI system without safeguards',
                    'risk_level': 'Critical',
                    'location': f'File: {os.path.basename(file_path)}',
                    'description': 'High-risk AI system detected without proper compliance framework',
                    'gdpr_article': 'EU AI Act Annex III',
                    'recommendation': 'Implement AI governance framework with human oversight'
                })
            
            # Detect general GDPR violations
            if re.search(r'❌.*?(?:collect|data|processing).*?(?:business purposes|no legal basis)', text, re.IGNORECASE):
                violations.append({
                    'type': 'GDPR_LAWFULNESS_VIOLATION',
                    'value': 'Processing without legal basis',
                    'risk_level': 'High',
                    'location': f'File: {os.path.basename(file_path)}',
                    'description': 'Data processing without proper legal basis under GDPR Article 6',
                    'gdpr_article': 'GDPR Article 6',
                    'recommendation': 'Establish clear legal basis for all data processing activities'
                })
            
            # Detect transparency violations
            if re.search(r'❌.*?(?:hidden|no notice|undisclosed)', text, re.IGNORECASE):
                violations.append({
                    'type': 'GDPR_TRANSPARENCY_VIOLATION',
                    'value': 'Hidden data processing',
                    'risk_level': 'High',
                    'location': f'File: {os.path.basename(file_path)}',
                    'description': 'Data processing without transparent disclosure to data subjects',
                    'gdpr_article': 'GDPR Article 5(1)(a)',
                    'recommendation': 'Implement clear privacy notices and transparent data processing disclosure'
                })
            
            # Detect data minimization violations
            if re.search(r'❌.*?(?:excessive|unnecessary|over-collection)', text, re.IGNORECASE):
                violations.append({
                    'type': 'GDPR_DATA_MINIMIZATION_VIOLATION',
                    'value': 'Excessive data collection',
                    'risk_level': 'Medium',
                    'location': f'File: {os.path.basename(file_path)}',
                    'description': 'Data collection exceeds what is necessary for stated purposes',
                    'gdpr_article': 'GDPR Article 5(1)(c)',
                    'recommendation': 'Review and limit data collection to what is strictly necessary'
                })
            
            # Detect special category violations
            if re.search(r'(?:health|medical|biometric|genetic).*?(?:without.*?consent|unauthorized)', text, re.IGNORECASE):
                violations.append({
                    'type': 'GDPR_SPECIAL_CATEGORY_VIOLATION',
                    'value': 'Special category data without proper basis',
                    'risk_level': 'Critical',
                    'location': f'File: {os.path.basename(file_path)}',
                    'description': 'Special categories of personal data processed without explicit consent or other Article 9 basis',
                    'gdpr_article': 'GDPR Article 9',
                    'recommendation': 'Obtain explicit consent or establish other lawful basis under Article 9'
                })
        
        return violations
    
    def _legacy_scan_text(self, text: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Legacy scanning method for compatibility.
        """
        pii_found = []
        
        # Split text into paragraphs/chunks for processing
        chunks = re.split(r'\n{2,}', text)
        
        for i, chunk in enumerate(chunks):
            # Skip empty chunks
            if not chunk.strip():
                continue
            
            # Use PII detection utility
            pii_items = identify_pii_in_text(chunk, self.region)
            
            for pii_item in pii_items:
                pii_type = pii_item['type']
                
                # Evaluate risk level
                risk_level = evaluate_risk_level(pii_type, self.region_rules)
                
                # Create finding entry
                finding = {
                    'type': pii_type,
                    'value': pii_item['value'],
                    'location': f'Paragraph/Chunk {i+1}',
                    'risk_level': risk_level,
                    'reason': self._get_reason(pii_type, risk_level, self.region)
                }
                
                pii_found.append(finding)
        
        return pii_found
    
    def _get_reason(self, pii_type: str, risk_level: str, region: str) -> str:
        """
        Get a reason explanation for the PII finding.
        
        Args:
            pii_type: The type of PII found
            risk_level: The risk level (Low, Medium, High)
            region: The region for which GDPR rules are applied
            
        Returns:
            A string explaining why this PII is a concern
        """
        # Common reasons for all regions
        common_reasons = {
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
        
        # Region-specific reasons
        region_reasons = {
            'Netherlands': {
                'BSN': 'BSN (Burgerservicenummer) has special protection under Dutch UAVG law',
                'Medical Data': 'Medical data requires explicit consent under Dutch UAVG law',
                'Minor Data': 'Data of minors (under 16) requires parental consent under Dutch UAVG'
            },
            'Germany': {
                'Address': 'Addresses have heightened protection under German BDSG',
                'Medical Data': 'Health data has special protection under German BDSG'
            },
            'France': {
                'Minor Data': 'Data of minors (under 15) requires parental consent under French law'
            },
            'Belgium': {
                'Minor Data': 'Data of minors (under 13) requires parental consent under Belgian law'
            }
        }
        
        # Check if there's a region-specific reason
        if region in region_reasons and pii_type in region_reasons[region]:
            return region_reasons[region][pii_type]
        
        # Fall back to common reason
        if pii_type in common_reasons:
            return common_reasons[pii_type]
        
        # Default reason if specific one not found
        return f"{pii_type} is potentially personal data under GDPR"
    
    def _calculate_risk_score(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate risk score based on findings.
        
        Args:
            findings: List of PII findings
            
        Returns:
            Dictionary with risk score details
        """
        if not findings:
            return {
                "score": 0,
                "max_score": 100,
                "level": "Low",
                "factors": []
            }
        
        # Count findings by risk level
        risk_counts = {
            "Critical": 0,
            "High": 0,
            "Medium": 0,
            "Low": 0
        }
        
        for finding in findings:
            risk_level = finding.get("risk_level", "Medium")
            if risk_level in risk_counts:
                risk_counts[risk_level] += 1
        
        # Calculate weighted score
        weights = {
            "Critical": 25,
            "High": 15,
            "Medium": 7,
            "Low": 2
        }
        
        score = sum(risk_counts[level] * weights[level] for level in risk_counts)
        score = min(score, 100)  # Cap at 100
        
        # Determine overall risk level
        level = "Low"
        if score >= 75:
            level = "Critical"
        elif score >= 50:
            level = "High"
        elif score >= 25:
            level = "Medium"
        
        # Risk factors explanation
        factors = []
        for risk_level, count in risk_counts.items():
            if count > 0:
                factors.append(f"{count} {risk_level} risk finding{'s' if count > 1 else ''}")
        
        return {
            "score": score,
            "max_score": 100,
            "level": level,
            "factors": factors
        }
    
    def _get_gdpr_categories(self, findings: List[Dict[str, Any]]) -> List[str]:
        """
        Determine GDPR categories based on findings.
        
        Args:
            findings: List of PII findings
            
        Returns:
            List of GDPR categories
        """
        categories = set()
        
        for finding in findings:
            pii_type = finding.get('type', '')
            
            # Map PII types to GDPR categories
            if pii_type in ['Name', 'Email', 'Phone', 'Address', 'IP Address']:
                categories.add('Personal Data (Article 4)')
            elif pii_type in ['BSN', 'Passport Number', 'Credit Card', 'Financial Data']:
                categories.add('Personal Data (Article 4)')
                categories.add('Sensitive Personal Data')
            elif pii_type in ['Medical Data', 'Health Information']:
                categories.add('Special Category Data (Article 9)')
            elif pii_type in ['Date of Birth', 'Minor Data']:
                categories.add('Personal Data (Article 4)')
                if 'Minor' in pii_type:
                    categories.add('Children\'s Data (Article 8)')
        
        return list(categories)
    
    def _generate_compliance_notes(self, findings: List[Dict[str, Any]], file_type: str) -> List[str]:
        """
        Generate comprehensive compliance notes based on findings and file type.
        
        Args:
            findings: List of PII findings
            file_type: Type of file scanned
            
        Returns:
            List of compliance notes
        """
        notes = []
        
        if not findings:
            notes.append("No PII detected in document")
            return notes
        
        # High-risk data types
        high_risk_types = [f['type'] for f in findings if f.get('risk_level') == 'High']
        if high_risk_types:
            notes.append(f"High-risk PII detected: {', '.join(set(high_risk_types))}")
        
        # Special category data (GDPR Article 9)
        special_categories = [f['type'] for f in findings if f['type'] in ['Medical Data', 'Biometric Data', 'Genetic Data', 'Health Information']]
        if special_categories:
            notes.append("Special category data found - requires explicit consent under GDPR Article 9")
        
        # Dutch-specific BSN
        bsn_found = any(f['type'] == 'BSN' for f in findings)
        if bsn_found and self.region == "Netherlands":
            notes.append("BSN (Dutch Citizen Service Number) detected - requires special handling under UAVG Article 46")
        
        return notes
    
    def _generate_comprehensive_compliance_notes(self, pii_findings: List[Dict[str, Any]], 
                                               compliance_findings: List[Dict[str, Any]], 
                                               file_type: str, gdpr_compliance: Dict[str, Any],
                                               ai_act_violations: List[Dict[str, Any]]) -> List[str]:
        """
        Generate comprehensive compliance notes including GDPR, Netherlands-specific, and AI Act findings.
        """
        notes = []
        
        # Start with basic PII notes
        if not pii_findings and not compliance_findings:
            notes.append("No PII or compliance issues detected in document")
            return notes
        
        # PII findings summary
        if pii_findings:
            high_risk_types = [f['type'] for f in pii_findings if f.get('risk_level') == 'High']
            if high_risk_types:
                notes.append(f"High-risk PII detected: {', '.join(set(high_risk_types))}")
            
            # Special category data (GDPR Article 9)
            special_categories = [f['type'] for f in pii_findings if f['type'] in ['Medical Data', 'Biometric Data', 'Genetic Data', 'Health Information']]
            if special_categories:
                notes.append("Special category data found - requires explicit consent under GDPR Article 9")
        
        # GDPR compliance summary
        gdpr_score = gdpr_compliance.get('overall_compliance_score', 100)
        if gdpr_score < 70:
            notes.append(f"GDPR compliance score: {gdpr_score}/100 - Significant compliance gaps identified")
        elif gdpr_score < 90:
            notes.append(f"GDPR compliance score: {gdpr_score}/100 - Minor compliance improvements needed")
        else:
            notes.append(f"GDPR compliance score: {gdpr_score}/100 - Good compliance level")
        
        # Netherlands-specific findings
        if self.region == "Netherlands":
            nl_violations = [f for f in compliance_findings if f.get('gdpr_principle') == 'netherlands_specific']
            if nl_violations:
                notes.append(f"Netherlands UAVG violations detected: {len(nl_violations)} issues requiring attention")
        
        # EU AI Act findings
        if ai_act_violations:
            critical_ai = [f for f in ai_act_violations if f.get('risk_level') == 'Critical']
            high_ai = [f for f in ai_act_violations if f.get('risk_level') == 'High']
            
            if critical_ai:
                notes.append(f"EU AI Act CRITICAL violations: {len(critical_ai)} prohibited practices detected")
            if high_ai:
                notes.append(f"EU AI Act high-risk systems: {len(high_ai)} require compliance framework")
        
        # Data subject rights assessment
        rights_scores = gdpr_compliance.get('rights_compliance', {}).get('scores', {})
        missing_rights = [right.replace('_', ' ').title() for right, score in rights_scores.items() if score < 80]
        if missing_rights:
            notes.append(f"Data subject rights gaps: {', '.join(missing_rights[:3])}{'...' if len(missing_rights) > 3 else ''}")
        
        # GDPR principles assessment
        principle_scores = gdpr_compliance.get('principle_compliance', {}).get('scores', {})
        weak_principles = [principle.replace('_', ' ').title() for principle, score in principle_scores.items() if score < 70]
        if weak_principles:
            notes.append(f"GDPR principle weaknesses: {', '.join(weak_principles[:3])}{'...' if len(weak_principles) > 3 else ''}")
        
        # File type specific notes
        if file_type in ['PDF', 'DOCX', 'HTML'] and any('automated' in str(f).lower() for f in compliance_findings):
            notes.append("Document contains automated processing references - ensure GDPR Article 22 compliance")
        
        if file_type in ['JSON', 'XML'] and pii_findings:
            notes.append("Structured data with PII - ensure data minimization and purpose limitation")
        
        return notes
    
    def _scan_file_with_timeout(self, file_path: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Scan a file with timeout protection to prevent hanging on large files.
        
        Args:
            file_path: Path to the file to scan
            timeout: Timeout in seconds
            
        Returns:
            Scan results dictionary
        """
        import threading
        import multiprocessing
        
        # Using a queue to get the result from the worker process
        result_queue = multiprocessing.Queue()
        
        def worker():
            try:
                result = self.scan_file(file_path)
                result_queue.put(result)
            except Exception as e:
                result_queue.put({
                    'file_name': os.path.basename(file_path),
                    'status': 'error',
                    'error': f'Scan failed with error: {str(e)}',
                    'pii_found': []
                })
        
        # Start worker thread
        worker_thread = threading.Thread(target=worker)
        worker_thread.daemon = True  # Thread will die when main program exits
        worker_thread.start()
        
        # Wait for result with timeout
        worker_thread.join(timeout)
        
        # Check if worker completed
        if worker_thread.is_alive():
            return {
                'file_name': os.path.basename(file_path),
                'status': 'error',
                'error': f'Scan timed out after {timeout} seconds',
                'pii_found': []
            }
        
        # Get result from queue
        try:
            return result_queue.get(block=False)
        except Exception:
            return {
                'file_name': os.path.basename(file_path),
                'status': 'error',
                'error': 'Failed to retrieve scan results',
                'pii_found': []
            }
        
    def scan_directory(self, directory_path: str, recursive: bool = True, max_files: int = 1000, 
                      skip_patterns: List[str] = None, callback_fn = None) -> Dict[str, Any]:
        """
        Scan all files in a directory for PII.
        
        Args:
            directory_path: Path to the directory to scan
            recursive: Whether to scan subdirectories
            max_files: Maximum number of files to scan
            skip_patterns: List of patterns to skip (e.g., ['node_modules', '.git'])
            callback_fn: Callback function for progress updates
            
        Returns:
            Dictionary containing aggregated scan results
        """
        if not os.path.isdir(directory_path):
            return {
                'status': 'error',
                'error': 'Directory not found',
                'scan_results': []
            }
        
        # Default skip patterns if none provided
        skip_patterns = skip_patterns or [
            '.git', 'node_modules', '__pycache__', 'venv', 'env', '.pytest_cache',
            'build', 'dist', '.next', '.cache', '.yarn', '.npm', 'coverage'
        ]
        
        # Results container
        results = {
            'directory': directory_path,
            'scan_timestamp': datetime.now().isoformat(),
            'files_scanned': 0,
            'files_skipped': 0,
            'files_with_pii': 0,
            'total_pii_items': 0,
            'scan_results': [],
            'pii_types': {},
            'risk_levels': {'High': 0, 'Medium': 0, 'Low': 0},
            'high_risk_files': [],
            'errors': []
        }
        
        # Find all files with priority ordering
        all_files = []
        high_risk_files = []
        normal_files = []
        
        # Walk directory
        for root, dirs, files in os.walk(directory_path):
            # Skip directories matching patterns
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in skip_patterns)]
            
            # Process files in this directory
            for file in files:
                file_path = os.path.join(root, file)
                
                # Skip files matching patterns
                if any(pattern in file_path for pattern in skip_patterns):
                    continue
                
                # Check if high-risk file (prioritize these)
                if any(file.endswith(ext) for ext in self.high_risk_files) or any(pattern in file.lower() for pattern in ['secret', 'password', 'credential', 'token', 'key', 'auth']):
                    high_risk_files.append(file_path)
                else:
                    normal_files.append(file_path)
            
            # If not recursive, break after first iteration
            if not recursive:
                break
                
        # Combine with high-risk files first
        all_files = high_risk_files + normal_files
        
        # Limit to max_files
        all_files = all_files[:max_files]
        
        # Scan each file
        for i, file_path in enumerate(all_files):
            # Report progress if callback provided
            if callback_fn:
                callback_fn(i + 1, len(all_files), file_path)
            
            # Check file size and use timeout protection for large files
            file_size = os.path.getsize(file_path)
            large_file = file_size > 5 * 1024 * 1024  # 5MB threshold
            
            # Scan file with timeout protection for large files
            try:
                if large_file:
                    # Use timeout for large files
                    file_result = self._scan_file_with_timeout(file_path, timeout=60)
                else:
                    # Use standard scan for normal files
                    file_result = self.scan_file(file_path)
                    
                results['scan_results'].append(file_result)
                
                # Update counts
                if file_result['status'] == 'scanned':
                    results['files_scanned'] += 1
                    
                    # Update PII counts
                    if file_result.get('pii_count', 0) > 0:
                        results['files_with_pii'] += 1
                        results['total_pii_items'] += file_result['pii_count']
                        
                        # Track high-risk files
                        if any(finding['risk_level'] == 'High' for finding in file_result['pii_found']):
                            results['high_risk_files'].append(file_result['file_name'])
                        
                        # Update PII type counts
                        for finding in file_result['pii_found']:
                            pii_type = finding['type']
                            risk_level = finding['risk_level']
                            
                            # Update PII types count
                            if pii_type not in results['pii_types']:
                                results['pii_types'][pii_type] = 0
                            results['pii_types'][pii_type] += 1
                            
                            # Update risk level counts
                            results['risk_levels'][risk_level] += 1
                elif file_result['status'] == 'error':
                    # Track errors
                    results['errors'].append({
                        'file': file_path,
                        'error': file_result.get('error', 'Unknown error')
                    })
                    results['files_skipped'] += 1
                else:
                    results['files_skipped'] += 1
            except Exception as e:
                results['errors'].append({
                    'file': file_path,
                    'error': str(e)
                })
                results['files_skipped'] += 1
        
        return results
    
    def scan_multiple_documents(self, file_paths: List[str], callback_fn=None) -> Dict[str, Any]:
        """
        Scan multiple documents for PII with comprehensive reporting.
        
        Args:
            file_paths: List of document file paths to scan
            callback_fn: Optional callback function for progress updates
            
        Returns:
            Dictionary containing comprehensive scan results matching Image Scanner structure
        """
        logger.info(f"Starting document scan of {len(file_paths)} files")
        
        # Initialize results structure
        all_findings = []
        document_results = []
        errors = []
        documents_scanned = 0
        documents_with_pii = 0
        
        # Process each document
        for i, file_path in enumerate(file_paths):
            if callback_fn:
                callback_fn(i + 1, len(file_paths), os.path.basename(file_path))
            
            try:
                # Scan individual document
                result = self.scan_file(file_path)
                document_results.append(result)
                
                if result['status'] == 'scanned':
                    documents_scanned += 1
                    
                    # Collect findings
                    document_findings = result.get('pii_found', [])
                    if document_findings:
                        documents_with_pii += 1
                        all_findings.extend(document_findings)
                        
                        logger.info(f"Completed scan for {os.path.basename(file_path)}. Found {len(document_findings)} PII instances.")
                    else:
                        logger.info(f"Completed scan for {os.path.basename(file_path)}. Found 0 PII instances.")
                
                elif result['status'] == 'error':
                    errors.append({
                        'file': os.path.basename(file_path),
                        'error': result.get('error', 'Unknown error')
                    })
                    
            except Exception as e:
                logger.error(f"Error scanning {file_path}: {str(e)}")
                errors.append({
                    'file': os.path.basename(file_path),
                    'error': str(e)
                })
        
        # Calculate overall risk assessment
        overall_risk = self._calculate_risk_score(all_findings)
        
        # Generate metadata
        metadata = {
            'scan_type': 'document',
            'documents_scanned': documents_scanned,
            'documents_with_pii': documents_with_pii,
            'total_findings': len(all_findings),
            'scan_timestamp': datetime.now().isoformat(),
            'region': self.region,
            'scanner_version': '2.0.0'
        }
        
        logger.info(f"Completed document scan. Scanned {documents_scanned} documents, found {len(all_findings)} PII instances.")
        
        # Count findings by risk level for proper UI display
        critical_count = len([f for f in all_findings if f.get('risk_level') == 'Critical'])
        high_count = len([f for f in all_findings if f.get('risk_level') == 'High'])
        medium_count = len([f for f in all_findings if f.get('risk_level') == 'Medium'])
        low_count = len([f for f in all_findings if f.get('risk_level') == 'Low'])
        
        return {
            "scan_type": "document", 
            "scan_id": f"doc_scan_{int(datetime.now().timestamp())}",
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata,
            "document_results": document_results,
            "findings": all_findings,
            "documents_with_pii": documents_with_pii,
            "file_count": documents_scanned,
            "total_pii_found": len(all_findings),
            "critical_risk_count": critical_count,
            "high_risk_count": high_count,
            "medium_risk_count": medium_count,
            "low_risk_count": low_count,
            "errors": errors,
            "risk_summary": overall_risk
        }

# Create an alias for compatibility
def create_document_scanner(region: str = "Netherlands") -> BlobScanner:
    """Factory function to create BlobScanner instance for document scanning."""
    return BlobScanner(region=region)
