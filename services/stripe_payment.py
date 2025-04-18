import os
import stripe
import streamlit as st
from typing import Dict, Any, Optional

# Initialize Stripe with secret key from environment
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Pricing for each scan type (in cents)
SCAN_PRICES = {
    "Code Scan": 2500,  # $25.00
    "Blob Scan": 1500,  # $15.00
    "Image Scan": 3000,  # $30.00
    "Database Scan": 5000,  # $50.00
    "API Scan": 2000,  # $20.00
    "Manual Upload": 1000,  # $10.00
    "Sustainability Scan": 3500,  # $35.00
    "AI Model Scan": 4500,  # $45.00
    "SOC2 Scan": 6000,  # $60.00
}

# Product names for each scan type
SCAN_PRODUCTS = {
    "Code Scan": "DataGuardian Pro Code Scanner",
    "Blob Scan": "DataGuardian Pro Blob Scanner",
    "Image Scan": "DataGuardian Pro Image Scanner",
    "Database Scan": "DataGuardian Pro Database Scanner",
    "API Scan": "DataGuardian Pro API Scanner",
    "Manual Upload": "DataGuardian Pro Manual Upload Scanner",
    "Sustainability Scan": "DataGuardian Pro Sustainability Scanner",
    "AI Model Scan": "DataGuardian Pro AI Model Scanner",
    "SOC2 Scan": "DataGuardian Pro SOC2 Scanner",
}

# Descriptions for each scan type
SCAN_DESCRIPTIONS = {
    "Code Scan": "Comprehensive code scanning for PII and secrets detection",
    "Blob Scan": "Document scanning for PII and sensitive information",
    "Image Scan": "Image scanning for faces and visual identifiers",
    "Database Scan": "Database scanning for GDPR compliance",
    "API Scan": "API scanning for data exposure and compliance issues",
    "Manual Upload": "Manual file scanning for PII detection",
    "Sustainability Scan": "Cloud resource optimization and sustainability analysis",
    "AI Model Scan": "AI model auditing for bias and GDPR compliance",
    "SOC2 Scan": "SOC2 security and access control auditing",
}

def create_checkout_session(scan_type: str, user_email: str, metadata: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
    """
    Create a Stripe checkout session for a given scan type
    
    Args:
        scan_type: The type of scan to create a checkout session for
        user_email: Email of the user making the payment
        metadata: Additional metadata to attach to the checkout session
        
    Returns:
        Dictionary containing checkout session details if successful, None otherwise
    """
    if scan_type not in SCAN_PRICES:
        st.error(f"Unknown scan type: {scan_type}")
        return None
    
    try:
        # Combine provided metadata with default metadata
        full_metadata = {
            "scan_type": scan_type,
            "user_email": user_email
        }
        if metadata:
            full_metadata.update(metadata)
            
        # Create a checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": SCAN_PRODUCTS[scan_type],
                            "description": SCAN_DESCRIPTIONS[scan_type],
                        },
                        "unit_amount": SCAN_PRICES[scan_type],
                    },
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url=f"{get_base_url()}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{get_base_url()}/cancel",
            customer_email=user_email,
            metadata=full_metadata,
        )
        
        return {
            "id": checkout_session.id,
            "url": checkout_session.url,
            "amount": SCAN_PRICES[scan_type] / 100  # Convert to dollars for display
        }
    
    except Exception as e:
        st.error(f"Error creating checkout session: {str(e)}")
        return None

def verify_payment(session_id: str) -> Dict[str, Any]:
    """
    Verify a payment based on a checkout session ID
    
    Args:
        session_id: The checkout session ID to verify
        
    Returns:
        Dictionary containing payment details
    """
    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        payment_intent = stripe.PaymentIntent.retrieve(checkout_session.payment_intent)
        
        return {
            "status": payment_intent.status,
            "amount": payment_intent.amount / 100,  # Convert to dollars
            "scan_type": checkout_session.metadata.get("scan_type"),
            "user_email": checkout_session.metadata.get("user_email"),
            "payment_method": payment_intent.payment_method_types[0] if payment_intent.payment_method_types else None,
            "timestamp": payment_intent.created,
            "currency": payment_intent.currency
        }
    except Exception as e:
        st.error(f"Error verifying payment: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

def get_base_url() -> str:
    """Get the base URL for Streamlit app"""
    # For deployment, would use a proper domain
    # For local development, using localhost
    return "http://localhost:5000"

def display_payment_button(scan_type: str, user_email: str, metadata: Dict[str, Any] = None) -> Optional[str]:
    """
    Display a payment button for a scan type and handle the checkout process
    
    Args:
        scan_type: The type of scan to create a checkout session for
        user_email: Email of the user making the payment
        metadata: Additional metadata to attach to the checkout session
        
    Returns:
        Session ID if checkout was created successfully, None otherwise
    """
    # Get price for scan type
    if scan_type not in SCAN_PRICES:
        st.error(f"Unknown scan type: {scan_type}")
        return None
    
    price = SCAN_PRICES[scan_type] / 100  # Convert to dollars
    
    # Display payment information
    st.info(f"Scanning service: **{SCAN_PRODUCTS[scan_type]}**  \nPrice: **${price:.2f}**")
    
    # Create payment button
    if st.button(f"Proceed with payment (${price:.2f})"):
        checkout_session = create_checkout_session(scan_type, user_email, metadata)
        
        if checkout_session:
            # Store checkout session ID in session state
            st.session_state.checkout_session_id = checkout_session["id"]
            
            # Display checkout link
            st.markdown(f"[Click here to complete your payment](${checkout_session['url']})")
            
            # Also provide a direct JavaScript redirect option
            js_redirect = f"""
            <script>
                window.open("{checkout_session['url']}", "_blank");
            </script>
            """
            st.components.v1.html(js_redirect, height=0)
            
            return checkout_session["id"]
    
    return None

def handle_payment_callback(results_aggregator) -> None:
    """
    Handle payment success and cancellation callbacks
    
    Args:
        results_aggregator: ResultsAggregator instance to log audit events
    """
    # Check for session_id in URL parameters - Streamlit 1.20.0+ uses query_params()
    query_params = st.query_params
    
    session_id = query_params.get("session_id", None)
    
    if session_id:
        # Verify payment
        payment_details = verify_payment(session_id)
        
        if payment_details["status"] == "succeeded":
            st.success(f"Payment of ${payment_details['amount']:.2f} successful for {payment_details['scan_type']}!")
            
            # Log the payment success audit event
            try:
                results_aggregator.log_audit_event(
                    username=st.session_state.get("username", "guest"),
                    action="PAYMENT_COMPLETED",
                    details={
                        "scan_type": payment_details["scan_type"],
                        "amount": payment_details["amount"],
                        "user_email": payment_details["user_email"],
                        "payment_method": payment_details["payment_method"],
                        "timestamp": payment_details["timestamp"]
                    }
                )
            except Exception as e:
                st.warning(f"Audit logging failed: {str(e)}")
            
            # Store payment details in session state
            st.session_state.payment_successful = True
            st.session_state.payment_details = payment_details
            
            # Clear the session ID from URL to prevent reprocessing
            st.query_params.clear()
        else:
            st.error(f"Payment failed with status: {payment_details['status']}")
            
            # Log the payment failure audit event
            try:
                results_aggregator.log_audit_event(
                    username=st.session_state.get("username", "guest"),
                    action="PAYMENT_FAILED",
                    details={
                        "status": payment_details["status"],
                        "session_id": session_id,
                        "error": payment_details.get("error", "Unknown error")
                    }
                )
            except Exception as e:
                st.warning(f"Audit logging failed: {str(e)}")
            
            # Clear the session ID from URL to prevent reprocessing
            st.query_params.clear()