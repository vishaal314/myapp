import streamlit as st
import soc2_scanner  # Import our new SOC2 scanner module
import pandas as pd
import time
import json
import os
import io
from io import BytesIO  # Import BytesIO for PDF generation
import random
import uuid
from datetime import datetime
import base64

# Import enhanced AI model scanner
from services.enhanced_ai_model_scanner import EnhancedAIModelScanner
# Import revised website scanner
from services.website_scanner_revised import WebsiteScanner, display_website_scan_results

# Import RBAC components
from access_control import (
    requires_permission,
    requires_role,
    check_permission,
    check_role,
    render_access_denied,
    get_user_permissions
)

# Import admin panel and user profile
from admin_panel import render_admin_panel
from user_profile import render_user_profile_page
from billing.billing_page import render_billing_page

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
    import json
    import hashlib
    from access_control.user_management import load_users
    
    try:
        # Load users from the user management system
        users = load_users()
        
        # Check if username exists directly
        if username in users:
            user_data = users[username]
            
            # Hash the provided password for comparison
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # Check if password matches (in production, use secure password hashing)
            # For this demo, we'll also allow "password" for any account
            if user_data["password_hash"] == password_hash or password == "password":
                # Get user role and permissions from RBAC system
                role = user_data.get("role", "viewer")
                permissions = get_permissions_for_role(role)
                
                # Create result with user data, including subscription information
                result = {
                    "username": username,
                    "role": role,
                    "email": user_data.get("email", f"{username}@dataguardian.pro"),
                    "permissions": permissions,
                    
                    # Add subscription data
                    "subscription_tier": user_data.get("subscription_tier", "basic"),
                    "subscription_active": user_data.get("subscription_active", True),
                    "stripe_customer_id": user_data.get("stripe_customer_id"),
                    "subscription_id": user_data.get("subscription_id"),
                    "user_id": user_data.get("user_id", str(uuid.uuid4())),
                    "subscription_renewal_date": user_data.get("subscription_renewal_date")
                }
                return result
                
        # If not found by username, check if the username is actually an email address
        # This allows users to log in with their email address
        for user_id, user_data in users.items():
            if user_data.get("email") == username:
                # Hash the provided password for comparison
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                
                # Check if password matches
                if user_data["password_hash"] == password_hash or password == "password":
                    # Get user role and permissions from RBAC system
                    role = user_data.get("role", "viewer")
                    permissions = get_permissions_for_role(role)
                    
                    # Create result with user data
                    result = {
                        "username": user_id,  # Use the actual username, not the email
                        "role": role,
                        "email": username,  # This is the email they logged in with
                        "permissions": permissions,
                        
                        # Add subscription data
                        "subscription_tier": user_data.get("subscription_tier", "basic"),
                        "subscription_active": user_data.get("subscription_active", True),
                        "stripe_customer_id": user_data.get("stripe_customer_id"),
                        "subscription_id": user_data.get("subscription_id"),
                        "user_id": user_data.get("user_id", str(uuid.uuid4())),
                        "subscription_renewal_date": user_data.get("subscription_renewal_date")
                    }
                    return result
                
    except Exception as e:
        st.error(f"Authentication error: {str(e)}")
        # Fall back to default authentication
        
    # Also allow default users for testing    
    if username == "admin" and password == "password":
        # Admin has full system access
        return {
            "username": "admin",
            "role": "admin",
            "email": "admin@dataguardian.pro",
            "permissions": get_permissions_for_role("admin"),
            "subscription_tier": "gold",
            "subscription_active": True,
            "user_id": "admin-" + str(uuid.uuid4())
        }
    elif username == "user" and password == "password":
        # Regular user with basic permissions
        return {
            "username": "user",
            "role": "viewer",
            "email": "user@dataguardian.pro",
            "permissions": get_permissions_for_role("viewer"),
            "subscription_tier": "basic",
            "subscription_active": True,
            "user_id": "user-" + str(uuid.uuid4())
        }
    elif username == "auditor" and password == "password":
        # Auditor with report access
        return {
            "username": "auditor",
            "role": "auditor",
            "email": "auditor@dataguardian.pro",
            "permissions": get_permissions_for_role("auditor"),
            "subscription_tier": "professional",
            "subscription_active": True,
            "user_id": "auditor-" + str(uuid.uuid4())
        }
    elif username == "security" and password == "password":
        # Security engineer with advanced scanning capabilities
        return {
            "username": "security",
            "role": "security_engineer",
            "email": "security@dataguardian.pro",
            "permissions": get_permissions_for_role("security_engineer"),
            "subscription_tier": "professional",
            "subscription_active": True,
            "user_id": "security-" + str(uuid.uuid4())
        }
        
    return None

def get_permissions_for_role(role):
    """Get permissions for a specific role from RBAC system"""
    # Map roles to their specific permissions
    if role == "admin":
        # Admin has full system access - include ALL possible permissions
        return [
            # Admin permissions
            "admin:all", 
            "admin:users",
            "admin:roles",
            "admin:settings",
            "admin:billing",
            "admin:api_keys",
            
            # User permissions
            "user:manage",
            "user:create",
            "user:edit",
            "user:delete",
            
            # Scan permissions
            "scan:all",
            "scan:run_basic",
            "scan:run_advanced",
            "scan:run_any",
            "scan:view_results",
            "scan:view_all",
            "scan:view_own",
            "scan:export",
            "scan:delete",
            "scan:configure",
            
            # Report permissions
            "reports:all",
            "reports:view",
            "reports:view_all", 
            "reports:view_own",
            "reports:create",
            "reports:generate",
            "reports:download",
            "reports:export",
            "reports:share",
            "reports:delete",
            
            # Dashboard permissions
            "dashboard:all",
            "dashboard:view_metrics",
            "dashboard:view_scan_history",
            
            # Settings permissions
            "settings:all",
            "settings:edit",
            "settings:view",
            
            # Feature permissions
            "feature:all",
            "feature:advanced_analytics",
            "feature:custom_policies",
            "feature:integrations",
            "feature:api_access",
            "feature:soc2",
            "feature:sustainability",
            
            # Team permissions
            "team:all",
            "team:view",
            "team:invite",
            "team:remove",
            "team:assign_role"
        ]
    elif role == "security_engineer":
        # Security engineer has advanced scanning capabilities
        return [
            "scan:run_basic",
            "scan:run_advanced",
            "scan:view_results",
            "scan:export",
            "reports:view",
            "reports:create",
            "reports:download",
            "dashboard:view_metrics",
            "dashboard:view_scan_history",
            "settings:view"
        ]
    elif role == "auditor":
        # Auditor focuses on report access
        return [
            "scan:view_results",
            "reports:view",
            "reports:download",
            "reports:share",
            "dashboard:view_metrics",
            "dashboard:view_scan_history"
        ]
    else:  # viewer or any other role
        # Basic permissions for regular users
        return [
            "scan:run_basic",
            "scan:view_results",
            "reports:view",
            "dashboard:view_metrics",
            "dashboard:view_scan_history"
        ]

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
    st.session_state.current_view = "landing"  # Default view (landing, signup, payment_method)
    st.session_state.signup_success = False  # Track if signup was successful

# =============================================================================
# UI COMPONENTS
# =============================================================================

def render_brand_logo():
    """Render the DataGuardian Pro logo with ultra-simple HTML"""
    st.markdown("""
    <div style="background-color:#1e293b; padding:20px; text-align:center; border-radius:10px; margin:20px 0;">
        <div style="font-size:28px; margin-bottom:10px;">🛡️</div>
        <div style="color:white; font-weight:bold; font-size:18px;">DataGuardian Pro</div>
        <div style="color:#94a3b8; font-size:12px; margin-top:5px;">Enterprise Edition</div>
        <div style="color:#cbd5e1; font-size:11px; margin-top:10px; border-top:1px solid rgba(255,255,255,0.1); padding-top:8px;">
            Advanced Privacy Compliance Platform
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_login_form():
    """Render the login form with Google OAuth option"""
    # Import Google auth function
    from enhanced_signup_flow import render_login_page
    
    # We'll maintain the original login form structure but enhance it with Google OAuth
    st.markdown("""
    <div style="padding: 24px; margin-bottom: 20px;">
        <h2 style="font-size: 18px; font-weight: 700; margin-bottom: 20px; color: #0f172a;">Sign In</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Google Sign-In Option
    from access_control.google_auth import get_google_auth_url, login_with_google
    import os
    
    # Check if Google OAuth is configured
    google_oauth_configured = bool(os.environ.get("GOOGLE_CLIENT_ID") and os.environ.get("GOOGLE_CLIENT_SECRET"))
    
    if google_oauth_configured:
        # Display Google login button if credentials are available
        google_auth_url = get_google_auth_url()
        st.markdown(f"""
        <a href="{google_auth_url}" style="display: flex; align-items: center; justify-content: center; 
            padding: 12px 16px; background-color: white; color: #333; border-radius: 8px;
            border: 1px solid #e2e8f0; width: 100%; text-decoration: none; font-weight: 500;
            transition: all 0.2s ease; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
            <img src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg" 
                 alt="Google logo" style="height: 24px; margin-right: 12px;"> 
            Sign in with Google
        </a>
        
        <div style="display: flex; align-items: center; text-align: center; margin: 30px 0;">
            <div style="flex: 1; border-bottom: 1px solid #e2e8f0;"></div>
            <span style="padding: 0 10px; color: #a0aec0; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px;">OR SIGN IN WITH EMAIL</span>
            <div style="flex: 1; border-bottom: 1px solid #e2e8f0;"></div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Show a simplified header for email login
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h3 style="font-size: 1.1rem; color: #4a5568;">Sign in with your account</h3>
        </div>
        """, unsafe_allow_html=True)
    
    # Standard login form
    username = st.text_input("Username or Email", key="login_username", placeholder="Enter your username or email")
    password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        remember = st.checkbox("Remember me", value=True, key="remember_me_checkbox")
    
    # Login button
    login_button = st.button("Sign In", key="login_button", use_container_width=True)
    
    # Forgot password button
    forgot_password = st.button("Forgot Password?", key="forgot_password_login", type="secondary")
    if forgot_password:
        st.session_state.current_view = "password_reset"
        st.rerun()
    
    # Add a "Sign Up" button 
    st.markdown("<div style='text-align: center; margin-top: 20px;'>Don't have an account?</div>", unsafe_allow_html=True)
    signup_button = st.button("Create Account", key="create_account_button", use_container_width=True)
    
    if signup_button:
        # Redirect to signup page
        st.session_state.current_view = "signup"
        st.rerun()
    
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
                
                # Store the complete user data in session state
                st.session_state.user_data = user_data
                
                # Add subscription data to session state
                st.session_state.subscription_tier = user_data.get("subscription_tier", "basic")
                st.session_state.subscription_active = user_data.get("subscription_active", True)
                st.session_state.stripe_customer_id = user_data.get("stripe_customer_id")
                st.session_state.subscription_id = user_data.get("subscription_id")
                st.session_state.user_id = user_data.get("user_id")
                st.session_state.subscription_renewal_date = user_data.get("subscription_renewal_date")
                
                # If we have a Stripe customer ID, get the latest subscription data
                if st.session_state.stripe_customer_id:
                    try:
                        # Import here to avoid circular import
                        from billing.stripe_integration import get_subscription_details
                        
                        # Get the latest subscription data
                        subscription_data = get_subscription_details(st.session_state.stripe_customer_id)
                        st.session_state.subscription_data = subscription_data
                        
                        # Update subscription tier if it's different
                        if subscription_data and subscription_data.get("has_subscription"):
                            st.session_state.subscription_tier = subscription_data.get("tier", st.session_state.subscription_tier)
                    except Exception as e:
                        st.warning(f"Could not fetch latest subscription data: {str(e)}")
                
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
    """Render the user profile card with native Streamlit components"""
    initial = st.session_state.username[0].upper()
    
    # Create a simple user info section
    col1, col2 = st.columns([1, 3])
    
    # Avatar with initial
    with col1:
        st.markdown(f"""
        <div style="background-color:#3b82f6; color:white; width:48px; height:48px; 
                 border-radius:50%; text-align:center; line-height:48px; font-weight:bold; font-size:20px;">
            {initial}
        </div>
        """, unsafe_allow_html=True)
    
    # Name and email
    with col2:
        st.markdown(f"**{st.session_state.username}**")
        st.markdown(f"<span style='color:#64748b; font-size:14px;'>{st.session_state.email}</span>", unsafe_allow_html=True)
    
    # Account type with simple badge
    st.markdown(f"""
    <div style="background-color:#EEF2FF; padding:8px; border-radius:8px; margin:16px 0;">
        <span style="color:#4f46e5; font-weight:bold;">👑 {st.session_state.role.title()} Account</span>
    </div>
    """, unsafe_allow_html=True)

def render_subscription_card(tier="basic"):
    """Render a subscription plan card using native Streamlit components"""
    plan = SUBSCRIPTION_PLANS[tier]
    
    # Simple card with border
    st.markdown(f"""
    <div style="border:1px solid #e2e8f0; border-radius:10px; padding:15px; margin-bottom:15px; background-color:white;">
        <h3 style="margin-top:0; color:#1e3a8a;">{plan['name']} Plan</h3>
        <p style="font-size:24px; font-weight:bold; margin:10px 0;">${plan['price']}<span style="font-size:14px; color:#64748b; font-weight:normal;"> /month</span></p>
        <p style="font-size:13px; color:#64748b; margin-bottom:15px;">Your plan renews on May 12, 2025</p>
    """, unsafe_allow_html=True)
    
    # List plan features
    for feature in plan['features']:
        st.markdown(f"✓ {feature}")
    
    # Add appropriate button based on tier
    if tier == "basic":
        st.button("Upgrade to Premium", use_container_width=True)
    elif tier == "premium":
        st.button("Upgrade to Gold", use_container_width=True)
    elif tier == "gold":
        st.success("✓ You're on our highest tier")
    
    # Close the div
    st.markdown("</div>", unsafe_allow_html=True)

def render_payment_method():
    """Render payment method card using native Streamlit components"""
    # Header with two columns for the title and add button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("Payment Method")
    with col2:
        st.markdown('<div style="text-align:right"><a href="#" style="color:#3B82F6; font-size:12px; text-decoration:none;">+ Add New</a></div>', unsafe_allow_html=True)
    
    # Card with simple styling
    st.markdown("""
    <div style="border:1px solid #e2e8f0; border-radius:10px; padding:15px; background-color:#f8fafc;">
        <div style="display:flex; align-items:center;">
            <span style="background:#e2e8f0; color:#4a5568; padding:8px; border-radius:5px; margin-right:10px;">💳</span>
            <div>
                <div style="font-weight:500;">•••• •••• •••• 4242</div>
                <div style="font-size:12px; color:#718096;">Expires 12/2025</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_billing_history():
    """Render billing history using native Streamlit components"""
    # Header with two columns for the title and view all link
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("Recent Invoices")
    with col2:
        st.markdown('<div style="text-align:right"><a href="#" style="color:#3B82F6; font-size:12px; text-decoration:none;">View All</a></div>', unsafe_allow_html=True)
    
    # Empty state with icon and message
    st.markdown("""
    <div style="text-align:center; padding:20px; color:#718096; background-color:#f8fafc; border-radius:10px; border:1px solid #e2e8f0;">
        <div style="font-size:24px; margin-bottom:10px;">📄</div>
        <div style="font-size:14px; font-weight:500;">No invoices yet</div>
        <div style="font-size:12px; margin-top:5px;">Your billing history will appear here</div>
    </div>
    """, unsafe_allow_html=True)

def render_landing_page():
    """Render an ultra-simple landing page with minimal HTML structure"""
    
    # Logo (using emoji directly)
    st.markdown("<div style='font-size:60px; text-align:center;'>🛡️</div>", unsafe_allow_html=True)
    
    # Title and subtitle using native Streamlit components
    st.title("DataGuardian Pro")
    st.subheader("Protect your data. Ensure compliance. Build trust.")
    
    # CTA Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Start Free Trial", type="primary", use_container_width=True, key="start_trial_button"):
            st.session_state.current_view = "signup"
            st.rerun()
    
    st.markdown("---")  # Separator
    
    # How It Works section
    st.header("How It Works")
    
    # Use columns for the 3 steps
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 1. Scan")
        st.markdown("Quickly scan your systems for sensitive data and compliance issues.")
    
    with col2:
        st.markdown("### 2. Analyze")
        st.markdown("Our AI identifies risks and prioritizes issues that need attention.")
    
    with col3:
        st.markdown("### 3. Fix")
        st.markdown("Get clear recommendations to resolve issues and maintain compliance.")
    
    st.markdown("---")  # Separator
    
    # Testimonial
    st.markdown("""
    > "DataGuardian Pro helped us identify privacy risks we didn't even know existed. Our compliance score improved by 40% in just one month."
    >
    > **Sarah Johnson, CTO** - Enterprise Solutions Inc.
    """)
    
    st.markdown("---")  # Separator
    
    # Final CTA section
    st.header("Ready to protect your data?")
    st.markdown("Get started with a free trial today. No credit card required.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Sign Up Now", type="primary", use_container_width=True, key="signup_button"):
            st.session_state.current_view = "signup"
            st.rerun()

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
        # Create a dataframe with safe access to dictionary keys using .get() method
        scan_df = pd.DataFrame([
            {
                "Date": datetime.fromisoformat(scan.get("timestamp", datetime.now().isoformat())).strftime("%Y-%m-%d %H:%M"),
                "Type": scan.get("scan_type", "Unknown"),
                "Findings": scan.get("total_findings", scan.get("findings_count", 0)),
                "High Risk": scan.get("high_risk", 0),
                "Medium Risk": scan.get("medium_risk", 0),
                "Low Risk": scan.get("low_risk", 0),
                "Compliance Score": f"{scan.get('compliance_score', 0)}%"
            } for scan in st.session_state.scan_history
        ])
        st.dataframe(scan_df, use_container_width=True)

def render_scan_form():
    """Render scan configuration form"""
    st.subheader("Configure Scan")
    
    scan_types = [
        "GDPR Code Scanner", 
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
        elif selected_scan == "Website Scanner":
            # Website URL input
            st.text_input("Website URL", placeholder="https://example.com", key="website_url")
            
            # Website name (optional)
            st.text_input("Website Name (Optional)", placeholder="Example Website", key="website_name")
            
            # Region selection for compliance rules
            st.selectbox(
                "Region",
                ["EU", "Global", "Netherlands"],
                key="region",
                help="Region to apply compliance rules for"
            )
            
            # Advanced options in an expandable section
            with st.expander("GDPR Compliance Options"):
                st.multiselect(
                    "Compliance Areas to Check",
                    [
                        "Cookie Consent", 
                        "Privacy Policy", 
                        "Data Processing", 
                        "Data Subject Rights",
                        "Forms & Consent Mechanisms", 
                        "Security & Encryption"
                    ],
                    default=[
                        "Cookie Consent", 
                        "Privacy Policy", 
                        "Data Processing", 
                        "Data Subject Rights",
                        "Forms & Consent Mechanisms"
                    ],
                    key="compliance_areas"
                )
                
                st.radio(
                    "Depth of Analysis",
                    ["Basic", "Standard", "Comprehensive"],
                    index=1,
                    key="scan_depth",
                    help="Basic: Surface checks only, Standard: Detailed scan, Comprehensive: In-depth analysis with content extraction"
                )
                
                st.checkbox(
                    "Include Screenshots in Report", 
                    value=False, 
                    key="include_screenshots",
                    help="Capture screenshots of the website for evidence in the report"
                )
                
        elif selected_scan == "AI Model Scanner":
            # Model source selection
            model_source = st.selectbox(
                "Model Source",
                ["Repository URL", "Model Hub", "API Endpoint", "Local File"],
                key="model_source"
            )
            
            # Model type selection
            model_type = st.selectbox(
                "Model Type",
                ["ONNX", "TensorFlow", "PyTorch", "Linear Model", "Decision Tree", "Neural Network"],
                key="model_type"
            )
            
            # Source details based on selection
            if model_source == "Repository URL":
                st.text_input("Repository URL", value="https://github.com/example/model-repo", key="repo_url")
                st.text_input("Branch", value="main", key="branch")
            elif model_source == "Model Hub":
                st.text_input("Hub URL", value="https://huggingface.co/model/example", key="hub_url")
                st.text_input("Model Path", value="/path/to/model", key="repository_path")
            elif model_source == "API Endpoint":
                st.text_input("API Endpoint", value="https://api.example.com/v1/model", key="api_endpoint")
                st.text_input("Model Path", value="/path/to/model", key="repository_path")
            elif model_source == "Local File":
                st.text_input("File Path", value="/path/to/local/model.onnx", key="file_path")
            
            # Advanced options in an expandable section
            with st.expander("Advanced Analysis Options"):
                st.multiselect(
                    "PII Detection Types",
                    ["PII in Training Data", "PII in Model Output", "PII in Model Parameters"],
                    default=["PII in Training Data", "PII in Model Output"],
                    key="leakage_types"
                )
                
                st.multiselect(
                    "Fairness Metrics",
                    ["Disparate Impact", "Equal Opportunity", "Predictive Parity"],
                    default=["Disparate Impact"],
                    key="fairness_metrics"
                )
                
                st.multiselect(
                    "Explainability Checks",
                    ["Feature Importance", "Decision Path", "Model Interpretability"],
                    default=["Feature Importance", "Model Interpretability"],
                    key="explainability_checks"
                )
                
                st.multiselect(
                    "Context",
                    ["General", "Health", "Finance", "Education", "Employment"],
                    default=["General"],
                    key="context"
                )
                
                sample_inputs = st.text_area(
                    "Sample Inputs (one per line)",
                    "",
                    key="sample_inputs"
                )
                
                # Add EU AI Act 2025 compliance analysis option
                st.markdown("---")
                st.markdown("### EU AI Act 2025 Compliance")
                
                perform_eu_ai_act = st.checkbox(
                    "Perform EU AI Act 2025 Compliance Analysis",
                    value=True,
                    key="perform_eu_ai_act",
                    help="Analyze the AI model against the EU AI Act 2025 requirements and generate a detailed compliance report"
                )
                
                if perform_eu_ai_act:
                    # Additional inputs for EU AI Act analysis
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.selectbox(
                            "Model Purpose",
                            ["General Purpose", "Healthcare", "Finance", "Education", "Employment", "Law Enforcement", "Critical Infrastructure"],
                            key="model_purpose",
                            help="Select the intended purpose of the model to determine applicable requirements"
                        )
                        
                        st.checkbox(
                            "Is Foundation Model",
                            value=False,
                            key="is_foundation_model",
                            help="Check if this is a foundation or general-purpose AI model with broad capabilities"
                        )
                    
                    with col2:
                        st.selectbox(
                            "Deployment Context",
                            ["Commercial", "Enterprise", "Public Sector", "Healthcare", "Education", "Research"],
                            key="deployment_context",
                            help="Environment where the model will be deployed"
                        )
                        
                        st.checkbox(
                            "Is Generative AI",
                            value=False,
                            key="is_generative_ai",
                            help="Check if this model has generative capabilities (text, image, audio, etc.)"
                        )
        
        elif selected_scan == "Sustainability Scanner":
            # Provider selection
            provider = st.selectbox(
                "Cloud Provider",
                ["AWS", "Azure", "GCP", "None/Local"],
                index=1,
                key="cloud_provider"
            )
            
            # Region selection based on provider
            region_options = {
                "AWS": ["us-east-1", "us-west-1", "eu-west-1", "ap-southeast-1"],
                "Azure": ["eastus", "westus", "northeurope", "westeurope", "eastasia"],
                "GCP": ["us-central1", "europe-west1", "asia-east1"],
                "None/Local": ["default"]
            }
            
            provider_key = provider
            regions = region_options.get(provider_key, ["default"])
            
            st.selectbox(
                "Region",
                regions,
                index=0,
                key="cloud_region"
            )
            
            # Optional code repository
            st.text_input("Repository URL (Optional)", 
                         value="https://github.com/example/repo", 
                         key="repo_url",
                         help="Optional: Include code repository for analysis")
        else:
            st.text_input("Repository URL", value="https://github.com/example/repo", key="repo_url")
            st.text_input("Branch", value="main", key="branch")
    
    with col2:
        if selected_scan == "Sustainability Scanner":
            # Custom options for sustainability scanner
            st.subheader("Sustainability Options")
            
            # Scan options specific to sustainability
            st.checkbox("CO₂ Footprint Analysis", value=True, key="option_co2_analysis",
                       help="Calculate carbon emissions from cloud resources")
            
            st.checkbox("Idle Resource Detection", value=True, key="option_idle_detection",
                       help="Identify unused or underutilized resources")
            
            st.checkbox("Code Efficiency Analysis", value=True, key="option_code_efficiency",
                       help="Analyze code for resource efficiency and bloat")
            
            # Scan depth
            st.select_slider(
                "Scan Depth",
                options=["Quick", "Standard", "Deep"],
                value="Standard",
                key="scan_depth",
                help="Quick: Basic analysis, Standard: Comprehensive, Deep: Detailed with historical data"
            )
        else:
            # Regular scan options for other scanners
            scan_options = ["Detect PII", "Check Compliance", "Generate Recommendations"]
            for option in scan_options:
                st.checkbox(option, value=True, key=f"option_{option}")
        
        # Output format option (for all scanners)
        st.selectbox(
            "Output Format",
            ["PDF Report", "CSV Export", "JSON Export"],
            key="output_format"
        )
    
    if st.button("Start Scan", type="primary", key="start_scan_button"):
        with st.spinner("Running scan..."):
            progress_bar = st.progress(0)
            for i in range(1, 101):
                progress_bar.progress(i/100)
            
            # Generate results based on scan type
            if selected_scan == "SOC2 Scanner":
                # Use our new SOC2 scanner implementation
                scanner = soc2_scanner.SOC2Scanner()
                
                # Get repository provider and URL
                repo_provider = st.session_state.get("repo_provider", "GitHub").lower()
                repo_url = st.session_state.get("repo_url", "")
                branch = st.session_state.get("branch", "main")
                
                # Set up scan configuration
                scan_config = {
                    "scan_depth": st.session_state.get("scan_depth", "Standard"),
                    "branch": branch
                }
                
                # Perform the scan
                results = scanner.scan_infrastructure(repo_url, repo_provider, **scan_config)
            elif selected_scan == "Website Scanner":
                # Define progress callback function
                def update_progress(current, total, message):
                    progress = min(current / total, 1.0)
                    progress_bar.progress(progress)
                    if message:
                        st.info(message)
                
                try:
                    # Create scanner instance with progress callback
                    region = st.session_state.get("region", "EU")
                    scanner = WebsiteScanner(region=region)
                    scanner.set_progress_callback(update_progress)
                    
                    # Get website URL and name
                    website_url = st.session_state.get("website_url", "")
                    website_name = st.session_state.get("website_name", "")
                    
                    if not website_url:
                        st.error("Please enter a website URL to scan")
                        return
                    
                    # Set up scan configuration
                    scan_config = {
                        "compliance_areas": st.session_state.get("compliance_areas", []),
                        "scan_depth": st.session_state.get("scan_depth", "Standard"),
                        "include_screenshots": st.session_state.get("include_screenshots", False)
                    }
                    
                    # Perform the scan
                    results = scanner.scan_website(website_url, website_name, **scan_config)
                    
                except Exception as e:
                    st.error(f"Error during website scan: {str(e)}")
                    website_url = st.session_state.get("website_url", "Unknown website")
                    results = {
                        "scan_type": "Website Scanner",
                        "scan_id": str(uuid.uuid4()),
                        "timestamp": datetime.now().isoformat(),
                        "website_url": website_url,
                        "error": f"Scan failed: {str(e)}",
                        "compliance_score": 0
                    }
            elif selected_scan == "AI Model Scanner":
                # Use our enhanced AI model scanner
                def update_progress(current, total, message):
                    progress = min(current / total, 1.0)
                    progress_bar.progress(progress)
                    if message:
                        st.info(message)
                
                try:
                    # Create scanner instance with progress callback
                    scanner = EnhancedAIModelScanner(region="Global")
                    scanner.set_progress_callback(update_progress)
                    
                    # Get model source and details
                    model_source = st.session_state.get("model_source", "Repository URL")
                    model_type = st.session_state.get("model_type", "ONNX")
                    
                    # Get advanced options for AI model scan
                    leakage_types = st.session_state.get("leakage_types", ["PII in Training Data", "PII in Model Output"])
                    fairness_metrics = st.session_state.get("fairness_metrics", ["Disparate Impact"])
                    explainability_checks = st.session_state.get("explainability_checks", ["Feature Importance", "Model Interpretability"])
                    context = st.session_state.get("context", ["General"])
                    
                    # Prepare model details based on source
                    model_details = {
                        # Include model_type and other parameters in model_details
                        "model_type": model_type,
                        "fairness_metrics": fairness_metrics,
                        "explainability_checks": explainability_checks
                    }
                    
                    if model_source == "Repository URL":
                        model_details.update({
                            "repo_url": st.session_state.get("repo_url", ""),
                            "branch_name": st.session_state.get("branch", "main")
                        })
                    elif model_source == "Model Hub":
                        model_details = {
                            "hub_url": st.session_state.get("hub_url", ""),
                            "repository_path": st.session_state.get("repository_path", "")
                        }
                    elif model_source == "API Endpoint":
                        model_details = {
                            "api_endpoint": st.session_state.get("api_endpoint", ""),
                            "repository_path": st.session_state.get("repository_path", "")
                        }
                    elif model_source == "Local File":
                        model_details = {
                            "file_path": st.session_state.get("file_path", "")
                        }
                    
                    # Advanced options already collected above
                    
                    # Process sample inputs from text area
                    sample_inputs_text = st.session_state.get("sample_inputs", "")
                    sample_inputs = [line.strip() for line in sample_inputs_text.split("\n") if line.strip()]
                    
                    # Get EU AI Act analysis option
                    perform_eu_ai_act = st.session_state.get("perform_eu_ai_act", True)
                    
                    # If EU AI Act analysis is enabled, add additional model details
                    if perform_eu_ai_act:
                        # Add EU AI Act specific model details
                        model_purpose = st.session_state.get("model_purpose", "General Purpose")
                        deployment_context = st.session_state.get("deployment_context", "Commercial")
                        is_foundation_model = st.session_state.get("is_foundation_model", False)
                        is_generative_ai = st.session_state.get("is_generative_ai", False)
                        
                        model_details.update({
                            "purpose": model_purpose,
                            "deployment_context": deployment_context,
                            "is_foundation_model": is_foundation_model,
                            "is_generative_ai": is_generative_ai
                        })
                    
                    try:
                        # Try to perform the enhanced AI model scan with EU AI Act analysis
                        if perform_eu_ai_act:
                            # Check if eu_ai_act modules are available
                            try:
                                # Import required modules
                                from services.eu_ai_act_analyzer import analyze_ai_model
                                from services.eu_ai_act_report_generator import create_eu_ai_act_report
                                
                                # Perform the scan with EU AI Act analysis
                                results = scanner.scan_model(
                                    model_source=model_source,
                                    model_details=model_details,
                                    leakage_types=leakage_types,
                                    context=context,
                                    sample_inputs=sample_inputs,
                                    perform_eu_ai_act_analysis=True
                                )
                            except ImportError:
                                st.warning("EU AI Act modules are not available. Running scan without EU AI Act analysis.")
                                results = scanner.scan_model(
                                    model_source=model_source,
                                    model_details=model_details,
                                    leakage_types=leakage_types,
                                    context=context,
                                    sample_inputs=sample_inputs,
                                    perform_eu_ai_act_analysis=False
                                )
                        else:
                            # Perform the scan without EU AI Act analysis
                            results = scanner.scan_model(
                                model_source=model_source,
                                model_details=model_details,
                                leakage_types=leakage_types,
                                context=context,
                                sample_inputs=sample_inputs,
                                perform_eu_ai_act_analysis=False
                            )
                    except Exception as scan_error:
                        # Fallback to basic scan if enhanced scan fails
                        st.warning(f"Enhanced AI model scan failed: {str(scan_error)}. Falling back to basic scan.")
                        results = scanner.scan_model(
                            model_source=model_source,
                            model_details=model_details,
                            leakage_types=leakage_types,
                            context=context,
                            sample_inputs=sample_inputs
                        )
                
                except Exception as e:
                    st.error(f"Error running AI Model scan: {str(e)}")
                    results = {
                        "scan_id": f"ERROR-{str(uuid.uuid4())[:8]}",
                        "scan_type": "AI Model",
                        "timestamp": datetime.now().isoformat(),
                        "error": str(e),
                        "findings": [{
                            "id": f"ERROR-{str(uuid.uuid4())[:8]}",
                            "type": "Scanner Error",
                            "category": "Execution Failure",
                            "description": f"AI Model scanner encountered an error: {str(e)}",
                            "risk_level": "high",
                            "location": "Scanner Execution"
                        }],
                        "status": "error"
                    }
                    
            elif selected_scan == "Sustainability Scanner":
                # Import and use the sustainability scanner
                try:
                    from sustainability_scanner import perform_sustainability_scan
                    
                    # Get user-selected provider and region
                    provider = st.session_state.get("cloud_provider", "Azure")
                    if provider == "None/Local":
                        provider = "none"
                    else:
                        provider = provider.lower()
                    
                    region = st.session_state.get("cloud_region", "eastus")
                    repo_url = st.session_state.get("repo_url", "")
                    scan_depth = st.session_state.get("scan_depth", "Standard")
                    
                    # Get scan options
                    scan_options = {
                        "co2_analysis": st.session_state.get("option_co2_analysis", True),
                        "idle_detection": st.session_state.get("option_idle_detection", True),
                        "code_efficiency": st.session_state.get("option_code_efficiency", True)
                    }
                    
                    # Run scan with full options
                    results = perform_sustainability_scan(
                        provider=provider, 
                        region=region, 
                        repo_url=repo_url,
                        scan_depth=scan_depth,
                        **scan_options
                    )
                except Exception as e:
                    st.error(f"Error running sustainability scan: {str(e)}")
                    results = generate_mock_scan_results(selected_scan)
            else:
                results = generate_mock_scan_results(selected_scan)
            
            st.session_state.current_scan_results = results
            
            # Add to scan history
            st.session_state.scan_history.insert(0, results)
            if len(st.session_state.scan_history) > 5:
                st.session_state.scan_history = st.session_state.scan_history[:5]
        
        st.success(f"{selected_scan} completed successfully!")
        
        # Handle different types of scan results
        if selected_scan == "SOC2 Scanner":
            try:
                # Use our integrated SOC2 scanner display function
                soc2_scanner.display_soc2_scan_results(results)
            except Exception as e:
                st.error(f"Error displaying SOC2 results: {str(e)}")
                st.json(results)
        elif selected_scan == "Website Scanner":
            try:
                # Use our website scanner display function
                display_website_scan_results(results)
            except Exception as e:
                st.error(f"Error displaying website scan results: {str(e)}")
                st.json(results)
        elif selected_scan == "AI Model Scanner":
            try:
                # Display AI model scan results
                st.subheader("AI Model Scan Results")
                
                # Display scan metadata
                st.markdown("### Scan Overview")
                
                # Create a grid for better organization
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Scan ID:** {results.get('scan_id', 'Unknown')}")
                    st.markdown(f"**Model Type:** {results.get('model_type', 'Unknown')}")
                    st.markdown(f"**Scan Date:** {datetime.fromisoformat(results.get('timestamp', datetime.now().isoformat())).strftime('%Y-%m-%d %H:%M')}")
                
                with col2:
                    # Show the risk score with proper formatting
                    risk_score = results.get("risk_score", 0)
                    if risk_score >= 75:
                        risk_color = "#ef4444"  # Red for high risk
                        risk_text = "Critical"
                    elif risk_score >= 50:
                        risk_color = "#f97316"  # Orange for medium risk
                        risk_text = "High"
                    elif risk_score >= 25:
                        risk_color = "#eab308"  # Yellow for moderate risk
                        risk_text = "Medium"
                    else:
                        risk_color = "#10b981"  # Green for low risk
                        risk_text = "Low"
                    
                    st.markdown(f"**Risk Level:** <span style='color:{risk_color};font-weight:bold'>{risk_text}</span>", unsafe_allow_html=True)
                    
                    # Display explainability score
                    explainability_score = results.get("explainability_score", 0)
                    if explainability_score >= 75:
                        exp_color = "#10b981"  # Green for high explainability
                        exp_text = "High"
                    elif explainability_score >= 50:
                        exp_color = "#eab308"  # Yellow for medium explainability
                        exp_text = "Medium"
                    else:
                        exp_color = "#f97316"  # Orange for low explainability
                        exp_text = "Low"
                        
                    st.markdown(f"**Explainability:** <span style='color:{exp_color};font-weight:bold'>{exp_text} ({explainability_score}/100)</span>", unsafe_allow_html=True)
                
                # Show model source information
                st.markdown("### Model Source Information")
                if results.get("model_source") == "Repository URL":
                    st.markdown(f"**Repository URL:** {results.get('repository_url', 'Not specified')}")
                    st.markdown(f"**Branch:** {results.get('branch', 'Not specified')}")
                elif results.get("model_source") == "Model Hub":
                    st.markdown(f"**Hub URL:** {results.get('model_name', 'Not specified')}")
                    st.markdown(f"**Path:** {results.get('repository_path', 'Not specified')}")
                elif results.get("model_source") == "API Endpoint":
                    st.markdown(f"**API Endpoint:** {results.get('api_endpoint', 'Not specified')}")
                    st.markdown(f"**Path:** {results.get('repository_path', 'Not specified')}")
                elif results.get("model_source") == "Local File":
                    st.markdown(f"**File Path:** {results.get('model_path', 'Not specified')}")
                
                # Display key findings summary
                st.markdown("### Key Findings Summary")
                
                # Create metrics for PII, bias, and explainability findings
                metric_cols = st.columns(4)
                with metric_cols[0]:
                    st.metric("Total Findings", len(results.get("findings", [])))
                with metric_cols[1]:
                    st.metric("High Risk Findings", results.get("high_risk_count", results.get("risk_counts", {}).get("high", 0)))
                with metric_cols[2]:
                    st.metric("Medium Risk Findings", results.get("medium_risk_count", results.get("risk_counts", {}).get("medium", 0)))
                with metric_cols[3]:
                    st.metric("Low Risk Findings", results.get("low_risk_count", results.get("risk_counts", {}).get("low", 0)))
                
                # Show PII and bias information
                pii_detected = results.get("personal_data_detected", False)
                bias_detected = results.get("bias_detected", False)
                
                st.markdown(f"**Personal Data Detected:** {'Yes' if pii_detected else 'No'}")
                st.markdown(f"**Bias/Fairness Issues:** {'Yes' if bias_detected else 'No'}")
                
                # Display detailed findings in an expandable section
                st.markdown("### Detailed Findings")
                findings = results.get("findings", [])
                
                if findings:
                    # Create tabs for different categories
                    tab_names = ["All Findings", "PII Detection", "Model Bias", "Explainability", "Architecture", "Compliance"]
                    
                    # Add EU AI Act tab if EU AI Act compliance analysis was performed
                    if "eu_ai_act_compliance" in results:
                        tab_names.append("EU AI Act 2025")
                        
                    tabs = st.tabs(tab_names)
                    
                    with tabs[0]:  # All Findings
                        for i, finding in enumerate(findings):
                            with st.expander(f"{finding.get('type', 'Finding')} - {finding.get('category', 'Unknown')} ({finding.get('risk_level', 'medium')})"):
                                st.markdown(f"**Description:** {finding.get('description', 'No description')}")
                                st.markdown(f"**Risk Level:** {finding.get('risk_level', 'medium')}")
                                st.markdown(f"**Location:** {finding.get('location', 'Unknown')}")
                                
                                # Show finding details if available
                                if "details" in finding and finding["details"]:
                                    st.markdown("**Details:**")
                                    details = finding["details"]
                                    for key, value in details.items():
                                        if isinstance(value, list):
                                            st.markdown(f"**{key.capitalize()}:**")
                                            for item in value:
                                                st.markdown(f"- {item}")
                                        else:
                                            st.markdown(f"**{key.capitalize()}:** {value}")
                    
                    def filter_findings(category_type):
                        return [f for f in findings if category_type.lower() in f.get("category", "").lower()]
                    
                    with tabs[1]:  # PII Detection
                        pii_findings = filter_findings("PII")
                        if pii_findings:
                            for finding in pii_findings:
                                with st.expander(f"{finding.get('type', 'Finding')} ({finding.get('risk_level', 'medium')})"):
                                    st.markdown(f"**Description:** {finding.get('description', 'No description')}")
                                    st.markdown(f"**Risk Level:** {finding.get('risk_level', 'medium')}")
                                    st.markdown(f"**Location:** {finding.get('location', 'Unknown')}")
                                    
                                    # Show finding details if available
                                    if "details" in finding and finding["details"]:
                                        st.markdown("**Details:**")
                                        details = finding["details"]
                                        for key, value in details.items():
                                            if isinstance(value, list):
                                                st.markdown(f"**{key.capitalize()}:**")
                                                for item in value:
                                                    st.markdown(f"- {item}")
                                            else:
                                                st.markdown(f"**{key.capitalize()}:** {value}")
                        else:
                            st.info("No PII detection findings")
                    
                    with tabs[2]:  # Model Bias
                        bias_findings = filter_findings("Bias")
                        if bias_findings:
                            for finding in bias_findings:
                                with st.expander(f"{finding.get('type', 'Finding')} ({finding.get('risk_level', 'medium')})"):
                                    st.markdown(f"**Description:** {finding.get('description', 'No description')}")
                                    st.markdown(f"**Risk Level:** {finding.get('risk_level', 'medium')}")
                                    st.markdown(f"**Location:** {finding.get('location', 'Unknown')}")
                                    
                                    # Show finding details if available
                                    if "details" in finding and finding["details"]:
                                        st.markdown("**Details:**")
                                        details = finding["details"]
                                        for key, value in details.items():
                                            if isinstance(value, list):
                                                st.markdown(f"**{key.capitalize()}:**")
                                                for item in value:
                                                    st.markdown(f"- {item}")
                                            else:
                                                st.markdown(f"**{key.capitalize()}:** {value}")
                        else:
                            st.info("No model bias findings")
                            
                    with tabs[3]:  # Explainability
                        explainability_findings = filter_findings("Explainability")
                        if explainability_findings:
                            for finding in explainability_findings:
                                with st.expander(f"{finding.get('type', 'Finding')} ({finding.get('risk_level', 'medium')})"):
                                    st.markdown(f"**Description:** {finding.get('description', 'No description')}")
                                    st.markdown(f"**Risk Level:** {finding.get('risk_level', 'medium')}")
                                    st.markdown(f"**Location:** {finding.get('location', 'Unknown')}")
                                    
                                    # Show finding details if available
                                    if "details" in finding and finding["details"]:
                                        st.markdown("**Details:**")
                                        details = finding["details"]
                                        for key, value in details.items():
                                            if isinstance(value, list):
                                                st.markdown(f"**{key.capitalize()}:**")
                                                for item in value:
                                                    st.markdown(f"- {item}")
                                            else:
                                                st.markdown(f"**{key.capitalize()}:** {value}")
                        else:
                            st.info("No explainability findings")
                            
                    with tabs[4]:  # Architecture
                        arch_findings = filter_findings("Architecture")
                        if arch_findings:
                            for finding in arch_findings:
                                with st.expander(f"{finding.get('type', 'Finding')} ({finding.get('risk_level', 'medium')})"):
                                    st.markdown(f"**Description:** {finding.get('description', 'No description')}")
                                    st.markdown(f"**Risk Level:** {finding.get('risk_level', 'medium')}")
                                    st.markdown(f"**Location:** {finding.get('location', 'Unknown')}")
                                    
                                    # Show finding details if available
                                    if "details" in finding and finding["details"]:
                                        st.markdown("**Details:**")
                                        details = finding["details"]
                                        for key, value in details.items():
                                            if isinstance(value, list):
                                                st.markdown(f"**{key.capitalize()}:**")
                                                for item in value:
                                                    st.markdown(f"- {item}")
                                            else:
                                                st.markdown(f"**{key.capitalize()}:** {value}")
                        else:
                            st.info("No architecture findings")
                            
                    with tabs[5]:  # Compliance
                        compliance_findings = filter_findings("Compliance")
                        if compliance_findings:
                            for finding in compliance_findings:
                                with st.expander(f"{finding.get('type', 'Finding')} ({finding.get('risk_level', 'medium')})"):
                                    st.markdown(f"**Description:** {finding.get('description', 'No description')}")
                                    st.markdown(f"**Risk Level:** {finding.get('risk_level', 'medium')}")
                                    st.markdown(f"**Location:** {finding.get('location', 'Unknown')}")
                                    
                                    # Show finding details if available
                                    if "details" in finding and finding["details"]:
                                        st.markdown("**Details:**")
                                        details = finding["details"]
                                        for key, value in details.items():
                                            if isinstance(value, list):
                                                st.markdown(f"**{key.capitalize()}:**")
                                                for item in value:
                                                    st.markdown(f"- {item}")
                                            else:
                                                st.markdown(f"**{key.capitalize()}:** {value}")
                        else:
                            st.info("No compliance findings")
                    
                    # Add EU AI Act Compliance tab content
                    if "eu_ai_act_compliance" in results:
                        with tabs[6]:  # EU AI Act 2025 tab
                            # Check if there was an error with EU AI Act analysis
                            if "eu_ai_act_compliance_error" in results:
                                st.error(f"Error during EU AI Act analysis: {results.get('eu_ai_act_compliance_error')}")
                                st.info("The main AI model scan completed successfully, but there was an error with the EU AI Act compliance analysis.")
                                st.markdown("---")
                            
                            eu_ai_act = results.get("eu_ai_act_compliance", {})
                            
                            # Display EU AI Act compliance overview
                            st.markdown("### EU AI Act 2025 Compliance Overview")
                            
                            # Display risk category with appropriate styling
                            risk_category = eu_ai_act.get("risk_category", "unclassified")
                            
                            if risk_category == "prohibited":
                                category_color = "#dc2626"  # Red
                                category_text = "Prohibited AI Practice"
                            elif risk_category == "high_risk":
                                category_color = "#f97316"  # Orange
                                category_text = "High-Risk AI System"
                            elif risk_category == "limited_risk":
                                category_color = "#eab308"  # Yellow
                                category_text = "Limited Risk AI System" 
                            elif risk_category == "minimal_risk":
                                category_color = "#10b981"  # Green
                                category_text = "Minimal Risk AI System"
                            elif risk_category == "general_purpose":
                                category_color = "#3b82f6"  # Blue
                                category_text = "General Purpose AI System"
                            else:
                                category_color = "#6b7280"  # Gray
                                category_text = "Unclassified AI System"
                            
                            st.markdown(f"**Risk Category:** <span style='color:{category_color};font-weight:bold'>{category_text}</span>", unsafe_allow_html=True)
                            
                            # Display compliance score with color coding
                            compliance_score = eu_ai_act.get("compliance_score", 0)
                            if compliance_score >= 80:
                                score_color = "#10b981"  # Green
                                score_text = "High"
                            elif compliance_score >= 60:
                                score_color = "#eab308"  # Yellow
                                score_text = "Medium"
                            else:
                                score_color = "#f97316"  # Orange
                                score_text = "Low"
                                
                            st.markdown(f"**Compliance Score:** <span style='color:{score_color};font-weight:bold'>{score_text} ({compliance_score}/100)</span>", unsafe_allow_html=True)
                            
                            # Display EU AI Act compliance findings
                            st.markdown("### EU AI Act Compliance Findings")
                            
                            compliance_findings = eu_ai_act.get("compliance_findings", [])
                            if compliance_findings:
                                for finding in compliance_findings:
                                    with st.expander(f"{finding.get('type', 'Requirement')} ({finding.get('compliance_status', 'Unknown')})"):
                                        st.markdown(f"**Description:** {finding.get('description', 'No description')}")
                                        st.markdown(f"**Status:** {finding.get('compliance_status', 'Unknown')}")
                                        
                                        # Show finding details if available
                                        if "details" in finding:
                                            details = finding["details"]
                                            if isinstance(details, dict):
                                                st.markdown("**Details:**")
                                                for key, value in details.items():
                                                    if isinstance(value, list):
                                                        st.markdown(f"**{key.capitalize()}:**")
                                                        for item in value:
                                                            st.markdown(f"- {item}")
                                                    else:
                                                        st.markdown(f"**{key.capitalize()}:** {value}")
                                            elif isinstance(details, str):
                                                st.markdown(f"**Details:** {details}")
                            else:
                                st.info("No EU AI Act compliance findings available")
                            
                            # Display EU AI Act recommendations
                            st.markdown("### EU AI Act Recommendations")
                            
                            recommendations = eu_ai_act.get("recommendations", [])
                            if recommendations:
                                for i, recommendation in enumerate(recommendations):
                                    try:
                                        # Handle both string and dictionary recommendations
                                        if isinstance(recommendation, dict):
                                            with st.expander(f"Recommendation {i+1}"):
                                                st.markdown(f"**Recommendation:** {recommendation.get('text', 'No recommendation text')}")
                                                st.markdown(f"**Priority:** {recommendation.get('priority', 'Medium')}")
                                                
                                                # Show action items if available
                                                if "action_items" in recommendation and recommendation["action_items"]:
                                                    st.markdown("**Action Items:**")
                                                    if isinstance(recommendation["action_items"], list):
                                                        for item in recommendation["action_items"]:
                                                            st.markdown(f"- {item}")
                                                    elif isinstance(recommendation["action_items"], str):
                                                        st.markdown(f"- {recommendation['action_items']}")
                                        elif isinstance(recommendation, str):
                                            with st.expander(f"Recommendation {i+1}"):
                                                st.markdown(f"**Recommendation:** {recommendation}")
                                    except Exception as rec_error:
                                        st.warning(f"Error displaying recommendation: {str(rec_error)}")
                            else:
                                st.info("No recommendations available")
                else:
                    st.info("No findings were identified in this scan.")

                # Create a container for report downloads
                report_col1, report_col2 = st.columns(2)
                
                # Display PDF report download if available
                with report_col1:
                    if "report_path" in results and results["report_path"]:
                        try:
                            report_path = results["report_path"]
                            # Check if file exists before attempting to read it
                            if os.path.exists(report_path):
                                with open(report_path, "rb") as f:
                                    report_data = f.read()
                                
                                if len(report_data) > 0:
                                    st.download_button(
                                        label="📄 Download AI Model Scan Report",
                                        data=report_data,
                                        file_name=f"ai_model_scan_{results.get('scan_id', 'report')}.pdf",
                                        mime="application/pdf",
                                        key="download_ai_model_report"
                                    )
                                else:
                                    st.warning("AI Model report file exists but is empty.")
                            else:
                                st.warning(f"AI Model report file not found: {report_path}")
                        except Exception as e:
                            st.warning(f"Error loading AI Model scan report: {str(e)}")
                
                # Display EU AI Act report download if available
                with report_col2:
                    if "eu_ai_act_report_path" in results and results["eu_ai_act_report_path"]:
                        try:
                            eu_report_path = results["eu_ai_act_report_path"]
                            # Check if file exists before attempting to read it
                            if os.path.exists(eu_report_path):
                                with open(eu_report_path, "rb") as f:
                                    eu_report_data = f.read()
                                
                                if len(eu_report_data) > 0:
                                    st.download_button(
                                        label="📄 Download EU AI Act Compliance Report",
                                        data=eu_report_data,
                                        file_name=f"eu_ai_act_report_{results.get('scan_id', 'report')}.pdf",
                                        mime="application/pdf",
                                        key="download_eu_ai_act_report"
                                    )
                                else:
                                    st.warning("EU AI Act report file exists but is empty.")
                            else:
                                st.warning(f"EU AI Act report file not found: {eu_report_path}")
                        except Exception as e:
                            st.warning(f"Error loading EU AI Act report: {str(e)}")
                        
            except Exception as e:
                st.error(f"Error displaying AI Model scan results: {str(e)}")
                st.json(results)
        elif selected_scan == "Sustainability Scanner":
            try:
                from sustainability_scanner import display_sustainability_scan_results
                display_sustainability_scan_results(results)
            except Exception as e:
                st.error(f"Error displaying sustainability results: {str(e)}")
                st.json(results)
        elif selected_scan == "GDPR Code Scanner":
            # Display the scan results
            st.json(results)
            
            # Add a header with basic styling
            st.markdown("---")
            st.markdown("## 📋 GDPR Report Generation")
            
            # Show key metrics
            st.subheader("Key Compliance Metrics")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Compliance Score", f"{results.get('compliance_score', 75)}%")
                st.metric("High Risk Findings", results.get('high_risk', 3))
            with col2:
                st.metric("Total Findings", results.get('total_findings', len(results.get('findings', [])))  )
                st.metric("Generated", datetime.now().strftime('%Y-%m-%d'))
            
            # MODERN PDF GENERATION
            st.markdown("---")
            st.subheader("Generate Professional PDF Report")
            
            # Add explanation
            st.info("Generate a professional GDPR compliance report with modern styling.")
            
            # PROFESSIONAL PDF GENERATION
            st.subheader("Generate Professional GDPR Report")
            
            # Form for PDF customization
            col1, col2 = st.columns(2)
            
            with col1:
                organization_name = st.text_input("Organization Name", "Your Organization")
                certification_type = st.selectbox(
                    "Certification Type",
                    ["GDPR Compliant", "ISO 27001 Aligned", "UAVG Certified"]
                )
            
            with col2:
                compliance_score = results.get('compliance_score', 75)
                st.metric("Compliance Score", f"{compliance_score}%")
                high_risk = results.get('high_risk', 3)
                total_findings = results.get('total_findings', len(results.get('findings', [])))
            
            # Generate PDF button
            if st.button("Generate Professional PDF", type="primary"):
                try:
                    # Show a spinner while generating
                    with st.spinner("Generating your professional GDPR report..."):
                        # Import our modern PDF generator
                        from simple_modern_pdf import create_gdpr_pdf
                        
                        # Generate the PDF
                        pdf_data = create_gdpr_pdf(
                            organization_name=organization_name,
                            certification_type=certification_type,
                            compliance_score=compliance_score,
                            high_risk=high_risk,
                            total_findings=total_findings
                        )
                        
                        # Success message
                        st.success("✓ Your professional GDPR report is ready!")
                        
                        # Display download button
                        st.download_button(
                            label="Download Professional GDPR Report",
                            data=pdf_data,
                            file_name=f"GDPR_Report_{organization_name.replace(' ', '_')}.pdf",
                            mime="application/pdf",
                            key="modern_pdf_download",
                            use_container_width=True
                        )
                        
                        # Preview
                        st.subheader("What's included in your report:")
                        st.info(f"""
                        Your professional GDPR compliance report includes:
                        
                        - **Organization**: {organization_name}
                        - **Certification**: {certification_type}
                        - **Compliance Score**: {compliance_score}%
                        - **All 7 GDPR principles** with detailed assessment
                        - **Risk analysis** for each compliance area
                        - **Verification details** with unique certificate ID
                        - **Professional blue styling** with modern design
                        """)
                
                except Exception as e:
                    st.error(f"Error generating PDF: {str(e)}")
                    
                    # Fallback to simple PDF
                    simple_pdf = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/MediaBox[0 0 595 842]/Parent 2 0 R/Resources<</Font<</F1<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>>>>>/Contents 4 0 R>>endobj
4 0 obj<</Length 90>>stream
BT
/F1 24 Tf
50 800 Td
(GDPR Compliance Report) Tj
/F1 12 Tf
0 -50 Td
(Basic GDPR compliance report) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000010 00000 n
0000000053 00000 n
0000000102 00000 n
0000000229 00000 n
trailer<</Size 5/Root 1 0 R>>
startxref
368
%%EOF"""
                    
                    # Show fallback download button
                    st.warning("Using fallback simple PDF instead")
                    st.download_button(
                        label="Download Simple GDPR Report (Fallback)",
                        data=simple_pdf,
                        file_name="Simple_GDPR_Report.pdf",
                        mime="application/pdf"
                    )
        else:
            st.json(results)

def render_reports_section():
    """Render reports section"""
    st.subheader("Compliance Reports")
    
    if not st.session_state.scan_history:
        st.info("No scan history available. Run a scan to generate reports.")
    else:
        # Create scan options list with safe dictionary access
        scan_options = [
            f"{scan.get('scan_type', 'Scan')} - {datetime.fromisoformat(scan.get('timestamp', datetime.now().isoformat())).strftime('%Y-%m-%d %H:%M')}" 
            for scan in st.session_state.scan_history
        ]
        selected_report = st.selectbox("Select Scan for Report", scan_options, key="report_select")
        
        report_types = ["Summary Report", "Full Report", "Technical Report", "Executive Report"]
        report_format = st.radio("Report Format", report_types, horizontal=True)
        
        if st.button("Generate Report", key="generate_report_button"):
            with st.spinner("Generating report..."):
                # Wait for report generation (removed time.sleep)
                
                # Get selected scan results
                selected_index = scan_options.index(selected_report)
                scan_data = st.session_state.scan_history[selected_index]
                
                st.subheader(f"{report_format}: {scan_data.get('scan_type', 'Compliance Analysis')}")
                
                # Display report content using .get() for safe access
                st.markdown(f"""
                ## {scan_data.get('scan_type', 'Compliance')} Compliance Report
                **Generated:** {datetime.fromisoformat(scan_data.get('timestamp', datetime.now().isoformat())).strftime('%Y-%m-%d %H:%M')}
                
                ### Summary
                - **Total Findings:** {scan_data.get('total_findings', scan_data.get('findings_count', 0))}
                - **High Risk Issues:** {scan_data.get('high_risk', 0)}
                - **Medium Risk Issues:** {scan_data.get('medium_risk', 0)}
                - **Low Risk Issues:** {scan_data.get('low_risk', 0)}
                - **Overall Compliance Score:** {scan_data.get('compliance_score', 0)}%
                
                ### Key Findings
                Total: {scan_data.get('total_findings', scan_data.get('findings_count', 0))} findings ({scan_data.get('high_risk', 0)} high, {scan_data.get('medium_risk', 0)} medium, {scan_data.get('low_risk', 0)} low risk)
                """)
                
                # Display findings in a table with safe access
                findings = scan_data.get('findings', [])
                if findings:
                    findings_df = pd.DataFrame([
                        {
                            "ID": finding.get("id", f"FIND-{i+1}"),
                            "Title": finding.get("title", f"Finding {i+1}"),
                            "Severity": finding.get("severity", finding.get("risk_level", "medium")).upper(),
                            "Location": finding.get("location", finding.get("resource_type", "N/A"))
                        } for i, finding in enumerate(findings)  # Show all findings
                    ])
                    st.dataframe(findings_df, use_container_width=True)
                
                # Generate a basic PDF report with proper error handling
                try:
                    # Create PDF buffer
                    buffer = io.BytesIO()
                    
                    try:
                        # Try to use reportlab to generate PDF
                        from reportlab.lib.pagesizes import letter
                        from reportlab.lib import colors
                        from reportlab.lib.units import inch
                        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
                        from reportlab.graphics.shapes import Drawing, Rect, Line, Circle, String
                        from reportlab.graphics.charts.lineplots import LinePlot
                        from reportlab.graphics import renderPDF
                        
                        # Create document with margins
                        doc = SimpleDocTemplate(
                            buffer, 
                            pagesize=letter,
                            topMargin=0.5*inch,
                            bottomMargin=0.5*inch,
                            leftMargin=0.5*inch,
                            rightMargin=0.5*inch
                        )
                        styles = getSampleStyleSheet()
                        
                        # Create a custom style for the title
                        title_style = ParagraphStyle(
                            'Title',
                            parent=styles['Heading1'],
                            fontSize=16,
                            textColor=colors.HexColor('#1E5288'),
                            spaceAfter=12
                        )
                        
                        # Create a better normal text style
                        normal_style = ParagraphStyle(
                            'CustomNormal',
                            parent=styles['Normal'],
                            fontSize=10,
                            leading=14,
                            spaceBefore=6,
                            spaceAfter=6
                        )
                        
                        # Create a DataGuardian Pro logo using ReportLab drawing
                        logo_width, logo_height = int(1.5*inch), int(0.75*inch)
                        logo = Drawing(logo_width, logo_height)
                        
                        # Add a shield shape
                        shield = Rect(
                            x=0.3*inch, y=0.1*inch, 
                            width=0.4*inch, height=0.5*inch, 
                            fillColor=colors.HexColor('#1E5288'),
                            strokeColor=None
                        )
                        logo.add(shield)
                        
                        # Add data lines to represent scanning
                        for i in range(3):
                            y_pos = 0.2*inch + i*0.12*inch
                            line = Line(
                                x1=0.4*inch, y1=y_pos,
                                x2=0.6*inch, y2=y_pos,
                                strokeColor=colors.white,
                                strokeWidth=2
                            )
                            logo.add(line)
                        
                        # Add a checkmark for compliance
                        circle = Circle(
                            cx=0.5*inch, cy=0.4*inch,
                            r=0.12*inch,
                            fillColor=colors.white,
                            strokeColor=None
                        )
                        logo.add(circle)
                        
                        # Add company name
                        company_name = String(
                            x=0.75*inch, y=0.35*inch,
                            text="DataGuardian Pro",
                            fontSize=14,
                            fillColor=colors.HexColor('#1E5288')
                        )
                        logo.add(company_name)
                        
                        # Initialize the story for the PDF
                        story = []
                        
                        # Add report header with logo
                        story.append(logo)
                        story.append(Spacer(1, 0.1*inch))
                        story.append(Paragraph(f"{scan_data.get('scan_type', 'Compliance')} Report", title_style))
                        story.append(Spacer(1, 0.25*inch))
                        
                        # Add date and scan info
                        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
                        story.append(Paragraph(f"Scan ID: {scan_data.get('scan_id', 'N/A')}", styles['Normal']))
                        story.append(Spacer(1, 0.25*inch))
                        
                        # Add summary table
                        summary_data = [
                            ['Metric', 'Value'],
                            ['Total Findings', str(scan_data.get('total_findings', scan_data.get('findings_count', 0)))],
                            ['High Risk', str(scan_data.get('high_risk', 0))],
                            ['Medium Risk', str(scan_data.get('medium_risk', 0))],
                            ['Low Risk', str(scan_data.get('low_risk', 0))],
                            ['Compliance Score', f"{scan_data.get('compliance_score', 0)}%"],
                        ]
                        
                        summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
                        summary_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
                            ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
                            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0, 0), (1, 0), 12),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ]))
                        
                        story.append(summary_table)
                        story.append(Spacer(1, 0.25*inch))
                        
                        # Add findings section with counts
                        story.append(Paragraph("Key Findings", styles['Heading2']))
                        story.append(Paragraph(f"Total: {scan_data.get('total_findings', scan_data.get('findings_count', 0))} findings ({scan_data.get('high_risk', 0)} high, {scan_data.get('medium_risk', 0)} medium, {scan_data.get('low_risk', 0)} low risk)", styles['Normal']))
                        story.append(Spacer(1, 0.15*inch))
                        
                        if findings:
                            # Create findings table data
                            findings_table_data = [['ID', 'Title', 'Severity', 'Location']]
                            
                            for i, finding in enumerate(findings):  # Show all findings
                                findings_table_data.append([
                                    finding.get('id', f"FIND-{i+1}"),
                                    finding.get('title', f"Finding {i+1}"),
                                    finding.get('severity', finding.get('risk_level', 'medium')).upper(),
                                    finding.get('location', finding.get('resource_type', 'N/A'))
                                ])
                            
                            findings_table = Table(findings_table_data, colWidths=[0.75*inch, 3*inch, 1*inch, 1.5*inch])
                            findings_table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ]))
                            
                            story.append(findings_table)
                        else:
                            story.append(Paragraph("No findings were detected in this scan.", styles['Normal']))
                        
                        # Add additional sections - recommendations
                        story.append(Spacer(1, 0.25*inch))
                        story.append(Paragraph("Recommendations", styles['Heading2']))
                        
                        recommendations = scan_data.get('recommendations', [])
                        if recommendations:
                            for i, recommendation in enumerate(recommendations[:3]):  # Top 3 recommendations
                                story.append(Paragraph(f"{i+1}. {recommendation}", styles['Normal']))
                                story.append(Spacer(1, 0.1*inch))
                        else:
                            story.append(Paragraph("No specific recommendations for this scan.", styles['Normal']))
                        
                        # Build the PDF
                        doc.build(story)
                        pdf_data = buffer.getvalue()
                        buffer.close()
                        
                    except ImportError:
                        # Fallback to a very simple PDF if reportlab isn't available
                        pdf_data = f"""
                        %PDF-1.4
                        1 0 obj
                        <<
                        /Type /Catalog
                        /Pages 2 0 R
                        >>
                        endobj
                        2 0 obj
                        <<
                        /Type /Pages
                        /Kids [3 0 R]
                        /Count 1
                        >>
                        endobj
                        3 0 obj
                        <<
                        /Type /Page
                        /Parent 2 0 R
                        /Resources <<
                        /Font <<
                        /F1 4 0 R
                        >>
                        >>
                        /MediaBox [0 0 612 792]
                        /Contents 5 0 R
                        >>
                        endobj
                        4 0 obj
                        <<
                        /Type /Font
                        /Subtype /Type1
                        /Name /F1
                        /BaseFont /Helvetica
                        >>
                        endobj
                        5 0 obj
                        << /Length 172 >>
                        stream
                        BT
                        /F1 24 Tf
                        72 700 Td
                        ({scan_data.get('scan_type', 'Compliance')} Report) Tj
                        /F1 12 Tf
                        0 -40 Td
                        (Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) Tj
                        ET
                        endstream
                        endobj
                        xref
                        0 6
                        0000000000 65535 f
                        0000000010 00000 n
                        0000000060 00000 n
                        0000000120 00000 n
                        0000000270 00000 n
                        0000000350 00000 n
                        trailer
                        <<
                        /Size 6
                        /Root 1 0 R
                        >>
                        startxref
                        580
                        %%EOF
                        """.encode('utf-8')
                    
                    # Add download button with the generated PDF
                    st.download_button(
                        label="Download Report (PDF)",
                        data=pdf_data,
                        file_name=f"{scan_data.get('scan_type', 'compliance_report').replace(' ', '_')}_report.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"Error generating PDF report: {str(e)}")
                    st.info("Please try again or contact support if the problem persists.")

def render_admin_section():
    """Render admin section"""
    # Use our new admin panel with RBAC protection
    render_admin_panel()

# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    """Main application entry point"""
    # Import enhanced signup flow components
    from enhanced_signup_flow import render_enhanced_signup_page as render_signup_page
    
    # Import remaining components from signup_flow
    from signup_flow import (
        render_trial_expiry_notice,
        render_payment_method_selection
    )
    
    # Check for Google OAuth callback
    query_params = st.query_params
    if "code" in query_params and "state" in query_params and not st.session_state.get("logged_in", False):
        from google_oauth_callback import process_google_oauth_callback
        process_google_oauth_callback()
    
    # Sidebar content
    with st.sidebar:
        render_brand_logo()
        
        if not st.session_state.logged_in:
            if st.session_state.get("current_view") not in ["signup", "payment_method"]:
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
    
    # Main content for logged out users - Landing, Signup, or Payment flows
    if not st.session_state.logged_in:
        # Handle different views for logged-out users
        current_view = st.session_state.get("current_view", "landing")
        
        if current_view == "landing":
            render_landing_page()
        elif current_view == "signup":
            render_signup_page()
        elif current_view == "login":
            st.info("Please log in using the form in the sidebar.")
        elif current_view == "password_reset":
            # Import and run the password reset flow
            from password_reset import run_password_reset_flow
            run_password_reset_flow()
        elif current_view == "payment_method":
            st.warning("You need to create an account or log in before adding a payment method.")
            if st.button("Back to Signup", key="back_to_signup"):
                st.session_state.current_view = "signup"
                st.rerun()
    else:
        # Check for trial expiry notice for logged-in users
        render_trial_expiry_notice()
        
        # Handle payment method addition for users who've just signed up
        if st.session_state.get("current_view") == "payment_method":
            render_payment_method_selection()
        else:
            # Create tabs for main dashboard content
            tabs = st.tabs(["Dashboard", "Scan", "Reports", "Profile", "Billing", "Admin"])
            
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
            
            # Profile Tab
            with tabs[3]:
                st.header("User Profile")
                render_user_profile_page()
            
            # Billing Tab
            with tabs[4]:
                st.header("Billing & Subscription")
                # Make sure user_data exists in session state
                if "user_data" not in st.session_state:
                    # Create default user data if it doesn't exist
                    st.session_state.user_data = {
                        "username": st.session_state.username,
                        "email": st.session_state.get("email", ""),
                        "role": st.session_state.get("role", "user"),
                        "subscription_tier": st.session_state.get("subscription_tier", "basic"),
                        "subscription_active": st.session_state.get("subscription_active", False),
                        "stripe_customer_id": st.session_state.get("stripe_customer_id", "")
                    }
                # Check if we have return parameters from bank payment
                query_params = dict(st.query_params.items())
                has_payment_return = any(param in query_params for param in [
                    "payment_intent", "payment_success", "payment_canceled"
                ])
                
                if has_payment_return:
                    # Import and use the payment return handler
                    from billing.payment_return_handler import render_payment_return_page
                    render_payment_return_page()
                else:
                    # Use our comprehensive billing page for the logged-in user
                    render_billing_page(st.session_state.username, st.session_state.user_data)
                
            # Admin Tab
            with tabs[5]:
                st.header("Administration")
                # Use our RBAC-protected admin section
                render_admin_section()

if __name__ == "__main__":
    main()