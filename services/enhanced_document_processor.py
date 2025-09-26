"""
Enhanced Document Processor - Replaces textract functionality
Provides comprehensive document text extraction without dependency conflicts.
"""

import os
import tempfile
import logging
from typing import Optional, Dict, Any
import PyPDF2
from io import BytesIO

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import openpyxl
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

logger = logging.getLogger(__name__)

class EnhancedDocumentProcessor:
    """
    Enhanced document processor that replaces textract functionality
    without dependency conflicts.
    """
    
    def __init__(self):
        self.supported_formats = {
            '.pdf': self._extract_pdf_text,
            '.docx': self._extract_docx_text,
            '.doc': self._extract_doc_text,
            '.txt': self._extract_text_file,
            '.xlsx': self._extract_excel_text,
            '.xls': self._extract_excel_text,
            '.csv': self._extract_csv_text,
            '.json': self._extract_json_text,
            '.xml': self._extract_xml_text,
            '.html': self._extract_html_text,
        }
    
    def process(self, file_path: str, **kwargs) -> bytes:
        """
        Process document and extract text (mimics textract.process interface)
        
        Args:
            file_path: Path to the file to process
            **kwargs: Additional arguments (for compatibility)
            
        Returns:
            bytes: Extracted text as bytes
        """
        try:
            _, ext = os.path.splitext(file_path.lower())
            
            if ext in self.supported_formats:
                text = self.supported_formats[ext](file_path)
                return text.encode('utf-8')
            else:
                logger.warning(f"Unsupported file format: {ext}")
                return b"[Unsupported file format]"
                
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            return f"[Error processing document: {str(e)}]".encode('utf-8')
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF using PyPDF2"""
        try:
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                text = ""
                for page_num in range(len(pdf_reader.pages)):
                    text += pdf_reader.pages[page_num].extract_text()
                return text
        except Exception as e:
            logger.error(f"Error extracting PDF text: {str(e)}")
            return f"[Error reading PDF: {str(e)}]"
    
    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX using python-docx"""
        if not DOCX_AVAILABLE:
            return "[python-docx not available]"
        
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting DOCX text: {str(e)}")
            return f"[Error reading DOCX: {str(e)}]"
    
    def _extract_doc_text(self, file_path: str) -> str:
        """Extract text from DOC files (legacy format)"""
        # For legacy DOC files, we'll return a message
        return "[Legacy DOC format - please convert to DOCX]"
    
    def _extract_text_file(self, file_path: str) -> str:
        """Extract text from plain text files"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading text file: {str(e)}")
            return f"[Error reading text file: {str(e)}]"
    
    def _extract_excel_text(self, file_path: str) -> str:
        """Extract text from Excel files"""
        if not EXCEL_AVAILABLE:
            return "[openpyxl not available]"
        
        try:
            import pandas as pd
            df = pd.read_excel(file_path)
            return df.to_string()
        except Exception as e:
            logger.error(f"Error reading Excel file: {str(e)}")
            return f"[Error reading Excel: {str(e)}]"
    
    def _extract_csv_text(self, file_path: str) -> str:
        """Extract text from CSV files"""
        try:
            import pandas as pd
            df = pd.read_csv(file_path)
            return df.to_string()
        except Exception as e:
            logger.error(f"Error reading CSV: {str(e)}")
            return f"[Error reading CSV: {str(e)}]"
    
    def _extract_json_text(self, file_path: str) -> str:
        """Extract text from JSON files"""
        try:
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return json.dumps(data, indent=2)
        except Exception as e:
            logger.error(f"Error reading JSON: {str(e)}")
            return f"[Error reading JSON: {str(e)}]"
    
    def _extract_xml_text(self, file_path: str) -> str:
        """Extract text from XML files"""
        try:
            from xml.etree import ElementTree as ET
            tree = ET.parse(file_path)
            root = tree.getroot()
            return ET.tostring(root, encoding='unicode')
        except Exception as e:
            logger.error(f"Error reading XML: {str(e)}")
            return f"[Error reading XML: {str(e)}]"
    
    def _extract_html_text(self, file_path: str) -> str:
        """Extract text from HTML files"""
        try:
            from bs4 import BeautifulSoup
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
                return soup.get_text()
        except Exception as e:
            logger.error(f"Error reading HTML: {str(e)}")
            return f"[Error reading HTML: {str(e)}]"

# Create global instance for compatibility
enhanced_processor = EnhancedDocumentProcessor()

# Compatibility functions that mimic textract interface
def process(file_path: str, **kwargs) -> bytes:
    """Mimic textract.process() function"""
    return enhanced_processor.process(file_path, **kwargs)

def extract_text(file_path: str) -> str:
    """Extract text and return as string"""
    return enhanced_processor.process(file_path).decode('utf-8')
