"""
Pricing Display Component for DataGuardian Pro
Clean, responsive pricing interface with competitive advantages
"""

import streamlit as st
from typing import Dict, Any, Optional, List
from config.pricing_config import get_pricing_config, PricingTier, BillingCycle
from services.license_integration import LicenseIntegration

def show_pricing_page():
    """Display the main pricing page"""
    # Import i18n for translations
    from utils.i18n import _
    
    # Header section
    st.title(f"💰 {_('pricing.title', 'DataGuardian Pro Pricing')}")
    st.markdown(f"""
    **{_('pricing.subtitle', 'Enterprise-grade privacy compliance at breakthrough prices')}**  
    {_('pricing.description', 'Save 85-90% vs OneTrust, BigID, and Varonis while getting Netherlands-specialized features')}
    """)
    
    # Billing toggle with translations
    from utils.i18n import _
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        billing_cycle = st.radio(
            "Select billing:",
            [_('pricing.billing_monthly', 'Monthly'), _('pricing.billing_annual', 'Annual (Save 2 months)')],
            horizontal=True,
            key="billing_toggle"
        )
    
    billing = BillingCycle.ANNUAL if "Annual" in billing_cycle else BillingCycle.MONTHLY
    
    # Main pricing cards
    show_pricing_cards(billing)
    
    # Competitive comparison
    show_competitive_comparison()
    
    # Features comparison table
    show_features_comparison()
    
    # Contact section
    show_contact_section()

def show_pricing_cards(billing_cycle: BillingCycle):
    """Display pricing cards for all tiers"""
    config = get_pricing_config()
    license_integration = LicenseIntegration()
    current_tier = license_integration.get_current_pricing_tier()
    
    st.markdown("## Choose Your Plan")
    
    # Standard tiers
    cols = st.columns(4)
    tiers = [PricingTier.STARTUP, PricingTier.GROWTH, PricingTier.SCALE, PricingTier.ENTERPRISE]
    
    for i, tier in enumerate(tiers):
        with cols[i]:
            pricing = config.get_tier_pricing(tier, billing_cycle)
            tier_data = config.pricing_data["tiers"][tier.value]
            
            # Card styling
            is_current = (current_tier == tier) if current_tier else False
            is_popular = tier_data.get("most_popular", False)
            
            if is_popular:
                st.markdown("🔥 **MOST POPULAR**")
            elif is_current:
                st.markdown("✅ **CURRENT PLAN**")
            
            # Pricing header
            st.markdown(f"### {pricing['name']}")
            
            if billing_cycle == BillingCycle.ANNUAL:
                st.markdown(f"**€{pricing['price']:,}/year**")
                st.markdown(f"*€{tier_data['monthly_price']}/month billed annually*")
                if 'savings' in pricing:
                    st.success(f"💰 Save €{pricing['savings']:,} vs monthly")
            else:
                st.markdown(f"**€{pricing['price']:,}/month**")
            
            # Target info
            st.markdown(f"**For {tier_data['target_employees']} employees**")
            st.markdown(f"*{tier_data['target_revenue']}*")
            
            # Key features (top 4)
            st.markdown("**Key Features:**")
            key_features = get_tier_key_features(tier)
            for feature in key_features[:4]:
                st.markdown(f"✅ {feature}")
            
            # Limits
            st.markdown(f"📊 {tier_data.get('max_scans_monthly', 'Unlimited')} scans/month")
            st.markdown(f"🔌 {tier_data.get('max_data_sources', 'Unlimited')} data sources")
            
            # CTA button
            button_text = "Current Plan" if is_current else f"Select {tier.value.title()}"
            button_disabled = is_current
            button_type = "secondary" if is_current else ("primary" if is_popular else "secondary")
            
            if st.button(button_text, key=f"select_{tier.value}", disabled=button_disabled, type=button_type):
                handle_tier_selection(tier, billing_cycle)
    
    # Government/Enterprise license
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🏛️ Government & Enterprise License")
        st.markdown("**€15,000** one-time license")
        st.markdown("**€2,500/year** maintenance")
        st.markdown("**Features:**")
        st.markdown("✅ On-premises deployment")
        st.markdown("✅ Source code access")
        st.markdown("✅ Custom development")
        st.markdown("✅ Government compliance")
        st.markdown("✅ Unlimited everything")
    
    with col2:
        st.markdown("**Perfect for:**")
        st.markdown("• Government agencies")
        st.markdown("• Large enterprises (500+ employees)")
        st.markdown("• Organizations requiring on-premises")
        st.markdown("• Custom compliance requirements")
        
        if st.button("📞 Contact Sales", key="contact_government", type="primary"):
            st.session_state['contact_sales'] = True
            st.rerun()

def get_tier_key_features(tier: PricingTier) -> List[str]:
    """Get user-friendly key features for a tier"""
    feature_mapping = {
        PricingTier.STARTUP: [
            "Basic PII scanning",
            "GDPR compliance reports", 
            "Netherlands BSN detection",
            "Email support"
        ],
        PricingTier.GROWTH: [
            "Enterprise data connectors",
            "Microsoft 365 integration",
            "Exact Online connector",
            "Compliance certificates",
            "Priority support"
        ],
        PricingTier.SCALE: [
            "Advanced AI scanning",
            "EU AI Act compliance",
            "Custom integrations",
            "DPIA automation",
            "Dedicated support manager"
        ],
        PricingTier.ENTERPRISE: [
            "White-label deployment",
            "API access",
            "Custom development",
            "24/7 support",
            "Unlimited everything"
        ]
    }
    
    return feature_mapping.get(tier, [])

def show_competitive_comparison():
    """Show competitive pricing comparison"""
    st.markdown("## 💡 Why DataGuardian Pro?")
    st.markdown("**Save 85-90% compared to international competitors**")
    
    config = get_pricing_config()
    
    # Comparison table
    comparison_data = []
    tiers = [PricingTier.GROWTH, PricingTier.SCALE, PricingTier.ENTERPRISE]
    
    for tier in tiers:
        comparison = config.get_competitive_comparison(tier)
        for comp in comparison["comparisons"]:
            comparison_data.append({
                "Our Plan": f"{tier.value.title()} - €{comparison['our_annual_price']:,}",
                "Competitor": comp['competitor'],
                "Competitor Price": f"€{comp['competitor_cost']:,}",
                "Your Savings": f"€{comp['savings']:,}",
                "Savings %": f"{comp['savings_percentage']}%"
            })
    
    if comparison_data:
        st.table(comparison_data)
    
    # Unique advantages
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### 🇳🇱 {_('pricing.netherlands_specialization', 'Netherlands Specialization')}")
        st.markdown(f"• {_('pricing.bsn_detection', 'BSN (Dutch Social Security) detection')}")
        st.markdown(f"• {_('pricing.kvk_validation', 'KvK number validation')}")
        st.markdown(f"• {_('pricing.uavg_compliance', 'UAVG compliance rules')}")
        st.markdown(f"• {_('pricing.dutch_ap_integration', 'Dutch AP authority integration')}")
        st.markdown(f"• {_('pricing.dutch_language', 'Native Dutch language support')}")
    
    with col2:
        st.markdown("### 🚀 Unique Features")
        st.markdown("• Only solution with Exact Online connector")
        st.markdown("• 60% of Dutch SMEs use Exact Online")
        st.markdown("• EU AI Act 2025 compliance")
        st.markdown("• Real-time compliance monitoring")
        st.markdown("• Professional compliance certificates")

def show_features_comparison():
    """Show detailed features comparison table"""
    if st.checkbox("Show detailed features comparison"):
        config = get_pricing_config()
        
        # Create features matrix
        features_data = []
        all_features = set()
        
        # Collect all features
        for category, features in config.features_matrix.items():
            for feature in features.keys():
                all_features.add(feature)
        
        tiers = [PricingTier.STARTUP, PricingTier.GROWTH, PricingTier.SCALE, PricingTier.ENTERPRISE]
        
        # Build comparison matrix
        for feature in sorted(all_features):
            row = {"Feature": feature.replace("_", " ").title()}
            for tier in tiers:
                available_features = config.get_features_for_tier(tier)
                row[tier.value.title()] = "✅" if feature in available_features else "❌"
            features_data.append(row)
        
        st.table(features_data)

def show_contact_section():
    """Show contact and support section"""
    st.markdown("---")
    st.markdown("## 📞 Questions? We're Here to Help")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 💬 Sales Support")
        st.markdown("Need help choosing the right plan?")
        if st.button("Contact Sales Team", key="contact_sales_main"):
            st.session_state['contact_sales'] = True
            st.rerun()
    
    with col2:
        st.markdown("### 🔧 Technical Questions")
        st.markdown("Have technical implementation questions?")
        if st.button("Talk to Engineers", key="contact_tech"):
            st.session_state['contact_tech'] = True
            st.rerun()
    
    with col3:
        st.markdown("### 📊 Custom Requirements")
        st.markdown("Need custom features or enterprise deployment?")
        if st.button("Request Custom Quote", key="custom_quote"):
            st.session_state['custom_quote'] = True
            st.rerun()

def handle_tier_selection(tier: PricingTier, billing_cycle: BillingCycle):
    """Handle when user selects a pricing tier"""
    config = get_pricing_config()
    pricing = config.get_tier_pricing(tier, billing_cycle)
    
    st.session_state['selected_tier'] = tier.value
    st.session_state['selected_billing'] = billing_cycle.value
    st.session_state['selected_price'] = pricing['price']
    st.session_state['show_checkout'] = True
    
    st.success(f"✅ Selected {pricing['name']} - €{pricing['price']} per {billing_cycle.value}")
    st.balloons()
    
    # Show next steps
    st.markdown("### Next Steps:")
    if billing_cycle == BillingCycle.ANNUAL:
        st.markdown(f"• **Annual Price**: €{pricing['price']:,}")
        if 'savings' in pricing:
            st.markdown(f"• **Savings**: €{pricing['savings']:,} vs monthly billing")
    
    st.markdown("• **Setup**: Instant activation")
    st.markdown("• **Support**: Included in your plan")
    st.markdown("• **Billing**: Secure payment processing")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💳 Proceed to Checkout", type="primary", key="proceed_checkout"):
            show_checkout_form(tier, billing_cycle, pricing)
    with col2:
        if st.button("📋 View Plan Details", key="view_details"):
            show_plan_details(tier, pricing)

def show_checkout_form(tier: PricingTier, billing_cycle: BillingCycle, pricing: Dict[str, Any]):
    """Show checkout form for selected plan"""
    st.markdown("### 💳 Secure Checkout")
    
    with st.form("checkout_form"):
        st.markdown(f"**Plan**: {pricing['name']}")
        st.markdown(f"**Price**: €{pricing['price']:,} per {billing_cycle.value}")
        
        # Customer information
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("Company Name*", key="company_name")
            first_name = st.text_input("First Name*", key="first_name")
            email = st.text_input("Email Address*", key="email")
        
        with col2:
            country = st.selectbox("Country*", ["Netherlands", "Belgium", "Germany", "Other EU"], key="country")
            last_name = st.text_input("Last Name*", key="last_name")
            phone = st.text_input("Phone Number", key="phone")
        
        # Billing address
        st.markdown("**Billing Address**")
        address = st.text_input("Street Address*", key="address")
        col1, col2, col3 = st.columns(3)
        with col1:
            city = st.text_input("City*", key="city")
        with col2:
            postal_code = st.text_input("Postal Code*", key="postal")
        with col3:
            vat_number = st.text_input("VAT Number", key="vat")
        
        # Payment method
        payment_method = st.selectbox("Payment Method", ["Credit Card", "SEPA Direct Debit", "Invoice (Enterprise only)"])
        
        # Terms
        terms_accepted = st.checkbox("I accept the Terms of Service and Privacy Policy*")
        
        submitted = st.form_submit_button("Complete Purchase", type="primary")
        
        if submitted:
            if not all([company_name, first_name, last_name, email, address, city, postal_code]) or not terms_accepted:
                st.error("Please fill in all required fields and accept the terms.")
            else:
                # Process the order (placeholder)
                st.success("🎉 Order processed successfully!")
                st.markdown("**Next Steps:**")
                st.markdown("1. Check your email for login credentials")
                st.markdown("2. Access your new DataGuardian Pro account")
                st.markdown("3. Start your first compliance scan")

def show_plan_details(tier: PricingTier, pricing: Dict[str, Any]):
    """Show detailed plan information"""
    config = get_pricing_config()
    features = config.get_features_for_tier(tier)
    tier_data = config.pricing_data["tiers"][tier.value]
    
    st.markdown(f"### {pricing['name']} - Detailed Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Plan Limits:**")
        st.markdown(f"• Max scans per month: {tier_data.get('max_scans_monthly', 'Unlimited')}")
        st.markdown(f"• Max data sources: {tier_data.get('max_data_sources', 'Unlimited')}")
        st.markdown(f"• Support level: {tier_data.get('support_level', 'Standard')}")
        st.markdown(f"• Response SLA: {tier_data.get('sla_hours', 48)} hours")
    
    with col2:
        st.markdown("**Included Features:**")
        for feature in features:
            st.markdown(f"✅ {feature.replace('_', ' ').title()}")

# Helper function for main app integration
def show_pricing_in_sidebar():
    """Show pricing info in sidebar"""
    license_integration = LicenseIntegration()
    current_tier = license_integration.get_current_pricing_tier()
    
    if current_tier:
        config = get_pricing_config()
        tier_data = config.pricing_data["tiers"][current_tier.value]
        st.sidebar.markdown(f"**Current Plan**: {tier_data['name']}")
        
        if current_tier != PricingTier.ENTERPRISE:
            st.sidebar.markdown("Upgrade for more features:")
            if st.sidebar.button("View Pricing", key="sidebar_pricing"):
                st.session_state['show_pricing'] = True
                st.rerun()