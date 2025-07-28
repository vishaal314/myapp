#!/usr/bin/env python3
"""
iDEAL Payment Testing Interface for DataGuardian Pro
Test real ABN AMRO card payments through Stripe iDEAL integration
"""

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.stripe_payment import display_payment_button, handle_payment_callback, verify_payment
from services.results_aggregator import ResultsAggregator

# Note: set_page_config already called in main app.py
# st.set_page_config(
#     page_title="iDEAL Payment Testing - DataGuardian Pro",
#     page_icon="💳",
#     layout="wide"
# )

# Initialize results aggregator for payment logging
@st.cache_resource
def get_results_aggregator():
    return ResultsAggregator()

def main():
    st.title("💳 iDEAL Payment Testing - DataGuardian Pro")
    st.markdown("### Test real ABN AMRO card payments with iDEAL integration")
    
    # Handle payment callbacks first
    results_aggregator = get_results_aggregator()
    handle_payment_callback(results_aggregator)
    
    # Check if payment was successful
    if st.session_state.get('payment_successful', False):
        st.success("🎉 Payment Successful!")
        payment_details = st.session_state.get('payment_details', {})
        
        st.json({
            "status": payment_details.get("status"),
            "amount": f"€{payment_details.get('amount', 0):.2f}",
            "payment_method": payment_details.get("payment_method"),
            "scan_type": payment_details.get("scan_type"),
            "currency": payment_details.get("currency", "eur").upper(),
            "country": payment_details.get("country_code", "NL"),
            "timestamp": payment_details.get("timestamp")
        })
        
        if st.button("🔄 Test Another Payment"):
            st.session_state.payment_successful = False
            st.session_state.payment_details = {}
            st.rerun()
        return
    
    # Payment test interface
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🧪 Test Configuration")
        
        # Test email (can use real email for receipts)
        test_email = st.text_input(
            "Your Email (for payment receipt):",
            value="test@example.com",
            help="Use your real email to receive payment confirmation"
        )
        
        # Select scan type to test
        scan_options = {
            "Code Scan": "€23.00 + €4.83 VAT = €27.83",
            "Blob Scan": "€14.00 + €2.94 VAT = €16.94", 
            "Image Scan": "€28.00 + €5.88 VAT = €33.88",
            "Database Scan": "€46.00 + €9.66 VAT = €55.66",
            "API Scan": "€18.00 + €3.78 VAT = €21.78",
            "Manual Upload": "€9.00 + €1.89 VAT = €10.89",
            "Sustainability Scan": "€32.00 + €6.72 VAT = €38.72",
            "AI Model Scan": "€41.00 + €8.61 VAT = €49.61",
            "SOC2 Scan": "€55.00 + €11.55 VAT = €66.55"
        }
        
        selected_scan = st.selectbox(
            "Select Scanner to Test:",
            options=list(scan_options.keys()),
            format_func=lambda x: f"{x} - {scan_options[x]}"
        )
        
        # Country selection (defaults to Netherlands for iDEAL)
        country = st.selectbox(
            "Country (for VAT calculation):",
            options=["NL", "DE", "FR", "BE"],
            index=0,
            help="Netherlands (NL) enables iDEAL payments"
        )
    
    with col2:
        st.markdown("### 💳 iDEAL Payment Info")
        
        if country == "NL":
            st.success("✅ iDEAL payments enabled for Netherlands")
            st.markdown("""
            **Available Payment Methods:**
            - 💳 Credit/Debit Cards (Visa, Mastercard)
            - 🏦 **iDEAL** (all Dutch banks including ABN AMRO)
            
            **iDEAL Banks Supported:**
            - ABN AMRO
            - ING Bank
            - Rabobank
            - SNS Bank
            - ASN Bank
            - Bunq
            - Knab
            - Moneyou
            - RegioBank
            - Triodos Bank
            """)
        else:
            st.info("ℹ️ iDEAL only available for Netherlands (NL)")
            st.markdown("**Available Payment Methods:** Credit/Debit Cards only")
        
        st.markdown("### 🔒 Security Features")
        st.markdown("""
        - ✅ **Stripe Secure Checkout**
        - ✅ **SSL/TLS Encryption**
        - ✅ **PCI DSS Compliant**
        - ✅ **GDPR Compliant**
        - ✅ **3D Secure Authentication**
        - ✅ **Real-time Fraud Detection**
        """)
    
    st.markdown("---")
    
    # Payment testing section
    st.markdown("### 🧪 Live Payment Test")
    
    if country == "NL":
        st.info("""
        **Testing with Real ABN AMRO Card:**
        1. Click the payment button below
        2. You'll be redirected to Stripe Checkout
        3. Select "iDEAL" as payment method
        4. Choose "ABN AMRO" from the bank list
        5. You'll be redirected to ABN AMRO's secure login
        6. Complete the payment with your real ABN AMRO credentials
        7. Return here to see the payment confirmation
        
        **Note:** This will process a real payment. Use small amounts for testing.
        """)
    else:
        st.warning("Select Netherlands (NL) to enable iDEAL testing with ABN AMRO")
    
    # Display payment button
    if test_email:
        display_payment_button(
            scan_type=selected_scan,
            user_email=test_email,
            metadata={
                "test_mode": "true",
                "testing_bank": "ABN AMRO",
                "test_timestamp": str(st.session_state.get('timestamp', ''))
            },
            country_code=country
        )
    else:
        st.warning("Please enter an email address to continue")
    
    # Testing instructions
    st.markdown("---")
    st.markdown("### 📋 Testing Instructions")
    
    with st.expander("🏦 How to Test with ABN AMRO iDEAL"):
        st.markdown("""
        **Step-by-Step Testing Process:**
        
        1. **Prepare Your ABN AMRO Account**
           - Ensure you have online banking access
           - Have your login credentials ready
           - Sufficient balance for the test amount
        
        2. **Initiate Payment**
           - Enter your real email above
           - Select a scan type to test
           - Click "Proceed to Secure Payment"
        
        3. **Stripe Checkout Process**
           - You'll be redirected to Stripe's secure checkout
           - Select "iDEAL" from payment methods
           - Choose "ABN AMRO" from the bank dropdown
        
        4. **ABN AMRO Authentication**
           - You'll be redirected to ABN AMRO's secure site
           - Log in with your normal banking credentials
           - Confirm the payment amount and details
           - Authorize the transaction
        
        5. **Payment Confirmation**
           - You'll be redirected back to this page
           - Payment confirmation will be displayed
           - Email receipt will be sent to your email
        
        **Security Notes:**
        - Your banking credentials never pass through our system
        - All authentication is handled directly by ABN AMRO
        - Payment processing is secured by Stripe (PCI DSS Level 1)
        - Transaction data is encrypted end-to-end
        """)
    
    with st.expander("🔧 Test Environment Details"):
        st.markdown(f"""
        **Current Configuration:**
        - **Environment:** {"Production" if "sk_live" in os.getenv('STRIPE_SECRET_KEY', '') else "Test Mode"}
        - **Stripe Account:** Configured and Active
        - **iDEAL Support:** Enabled for Netherlands
        - **VAT Calculation:** 21% for Netherlands
        - **Currency:** EUR (Euros)
        - **Base URL:** {os.getenv('REPLIT_URL', 'http://localhost:5000')}
        
        **Available Test Banks:**
        - ABN AMRO (your primary test target)
        - ING Bank
        - Rabobank
        - All other Dutch iDEAL banks
        """)

if __name__ == "__main__":
    main()