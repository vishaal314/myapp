"""
Ultra Simple GDPR PDF Generator

This is an extremely simplified version with just one purpose:
Generate and download a GDPR compliance PDF with minimal UI.
"""

import streamlit as st
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io
import random

def create_pdf(organization_name, certification_type):
    """Create a simple PDF report"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    title_style.alignment = 1  # Center
    
    # Add title
    story.append(Paragraph(f"GDPR Compliance Report", title_style))
    story.append(Spacer(1, 20))
    
    # Add organization info
    story.append(Paragraph(f"Organization: {organization_name}", styles["Heading2"]))
    story.append(Paragraph(f"Certification: {certification_type}", styles["Heading3"]))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d')}", styles["Normal"]))
    story.append(Spacer(1, 20))
    
    # Add certification
    story.append(Paragraph("Certification", styles["Heading2"]))
    story.append(Paragraph(
        f"Based on the assessment results, {organization_name} is hereby certified as "
        f"{certification_type} as of {datetime.now().strftime('%Y-%m-%d')}.", 
        styles["Normal"]
    ))
    
    # Build the PDF
    doc.build(story)
    return buffer.getvalue()

def main():
    st.set_page_config(page_title="Simple GDPR PDF", layout="centered")
    
    st.title("Simple GDPR PDF Generator")
    
    # Simple inputs
    organization_name = st.text_input("Organization Name", "Your Organization")
    certification_type = st.selectbox(
        "Certification Type",
        ["GDPR Compliant", "ISO 27001 Aligned", "UAVG Certified"]
    )
    
    # Generate button
    if st.button("Download GDPR PDF Report", type="primary", use_container_width=True):
        with st.spinner("Creating PDF..."):
            # Generate PDF
            pdf_bytes = create_pdf(organization_name, certification_type)
            
            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"GDPR_Report_{organization_name.replace(' ', '_')}_{timestamp}.pdf"
            
            # Show success
            st.success("✅ PDF report created!")
            
            # Download button
            st.download_button(
                label="📥 Download PDF Now",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                use_container_width=True
            )

if __name__ == "__main__":
    main()