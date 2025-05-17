"""
GDPR Code Scanner Page

A dedicated standalone page for the advanced GDPR code scanner that implements 
all 7 core GDPR principles with comprehensive repository analysis.
"""

import streamlit as st
import os
import json
import time
from datetime import datetime
from services.gdpr_code_scanner import GDPRCodeScanner, generate_html_report

st.set_page_config(
    page_title="GDPR Code Scanner",
    page_icon="🛡️",
    layout="wide"
)

def run_gdpr_code_scanner():
    st.title("GDPR Code Scanner")
    st.markdown("""
    This advanced scanner analyzes code repositories for GDPR compliance issues based on the 7 core GDPR principles.
    Upload your code or provide a repository URL to get a detailed compliance report.
    """)
    
    # Create a two-column layout for the scanner options and results
    scan_options_col, scan_results_col = st.columns([1, 2])
    
    with scan_options_col:
        st.markdown("### Scan Configuration")
        
        # Repository input options
        repository_type = st.radio(
            "Repository Type", 
            ["Local Directory", "GitHub Repository"],
            index=0,
            key="repo_type"
        )
        
        if repository_type == "Local Directory":
            repo_path = st.text_input(
                "Directory Path", 
                value=".",
                placeholder="Enter the path to your code directory",
                key="repo_path"
            )
            st.info("Using current directory for scan by default.")
        else:
            repo_path = st.text_input(
                "GitHub Repository URL", 
                placeholder="https://github.com/user/repo",
                key="repo_url"
            )
            github_branch = st.text_input(
                "Branch (optional)",
                placeholder="main",
                key="branch"
            )
        
        # Advanced scanning options
        with st.expander("Advanced Options"):
            languages = st.multiselect(
                "Select languages to scan",
                ["Python", "JavaScript", "TypeScript", "Java", "Terraform", "YAML", "JSON"],
                ["Python", "JavaScript"],
                key="languages"
            )
            
            scan_timeout = st.slider(
                "Scan timeout (seconds per file)", 
                min_value=5, 
                max_value=60, 
                value=20,
                key="timeout"
            )
            
            include_tests = st.checkbox(
                "Include test files",
                value=False,
                key="include_tests"
            )
            
            scan_principles = st.multiselect(
                "GDPR Principles to Scan",
                [
                    "Lawfulness, Fairness and Transparency",
                    "Purpose Limitation",
                    "Data Minimization",
                    "Accuracy",
                    "Storage Limitation",
                    "Integrity and Confidentiality",
                    "Accountability"
                ],
                [
                    "Lawfulness, Fairness and Transparency",
                    "Purpose Limitation",
                    "Data Minimization",
                    "Accuracy",
                    "Storage Limitation",
                    "Integrity and Confidentiality",
                    "Accountability"
                ],
                key="principles"
            )
        
        # Start scan button
        scan_button = st.button("Run GDPR Scan", key="run_scan", use_container_width=True)

    # Handle scan initiation
    if scan_button and repo_path:
        with scan_results_col:
            st.markdown("### Scan Progress")
            
            # Progress bar
            progress_bar = st.progress(0.0, text="Preparing to scan...")
            progress_text = st.empty()
            
            # Run the scan
            try:
                # Convert selected languages to lowercase for scanner
                selected_languages = [lang.lower() for lang in languages]
                
                # Initialize scanner
                progress_text.text("Initializing scanner...")
                progress_bar.progress(0.1)
                
                scanner = GDPRCodeScanner(
                    repo_path=repo_path,
                    languages=selected_languages,
                    timeout=scan_timeout
                )
                
                # Run the scan
                progress_text.text("Scanning repository...")
                progress_bar.progress(0.2)
                
                # Simulate scan progress (in a real implementation, this would be updated during the scan)
                for i in range(3, 10):
                    time.sleep(0.5)  # Simulate processing time
                    progress_bar.progress(i/10, text=f"Scanning files... ({i*10}%)")
                
                # Perform the actual scan
                scan_results = scanner.scan()
                
                # Complete the progress bar
                progress_bar.progress(1.0, text="Scan completed!")
                progress_text.text("Scan completed successfully.")
                
                # Store the results in session state for report generation
                st.session_state.last_scan_results = scan_results
                
                # Display scan summary
                st.markdown("### Scan Summary")
                
                # Create metrics for a quick overview
                stats = scan_results.get("stats", {})
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Files Scanned", stats.get("files_scanned", 0))
                with col2:
                    st.metric("Lines of Code", stats.get("lines_scanned", 0))
                with col3:
                    st.metric("Findings", stats.get("findings_count", 0))
                
                # Display compliance scores
                st.markdown("### GDPR Compliance Scores")
                compliance_scores = scan_results.get("compliance_scores", {})
                
                # Create score bars
                score_cols = st.columns(2)
                
                for i, (principle, score) in enumerate(compliance_scores.items()):
                    col_idx = i % 2
                    with score_cols[col_idx]:
                        st.markdown(f"**{principle}**: {score}%")
                        # Color-coded progress bar
                        color = "green" if score >= 90 else "orange" if score >= 70 else "red"
                        st.progress(score/100, text=f"{score}%")
                
                # Display findings
                st.markdown("### Key Findings")
                findings = scan_results.get("findings", [])
                
                if findings:
                    # Group findings by severity for better presentation
                    severity_groups = {"high": [], "medium": [], "low": []}
                    
                    for finding in findings:
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
                                    st.markdown(f"**Context:**")
                                    st.code(finding.get("context_snippet", "No context available"))
                else:
                    st.success("No GDPR compliance issues found! Your codebase looks great.")
                
                # Generate report options
                st.markdown("### Generate Report")
                
                report_type = st.radio(
                    "Report Format",
                    ["HTML", "PDF", "JSON"],
                    horizontal=True,
                    key="report_format"
                )
                
                if st.button("Generate Report", key="generate_report", use_container_width=True):
                    if report_type == "HTML":
                        # Generate HTML report
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        html_file = f"gdpr_report_{timestamp}.html"
                        report_path = generate_html_report(scan_results, html_file)
                        
                        # Read the HTML content for download
                        with open(html_file, 'r') as f:
                            html_content = f.read()
                        
                        st.success("HTML report generated successfully!")
                        st.download_button(
                            label="Download HTML Report",
                            data=html_content,
                            file_name=html_file,
                            mime="text/html",
                            key="download_html_report",
                            use_container_width=True
                        )
                    
                    elif report_type == "PDF":
                        st.info("Generating PDF report...")
                        # In a real implementation, this would generate a PDF
                        # For now, we'll create a simple HTML report as a placeholder
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        html_file = f"gdpr_report_{timestamp}.html"
                        generate_html_report(scan_results, html_file)
                        
                        st.success("Report generated!")
                        st.markdown("""
                        For a full PDF report of your GDPR compliance scan, please use one of our dedicated 
                        PDF generators that can be accessed from the main application under "GDPR Report Options".
                        """)
                    
                    else:  # JSON
                        # Export results as JSON
                        json_str = json.dumps(scan_results, indent=2)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        
                        st.success("JSON report generated successfully!")
                        st.download_button(
                            label="Download JSON Report",
                            data=json_str,
                            file_name=f"gdpr_scan_results_{timestamp}.json",
                            mime="application/json",
                            key="download_json_report",
                            use_container_width=True
                        )
            
            except Exception as e:
                st.error(f"Error during scan: {str(e)}")
                st.info("Please check the repository path and try again.")

if __name__ == "__main__":
    run_gdpr_code_scanner()