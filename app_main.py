"""
DataGuardian Pro - Main Application (Refactored)

Simplified main application with proper variable scoping,
session management, and modular architecture.
"""

import streamlit as st
import os
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import modular components
from app_auth import handle_authentication, show_logout_option
from utils.session_manager import session_middleware, SessionManager, get_safe_session_value, fix_variable_scoping
from utils.i18n import initialize, get_text, set_language, LANGUAGES
from services.results_aggregator import ResultsAggregator

# Translation function
def _(key, default=None):
    return get_text(key, default)

def initialize_language_system():
    """Initialize language system with proper variable scoping"""
    # Run session middleware first
    if not session_middleware():
        return False
    
    # Fix variable scoping issues
    current_language = fix_variable_scoping()
    
    # Initialize translations
    initialize()
    
    # Set page config
    st.set_page_config(
        page_title="DataGuardian Pro",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    return current_language

def show_language_selector():
    """Show language selector with proper variable handling"""
    current_language = get_safe_session_value('language', 'en')
    
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

def show_header():
    """Show application header"""
    title = get_safe_session_value('app_title', _("app.title", "DataGuardian Pro"))
    subtitle = get_safe_session_value('app_subtitle', _("app.subtitle", "Enterprise Privacy Compliance Platform"))
    
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #4a90e2; margin-bottom: 0.5rem;">{title}</h1>
        <p style="color: #666; font-size: 1.2rem; margin: 0;">{subtitle}</p>
        <p style="color: #888; margin-top: 0.5rem;">{_("app.tagline", "Detect, Manage, and Report Privacy Compliance with AI-powered Precision")}</p>
    </div>
    """, unsafe_allow_html=True)

def create_navigation():
    """Create navigation with proper variable initialization"""
    # Get navigation titles with safe defaults
    scan_title = _("scan.title", "Scan")
    simple_dpia_title = "Simple DPIA"
    dashboard_title = _("dashboard.welcome", "Dashboard")
    history_title = _("history.title", "History")
    results_title = _("results.title", "Results")
    report_title = _("report.generate", "Report")
    
    # Base navigation options
    nav_options = [scan_title, simple_dpia_title, dashboard_title, history_title, results_title, report_title]
    
    # Add admin if user has permissions
    if get_safe_session_value('user_role', 'user') == 'admin':
        admin_title = _("admin.title", "Admin")
        nav_options.append(admin_title)
    
    # Icon mapping
    icon_map = {
        scan_title: "🔍",
        simple_dpia_title: "📝",
        dashboard_title: "📊",
        history_title: "📜",
        results_title: "📋",
        report_title: "📑",
        _("admin.title", "Admin"): "⚙️"
    }
    
    # Navigation header
    st.sidebar.markdown("### Navigation")
    
    # Get current selection
    selected_nav = get_safe_session_value('selected_nav', dashboard_title)
    
    # Create navigation buttons
    for nav_option in nav_options:
        if not nav_option:
            continue
            
        icon = icon_map.get(nav_option, "🔗")
        
        if st.sidebar.button(f"{icon} {nav_option}", key=f"nav_{nav_option.replace(' ', '_')}", use_container_width=True):
            st.session_state.selected_nav = nav_option
            st.rerun()
    
    return selected_nav

def show_membership_status():
    """Show membership status in sidebar"""
    st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    st.sidebar.markdown("### Membership")
    
    premium_member = get_safe_session_value('premium_member', False)
    
    if premium_member:
        membership_details = get_safe_session_value('membership_details', {})
        plan_name = membership_details.get("plan", "Premium")
        
        st.sidebar.success(f"✅ {plan_name} Member")
        
        # Show expiry if available
        if "expires_at" in membership_details:
            try:
                expiry_date = datetime.fromisoformat(membership_details["expires_at"].replace('Z', '+00:00'))
                days_remaining = (expiry_date - datetime.now()).days
                
                if days_remaining > 30:
                    st.sidebar.info(f"Valid for {days_remaining} days")
                elif days_remaining > 0:
                    st.sidebar.warning(f"Expires in {days_remaining} days")
                else:
                    st.sidebar.error("Membership expired")
            except Exception:
                st.sidebar.info("Active membership")
    else:
        st.sidebar.info("🆓 Free Member")
        free_trial_days_left = get_safe_session_value('free_trial_days_left', 7)
        if free_trial_days_left > 0:
            st.sidebar.info(f"Trial: {free_trial_days_left} days left")

def show_dashboard():
    """Show dashboard content"""
    st.markdown("## Welcome to DataGuardian Pro")
    
    current_user = get_safe_session_value('username', 'Guest')
    user_role = get_safe_session_value('user_role', 'user')
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("User", current_user)
    
    with col2:
        st.metric("Role", user_role.replace('_', ' ').title())
    
    with col3:
        membership_status = "Premium" if get_safe_session_value('premium_member', False) else "Free"
        st.metric("Plan", membership_status)
    
    st.markdown("### Quick Actions")
    
    action_col1, action_col2 = st.columns(2)
    
    with action_col1:
        if st.button("🔍 Start New Scan", use_container_width=True):
            st.session_state.selected_nav = _("scan.title", "Scan")
            st.rerun()
    
    with action_col2:
        if st.button("📝 Simple DPIA Assessment", use_container_width=True):
            st.session_state.selected_nav = "Simple DPIA"
            st.rerun()

def show_scan_interface():
    """Show scanning interface"""
    st.markdown("## Privacy Compliance Scanning")
    
    scan_types = [
        (_("scan.code", "Code"), "🔍"),
        (_("scan.blob", "Document"), "📄"), 
        (_("scan.dpia", "Data Protection Impact Assessment"), "📝"),
        (_("scan.image", "Image"), "🖼️"),
        (_("scan.website", "Website"), "🌐"),
        (_("scan.database", "Database"), "🗄️")
    ]
    
    st.markdown("### Select Scan Type")
    
    selected_scan = st.selectbox(
        "Choose the type of scan you want to perform:",
        options=[scan_type[0] for scan_type in scan_types],
        format_func=lambda x: f"{next(icon for name, icon in scan_types if name == x)} {x}"
    )
    
    if selected_scan == _("scan.dpia", "Data Protection Impact Assessment"):
        try:
            from simple_dpia import run_simple_dpia
            run_simple_dpia()
        except ImportError as e:
            st.error(f"DPIA module not available: {str(e)}")
    else:
        st.info(f"Selected: {selected_scan}")
        st.markdown("Configure your scan settings here...")

def show_history():
    """Show scan history"""
    st.markdown("## Scan History")
    
    try:
        results_aggregator = ResultsAggregator()
        # Implementation would show historical scans
        st.info("Scan history functionality will be displayed here")
    except Exception as e:
        st.error(f"Error loading history: {str(e)}")

def show_results():
    """Show scan results"""
    st.markdown("## Scan Results")
    st.info("Scan results will be displayed here")

def show_reports():
    """Show reports interface"""
    st.markdown("## Reports")
    st.info("Report generation interface will be displayed here")

def show_admin():
    """Show admin interface"""
    if get_safe_session_value('user_role', 'user') != 'admin':
        st.error("Access denied: Admin privileges required")
        return
    
    st.markdown("## Administration")
    st.info("Admin functionality will be displayed here")

def main():
    """Main application function"""
    try:
        # Initialize language and session management
        current_language = initialize_language_system()
        if current_language is False:
            return  # Session expired
        
        # Handle authentication
        if not handle_authentication():
            return  # Not authenticated
        
        # Show header
        show_header()
        
        # Show language selector
        show_language_selector()
        
        # Show logout option
        show_logout_option()
        
        # Create navigation
        selected_nav = create_navigation()
        
        # Show membership status
        show_membership_status()
        
        # Route to appropriate page based on navigation
        if selected_nav == _("scan.title", "Scan"):
            show_scan_interface()
        elif selected_nav == "Simple DPIA":
            show_scan_interface()  # Will show DPIA interface
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
        else:
            show_dashboard()  # Default fallback
    
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error("An unexpected error occurred. Please refresh the page.")
        
        # Show session debug info for admins
        if get_safe_session_value('user_role', 'user') == 'admin':
            with st.expander("Debug Information"):
                session_info = SessionManager.get_session_info()
                st.json(session_info)

if __name__ == "__main__":
    main()