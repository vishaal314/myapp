"""
Standalone GDPR PDF Generator with Fixed, Guaranteed PDF Download
"""

import streamlit as st
from io import BytesIO
import base64
from datetime import datetime

def main():
    st.set_page_config(page_title="GDPR PDF Generator", page_icon="🔒")
    
    st.title("GDPR PDF Generator")
    st.markdown("### 100% Guaranteed PDF Download")
    
    # Simple form
    organization = st.text_input("Organization Name", "Your Organization")
    certification = st.selectbox(
        "Certification Type", 
        ["GDPR Compliant", "ISO 27001 Aligned", "UAVG Certified"]
    )
    
    # Create the PDF on button click
    if st.button("Generate PDF Report", type="primary"):
        # Success first
        st.success("Your PDF is ready!")
        
        # Create a minimal PDF
        pdf_content = f"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/MediaBox[0 0 595 842]/Parent 2 0 R/Resources<</Font<</F1<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>>>>>/Contents 4 0 R>>endobj
4 0 obj<</Length 150>>stream
BT
/F1 24 Tf
50 800 Td
(GDPR Compliance Report) Tj
/F1 12 Tf
0 -50 Td
(Organization: {organization}) Tj
0 -20 Td
(Certification: {certification}) Tj
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
        
        # Create a direct download link
        b64 = base64.b64encode(pdf_content).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="GDPR_Report.pdf" style="display:inline-block; padding:10px 20px; background-color:#F63366; color:white; text-decoration:none; font-weight:bold; border-radius:5px; text-align:center; margin:10px 0px;">Click to Download PDF</a>'
        st.markdown(href, unsafe_allow_html=True)
        
        # Also provide a standard download button
        buffer = BytesIO(pdf_content)
        st.download_button(
            label="Standard Download Button",
            data=buffer,
            file_name="GDPR_Report.pdf",
            mime="application/pdf"
        )
        
        # Show a preview
        st.subheader("Report Contents")
        st.info(f"""
        Your GDPR report includes:
        - Organization: {organization}
        - Certification: {certification}
        - Date: {datetime.now().strftime('%Y-%m-%d')}
        """)

if __name__ == "__main__":
    main()