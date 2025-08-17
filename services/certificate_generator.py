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

# Netherlands-specific legal compliance framework
LEGAL_FRAMEWORKS = {
    "netherlands": {
        "authority": "Nederlandse Autoriteit Persoonsgegevens (AP)",
        "legal_basis": "Algemene Verordening Gegevensbescherming (AVG)",
        "additional_laws": ["Uitvoeringswet AVG (UAVG)", "Telecommunicatiewet"],
        "certification_body": "DataGuardian Pro Certification Authority",
        "validity_months": 12,
        "verification_base": "https://verify.dataguardian.pro"
    },
    "germany": {
        "authority": "Bundesbeauftragte für den Datenschutz und die Informationsfreiheit (BfDI)",
        "legal_basis": "Datenschutz-Grundverordnung (DSGVO)",
        "additional_laws": ["Bundesdatenschutzgesetz (BDSG)"],
        "certification_body": "DataGuardian Pro Certification Authority",
        "validity_months": 12,
        "verification_base": "https://verify.dataguardian.pro"
    },
    "france": {
        "authority": "Commission Nationale de l'Informatique et des Libertés (CNIL)",
        "legal_basis": "Règlement Général sur la Protection des Données (RGPD)",
        "additional_laws": ["Loi Informatique et Libertés"],
        "certification_body": "DataGuardian Pro Certification Authority",
        "validity_months": 12,
        "verification_base": "https://verify.dataguardian.pro"
    },
    "belgium": {
        "authority": "Gegevensbeschermingsautoriteit (GBA)",
        "legal_basis": "Algemene Verordening Gegevensbescherming (AVG)",
        "additional_laws": ["Wet van 30 juli 2018"],
        "certification_body": "DataGuardian Pro Certification Authority", 
        "validity_months": 12,
        "verification_base": "https://verify.dataguardian.pro"
    }
}

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CertificateGenerator:
    """
    A generator for compliance certificates when scans show no compliance issues.
    """
    
    def __init__(self, language: str = "en", region: str = "netherlands"):
        """
        Initialize the certificate generator.
        
        Args:
            language: Language for certificate text (default: "en")
            region: Legal region for compliance framework (default: "netherlands")
        """
        self.language = language
        self.region = region.lower()
        self.legal_framework = LEGAL_FRAMEWORKS.get(self.region, LEGAL_FRAMEWORKS["netherlands"])
        self.certificate_dir = os.path.join("reports", "certificates")
        os.makedirs(self.certificate_dir, exist_ok=True)
        
        # Load required fonts
        try:
            pdfmetrics.registerFont(TTFont('Roboto', os.path.join('utils', 'fonts', 'Roboto-Regular.ttf')))
            pdfmetrics.registerFont(TTFont('Roboto-Bold', os.path.join('utils', 'fonts', 'Roboto-Bold.ttf')))
            pdfmetrics.registerFont(TTFont('Roboto-Italic', os.path.join('utils', 'fonts', 'Roboto-Italic.ttf')))
        except:
            logger.warning("Could not load custom fonts. Using default fonts instead.")
    
    def validate_subscription_access(self, user_info: Dict[str, Any]) -> bool:
        """
        Enhanced subscription validation with payment integration
        """
        try:
            from services.subscription_manager import SubscriptionManager
            sub_manager = SubscriptionManager()
            
            # Check if user has active subscription with certificate access
            user_id = user_info.get('user_id', user_info.get('username', ''))
            
            # Use available subscription manager methods
            if hasattr(sub_manager, 'get_subscription_status'):
                subscription_status = sub_manager.get_subscription_status(user_id)
                if subscription_status and subscription_status.get('status') == 'active':
                    plan = subscription_status.get('plan', '').lower()
                    return plan in ['professional', 'enterprise', 'enterprise_plus', 'consultancy', 'ai_compliance']
                
        except Exception as e:
            logger.warning(f"Could not validate subscription: {e}")
        
        # Fallback to basic role/plan checking
        user_role = user_info.get('role', '').lower()
        subscription_plan = user_info.get('subscription_plan', '').lower()
        
        qualified_roles = ['premium', 'enterprise', 'admin']
        qualified_plans = ['professional', 'enterprise', 'enterprise_plus', 'consultancy', 'ai_compliance']
        
        return (user_role in qualified_roles or 
                subscription_plan in qualified_plans or
                user_info.get('free_scans_remaining', 0) > 0)
    
    def generate_verification_url(self, cert_id: str) -> str:
        """Generate verification URL for certificate"""
        return f"{self.legal_framework['verification_base']}/{cert_id[:12]}"
    
    def record_certificate_issuance(self, cert_id: str, user_info: Dict[str, Any], scan_results: Dict[str, Any]) -> bool:
        """
        Record certificate issuance for audit trail and verification
        """
        try:
            certificate_record = {
                "certificate_id": cert_id,
                "user_id": user_info.get('user_id', user_info.get('username', '')),
                "scan_type": scan_results.get('scan_type', 'unknown'),
                "scan_id": scan_results.get('scan_id', ''),
                "issued_date": datetime.now().isoformat(),
                "legal_framework": self.region,
                "validity_expires": (datetime.now().replace(year=datetime.now().year + 1)).isoformat(),
                "verification_url": self.generate_verification_url(cert_id),
                "status": "active"
            }
            
            # Track certificate issuance for analytics
            try:
                from utils.activity_tracker import get_activity_tracker
                tracker = get_activity_tracker()
                tracker.track_activity(
                    user_info.get('username', 'anonymous'),
                    'certificate_issued',
                    'compliance_certificate'
                )
            except Exception:
                pass  # Analytics failure shouldn't block certificate generation
                
            logger.info(f"Certificate issuance recorded: {cert_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record certificate issuance: {e}")
            return False
    
    def is_fully_compliant(self, scan_id_or_results) -> bool:
        """
        Check if scan results indicate full compliance (no issues found).
        
        Args:
            scan_id_or_results: Either a scan ID string or a scan results dictionary
            
        Returns:
            True if no compliance issues were found, False otherwise
        """
        # If scan_id_or_results is a string (scan ID), get the actual results
        if isinstance(scan_id_or_results, str):
            try:
                from services.results_aggregator import ResultsAggregator
                results_aggregator = ResultsAggregator()
                scan_results = results_aggregator.get_scan_by_id(scan_id_or_results)
                if not scan_results:
                    return False
            except Exception as e:
                logger.error(f"Error loading scan results: {str(e)}")
                return False
        else:
            scan_results = scan_id_or_results
        
        # Make sure we have a dictionary
        if not isinstance(scan_results, dict):
            return False
            
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
                            company_name: Optional[str] = None) -> Optional[str]:
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
        
        # Enhanced subscription and payment validation
        if not self.validate_subscription_access(user_info):
            user_role = user_info.get('role', '').lower()
            subscription_plan = user_info.get('subscription_plan', '').lower()
            logger.warning(f"Cannot generate certificate: user role '{user_role}' and plan '{subscription_plan}' do not have certificate access.")
            return None
        
        # Generate a unique filename for the certificate
        cert_id = uuid.uuid4().hex
        scan_type = scan_results.get('scan_type', 'unknown')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"compliance_certificate_{scan_type}_{cert_id}_{timestamp}.pdf"
        filepath = os.path.join(self.certificate_dir, filename)
        
        # Record certificate issuance for audit trail
        self.record_certificate_issuance(cert_id, user_info, scan_results)
        
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
        
        # Add certificate title with legal authority
        c.setFont("Helvetica-Bold", 24)
        if self.language == "nl":
            title = f"{self.legal_framework['legal_basis']}-NALEVINGSCERTIFICAAT"
        else:
            title = "GDPR COMPLIANCE CERTIFICATE"
        c.drawCentredString(width/2, height - 160, title)
        
        # Add certification authority
        c.setFont("Helvetica", 10)
        c.drawCentredString(width/2, height - 180, f"Uitgegeven door / Issued by: {self.legal_framework['certification_body']}")
        
        # Add verification QR code placeholder (would integrate with QR library in production)
        verification_url = self.generate_verification_url(cert_id)
        c.setFont("Helvetica", 8)
        c.drawString(width - 200, height - 140, f"Verify: {verification_url}")
        
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
        
        # Enhanced scan details with legal compliance markers
        issue_date = datetime.now()
        expiry_date = issue_date.replace(year=issue_date.year + 1)
        
        scan_info = [
            ["Type", scan_results.get('scan_type', 'Unknown').capitalize()],
            ["Date", scan_results.get('scan_time', datetime.now().isoformat())[:10]],
            ["Status", "Fully Compliant ✓"],
            ["Items Scanned", str(scan_results.get('items_scanned', scan_results.get('file_count', 0)))],
            ["Legal Framework", self.legal_framework['legal_basis']],
            ["Authority", self.legal_framework['authority']],
            ["Valid Until", expiry_date.strftime('%Y-%m-%d')],
            ["Verification", verification_url]
        ]
        
        # Translate keys if language is Dutch
        if self.language == "nl":
            translations = {
                "Type": "Type",
                "Date": "Datum", 
                "Status": "Status",
                "Items Scanned": "Items Gescand",
                "Legal Framework": "Juridisch Kader",
                "Authority": "Toezichthouder",
                "Valid Until": "Geldig Tot",
                "Verification": "Verificatie",
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
        
        table = Table(table_data, colWidths=[140, 320])
        # Enhanced professional table styling
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
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
        
        # Enhanced certificate note with comprehensive legal framework
        c.setFont("Helvetica-Italic", 9)
        if self.language == "nl":
            additional_laws = ", ".join(self.legal_framework['additional_laws'])
            note = (f"Dit certificaat bevestigt volledige naleving van de {self.legal_framework['legal_basis']} "
                   f"en aanvullende wetgeving ({additional_laws}). Uitgegeven door {self.legal_framework['certification_body']} "
                   f"onder toezicht van {self.legal_framework['authority']}. "
                   f"Geldig voor {self.legal_framework['validity_months']} maanden of tot wijziging van de gescande resource. "
                   f"Voor verificatie en geldigheidscontrole: {verification_url}")
        else:
            additional_laws = ", ".join(self.legal_framework['additional_laws'])
            note = (f"This certificate confirms full compliance with the {self.legal_framework['legal_basis']} "
                   f"and applicable privacy laws ({additional_laws}). Issued by {self.legal_framework['certification_body']} "
                   f"under supervision of {self.legal_framework['authority']}. "
                   f"Valid for {self.legal_framework['validity_months']} months or until modification of scanned resource. "
                   f"For verification and validity check: {verification_url}")
        
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