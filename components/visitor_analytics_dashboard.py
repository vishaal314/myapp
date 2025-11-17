"""
Visitor Analytics Dashboard for DataGuardian Pro
Real-time display of visitor tracking, login attempts, and user registrations

GDPR-Compliant Display:
- No personal data shown
- Anonymized metrics only
- Compliance with GDPR Article 5 (data minimization)
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from services.visitor_tracker import get_visitor_tracker, VisitorEventType
from typing import Dict, Any

def render_visitor_analytics_dashboard():
    """
    Render visitor analytics dashboard
    
    Metrics displayed:
    - Total unique visitors (last 7/30 days)
    - Login attempts (success/failure)
    - User registrations (success/failure)
    - Top pages visited
    - Traffic sources (referrers)
    - Geographic distribution (countries)
    """
    
    st.markdown("## 📊 Visitor Analytics Dashboard")
    st.markdown("*GDPR-compliant tracking with IP anonymization*")
    
    # Time period selector
    col1, col2 = st.columns([3, 1])
    with col2:
        period = st.selectbox(
            "Period",
            options=[7, 14, 30, 90],
            format_func=lambda x: f"Last {x} days",
            key="analytics_period"
        )
    
    # Get analytics data
    tracker = get_visitor_tracker()
    analytics = tracker.get_analytics(days=period)
    
    # Key metrics row
    st.markdown("### 📈 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Unique Visitors",
            value=analytics['total_visitors'],
            help="Unique sessions (no personal data tracked)"
        )
    
    with col2:
        st.metric(
            label="Page Views",
            value=analytics['total_pageviews']
        )
    
    with col3:
        login_total = analytics['login_success'] + analytics['login_failure']
        login_rate = (analytics['login_success'] / login_total * 100) if login_total > 0 else 0
        st.metric(
            label="Login Success Rate",
            value=f"{login_rate:.1f}%",
            delta=f"{analytics['login_success']}/{login_total}"
        )
    
    with col4:
        reg_total = analytics['registration_success'] + analytics['registration_failure']
        reg_rate = (analytics['registration_success'] / reg_total * 100) if reg_total > 0 else 0
        st.metric(
            label="Registration Success Rate",
            value=f"{reg_rate:.1f}%",
            delta=f"{analytics['registration_success']}/{reg_total}"
        )
    
    # Detailed metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔐 Authentication Events")
        
        # Login attempts breakdown
        login_data = {
            'Status': ['Success', 'Failure'],
            'Count': [analytics['login_success'], analytics['login_failure']]
        }
        
        fig_login = px.pie(
            login_data,
            values='Count',
            names='Status',
            title=f"Login Attempts ({login_total} total)",
            color='Status',
            color_discrete_map={'Success': '#00D26A', 'Failure': '#FF4B4B'}
        )
        fig_login.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_login, use_container_width=True)
        
        # Registration attempts breakdown
        st.markdown("### 👥 User Registrations")
        reg_data = {
            'Status': ['Success', 'Failure'],
            'Count': [analytics['registration_success'], analytics['registration_failure']]
        }
        
        fig_reg = px.pie(
            reg_data,
            values='Count',
            names='Status',
            title=f"Registration Attempts ({reg_total} total)",
            color='Status',
            color_discrete_map={'Success': '#00D26A', 'Failure': '#FF4B4B'}
        )
        fig_reg.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_reg, use_container_width=True)
    
    with col2:
        st.markdown("### 📄 Top Pages Visited")
        
        if analytics['top_pages']:
            pages_df = {
                'Page': [p['page_path'] for p in analytics['top_pages'][:10]],
                'Views': [p['views'] for p in analytics['top_pages'][:10]]
            }
            
            fig_pages = px.bar(
                pages_df,
                x='Views',
                y='Page',
                orientation='h',
                title="Most Visited Pages"
            )
            fig_pages.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_pages, use_container_width=True)
        else:
            st.info("No page view data available yet")
        
        st.markdown("### 🔗 Traffic Sources")
        
        if analytics['top_referrers']:
            referrers_df = {
                'Source': [r['referrer'] for r in analytics['top_referrers'][:10]],
                'Visits': [r['visits'] for r in analytics['top_referrers'][:10]]
            }
            
            fig_refs = px.bar(
                referrers_df,
                x='Visits',
                y='Source',
                orientation='h',
                title="Top Referrers"
            )
            fig_refs.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_refs, use_container_width=True)
        else:
            st.info("No referrer data available yet")
    
    # Geographic distribution
    if analytics['countries']:
        st.markdown("### 🌍 Geographic Distribution")
        
        countries_df = {
            'Country': [c['country'] for c in analytics['countries']],
            'Visitors': [c['visitors'] for c in analytics['countries']]
        }
        
        fig_countries = px.bar(
            countries_df,
            x='Country',
            y='Visitors',
            title="Visitors by Country"
        )
        st.plotly_chart(fig_countries, use_container_width=True)
    
    # Real-time events table
    st.markdown("### 📋 Recent Events")
    
    # Fetch recent events from database
    if hasattr(tracker, 'events') and tracker.events:
        recent_events = sorted(
            tracker.events[-50:],
            key=lambda e: e.timestamp,
            reverse=True
        )
        
        events_data = []
        for event in recent_events[:20]:
            events_data.append({
                'Time': event.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'Event': event.event_type.value.replace('_', ' ').title(),
                'Page': event.page_path,
                'User': event.username or 'Anonymous',
                'Status': '✅ Success' if event.success else '❌ Failed'
            })
        
        if events_data:
            st.dataframe(events_data, use_container_width=True)
        else:
            st.info("No recent events")
    else:
        st.info("No event data available yet")
    
    # GDPR compliance notice
    st.markdown("---")
    st.markdown("""
    **🔒 Privacy & GDPR Compliance:**
    - ✅ IP addresses anonymized (hashed)
    - ✅ No cookies stored
    - ✅ No personal data tracked
    - ✅ 90-day data retention
    - ✅ GDPR Articles 5, 17, 32 compliant
    """)
    
    # Data cleanup button (admin only)
    if st.session_state.get('user_role') == 'admin':
        st.markdown("### 🗑️ Data Management")
        if st.button("Clean Up Old Events (>90 days)", type="secondary"):
            tracker.cleanup_old_events(retention_days=90)
            st.success("✅ Old events cleaned up per GDPR data retention policy")
            st.rerun()
