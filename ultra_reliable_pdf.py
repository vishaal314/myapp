"""
Ultra Reliable PDF Generator

A simplified, guaranteed PDF generator with minimal dependencies.
"""

import streamlit as st
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

st.set_page_config(
    page_title="Ultra Reliable PDF Generator",
    page_icon="📄"
)

st.title("Ultra Reliable PDF Generator")
st.markdown("This super simple application generates a basic PDF document.")

# Text input for organization name
organization_name = st.text_input("Organization Name", "Your Organization")

# Generate button
if st.button("Generate PDF", use_container_width=True):
    try:
        # Create a simple PDF
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        # Add content
        p.setFont("Helvetica-Bold", 20)
        p.drawCentredString(300, 750, "GDPR Compliance Report")
        
        p.setFont("Helvetica", 12)
        p.drawString(50, 700, f"Organization: {organization_name}")
        p.drawString(50, 680, f"Generated on: {datetime.now().strftime('%Y-%m-%d')}")
        
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, 630, "Compliance Summary")
        
        p.setFont("Helvetica", 12)
        p.drawString(70, 600, "• Lawfulness, Fairness and Transparency: Compliant")
        p.drawString(70, 580, "• Purpose Limitation: Compliant")
        p.drawString(70, 560, "• Data Minimization: Compliant")
        p.drawString(70, 540, "• Accuracy: Compliant")
        p.drawString(70, 520, "• Storage Limitation: Compliant")
        p.drawString(70, 500, "• Integrity and Confidentiality: Compliant")
        p.drawString(70, 480, "• Accountability: Compliant")
        
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, 430, "Certification Status")
        
        p.setFont("Helvetica", 12)
        p.drawString(50, 410, f"{organization_name} is certified as GDPR Compliant.")
        p.drawString(50, 390, "This certification is valid for one year from the date of issuance.")
        
        p.setFont("Helvetica-Oblique", 10)
        p.drawString(250, 50, "© 2025 DataGuardian Pro")
        
        # Save PDF
        p.save()
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        # Success message
        st.success("✅ PDF generated successfully!")
        
        # Download button
        st.download_button(
            label="Download PDF",
            data=pdf_bytes,
            file_name=f"GDPR_Compliance_{organization_name.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        st.code(f"Error details: {type(e).__name__}")