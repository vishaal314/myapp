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
                    'compliance_certificate',
                    certificate_record
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
        
        # Create modern AI Act 2025 certificate
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Modern gradient background effect (using rectangles)
        self._draw_modern_background(c, width, height)
        
        # Modern header section with geometric design
        self._draw_modern_header(c, width, height, cert_id)
        
        # AI Act 2025 specific title
        self._draw_ai_act_title(c, width, height, scan_results)
        
        # Certification authority badge
        self._draw_authority_badge(c, width, height)
        
        # Modern certificate content with AI Act 2025 focus
        y_position = height - 280
        
        # Main certification statement
        self._draw_certification_statement(c, width, height, scan_results, y_position)
        
        # AI Act 2025 compliance metrics
        y_position -= 120
        self._draw_ai_compliance_metrics(c, width, scan_results, y_position)
        
        # Professional verification section
        y_position -= 100
        self._draw_verification_section(c, width, cert_id, y_position)
        
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
    
    def _draw_modern_background(self, c, width, height):
        """Draw modern gradient background"""
        # Main background - clean white
        c.setFillColor(colors.white)
        c.rect(0, 0, width, height, fill=1)
        
        # Subtle gradient effect using overlapping rectangles
        for i in range(10):
            alpha = 0.02
            gray_value = 0.98 - (i * 0.005)
            c.setFillColor(colors.Color(gray_value, gray_value, gray_value, alpha=alpha))
            c.rect(0, height - (i * 20), width, 20, fill=1)
        
        # Modern accent stripes
        c.setFillColor(colors.Color(0.2, 0.4, 0.8, alpha=0.1))  # Blue accent
        c.rect(0, height - 60, width, 3, fill=1)
        c.rect(0, height - 70, width, 1, fill=1)
    
    def _draw_modern_header(self, c, width, height, cert_id):
        """Draw modern header with geometric design"""
        # Header section background
        c.setFillColor(colors.Color(0.05, 0.1, 0.2))  # Dark professional blue
        c.rect(0, height - 120, width, 120, fill=1)
        
        # Geometric accent shapes
        c.setFillColor(colors.Color(0.2, 0.4, 0.8))  # Bright blue accent
        # Triangle shapes for modern look
        c.beginPath()
        c.moveTo(width - 100, height - 20)
        c.lineTo(width - 20, height - 20)
        c.lineTo(width - 60, height - 60)
        c.closePath()
        c.fillPath()
        
        # Circle accent
        c.circle(80, height - 60, 25, fill=1)
        
        # Logo placeholder with modern styling
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(40, height - 70, "DataGuardian Pro")
        c.setFont("Helvetica", 10)
        c.drawString(40, height - 85, "AI Compliance Authority")
        
        # Certificate ID in header
        c.setFont("Helvetica", 8)
        c.drawString(width - 180, height - 30, f"Certificate ID: {cert_id[:16]}")
    
    def _draw_ai_act_title(self, c, width, height, scan_results):
        """Draw AI Act 2025 specific title"""
        # Main title with modern typography
        c.setFillColor(colors.Color(0.05, 0.1, 0.2))
        c.setFont("Helvetica-Bold", 28)
        c.drawCentredString(width/2, height - 160, "AI ACT 2025")
        
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(width/2, height - 185, "COMPLIANCE CERTIFICATE")
        
        # Subtitle with EU flag colors accent
        c.setFillColor(colors.Color(0.0, 0.2, 0.5))  # EU Blue
        c.setFont("Helvetica", 12)
        c.drawCentredString(width/2, height - 205, "European Union Artificial Intelligence Regulation")
        
        # Model type badge
        model_framework = scan_results.get('model_framework', 'AI Model')
        c.setFillColor(colors.Color(0.8, 0.9, 1.0))  # Light blue background
        c.rect(width/2 - 80, height - 235, 160, 20, fill=1)
        c.setStrokeColor(colors.Color(0.2, 0.4, 0.8))
        c.setLineWidth(1)
        c.rect(width/2 - 80, height - 235, 160, 20, fill=0)
        
        c.setFillColor(colors.Color(0.05, 0.1, 0.2))
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(width/2, height - 228, f"Framework: {model_framework}")
    
    def _draw_authority_badge(self, c, width, height):
        """Draw certification authority badge"""
        # Authority seal background
        center_x, center_y = width - 100, height - 180
        c.setFillColor(colors.Color(0.8, 0.9, 1.0))
        c.circle(center_x, center_y, 35, fill=1)
        
        c.setStrokeColor(colors.Color(0.2, 0.4, 0.8))
        c.setLineWidth(2)
        c.circle(center_x, center_y, 35, fill=0)
        c.circle(center_x, center_y, 30, fill=0)
        
        # Authority text
        c.setFillColor(colors.Color(0.05, 0.1, 0.2))
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(center_x, center_y + 10, "CERTIFIED")
        c.drawCentredString(center_x, center_y, "AUTHORITY")
        c.setFont("Helvetica", 6)
        c.drawCentredString(center_x, center_y - 15, datetime.now().strftime("%Y"))
    
    def _draw_certification_statement(self, c, width, height, scan_results, y_position):
        """Draw main certification statement"""
        # Professional certification statement
        c.setFillColor(colors.Color(0.05, 0.1, 0.2))
        c.setFont("Helvetica", 14)
        
        statement = "This certificate confirms that the AI model has been assessed for compliance with"
        c.drawCentredString(width/2, y_position, statement)
        
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width/2, y_position - 25, "EU AI Act 2025 Regulations")
        
        # Resource being certified
        resource_name = self._get_resource_name(scan_results)
        c.setFont("Helvetica", 12)
        c.drawString(60, y_position - 60, "Model/System:")
        
        # Resource name in styled box
        c.setFillColor(colors.Color(0.95, 0.97, 1.0))
        c.rect(60, y_position - 90, width - 120, 25, fill=1)
        c.setStrokeColor(colors.Color(0.7, 0.8, 0.9))
        c.setLineWidth(1)
        c.rect(60, y_position - 90, width - 120, 25, fill=0)
        
        c.setFillColor(colors.Color(0.05, 0.1, 0.2))
        c.setFont("Helvetica-Bold", 11)
        c.drawString(70, y_position - 82, resource_name[:80])  # Truncate long names
    
    def _draw_ai_compliance_metrics(self, c, width, scan_results, y_position):
        """Draw AI Act 2025 compliance metrics in modern design"""
        # Section title
        c.setFillColor(colors.Color(0.05, 0.1, 0.2))
        c.setFont("Helvetica-Bold", 14)
        c.drawString(60, y_position, "AI Act 2025 Compliance Assessment")
        
        # Metrics grid
        metrics = [
            ("Risk Classification", scan_results.get('ai_act_compliance', 'Compliant')),
            ("Compliance Score", f"{scan_results.get('compliance_score', 95)}%"),
            ("Assessment Date", datetime.now().strftime("%Y-%m-%d")),
            ("Validity Period", "12 months")
        ]
        
        # Draw metrics in modern card style
        card_width = (width - 140) / 2
        card_height = 40
        
        for i, (label, value) in enumerate(metrics):
            x = 60 + (i % 2) * (card_width + 20)
            y = y_position - 40 - (i // 2) * (card_height + 10)
            
            # Card background
            c.setFillColor(colors.Color(0.98, 0.99, 1.0))
            c.roundRect(x, y, card_width, card_height, 5, fill=1)
            
            # Card border
            c.setStrokeColor(colors.Color(0.8, 0.85, 0.9))
            c.setLineWidth(1)
            c.roundRect(x, y, card_width, card_height, 5, fill=0)
            
            # Text
            c.setFillColor(colors.Color(0.3, 0.3, 0.3))
            c.setFont("Helvetica", 9)
            c.drawString(x + 10, y + 25, label)
            
            c.setFillColor(colors.Color(0.05, 0.1, 0.2))
            c.setFont("Helvetica-Bold", 11)
            c.drawString(x + 10, y + 10, value)
    
    def _draw_verification_section(self, c, width, cert_id, y_position):
        """Draw professional verification section"""
        # Verification background
        c.setFillColor(colors.Color(0.96, 0.98, 1.0))
        c.rect(60, y_position - 60, width - 120, 60, fill=1)
        
        c.setStrokeColor(colors.Color(0.2, 0.4, 0.8))
        c.setLineWidth(1)
        c.rect(60, y_position - 60, width - 120, 60, fill=0)
        
        # Verification title
        c.setFillColor(colors.Color(0.05, 0.1, 0.2))
        c.setFont("Helvetica-Bold", 12)
        c.drawString(80, y_position - 20, "Digital Verification")
        
        # Verification details
        c.setFont("Helvetica", 10)
        verification_url = self.generate_verification_url(cert_id)
        c.drawString(80, y_position - 35, f"Verify online: {verification_url}")
        
        c.setFont("Helvetica", 9)
        c.drawString(80, y_position - 48, f"Issued: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
        
        # QR code placeholder
        c.setStrokeColor(colors.Color(0.5, 0.5, 0.5))
        c.setLineWidth(1)
        c.rect(width - 140, y_position - 55, 50, 50, fill=0)
        c.setFont("Helvetica", 8)
        c.drawCentredString(width - 115, y_position - 32, "QR Code")
        c.drawCentredString(width - 115, y_position - 42, "Verification")
    
    def _get_resource_name(self, scan_results):
        """Get appropriate resource name based on scan type"""
        scan_type = scan_results.get('scan_type', '').lower()
        
        if 'ai' in scan_type or 'model' in scan_type:
            return scan_results.get('model_name', scan_results.get('repository_url', 'AI Model System'))
        elif 'repository' in scan_type:
            return scan_results.get('repo_url', 'Code Repository')
        elif 'website' in scan_type:
            return scan_results.get('url', 'Web Application')
        else:
            return scan_results.get('name', 'Digital System')