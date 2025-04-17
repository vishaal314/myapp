import os
import tempfile
import re
from typing import Dict, List, Any, Optional
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
        self.file_types = file_types or ["PDF", "DOCX", "TXT", "RTF", "CSV"]
        self.region = region
        self.region_rules = get_region_rules(region)
        
        # Mapping of file extensions to their types
        self.extension_map = {
            '.pdf': 'PDF',
            '.docx': 'DOCX',
            '.doc': 'DOCX',
            '.txt': 'TXT',
            '.rtf': 'RTF',
            '.csv': 'CSV',
            '.xlsx': 'XLSX',
            '.xls': 'XLSX',
            '.odt': 'DOCX'
        }
    
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
        
        # Check if file type is supported
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext not in self.extension_map:
            return {
                'file_name': os.path.basename(file_path),
                'status': 'skipped',
                'reason': f'File extension {ext} not supported',
                'pii_found': []
            }
        
        file_type = self.extension_map[ext]
        if file_type not in self.file_types:
            return {
                'file_name': os.path.basename(file_path),
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
        if file_type == 'PDF':
            return self._extract_pdf_text(file_path)
        elif file_type == 'TXT':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        elif file_type in ['DOCX', 'RTF', 'XLSX', 'CSV']:
            try:
                # Use textract to handle various document formats
                return textract.process(file_path).decode('utf-8', errors='ignore')
            except:
                # Fallback method
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        return f.read()
                except:
                    return ""
        
        return ""
    
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
