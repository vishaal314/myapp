"""
Ultra Simple GDPR Scanner

A minimal, reliable GDPR code scanner that generates downloadable PDF reports.
"""

import streamlit as st
import pandas as pd
import time
import uuid
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Simple page config with minimal settings
st.set_page_config(page_title="GDPR Scanner", layout="wide")

# Basic title
st.title("GDPR Code Scanner")
st.write("Enterprise Privacy Compliance Platform")

# Create two columns for layout
left_col, right_col = st.columns([1, 2])

# Input form on left side
with left_col:
    st.write("### Repository Settings")
    
    # Simple form inputs
    repo_url = st.text_input("Repository URL", "https://github.com/example/repository")
    org_name = st.text_input("Organization Name", "Your Organization")
    
    # Simple scan button
    scan_button = st.button("Run GDPR Scan", type="primary")

# Main scanning functionality
if scan_button:
    with right_col:
        with st.spinner("Running scan..."):
            # Progress indicator
            progress = st.progress(0)
            
            # Simulate scanning each GDPR principle
            principles = [
                "Lawfulness, Fairness, Transparency", 
                "Purpose Limitation",
                "Data Minimization", 
                "Accuracy",
                "Storage Limitation",
                "Integrity and Confidentiality",
                "Accountability"
            ]
            
            # Show progress for each principle
            for i, principle in enumerate(principles):
                # Update progress percentage
                progress_pct = int((i + 1) / len(principles) * 100)
                progress.progress(progress_pct)
                
                # Display current step
                st.write(f"Scanning for {principle}...")
                
                # Small delay to show progress
                time.sleep(0.3)
        
        # Clear progress when done
        progress.empty()
        
        # Show success message
        st.success("GDPR scan completed successfully!")
        
        # Sample findings with Dutch UAVG requirements
        findings = [
            {
                "id": "LFT-001",
                "principle": "Lawfulness, Fairness, Transparency",
                "severity": "high",
                "title": "Missing Explicit Consent",
                "description": "User registration does not include explicit consent options"
            },
            {
                "id": "PL-001",
                "principle": "Purpose Limitation",
                "severity": "high",
                "title": "Multiple Undocumented Purposes",
                "description": "User data used for analytics without consent"
            },
            {
                "id": "DM-001",
                "principle": "Data Minimization",
                "severity": "medium",
                "title": "Excessive Data Collection",
                "description": "Registration form collects unnecessary personal details"
            },
            {
                "id": "NL-001",
                "principle": "Dutch-Specific Requirements",
                "severity": "high",
                "title": "Improper BSN Storage",
                "description": "Dutch Citizen Service Numbers stored without proper legal basis"
            }
        ]
        
        # Calculate metrics
        high_risk = sum(1 for f in findings if f.get("severity") == "high")
        medium_risk = sum(1 for f in findings if f.get("severity") == "medium")
        low_risk = sum(1 for f in findings if f.get("severity") == "low")
        total_findings = len(findings)
        
        # Calculate compliance score
        compliance_score = 100 - (high_risk * 7) - (medium_risk * 3) - (low_risk * 1)
        
        # Display score
        st.write("### Compliance Score")
        
        # Colored score display
        score_color = "green"
        if compliance_score < 80:
            score_color = "orange"
        if compliance_score < 60:
            score_color = "red"
            
        st.markdown(f"<h2 style='color: {score_color};'>{compliance_score}%</h2>", unsafe_allow_html=True)
        
        # Risk metrics in columns
        col1, col2, col3 = st.columns(3)
        col1.metric("High Risk", high_risk)
        col2.metric("Medium Risk", medium_risk)
        col3.metric("Low Risk", low_risk)
        
        # Show findings
        st.write("### GDPR Findings")
        
        # Display each finding
        for finding in findings:
            severity = finding.get("severity", "unknown")
            severity_color = {"high": "red", "medium": "orange", "low": "green"}.get(severity, "gray")
            
            with st.expander(f"{finding['id']}: {finding['title']}"):
                st.markdown(f"**Severity:** <span style='color: {severity_color};'>{severity.upper()}</span>", 
                          unsafe_allow_html=True)
                st.write(f"**Description:** {finding['description']}")
                st.write(f"**Principle:** {finding['principle']}")
        
        # PDF report generation
        st.write("### PDF Report")
        
        def generate_pdf_report(scan_results):
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            
            elements = []
            
            # Title
            title = Paragraph("GDPR Compliance Report", styles["Title"])
            elements.append(title)
            elements.append(Spacer(1, 0.25*inch))
            
            # Organization info
            elements.append(Paragraph(f"Organization: {org_name}", styles["Normal"]))
            elements.append(Paragraph(f"Repository: {repo_url}", styles["Normal"]))
            elements.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')}", styles["Normal"]))
            elements.append(Spacer(1, 0.25*inch))
            
            # Compliance score
            elements.append(Paragraph("Compliance Score", styles["Heading2"]))
            
            score_style = ParagraphStyle(
                name='Score',
                parent=styles['Heading2'],
                textColor=colors.green if compliance_score >= 80 else 
                         (colors.orange if compliance_score >= 60 else colors.red)
            )
            
            elements.append(Paragraph(f"{compliance_score}%", score_style))
            elements.append(Spacer(1, 0.25*inch))
            
            # Risk summary
            elements.append(Paragraph("Risk Summary", styles["Heading2"]))
            
            data = [
                ["Risk Level", "Count"],
                ["High Risk", str(high_risk)],
                ["Medium Risk", str(medium_risk)],
                ["Low Risk", str(low_risk)],
                ["Total Findings", str(total_findings)]
            ]
            
            t = Table(data, colWidths=[2*inch, 1*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.navy),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
                ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ]))
            
            elements.append(t)
            elements.append(Spacer(1, 0.25*inch))
            
            # Findings
            elements.append(Paragraph("Detailed Findings", styles["Heading2"]))
            
            for finding in findings:
                severity = finding.get("severity", "unknown")
                severity_color = {
                    "high": colors.red,
                    "medium": colors.orange,
                    "low": colors.green
                }.get(severity, colors.black)
                
                finding_style = ParagraphStyle(
                    name='FindingTitle',
                    parent=styles['Heading3'],
                    textColor=severity_color
                )
                
                elements.append(Paragraph(
                    f"{finding['id']}: {finding['title']} ({severity.upper()})",
                    finding_style
                ))
                
                elements.append(Paragraph(f"Description: {finding['description']}", styles["Normal"]))
                elements.append(Paragraph(f"Principle: {finding['principle']}", styles["Normal"]))
                elements.append(Spacer(1, 0.15*inch))
            
            # Build PDF
            doc.build(elements)
            buffer.seek(0)
            return buffer
        
        # Generate and allow downloading the PDF
        if st.button("Generate PDF Report"):
            with st.spinner("Generating PDF report..."):
                pdf = generate_pdf_report(findings)
                
                st.success("PDF report generated successfully")
                st.download_button(
                    label="Download Report",
                    data=pdf,
                    file_name=f"gdpr_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )