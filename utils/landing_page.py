"""
Landing page components for DataGuardian.
Provides professionally designed UI components for the landing page.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List, Optional

def display_gdpr_fine_card() -> None:
    """
    Display a professional, simple card showing GDPR fine information.
    """
    # Using fixed values for the landing page demo
    protection_percentage = 65
    max_fine_millions = 20
    
    st.markdown(f"""
    <div style="background-color: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); border: 1px solid #f0f0f0; margin-bottom: 20px;">
        <h3 style="color: #4f46e5; margin-top: 0; font-weight: 600; font-size: 18px;">GDPR Fine Protection</h3>
        <p style="font-size: 14px; color: #4b5563; margin-bottom: 15px;">
            The EU can impose fines up to <strong>€{max_fine_millions} million</strong> or <strong>4% of global revenue</strong> for GDPR violations. 
            Our platform helps mitigate these risks.
        </p>
        <div style="display: flex; align-items: center; gap: 15px;">
            <div style="background-color: #4f46e5; border-radius: 8px; height: 100px; width: 120px; display: flex; justify-content: center; align-items: center; flex-direction: column;">
                <span style="color: white; font-size: 22px; font-weight: bold;">€{max_fine_millions}M</span>
                <span style="color: white; font-size: 12px;">Maximum Fine</span>
            </div>
            <div style="flex-grow: 1;">
                <div style="height: 8px; background-color: #e5e7eb; border-radius: 4px; margin-bottom: 10px; position: relative;">
                    <div style="position: absolute; top: 0; left: 0; height: 8px; width: {protection_percentage}%; background-color: #4f46e5; border-radius: 4px;"></div>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 12px; color: #6b7280;">
                    <span>Lower Risk</span>
                    <span style="font-weight: 600; color: #4f46e5;">Current Status: {protection_percentage}% Protected</span>
                    <span>Higher Risk</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_compliance_status_card() -> None:
    """
    Display a professional card showing compliance status.
    """
    # Using fixed values for the landing page demo
    pii_detection = 87
    data_processing = 79
    data_security = 92
    documentation = 65
    
    st.markdown(f"""
    <div style="background-color: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); border: 1px solid #f0f0f0; margin-bottom: 20px;">
        <h3 style="color: #4f46e5; margin-top: 0; font-weight: 600; font-size: 18px;">Compliance Status</h3>
        
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-top: 15px;">
            <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px;">
                <div style="font-size: 13px; color: #6b7280; margin-bottom: 5px;">PII Detection</div>
                <div style="display: flex; align-items: flex-end; justify-content: space-between;">
                    <span style="font-size: 22px; font-weight: 600; color: #111827;">{pii_detection}%</span>
                    <div style="height: 30px; width: 60px;">
                        <div style="background-color: #4f46e5; width: {pii_detection}%; height: 6px; border-radius: 3px;"></div>
                    </div>
                </div>
            </div>
            
            <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px;">
                <div style="font-size: 13px; color: #6b7280; margin-bottom: 5px;">Data Processing</div>
                <div style="display: flex; align-items: flex-end; justify-content: space-between;">
                    <span style="font-size: 22px; font-weight: 600; color: #111827;">{data_processing}%</span>
                    <div style="height: 30px; width: 60px;">
                        <div style="background-color: #4f46e5; width: {data_processing}%; height: 6px; border-radius: 3px;"></div>
                    </div>
                </div>
            </div>
            
            <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px;">
                <div style="font-size: 13px; color: #6b7280; margin-bottom: 5px;">Data Security</div>
                <div style="display: flex; align-items: flex-end; justify-content: space-between;">
                    <span style="font-size: 22px; font-weight: 600; color: #111827;">{data_security}%</span>
                    <div style="height: 30px; width: 60px;">
                        <div style="background-color: #4f46e5; width: {data_security}%; height: 6px; border-radius: 3px;"></div>
                    </div>
                </div>
            </div>
            
            <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px;">
                <div style="font-size: 13px; color: #6b7280; margin-bottom: 5px;">Documentation</div>
                <div style="display: flex; align-items: flex-end; justify-content: space-between;">
                    <span style="font-size: 22px; font-weight: 600; color: #111827;">{documentation}%</span>
                    <div style="height: 30px; width: 60px;">
                        <div style="background-color: #4f46e5; width: {documentation}%; height: 6px; border-radius: 3px;"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_sustainability_simple_card() -> None:
    """
    Display a simple, professional sustainability card.
    """
    # Using fixed values for the landing page
    sustainability_score = 78
    annual_savings = 14500
    
    # Calculate circle metrics
    circumference = 2 * 3.14159 * 35  # 2πr where r=35
    dashoffset = circumference * (1 - sustainability_score/100)
    
    st.markdown(f"""
    <div style="background-color: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); border: 1px solid #f0f0f0; margin-bottom: 20px;">
        <h3 style="color: #4f46e5; margin-top: 0; font-weight: 600; font-size: 18px;">Sustainability Impact</h3>
        
        <div style="display: flex; align-items: center; gap: 15px; margin-top: 10px; margin-bottom: 15px;">
            <div style="position: relative; width: 80px; height: 80px;">
                <!-- SVG Circle Chart -->
                <svg width="80" height="80" viewBox="0 0 80 80">
                    <circle cx="40" cy="40" r="35" fill="none" stroke="#e5e7eb" stroke-width="8"/>
                    <circle cx="40" cy="40" r="35" fill="none" stroke="#4f46e5" stroke-width="8" stroke-dasharray="{circumference}" stroke-dashoffset="{dashoffset}" transform="rotate(-90 40 40)"/>
                    <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-size="16" font-weight="bold" fill="#111827">{sustainability_score}%</text>
                </svg>
            </div>
            <div>
                <p style="font-size: 14px; color: #4b5563; margin: 0;">
                    Your privacy practices contribute to a <strong>{sustainability_score}% sustainability score</strong>, reducing digital waste and energy consumption.
                </p>
            </div>
        </div>
        
        <div style="background-color: #f9fafb; border-radius: 8px; padding: 10px 15px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 14px; color: #4b5563;">Estimated Annual Savings:</span>
                <span style="font-size: 16px; font-weight: 600; color: #047857;">€{annual_savings:,}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_gdpr_principles_card() -> None:
    """
    Display a professional card showing the 7 GDPR principles.
    """
    st.markdown("""
    <div style="background-color: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); border: 1px solid #f0f0f0; margin-bottom: 20px;">
        <h3 style="color: #4f46e5; margin-top: 0; font-weight: 600; font-size: 18px;">7 GDPR Principles</h3>
        
        <div style="display: grid; grid-template-columns: repeat(1, 1fr); gap: 10px; margin-top: 10px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="background-color: #4f46e5; border-radius: 50%; width: 24px; height: 24px; display: flex; justify-content: center; align-items: center; flex-shrink: 0;">
                    <span style="color: white; font-size: 12px; font-weight: bold;">1</span>
                </div>
                <span style="font-size: 14px; color: #4b5563;"><strong>Lawfulness, Fairness and Transparency</strong> - Process data legally with transparency</span>
            </div>
            
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="background-color: #4f46e5; border-radius: 50%; width: 24px; height: 24px; display: flex; justify-content: center; align-items: center; flex-shrink: 0;">
                    <span style="color: white; font-size: 12px; font-weight: bold;">2</span>
                </div>
                <span style="font-size: 14px; color: #4b5563;"><strong>Purpose Limitation</strong> - Collect data for specified purposes only</span>
            </div>
            
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="background-color: #4f46e5; border-radius: 50%; width: 24px; height: 24px; display: flex; justify-content: center; align-items: center; flex-shrink: 0;">
                    <span style="color: white; font-size: 12px; font-weight: bold;">3</span>
                </div>
                <span style="font-size: 14px; color: #4b5563;"><strong>Data Minimization</strong> - Only collect what's absolutely necessary</span>
            </div>
            
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="background-color: #4f46e5; border-radius: 50%; width: 24px; height: 24px; display: flex; justify-content: center; align-items: center; flex-shrink: 0;">
                    <span style="color: white; font-size: 12px; font-weight: bold;">4</span>
                </div>
                <span style="font-size: 14px; color: #4b5563;"><strong>Accuracy</strong> - Keep personal data accurate and up to date</span>
            </div>
            
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="background-color: #4f46e5; border-radius: 50%; width: 24px; height: 24px; display: flex; justify-content: center; align-items: center; flex-shrink: 0;">
                    <span style="color: white; font-size: 12px; font-weight: bold;">5</span>
                </div>
                <span style="font-size: 14px; color: #4b5563;"><strong>Storage Limitation</strong> - Keep data only as long as necessary</span>
            </div>
            
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="background-color: #4f46e5; border-radius: 50%; width: 24px; height: 24px; display: flex; justify-content: center; align-items: center; flex-shrink: 0;">
                    <span style="color: white; font-size: 12px; font-weight: bold;">6</span>
                </div>
                <span style="font-size: 14px; color: #4b5563;"><strong>Integrity and Confidentiality</strong> - Ensure appropriate security</span>
            </div>
            
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="background-color: #4f46e5; border-radius: 50%; width: 24px; height: 24px; display: flex; justify-content: center; align-items: center; flex-shrink: 0;">
                    <span style="color: white; font-size: 12px; font-weight: bold;">7</span>
                </div>
                <span style="font-size: 14px; color: #4b5563;"><strong>Accountability</strong> - Take responsibility for compliance</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_landing_page_grid() -> None:
    """
    Display a simplified, professional grid layout for the landing page.
    This design prioritizes clean presentation without exceptions or overlapping content.
    """
    # Create a clean header with the platform title
    st.markdown("""
    <h1 style="color: #1e3a8a; margin-bottom: 5px;">DataGuardian</h1>
    <h3 style="color: #4b5563; font-weight: 500; margin-top: 0; margin-bottom: 20px;">Enterprise Privacy Compliance Platform</h3>
    """, unsafe_allow_html=True)
    
    # Create two columns with specific widths
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Main description
        st.markdown("""
        DataGuardian is a comprehensive GDPR compliance platform that helps organizations identify, 
        analyze, and protect personally identifiable information (PII) across multiple data sources.
        """)
        
        # Create call-to-action buttons
        st.markdown("""
        <div style="display: flex; gap: 10px; margin: 20px 0;">
            <button style="background-color: #4f46e5; color: white; border: none; padding: 8px 16px; font-size: 14px; font-weight: 600; border-radius: 6px; cursor: pointer;">
                Start Free Trial ➔
            </button>
            <button style="background-color: rgba(79, 70, 229, 0.1); color: #4f46e5; border: 1px solid #4f46e5; padding: 8px 16px; font-size: 14px; font-weight: 500; border-radius: 6px; cursor: pointer;">
                Request Demo ✉
            </button>
        </div>
        """, unsafe_allow_html=True)
        
        # Simple text-based scanning services section
        st.markdown("### Our Scanning Services")
        
        services = {
            "Code Scanner": "Detect PII and security vulnerabilities in source code repositories.",
            "Document Scanner": "Find sensitive information in PDFs, Word documents, and other files.",
            "Database Scanner": "Identify PII stored in databases and data warehouses.",
            "API Scanner": "Detect personal data transmitted through APIs.",
            "Image Scanner": "Find faces and other PII in images using computer vision.",
            "Website Scanner": "Analyze websites for cookie compliance and data collection."
        }
        
        # Create a clean layout for services
        service_cols = st.columns(2)
        for i, (service, description) in enumerate(services.items()):
            with service_cols[i % 2]:
                st.markdown(f"""
                <div style="background-color: white; padding: 15px; border-radius: 10px; 
                           box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #f0f0f0;
                           margin-bottom: 15px;">
                    <div style="color: #4f46e5; font-weight: 600; margin-bottom: 5px;">{service}</div>
                    <p style="font-size: 14px; color: #4b5563; margin: 0;">
                        {description}
                    </p>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        # Add the fine protection card only - keep it clean and simple
        display_gdpr_fine_card()
        
        # Simple information box for GDPR principles
        st.markdown("""
        <div style="background-color: white; border-radius: 10px; padding: 20px; 
                   box-shadow: 0 2px 12px rgba(0,0,0,0.1); border: 1px solid #f0f0f0; 
                   margin-bottom: 20px;">
            <h3 style="color: #4f46e5; margin-top: 0; font-weight: 600; font-size: 18px;">GDPR Core Principles</h3>
            <ul style="margin: 0; padding-left: 20px;">
                <li style="margin-bottom: 8px; font-size: 14px; color: #4b5563;">Lawfulness, Fairness and Transparency</li>
                <li style="margin-bottom: 8px; font-size: 14px; color: #4b5563;">Purpose Limitation</li>
                <li style="margin-bottom: 8px; font-size: 14px; color: #4b5563;">Data Minimization</li>
                <li style="margin-bottom: 8px; font-size: 14px; color: #4b5563;">Accuracy</li>
                <li style="margin-bottom: 8px; font-size: 14px; color: #4b5563;">Storage Limitation</li>
                <li style="margin-bottom: 8px; font-size: 14px; color: #4b5563;">Integrity and Confidentiality</li>
                <li style="margin-bottom: 0px; font-size: 14px; color: #4b5563;">Accountability</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature highlight box
        st.markdown("""
        <div style="background-color: white; border-radius: 10px; padding: 20px; 
                   box-shadow: 0 2px 12px rgba(0,0,0,0.1); border: 1px solid #f0f0f0;">
            <h3 style="color: #4f46e5; margin-top: 0; font-weight: 600; font-size: 18px;">Key Features</h3>
            <div style="margin-top: 15px;">
                <div style="margin-bottom: 12px;">
                    <div style="font-weight: 600; color: #111827; font-size: 15px;">Multi-source scanning</div>
                    <p style="margin-top: 4px; margin-bottom: 0; font-size: 14px; color: #4b5563;">
                        PII detection across code, documents, databases and APIs
                    </p>
                </div>
                <div style="margin-bottom: 12px;">
                    <div style="font-weight: 600; color: #111827; font-size: 15px;">Advanced AI Analysis</div>
                    <p style="margin-top: 4px; margin-bottom: 0; font-size: 14px; color: #4b5563;">
                        Smart risk assessment and automated remediation advice
                    </p>
                </div>
                <div style="margin-bottom: 0px;">
                    <div style="font-weight: 600; color: #111827; font-size: 15px;">Compliance Dashboards</div>
                    <p style="margin-top: 4px; margin-bottom: 0; font-size: 14px; color: #4b5563;">
                        Visualize compliance status and track progress over time
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)