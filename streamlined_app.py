import streamlit as st
import pandas as pd
import time
import json
import os
import io
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
        st.button("Start Free Trial", type="primary", use_container_width=True)
    
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
        st.button("Sign Up Now", type="primary", use_container_width=True, key="signup_button")

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
                time.sleep(1.5)  # Simulate report generation
                
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
                """)
                
                # Display findings in a table with safe access
                findings = scan_data.get('findings', [])
                if findings:
                    findings_df = pd.DataFrame([
                        {
                            "ID": finding.get("id", f"FIND-{i+1}"),
                            "Title": finding.get("title", f"Finding {i+1}"),
                            "Severity": finding.get("severity", "medium").upper(),
                            "Location": finding.get("location", "N/A")
                        } for i, finding in enumerate(findings[:5])  # Show top 5 findings
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
                        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
                        
                        # Create document
                        doc = SimpleDocTemplate(buffer, pagesize=letter)
                        styles = getSampleStyleSheet()
                        story = []
                        
                        # Add report header
                        title_style = ParagraphStyle(
                            name='Title',
                            parent=styles['Title'],
                            fontSize=16,
                            leading=20,
                        )
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
                        
                        # Add findings section
                        story.append(Paragraph("Key Findings", styles['Heading2']))
                        
                        if findings:
                            # Create findings table data
                            findings_table_data = [['ID', 'Title', 'Severity', 'Location']]
                            
                            for i, finding in enumerate(findings[:5]):  # Show top 5 findings
                                findings_table_data.append([
                                    finding.get('id', f"FIND-{i+1}"),
                                    finding.get('title', f"Finding {i+1}"),
                                    finding.get('severity', 'medium').upper(),
                                    finding.get('location', 'N/A')
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