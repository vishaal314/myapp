"""
PCI DSS Report Template

This module provides templates and helper functions for generating PCI DSS-focused
security reports.
"""

import io
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional

# Import ReportLab components for PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.colors import HexColor

# Import PCI compliance utilities
from utils.pci_compliance import get_pci_requirement_description

# Set up logging
logger = logging.getLogger("pcidss_report_template")

def generate_pcidss_report(scan_data: Dict[str, Any]) -> bytes:
    """
    Generate a PCI DSS-focused security report in PDF format.
    
    Args:
        scan_data: Dictionary containing scan results
        
    Returns:
        PDF report as bytes
    """
    # Create a new PDF buffer
    buffer = io.BytesIO()
    
    # Extract data from scan results
    repository = scan_data.get('repository', 'Unknown')
    branch = scan_data.get('branch', 'main')
    timestamp = scan_data.get('timestamp', datetime.now().isoformat())
    findings = scan_data.get('findings', [])
    high_risk_count = scan_data.get('high_risk_count', 0)
    medium_risk_count = scan_data.get('medium_risk_count', 0)
    low_risk_count = scan_data.get('low_risk_count', 0)
    total_findings = scan_data.get('total_pii_found', len(findings))
    compliance_score = scan_data.get('compliance_score', 0)
    recommendations = scan_data.get('recommendations', [])
    
    # Format timestamp
    try:
        formatted_timestamp = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    except:
        formatted_timestamp = timestamp
    
    # Set up the document
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Create styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    title_style.textColor = HexColor('#1e3a8a')
    
    heading_style = styles['Heading1']
    heading_style.textColor = HexColor('#1e3a8a')
    heading_style.fontSize = 14
    
    subheading_style = styles['Heading2']
    subheading_style.textColor = HexColor('#1e3a8a')
    subheading_style.fontSize = 12
    
    normal_style = styles['Normal']
    
    # Create a table style for findings tables
    findings_table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ])
    
    # Custom paragraph styles
    centered_style = ParagraphStyle(
        'centered',
        parent=normal_style,
        alignment=TA_CENTER
    )
    
    subtitle_style = ParagraphStyle(
        'subtitle',
        parent=normal_style,
        fontSize=12,
        textColor=HexColor('#4b5563'),
        spaceAfter=0.1*inch
    )
    
    section_title_style = ParagraphStyle(
        'section_title',
        parent=heading_style,
        fontSize=13,
        textColor=HexColor('#1e3a8a'),
        spaceBefore=0.2*inch,
        spaceAfter=0.1*inch
    )
    
    risk_high_style = ParagraphStyle(
        'risk_high',
        parent=normal_style,
        textColor=colors.red,
        fontName='Helvetica-Bold'
    )
    
    risk_medium_style = ParagraphStyle(
        'risk_medium',
        parent=normal_style,
        textColor=colors.orange,
        fontName='Helvetica-Bold'
    )
    
    risk_low_style = ParagraphStyle(
        'risk_low',
        parent=normal_style,
        textColor=colors.green,
        fontName='Helvetica-Bold'
    )
    
    # Building the PDF
    elements = []
    
    # Title
    elements.append(Paragraph("PCI DSS Security Assessment Report", title_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Subtitle with timestamp
    elements.append(Paragraph(f"Generated on {formatted_timestamp}", subtitle_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Repository information
    elements.append(Paragraph("Repository Information", section_title_style))
    
    repo_data = [
        ["Repository", repository],
        ["Branch", branch],
        ["Scan Date", formatted_timestamp]
    ]
    
    repo_table = Table(repo_data, colWidths=[2*inch, 4*inch])
    repo_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#f9fafb')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(repo_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Executive Summary
    elements.append(Paragraph("Executive Summary", section_title_style))
    
    summary_text = f"""
    This report presents the results of a PCI DSS-focused security assessment of the codebase. 
    The assessment was performed to identify security issues relevant to PCI DSS requirements,
    particularly focusing on requirements in sections 3, 4, and 6 that address secure coding,
    encryption, and vulnerability management.
    
    The scan identified a total of {total_findings} findings:
    • {high_risk_count} High Risk Issues
    • {medium_risk_count} Medium Risk Issues
    • {low_risk_count} Low Risk Issues
    
    The overall PCI DSS compliance score is {compliance_score}/100.
    """
    
    elements.append(Paragraph(summary_text, normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Findings Summary
    elements.append(Paragraph("Findings Summary", section_title_style))
    
    # Create a summary table
    summary_data = [
        ["Risk Level", "Count", "Description"],
        ["High", str(high_risk_count), "Critical security issues that must be addressed immediately"],
        ["Medium", str(medium_risk_count), "Important security issues that should be addressed soon"],
        ["Low", str(low_risk_count), "Minor security issues that should be addressed when possible"]
    ]
    
    summary_table = Table(summary_data, colWidths=[1.2*inch, 0.8*inch, 4.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 1), (0, 1), HexColor('#fee2e2')),
        ('BACKGROUND', (0, 2), (0, 2), HexColor('#ffedd5')),
        ('BACKGROUND', (0, 3), (0, 3), HexColor('#dcfce7')),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # PCI DSS Requirement Coverage
    elements.append(Paragraph("PCI DSS Requirement Coverage", section_title_style))
    
    # Get unique PCI requirements from findings
    pci_requirements = set()
    for finding in findings:
        req = finding.get('pci_requirement', '')
        if req:
            for r in req.split(','):
                pci_requirements.add(r.strip())
    
    # Create a table of PCI requirements covered
    if pci_requirements:
        pci_req_data = [["Requirement", "Description"]]
        
        for req in sorted(pci_requirements):
            desc = get_pci_requirement_description(req)
            pci_req_data.append([req, desc])
        
        pci_req_table = Table(pci_req_data, colWidths=[1*inch, 5.5*inch])
        pci_req_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(pci_req_table)
    else:
        elements.append(Paragraph("No specific PCI DSS requirements were identified in the findings.", normal_style))
    
    elements.append(Spacer(1, 0.2*inch))
    
    # Add a page break before detailed findings
    elements.append(PageBreak())
    
    # Detailed Findings
    elements.append(Paragraph("Detailed Findings", section_title_style))
    
    # Group findings by risk level
    high_risk_findings = [f for f in findings if f.get('risk_level', '').lower() == 'high']
    medium_risk_findings = [f for f in findings if f.get('risk_level', '').lower() == 'medium']
    low_risk_findings = [f for f in findings if f.get('risk_level', '').lower() == 'low']
    
    # Function to create a findings table
    def create_findings_table(findings_list, risk_level):
        if not findings_list:
            elements.append(Paragraph(f"No {risk_level} Risk findings identified.", normal_style))
            elements.append(Spacer(1, 0.1*inch))
            return
        
        elements.append(Paragraph(f"{risk_level} Risk Findings ({len(findings_list)})", subheading_style))
        
        # Create table headers
        table_data = [["Finding Type", "Location", "PCI Requirement", "Remediation"]]
        
        # Add findings to table
        for finding in findings_list:
            finding_type = finding.get('type', 'Unknown')
            location = finding.get('location', 'Unknown')
            pci_req = finding.get('pci_requirement', 'Unknown')
            remediation = finding.get('remediation', 'No specific remediation provided')
            
            table_data.append([
                finding_type,
                location,
                pci_req,
                remediation
            ])
        
        # Create table
        findings_table = Table(table_data, colWidths=[1.5*inch, 1.5*inch, 1*inch, 2.5*inch])
        findings_table.setStyle(findings_table_style)
        
        elements.append(findings_table)
        elements.append(Spacer(1, 0.2*inch))
    
    # Add findings tables by risk level
    if high_risk_findings:
        create_findings_table(high_risk_findings, "High")
    
    if medium_risk_findings:
        create_findings_table(medium_risk_findings, "Medium")
    
    if low_risk_findings:
        create_findings_table(low_risk_findings, "Low")
    
    # Add a page break before recommendations
    elements.append(PageBreak())
    
    # Recommendations Section
    elements.append(Paragraph("Recommendations", section_title_style))
    
    if recommendations:
        rec_data = [["Category", "Description", "Severity"]]
        
        for rec in recommendations:
            category = rec.get('category', 'General')
            description = rec.get('description', 'No description available')
            severity = rec.get('severity', 'Medium')
            
            rec_data.append([category, description, severity])
        
        rec_table = Table(rec_data, colWidths=[1.5*inch, 4*inch, 1*inch])
        rec_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(rec_table)
    else:
        elements.append(Paragraph("No specific recommendations available.", normal_style))
    
    elements.append(Spacer(1, 0.2*inch))
    
    # Best Practices Section
    elements.append(Paragraph("Best Practices for PCI DSS Compliance", section_title_style))
    
    best_practices_text = """
    1. <b>Implement Strong Access Controls</b>:
       • Apply the principle of least privilege
       • Use multi-factor authentication for all access to cardholder data
       • Regularly review and update access permissions
    
    2. <b>Secure Code Development</b>:
       • Follow secure coding standards (OWASP)
       • Conduct regular code reviews
       • Implement static and dynamic application security testing
    
    3. <b>Protect Stored Data</b>:
       • Encrypt sensitive data using strong cryptography
       • Implement secure key management procedures
       • Minimize storage of sensitive data
    
    4. <b>Network Security</b>:
       • Maintain a firewall to protect cardholder data
       • Use encrypted protocols for data transmission
       • Implement network segmentation
    
    5. <b>Regular Testing and Monitoring</b>:
       • Conduct regular vulnerability scans
       • Perform penetration testing at least annually
       • Maintain and monitor audit logs
    """
    
    elements.append(Paragraph(best_practices_text, normal_style))
    
    # Build the PDF
    doc.build(elements)
    
    # Get the PDF content
    buffer.seek(0)
    return buffer.getvalue()