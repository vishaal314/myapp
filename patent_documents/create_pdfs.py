#!/usr/bin/env python3
"""
Create proper PDF files for patent submission
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
import os

def create_application_pdf():
    """Create CORRECTED_Aanvraag_om_Octrooi.pdf"""
    
    # Read the text content
    with open('patent_documents/CORRECTED_Aanvraag_om_Octrooi.pdf', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create PDF
    pdf_path = 'patent_documents/CORRECTED_Aanvraag_om_Octrooi_REAL.pdf'
    doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                           topMargin=2*cm, bottomMargin=2*cm,
                           leftMargin=2*cm, rightMargin=2*cm)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=14,
        textColor='black',
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=TA_LEFT
    )
    
    # Build content
    story = []
    
    # Split content into lines and create paragraphs
    lines = content.split('\n')
    for line in lines:
        if line.strip():
            if line.strip().startswith('Aanvraag om octrooi'):
                story.append(Paragraph(line.strip(), title_style))
            else:
                # Replace multiple spaces with proper formatting
                story.append(Paragraph(line.strip(), normal_style))
        else:
            story.append(Spacer(1, 0.2*cm))
    
    # Build PDF
    doc.build(story)
    print(f"✅ Created: {pdf_path}")
    return pdf_path

def create_extract_pdf():
    """Create CORRECTED_Patent_Extract.pdf"""
    
    # Read the text content
    with open('patent_documents/CORRECTED_Patent_Extract.pdf', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create PDF
    pdf_path = 'patent_documents/CORRECTED_Patent_Extract_REAL.pdf'
    doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                           topMargin=2*cm, bottomMargin=2*cm,
                           leftMargin=2*cm, rightMargin=2*cm)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=14,
        textColor='black',
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor='black',
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY
    )
    
    # Build content
    story = []
    
    # Split content into paragraphs
    paragraphs = content.split('\n\n')
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
            
        if 'UITTREKSEL' in para or 'EXTRACT' in para:
            story.append(Paragraph(para, title_style))
        elif para.startswith('TITEL') or para.startswith('SAMENVATTING'):
            story.append(Paragraph(para, heading_style))
        elif 'AI Model Scanner' in para and len(para) < 50:
            story.append(Paragraph(para, heading_style))
        elif '=====' in para:
            story.append(Spacer(1, 0.5*cm))
        else:
            story.append(Paragraph(para, normal_style))
            story.append(Spacer(1, 0.3*cm))
    
    # Build PDF
    doc.build(story)
    print(f"✅ Created: {pdf_path}")
    
    # Word count verification
    text_only = content.replace('=====', '').replace('UITTREKSEL', '').replace('EXTRACT', '')
    text_only = text_only.replace('TITEL', '').replace('SAMENVATTING', '').replace('MAX 250 WOORDEN', '')
    words = text_only.split()
    word_count = len([w for w in words if w.strip() and not w.startswith('[')])
    print(f"   Word count: {word_count} words")
    
    return pdf_path

if __name__ == '__main__':
    print("Creating proper PDF files...")
    print()
    
    app_pdf = create_application_pdf()
    extract_pdf = create_extract_pdf()
    
    print()
    print("✅ PDF files created successfully!")
    print()
    print("Files created:")
    print(f"  1. {app_pdf}")
    print(f"  2. {extract_pdf}")
    print()
    print("Next: Verify PDFs open correctly, then rename by removing '_REAL' suffix")
