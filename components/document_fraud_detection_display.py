"""
Document Fraud Detection Display Component

Displays AI fraud detection analysis for scanned documents with visual indicators,
confidence scores, AI model detection, and remediation recommendations.
"""

import streamlit as st
from typing import Dict, Any, List, Optional


def render_document_fraud_analysis(doc_results: Dict[str, Any], index: int = 0):
    """
    Render fraud analysis for a single document.
    
    Args:
        doc_results: Document scan results with fraud_analysis field
        index: Document index for unique key generation
    """
    fraud_analysis = doc_results.get('fraud_analysis')
    
    if not fraud_analysis:
        return
    
    file_name = doc_results.get('file_name', f'Document {index + 1}')
    
    # Risk level colors
    risk_colors = {
        'Critical': '#F44336',    # Red
        'High': '#FF6F00',        # Deep Orange
        'Medium': '#FF9800',      # Orange
        'Low': '#4CAF50'          # Green
    }
    
    risk_level = fraud_analysis.get('risk_level', 'Low')
    risk_color = risk_colors.get(risk_level, '#9E9E9E')
    ai_generated_risk = fraud_analysis.get('ai_generated_risk', 0)
    confidence = fraud_analysis.get('confidence', 0)
    ai_model = fraud_analysis.get('ai_model', 'Unknown')
    
    # Main fraud analysis card
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {risk_color}15 0%, {risk_color}05 100%);
                border-left: 4px solid {risk_color};
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 16px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.08);">
        
        <div style="display: flex; justify-content: space-between; align-items: start;">
            
            <div style="flex: 1;">
                <div style="display: flex; align-items: center; margin-bottom: 12px;">
                    <span style="font-size: 20px; margin-right: 8px;">🔍</span>
                    <h4 style="margin: 0; color: {risk_color}; font-weight: 700;">
                        AI Fraud Detection: {file_name}
                    </h4>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-bottom: 16px;">
                    <div style="background: white; padding: 12px; border-radius: 6px;">
                        <div style="font-size: 12px; color: #999; font-weight: 500;">Risk Level</div>
                        <div style="font-size: 20px; font-weight: 700; color: {risk_color};">
                            {risk_level}
                        </div>
                    </div>
                    
                    <div style="background: white; padding: 12px; border-radius: 6px;">
                        <div style="font-size: 12px; color: #999; font-weight: 500;">AI Risk Score</div>
                        <div style="font-size: 20px; font-weight: 700; color: {risk_color};">
                            {ai_generated_risk:.0%}
                        </div>
                    </div>
                    
                    <div style="background: white; padding: 12px; border-radius: 6px;">
                        <div style="font-size: 12px; color: #999; font-weight: 500;">Confidence</div>
                        <div style="font-size: 20px; font-weight: 700; color: #2196F3;">
                            {confidence:.1f}%
                        </div>
                    </div>
                </div>
                
                <div style="background: white; padding: 12px; border-radius: 6px; margin-bottom: 12px;">
                    <div style="font-size: 12px; color: #999; font-weight: 500; margin-bottom: 4px;">
                        Suspected AI Model
                    </div>
                    <div style="font-size: 14px; font-weight: 600; color: #333;">
                        🤖 {ai_model}
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Fraud indicators breakdown
    fraud_indicators = fraud_analysis.get('fraud_indicators', [])
    if fraud_indicators:
        st.markdown(f"""
        <div style="background: white; border-radius: 8px; padding: 16px; 
                    margin-bottom: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.05);">
            <h5 style="margin-top: 0; color: #333; font-weight: 600;">
                📊 Fraud Indicators Detected
            </h5>
        </div>
        """, unsafe_allow_html=True)
        
        for indicator in fraud_indicators:
            indicator_type = indicator.get('type', 'Unknown')
            indicator_score = indicator.get('score', 0)
            indicator_details = indicator.get('details', 'No details')
            
            # Color based on score
            if indicator_score >= 0.7:
                ind_color = '#F44336'  # Red
                ind_emoji = '🔴'
            elif indicator_score >= 0.5:
                ind_color = '#FF6F00'  # Orange
                ind_emoji = '🟠'
            else:
                ind_color = '#FFC107'  # Yellow
                ind_emoji = '🟡'
            
            # Format indicator type for display
            type_display = indicator_type.replace('_', ' ').title()
            
            st.markdown(f"""
            <div style="background: {ind_color}08; border-left: 3px solid {ind_color};
                        border-radius: 6px; padding: 12px; margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 13px; color: #333; font-weight: 600;">
                            {ind_emoji} {type_display}
                        </div>
                        <div style="font-size: 12px; color: #666; margin-top: 4px;">
                            {indicator_details}
                        </div>
                    </div>
                    <div style="background: white; padding: 6px 12px; border-radius: 4px; 
                                text-align: center; white-space: nowrap;">
                        <div style="font-size: 11px; color: #999;">Score</div>
                        <div style="font-size: 16px; font-weight: 700; color: {ind_color};">
                            {indicator_score:.0%}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Recommendations
    recommendations = fraud_analysis.get('recommendations', [])
    if recommendations:
        st.markdown(f"""
        <div style="background: white; border-radius: 8px; padding: 16px; 
                    margin-bottom: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.05);">
            <h5 style="margin-top: 0; color: #333; font-weight: 600;">
                💡 Recommended Actions
            </h5>
        </div>
        """, unsafe_allow_html=True)
        
        for i, recommendation in enumerate(recommendations, 1):
            st.markdown(f"""
            <div style="background: #E3F2FD; border-radius: 6px; padding: 12px; 
                        margin-bottom: 8px; border-left: 3px solid #2196F3;">
                <div style="font-size: 13px; color: #1976D2; font-weight: 500;">
                    ✓ {recommendation}
                </div>
            </div>
            """, unsafe_allow_html=True)


def render_fraud_summary_for_batch(scan_results: Dict[str, Any]):
    """
    Render overall fraud detection summary for batch document scan.
    
    Args:
        scan_results: Complete scan results with all documents
    """
    # Collect all documents' fraud analysis
    fraud_docs = []
    high_risk_count = 0
    medium_risk_count = 0
    
    findings = scan_results.get('findings', [])
    for finding in findings:
        fraud_analysis = finding.get('fraud_analysis')
        if fraud_analysis:
            fraud_docs.append((finding.get('file_name', 'Unknown'), fraud_analysis))
            
            risk_level = fraud_analysis.get('risk_level', 'Low')
            if risk_level == 'Critical' or risk_level == 'High':
                high_risk_count += 1
            elif risk_level == 'Medium':
                medium_risk_count += 1
    
    if not fraud_docs:
        return
    
    # Display summary metrics
    st.subheader("🚨 AI Fraud Detection Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Documents Analyzed", len(scan_results.get('findings', [])))
    
    with col2:
        st.metric("Potential AI Fraud", len(fraud_docs), 
                 delta=f"{(len(fraud_docs) / max(len(scan_results.get('findings', [])), 1) * 100):.0f}% flagged",
                 delta_color="inverse")
    
    with col3:
        st.metric("High Risk Documents", high_risk_count,
                 delta=f"{medium_risk_count} medium risk",
                 delta_color="inverse")
    
    # Display each document's fraud analysis
    for i, (file_name, fraud_analysis) in enumerate(fraud_docs):
        with st.expander(f"📄 {file_name} - {fraud_analysis.get('risk_level', 'Low')} Risk", 
                        expanded=(i == 0)):  # First one expanded
            doc_result = {'file_name': file_name, 'fraud_analysis': fraud_analysis}
            render_document_fraud_analysis(doc_result, i)


def render_fraud_warning_banner(scan_results: Dict[str, Any]):
    """
    Render warning banner if high-risk documents detected.
    
    Args:
        scan_results: Complete scan results
    """
    findings = scan_results.get('findings', [])
    
    critical_count = 0
    high_count = 0
    
    for finding in findings:
        fraud_analysis = finding.get('fraud_analysis')
        if fraud_analysis:
            risk_level = fraud_analysis.get('risk_level', 'Low')
            if risk_level == 'Critical':
                critical_count += 1
            elif risk_level == 'High':
                high_count += 1
    
    if critical_count > 0:
        st.error(f"""
        ⚠️ **CRITICAL AI FRAUD DETECTED**
        
        {critical_count} document(s) show critical signs of AI generation or tampering.
        Immediate verification required before processing.
        """)
    
    elif high_count > 0:
        st.warning(f"""
        ⚠️ **HIGH-RISK DOCUMENTS DETECTED**
        
        {high_count} document(s) show significant AI fraud indicators.
        Manual review recommended.
        """)
