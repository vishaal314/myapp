"""
Ultra-Simple GDPR Scanner

A minimal, reliable GDPR code scanner that generates downloadable PDF reports.
"""

import streamlit as st
import time
import uuid
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Basic page configuration
st.set_page_config(page_title="GDPR Scanner", page_icon="🔒")

# Simple header
st.title("GDPR Code Scanner")
st.write("Scan for GDPR compliance issues and generate reports")

# Simple form
repo_url = st.text_input("Repository URL", "https://github.com/example/repo")
organization = st.text_input("Organization Name", "Your Organization")

if st.button("Run GDPR Scan"):
    with st.spinner("Running scan..."):
        # Simulate scan with a slight delay
        time.sleep(1)
        
        # Get findings
        findings = [
            {
                "id": "LFT-001",
                "principle": "Lawfulness, Fairness and Transparency",
                "severity": "high",
                "title": "Missing Explicit Consent Collection",
                "description": "User registration process does not include explicit consent options",
                "location": "File: auth/signup.py, Line: 42-57",
                "article": "GDPR Art. 6"
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
                "description": "User registration form collects unnecessary personal details",
                "location": "File: models/user.py, Line: 15-28",
                "article": "GDPR Art. 5-1c"
            },
            {
                "id": "NL-001",
                "principle": "Dutch-Specific Requirements",
                "severity": "high",
                "title": "Missing Age Verification for Minors",
                "description": "No verification mechanism for users under 16 years",
                "location": "File: registration/signup.py, Line: 55-62",
                "article": "UAVG Art. 5, GDPR Art. 8"
            }
        ]
        
        # Calculate risk counts
        high_risk = sum(1 for f in findings if f.get("severity") == "high")
        medium_risk = sum(1 for f in findings if f.get("severity") == "medium")
        low_risk = sum(1 for f in findings if f.get("severity") == "low")
        total_findings = len(findings)
        
        # Calculate compliance score
        compliance_score = 100 - (high_risk * 7) - (medium_risk * 3) - (low_risk * 1)
        compliance_score = max(0, compliance_score)
        
        # Create scan results object
        scan_results = {
            "scan_id": str(uuid.uuid4()),
            "repo_url": repo_url,
            "organization": organization,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "findings": findings,
            "high_risk": high_risk,
            "medium_risk": medium_risk,
            "low_risk": low_risk,
            "total_findings": total_findings,
            "compliance_score": compliance_score
        }
        
        # Show results
        st.success(f"Scan completed! Found {total_findings} issues.")
        
        # Display compliance score
        st.subheader("Compliance Score")
        score_color = "green" if compliance_score >= 80 else ("orange" if compliance_score >= 60 else "red")
        st.markdown(f"<h2 style='color: {score_color};'>{compliance_score}%</h2>", unsafe_allow_html=True)
        
        # Display risk metrics
        st.subheader("Risk Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("High Risk", high_risk)
        
        with col2:
            st.metric("Medium Risk", medium_risk)
        
        with col3:
            st.metric("Low Risk", low_risk)
        
        # Display findings
        st.subheader("Findings")
        for finding in findings:
            severity = finding.get("severity", "unknown")
            severity_color = {
                "high": "red",
                "medium": "orange",
                "low": "green"
            }.get(severity, "gray")
            
            with st.expander(f"{finding['id']}: {finding['title']}"):
                st.markdown(f"**Severity:** <span style='color: {severity_color};'>{severity.upper()}</span>", unsafe_allow_html=True)
                st.markdown(f"**Description:** {finding['description']}")
                st.markdown(f"**Location:** {finding['location']}")
                st.markdown(f"**Regulation:** {finding['article']}")
        
        # Generate PDF report function
        def generate_pdf_report(scan_results):
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                name='TitleStyle',
                parent=styles['Heading1'],
                fontSize=18,
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
            
            # Create PDF elements
            elements = []
            
            # Header
            elements.append(Paragraph("GDPR Compliance Report", title_style))
            elements.append(Spacer(1, 0.25*inch))
            
            # Report metadata
            elements.append(Paragraph(f"Organization: {scan_results['organization']}", normal_style))
            elements.append(Paragraph(f"Scan Date: {scan_results['timestamp']}", normal_style))
            elements.append(Paragraph(f"Repository: {scan_results['repo_url']}", normal_style))
            elements.append(Spacer(1, 0.25*inch))
            
            # Compliance score
            score_color = colors.green
            if scan_results['compliance_score'] < 80:
                score_color = colors.orange
            if scan_results['compliance_score'] < 60:
                score_color = colors.red
                
            elements.append(Paragraph("Compliance Score", header_style))
            score_style = ParagraphStyle(
                name='ScoreStyle',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=score_color,
                spaceAfter=12
            )
            elements.append(Paragraph(f"{scan_results['compliance_score']}%", score_style))
            elements.append(Spacer(1, 0.25*inch))
            
            # Risk summary
            elements.append(Paragraph("Risk Summary", header_style))
            
            risk_data = [
                ["Risk Level", "Count"],
                ["High Risk", scan_results['high_risk']],
                ["Medium Risk", scan_results['medium_risk']],
                ["Low Risk", scan_results['low_risk']],
                ["Total Findings", scan_results['total_findings']]
            ]
            
            risk_table = Table(risk_data, colWidths=[2*inch, 1*inch])
            risk_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.navy),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
                ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (1, 0), 8),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ]))
            
            elements.append(risk_table)
            elements.append(Spacer(1, 0.25*inch))
            
            # Detailed findings
            elements.append(Paragraph("Detailed Findings", header_style))
            
            for finding in scan_results['findings']:
                severity = finding.get("severity", "unknown")
                severity_color = {
                    "high": colors.red,
                    "medium": colors.orange,
                    "low": colors.green
                }.get(severity, colors.grey)
                
                finding_style = ParagraphStyle(
                    name='FindingStyle',
                    parent=styles['Heading3'],
                    fontSize=12,
                    textColor=severity_color,
                    spaceBefore=6,
                    spaceAfter=2
                )
                
                elements.append(Paragraph(f"{finding['id']}: {finding['title']} ({severity.upper()})", finding_style))
                elements.append(Paragraph(f"Description: {finding['description']}", normal_style))
                elements.append(Paragraph(f"Location: {finding['location']}", normal_style))
                elements.append(Paragraph(f"Regulation: {finding['article']}", normal_style))
                elements.append(Spacer(1, 0.1*inch))
            
            # Build PDF
            doc.build(elements)
            buffer.seek(0)
            
            return buffer.getvalue()
        
        # Generate PDF report
        with st.spinner("Generating PDF report..."):
            pdf_bytes = generate_pdf_report(scan_results)
            
            # Create download button
            st.download_button(
                label="Download PDF Report",
                data=pdf_bytes,
                file_name=f"gdpr_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )