"""
Simple GDPR PDF Generator

This is a completely standalone, simplified PDF generator for GDPR reports.
"""

import streamlit as st
import time
from datetime import datetime
from io import BytesIO

def main():
    st.set_page_config(page_title="GDPR PDF Generator", page_icon="🛡️")
    
    st.title("GDPR PDF Generator")
    st.markdown("Generate a simple GDPR compliance report PDF")
    
    # Create a simple form
    with st.form(key="pdf_form"):
        # Form inputs
        organization = st.text_input("Organization Name", value="Your Organization")
        
        certification = st.selectbox(
            "Certification Type",
            ["GDPR Compliant", "ISO 27001 Aligned", "UAVG Certified"]
        )
        
        compliance_score = st.slider("Compliance Score (%)", 0, 100, 75)
        
        # Submit button
        submit_button = st.form_submit_button(label="Generate PDF", type="primary")
        
    # Outside the form to avoid form validation issues
    if submit_button:
        # Show a spinner during generation
        with st.spinner("Generating your PDF..."):
            # Fake progress bar
            progress = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress.progress((i + 1)/100)
            
            # Create a very simple PDF
            pdf_content = f"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/MediaBox[0 0 595 842]/Parent 2 0 R/Resources<</Font<</F1<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>>>>>/Contents 4 0 R>>endobj
4 0 obj<</Length 300>>stream
BT
/F1 24 Tf
50 800 Td
(GDPR Compliance Report) Tj
/F1 12 Tf
0 -50 Td
(Organization: {organization}) Tj
0 -20 Td
(Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}) Tj
0 -20 Td
(Certification: {certification}) Tj
0 -20 Td
(Compliance Score: {compliance_score}%) Tj
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
578
%%EOF""".encode('latin1')
            
            # Create a BytesIO object from the PDF content
            pdf_buffer = BytesIO(pdf_content)
            
            # Display download button
            st.download_button(
                label="Download GDPR Report PDF",
                data=pdf_buffer,
                file_name=f"GDPR_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf"
            )
            
            # Success message
            st.success("PDF generated successfully!")
            
            # Show some info about the generated PDF
            st.info(f"""
            Report generated with:
            - Organization: {organization}
            - Certification: {certification}
            - Compliance Score: {compliance_score}%
            - Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
            """)

if __name__ == "__main__":
    main()