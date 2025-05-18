"""
Test Script for iDEAL Payment Integration

This script provides a standalone test for the iDEAL payment flow
using the Stripe API integration. It allows testing the complete
end-to-end process from customer creation to payment completion.
"""

import streamlit as st
from billing.ideal_payment_page import test_ideal_payment_page

def main():
    """
    Main function to run the iDEAL payment test page
    """
    st.set_page_config(
        page_title="iDEAL Payment Test",
        page_icon="💶",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Display sidebar with test controls
    st.sidebar.title("iDEAL Payment Test")
    st.sidebar.info("""
    This is a test page for the iDEAL payment integration.
    
    The integration includes:
    
    1. Creating Stripe customers
    2. Saving iDEAL payment methods
    3. Processing payments with bank redirect
    4. Checking payment status
    
    Test with different banks and amounts to verify the integration.
    """)
    
    # Add API key status indicator in sidebar
    import os
    api_key = os.environ.get("STRIPE_SECRET_KEY")
    publishable_key = os.environ.get("STRIPE_PUBLISHABLE_KEY")
    
    st.sidebar.subheader("API Key Status")
    if api_key:
        st.sidebar.success("✅ Stripe Secret Key: Available")
    else:
        st.sidebar.error("❌ Stripe Secret Key: Missing")
        st.sidebar.warning("""
        The Stripe Secret Key is required for live API integration.
        Without it, the system will fall back to mock mode.
        """)
        
    if publishable_key:
        st.sidebar.success("✅ Stripe Publishable Key: Available")
    else:
        st.sidebar.info("ℹ️ Stripe Publishable Key: Not needed for server-side integration")
    
    # Run the test page
    test_ideal_payment_page()

if __name__ == "__main__":
    main()