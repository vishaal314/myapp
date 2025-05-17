"""
Clean GDPR Code Scanner Page

A standalone GDPR Code Scanner with modern UI design for DataGuardian Pro
"""

import streamlit as st
import os
import base64
import time
from datetime import datetime

# Import the scanner module and UI components
from gdpr_scanner_module import GDPRScanner, generate_pdf_report
from clean_gdpr_code_scanner_ui import render_gdpr_scanner_ui

def main():
    # Set page configuration
    st.set_page_config(
        page_title="GDPR Code Scanner",
        page_icon="🛡️",
        layout="wide"
    )
    
    # Render the scanner UI
    render_gdpr_scanner_ui()

if __name__ == "__main__":
    main()