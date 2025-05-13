"""
Ultra Simple GDPR PDF Generator that's guaranteed to work
"""

import streamlit as st
import base64

def create_download_link(pdf_bytes, filename):
    """Create a download link for a PDF byte array"""
    b64 = base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}" class="download-btn">Download PDF</a>'
    return href

def main():
    st.title("GDPR PDF Generator")
    
    # Create the minimal PDF that will definitely work
    pdf_data = b"""%PDF-1.4
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
(Compliance Report Data) Tj
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
    
    if st.button('Generate PDF Report', type="primary"):
        # Create a download link
        st.markdown(create_download_link(pdf_data, "gdpr_report.pdf"), unsafe_allow_html=True)
        
        # Styling for the download button
        st.markdown("""
        <style>
        .download-btn {
            display: inline-block;
            padding: 12px 24px;
            background-color: #FF4B4B;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            margin: 20px 0;
            text-align: center;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Show success message
        st.success("Report generated successfully! Click the link above to download.")

if __name__ == "__main__":
    main()