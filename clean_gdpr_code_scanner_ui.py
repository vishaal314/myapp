"""
Clean GDPR Code Scanner UI

A modern, user-friendly interface for the GDPR Code Scanner with Dutch-specific UAVG requirements.
This UI component can be directly integrated into the main application.
"""

import streamlit as st
import base64
import time
from datetime import datetime
import os
from gdpr_scanner_module import GDPRScanner, generate_pdf_report

def render_gdpr_scanner_ui():
    """Render the GDPR Code Scanner UI"""
    
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
            border-radius: 0.5rem;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 600;
        }
        .stButton>button:hover {
            background-color: #3B82F6;
        }
        .gdpr-card {
            background-color: white;
            border-radius: 0.5rem;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
        }
        .finding-high {
            border-left: 4px solid #DC2626;
            padding-left: 1rem;
            margin-bottom: 0.5rem;
        }
        .finding-medium {
            border-left: 4px solid #F59E0B;
            padding-left: 1rem;
            margin-bottom: 0.5rem;
        }
        .finding-low {
            border-left: 4px solid #10B981;
            padding-left: 1rem;
            margin-bottom: 0.5rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.title("GDPR Code Scanner")
    st.markdown("Scan your code repository for GDPR compliance with Dutch-specific rules (UAVG)")
    
    # Main layout with two columns
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<div class="gdpr-card">', unsafe_allow_html=True)
        st.markdown("### Scan Configuration")
        
        # Repository path input
        repo_path = st.text_input(
            "Repository Path",
            value=".",
            help="Path to the repository to scan",
            key="repo_path_config"
        )
        
        # Language selection
        languages = st.multiselect(
            "Select Languages",
            options=["Python", "JavaScript", "TypeScript", "Java", "Terraform", "YAML", "JSON"],
            default=["Python", "JavaScript"],
            help="Select languages to scan",
            key="languages_config"
        )
        
        # Organization name for report
        organization_name = st.text_input(
            "Organization Name",
            value="Your Organization",
            help="Your organization name for the report",
            key="org_name_config"
        )
        
        # Advanced options in expandable section
        with st.expander("Advanced Options"):
            include_git_info = st.checkbox(
                "Include Git Information",
                value=True,
                help="Include git blame and commit information in findings",
                key="git_info_config"
            )
        
        # Start scan button
        scan_button = st.button(
            "Start GDPR Scan",
            use_container_width=True,
            key="start_scan_config"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Display scan results when scan is initiated
        if scan_button:
            st.markdown('<div class="gdpr-card">', unsafe_allow_html=True)
            st.markdown("### Scanning Repository")
            
            # Set up progress reporting
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Callback for updating progress
            def update_progress(progress, message):
                progress_bar.progress(progress)
                status_text.text(message)
            
            # Run the scan
            try:
                # Initialize scanner
                scanner = GDPRScanner(
                    repo_path=repo_path,
                    languages=[lang.lower() for lang in languages]
                )
                
                # Run scan with progress reporting
                scan_results = scanner.scan(on_progress=update_progress)
                
                # Update final progress
                update_progress(1.0, "Scan completed!")
                
                # Store scan results in session state
                st.session_state.gdpr_scan_results = scan_results
                
                # Show success message
                st.success(f"GDPR compliance scan completed successfully! Found {scan_results['findings_count']} issues.")
                
            except Exception as e:
                st.error(f"Error during scan: {str(e)}")
                st.markdown('</div>', unsafe_allow_html=True)
                return
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Display scan results
            st.markdown('<div class="gdpr-card">', unsafe_allow_html=True)
            st.markdown("### Scan Summary")
            
            # Create metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Files Scanned", scan_results.get("file_count", 0))
            with col2:
                st.metric("Lines of Code", scan_results.get("line_count", 0))
            with col3:
                st.metric("Findings", scan_results.get("findings_count", 0))
            with col4:
                st.metric("Scan Duration", f"{scan_results.get('scan_duration', 0):.2f}s")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Display compliance scores
            st.markdown('<div class="gdpr-card">', unsafe_allow_html=True)
            st.markdown("### GDPR Compliance Scores")
            
            # Get compliance scores and create a visualization
            compliance_scores = scan_results.get("compliance_scores", {})
            
            # Create columns for scores
            score_cols = st.columns(2)
            for i, (principle, score) in enumerate(compliance_scores.items()):
                col_idx = i % 2
                with score_cols[col_idx]:
                    # Color based on score
                    if score >= 90:
                        st.success(f"**{principle}**: {score}%")
                    elif score >= 70:
                        st.warning(f"**{principle}**: {score}%")
                    else:
                        st.error(f"**{principle}**: {score}%")
                    
                    st.progress(score/100)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Display findings
            findings = scan_results.get("findings", [])
            if findings:
                st.markdown('<div class="gdpr-card">', unsafe_allow_html=True)
                st.markdown("### Key Findings")
                
                # Group findings by severity
                high_findings = [f for f in findings if f.get("severity") == "high"]
                medium_findings = [f for f in findings if f.get("severity") == "medium"]
                low_findings = [f for f in findings if f.get("severity") == "low"]
                
                # Show high severity findings
                if high_findings:
                    st.markdown('<div class="finding-high">', unsafe_allow_html=True)
                    st.markdown(f"**🔴 HIGH SEVERITY ISSUES: {len(high_findings)}**")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    for finding in high_findings[:5]:  # Show top 5
                        with st.expander(f"{finding['description']} - {os.path.basename(finding['file'])}:{finding['line']}"):
                            st.text(f"File: {finding['file']}")
                            st.text(f"Line: {finding['line']}")
                            st.text(f"Principle: {finding['principle']}")
                            st.text(f"GDPR References: {', '.join(finding['region_flags'])}")
                            st.code(finding['context_snippet'])
                    
                    if len(high_findings) > 5:
                        st.markdown(f"*...and {len(high_findings) - 5} more high severity findings*")
                
                # Show medium severity findings
                if medium_findings:
                    st.markdown('<div class="finding-medium">', unsafe_allow_html=True)
                    st.markdown(f"**🟠 MEDIUM SEVERITY ISSUES: {len(medium_findings)}**")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    for finding in medium_findings[:5]:  # Show top 5
                        with st.expander(f"{finding['description']} - {os.path.basename(finding['file'])}:{finding['line']}"):
                            st.text(f"File: {finding['file']}")
                            st.text(f"Line: {finding['line']}")
                            st.text(f"Principle: {finding['principle']}")
                            st.text(f"GDPR References: {', '.join(finding['region_flags'])}")
                            st.code(finding['context_snippet'])
                    
                    if len(medium_findings) > 5:
                        st.markdown(f"*...and {len(medium_findings) - 5} more medium severity findings*")
                
                # Show low severity findings
                if low_findings:
                    st.markdown('<div class="finding-low">', unsafe_allow_html=True)
                    st.markdown(f"**🟢 LOW SEVERITY ISSUES: {len(low_findings)}**")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    for finding in low_findings[:3]:  # Show top 3
                        with st.expander(f"{finding['description']} - {os.path.basename(finding['file'])}:{finding['line']}"):
                            st.text(f"File: {finding['file']}")
                            st.text(f"Line: {finding['line']}")
                            st.text(f"Principle: {finding['principle']}")
                            st.text(f"GDPR References: {', '.join(finding['region_flags'])}")
                            st.code(finding['context_snippet'])
                    
                    if len(low_findings) > 3:
                        st.markdown(f"*...and {len(low_findings) - 3} more low severity findings*")
                
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="gdpr-card">', unsafe_allow_html=True)
                st.success("No GDPR compliance issues found in the repository!")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Generate reports
            st.markdown('<div class="gdpr-card">', unsafe_allow_html=True)
            st.markdown("### Generate Reports")
            
            if st.button("Generate PDF Report", use_container_width=True, key="gen_pdf_button"):
                with st.spinner("Generating PDF report..."):
                    # Generate PDF report
                    pdf_data = generate_pdf_report(scan_results, organization_name)
                    
                    # Create a unique timestamp for the filename
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                    filename = f"GDPR_Compliance_Report_{organization_name.replace(' ', '_')}_{timestamp}.pdf"
                    
                    # Show success message
                    st.success("PDF report generated successfully!")
                    
                    # Download button
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=pdf_data,
                        file_name=filename,
                        mime="application/pdf",
                        key=f"download_pdf_{timestamp}",
                        use_container_width=True
                    )
                    
                    # Alternative download method for better reliability
                    b64_pdf = base64.b64encode(pdf_data).decode()
                    href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{filename}" style="display:block;text-align:center;margin-top:10px;padding:10px;background-color:#1E3A8A;color:white;text-decoration:none;border-radius:4px;">📥 Alternative Download Link</a>'
                    st.markdown(href, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # If no scan has been run, show placeholder
    if not scan_button and 'gdpr_scan_results' not in st.session_state:
        with col2:
            st.markdown('<div class="gdpr-card">', unsafe_allow_html=True)
            st.markdown("### Ready to Scan")
            st.info("Configure your scan settings on the left and click 'Start GDPR Scan' to begin.")
            
            # Feature highlights
            st.markdown("#### Key Features")
            st.markdown("""
            - **Multi-language Support**: Scan Python, JavaScript, Java, and more
            - **Dutch-specific Rules**: Compliance with UAVG requirements
            - **Complete GDPR Coverage**: All 7 core principles
            - **Professional Reports**: Generate detailed PDF reports
            - **PII Detection**: Identify personal data in your codebase
            """)
            
            # Sample findings visualization
            st.markdown("#### Example Findings")
            
            st.markdown('<div class="finding-high">', unsafe_allow_html=True)
            st.markdown("🔴 **HIGH**: BSN (Dutch Citizen Service Number) detected - user_model.py:42 (UAVG, GDPR-Article9)")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="finding-medium">', unsafe_allow_html=True)
            st.markdown("🟠 **MEDIUM**: Missing data retention policy - database.py:78 (GDPR-Article5-1e, UAVG)")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="finding-low">', unsafe_allow_html=True)
            st.markdown("🟢 **LOW**: Dutch postal code pattern detected - address.py:105 (UAVG, GDPR-Article6)")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    render_gdpr_scanner_ui()