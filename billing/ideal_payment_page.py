"""
iDEAL Payment Page for DataGuardian Pro

This module provides a complete test interface for iDEAL payments
including bank selection, payment initiation, and status checking.
"""

import streamlit as st
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from billing.stripe_integration import (
    init_stripe,
    create_stripe_customer,
    create_payment_method,
    process_ideal_payment,
    check_payment_status
)

def render_ideal_payment_page(username: str, user_data: Dict[str, Any]):
    """
    Render a test page for iDEAL payments
    
    Args:
        username: Username of the logged-in user
        user_data: User data dictionary
    """
    # Check if we're in bank auth mode and handle it first
    if 'in_bank_auth_mode' in st.session_state and st.session_state.in_bank_auth_mode:
        # Import bank auth simulator
        from billing.bank_auth_simulator import render_bank_auth_simulator
        
        # Render the bank auth simulator
        payment_id = st.session_state.get('bank_auth_payment_id', '')
        return_url = st.session_state.get('bank_auth_return_url', 'https://dataguardianpro.com/payment/complete')
        
        if payment_id:
            # Add a title with back button
            col1, col2 = st.columns([5, 1])
            with col1:
                st.title("Bank Authentication")
            with col2:
                if st.button("❌ Close", key="close_bank_auth"):
                    st.session_state.in_bank_auth_mode = False
                    st.rerun()
            
            # Render the simulator
            render_bank_auth_simulator(payment_id, return_url)
            
            # Add a way to exit bank auth mode
            if st.button("Return to Payment Page", key="exit_bank_auth"):
                st.session_state.in_bank_auth_mode = False
                st.rerun()
                
            # Don't render the rest of the page
            return
    
    # Regular payment page
    st.title("iDEAL Payment Test")
    
    # Custom CSS
    st.markdown("""
    <style>
    .bank-selection {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 10px;
        margin-bottom: 20px;
    }
    .bank-option {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s;
    }
    .bank-option:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    .bank-logo {
        width: 100px;
        height: 60px;
        margin: 0 auto 10px auto;
        display: block;
        object-fit: contain;
    }
    .selected {
        border: 2px solid #4CAF50;
        background-color: #f0fff4;
    }
    .payment-status {
        padding: 15px;
        border-radius: 8px;
        margin-top: 20px;
    }
    .payment-status.success {
        background-color: #f0fff4;
        border: 1px solid #c6f6d5;
    }
    .payment-status.pending {
        background-color: #fffaf0;
        border: 1px solid #feebc8;
    }
    .payment-status.error {
        background-color: #fff5f5;
        border: 1px solid #fed7d7;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Get customer ID
    customer_id = user_data.get("stripe_customer_id")
    if not customer_id:
        st.warning("You don't have a Stripe customer account yet. Creating one for testing.")
        customer_id = create_stripe_customer({
            "email": user_data.get("email", f"{username}@example.com"),
            "name": user_data.get("name", username),
            "metadata": {"username": username}
        })
        st.success(f"Created test customer ID: {customer_id}")
        
        # Update user data with the new customer ID
        user_data["stripe_customer_id"] = customer_id
    
    # Payment flow state
    if "payment_flow_step" not in st.session_state:
        st.session_state.payment_flow_step = "select_bank"
        
    if "selected_bank" not in st.session_state:
        st.session_state.selected_bank = None
        
    if "payment_amount" not in st.session_state:
        st.session_state.payment_amount = 2500  # €25.00
        
    if "payment_intent" not in st.session_state:
        st.session_state.payment_intent = None
        
    if "payment_status" not in st.session_state:
        st.session_state.payment_status = None
    
    # Step 1: Bank Selection
    if st.session_state.payment_flow_step == "select_bank":
        st.header("Step 1: Select Your Bank")
        
        # Live mode toggle
        live_mode_col1, live_mode_col2 = st.columns([3, 1])
        with live_mode_col1:
            st.session_state.use_live_mode = st.toggle(
                "Enable real bank transactions (Live Mode)", 
                value=st.session_state.get("use_live_mode", False),
                help="When enabled, your payment will be processed through the actual banking system."
            )
            
        with live_mode_col2:
            if st.session_state.use_live_mode:
                st.info("LIVE MODE")
                st.warning("""
                ⚠️ **Important**: Real money will be charged to your bank account when using Live Mode.
                
                This will process an actual payment through the banking system using the Stripe iDEAL API.
                """)
            else:
                st.warning("TEST MODE")
                st.info("""
                ℹ️ In test mode, no real money is charged and you'll be redirected to our test bank simulator.
                
                To test with real banks, enable Live Mode above.
                """)
        
        # If live mode changes, reinitialize Stripe
        if "previous_live_mode" not in st.session_state or st.session_state.previous_live_mode != st.session_state.use_live_mode:
            st.session_state.previous_live_mode = st.session_state.use_live_mode
            st.session_state.stripe_initialized = init_stripe(live_mode=st.session_state.use_live_mode)
            
        # Available iDEAL banks
        banks = [
            {"id": "abn_amro", "name": "ABN AMRO"},
            {"id": "asn_bank", "name": "ASN Bank"},
            {"id": "bunq", "name": "Bunq"},
            {"id": "ing", "name": "ING"},
            {"id": "knab", "name": "Knab"},
            {"id": "rabobank", "name": "Rabobank"},
            {"id": "sns_bank", "name": "SNS Bank"},
            {"id": "triodos_bank", "name": "Triodos Bank"},
            {"id": "van_lanschot", "name": "Van Lanschot"}
        ]
        
        # Payment amount selection
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("Payment Amount")
            amount_options = {
                1000: "€10,00",
                2500: "€25,00", 
                5000: "€50,00",
                10000: "€100,00"
            }
            selected_amount = st.select_slider(
                "Select payment amount:", 
                options=list(amount_options.keys()),
                format_func=lambda x: amount_options[x],
                value=st.session_state.payment_amount
            )
            st.session_state.payment_amount = selected_amount
        
        # Bank selection
        st.subheader("Select your bank")
        
        # Display bank options in a grid
        st.markdown('<div class="bank-selection">', unsafe_allow_html=True)
        
        columns = st.columns(3)
        
        for i, bank in enumerate(banks):
            with columns[i % 3]:
                bank_id = bank["id"]
                bank_name = bank["name"]
                
                # Check if this bank is selected
                is_selected = st.session_state.selected_bank == bank_id
                selection_class = "selected" if is_selected else ""
                
                # Create clickable bank option
                if st.button(bank_name, key=f"bank_{bank_id}"):
                    st.session_state.selected_bank = bank_id
                    st.rerun()
                
                if is_selected:
                    st.success(f"Selected: {bank_name}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Continue button
        if st.session_state.selected_bank:
            if st.button("Continue to Payment", type="primary"):
                st.session_state.payment_flow_step = "process_payment"
                st.rerun()
        else:
            st.info("Please select your bank to continue.")
    
    # Step 2: Process Payment
    elif st.session_state.payment_flow_step == "process_payment":
        st.header("Step 2: Process Payment")
        
        selected_bank = st.session_state.selected_bank
        payment_amount = st.session_state.payment_amount
        
        # Find bank name for display
        bank_name = next((bank["name"] for bank in [
            {"id": "abn_amro", "name": "ABN AMRO"},
            {"id": "asn_bank", "name": "ASN Bank"},
            {"id": "bunq", "name": "Bunq"},
            {"id": "ing", "name": "ING"},
            {"id": "knab", "name": "Knab"},
            {"id": "rabobank", "name": "Rabobank"},
            {"id": "sns_bank", "name": "SNS Bank"},
            {"id": "triodos_bank", "name": "Triodos Bank"},
            {"id": "van_lanschot", "name": "Van Lanschot"}
        ] if bank["id"] == selected_bank), "Unknown Bank")
        
        st.write(f"Selected Bank: **{bank_name}**")
        st.write(f"Payment Amount: **€{payment_amount/100:.2f}**")
        
        # Confirm payment
        st.subheader("Payment Details")
        account_name = st.text_input(
            "Account Holder Name", 
            value=user_data.get("name", username),
            key="account_name"
        )
        
        receipt_email = st.text_input(
            "Receipt Email", 
            value=user_data.get("email", f"{username}@example.com"),
            key="receipt_email"
        )
        
        # Save payment method for future use
        save_payment_method = st.checkbox(
            "Save this payment method for future use", 
            value=True,
            key="save_payment_method"
        )
        
        # Create a placeholder for the payment status
        payment_status_placeholder = st.empty()
        
        # Process payment button
        if st.button("Process Payment", type="primary"):
            with st.spinner("Processing payment..."):
                try:
                    payment_method = None
                    
                    # Save the payment method if requested
                    if save_payment_method:
                        # Create iDEAL payment method
                        payment_method = create_payment_method(
                            customer_id,
                            payment_type="ideal",
                            bank=selected_bank,
                            account_name=account_name,
                            email=receipt_email
                        )
                        payment_method_id = payment_method.get("id")
                        st.session_state.payment_method_id = payment_method_id
                        st.success(f"Created iDEAL payment method: {payment_method_id}")
                    
                    # Process the payment
                    return_url = "https://dataguardianpro.com/payment/complete"  # In real app, use dynamic URL
                    
                    # Get current live mode status
                    is_live_mode = st.session_state.get("use_live_mode", False)
                    
                    # Dynamic description based on mode
                    payment_description = f"DataGuardian Pro {'LIVE' if is_live_mode else 'test'} payment via {bank_name}"
                    
                    payment_intent = process_ideal_payment(
                        customer_id=customer_id,
                        amount=payment_amount,
                        payment_method_id=payment_method.get("id") if payment_method else None,
                        return_url=return_url,
                        receipt_email=receipt_email,
                        description=payment_description,
                        live_mode=is_live_mode,
                        metadata={
                            "username": username,
                            "bank": selected_bank,
                            "test_payment": str(not is_live_mode).lower(),
                            "live_mode": str(is_live_mode).lower()
                        }
                    )
                    
                    st.session_state.payment_intent = payment_intent
                    st.session_state.payment_flow_step = "payment_status"
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error processing payment: {str(e)}")
                    payment_status_placeholder.error(f"Payment processing failed. Please try again.")
        
        # Back button
        if st.button("Back to Bank Selection"):
            st.session_state.payment_flow_step = "select_bank"
            st.rerun()
    
    # Step 3: Payment Status
    elif st.session_state.payment_flow_step == "payment_status":
        st.header("Step 3: Payment Status")
        
        payment_intent = st.session_state.payment_intent
        
        if not payment_intent:
            st.error("No payment information found. Please start over.")
            if st.button("Start Over"):
                st.session_state.payment_flow_step = "select_bank"
                st.session_state.payment_intent = None
                st.rerun()
            return
            
        # Display payment details
        payment_id = payment_intent.get("payment_intent_id")
        status = payment_intent.get("status", "unknown")
        client_secret = payment_intent.get("client_secret")
        redirect_url = payment_intent.get("redirect_url")
        error = payment_intent.get("error")
        
        # Show appropriate status UI
        if error:
            st.error(f"Payment Error: {error}")
            status_class = "error"
        elif status == "succeeded":
            st.success("Payment Successful!")
            status_class = "success"
        elif status == "processing":
            st.info("Payment is processing...")
            status_class = "pending"
        elif status == "requires_action" and redirect_url:
            # Check if we're in live mode or test mode
            is_live_mode = st.session_state.get("use_live_mode", False)
            
            if is_live_mode:
                st.warning("Your bank requires authentication to complete this payment.")
                st.info("You will be redirected to your bank's secure payment page to authenticate this transaction.")
                
                # Mode indicator for live mode
                st.error("⚠️ LIVE MODE: This will process a real payment at your bank")
                
                # Add a button to redirect directly to the real bank in live mode
                if st.button("Proceed to Bank Authentication", type="primary", key="go_to_real_bank"):
                    # Use JavaScript to redirect to the real bank
                    st.markdown(f"""
                    <script>
                        window.location.href = "{redirect_url}";
                    </script>
                    """, unsafe_allow_html=True)
                    
                    st.info("Redirecting to your bank's secure payment page...")
                    st.markdown(f"If you are not automatically redirected, [click here to continue to your bank]({redirect_url}).")
            else:
                st.warning("Your bank requires authentication to complete this payment.")
                
                # Mode indicator for test mode
                st.info("TEST MODE: This will use our simulated bank environment")
                
                # Add a button to start bank auth simulator in test mode
                if st.button("Click here to authenticate with your bank", type="primary", key="start_bank_auth"):
                    # Set session state for bank auth mode
                    st.session_state.in_bank_auth_mode = True
                    st.session_state.bank_auth_payment_id = payment_id
                    st.session_state.bank_auth_return_url = redirect_url
                    st.rerun()
                
            status_class = "pending"
        else:
            st.info(f"Payment Status: {status}")
            status_class = "pending"
        
        # Display payment details
        st.markdown(f"""
        <div class="payment-status {status_class}">
            <h3>Payment Details</h3>
            <p><strong>Payment ID:</strong> {payment_id}</p>
            <p><strong>Status:</strong> {status}</p>
            <p><strong>Amount:</strong> €{st.session_state.payment_amount/100:.2f}</p>
            <p><strong>Bank:</strong> {st.session_state.selected_bank}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Check status button (for demo/testing)
        if st.button("Check Payment Status"):
            if payment_id:
                with st.spinner("Checking payment status..."):
                    try:
                        updated_status = check_payment_status(payment_id)
                        st.session_state.payment_status = updated_status
                        st.success(f"Updated Status: {updated_status.get('status')}")
                        
                        if updated_status.get("is_success"):
                            st.balloons()
                    except Exception as e:
                        st.error(f"Error checking payment status: {str(e)}")
        
        # Start over button
        if st.button("Make Another Payment"):
            st.session_state.payment_flow_step = "select_bank"
            st.session_state.payment_intent = None
            st.session_state.payment_status = None
            st.rerun()

# Test function for direct execution
def test_ideal_payment_page():
    st.title("iDEAL Payment Test Page")
    
    # Mock user data
    username = "test_user"
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "stripe_customer_id": f"cus_{username}"
    }
    
    # Render the payment page
    render_ideal_payment_page(username, user_data)

# Direct execution
if __name__ == "__main__":
    test_ideal_payment_page()