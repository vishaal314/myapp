import streamlit as st
import os
from datetime import datetime
from services.blob_scanner import BlobScanner
from services.document_report_generator import generate_document_html_report, generate_document_pdf_report

# Set page configuration first
st.set_page_config(
    page_title="DataGuardian Pro - Document Scanner",
    page_icon="🛡️",
    layout="wide"
)

def main():
    """Clean, simple Document Scanner interface"""
    st.title("🛡️ DataGuardian Pro")
    st.subheader("Document Privacy Compliance Scanner")
    st.write("Upload and scan documents for GDPR compliance violations")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a document to scan", 
        type=['txt', 'pdf', 'docx'],
        help="Upload text files, PDFs, or Word documents"
    )
    
    if uploaded_file:
        st.success(f"File uploaded: {uploaded_file.name}")
        
        if st.button("🔍 Run Document Scan", type="primary"):
            with st.spinner("Scanning document for GDPR violations..."):
                try:
                    # Save uploaded file temporarily
                    temp_path = f"temp_{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Run scanner
                    scanner = BlobScanner(region='Netherlands')
                    results = scanner.scan_multiple_documents([temp_path])
                    
                    # Display results
                    st.success("✅ Scan completed!")
                    
                    # Results metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Findings", len(results.get('findings', [])))
                    with col2:
                        st.metric("Critical Risk", results.get('critical_risk_count', 0))
                    with col3:
                        st.metric("High Risk", results.get('high_risk_count', 0))
                    with col4:
                        st.metric("Medium Risk", results.get('medium_risk_count', 0))
                    
                    # Show findings details
                    if results.get('findings'):
                        st.markdown("### 🔍 Key Findings")
                        for i, finding in enumerate(results['findings'][:10]):  # Show first 10
                            risk_color = {
                                'Critical': '🔴',
                                'High': '🟠', 
                                'Medium': '🟡',
                                'Low': '🟢'
                            }.get(finding.get('risk_level', 'Medium'), '🟡')
                            
                            st.write(f"{risk_color} **{finding.get('type', 'PII')}**: {finding.get('value', 'Detected')}")
                    
                    # Generate reports
                    html_content = generate_document_html_report(results)
                    pdf_bytes = generate_document_pdf_report(results)
                    
                    # Download buttons
                    st.markdown("### 📥 Download Reports")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.download_button(
                            label="📊 Download HTML Report",
                            data=html_content,
                            file_name=f"document_scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                            mime="text/html",
                            use_container_width=True
                        )
                    
                    with col2:
                        st.download_button(
                            label="📄 Download PDF Certificate",
                            data=pdf_bytes,
                            file_name=f"document_scan_certificate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf", 
                            use_container_width=True
                        )
                    
                    # Clean up
                    os.remove(temp_path)
                    
                except Exception as e:
                    st.error(f"Scan failed: {str(e)}")
    
    else:
        # Show example
        st.info("💡 Upload a document above to test the scanner. The system detects BSN numbers, PII data, and GDPR violations.")

if __name__ == "__main__":
    main()