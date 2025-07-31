"""
License Integration with DataGuardian Pro
Seamless integration of licensing controls with the main application
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import logging
from services.license_manager import (
    LicenseManager, LicenseType, UsageLimitType, 
    check_license, check_feature, check_scanner, check_region, 
    check_usage, increment_usage, get_license_info, track_user_session
)
from services.usage_analytics import (
    UsageAnalytics, UsageEventType, track_usage_event, 
    get_usage_stats, get_compliance_report
)
from utils.activity_tracker import ScannerType

logger = logging.getLogger(__name__)

class LicenseIntegration:
    """Integration layer for license management in DataGuardian Pro"""
    
    def __init__(self):
        self.license_manager = LicenseManager()
        self.usage_analytics = UsageAnalytics()
    
    def initialize_license_check(self) -> bool:
        """Initialize license check for the application"""
        try:
            is_valid, message = check_license()
            
            if not is_valid:
                st.error(f"License Error: {message}")
                self.show_license_upgrade_prompt()
                return False
            
            # Track application start
            if 'user_id' in st.session_state:
                track_usage_event(
                    event_type=UsageEventType.USER_LOGIN,
                    user_id=st.session_state['user_id'],
                    session_id=st.session_state.get('session_id', 'unknown'),
                    feature='application_start'
                )
            
            return True
            
        except Exception as e:
            logger.error(f"License initialization failed: {e}")
            st.error("License system error. Please contact support.")
            return False
    
    def check_scanner_permission(self, scanner_type: str, region: str) -> Tuple[bool, str]:
        """Check if user can access a scanner type in a region"""
        
        # Check license validity
        is_valid, message = check_license()
        if not is_valid:
            return False, f"License invalid: {message}"
        
        # Check scanner access
        if not check_scanner(scanner_type):
            return False, f"Scanner '{scanner_type}' not available in your license"
        
        # Check region access
        if not check_region(region):
            return False, f"Region '{region}' not available in your license"
        
        # Check usage limits
        allowed, current, limit = check_usage(UsageLimitType.SCANS_PER_MONTH)
        if not allowed:
            return False, f"Monthly scan limit reached ({current}/{limit})"
        
        # Check concurrent users
        if 'user_id' in st.session_state:
            if not track_user_session(st.session_state['user_id']):
                return False, "Maximum concurrent users reached"
        
        return True, "Access granted"
    
    def track_scan_usage(self, scanner_type: str, region: str, success: bool = True, 
                        duration_ms: Optional[int] = None, error_message: Optional[str] = None):
        """Track scanner usage for licensing and analytics"""
        
        if 'user_id' not in st.session_state:
            return
        
        user_id = st.session_state['user_id']
        session_id = st.session_state.get('session_id', 'unknown')
        
        # Increment usage counters
        if success:
            increment_usage(UsageLimitType.SCANS_PER_MONTH, 1)
            increment_usage(UsageLimitType.SCANS_PER_DAY, 1)
        
        # Track in analytics
        event_type = UsageEventType.SCAN_COMPLETED if success else UsageEventType.SCAN_FAILED
        track_usage_event(
            event_type=event_type,
            user_id=user_id,
            session_id=session_id,
            scanner_type=scanner_type,
            region=region,
            duration_ms=duration_ms,
            success=success,
            error_message=error_message
        )
    
    def check_report_generation(self) -> Tuple[bool, str]:
        """Check if user can generate reports"""
        
        # Check license validity
        is_valid, message = check_license()
        if not is_valid:
            return False, f"License invalid: {message}"
        
        # Check reporting feature
        if not check_feature("reporting"):
            return False, "Report generation not available in your license"
        
        # Check export limits
        allowed, current, limit = check_usage(UsageLimitType.EXPORT_REPORTS)
        if not allowed:
            return False, f"Report export limit reached ({current}/{limit})"
        
        return True, "Report generation allowed"
    
    def track_report_generation(self, report_type: str, success: bool = True):
        """Track report generation for licensing"""
        
        if 'user_id' not in st.session_state:
            return
        
        user_id = st.session_state['user_id']
        session_id = st.session_state.get('session_id', 'unknown')
        
        # Increment usage if successful
        if success:
            increment_usage(UsageLimitType.EXPORT_REPORTS, 1)
        
        # Track in analytics
        track_usage_event(
            event_type=UsageEventType.REPORT_GENERATED,
            user_id=user_id,
            session_id=session_id,
            feature=f"report_{report_type}",
            success=success
        )
    
    def track_report_download(self, report_type: str):
        """Track report download"""
        
        if 'user_id' not in st.session_state:
            return
        
        user_id = st.session_state['user_id']
        session_id = st.session_state.get('session_id', 'unknown')
        
        track_usage_event(
            event_type=UsageEventType.REPORT_DOWNLOADED,
            user_id=user_id,
            session_id=session_id,
            feature=f"download_{report_type}"
        )
    
    def check_api_access(self) -> Tuple[bool, str]:
        """Check API access permissions"""
        
        # Check license validity
        is_valid, message = check_license()
        if not is_valid:
            return False, f"License invalid: {message}"
        
        # Check API feature
        if not check_feature("api_access"):
            return False, "API access not available in your license"
        
        # Check API call limits
        allowed, current, limit = check_usage(UsageLimitType.API_CALLS)
        if not allowed:
            return False, f"API call limit reached ({current}/{limit})"
        
        return True, "API access granted"
    
    def show_license_status(self):
        """Show license status in sidebar"""
        
        license_info = get_license_info()
        
        if license_info.get("status") == "Valid":
            st.sidebar.success("✅ License Valid")
            
            # Show license details
            with st.sidebar.expander("License Details"):
                st.write(f"**Type:** {license_info['license_type'].title()}")
                st.write(f"**Company:** {license_info['company_name']}")
                st.write(f"**Expires:** {license_info['expiry_date'][:10]}")
                st.write(f"**Days remaining:** {license_info['days_remaining']}")
                
                # Show usage
                st.write("**Usage:**")
                for limit_type, usage_data in license_info.get("usage", {}).items():
                    percentage = usage_data["percentage"]
                    current = usage_data["current"]
                    limit = usage_data["limit"]
                    
                    if percentage > 90:
                        color = "red"
                    elif percentage > 75:
                        color = "orange"
                    else:
                        color = "green"
                    
                    st.write(f"- {limit_type.replace('_', ' ').title()}: {current}/{limit} ({percentage:.1f}%)")
                    st.progress(percentage / 100)
        else:
            st.sidebar.error("❌ License Invalid")
            st.sidebar.write(license_info.get("message", "Unknown error"))
            
            if st.sidebar.button("Upgrade License"):
                self.show_license_upgrade_prompt()
    
    def show_license_upgrade_prompt(self):
        """Show license upgrade options"""
        
        st.error("🔐 License Upgrade Required")
        
        st.markdown("""
        Your current license has limitations. Upgrade to unlock full features:
        """)
        
        # License comparison table
        license_options = {
            "Trial": {
                "price": "Free",
                "scans": "50/month",
                "users": "2",
                "features": "Basic scanners",
                "regions": "Netherlands"
            },
            "Basic": {
                "price": "€49.99/month",
                "scans": "500/month",
                "users": "5",
                "features": "All scanners",
                "regions": "Netherlands, Germany"
            },
            "Professional": {
                "price": "€149.99/month",
                "scans": "2,000/month",
                "users": "15",
                "features": "All scanners + API",
                "regions": "All EU regions"
            },
            "Enterprise": {
                "price": "€399.99/month",
                "scans": "10,000/month",
                "users": "50",
                "features": "All features + White-label",
                "regions": "Global"
            }
        }
        
        cols = st.columns(len(license_options))
        for i, (name, details) in enumerate(license_options.items()):
            with cols[i]:
                st.markdown(f"### {name}")
                st.write(f"**Price:** {details['price']}")
                st.write(f"**Scans:** {details['scans']}")
                st.write(f"**Users:** {details['users']}")
                st.write(f"**Features:** {details['features']}")
                st.write(f"**Regions:** {details['regions']}")
                
                if st.button(f"Select {name}", key=f"select_{name}"):
                    st.info(f"Redirecting to upgrade to {name} plan...")
                    # Here you would redirect to payment or contact form
    
    def show_usage_dashboard(self):
        """Show usage analytics dashboard"""
        
        if not check_feature("compliance_dashboard"):
            st.error("Usage dashboard not available in your license")
            return
        
        st.header("📊 Usage Analytics Dashboard")
        
        # Get usage statistics
        stats = get_usage_stats()
        license_info = get_license_info()
        
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Scans", stats.total_scans)
        with col2:
            st.metric("Success Rate", f"{100 - stats.error_rate:.1f}%")
        with col3:
            st.metric("Avg Duration", f"{stats.average_duration_ms/1000:.1f}s")
        with col4:
            st.metric("Peak Users", stats.peak_concurrent_users)
        
        # License compliance
        st.subheader("License Compliance")
        compliance = get_compliance_report(license_info)
        
        if compliance.get("warnings"):
            st.warning("⚠️ License Usage Warnings:")
            for warning in compliance["warnings"]:
                st.write(f"- {warning}")
        else:
            st.success("✅ All usage within license limits")
        
        # Usage charts
        st.subheader("Usage Trends")
        
        # Usage by day
        if stats.usage_by_day:
            st.line_chart(stats.usage_by_day)
        
        # Scanner usage
        st.subheader("Scanner Usage")
        scanner_usage = {scanner: stats.scanners_used.count(scanner) for scanner in set(stats.scanners_used)}
        if scanner_usage:
            st.bar_chart(scanner_usage)
        
        # Recent activity
        st.subheader("Recent Activity")
        if 'user_id' in st.session_state:
            recent_activity = self.usage_analytics.get_user_activity(st.session_state['user_id'], 10)
            
            for activity in recent_activity:
                icon = "✅" if activity.success else "❌"
                event_type_str = getattr(getattr(activity, 'event_type', None), 'value', 'unknown')
                timestamp_str = activity.timestamp.strftime('%Y-%m-%d %H:%M:%S') if getattr(activity, 'timestamp', None) else "unknown"
                st.write(f"{icon} {event_type_str} - {timestamp_str}")
    
    def create_license_decorator(self):
        """Create decorator for license-protected functions"""
        
        def license_required(scanner_type: str = None, feature: str = None, region: str = None):
            def decorator(func):
                def wrapper(*args, **kwargs):
                    # Check license
                    is_valid, message = check_license()
                    if not is_valid:
                        st.error(f"License Error: {message}")
                        return None
                    
                    # Check specific permissions
                    if scanner_type and not check_scanner(scanner_type):
                        st.error(f"Scanner '{scanner_type}' not available in your license")
                        return None
                    
                    if feature and not check_feature(feature):
                        st.error(f"Feature '{feature}' not available in your license")
                        return None
                    
                    if region and not check_region(region):
                        st.error(f"Region '{region}' not available in your license")
                        return None
                    
                    # Check usage limits
                    if scanner_type:
                        allowed, current, limit = check_usage(UsageLimitType.SCANS_PER_MONTH)
                        if not allowed:
                            st.error(f"Monthly scan limit reached ({current}/{limit})")
                            return None
                    
                    # Execute function
                    return func(*args, **kwargs)
                
                return wrapper
            return decorator
        
        return license_required

# Global license integration instance
license_integration = LicenseIntegration()

# Convenience functions
def require_license_check() -> bool:
    """Check if license is valid for application use"""
    return license_integration.initialize_license_check()

def require_scanner_access(scanner_type: str, region: str) -> bool:
    """Check scanner access permissions"""
    allowed, message = license_integration.check_scanner_permission(scanner_type, region)
    if not allowed:
        st.error(f"Access denied: {message}")
        return False
    return True

def track_scanner_usage(scanner_type: str, region: str, success: bool = True, 
                       duration_ms: Optional[int] = None, error_message: Optional[str] = None):
    """Track scanner usage"""
    license_integration.track_scan_usage(scanner_type, region, success, duration_ms, error_message)

def require_report_access() -> bool:
    """Check report generation permissions"""
    allowed, message = license_integration.check_report_generation()
    if not allowed:
        st.error(f"Report access denied: {message}")
        return False
    return True

def track_report_usage(report_type: str, success: bool = True):
    """Track report generation"""
    license_integration.track_report_generation(report_type, success)

def track_download_usage(report_type: str):
    """Track report download"""
    license_integration.track_report_download(report_type)

def show_license_sidebar():
    """Show license information in sidebar"""
    license_integration.show_license_status()

def show_usage_dashboard():
    """Show usage analytics dashboard"""
    license_integration.show_usage_dashboard()

# Create license decorator
license_required = license_integration.create_license_decorator()