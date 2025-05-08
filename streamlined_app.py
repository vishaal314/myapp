import streamlit as st
import pandas as pd
import time
import json
import os
import random
import uuid
from datetime import datetime
import base64

# =============================================================================
# CONFIGURATION
# =============================================================================

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
        "color": "blue", 
        "icon": "🔍",
        "stripe_price_id": "price_basic123"
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
        "color": "indigo",
        "icon": "⚡",
        "stripe_price_id": "price_premium456"
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
        "color": "amber",
        "icon": "👑",
        "stripe_price_id": "price_gold789"
    }
}

# Page configuration
st.set_page_config(
    page_title="DataGuardian Pro - Privacy Compliance Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# STYLES AND THEME
# =============================================================================

# CSS for overall styling
st.markdown("""
<style>
    /* Modern UI Theme */
    :root {
        --primary-color: #4f46e5;
        --primary-light: #818cf8;
        --primary-dark: #3730a3;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
        --gray-50: #f8fafc;
        --gray-100: #f1f5f9;
        --gray-200: #e2e8f0;
        --gray-300: #cbd5e1;
        --gray-400: #94a3b8;
        --gray-500: #64748b;
        --gray-600: #475569;
        --gray-700: #334155;
        --gray-800: #1e293b;
        --gray-900: #0f172a;
        --radius-sm: 0.375rem;
        --radius-md: 0.5rem;
        --radius-lg: 0.75rem;
        --radius-xl: 1rem;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    
    /* Typography */
    .text-xs { font-size: 0.75rem; line-height: 1rem; }
    .text-sm { font-size: 0.875rem; line-height: 1.25rem; }
    .text-base { font-size: 1rem; line-height: 1.5rem; }
    .text-lg { font-size: 1.125rem; line-height: 1.75rem; }
    .text-xl { font-size: 1.25rem; line-height: 1.75rem; }
    .text-2xl { font-size: 1.5rem; line-height: 2rem; }
    .text-3xl { font-size: 1.875rem; line-height: 2.25rem; }
    
    .font-normal { font-weight: 400; }
    .font-medium { font-weight: 500; }
    .font-semibold { font-weight: 600; }
    .font-bold { font-weight: 700; }
    
    /* Layout Components */
    .card {
        background: white;
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-md);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid var(--gray-200);
    }
    
    .container {
        max-width: 1200px;
        margin-left: auto;
        margin-right: auto;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    /* Form Elements */
    input, select, textarea {
        width: 100%;
        padding: 0.75rem;
        border: 1px solid var(--gray-300);
        border-radius: var(--radius-md);
        background-color: white;
        margin-bottom: 1rem;
    }
    
    /* Custom Components */
    .page-title {
        font-size: 1.875rem;
        font-weight: 700;
        color: var(--gray-900);
        margin-bottom: 1.5rem;
    }
    
    .section-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--gray-800);
        margin-bottom: 1rem;
    }
    
    .gradient-text {
        background: linear-gradient(90deg, var(--primary-color), var(--primary-light));
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        color: transparent !important;
        display: inline-block !important;
    }
    
    /* Button Styles */
    .stButton > button {
        border-radius: var(--radius-md);
        font-weight: 500;
    }
    
    /* Header Styles */
    header {
        border-bottom: 1px solid var(--gray-200);
        padding-bottom: 1rem;
        margin-bottom: 2rem;
    }
    
    /* Sidebar Styling */
    .css-1544g2n {  /* Sidebar */
        background-color: var(--gray-50);
    }
    
    /* Override Streamlit Defaults */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: var(--radius-md);
        padding: 0.5rem 1rem;
    }
    
    /* Blue gradient design */
    .blue-gradient {
        background: linear-gradient(135deg, #3b82f6, #1e40af);
        color: white;
    }
    
    /* Card design */
    .simple-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 1rem;
    }
    
    /* Profile styles */
    .avatar {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: white;
    }
    
    /* Tailwind-like utilites */
    .flex { display: flex; }
    .flex-col { flex-direction: column; }
    .items-center { align-items: center; }
    .justify-between { justify-content: space-between; }
    .gap-2 { gap: 0.5rem; }
    .gap-4 { gap: 1rem; }
    .mb-2 { margin-bottom: 0.5rem; }
    .mb-4 { margin-bottom: 1rem; }
    .mb-6 { margin-bottom: 1.5rem; }
    .p-4 { padding: 1rem; }
    .rounded-full { border-radius: 9999px; }
    .w-full { width: 100%; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# AUTHENTICATION FUNCTIONS
# =============================================================================

def authenticate(username, password):
    """Authenticate a user with username and password"""
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

# =============================================================================
# MOCK SCAN FUNCTIONS
# =============================================================================

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
    
    # Generate some mock findings
    for i in range(random.randint(5, 10)):
        severity_options = ["high", "medium", "low"]
        weights = [0.2, 0.5, 0.3]  # Probability weights
        severity = random.choices(severity_options, weights=weights, k=1)[0]
        
        finding = {
            "id": f"FIND-{i+1}",
            "title": f"Privacy Issue {i+1}",
            "description": f"This is a mock {severity} severity finding for demonstration purposes.",
            "severity": severity,
            "location": f"File: /src/main/module{i}.py, Line: {random.randint(10, 500)}"
        }
        results["findings"].append(finding)
    
    return results

def generate_mock_soc2_results(repo_url, branch=None):
    """Generate mock SOC2 scan results"""
    results = {
        "scan_type": "SOC2 Compliance",
        "repo_url": repo_url,
        "branch": branch or "main",
        "timestamp": datetime.now().isoformat(),
        "scan_id": str(uuid.uuid4()),
        "compliance_score": random.randint(60, 95),
        "controls": {}
    }
    
    # SOC2 control categories
    categories = [
        "Security", "Availability", "Processing Integrity", 
        "Confidentiality", "Privacy"
    ]
    
    # Generate mock results for each category
    for category in categories:
        results["controls"][category] = {
            "score": random.randint(60, 95),
            "findings": []
        }
        
        # Generate findings for this category
        num_findings = random.randint(1, 5)
        for i in range(num_findings):
            severity_options = ["high", "medium", "low"]
            weights = [0.2, 0.5, 0.3]  # Probability weights
            severity = random.choices(severity_options, weights=weights, k=1)[0]
            
            finding = {
                "id": f"{category[:3].upper()}-{i+1}",
                "title": f"{category} Finding {i+1}",
                "description": f"This is a mock {severity} severity finding related to {category}.",
                "severity": severity,
                "remediation": f"Consider implementing proper {category.lower()} controls"
            }
            results["controls"][category]["findings"].append(finding)
    
    return results

# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

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

# =============================================================================
# UI COMPONENTS
# =============================================================================

def render_brand_logo():
    """Render the DataGuardian Pro logo"""
    st.markdown("""
    <div style="padding: 20px 0; text-align: center;">
        <div style="
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border-radius: 16px;
            padding: 20px;
            position: relative;
            overflow: hidden;
            border: none;
            box-shadow: 0 10px 30px rgba(15, 23, 42, 0.15);
        ">
            <!-- Simple logo container -->
            <div style="
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 12px;
            ">
                <!-- Shield Icon -->
                <div style="
                    width: 40px;
                    height: 40px;
                    background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
                    border-radius: 10px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-right: 12px;
                ">
                    <span style="font-size: 20px; color: white;">🛡️</span>
                </div>
                
                <!-- Brand Name -->
                <div style="text-align: left;">
                    <h1 style="
                        font-weight: 800; 
                        font-size: 20px; 
                        color: white; 
                        margin: 0;
                        padding: 0;
                        line-height: 1.2;
                        display: block;
                    ">DataGuardian Pro</h1>
                    <div style="
                        font-size: 12px;
                        color: #94a3b8;
                        margin-top: 4px;
                        display: block;
                    ">Enterprise Edition</div>
                </div>
            </div>
            
            <!-- Simple tagline -->
            <div style="
                font-size: 12px;
                color: #cbd5e1;
                padding-top: 8px;
                border-top: 1px solid rgba(255,255,255,0.1);
            ">Advanced Privacy Compliance Platform</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_login_form():
    """Render the login form"""
    st.markdown("""
    <div style="padding: 24px; margin-bottom: 20px;">
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

def render_user_profile():
    """Render the user profile card"""
    initial = st.session_state.username[0].upper()
    
    st.markdown(f"""
    <div style="padding: 20px; margin-bottom: 24px;">
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
            ">{initial}</div>
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
    """, unsafe_allow_html=True)

def render_subscription_card(tier="basic"):
    """Render a subscription plan card"""
    plan = SUBSCRIPTION_PLANS[tier]
    
    if tier == "basic":
        st.markdown(f"""
        <div style='background-color: white; padding: 15px; border-radius: 10px; 
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06); border: 1px solid #f0f0f0;
                    margin-bottom: 15px;'>
            <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                <div style='background-color: #EBF4FF; border-radius: 50%; width: 24px; height: 24px; 
                            display: flex; align-items: center; justify-content: center; margin-right: 10px;'>
                    <span style='color: #2C5282; font-weight: bold; font-size: 12px;'>B</span>
                </div>
                <div style='color: #2C5282; font-weight: 600; font-size: 16px;'>{plan['name']}</div>
            </div>
            <div style='color: #2C5282; font-weight: 700; font-size: 20px; margin-bottom: 5px;'>${plan['price']}<span style='color: #718096; font-weight: 400; font-size: 14px;'>/month</span></div>
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
    elif tier == "premium":
        st.markdown(f"""
        <div style='background-color: white; padding: 15px; border-radius: 10px; 
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06); border: 1px solid #3B82F6;
                    margin-bottom: 15px;'>
            <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                <div style='background-color: #2C5282; border-radius: 50%; width: 24px; height: 24px; 
                            display: flex; align-items: center; justify-content: center; margin-right: 10px;'>
                    <span style='color: white; font-weight: bold; font-size: 12px;'>P</span>
                </div>
                <div style='color: #2C5282; font-weight: 600; font-size: 16px;'>{plan['name']}</div>
            </div>
            <div style='color: #2C5282; font-weight: 700; font-size: 20px; margin-bottom: 5px;'>${plan['price']}<span style='color: #718096; font-weight: 400; font-size: 14px;'>/month</span></div>
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
    elif tier == "gold":
        st.markdown(f"""
        <div style='background-color: white; padding: 15px; border-radius: 10px; 
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06); border: 1px solid #F59E0B;
                    margin-bottom: 15px;'>
            <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                <div style='background-color: #F59E0B; border-radius: 50%; width: 24px; height: 24px; 
                            display: flex; align-items: center; justify-content: center; margin-right: 10px;'>
                    <span style='color: white; font-weight: bold; font-size: 12px;'>G</span>
                </div>
                <div style='color: #92400E; font-weight: 600; font-size: 16px;'>{plan['name']}</div>
            </div>
            <div style='color: #92400E; font-weight: 700; font-size: 20px; margin-bottom: 5px;'>${plan['price']}<span style='color: #718096; font-weight: 400; font-size: 14px;'>/month</span></div>
            <div style='color: #718096; font-size: 13px; margin-bottom: 15px;'>Your plan renews on May 12, 2025</div>
            <div style='background-color: #FEF3C7; color: #92400E; border-radius: 6px; 
                       padding: 8px 16px; text-align: center; font-weight: 600; font-size: 14px;'>
                ✓ You're on our highest tier
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_payment_method():
    """Render payment method card"""
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

def render_billing_history():
    """Render billing history card"""
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

def render_landing_page():
    """Render a simple, clear landing page"""
    st.markdown("""
    <div style="
        max-width: 1000px;
        margin: 0 auto;
        padding: 40px 20px;
    ">
        <!-- Hero Section -->
        <div style="
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            padding-bottom: 40px;
            border-bottom: 1px solid #e2e8f0;
            margin-bottom: 40px;
        ">
            <!-- Logo -->
            <div style="
                width: 80px;
                height: 80px;
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                border-radius: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 24px;
                box-shadow: 0 10px 25px rgba(59, 130, 246, 0.2);
            ">
                <span style="font-size: 40px; color: white;">🛡️</span>
            </div>
            
            <!-- Title - fixed styling -->
            <div style="margin-bottom: 16px;">
                <h1 style="
                    font-size: 40px;
                    font-weight: 800;
                    color: #0f172a;
                    margin: 0 0 16px 0;
                    padding: 0;
                    line-height: 1.2;
                    display: block;
                ">DataGuardian Pro</h1>
            </div>
            
            <!-- Subtitle - fixed styling -->
            <div style="
                margin-bottom: 32px;
                width: 100%;
                max-width: 600px;
                margin-left: auto;
                margin-right: auto;
            ">
                <p style="
                    font-size: 20px;
                    color: #64748b;
                    margin: 0;
                    padding: 0;
                    line-height: 1.5;
                ">Protect your data. Ensure compliance. Build trust.</p>
            </div>
            
            <!-- CTA Button -->
            <a href="#" style="
                background: #3b82f6;
                color: white;
                font-weight: 600;
                font-size: 18px;
                padding: 14px 28px;
                border-radius: 8px;
                text-decoration: none;
                transition: all 0.2s ease;
                box-shadow: 0 4px 6px rgba(59, 130, 246, 0.25);
            ">Start Free Trial</a>
        </div>
        
        <!-- Three Simple Feature Blocks -->
        <div style="margin-bottom: 60px;">
            <h2 style="
                font-size: 32px;
                font-weight: 700;
                color: #0f172a;
                text-align: center;
                margin-bottom: 40px;
            ">How It Works</h2>
            
            <div style="
                display: flex;
                gap: 30px;
                justify-content: center;
                flex-wrap: wrap;
            ">
                <!-- Feature 1 -->
                <div style="
                    flex: 1;
                    min-width: 280px;
                    background: white;
                    border-radius: 16px;
                    padding: 30px;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
                    text-align: center;
                ">
                    <div style="
                        width: 60px;
                        height: 60px;
                        background: #eef2ff;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin: 0 auto 20px auto;
                        font-size: 24px;
                    ">1</div>
                    <h3 style="
                        font-size: 20px;
                        font-weight: 600;
                        color: #1e293b;
                        margin-bottom: 12px;
                    ">Scan</h3>
                    <p style="
                        color: #64748b;
                        font-size: 16px;
                        line-height: 1.5;
                    ">Quickly scan your systems for sensitive data and compliance issues.</p>
                </div>
                
                <!-- Feature 2 -->
                <div style="
                    flex: 1;
                    min-width: 280px;
                    background: white;
                    border-radius: 16px;
                    padding: 30px;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
                    text-align: center;
                ">
                    <div style="
                        width: 60px;
                        height: 60px;
                        background: #eef2ff;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin: 0 auto 20px auto;
                        font-size: 24px;
                    ">2</div>
                    <h3 style="
                        font-size: 20px;
                        font-weight: 600;
                        color: #1e293b;
                        margin-bottom: 12px;
                    ">Analyze</h3>
                    <p style="
                        color: #64748b;
                        font-size: 16px;
                        line-height: 1.5;
                    ">Our AI identifies risks and prioritizes issues that need attention.</p>
                </div>
                
                <!-- Feature 3 -->
                <div style="
                    flex: 1;
                    min-width: 280px;
                    background: white;
                    border-radius: 16px;
                    padding: 30px;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
                    text-align: center;
                ">
                    <div style="
                        width: 60px;
                        height: 60px;
                        background: #eef2ff;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin: 0 auto 20px auto;
                        font-size: 24px;
                    ">3</div>
                    <h3 style="
                        font-size: 20px;
                        font-weight: 600;
                        color: #1e293b;
                        margin-bottom: 12px;
                    ">Fix</h3>
                    <p style="
                        color: #64748b;
                        font-size: 16px;
                        line-height: 1.5;
                    ">Get clear recommendations to resolve issues and maintain compliance.</p>
                </div>
            </div>
        </div>
        
        <!-- Simple Testimonial -->
        <div style="
            background: #f8fafc;
            border-radius: 16px;
            padding: 40px;
            text-align: center;
            margin-bottom: 60px;
        ">
            <div style="
                font-size: 24px;
                color: #0f172a;
                font-weight: 500;
                font-style: italic;
                margin-bottom: 24px;
                line-height: 1.5;
                max-width: 700px;
                margin-left: auto;
                margin-right: auto;
            ">
                "DataGuardian Pro helped us identify privacy risks we didn't even know existed. Our compliance score improved by 40% in just one month."
            </div>
            <div style="
                font-weight: 600;
                color: #334155;
            ">Sarah Johnson, CTO</div>
            <div style="
                color: #64748b;
                font-size: 14px;
            ">Enterprise Solutions Inc.</div>
        </div>
        
        <!-- Simple CTA -->
        <div style="
            text-align: center;
            padding: 40px;
            background: #0f172a;
            border-radius: 16px;
        ">
            <h2 style="
                font-size: 28px;
                font-weight: 700;
                color: white;
                margin-bottom: 16px;
            ">Ready to protect your data?</h2>
            <p style="
                color: #cbd5e1;
                margin-bottom: 24px;
                font-size: 16px;
            ">Get started with a free trial today. No credit card required.</p>
            <a href="#" style="
                background: white;
                color: #0f172a;
                font-weight: 600;
                font-size: 16px;
                padding: 12px 24px;
                border-radius: 8px;
                text-decoration: none;
                display: inline-block;
            ">Sign Up Now</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# DASHBOARD COMPONENTS
# =============================================================================

def render_summary_metrics():
    """Render summary metrics for the dashboard"""
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Scans", value=random.randint(10, 100))
    with col2:
        st.metric(label="Open Issues", value=random.randint(5, 50))
    with col3:
        st.metric(label="Avg. Compliance", value=f"{random.randint(70, 95)}%")
    with col4:
        st.metric(label="Risk Score", value=f"{random.randint(10, 40)}/100")

def render_scan_history():
    """Render scan history table"""
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

def render_scan_form():
    """Render scan configuration form"""
    st.subheader("Configure Scan")
    
    scan_types = [
        "Code Scanner", 
        "Blob Scanner", 
        "Image Scanner", 
        "Database Scanner", 
        "API Scanner", 
        "Website Scanner", 
        "AI Model Scanner", 
        "SOC2 Scanner",
        "Sustainability Scanner"
    ]
    
    selected_scan = st.selectbox("Select Scan Type", scan_types, key="scan_type_select")
    
    # Common scan options
    col1, col2 = st.columns(2)
    with col1:
        if selected_scan == "SOC2 Scanner":
            repo_provider = st.radio(
                "Repository Provider:",
                ["GitHub", "Azure DevOps"],
                horizontal=True,
                key="repo_provider"
            )
            
            if repo_provider == "GitHub":
                st.text_input("Repository URL", value="https://github.com/example/repo", key="repo_url")
                st.text_input("Branch", value="main", key="branch")
            else:
                st.text_input("Azure DevOps URL", value="https://dev.azure.com/org/project", key="repo_url")
                st.text_input("Project", value="example-project", key="project")
                st.text_input("Branch", value="main", key="branch")
        else:
            st.text_input("Repository URL", value="https://github.com/example/repo", key="repo_url")
            st.text_input("Branch", value="main", key="branch")
    
    with col2:
        scan_options = ["Detect PII", "Check Compliance", "Generate Recommendations"]
        for option in scan_options:
            st.checkbox(option, value=True, key=f"option_{option}")
        
        st.selectbox(
            "Output Format",
            ["PDF Report", "CSV Export", "JSON Export"],
            key="output_format"
        )
    
    if st.button("Start Scan", type="primary", key="start_scan_button"):
        with st.spinner("Running scan..."):
            progress_bar = st.progress(0)
            for i in range(1, 101):
                time.sleep(0.02)  # Simulate scan process
                progress_bar.progress(i/100)
            
            # Generate mock results
            if selected_scan == "SOC2 Scanner":
                results = generate_mock_soc2_results(st.session_state.repo_url)
            else:
                results = generate_mock_scan_results(selected_scan)
            
            st.session_state.current_scan_results = results
            
            # Add to scan history
            st.session_state.scan_history.insert(0, results)
            if len(st.session_state.scan_history) > 5:
                st.session_state.scan_history = st.session_state.scan_history[:5]
        
        st.success(f"{selected_scan} completed successfully!")
        st.json(results)

def render_reports_section():
    """Render reports section"""
    st.subheader("Compliance Reports")
    
    if not st.session_state.scan_history:
        st.info("No scan history available. Run a scan to generate reports.")
    else:
        scan_options = [f"{scan['scan_type']} - {datetime.fromisoformat(scan['timestamp']).strftime('%Y-%m-%d %H:%M')}" 
                       for scan in st.session_state.scan_history]
        selected_report = st.selectbox("Select Scan for Report", scan_options, key="report_select")
        
        report_types = ["Summary Report", "Full Report", "Technical Report", "Executive Report"]
        report_format = st.radio("Report Format", report_types, horizontal=True)
        
        if st.button("Generate Report", key="generate_report_button"):
            with st.spinner("Generating report..."):
                time.sleep(1.5)  # Simulate report generation
                
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
                            "ID": finding.get("id", f"FIND-{i+1}"),
                            "Title": finding.get("title", f"Finding {i+1}"),
                            "Severity": finding.get("severity", "medium").upper(),
                            "Location": finding.get("location", "N/A")
                        } for i, finding in enumerate(scan_data['findings'][:5])  # Show top 5 findings
                    ])
                    st.dataframe(findings_df, use_container_width=True)
                
                # Add a download button
                st.download_button(
                    label="Download Report (PDF)",
                    data="This would be a PDF report in a real application",
                    file_name=f"{scan_data['scan_type'].replace(' ', '_')}_report.pdf",
                    mime="application/pdf"
                )

def render_admin_section():
    """Render admin section"""
    if "admin:all" not in st.session_state.permissions:
        st.warning("You do not have permission to access the administration section.")
        return
        
    st.subheader("Administration")
    
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
            
            if st.button("Create User", key="create_user_button"):
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
            st.checkbox("Enable 2FA", value=True, key="enable_2fa")
            st.checkbox("Enforce Password Complexity", value=True, key="enforce_pwd_complexity")
            st.slider("Minimum Password Length", min_value=8, max_value=24, value=12)
        
        with settings_tabs[2]:
            st.text_input("API Key", value="sk_test_*********************", type="password")
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
            st.checkbox("Enable Deep Scanning", value=False, key="enable_deep_scan")
            st.checkbox("Debug Mode", value=False, key="debug_mode")
        
        with col2:
            st.selectbox("Log Level", ["ERROR", "WARNING", "INFO", "DEBUG"])
            st.text_area("Custom Scan Rules")
            
        if st.button("Apply Settings", key="apply_settings_button"):
            st.success("Settings applied successfully")

# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    """Main application entry point"""
    # Sidebar content
    with st.sidebar:
        render_brand_logo()
        
        if not st.session_state.logged_in:
            render_login_form()
        else:
            render_user_profile()
            
            # Modern subscription status display
            st.markdown("### Your Subscription", help="Manage your subscription plan")
            current_plan = st.session_state.get("subscription_tier", "basic")
            render_subscription_card(current_plan)
            
            # Payment & Billing section
            st.markdown("### Billing", help="Manage your payment methods and billing history")
            render_payment_method()
            render_billing_history()
            
            st.divider()
            
            if st.button("Logout", key="logout_button"):
                for key in st.session_state.keys():
                    del st.session_state[key]
                st.rerun()
    
    # Main content
    if not st.session_state.logged_in:
        render_landing_page()
    else:
        # Create tabs for main content
        tabs = st.tabs(["Dashboard", "Scan", "Reports", "Admin"])
        
        # Dashboard Tab
        with tabs[0]:
            st.header("Analytics Dashboard")
            render_summary_metrics()
            render_scan_history()
        
        # Scan Tab
        with tabs[1]:
            st.header("Privacy Compliance Scan")
            render_scan_form()
        
        # Reports Tab
        with tabs[2]:
            st.header("Compliance Reports")
            render_reports_section()
        
        # Admin Tab
        with tabs[3]:
            st.header("Administration")
            render_admin_section()

if __name__ == "__main__":
    main()