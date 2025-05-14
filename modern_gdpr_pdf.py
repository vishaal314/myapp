"""
Modern GDPR PDF Generator with logo and professional styling
"""

import io
import base64
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

def create_logo():
    """Create a simple logo as SVG"""
    svg_logo = """<svg width="200" height="60" xmlns="http://www.w3.org/2000/svg">
        <rect width="200" height="60" fill="#1E88E5" rx="10" ry="10"/>
        <text x="15" y="40" font-family="Arial" font-size="22" fill="white" font-weight="bold">DataGuardian Pro</text>
        <circle cx="180" cy="30" r="15" fill="white"/>
        <path d="M180 20 L180 40 M170 30 L190 30" stroke="#1E88E5" stroke-width="4"/>
    </svg>"""
    
    # Use a data URI
    return f"data:image/svg+xml;base64,{base64.b64encode(svg_logo.encode()).decode()}"

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
    
    # Set up the document with A4 page size
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2*cm,
        rightMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
        title=f"GDPR Compliance Report - {organization_name}"
    )
    
    # Styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='Title',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1E88E5'),
        spaceAfter=12
    ))
    styles.add(ParagraphStyle(
        name='Subtitle',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.HexColor('#1976D2'),
        spaceBefore=12,
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name='Section',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor('#1976D2'),
        spaceBefore=10,
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name='NormalBlue',
        parent=styles['Normal'],
        textColor=colors.HexColor('#0D47A1'),
        spaceBefore=6
    ))
    
    # Create content
    story = []
    
    # Logo
    logo_data = create_logo()
    
    # Header with logo
    header_data = [
        [Paragraph(f'<img src="{logo_data}" width="200" height="60"/>', styles['Normal']),
         Paragraph(f'<b>Date:</b> {datetime.now().strftime("%Y-%m-%d")}', styles['Normal'])],
    ]
    header = Table(header_data, colWidths=[doc.width/2, doc.width/2])
    header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(header)
    story.append(Spacer(1, 20))
    
    # Title
    story.append(Paragraph(f"GDPR Compliance Certificate", styles['Title']))
    story.append(Spacer(1, 10))
    
    # Organization info
    story.append(Paragraph(f"Organization: <b>{organization_name}</b>", styles['NormalBlue']))
    story.append(Paragraph(f"Certification Type: <b>{certification_type}</b>", styles['NormalBlue']))
    story.append(Paragraph(f"Issue Date: <b>{datetime.now().strftime('%Y-%m-%d')}</b>", styles['NormalBlue']))
    story.append(Spacer(1, 20))
    
    # Summary
    story.append(Paragraph("Compliance Summary", styles['Subtitle']))
    summary_data = [
        ["Compliance Score", f"{compliance_score}%"],
        ["Risk Level", "Medium" if 60 <= compliance_score < 80 else "Low" if compliance_score >= 80 else "High"],
        ["High Risk Findings", str(high_risk)],
        ["Total Findings", str(total_findings)],
    ]
    summary_table = Table(summary_data, colWidths=[doc.width/2, doc.width/2])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E3F2FD')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#0D47A1')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BBDEFB')),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 15))
    
    # GDPR Principles Assessment
    story.append(Paragraph("GDPR Principles Assessment", styles['Subtitle']))
    
    principles = [
        ("Lawfulness, Fairness and Transparency", 
         "Personal data shall be processed lawfully, fairly and in a transparent manner in relation to the individual.", 
         "High" if compliance_score < 60 else "Medium" if compliance_score < 80 else "Low"),
        
        ("Purpose Limitation", 
         "Personal data shall be collected for specified, explicit and legitimate purposes.", 
         "Medium" if compliance_score < 70 else "Low"),
        
        ("Data Minimization", 
         "Personal data shall be adequate, relevant and limited to what is necessary.", 
         "Medium" if compliance_score < 75 else "Low"),
        
        ("Accuracy", 
         "Personal data shall be accurate and, where necessary, kept up to date.", 
         "Low"),
        
        ("Storage Limitation", 
         "Personal data shall be kept in a form which permits identification of data subjects for no longer than is necessary.", 
         "Medium" if high_risk > 2 else "Low"),
        
        ("Integrity and Confidentiality", 
         "Personal data shall be processed in a manner that ensures appropriate security.", 
         "High" if high_risk > 5 else "Medium" if high_risk > 2 else "Low"),
        
        ("Accountability", 
         "The controller shall be responsible for, and be able to demonstrate compliance with the GDPR principles.", 
         "Medium" if compliance_score < 80 else "Low"),
    ]
    
    for principle, description, risk in principles:
        story.append(Paragraph(f"{principle}", styles['Section']))
        story.append(Paragraph(f"{description}", styles['Normal']))
        
        # Risk level with color
        color = "#4CAF50" if risk == "Low" else "#FF9800" if risk == "Medium" else "#F44336"
        story.append(Paragraph(f"Risk Level: <font color='{color}'><b>{risk}</b></font>", styles['Normal']))
        
        story.append(Spacer(1, 5))
    
    # Certification statement
    story.append(Spacer(1, 10))
    story.append(Paragraph("Certification Statement", styles['Subtitle']))
    story.append(Paragraph(
        f"This document certifies that {organization_name} has undergone a GDPR compliance "
        f"assessment and has been found to be {certification_type}. The assessment was conducted "
        f"using the DataGuardian Pro platform on {datetime.now().strftime('%Y-%m-%d')}.",
        styles['Normal']
    ))
    
    story.append(Spacer(1, 20))
    
    # Verification signature
    story.append(Paragraph("Verification", styles['Section']))
    verification_data = [
        ["Certified By:", "DataGuardian Pro Verification System"],
        ["Certificate ID:", f"GDPR-{datetime.now().strftime('%Y%m%d')}-{hash(organization_name) % 10000:04d}"],
        ["Valid Until:", f"{(datetime.now().replace(year=datetime.now().year + 1)).strftime('%Y-%m-%d')}"]
    ]
    verification_table = Table(verification_data, colWidths=[doc.width/3, 2*doc.width/3])
    verification_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BBDEFB')),
    ]))
    story.append(verification_table)
    
    # Footer
    story.append(Spacer(1, 30))
    story.append(Paragraph(
        "<i>This report is generated automatically by the DataGuardian Pro platform "
        "and represents an assessment of GDPR compliance at the time of scanning. "
        "Regular reassessment is recommended as part of ongoing compliance efforts.</i>",
        styles['Normal']
    ))
    
    # Build document
    doc.build(story)
    
    # Get PDF data
    pdf_data = buffer.getvalue()
    buffer.close()
    
    return pdf_data