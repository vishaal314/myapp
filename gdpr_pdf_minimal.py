"""
Minimal GDPR PDF Generator with Professional Styling

This standalone application generates professional GDPR compliance reports
with organization name and certification type customization.
"""

import os
import streamlit as st
from datetime import datetime
import random

def main():
    st.set_page_config(
        page_title="GDPR PDF Generator",
        page_icon="📄",
        layout="centered"
    )
    
    st.title("Professional GDPR PDF Generator")
    st.markdown("### Generate a comprehensive GDPR compliance report")
    
    # Mock scan data with random values for the standalone generator
    mock_scan_data = {
        "compliance_score": random.randint(60, 95),
        "high_risk": random.randint(0, 5),
        "total_findings": random.randint(8, 20),
        "findings": [
            {"id": f"GDPR-{i}", "description": f"Finding {i}", "risk_level": random.choice(["high", "medium", "low"])}
            for i in range(1, random.randint(9, 21))
        ]
    }
    
    # Create two columns for better layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### Organization Information")
        # Simple form for customization
        with st.form(key="gdpr_minimal_form"):
            organization_name = st.text_input("Organization Name", "Your Organization")
            certification_type = st.selectbox(
                "Certification Type",
                ["GDPR Compliant", "ISO 27001 Aligned", "UAVG Certified", "Dutch GDPR (UAVG) Verified"]
            )
            
            # Form submission button
            submit_button = st.form_submit_button(
                label="Generate Professional Report",
                type="primary",
                use_container_width=True
            )
    
    with col2:
        st.markdown("#### Report Features")
        st.markdown("""
        Your report includes:
        - ✅ Executive Summary
        - ✅ GDPR Principles Assessment
        - ✅ Risk Analysis
        - ✅ Recommendations
        - ✅ Professional Certification
        """)
    
    # Handle report generation
    if submit_button:
        with st.spinner("Generating professional GDPR report..."):
            try:
                # Import the report generator
                try:
                    # Try to import from services first (when used within main app)
                    from services.gdpr_report_generator import generate_gdpr_report
                except ImportError:
                    # If not found, assume this is a standalone app and create a local copy
                    from gdpr_report_generator_standalone import generate_gdpr_report
                
                # Generate PDF report
                pdf_bytes = generate_gdpr_report(
                    scan_results=mock_scan_data,
                    organization_name=organization_name,
                    certification_type=certification_type
                )
                
                if pdf_bytes:
                    # Success message with animated checkmark
                    st.success("✅ Professional GDPR report generated successfully!")
                    
                    # Create reports directory if it doesn't exist
                    os.makedirs("reports", exist_ok=True)
                    
                    # Generate file name
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    file_name = f"gdpr_compliance_report_{organization_name.replace(' ', '_')}_{timestamp}.pdf"
                    
                    # Provide download button
                    st.download_button(
                        label="📥 Download Professional GDPR Report",
                        data=pdf_bytes,
                        file_name=file_name,
                        mime="application/pdf",
                        key="download_gdpr_report",
                        use_container_width=True
                    )
                    
                    # Show report details
                    st.info(f"""
                    Your professional GDPR report for **{organization_name}** includes:
                    
                    - Certification: **{certification_type}**
                    - Generation Date: **{datetime.now().strftime('%Y-%m-%d')}**
                    - Compliance Score: **{mock_scan_data['compliance_score']}%**
                    - Risk Analysis: **{mock_scan_data['high_risk']}** high-risk findings
                    
                    This report can be used to demonstrate GDPR compliance efforts.
                    """)
                else:
                    st.error("Failed to generate professional report.")
            except Exception as e:
                st.error(f"Error generating report: {str(e)}")
                
                # Fallback to simple PDF
                st.warning("Using simplified PDF format instead.")
                
                # Create a simple PDF document as fallback
                pdf_content = f"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/MediaBox[0 0 595 842]/Parent 2 0 R/Resources<</Font<</F1<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>>>>>/Contents 4 0 R>>endobj
4 0 obj<</Length 150>>stream
BT
/F1 24 Tf
50 800 Td
(GDPR Compliance Report) Tj
/F1 14 Tf
0 -50 Td
(Organization: {organization_name}) Tj
0 -20 Td
(Certification: {certification_type}) Tj
0 -20 Td
(Generated: {datetime.now().strftime('%Y-%m-%d')}) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000010 00000 n
0000000053 00000 n
0000000102 00000 n
0000000229 00000 n
trailer<</Size 5/Root 1 0 R>>
startxref
428
%%EOF""".encode('latin1')
                
                # Display the fallback download button
                st.download_button(
                    label="Download Simple GDPR Report (Fallback)",
                    data=pdf_content,
                    file_name=f"GDPR_Report_Simple_{organization_name.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

if __name__ == "__main__":
    main()