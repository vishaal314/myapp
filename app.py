import streamlit as st
import pandas as pd
import time
import json
import os
import random
import uuid
import base64
from datetime import datetime
import stripe
import re

# Import scanners - adjust paths as needed
try:
    from services.enhanced_soc2_scanner import scan_github_repository as soc2_scan_github
    from services.enhanced_soc2_scanner import scan_azure_repository as soc2_scan_azure
    from services.soc2_display import display_soc2_findings
except ImportError:
    # Mock implementations if modules not found
    def soc2_scan_github(repo_url, branch=None, token=None):
        """Mock SOC2 scanner implementation"""
        return generate_mock_soc2_results(repo_url, branch)
        
    def soc2_scan_azure(repo_url, project, branch=None, token=None, organization=None):
        """Mock SOC2 scanner implementation for Azure"""
        return generate_mock_soc2_results(repo_url, branch)
        
    def display_soc2_findings(results):
        """Mock SOC2 findings display"""
        st.json(results)

# Import sustainability scanner
try:
    from utils.scanners.sustainability_scanner import run_sustainability_scanner
    from utils.sustainability_analyzer import SustainabilityAnalyzer
except ImportError:
    # Mock implementation
    def run_sustainability_scanner():
        """Mock sustainability scanner implementation"""
        st.title("Sustainability Scanner")
        st.info("Running mock implementation of Sustainability Scanner")
        
    class SustainabilityAnalyzer:
        """Mock sustainability analyzer"""
        def __init__(self, scan_results=None, industry="average"):
            self.scan_results = scan_results
            self.industry = industry
            
        def analyze(self):
            """Return mock analysis"""
            return {
                "sustainability_score": random.randint(60, 95),
                "potential_savings": random.randint(10000, 50000),
                "carbon_reduction": random.randint(5, 30)
            }

# Initialize Stripe
stripe_public_key = os.environ.get('STRIPE_PUBLISHABLE_KEY')
stripe_secret_key = os.environ.get('STRIPE_SECRET_KEY')
stripe.api_key = stripe_secret_key

# Define subscription plans
SUBSCRIPTION_PLANS = {
    "basic": {
        "name": "Basic",
        "price": 49,
        "features": [
            "Basic Privacy Scans",
            "5 repositories",
            "Weekly scans",
            "Email support"
        ],
        "stripe_price_id": "price_basic123"  # Replace with actual Stripe price ID
    },
    "premium": {
        "name": "Premium",
        "price": 99,
        "features": [
            "All Basic features",
            "20 repositories",
            "Daily scans",
            "SOC2 compliance",
            "Priority support"
        ],
        "stripe_price_id": "price_premium456"  # Replace with actual Stripe price ID
    },
    "gold": {
        "name": "Gold",
        "price": 199,
        "features": [
            "All Premium features",
            "Unlimited repositories",
            "Continuous scanning",
            "Custom integrations",
            "Dedicated support",
            "Compliance certification"
        ],
        "stripe_price_id": "price_gold789"  # Replace with actual Stripe price ID
    }
}

# Page configuration
st.set_page_config(
    page_title="DataGuardian Pro - Privacy Compliance Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# New modern design system with a clean, professional aesthetic
st.markdown("""
<style>
    /* Global Reset and Base Styles */
    * {
        box-sizing: border-box;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    }
    
    /* App Background with subtle gradient */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    /* Modern Typography System */
    h1, h2, h3, h4, h5, h6 {
        font-weight: 700;
        color: #0f172a;
        letter-spacing: -0.025em;
    }
    
    p, li, span {
        color: #334155;
        line-height: 1.7;
    }
    
    /* Brand Colors - Midnight Blue to Electric Purple gradient */
    .brand-gradient {
        background: linear-gradient(135deg, #0f172a 0%, #3b82f6 50%, #8b5cf6 100%);
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        color: transparent !important;
        display: inline-block !important;
    }
    
    /* Hero Header */
    .hero-header {
        font-size: clamp(2.5rem, 5vw, 3.75rem);
        font-weight: 800;
        background: linear-gradient(135deg, #0f172a 0%, #3b82f6 50%, #8b5cf6 100%);
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        color: transparent !important;
        display: inline-block !important;
        margin-bottom: 0.5rem;
        line-height: 1.1;
    }
    
    .sub-header {
        font-size: 1.4rem;
        color: #2c5282;
        margin-top: 10px;
        padding-top: 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        letter-spacing: -0.3px;
        font-weight: 400;
    }
    
    /* Card Components */
    .dashboard-card {
        background-color: white;
        border-radius: 16px;
        padding: 28px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        margin-bottom: 28px;
        border: 1px solid #f0f0f0;
        transition: all 0.3s ease-in-out;
    }
    
    .dashboard-card:hover {
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
        transform: translateY(-4px);
    }
    
    /* Navigation Elements */
    .nav-link {
        color: #4f46e5;
        text-decoration: none;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .nav-link:hover {
        color: #7c3aed;
        text-decoration: none;
        transform: translateY(-1px);
    }
    
    /* Sidebar Customization */
    .css-1d391kg, .css-163ttbj, div[data-testid="stSidebar"] {
        background-color: #ffffff;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.05);
    }
    
    /* Custom Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #f0f4ff;
        padding: 5px;
        border-radius: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f8faff;
        border-radius: 10px;
        gap: 1px;
        padding: 10px 20px;
        margin: 0 4px;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(120deg, #0b3d91 0%, #4f46e5 100%);
        color: white;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
        transform: translateY(-2px);
    }
    
    /* Button Styling - Multi-color options */
    .stButton > button {
        background: linear-gradient(120deg, #0b3d91 0%, #4f46e5 100%);
        color: white;
        border-radius: 8px;
        padding: 12px 30px;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
        margin: 10px 0;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.1);
    }
    
    .stButton > button:hover {
        background: linear-gradient(120deg, #1853b3 0%, #6366f1 100%);
        box-shadow: 0 6px 18px rgba(79, 70, 229, 0.3);
        transform: translateY(-2px);
    }
    
    .button-primary {
        background: linear-gradient(120deg, #0b3d91 0%, #4f46e5 100%) !important;
    }
    
    .button-success {
        background: linear-gradient(120deg, #059669 0%, #10b981 100%) !important;
    }
    
    .button-warning {
        background: linear-gradient(120deg, #d97706 0%, #f59e0b 100%) !important;
    }
    
    .button-danger {
        background: linear-gradient(120deg, #dc2626 0%, #ef4444 100%) !important;
    }
    
    /* Metric Card Styling */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(120deg, #0b3d91 0%, #4f46e5 100%);
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        color: transparent !important;
        display: inline-block !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-weight: 500;
    }
    
    /* Input Field Styling */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        padding: 12px 16px;
        transition: all 0.2s ease;
        font-size: 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #4f46e5;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2);
        transform: translateY(-1px);
    }
    
    /* Select Box Styling */
    .stSelectbox > div[data-baseweb="select"] > div:first-child {
        border-radius: 10px;
        background-color: white;
    }
    
    /* Checkbox Styling */
    .stCheckbox > div[role="checkbox"] {
        transform: scale(1.1);
    }
    
    /* Section Spacing */
    .main-section {
        padding: 40px 0;
    }
    
    .section-divider {
        height: 2px;
        background: linear-gradient(90deg, rgba(79, 70, 229, 0.1) 0%, rgba(79, 70, 229, 0.6) 50%, rgba(79, 70, 229, 0.1) 100%);
        margin: 30px 0;
        border-radius: 100px;
    }
</style>
""", unsafe_allow_html=True)

# New Component System for 2025 Design
st.markdown("""
<style>
    /* 
    * MODERN DESIGN SYSTEM 2025 
    * DataGuardian Pro Enterprise Platform
    */
    
    /* Cards & Container System */
    .card {
        background: white;
        border-radius: 24px;
        box-shadow: 0 4px 24px rgba(15, 23, 42, 0.06);
        overflow: hidden;
        transition: all 0.3s ease;
        border: 1px solid rgba(226, 232, 240, 0.8);
    }
    
    .card-hover:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 36px rgba(15, 23, 42, 0.1);
    }
    
    .card-header {
        padding: 24px 28px 0 28px;
    }
    
    .card-body {
        padding: 20px 28px;
    }
    
    .card-footer {
        padding: 0 28px 24px 28px;
        border-top: 1px solid #f1f5f9;
    }
    
    /* Glass Morphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(15, 23, 42, 0.1);
    }
    
    /* Status Cards */
    .status-card {
        padding: 24px;
        border-radius: 16px;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        transition: all 0.3s ease;
    }
    
    .status-card-primary {
        background: linear-gradient(135deg, #e0f2fe 0%, #dbeafe 100%);
        border: 1px solid #bfdbfe;
    }
    
    .status-card-success {
        background: linear-gradient(135deg, #dcfce7 0%, #d1fae5 100%);
        border: 1px solid #a7f3d0;
    }
    
    .status-card-warning {
        background: linear-gradient(135deg, #fef3c7 0%, #fef9c3 100%);
        border: 1px solid #fde68a;
    }
    
    .status-card-danger {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border: 1px solid #fca5a5;
    }
    
    /* Subscription Cards - Modernized */
    .plan-card {
        background: white;
        border-radius: 24px;
        padding: 40px 32px;
        box-shadow: 0 10px 40px rgba(15, 23, 42, 0.08);
        margin-bottom: 24px;
        text-align: center;
        border: 1px solid rgba(241, 245, 249, 0.8);
        transition: all 0.4s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        position: relative;
        overflow: hidden;
    }
    
    .plan-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 8px;
        background: linear-gradient(90deg, #4f46e5, #7c3aed);
        opacity: 0.7;
        transition: height 0.3s ease;
    }
    
    .plan-card:hover {
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
        transform: translateY(-6px);
    }
    
    .plan-card:hover::before {
        height: 12px;
    }
    
    /* Plan Card Variations */
    .plan-card.basic::before {
        background: linear-gradient(90deg, #0ea5e9, #38bdf8);
    }
    
    .plan-card.premium::before {
        background: linear-gradient(90deg, #4f46e5, #7c3aed);
    }
    
    .plan-card.gold::before {
        background: linear-gradient(90deg, #f59e0b, #fbbf24);
    }
    
    .plan-name {
        font-size: 1.6rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 12px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        position: relative;
    }
    
    .plan-price {
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(120deg, #0b3d91 0%, #4f46e5 100%);
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        color: transparent !important;
        display: inline-block !important;
        margin-bottom: 20px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1;
    }
    
    .plan-price-period {
        font-size: 1rem;
        color: #64748b;
        font-weight: 500;
        margin-top: -5px;
        display: block;
    }
    
    .plan-card.basic .plan-price {
        background: linear-gradient(120deg, #0ea5e9 0%, #38bdf8 100%);
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        color: transparent !important;
        display: inline-block !important;
    }
    
    .plan-card.premium .plan-price {
        background: linear-gradient(120deg, #4f46e5 0%, #7c3aed 100%);
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        color: transparent !important;
        display: inline-block !important;
    }
    
    .plan-card.gold .plan-price {
        background: linear-gradient(120deg, #f59e0b 0%, #fbbf24 100%);
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        color: transparent !important;
        display: inline-block !important;
    }
    
    .plan-features {
        text-align: left;
        margin-bottom: 25px;
        flex-grow: 1;
        padding: 5px 0;
    }
    
    .plan-feature-item {
        margin-bottom: 16px;
        display: flex;
        align-items: flex-start;
        font-size: 0.95rem;
        color: #475569;
        line-height: 1.4;
    }
    
    .plan-feature-item::before {
        content: "✓";
        color: white;
        font-weight: bold;
        margin-right: 12px;
        margin-top: 2px;
        background: linear-gradient(120deg, #0ea5e9 0%, #38bdf8 100%);
        min-width: 22px;
        height: 22px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
    }
    
    .plan-card.premium .plan-feature-item::before {
        background: linear-gradient(120deg, #4f46e5 0%, #7c3aed 100%);
    }
    
    .plan-card.gold .plan-feature-item::before {
        background: linear-gradient(120deg, #f59e0b 0%, #fbbf24 100%);
    }
    
    .subscribe-button {
        margin-top: 10px;
        padding: 14px 0;
        border-radius: 12px;
        text-decoration: none;
        display: block;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        cursor: pointer;
        font-size: 1rem;
        width: 100%;
        background: linear-gradient(120deg, #0ea5e9 0%, #38bdf8 100%);
        color: white;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
    }
    
    .plan-card.premium .subscribe-button {
        background: linear-gradient(120deg, #4f46e5 0%, #7c3aed 100%);
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
    }
    
    .plan-card.gold .subscribe-button {
        background: linear-gradient(120deg, #f59e0b 0%, #fbbf24 100%);
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
    }
    
    .subscribe-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(14, 165, 233, 0.4);
    }
    
    .plan-card.premium .subscribe-button:hover {
        box-shadow: 0 6px 16px rgba(79, 70, 229, 0.4);
    }
    
    .plan-card.gold .subscribe-button:hover {
        box-shadow: 0 6px 16px rgba(245, 158, 11, 0.4);
    }
    
    /* Popular badge */
    .popular-badge {
        position: absolute;
        top: -3px;
        right: -3px;
        background: linear-gradient(120deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        padding: 8px 16px;
        font-size: 0.8rem;
        font-weight: 600;
        border-radius: 0 16px 0 16px;
        box-shadow: 0 4px 10px rgba(79, 70, 229, 0.3);
        z-index: 1;
    }
    
    /* Authentication UI */
    .login-options {
        text-align: center;
        margin: 30px 0;
    }
    
    .auth-container {
        background: white;
        border-radius: 16px;
        padding: 35px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        max-width: 500px;
        margin: 0 auto;
    }
    
    .google-login-button {
        background-color: white;
        border: 1px solid #e2e8f0;
        color: #333333;
        padding: 14px 24px;
        border-radius: 12px;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin: 15px 0;
        width: 100%;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        font-size: 1rem;
    }
    
    .google-login-button:hover {
        background-color: #f8f9fa;
        border-color: #c1c7cd;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }
    
    .divider {
        display: flex;
        align-items: center;
        text-align: center;
        margin: 30px 0;
    }
    
    .divider::before,
    .divider::after {
        content: '';
        flex: 1;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .divider-text {
        padding: 0 18px;
        color: #64748b;
        font-weight: 500;
        font-size: 0.9rem;
    }
    
    /* Form styling */
    .form-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 25px;
        text-align: center;
    }
    
    .form-container {
        background-color: white;
        padding: 35px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        margin-bottom: 25px;
    }
    
    /* Badge styling */
    .badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 0.35em 0.75em;
        font-size: 0.75em;
        font-weight: 600;
        border-radius: 9999px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .badge-blue {
        background: rgba(14, 165, 233, 0.1);
        color: #0284c7;
    }
    
    .badge-purple {
        background: rgba(79, 70, 229, 0.1);
        color: #4338ca;
    }
    
    .badge-amber {
        background: rgba(245, 158, 11, 0.1);
        color: #d97706;
    }
    
    /* Status Badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 6px 12px;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 10px;
    }
    
    .status-badge:before {
        content: "";
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-high {
        background-color: #FEE2E2;
        color: #B91C1C;
    }
    
    .status-high:before {
        background-color: #DC2626;
    }
    
    .status-medium {
        background-color: #FEF3C7;
        color: #92400E;
    }
    
    .status-medium:before {
        background-color: #D97706;
    }
    
    .status-low {
        background-color: #ECFDF5;
        color: #047857;
    }
    
    .status-low:before {
        background-color: #10B981;
    }
    
    /* Dashboard Stats */
    .stat-container {
        background-color: white;
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
        text-align: center;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        transition: all 0.3s ease;
    }
    
    .stat-container:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }
    
    .stat-value {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(120deg, #0b3d91 0%, #4f46e5 100%);
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        color: transparent !important;
        display: inline-block !important;
        margin-bottom: 8px;
    }
    
    .stat-label {
        font-size: 1rem;
        color: #64748b;
        font-weight: 500;
    }
    
    /* Landing page button spacing */
    .landing-button {
        margin: 16px 0;
        padding: 14px 40px !important;
        font-size: 1.1rem !important;
        letter-spacing: 0.02em;
    }
    
    .button-group {
        display: flex;
        gap: 20px;
        margin: 30px 0;
    }
    
    .landing-features {
        margin: 50px 0;
    }
    
    .feature-item {
        background: white;
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    
    .feature-item:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }
    
    .feature-icon {
        width: 60px;
        height: 60px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.6rem;
        margin-bottom: 16px;
        background: linear-gradient(120deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.email = ""
    st.session_state.active_tab = "login"
    st.session_state.scan_history = []
    st.session_state.current_scan_results = None
    st.session_state.permissions = []
    st.session_state.subscription_tier = "basic"  # Default subscription tier

# Mock authentication function
def authenticate(username, password):
    # Mock authentication - in a real app, this would check against a database
    if username == "admin" and password == "password":
        return {
            "username": "admin",
            "role": "admin",
            "email": "admin@dataguardian.pro",
            "permissions": ["scan:all", "report:all", "admin:all"]
        }
    elif username == "user" and password == "password":
        return {
            "username": "user",
            "role": "viewer",
            "email": "user@dataguardian.pro",
            "permissions": ["scan:basic", "report:view"]
        }
    return None

# Mock scan result generation
def generate_mock_scan_results(scan_type):
    """Generate mock scan results based on scan type"""
    results = {
        "scan_type": scan_type,
        "timestamp": datetime.now().isoformat(),
        "scan_id": str(uuid.uuid4()),
        "findings": [],
        "total_findings": random.randint(5, 20),
        "high_risk": random.randint(0, 5),
        "medium_risk": random.randint(3, 8),
        "low_risk": random.randint(2, 10),
        "compliance_score": random.randint(60, 95)
    }
    
    return results

def generate_mock_soc2_results(repo_url, branch=None):
    """Generate mock SOC2 scan results"""
    results = {
        "scan_type": "SOC2 Scanner",
        "timestamp": datetime.now().isoformat(),
        "scan_id": str(uuid.uuid4()),
        "repo_url": repo_url,
        "branch": branch or "main",
        "findings": [],
        "high_risk_count": random.randint(1, 5),
        "medium_risk_count": random.randint(3, 8),
        "low_risk_count": random.randint(2, 10),
        "total_findings": 0,
        "compliance_score": random.randint(60, 95),
        "technologies_detected": ["Terraform", "CloudFormation", "Kubernetes", "Docker"],
        "scan_status": "success"
    }
    
    # Generate random findings
    finding_types = ["PII Exposure", "Insecure Configuration", "Missing Encryption", 
                     "Data Retention Policy", "Authentication Issue", "Authorization Gap"]
    
    for i in range(results["total_findings"]):
        severity = random.choice(["high", "medium", "low"])
        results["findings"].append({
            "id": f"FIND-{i+1}",
            "title": random.choice(finding_types),
            "description": f"Finding description for issue #{i+1}",
            "severity": severity,
            "location": f"location/path/file{i}.py",
            "remediation": "Suggested fix for this issue..."
        })
    
    return results

# Main application
def main():
    # 2025 Modern Sidebar Design
    with st.sidebar:
        # New Premium Brand Identity
        st.markdown("""
        <div style="padding: 20px 0 30px 0; text-align: center;">
            <div class="card" style="
                background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                border-radius: 24px;
                padding: 24px 20px;
                margin-bottom: 20px;
                position: relative;
                overflow: hidden;
                border: none;
                box-shadow: 0 20px 40px rgba(15, 23, 42, 0.2);
            ">
                <!-- Abstract shapes background -->
                <div style="position: absolute; width: 150px; height: 150px; border-radius: 75px; background: radial-gradient(circle, rgba(99,102,241,0.2) 0%, rgba(99,102,241,0) 70%); top: -75px; right: -75px;"></div>
                <div style="position: absolute; width: 100px; height: 100px; border-radius: 50px; background: radial-gradient(circle, rgba(139,92,246,0.15) 0%, rgba(139,92,246,0) 70%); bottom: -50px; left: -25px;"></div>
                
                <!-- Logo Container -->
                <div style="
                    position: relative;
                    z-index: 5;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-bottom: 16px;
                ">
                    <!-- Shield Icon -->
                    <div style="
                        width: 48px;
                        height: 48px;
                        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
                        border-radius: 14px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-right: 14px;
                        box-shadow: 0 10px 25px rgba(139, 92, 246, 0.3);
                    ">
                        <span style="font-size: 24px; color: white; filter: drop-shadow(0 2px 5px rgba(0,0,0,0.2));">🛡️</span>
                    </div>
                    
                    <!-- Brand Name -->
                    <div style="text-align: left;">
                        <h1 style="
                            font-weight: 800; 
                            font-size: 22px; 
                            color: white; 
                            margin: 0;
                            padding: 0;
                            line-height: 1.1;
                            letter-spacing: -0.02em;
                        ">DataGuardian</h1>
                        <div style="
                            display: flex;
                            align-items: center;
                            margin-top: 2px;
                        ">
                            <span style="
                                font-weight: 700; 
                                font-size: 12px;
                                background: linear-gradient(90deg, #3b82f6, #8b5cf6);
                                -webkit-background-clip: text !important;
                                -webkit-text-fill-color: transparent !important;
                                background-clip: text !important;
                                color: transparent !important;
                                display: inline-block !important;
                                text-transform: uppercase;
                                letter-spacing: 0.1em;
                            ">Pro</span>
                            <span style="
                                background: linear-gradient(90deg, #f59e0b, #fbbf24);
                                color: #0f172a;
                                font-size: 10px;
                                font-weight: 700;
                                padding: 3px 8px;
                                border-radius: 20px;
                                margin-left: 8px;
                                text-transform: uppercase;
                                letter-spacing: 0.05em;
                            ">Enterprise</span>
                        </div>
                    </div>
                </div>
                
                <!-- Tagline -->
                <div style="
                    font-size: 12px;
                    font-weight: 500;
                    color: #94a3b8;
                    margin-top: 8px;
                    letter-spacing: 0.02em;
                    line-height: 1.4;
                ">Advanced AI-Powered Privacy Compliance Platform</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.logged_in:
            st.markdown("""
            <div class="card" style="padding: 24px; margin-bottom: 20px;">
                <h2 style="font-size: 18px; font-weight: 700; margin-bottom: 20px; color: #0f172a;">Sign In</h2>
            </div>
            """, unsafe_allow_html=True)
            
            username = st.text_input("Username", key="login_username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                remember = st.checkbox("Remember me", value=True, key="remember_me_checkbox")
            with col2:
                st.markdown('<div style="text-align: right;"><a href="#" style="color: #4f46e5; font-size: 14px; text-decoration: none;">Forgot password?</a></div>', unsafe_allow_html=True)
            
            login_button = st.button("Sign In", key="login_button", use_container_width=True)
            
            if login_button:
                if not username or not password:
                    st.error("Please enter both username and password")
                else:
                    user_data = authenticate(username, password)
                    if user_data:
                        st.session_state.logged_in = True
                        st.session_state.username = user_data["username"]
                        st.session_state.role = user_data["role"]
                        st.session_state.email = user_data.get("email", "")
                        st.session_state.permissions = user_data.get("permissions", [])
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
            
            st.markdown("""
            <div style="text-align: center; margin-top: 15px; font-size: 14px; color: #64748b;">
                Demo accounts: <code>admin/password</code> or <code>user/password</code>
            </div>
            """, unsafe_allow_html=True)
        else:
            # User Profile Card
            st.markdown(f"""
            <div class="card" style="padding: 20px; margin-bottom: 24px;">
                <div style="display: flex; align-items: center; margin-bottom: 16px;">
                    <div style="
                        width: 48px;
                        height: 48px;
                        border-radius: 24px;
                        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-right: 12px;
                        font-size: 16px;
                        color: white;
                        font-weight: 600;
                    ">{st.session_state.username[0].upper()}</div>
                    <div>
                        <div style="font-weight: 700; font-size: 16px; color: #0f172a; line-height: 1.2;">
                            {st.session_state.username}
                        </div>
                        <div style="font-size: 14px; color: #64748b;">
                            {st.session_state.email}
                        </div>
                    </div>
                </div>
                
                <div style="
                    display: flex;
                    align-items: center;
                    padding: 8px 12px;
                    background: rgba(79, 70, 229, 0.1);
                    border-radius: 8px;
                    margin-bottom: 16px;
                ">
                    <div style="
                        width: 24px;
                        height: 24px;
                        border-radius: 12px;
                        background: #4f46e5;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-right: 10px;
                        font-size: 10px;
                        color: white;
                    ">
                        <span style="display: inline-block; transform: translateY(-1px);">👑</span>
                    </div>
                    <div style="font-weight: 600; font-size: 14px; color: #4f46e5;">
                        {st.session_state.role.title()} Account
                    </div>
                </div>
            </div>
            """
            , unsafe_allow_html=True)
            
            # Modern subscription status display
            st.markdown("### Your Subscription", help="Manage your subscription plan")
            
            current_plan = st.session_state.get("subscription_tier", "basic")
            
            # Display appropriate plan card based on subscription
            if current_plan == "basic":
                st.markdown(f"""
                <div style='background-color: white; padding: 15px; border-radius: 10px; 
                            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06); border: 1px solid #f0f0f0;
                            margin-bottom: 15px;'>
                    <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                        <div style='background-color: #EBF4FF; border-radius: 50%; width: 24px; height: 24px; 
                                    display: flex; align-items: center; justify-content: center; margin-right: 10px;'>
                            <span style='color: #2C5282; font-weight: bold; font-size: 12px;'>B</span>
                        </div>
                        <div style='color: #2C5282; font-weight: 600; font-size: 16px;'>{SUBSCRIPTION_PLANS['basic']['name']}</div>
                    </div>
                    <div style='color: #2C5282; font-weight: 700; font-size: 20px; margin-bottom: 5px;'>${SUBSCRIPTION_PLANS['basic']['price']}<span style='color: #718096; font-weight: 400; font-size: 14px;'>/month</span></div>
                    <div style='color: #718096; font-size: 13px; margin-bottom: 15px;'>Your plan renews on May 12, 2025</div>
                    <button style='background-color: #0b3d91; color: white; border: none; border-radius: 6px; 
                                   padding: 8px 16px; width: 100%; font-weight: 600; cursor: pointer;
                                   transition: all 0.3s ease;'
                            onmouseover="this.style.backgroundColor='#1853b3'"
                            onmouseout="this.style.backgroundColor='#0b3d91'">
                        Upgrade to Premium
                    </button>
                </div>
                """, unsafe_allow_html=True)
                
            elif current_plan == "premium":
                st.markdown(f"""
                <div style='background-color: white; padding: 15px; border-radius: 10px; 
                            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06); border: 1px solid #3B82F6;
                            margin-bottom: 15px;'>
                    <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                        <div style='background-color: #2C5282; border-radius: 50%; width: 24px; height: 24px; 
                                    display: flex; align-items: center; justify-content: center; margin-right: 10px;'>
                            <span style='color: white; font-weight: bold; font-size: 12px;'>P</span>
                        </div>
                        <div style='color: #2C5282; font-weight: 600; font-size: 16px;'>{SUBSCRIPTION_PLANS['premium']['name']}</div>
                    </div>
                    <div style='color: #2C5282; font-weight: 700; font-size: 20px; margin-bottom: 5px;'>${SUBSCRIPTION_PLANS['premium']['price']}<span style='color: #718096; font-weight: 400; font-size: 14px;'>/month</span></div>
                    <div style='color: #718096; font-size: 13px; margin-bottom: 15px;'>Your plan renews on May 12, 2025</div>
                    <button style='background-color: #0b3d91; color: white; border: none; border-radius: 6px; 
                                  padding: 8px 16px; width: 100%; font-weight: 600; cursor: pointer;
                                  transition: all 0.3s ease;'
                           onmouseover="this.style.backgroundColor='#1853b3'"
                           onmouseout="this.style.backgroundColor='#0b3d91'">
                        Upgrade to Gold
                    </button>
                </div>
                """, unsafe_allow_html=True)
                
            elif current_plan == "gold":
                st.markdown(f"""
                <div style='background-color: white; padding: 15px; border-radius: 10px; 
                            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06); border: 1px solid #F59E0B;
                            margin-bottom: 15px;'>
                    <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                        <div style='background-color: #F59E0B; border-radius: 50%; width: 24px; height: 24px; 
                                    display: flex; align-items: center; justify-content: center; margin-right: 10px;'>
                            <span style='color: white; font-weight: bold; font-size: 12px;'>G</span>
                        </div>
                        <div style='color: #92400E; font-weight: 600; font-size: 16px;'>{SUBSCRIPTION_PLANS['gold']['name']}</div>
                    </div>
                    <div style='color: #92400E; font-weight: 700; font-size: 20px; margin-bottom: 5px;'>${SUBSCRIPTION_PLANS['gold']['price']}<span style='color: #718096; font-weight: 400; font-size: 14px;'>/month</span></div>
                    <div style='color: #718096; font-size: 13px; margin-bottom: 15px;'>Your plan renews on May 12, 2025</div>
                    <div style='background-color: #FEF3C7; color: #92400E; border-radius: 6px; 
                               padding: 8px 16px; text-align: center; font-weight: 600; font-size: 14px;'>
                        ✓ You're on our highest tier
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Payment & Billing section with improved design
            st.markdown("### Billing", help="Manage your payment methods and billing history")
            
            # Payment method
            st.markdown("""
            <div style='background-color: white; padding: 15px; border-radius: 10px; 
                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06); border: 1px solid #f0f0f0;
                        margin-bottom: 15px;'>
                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;'>
                    <div style='font-weight: 600; color: #2C5282;'>Payment Method</div>
                    <div style='font-size: 12px; color: #3B82F6; cursor: pointer;'>+ Add New</div>
                </div>
                <div style='display: flex; align-items: center;'>
                    <div style='background-color: #F8F9FA; border-radius: 6px; padding: 10px; margin-right: 10px;'>
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <rect width="24" height="24" rx="4" fill="#0B3D91" fill-opacity="0.1"/>
                            <path d="M5 11H19V17C19 17.5523 18.5523 18 18 18H6C5.44772 18 5 17.5523 5 17V11Z" fill="#0B3D91" fill-opacity="0.1"/>
                            <path d="M5 8C5 7.44772 5.44772 7 6 7H18C18.5523 7 19 7.44772 19 8V11H5V8Z" fill="#0B3D91"/>
                            <path d="M7 14.5C7 14.2239 7.22386 14 7.5 14H10.5C10.7761 14 11 14.2239 11 14.5C11 14.7761 10.7761 15 10.5 15H7.5C7.22386 15 7 14.7761 7 14.5Z" fill="#0B3D91"/>
                            <path d="M13 14.5C13 14.2239 13.2239 14 13.5 14H15.5C15.7761 14 16 14.2239 16 14.5C16 14.7761 15.7761 15 15.5 15H13.5C13.2239 15 13 14.7761 13 14.5Z" fill="#0B3D91"/>
                        </svg>
                    </div>
                    <div>
                        <div style='font-weight: 500; color: #2D3748;'>•••• •••• •••• 4242</div>
                        <div style='font-size: 12px; color: #718096;'>Expires 12/2025</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Billing history
            st.markdown("""
            <div style='background-color: white; padding: 15px; border-radius: 10px; 
                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06); border: 1px solid #f0f0f0;'>
                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;'>
                    <div style='font-weight: 600; color: #2C5282;'>Recent Invoices</div>
                    <div style='font-size: 12px; color: #3B82F6; cursor: pointer;'>View All</div>
                </div>
                <div style='color: #718096; text-align: center; padding: 20px 0;'>
                    <div style='margin-bottom: 8px; opacity: 0.6;'>
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin: 0 auto; display: block;">
                            <path d="M9 5H7C5.89543 5 5 5.89543 5 7V19C5 20.1046 5.89543 21 7 21H17C18.1046 21 19 20.1046 19 19V7C19 5.89543 18.1046 5 17 5H15" stroke="#718096" stroke-width="2" stroke-linecap="round"/>
                            <path d="M9 5C9 3.89543 9.89543 3 11 3H13C14.1046 3 15 3.89543 15 5C15 6.10457 14.1046 7 13 7H11C9.89543 7 9 6.10457 9 5Z" stroke="#718096" stroke-width="2"/>
                            <path d="M9 12H15" stroke="#718096" stroke-width="2" stroke-linecap="round"/>
                            <path d="M9 16H15" stroke="#718096" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                    </div>
                    <div style='font-size: 14px;'>No invoices yet</div>
                    <div style='font-size: 12px; margin-top: 4px;'>Your billing history will appear here</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.divider()
            
            if st.button("Logout", key="logout_button"):
                for key in st.session_state.keys():
                    del st.session_state[key]
                st.rerun()
    
    # Main content
    if not st.session_state.logged_in:
        # Enhanced landing page with hero section
        st.markdown("""
        <div style="
            text-align: center;
            padding: 40px 0;
            background: linear-gradient(135deg, rgba(240,244,255,0.8) 0%, rgba(230,240,255,0.8) 100%);
            border-radius: 24px;
            margin-bottom: 40px;
            box-shadow: 0 10px 30px rgba(79, 70, 229, 0.06);
            position: relative;
            overflow: hidden;
        ">
            <!-- Decorative elements -->
            <div style="position: absolute; width: 300px; height: 300px; border-radius: 50%; background: radial-gradient(circle, rgba(79,70,229,0.05) 0%, rgba(79,70,229,0) 70%); top: -150px; right: -100px;"></div>
            <div style="position: absolute; width: 200px; height: 200px; border-radius: 50%; background: radial-gradient(circle, rgba(245,158,11,0.05) 0%, rgba(245,158,11,0) 70%); bottom: -100px; left: -50px;"></div>
            
            <!-- Content -->
            <h1 style="
                font-size: 3.5rem;
                font-weight: 800;
                margin-bottom: 15px;
                background: linear-gradient(120deg, #0b3d91 0%, #4f46e5 50%, #7c3aed 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                padding: 0 20px;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                letter-spacing: -1px;
                line-height: 1.1;
            ">
                DataGuardian Pro
            </h1>
            
            <p style="
                font-size: 1.5rem;
                color: #4b5563;
                max-width: 700px;
                margin: 0 auto 30px auto;
                font-weight: 400;
                padding: 0 20px;
            ">
                The most comprehensive enterprise privacy compliance platform
            </p>
            
            <!-- Feature badges -->
            <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 12px; margin-bottom: 30px; padding: 0 20px;">
                <span style="
                    background: rgba(79, 70, 229, 0.1);
                    color: #4f46e5;
                    padding: 8px 16px;
                    border-radius: 50px;
                    font-size: 0.9rem;
                    font-weight: 600;
                ">
                    GDPR Compliant
                </span>
                
                <span style="
                    background: rgba(14, 165, 233, 0.1);
                    color: #0ea5e9;
                    padding: 8px 16px;
                    border-radius: 50px;
                    font-size: 0.9rem;
                    font-weight: 600;
                ">
                    SOC2 Ready
                </span>
                
                <span style="
                    background: rgba(245, 158, 11, 0.1);
                    color: #f59e0b;
                    padding: 8px 16px;
                    border-radius: 50px;
                    font-size: 0.9rem;
                    font-weight: 600;
                ">
                    AI-Powered
                </span>
                
                <span style="
                    background: rgba(16, 185, 129, 0.1);
                    color: #10b981;
                    padding: 8px 16px;
                    border-radius: 50px;
                    font-size: 0.9rem;
                    font-weight: 600;
                ">
                    Cloud Native
                </span>
            </div>
            
            <!-- Action buttons with proper spacing -->
            <div style="display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; margin-top: 20px; padding: 0 20px;">
                <a href="#sign-in" style="
                    background: linear-gradient(120deg, #0b3d91 0%, #4f46e5 100%);
                    color: white;
                    font-weight: 600;
                    padding: 14px 32px;
                    border-radius: 8px;
                    text-decoration: none;
                    display: inline-block;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
                    font-size: 1.1rem;
                ">
                    Get Started
                </a>
                
                <a href="#plans" style="
                    background: white;
                    color: #4f46e5;
                    font-weight: 600;
                    padding: 14px 32px;
                    border-radius: 8px;
                    text-decoration: none;
                    display: inline-block;
                    transition: all 0.3s ease;
                    border: 1px solid rgba(79, 70, 229, 0.3);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
                    font-size: 1.1rem;
                ">
                    View Plans
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Auth tabs
        auth_tabs = st.tabs(["Sign In", "Register", "Plans"])
        
        # Sign In tab
        with auth_tabs[0]:
            # Enhanced sign in container
            st.markdown("""
            <div class="auth-container">
                <h2 class="form-header">Sign in to your account</h2>
                
                <!-- Google Sign In button -->
                <button class="google-login-button">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg" 
                         style="height: 20px; margin-right: 12px; vertical-align: middle;"> 
                    Sign in with Google
                </button>
                
                <!-- Divider -->
                <div class="divider"><span class="divider-text">OR CONTINUE WITH EMAIL</span></div>
            </div>
            """, unsafe_allow_html=True)
            
            # Email login form
            col1, col2 = st.columns([3, 1])
            with col1:
                email = st.text_input("Email", key="login_email", placeholder="Your email address")
            with col2:
                st.write("")  # For spacing
            
            password = st.text_input("Password", type="password", key="login_password_email", placeholder="Your password")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                remember = st.checkbox("Remember me", value=True)
            with col2:
                st.markdown('<div style="text-align: right; margin-top: 5px;"><a href="#" style="color: #4f46e5; text-decoration: none; font-size: 0.9rem; font-weight: 500;">Forgot password?</a></div>', unsafe_allow_html=True)
            
            # Button with plenty of spacing
            st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
            if st.button("Sign In", key="signin_button", use_container_width=True):
                if not email or not password:
                    st.error("Please enter both email and password")
                elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    st.error("Please enter a valid email address")
                else:
                    # In a real app, validate credentials against database
                    # For now just set as logged in if email format is valid
                    st.session_state.logged_in = True
                    st.session_state.username = email.split('@')[0]
                    st.session_state.role = "user"
                    st.session_state.email = email
                    st.session_state.permissions = ["scan:basic", "report:view"]
                    st.success("Login successful!")
                    st.rerun()
            
            st.markdown('<div style="text-align: center; margin-top: 20px;"><span style="color: #64748b; font-size: 0.9rem;">Don\'t have an account?</span> <a href="#" style="color: #4f46e5; text-decoration: none; font-weight: 500;">Sign up</a></div>', unsafe_allow_html=True)
        
        # Register tab
        with auth_tabs[1]:
            # Enhanced registration container
            st.markdown("""
            <div class="auth-container">
                <h2 class="form-header">Create your account</h2>
                
                <!-- Google Registration button -->
                <button class="google-login-button">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg" 
                         style="height: 20px; margin-right: 12px; vertical-align: middle;"> 
                    Register with Google
                </button>
                
                <!-- Divider -->
                <div class="divider"><span class="divider-text">OR REGISTER WITH EMAIL</span></div>
            </div>
            """, unsafe_allow_html=True)
            
            # Email registration form with proper spacing
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name", key="reg_first_name", placeholder="Your first name")
            with col2:
                last_name = st.text_input("Last Name", key="reg_last_name", placeholder="Your last name")
            
            email = st.text_input("Work Email", key="reg_email", placeholder="you@company.com")
            password = st.text_input("Password", type="password", key="reg_password", placeholder="Create a strong password")
            company = st.text_input("Company (Optional)", key="reg_company", placeholder="Your organization")
            
            st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
            terms = st.checkbox("I agree to the Terms of Service and Privacy Policy", key="reg_terms")
            
            # Button with plenty of spacing
            st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
            if st.button("Create Account", key="register_button", use_container_width=True):
                if not first_name or not last_name or not email or not password:
                    st.error("Please fill in all required fields")
                elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    st.error("Please enter a valid email address")
                elif not terms:
                    st.error("You must agree to the Terms of Service and Privacy Policy")
                else:
                    # In a real app, create user in database
                    st.success("Account created successfully! Please sign in.")
                    # Switch to sign in tab
                    st.session_state.active_tab = "login"
            
            st.markdown('<div style="text-align: center; margin-top: 20px;"><span style="color: #64748b; font-size: 0.9rem;">Already have an account?</span> <a href="#" style="color: #4f46e5; text-decoration: none; font-weight: 500;">Sign in</a></div>', unsafe_allow_html=True)
                    
        # Plans tab with enhanced styling
        with auth_tabs[2]:
            st.markdown("""
            <div style="text-align: center; margin-bottom: 40px;">
                <h2 style="font-size: 2.2rem; font-weight: 700; color: #1e293b; margin-bottom: 15px;">Choose the right plan for your needs</h2>
                <p style="color: #64748b; max-width: 600px; margin: 0 auto;">Our flexible plans are designed to meet the needs of businesses of all sizes, from startups to enterprises.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Display subscription plans with enhanced styling
            plan_cols = st.columns(3)
            
            # Basic plan
            with plan_cols[0]:
                st.markdown(f"""
                <div class="plan-card basic">
                    <div class="plan-name">{SUBSCRIPTION_PLANS['basic']['name']}</div>
                    <div class="plan-price">${SUBSCRIPTION_PLANS['basic']['price']}<span class="plan-price-period">/month</span></div>
                    <div class="plan-features">
                        {''.join([f'<div class="plan-feature-item">{feature}</div>' for feature in SUBSCRIPTION_PLANS['basic']['features']])}
                    </div>
                    <a href="#" class="subscribe-button">Subscribe Now</a>
                </div>
                """, unsafe_allow_html=True)
            
            # Premium plan with popular badge
            with plan_cols[1]:
                st.markdown(f"""
                <div class="plan-card premium">
                    <div class="popular-badge">Popular</div>
                    <div class="plan-name">{SUBSCRIPTION_PLANS['premium']['name']}</div>
                    <div class="plan-price">${SUBSCRIPTION_PLANS['premium']['price']}<span class="plan-price-period">/month</span></div>
                    <div class="plan-features">
                        {''.join([f'<div class="plan-feature-item">{feature}</div>' for feature in SUBSCRIPTION_PLANS['premium']['features']])}
                    </div>
                    <a href="#" class="subscribe-button">Subscribe Now</a>
                </div>
                """, unsafe_allow_html=True)
            
            # Gold plan
            with plan_cols[2]:
                st.markdown(f"""
                <div class="plan-card gold">
                    <div class="plan-name">{SUBSCRIPTION_PLANS['gold']['name']}</div>
                    <div class="plan-price">${SUBSCRIPTION_PLANS['gold']['price']}<span class="plan-price-period">/month</span></div>
                    <div class="plan-features">
                        {''.join([f'<div class="plan-feature-item">{feature}</div>' for feature in SUBSCRIPTION_PLANS['gold']['features']])}
                    </div>
                    <a href="#" class="subscribe-button">Subscribe Now</a>
                </div>
                """, unsafe_allow_html=True)
            
            # Enhanced pricing note
            st.markdown("""
            <div style="
                background: linear-gradient(to right, rgba(14, 165, 233, 0.05), rgba(79, 70, 229, 0.05));
                padding: 20px;
                border-radius: 12px;
                text-align: center;
                margin-top: 20px;
                border: 1px solid rgba(79, 70, 229, 0.1);
            ">
                <div style="color: #4f46e5; font-weight: 600; margin-bottom: 5px;">All plans include a 14-day free trial</div>
                <div style="color: #64748b;">No credit card required to get started. Cancel anytime.</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Feature highlights section with enhanced styling
        st.markdown("""
        <div style="margin: 60px 0;">
            <h2 style="font-size: 2.2rem; font-weight: 700; color: #1e293b; margin-bottom: 40px; text-align: center;">Why Choose DataGuardian Pro?</h2>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px;">
                <!-- Feature 1 -->
                <div style="
                    background: white;
                    border-radius: 16px;
                    padding: 30px;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
                    transition: all 0.3s ease;
                ">
                    <div style="
                        width: 60px;
                        height: 60px;
                        border-radius: 12px;
                        background: linear-gradient(120deg, #0ea5e9 0%, #38bdf8 100%);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 24px;
                        color: white;
                        margin-bottom: 20px;
                    ">📊</div>
                    <h3 style="font-size: 1.3rem; font-weight: 700; color: #1e293b; margin-bottom: 10px;">
                        Multi-Service Scanning
                    </h3>
                    <p style="color: #64748b; line-height: 1.6;">
                        Comprehensive scanning of code, API, database, and AI models to detect privacy risks and compliance issues.
                    </p>
                </div>
                
                <!-- Feature 2 -->
                <div style="
                    background: white;
                    border-radius: 16px;
                    padding: 30px;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
                    transition: all 0.3s ease;
                ">
                    <div style="
                        width: 60px;
                        height: 60px;
                        border-radius: 12px;
                        background: linear-gradient(120deg, #4f46e5 0%, #7c3aed 100%);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 24px;
                        color: white;
                        margin-bottom: 20px;
                    ">🧠</div>
                    <h3 style="font-size: 1.3rem; font-weight: 700; color: #1e293b; margin-bottom: 10px;">
                        AI-Powered Risk Detection
                    </h3>
                    <p style="color: #64748b; line-height: 1.6;">
                        Machine learning algorithms that detect and prioritize privacy risks with higher accuracy than traditional methods.
                    </p>
                </div>
                
                <!-- Feature 3 -->
                <div style="
                    background: white;
                    border-radius: 16px;
                    padding: 30px;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
                    transition: all 0.3s ease;
                ">
                    <div style="
                        width: 60px;
                        height: 60px;
                        border-radius: 12px;
                        background: linear-gradient(120deg, #f59e0b 0%, #fbbf24 100%);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 24px;
                        color: white;
                        margin-bottom: 20px;
                    ">📝</div>
                    <h3 style="font-size: 1.3rem; font-weight: 700; color: #1e293b; margin-bottom: 10px;">
                        Detailed Compliance Reporting
                    </h3>
                    <p style="color: #64748b; line-height: 1.6;">
                        Generate comprehensive compliance reports with actionable insights and remediation recommendations.
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Call to action section
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #0b3d91 0%, #4f46e5 50%, #7c3aed 100%);
            padding: 60px 40px;
            border-radius: 24px;
            text-align: center;
            color: white;
            margin: 60px 0 40px 0;
            box-shadow: 0 10px 30px rgba(79, 70, 229, 0.2);
        ">
            <h2 style="
                font-size: 2.4rem;
                font-weight: 700;
                margin-bottom: 20px;
                max-width: 700px;
                margin-left: auto;
                margin-right: auto;
            ">Ready to take control of your data privacy?</h2>
            
            <p style="
                font-size: 1.2rem;
                opacity: 0.9;
                max-width: 600px;
                margin: 0 auto 30px auto;
            ">
                Join thousands of companies that trust DataGuardian Pro to secure their data and ensure compliance.
            </p>
            
            <a href="#" style="
                background: white;
                color: #4f46e5;
                font-weight: 600;
                padding: 16px 36px;
                border-radius: 12px;
                text-decoration: none;
                display: inline-block;
                transition: all 0.3s ease;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                font-size: 1.1rem;
                margin: 0 10px;
            ">
                Start Free Trial
            </a>
            
            <a href="#" style="
                background: rgba(255, 255, 255, 0.1);
                color: white;
                font-weight: 600;
                padding: 16px 36px;
                border-radius: 12px;
                text-decoration: none;
                display: inline-block;
                transition: all 0.3s ease;
                border: 1px solid rgba(255, 255, 255, 0.2);
                font-size: 1.1rem;
                margin: 0 10px;
            ">
                Contact Sales
            </a>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Create tabs
        tabs = st.tabs(["Dashboard", "Scan", "Reports", "Admin"])
        
        # Dashboard Tab
        with tabs[0]:
            st.markdown("<h2>Analytics Dashboard</h2>", unsafe_allow_html=True)
            
            # Modern dashboard header with stats
            st.markdown("""
            <div style="background: linear-gradient(135deg, #0b3d91 0%, #2c5282 100%); padding: 20px; border-radius: 12px; margin-bottom: 24px; color: white;">
                <h3 style="margin: 0 0 15px 0; font-weight: 600; font-size: 18px;">Dashboard Overview</h3>
                <div style="display: flex; justify-content: space-between; flex-wrap: wrap;">
                    <div style="flex: 1; min-width: 120px; background-color: rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 16px; margin: 0 8px 8px 0;">
                        <div style="font-size: 28px; font-weight: 700;">{random.randint(10, 100)}</div>
                        <div style="font-size: 14px; opacity: 0.8;">Total Scans</div>
                    </div>
                    <div style="flex: 1; min-width: 120px; background-color: rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 16px; margin: 0 8px 8px 0;">
                        <div style="font-size: 28px; font-weight: 700;">{random.randint(5, 50)}</div>
                        <div style="font-size: 14px; opacity: 0.8;">Open Issues</div>
                    </div>
                    <div style="flex: 1; min-width: 120px; background-color: rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 16px; margin: 0 8px 8px 0;">
                        <div style="font-size: 28px; font-weight: 700;">{random.randint(70, 95)}%</div>
                        <div style="font-size: 14px; opacity: 0.8;">Avg. Compliance</div>
                    </div>
                    <div style="flex: 1; min-width: 120px; background-color: rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 16px; margin: 0 0 8px 0;">
                        <div style="font-size: 28px; font-weight: 700;">{random.randint(10, 40)}/100</div>
                        <div style="font-size: 14px; opacity: 0.8;">Risk Score</div>
                    </div>
                </div>
            </div>
            """
            , unsafe_allow_html=True)
            
            # Additional dashboard content in cards
            col1, col2 = st.columns(2)
            
            # Compliance Trend Card
            with col1:
                st.markdown("""
                <div style="background: white; border-radius: 12px; padding: 20px; height: 250px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06); margin-bottom: 24px;">
                    <h3 style="margin: 0 0 20px 0; font-weight: 600; font-size: 16px; color: #2C5282;">Compliance Score Trend</h3>
                    <div style="display: flex; align-items: flex-end; height: 150px; padding-bottom: 20px; position: relative;">
                        <div style="position: absolute; left: 0; right: 0; bottom: 20px; height: 1px; background-color: #E2E8F0;"></div>
                        <div style="flex: 1; position: relative; height: 75%;">
                            <div style="position: absolute; left: 0; right: 0; bottom: 0; height: 100%; background: linear-gradient(to top, #0b3d91, #3B82F6); border-radius: 4px 4px 0 0;"></div>
                        </div>
                        <div style="flex: 1; position: relative; height: 60%; margin: 0 2px;">
                            <div style="position: absolute; left: 0; right: 0; bottom: 0; height: 100%; background: linear-gradient(to top, #0b3d91, #3B82F6); border-radius: 4px 4px 0 0;"></div>
                        </div>
                        <div style="flex: 1; position: relative; height: 80%; margin: 0 2px;">
                            <div style="position: absolute; left: 0; right: 0; bottom: 0; height: 100%; background: linear-gradient(to top, #0b3d91, #3B82F6); border-radius: 4px 4px 0 0;"></div>
                        </div>
                        <div style="flex: 1; position: relative; height: 70%; margin: 0 2px;">
                            <div style="position: absolute; left: 0; right: 0; bottom: 0; height: 100%; background: linear-gradient(to top, #0b3d91, #3B82F6); border-radius: 4px 4px 0 0;"></div>
                        </div>
                        <div style="flex: 1; position: relative; height: 90%; margin: 0 2px;">
                            <div style="position: absolute; left: 0; right: 0; bottom: 0; height: 100%; background: linear-gradient(to top, #0b3d91, #3B82F6); border-radius: 4px 4px 0 0;"></div>
                        </div>
                        <div style="flex: 1; position: relative; height: 85%;">
                            <div style="position: absolute; left: 0; right: 0; bottom: 0; height: 100%; background: linear-gradient(to top, #0b3d91, #3B82F6); border-radius: 4px 4px 0 0;"></div>
                        </div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                        <span style="font-size: 12px; color: #718096;">Mar</span>
                        <span style="font-size: 12px; color: #718096;">Apr</span>
                        <span style="font-size: 12px; color: #0b3d91; font-weight: 600;">May</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Risk Distribution Card
            with col2:
                st.markdown("""
                <div style="background: white; border-radius: 12px; padding: 20px; height: 250px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06); margin-bottom: 24px;">
                    <h3 style="margin: 0 0 20px 0; font-weight: 600; font-size: 16px; color: #2C5282;">Risk Distribution</h3>
                    <div style="display: flex; height: 150px; align-items: center; justify-content: space-around;">
                        <div style="text-align: center;">
                            <div style="width: 80px; height: 80px; border-radius: 50%; background-color: #FEE2E2; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px auto;">
                                <span style="font-size: 24px; font-weight: 700; color: #B91C1C;">{random.randint(3, 8)}</span>
                            </div>
                            <div style="font-size: 14px; color: #B91C1C; font-weight: 600;">High</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="width: 80px; height: 80px; border-radius: 50%; background-color: #FEF3C7; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px auto;">
                                <span style="font-size: 24px; font-weight: 700; color: #92400E;">{random.randint(10, 20)}</span>
                            </div>
                            <div style="font-size: 14px; color: #92400E; font-weight: 600;">Medium</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="width: 80px; height: 80px; border-radius: 50%; background-color: #ECFDF5; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px auto;">
                                <span style="font-size: 24px; font-weight: 700; color: #047857;">{random.randint(15, 30)}</span>
                            </div>
                            <div style="font-size: 14px; color: #047857; font-weight: 600;">Low</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Recent scans
            st.subheader("Recent Scans")
            if not st.session_state.scan_history:
                st.info("No scan history available. Run a scan to see results here.")
            else:
                scan_df = pd.DataFrame([
                    {
                        "Date": datetime.fromisoformat(scan["timestamp"]).strftime("%Y-%m-%d %H:%M"),
                        "Type": scan["scan_type"],
                        "Findings": scan["total_findings"],
                        "High Risk": scan["high_risk"],
                        "Medium Risk": scan["medium_risk"],
                        "Low Risk": scan["low_risk"],
                        "Compliance Score": f"{scan['compliance_score']}%"
                    } for scan in st.session_state.scan_history
                ])
                st.dataframe(scan_df, use_container_width=True)
        
        # Scan Tab
        with tabs[1]:
            st.markdown("<h2>Privacy Scan</h2>", unsafe_allow_html=True)
            
            scan_types = [
                "Code Scanner", 
                "Blob Scanner", 
                "Image Scanner", 
                "Database Scanner", 
                "API Scanner", 
                "Website Scanner", 
                "AI Model Scanner", 
                "DPIA Assessment",
                "SOC2 Scanner",
                "Sustainability Scanner"
            ]
            
            selected_scan = st.selectbox("Select Scan Type", scan_types)
            
            # Common scan options
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Repository URL", value="https://github.com/example/repo", key="repo_url")
                st.text_input("Branch", value="main", key="branch")
            
            with col2:
                scan_options = ["Detect PII", "Check Compliance", "Generate Recommendations"]
                for option in scan_options:
                    st.checkbox(option, value=True, key=f"option_{option}")
            
            # Show specific options for each scanner type
            if selected_scan == "SOC2 Scanner":
                st.subheader("SOC2 Scanner Options")
                repo_type = st.radio("Repository Type", ["GitHub", "Azure DevOps"], horizontal=True)
                if repo_type == "Azure DevOps":
                    st.text_input("Project Name", key="project_name")
                    st.text_input("Organization", key="organization")
            
            elif selected_scan == "Sustainability Scanner":
                st.subheader("Sustainability Scanner Options")
                sustainability_scan_type = st.radio("Scan Type", ["Cloud Resources", "GitHub Repository", "Code Analysis"], horizontal=True)
                
                if sustainability_scan_type == "Cloud Resources":
                    st.selectbox("Cloud Provider", ["Azure", "AWS", "GCP"], key="cloud_provider")
                    st.selectbox("Region", ["Global", "East US", "West US", "Europe"], key="cloud_region")
                    
            if st.button("Start Scan", key="start_scan"):
                with st.spinner("Running scan..."):
                    progress_bar = st.progress(0)
                    
                    # Handle different scan types
                    if selected_scan == "SOC2 Scanner":
                        # Get inputs
                        repo_url = st.session_state.get("repo_url", "")
                        branch = st.session_state.get("branch", "main")
                        
                        # Update progress while simulating scan
                        for i in range(1, 101):
                            time.sleep(0.02)  # Faster simulation
                            progress_bar.progress(i)
                        
                        # Use the SOC2 scanner based on repository type
                        if repo_type == "GitHub":
                            results = soc2_scan_github(repo_url, branch)
                        else:
                            project = st.session_state.get("project_name", "")
                            organization = st.session_state.get("organization", "")
                            results = soc2_scan_azure(repo_url, project, branch, organization=organization)
                            
                        # For mock implementation, set the other required fields
                        if "total_findings" not in results:
                            results["total_findings"] = results.get("high_risk_count", 0) + results.get("medium_risk_count", 0) + results.get("low_risk_count", 0)
                        if "high_risk" not in results:
                            results["high_risk"] = results.get("high_risk_count", 0)
                        if "medium_risk" not in results:
                            results["medium_risk"] = results.get("medium_risk_count", 0)
                        if "low_risk" not in results:
                            results["low_risk"] = results.get("low_risk_count", 0)
                    
                    elif selected_scan == "Sustainability Scanner":
                        # Show the standalone Sustainability Scanner instead
                        try:
                            # Try to use the actual sustainability scanner
                            analyzer = SustainabilityAnalyzer()
                            results = {
                                "scan_type": "Sustainability Scanner",
                                "timestamp": datetime.now().isoformat(),
                                "scan_id": str(uuid.uuid4()),
                                "findings": [],
                                "total_findings": random.randint(5, 20),
                                "high_risk": random.randint(0, 5),
                                "medium_risk": random.randint(3, 8),
                                "low_risk": random.randint(2, 10),
                                "compliance_score": random.randint(60, 95),
                                "sustainability_analysis": analyzer.analyze()
                            }
                            
                            # Update progress
                            for i in range(1, 101):
                                time.sleep(0.02)  # Faster simulation
                                progress_bar.progress(i)
                        except Exception as e:
                            st.error(f"Error running Sustainability Scanner: {str(e)}")
                            # Fall back to mock results
                            results = generate_mock_scan_results(selected_scan)
                    else:
                        # For other scan types, use the standard approach
                        for i in range(1, 101):
                            time.sleep(0.05)  # Standard simulation
                            progress_bar.progress(i)
                        
                        # Generate mock results
                        results = generate_mock_scan_results(selected_scan)
                    
                    # Store the results
                    st.session_state.current_scan_results = results
                    
                    # Add to scan history
                    st.session_state.scan_history.insert(0, results)
                    if len(st.session_state.scan_history) > 5:
                        st.session_state.scan_history = st.session_state.scan_history[:5]
                
                st.success(f"{selected_scan} completed successfully!")
                
                # Display results
                if selected_scan == "SOC2 Scanner":
                    # Use the specialized SOC2 display function if available
                    try:
                        display_soc2_findings(results)
                    except:
                        st.json(results)
                elif selected_scan == "Sustainability Scanner":
                    # Display sustainability-specific results
                    if "sustainability_analysis" in results:
                        sustainability_score = results["sustainability_analysis"].get("sustainability_score", 0)
                        potential_savings = results["sustainability_analysis"].get("potential_savings", 0)
                        carbon_reduction = results["sustainability_analysis"].get("carbon_reduction", 0)
                        
                        st.subheader("Sustainability Analysis")
                        cols = st.columns(3)
                        with cols[0]:
                            st.metric("Sustainability Score", f"{sustainability_score}%")
                        with cols[1]:
                            st.metric("Potential Cost Savings", f"${potential_savings:,}")
                        with cols[2]:
                            st.metric("Carbon Reduction", f"{carbon_reduction}%")
                            
                        st.subheader("Detailed Findings")
                        st.json(results)
                    else:
                        st.json(results)
                else:
                    st.json(results)
        
        # Reports Tab
        with tabs[2]:
            st.markdown("<h2>Compliance Reports</h2>", unsafe_allow_html=True)
            
            if not st.session_state.scan_history:
                st.info("No scan history available. Run a scan to generate reports.")
            else:
                scan_options = [f"{scan['scan_type']} - {datetime.fromisoformat(scan['timestamp']).strftime('%Y-%m-%d %H:%M')}" 
                               for scan in st.session_state.scan_history]
                selected_report = st.selectbox("Select Scan for Report", scan_options, key="report_select")
                
                report_types = ["Summary Report", "Full Report", "Technical Report", "Executive Report"]
                report_format = st.radio("Report Format", report_types, horizontal=True)
                
                if st.button("Generate Report"):
                    with st.spinner("Generating report..."):
                        time.sleep(2)  # Simulate report generation
                        
                        # Get selected scan results
                        selected_index = scan_options.index(selected_report)
                        scan_data = st.session_state.scan_history[selected_index]
                        
                        st.subheader(f"{report_format}: {scan_data['scan_type']}")
                        
                        # Display report content
                        st.markdown(f"""
                        ## {scan_data['scan_type']} Compliance Report
                        **Generated:** {datetime.fromisoformat(scan_data['timestamp']).strftime('%Y-%m-%d %H:%M')}
                        
                        ### Summary
                        - **Total Findings:** {scan_data['total_findings']}
                        - **High Risk Issues:** {scan_data['high_risk']}
                        - **Medium Risk Issues:** {scan_data['medium_risk']}
                        - **Low Risk Issues:** {scan_data['low_risk']}
                        - **Overall Compliance Score:** {scan_data['compliance_score']}%
                        
                        ### Key Findings
                        """)
                        
                        # Display findings in a table
                        if scan_data['findings']:
                            findings_df = pd.DataFrame([
                                {
                                    "ID": finding["id"],
                                    "Title": finding["title"],
                                    "Severity": finding["severity"].upper(),
                                    "Location": finding["location"]
                                } for finding in scan_data['findings'][:5]  # Show top 5 findings
                            ])
                            st.dataframe(findings_df, use_container_width=True)
                        
                        # Add a download button (mock)
                        st.download_button(
                            label="Download Report (PDF)",
                            data="This would be a PDF report in a real application",
                            file_name=f"{scan_data['scan_type'].replace(' ', '_')}_report.pdf",
                            mime="application/pdf"
                        )
        
        # Admin Tab
        with tabs[3]:
            if "admin:all" in st.session_state.permissions:
                st.markdown("<h2>Administration</h2>", unsafe_allow_html=True)
                
                admin_tabs = st.tabs(["Users", "Settings", "Advanced"])
                
                # Users Tab
                with admin_tabs[0]:
                    st.subheader("User Management")
                    
                    # Mock user data
                    users = [
                        {"username": "admin", "role": "admin", "email": "admin@dataguardian.pro", "last_login": "2023-04-30 10:15"},
                        {"username": "user", "role": "viewer", "email": "user@dataguardian.pro", "last_login": "2023-04-29 14:22"},
                        {"username": "security", "role": "security_engineer", "email": "security@dataguardian.pro", "last_login": "2023-04-28 09:45"}
                    ]
                    
                    users_df = pd.DataFrame(users)
                    st.dataframe(users_df, use_container_width=True)
                    
                    # User creation form
                    with st.expander("Add New User"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.text_input("Username", key="new_username")
                            st.text_input("Email", key="new_email")
                        with col2:
                            st.text_input("Password", type="password", key="new_password")
                            st.selectbox("Role", ["admin", "security_engineer", "auditor", "viewer"], key="new_role")
                        
                        if st.button("Create User"):
                            st.success("User created successfully (mock)")
                
                # Settings Tab
                with admin_tabs[1]:
                    st.subheader("System Settings")
                    
                    settings_tabs = st.tabs(["General", "Security", "Integrations"])
                    
                    with settings_tabs[0]:
                        st.text_input("Company Name", value="Example Corporation")
                        st.number_input("Session Timeout (minutes)", min_value=5, max_value=120, value=30)
                        st.selectbox("Default Language", ["English", "Dutch", "French", "German", "Spanish"])
                    
                    with settings_tabs[1]:
                        st.checkbox("Enable 2FA", value=True)
                        st.checkbox("Enforce Password Complexity", value=True)
                        st.slider("Minimum Password Length", min_value=8, max_value=24, value=12)
                    
                    with settings_tabs[2]:
                        st.text_input("API Key", value="sk_test_*********************")
                        st.text_input("Webhook URL")
                        st.multiselect("Active Integrations", 
                                       ["GitHub", "GitLab", "Bitbucket", "Jira", "Slack", "Microsoft Teams"],
                                       ["GitHub", "Slack"])
                
                # Advanced Tab
                with admin_tabs[2]:
                    st.subheader("Advanced Settings")
                    
                    st.info("Note: Changes to advanced settings may require system restart")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.slider("Scan Threads", min_value=1, max_value=16, value=4)
                        st.checkbox("Enable Deep Scanning", value=False)
                        st.checkbox("Debug Mode", value=False)
                    
                    with col2:
                        st.selectbox("Log Level", ["ERROR", "WARNING", "INFO", "DEBUG"])
                        st.text_area("Custom Scan Rules")
                        
                    if st.button("Apply Settings"):
                        st.success("Settings applied successfully (mock)")
            else:
                st.warning("You do not have permission to access the administration section.")

if __name__ == "__main__":
    main()