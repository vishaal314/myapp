"""
Landing page components for DataGuardian Pro.
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
    st.markdown("""
    <div style="background-color: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); border: 1px solid #f0f0f0; margin-bottom: 20px;">
        <h3 style="color: #4f46e5; margin-top: 0; font-weight: 600; font-size: 18px;">GDPR Fine Protection</h3>
        <p style="font-size: 14px; color: #4b5563; margin-bottom: 15px;">
            The EU can impose fines up to <strong>€20 million</strong> or <strong>4% of global revenue</strong> for GDPR violations. 
            Our platform helps mitigate these risks.
        </p>
        <div style="display: flex; align-items: center; gap: 15px;">
            <div style="background-color: #4f46e5; border-radius: 8px; height: 100px; width: 120px; display: flex; justify-content: center; align-items: center; flex-direction: column;">
                <span style="color: white; font-size: 22px; font-weight: bold;">€20M</span>
                <span style="color: white; font-size: 12px;">Maximum Fine</span>
            </div>
            <div style="flex-grow: 1;">
                <div style="height: 8px; background-color: #e5e7eb; border-radius: 4px; margin-bottom: 10px; position: relative;">
                    <div style="position: absolute; top: 0; left: 0; height: 8px; width: 65%; background-color: #4f46e5; border-radius: 4px;"></div>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 12px; color: #6b7280;">
                    <span>Lower Risk</span>
                    <span style="font-weight: 600; color: #4f46e5;">Current Status: 65% Protected</span>
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
    st.markdown("""
    <div style="background-color: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); border: 1px solid #f0f0f0; margin-bottom: 20px;">
        <h3 style="color: #4f46e5; margin-top: 0; font-weight: 600; font-size: 18px;">Compliance Status</h3>
        
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-top: 15px;">
            <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px;">
                <div style="font-size: 13px; color: #6b7280; margin-bottom: 5px;">PII Detection</div>
                <div style="display: flex; align-items: flex-end; justify-content: space-between;">
                    <span style="font-size: 22px; font-weight: 600; color: #111827;">87%</span>
                    <div style="height: 30px; width: 60px;">
                        <div style="background-color: #4f46e5; width: 87%; height: 6px; border-radius: 3px;"></div>
                    </div>
                </div>
            </div>
            
            <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px;">
                <div style="font-size: 13px; color: #6b7280; margin-bottom: 5px;">Data Processing</div>
                <div style="display: flex; align-items: flex-end; justify-content: space-between;">
                    <span style="font-size: 22px; font-weight: 600; color: #111827;">79%</span>
                    <div style="height: 30px; width: 60px;">
                        <div style="background-color: #4f46e5; width: 79%; height: 6px; border-radius: 3px;"></div>
                    </div>
                </div>
            </div>
            
            <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px;">
                <div style="font-size: 13px; color: #6b7280; margin-bottom: 5px;">Data Security</div>
                <div style="display: flex; align-items: flex-end; justify-content: space-between;">
                    <span style="font-size: 22px; font-weight: 600; color: #111827;">92%</span>
                    <div style="height: 30px; width: 60px;">
                        <div style="background-color: #4f46e5; width: 92%; height: 6px; border-radius: 3px;"></div>
                    </div>
                </div>
            </div>
            
            <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px;">
                <div style="font-size: 13px; color: #6b7280; margin-bottom: 5px;">Documentation</div>
                <div style="display: flex; align-items: flex-end; justify-content: space-between;">
                    <span style="font-size: 22px; font-weight: 600; color: #111827;">65%</span>
                    <div style="height: 30px; width: 60px;">
                        <div style="background-color: #4f46e5; width: 65%; height: 6px; border-radius: 3px;"></div>
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
    st.markdown("""
    <div style="background-color: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); border: 1px solid #f0f0f0; margin-bottom: 20px;">
        <h3 style="color: #4f46e5; margin-top: 0; font-weight: 600; font-size: 18px;">Sustainability Impact</h3>
        
        <div style="display: flex; align-items: center; gap: 15px; margin-top: 10px; margin-bottom: 15px;">
            <div style="position: relative; width: 80px; height: 80px;">
                <!-- SVG Circle Chart -->
                <svg width="80" height="80" viewBox="0 0 80 80">
                    <circle cx="40" cy="40" r="35" fill="none" stroke="#e5e7eb" stroke-width="8"/>
                    <circle cx="40" cy="40" r="35" fill="none" stroke="#4f46e5" stroke-width="8" stroke-dasharray="220" stroke-dashoffset="60" transform="rotate(-90 40 40)"/>
                    <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-size="16" font-weight="bold" fill="#111827">78%</text>
                </svg>
            </div>
            <div>
                <p style="font-size: 14px; color: #4b5563; margin: 0;">
                    Your privacy practices contribute to a <strong>78% sustainability score</strong>, reducing digital waste and energy consumption.
                </p>
            </div>
        </div>
        
        <div style="background-color: #f9fafb; border-radius: 8px; padding: 10px 15px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 14px; color: #4b5563;">Estimated Annual Savings:</span>
                <span style="font-size: 16px; font-weight: 600; color: #047857;">€14,500</span>
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
    Display a grid layout with all landing page components.
    """
    # Create two columns with specific widths
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("""
        # DataGuardian Pro
        ### Enterprise Privacy Compliance Platform
        
        DataGuardian Pro is a comprehensive GDPR compliance platform that helps organizations identify, 
        analyze, and protect personally identifiable information (PII) across multiple data sources.
        """)
        
        # Create call-to-action buttons
        st.markdown("""
        <div style="display: flex; gap: 10px; margin-bottom: 20px;">
            <button style="background-color: #4f46e5; color: white; border: none; padding: 8px 16px; font-size: 14px; font-weight: 600; border-radius: 6px; cursor: pointer;">
                Start Free Trial ➔
            </button>
            <button style="background-color: rgba(79, 70, 229, 0.1); color: #4f46e5; border: 1px solid #4f46e5; padding: 8px 16px; font-size: 14px; font-weight: 500; border-radius: 6px; cursor: pointer;">
                Request Demo ✉
            </button>
        </div>
        """, unsafe_allow_html=True)
        
        # Service cards
        st.markdown("""
        ### Our Scanning Services
        
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-top: 15px; margin-bottom: 20px;">
            <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); border: 1px solid #f0f0f0;">
                <div style="color: #4f46e5; font-weight: 600; margin-bottom: 10px;">Code Scanner</div>
                <p style="font-size: 14px; color: #4b5563; margin: 0;">
                    Detect PII and security vulnerabilities in your source code repositories.
                </p>
            </div>
            
            <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); border: 1px solid #f0f0f0;">
                <div style="color: #4f46e5; font-weight: 600; margin-bottom: 10px;">Document Scanner</div>
                <p style="font-size: 14px; color: #4b5563; margin: 0;">
                    Find sensitive information in PDFs, Word documents, and other files.
                </p>
            </div>
            
            <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); border: 1px solid #f0f0f0;">
                <div style="color: #4f46e5; font-weight: 600; margin-bottom: 10px;">Database Scanner</div>
                <p style="font-size: 14px; color: #4b5563; margin: 0;">
                    Identify PII stored in databases and data warehouses.
                </p>
            </div>
            
            <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); border: 1px solid #f0f0f0;">
                <div style="color: #4f46e5; font-weight: 600; margin-bottom: 10px;">API Scanner</div>
                <p style="font-size: 14px; color: #4b5563; margin: 0;">
                    Detect personal data transmitted through your APIs.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Add the fine protection card
        display_gdpr_fine_card()
        
        # Add the compliance status card
        display_compliance_status_card()
        
        # Add the sustainability card
        display_sustainability_simple_card()
        
        # Add the GDPR principles card
        display_gdpr_principles_card()