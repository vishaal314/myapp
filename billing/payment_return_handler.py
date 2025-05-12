"""
Payment Return Handler

This module handles callbacks from external payment providers (like banks via iDEAL)
and ensures proper payment verification and status updates.
"""

import streamlit as st
import time
from urllib.parse import parse_qs, urlparse
from typing import Dict, Any, Optional, Tuple

from billing.stripe_integration import check_payment_status, _update_mock_payment_status

def parse_return_parameters() -> Dict[str, str]:
    """
    Parse URL parameters to extract payment information
    
    Returns:
        Dictionary with payment parameters
    """
    # Get query parameters
    query_params = st.experimental_get_query_params()
    
    # Extract common payment parameters
    params = {
        "payment_intent": query_params.get("payment_intent", [""])[0],
        "payment_intent_client_secret": query_params.get("payment_intent_client_secret", [""])[0],
        "redirect_status": query_params.get("redirect_status", [""])[0],
        "payment_success": query_params.get("payment_success", [""])[0],
        "payment_canceled": query_params.get("payment_canceled", [""])[0],
    }
    
    return params

def handle_payment_return() -> Tuple[bool, Dict[str, Any]]:
    """
    Handle a user returning from an external payment flow
    
    Returns:
        Tuple of (has_payment_return, payment_result)
    """
    # Parse URL parameters
    params = parse_return_parameters()
    
    # Check if we have relevant payment params
    has_payment_params = bool(
        params.get("payment_intent") or 
        params.get("payment_success") or 
        params.get("payment_canceled")
    )
    
    if not has_payment_params:
        return False, {}
    
    # Process payment verification
    payment_intent_id = params.get("payment_intent")
    redirect_status = params.get("redirect_status")
    payment_success = params.get("payment_success") == "true"
    payment_canceled = params.get("payment_canceled") == "true"
    
    # Initialize default status
    status = "unknown"
    payment_result = {
        "payment_intent_id": payment_intent_id,
        "status": status,
        "is_success": False,
        "is_canceled": False,
        "is_pending": True,
        "message": "Processing payment result..."
    }
    
    # Check direct success/canceled flags first (from our simulator)
    if payment_success:
        payment_result.update({
            "status": "succeeded",
            "is_success": True,
            "is_canceled": False,
            "is_pending": False,
            "message": "Payment was successful!"
        })
        
        # Update mock payment if there's a payment intent
        if payment_intent_id:
            _update_mock_payment_status(payment_intent_id, "succeeded")
            
    elif payment_canceled:
        payment_result.update({
            "status": "canceled",
            "is_success": False,
            "is_canceled": True,
            "is_pending": False,
            "message": "Payment was canceled."
        })
        
        # Update mock payment if there's a payment intent
        if payment_intent_id:
            _update_mock_payment_status(payment_intent_id, "canceled")
    
    # Check the payment status from Stripe if we have a payment intent
    elif payment_intent_id:
        try:
            # Check payment status (either real or mock)
            payment_status = check_payment_status(payment_intent_id)
            
            # Update result with payment status
            status = payment_status.get("status", "unknown")
            payment_result.update({
                "status": status,
                "is_success": payment_status.get("is_success", False),
                "is_canceled": payment_status.get("is_canceled", False),
                "is_pending": not (payment_status.get("is_success", False) or payment_status.get("is_canceled", False)),
                "message": f"Payment status: {status}"
            })
            
            # Provide more detailed messages based on status
            if status == "succeeded":
                payment_result["message"] = "Payment was successful!"
            elif status == "processing":
                payment_result["message"] = "Payment is being processed. Please check back later."
            elif status == "requires_action":
                payment_result["message"] = "Payment requires additional authentication."
            elif status == "canceled":
                payment_result["message"] = "Payment was canceled."
                
        except Exception as e:
            # Handle errors gracefully
            payment_result.update({
                "status": "error",
                "is_success": False, 
                "is_canceled": False,
                "is_pending": False,
                "message": f"Error checking payment status: {str(e)}"
            })
    
    # Return result
    return True, payment_result

def render_payment_return_page():
    """
    Render a dedicated page for users returning from external payment flows
    """
    st.title("Payment Verification")
    
    # Process the return parameters
    has_payment_return, payment_result = handle_payment_return()
    
    if not has_payment_return:
        st.info("No payment information detected.")
        return
    
    # Show a spinner while verifying payment
    with st.spinner("Verifying payment status..."):
        # Simulate a delay for better UX
        time.sleep(1.5)
        
        # Display the payment result
        if payment_result.get("is_success"):
            st.success(payment_result.get("message", "Payment successful!"))
            st.balloons()
        elif payment_result.get("is_canceled"):
            st.warning(payment_result.get("message", "Payment canceled."))
        elif payment_result.get("is_pending"):
            st.info(payment_result.get("message", "Payment is being processed."))
        else:
            st.error(payment_result.get("message", "Payment failed."))
    
    # Payment details
    payment_id = payment_result.get("payment_intent_id")
    status = payment_result.get("status")
    
    if payment_id:
        st.subheader("Payment Details")
        st.write(f"Payment ID: {payment_id}")
        st.write(f"Status: {status}")
    
    # Provide navigation options
    st.subheader("What would you like to do next?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Return to Dashboard", type="primary"):
            # Clear query parameters by redirecting
            st.experimental_set_query_params()
            st.rerun()
            
    with col2:
        if st.button("Make Another Payment"):
            # Navigate to payment page
            st.session_state.payment_flow_step = "select_bank"
            st.session_state.payment_intent = None
            st.session_state.payment_status = None
            st.session_state.in_bank_auth_mode = False
            
            # Clear query parameters by redirecting
            st.experimental_set_query_params()
            st.rerun()