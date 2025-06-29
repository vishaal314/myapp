# DataGuardian Pro - Enterprise Privacy Compliance Platform
# This file now delegates to the modular app_main.py to reduce complexity

try:
    # Import and run the modular main application
    from app_main import main
    
    if __name__ == "__main__":
        main()
    else:
        main()  # Run main regardless of how this module is imported
        
except Exception as e:
    import streamlit as st
    import logging
    
    logging.error(f"Critical error in main application: {str(e)}")
    st.error("Application startup error. Please refresh the page.")
    
    # Fallback to simple error display
    st.markdown("""
    ### DataGuardian Pro - Startup Error
    
    There was an error starting the application. This may be due to:
    - Missing dependencies
    - Configuration issues
    - Database connectivity problems
    
    Please contact support if this error persists.
    """)