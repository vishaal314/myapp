"""
PCI DSS Compliance Scanner Standalone Application

This is a clean, standalone version of the PCI DSS scanner with a
properly structured UI that ensures all fields are correctly displayed.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import time
from datetime import datetime
import os
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create mock PCIDSSScanner class for standalone application
class PCIDSSScanner:
    """
    Simplified PCI DSS Scanner for demonstration purposes.
    This implements the same interface as the real scanner but returns mock data.
    """
    
    def __init__(self, region="Global", progress_callback=None):
        """Initialize the scanner with region context."""
        self.region = region
        self.progress_callback = progress_callback
    
    def scan(self, **kwargs):
        """
        Simulate scanning with the provided parameters.
        
        Args:
            **kwargs: Scan parameters including:
                - repo_url: Repository URL to scan
                - branch: Branch to scan
                - uploaded_files: Uploaded files list
                - requirements: PCI DSS requirements filter dictionary
                - scan_scope: List of scan components to include
                - output_formats: List of desired output formats
                
        Returns:
            Dictionary containing simulated scan results
        """
        # Extract parameters
        repo_url = kwargs.get('repo_url', '')
        branch = kwargs.get('branch', 'main')
        uploaded_files = kwargs.get('uploaded_files', [])
        requirements = kwargs.get('requirements', {})
        
        # Update progress if callback provided
        if self.progress_callback:
            self.progress_callback(1, 10, "Starting scan...")
        
        # Simulate scanning process with progress updates
        for i in range(2, 11):
            time.sleep(0.5)  # Simulate processing time
            if self.progress_callback:
                self.progress_callback(i, 10, f"Scanning {'files' if uploaded_files else 'repository'}...")
        
        # Generate mock findings
        findings = [
            {
                "type": "Insecure Storage",
                "location": "payment_processor.py:45",
                "risk_level": "High",
                "pci_requirement": "Req 3.4",
                "description": "Credit card numbers stored in plaintext"
            },
            {
                "type": "Weak Cryptography",
                "location": "encryption.py:78",
                "risk_level": "Medium",
                "pci_requirement": "Req 4.1",
                "description": "Using outdated encryption algorithm (MD5)"
            },
            {
                "type": "Insecure Authentication",
                "location": "auth/login.py:120",
                "risk_level": "High",
                "pci_requirement": "Req 8.2",
                "description": "Password stored with weak hashing"
            },
            {
                "type": "Missing Logging",
                "location": "transactions.py:213",
                "risk_level": "Medium",
                "pci_requirement": "Req 10.2",
                "description": "Payment operations not logged properly"
            },
            {
                "type": "Hardcoded Secret",
                "location": "config.py:32",
                "risk_level": "High",
                "pci_requirement": "Req 6.5",
                "description": "API key hardcoded in source file"
            }
        ]
        
        # Generate mock PCI categories data
        pci_categories = {
            "Data Protection": 2,
            "Authentication": 1,
            "Network Security": 0,
            "Logging & Monitoring": 1,
            "Secure Coding": 1,
            "Access Control": 0
        }
        
        # Create mock recommendations
        recommendations = [
            "Encrypt all stored credit card data using strong cryptography",
            "Implement secure authentication with proper password hashing",
            "Remove hardcoded credentials from code and use a secure vault",
            "Implement comprehensive logging for all payment operations",
            "Use modern encryption algorithms (AES-256 or better)"
        ]
        
        # Return simulated results
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "repository": repo_url if repo_url else "File Upload",
            "branch": branch,
            "region": self.region,
            "findings": findings,
            "high_risk_count": 3,
            "medium_risk_count": 2,
            "low_risk_count": 0,
            "compliance_score": 68,
            "pci_categories": pci_categories,
            "recommendations": recommendations,
            "performance": {
                "clone_time": 1.2,
                "scan_time": 3.8,
                "total_time": 5.0
            },
            "output_formats": kwargs.get('output_formats', [])
        }

# Create simplified PDF report generator
def generate_pcidss_report(scan_results):
    """
    Generate a simple mock PDF report.
    
    Args:
        scan_results: Scan results dictionary
        
    Returns:
        Bytes containing the PDF report
    """
    # In a real implementation, this would generate a proper PDF
    # For this demo, we just return sample PDF bytes
    return b"%PDF-1.7\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /MediaBox [0 0 612 792] /Contents 5 0 R >>\nendobj\n4 0 obj\n<< /Type /Font /Subtype /Type1 /Name /F1 /BaseFont /Helvetica >>\nendobj\n5 0 obj\n<< /Length 68 >>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(PCI DSS Compliance Report - Sample) Tj\nET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000234 00000 n\n0000000311 00000 n\ntrailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n429\n%%EOF"

def main():
    """Main application function."""
    st.set_page_config(
        page_title="PCI DSS Compliance Scanner",
        page_icon="🔐",
        layout="wide"
    )
    
    # App header
    st.title("PCI DSS Compliance Scanner")
    
    st.write(
        "Scan your codebase for Payment Card Industry Data Security Standard (PCI DSS) compliance issues. "
        "This scanner identifies security vulnerabilities, exposures, and configuration issues that could "
        "impact your ability to securely process, store, or transmit credit card data."
    )
    
    # Add more detailed info in an info box
    st.info(
        "PCI DSS scanning analyzes your code against the 12 PCI DSS requirements to identify "
        "potential compliance issues. The scanner detects insecure coding patterns, vulnerable "
        "dependencies, and configurations that could put cardholder data at risk."
    )
    
    # Trial status notice
    st.markdown("""
    <div style="padding: 10px; border-radius: 5px; background-color: #f0f2f6; margin-bottom: 20px;">
        <span style="font-weight: bold;">Free Trial:</span> 3 days left
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for layout
    config_col, results_col = st.columns([1, 1.5])
    
    # Configuration column
    with config_col:
        st.markdown("## Configuration")
        
        # 1. Region Selection
        st.subheader("1. Select Region")
        region_options = ["Global", "Netherlands", "Germany", "France", "Belgium"]
        selected_region = st.selectbox(
            "Region:",
            region_options,
            index=0,
            key="pcidss_region"
        )
        
        # 2. Source Type Selection
        st.subheader("2. Source Selection")
        source_type = st.radio(
            "Select source type:",
            ["Repository URL", "Upload Files"],
            key="pcidss_source_type"
        )
        
        # 3. Source Details
        st.subheader("3. Source Details")
        
        if source_type == "Repository URL":
            # Repository provider selection
            repo_provider = st.radio(
                "Repository Provider:",
                ["GitHub", "BitBucket", "Azure DevOps"],
                horizontal=True,
                key="pcidss_repo_provider"
            )
            
            # Repository URL input
            repo_url = st.text_input(
                "Repository URL:",
                placeholder=f"Example: https://{repo_provider.lower()}.com/username/repo",
                key="pcidss_repo_url"
            )
            
            # Branch input
            branch = st.text_input(
                "Branch:",
                value="main",
                key="pcidss_branch"
            )
            
            # Private repository toggle
            with st.expander("Private Repository?"):
                token = st.text_input(
                    "Access Token:",
                    type="password",
                    key="pcidss_token",
                    help="Only required for private repositories"
                )
            
            # For file upload source, initialize empty list
            uploaded_files = []
        else:
            # File upload section
            uploaded_files = st.file_uploader(
                "Upload files to scan:",
                accept_multiple_files=True,
                key="pcidss_files"
            )
            
            if uploaded_files:
                st.success(f"Uploaded {len(uploaded_files)} files")
            
            # For repository URL source, initialize empty values
            repo_url = ""
            branch = "main"
            token = ""
        
        # 4. Scan Options
        st.subheader("4. Scan Options")
        
        # Create two columns for options
        opt_col1, opt_col2 = st.columns(2)
        
        with opt_col1:
            scan_dependencies = st.checkbox(
                "Scan Dependencies",
                value=True,
                key="pcidss_deps"
            )
            scan_iac = st.checkbox(
                "Scan Infrastructure",
                value=True,
                key="pcidss_iac"
            )
        
        with opt_col2:
            scan_secrets = st.checkbox(
                "Detect Secrets",
                value=True,
                key="pcidss_secrets"
            )
            scan_sast = st.checkbox(
                "Static Analysis",
                value=True,
                key="pcidss_sast",
                help="SAST for application security issues"
            )
        
        # PCI DSS Requirements filter in an expander
        with st.expander("PCI DSS Requirements Filter"):
            st.markdown("**Select specific requirements to focus on:**")
            
            # Create two columns for requirements selection
            req_col1, req_col2 = st.columns(2)
            
            with req_col1:
                req1 = st.checkbox("Req 1: Firewalls", key="pcidss_req1")
                req2 = st.checkbox("Req 2: Defaults", key="pcidss_req2")
                req3 = st.checkbox("Req 3: Data Storage", key="pcidss_req3")
                req4 = st.checkbox("Req 4: Transmission", key="pcidss_req4")
                req5 = st.checkbox("Req 5: Malware", key="pcidss_req5")
                req6 = st.checkbox("Req 6: Systems", key="pcidss_req6")
            
            with req_col2:
                req7 = st.checkbox("Req 7: Access", key="pcidss_req7")
                req8 = st.checkbox("Req 8: Identity", key="pcidss_req8")
                req9 = st.checkbox("Req 9: Physical", key="pcidss_req9")
                req10 = st.checkbox("Req 10: Monitoring", key="pcidss_req10")
                req11 = st.checkbox("Req 11: Testing", key="pcidss_req11")
                req12 = st.checkbox("Req 12: Policy", key="pcidss_req12")
        
        # 5. Output Format
        st.subheader("5. Output Format")
        output_formats = st.multiselect(
            "Select output formats:",
            ["PDF Report", "CSV Export", "JSON Export"],
            default=["PDF Report"],
            key="pcidss_output"
        )
        
        # 6. Start Scan
        st.subheader("6. Start Scan")
        scan_button = st.button(
            "Start PCI DSS Compliance Scan",
            type="primary",
            use_container_width=True,
            key="pcidss_scan_button"
        )
    
    # Results column
    with results_col:
        st.markdown("## Results")
        
        # Process scan button click
        if scan_button:
            # Validation
            valid_input = True
            if source_type == "Repository URL" and not repo_url:
                st.error("Please enter a repository URL")
                valid_input = False
            elif source_type == "Upload Files" and not uploaded_files:
                st.error("Please upload at least one file")
                valid_input = False
            
            if valid_input:
                # Show scan progress
                st.subheader("Scan in Progress")
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Build requirements dictionary
                requirements = {
                    "req1": req1,
                    "req2": req2,
                    "req3": req3,
                    "req4": req4,
                    "req5": req5,
                    "req6": req6,
                    "req7": req7,
                    "req8": req8,
                    "req9": req9,
                    "req10": req10,
                    "req11": req11,
                    "req12": req12
                }
                
                # Build scan scope list
                scan_scope = []
                if scan_sast:
                    scan_scope.append("SAST (Static Application Security Testing)")
                if scan_dependencies:
                    scan_scope.append("SCA (Software Composition Analysis)")
                if scan_iac:
                    scan_scope.append("IaC (Infrastructure-as-Code) Scanning")
                if scan_secrets:
                    scan_scope.append("Secrets Detection")
                
                try:
                    # Progress callback function
                    def update_progress(current, total, message):
                        progress_val = current / total
                        progress_bar.progress(progress_val)
                        status_text.text(message)
                    
                    # Initialize scanner
                    scanner = PCIDSSScanner(
                        region=selected_region,
                        progress_callback=update_progress
                    )
                    
                    # Prepare scan parameters
                    scan_params = {
                        "scan_scope": scan_scope,
                        "requirements": requirements,
                        "output_formats": output_formats,
                        "region": selected_region
                    }
                    
                    # Add source-specific parameters
                    if source_type == "Repository URL":
                        scan_params["repo_url"] = repo_url
                        scan_params["branch"] = branch
                        if token:
                            scan_params["token"] = token
                    else:
                        scan_params["uploaded_files"] = uploaded_files
                    
                    # Execute scan
                    with st.spinner("Running PCI DSS scan..."):
                        scan_results = scanner.scan(**scan_params)
                    
                    # Store results in session state
                    st.session_state.pcidss_scan_results = scan_results
                    
                    # Update progress
                    progress_bar.progress(1.0)
                    status_text.success("Scan completed successfully!")
                    
                    # Force rerun to update UI with results
                    st.rerun()
                
                except Exception as e:
                    status_text.error(f"Error during scan: {str(e)}")
                    st.exception(e)
        
        # Display results if available
        if 'pcidss_scan_results' in st.session_state:
            scan_results = st.session_state.pcidss_scan_results
            
            # Create results tabs
            summary_tab, findings_tab, visuals_tab = st.tabs(["Summary", "Findings", "Visualizations"])
            
            # Summary tab content
            with summary_tab:
                st.subheader("Scan Results Summary")
                
                # Display source information
                if scan_results.get('repository') and scan_results.get('repository') != "File Upload":
                    st.markdown(f"**Repository:** {scan_results.get('repository')}")
                    st.markdown(f"**Branch:** {scan_results.get('branch', 'main')}")
                else:
                    st.markdown("**Source:** Uploaded Files")
                
                st.markdown(f"**Region:** {scan_results.get('region', 'Global')}")
                
                # Create metrics
                metrics_cols = st.columns(4)
                
                # Get metric values
                compliance_score = scan_results.get("compliance_score", 0)
                high_risk = scan_results.get("high_risk_count", 0)
                medium_risk = scan_results.get("medium_risk_count", 0)
                low_risk = scan_results.get("low_risk_count", 0)
                
                # Determine compliance status
                if compliance_score >= 80:
                    status = "✓ Compliant"
                    color = "normal"
                elif compliance_score >= 60:
                    status = "⚠ Action Needed"
                    color = "off"
                else:
                    status = "❌ Critical"
                    color = "inverse"
                
                # Display metrics
                with metrics_cols[0]:
                    st.metric(
                        "Compliance Score",
                        f"{compliance_score}%",
                        delta=status,
                        delta_color=color
                    )
                
                with metrics_cols[1]:
                    st.metric(
                        "High Risk",
                        high_risk,
                        delta=None,
                        delta_color="inverse"
                    )
                
                with metrics_cols[2]:
                    st.metric(
                        "Medium Risk",
                        medium_risk,
                        delta=None,
                        delta_color="off"
                    )
                
                with metrics_cols[3]:
                    st.metric(
                        "Low Risk",
                        low_risk,
                        delta=None,
                        delta_color="normal"
                    )
                
                # Performance metrics
                st.subheader("Performance")
                perf = scan_results.get("performance", {})
                st.text(f"Clone time: {perf.get('clone_time', 0)}s, Scan time: {perf.get('scan_time', 0)}s, Total time: {perf.get('total_time', 0)}s")
                
                # Key recommendations
                st.subheader("Key Recommendations")
                recommendations = scan_results.get("recommendations", [])
                
                if recommendations:
                    for i, rec in enumerate(recommendations[:3]):
                        st.markdown(f"**{i+1}.** {rec}")
                    
                    if len(recommendations) > 3:
                        with st.expander("View All Recommendations"):
                            for i, rec in enumerate(recommendations[3:], 4):
                                st.markdown(f"**{i}.** {rec}")
                else:
                    st.info("No recommendations available")
            
            # Findings tab content
            with findings_tab:
                st.subheader("Detailed Findings")
                findings = scan_results.get("findings", [])
                
                if findings:
                    # Create dataframe for findings
                    findings_df = pd.DataFrame(findings)
                    
                    # Rename columns for display
                    display_df = findings_df.rename(columns={
                        "type": "Type",
                        "location": "Location",
                        "risk_level": "Risk Level",
                        "pci_requirement": "PCI Requirement",
                        "description": "Description"
                    })
                    
                    # Apply styling to risk levels
                    def highlight_risk(val):
                        if val == "High":
                            return 'background-color: #FFCCCC'
                        elif val == "Medium":
                            return 'background-color: #FFFFCC'
                        elif val == "Low":
                            return 'background-color: #CCFFCC'
                        return ''
                    
                    # Apply styling and display
                    styled_df = display_df.style.applymap(highlight_risk, subset=['Risk Level'])
                    st.dataframe(styled_df, use_container_width=True)
                    
                    # Export options
                    export_cols = st.columns(2)
                    with export_cols[0]:
                        st.download_button(
                            "Export to CSV",
                            data=display_df.to_csv(index=False),
                            file_name=f"pcidss_findings_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
                else:
                    st.info("No findings detected in the scan")
            
            # Visualizations tab content
            with visuals_tab:
                st.subheader("PCI DSS Compliance Visualizations")
                
                # Extract categories data
                pci_categories = scan_results.get("pci_categories", {})
                
                if pci_categories:
                    # Create dataframe for visualization
                    categories_df = pd.DataFrame({
                        "Category": list(pci_categories.keys()),
                        "Findings": list(pci_categories.values())
                    })
                    
                    # Sort by number of findings
                    categories_df = categories_df.sort_values("Findings", ascending=False)
                    
                    # Create bar chart
                    fig = px.bar(
                        categories_df,
                        x="Category",
                        y="Findings",
                        title="Findings by PCI DSS Category",
                        color="Findings",
                        color_continuous_scale=["green", "yellow", "red"],
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Create pie chart of findings by risk level
                    risk_counts = {
                        "High": scan_results.get("high_risk_count", 0),
                        "Medium": scan_results.get("medium_risk_count", 0),
                        "Low": scan_results.get("low_risk_count", 0)
                    }
                    
                    # Only create pie chart if there are findings
                    if sum(risk_counts.values()) > 0:
                        risk_df = pd.DataFrame({
                            "Risk Level": list(risk_counts.keys()),
                            "Count": list(risk_counts.values())
                        })
                        
                        fig2 = px.pie(
                            risk_df,
                            values="Count",
                            names="Risk Level",
                            title="Findings by Risk Level",
                            color="Risk Level",
                            color_discrete_map={
                                "High": "red",
                                "Medium": "orange",
                                "Low": "green"
                            },
                            height=400
                        )
                        st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("No visualization data available")
            
            # Download report section after tabs
            st.markdown("---")
            st.subheader("Download Report")
            
            # Generate report if PDF format selected
            if "PDF Report" in scan_results.get("output_formats", []):
                try:
                    # Generate PDF report
                    report_data = generate_pcidss_report(scan_results)
                    
                    # Create download button
                    report_filename = f"pcidss_report_{datetime.now().strftime('%Y%m%d')}.pdf"
                    st.download_button(
                        "📥 Download PCI DSS Compliance Report (PDF)",
                        data=report_data,
                        file_name=report_filename,
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"Error generating report: {str(e)}")
        else:
            # Show instructions when no scan results available
            st.info(
                "Configure scan options in the left panel and click 'Start PCI DSS Compliance Scan' to begin. "
                "Results will appear here after scanning is complete."
            )

if __name__ == "__main__":
    main()