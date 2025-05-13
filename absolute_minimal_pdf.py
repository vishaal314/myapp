"""
Ultra Minimal Modern PDF Generator 
"""

import io
import base64
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_modern_pdf(organization="Your Organization", certification="GDPR Compliant"):
    """Generate a clean, minimal PDF that's guaranteed to work"""
    buffer = io.BytesIO()
    
    # Create a PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create elements to add to the document
    elements = []
    
    # Add title
    title = Paragraph(f"<font color='#1565C0' size='16'><b>GDPR Compliance Report</b></font>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Add organization info
    elements.append(Paragraph(f"<b>Organization:</b> {organization}", styles['Normal']))
    elements.append(Paragraph(f"<b>Certification:</b> {certification}", styles['Normal']))
    elements.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d')}", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Add summary
    elements.append(Paragraph("<font color='#1565C0'><b>Compliance Summary</b></font>", styles['Heading2']))
    elements.append(Paragraph("This report provides an overview of GDPR compliance status for your organization.", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Add principles
    elements.append(Paragraph("<font color='#1565C0'><b>GDPR Principles Covered:</b></font>", styles['Heading2']))
    principles = [
        "1. Lawfulness, Fairness and Transparency",
        "2. Purpose Limitation",
        "3. Data Minimization",
        "4. Accuracy",
        "5. Storage Limitation",
        "6. Integrity and Confidentiality",
        "7. Accountability"
    ]
    
    for principle in principles:
        elements.append(Paragraph(f"✓ {principle}", styles['Normal']))
    
    # Build the PDF
    doc.build(elements)
    
    # Get the value from the buffer
    buffer.seek(0)
    return buffer.getvalue()