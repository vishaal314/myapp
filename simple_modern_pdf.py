"""
Simple modern PDF generator that's guaranteed to work
"""

import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER

def create_modern_pdf(organization_name="Your Organization", 
                     compliance_score=75, 
                     certification_type="GDPR Compliant",
                     high_risk=3,
                     total_findings=12):
    """Generate a simple but professional GDPR report PDF"""
    
    buffer = io.BytesIO()
    
    # Create the PDF document
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