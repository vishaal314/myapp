import streamlit as st
import os
import uuid
import logging
from datetime import datetime
import json
import tempfile
import shutil

# Core imports that don't depend on numpy
from services.image_scanner import ImageScanner
from services.image_report_generator import ImageReportGenerator
from services.html_report_generator_fixed import HTMLReportGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="DataGuardian Pro",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("DataGuardian Pro")
    st.subheader("Enterprise Privacy Compliance Platform")
    
    # Navigation
    tab1, tab2 = st.tabs(["Image Scanner", "About"])
    
    with tab1:
        st.header("Image Scanner")
        st.write("Upload images to scan for personally identifiable information (PII)")
        
        # File upload
        uploaded_files = st.file_uploader(
            "Choose images", 
            accept_multiple_files=True, 
            type=["png", "jpg", "jpeg", "gif", "bmp"]
        )
        
        if uploaded_files:
            st.write(f"Uploaded {len(uploaded_files)} file(s)")
            
            # Scan button
            if st.button("Start Image Scan", type="primary"):
                run_image_scan(uploaded_files)
    
    with tab2:
        st.header("About DataGuardian Pro")
        st.write("""
        DataGuardian Pro is an advanced enterprise privacy compliance platform that 
        leverages AI-powered scanning for comprehensive digital ecosystem risk assessment.
        
        **Features:**
        - Image PII Detection with OCR
        - Professional compliance reporting
        - PDF and HTML report generation
        - GDPR compliance assessment
        """)

def run_image_scan(uploaded_files):
    """Run image scan with progress tracking and results display"""
    
    # Create progress indicators
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Initialize scanner
        status_text.text("Initializing image scanner...")
        scanner = ImageScanner(region="Netherlands")
        progress_bar.progress(10)
        
        # Create temporary directory for uploaded files
        temp_dir = tempfile.mkdtemp()
        image_paths = []
        
        # Save uploaded files to temp directory
        status_text.text("Processing uploaded files...")
        for i, uploaded_file in enumerate(uploaded_files):
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            image_paths.append(file_path)
            progress_bar.progress(10 + (i + 1) * 30 // len(uploaded_files))
        
        # Run scan
        status_text.text("Scanning images for PII...")
        progress_bar.progress(50)
        
        scan_results = scanner.scan_images(image_paths)
        progress_bar.progress(90)
        
        # Display results
        status_text.text("Scan complete!")
        progress_bar.progress(100)
        
        display_image_scan_results(scan_results)
        
        # Clean up temp directory
        shutil.rmtree(temp_dir, ignore_errors=True)
        
    except Exception as e:
        st.error(f"Error during image scan: {str(e)}")
        logger.error(f"Image scan error: {e}")
        # Clean up on error
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir, ignore_errors=True)

def display_image_scan_results(scan_results):
    """Display image scan results with download options"""
    
    st.header("Image Scan Results")
    
    # Get scan metadata
    metadata = scan_results.get('metadata', {})
    findings = scan_results.get('findings', [])
    risk_summary = scan_results.get('risk_summary', {})
    
    # Display summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Images Scanned", metadata.get('images_scanned', 0))
    
    with col2:
        st.metric("PII Findings", len(findings))
    
    with col3:
        risk_level = risk_summary.get('level', 'Unknown')
        risk_color = {
            'Critical': '🔴',
            'High': '🟠', 
            'Medium': '🟡',
            'Low': '🟢'
        }.get(risk_level, '⚪')
        st.metric("Risk Level", f"{risk_color} {risk_level}")
    
    with col4:
        st.metric("Risk Score", f"{risk_summary.get('score', 0)}/100")
    
    # Display findings or compliance message
    if findings:
        st.subheader("PII Findings")
        
        for finding in findings:
            with st.expander(f"{finding.get('type', 'Unknown')} - {finding.get('risk_level', 'Unknown')} Risk"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Source:** {os.path.basename(finding.get('source', 'Unknown'))}")
                    st.write(f"**Confidence:** {finding.get('confidence', 0):.0%}")
                with col2:
                    st.write(f"**Risk Level:** {finding.get('risk_level', 'Unknown')}")
                    st.write(f"**Method:** {finding.get('extraction_method', 'Unknown')}")
    else:
        # Display compliance success message
        st.success("✅ **Compliance Check Passed**")
        st.info("""
        **No PII Detected** - Your images have been thoroughly scanned and no personally 
        identifiable information was found. This indicates good privacy compliance practices.
        
        **Scan Coverage:**
        - OCR text extraction and analysis
        - Pattern matching for common PII types
        - Computer vision analysis for sensitive content
        - Dutch GDPR compliance standards applied
        """)
    
    # Download options
    st.subheader("Download Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Download PDF Report", type="secondary"):
            generate_and_download_pdf(scan_results)
    
    with col2:
        if st.button("🌐 Download HTML Report", type="secondary"):
            generate_and_download_html(scan_results)

def generate_and_download_pdf(scan_results):
    """Generate and offer PDF report for download"""
    try:
        # Initialize report generator
        report_generator = ImageReportGenerator()
        
        # Generate PDF
        pdf_data = report_generator.generate_pdf_report(scan_results)
        
        # Create download
        st.download_button(
            label="💾 Save PDF Report",
            data=pdf_data,
            file_name=f"image_scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            type="primary"
        )
        
        st.success("PDF report generated successfully!")
        
    except Exception as e:
        st.error(f"Error generating PDF report: {str(e)}")
        logger.error(f"PDF generation error: {e}")

def generate_and_download_html(scan_results):
    """Generate and offer HTML report for download"""
    try:
        # Initialize HTML report generator  
        html_generator = HTMLReportGenerator()
        
        # Generate HTML
        html_content = html_generator.generate_image_html_report(scan_results)
        
        # Create download
        st.download_button(
            label="💾 Save HTML Report", 
            data=html_content,
            file_name=f"image_scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            mime="text/html",
            type="primary"
        )
        
        st.success("HTML report generated successfully!")
        
    except Exception as e:
        st.error(f"Error generating HTML report: {str(e)}")
        logger.error(f"HTML generation error: {e}")

if __name__ == "__main__":
    main()