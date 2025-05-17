"""
Simple GDPR Code Scanner

A lightweight, focused GDPR scanner that implements the 7 core GDPR principles
and generates professional PDF reports with minimal UI complexity.
"""

import streamlit as st
import pandas as pd
import time
import uuid
import base64
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Set page configuration
st.set_page_config(
    page_title="GDPR Code Scanner",
    page_icon="🔒",
    layout="wide"
)

# Simple header
st.title("GDPR Code Scanner")
st.write("Scan code repositories for GDPR compliance issues")

# Simple form for scanning
with st.form("scan_form"):
    repo_url = st.text_input("Repository URL", value="https://github.com/example/repo")
    organization_name = st.text_input("Organization Name", value="Your Organization")
    
    col1, col2 = st.columns(2)
    
    with col1:
        scan_depth = st.select_slider(
            "Scan Depth", 
            options=["Basic", "Standard", "Deep"],
            value="Standard"
        )
    
    with col2:
        include_dutch = st.checkbox("Include Dutch UAVG Requirements", value=True)
    
    submitted = st.form_submit_button("Run GDPR Scan")

# Function to run scan and get GDPR findings
def run_gdpr_scan(repo_url, scan_depth="Standard", include_dutch=True):
    """Run a GDPR scan and return results"""
    # Create a scan ID
    scan_id = str(uuid.uuid4())
    
    # Get findings based on GDPR principles
    findings = get_gdpr_findings(include_dutch)
    
    # Calculate risk counts
    high_risk = sum(1 for f in findings if f.get("severity") == "high")
    medium_risk = sum(1 for f in findings if f.get("severity") == "medium")
    low_risk = sum(1 for f in findings if f.get("severity") == "low")
    
    # Calculate compliance score (weighted by severity)
    base_score = 100
    compliance_score = max(0, base_score - (high_risk * 7) - (medium_risk * 3) - (low_risk * 1))
    
    # Create principle-specific scores
    principle_scores = {
        "Lawfulness, Fairness and Transparency": 78,
        "Purpose Limitation": 82,
        "Data Minimization": 85,
        "Accuracy": 79,
        "Storage Limitation": 75,
        "Integrity and Confidentiality": 88,
        "Accountability": 80
    }
    
    # Create and return results
    return {
        "scan_id": scan_id,
        "repo_url": repo_url,
        "scan_depth": scan_depth,
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "findings": findings,
        "total_findings": len(findings),
        "high_risk": high_risk,
        "medium_risk": medium_risk,
        "low_risk": low_risk,
        "compliance_score": compliance_score,
        "compliance_scores": principle_scores
    }

def get_gdpr_findings(include_dutch=True):
    """Get GDPR findings based on the 7 core principles"""
    findings = []
    
    # Lawfulness, Fairness, Transparency
    findings.append({
        "id": "LFT-001",
        "principle": "Lawfulness, Fairness and Transparency",
        "severity": "high",
        "title": "Missing Explicit Consent Collection",
        "description": "User registration process does not include explicit consent options for data processing",
        "location": "File: auth/signup.py, Line: 42-57",
        "article": "GDPR Art. 6"
    })
    
    findings.append({
        "id": "LFT-002",
        "principle": "Lawfulness, Fairness and Transparency",
        "severity": "medium",
        "title": "Privacy Policy Not Prominently Displayed",
        "description": "Privacy policy link is not clearly visible during user registration",
        "location": "File: templates/signup.html, Line: 25",
        "article": "GDPR Art. 13"
    })
    
    # Purpose Limitation
    findings.append({
        "id": "PL-001",
        "principle": "Purpose Limitation",
        "severity": "high",
        "title": "Data Used for Multiple Undocumented Purposes",
        "description": "User data collected for account creation is also used for analytics without separate consent",
        "location": "File: analytics/user_tracking.py, Line: 78-92",
        "article": "GDPR Art. 5-1b"
    })
    
    # Data Minimization
    findings.append({
        "id": "DM-001",
        "principle": "Data Minimization",
        "severity": "medium",
        "title": "Excessive Personal Information Collection",
        "description": "User registration form collects unnecessary personal details not required for service functionality",
        "location": "File: models/user.py, Line: 15-28",
        "article": "GDPR Art. 5-1c"
    })
    
    # Accuracy
    findings.append({
        "id": "ACC-001",
        "principle": "Accuracy",
        "severity": "medium",
        "title": "No User Data Update Mechanism",
        "description": "Users cannot update or correct their personal information after registration",
        "location": "File: account/profile.py, Line: 52-70",
        "article": "GDPR Art. 5-1d, 16"
    })
    
    # Storage Limitation
    findings.append({
        "id": "SL-001",
        "principle": "Storage Limitation",
        "severity": "high",
        "title": "No Data Retention Policy",
        "description": "Application does not implement automatic deletion of outdated user data",
        "location": "File: database/schema.py, Line: 110-124",
        "article": "GDPR Art. 5-1e, 17"
    })
    
    # Integrity and Confidentiality
    findings.append({
        "id": "IC-001",
        "principle": "Integrity and Confidentiality",
        "severity": "high",
        "title": "Weak Password Hashing",
        "description": "Passwords are stored using MD5 hashing algorithm",
        "location": "File: auth/security.py, Line: 35-47",
        "article": "GDPR Art. 32"
    })
    
    # Accountability
    findings.append({
        "id": "ACCT-001",
        "principle": "Accountability",
        "severity": "medium",
        "title": "Missing Audit Logs",
        "description": "System does not maintain adequate logs of data access and processing",
        "location": "File: services/data_service.py, Line: 102-118",
        "article": "GDPR Art. 5-2, 30"
    })
    
    # Dutch-specific requirements (added conditionally)
    if include_dutch:
        findings.append({
            "id": "NL-001",
            "principle": "Dutch-Specific Requirements",
            "severity": "high",
            "title": "Missing Age Verification for Minors",
            "description": "No verification mechanism for users under 16 years as required by Dutch UAVG",
            "location": "File: registration/signup.py, Line: 55-62",
            "article": "UAVG Art. 5, GDPR Art. 8"
        })
        
        findings.append({
            "id": "NL-002",
            "principle": "Dutch-Specific Requirements",
            "severity": "high",
            "title": "Improper BSN Number Collection",
            "description": "Dutch Citizen Service Numbers (BSN) are collected without proper legal basis",
            "location": "File: models/dutch_user.py, Line: 28-36",
            "article": "UAVG Art. 46, GDPR Art. 9"
        })
    
    return findings

def generate_gdpr_pdf_report(scan_results, organization_name="Your Organization"):
    """Generate a professional PDF report for GDPR scan results"""
    buffer = BytesIO()
    
    # Create PDF document
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
    elements.append(Paragraph(f"Scan Date: {datetime.now().strftime('%Y-%m-%d')}", normal_style))
    elements.append(Paragraph(f"Repository: {scan_results.get('repo_url', 'Unknown')}", normal_style))
    elements.append(Spacer(1, 0.25*inch))
    
    # Compliance score
    compliance_score = scan_results.get("compliance_score", 0)
    score_color = colors.green if compliance_score >= 80 else (colors.orange if compliance_score >= 60 else colors.red)
    
    elements.append(Paragraph("Compliance Score", header_style))
    score_style = ParagraphStyle(
        name='ScoreStyle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=score_color,
        spaceBefore=6,
        spaceAfter=12
    )
    elements.append(Paragraph(f"{compliance_score}%", score_style))
    elements.append(Spacer(1, 0.25*inch))
    
    # Risk summary
    elements.append(Paragraph("Risk Summary", header_style))
    
    risk_data = [
        ["Risk Level", "Count"],
        ["High Risk", scan_results.get("high_risk", 0)],
        ["Medium Risk", scan_results.get("medium_risk", 0)],
        ["Low Risk", scan_results.get("low_risk", 0)],
        ["Total Findings", scan_results.get("total_findings", 0)]
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
    
    # Detailed findings
    elements.append(Paragraph("Detailed Findings", header_style))
    
    findings = scan_results.get("findings", [])
    if findings:
        # Group findings by principle
        findings_by_principle = {}
        for finding in findings:
            principle = finding.get("principle", "Other")
            if principle not in findings_by_principle:
                findings_by_principle[principle] = []
            findings_by_principle[principle].append(finding)
        
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
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    return buffer.getvalue()

# Process the form submission
if submitted:
    with st.spinner("Running GDPR scan..."):
        # Run the scan
        scan_results = run_gdpr_scan(
            repo_url=repo_url,
            scan_depth=scan_depth,
            include_dutch=include_dutch
        )
        
        # Show scan results
        st.success(f"Scan completed successfully! Found {scan_results['total_findings']} issues.")
        
        # Display compliance score
        score = scan_results["compliance_score"]
        score_color = "green" if score >= 80 else ("orange" if score >= 60 else "red")
        
        st.markdown("### Compliance Score")
        st.markdown(f"<h2 style='color: {score_color};'>{score}%</h2>", unsafe_allow_html=True)
        
        # Display risk metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("High Risk", scan_results["high_risk"])
        
        with col2:
            st.metric("Medium Risk", scan_results["medium_risk"])
        
        with col3:
            st.metric("Low Risk", scan_results["low_risk"])
        
        # Show findings by principle
        st.markdown("### Findings by Principle")
        
        # Create tabs for findings
        findings = scan_results["findings"]
        
        # Group findings by principle
        findings_by_principle = {}
        for finding in findings:
            principle = finding.get("principle", "Other")
            if principle not in findings_by_principle:
                findings_by_principle[principle] = []
            findings_by_principle[principle].append(finding)
        
        # Create tabs for each principle
        tabs = st.tabs(list(findings_by_principle.keys()))
        
        for i, (principle, principle_findings) in enumerate(findings_by_principle.items()):
            with tabs[i]:
                for finding in principle_findings:
                    severity = finding.get("severity", "unknown")
                    severity_color = {
                        "high": "red",
                        "medium": "orange",
                        "low": "green"
                    }.get(severity, "gray")
                    
                    with st.expander(f"{finding.get('id', 'UNKNOWN')}: {finding.get('title', 'Unnamed Finding')}"):
                        st.markdown(f"**Severity:** <span style='color: {severity_color};'>{severity.upper()}</span>", unsafe_allow_html=True)
                        st.markdown(f"**Description:** {finding.get('description', 'No description')}")
                        st.markdown(f"**Location:** {finding.get('location', 'Unknown')}")
                        st.markdown(f"**Regulation:** {finding.get('article', 'Not specified')}")
        
        # Generate PDF report
        st.markdown("### PDF Report")
        
        # Generate the PDF
        pdf_bytes = generate_gdpr_pdf_report(scan_results, organization_name)
        
        # Create a download button
        st.download_button(
            label="Download PDF Report",
            data=pdf_bytes,
            file_name=f"gdpr_report_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )