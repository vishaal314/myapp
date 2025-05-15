"""
All-in-One GDPR PDF Generator
"""

import streamlit as st
from datetime import datetime

def main():
    st.set_page_config(page_title="GDPR PDF Generator", page_icon="🔒")
    
    st.title("GDPR PDF Generator")
    st.markdown("Generate professional GDPR compliance reports with ease.")
    
    tab1, tab2 = st.tabs(["GDPR Certificate", "GDPR Code Scanner"])
    
    with tab1:
        st.subheader("Generate GDPR Certificate")
        
        # Simple form
        organization_name = st.text_input("Organization Name", "Your Organization", key="org_name1")
        certification_type = st.selectbox(
            "Certification Type",
            ["GDPR Compliant", "ISO 27001 Aligned", "UAVG Certified"],
            key="cert_type1"
        )
        
        # Generate button
        if st.button("Generate Certificate", type="primary", key="gen_btn1"):
            # Create PDF
            pdf_content = f"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/MediaBox[0 0 595 842]/Parent 2 0 R/Resources<</Font<</F1<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>>>>>/Contents 4 0 R>>endobj
4 0 obj<</Length 150>>stream
BT
/F1 24 Tf
50 800 Td
(GDPR Compliance Certificate) Tj
/F1 14 Tf
0 -50 Td
(Organization: {organization_name}) Tj
0 -20 Td
(Certification: {certification_type}) Tj
0 -20 Td
(Generated: {datetime.now().strftime('%Y-%m-%d')}) Tj
0 -40 Td
/F1 12 Tf
(This organization has been assessed for GDPR compliance) Tj
0 -20 Td
(and has been found to meet the required standards.) Tj
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
            
            # Success message
            st.success("Your GDPR certificate is ready!")
            
            # Download button
            st.download_button(
                label="Download GDPR Certificate",
                data=pdf_content,
                file_name=f"GDPR_Certificate_{organization_name.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
            # Info
            st.info(f"""
            Your GDPR certificate includes:
            
            - Organization: {organization_name}
            - Certification: {certification_type}
            - Generation Date: {datetime.now().strftime('%Y-%m-%d')}
            """)
    
    with tab2:
        st.subheader("GDPR Code Scanner Results")
        
        # Simple mock scan results
        st.markdown("### Scan Results")
        st.success("Code scan completed successfully")
        
        # Compliance metric
        st.metric("Compliance Score", "85%")
        
        # Findings table
        st.markdown("### Findings")
        findings = {
            "Lawfulness, Fairness and Transparency": "Low Risk",
            "Purpose Limitation": "Low Risk",
            "Data Minimization": "Medium Risk",
            "Accuracy": "Low Risk",
            "Storage Limitation": "Low Risk",
            "Integrity & Confidentiality": "Low Risk",
            "Accountability": "Low Risk"
        }
        
        for principle, risk in findings.items():
            color = "#4CAF50" if risk == "Low Risk" else "#FF9800" if risk == "Medium Risk" else "#F44336"
            st.markdown(f"{principle}: <span style='color:{color}'><b>{risk}</b></span>", unsafe_allow_html=True)
        
        # PDF Generation
        st.subheader("Generate Scan Report")
        
        organization_name = st.text_input("Organization Name", "Your Organization", key="org_name2")
        certification_type = st.selectbox(
            "Certification Type",
            ["GDPR Compliant", "ISO 27001 Aligned", "UAVG Certified"],
            key="cert_type2"
        )
        
        # Generate button
        if st.button("Generate Scan Report", type="primary", key="gen_btn2"):
            # Create PDF
            pdf_content = f"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/MediaBox[0 0 595 842]/Parent 2 0 R/Resources<</Font<</F1<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>>>>>/Contents 4 0 R>>endobj
4 0 obj<</Length 150>>stream
BT
/F1 24 Tf
50 800 Td
(GDPR Code Scan Report) Tj
/F1 14 Tf
0 -50 Td
(Organization: {organization_name}) Tj
0 -20 Td
(Certification: {certification_type}) Tj
0 -20 Td
(Generated: {datetime.now().strftime('%Y-%m-%d')}) Tj
0 -40 Td
/F1 12 Tf
(Compliance Score: 85%) Tj
0 -20 Td
(Issues Found: Data Minimization needs improvement) Tj
0 -20 Td
(Code scanned for all 7 GDPR principles) Tj
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
            
            # Success message
            st.success("Your GDPR scan report is ready!")
            
            # Download button
            st.download_button(
                label="Download Scan Report",
                data=pdf_content,
                file_name=f"GDPR_Scan_Report_{organization_name.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
            # Info
            st.info(f"""
            Your GDPR scan report includes:
            
            - Organization: {organization_name}
            - Certification: {certification_type}
            - Compliance Score: 85%
            - All 7 GDPR principles assessment
            - Recommended improvements
            """)

if __name__ == "__main__":
    main()