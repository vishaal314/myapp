"""
Simple GDPR PDF Generator with Modern Styling
"""

import streamlit as st
from simple_modern_pdf import create_gdpr_pdf

def main():
    st.set_page_config(page_title="Professional GDPR PDF Generator", 
                     page_icon="🔒",
                     layout="centered")
    
    st.title("Professional GDPR PDF Generator")
    st.markdown("### Generate a professionally styled GDPR compliance report")
    
    # Form inputs
    col1, col2 = st.columns(2)
    
    with col1:
        organization_name = st.text_input("Organization Name", "Acme Corporation")
        certification_type = st.selectbox(
            "Certification Type", 
            ["GDPR Compliant", "ISO 27001 Aligned", "UAVG Certified"]
        )
    
    with col2:
        compliance_score = st.slider("Compliance Score (%)", 0, 100, 80)
        high_risk = st.number_input("High Risk Findings", 0, 20, 2)
        total_findings = st.number_input("Total Findings", 0, 50, 8)
    
    # Generate button
    if st.button("Generate Professional PDF", type="primary"):
        with st.spinner("Generating your professional GDPR report..."):
            # Generate PDF
            pdf_data = create_gdpr_pdf(
                organization_name=organization_name,
                certification_type=certification_type,
                compliance_score=compliance_score,
                high_risk=high_risk,
                total_findings=total_findings
            )
            
            # Success message
            st.success("✓ Your professional GDPR report is ready!")
            
            # Download button
            st.download_button(
                label="Download Professional GDPR Report",
                data=pdf_data,
                file_name=f"GDPR_Report_{organization_name.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
            # Preview
            with st.expander("What's included in your report"):
                st.markdown(f"""
                ### Report Details
                
                - **Organization**: {organization_name}
                - **Certification**: {certification_type}
                - **Compliance Score**: {compliance_score}%
                - **All 7 GDPR principles** with detailed assessment
                - **Risk analysis** for each compliance area
                - **Verification details** with unique certificate ID
                - **Professional blue styling** with modern design
                """)
                
                st.info("The PDF contains a professional assessment of GDPR compliance with all seven core principles evaluated in detail.")
    
    # Footer
    st.markdown("---")
    st.caption("DataGuardian Pro - Advanced Enterprise Privacy Compliance Platform")

if __name__ == "__main__":
    main()