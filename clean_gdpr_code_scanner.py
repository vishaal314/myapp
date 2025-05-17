"""
Clean GDPR Code Scanner

A focused, streamlined GDPR code scanner that analyzes repositories
for compliance issues and generates professional PDF reports.
"""

import streamlit as st
import os
import json
import time
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
import base64

# Set page configuration
st.set_page_config(
    page_title="GDPR Code Scanner",
    page_icon="🛡️",
    layout="wide"
)

# Define scanner class
class GDPRScanner:
    def __init__(self, repo_path='.', languages=None):
        self.repo_path = repo_path
        self.languages = languages or ['python', 'javascript', 'java', 'typescript']
        self.findings = []
        
    def scan(self):
        """Perform GDPR code scan"""
        start_time = datetime.now()
        
        # Scan directories
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                # Skip hidden files and non-relevant file types
                if file.startswith('.') or not self._should_scan_file(file):
                    continue
                    
                file_path = os.path.join(root, file)
                try:
                    self._scan_file(file_path)
                except Exception as e:
                    print(f"Error scanning {file_path}: {e}")
        
        # Prepare scan results
        scan_duration = (datetime.now() - start_time).total_seconds()
        
        # Calculate compliance scores
        compliance_scores = self._calculate_compliance_scores()
        
        return {
            "scan_date": datetime.now().isoformat(),
            "repo_path": self.repo_path,
            "languages": self.languages,
            "scan_duration": scan_duration,
            "file_count": len(set(finding["file"] for finding in self.findings)),
            "findings": self.findings,
            "findings_count": len(self.findings),
            "compliance_scores": compliance_scores
        }
    
    def _should_scan_file(self, filename):
        """Check if a file should be scanned based on its extension"""
        ext = os.path.splitext(filename.lower())[1]
        extensions_map = {
            'python': ['.py', '.pyw'],
            'javascript': ['.js', '.jsx', '.mjs'],
            'typescript': ['.ts', '.tsx'],
            'java': ['.java'],
            'terraform': ['.tf'],
            'yaml': ['.yml', '.yaml'],
            'json': ['.json'],
        }
        
        # Check if extension is scannable
        for lang, exts in extensions_map.items():
            if lang in self.languages and ext in exts:
                return True
        
        return False
    
    def _scan_file(self, file_path):
        """Scan a single file for GDPR compliance issues"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                # Scan for different GDPR principle issues
                self._scan_for_lawfulness(file_path, lines, content)
                self._scan_for_purpose_limitation(file_path, lines, content)
                self._scan_for_data_minimization(file_path, lines, content)
                self._scan_for_accuracy(file_path, lines, content)
                self._scan_for_storage_limitation(file_path, lines, content)
                self._scan_for_integrity_confidentiality(file_path, lines, content)
                self._scan_for_accountability(file_path, lines, content)
        except Exception as e:
            # Log error but continue scanning
            self.findings.append({
                "file": file_path,
                "line": 0,
                "principle": "Error",
                "severity": "low",
                "description": f"Error scanning file: {str(e)}",
                "snippet": "",
                "gdpr_article": "N/A"
            })
    
    def _scan_for_lawfulness(self, file_path, lines, content):
        """Scan for lawfulness, fairness and transparency issues"""
        patterns = [
            (r'(?i)consent.*not.*valid', "Invalid consent handling", "high", "Article 6"),
            (r'(?i)process.*without.*consent', "Processing without consent", "high", "Article 6"),
            (r'(?i)bypass.*consent', "Consent bypass", "high", "Article 6"),
        ]
        self._check_patterns(file_path, lines, "Lawfulness, Fairness and Transparency", patterns)
    
    def _scan_for_purpose_limitation(self, file_path, lines, content):
        """Scan for purpose limitation issues"""
        patterns = [
            (r'(?i)data.*use.*marketing', "Potential repurposing for marketing", "medium", "Article 5(1)(b)"),
            (r'(?i)repurpose.*data', "Data repurposing", "medium", "Article 5(1)(b)"),
        ]
        self._check_patterns(file_path, lines, "Purpose Limitation", patterns)
    
    def _scan_for_data_minimization(self, file_path, lines, content):
        """Scan for data minimization issues"""
        patterns = [
            (r'(?i)collect.*(?:unnecessary|excessive).*data', "Excessive data collection", "medium", "Article 5(1)(c)"),
            (r'(?i)store.*(?:full|complete).*profile', "Storing complete profiles", "medium", "Article 5(1)(c)"),
        ]
        self._check_patterns(file_path, lines, "Data Minimization", patterns)
    
    def _scan_for_accuracy(self, file_path, lines, content):
        """Scan for accuracy issues"""
        patterns = [
            (r'(?i)no.*validation', "Missing data validation", "medium", "Article 5(1)(d)"),
            (r'(?i)outdated.*data', "Potentially outdated data", "medium", "Article 5(1)(d)"),
        ]
        self._check_patterns(file_path, lines, "Accuracy", patterns)
    
    def _scan_for_storage_limitation(self, file_path, lines, content):
        """Scan for storage limitation issues"""
        patterns = [
            (r'(?i)(?:no|missing).*retention', "Missing retention policy", "medium", "Article 5(1)(e)"),
            (r'(?i)store.*(?:forever|indefinite)', "Indefinite data storage", "high", "Article 5(1)(e)"),
        ]
        self._check_patterns(file_path, lines, "Storage Limitation", patterns)
    
    def _scan_for_integrity_confidentiality(self, file_path, lines, content):
        """Scan for security & confidentiality issues"""
        patterns = [
            (r'(?i)api[_-]?key.*[\'"][a-zA-Z0-9_\-]{10,}[\'"]', "Hardcoded API key", "high", "Article 32"),
            (r'(?i)password.*[\'"][^\'"\n]{4,}[\'"]', "Hardcoded password", "high", "Article 32"),
            (r'(?i)unencrypted.*data', "Unencrypted data", "high", "Article 32"),
            (r'(?i)md5\(', "Weak hash algorithm (MD5)", "medium", "Article 32"),
        ]
        self._check_patterns(file_path, lines, "Integrity and Confidentiality", patterns)
    
    def _scan_for_accountability(self, file_path, lines, content):
        """Scan for accountability issues"""
        patterns = [
            (r'(?i)(?:no|missing).*log', "Missing data processing logs", "medium", "Article 5(2)"),
            (r'(?i)(?:no|missing).*audit', "Missing audit trail", "medium", "Article 5(2)"),
        ]
        self._check_patterns(file_path, lines, "Accountability", patterns)
    
    def _check_patterns(self, file_path, lines, principle, patterns):
        """Check for patterns in file content"""
        import re
        
        for i, line in enumerate(lines, 1):
            for pattern, description, severity, article in patterns:
                if re.search(pattern, line):
                    # Get context (line and surrounding lines)
                    start = max(0, i - 2)
                    end = min(len(lines), i + 2)
                    context = '\n'.join(lines[start-1:end])
                    
                    # Add finding
                    self.findings.append({
                        "file": file_path,
                        "line": i,
                        "principle": principle,
                        "severity": severity,
                        "description": description,
                        "snippet": context,
                        "gdpr_article": article
                    })
    
    def _calculate_compliance_scores(self):
        """Calculate compliance scores for each principle"""
        principles = [
            "Lawfulness, Fairness and Transparency",
            "Purpose Limitation",
            "Data Minimization",
            "Accuracy", 
            "Storage Limitation",
            "Integrity and Confidentiality",
            "Accountability"
        ]
        
        # Count findings by principle and severity
        severity_weights = {"high": 15, "medium": 5, "low": 1}
        principle_issues = {p: 0 for p in principles}
        
        for finding in self.findings:
            principle = finding.get("principle")
            severity = finding.get("severity", "low")
            if principle in principle_issues:
                principle_issues[principle] += severity_weights.get(severity, 1)
        
        # Calculate scores (100 - weighted issues, minimum 0)
        scores = {}
        for principle in principles:
            # Calculate score by deducting weighted issues
            deduction = min(100, principle_issues.get(principle, 0))
            scores[principle] = max(0, 100 - deduction)
            
        return scores

def generate_pdf_report(scan_results):
    """Generate a PDF report from scan results"""
    buffer = io.BytesIO()
    
    # Create document
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        title="GDPR Compliance Scan Report",
        leftMargin=1.5*cm, 
        rightMargin=1.5*cm, 
        topMargin=2*cm, 
        bottomMargin=2*cm
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
    content.append(Spacer(1, 0.5*cm))
    
    scan_date = datetime.fromisoformat(scan_results["scan_date"]) if isinstance(scan_results["scan_date"], str) else scan_results["scan_date"]
    content.append(Paragraph(f"Generated: {scan_date.strftime('%Y-%m-%d %H:%M')}", normal_style))
    content.append(Paragraph(f"Repository: {scan_results['repo_path']}", normal_style))
    content.append(Spacer(1, 1*cm))
    
    # Summary section
    content.append(Paragraph("Executive Summary", section_style))
    
    # Add metrics table
    summary_data = [
        ["Metric", "Value"],
        ["Files Scanned", str(scan_results["file_count"])],
        ["Findings", str(scan_results["findings_count"])],
        ["Scan Duration", f"{scan_results['scan_duration']:.2f} seconds"],
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
    content.append(Spacer(1, 0.5*cm))
    
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
    content.append(Spacer(1, 1*cm))
    
    # Findings section
    if scan_results["findings"]:
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
                
                # Set color based on severity
                color_code = colors.red if severity == "HIGH" else (colors.orange if severity == "MEDIUM" else colors.green)
                
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
                
                content.append(Spacer(1, 0.3*cm))
    else:
        content.append(Paragraph("No GDPR compliance issues were found!", heading2_style))
    
    # Build PDF document
    doc.build(content)
    
    # Get PDF data
    pdf_data = buffer.getvalue()
    buffer.close()
    
    return pdf_data

def main():
    """Main application function"""
    st.title("GDPR Code Scanner")
    st.markdown("Scan your codebase for GDPR compliance issues and generate a comprehensive PDF report.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Scan Configuration")
        
        # Repository path selection
        repo_path = st.text_input(
            "Repository Path",
            value=".",
            help="Enter the path to the code repository you want to scan"
        )
        
        # Language selection
        languages = st.multiselect(
            "Select Languages to Scan",
            options=["Python", "JavaScript", "TypeScript", "Java", "Terraform", "YAML", "JSON"],
            default=["Python", "JavaScript"],
            help="Select the programming languages to include in the scan"
        )
        
        # Start scan button
        scan_button = st.button("Start GDPR Scan", use_container_width=True)
        
        if scan_button:
            # Prepare for scanning
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Initialize scanner
                scanner = GDPRScanner(
                    repo_path=repo_path,
                    languages=[lang.lower() for lang in languages]
                )
                
                # Update progress
                status_text.text("Initializing scanner...")
                progress_bar.progress(0.1)
                
                # Run the scan
                status_text.text("Scanning repository...")
                
                # Simulate progress updates (in a real app, this would be based on actual progress)
                for i in range(2, 9):
                    time.sleep(0.3)
                    progress_bar.progress(i/10)
                    status_text.text(f"Scanning files... ({i*10}%)")
                
                # Get scan results
                scan_results = scanner.scan()
                
                # Complete progress
                progress_bar.progress(1.0)
                status_text.text("Scan completed!")
                
                # Store results in session state
                st.session_state.scan_results = scan_results
                
                # Generate PDF report
                pdf_data = generate_pdf_report(scan_results)
                st.session_state.pdf_report = pdf_data
                
                # Success message
                st.success("GDPR compliance scan completed successfully!")
                
                # Display download button for PDF
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"GDPR_Scan_Report_{timestamp}.pdf"
                
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_data,
                    file_name=filename,
                    mime="application/pdf",
                    key=f"download_pdf_{timestamp}",
                    use_container_width=True
                )
                
                # Alternative download link for reliability
                b64_pdf = base64.b64encode(pdf_data).decode()
                href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{filename}" style="display:block; text-align:center; margin-top:10px; padding:10px; background-color:#4f46e5; color:white; text-decoration:none; border-radius:4px;">📥 Alternative Download Link</a>'
                st.markdown(href, unsafe_allow_html=True)
            
            except Exception as e:
                st.error(f"Error during scan: {str(e)}")
                st.info("Please check the repository path and try again.")
    
    with col2:
        if 'scan_results' in st.session_state:
            scan_results = st.session_state.scan_results
            
            # Display scan summary
            st.markdown("### Scan Summary")
            
            # Create 3 metrics in a row
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Files Scanned", scan_results["file_count"])
            with col2:
                st.metric("Findings", scan_results["findings_count"])
            with col3:
                st.metric("Scan Duration", f"{scan_results['scan_duration']:.2f}s")
            
            # Display compliance scores with color-coded progress bars
            st.markdown("### GDPR Compliance Scores")
            scores = scan_results["compliance_scores"]
            
            score_cols = st.columns(2)
            for i, (principle, score) in enumerate(scores.items()):
                col_idx = i % 2
                with score_cols[col_idx]:
                    # Determine color based on score
                    color = "green" if score >= 90 else "orange" if score >= 70 else "red"
                    st.markdown(f"**{principle}**: {score}%")
                    st.progress(score/100, text=f"{score}%")
            
            # Display findings
            st.markdown("### Key Findings")
            findings = scan_results["findings"]
            
            if findings:
                # Group findings by severity for better presentation
                severity_groups = {"high": [], "medium": [], "low": []}
                for finding in findings:
                    severity = finding.get("severity", "low")
                    severity_groups[severity].append(finding)
                
                # Display findings by severity
                for severity, severity_findings in [
                    ("high", severity_groups["high"]), 
                    ("medium", severity_groups["medium"]), 
                    ("low", severity_groups["low"])
                ]:
                    if severity_findings:
                        if severity == "high":
                            st.error(f"**{severity.upper()} Severity Issues ({len(severity_findings)})**")
                        elif severity == "medium":
                            st.warning(f"**{severity.upper()} Severity Issues ({len(severity_findings)})**")
                        else:
                            st.info(f"**{severity.upper()} Severity Issues ({len(severity_findings)})**")
                        
                        for finding in severity_findings:
                            with st.expander(f"{finding.get('principle')}: {finding.get('description')}"):
                                st.markdown(f"**File:** `{finding.get('file')}`")
                                st.markdown(f"**Line:** {finding.get('line')}")
                                st.markdown(f"**GDPR Article:** {finding.get('gdpr_article', 'N/A')}")
                                if "snippet" in finding and finding["snippet"]:
                                    st.markdown(f"**Code Snippet:**")
                                    st.code(finding["snippet"])
            else:
                st.success("No GDPR compliance issues found! Your codebase looks great.")
        else:
            st.info("Configure and run a scan to see results here.")

if __name__ == "__main__":
    main()