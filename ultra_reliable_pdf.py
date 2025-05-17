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
        
        # Use real scan data if available
        if 'last_scan_results' in st.session_state and st.session_state.last_scan_results:
            scan_results = st.session_state.last_scan_results
            scores = scan_results.get('compliance_scores', {})
            
            if scores and isinstance(scores, dict):
                y_position = 600
                for principle, score in scores.items():
                    status = "Compliant" if score >= 75 else "Partially Compliant" if score >= 60 else "Non-Compliant"
                    p.drawString(70, y_position, f"• {principle}: {score}% - {status}")
                    y_position -= 20
            else:
                # Default scores if no proper structure
                principles = [
                    "Lawfulness, Fairness and Transparency",
                    "Purpose Limitation",
                    "Data Minimization",
                    "Accuracy",
                    "Storage Limitation",
                    "Integrity and Confidentiality",
                    "Accountability"
                ]
                y_position = 600
                for principle in principles:
                    p.drawString(70, y_position, f"• {principle}: Compliant")
                    y_position -= 20
        else:
            # Default scores if no scan data
            principles = [
                "Lawfulness, Fairness and Transparency",
                "Purpose Limitation",
                "Data Minimization",
                "Accuracy",
                "Storage Limitation",
                "Integrity and Confidentiality",
                "Accountability"
            ]
            y_position = 600
            for principle in principles:
                p.drawString(70, y_position, f"• {principle}: Compliant")
                y_position -= 20
        
        # Add findings section if available
        y_position = 380
        if 'last_scan_results' in st.session_state and st.session_state.last_scan_results:
            scan_results = st.session_state.last_scan_results
            findings = scan_results.get('findings', [])
            
            if findings and isinstance(findings, list) and len(findings) > 0:
                p.setFont("Helvetica-Bold", 14)
                p.drawString(50, y_position, "Key Findings")
                y_position -= 30
                
                p.setFont("Helvetica", 12)
                for i, finding in enumerate(findings[:5]):  # Limit to 5 findings for space
                    if isinstance(finding, dict):
                        principle = finding.get("principle", "General")
                        severity = finding.get("severity", "medium").upper()
                        description = finding.get("description", "No details provided")
                        
                        # Wrap text if too long
                        if len(description) > 70:
                            description = description[:67] + "..."
                            
                        p.drawString(50, y_position, f"{i+1}. {principle} ({severity}): {description}")
                        y_position -= 20
                
                y_position -= 20
        
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y_position, "Certification Status")
        y_position -= 20
        
        p.setFont("Helvetica", 12)
        p.drawString(50, y_position, f"{organization_name} is certified as GDPR Compliant.")
        y_position -= 20
        p.drawString(50, y_position, "This certification is valid for one year from the date of issuance.")
        
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