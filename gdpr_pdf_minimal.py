"""
Minimal GDPR PDF Generator with Organization and Certification Info
"""

import streamlit as st
from datetime import datetime

def main():
    st.title("Minimal GDPR PDF Generator")
    st.markdown("### Generate a simple GDPR compliance report")
    
    # Simple form for basic customization
    organization_name = st.text_input("Organization Name", "Your Organization")
    certification_type = st.selectbox(
        "Certification Type",
        ["GDPR Compliant", "ISO 27001 Aligned", "UAVG Certified"]
    )
    
    # Generate button
    if st.button("Generate GDPR Report", type="primary"):
        # Create a simple PDF with organization information
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
        
        # Success message
        st.success("Your GDPR report is ready!")
        
        # Download button
        st.download_button(
            label="Download GDPR Report",
            data=pdf_content,
            file_name=f"GDPR_Report_{organization_name.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
        # Report info
        st.info(f"""
        Your GDPR report includes:
        
        - Organization: {organization_name}
        - Certification: {certification_type}
        - Generation Date: {datetime.now().strftime('%Y-%m-%d')}
        """)

if __name__ == "__main__":
    main()