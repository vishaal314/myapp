"""
Bank Authentication Simulator for iDEAL Payments

This module provides a simulated bank authentication interface for iDEAL payments.
It handles the redirect from the payment process and simulates the bank's authorization flow.
"""

import streamlit as st
import time
import random
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
from billing.stripe_integration import _get_mock_payment_intent, _update_mock_payment_status, _save_mock_payment_intent

def render_bank_auth_simulator(payment_intent_id: str, return_url: str = "https://dataguardianpro.com/payment/complete"):
    """
    Render a simulated bank authentication interface
    
    Args:
        payment_intent_id: The ID of the payment intent to authenticate
        return_url: URL to return to after authentication
    """
    st.title("iDEAL Bank Authentication Simulator")
    
    # Custom CSS for bank appearance
    st.markdown("""
    <style>
    .bank-header {
        background-color: #003366;
        color: white;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 30px;
        text-align: center;
    }
    
    .auth-container {
        background-color: #f8f9fa;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    .bank-footer {
        font-size: 0.8rem;
        color: #718096;
        text-align: center;
        margin-top: 50px;
        border-top: 1px solid #e2e8f0;
        padding-top: 20px;
    }
    
    .action-button {
        width: 100%;
        margin-top: 10px;
    }
    
    .secure-badge {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-top: 20px;
        color: #2d3748;
        font-size: 0.9rem;
    }
    
    .spinner-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 30px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Get payment details if available
    payment_details = _get_mock_payment_intent(payment_intent_id)
    if not payment_details:
        st.error("Invalid payment session. Please return to the payment page and try again.")
        if st.button("Return to Payment Page"):
            st.session_state.bank_auth_step = "init"
            st.session_state.payment_flow_step = "select_bank"
            st.rerun()
        return
    
    # Initialize session state for auth flow
    if "bank_auth_step" not in st.session_state:
        st.session_state.bank_auth_step = "init"
        
    if "auth_attempts" not in st.session_state:
        st.session_state.auth_attempts = 0
        
    # Step 1: Bank Login
    if st.session_state.bank_auth_step == "init":
        # Bank header
        bank_name = payment_details.get("bank", "ING")
        amount = payment_details.get("amount", 2500) / 100
        currency = payment_details.get("currency", "EUR").upper()
        merchant = payment_details.get("description", "DataGuardian Pro")
        
        st.markdown(f"""
        <div class="bank-header">
            <h2>{bank_name.upper()} Bank Authentication</h2>
            <p>Secure Payment Portal</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Payment details
        st.subheader("Confirm Your Payment")
        st.markdown(f"""
        <div class="auth-container">
            <p><strong>Merchant:</strong> {merchant}</p>
            <p><strong>Amount:</strong> {currency} {amount:.2f}</p>
            <p><strong>Date:</strong> {datetime.now().strftime('%d-%m-%Y %H:%M')}</p>
            <p><strong>Payment ID:</strong> {payment_intent_id[:8]}...{payment_intent_id[-4:]}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Authentication options
        st.subheader("Choose Authentication Method")
        auth_method = st.radio(
            "Select your authentication method:",
            ["Mobile Banking App", "SMS Verification", "Security Token"],
            key="auth_method"
        )
        
        if auth_method == "Mobile Banking App":
            st.info("You'll need to confirm this payment in your mobile banking app.")
            st.text_input("Mobile Number", value="+31 6 ** *** **89", disabled=True)
            
        elif auth_method == "SMS Verification":
            st.text_input("Mobile Number", value="+31 6 ** *** **89", disabled=True)
            
        elif auth_method == "Security Token":
            st.text_input("Token Serial Number", value="TOKEN-******3456", disabled=True)
            st.text_input("Challenge Code", value="674831", disabled=True)
            response_code = st.text_input("Response Code", placeholder="Enter the 6-digit code from your token")
            
            if response_code and len(response_code) != 6:
                st.error("Response code must be 6 digits")
                
        # Continue button
        if st.button("Continue with Authentication", type="primary", key="auth_continue"):
            st.session_state.bank_auth_step = "processing"
            st.rerun()
            
        # Cancel button
        if st.button("Cancel Payment", key="auth_cancel"):
            # Update payment status to canceled
            _update_mock_payment_status(payment_intent_id, "canceled")
            st.error("Payment has been canceled.")
            time.sleep(2)
            # Redirect to return URL with canceled status
            st.session_state.bank_auth_step = "canceled"
            st.rerun()
            
        # Security badge
        st.markdown("""
        <div class="secure-badge">
            🔒 Secure connection | Bank-level encryption | PSD2 Compliant
        </div>
        """, unsafe_allow_html=True)
            
    # Step 2: Processing
    elif st.session_state.bank_auth_step == "processing":
        st.markdown(f"""
        <div class="bank-header">
            <h2>Processing Authentication</h2>
            <p>Please wait while we verify your payment</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show spinner and progress messages
        with st.spinner("Authenticating your payment..."):
            # Simulate processing time
            status_message = st.empty()
            
            # Show progression messages
            status_message.info("Connecting to secure payment gateway...")
            time.sleep(1.5)
            
            status_message.info("Verifying account details...")
            time.sleep(1.2)
            
            status_message.info("Processing payment authorization...")
            time.sleep(1.8)
            
            # 90% success rate
            success = random.random() < 0.9
            
            if success:
                # Update payment status to succeeded
                _update_mock_payment_status(payment_intent_id, "succeeded")
                
                status_message.success("Payment successfully authorized!")
                time.sleep(1)
                
                st.balloons()
                
                # Show success message and redirect button
                st.success("Your payment has been authorized successfully. You will now be redirected back to the merchant.")
                
                # Create success message
                st.success("Your payment has been authorized successfully. You will be redirected back to the merchant.")
                
                # Return button
                if st.button("Return to Merchant Now", type="primary"):
                    # Reset state
                    st.session_state.bank_auth_step = "init"
                    st.session_state.in_bank_auth_mode = False
                    
                    # Set query parameters for return handler
                    st.query_params["payment_intent"] = payment_intent_id
                    st.query_params["payment_success"] = "true"
                    
                    # Rerun to apply the parameters and trigger the return handler
                    st.rerun()
                    
            else:
                # Update payment status to failed
                _update_mock_payment_status(payment_intent_id, "requires_payment_method")
                
                status_message.error("Authentication failed!")
                time.sleep(1)
                
                # Show error message and retry button
                st.error("Unfortunately, the payment authorization has failed. Please try again or select a different payment method.")
                
                if st.button("Try Again", key="retry_auth"):
                    st.session_state.auth_attempts += 1
                    
                    if st.session_state.auth_attempts >= 3:
                        st.warning("Multiple failed attempts detected. Please try a different payment method.")
                        st.session_state.bank_auth_step = "canceled"
                    else:
                        st.session_state.bank_auth_step = "init"
                    
                    st.rerun()
                    
                if st.button("Cancel and Return to Merchant", key="cancel_return"):
                    st.session_state.bank_auth_step = "canceled"
                    st.rerun()
                    
    # Step 3: Canceled
    elif st.session_state.bank_auth_step == "canceled":
        st.markdown(f"""
        <div class="bank-header" style="background-color: #742a2a;">
            <h2>Payment Canceled</h2>
            <p>Your payment has been canceled</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.warning("You have canceled the payment or the authentication failed.")
        
        # Create return URL with payment canceled parameter
        return_url = f"/?payment_intent={payment_intent_id}&payment_canceled=true"
        
        # Show redirect button
        if st.button("Return to Merchant", type="primary"):
            # Reset state
            st.session_state.bank_auth_step = "init"
            st.session_state.in_bank_auth_mode = False
            
            # Redirect to payment return handler
            st.markdown(f'<meta http-equiv="refresh" content="0;URL=\'{return_url}\'" />', unsafe_allow_html=True)
            st.stop()
            
        # Auto-redirect after a delay
        redirect_url = f"/?payment_intent={payment_intent_id}&payment_canceled=true"
        st.markdown(f"""
        <meta http-equiv="refresh" content="5;URL='{redirect_url}'" />
        """, unsafe_allow_html=True)
        
    # Bank footer
    st.markdown("""
    <div class="bank-footer">
        <p>This is a simulated bank authentication environment for demonstration purposes only.</p>
        <p>No real banking transactions are being processed, and no personal data is being stored.</p>
        <p>© 2025 Secure Banking Simulator | Privacy Policy | Terms of Service</p>
    </div>
    """, unsafe_allow_html=True)
    
def run_standalone_simulator():
    """Run a standalone bank authentication simulator for testing"""
    st.title("Standalone Bank Authentication Simulator")
    
    # Create a test payment intent ID
    test_intent_id = f"pi_test_{hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:16]}"
    
    # Create mock payment details
    payment_details = {
        "id": test_intent_id,
        "amount": 2500,
        "currency": "eur",
        "bank": "ING",
        "description": "DataGuardian Pro Test Payment",
        "status": "requires_action",
        "created_at": datetime.now().strftime("%d/%m/%Y %H:%M")
    }
    
    # Save the test intent
    _save_mock_payment_intent(test_intent_id, payment_details)
    
    # Launch the simulator
    render_bank_auth_simulator(test_intent_id, "http://localhost:5000")
    
# For direct testing
if __name__ == "__main__":
    run_standalone_simulator()