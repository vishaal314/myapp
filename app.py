import streamlit as st
# Disable visualization dependencies to resolve numpy conflicts
# Core Image Scanner functionality preserved
pd = None
px = None
VISUALIZATION_AVAILABLE = False
import os
import uuid
import random
import string
import logging
import traceback
from datetime import datetime
import json
import base64
from io import BytesIO

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create a logger instance for this module
logger = logging.getLogger(__name__)

from services.code_scanner import CodeScanner
from services.blob_scanner import BlobScanner
from services.website_scanner import WebsiteScanner
from services.results_aggregator import ResultsAggregator
from services.repo_scanner import RepoScanner
from services.report_generator_safe import generate_report
from services.certificate_generator import CertificateGenerator
from services.optimized_scanner import OptimizedScanner
from services.dpia_scanner import DPIAScanner, generate_dpia_report
from services.ai_model_scanner import AIModelScanner
from services.enhanced_soc2_scanner import scan_github_repository, scan_azure_repository, display_soc2_scan_results
from services.auth import authenticate, is_authenticated, logout, create_user, validate_email
from services.soc2_display import display_soc2_findings, run_soc2_display_standalone
from services.soc2_scanner import scan_github_repo_for_soc2, scan_azure_repo_for_soc2
from services.stripe_payment import display_payment_button, handle_payment_callback, SCAN_PRICES
from utils.gdpr_rules import REGIONS, get_region_rules
from utils.risk_analyzer import RiskAnalyzer, get_severity_color, colorize_finding, get_risk_color_gradient
from utils.i18n import initialize, language_selector, get_text, set_language, LANGUAGES, _translations

# Define translation function
def _(key, default=None):
    return get_text(key, default)
from utils.compliance_score import calculate_compliance_score, display_compliance_score_card

# Initialize language system
if 'language' not in st.session_state:
    st.session_state['language'] = 'en'
    st.session_state['_persistent_language'] = 'en'
    st.session_state['backup_language'] = 'en'

current_language = st.session_state.get('language', 'en')
initialize()

# Set page config
st.set_page_config(
    page_title="DataGuardian Pro",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application function"""
    
    # Initialize language and session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # Show header
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #4a90e2; margin-bottom: 0.5rem;">DataGuardian Pro</h1>
        <p style="color: #666; font-size: 1.2rem; margin: 0;">Enterprise Privacy Compliance Platform</p>
        <p style="color: #888; margin-top: 0.5rem;">Detect, Manage, and Report Privacy Compliance with AI-powered Precision</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Language selector
    st.sidebar.markdown("### Language / Taal")
    
    language_options = {
        'en': '🇺🇸 English',
        'nl': '🇳🇱 Nederlands'
    }
    
    selected_language = st.sidebar.selectbox(
        "Choose Language",
        options=list(language_options.keys()),
        format_func=lambda x: language_options[x],
        index=list(language_options.keys()).index(current_language),
        key="language_selector"
    )
    
    if selected_language != current_language:
        st.session_state.language = selected_language
        st.session_state._persistent_language = selected_language
        set_language(selected_language)
        st.rerun()
    
    # Authentication
    if not st.session_state.get('authenticated', False):
        handle_authentication()
        return
    
    # Navigation
    st.sidebar.markdown("### Navigation")
    
    nav_options = [
        _("scan.title", "Scan"),
        "Simple DPIA",
        _("dashboard.welcome", "Dashboard"),
        _("history.title", "History"),
        _("results.title", "Results"),
        _("report.generate", "Report")
    ]
    
    if st.session_state.get('user_role', 'user') == 'admin':
        nav_options.append(_("admin.title", "Admin"))
    
    selected_nav = st.sidebar.radio("Select", nav_options)
    
    # Logout button
    if st.sidebar.button("Logout", key="logout_button"):
        st.session_state.authenticated = False
        st.session_state.pop('username', None)
        st.session_state.pop('user_email', None)
        st.session_state.pop('user_role', None)
        st.rerun()
    
    # Main content based on navigation
    if selected_nav == _("scan.title", "Scan"):
        show_scan_interface()
    elif selected_nav == "Simple DPIA":
        show_simple_dpia()
    elif selected_nav == _("dashboard.welcome", "Dashboard"):
        show_dashboard()
    elif selected_nav == _("history.title", "History"):
        show_history()
    elif selected_nav == _("results.title", "Results"):
        show_results()
    elif selected_nav == _("report.generate", "Report"):
        show_reports()
    elif selected_nav == _("admin.title", "Admin"):
        show_admin()

def handle_authentication():
    """Handle authentication"""
    auth_tabs = st.tabs(["Login", "Register"])
    
    with auth_tabs[0]:
        st.markdown("### Login")
        
        with st.form("login_form"):
            username_or_email = st.text_input("Username or Email")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")
            
            if login_button:
                if username_or_email and password:
                    user_data = authenticate(username_or_email, password)
                    if user_data:
                        st.session_state.authenticated = True
                        st.session_state.username = user_data['username']
                        st.session_state.user_email = user_data['email']
                        st.session_state.user_role = user_data.get('role', 'user')
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username/email or password")
                else:
                    st.error("Please enter both username/email and password")
    
    with auth_tabs[1]:
        st.markdown("### Register")
        
        role_options = {
            'user': 'Standard User - Basic scanning capabilities',
            'premium_user': 'Premium User - Advanced features and unlimited scans',
            'compliance_officer': 'Compliance Officer - Full compliance management',
            'privacy_officer': 'Privacy Officer - Complete privacy assessment tools',
            'enterprise_user': 'Enterprise User - Full enterprise features',
            'consultant': 'Privacy Consultant - Professional consulting tools',
            'admin': 'Administrator - Full system access'
        }
        
        with st.form("registration_form"):
            new_username = st.text_input("Username")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            new_role = st.selectbox("Role", options=list(role_options.keys()), 
                                   format_func=lambda x: role_options[x])
            terms = st.checkbox("I agree to the Terms and Conditions")
            register_button = st.form_submit_button("Register")
            
            if register_button:
                if new_username and new_email and new_password and new_password == confirm_password and terms:
                    success, message = create_user(new_username, new_password, new_role, new_email)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.error("Please fill all fields correctly and accept terms")

def show_scan_interface():
    """Show the main scanning interface"""
    st.markdown("## Privacy Compliance Scanning")
    
    # Scanner selection
    scanner_tabs = st.tabs([
        "Code Scanner",
        "Document Scanner", 
        "Image Scanner",
        "Website Scanner",
        "Database Scanner",
        "AI Model Scanner",
        "SOC2 Scanner",
        "Sustainability Scanner"
    ])
    
    with scanner_tabs[0]:
        st.markdown("### Code Scanner")
        st.write("Scan source code repositories for security vulnerabilities and PII")
        
        scan_type = st.radio("Repository Type", ["GitHub", "Azure DevOps", "Local Upload"])
        
        if scan_type == "GitHub":
            repo_url = st.text_input("GitHub Repository URL")
            if st.button("Scan GitHub Repository"):
                if repo_url:
                    run_code_scan(repo_url, "github")
                else:
                    st.error("Please enter a repository URL")
        
        elif scan_type == "Azure DevOps":
            org_name = st.text_input("Organization Name")
            project_name = st.text_input("Project Name")
            repo_name = st.text_input("Repository Name")
            if st.button("Scan Azure Repository"):
                if org_name and project_name and repo_name:
                    run_code_scan(f"{org_name}/{project_name}/{repo_name}", "azure")
                else:
                    st.error("Please fill all fields")
        
        else:  # Local Upload
            uploaded_files = st.file_uploader("Upload code files", accept_multiple_files=True, 
                                            type=["py", "js", "java", "cpp", "c", "cs", "php", "rb", "go"])
            if uploaded_files and st.button("Scan Uploaded Files"):
                run_local_code_scan(uploaded_files)
    
    with scanner_tabs[1]:
        st.markdown("### Document Scanner")
        st.write("Analyze documents (PDF, DOCX, TXT) for PII detection")
        
        uploaded_docs = st.file_uploader("Upload documents", accept_multiple_files=True,
                                       type=["pdf", "docx", "txt", "doc"])
        if uploaded_docs and st.button("Scan Documents"):
            run_document_scan(uploaded_docs)
    
    with scanner_tabs[2]:
        st.markdown("### Image Scanner")
        st.write("OCR-based PII detection in images")
        
        uploaded_images = st.file_uploader("Upload images", accept_multiple_files=True,
                                         type=["png", "jpg", "jpeg", "gif", "bmp"])
        if uploaded_images and st.button("Scan Images"):
            run_image_scan(uploaded_images)
    
    with scanner_tabs[3]:
        st.markdown("### Website Scanner")
        st.write("Web scraping and analysis for privacy compliance")
        
        website_url = st.text_input("Website URL")
        scan_depth = st.slider("Scan Depth", 1, 5, 2)
        if st.button("Scan Website"):
            if website_url:
                run_website_scan(website_url, scan_depth)
            else:
                st.error("Please enter a website URL")
    
    with scanner_tabs[4]:
        st.markdown("### Database Scanner")
        st.write("Direct database scanning for PII across multiple DB types")
        
        db_type = st.selectbox("Database Type", ["PostgreSQL", "MySQL", "MongoDB", "SQL Server"])
        connection_string = st.text_input("Connection String", type="password")
        if st.button("Scan Database"):
            if connection_string:
                run_database_scan(db_type, connection_string)
            else:
                st.error("Please enter a connection string")
    
    with scanner_tabs[5]:
        st.markdown("### AI Model Scanner")
        st.write("AI/ML model privacy compliance analysis")
        
        model_type = st.selectbox("Model Type", ["TensorFlow", "PyTorch", "Scikit-learn", "Hugging Face"])
        model_path = st.text_input("Model Path or URL")
        if st.button("Scan AI Model"):
            if model_path:
                run_ai_model_scan(model_type, model_path)
            else:
                st.error("Please enter a model path")
    
    with scanner_tabs[6]:
        st.markdown("### SOC2 Scanner")
        st.write("SOC2 compliance validation")
        
        soc2_type = st.radio("Scan Type", ["GitHub Repository", "Azure Repository"])
        
        if soc2_type == "GitHub Repository":
            github_url = st.text_input("GitHub Repository URL")
            if st.button("Scan for SOC2 Compliance"):
                if github_url:
                    run_soc2_scan(github_url, "github")
                else:
                    st.error("Please enter a repository URL")
        else:
            azure_org = st.text_input("Azure Organization")
            azure_project = st.text_input("Azure Project")
            azure_repo = st.text_input("Azure Repository")
            if st.button("Scan Azure for SOC2"):
                if azure_org and azure_project and azure_repo:
                    run_soc2_scan(f"{azure_org}/{azure_project}/{azure_repo}", "azure")
                else:
                    st.error("Please fill all fields")
    
    with scanner_tabs[7]:
        st.markdown("### Sustainability Scanner")
        st.write("Environmental impact analysis")
        
        sustainability_type = st.selectbox("Analysis Type", ["Carbon Footprint", "Energy Efficiency", "Resource Usage"])
        target_system = st.text_input("Target System/Application")
        if st.button("Run Sustainability Analysis"):
            if target_system:
                run_sustainability_scan(sustainability_type, target_system)
            else:
                st.error("Please specify a target system")

def show_simple_dpia():
    """Show Simple DPIA interface"""
    try:
        from simple_dpia import run_simple_dpia
        run_simple_dpia()
    except ImportError as e:
        st.error(f"DPIA module not available: {str(e)}")

def show_dashboard():
    """Show dashboard"""
    st.markdown("## Dashboard")
    st.info("Dashboard functionality")

def show_history():
    """Show scan history"""
    st.markdown("## Scan History")
    st.info("Scan history will be displayed here")

def show_results():
    """Show scan results"""
    st.markdown("## Scan Results")
    st.info("Scan results will be displayed here")

def show_reports():
    """Show reports"""
    st.markdown("## Reports")
    st.info("Report generation interface will be displayed here")

def show_admin():
    """Show admin interface"""
    st.markdown("## Administration")
    st.info("Admin functionality will be displayed here")

# Scanner implementation functions
def run_code_scan(repo_info, repo_type):
    """Run code scanner"""
    with st.spinner("Scanning code repository..."):
        try:
            scanner = CodeScanner()
            results = scanner.scan_repository(repo_info, repo_type)
            st.success("Code scan completed!")
            st.json(results)
        except Exception as e:
            st.error(f"Code scan failed: {str(e)}")

def run_local_code_scan(uploaded_files):
    """Run local code scan"""
    with st.spinner("Scanning uploaded files..."):
        try:
            scanner = CodeScanner()
            results = scanner.scan_uploaded_files(uploaded_files)
            st.success("Local code scan completed!")
            st.json(results)
        except Exception as e:
            st.error(f"Local code scan failed: {str(e)}")

def run_document_scan(uploaded_docs):
    """Run document scanner"""
    with st.spinner("Scanning documents..."):
        try:
            scanner = BlobScanner()
            results = scanner.scan_documents(uploaded_docs)
            st.success("Document scan completed!")
            st.json(results)
        except Exception as e:
            st.error(f"Document scan failed: {str(e)}")

def run_image_scan(uploaded_images):
    """Run image scanner"""
    with st.spinner("Scanning images..."):
        try:
            from services.image_scanner import ImageScanner
            scanner = ImageScanner()
            results = scanner.scan_images(uploaded_images)
            st.success("Image scan completed!")
            st.json(results)
        except Exception as e:
            st.error(f"Image scan failed: {str(e)}")

def run_website_scan(url, depth):
    """Run website scanner"""
    with st.spinner("Scanning website..."):
        try:
            scanner = WebsiteScanner()
            results = scanner.scan_website(url, depth)
            st.success("Website scan completed!")
            st.json(results)
        except Exception as e:
            st.error(f"Website scan failed: {str(e)}")

def run_database_scan(db_type, connection_string):
    """Run database scanner"""
    with st.spinner("Scanning database..."):
        try:
            from services.db_scanner import DatabaseScanner
            scanner = DatabaseScanner()
            results = scanner.scan_database(db_type, connection_string)
            st.success("Database scan completed!")
            st.json(results)
        except Exception as e:
            st.error(f"Database scan failed: {str(e)}")

def run_ai_model_scan(model_type, model_path):
    """Run AI model scanner"""
    with st.spinner("Scanning AI model..."):
        try:
            scanner = AIModelScanner()
            results = scanner.scan_model(model_type, model_path)
            st.success("AI model scan completed!")
            st.json(results)
        except Exception as e:
            st.error(f"AI model scan failed: {str(e)}")

def run_soc2_scan(repo_info, repo_type):
    """Run SOC2 scanner"""
    with st.spinner("Running SOC2 compliance scan..."):
        try:
            if repo_type == "github":
                results = scan_github_repo_for_soc2(repo_info)
            else:
                results = scan_azure_repo_for_soc2(repo_info)
            st.success("SOC2 scan completed!")
            display_soc2_scan_results(results)
        except Exception as e:
            st.error(f"SOC2 scan failed: {str(e)}")

def run_sustainability_scan(scan_type, target_system):
    """Run sustainability scanner"""
    with st.spinner("Running sustainability analysis..."):
        try:
            from utils.scanners.sustainability_scanner import SustainabilityScanner
            scanner = SustainabilityScanner()
            results = scanner.analyze_sustainability(scan_type, target_system)
            st.success("Sustainability analysis completed!")
            st.json(results)
        except Exception as e:
            st.error(f"Sustainability scan failed: {str(e)}")

if __name__ == "__main__":
    main()