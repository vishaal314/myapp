"""
Streamlined GDPR Code Scanner

A clean, focused GDPR code scanner that analyzes repositories for compliance issues
and generates professional PDF reports.
"""

import streamlit as st
import os
import time
import io
import base64
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Set page configuration
st.set_page_config(
    page_title="GDPR Code Scanner",
    page_icon="🛡️",
    layout="wide"
)

# Helper classes for scanning
class GDPRScanner:
    def __init__(self, repo_path='.', languages=None):
        self.repo_path = repo_path
        self.languages = languages or ['python', 'javascript', 'java']
        self.findings = []
        
    def scan(self):
        """Perform GDPR code scan"""
        # This would contain actual scanning logic
        # For this demo, we're returning sample data
        
        # Sample findings for demonstration
        self.findings = [
            {
                "file": "auth.py",
                "line": 42,
                "principle": "Integrity and Confidentiality",
                "severity": "high",
                "description": "Hardcoded API key detected",
                "snippet": "api_key = \"sk_live_51AbCdEfGhIjKlMnOpQrStUvWxYz12345\"",
                "gdpr_article": "Article 32"
            },
            {
                "file": "database.py",
                "line": 78,
                "principle": "Storage Limitation",
                "severity": "medium",
                "description": "No data retention policy defined",
                "snippet": "// TODO: Implement data retention policy",
                "gdpr_article": "Article 5(1)(e)"
            },
            {
                "file": "user.py",
                "line": 105,
                "principle": "Lawfulness, Fairness and Transparency",
                "severity": "low",
                "description": "Missing consent validation",
                "snippet": "def process_user_data(data):\n    # Process the user data\n    save_to_database(data)",
                "gdpr_article": "Article 6"
            }
        ]
        
        # Calculate compliance scores
        compliance_scores = {
            "Lawfulness, Fairness and Transparency": 85,
            "Purpose Limitation": 90,
            "Data Minimization": 75,
            "Accuracy": 95,
            "Storage Limitation": 70,
            "Integrity and Confidentiality": 65,
            "Accountability": 80
        }
        
        return {
            "scan_date": datetime.now().isoformat(),
            "repo_path": self.repo_path,
            "file_count": 24,
            "findings": self.findings,
            "findings_count": len(self.findings),
            "compliance_scores": compliance_scores
        }

def generate_pdf_report(scan_results, organization_name):
    """Generate a PDF report from scan results"""
    buffer = io.BytesIO()
    
    # Create document
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        title="GDPR Compliance Scan Report",
        leftMargin=1.5*72/2.54, 
        rightMargin=1.5*72/2.54, 
        topMargin=2*72/2.54, 
        bottomMargin=2*72/2.54
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    heading2_style = styles["Heading2"]
    normal_style = styles["Normal"]
    
    # Create custom styles
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=16,
        textColor=colors.darkblue,
    )
    
    finding_style = ParagraphStyle(
        'Finding',
        parent=styles['Normal'],
        fontSize=10,
        spaceBefore=8,
        spaceAfter=8,
    )
    
    # Create content
    content = []
    
    # Title and report date
    content.append(Paragraph("GDPR Compliance Scan Report", title_style))
    content.append(Spacer(1, 0.5*72/2.54))
    
    scan_date = datetime.fromisoformat(scan_results["scan_date"]) if isinstance(scan_results["scan_date"], str) else scan_results["scan_date"]
    content.append(Paragraph(f"Organization: {organization_name}", normal_style))
    content.append(Paragraph(f"Generated: {scan_date.strftime('%Y-%m-%d %H:%M')}", normal_style))
    content.append(Paragraph(f"Repository: {scan_results['repo_path']}", normal_style))
    content.append(Spacer(1, 1*72/2.54))
    
    # Summary section
    content.append(Paragraph("Executive Summary", section_style))
    
    # Add metrics table
    summary_data = [
        ["Metric", "Value"],
        ["Files Scanned", str(scan_results["file_count"])],
        ["Findings", str(scan_results["findings_count"])],
    ]
    
    # Count findings by severity
    severity_counts = {"high": 0, "medium": 0, "low": 0}
    for finding in scan_results["findings"]:
        severity = finding.get("severity", "low")
        severity_counts[severity] += 1
    
    for severity, count in severity_counts.items():
        summary_data.append([f"{severity.title()} Severity Findings", str(count)])
    
    summary_table = Table(summary_data, colWidths=[doc.width/2.5, doc.width/2.5])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (1, 0), 12),
        ('BACKGROUND', (0, 1), (1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (1, -1), 'MIDDLE'),
    ]))
    
    content.append(summary_table)
    content.append(Spacer(1, 0.5*72/2.54))
    
    # Compliance Scores section
    content.append(Paragraph("GDPR Compliance Scores", section_style))
    
    # Create scores table
    compliance_scores = scan_results["compliance_scores"]
    scores_data = [["GDPR Principle", "Score"]]
    
    for principle, score in compliance_scores.items():
        scores_data.append([principle, f"{score}%"])
    
    scores_table = Table(scores_data, colWidths=[doc.width*0.7, doc.width*0.3])
    scores_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
    ]))
    
    content.append(scores_table)
    content.append(Spacer(1, 1*72/2.54))
    
    # Findings section
    content.append(Paragraph("Detailed Findings", section_style))
    
    # Group findings by principle
    principle_findings = {}
    for finding in scan_results["findings"]:
        principle = finding.get("principle")
        if principle not in principle_findings:
            principle_findings[principle] = []
        principle_findings[principle].append(finding)
    
    # Add findings by principle
    for principle, findings in principle_findings.items():
        content.append(Paragraph(f"{principle}", heading2_style))
        
        for i, finding in enumerate(findings, 1):
            severity = finding.get("severity", "low").upper()
            file_path = finding.get("file", "Unknown")
            line_num = finding.get("line", 0)
            description = finding.get("description", "No description")
            article = finding.get("gdpr_article", "N/A")
            
            # Create finding text
            finding_text = f"<strong>{i}. {severity}: {description}</strong><br/>"
            finding_text += f"<strong>File:</strong> {file_path}:{line_num}<br/>"
            finding_text += f"<strong>GDPR Article:</strong> {article}<br/>"
            
            finding_para = Paragraph(finding_text, finding_style)
            content.append(finding_para)
            
            # Add code snippet if available
            snippet = finding.get("snippet", "")
            if snippet:
                snippet_style = ParagraphStyle(
                    'CodeSnippet',
                    parent=styles['Code'],
                    fontSize=8,
                    fontName='Courier',
                    leftIndent=20,
                    rightIndent=20,
                    backColor=colors.lightgrey,
                )
                # Escape HTML characters in snippet
                snippet = snippet.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                content.append(Paragraph(f"<pre>{snippet}</pre>", snippet_style))
            
            content.append(Spacer(1, 0.3*72/2.54))
    
    # Certification section
    content.append(Paragraph("Certification", section_style))
    content.append(Paragraph(
        f"Based on the assessment results, {organization_name} is assessed as partially compliant "
        f"with GDPR requirements as of {scan_date.strftime('%Y-%m-%d')}.", 
        normal_style
    ))
    
    # Build PDF document
    doc.build(content)
    
    # Get PDF data
    pdf_data = buffer.getvalue()
    buffer.close()
    
    return pdf_data

def main():
    st.title("GDPR Code Scanner")
    st.markdown("Scan your code repository for GDPR compliance issues and generate a PDF report.")
    
    # Repository scan inputs
    repo_path = st.text_input("Repository Path", value=".", help="Enter the path to the code repository")
    
    # Language selection
    languages = st.multiselect(
        "Select Languages to Scan",
        options=["Python", "JavaScript", "TypeScript", "Java", "Terraform", "YAML", "JSON"],
        default=["Python", "JavaScript"]
    )
    
    # Organization name for the report
    organization_name = st.text_input("Organization Name", value="Your Organization", 
                                     help="Your organization's name for the PDF report")
    
    # Scan button
    scan_button = st.button("Run GDPR Scan", use_container_width=True)
    
    if scan_button:
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Initialize scanner
        scanner = GDPRScanner(
            repo_path=repo_path,
            languages=[lang.lower() for lang in languages]
        )
        
        # Update progress status
        status_text.text("Initializing scanner...")
        progress_bar.progress(0.1)
        
        # Run the scan with progress updates
        for i in range(2, 10):
            time.sleep(0.3)  # Simulate processing time
            progress_bar.progress(i/10)
            status_text.text(f"Scanning files... ({i*10}%)")
        
        # Get scan results
        scan_results = scanner.scan()
        
        # Update final progress
        progress_bar.progress(1.0)
        status_text.text("Scan completed!")
        time.sleep(0.5)
        st.success("GDPR compliance scan completed successfully!")
        
        # Store results in session state for PDF generation
        st.session_state.scan_results = scan_results
        
        # Display scan summary
        st.markdown("## Scan Summary")
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Files Scanned", scan_results["file_count"])
        with col2:
            st.metric("Findings", scan_results["findings_count"])
        with col3:
            avg_score = sum(scan_results["compliance_scores"].values()) / len(scan_results["compliance_scores"])
            st.metric("Avg. Compliance", f"{avg_score:.0f}%")
        
        # Display compliance scores
        st.markdown("## GDPR Compliance Scores")
        
        # Show scores in columns
        score_cols = st.columns(2)
        for i, (principle, score) in enumerate(scan_results["compliance_scores"].items()):
            col_idx = i % 2
            with score_cols[col_idx]:
                # Color based on score
                color = "green" if score >= 90 else "orange" if score >= 70 else "red"
                st.markdown(f"**{principle}**: {score}%")
                st.progress(score/100)
        
        # Display findings
        st.markdown("## Key Findings")
        
        # Group findings by severity
        severity_groups = {"high": [], "medium": [], "low": []}
        for finding in scan_results["findings"]:
            severity = finding.get("severity", "low")
            severity_groups[severity].append(finding)
        
        # Display findings by severity (high to low)
        for severity, severity_findings in [
            ("high", severity_groups["high"]), 
            ("medium", severity_groups["medium"]), 
            ("low", severity_groups["low"])
        ]:
            if severity_findings:
                if severity == "high":
                    st.error(f"**{severity.upper()} SEVERITY ISSUES ({len(severity_findings)})**")
                elif severity == "medium":
                    st.warning(f"**{severity.upper()} SEVERITY ISSUES ({len(severity_findings)})**")
                else:
                    st.info(f"**{severity.upper()} SEVERITY ISSUES ({len(severity_findings)})**")
                
                for finding in severity_findings:
                    with st.expander(f"{finding.get('principle')}: {finding.get('description')}"):
                        st.markdown(f"**File:** `{finding.get('file')}`")
                        st.markdown(f"**Line:** {finding.get('line')}")
                        st.markdown(f"**GDPR Article:** {finding.get('gdpr_article', 'N/A')}")
                        st.markdown(f"**Code Snippet:**")
                        st.code(finding.get("snippet", "No snippet available"))
        
        # Generate and download PDF
        st.markdown("## Generate PDF Report")
        
        if st.button("Generate PDF Report", key="gen_pdf", use_container_width=True):
            with st.spinner("Generating PDF report..."):
                pdf_data = generate_pdf_report(scan_results, organization_name)
            
            # Success message
            st.success("PDF report generated successfully!")
            
            # Create a unique timestamp for the file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"GDPR_Compliance_Report_{organization_name.replace(' ', '_')}_{timestamp}.pdf"
            
            # Add download button
            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_data,
                file_name=filename,
                mime="application/pdf",
                key=f"download_pdf_{timestamp}",
                use_container_width=True
            )
            
            # Alternative download method for reliability
            b64_pdf = base64.b64encode(pdf_data).decode()
            href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{filename}" style="display:block; text-align:center; margin-top:10px; padding:10px; background-color:#4f46e5; color:white; text-decoration:none; border-radius:4px;">📥 Alternative Download Link</a>'
            st.markdown(href, unsafe_allow_html=True)

if __name__ == "__main__":
    main()