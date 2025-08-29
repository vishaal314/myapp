import os
import stripe
import streamlit as st
import re
from typing import Dict, Any, Optional

# Initialize Stripe with proper validation
def initialize_stripe():
    """Initialize Stripe with proper error handling"""
    secret_key = os.getenv('STRIPE_SECRET_KEY')
    if not secret_key:
        raise ValueError("STRIPE_SECRET_KEY environment variable not set")
    
    stripe.api_key = secret_key
    return True

# Initialize on import
try:
    initialize_stripe()
except ValueError as e:
    st.error(f"Payment system configuration error: {e}")
    stripe.api_key = None

# Pricing for each scan type (in cents EUR)
SCAN_PRICES = {
    "Code Scan": 2300,  # €23.00
    "Blob Scan": 1400,  # €14.00
    "Image Scan": 2800,  # €28.00
    "Database Scan": 4600,  # €46.00
    "API Scan": 1800,  # €18.00
    "Manual Upload": 900,  # €9.00
    "Sustainability Scan": 3200,  # €32.00
    "AI Model Scan": 4100,  # €41.00
    "SOC2 Scan": 5500,  # €55.00
    "Enterprise Scan": 8900,  # €89.00
    "Exact Online Scan": 12500,  # €125.00
    "SAP Integration Scan": 15000,  # €150.00
    "Microsoft 365 Scan": 7500,  # €75.00
    "Google Workspace Scan": 6800,  # €68.00
    "Salesforce Scan": 9200,  # €92.00
}

# VAT rates by country
VAT_RATES = {
    "NL": 0.21,  # Netherlands 21%
    "DE": 0.19,  # Germany 19%
    "FR": 0.20,  # France 20%
    "BE": 0.21,  # Belgium 21%
    "default": 0.21  # Default to Netherlands rate
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
    "Enterprise Scan": "DataGuardian Pro Enterprise Scanner",
    "Exact Online Scan": "DataGuardian Pro Exact Online Connector",
    "SAP Integration Scan": "DataGuardian Pro SAP Integration Scanner",
    "Microsoft 365 Scan": "DataGuardian Pro Microsoft 365 Scanner",
    "Google Workspace Scan": "DataGuardian Pro Google Workspace Scanner",
    "Salesforce Scan": "DataGuardian Pro Salesforce Scanner",
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
    "Enterprise Scan": "Advanced enterprise data scanning with full connector suite",
    "Exact Online Scan": "Direct integration scanning for Exact Online accounting data",
    "SAP Integration Scan": "SAP ERP system integration with GDPR compliance analysis",
    "Microsoft 365 Scan": "Microsoft 365 tenant scanning for PII and compliance issues",
    "Google Workspace Scan": "Google Workspace organization scanning for data exposure",
    "Salesforce Scan": "Salesforce CRM data scanning for customer privacy compliance",
}

# Security and validation functions
def validate_email(email: str) -> bool:
    """Validate email format with security checks"""
    if not email or len(email) > 254:
        return False
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))

def validate_scan_type(scan_type: str) -> bool:
    """Validate scan type against allowed values"""
    return scan_type in SCAN_PRICES

def sanitize_metadata(metadata: Dict[str, Any]) -> Dict[str, str]:
    """Sanitize metadata to prevent injection attacks"""
    if not metadata:
        return {}
    
    sanitized = {}
    for key, value in metadata.items():
        # Only allow alphanumeric keys and string values
        if isinstance(key, str) and key.replace('_', '').isalnum():
            if isinstance(value, (str, int, float, bool)):
                sanitized[key] = str(value)[:100]  # Limit length
    return sanitized

def calculate_vat(amount: int, country_code: str = "NL") -> dict:
    """Calculate VAT for EU countries"""
    vat_rate = VAT_RATES.get(country_code.upper(), VAT_RATES["default"])
    vat_amount = int(amount * vat_rate)
    
    return {
        "subtotal": amount,
        "vat_rate": vat_rate,
        "vat_amount": vat_amount,
        "total": amount + vat_amount,
        "currency": "eur"
    }

def get_base_url() -> str:
    """Get secure base URL from environment"""
    base_url = os.getenv('BASE_URL', os.getenv('REPLIT_URL'))
    
    if not base_url:
        # Fallback for development
        port = os.getenv('PORT', '5000')
        base_url = f"http://localhost:{port}"
    
    return base_url.rstrip('/')

def verify_webhook_signature(payload: str, signature: str) -> bool:
    """Verify Stripe webhook signature for security"""
    endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    if not endpoint_secret:
        st.warning("Webhook secret not configured - payments may not be verified")
        return False
    
    try:
        stripe.Webhook.construct_event(payload, signature, endpoint_secret)
        return True
    except stripe.SignatureVerificationError:
        st.error("Invalid webhook signature")
        return False
    except Exception as e:
        st.error(f"Webhook verification failed: {str(e)}")
        return False

def create_checkout_session(scan_type: str, user_email: str, metadata: Optional[Dict[str, Any]] = None, country_code: str = "NL") -> Optional[Dict[str, Any]]:
    """
    Create a secure Stripe checkout session with VAT calculation
    
    Args:
        scan_type: The type of scan to create a checkout session for
        user_email: Email of the user making the payment
        metadata: Additional metadata to attach to the checkout session
        country_code: Country code for VAT calculation (default: NL)
        
    Returns:
        Dictionary containing checkout session details if successful, None otherwise
    """
    # Input validation
    if not validate_scan_type(scan_type):
        st.error("Invalid scan type selected")
        return None
    
    if not validate_email(user_email):
        st.error("Please provide a valid email address")
        return None
    
    if not stripe.api_key:
        st.error("Payment system not properly configured")
        return None
    
    try:
        # Calculate pricing with VAT
        base_price = SCAN_PRICES[scan_type]
        pricing = calculate_vat(base_price, country_code)
        
        # Sanitize metadata
        safe_metadata = sanitize_metadata(metadata or {})
        safe_metadata.update({
            "scan_type": scan_type,
            "user_email": user_email,
            "country_code": country_code,
            "vat_rate": str(pricing["vat_rate"])
        })
        
        # Payment methods including iDEAL for Netherlands
        from typing import cast, Any
        payment_methods: Any = ["card"]
        if country_code.upper() == "NL":
            payment_methods.append("ideal")
        
        # Create a checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=payment_methods,
            line_items=[
                {
                    "price_data": {
                        "currency": "eur",
                        "product_data": {
                            "name": SCAN_PRODUCTS[scan_type],
                            "description": SCAN_DESCRIPTIONS[scan_type],
                        },
                        "unit_amount": pricing["total"],
                    },
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url=f"{get_base_url()}?session_id={{CHECKOUT_SESSION_ID}}&payment_success=true",
            cancel_url=f"{get_base_url()}?payment_cancelled=true",
            customer_email=user_email,
            metadata=safe_metadata,
            automatic_tax={
                "enabled": True,
            },
        )
        
        return {
            "id": checkout_session.id,
            "url": checkout_session.url,
            "amount": pricing["total"] / 100,
            "subtotal": pricing["subtotal"] / 100,
            "vat": pricing["vat_amount"] / 100,
            "currency": "EUR"
        }
    
    except stripe.StripeError as e:
        st.error("Payment service temporarily unavailable. Please try again later.")
        return None
    except Exception as e:
        st.error("An unexpected error occurred. Please contact support.")
        return None

def verify_payment(session_id: str) -> Dict[str, Any]:
    """
    Verify a payment based on a checkout session ID with security checks
    
    Args:
        session_id: The checkout session ID to verify
        
    Returns:
        Dictionary containing payment details
    """
    if not session_id or not isinstance(session_id, str):
        return {"status": "error", "error": "Invalid session ID"}
    
    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        
        # Check if payment_intent exists and is not None
        if not checkout_session.payment_intent:
            return {"status": "error", "error": "No payment intent found"}
        
        # Handle payment intent ID extraction safely
        payment_intent_obj = checkout_session.payment_intent
        if hasattr(payment_intent_obj, 'id'):
            # If it's a PaymentIntent object, get the ID
            payment_intent_id = str(getattr(payment_intent_obj, 'id', ''))
        else:
            # If it's already a string ID, use it directly
            payment_intent_id = str(payment_intent_obj)
            
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        # Safely extract metadata
        metadata = checkout_session.metadata or {}
        
        return {
            "status": payment_intent.status,
            "amount": payment_intent.amount / 100,  # Convert to euros
            "scan_type": metadata.get("scan_type"),
            "user_email": metadata.get("user_email"),
            "payment_method": payment_intent.payment_method_types[0] if payment_intent.payment_method_types else None,
            "timestamp": payment_intent.created,
            "currency": payment_intent.currency,
            "country_code": metadata.get("country_code", "NL"),
            "vat_rate": metadata.get("vat_rate")
        }
    except stripe.StripeError as e:
        return {"status": "error", "error": "Payment verification failed"}
    except Exception as e:
        return {"status": "error", "error": "Verification service temporarily unavailable"}

def display_payment_button(scan_type: str, user_email: str, metadata: Optional[Dict[str, Any]] = None, country_code: str = "NL") -> Optional[str]:
    """
    Display a secure payment button with VAT breakdown
    
    Args:
        scan_type: The type of scan to create a checkout session for
        user_email: Email of the user making the payment
        metadata: Additional metadata to attach to the checkout session
        country_code: Country code for VAT calculation
        
    Returns:
        Session ID if checkout was created successfully, None otherwise
    """
    # Validate inputs
    if not validate_scan_type(scan_type):
        st.error("Invalid scan type selected")
        return None
    
    if not validate_email(user_email):
        st.error("Please provide a valid email address")
        return None
    
    # Calculate pricing with VAT
    base_price = SCAN_PRICES[scan_type]
    pricing = calculate_vat(base_price, country_code)
    
    # Display payment information with VAT breakdown
    st.markdown(f"""
    ### 🔒 Secure Payment
    
    **Service:** {SCAN_PRODUCTS[scan_type]}  
    **Description:** {SCAN_DESCRIPTIONS[scan_type]}
    
    **Pricing Breakdown:**
    - Subtotal: €{pricing['subtotal']/100:.2f}
    - VAT ({pricing['vat_rate']*100:.0f}%): €{pricing['vat_amount']/100:.2f}
    - **Total: €{pricing['total']/100:.2f}**
    
    💳 Payment methods: Credit Card{', iDEAL' if country_code.upper() == 'NL' else ''}
    """)
    
    # Create secure payment button
    if st.button(f"🔒 Proceed to Secure Payment (€{pricing['total']/100:.2f})", type="primary"):
        checkout_session = create_checkout_session(scan_type, user_email, metadata, country_code)
        
        if checkout_session:
            # Store checkout session ID in session state
            st.session_state.checkout_session_id = checkout_session["id"]
            
            # Display secure payment link (no JavaScript injection)
            st.markdown(f"""
            ### 🔒 Complete Your Payment
            
            Your secure payment session has been created. Click the button below to complete your payment:
            
            <a href="{checkout_session['url']}" target="_blank" 
               style="display: inline-block; padding: 12px 24px; 
                      background: #28a745; color: white; text-decoration: none; 
                      border-radius: 6px; font-weight: bold; margin: 10px 0;">
                🔒 Complete Payment Securely →
            </a>
            
            <p style="font-size: 12px; color: #666; margin-top: 10px;">
                ✅ Secured by Stripe • 🔒 SSL Encrypted • 🇪🇺 GDPR Compliant
            </p>
            """, unsafe_allow_html=True)
            
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