import os
import tempfile
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
import PyPDF2
import textract
from utils.pii_detection import identify_pii_in_text
from utils.gdpr_rules import get_region_rules, evaluate_risk_level

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
            
            # Create results
            result = {
                'file_name': os.path.basename(file_path),
                'status': 'scanned',
                'file_type': file_type,
                'pii_found': pii_items,
                'pii_count': len(pii_items)
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
        Scan text content for PII.
        
        Args:
            text: The text content to scan
            file_path: Original file path for reference
            
        Returns:
            List of PII findings
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
