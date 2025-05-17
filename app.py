"""
DataGuardian Pro - Enterprise Privacy Compliance Platform

This is the main application that integrates all scanners, including:
- GDPR Code Scanner (with Dutch UAVG requirements)
- SOC2 Scanner
- PCI DSS Scanner
- EU AI Act Analyzer
"""

import streamlit as st
import pandas as pd
import time
import datetime
from io import BytesIO
import json
import uuid
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Set page configuration
st.set_page_config(
    page_title="DataGuardian Pro",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better appearance
st.markdown("""
<style>
    .main-header {
        background-color: #1E3A8A;
        padding: 1.5rem;
        border-radius: 5px;
        margin-bottom: 1.5rem;
    }
    .main-header h1 {
        color: white;
        margin: 0;
    }
    .main-header p {
        color: #BDD7FD;
        margin: 0;
    }
    .scanner-box {
        background-color: #F7FAFC;
        padding: 1.5rem;
        border-radius: 5px;
        border-left: 4px solid #3182CE;
        margin-bottom: 1rem;
    }
    .scanner-box h3 {
        margin-top: 0;
        color: #2C5282;
    }
    .finding-box-high {
        background-color: #FEF2F2;
        border-left: 4px solid #DC2626;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 0.5rem;
    }
    .finding-box-medium {
        background-color: #FFF7ED;
        border-left: 4px solid #F97316;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 0.5rem;
    }
    .finding-box-low {
        background-color: #F0FDF4;
        border-left: 4px solid #22C55E;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 0.5rem;
    }
    .score-box {
        background-color: #F9FAFB;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
    }
    .stTabs {
        background-color: white;
        padding: 1rem;
        border-radius: 5px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)


# Authentication function (simplified for demo)
def authenticate(username, password):
    """Simple authentication check"""
    if username == "admin" and password == "admin":
        return True
    return False


# Main application
def main():
    # Header
    st.markdown(
        "<div class='main-header'><h1>DataGuardian Pro</h1><p>Enterprise Privacy Compliance Platform</p></div>",
        unsafe_allow_html=True
    )
    
    # Sidebar navigation
    with st.sidebar:
        st.image("https://via.placeholder.com/150x150.png?text=DataGuardian", width=150)
        
        # Navigation menu
        st.subheader("Navigation")
        page = st.radio(
            "Select Scanner",
            [
                "Dashboard", 
                "GDPR Scanner",
                "SOC2 Scanner", 
                "PCI DSS Scanner",
                "EU AI Act Analyzer",
                "Settings"
            ]
        )
        
        # Authentication status (simplified)
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False
            
        # Login form
        if not st.session_state.authenticated:
            st.subheader("Login")
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login")
                
                if submit:
                    if authenticate(username, password):
                        st.session_state.authenticated = True
                        st.success("Login successful!")
                    else:
                        st.error("Invalid credentials")
        else:
            st.success("Logged in")
            if st.button("Logout"):
                st.session_state.authenticated = False
    
    # Main content based on selected page
    if page == "Dashboard":
        show_dashboard()
    elif page == "GDPR Scanner":
        show_gdpr_scanner()
    elif page == "SOC2 Scanner":
        show_soc2_scanner()
    elif page == "PCI DSS Scanner":
        show_pcidss_scanner()
    elif page == "EU AI Act Analyzer":
        show_eu_ai_act_analyzer()
    elif page == "Settings":
        show_settings()


# Dashboard page
def show_dashboard():
    st.header("Compliance Dashboard")
    
    # Overview metrics
    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
    
    with metrics_col1:
        st.metric("GDPR Compliance", "85%", "+3%")
    
    with metrics_col2:
        st.metric("SOC2 Compliance", "92%", "+1%")
    
    with metrics_col3:
        st.metric("PCI DSS Compliance", "78%", "-2%")
    
    with metrics_col4:
        st.metric("EU AI Act Readiness", "71%", "+5%")
    
    # Recent scans
    st.subheader("Recent Scans")
    
    # Sample data for recent scans
    scan_data = {
        "Date": ["2025-05-15", "2025-05-14", "2025-05-13", "2025-05-12", "2025-05-10"],
        "Scanner": ["GDPR", "SOC2", "PCI DSS", "EU AI Act", "GDPR"],
        "Repository": [
            "github.com/example/repo1", 
            "github.com/example/repo2",
            "github.com/example/repo3",
            "AI Model: recommendation-engine-v2",
            "github.com/example/repo4"
        ],
        "Score": [85, 92, 78, 71, 82],
        "Findings": [12, 5, 18, 9, 14]
    }
    
    scan_df = pd.DataFrame(scan_data)
    st.dataframe(scan_df)
    
    # Top issues
    st.subheader("Top Compliance Issues")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="finding-box-high">
            <h4>Missing Consent Collection</h4>
            <p>Found in 3 repositories</p>
            <p><strong>Regulation:</strong> GDPR Art. 6, UAVG</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="finding-box-high">
            <h4>Exposed API Keys</h4>
            <p>Found in 2 repositories</p>
            <p><strong>Regulation:</strong> SOC2 CC6.1, GDPR Art. 32</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="finding-box-high">
            <h4>Insecure Data Storage</h4>
            <p>Found in 2 repositories</p>
            <p><strong>Regulation:</strong> PCI DSS Req. 3.4</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="finding-box-medium">
            <h4>Inadequate Risk Assessment</h4>
            <p>Found in 1 AI model</p>
            <p><strong>Regulation:</strong> EU AI Act Art. 9</p>
        </div>
        """, unsafe_allow_html=True)


# GDPR Scanner page
def show_gdpr_scanner():
    st.header("GDPR Code Scanner")
    st.markdown("Scan your code repositories for GDPR compliance issues, including Dutch UAVG requirements")
    
    # Create layout with two columns
    col1, col2 = st.columns([1, 3])
    
    # Left column - Input form
    with col1:
        st.markdown("### Repository Settings")
        
        with st.form("gdpr_scan_form"):
            repo_url = st.text_input(
                "Repository URL",
                value="https://github.com/example/repository",
                help="URL to the GitHub or GitLab repository to scan"
            )
            
            scan_depth = st.select_slider(
                "Scan Depth",
                options=["Basic", "Standard", "Deep"],
                value="Standard",
                help="Deeper scans examine more files and git history"
            )
            
            organization_name = st.text_input(
                "Organization Name", 
                value="Your Organization",
                help="Will be included in the PDF report"
            )
            
            # Include Dutch UAVG regulations
            include_dutch = st.checkbox("Include Dutch UAVG Regulations", value=True)
            
            # Submit button
            submitted = st.form_submit_button("Run GDPR Scan", type="primary")
    
    # Right column - Results
    with col2:
        if submitted:
            # Add scan session to state
            if "gdpr_scan_completed" not in st.session_state:
                st.session_state.gdpr_scan_completed = False
            
            # Show scanning progress
            if not st.session_state.gdpr_scan_completed:
                with st.spinner("Running GDPR compliance scan..."):
                    # Progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Simulate scanning each principle
                    principles = [
                        "Lawfulness, Fairness and Transparency",
                        "Purpose Limitation",
                        "Data Minimization",
                        "Accuracy",
                        "Storage Limitation", 
                        "Integrity and Confidentiality",
                        "Accountability"
                    ]
                    
                    if include_dutch:
                        principles.append("Dutch UAVG Requirements")
                    
                    # Update progress for each principle
                    for i, principle in enumerate(principles):
                        # Update progress
                        progress = int((i + 1) / len(principles) * 100)
                        progress_bar.progress(progress)
                        status_text.text(f"Scanning for {principle}...")
                        time.sleep(0.5)  # Simulate processing time
                    
                    # Mark scan as complete
                    st.session_state.gdpr_scan_completed = True
                    st.session_state.repo_url = repo_url
                    st.session_state.organization_name = organization_name
                    st.session_state.include_dutch = include_dutch
                    
                    # Clear progress indicators
                    time.sleep(0.5)
                    progress_bar.empty()
                    status_text.empty()
            
            # Display scan completion message
            st.success("GDPR scan completed successfully!")
            
            # Generate realistic findings
            findings = [
                {
                    "id": "LFT-001",
                    "principle": "Lawfulness, Fairness and Transparency",
                    "severity": "high",
                    "title": "Missing Explicit Consent Collection",
                    "description": "User registration process does not include explicit consent options for data processing",
                    "location": "File: auth/signup.py, Line: 42-57",
                    "article": "GDPR Art. 6, UAVG Art. 8"
                },
                {
                    "id": "LFT-002",
                    "principle": "Lawfulness, Fairness and Transparency",
                    "severity": "medium",
                    "title": "Privacy Policy Not Prominently Displayed",
                    "description": "Privacy policy link is not clearly visible during user registration",
                    "location": "File: templates/signup.html, Line: 25",
                    "article": "GDPR Art. 13"
                },
                {
                    "id": "PL-001",
                    "principle": "Purpose Limitation",
                    "severity": "high",
                    "title": "Data Used for Multiple Undocumented Purposes",
                    "description": "User data collected for account creation is also used for analytics without separate consent",
                    "location": "File: analytics/user_tracking.py, Line: 78-92",
                    "article": "GDPR Art. 5-1b"
                },
                {
                    "id": "DM-001",
                    "principle": "Data Minimization",
                    "severity": "medium",
                    "title": "Excessive Personal Information Collection",
                    "description": "User registration form collects unnecessary personal details not required for service functionality",
                    "location": "File: models/user.py, Line: 15-28",
                    "article": "GDPR Art. 5-1c"
                }
            ]
            
            # Add Dutch-specific findings if selected
            if include_dutch:
                findings.append({
                    "id": "NL-001",
                    "principle": "Dutch-Specific Requirements",
                    "severity": "high",
                    "title": "Improper BSN Number Collection",
                    "description": "Dutch Citizen Service Numbers (BSN) are collected without proper legal basis",
                    "location": "File: models/dutch_user.py, Line: 28-36", 
                    "article": "UAVG Art. 46, GDPR Art. 9"
                })
                
                findings.append({
                    "id": "NL-002",
                    "principle": "Dutch-Specific Requirements",
                    "severity": "medium",
                    "title": "Missing Age Verification for Minors",
                    "description": "Application does not verify age for users under 16 years as required by Dutch regulations",
                    "location": "File: auth/registration.py, Line: 103-118", 
                    "article": "UAVG Art. 5, GDPR Art. 8"
                })
            
            # Calculate metrics
            high_risk = sum(1 for f in findings if f.get("severity") == "high")
            medium_risk = sum(1 for f in findings if f.get("severity") == "medium")
            low_risk = sum(1 for f in findings if f.get("severity") == "low")
            total_findings = len(findings)
            
            # Calculate compliance score
            compliance_score = max(0, 100 - (high_risk * 7) - (medium_risk * 3) - (low_risk * 1))
            
            # Create tabs for results
            tabs = st.tabs(["Overview", "Findings", "PDF Report"])
            
            # Overview tab
            with tabs[0]:
                # Compliance score with styling
                st.markdown("### Compliance Score")
                
                # Determine color based on score
                score_color = "green"
                if compliance_score < 80:
                    score_color = "orange"
                if compliance_score < 60:
                    score_color = "red"
                    
                # Display score
                st.markdown(f"""
                <div class='score-box'>
                    <h1 style='color: {score_color}; font-size: 4rem;'>{compliance_score}%</h1>
                    <p>GDPR Compliance Score</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Risk metrics
                st.markdown("### Risk Summary")
                metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                
                with metrics_col1:
                    st.metric("High Risk Issues", high_risk)
                
                with metrics_col2:
                    st.metric("Medium Risk Issues", medium_risk)
                
                with metrics_col3:
                    st.metric("Low Risk Issues", low_risk)
                    
                # Scan info
                st.markdown("### Scan Information")
                st.markdown(f"""
                * **Repository URL:** {st.session_state.repo_url}
                * **Organization:** {st.session_state.organization_name}
                * **Scan Date:** {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
                * **Dutch UAVG Regulations:** {'Included' if st.session_state.include_dutch else 'Excluded'}
                * **Total Issues:** {total_findings}
                """)
                
                # GDPR principles
                st.markdown("### GDPR Principle Compliance")
                
                # Create mock scores for each principle
                principle_scores = {
                    "Lawfulness, Fairness, Transparency": 70,
                    "Purpose Limitation": 80,
                    "Data Minimization": 85,
                    "Accuracy": 90,
                    "Storage Limitation": 85,
                    "Integrity and Confidentiality": 76,
                    "Accountability": 82
                }
                
                if include_dutch:
                    principle_scores["Dutch UAVG Compliance"] = 65
                
                # Create dataframe and chart
                principle_df = pd.DataFrame({
                    "Principle": list(principle_scores.keys()),
                    "Score": list(principle_scores.values())
                })
                
                st.bar_chart(principle_df.set_index("Principle"))
                    
            # Findings tab
            with tabs[1]:
                st.markdown("### Detailed Findings")
                
                # Group findings by principle
                findings_by_principle = {}
                for finding in findings:
                    principle = finding.get("principle", "Other")
                    if principle not in findings_by_principle:
                        findings_by_principle[principle] = []
                    findings_by_principle[principle].append(finding)
                
                # Display findings by principle
                for principle, principle_findings in findings_by_principle.items():
                    st.markdown(f"#### {principle}")
                    
                    for finding in principle_findings:
                        # Get severity and styling class
                        severity = finding.get("severity", "unknown")
                        severity_class = f"finding-box-{severity}"
                        
                        # Display finding with proper styling
                        st.markdown(f"""
                        <div class='{severity_class}'>
                            <h5>{finding.get('id', '')}: {finding.get('title', '')}</h5>
                            <p><strong>Severity:</strong> {severity.upper()}</p>
                            <p><strong>Description:</strong> {finding.get('description', '')}</p>
                            <p><strong>Location:</strong> {finding.get('location', '')}</p>
                            <p><strong>Regulation:</strong> {finding.get('article', '')}</p>
                        </div>
                        """, unsafe_allow_html=True)
            
            # PDF Report tab
            with tabs[2]:
                st.markdown("### Generate GDPR Compliance Report")
                
                # PDF generation function
                def generate_gdpr_pdf_report():
                    buffer = BytesIO()
                    doc = SimpleDocTemplate(buffer, pagesize=letter)
                    styles = getSampleStyleSheet()
                    
                    # Custom styles
                    title_style = ParagraphStyle(
                        name='TitleStyle',
                        parent=styles['Heading1'],
                        fontSize=20,
                        textColor=colors.navy,
                        spaceAfter=12
                    )
                    
                    header_style = ParagraphStyle(
                        name='HeaderStyle',
                        parent=styles['Heading2'],
                        fontSize=14,
                        textColor=colors.darkblue,
                        spaceAfter=8
                    )
                    
                    normal_style = styles['Normal']
                    
                    # Generate elements for PDF
                    elements = []
                    
                    # Header
                    elements.append(Paragraph("GDPR Compliance Report", title_style))
                    elements.append(Spacer(1, 0.25*inch))
                    
                    # Report metadata
                    elements.append(Paragraph(f"Organization: {st.session_state.organization_name}", normal_style))
                    elements.append(Paragraph(f"Repository: {st.session_state.repo_url}", normal_style))
                    elements.append(Paragraph(f"Scan Date: {datetime.datetime.now().strftime('%Y-%m-%d')}", normal_style))
                    elements.append(Paragraph(f"Dutch UAVG Regulations: {'Included' if st.session_state.include_dutch else 'Excluded'}", normal_style))
                    elements.append(Spacer(1, 0.25*inch))
                    
                    # Compliance score
                    elements.append(Paragraph("Compliance Score", header_style))
                    score_style = ParagraphStyle(
                        name='ScoreStyle',
                        parent=styles['Heading2'],
                        fontSize=16,
                        textColor=colors.green if compliance_score >= 80 else 
                                 (colors.orange if compliance_score >= 60 else colors.red),
                        spaceBefore=6,
                        spaceAfter=12
                    )
                    elements.append(Paragraph(f"{compliance_score}%", score_style))
                    elements.append(Spacer(1, 0.25*inch))
                    
                    # Risk summary
                    elements.append(Paragraph("Risk Summary", header_style))
                    
                    risk_data = [
                        ["Risk Level", "Count"],
                        ["High Risk", str(high_risk)],
                        ["Medium Risk", str(medium_risk)],
                        ["Low Risk", str(low_risk)],
                        ["Total Findings", str(total_findings)]
                    ]
                    
                    risk_table = Table(risk_data, colWidths=[2*inch, 1*inch])
                    risk_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (1, 0), colors.navy),
                        ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
                        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (1, 0), 8),
                        ('BACKGROUND', (0, 1), (0, 1), colors.lightcoral),
                        ('BACKGROUND', (0, 2), (0, 2), colors.lightyellow),
                        ('BACKGROUND', (0, 3), (0, 3), colors.lightgreen),
                        ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
                        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
                    ]))
                    
                    elements.append(risk_table)
                    elements.append(Spacer(1, 0.25*inch))
                    
                    # Principle-specific compliance scores
                    elements.append(Paragraph("GDPR Principle Compliance", header_style))
                    
                    principle_data = [["GDPR Principle", "Score"]]
                    for principle, score in principle_scores.items():
                        principle_data.append([principle, f"{score}%"])
                    
                    principle_table = Table(principle_data, colWidths=[4*inch, 1*inch])
                    principle_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (1, 0), colors.navy),
                        ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
                        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (1, 0), 8),
                        ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
                        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
                    ]))
                    
                    elements.append(principle_table)
                    elements.append(Spacer(1, 0.25*inch))
                    
                    # Findings
                    elements.append(Paragraph("Detailed Findings", header_style))
                    
                    # Add findings by principle
                    for principle, principle_findings in findings_by_principle.items():
                        principle_style = ParagraphStyle(
                            name='PrincipleStyle',
                            parent=styles['Heading3'],
                            fontSize=12,
                            textColor=colors.darkblue,
                            spaceBefore=6,
                            spaceAfter=6
                        )
                        elements.append(Paragraph(principle, principle_style))
                        
                        for finding in principle_findings:
                            severity = finding.get("severity", "unknown")
                            severity_color = {
                                "high": colors.red,
                                "medium": colors.orange,
                                "low": colors.green
                            }.get(severity, colors.gray)
                            
                            finding_title_style = ParagraphStyle(
                                name='FindingTitleStyle',
                                parent=styles['Heading4'],
                                fontSize=10,
                                textColor=severity_color,
                                spaceBefore=4,
                                spaceAfter=4
                            )
                            
                            elements.append(Paragraph(
                                f"{finding.get('id', '')}: {finding.get('title', '')} ({severity.upper()})",
                                finding_title_style
                            ))
                            
                            elements.append(Paragraph(f"Description: {finding.get('description', '')}", normal_style))
                            elements.append(Paragraph(f"Location: {finding.get('location', '')}", normal_style))
                            elements.append(Paragraph(f"Regulation: {finding.get('article', '')}", normal_style))
                            elements.append(Spacer(1, 0.1*inch))
                    
                    # Certification footer
                    elements.append(Spacer(1, 0.5*inch))
                    elements.append(Paragraph("DataGuardian Pro Certification", header_style))
                    elements.append(Paragraph(
                        "This report was generated using DataGuardian Pro GDPR Compliance Scanner. "
                        "The findings represent potential GDPR compliance issues identified during automated scanning "
                        "and should be reviewed by your organization's data protection officer or legal team.",
                        normal_style
                    ))
                    
                    # Build PDF
                    doc.build(elements)
                    buffer.seek(0)
                    return buffer
                
                # Generate PDF on button click
                if st.button("Generate PDF Report"):
                    with st.spinner("Generating PDF report..."):
                        pdf_buffer = generate_gdpr_pdf_report()
                        
                        # Show success message
                        st.success("GDPR compliance report successfully generated!")
                        
                        # Provide download option
                        st.download_button(
                            label="Download PDF Report",
                            data=pdf_buffer,
                            file_name=f"gdpr_report_{datetime.datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf"
                        )
        else:
            # Default content when no scan has been run
            st.markdown("""
            <div class='scanner-box'>
                <h3>GDPR Scanner</h3>
                <p>Enter a repository URL and click "Run GDPR Scan" to start analyzing your code for GDPR compliance issues.</p>
                <p>This scanner performs a comprehensive assessment based on:</p>
                <ul>
                    <li>All 7 core GDPR principles</li>
                    <li>Optional Dutch-specific UAVG requirements</li>
                    <li>PII detection and handling</li>
                    <li>Data protection measures</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### How It Works")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                **Step 1: Configuration**
                - Enter repository URL
                - Set scan depth
                - Enable Dutch UAVG regulations (if needed)
                """)
            
            with col2:
                st.markdown("""
                **Step 2: Scanning**
                - Scanner analyzes your repository
                - Checks for GDPR compliance issues
                - Evaluates all 7 core principles
                """)
            
            with col3:
                st.markdown("""
                **Step 3: Results & Reporting**
                - Review detailed findings
                - See overall compliance score
                - Generate comprehensive PDF report
                """)


# SOC2 Scanner page
def show_soc2_scanner():
    st.header("SOC2 Scanner")
    st.markdown("Scan your repositories for SOC2 compliance, focusing on the Trust Services Criteria")
    
    # Placeholder content for SOC2 scanner
    st.info("SOC2 Scanner is available in the full application")


# PCI DSS Scanner page
def show_pcidss_scanner():
    st.header("PCI DSS Scanner")
    st.markdown("Scan your code for PCI DSS compliance, focusing on cardholder data protection")
    
    # Placeholder content for PCI DSS scanner
    st.info("PCI DSS Scanner is available in the full application")


# EU AI Act Analyzer page
def show_eu_ai_act_analyzer():
    st.header("EU AI Act Analyzer")
    st.markdown("Evaluate your AI systems for compliance with the EU Artificial Intelligence Act (2025)")
    
    # Placeholder content for EU AI Act analyzer
    st.info("EU AI Act Analyzer is available in the full application")


# Settings page
def show_settings():
    st.header("Settings")
    
    # Tabs for different settings categories
    settings_tabs = st.tabs(["General", "Scanners", "Reports", "API Keys"])
    
    with settings_tabs[0]:
        st.subheader("General Settings")
        st.text_input("Organization Name", value="Your Organization")
        st.selectbox("Default Language", ["English", "Dutch", "German", "French"])
        st.checkbox("Enable Email Notifications", value=True)
    
    with settings_tabs[1]:
        st.subheader("Scanner Settings")
        st.checkbox("Enable Dutch UAVG Regulations by Default", value=True)
        st.checkbox("Include Git History in Scans", value=True)
        st.number_input("Max Files to Scan (0 = unlimited)", value=500, min_value=0)
    
    with settings_tabs[2]:
        st.subheader("Report Settings")
        st.selectbox("Default Report Format", ["PDF", "HTML", "JSON"])
        st.checkbox("Include Organization Logo in Reports", value=True)
        st.text_input("Default Report Footer")
    
    with settings_tabs[3]:
        st.subheader("API Keys")
        st.text_input("GitHub API Key", type="password")
        st.text_input("GitLab API Key", type="password")
        st.text_input("Azure DevOps API Key", type="password")
        
    # Save settings button
    if st.button("Save Settings"):
        st.success("Settings saved successfully!")


# Run the main application
if __name__ == "__main__":
    main()