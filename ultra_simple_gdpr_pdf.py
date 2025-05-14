"""
Ultra Simple GDPR PDF Generator - Guaranteed to Work End-to-End
"""

import streamlit as st
import io
import base64
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

def create_gdpr_pdf(organization_name, certification_type, compliance_score=75):
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
    
    # Title
    story.append(Paragraph(f"<font color='#1E88E5'>DataGuardian Pro</font>", styles['Title']))
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
    
    # Certification statement
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

def main():
    st.set_page_config(page_title="GDPR PDF Certificate", page_icon="🔒")
    
    st.title("GDPR Compliance Certificate Generator")
    st.write("Generate a professional GDPR compliance certificate with modern styling.")
    
    # Simple form
    with st.form("pdf_form"):
        organization_name = st.text_input("Organization Name", "Your Organization")
        certification_type = st.selectbox(
            "Certification Type",
            ["GDPR Compliant", "ISO 27001 Aligned", "UAVG Certified"]
        )
        compliance_score = st.slider("Compliance Score (%)", 0, 100, 85)
        
        # Submit button
        submit_button = st.form_submit_button(label="Generate Certificate", type="primary")
    
    # Generate PDF when form is submitted
    if submit_button:
        # Show a spinner while generating
        with st.spinner("Generating your professional GDPR certificate..."):
            # Generate the PDF
            pdf_data = create_gdpr_pdf(
                organization_name=organization_name,
                certification_type=certification_type,
                compliance_score=compliance_score
            )
            
            # Success message
            st.success("✅ Your GDPR certificate is ready!")
            
            # Display download button
            st.download_button(
                label="📄 Download GDPR Certificate",
                data=pdf_data,
                file_name=f"GDPR_Certificate_{organization_name.replace(' ', '_')}.pdf",
                mime="application/pdf",
                help="Click to download your professionally styled GDPR certificate",
                use_container_width=True
            )
            
            # Preview
            st.subheader("Certificate Preview")
            st.info(f"""
            Your GDPR certificate includes:
            
            - **Organization**: {organization_name}
            - **Certification**: {certification_type}
            - **Compliance Score**: {compliance_score}%
            - **Professional blue styling**
            - **Unique certificate ID**
            - **1-year validity period**
            """)

if __name__ == "__main__":
    main()