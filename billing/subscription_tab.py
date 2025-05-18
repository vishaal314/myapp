"""
Subscription Management Tab for DataGuardian Pro

This module provides the subscription management interface including:
- View current subscription details
- Change subscription plans
- Cancel subscriptions
"""

import streamlit as st
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple

# Import from access control
from access_control.user_management import update_user, load_users, save_users
from billing.stripe_integration import get_subscription_details

def render_subscription_tab(username: str, user_data: Dict[str, Any]):
    """Render the subscription management tab"""
    
    # Get subscription details
    subscription_tier = user_data.get("subscription_tier", "basic")
    subscription_active = user_data.get("subscription_active", False)
    free_trial = user_data.get("free_trial", False)
    free_trial_end = user_data.get("free_trial_end")
    renewal_date = user_data.get("subscription_renewal_date")
    
    # Subscription status section
    st.subheader("Current Subscription")
    
    # Display subscription tier and status
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style="margin-bottom: 20px;">
            <p><strong>Plan:</strong> {subscription_tier.title()}</p>
            <p><strong>Status:</strong> 
                <span class="status-badge {
                    'status-active' if subscription_active else 
                    'status-trial' if free_trial else 
                    'status-inactive'
                }">
                    {
                        'Active' if subscription_active else 
                        'Trial' if free_trial else 
                        'Inactive'
                    }
                </span>
            </p>
            {
                f'<p><strong>Trial Ends:</strong> {free_trial_end}</p>' 
                if free_trial else 
                f'<p><strong>Renews On:</strong> {renewal_date}</p>' 
                if subscription_active else 
                ''
            }
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Available scans
        if subscription_tier == "basic":
            scan_limits = {"gdpr": 5, "soc2": 0, "ai_model": 0}
        elif subscription_tier == "professional":
            scan_limits = {"gdpr": 20, "soc2": 10, "ai_model": 0}
        elif subscription_tier == "enterprise":
            scan_limits = {"gdpr": -1, "soc2": -1, "ai_model": -1}  # Unlimited
        else:
            scan_limits = {"gdpr": 3, "soc2": 0, "ai_model": 0}  # Default
        
        st.markdown(f"""
        <div style="margin-bottom: 20px;">
            <p><strong>Available Scans:</strong></p>
            <ul>
                <li>GDPR Scans: {
                    'Unlimited' if scan_limits['gdpr'] < 0 else scan_limits['gdpr']
                }</li>
                <li>SOC2 Scans: {
                    'Unlimited' if scan_limits['soc2'] < 0 else scan_limits['soc2']
                }</li>
                <li>AI Model Scans: {
                    'Unlimited' if scan_limits['ai_model'] < 0 else scan_limits['ai_model']
                }</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Plan Selection - Only show if not on enterprise or if inactive
    if subscription_tier != "enterprise" or not subscription_active:
        st.subheader("Available Plans")
        
        # Define available plans
        plans = [
            {
                "name": "Basic",
                "price": "€9.99/month",
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
                "price": "€49.99/month",
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
                "price": "€99.99/month",
                "features": [
                    "Unlimited GDPR Scans",
                    "Unlimited SOC2 Scans",
                    "Advanced AI Model Scans",
                    "Custom reporting",
                    "24/7 phone support",
                    "Dashboard access",
                    "Unlimited user accounts",
                    "Compliance certificate generation",
                    "API access"
                ]
            }
        ]
        
        # Display plans in columns
        cols = st.columns(len(plans))
        
        for i, plan in enumerate(plans):
            with cols[i]:
                st.markdown(f"""
                <div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; height: 100%;">
                    <h4 style="text-align: center; margin-bottom: 10px;">{plan['name']}</h4>
                    <p style="text-align: center; font-weight: 600; margin-bottom: 15px;">{plan['price']}</p>
                    <ul style="margin-bottom: 20px; padding-left: 20px;">
                        {''.join([f'<li>{feature}</li>' for feature in plan['features']])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                # Only show upgrade/switch button if plan is different
                if plan['name'].lower() != subscription_tier:
                    if st.button(f"Switch to {plan['name']}", key=f"switch_{plan['name'].lower()}"):
                        st.success(f"Switching to {plan['name']} plan...")
                        
                        # In a real implementation, this would call the Stripe API
                        # For this demo, we'll update the user data directly
                        
                        # Load user data
                        users = load_users()
                        
                        # Update subscription information
                        # For demo, we'll just assume a renewal date one month from now
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
                else:
                    st.info("Current Plan", icon="✅")
    
    # Cancellation Section
    if subscription_active and not free_trial:
        st.subheader("Cancel Subscription")
        st.info("""
        Canceling your subscription will stop automatic billing at the end of your current billing period.
        You'll continue to have access to your current plan until the end of your billing period.
        """)
        
        if st.button("Cancel Subscription"):
            if st.checkbox("I understand I'm canceling my subscription"):
                # In real implementation, this would call the Stripe API
                # For demo, we'll update the user data directly
                users = load_users()
                users[username]["subscription_active"] = False
                save_users(users)
                
                st.success("Your subscription has been canceled and will end at the end of your current billing period.")
                st.rerun()