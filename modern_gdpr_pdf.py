"""
Modern GDPR PDF Generator with logo and professional styling
"""

import io
import base64
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

def create_logo():
    """Create a simple logo as SVG"""
    logo_svg = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
    <svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 120 120">
      <circle cx="60" cy="60" r="55" fill="#1565C0" />
      <text x="60" y="80" font-size="80" text-anchor="middle" fill="white" font-family="Arial">🛡️</text>
    </svg>'''
    
    return logo_svg
    
def create_gdpr_pdf(organization_name="Your Organization", 
                  compliance_score=75, 
                  certification_type="GDPR Compliant",
                  high_risk=3,
                  total_findings=12):
    """
    Generate a professional GDPR compliance report as a PDF
    
    Returns:
        bytes: PDF file as bytes
    """
    buffer = io.BytesIO()
    
    # Create the PDF document using ReportLab
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1565C0'),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor('#1565C0'),
        spaceBefore=12
    )
    
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6
    )
    
    # Story is the list of flowables to add to the document
    story = []
    
    # Create an SVG logo
    from reportlab.graphics import renderPM
    from svglib.svglib import svg2rlg
    
    svg_data = create_logo()
    svg_file = io.BytesIO(svg_data.encode('utf-8'))
    drawing = svg2rlg(svg_file)
    
    # Convert drawing to PNG and add to story
    img_data = io.BytesIO()
    renderPM.drawToFile(drawing, img_data, fmt="PNG")
    img_data.seek(0)
    logo_img = Image(img_data, width=1.5*inch, height=1.5*inch)
    logo_img.hAlign = 'CENTER'
    story.append(logo_img)
    story.append(Spacer(1, 12))
    
    # Add the title
    story.append(Paragraph("GDPR Compliance Report", title_style))
    story.append(Spacer(1, 12))
    
    # Add organization name and date
    story.append(Paragraph(f"Organization: {organization_name}", subtitle_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", normal_style))
    story.append(Paragraph(f"Certification: {certification_type}", normal_style))
    story.append(Spacer(1, 24))
    
    # Add compliance summary section
    story.append(Paragraph("Compliance Summary", header_style))
    story.append(Spacer(1, 12))
    
    # Create a table for metrics
    data = [
        ["Metric", "Value", "Target"],
        ["Compliance Score", f"{compliance_score}%", "100%"],
        ["High Risk Findings", str(high_risk), "0"],
        ["Total Findings", str(total_findings), "Review All"]
    ]
    
    t = Table(data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565C0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(t)
    story.append(Spacer(1, 24))
    
    # Add findings section
    story.append(Paragraph("Key Findings", header_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("This report contains an assessment of GDPR compliance status. Key areas evaluated include data processing, security measures, and documentation of compliance procedures.", normal_style))
    
    # Add GDPR Principles section
    story.append(Spacer(1, 12))
    story.append(Paragraph("GDPR Principles Coverage", header_style))
    story.append(Spacer(1, 12))
    
    principles = [
        "Lawfulness, Fairness and Transparency",
        "Purpose Limitation",
        "Data Minimization",
        "Accuracy", 
        "Storage Limitation",
        "Integrity and Confidentiality",
        "Accountability"
    ]
    
    for principle in principles:
        story.append(Paragraph(f"✓ {principle}", normal_style))
    
    # Add recommendations section
    story.append(Spacer(1, 24))
    story.append(Paragraph("Recommendations", header_style))
    story.append(Spacer(1, 12))
    
    recommendations = [
        "Ensure all data processing activities are documented",
        "Implement regular privacy impact assessments",
        "Review data retention policies",
        "Strengthen access controls to personal data"
    ]
    
    for i, rec in enumerate(recommendations):
        story.append(Paragraph(f"{i+1}. {rec}", normal_style))
    
    # Add footer
    story.append(Spacer(1, 48))
    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.gray,
        alignment=TA_CENTER
    )
    story.append(Paragraph(f"DataGuardian Pro - GDPR Compliance Report © {datetime.now().year}", footer_style))
    
    # Build the PDF
    doc.build(story)
    
    # Get the PDF data from the buffer
    buffer.seek(0)
    return buffer.getvalue()