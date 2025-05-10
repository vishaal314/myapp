"""
Billing UI Components for DataGuardian Pro

This module provides Streamlit UI components for subscription management,
including plan selection, usage display, payment methods, and invoices.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional

# Import billing components
from billing.plans_config import SUBSCRIPTION_PLANS, get_plan_by_tier
from billing.stripe_integration import (
    create_checkout_session,
    create_customer_portal_session,
    get_invoice_history
)
from billing.usage_tracker import get_usage_metrics

def render_subscription_info(username: str, subscription_data: Dict[str, Any]):
    """
    Render subscription information and status
    
    Args:
        username: Username to display subscription for
        subscription_data: Dictionary with subscription details
    """
    # Get the current plan
    plan_tier = subscription_data.get("plan_tier", "basic")
    plan = get_plan_by_tier(plan_tier)
    
    # Check if there's an active subscription
    has_subscription = subscription_data.get("has_subscription", False)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"""
        <div style="background-color:{_get_plan_color_bg(plan_tier)}; color:{_get_plan_color_text(plan_tier)}; 
                  border-radius:8px; padding:16px; text-align:center;">
            <div style="font-size:28px; margin-bottom:8px;">{plan.get('icon', '✨')}</div>
            <div style="font-weight:bold; font-size:18px;">{plan.get('name', 'Basic')} Plan</div>
            <div style="margin-top:8px;">${plan.get('price', 0)}/{plan.get('unit', 'month')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### Your Subscription")
        
        # Status badge
        if has_subscription:
            renewal_date = subscription_data.get("renewal_date", "Unknown")
            st.markdown(f"""
            <div style="margin-bottom:12px;">
                <span style="background-color:#c6f6d5; color:#22543d; padding:4px 8px; border-radius:4px; font-size:14px;">
                    Active
                </span>
                <span style="margin-left:8px; color:#718096; font-size:14px;">
                    Renews on {renewal_date}
                </span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="margin-bottom:12px;">
                <span style="background-color:#EDF2F7; color:#4A5568; padding:4px 8px; border-radius:4px; font-size:14px;">
                    Basic
                </span>
                <span style="margin-left:8px; color:#718096; font-size:14px;">
                    Free tier
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        # Display key features
        features = plan.get("features", [])[:3]  # Show first 3 features
        for feature in features:
            st.markdown(f"<div style='margin-bottom:4px;'>✓ {feature}</div>", unsafe_allow_html=True)
        
        # Customer Portal button (if they have a subscription)
        if has_subscription and "stripe_customer_id" in st.session_state:
            customer_id = st.session_state["stripe_customer_id"]
            if st.button("Manage Subscription", key="manage_subscription"):
                portal_url = create_customer_portal_session(customer_id)
                if portal_url:
                    st.markdown(f"[Click here to manage your subscription]({portal_url})")
                    st.info("You'll be redirected to Stripe's secure portal.")

def render_usage_stats(username: str):
    """
    Render usage statistics for the current subscription
    
    Args:
        username: Username to display usage for
    """
    # Get usage metrics
    metrics = get_usage_metrics(username)
    
    st.markdown("#### Usage This Month")
    
    col1, col2 = st.columns(2)
    
    # Format dates for display
    period_start = metrics.get("period_start", "")
    period_end = metrics.get("period_end", "")
    
    with col1:
        # Scans usage
        scans_used = metrics.get("scans_used", 0)
        scans_limit = metrics.get("scans_limit", "Unlimited")
        scan_percentage = metrics.get("scan_percentage", 0)
        
        st.markdown(f"**Scans Used:** {scans_used} / {scans_limit}")
        st.progress(scan_percentage / 100)
    
    with col2:
        # Repository usage
        repos_used = metrics.get("repositories_used", 0)
        repos_limit = metrics.get("repositories_limit", "Unlimited")
        repo_percentage = metrics.get("repository_percentage", 0)
        
        st.markdown(f"**Repositories:** {repos_used} / {repos_limit}")
        st.progress(repo_percentage / 100)
    
    # Billing period info
    st.markdown(f"""
    <div style="color:#718096; font-size:14px; margin-top:8px;">
        Billing period: {period_start} to {period_end}
    </div>
    """, unsafe_allow_html=True)
    
    # Scan type breakdown
    scan_types = metrics.get("scan_types", {})
    if scan_types:
        st.markdown("##### Scan Type Breakdown")
        
        # Create a DataFrame for the scan types
        scan_data = [
            {"Type": scan_type.title(), "Count": count}
            for scan_type, count in scan_types.items()
        ]
        
        if scan_data:
            df = pd.DataFrame(scan_data)
            st.dataframe(df, hide_index=True)

def render_payment_methods(subscription_data: Dict[str, Any]):
    """
    Render payment methods section
    
    Args:
        subscription_data: Dictionary with subscription details
    """
    st.markdown("#### Payment Method")
    
    payment_method = subscription_data.get("payment_method", None)
    
    if payment_method:
        # Display the payment method
        card_brand = payment_method.get("brand", "card").title()
        last4 = payment_method.get("last4", "****")
        exp_month = payment_method.get("exp_month", "12")
        exp_year = payment_method.get("exp_year", "2025")
        
        st.markdown(f"""
        <div style="border:1px solid #e2e8f0; border-radius:10px; padding:15px; background-color:#f8fafc;">
            <div style="display:flex; align-items:center;">
                <span style="background:#e2e8f0; color:#4a5568; padding:8px; border-radius:5px; margin-right:10px;">💳</span>
                <div>
                    <div style="font-weight:500;">{card_brand} •••• {last4}</div>
                    <div style="font-size:12px; color:#718096;">Expires {exp_month}/{exp_year}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # No payment method message
        st.markdown("""
        <div style="border:1px solid #e2e8f0; border-radius:10px; padding:15px; background-color:#f8fafc; text-align:center;">
            <div style="color:#718096;">No payment method on file</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Update payment method button
    if "stripe_customer_id" in st.session_state:
        customer_id = st.session_state["stripe_customer_id"]
        if st.button("Update Payment Method", key="update_payment"):
            portal_url = create_customer_portal_session(customer_id)
            if portal_url:
                st.markdown(f"[Click here to update your payment method]({portal_url})")
                st.info("You'll be redirected to Stripe's secure portal.")

def render_invoice_history(customer_id: Optional[str] = None):
    """
    Render invoice history
    
    Args:
        customer_id: Optional Stripe customer ID to fetch invoices for
    """
    st.markdown("#### Recent Invoices")
    
    if not customer_id:
        # No customer ID available
        st.markdown("""
        <div style="border:1px solid #e2e8f0; border-radius:10px; padding:15px; background-color:#f8fafc; text-align:center;">
            <div style="color:#718096;">No billing history available</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Get invoice history
    invoices = get_invoice_history(customer_id, limit=5)
    
    if not invoices:
        # No invoices found
        st.markdown("""
        <div style="border:1px solid #e2e8f0; border-radius:10px; padding:15px; background-color:#f8fafc; text-align:center;">
            <div style="color:#718096;">No invoices found</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Create a DataFrame for the invoices
    invoice_data = []
    for invoice in invoices:
        invoice_data.append({
            "Date": invoice.get("date", ""),
            "Amount": f"{invoice.get('currency', 'USD')} {invoice.get('amount', 0)}",
            "Status": invoice.get("status", "").title(),
            "Invoice": f"[Download]({invoice.get('pdf_url', '#')})"
        })
    
    if invoice_data:
        df = pd.DataFrame(invoice_data)
        st.dataframe(df, hide_index=True, use_container_width=True)

def render_plan_selection():
    """
    Render subscription plan selection cards
    """
    st.markdown("### Choose a Plan")
    
    # Create columns for the plans
    cols = st.columns(len(SUBSCRIPTION_PLANS))
    
    for i, (plan_id, plan_data) in enumerate(SUBSCRIPTION_PLANS.items()):
        with cols[i]:
            # Plan card
            st.markdown(f"""
            <div style="border:1px solid #e2e8f0; border-radius:10px; padding:20px; 
                      height:100%; background-color:white;">
                <div style="text-align:center; margin-bottom:10px;">
                    <span style="font-size:24px;">{plan_data.get('icon', '✨')}</span>
                </div>
                <h3 style="text-align:center; margin:5px 0; font-size:18px;">
                    {plan_data.get('name', 'Basic')}
                </h3>
                <div style="text-align:center; font-size:24px; font-weight:bold; margin:15px 0;">
                    ${plan_data.get('price', 0)}
                    <span style="font-size:14px; font-weight:normal; color:#718096;">
                        /{plan_data.get('unit', 'month')}
                    </span>
                </div>
                
                <div style="margin:20px 0;">
            """, unsafe_allow_html=True)
            
            # List features
            for feature in plan_data.get("features", []):
                st.markdown(f"""
                <div style="margin-bottom:8px; display:flex; align-items:start;">
                    <span style="color:{_get_plan_color_text(plan_id)}; margin-right:6px;">✓</span>
                    <span style="font-size:14px;">{feature}</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Subscribe button
            current_plan = st.session_state.get("subscription_tier", "basic")
            button_label = "Current Plan" if plan_id == current_plan else "Subscribe"
            
            if plan_id == current_plan:
                st.markdown(f"""
                <div style="text-align:center; margin-top:15px;">
                    <div style="background-color:#EDF2F7; color:#4A5568; border-radius:5px; 
                              padding:8px 16px; display:inline-block; font-weight:500;">
                        Current Plan
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                if st.button(f"Subscribe to {plan_data['name']}", key=f"subscribe_{plan_id}"):
                    if "stripe_customer_id" in st.session_state:
                        # Create checkout session
                        customer_id = st.session_state["stripe_customer_id"]
                        price_id = plan_data.get("stripe_price_id")
                        
                        checkout_url = create_checkout_session(customer_id, price_id)
                        if checkout_url:
                            st.markdown(f"[Click here to complete your subscription]({checkout_url})")
                            st.info("You'll be redirected to Stripe's secure checkout.")
                    else:
                        st.error("You need to be logged in with a Stripe account to subscribe.")
            
            # Close the card div
            st.markdown("</div>", unsafe_allow_html=True)

def render_billing_page():
    """
    Render the complete billing page
    """
    st.title("Subscription & Billing")
    
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.warning("Please log in to access subscription management.")
        return
    
    username = st.session_state.get("username", "")
    
    # Create tabs for the billing page
    tabs = st.tabs(["Current Subscription", "Usage", "Payment Methods", "Invoices", "Upgrade Plan"])
    
    with tabs[0]:
        # Show current subscription
        subscription_data = {
            "has_subscription": st.session_state.get("subscription_active", False),
            "plan_tier": st.session_state.get("subscription_tier", "basic"),
            "renewal_date": st.session_state.get("subscription_renewal_date", ""),
            "payment_method": st.session_state.get("payment_method", None)
        }
        
        render_subscription_info(username, subscription_data)
    
    with tabs[1]:
        # Show usage statistics
        render_usage_stats(username)
    
    with tabs[2]:
        # Show payment methods
        render_payment_methods(st.session_state.get("subscription_data", {}))
    
    with tabs[3]:
        # Show invoice history
        render_invoice_history(st.session_state.get("stripe_customer_id"))
    
    with tabs[4]:
        # Show plan selection for upgrades
        render_plan_selection()

def _get_plan_color_bg(plan_id: str) -> str:
    """Get background color for plan"""
    colors = {
        "basic": "#EBF8FF",
        "premium": "#EBF4FF",
        "gold": "#FFFBEB"
    }
    return colors.get(plan_id, "#EBF8FF")

def _get_plan_color_text(plan_id: str) -> str:
    """Get text color for plan"""
    colors = {
        "basic": "#3182CE",
        "premium": "#4C51BF",
        "gold": "#D97706"
    }
    return colors.get(plan_id, "#3182CE")