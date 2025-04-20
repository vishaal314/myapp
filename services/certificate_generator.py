"""
Certificate Generator module for creating compliance certificates for scans with no issues.

This module provides functionality to create professional-looking compliance 
certificates for repositories or products that pass all compliance checks,
available only for premium members.
"""

import os
import io
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import uuid
import json

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm, mm, inch
from reportlab.platypus import Paragraph, Frame, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from utils.i18n import _

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CertificateGenerator:
    """
    A generator for compliance certificates when scans show no compliance issues.
    """
    
    def __init__(self, language: str = "en"):
        """
        Initialize the certificate generator.
        
        Args:
            language: Language for certificate text (default: "en")
        """
        self.language = language
        self.certificate_dir = os.path.join("reports", "certificates")
        os.makedirs(self.certificate_dir, exist_ok=True)
        
        # Load required fonts
        try:
            pdfmetrics.registerFont(TTFont('Roboto', os.path.join('utils', 'fonts', 'Roboto-Regular.ttf')))
            pdfmetrics.registerFont(TTFont('Roboto-Bold', os.path.join('utils', 'fonts', 'Roboto-Bold.ttf')))
            pdfmetrics.registerFont(TTFont('Roboto-Italic', os.path.join('utils', 'fonts', 'Roboto-Italic.ttf')))
        except:
            logger.warning("Could not load custom fonts. Using default fonts instead.")
    
    def is_fully_compliant(self, scan_results: Dict[str, Any]) -> bool:
        """
        Check if scan results indicate full compliance (no issues found).
        
        Args:
            scan_results: Dictionary containing scan results
            
        Returns:
            True if no compliance issues were found, False otherwise
        """
        # Check if there are any findings that indicate non-compliance
        if 'findings' in scan_results:
            # If there are findings, check if any have medium or high risk
            for finding in scan_results['findings']:
                if finding.get('risk_level', '').lower() in ['medium', 'high']:
                    return False
            
            # If only low-risk findings, we can still consider it compliant
            return True
        
        # If no findings key exists, check status
        return scan_results.get('status', '') == 'success' and scan_results.get('issues_found', 0) == 0
    
    def generate_certificate(self, scan_results: Dict[str, Any], 
                            user_info: Dict[str, Any],
                            company_name: Optional[str] = None) -> str:
        """
        Generate a PDF compliance certificate.
        
        Args:
            scan_results: Dictionary containing scan results
            user_info: Dictionary containing user information
            company_name: Optional company name to include on certificate
            
        Returns:
            Path to the generated certificate PDF
        """
        if not self.is_fully_compliant(scan_results):
            logger.warning("Cannot generate certificate: scan results show compliance issues.")
            return None
        
        # Check if user is premium
        if user_info.get('role', '').lower() != 'premium' and user_info.get('membership', '').lower() != 'premium':
            logger.warning("Cannot generate certificate: user does not have premium membership.")
            return None
        
        # Generate a unique filename for the certificate
        cert_id = uuid.uuid4().hex
        scan_type = scan_results.get('scan_type', 'unknown')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"compliance_certificate_{scan_type}_{cert_id}_{timestamp}.pdf"
        filepath = os.path.join(self.certificate_dir, filename)
        
        # Create PDF certificate
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Add header with logo
        try:
            logo_path = os.path.join("static", "img", "dataguardian-logo.png")
            if os.path.exists(logo_path):
                c.drawImage(logo_path, 50, height - 120, width=150, height=100, preserveAspectRatio=True)
        except:
            logger.warning("Could not add logo to certificate. Continuing without logo.")
        
        # Add certificate title
        c.setFont("Helvetica-Bold", 24)
        if self.language == "nl":
            title = "GDPR-NALEVINGSCERTIFICAAT"
        else:
            title = "GDPR COMPLIANCE CERTIFICATE"
        c.drawCentredString(width/2, height - 160, title)
        
        # Add decorative line
        c.setStrokeColor(colors.darkblue)
        c.setLineWidth(2)
        c.line(100, height - 180, width-100, height - 180)
        
        # Certificate content
        c.setFont("Helvetica", 12)
        
        # Date text
        if self.language == "nl":
            date_text = f"Datum: {datetime.now().strftime('%d-%m-%Y')}"
        else:
            date_text = f"Date: {datetime.now().strftime('%Y-%m-%d')}"
        c.drawString(50, height - 220, date_text)
        
        # Certificate ID
        if self.language == "nl":
            cert_id_text = f"Certificaat ID: {cert_id}"
        else:
            cert_id_text = f"Certificate ID: {cert_id}"
        c.drawString(width-250, height - 220, cert_id_text)
        
        # Main certificate text
        c.setFont("Helvetica", 14)
        y_position = height - 270
        
        if self.language == "nl":
            c.drawString(50, y_position, "Dit is om te certificeren dat:")
        else:
            c.drawString(50, y_position, "This is to certify that:")
        
        # Name of the scanned resource
        y_position -= 40
        c.setFont("Helvetica-Bold", 16)
        
        # Get the resource name based on scan type
        if scan_type == 'repository':
            resource_name = scan_results.get('repo_url', 'Unknown Repository')
        elif scan_type == 'database':
            resource_name = scan_results.get('db_name', 'Unknown Database')
        elif scan_type == 'website':
            resource_name = scan_results.get('url', 'Unknown Website')
        else:
            resource_name = scan_results.get('name', 'Unknown Resource')
        
        c.drawCentredString(width/2, y_position, resource_name)
        
        # Statement text
        y_position -= 60
        c.setFont("Helvetica", 14)
        
        if self.language == "nl":
            statement = (f"is gescand en voldoet volledig aan de vereisten van de "
                       f"Algemene Verordening Gegevensbescherming (AVG) "
                       f"op {datetime.now().strftime('%d-%m-%Y')}.")
        else:
            statement = (f"has been scanned and is fully compliant with the "
                       f"General Data Protection Regulation (GDPR) requirements "
                       f"as of {datetime.now().strftime('%Y-%m-%d')}.")
        
        # Split statement into multiple lines if needed
        max_width = width - 100
        words = statement.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if c.stringWidth(test_line, "Helvetica", 14) < max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        for line in lines:
            c.drawCentredString(width/2, y_position, line)
            y_position -= 25
        
        # Add scan details
        y_position -= 40
        c.setFont("Helvetica-Bold", 14)
        
        if self.language == "nl":
            c.drawString(50, y_position, "Scan Details:")
        else:
            c.drawString(50, y_position, "Scan Details:")
        
        y_position -= 30
        c.setFont("Helvetica", 12)
        
        # Format scan details
        scan_info = [
            ["Type", scan_results.get('scan_type', 'Unknown').capitalize()],
            ["Date", scan_results.get('scan_time', datetime.now().isoformat())[:10]],
            ["Status", "Fully Compliant ✓"],
            ["Items Scanned", str(scan_results.get('items_scanned', scan_results.get('file_count', 0)))],
            ["Region", scan_results.get('region', 'Global')]
        ]
        
        # Translate keys if language is Dutch
        if self.language == "nl":
            translations = {
                "Type": "Type",
                "Date": "Datum",
                "Status": "Status",
                "Items Scanned": "Items Gescand",
                "Region": "Regio",
                "Fully Compliant ✓": "Volledig Conform ✓"
            }
            
            for i, row in enumerate(scan_info):
                if row[0] in translations:
                    scan_info[i][0] = translations[row[0]]
                if row[1] in translations:
                    scan_info[i][1] = translations[row[1]]
        
        # Draw scan info as a table
        table_data = []
        for row in scan_info:
            table_data.append(row)
        
        table = Table(table_data, colWidths=[120, 300])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        table.wrapOn(c, width, height)
        table.drawOn(c, 70, y_position - (len(scan_info) * 20))
        
        # Add signature section
        y_position = 150
        
        c.setFont("Helvetica-Bold", 12)
        if self.language == "nl":
            c.drawString(70, y_position, "Gecertificeerd door DataGuardian Pro")
        else:
            c.drawString(70, y_position, "Certified by DataGuardian Pro")
        
        # Add signature line
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.line(70, y_position - 30, 250, y_position - 30)
        
        # Add certificate note
        c.setFont("Helvetica-Italic", 10)
        if self.language == "nl":
            note = ("Dit certificaat bevestigt dat er geen AVG/GDPR-problemen zijn "
                   "gedetecteerd tijdens de scan. Het blijft geldig tot de volgende "
                   "wijziging aan de gescande resource of maximaal 12 maanden.")
        else:
            note = ("This certificate confirms that no GDPR compliance issues were "
                   "detected during scanning. It remains valid until the next "
                   "modification to the scanned resource or for a maximum of 12 months.")
        
        # Draw the note at the bottom of the page
        text_obj = c.beginText(50, 50)
        text_obj.setFont("Helvetica-Italic", 10)
        
        # Split note into multiple lines if needed
        max_width = width - 100
        words = note.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if c.stringWidth(test_line, "Helvetica-Italic", 10) < max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        for line in lines:
            text_obj.textLine(line)
        
        c.drawText(text_obj)
        
        # Finalize the PDF
        c.save()
        buffer.seek(0)
        
        # Save the PDF to file
        with open(filepath, 'wb') as f:
            f.write(buffer.getvalue())
        
        logger.info(f"Generated compliance certificate: {filepath}")
        return filepath
    
    def generate_certificate_for_user(self, scan_id: str, user_info: Dict[str, Any],
                                     company_name: Optional[str] = None) -> Optional[str]:
        """
        Generate a certificate for a specific scan and user.
        
        Args:
            scan_id: ID of the scan to generate certificate for
            user_info: Dictionary containing user information
            company_name: Optional company name to include on certificate
            
        Returns:
            Path to the generated certificate PDF or None if certificate can't be generated
        """
        try:
            # Load scan results from database
            from services.results_aggregator import ResultsAggregator
            aggregator = ResultsAggregator()
            scan_results = aggregator.get_scan_by_id(scan_id)
            
            if not scan_results:
                logger.error(f"Scan with ID {scan_id} not found")
                return None
            
            return self.generate_certificate(scan_results, user_info, company_name)
        except Exception as e:
            logger.error(f"Error generating certificate: {str(e)}")
            return None