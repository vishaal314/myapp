"""
Streamlit demo of the Smart AI-powered risk severity color-coding system.
Run this file to see a visual demonstration of the risk analyzer.

Usage:
    streamlit run examples/risk_analyzer_streamlit_demo.py
"""
import sys
import os
import json
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import risk analyzer
from utils.risk_analyzer import RiskAnalyzer, get_severity_color, colorize_finding, get_risk_color_gradient

# Set page config
# Note: set_page_config already called in main app.py
# st.set_page_config(
#     page_title="DataGuardian Pro - Risk Analyzer Demo",
#     page_icon="🔒",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# Configure the app
st.title("Smart AI-powered Risk Severity Analysis")
st.markdown("""
This interactive demo shows how the Smart AI-powered risk severity color-coding system 
analyzes findings from different scan types and assigns severity levels based on context, 
concentration, and clustering factors.
""")

# Add CSS for custom styling
st.markdown("""
<style>
    .risk-critical {
        background-color: #FFEBEE;
        color: #C62828;
        font-weight: bold;
        padding: 4px 8px;
        border-radius: 4px;
    }
    .risk-high {
        background-color: #FFEBEE;
        color: #D32F2F;
        font-weight: bold;
        padding: 4px 8px;
        border-radius: 4px;
    }
    .risk-medium {
        background-color: #FFF8E1;
        color: #F57F17;
        font-weight: bold;
        padding: 4px 8px;
        border-radius: 4px;
    }
    .risk-low {
        background-color: #F1F8E9;
        color: #558B2F;
        padding: 4px 8px;
        border-radius: 4px;
    }
    .risk-info {
        background-color: #E3F2FD;
        color: #1976D2;
        padding: 4px 8px;
        border-radius: 4px;
    }
    .risk-safe {
        background-color: #E8F5E9;
        color: #388E3C;
        padding: 4px 8px;
        border-radius: 4px;
    }
    .risk-score-box {
        padding: 20px;
        border-radius: 10px;
        color: white;
        font-weight: bold;
        text-align: center;
        font-size: 24px;
    }
</style>
""", unsafe_allow_html=True)

# Example findings from different scan types
def load_example_findings():
    """Load example findings for different scan types"""
    # Code scan findings (example with source code vulnerabilities)
    code_findings = [
        {
            'type': 'Vulnerability:SQL Injection',
            'value': 'SELECT * FROM users WHERE id = " + user_id',
            'location': 'File: app.py, Line 42',
            'risk_level': 'High',
            'reason': 'SQL injection vulnerability can lead to data breach'
        },
        {
            'type': 'Vulnerability:XSS',
            'value': '<div>" + user_input + "</div>',
            'location': 'File: templates/page.html, Line 23',
            'risk_level': 'High',
            'reason': 'Cross-site scripting vulnerability can lead to session hijacking'
        },
        {
            'type': 'Credentials',
            'value': 'password = "admin123"',
            'location': 'File: config.py, Line 15',
            'risk_level': 'High',
            'reason': 'Hardcoded credentials can lead to unauthorized access'
        },
        {
            'type': 'Email',
            'value': 'john.doe@example.com',
            'location': 'File: users.py, Line 78',
            'risk_level': 'Medium',
            'reason': 'Email addresses are personal data under GDPR'
        },
        {
            'type': 'Email',
            'value': 'jane.smith@example.com',
            'location': 'File: users.py, Line 79',
            'risk_level': 'Medium',
            'reason': 'Email addresses are personal data under GDPR'
        },
        {
            'type': 'Email',
            'value': 'support@company.com',
            'location': 'File: config.py, Line 25',
            'risk_level': 'Low',
            'reason': 'Company email addresses are lower risk but still personal data'
        },
        {
            'type': 'API Key',
            'value': 'sk_test_abcdefghijklmnopqrstuvwxyz1234',
            'location': 'File: payment.py, Line 10',
            'risk_level': 'High',
            'reason': 'API keys should not be hardcoded in source code'
        }
    ]
    
    # Website scan findings (example with website vulnerabilities)
    website_findings = [
        {
            'type': 'Vulnerability:XSS',
            'value': 'document.write("<h2>Welcome, " + username + "!</h2>");',
            'location': 'URL: https://example.com/welcome, Line 15',
            'risk_level': 'High',
            'reason': 'Cross-site scripting vulnerability can lead to session hijacking'
        },
        {
            'type': 'Credit Card',
            'value': '4111-1111-1111-1111',
            'location': 'URL: https://example.com/checkout, Line 25',
            'risk_level': 'High',
            'reason': 'Credit card numbers should not be exposed in website content'
        },
        {
            'type': 'Email',
            'value': 'info@example.com',
            'location': 'URL: https://example.com/contact, Line 30',
            'risk_level': 'Medium',
            'reason': 'Email addresses are personal data under GDPR'
        },
        {
            'type': 'Vulnerability:CSRF',
            'value': '<form action="/transfer" method="POST">',
            'location': 'URL: https://example.com/account, Line 50',
            'risk_level': 'Medium',
            'reason': 'CSRF vulnerability can lead to unauthorized actions'
        },
        {
            'type': 'Vulnerability:Insecure Cookies',
            'value': 'document.cookie = "session_id=12345; path=/";',
            'location': 'URL: https://example.com/, Line 40',
            'risk_level': 'Medium',
            'reason': 'Insecure cookies can lead to session hijacking'
        },
        {
            'type': 'IP Address',
            'value': '192.168.1.1',
            'location': 'URL: https://example.com/admin, Line 10',
            'risk_level': 'Low',
            'reason': 'Internal IP addresses are personal data under GDPR'
        }
    ]
    
    # Document scan findings (example with sensitive personal data)
    document_findings = [
        {
            'type': 'Credit Card',
            'value': '5555-5555-5555-4444',
            'location': 'Document: contract.pdf, Page 5',
            'risk_level': 'High',
            'reason': 'Credit card numbers are high-risk financial data'
        },
        {
            'type': 'BSN',
            'value': '123456782',
            'location': 'Document: employees.xlsx, Row 8',
            'risk_level': 'High',
            'reason': 'BSN (Dutch SSN) is highly sensitive personal data'
        },
        {
            'type': 'Passport Number',
            'value': 'NW123456',
            'location': 'Document: travel.docx, Page 2',
            'risk_level': 'High',
            'reason': 'Passport numbers are sensitive identification data'
        },
        {
            'type': 'Medical Data',
            'value': 'Diagnosed with Type 2 Diabetes',
            'location': 'Document: medical_records.pdf, Page 10',
            'risk_level': 'High',
            'reason': 'Medical data is special category data under GDPR Art. 9'
        },
        {
            'type': 'Date of Birth',
            'value': '1980-01-15',
            'location': 'Document: employees.xlsx, Row 8',
            'risk_level': 'Medium',
            'reason': 'Date of birth is personal data and can be used for identity theft'
        },
        {
            'type': 'Address',
            'value': '123 Main Street, Amsterdam',
            'location': 'Document: customers.csv, Row 15',
            'risk_level': 'Medium',
            'reason': 'Physical addresses are personal data under GDPR'
        },
        {
            'type': 'Address',
            'value': '456 High Street, Rotterdam',
            'location': 'Document: customers.csv, Row 16',
            'risk_level': 'Medium',
            'reason': 'Physical addresses are personal data under GDPR'
        },
        {
            'type': 'Phone',
            'value': '+31 20 123 4567',
            'location': 'Document: contacts.xlsx, Row 5',
            'risk_level': 'Medium',
            'reason': 'Phone numbers are personal data under GDPR'
        },
        {
            'type': 'Email',
            'value': 'personal@example.com',
            'location': 'Document: contacts.xlsx, Row 5',
            'risk_level': 'Medium',
            'reason': 'Email addresses are personal data under GDPR'
        },
        {
            'type': 'Email',
            'value': 'another@example.com',
            'location': 'Document: contacts.xlsx, Row 6',
            'risk_level': 'Medium',
            'reason': 'Email addresses are personal data under GDPR'
        }
    ]
    
    # Database scan findings (example with sensitive database data)
    database_findings = [
        {
            'type': 'Credit Card',
            'value': '4111-1111-1111-1111',
            'location': 'Table: payments, Column: card_number',
            'risk_level': 'High',
            'reason': 'Unencrypted credit card data violates PCI DSS and GDPR'
        },
        {
            'type': 'BSN',
            'value': '123456782',
            'location': 'Table: employees, Column: bsn',
            'risk_level': 'High',
            'reason': 'BSN (Dutch SSN) requires special safeguards'
        },
        {
            'type': 'Vulnerability:Insecure Storage',
            'value': 'Passwords stored in plaintext',
            'location': 'Table: users, Column: password',
            'risk_level': 'Critical',
            'reason': 'Plaintext passwords can lead to account compromise'
        },
        {
            'type': 'Vulnerability:Encryption Missing',
            'value': 'No encryption for financial data',
            'location': 'Table: transactions, Database: financial',
            'risk_level': 'High',
            'reason': 'Financial data must be encrypted under GDPR'
        },
        {
            'type': 'Vulnerability:Excess Privilege',
            'value': 'User has excessive database privileges',
            'location': 'Database: customer_data, User: app_user',
            'risk_level': 'Medium',
            'reason': 'Principle of least privilege violation'
        },
        {
            'type': 'Email',
            'value': 'john.doe@example.com',
            'location': 'Table: users, Column: email',
            'risk_level': 'Medium',
            'reason': 'Email addresses are personal data under GDPR'
        },
        {
            'type': 'Phone',
            'value': '+31 20 123 4567',
            'location': 'Table: users, Column: phone',
            'risk_level': 'Medium',
            'reason': 'Phone numbers are personal data under GDPR'
        }
    ]
    
    return {
        'code_scan': code_findings,
        'website_scan': website_findings,
        'blob_scan': document_findings,
        'database_scan': database_findings
    }

def display_severity_scale():
    """Display the risk severity color scale"""
    st.subheader("Risk Severity Color Scale")
    cols = st.columns(6)
    
    severity_levels = [
        ("Critical", "critical", "#FF2A2A", "Severe vulnerabilities requiring immediate attention"),
        ("High", "high", "#FF5C5C", "High-risk issues that should be addressed urgently"),
        ("Medium", "medium", "#FFA726", "Moderate risk issues that should be planned for remediation"),
        ("Low", "low", "#FFEB3B", "Low risk issues to be aware of, address when possible"),
        ("Info", "info", "#2196F3", "Informational findings with minimal risk"),
        ("Safe", "safe", "#4CAF50", "No risk detected")
    ]
    
    for i, (label, cls, color, desc) in enumerate(severity_levels):
        with cols[i]:
            st.markdown(f"""
            <div style="background-color: {color}; color: white; padding: 10px; 
                       border-radius: 5px; text-align: center; font-weight: bold;">
                {label}
            </div>
            <div style="font-size: 0.8em; margin-top: 5px;">
                {desc}
            </div>
            """, unsafe_allow_html=True)

def display_findings_table(findings, title):
    """Display a table of findings with colorized severity levels"""
    st.subheader(title)
    
    if not findings:
        st.info("No findings to display")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(findings)
    
    # Create a new column for display
    df['severity_display'] = df['smart_severity'].apply(
        lambda x: f'<span class="risk-{x.lower()}">{x}</span>'
    )
    
    # Select columns to display
    display_cols = ['type', 'value', 'location', 'severity_display', 'smart_score']
    display_names = {
        'type': 'Finding Type',
        'value': 'Value',
        'location': 'Location',
        'severity_display': 'Severity',
        'smart_score': 'Risk Score'
    }
    
    # Create the table with custom formatting
    styled_table = f"""
    <div style="max-height: 300px; overflow-y: auto;">
    <table class="dataframe">
        <thead>
            <tr>
                {"".join(f'<th>{display_names[col]}</th>' for col in display_cols)}
            </tr>
        </thead>
        <tbody>
    """
    
    for _, row in df.iterrows():
        styled_table += "<tr>"
        for col in display_cols:
            if col == 'severity_display':
                styled_table += f"<td>{row[col]}</td>"
            elif col == 'smart_score':
                styled_table += f"<td>{row[col]:.2f}</td>"
            else:
                # Truncate long values
                val = str(row[col])
                if len(val) > 50:
                    val = val[:47] + "..."
                styled_table += f"<td>{val}</td>"
        styled_table += "</tr>"
    
    styled_table += """
        </tbody>
    </table>
    </div>
    """
    
    st.markdown(styled_table, unsafe_allow_html=True)

def create_risk_distribution_chart(summary):
    """Create a risk distribution chart"""
    # Extract risk distribution data
    risk_data = []
    for severity, count in summary['risk_distribution'].items():
        if count > 0:
            risk_data.append({'Severity': severity, 'Count': count})
    
    if not risk_data:
        return None
    
    # Convert to DataFrame
    risk_df = pd.DataFrame(risk_data)
    
    # Create color map
    color_map = {
        'critical': '#FF2A2A',
        'high': '#FF5C5C',
        'medium': '#FFA726',
        'low': '#FFEB3B',
        'info': '#2196F3',
        'safe': '#4CAF50'
    }
    
    # Create pie chart
    fig = px.pie(
        risk_df,
        values='Count',
        names='Severity',
        title="Risk Level Distribution",
        color='Severity',
        color_discrete_map=color_map
    )
    
    # Update layout
    fig.update_layout(
        legend_title="Severity Level",
        height=350
    )
    
    return fig

def create_findings_by_type_chart(summary):
    """Create a findings by type chart"""
    # Extract type distribution data
    type_data = []
    for finding_type, count in summary['type_distribution'].items():
        if count > 0:
            type_data.append({'Finding Type': finding_type, 'Count': count})
    
    if not type_data:
        return None
    
    # Convert to DataFrame
    type_df = pd.DataFrame(type_data)
    
    # Sort by count descending
    type_df = type_df.sort_values('Count', ascending=False)
    
    # Create horizontal bar chart
    fig = px.bar(
        type_df,
        y='Finding Type',
        x='Count',
        title="Findings by Type",
        orientation='h',
        color='Count',
        color_continuous_scale='Blues'
    )
    
    # Update layout
    fig.update_layout(
        yaxis_title="",
        xaxis_title="Count",
        height=350
    )
    
    return fig

def display_scan_analysis(scan_type, scan_name):
    """Display the analysis for a specific scan type"""
    st.header(f"{scan_name} Analysis")
    
    # Load findings
    findings = load_example_findings().get(scan_type, [])
    
    # Initialize risk analyzer
    risk_analyzer = RiskAnalyzer(scan_type=scan_type)
    
    # Analyze the findings
    summary, enhanced_findings = risk_analyzer.analyze_findings(findings)
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="risk-score-box" style="background-color: {summary['severity_color']};">
            Risk Score: {summary['risk_score']}/100
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.metric("Total Findings", summary['total_findings'])
    
    with col3:
        st.metric("Severity Level", summary['severity_level'].upper())
    
    # Display charts
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        risk_chart = create_risk_distribution_chart(summary)
        if risk_chart:
            st.plotly_chart(risk_chart, use_container_width=True)
    
    with chart_col2:
        type_chart = create_findings_by_type_chart(summary)
        if type_chart:
            st.plotly_chart(type_chart, use_container_width=True)
    
    # Display findings table
    display_findings_table(enhanced_findings, "Findings (Sorted by Smart Risk Score)")
    
    # Explanation of scoring factors
    with st.expander("How is the Smart Risk Score calculated?"):
        st.markdown("""
        ### Smart Risk Score Calculation

        The Smart AI-powered risk severity analysis calculates a risk score for each finding using these factors:

        1. **Base Score** - Initial score based on the standard risk level (High=3, Medium=2, Low=1)
        2. **Context Weight** - Different weights for different types of findings based on the scan context
        3. **Concentration Factor** - Increased severity when multiple findings of the same type are found
        4. **Clustering Factor** - Increased severity when multiple findings are found in the same area

        **Formula**: Smart Score = Base Score × Context Weight × Concentration Factor × Clustering Factor

        The overall risk score for the scan is calculated from the average of all smart scores, normalized to a 0-100 scale.
        """)
        
        # Example factors table
        st.subheader("Context Weight Examples for this Scan Type")
        context_weights = risk_analyzer.weights
        weight_df = pd.DataFrame({
            'Finding Type': list(context_weights.keys())[:10],  # Show first 10
            'Context Weight': [context_weights[k] for k in list(context_weights.keys())[:10]]
        })
        st.dataframe(weight_df, use_container_width=True)

def main():
    """Main function to run the Streamlit app"""
    # Display the severity scale
    display_severity_scale()
    
    st.markdown("---")
    
    # Add scan type selector
    scan_options = {
        'code_scan': 'Code Scanner',
        'website_scan': 'Website Scanner',
        'blob_scan': 'Document Scanner',
        'database_scan': 'Database Scanner'
    }
    
    selected_scan = st.selectbox(
        "Select Scan Type to Analyze",
        options=list(scan_options.keys()),
        format_func=lambda x: scan_options[x]
    )
    
    # Display the analysis for the selected scan
    display_scan_analysis(selected_scan, scan_options[selected_scan])
    
    # Information about the demo
    st.markdown("---")
    st.markdown("""
    ### About this Demo

    This demo showcases the Smart AI-powered risk severity color-coding system implemented in 
    DataGuardian Pro. The system uses context-aware analysis to provide more accurate risk assessments 
    than traditional static risk levels.

    All data shown in this demo is simulated and used for demonstration purposes only.
    """)

if __name__ == "__main__":
    main()