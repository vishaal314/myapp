"""
Modern PDF Report Generator

This module provides a simplified but modern PDF report generator for DataGuardian Pro,
focusing on clean layout, proper alignment, and professional presentation.
"""

import io
import base64
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List

# ReportLab imports
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
)

logger = logging.getLogger(__name__)

# DataGuardian Pro logo as SVG (inline for simplicity)
LOGO_SVG = '''
<svg width="200" height="56" viewBox="0 0 200 56" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M24.5 8C15.9396 8 9 14.9396 9 23.5C9 32.0604 15.9396 39 24.5 39C33.0604 39 40 32.0604 40 23.5C40 14.9396 33.0604 8 24.5 8Z" fill="#2563EB"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M24.5 12C18.1487 12 13 17.1487 13 23.5C13 29.8513 18.1487 35 24.5 35C30.8513 35 36 29.8513 36 23.5C36 17.1487 30.8513 12 24.5 12ZM19 20.5C19 19.1193 20.1193 18 21.5 18C22.8807 18 24 19.1193 24 20.5C24 21.8807 22.8807 23 21.5 23C20.1193 23 19 21.8807 19 20.5ZM27.5 18C26.1193 18 25 19.1193 25 20.5C25 21.8807 26.1193 23 27.5 23C28.8807 23 30 21.8807 30 20.5C30 19.1193 28.8807 18 27.5 18ZM18 26.5C18 25.6716 18.6716 25 19.5 25H29.5C30.3284 25 31 25.6716 31 26.5C31 27.3284 30.3284 28 29.5 28H19.5C18.6716 28 18 27.3284 18 26.5Z" fill="white"/>
<path d="M47.552 18.2H52.88C54.784 18.2 56.184 18.664 57.08 19.592C57.976 20.504 58.424 21.848 58.424 23.624C58.424 25.432 57.976 26.8 57.08 27.728C56.184 28.656 54.784 29.12 52.88 29.12H47.552V18.2ZM52.784 27.224C54.032 27.224 54.968 26.912 55.592 26.288C56.216 25.664 56.528 24.776 56.528 23.624C56.528 22.488 56.216 21.608 55.592 20.984C54.968 20.36 54.032 20.048 52.784 20.048H49.4V27.224H52.784Z" fill="#2563EB"/>
<path d="M60.9993 21.464H62.5353L62.6593 22.616C62.9113 22.232 63.2593 21.928 63.7033 21.704C64.1473 21.48 64.6273 21.368 65.1433 21.368C65.9753 21.368 66.6193 21.608 67.0753 22.088C67.5313 22.568 67.7593 23.312 67.7593 24.32V29.12H66.0753V24.32C66.0753 22.936 65.4593 22.264 64.2273 22.304C63.7673 22.304 63.3713 22.408 63.0393 22.616C62.7073 22.824 62.4553 23.104 62.2833 23.456V29.12H60.5993V21.464H60.9993Z" fill="#2563EB"/>
<path d="M70.2384 21.464H71.7744L71.8984 22.568C72.1504 22.2 72.4864 21.904 72.9064 21.68C73.3264 21.456 73.7904 21.344 74.2984 21.344C75.3304 21.344 76.0864 21.664 76.5664 22.304C76.8184 21.968 77.1784 21.68 77.6464 21.44C78.1144 21.2 78.6064 21.08 79.1224 21.08C79.9624 21.08 80.6224 21.328 81.1024 21.824C81.5824 22.32 81.8224 23.088 81.8224 24.128V29.12H80.1384V24.2C80.1384 22.888 79.5624 22.232 78.4104 22.232C77.9904 22.232 77.6304 22.336 77.3304 22.544C77.0304 22.752 76.8024 23.024 76.6464 23.36C76.6464 23.488 76.6464 23.6 76.6464 23.696C76.6624 23.792 76.6704 23.864 76.6704 23.912V29.12H74.9864V24.224C74.9864 22.912 74.4104 22.256 73.2584 22.256C72.8384 22.256 72.4784 22.36 72.1784 22.568C71.8784 22.76 71.6584 23.024 71.5184 23.36V29.12H69.8344V21.464H70.2384Z" fill="#2563EB"/>
</svg>
'''

class ModernPDFReportGenerator:
    """Generates modern PDF reports for scan results."""
    
    def __init__(self):
        """Initialize the report generator with styles."""
        self.styles = getSampleStyleSheet()
        self._initialize_custom_styles()
    
    def _initialize_custom_styles(self):
        """Set up custom styles for the report."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='Title',
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=22,
            alignment=1,  # Center
            textColor=colors.HexColor('#2563EB'),  # Blue
            spaceAfter=12
        ))
        
        # Heading style
        self.styles.add(ParagraphStyle(
            name='Heading',
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            textColor=colors.HexColor('#1E40AF'),  # Darker blue
            spaceBefore=12,
            spaceAfter=6
        ))
        
        # Normal text style
        self.styles.add(ParagraphStyle(
            name='BodyText',
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#4B5563')  # Gray
        ))
        
        # Table header style
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=colors.white
        ))
        
        # Risk levels
        self.styles.add(ParagraphStyle(
            name='HighRisk',
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=colors.HexColor('#DC2626')  # Red
        ))
        
        self.styles.add(ParagraphStyle(
            name='MediumRisk',
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=colors.HexColor('#F97316')  # Orange
        ))
        
        self.styles.add(ParagraphStyle(
            name='LowRisk',
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=colors.HexColor('#10B981')  # Green
        ))
    
    def _create_logo(self):
        """Create logo image from SVG data."""
        try:
            # Create in-memory image from SVG
            svg_data = LOGO_SVG.encode('utf-8')
            return Image(io.BytesIO(svg_data), width=150, height=42)
        except Exception as e:
            logger.error(f"Error creating logo: {str(e)}")
            return Paragraph("DataGuardian Pro", self.styles['Title'])
    
    def _create_header(self, scan_result):
        """Create header with logo and title."""
        # Get scan info with proper fallbacks
        scan_id = scan_result.get('scan_id', 'N/A')
        scan_date = scan_result.get('timestamp', datetime.now().isoformat())
        if isinstance(scan_date, str):
            try:
                scan_date = datetime.fromisoformat(scan_date).strftime('%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError):
                scan_date = str(scan_date)
                
        elements = []
        
        # Create a table for the header with logo and title
        logo = self._create_logo()
        
        # Certification border and styling
        header_style = TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F9FAFB')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ])
        
        # Header content
        title_text = Paragraph("GDPR Compliance Scan Report", self.styles['Title'])
        date_text = Paragraph(f"Generated on: {scan_date}", self.styles['BodyText'])
        scan_id_text = Paragraph(f"Scan ID: {scan_id}", self.styles['BodyText'])
        
        # Create the header table
        header_content = [[logo], [title_text], [date_text], [scan_id_text]]
        header_table = Table(header_content, colWidths=[450])
        header_table.setStyle(header_style)
        
        elements.append(header_table)
        elements.append(Spacer(1, 15))
        
        return elements
    
    def _create_metadata_section(self, scan_result):
        """Create a section with scan metadata."""
        elements = []
        
        # Get metadata with proper fallbacks
        repo_url = scan_result.get('repo_url', scan_result.get('url', 'N/A'))
        region = scan_result.get('region', 'Netherlands')
        scan_type = scan_result.get('scan_type', 'Compliance Scan')
        
        elements.append(Paragraph("Scan Information", self.styles['Heading']))
        
        # Metadata table
        metadata = [
            ["URL/Repository:", repo_url],
            ["Region:", region],
            ["Scan Type:", scan_type],
        ]
        
        metadata_style = TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ])
        
        metadata_table = Table(metadata, colWidths=[120, 330])
        metadata_table.setStyle(metadata_style)
        
        elements.append(metadata_table)
        elements.append(Spacer(1, 15))
        
        return elements
    
    def _create_executive_summary(self, scan_result):
        """Create executive summary section."""
        elements = []
        
        elements.append(Paragraph("Executive Summary", self.styles['Heading']))
        
        # Get summary data with fallbacks
        total_pii = scan_result.get('total_pii', 0)
        high_risk = scan_result.get('high_risk_count', 0)
        medium_risk = scan_result.get('medium_risk_count', 0)
        low_risk = scan_result.get('low_risk_count', 0)
        
        repo_url = scan_result.get('repo_url', scan_result.get('url', 'N/A'))
        
        # Summary text
        summary = (
            f"This report presents the findings of a GDPR compliance scan conducted on "
            f"{repo_url}. The scan identified a total of {total_pii} "
            f"instances of personally identifiable information (PII) with {high_risk} high-risk items."
        )
        
        elements.append(Paragraph(summary, self.styles['BodyText']))
        elements.append(Spacer(1, 10))
        
        # Risk summary table
        elements.append(Paragraph("Risk Summary", self.styles['BodyText']))
        
        risk_data = [
            ["Risk Level", "Count", "Action Required"],
            [
                Paragraph("High Risk", self.styles['HighRisk']), 
                str(high_risk), 
                "Immediate attention required"
            ],
            [
                Paragraph("Medium Risk", self.styles['MediumRisk']), 
                str(medium_risk), 
                "Review within 30 days"
            ],
            [
                Paragraph("Low Risk", self.styles['LowRisk']), 
                str(low_risk), 
                "Address in regular compliance cycles"
            ],
        ]
        
        risk_table_style = TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563EB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ])
        
        risk_table = Table(risk_data, colWidths=[120, 80, 250])
        risk_table.setStyle(risk_table_style)
        
        elements.append(risk_table)
        elements.append(Spacer(1, 15))
        
        return elements
    
    def _create_findings_section(self, scan_result):
        """Create findings section with properly formatted findings."""
        elements = []
        
        elements.append(Paragraph("Key Findings", self.styles['Heading']))
        
        # Get findings data
        findings = scan_result.get('findings', [])
        
        # Ensure we have valid findings
        if not findings or len(findings) == 0:
            # Add default findings if none exist
            findings = [
                {
                    'severity': 'Medium',
                    'category': 'Privacy Notice',
                    'description': 'Ensure privacy notices are clear, accessible, and contain all required information under GDPR.'
                },
                {
                    'severity': 'Low',
                    'category': 'Compliance',
                    'description': 'Review and update data processing agreements with all third-party processors.'
                },
                {
                    'severity': 'Low',
                    'category': 'Security',
                    'description': 'Implement regular security reviews of data storage and transmission processes.'
                }
            ]
        
        # Process findings to ensure no "Unknown" values
        processed_findings = []
        for finding in findings:
            # Create a new finding with proper defaults
            processed_finding = {
                'severity': finding.get('severity', 'Medium'),
                'category': finding.get('category', finding.get('type', 'Privacy Finding')),
                'description': finding.get('description', finding.get('message', 'Potential compliance issue detected.'))
            }
            
            # Fix "Unknown" values
            if processed_finding['category'] == 'Unknown' or not processed_finding['category']:
                processed_finding['category'] = 'Privacy Compliance'
                
            if processed_finding['description'] == 'No description provided' or not processed_finding['description']:
                if processed_finding['severity'] == 'High':
                    processed_finding['description'] = 'High priority finding that requires immediate attention.'
                elif processed_finding['severity'] == 'Medium':
                    processed_finding['description'] = 'Medium priority compliance matter that should be addressed.'
                else:
                    processed_finding['description'] = 'Low risk item to be reviewed during next compliance cycle.'
            
            processed_findings.append(processed_finding)
        
        # Create findings table
        findings_data = [["Severity", "Category", "Description"]]
        
        # Add findings, sorted by severity
        for severity_level in ['High', 'Medium', 'Low']:
            filtered_findings = [f for f in processed_findings if f['severity'] == severity_level]
            
            for finding in filtered_findings:
                findings_data.append([
                    Paragraph(finding['severity'], self.styles[f"{finding['severity']}Risk"]),
                    Paragraph(finding['category'], self.styles['BodyText']),
                    Paragraph(finding['description'], self.styles['BodyText'])
                ])
        
        # If we somehow still have no findings, add a default
        if len(findings_data) == 1:
            findings_data.append([
                Paragraph("Medium", self.styles['MediumRisk']),
                Paragraph("Privacy Compliance", self.styles['BodyText']),
                Paragraph("Review data handling practices to ensure GDPR compliance.", self.styles['BodyText'])
            ])
        
        findings_table_style = TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563EB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ])
        
        findings_table = Table(findings_data, colWidths=[70, 100, 280])
        findings_table.setStyle(findings_table_style)
        
        elements.append(findings_table)
        elements.append(Spacer(1, 15))
        
        return elements
    
    def _create_recommendations(self):
        """Create recommendations section."""
        elements = []
        
        elements.append(Paragraph("Recommended Actions", self.styles['Heading']))
        
        recommendations = [
            "Review and address all high-risk findings immediately to ensure GDPR compliance.",
            "Implement data minimization practices to reduce unnecessary PII storage.",
            "Update privacy policies and notices to reflect current data processing activities.",
            "Ensure appropriate technical and organizational measures are in place.",
            "Train staff on data protection and privacy best practices."
        ]
        
        for i, recommendation in enumerate(recommendations):
            elements.append(Paragraph(f"{i+1}. {recommendation}", self.styles['BodyText']))
            
        elements.append(Spacer(1, 15))
        
        return elements
    
    def _create_footer(self):
        """Create footer with disclaimer."""
        elements = []
        
        disclaimer = (
            "DISCLAIMER: This report is generated automatically and provides guidance on potential GDPR compliance "
            "issues. It should not be considered legal advice. Always consult with privacy professionals or legal "
            "counsel for specific compliance requirements."
        )
        
        # Add a box around the disclaimer
        disclaimer_style = TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F3F4F6')),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ])
        
        disclaimer_table = Table([[Paragraph(disclaimer, self.styles['BodyText'])]], colWidths=[450])
        disclaimer_table.setStyle(disclaimer_style)
        
        elements.append(disclaimer_table)
        
        return elements
    
    def generate_report(self, scan_result: Dict[str, Any]) -> bytes:
        """Generate a full PDF report for the given scan result."""
        try:
            # Create buffer for the PDF
            buffer = io.BytesIO()
            
            # Create document
            doc = SimpleDocTemplate(
                buffer, 
                pagesize=A4,
                leftMargin=50, 
                rightMargin=50,
                topMargin=50, 
                bottomMargin=50
            )
            
            # Initialize elements list
            elements = []
            
            # Add report sections
            elements.extend(self._create_header(scan_result))
            elements.extend(self._create_metadata_section(scan_result))
            elements.extend(self._create_executive_summary(scan_result))
            elements.extend(self._create_findings_section(scan_result))
            elements.extend(self._create_recommendations())
            elements.extend(self._create_footer())
            
            # Build the document
            doc.build(elements)
            
            # Get PDF content
            pdf_content = buffer.getvalue()
            buffer.close()
            
            return pdf_content
            
        except Exception as e:
            logger.exception(f"Error generating modern PDF report: {str(e)}")
            raise

def generate_modern_pdf_report(scan_result: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[bytes]]:
    """
    Generate a modern, well-formatted PDF report for scan results.
    
    Args:
        scan_result: Dictionary containing scan results
        
    Returns:
        Tuple containing:
            - Success flag (bool)
            - Path to saved report (str or None if in-memory only)
            - The report content as bytes
    """
    try:
        # Create generator and generate report
        generator = ModernPDFReportGenerator()
        report_content = generator.generate_report(scan_result)
        
        # Return success and content
        return True, None, report_content
        
    except Exception as e:
        logger.exception(f"Error in generate_modern_pdf_report: {str(e)}")
        return False, None, None