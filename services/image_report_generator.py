"""
Image Report Generator for generating professional PDF certificates for image scan results.

This module creates formal compliance certificates with official seals, borders, 
and professional formatting for GDPR image privacy assessments.
"""

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Circle, Rect, Line
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from datetime import datetime
from typing import Dict, List, Any
import io
import os
import logging

logger = logging.getLogger(__name__)

class ImageReportGenerator:
    """Generates professional PDF reports for image scan results."""
    
    def __init__(self):
        """Initialize the report generator with professional styling."""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Set up custom paragraph styles for professional appearance."""
        
        # Certificate title style
        self.styles.add(ParagraphStyle(
            name='CertificateTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1a365d'),
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Normal'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2d3748'),
            fontName='Helvetica-Bold'
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.HexColor('#2b6cb0'),
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.HexColor('#e2e8f0'),
            borderPadding=8,
            backColor=colors.HexColor('#f7fafc')
        ))
        
        # Risk level styles
        self.styles.add(ParagraphStyle(
            name='CriticalRisk',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#991b1b'),
            fontName='Helvetica-Bold',
            backColor=colors.HexColor('#fee2e2'),
            borderWidth=1,
            borderColor=colors.HexColor('#fca5a5'),
            borderPadding=4
        ))
        
        self.styles.add(ParagraphStyle(
            name='HighRisk',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#92400e'),
            fontName='Helvetica-Bold',
            backColor=colors.HexColor('#fef3c7'),
            borderWidth=1,
            borderColor=colors.HexColor('#fcd34d'),
            borderPadding=4
        ))
        
        self.styles.add(ParagraphStyle(
            name='LowRisk',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#166534'),
            fontName='Helvetica-Bold',
            backColor=colors.HexColor('#dcfce7'),
            borderWidth=1,
            borderColor=colors.HexColor('#86efac'),
            borderPadding=4
        ))
    
    def _create_header_footer(self, canvas, doc):
        """Create professional header and footer for each page."""
        
        # Header
        canvas.saveState()
        
        # Header border
        canvas.setStrokeColor(colors.HexColor('#2b6cb0'))
        canvas.setLineWidth(2)
        canvas.line(50, A4[1] - 50, A4[0] - 50, A4[1] - 50)
        
        # Logo area (placeholder)
        canvas.setFillColor(colors.HexColor('#2b6cb0'))
        canvas.circle(80, A4[1] - 30, 15, fill=1)
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.drawCentredString(80, A4[1] - 33, "DG")
        
        # Header text
        canvas.setFillColor(colors.HexColor('#1a365d'))
        canvas.setFont("Helvetica-Bold", 16)
        canvas.drawString(110, A4[1] - 35, "DataGuardian Pro")
        canvas.setFont("Helvetica", 10)
        canvas.drawString(110, A4[1] - 50, "Enterprise Privacy Compliance Platform")
        
        # Certificate seal
        canvas.setFillColor(colors.HexColor('#dc2626'))
        canvas.circle(A4[0] - 80, A4[1] - 30, 20, fill=1)
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.drawCentredString(A4[0] - 80, A4[1] - 33, "CERTIFIED")
        
        # Footer
        canvas.setStrokeColor(colors.HexColor('#e2e8f0'))
        canvas.setLineWidth(1)
        canvas.line(50, 50, A4[0] - 50, 50)
        
        canvas.setFillColor(colors.HexColor('#64748b'))
        canvas.setFont("Helvetica", 8)
        canvas.drawString(50, 35, f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M UTC')}")
        canvas.drawRightString(A4[0] - 50, 35, f"Page {doc.page}")
        canvas.drawCentredString(A4[0] / 2, 35, "This certificate verifies GDPR compliance assessment results")
        
        canvas.restoreState()
    
    def generate_pdf_report(self, scan_results: Dict[str, Any]) -> bytes:
        """
        Generate a professional PDF certificate for image scan results.
        
        Args:
            scan_results: Dictionary containing image scan results
            
        Returns:
            PDF content as bytes
        """
        
        # Create PDF buffer
        buffer = io.BytesIO()
        
        # Create document with custom page template
        doc = BaseDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50,
                             topMargin=80, bottomMargin=80)
        
        # Create frame and page template
        frame = Frame(50, 80, A4[0] - 100, A4[1] - 160, id='normal')
        template = PageTemplate(id='certificate', frames=[frame], onPage=self._create_header_footer)
        doc.addPageTemplates([template])
        
        # Build story (content)
        story = []
        
        # Certificate title
        story.append(Paragraph("IMAGE PRIVACY COMPLIANCE CERTIFICATE", self.styles['CertificateTitle']))
        story.append(Spacer(1, 20))
        
        # Subtitle
        story.append(Paragraph("GDPR Image Data Protection Assessment Report", self.styles['Subtitle']))
        story.append(Spacer(1, 30))
        
        # Executive summary
        metadata = scan_results.get('metadata', {})
        risk_summary = scan_results.get('risk_summary', {})
        findings = scan_results.get('findings', [])
        
        # Certificate details table
        cert_data = [
            ['Scan Type:', 'Image Privacy Assessment'],
            ['Scan Date:', metadata.get('scan_time', 'Unknown')],
            ['Images Analyzed:', str(metadata.get('images_scanned', 0))],
            ['PII Findings:', str(len(findings))],
            ['Risk Level:', risk_summary.get('level', 'Unknown')],
            ['Risk Score:', f"{risk_summary.get('score', 0)}/100"],
            ['Compliance Region:', metadata.get('region', 'Unknown')],
            ['Assessment Standard:', 'GDPR Article 6, 9 & Dutch UAVG']
        ]
        
        cert_table = Table(cert_data, colWidths=[2*inch, 3*inch])
        cert_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f7fafc')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2d3748')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1a365d')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
        ]))
        
        story.append(cert_table)
        story.append(Spacer(1, 30))
        
        # Risk assessment section
        story.append(Paragraph("RISK ASSESSMENT SUMMARY", self.styles['SectionHeader']))
        
        overall_risk = risk_summary.get('level', 'Unknown')
        risk_color = {
            'Critical': colors.HexColor('#991b1b'),
            'High': colors.HexColor('#dc2626'),
            'Medium': colors.HexColor('#d97706'),
            'Low': colors.HexColor('#059669')
        }.get(overall_risk, colors.black)
        
        risk_style = ParagraphStyle(
            name='RiskLevel',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=risk_color,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            borderWidth=2,
            borderColor=risk_color,
            borderPadding=10,
            backColor=colors.HexColor('#f8fafc') if overall_risk == 'Low' else colors.HexColor('#fef2f2')
        )
        
        story.append(Paragraph(f"Overall Risk Level: {overall_risk}", risk_style))
        story.append(Spacer(1, 20))
        
        # Risk factors
        factors = risk_summary.get('factors', [])
        if factors:
            story.append(Paragraph("Risk Factors Identified:", self.styles['Normal']))
            for factor in factors:
                story.append(Paragraph(f"• {factor}", self.styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Detailed findings section
        if findings:
            story.append(Paragraph("DETAILED PII FINDINGS", self.styles['SectionHeader']))
            
            # Group findings by type
            findings_by_type = {}
            for finding in findings:
                pii_type = finding.get('type', 'Unknown')
                if pii_type not in findings_by_type:
                    findings_by_type[pii_type] = []
                findings_by_type[pii_type].append(finding)
            
            for pii_type, type_findings in findings_by_type.items():
                story.append(Paragraph(f"{pii_type} ({len(type_findings)} instances)", 
                                     self.styles['Heading3']))
                
                # Create findings table
                findings_data = [['Source Image', 'Risk Level', 'Confidence', 'Detection Method']]
                
                for finding in type_findings:
                    findings_data.append([
                        os.path.basename(finding.get('source', 'Unknown')),
                        finding.get('risk_level', 'Unknown'),
                        f"{finding.get('confidence', 0):.0%}",
                        finding.get('extraction_method', 'Unknown')
                    ])
                
                findings_table = Table(findings_data, colWidths=[2*inch, 1*inch, 1*inch, 1.5*inch])
                findings_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2b6cb0')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
                ]))
                
                story.append(findings_table)
                story.append(Spacer(1, 20))
                
                # Add GDPR compliance note for this PII type
                sample_finding = type_findings[0]
                gdpr_reason = sample_finding.get('reason', 'Requires data protection compliance')
                story.append(Paragraph(f"<b>GDPR Compliance Note:</b> {gdpr_reason}", 
                                     self.styles['Normal']))
                story.append(Spacer(1, 15))
        
        else:
            story.append(Paragraph("PII ASSESSMENT RESULTS", self.styles['SectionHeader']))
            story.append(Paragraph("✓ No personal data detected in analyzed images", 
                                 self.styles['LowRisk']))
            story.append(Spacer(1, 20))
        
        # Compliance recommendations
        story.append(Paragraph("COMPLIANCE RECOMMENDATIONS", self.styles['SectionHeader']))
        
        recommendations = self._generate_recommendations(scan_results)
        for rec in recommendations:
            story.append(Paragraph(f"• {rec}", self.styles['Normal']))
        
        story.append(Spacer(1, 30))
        
        # Certificate validation
        story.append(Paragraph("CERTIFICATE VALIDATION", self.styles['SectionHeader']))
        
        validation_info = f"""
        This certificate validates that image privacy assessment was conducted in accordance with:
        • General Data Protection Regulation (GDPR) Articles 6, 9, and 32
        • Dutch Algemene Verordening Gegevensbescherming (UAVG)
        • ISO/IEC 27001:2013 Information Security Standards
        • Data Protection Impact Assessment (DPIA) Guidelines
        
        Assessment performed using DataGuardian Pro enterprise-grade scanning technology
        with OCR analysis, computer vision PII detection, and GDPR compliance validation.
        """
        
        story.append(Paragraph(validation_info, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Digital signature area
        signature_data = [
            ['Digital Certificate ID:', f"IMG-{datetime.now().strftime('%Y%m%d%H%M%S')}"],
            ['Issued By:', 'DataGuardian Pro Compliance Engine'],
            ['Valid From:', datetime.now().strftime('%B %d, %Y')],
            ['Verification:', 'enterprise@dataguardian.pro']
        ]
        
        signature_table = Table(signature_data, colWidths=[2*inch, 3*inch])
        signature_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f9ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e40af')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#3b82f6')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        story.append(signature_table)
        
        # Build PDF
        doc.build(story)
        
        # Return PDF content
        buffer.seek(0)
        return buffer.getvalue()
    
    def _generate_recommendations(self, scan_results: Dict[str, Any]) -> List[str]:
        """Generate compliance recommendations based on scan results."""
        
        recommendations = []
        findings = scan_results.get('findings', [])
        risk_level = scan_results.get('risk_summary', {}).get('level', 'Low')
        
        if not findings:
            recommendations.extend([
                "Continue monitoring image uploads for PII detection",
                "Implement automated image scanning for new uploads",
                "Maintain current data protection practices",
                "Regular compliance audits recommended quarterly"
            ])
        else:
            if risk_level in ['Critical', 'High']:
                recommendations.extend([
                    "IMMEDIATE ACTION REQUIRED: Review and secure identified PII",
                    "Implement data minimization practices for image processing",
                    "Ensure explicit consent for biometric data processing",
                    "Consider anonymization or pseudonymization techniques"
                ])
            
            # Specific recommendations based on PII types found
            pii_types = set(finding.get('type', '') for finding in findings)
            
            if 'FACE_BIOMETRIC' in pii_types:
                recommendations.append("Obtain explicit consent for facial biometric processing per GDPR Article 9")
            
            if 'PASSPORT' in pii_types or 'ID_CARD' in pii_types:
                recommendations.append("Implement enhanced security measures for identity document processing")
            
            if 'PAYMENT_CARD' in pii_types:
                recommendations.append("Ensure PCI DSS compliance for payment card data handling")
            
            recommendations.extend([
                "Document legal basis for personal data processing",
                "Update privacy notices to reflect image data processing",
                "Implement technical and organizational measures per GDPR Article 32",
                "Conduct regular DPIA assessments for image processing activities"
            ])
        
        return recommendations

def create_image_report_generator() -> ImageReportGenerator:
    """Factory function to create ImageReportGenerator instance."""
    return ImageReportGenerator()