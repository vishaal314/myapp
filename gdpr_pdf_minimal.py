"""
Absolute Minimal GDPR PDF Generator
"""

import streamlit as st

def main():
    st.title("Minimal GDPR PDF Generator")
    
    # Fixed, pre-generated PDF content (minimal valid PDF)
    pdf_data = """%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/MediaBox[0 0 595 842]/Parent 2 0 R/Resources<</Font<</F1<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>>>>>/Contents 4 0 R>>endobj
4 0 obj<</Length 90>>stream
BT
/F1 24 Tf
50 800 Td
(GDPR Compliance Report) Tj
/F1 12 Tf
0 -50 Td
(Basic GDPR compliance report) Tj
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
368
%%EOF"""
    
    if st.button("Get PDF Report", type="primary"):
        # Convert string to bytes for download
        pdf_bytes = pdf_data.encode('latin1')
        
        # Display download button
        st.download_button(
            label="Download Report",
            data=pdf_bytes,
            file_name="basic_gdpr_report.pdf",
            mime="application/pdf"
        )
        
        # Show success
        st.success("PDF report generated successfully!")

if __name__ == "__main__":
    main()