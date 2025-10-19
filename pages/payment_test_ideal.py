"""
iDEAL Payment Testing - DataGuardian Pro
Test real ABN AMRO card payments with iDEAL integration
"""

import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.stripe_payment import create_checkout_session, handle_payment_callback
from services.results_aggregator import ResultsAggregator

# Initialize results aggregator
results_aggregator = ResultsAggregator()

# Page configuration
st.set_page_config(
    page_title="iDEAL Payment Testing - DataGuardian Pro",
    page_icon="💳",
    layout="wide"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .ideal-header {
        background: linear-gradient(135deg, #FF6B00 0%, #FF8C00 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .test-config-box {
        background: #f8f9fa;
        border-left: 4px solid #0066CC;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .ideal-info-box {
        background: #e7f5e7;
        border-left: 4px solid #28a745;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .scanner-option {
        padding: 0.8rem;
        border: 1px solid #dee2e6;
        border-radius: 6px;
        margin: 0.5rem 0;
        background: white;
    }
    .price-badge {
        background: #28a745;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Handle payment callback first
handle_payment_callback(results_aggregator)

# Header
st.markdown("""
<div class="ideal-header">
    <h1>💳 iDEAL Payment Testing - DataGuardian Pro</h1>
    <p style="font-size: 1.2rem; margin-top: 1rem;">Test real ABN AMRO card payments with iDEAL integration</p>
</div>
""", unsafe_allow_html=True)

# Create two columns layout
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### ✏️ Test Configuration")
    
    # Email input
    st.markdown('<div class="test-config-box">', unsafe_allow_html=True)
    user_email = st.text_input(
        "Your Email (for payment receipt):",
        value="test@example.com",
        help="Enter your email to receive payment confirmation"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Scanner type dropdown with pricing (all scanner types from platform)
    st.markdown("**Select Scanner to Test:**")
    
    # Complete scanner pricing (base prices in EUR, VAT 21% for Netherlands)
    # Matching SCAN_PRICES from services/stripe_payment.py
    scanner_options = {
        # Basic Scanners
        "Manual Upload": {"base": 9.00, "vat": 1.89, "total": 10.89, "category": "Basic"},
        "API Scan": {"base": 18.00, "vat": 3.78, "total": 21.78, "category": "Basic"},
        "Code Scan": {"base": 23.00, "vat": 4.83, "total": 27.83, "category": "Basic"},
        "Website Scan": {"base": 25.00, "vat": 5.25, "total": 30.25, "category": "Basic"},
        "Image Scan": {"base": 28.00, "vat": 5.88, "total": 33.88, "category": "Basic"},
        "DPIA Scan": {"base": 38.00, "vat": 7.98, "total": 45.98, "category": "Basic"},
        "Database Scan": {"base": 46.00, "vat": 9.66, "total": 55.66, "category": "Basic"},
        
        # Advanced Scanners
        "Sustainability Scan": {"base": 32.00, "vat": 6.72, "total": 38.72, "category": "Advanced"},
        "AI Model Scan": {"base": 41.00, "vat": 8.61, "total": 49.61, "category": "Advanced"},
        "SOC2 Scan": {"base": 55.00, "vat": 11.55, "total": 66.55, "category": "Advanced"},
        
        # Enterprise Connectors
        "Google Workspace Scan": {"base": 68.00, "vat": 14.28, "total": 82.28, "category": "Enterprise"},
        "Microsoft 365 Scan": {"base": 75.00, "vat": 15.75, "total": 90.75, "category": "Enterprise"},
        "Enterprise Scan": {"base": 89.00, "vat": 18.69, "total": 107.69, "category": "Enterprise"},
        "Salesforce Scan": {"base": 92.00, "vat": 19.32, "total": 111.32, "category": "Enterprise"},
        "Exact Online Scan": {"base": 125.00, "vat": 26.25, "total": 151.25, "category": "Enterprise"},
        "SAP Integration Scan": {"base": 150.00, "vat": 31.50, "total": 181.50, "category": "Enterprise"},
    }
    
    # Create dropdown options with prices (grouped by category)
    scanner_display_options = []
    
    # Group by category
    basic_scanners = {k: v for k, v in scanner_options.items() if v['category'] == 'Basic'}
    advanced_scanners = {k: v for k, v in scanner_options.items() if v['category'] == 'Advanced'}
    enterprise_scanners = {k: v for k, v in scanner_options.items() if v['category'] == 'Enterprise'}
    
    # Add category headers and scanners
    for scanner, pricing in basic_scanners.items():
        scanner_display_options.append(f"{scanner} - €{pricing['base']:.2f} + €{pricing['vat']:.2f} VAT = €{pricing['total']:.2f}")
    
    for scanner, pricing in advanced_scanners.items():
        scanner_display_options.append(f"{scanner} - €{pricing['base']:.2f} + €{pricing['vat']:.2f} VAT = €{pricing['total']:.2f}")
    
    for scanner, pricing in enterprise_scanners.items():
        scanner_display_options.append(f"{scanner} - €{pricing['base']:.2f} + €{pricing['vat']:.2f} VAT = €{pricing['total']:.2f}")
    
    selected_scanner_display = st.selectbox(
        "Choose scan type:",
        scanner_display_options,
        key="scanner_select"
    )
    
    # Extract scanner type from selection
    selected_scanner = selected_scanner_display.split(" - ")[0]
    selected_pricing = scanner_options[selected_scanner]
    
    # Display selected scanner details
    st.markdown(f"""
    <div class="scanner-option">
        <strong>{selected_scanner}</strong><br>
        Base: €{selected_pricing['base']:.2f} | VAT (21%): €{selected_pricing['vat']:.2f} | 
        <span class="price-badge">Total: €{selected_pricing['total']:.2f}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Country selector (default to NL for iDEAL)
    country_code = "NL"
    st.info("🇳🇱 **Country: Netherlands** (iDEAL enabled)")
    
    # Create checkout session button
    st.markdown("---")
    if st.button("🚀 Create Checkout Session", type="primary", use_container_width=True):
        if not user_email:
            st.error("Please enter your email address")
        else:
            with st.spinner("Creating Stripe checkout session..."):
                try:
                    # Create checkout session
                    session_data = create_checkout_session(
                        scan_type=selected_scanner,
                        user_email=user_email,
                        country_code=country_code
                    )
                    
                    if session_data and "url" in session_data:
                        st.success(f"✅ Checkout session created! ID: {session_data['id']}")
                        st.markdown(f"**[Click here to pay with iDEAL or Card →]({session_data['url']})**")
                        
                        # Show redirect info
                        st.info("""
                        💡 **Next Steps:**
                        1. Click the payment link above
                        2. Choose iDEAL or Card payment method
                        3. Complete the payment
                        4. You'll be redirected back automatically
                        5. **You'll stay logged in** - no re-login needed!
                        """)
                    else:
                        st.error("Failed to create checkout session. Please check your Stripe configuration.")
                        
                except Exception as e:
                    st.error(f"Error creating checkout session: {str(e)}")

with col2:
    st.markdown("### 💳 iDEAL Payment Info")
    
    # iDEAL status
    st.markdown("""
    <div class="ideal-info-box">
        <h4>✅ iDEAL payments enabled for Netherlands</h4>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("**Available Payment Methods:**")
    st.markdown("""
    - 💳 **Credit/Debit Cards** (Visa, Mastercard)
    - 🏦 **iDEAL** (all Dutch banks including ABN AMRO)
    """)
    
    st.markdown("---")
    st.markdown("**iDEAL Banks Supported:**")
    
    ideal_banks = [
        "ABN AMRO",
        "ING Bank",
        "Rabobank",
        "SNS Bank",
        "ASN Bank",
        "Bunq",
        "Knab",
        "Revolut",
        "Triodos Bank"
    ]
    
    for bank in ideal_banks:
        st.markdown(f"• {bank}")
    
    st.markdown("---")
    st.markdown("### 🧪 Test Card Details")
    
    st.code("""
Test Card (International):
Card: 4242 4242 4242 4242
Expiry: 12/25 (any future date)
CVV: 123 (any 3 digits)
    """)
    
    st.markdown("""
    <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
        <strong>⚡ iDEAL Test Mode:</strong><br>
        In Stripe test mode, iDEAL payments are simulated. Choose "Test Mode" when selecting your bank to complete the payment instantly.
    </div>
    """, unsafe_allow_html=True)

# Payment status section
st.markdown("---")
st.markdown("### 📊 Payment Status")

if st.session_state.get("payment_successful"):
    st.success("🎉 Payment Successful!")
    
    payment_details = st.session_state.get("payment_details", {})
    if payment_details:
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            st.metric("Amount", f"€{payment_details.get('amount', '0.00')}")
        
        with col_b:
            st.metric("Payment Method", payment_details.get("payment_method", "Unknown").upper())
        
        with col_c:
            st.metric("Scanner Type", payment_details.get("scan_type", "Unknown"))
        
        st.json(payment_details)
        
        # Test another payment button
        if st.button("🔄 Test Another Payment", type="secondary"):
            st.session_state.payment_successful = False
            st.session_state.payment_details = {}
            st.rerun()

elif st.session_state.get("payment_cancelled"):
    st.warning("⚠️ Payment was cancelled")
    
    if st.button("🔄 Try Again"):
        st.session_state.payment_cancelled = False
        st.rerun()

# Footer with instructions
st.markdown("---")
st.markdown("""
### 📝 Testing Instructions

**1. Test Card Payment:**
- Select a scanner type
- Click "Create Checkout Session"
- Choose "Card" payment method
- Use test card: `4242 4242 4242 4242`
- Complete payment

**2. Test iDEAL Payment:**
- Select a scanner type
- Click "Create Checkout Session"  
- Choose "iDEAL" payment method
- Select any Dutch bank
- Click "Test Mode" to simulate payment
- Complete payment instantly

**3. Verify Results:**
- ✅ You're redirected back to this page
- ✅ You stay logged in (no re-login!)
- ✅ Payment confirmation shown
- ✅ Payment recorded in database
- ✅ Ready to test another payment

**Expected Behavior:**
- **Session Persistence:** You won't need to log in again after payment
- **Instant Feedback:** Payment status shown immediately
- **Multiple Tests:** Can test multiple payments in succession
- **Webhook Delivery:** Stripe webhooks are logged (check Stripe Dashboard)
""")

# Debug info (only for development)
if st.checkbox("🔧 Show Debug Info"):
    st.markdown("### Debug Information")
    st.write("Session State:", st.session_state)
    
    # Show environment check
    import os
    env_status = {
        "STRIPE_SECRET_KEY": "✅ Set" if os.getenv("STRIPE_SECRET_KEY") else "❌ Missing",
        "STRIPE_WEBHOOK_SECRET": "✅ Set" if os.getenv("STRIPE_WEBHOOK_SECRET") else "❌ Missing",
        "REPLIT_DEV_DOMAIN": os.getenv("REPLIT_DEV_DOMAIN", "Not set")
    }
    st.json(env_status)
