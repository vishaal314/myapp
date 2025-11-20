"""
Fraud Detection Risk Display Component

Displays AI-generated document and identity fraud detection risk forecasting
on the compliance dashboard with visual indicators and cost analysis.
"""

import streamlit as st
from typing import Dict, Any, Optional
from services.predictive_compliance_engine import PredictiveComplianceEngine, RiskForecast


def render_fraud_detection_risk_card():
    """
    Render fraud detection risk card on the compliance dashboard.
    Displays AI-generated document fraud risk with cost analysis.
    """
    
    # Initialize predictive engine
    engine = PredictiveComplianceEngine(region="Netherlands")
    
    # Sample business context (in real implementation, pulled from database)
    business_context = {
        'document_fraud_exposure': 'high',  # Financial/fintech = higher exposure
        'document_verification_systems': False,  # No verification yet
        'synthetic_media_scanning': False,  # No AI detection yet
        'uses_ai_systems': True,  # Uses AI systems (AI Act 2025)
    }
    
    current_state = {}
    
    # Get fraud risk forecast
    fraud_risk = engine._forecast_fraud_detection_risk(current_state, business_context)
    
    if not fraud_risk:
        return
    
    # Determine color based on risk level
    risk_colors = {
        'Critical': '#F44336',  # Red
        'High': '#FF6F00',      # Deep Orange
        'Medium': '#FF9800',    # Orange
        'Low': '#4CAF50'        # Green
    }
    
    risk_color = risk_colors.get(fraud_risk.risk_level, '#9E9E9E')
    
    # Calculate cost of inaction
    total_cost = sum(fraud_risk.cost_of_inaction.values())
    
    # Display fraud risk card
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {risk_color}20 0%, {risk_color}05 100%); 
                border-left: 4px solid {risk_color}; border-radius: 8px; padding: 20px; 
                margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
        
        <div style="display: flex; justify-content: space-between; align-items: start;">
            
            <div>
                <div style="display: flex; align-items: center; margin-bottom: 12px;">
                    <span style="font-size: 24px; margin-right: 10px;">🚨</span>
                    <h3 style="margin: 0; color: {risk_color}; font-weight: 700;">
                        Fraud Detection Risk Forecast
                    </h3>
                </div>
                
                <div style="margin-bottom: 16px;">
                    <span style="font-size: 14px; color: #666; font-weight: 500;">Risk Level:</span>
                    <span style="font-size: 18px; font-weight: 700; color: {risk_color}; margin-left: 8px;">
                        {fraud_risk.risk_level}
                    </span>
                </div>
                
                <div style="display: flex; gap: 24px; margin-bottom: 12px;">
                    <div>
                        <div style="font-size: 13px; color: #999; font-weight: 500;">Probability</div>
                        <div style="font-size: 22px; font-weight: 700; color: {risk_color};">
                            {fraud_risk.probability:.0%}
                        </div>
                    </div>
                    <div>
                        <div style="font-size: 13px; color: #999; font-weight: 500;">Impact Severity</div>
                        <div style="font-size: 16px; font-weight: 600; color: {risk_color};">
                            {fraud_risk.impact_severity}
                        </div>
                    </div>
                </div>
                
                <div style="padding-top: 12px; border-top: 1px solid rgba(0,0,0,0.1);">
                    <div style="font-size: 13px; color: #666; margin-bottom: 4px;">
                        <strong>Timeline:</strong> {fraud_risk.timeline}
                    </div>
                    <div style="font-size: 13px; color: #666;">
                        <strong>Action Window:</strong> {fraud_risk.mitigation_window}
                    </div>
                </div>
            </div>
            
            <div style="background: white; border-radius: 8px; padding: 16px; 
                        min-width: 220px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <div style="font-size: 12px; color: #999; font-weight: 600; margin-bottom: 8px; 
                            text-transform: uppercase; letter-spacing: 0.5px;">
                    💰 Cost of Inaction
                </div>
                <div style="font-size: 28px; font-weight: 700; color: #F44336; margin-bottom: 16px;">
                    €{total_cost/1_000_000:.1f}M
                </div>
                
                <div style="font-size: 12px; color: #333; line-height: 1.6;">
                    <div style="margin-bottom: 6px;">
                        • Fraud losses: €{fraud_risk.cost_of_inaction.get('fraud_losses_per_incident', 0):,}
                    </div>
                    <div style="margin-bottom: 6px;">
                        • AML fines: €{fraud_risk.cost_of_inaction.get('regulatory_fines_aml', 0):,}
                    </div>
                    <div style="margin-bottom: 6px;">
                        • Operational: €{fraud_risk.cost_of_inaction.get('operational_losses', 0):,}
                    </div>
                    <div style="margin-bottom: 6px;">
                        • Reputation: €{fraud_risk.cost_of_inaction.get('reputation_damage', 0):,}
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_fraud_mitigation_actions():
    """
    Render fraud mitigation action items with priorities.
    """
    
    st.markdown("""
    <div style="background: white; border-radius: 8px; padding: 20px; 
                margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
        <h3 style="margin-top: 0; color: #333; font-weight: 700;">
            🛡️ Recommended Fraud Detection Actions
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Mitigation actions
    actions = [
        {
            'priority': 'CRITICAL',
            'action': 'Implement AI Document Fraud Detection',
            'description': 'Deploy AI-generated document detection (ChatGPT, Stable Diffusion, DALL-E)',
            'timeline': '0-7 days',
            'impact': 'Blocks 80% of AI-generated documents'
        },
        {
            'priority': 'CRITICAL',
            'action': 'Enable Deepfake/Synthetic Media Detection',
            'description': 'Activate synthetic image and video detection for identity verification',
            'timeline': '0-7 days',
            'impact': 'Prevents identity fraud and liveness bypasses'
        },
        {
            'priority': 'HIGH',
            'action': 'Implement Document Metadata Forensics',
            'description': 'Analyze document metadata for editing signatures and anomalies',
            'timeline': '7-14 days',
            'impact': 'Detects 30%+ of edited/forged documents'
        },
        {
            'priority': 'HIGH',
            'action': 'Add Font/Typography Analysis',
            'description': 'Detect font inconsistencies indicating document tampering',
            'timeline': '7-14 days',
            'impact': 'Flags 17.9% of frauds (amount/name changes)'
        },
        {
            'priority': 'MEDIUM',
            'action': 'Enable KvK/BSN Verification',
            'description': 'Cross-reference submitted KvK/BSN numbers with official databases',
            'timeline': '14-30 days',
            'impact': 'Prevents fake business registrations'
        }
    ]
    
    for i, action in enumerate(actions, 1):
        priority_colors = {
            'CRITICAL': '#F44336',
            'HIGH': '#FF6F00',
            'MEDIUM': '#FF9800'
        }
        
        priority_color = priority_colors.get(action['priority'], '#9E9E9E')
        
        st.markdown(f"""
        <div style="background: white; border-left: 4px solid {priority_color}; 
                    border-radius: 6px; padding: 16px; margin-bottom: 12px; 
                    box-shadow: 0 1px 4px rgba(0,0,0,0.05);">
            
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="flex: 1;">
                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                        <span style="background: {priority_color}; color: white; 
                                    border-radius: 4px; padding: 2px 8px; font-size: 11px; 
                                    font-weight: 700; margin-right: 8px;">
                            {action['priority']}
                        </span>
                        <h4 style="margin: 0; color: #333; font-weight: 600;">
                            {i}. {action['action']}
                        </h4>
                    </div>
                    
                    <div style="color: #666; font-size: 13px; margin-bottom: 8px;">
                        {action['description']}
                    </div>
                    
                    <div style="display: flex; gap: 16px; font-size: 12px; color: #999;">
                        <div>⏱️ Timeline: <strong>{action['timeline']}</strong></div>
                        <div>📊 Impact: <strong>{action['impact']}</strong></div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_fraud_stats_row():
    """
    Render fraud detection statistics in a metric row.
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📈 Fraud Trend (2025)",
            "↑ 208%",
            "AI-generated documents",
            delta_color="inverse"
        )
    
    with col2:
        st.metric(
            "🏦 Bank Statement Fraud",
            "59%",
            "of fraudulent documents",
            delta_color="off"
        )
    
    with col3:
        st.metric(
            "⚠️ Detection Gap",
            "UK Bank",
            "£750K fraud prevented",
            delta_color="normal"
        )
    
    with col4:
        st.metric(
            "🛡️ Your Status",
            "NOT ACTIVE",
            "AI fraud detection",
            delta_color="inverse"
        )
