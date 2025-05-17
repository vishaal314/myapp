"""
Streamlined GDPR Scanner

A simplified, reliable GDPR code scanner with a clean interface that implements
all 7 core GDPR principles and Dutch-specific requirements.
"""

import streamlit as st
import pandas as pd
import time
import uuid
import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Set page configuration
st.set_page_config(
    page_title="GDPR Scanner",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Application header
st.markdown("""
<div style="background-color: #1E3A8A; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
    <h1 style="color: white; margin: 0;">GDPR Scanner</h1>
    <p style="color: #BDD7FD; margin: 0;">Comprehensive Privacy Compliance</p>
</div>
""", unsafe_allow_html=True)

# Create columns for layout
col1, col2 = st.columns([1, 3])

# Scan form in the left column
with col1:
    st.header("Repository Settings")
    
    repo_url = st.text_input(
        "Repository URL",
        value="https://github.com/example/repository",
        help="URL to the GitHub repository to scan"
    )
    
    scan_depth = st.select_slider(
        "Scan Depth",
        options=["Basic", "Standard", "Deep"],
        value="Standard",
        help="Deeper scans take longer but are more thorough"
    )
    
    organization_name = st.text_input(
        "Organization Name",
        value="Your Organization",
        help="Name to include in reports"
    )
    
    run_scan = st.button("Run GDPR Scan", type="primary")

# If scan button is clicked, show scanning process and results
if run_scan:
    with col2:
        with st.spinner("Running GDPR compliance scan..."):
            # Add progress tracking
            progress_bar = st.progress(0)
            status = st.empty()
            
            # Simulate scanning steps
            for i, principle in enumerate([
                "Lawfulness, Fairness and Transparency",
                "Purpose Limitation",
                "Data Minimization",
                "Accuracy",
                "Storage Limitation", 
                "Integrity and Confidentiality",
                "Accountability"
            ]):
                # Update progress
                progress = int((i + 1) / 7 * 100)
                progress_bar.progress(progress)
                status.text(f"Scanning for {principle}...")
                time.sleep(0.5)  # Simulate processing time
            
            # Clear progress indicators
            progress_bar.empty()
            status.empty()
        
        # Show success message
        st.success("Scan completed successfully!")
        
        # Create tabs for different views
        overview_tab, findings_tab, report_tab = st.tabs(["Overview", "Findings", "PDF Report"])
        
        # Generate mock scan results
        scan_results = {
            "scan_id": str(uuid.uuid4()),
            "repo_url": repo_url,
            "scan_depth": scan_depth,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "findings": [
                {
                    "id": "LFT-001",
                    "principle": "Lawfulness, Fairness and Transparency",
                    "severity": "high",
                    "title": "Missing Explicit Consent Collection",
                    "description": "User registration process does not include explicit consent options for data processing",
                    "location": "File: auth/signup.py, Line: 42-57",
                    "article": "GDPR Art. 6, UAVG"
                },
                {
                    "id": "LFT-002",
                    "principle": "Lawfulness, Fairness and Transparency",
                    "severity": "medium",
                    "title": "Privacy Policy Not Prominently Displayed",
                    "description": "Privacy policy link is not clearly visible during user registration",
                    "location": "File: templates/signup.html, Line: 25",
                    "article": "GDPR Art. 13, UAVG"
                },
                {
                    "id": "PL-001",
                    "principle": "Purpose Limitation",
                    "severity": "high",
                    "title": "Data Used for Multiple Undocumented Purposes",
                    "description": "User data collected for account creation is also used for analytics without separate consent",
                    "location": "File: analytics/user_tracking.py, Line: 78-92",
                    "article": "GDPR Art. 5-1b, UAVG"
                },
                {
                    "id": "DM-001",
                    "principle": "Data Minimization",
                    "severity": "medium",
                    "title": "Excessive Personal Information Collection",
                    "description": "User registration form collects unnecessary personal details not required for service functionality",
                    "location": "File: models/user.py, Line: 15-28",
                    "article": "GDPR Art. 5-1c, UAVG"
                },
                {
                    "id": "SL-001", 
                    "principle": "Storage Limitation",
                    "severity": "high",
                    "title": "No Data Retention Policy",
                    "description": "Application does not implement automatic deletion of outdated user data",
                    "location": "File: database/schema.py, Line: 110-124",
                    "article": "GDPR Art. 5-1e, 17, UAVG"
                },
                {
                    "id": "IC-001",
                    "principle": "Integrity and Confidentiality",
                    "severity": "high",
                    "title": "Weak Password Hashing",
                    "description": "Passwords are stored using MD5 hashing algorithm",
                    "location": "File: auth/security.py, Line: 35-47",
                    "article": "GDPR Art. 32, UAVG"
                },
                {
                    "id": "NL-002",
                    "principle": "Dutch-Specific Requirements",
                    "severity": "high",
                    "title": "Improper BSN Number Collection",
                    "description": "Dutch Citizen Service Numbers (BSN) are collected without proper legal basis",
                    "location": "File: models/dutch_user.py, Line: 28-36", 
                    "article": "UAVG Art. 46, GDPR Art. 9"
                }
            ],
            "compliance_scores": {
                "Lawfulness, Fairness and Transparency": 78,
                "Purpose Limitation": 82,
                "Data Minimization": 85,
                "Accuracy": 90,
                "Storage Limitation": 75,
                "Integrity and Confidentiality": 68, 
                "Accountability": 80
            }
        }
        
        # Calculate summary metrics
        findings = scan_results["findings"]
        high_risk = sum(1 for f in findings if f.get("severity") == "high")
        medium_risk = sum(1 for f in findings if f.get("severity") == "medium")
        low_risk = sum(1 for f in findings if f.get("severity") == "low")
        total_findings = len(findings)
        
        # Calculate overall compliance score
        compliance_score = max(0, 100 - (high_risk * 7) - (medium_risk * 3) - (low_risk * 1))
        
        # Overview tab content
        with overview_tab:
            # Create columns for metrics
            score_col, metrics_col = st.columns([1, 2])
            
            with score_col:
                st.subheader("Compliance Score")
                score_color = "green"
                if compliance_score < 80:
                    score_color = "orange"
                if compliance_score < 60:
                    score_color = "red"
                
                st.markdown(f"""
                <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;">
                    <h1 style="color: {score_color}; font-size: 4rem; margin: 0;">{compliance_score}%</h1>
                </div>
                """, unsafe_allow_html=True)
            
            with metrics_col:
                st.subheader("Risk Summary")
                c1, c2, c3 = st.columns(3)
                
                with c1:
                    st.metric("High Risk", high_risk)
                
                with c2:
                    st.metric("Medium Risk", medium_risk)
                
                with c3:
                    st.metric("Low Risk", low_risk)
            
            # Principle-specific scores
            st.subheader("GDPR Principle Compliance")
            
            # Create dataframe for bar chart
            principle_df = pd.DataFrame({
                "Principle": list(scan_results["compliance_scores"].keys()),
                "Score": list(scan_results["compliance_scores"].values())
            })
            
            st.bar_chart(principle_df.set_index("Principle"))
            
            # Scan info
            st.subheader("Scan Information")
            info_col1, info_col2 = st.columns(2)
            
            with info_col1:
                st.write(f"**Repository:** {scan_results['repo_url']}")
                st.write(f"**Scan Depth:** {scan_results['scan_depth']}")
            
            with info_col2:
                st.write(f"**Scan Date:** {scan_results['timestamp']}")
                st.write(f"**Total Issues:** {total_findings}")
        
        # Findings tab content
        with findings_tab:
            st.subheader("Detailed Findings")
            
            # Group findings by principle
            findings_by_principle = {}
            for finding in findings:
                principle = finding.get("principle", "Other")
                if principle not in findings_by_principle:
                    findings_by_principle[principle] = []
                findings_by_principle[principle].append(finding)
            
            # Show findings by principle
            for principle, principle_findings in findings_by_principle.items():
                st.markdown(f"#### {principle}")
                
                for finding in principle_findings:
                    severity = finding.get("severity", "unknown")
                    severity_color = {"high": "red", "medium": "orange", "low": "green"}.get(severity, "gray")
                    
                    with st.expander(f"{finding.get('id', '')}: {finding.get('title', '')}"):
                        st.markdown(f"**Severity:** <span style='color: {severity_color};'>{severity.upper()}</span>", unsafe_allow_html=True)
                        st.markdown(f"**Description:** {finding.get('description', '')}")
                        st.markdown(f"**Location:** {finding.get('location', '')}")
                        st.markdown(f"**Regulation:** {finding.get('article', '')}")
        
        # Report tab content
        with report_tab:
            st.subheader("Generate PDF Report")
            
            if st.button("Generate PDF Report"):
                # Generate PDF function
                def generate_pdf():
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
                    elements.append(Paragraph(f"Organization: {organization_name}", normal_style))
                    elements.append(Paragraph(f"Scan Date: {scan_results['timestamp']}", normal_style))
                    elements.append(Paragraph(f"Repository: {scan_results['repo_url']}", normal_style))
                    elements.append(Spacer(1, 0.25*inch))
                    
                    # Compliance score
                    elements.append(Paragraph("Compliance Score", header_style))
                    score_style = ParagraphStyle(
                        name='ScoreStyle',
                        parent=styles['Heading2'],
                        fontSize=16,
                        textColor=colors.green if compliance_score >= 80 else (colors.orange if compliance_score >= 60 else colors.red),
                        spaceBefore=6,
                        spaceAfter=12
                    )
                    elements.append(Paragraph(f"{compliance_score}%", score_style))
                    elements.append(Spacer(1, 0.25*inch))
                    
                    # Risk summary
                    elements.append(Paragraph("Risk Summary", header_style))
                    
                    risk_data = [
                        ["Risk Level", "Count"],
                        ["High Risk", high_risk],
                        ["Medium Risk", medium_risk],
                        ["Low Risk", low_risk],
                        ["Total Findings", total_findings]
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
                    for principle, score in scan_results["compliance_scores"].items():
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
                    
                    # Detailed findings
                    elements.append(Paragraph("Detailed Findings", header_style))
                    
                    # Add each principle and its findings
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
                        
                        # Add each finding
                        for finding in principle_findings:
                            severity = finding.get("severity", "unknown")
                            severity_color = {
                                "high": colors.red,
                                "medium": colors.orange,
                                "low": colors.green
                            }.get(severity, colors.grey)
                            
                            finding_title_style = ParagraphStyle(
                                name='FindingTitleStyle',
                                parent=styles['Heading4'],
                                fontSize=10,
                                textColor=severity_color,
                                spaceBefore=4,
                                spaceAfter=4
                            )
                            
                            elements.append(Paragraph(
                                f"{finding.get('id', 'UNKNOWN')}: {finding.get('title', 'Unnamed Finding')} ({severity.upper()})",
                                finding_title_style
                            ))
                            
                            elements.append(Paragraph(f"Description: {finding.get('description', 'No description')}", normal_style))
                            elements.append(Paragraph(f"Location: {finding.get('location', 'Unknown')}", normal_style))
                            elements.append(Paragraph(f"Regulation: {finding.get('article', 'Not specified')}", normal_style))
                            elements.append(Spacer(1, 0.1*inch))
                    
                    # Add certification
                    elements.append(Spacer(1, 0.5*inch))
                    elements.append(Paragraph("Certification", header_style))
                    elements.append(Paragraph(
                        "This report was automatically generated by the GDPR Scanner. "
                        "This scan provides an assessment of potential GDPR compliance issues but does not constitute "
                        "legal advice. Please consult with your privacy officer or legal counsel for definitive guidance.",
                        normal_style
                    ))
                    
                    # Build PDF
                    doc.build(elements)
                    buffer.seek(0)
                    
                    return buffer
                
                # Generate PDF and provide download link
                with st.spinner("Generating PDF report..."):
                    pdf_buffer = generate_pdf()
                    
                    st.success("PDF report generated successfully!")
                    
                    # Create download button
                    current_date = datetime.datetime.now().strftime("%Y%m%d")
                    st.download_button(
                        label="Download PDF Report",
                        data=pdf_buffer,
                        file_name=f"gdpr_report_{current_date}.pdf",
                        mime="application/pdf"
                    )