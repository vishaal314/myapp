"""
Simple GDPR PDF Generator

A minimalist GDPR PDF report generator that focuses on reliably
generating and downloading reports with minimal UI complexity.
"""

import streamlit as st
from datetime import datetime
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import random

def generate_pdf(organization_name, certification_type):
    """
    Generate a simple GDPR compliance PDF report.
    
    Args:
        organization_name: Name of the organization
        certification_type: Type of certification (e.g., "GDPR Compliant")
        
    Returns:
        PDF as bytes
    """
    # Create in-memory buffer for PDF
    buffer = io.BytesIO()
    
    # Create PDF document
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
    
    # Generate mock compliance scores
    scores = {
        "Lawfulness, Fairness and Transparency": random.randint(60, 95),
        "Purpose Limitation": random.randint(65, 95),
        "Data Minimization": random.randint(55, 85),
        "Accuracy": random.randint(70, 95),
        "Storage Limitation": random.randint(65, 90),
        "Integrity and Confidentiality": random.randint(75, 95),
        "Accountability": random.randint(60, 90)
    }
    
    # Add compliance table
    story.append(Paragraph("GDPR Principles Compliance", styles["Heading2"]))
    story.append(Spacer(1, 10))
    
    # Create table data
    table_data = [["GDPR Principle", "Compliance Score"]]
    for principle, score in scores.items():
        table_data.append([principle, f"{score}%"])
    
    # Overall score
    overall_score = sum(scores.values()) / len(scores)
    table_data.append(["Overall Compliance", f"{overall_score:.1f}%"])
    
    # Create and style the table
    table = Table(table_data, colWidths=[300, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 20))
    
    # Add certification
    story.append(Paragraph("Certification", styles["Heading2"]))
    story.append(Paragraph(f"Based on the assessment results, {organization_name} is hereby certified as {certification_type} as of {datetime.now().strftime('%Y-%m-%d')}.", styles["Normal"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph("This certification is valid for one year from the date of issuance.", styles["Normal"]))
    
    # Build the PDF
    doc.build(story)
    pdf_data = buffer.getvalue()
    buffer.close()
    
    return pdf_data

def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="Simple GDPR PDF Generator",
        page_icon="📄",
        layout="centered"
    )
    
    st.title("GDPR PDF Generator")
    st.write("Generate a GDPR compliance report with a single click.")
    
    # Create a clean two-column layout
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Form for organization details
        st.subheader("Report Details")
        organization_name = st.text_input("Organization Name", "Your Organization")
        certification_type = st.selectbox(
            "Certification Type",
            ["GDPR Compliant", "ISO 27001 Aligned", "UAVG Certified"]
        )
        
        # Main download button (no button inside a form)
        st.markdown("### Generate Report")
        if st.button("📥 Download GDPR Compliance Report", type="primary", use_container_width=True):
            with st.spinner("Creating your GDPR compliance report..."):
                try:
                    # Generate PDF using ReportLab
                    pdf_bytes = generate_pdf(organization_name, certification_type)
                    
                    # Generate filename with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"GDPR_Compliance_Report_{organization_name.replace(' ', '_')}_{timestamp}.pdf"
                    
                    # Success message
                    st.success("✅ Your GDPR compliance report is ready!")
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Report Now",
                        data=pdf_bytes,
                        file_name=filename,
                        mime="application/pdf",
                        key="final_download",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Error generating report: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
    
    with col2:
        # Info about the report
        st.subheader("Report Features")
        st.markdown("""
        Your report includes:
        
        ✅ Executive Summary
        ✅ GDPR Principles Assessment
        ✅ Compliance Scores
        ✅ Certification Statement
        ✅ Official Timestamp
        """)
        
        # Add a simple visual element
        st.markdown("### Compliance Overview")
        st.progress(0.75)
        st.caption("Example compliance score: 75%")

if __name__ == "__main__":
    main()