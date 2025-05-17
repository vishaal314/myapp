"""
Streamlined GDPR Code Scanner

A clean, efficient scanner that analyzes code repositories for GDPR compliance issues
based on the 7 core GDPR principles with a focus on Dutch-specific rules (UAVG).

Features:
- Multi-language support
- Core GDPR principles scanning
- Dutch-specific requirements
- Professional PDF report generation
"""

import streamlit as st
import os
import re
import time
import io
import base64
from datetime import datetime
from typing import Dict, List, Any, Tuple

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

# Set page configuration
st.set_page_config(
    page_title="GDPR Code Scanner",
    page_icon="🛡️",
    layout="wide"
)

# Add custom CSS for modern UI
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
    }
    h1, h2, h3 {
        color: #1E3A8A;
    }
    .stButton>button {
        background-color: #1E3A8A;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# GDPR Principle Patterns (simplified)
GDPR_PRINCIPLES = {
    "Lawfulness, Fairness and Transparency": [
        (r'(?i)consent.*(?:not|missing|invalid)', "Potential invalid consent handling", "high", ["GDPR-Article6", "UAVG"]),
        (r'(?i)process(?:ing)?.*data.*without.*consent', "Processing data without explicit consent", "high", ["GDPR-Article6", "UAVG"]),
        (r'(?i)privacy.*policy.*missing', "Missing privacy policy reference", "medium", ["GDPR-Article13", "UAVG"]),
    ],
    
    "Purpose Limitation": [
        (r'(?i)use.*data.*(?:marketing|analytics).*without', "Using data beyond intended purpose", "high", ["GDPR-Article5-1b", "UAVG"]),
        (r'(?i)repurpos(?:e|ing).*data', "Repurposing data without consent", "medium", ["GDPR-Article5-1b", "UAVG"]),
    ],
    
    "Data Minimization": [
        (r'(?i)collect(?:ing)?.*(?:unnecessary|excessive).*data', "Collecting excessive data", "medium", ["GDPR-Article5-1c", "UAVG"]),
        (r'(?i)(?:store|save).*(?:full|complete).*(?:profile|history)', "Storing complete user profiles", "medium", ["GDPR-Article5-1c", "UAVG"]),
    ],
    
    "Accuracy": [
        (r'(?i)no.*(?:validation|verification)', "Lack of data validation", "medium", ["GDPR-Article5-1d", "UAVG"]),
        (r'(?i)(?:old|outdated|stale).*data', "Using potentially outdated data", "medium", ["GDPR-Article5-1d", "UAVG"]),
    ],
    
    "Storage Limitation": [
        (r'(?i)(?:no|missing).*retention.*(?:policy|period)', "Missing data retention policy", "medium", ["GDPR-Article5-1e", "UAVG"]),
        (r'(?i)(?:store|keep).*(?:forever|indefinite|permanent)', "Storing data indefinitely", "high", ["GDPR-Article5-1e", "UAVG"]),
    ],
    
    "Integrity and Confidentiality": [
        (r'(?i)data.{0,20}(?:not|un)encrypted', "Unencrypted data storage", "high", ["GDPR-Article5-1f", "GDPR-Article32", "UAVG"]),
        (r'(?i)(?:md5|sha1)\(', "Using weak hash algorithm", "medium", ["GDPR-Article5-1f", "GDPR-Article32", "UAVG"]),
    ],
    
    "Accountability": [
        (r'(?i)(?:no|missing).*log(?:ging|s)', "Missing data processing logs", "medium", ["GDPR-Article5-2", "UAVG"]),
        (r'(?i)(?:no|missing).*(?:audit|trail)', "Missing audit trail", "medium", ["GDPR-Article5-2", "UAVG"]),
    ],
}

# Dutch-specific patterns (UAVG)
DUTCH_PATTERNS = {
    "bsn": (r'\b[0-9]{9}\b', "BSN (Dutch Citizen Service Number)", "high", ["UAVG", "GDPR-Article9"]),
    "dutch_passport": (r'\b[A-Z]{2}[0-9]{6}\b', "Dutch Passport Number", "high", ["UAVG", "GDPR-Article6"]),
    "dutch_phone": (r'\b(?:\+31|0031|0)[1-9][0-9]{8}\b', "Dutch Phone Number", "medium", ["UAVG", "GDPR-Article6"]),
    "minor_consent": (r'(?i)(?:minor|child|under[_-]?16|age[_-]?check)', "Minor Consent Check", "high", ["UAVG", "GDPR-Article8"]),
    "breach_notification": (r'(?i)(?:breach[_-]?notification|security[_-]?incident|data[_-]?breach|72[_-]?hour)', "Breach Notification", "high", ["UAVG", "GDPR-Article33"]),
}

# Secret patterns
SECRET_PATTERNS = {
    "api_key": (r'(?i)(?:api[_-]?key|apikey|secret[_-]?key)[^a-zA-Z0-9][ \t]*[:=][ \t]*[\'"][a-zA-Z0-9_\-]{10,}[\'"]', "API Key", "high", ["GDPR-Article32"]),
    "password": (r'(?i)(?:password|passwd|pwd)[^a-zA-Z0-9][ \t]*[:=][ \t]*[\'"][^\'"\n]{4,}[\'"]', "Password", "high", ["GDPR-Article32"]),
}

class GDPRScanner:
    def __init__(self, repo_path='.', languages=None):
        self.repo_path = repo_path
        self.languages = languages or ["python", "javascript", "java", "typescript", "terraform", "yaml", "json"]
        self.findings = []
        self.file_count = 0
        self.line_count = 0
        
        # Language file extensions
        self.extensions = {
            "python": [".py", ".pyw"],
            "javascript": [".js", ".jsx", ".mjs"],
            "typescript": [".ts", ".tsx"],
            "java": [".java"],
            "terraform": [".tf", ".tfvars"],
            "yaml": [".yml", ".yaml"],
            "json": [".json"]
        }
    
    def scan(self):
        """Perform GDPR code scan"""
        start_time = datetime.now()
        
        # Get supported file extensions
        supported_exts = []
        for lang in self.languages:
            if lang.lower() in self.extensions:
                supported_exts.extend(self.extensions[lang.lower()])
                
        # Scan repository files
        for root, _, files in os.walk(self.repo_path):
            # Skip hidden directories
            if any(part.startswith('.') for part in root.split(os.sep)):
                continue
                
            for file in files:
                # Skip hidden files
                if file.startswith('.'):
                    continue
                    
                # Check if file extension is supported
                ext = os.path.splitext(file.lower())[1]
                if ext in supported_exts:
                    file_path = os.path.join(root, file)
                    self._scan_file(file_path)
        
        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()
        
        # Calculate compliance scores
        scores = self._calculate_compliance_scores()
        
        return {
            "scan_date": datetime.now().isoformat(),
            "repo_path": self.repo_path,
            "file_count": self.file_count,
            "line_count": self.line_count,
            "findings_count": len(self.findings),
            "findings": self.findings,
            "compliance_scores": scores,
            "scan_duration": duration
        }
    
    def _should_scan_file(self, filename):
        """Check if a file should be scanned based on its extension"""
        ext = os.path.splitext(filename.lower())[1]
        supported_exts = []
        for lang in self.languages:
            if lang.lower() in self.extensions:
                supported_exts.extend(self.extensions[lang.lower()])
        return ext in supported_exts
    
    def _scan_file(self, file_path):
        """Scan a single file for GDPR compliance issues"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
                
                # Update counts
                self.file_count += 1
                self.line_count += len(lines)
                
                # Scan for each GDPR principle
                self._scan_for_lawfulness(file_path, lines, content)
                self._scan_for_purpose_limitation(file_path, lines, content)
                self._scan_for_data_minimization(file_path, lines, content)
                self._scan_for_accuracy(file_path, lines, content)
                self._scan_for_storage_limitation(file_path, lines, content)
                self._scan_for_integrity_confidentiality(file_path, lines, content)
                self._scan_for_accountability(file_path, lines, content)
                
                # Scan for Dutch-specific patterns
                for pattern_name, (pattern, description, severity, region_flags) in DUTCH_PATTERNS.items():
                    self._check_patterns(file_path, lines, "Dutch-specific", [(pattern, description, severity, region_flags)])
                
                # Scan for secrets
                for pattern_name, (pattern, description, severity, region_flags) in SECRET_PATTERNS.items():
                    self._check_patterns(file_path, lines, "Secrets", [(pattern, description, severity, region_flags)])
                
        except Exception as e:
            # Log scanning error
            self.findings.append({
                "file": file_path,
                "line": 0,
                "type": "SCAN_ERROR",
                "principle": "Other",
                "description": f"Error scanning file: {str(e)}",
                "severity": "low",
                "region_flags": ["GDPR-Article5"],
            })
    
    def _scan_for_lawfulness(self, file_path, lines, content):
        """Scan for lawfulness, fairness and transparency issues"""
        principle = "Lawfulness, Fairness and Transparency"
        patterns = GDPR_PRINCIPLES[principle]
        self._check_patterns(file_path, lines, principle, patterns)
    
    def _scan_for_purpose_limitation(self, file_path, lines, content):
        """Scan for purpose limitation issues"""
        principle = "Purpose Limitation"
        patterns = GDPR_PRINCIPLES[principle]
        self._check_patterns(file_path, lines, principle, patterns)
        
    def _scan_for_data_minimization(self, file_path, lines, content):
        """Scan for data minimization issues"""
        principle = "Data Minimization"
        patterns = GDPR_PRINCIPLES[principle]
        self._check_patterns(file_path, lines, principle, patterns)
        
    def _scan_for_accuracy(self, file_path, lines, content):
        """Scan for accuracy issues"""
        principle = "Accuracy"
        patterns = GDPR_PRINCIPLES[principle]
        self._check_patterns(file_path, lines, principle, patterns)
        
    def _scan_for_storage_limitation(self, file_path, lines, content):
        """Scan for storage limitation issues"""
        principle = "Storage Limitation"
        patterns = GDPR_PRINCIPLES[principle]
        self._check_patterns(file_path, lines, principle, patterns)
        
    def _scan_for_integrity_confidentiality(self, file_path, lines, content):
        """Scan for security & confidentiality issues"""
        principle = "Integrity and Confidentiality"
        patterns = GDPR_PRINCIPLES[principle]
        self._check_patterns(file_path, lines, principle, patterns)
        
    def _scan_for_accountability(self, file_path, lines, content):
        """Scan for accountability issues"""
        principle = "Accountability"
        patterns = GDPR_PRINCIPLES[principle]
        self._check_patterns(file_path, lines, principle, patterns)
        
    def _check_patterns(self, file_path, lines, principle, patterns):
        """Check for patterns in file content"""
        for i, line in enumerate(lines, 1):
            for pattern, description, severity, region_flags in patterns:
                if re.search(pattern, line):
                    # Get code context (a few lines around the finding)
                    context_start = max(0, i - 2)
                    context_end = min(len(lines), i + 2)
                    context_snippet = '\n'.join(lines[context_start:context_end])
                    
                    # Add finding
                    self.findings.append({
                        "file": file_path,
                        "line": i,
                        "type": "GDPR_ISSUE",
                        "principle": principle,
                        "description": description,
                        "severity": severity,
                        "region_flags": region_flags,
                        "context_snippet": context_snippet
                    })
    
    def _calculate_compliance_scores(self):
        """Calculate compliance scores for each principle"""
        scores = {
            "Lawfulness, Fairness and Transparency": 100,
            "Purpose Limitation": 100,
            "Data Minimization": 100,
            "Accuracy": 100,
            "Storage Limitation": 100,
            "Integrity and Confidentiality": 100,
            "Accountability": 100
        }
        
        # Deduct points based on findings severity
        severity_weights = {
            "high": 20,
            "medium": 10,
            "low": 5
        }
        
        for finding in self.findings:
            principle = finding.get("principle")
            if principle in scores:
                severity = finding.get("severity", "low")
                weight = severity_weights.get(severity, 5)
                scores[principle] = max(0, scores[principle] - weight)
            
            # Handle Dutch-specific and Secret findings
            elif principle == "Dutch-specific" or principle == "Secrets":
                severity = finding.get("severity", "low")
                weight = severity_weights.get(severity, 5)
                # Deduct from most relevant principles
                if any("Article32" in flag for flag in finding.get("region_flags", [])):
                    scores["Integrity and Confidentiality"] = max(0, scores["Integrity and Confidentiality"] - weight)
                elif any("Article6" in flag for flag in finding.get("region_flags", [])):
                    scores["Lawfulness, Fairness and Transparency"] = max(0, scores["Lawfulness, Fairness and Transparency"] - weight)
                
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
    
    # Create content
    content = []
    
    # Title and report date
    content.append(Paragraph("GDPR Compliance Scan Report", title_style))
    content.append(Spacer(1, 0.5*cm))
    
    # Extract scan date
    scan_date = scan_results.get("scan_date", datetime.now().isoformat())
    if isinstance(scan_date, str):
        try:
            scan_date = datetime.fromisoformat(scan_date)
        except ValueError:
            scan_date = datetime.now()
    
    # Generate organization name from repo path
    repo_path = scan_results.get("repo_path", ".")
    org_name = os.path.basename(os.path.abspath(repo_path))
    
    content.append(Paragraph(f"Organization: {org_name}", normal_style))
    content.append(Paragraph(f"Generated: {scan_date.strftime('%Y-%m-%d %H:%M')}", normal_style))
    content.append(Paragraph(f"Repository: {repo_path}", normal_style))
    content.append(Spacer(1, 1*cm))
    
    # Summary section
    content.append(Paragraph("Executive Summary", section_style))
    
    # Add metrics table
    summary_data = [
        ["Metric", "Value"],
        ["Files Scanned", str(scan_results.get("file_count", 0))],
        ["Lines of Code", str(scan_results.get("line_count", 0))],
        ["Findings", str(scan_results.get("findings_count", 0))],
        ["Scan Duration", f"{scan_results.get('scan_duration', 0):.2f} seconds"],
    ]
    
    # Count findings by severity
    findings = scan_results.get("findings", [])
    severity_counts = {"high": 0, "medium": 0, "low": 0}
    for finding in findings:
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
    ]))
    
    content.append(summary_table)
    content.append(Spacer(1, 0.5*cm))
    
    # Compliance Scores section
    content.append(Paragraph("GDPR Compliance Scores", section_style))
    
    # Create scores table
    compliance_scores = scan_results.get("compliance_scores", {})
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
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
    ]))
    
    content.append(scores_table)
    content.append(Spacer(1, 1*cm))
    
    # Findings section - group by principle
    if findings:
        content.append(Paragraph("Key Findings", section_style))
        
        # Group findings by principle
        principle_findings = {}
        for finding in findings:
            principle = finding.get("principle", "Other")
            if principle not in principle_findings:
                principle_findings[principle] = []
            principle_findings[principle].append(finding)
        
        # Add findings by principle
        for principle, findings_list in principle_findings.items():
            content.append(Paragraph(f"{principle}", heading2_style))
            
            # Sort by severity
            findings_list.sort(key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x.get("severity", "low"), 3))
            
            # List findings
            for i, finding in enumerate(findings_list[:5], 1):  # Show only top 5 per principle
                severity = finding.get("severity", "low").upper()
                file_path = finding.get("file", "Unknown")
                line_num = finding.get("line", 0)
                description = finding.get("description", "No description")
                
                finding_text = f"{i}. {severity}: {description} ({os.path.basename(file_path)}:{line_num})"
                content.append(Paragraph(finding_text, normal_style))
            
            # Show message if more findings exist
            if len(findings_list) > 5:
                more_count = len(findings_list) - 5
                content.append(Paragraph(f"...and {more_count} more {principle} findings", normal_style))
            
            content.append(Spacer(1, 0.5*cm))
    else:
        content.append(Paragraph("No GDPR compliance issues were found!", heading2_style))
    
    # Build document
    doc.build(content)
    
    # Get PDF data
    pdf_data = buffer.getvalue()
    buffer.close()
    
    return pdf_data

def main():
    """Main application function"""
    st.title("GDPR Code Scanner")
    st.markdown("Scan your code for GDPR compliance issues with Dutch-specific rules (UAVG)")
    
    # Main layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Scan Configuration")
        
        # Repository path
        repo_path = st.text_input(
            "Repository Path",
            value=".",
            help="Path to the repository to scan"
        )
        
        # Select languages
        languages = st.multiselect(
            "Select Languages",
            options=["Python", "JavaScript", "TypeScript", "Java", "Terraform", "YAML", "JSON"],
            default=["Python", "JavaScript"],
            help="Select languages to scan"
        )
        
        # Organization name
        organization_name = st.text_input(
            "Organization Name",
            value="Your Organization",
            help="Your organization name for the report"
        )
        
        # Scan button
        scan_button = st.button("Start GDPR Scan", use_container_width=True)
    
    with col2:
        # Display scan results
        if scan_button:
            # Initialize scanner
            scanner = GDPRScanner(
                repo_path=repo_path,
                languages=[lang.lower() for lang in languages]
            )
            
            # Show progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Simulate scan progress
            for i in range(1, 11):
                progress_bar.progress(i/10)
                status_text.text(f"Scanning repository... ({i*10}%)")
                if i < 10:  # Don't sleep on the last iteration
                    time.sleep(0.3)
            
            # Run scan
            with st.spinner("Finalizing scan..."):
                results = scanner.scan()
                st.session_state.gdpr_scan_results = results
            
            # Update progress
            progress_bar.progress(1.0)
            status_text.text("Scan completed!")
            
            # Show success message
            st.success(f"GDPR compliance scan completed! Found {results['findings_count']} issues.")
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Files Scanned", results["file_count"])
            with col2:
                st.metric("Lines of Code", results["line_count"])
            with col3:
                st.metric("Issues Found", results["findings_count"])
            
            # Display GDPR compliance scores
            st.markdown("### GDPR Compliance Scores")
            
            for principle, score in results["compliance_scores"].items():
                # Color based on score
                if score >= 90:
                    st.success(f"**{principle}**: {score}%")
                elif score >= 70:
                    st.warning(f"**{principle}**: {score}%")
                else:
                    st.error(f"**{principle}**: {score}%")
            
            # Display findings
            if results["findings"]:
                st.markdown("### Key Findings")
                
                # Group findings by severity
                high_findings = [f for f in results["findings"] if f.get("severity") == "high"]
                medium_findings = [f for f in results["findings"] if f.get("severity") == "medium"]
                low_findings = [f for f in results["findings"] if f.get("severity") == "low"]
                
                # Show high severity findings
                if high_findings:
                    st.error(f"**HIGH SEVERITY ISSUES: {len(high_findings)}**")
                    for finding in high_findings[:5]:  # Show top 5
                        with st.expander(f"{finding['description']} - {os.path.basename(finding['file'])}:{finding['line']}"):
                            st.text(f"File: {finding['file']}")
                            st.text(f"Line: {finding['line']}")
                            st.text(f"Principle: {finding['principle']}")
                            st.text(f"GDPR References: {', '.join(finding['region_flags'])}")
                            st.code(finding['context_snippet'])
                
                # Show medium severity findings
                if medium_findings:
                    st.warning(f"**MEDIUM SEVERITY ISSUES: {len(medium_findings)}**")
                    for finding in medium_findings[:5]:  # Show top 5
                        with st.expander(f"{finding['description']} - {os.path.basename(finding['file'])}:{finding['line']}"):
                            st.text(f"File: {finding['file']}")
                            st.text(f"Line: {finding['line']}")
                            st.text(f"Principle: {finding['principle']}")
                            st.text(f"GDPR References: {', '.join(finding['region_flags'])}")
                            st.code(finding['context_snippet'])
            
            # PDF Report generation
            st.markdown("### Generate PDF Report")
            if st.button("Generate PDF Report", key="gen_pdf", use_container_width=True):
                with st.spinner("Generating PDF report..."):
                    pdf_data = generate_pdf_report(results)
                    
                    # Create filename with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                    filename = f"GDPR_Report_{organization_name.replace(' ', '_')}_{timestamp}.pdf"
                    
                    # Success message
                    st.success("PDF report generated successfully!")
                    
                    # Download button
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=pdf_data,
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                    # Alternative download link
                    b64_pdf = base64.b64encode(pdf_data).decode()
                    href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{filename}" style="display:block;text-align:center;margin-top:10px;padding:10px;background-color:#1E3A8A;color:white;text-decoration:none;border-radius:4px;">📥 Alternative Download Link</a>'
                    st.markdown(href, unsafe_allow_html=True)

if __name__ == "__main__":
    main()