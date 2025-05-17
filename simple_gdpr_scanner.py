"""
Simple GDPR Scanner

A focused GDPR code scanner following the DataGuardian Pro architecture
with key components and modular design for enterprise compliance.
"""

import streamlit as st
import pandas as pd
import json
import time
import uuid
import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Page configuration
st.set_page_config(
    page_title="GDPR Scanner", 
    page_icon="🔒",
    layout="wide"
)

# Application header
st.markdown("""
<div style="background-color: #1E3A8A; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
    <h1 style="color: white; margin: 0;">GDPR Scanner</h1>
    <p style="color: #BDD7FD; margin: 0;">DataGuardian Pro Compliance Platform</p>
</div>
""", unsafe_allow_html=True)

# Simple layout
col1, col2 = st.columns([1, 2])

with col1:
    # Repository input form
    st.markdown("### Scan Settings")
    
    repo_url = st.text_input(
        "Repository URL",
        value="https://github.com/example/repository"
    )
    
    scan_depth = st.radio(
        "Scan Depth",
        options=["Basic", "Standard", "Deep"]
    )
    
    organization_name = st.text_input(
        "Organization Name", 
        value="Your Organization"
    )
    
    # Run scan button
    run_scan = st.button("Run GDPR Scan", type="primary")

# Main scanning logic
if run_scan:
    with col2:
        with st.spinner("Running GDPR scan..."):
            # Display progress
            progress = st.progress(0)
            status = st.empty()
            
            # Simulate scanning process
            principles = [
                "Lawfulness, Fairness, Transparency",
                "Purpose Limitation",
                "Data Minimization",
                "Accuracy",
                "Storage Limitation",
                "Integrity and Confidentiality",
                "Accountability"
            ]
            
            for i, principle in enumerate(principles):
                # Update progress
                percent = int((i + 1) / len(principles) * 100)
                progress.progress(percent)
                status.write(f"Scanning for {principle}...")
                time.sleep(0.5)  # Simulate processing time
            
            # Mark scan as complete
            progress.empty()
            status.empty()
            st.success("Scan completed successfully!")
        
        # Sample findings - real implementation would use TruffleHog/Semgrep
        findings = [
            {
                "id": "LFT-001",
                "principle": "Lawfulness, Fairness, Transparency",
                "severity": "high",
                "title": "Missing Explicit Consent",
                "description": "User registration does not include explicit consent options",
                "location": "auth/signup.py:42-57",
                "article": "GDPR Art. 6, UAVG Art. 8" 
            },
            {
                "id": "PL-001",
                "principle": "Purpose Limitation",
                "severity": "high", 
                "title": "Multiple Undocumented Purposes",
                "description": "User data used for analytics without consent", 
                "location": "analytics/tracking.py:78-92",
                "article": "GDPR Art. 5-1b"
            },
            {
                "id": "DM-001",
                "principle": "Data Minimization",
                "severity": "medium",
                "title": "Excessive Data Collection",
                "description": "Registration form collects unnecessary personal details",
                "location": "models/user.py:15-28",
                "article": "GDPR Art. 5-1c" 
            },
            {
                "id": "NL-001",
                "principle": "Dutch-Specific Requirements",
                "severity": "high",
                "title": "Improper BSN Storage",
                "description": "Dutch Citizen Service Numbers stored without proper legal basis",
                "location": "models/dutch_user.py:28-36",
                "article": "UAVG Art. 46, GDPR Art. 9"
            }
        ]
        
        # Calculate metrics
        high_risk = sum(1 for f in findings if f.get("severity") == "high")
        medium_risk = sum(1 for f in findings if f.get("severity") == "medium")
        low_risk = sum(1 for f in findings if f.get("severity") == "low")
        total_findings = len(findings)
        
        # Calculate compliance score
        compliance_score = max(0, 100 - (high_risk * 7) - (medium_risk * 3) - (low_risk * 1))
        
        # Display summary
        st.markdown("### Compliance Summary")
        
        # Display compliance score with color
        score_color = "green" if compliance_score >= 80 else ("orange" if compliance_score >= 60 else "red")
        st.markdown(f"""
        <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;'>
            <h1 style='color: {score_color}; margin: 0;'>{compliance_score}%</h1>
            <p>Overall Compliance</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Risk metrics
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("High Risk", high_risk)
        with c2:
            st.metric("Medium Risk", medium_risk)
        with c3:
            st.metric("Low Risk", low_risk)
        
        # Show findings
        st.markdown("### Detailed Findings")
        
        # Group findings by principle
        findings_by_principle = {}
        for f in findings:
            principle = f.get("principle", "Other")
            if principle not in findings_by_principle:
                findings_by_principle[principle] = []
            findings_by_principle[principle].append(f)
        
        # Show each finding
        for principle, principle_findings in findings_by_principle.items():
            st.markdown(f"#### {principle}")
            
            for finding in principle_findings:
                severity = finding.get("severity", "unknown")
                severity_color = {"high": "red", "medium": "orange", "low": "green"}.get(severity, "gray")
                
                with st.expander(f"{finding.get('id')}: {finding.get('title')}"):
                    st.markdown(f"**Severity:** <span style='color: {severity_color};'>{severity.upper()}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Description:** {finding.get('description')}")
                    st.markdown(f"**Location:** {finding.get('location')}")
                    st.markdown(f"**Regulation:** {finding.get('article')}")
        
        # PDF Report option
        st.markdown("### PDF Report")
        
        if st.button("Generate PDF Report"):
            # Simple PDF generation function
            def generate_pdf():
                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=letter)
                styles = getSampleStyleSheet()
                
                # Add content
                elements = []
                
                # Title
                title_style = ParagraphStyle(
                    name='Title',
                    parent=styles['Heading1'],
                    fontSize=20,
                    textColor=colors.navy
                )
                elements.append(Paragraph("GDPR Compliance Report", title_style))
                elements.append(Spacer(1, 0.25*inch))
                
                # Details
                elements.append(Paragraph(f"Organization: {organization_name}", styles["Normal"]))
                elements.append(Paragraph(f"Repository: {repo_url}", styles["Normal"]))
                elements.append(Paragraph(f"Scan Date: {datetime.datetime.now().strftime('%Y-%m-%d')}", styles["Normal"]))
                elements.append(Spacer(1, 0.25*inch))
                
                # Summary
                elements.append(Paragraph("Compliance Summary", styles["Heading2"]))
                elements.append(Spacer(1, 0.1*inch))
                
                # Summary table
                summary_data = [
                    ["Metric", "Value"],
                    ["Compliance Score", f"{compliance_score}%"],
                    ["High Risk Issues", str(high_risk)],
                    ["Medium Risk Issues", str(medium_risk)],
                    ["Low Risk Issues", str(low_risk)],
                    ["Total Findings", str(total_findings)]
                ]
                
                summary_table = Table(summary_data, colWidths=[2.5*inch, 1.5*inch])
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (1, 0), colors.navy),
                    ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
                    ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
                    ('ALIGN', (1, 1), (1, -1), 'CENTER'),
                ]))
                
                elements.append(summary_table)
                elements.append(Spacer(1, 0.25*inch))
                
                # Findings
                elements.append(Paragraph("Detailed Findings", styles["Heading2"]))
                elements.append(Spacer(1, 0.1*inch))
                
                # Add each finding
                for principle, principle_findings in findings_by_principle.items():
                    elements.append(Paragraph(principle, styles["Heading3"]))
                    elements.append(Spacer(1, 0.1*inch))
                    
                    for finding in principle_findings:
                        severity = finding.get("severity", "unknown")
                        severity_color = {
                            "high": colors.red,
                            "medium": colors.orange,
                            "low": colors.green
                        }.get(severity, colors.gray)
                        
                        # Finding title with severity
                        finding_title = ParagraphStyle(
                            name='FindingTitle',
                            parent=styles['Heading4'],
                            fontSize=10,
                            textColor=severity_color
                        )
                        
                        elements.append(Paragraph(
                            f"{finding.get('id')}: {finding.get('title')} ({severity.upper()})",
                            finding_title
                        ))
                        
                        # Finding details
                        elements.append(Paragraph(f"Description: {finding.get('description')}", styles["Normal"]))
                        elements.append(Paragraph(f"Location: {finding.get('location')}", styles["Normal"]))
                        elements.append(Paragraph(f"Regulation: {finding.get('article')}", styles["Normal"]))
                        elements.append(Spacer(1, 0.1*inch))
                
                # Build PDF
                doc.build(elements)
                buffer.seek(0)
                
                return buffer
            
            # Create PDF and provide download
            with st.spinner("Generating PDF report..."):
                pdf_buffer = generate_pdf()
                
                st.success("PDF report generated successfully!")
                
                st.download_button(
                    label="Download PDF Report",
                    data=pdf_buffer,
                    file_name=f"gdpr_report_{datetime.datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )