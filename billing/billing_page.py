"""
Billing Management Page for DataGuardian Pro

This module provides a comprehensive billing management interface including:
- View current subscription details
- Manage payment methods
- Add new payment methods (VISA and iDEAL)
- View billing history
- Change subscription plan
- Download invoices
"""

import streamlit as st
import hashlib
import uuid
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple

# Import from access control
from access_control.user_management import update_user, load_users, save_users
from billing.stripe_integration import (
    create_payment_method,
    list_payment_methods,
    update_default_payment_method,
    delete_payment_method,
    get_subscription_details
)

def load_stripe_keys():
    """Load Stripe API keys from environment variables"""
    stripe_publishable_key = os.environ.get("STRIPE_PUBLISHABLE_KEY")
    stripe_secret_key = os.environ.get("STRIPE_SECRET_KEY")
    
    return stripe_publishable_key, stripe_secret_key

def render_billing_page(username: str, user_data: Dict[str, Any]):
    """
    Render the billing management page for the logged-in user
    
    Args:
        username: Username of the logged-in user
        user_data: User data dictionary
    """
    st.title("Billing Management")
    
    # Load Stripe keys
    stripe_publishable_key, stripe_secret_key = load_stripe_keys()
    
    # Custom CSS for better presentation
    st.markdown("""
    <style>
    .billing-container {
        background: white;
        border-radius: 10px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    
    .section-header {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 15px;
        color: #1a202c;
    }
    
    .status-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .status-active {
        background-color: #def7ec;
        color: #03543e;
    }
    
    .status-inactive {
        background-color: #fde8e8;
        color: #9b1c1c;
    }
    
    .status-trial {
        background-color: #e1effe;
        color: #1e429f;
    }
    
    .payment-method-card {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        position: relative;
    }
    
    .default-badge {
        position: absolute;
        top: 10px;
        right: 10px;
        background: #ebf4ff;
        color: #4c51bf;
        font-size: 0.7rem;
        padding: 2px 6px;
        border-radius: 4px;
    }
    
    .card-brand {
        font-weight: 600;
        margin-bottom: 5px;
    }
    
    .card-details {
        color: #4a5568;
        font-size: 0.9rem;
    }
    
    .add-payment-button {
        background-color: #4c51bf;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.9rem;
    }
    
    .plan-card {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 15px;
        position: relative;
    }
    
    .current-plan {
        border: 2px solid #4c51bf;
    }
    
    .current-plan-badge {
        position: absolute;
        top: 10px;
        right: 10px;
        background: #4c51bf;
        color: white;
        font-size: 0.7rem;
        padding: 2px 6px;
        border-radius: 4px;
    }
    
    .plan-name {
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 5px;
    }
    
    .plan-price {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 10px;
        color: #1a202c;
    }
    
    .plan-features {
        margin-bottom: 15px;
    }
    
    .invoice-row {
        display: flex;
        justify-content: space-between;
        padding: 10px 0;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .invoice-date {
        color: #4a5568;
        font-size: 0.9rem;
    }
    
    .invoice-amount {
        font-weight: 600;
    }
    
    .tab-content {
        padding: 20px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Tabs for billing management
    tab1, tab2, tab3, tab4 = st.tabs(["Subscription", "Payment Methods", "Billing History", "Plan Management"])
    
    # Get subscription details
    subscription_tier = user_data.get("subscription_tier", "basic")
    subscription_active = user_data.get("subscription_active", False)
    free_trial = user_data.get("free_trial", False)
    free_trial_end = user_data.get("free_trial_end")
    renewal_date = user_data.get("subscription_renewal_date")
    
    # TAB 1: Subscription Details
    with tab1:
        st.markdown('<div class="billing-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-header">Current Subscription</h3>', unsafe_allow_html=True)
        
        # Display subscription tier and status
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div style="margin-bottom: 20px;">
                <div style="font-size: 0.9rem; color: #4a5568; margin-bottom: 5px;">Subscription Plan</div>
                <div style="font-size: 1.2rem; font-weight: 600;">{subscription_tier.title()}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Status badge
            if free_trial:
                status_badge = '<span class="status-badge status-trial">Free Trial</span>'
            elif subscription_active:
                status_badge = '<span class="status-badge status-active">Active</span>'
            else:
                status_badge = '<span class="status-badge status-inactive">Inactive</span>'
            
            st.markdown(f"""
            <div style="margin-bottom: 20px;">
                <div style="font-size: 0.9rem; color: #4a5568; margin-bottom: 5px;">Status</div>
                <div>{status_badge}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Display next billing date
        if renewal_date:
            st.markdown(f"""
            <div style="margin-bottom: 20px;">
                <div style="font-size: 0.9rem; color: #4a5568; margin-bottom: 5px;">Next Billing Date</div>
                <div style="font-size: 1.1rem;">{renewal_date}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Display free trial information
        if free_trial and free_trial_end:
            days_left = (datetime.strptime(free_trial_end, "%Y-%m-%d") - datetime.now()).days
            days_left = max(0, days_left)
            
            st.markdown(f"""
            <div style="background-color: #e1effe; padding: 15px; border-radius: 8px; margin-top: 20px;">
                <div style="font-weight: 600; color: #1e429f; margin-bottom: 5px;">Free Trial Active</div>
                <div style="color: #2c5282;">You have {days_left} days left in your free trial. Your free trial ends on {free_trial_end}.</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Add button to upgrade to paid plan
            if st.button("Upgrade to Paid Plan", key="upgrade_from_trial", use_container_width=True):
                st.session_state.show_upgrade_modal = True
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Subscription Features
        st.markdown('<div class="billing-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-header">Subscription Features</h3>', unsafe_allow_html=True)
        
        # Import the plans config
        from billing.plans_config import SUBSCRIPTION_PLANS
        
        # Get features based on subscription tier (default to basic if not found)
        tier_key = subscription_tier.lower()
        if tier_key not in SUBSCRIPTION_PLANS:
            tier_key = "basic"  # Default to basic if tier not found
            
        plan_features = SUBSCRIPTION_PLANS[tier_key]["features"]
        
        # Display features
        for feature in plan_features:
            st.markdown(f"✓ {feature}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 2: Payment Methods
    with tab2:
        st.markdown('<div class="billing-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-header">Payment Methods</h3>', unsafe_allow_html=True)
        
        # Get payment methods for the user
        stripe_customer_id = user_data.get("stripe_customer_id", "")
        payment_methods = list_payment_methods(stripe_customer_id) if stripe_customer_id else []
        
        if not payment_methods:
            st.info("You don't have any payment methods added yet.")
        else:
            # Display payment methods
            for pm in payment_methods:
                is_default = pm.get("is_default", False)
                card_brand = pm.get("card_brand", "Card")
                last4 = pm.get("last4", "****")
                exp_month = pm.get("exp_month", "12")
                exp_year = pm.get("exp_year", "2025")
                pm_id = pm.get("id", "")
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="payment-method-card">
                        {f'<div class="default-badge">Default</div>' if is_default else ''}
                        <div class="card-brand">{card_brand}</div>
                        <div class="card-details">•••• •••• •••• {last4} | Expires {exp_month}/{exp_year}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if not is_default:
                        if st.button("Set Default", key=f"default_{pm_id}"):
                            # Set this payment method as default
                            stripe_customer_id = user_data.get("stripe_customer_id", "")
                            if stripe_customer_id:
                                update_default_payment_method(
                                    customer_id=stripe_customer_id,
                                    payment_method_id=pm_id
                                )
                            st.success("Default payment method updated!")
                            st.rerun()
                    
                    if st.button("Remove", key=f"remove_{pm_id}"):
                        # Delete payment method
                        stripe_customer_id = user_data.get("stripe_customer_id", "")
                        if stripe_customer_id:
                            delete_payment_method(
                                customer_id=stripe_customer_id,
                                payment_method_id=pm_id
                            )
                        st.success("Payment method removed successfully!")
                        st.rerun()
        
        # Add new payment method section
        st.markdown('<h3 class="section-header" style="margin-top: 30px;">Add New Payment Method</h3>', unsafe_allow_html=True)
        
        # Payment method selection
        payment_type = st.selectbox("Payment Method Type", ["Credit Card", "iDEAL (Netherlands)"], key="payment_type")
        
        # Credit Card Form
        if payment_type == "Credit Card":
            with st.form("add_card_form"):
                card_holder = st.text_input("Cardholder Name", placeholder="Jane Smith")
                card_number = st.text_input("Card Number", placeholder="4242 4242 4242 4242")
                
                col1, col2 = st.columns(2)
                with col1:
                    expiry = st.text_input("Expiry (MM/YY)", placeholder="12/25")
                with col2:
                    cvv = st.text_input("CVV", placeholder="123", type="password", max_chars=4)
                
                submit_card = st.form_submit_button("Add Card", use_container_width=True)
                
                if submit_card:
                    if not card_holder or not card_number or not expiry or not cvv:
                        st.error("Please fill in all fields.")
                    else:
                        try:
                            # In a real app, we would use Stripe Elements or Stripe.js for secure card collection
                            # This is a mock implementation for the demo
                            
                            # Basic validation
                            card_number = card_number.replace(" ", "").strip()
                            if not card_number.isdigit() or len(card_number) < 13 or len(card_number) > 19:
                                st.error("Please enter a valid card number.")
                            elif not expiry.strip().count("/") == 1:
                                st.error("Please enter a valid expiry date (MM/YY).")
                            elif not cvv.isdigit() or len(cvv) < 3:
                                st.error("Please enter a valid CVV.")
                            else:
                                # Create new payment method
                                exp_month, exp_year = expiry.strip().split("/")
                                
                                # Create mock payment method
                                new_payment_method = create_payment_method(
                                    customer_id=user_data.get("stripe_customer_id", ""),
                                    card_number=card_number,
                                    exp_month=exp_month,
                                    exp_year=exp_year,
                                    cvc=cvv,
                                    cardholder_name=card_holder
                                )
                                
                                # Update user record
                                users = load_users()
                                if username in users:
                                    users[username]["has_payment_method"] = True
                                    save_users(users)
                                
                                st.success("Card added successfully!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error adding card: {str(e)}")
        
        # iDEAL Form
        elif payment_type == "iDEAL (Netherlands)":
            with st.form("add_ideal_form"):
                account_name = st.text_input("Account Holder Name", placeholder="Jane Smith")
                
                # Bank selection
                banks = [
                    "ABN AMRO",
                    "ASN Bank",
                    "Bunq",
                    "Handelsbanken",
                    "ING Bank",
                    "Knab",
                    "Moneyou",
                    "Rabobank",
                    "RegioBank",
                    "SNS Bank",
                    "Triodos Bank",
                    "Van Lanschot"
                ]
                selected_bank = st.selectbox("Select Your Bank", banks)
                
                submit_ideal = st.form_submit_button("Continue with iDEAL", use_container_width=True)
                
                if submit_ideal:
                    if not account_name or not selected_bank:
                        st.error("Please fill in all fields.")
                    else:
                        try:
                            # In a real app, we would redirect to the iDEAL payment flow
                            # This is a mock implementation for the demo
                            
                            # Create mock payment method
                            new_payment_method = create_payment_method(
                                customer_id=user_data.get("stripe_customer_id", ""),
                                payment_type="ideal",
                                bank=selected_bank,
                                account_name=account_name
                            )
                            
                            # Update user record
                            users = load_users()
                            if username in users:
                                users[username]["has_payment_method"] = True
                                save_users(users)
                            
                            st.success(f"iDEAL payment method added for {selected_bank} successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error setting up iDEAL: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 3: Billing History
    with tab3:
        st.markdown('<div class="billing-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-header">Billing History</h3>', unsafe_allow_html=True)
        
        # Mock billing history for demo purposes
        if subscription_tier == "basic":
            price = "€9.99"
        elif subscription_tier == "professional":
            price = "€49.99"
        else:
            price = "€99.99"
        
        # Generate mock invoices for last 6 months
        invoices = []
        for i in range(6):
            invoice_date = (datetime.now() - timedelta(days=30 * i)).strftime("%Y-%m-%d")
            invoice_id = f"INV-{hashlib.md5(invoice_date.encode()).hexdigest()[:8].upper()}"
            
            invoices.append({
                "date": invoice_date,
                "id": invoice_id,
                "amount": price,
                "status": "Paid" if i < 5 else "Upcoming"
            })
        
        # Display invoices
        for invoice in invoices:
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown(f"""
                <div>
                    <div style="font-weight: 500;">{invoice['date']}</div>
                    <div style="font-size: 0.8rem; color: #4a5568;">{invoice['id']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                status_color = "#059669" if invoice['status'] == "Paid" else "#9f580a"
                st.markdown(f"""
                <div>
                    <div style="font-weight: 500;">{invoice['amount']}</div>
                    <div style="font-size: 0.8rem; color: {status_color};">{invoice['status']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                if invoice['status'] == "Paid":
                    st.download_button(
                        label="PDF",
                        data="Mock Invoice PDF Content",
                        file_name=f"{invoice['id']}.pdf",
                        mime="application/pdf",
                        key=f"dl_{invoice['id']}"
                    )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 4: Plan Management
    with tab4:
        st.markdown('<div class="billing-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-header">Available Plans</h3>', unsafe_allow_html=True)
        
        # Define plans
        plans = [
            {
                "name": "Basic",
                "price": "€9.99",
                "description": "Essential compliance scanning for small businesses",
                "features": [
                    "5 GDPR Scans per month",
                    "Basic reporting",
                    "Email support",
                    "Dashboard access",
                    "Single user account"
                ]
            },
            {
                "name": "Professional",
                "price": "€49.99",
                "description": "Advanced compliance for growing businesses",
                "features": [
                    "20 GDPR Scans per month",
                    "10 SOC2 Scans per month",
                    "Advanced reporting",
                    "Priority email support",
                    "Dashboard access",
                    "Up to 5 user accounts",
                    "Compliance certificate generation"
                ]
            },
            {
                "name": "Enterprise",
                "price": "€99.99",
                "description": "Complete compliance solution for organizations",
                "features": [
                    "Unlimited GDPR Scans",
                    "Unlimited SOC2 Scans",
                    "Advanced AI Model Scans",
                    "Premium reporting with risk analysis",
                    "24/7 Priority support",
                    "Full dashboard access",
                    "Unlimited user accounts",
                    "Compliance certificate generation",
                    "Custom compliance policy development",
                    "Dedicated compliance officer"
                ]
            }
        ]
        
        # Display plans
        for plan in plans:
            # Determine if this is the current plan
            is_current = plan["name"].lower() == subscription_tier.lower()
            
            st.markdown(f"""
            <div class="plan-card{' current-plan' if is_current else ''}">
                {f'<div class="current-plan-badge">Current Plan</div>' if is_current else ''}
                <div class="plan-name">{plan['name']}</div>
                <div class="plan-price">{plan['price']}<span style="font-size: 0.9rem; font-weight: 400;"> / month</span></div>
                <div style="font-size: 0.9rem; color: #4a5568; margin-bottom: 15px;">{plan['description']}</div>
                <div class="plan-features">
                    {'<br>'.join([f"✓ {feature}" for feature in plan['features']])}
                </div>
                {'<button disabled style="width: 100%; padding: 8px 0; background: #e2e8f0; color: #4a5568; border: none; border-radius: 4px; cursor: not-allowed;">Current Plan</button>' if is_current else '<button style="width: 100%; padding: 8px 0; background: #4c51bf; color: white; border: none; border-radius: 4px; cursor: pointer;">Switch to ' + plan["name"] + '</button>'}
            </div>
            """, unsafe_allow_html=True)
            
            # Hidden button for plan change - Streamlit can't handle JS onclick directly
            if not is_current:
                if st.button(f"Change to {plan['name']}", key=f"change_plan_{plan['name'].lower()}", help="Switch to this plan"):
                    # Update user's subscription
                    users = load_users()
                    if username in users:
                        # Calculate next billing date (1 month from now)
                        next_billing = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
                        
                        # Update user record
                        users[username]["subscription_tier"] = plan["name"].lower()
                        users[username]["subscription_active"] = True
                        users[username]["subscription_renewal_date"] = next_billing
                        users[username]["free_trial"] = False
                        users[username]["free_trial_end"] = None
                        
                        save_users(users)
                        
                        st.success(f"Successfully switched to {plan['name']} plan!")
                        st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Cancellation Section
        if subscription_active and not free_trial:
            st.markdown('<div class="billing-container" style="margin-top: 30px;">', unsafe_allow_html=True)
            st.markdown('<h3 class="section-header">Cancel Subscription</h3>', unsafe_allow_html=True)
            st.markdown("""
            <div style="color: #4a5568; margin-bottom: 20px;">
                Canceling your subscription will stop automatic billing at the end of your current billing period.
                You'll continue to have access to your current plan until the end of your billing period.
            </div>
            """, unsafe_allow_html=True)
            
            # Implement cancellation button
            if st.button("Cancel Subscription", key="cancel_subscription"):
                # Show confirmation dialog
                st.session_state.show_cancel_confirm = True
            
            # Cancel confirmation dialog
            if st.session_state.get("show_cancel_confirm", False):
                with st.expander("Are you sure you want to cancel?", expanded=True):
                    st.warning("This will cancel your subscription at the end of the current billing period.")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Yes, Cancel", key="confirm_cancel"):
                            # Update user record
                            users = load_users()
                            if username in users:
                                # Don't deactivate immediately, just mark for cancellation
                                users[username]["subscription_cancel_at_period_end"] = True
                                save_users(users)
                                
                                st.success("Your subscription has been canceled. You'll have access until the end of your current billing period.")
                                st.session_state.show_cancel_confirm = False
                                st.rerun()
                    
                    with col2:
                        if st.button("No, Keep Subscription", key="keep_subscription"):
                            st.session_state.show_cancel_confirm = False
                            st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    # Test rendering
    st.set_page_config(page_title="Billing Management", layout="wide")
    
    # Mock user data for testing
    mock_user = {
        "username": "testuser",
        "email": "test@example.com",
        "subscription_tier": "professional",
        "subscription_active": True,
        "stripe_customer_id": "cus_mock123",
        "free_trial": False,
        "subscription_renewal_date": "2025-06-15"
    }
    
    render_billing_page("testuser", mock_user)