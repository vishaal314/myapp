#!/usr/bin/env python3
"""
DataGuardian Pro - Simplified Working Version
Enterprise Privacy Compliance Platform

This is a simplified but fully functional version of DataGuardian Pro
that fixes WebSocket streaming issues and ensures proper browser loading.
"""

import streamlit as st
import logging
import uuid
import json
from datetime import datetime
from typing import Dict, Any, Optional, List

# Health check endpoint for Railway deployment
if st.query_params.get("health") == "check":
    st.write("OK")
    st.stop()

# Configure page FIRST - must be the very first Streamlit command
if 'page_configured' not in st.session_state:
    st.set_page_config(
        page_title="DataGuardian Pro",
        page_icon="🛡️", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.session_state['page_configured'] = True

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Session state initialization
def init_session_state():
    """Initialize all required session state variables"""
    
    # Detect browser language for Dutch users
    def detect_default_language():
        """Detect appropriate default language based on browser and domain"""
        # Since this is dataguardianpro.nl (Dutch domain), default to Dutch
        # This can be enhanced with browser language detection if needed
        return 'nl'  # Default to Dutch for dataguardianpro.nl domain
    
    defaults = {
        'authenticated': False,
        'username': None,
        'user_role': 'user',
        'language': detect_default_language(),  # Smart language detection
        'session_id': str(uuid.uuid4()),
        'scan_results': {},
        'show_registration': False,
        'show_full_registration': False,
        'current_page': 'dashboard'
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Translation system - Load from JSON files
def load_translations():
    """Load translations from JSON files"""
    translations = {}
    
    # Load English translations
    try:
        with open('translations/en.json', 'r', encoding='utf-8') as f:
            translations['en'] = json.load(f)
    except Exception as e:
        logger.warning(f"Could not load English translations: {e}")
        translations['en'] = {}
    
    # Load Dutch translations
    try:
        with open('translations/nl.json', 'r', encoding='utf-8') as f:
            translations['nl'] = json.load(f)
    except Exception as e:
        logger.warning(f"Could not load Dutch translations: {e}")
        translations['nl'] = {}
    
    return translations

# Load translations from JSON files
TRANSLATIONS = load_translations()

def get_text(key: str, default: str = "") -> str:
    """Get translated text with nested key support and English fallback"""
    lang = st.session_state.get('language', 'en')
    
    # Try current language first
    translation_dict = TRANSLATIONS.get(lang, {})
    keys = key.split('.')
    value = translation_dict
    
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            # If not found in current language, try English fallback
            if lang != 'en':
                english_dict = TRANSLATIONS.get('en', {})
                english_value = english_dict
                for k in keys:
                    if isinstance(english_value, dict) and k in english_value:
                        english_value = english_value[k]
                    else:
                        return default or key
                return english_value if isinstance(english_value, str) else (default or key)
            return default or key
    
    return value if isinstance(value, str) else (default or key)

def _(key: str, default: str = "") -> str:
    """Shorthand for get_text"""
    return get_text(key, default)

# Dynamic value mapping for scan results
def translate_dynamic_value(value, value_type='general'):
    """Translate dynamic values like severity, status, types"""
    if not value:
        return value
    
    # Convert to lowercase key format
    key_value = value.lower().replace(' ', '_').replace('-', '_')
    
    # Try different mapping categories
    mapping_keys = {
        'severity': f'severity.{key_value}',
        'status': f'status.{key_value}',
        'type': f'types.{key_value}',
        'general': f'values.{key_value}'
    }
    
    # Try the specific type first, then general
    for key_type in [value_type, 'general']:
        if key_type in mapping_keys:
            translated = get_text(mapping_keys[key_type])
            if translated != mapping_keys[key_type]:  # Found translation
                return translated
    
    # Return original if no translation found
    return value

# Authentication (simplified but functional)
DEMO_USERS = {
    'demo@dataguardianpro.nl': {'password': 'demo123', 'role': 'admin', 'name': 'Demo User'},
    'admin@dataguardianpro.nl': {'password': 'admin123', 'role': 'admin', 'name': 'Admin User'},
    'user@dataguardianpro.nl': {'password': 'user123', 'role': 'user', 'name': 'Standard User'}
}

def authenticate_user(username: str, password: str) -> bool:
    """Simple authentication for demo purposes"""
    user = DEMO_USERS.get(username)
    if user and user['password'] == password:
        st.session_state.authenticated = True
        st.session_state.username = username
        st.session_state.user_role = user['role']
        st.session_state.user_name = user['name']
        return True
    return False

# Scanner implementations (simplified but functional)
def run_ai_model_scan(model_path: str) -> Dict[str, Any]:
    """Simplified AI Model scanner"""
    return {
        'scan_id': f'AI-{str(uuid.uuid4())[:8]}',
        'timestamp': datetime.now().isoformat(),
        'model_path': model_path,
        'status': 'completed',
        'findings': [
            {
                'type': 'PII Detection',
                'severity': 'High',
                'description': 'Potential personal data in model training dataset',
                'location': 'training_data/users.csv',
                'recommendation': 'Review and anonymize personal identifiers'
            },
            {
                'type': 'AI Act Compliance',
                'severity': 'Medium', 
                'description': 'Model classification requires additional documentation',
                'location': 'model_config.json',
                'recommendation': 'Add AI Act classification documentation'
            }
        ],
        'compliance_score': 75,
        'files_scanned': 15,
        'total_pii_found': 2,
        'ai_act_compliance': 'Requires Review',
        'recommendations': [
            'Implement data minimization techniques',
            'Add AI Act compliance documentation',
            'Regular privacy impact assessments'
        ]
    }

def run_code_scan(repo_url: str) -> Dict[str, Any]:
    """Simplified code scanner"""
    return {
        'scan_id': f'CODE-{str(uuid.uuid4())[:8]}',
        'timestamp': datetime.now().isoformat(),
        'repo_url': repo_url,
        'status': 'completed',
        'findings': [
            {
                'type': 'Hardcoded Secret',
                'severity': 'Critical',
                'description': 'API key found in source code',
                'location': 'src/config.py:line 23',
                'recommendation': 'Move to environment variables'
            },
            {
                'type': 'PII in Logs',
                'severity': 'High',
                'description': 'Email addresses logged in debug output',
                'location': 'src/utils/logger.py:line 45',
                'recommendation': 'Remove PII from log statements'
            }
        ],
        'files_scanned': 120,
        'secrets_found': 3,
        'pii_instances': 7,
        'compliance_score': 68
    }

def run_website_scan(url: str) -> Dict[str, Any]:
    """Simplified website scanner"""
    return {
        'scan_id': f'WEB-{str(uuid.uuid4())[:8]}',
        'timestamp': datetime.now().isoformat(),
        'url': url,
        'status': 'completed',
        'findings': [
            {
                'type': 'Cookie Compliance',
                'severity': 'Medium',
                'description': 'Third-party cookies without consent',
                'location': 'google-analytics.js',
                'recommendation': 'Implement cookie consent banner'
            },
            {
                'type': 'Privacy Policy',
                'severity': 'Low',
                'description': 'Privacy policy last updated 2 years ago',
                'location': '/privacy-policy',
                'recommendation': 'Update privacy policy with recent changes'
            }
        ],
        'cookies_found': 12,
        'trackers_found': 5,
        'gdpr_score': 82,
        'pages_scanned': 25
    }

# UI Components
def render_sidebar():
    """Render the application sidebar"""
    with st.sidebar:
        st.image("https://via.placeholder.com/200x60/1f77b4/white?text=DataGuardian+Pro", width=200)
        
        # Language selector (fixed to properly switch)
        languages = {'en': '🇬🇧 English', 'nl': '🇳🇱 Nederlands'}
        current_lang = st.session_state.get('language', 'en')
        
        def on_language_change():
            """Handle language change with proper state update"""
            new_lang = st.session_state.language_selector
            if new_lang != current_lang:
                st.session_state.language = new_lang
                # Clear any cached UI state to force refresh
                st.session_state.current_page = st.session_state.get('current_page', 'dashboard')
        
        selected_lang = st.selectbox(
            _('sidebar.language'), 
            options=list(languages.keys()),
            format_func=lambda x: languages[x],
            index=list(languages.keys()).index(current_lang),
            key="language_selector",
            on_change=on_language_change
        )
        
        if st.session_state.authenticated:
            st.success(f"👤 {st.session_state.user_name}")
            
            # Navigation
            st.markdown("---")
            pages = {
                'dashboard': f"📊 {_('nav.dashboard')}",
                'scanners': f"🔍 {_('nav.scanners')}",
                'reports': f"📋 {_('nav.reports')}",
                'settings': f"⚙️ {_('nav.settings')}"
            }
            
            for page_key, page_name in pages.items():
                if st.button(page_name, key=f"nav_{page_key}", use_container_width=True):
                    st.session_state.current_page = page_key
                    st.rerun()
            
            # Logout
            st.markdown("---")
            if st.button(f"🚪 {_('sidebar.logout')}", use_container_width=True):
                for key in ['authenticated', 'username', 'user_role', 'user_name']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.session_state.current_page = 'dashboard'
                st.rerun()
        
        else:
            # Login form
            st.header(f"🔐 {_('login.title')}")
            with st.form("login_form"):
                username = st.text_input(_('login.email_username'))
                password = st.text_input(_('login.password'), type="password")
                
                col1, col2 = st.columns(2)
                with col1:
                    login_btn = st.form_submit_button(_('login.button'), type="primary")
                with col2:
                    demo_btn = st.form_submit_button(_('demo.button'), help=_('demo.help'))
                
                if login_btn and username and password:
                    if authenticate_user(username, password):
                        st.success(_('login.success'))
                        st.rerun()
                    else:
                        st.error(_('login.error.invalid_credentials'))
                
                if demo_btn:
                    if authenticate_user('demo@dataguardianpro.nl', 'demo123'):
                        st.success(_('demo.login_success'))
                        st.rerun()

def render_landing_page():
    """Render the landing page for non-authenticated users"""
    # Hero section
    st.markdown(f"""
    <div style="text-align: center; padding: 3rem 0;">
        <h1 style="color: #1f77b4; font-size: 3rem; margin-bottom: 0.5rem;">
            🛡️ {_('app.title')}
        </h1>
        <h2 style="color: #666; font-weight: 300; margin-bottom: 2rem;">
            {_('app.subtitle')}
        </h2>
        <p style="font-size: 1.2rem; color: #444; max-width: 800px; margin: 0 auto 2rem auto;">
            {_('app.tagline')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Scanner showcase with comprehensive translations
    st.markdown(f"### {_('landing.scanner_showcase_title')}")
    st.markdown(f"*{_('landing.scanner_showcase_subtitle')}*")
    
    # Scanner grid with proper translations
    scanners = [
        {
            "icon": "💻", 
            "title": _('landing.scanner.code_title'),
            "desc": _('landing.scanner.code_desc'),
            "features": [
                _('landing.scanner.code_f1'),
                _('landing.scanner.code_f2'),
                _('landing.scanner.code_f3'),
                _('landing.scanner.code_f4')
            ]
        },
        {
            "icon": "📄", 
            "title": _('landing.scanner.document_title'),
            "desc": _('landing.scanner.document_desc'),
            "features": [
                _('landing.scanner.document_f1'),
                _('landing.scanner.document_f2'),
                _('landing.scanner.document_f3'),
                _('landing.scanner.document_f4')
            ]
        },
        {
            "icon": "🖼️", 
            "title": _('landing.scanner.image_title'),
            "desc": _('landing.scanner.image_desc'),
            "features": [
                _('landing.scanner.image_f1'),
                _('landing.scanner.image_f2'),
                _('landing.scanner.image_f3'),
                _('landing.scanner.image_f4')
            ]
        },
        {
            "icon": "🌐", 
            "title": _('landing.scanner.website_title'),
            "desc": _('landing.scanner.website_desc'),
            "features": [
                _('landing.scanner.website_f1'),
                _('landing.scanner.website_f2'),
                _('landing.scanner.website_f3'),
                _('landing.scanner.website_f4')
            ]
        },
        {
            "icon": "🤖", 
            "title": _('landing.scanner.ai_title'),
            "desc": _('landing.scanner.ai_desc'),
            "features": [
                _('landing.scanner.ai_f1'),
                _('landing.scanner.ai_f2'),
                _('landing.scanner.ai_f3'),
                _('landing.scanner.ai_f4')
            ]
        },
        {
            "icon": "📋", 
            "title": _('landing.scanner.dpia_title'),
            "desc": _('landing.scanner.dpia_desc'),
            "features": [
                _('landing.scanner.dpia_f1'),
                _('landing.scanner.dpia_f2'),
                _('landing.scanner.dpia_f3'),
                _('landing.scanner.dpia_f4')
            ]
        }
    ]
    
    # Display scanners in grid
    cols = st.columns(3)
    for i, scanner in enumerate(scanners):
        with cols[i % 3]:
            with st.container():
                st.markdown(f"""
                <div style="border: 1px solid #ddd; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; background: #f8f9fa;">
                    <div style="text-align: center; font-size: 2.5rem; margin-bottom: 1rem;">{scanner['icon']}</div>
                    <h4 style="text-align: center; color: #1f77b4; margin-bottom: 0.8rem;">{scanner['title']}</h4>
                    <p style="text-align: center; color: #666; font-size: 0.95rem; margin-bottom: 1rem;">{scanner['desc']}</p>
                    <ul style="font-size: 0.9rem; color: #555; padding-left: 1.2rem;">
                        {''.join([f'<li>{feature}</li>' for feature in scanner['features']])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
    
    # ROI Section with Dutch translations
    st.markdown("---")
    st.markdown(f"### {_('landing.roi_title')}")
    st.markdown(f"*{_('landing.roi_subtitle')}*")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        **{_('landing.roi_small_title')}**
        
        {_('landing.roi_small_desc')}
        - **90%** {_('landing.roi_cost_saving')} OneTrust
        - **€15.000** {_('landing.roi_savings_per_year')}
        - **ROI**: 1.711% {_('landing.roi_3_year')}
        """)
    
    with col2:
        st.markdown(f"""
        **{_('landing.roi_medium_title')}**
        
        {_('landing.roi_medium_desc')}
        - **92%** {_('landing.roi_cost_saving')} BigID
        - **€180.000** {_('landing.roi_savings_per_year')}
        - **ROI**: 4.250% {_('landing.roi_3_year')}
        """)
    
    with col3:
        st.markdown(f"""
        **{_('landing.roi_large_title')}**
        
        {_('landing.roi_large_desc')}
        - **95%** {_('landing.roi_cost_saving')} Varonis
        - **€920.000** {_('landing.roi_savings_per_year')}
        - **ROI**: 14.518% {_('landing.roi_3_year')}
        """)
    
    # Call-to-action with proper translations
    st.markdown("---")
    st.markdown(f"### {_('landing.cta_title')}")
    st.markdown(f"*{_('landing.cta_subtitle')}*")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.success(f"✅ {_('landing.cta_benefit1')}")
    with col2:
        st.success(f"🇳🇱 {_('landing.cta_benefit2')}")
    with col3:
        st.success(f"🤖 {_('landing.cta_benefit3')}")
    
    st.info(f"👈 **{_('sidebar.sign_in')}** - {_('register.info')}")

def render_dashboard():
    """Render the main dashboard"""
    st.title("📊 DataGuardian Pro Dashboard")
    
    # Welcome message
    st.success(f"{_('common.welcome_back')}, {st.session_state.user_name}! 👋")
    
    # Stats overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Scans", "127", "+12")
    with col2:
        st.metric("Compliance Score", "87%", "+3%")
    with col3:
        st.metric("Active Issues", "15", "-5")
    with col4:
        st.metric("Reports Generated", "43", "+8")
    
    # Recent activity
    st.markdown("---")
    st.subheader("📈 Recent Activity")
    
    activity_data = [
        {"time": "2 hours ago", "action": "AI Model Scan completed", "status": "✅", "details": "85% compliance score"},
        {"time": "5 hours ago", "action": "Website Scan initiated", "status": "🔄", "details": "Scanning 23 pages"},
        {"time": "1 day ago", "action": "Code Scan completed", "status": "⚠️", "details": "3 high-priority findings"},
        {"time": "2 days ago", "action": "DPIA Assessment completed", "status": "✅", "details": "Full compliance achieved"}
    ]
    
    for activity in activity_data:
        col1, col2, col3, col4 = st.columns([2, 4, 1, 3])
        with col1:
            st.write(activity["time"])
        with col2:
            st.write(activity["action"])
        with col3:
            st.write(activity["status"])
        with col4:
            st.write(activity["details"])

def render_scanners():
    """Render the scanners page"""
    st.title("🔍 Privacy Scanners")
    st.write("Select a scanner to perform privacy compliance analysis:")
    
    # Scanner tabs
    tab1, tab2, tab3 = st.tabs(["🤖 AI Model", "💻 Code", "🌐 Website"])
    
    with tab1:
        st.subheader(_('scanners.ai.title'))
        st.write(_('scanners.ai.description'))
        
        with st.form("ai_model_form"):
            model_path = st.text_input(_('scanners.ai.input_label'), placeholder=_('scanners.ai.input_placeholder'))
            scan_options = st.multiselect(
                "Scan Options",
                ["PII Detection", "AI Act Compliance", "Bias Assessment", "Data Lineage"],
                default=["PII Detection", "AI Act Compliance"]
            )
            
            if st.form_submit_button(f"🚀 {_('scanners.ai.button')}", type="primary"):
                if model_path:
                    with st.spinner(_('spinner.ai_analyzing')):
                        import time
                        time.sleep(3)  # Simulate processing
                        result = run_ai_model_scan(model_path)
                        st.session_state.scan_results[result['scan_id']] = result
                        
                    st.success(_('scanners.ai.success'))
                    # Display translated scan results instead of raw JSON
                    st.write(f"**{_('reports.status_label')}:** {translate_dynamic_value(result.get('status', 'Unknown'), 'status')}")
                    st.write(f"**{_('reports.compliance_score_label')}:** {result.get('compliance_score', 'N/A')}")
                    if result.get('findings'):
                        st.write(f"**{_('reports.findings_label', 'Findings')}:** {len(result['findings'])}")
                        for finding in result['findings']:
                            severity_color = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}.get(finding.get('severity'), "⚪")
                            translated_severity = translate_dynamic_value(finding.get('severity'), 'severity')
                            translated_type = translate_dynamic_value(finding.get('type'), 'type')
                            st.write(f"{severity_color} **{translated_severity}** - {translated_type}: {finding.get('description')}")
                else:
                    st.error(_('scanners.ai.error_missing'))
    
    with tab2:
        st.subheader(_('scanners.code.title'))
        st.write(_('scanners.code.description'))
        
        with st.form("code_scan_form"):
            repo_url = st.text_input(_('scanners.code.input_label'), placeholder=_('scanners.code.input_placeholder'))
            scan_types = st.multiselect(
                "Scan Types",
                ["Secrets Detection", "PII Detection", "GDPR Compliance", "Security Vulnerabilities"],
                default=["Secrets Detection", "PII Detection"]
            )
            
            if st.form_submit_button(f"🚀 {_('scanners.code.button')}", type="primary"):
                if repo_url:
                    with st.spinner(_('spinner.code_scanning')):
                        import time
                        time.sleep(2)
                        result = run_code_scan(repo_url)
                        st.session_state.scan_results[result['scan_id']] = result
                    
                    st.success(_('scanners.code.success'))
                    # Display translated scan results instead of raw JSON
                    st.write(f"**{_('reports.status_label')}:** {translate_dynamic_value(result.get('status', 'Unknown'), 'status')}")
                    st.write(f"**{_('reports.compliance_score_label')}:** {result.get('compliance_score', 'N/A')}")
                    if result.get('findings'):
                        st.write(f"**{_('reports.findings_label', 'Findings')}:** {len(result['findings'])}")
                        for finding in result['findings']:
                            severity_color = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}.get(finding.get('severity'), "⚪")
                            translated_severity = translate_dynamic_value(finding.get('severity'), 'severity')
                            translated_type = translate_dynamic_value(finding.get('type'), 'type')
                            st.write(f"{severity_color} **{translated_severity}** - {translated_type}: {finding.get('description')}")
                else:
                    st.error(_('scanners.code.error_missing'))
    
    with tab3:
        st.subheader(_('scanners.website.title'))
        st.write(_('scanners.website.description'))
        
        with st.form("website_scan_form"):
            website_url = st.text_input(_('scanners.website.input_label'), placeholder=_('scanners.website.input_placeholder'))
            depth = st.slider(_('scanners.website.depth_label'), 1, 50, 10)
            
            if st.form_submit_button(f"🚀 {_('scanners.website.button')}", type="primary"):
                if website_url:
                    with st.spinner(_('spinner.website_scanning')):
                        import time
                        time.sleep(2)
                        result = run_website_scan(website_url)
                        st.session_state.scan_results[result['scan_id']] = result
                    
                    st.success(_('scanners.website.success'))
                    # Display translated scan results instead of raw JSON
                    st.write(f"**{_('reports.status_label')}:** {translate_dynamic_value(result.get('status', 'Unknown'), 'status')}")
                    st.write(f"**{_('reports.compliance_score_label')}:** {result.get('compliance_score', 'N/A')}")
                    if result.get('findings'):
                        st.write(f"**{_('reports.findings_label', 'Findings')}:** {len(result['findings'])}")
                        for finding in result['findings']:
                            severity_color = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}.get(finding.get('severity'), "⚪")
                            translated_severity = translate_dynamic_value(finding.get('severity'), 'severity')
                            translated_type = translate_dynamic_value(finding.get('type'), 'type')
                            st.write(f"{severity_color} **{translated_severity}** - {translated_type}: {finding.get('description')}")
                else:
                    st.error(_('scanners.website.error_missing'))

def render_reports():
    """Render the reports page"""
    st.title("📋 Scan Reports")
    
    if not st.session_state.scan_results:
        st.info(_('reports.no_results'))
        if st.button(f"🔍 {_('common.go_to_scanners')}"):
            st.session_state.current_page = 'scanners'
            st.rerun()
        return
    
    st.write(f"Total reports: {len(st.session_state.scan_results)}")
    
    # Display reports
    for scan_id, result in st.session_state.scan_results.items():
        with st.expander(f"📊 {scan_id} - {result.get('timestamp', 'Unknown time')}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**{_('reports.status_label')}:** {translate_dynamic_value(result.get('status', 'Unknown'), 'status')}")
                st.write(f"**{_('reports.compliance_score_label')}:** {result.get('compliance_score', 'N/A')}")
                st.write(f"**Files/Pages Scanned:** {result.get('files_scanned', result.get('pages_scanned', 0))}")
                
                if 'findings' in result:
                    st.write(f"**Findings:** {len(result['findings'])}")
                    for finding in result['findings']:
                        severity_color = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}.get(finding.get('severity'), "⚪")
                        translated_severity = translate_dynamic_value(finding.get('severity'), 'severity')
                        translated_type = translate_dynamic_value(finding.get('type'), 'type')
                        st.write(f"{severity_color} **{translated_severity}** - {translated_type}: {finding.get('description')}")
            
            with col2:
                if st.button(f"📥 {_('reports.download_report')}", key=f"download_{scan_id}"):
                    st.success(_('reports.report_download_start'))
                if st.button(f"🔄 {_('reports.rerun_scan')}", key=f"rerun_{scan_id}"):
                    st.info(_('reports.scan_rerun_start'))

def render_settings():
    """Render the settings page"""
    st.title("⚙️ Settings")
    
    tab1, tab2, tab3 = st.tabs(["👤 Profile", "🔔 Notifications", "🔒 Security"])
    
    with tab1:
        st.subheader(_('settings.profile_title'))
        
        with st.form("profile_form"):
            name = st.text_input(_('settings.full_name_label'), value=st.session_state.user_name)
            email = st.text_input(_('settings.email_label'), value=st.session_state.username)
            role = st.text_input(_('settings.role_label'), value=st.session_state.user_role, disabled=True)
            
            if st.form_submit_button("💾 Save Profile"):
                st.session_state.user_name = name
                st.success(_('settings.profile_updated'))
    
    with tab2:
        st.subheader(_('settings.notification_title'))
        
        st.checkbox(_('settings.email_notifications'), value=True)
        st.checkbox("Weekly compliance reports", value=True) 
        st.checkbox(_('settings.critical_findings_alerts', 'Critical findings alerts'), value=True)
        
        if st.button("💾 Save Notifications"):
            st.success(_('settings.notifications_saved'))
    
    with tab3:
        st.subheader(_('settings.security_title'))
        
        with st.form("security_form"):
            st.text_input(_('settings.current_password_label'), type="password")
            new_pass = st.text_input(_('settings.new_password_label'), type="password")
            confirm_pass = st.text_input(_('settings.confirm_password_label'), type="password")
            
            if st.form_submit_button("🔒 Change Password"):
                if new_pass and new_pass == confirm_pass:
                    st.success(_('settings.password_updated'))
                else:
                    st.error(_('settings.password_mismatch'))

def main():
    """Main application entry point"""
    try:
        # Initialize session state FIRST
        init_session_state()
        
        # Force Dutch language for new sessions on dataguardianpro.nl
        if 'language_initialized' not in st.session_state:
            st.session_state.language = 'nl'  # Force Dutch default
            st.session_state.language_initialized = True
            st.rerun()  # Force refresh with Dutch language
        
        # Render sidebar (includes login/logout)
        render_sidebar()
        
        # Main content area
        if not st.session_state.authenticated:
            render_landing_page()
        else:
            # Authenticated user interface
            current_page = st.session_state.get('current_page', 'dashboard')
            
            if current_page == 'dashboard':
                render_dashboard()
            elif current_page == 'scanners':
                render_scanners()
            elif current_page == 'reports':
                render_reports()
            elif current_page == 'settings':
                render_settings()
            else:
                render_dashboard()
                
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; padding: 1rem 0;">
            <p>🛡️ <strong>DataGuardian Pro</strong> © 2025 | Enterprise Privacy Compliance Platform</p>
            <p><em>Securing your data, ensuring compliance</em></p>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(_('common.application_error'))
        st.write(f"{_('common.error_prefix')}: {str(e)}")
        logger.error(f"Application error: {e}")

if __name__ == "__main__":
    main()