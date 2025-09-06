#!/usr/bin/env python3
"""
DataGuardian Pro - Scanner Log Dashboard Page
Redesigned scanner-focused log monitoring and analysis dashboard
"""

import streamlit as st
from utils.scanner_log_dashboard import show_scanner_log_dashboard
from utils.centralized_logger import get_logger, LogCategory

# Initialize logger for this page
logger = get_logger("scanner_log_dashboard", LogCategory.SYSTEM)

def main():
    """Main scanner log dashboard page"""
    st.set_page_config(
        page_title="DataGuardian Pro - Scanner Logs",
        page_icon="🔍",
        layout="wide"
    )
    
    logger.info("Scanner log dashboard accessed", user_id=st.session_state.get('username', 'anonymous'))
    
    # Show the redesigned scanner log dashboard
    show_scanner_log_dashboard()

if __name__ == "__main__":
    main()