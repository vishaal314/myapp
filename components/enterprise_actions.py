"""
Enterprise Actions Component

Provides contextual enterprise actions for scan results and compliance findings.
Integrates with the enterprise event system to trigger workflows.
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

# Enterprise integration - non-breaking import
try:
    from utils.event_bus import EventType, publish_event
    ENTERPRISE_EVENTS_AVAILABLE = True
except ImportError:
    ENTERPRISE_EVENTS_AVAILABLE = False

def show_enterprise_actions(scan_result: Dict[str, Any], scan_type: str = "code", 
                          username: str = "unknown"):
    """
    Display contextual enterprise actions based on scan results.
    
    Args:
        scan_result: The scan result data
        scan_type: Type of scan performed
        username: Current user
    """
    if not ENTERPRISE_EVENTS_AVAILABLE:
        return  # Silently skip if enterprise features not available
    
    # Get user context
    session_id = st.session_state.get('session_id', 'unknown')
    user_id = st.session_state.get('user_id', username)
    
    # Get findings for analysis
    findings = scan_result.get('findings', [])
    high_risk_findings = [f for f in findings if f.get('risk_level') == 'Critical' or f.get('severity') == 'Critical']
    pii_findings = [f for f in findings if 'pii' in str(f).lower() or 'personal' in str(f).lower()]
    
    # Create enterprise actions section
    with st.expander("🔧 Enterprise Actions", expanded=False):
        st.markdown("**Compliance & Risk Management Actions**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # DSAR action for PII findings
            if pii_findings:
                if st.button("📝 Create DSAR", help="Create Data Subject Access Request for PII findings", 
                           key=f"dsar_action_{scan_result.get('scan_id', 'unknown')}"):
                    _handle_dsar_action(scan_result, pii_findings, user_id, session_id, username)
            
            # Evidence export action
            if st.button("📊 Export Evidence", help="Export compliance evidence for audit purposes",
                        key=f"evidence_action_{scan_result.get('scan_id', 'unknown')}"):
                _handle_evidence_export(scan_result, scan_type, user_id, session_id, username)
        
        with col2:
            # Ticket creation for high-risk findings
            if high_risk_findings:
                if st.button("🎫 Create Ticket", help="Create ticket for high-risk findings",
                           key=f"ticket_action_{scan_result.get('scan_id', 'unknown')}"):
                    _handle_ticket_creation(scan_result, high_risk_findings, user_id, session_id, username)
            
            # Vendor risk assessment
            if scan_type in ['website', 'api'] and findings:
                if st.button("⚠️ Assess Vendor", help="Create vendor risk assessment",
                           key=f"vendor_action_{scan_result.get('scan_id', 'unknown')}"):
                    _handle_vendor_assessment(scan_result, findings, user_id, session_id, username)
        
        with col3:
            # Compliance report generation
            if st.button("📋 Generate Report", help="Generate compliance report",
                        key=f"report_action_{scan_result.get('scan_id', 'unknown')}"):
                _handle_compliance_report(scan_result, scan_type, user_id, session_id, username)
            
            # Consent tracking for privacy findings
            privacy_findings = [f for f in findings if any(keyword in str(f).lower() 
                               for keyword in ['consent', 'cookie', 'tracking', 'privacy'])]
            if privacy_findings:
                if st.button("🔐 Track Consent", help="Update consent tracking records",
                           key=f"consent_action_{scan_result.get('scan_id', 'unknown')}"):
                    _handle_consent_tracking(scan_result, privacy_findings, user_id, session_id, username)

def _handle_dsar_action(scan_result: Dict[str, Any], pii_findings: List[Dict], 
                       user_id: str, session_id: str, username: str):
    """Handle DSAR creation action"""
    try:
        # Prepare DSAR event data
        event_data = {
            'source_scan_id': scan_result.get('scan_id'),
            'scan_type': scan_result.get('scan_type', 'unknown'),
            'pii_findings_count': len(pii_findings),
            'pii_types': [finding.get('pii_type', 'unknown') for finding in pii_findings],
            'risk_level': 'high' if any(f.get('risk_level') == 'Critical' for f in pii_findings) else 'medium',
            'timestamp': datetime.now().isoformat(),
            'requester_context': 'compliance_scan',
            'auto_generated': True
        }
        
        # Publish DSAR submission event
        publish_event(
            event_type=EventType.DSAR_REQUEST_SUBMITTED,
            source="enterprise_actions",
            user_id=user_id,
            session_id=session_id,
            data=event_data
        )
        
        st.success(f"✅ DSAR request initiated for {len(pii_findings)} PII findings")
        st.info("📧 Enterprise listeners will process this request and create appropriate records")
        
    except Exception as e:
        st.error(f"Failed to create DSAR: {str(e)}")

def _handle_evidence_export(scan_result: Dict[str, Any], scan_type: str, 
                           user_id: str, session_id: str, username: str):
    """Handle evidence export action"""
    try:
        # Prepare evidence event data
        event_data = {
            'source_scan_id': scan_result.get('scan_id'),
            'scan_type': scan_type,
            'evidence_type': 'scan_result',
            'total_findings': scan_result.get('total_pii_found', 0),
            'high_risk_count': scan_result.get('high_risk_count', 0),
            'compliance_framework': 'GDPR',
            'region': scan_result.get('region', 'EU'),
            'timestamp': datetime.now().isoformat(),
            'retention_period_months': 84,  # 7 years
            'classification': 'internal'
        }
        
        # Publish evidence added event
        publish_event(
            event_type=EventType.COMPLIANCE_EVIDENCE_ADDED,
            source="enterprise_actions",
            user_id=user_id,
            session_id=session_id,
            data=event_data
        )
        
        st.success("✅ Evidence export initiated")
        st.info("📁 Evidence will be stored in the enterprise audit repository")
        
    except Exception as e:
        st.error(f"Failed to export evidence: {str(e)}")

def _handle_ticket_creation(scan_result: Dict[str, Any], high_risk_findings: List[Dict],
                           user_id: str, session_id: str, username: str):
    """Handle ticket creation action"""
    try:
        # Prepare ticket event data
        event_data = {
            'title': f"High-Risk Findings - {scan_result.get('scan_type', 'Scan').title()}",
            'description': f"Automated ticket for {len(high_risk_findings)} high-risk findings",
            'ticket_type': 'compliance_issue',
            'priority': 'high' if len(high_risk_findings) > 5 else 'medium',
            'source_scan_id': scan_result.get('scan_id'),
            'findings_count': len(high_risk_findings),
            'finding_types': [f.get('type', 'unknown') for f in high_risk_findings],
            'risk_level': 'high',
            'compliance_framework': 'GDPR',
            'region': scan_result.get('region', 'EU'),
            'created_by_automation': True,
            'timestamp': datetime.now().isoformat()
        }
        
        # Publish ticket creation event
        publish_event(
            event_type=EventType.TICKET_CREATED,
            source="enterprise_actions",
            user_id=user_id,
            session_id=session_id,
            data=event_data
        )
        
        st.success(f"✅ Ticket created for {len(high_risk_findings)} high-risk findings")
        st.info("🎫 Enterprise ticketing system will process this automatically")
        
    except Exception as e:
        st.error(f"Failed to create ticket: {str(e)}")

def _handle_vendor_assessment(scan_result: Dict[str, Any], findings: List[Dict],
                             user_id: str, session_id: str, username: str):
    """Handle vendor risk assessment action"""
    try:
        # Extract vendor information from scan results
        vendor_info = _extract_vendor_info(scan_result, findings)
        
        event_data = {
            'vendor_name': vendor_info.get('name', 'Unknown Vendor'),
            'vendor_url': vendor_info.get('url', ''),
            'risk_level': 'high' if any(f.get('severity') == 'Critical' for f in findings) else 'medium',
            'source_scan_id': scan_result.get('scan_id'),
            'findings_count': len(findings),
            'assessment_trigger': 'compliance_scan',
            'data_processing': True,  # Assume true if findings detected
            'region': scan_result.get('region', 'EU'),
            'timestamp': datetime.now().isoformat(),
            'auto_generated': True
        }
        
        # Publish vendor risk alert
        publish_event(
            event_type=EventType.VENDOR_RISK_ALERT,
            source="enterprise_actions",
            user_id=user_id,
            session_id=session_id,
            data=event_data
        )
        
        st.success("✅ Vendor risk assessment initiated")
        st.info("⚠️ Vendor risk management system will evaluate this vendor")
        
    except Exception as e:
        st.error(f"Failed to create vendor assessment: {str(e)}")

def _handle_compliance_report(scan_result: Dict[str, Any], scan_type: str,
                             user_id: str, session_id: str, username: str):
    """Handle compliance report generation"""
    try:
        # This could trigger a comprehensive compliance report
        event_data = {
            'report_type': 'compliance_summary',
            'source_scan_id': scan_result.get('scan_id'),
            'scan_type': scan_type,
            'compliance_framework': 'GDPR',
            'region': scan_result.get('region', 'EU'),
            'timestamp': datetime.now().isoformat(),
            'requested_by': username,
            'auto_generated': False
        }
        
        # Use compliance evidence event as trigger
        publish_event(
            event_type=EventType.COMPLIANCE_EVIDENCE_ADDED,
            source="enterprise_actions",
            user_id=user_id,
            session_id=session_id,
            data=event_data
        )
        
        st.success("✅ Compliance report generation started")
        st.info("📋 Report will be available in the compliance dashboard")
        
    except Exception as e:
        st.error(f"Failed to generate report: {str(e)}")

def _handle_consent_tracking(scan_result: Dict[str, Any], privacy_findings: List[Dict],
                            user_id: str, session_id: str, username: str):
    """Handle consent tracking update"""
    try:
        event_data = {
            'consent_type': 'tracking',
            'source_scan_id': scan_result.get('scan_id'),
            'privacy_findings_count': len(privacy_findings),
            'findings_types': [f.get('type', 'unknown') for f in privacy_findings],
            'compliance_update': True,
            'region': scan_result.get('region', 'EU'),
            'timestamp': datetime.now().isoformat(),
            'trigger': 'compliance_scan'
        }
        
        # Publish consent update event
        publish_event(
            event_type=EventType.CONSENT_UPDATED,
            source="enterprise_actions",
            user_id=user_id,
            session_id=session_id,
            data=event_data
        )
        
        st.success("✅ Consent tracking updated")
        st.info("🔐 Consent management system will process these updates")
        
    except Exception as e:
        st.error(f"Failed to update consent tracking: {str(e)}")

def _extract_vendor_info(scan_result: Dict[str, Any], findings: List[Dict]) -> Dict[str, Any]:
    """Extract vendor information from scan results"""
    vendor_info = {}
    
    # Try to extract vendor name and URL from scan results
    if scan_result.get('scan_type') == 'website':
        vendor_info['url'] = scan_result.get('url', '')
        # Extract domain as vendor name
        if vendor_info['url']:
            try:
                from urllib.parse import urlparse
                parsed = urlparse(vendor_info['url'])
                vendor_info['name'] = parsed.netloc.replace('www.', '')
            except Exception:
                vendor_info['name'] = 'Website Vendor'
    else:
        vendor_info['name'] = f"{scan_result.get('scan_type', 'Unknown').title()} Service"
    
    return vendor_info

def show_quick_enterprise_sidebar():
    """Show quick enterprise actions in sidebar"""
    if not ENTERPRISE_EVENTS_AVAILABLE:
        return
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("**🏢 Enterprise Quick Actions**")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 New DSAR", key="quick_dsar", help="Create new DSAR request"):
                _show_quick_dsar_form()
        
        with col2:
            if st.button("🎫 New Ticket", key="quick_ticket", help="Create new ticket"):
                _show_quick_ticket_form()

def _show_quick_dsar_form():
    """Show quick DSAR creation form"""
    with st.form("quick_dsar_form"):
        st.markdown("**Quick DSAR Request**")
        email = st.text_input("Requester Email")
        request_type = st.selectbox("Request Type", 
                                   ["access", "rectification", "erasure", "portability"])
        details = st.text_area("Request Details")
        
        if st.form_submit_button("Submit DSAR"):
            if email and details:
                # Publish DSAR event
                event_data = {
                    'requester_email': email,
                    'request_type': request_type,
                    'request_details': details,
                    'source': 'manual_entry',
                    'timestamp': datetime.now().isoformat()
                }
                
                publish_event(
                    event_type=EventType.DSAR_REQUEST_SUBMITTED,
                    source="quick_actions",
                    user_id=st.session_state.get('user_id', 'unknown'),
                    session_id=st.session_state.get('session_id', 'unknown'),
                    data=event_data
                )
                
                st.success("DSAR request submitted successfully!")
            else:
                st.error("Please fill in all required fields")

def _show_quick_ticket_form():
    """Show quick ticket creation form"""
    with st.form("quick_ticket_form"):
        st.markdown("**Quick Ticket Creation**")
        title = st.text_input("Ticket Title")
        ticket_type = st.selectbox("Type", 
                                  ["compliance_issue", "security_finding", "privacy_violation"])
        priority = st.selectbox("Priority", ["low", "medium", "high", "critical"])
        description = st.text_area("Description")
        
        if st.form_submit_button("Create Ticket"):
            if title and description:
                event_data = {
                    'title': title,
                    'description': description,
                    'ticket_type': ticket_type,
                    'priority': priority,
                    'source': 'manual_entry',
                    'timestamp': datetime.now().isoformat()
                }
                
                publish_event(
                    event_type=EventType.TICKET_CREATED,
                    source="quick_actions",
                    user_id=st.session_state.get('user_id', 'unknown'),
                    session_id=st.session_state.get('session_id', 'unknown'),
                    data=event_data
                )
                
                st.success("Ticket created successfully!")
            else:
                st.error("Please fill in all required fields")