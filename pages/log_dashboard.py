#!/usr/bin/env python3
"""
DataGuardian Pro - Log Dashboard Page
Real-time log monitoring and analysis dashboard
"""

import streamlit as st
from utils.log_monitor import show_log_dashboard
from utils.centralized_logger import get_logger, LogCategory

# Initialize logger for this page
logger = get_logger("log_dashboard", LogCategory.SYSTEM)

def main():
    """Main log dashboard page"""
    st.set_page_config(
        page_title="DataGuardian Pro - Log Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    logger.info("Log dashboard page accessed", user_id=st.session_state.get('username', 'anonymous'))
    
    # Show the log monitoring dashboard
    show_log_dashboard()

if __name__ == "__main__":
    main()