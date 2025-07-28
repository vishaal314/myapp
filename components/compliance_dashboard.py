"""
Compliance Dashboard Component

This module provides the real-time compliance score visualization and tracking
for the DataGuardian Pro dashboard.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from services.compliance_score import ComplianceScoreManager

def render_compliance_dashboard(current_username: Optional[str] = None):
    """
    Render the compliance score dashboard with interactive visualizations.
    
    Args:
        current_username: Optional username to filter results by
    """
    # Initialize compliance score manager
    manager = ComplianceScoreManager()
    
    # Update score with latest data
    current_score = manager.update_score()
    
    # Get trend information
    trend = manager.get_score_trend(days=30)
    
    # Get badge data
    badge = manager.get_score_badge(current_score["overall_score"])
    
    # Create dashboard layout
    st.subheader("Compliance Score Dashboard")
    
    # Main score display with badge
    st.markdown(f"""
    <div style="background-color: white; border-radius: 10px; padding: 20px; margin-bottom: 20px;
               box-shadow: 0 2px 10px rgba(0,0,0,0.1); position: relative;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h3 style="margin: 0; color: #333;">Current Compliance Score</h3>
                <div style="display: flex; align-items: baseline; margin-top: 5px;">
                    <span style="font-size: 42px; font-weight: bold; color: {badge['color']};">
                        {current_score["overall_score"]}
                    </span>
                    <span style="font-size: 16px; color: #666; margin-left: 5px;">/100</span>
                </div>
                <div style="margin-top: 10px;">
                    <span style="font-weight: 500; color: {badge['color']};">{badge['level']}</span>
                    <span style="color: #666; font-size: 14px; display: block; margin-top: 3px;">
                        {badge['description']}
                    </span>
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 16px; font-weight: 500; margin-bottom: 5px;">30-Day Trend</div>
                <div style="display: flex; align-items: center; justify-content: flex-end;">
                    <span style="font-size: 24px; color: {
                        '#4CAF50' if trend['direction'] == 'improving' else 
                        '#F44336' if trend['direction'] == 'declining' else 
                        '#9E9E9E'
                    };">
                        {
                            '↑' if trend['direction'] == 'improving' else 
                            '↓' if trend['direction'] == 'declining' else 
                            '→'
                        }
                    </span>
                    <span style="margin-left: 5px; font-weight: 500; color: {
                        '#4CAF50' if trend['direction'] == 'improving' else 
                        '#F44336' if trend['direction'] == 'declining' else 
                        '#9E9E9E'
                    };">
                        {f"{abs(trend['percentage_change'])}%" if trend['direction'] != 'stable' else 'Stable'}
                    </span>
                </div>
                <div style="color: #666; font-size: 14px; margin-top: 3px;">
                    {f"{'Increased' if trend['score_change'] > 0 else 'Decreased'} by {abs(trend['score_change'])} points" 
                     if trend['direction'] != 'stable' else 'No significant change'}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two-column layout for charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Timeline chart
        st.write("#### Compliance Score Timeline")
        timeline_chart = manager.create_score_timeline_chart(days=90)
        st.plotly_chart(timeline_chart, use_container_width=True)
    
    with col2:
        # Component radar chart
        st.write("#### Component Analysis")
        radar_chart = manager.create_component_radar_chart()
        st.plotly_chart(radar_chart, use_container_width=True)
    
    # Add compliance recommendations based on component scores
    _render_compliance_recommendations(current_score)

def _render_compliance_recommendations(score_data: Dict[str, Any]):
    """
    Render actionable compliance recommendations based on the current score.
    
    Args:
        score_data: Current compliance score data
    """
    # Get component scores
    components = score_data.get("components", {})
    
    # Filter components that need improvement (score < 80)
    needs_improvement = {k: v for k, v in components.items() if v is not None and v < 80}
    
    if not needs_improvement:
        st.success("🎉 Great job! Your compliance practices meet or exceed all standards. Continue monitoring to maintain this level.")
        return
    
    # Recommendations by component
    recommendations = {
        "code": [
            "Implement automated PII detection in your CI/CD pipeline",
            "Add code review steps specifically for privacy compliance",
            "Update PII handling patterns in your codebase"
        ],
        "blob": [
            "Review document retention policies",
            "Implement document classification for sensitive information",
            "Add metadata scanning for sensitive documents"
        ],
        "dpia": [
            "Schedule regular DPIA reviews for all data processing activities",
            "Document all high-risk processing activities",
            "Consult with your DPO on DPIA findings"
        ],
        "image": [
            "Implement image redaction for sensitive content",
            "Add face detection and blurring capabilities",
            "Document image processing practices"
        ],
        "website": [
            "Update cookie consent mechanisms",
            "Review third-party tracking scripts",
            "Implement privacy by design in web forms"
        ],
        "database": [
            "Implement column-level encryption for sensitive data",
            "Review database access controls",
            "Add audit logging for sensitive data access"
        ]
    }
    
    # Display recommendations
    st.write("### Compliance Recommendations")
    
    for component, score in sorted(needs_improvement.items(), key=lambda x: x[1]):
        if component in recommendations:
            # Determine severity based on score
            if score < 60:
                severity = "High Priority"
                color = "#F44336"  # Red
            elif score < 70:
                severity = "Medium Priority"
                color = "#FF9800"  # Orange
            else:
                severity = "Low Priority" 
                color = "#FFC107"  # Amber
            
            # Get component display name
            display_name = {
                "code": "Code Repositories",
                "blob": "Documents & Files",
                "dpia": "Data Protection Impact Assessment",
                "image": "Image Processing",
                "website": "Website & Cookies",
                "database": "Database Management"
            }.get(component, component.title())
            
            # Display component recommendations
            st.markdown(f"""
            <div style="background-color: white; border-radius: 8px; padding: 15px; margin-bottom: 15px;
                       box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-left: 4px solid {color};">
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span style="font-weight: 500;">{display_name}</span>
                    <span style="color: {color}; font-weight: 500;">{severity}</span>
                </div>
                <div style="margin-left: 15px;">
                    {"<br>".join(f"• {rec}" for rec in recommendations[component][:2])}
                </div>
            </div>
            """, unsafe_allow_html=True)

def generate_mock_compliance_data():
    """
    Generate mock compliance data for testing.
    This should only be called if no real scan data is available to generate compliance scores.
    """
    # Call the mock data generator from the compliance score module
    from services.compliance_score import generate_mock_history
    generate_mock_history(days=90)
    st.success("Generated mock compliance history for demonstration purposes.")

if __name__ == "__main__":
    # Note: set_page_config is already called in main app.py
    # Remove duplicate call to prevent Streamlit error
    render_compliance_dashboard()