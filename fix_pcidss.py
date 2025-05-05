"""
PCI DSS Scanner UI Fix

This is a standalone version of the PCI DSS scanner with a completely reworked UI
that ensures the repository URL input field is properly displayed.
"""

import streamlit as st
import pandas as pd 
import plotly.express as px
import time
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="PCI DSS Scanner",
    page_icon="🔒",
    layout="wide"
)

# Define mock scanner for testing
class MockPCIDSSScanner:
    """Mock PCI DSS Scanner for UI testing"""
    
    def __init__(self, region="Global", progress_callback=None):
        self.region = region
        self.progress_callback = progress_callback
    
    def scan(self, **kwargs):
        """Simulate scanning with progress updates"""
        # Extract parameters
        repo_url = kwargs.get('repo_url', '')
        branch = kwargs.get('branch', 'main')
        
        # Simulate progress
        total_steps = 10
        for i in range(1, total_steps + 1):
            if self.progress_callback:
                self.progress_callback(i, total_steps, f"Processing step {i}/{total_steps}...")
            time.sleep(0.3)
        
        # Return mock results
        return {
            "status": "success",
            "repo_url": repo_url,
            "branch": branch,
            "region": self.region,
            "compliance_score": 75,
            "high_risk_count": 2,
            "medium_risk_count": 3,
            "low_risk_count": 5,
            "findings": [
                {
                    "type": "Insecure Data Storage",
                    "location": "app/payments.py:45",
                    "risk_level": "High",
                    "pci_requirement": "3.4",
                    "description": "Credit card number stored in plaintext"
                },
                {
                    "type": "Weak Cryptography",
                    "location": "utils/encryption.py:67",
                    "risk_level": "Medium",
                    "pci_requirement": "4.1",
                    "description": "Using outdated encryption algorithm (MD5)"
                },
                {
                    "type": "Missing Authentication",
                    "location": "api/endpoints.py:128",
                    "risk_level": "High",
                    "pci_requirement": "8.2",
                    "description": "Payment endpoint missing proper authentication"
                }
            ],
            "pci_categories": {
                "Data Protection": 1,
                "Authentication": 1,
                "Network Security": 0,
                "Secure Coding": 1
            },
            "recommendations": [
                "Encrypt all stored cardholder data using strong cryptography",
                "Implement proper authentication for all payment-related API endpoints",
                "Update encryption algorithms to modern standards (AES-256 or better)"
            ]
        }

# Main function
def main():
    # Page header
    st.title("PCI DSS Compliance Scanner")
    
    st.write(
        "Scan your codebase for Payment Card Industry Data Security Standard (PCI DSS) compliance issues. "
        "This scanner identifies security vulnerabilities that could impact your ability to securely handle payment data."
    )
    
    # Info box with additional details
    st.info(
        "This scanner detects issues related to the PCI DSS requirements including insecure data storage, "
        "weak encryption, authentication problems, and more."
    )
    
    # Create two columns for layout
    config_col, results_col = st.columns([1, 1.5])
    
    # Configuration column (LEFT SIDE)
    with config_col:
        st.markdown("## Configuration")
        
        # 1. Region Selection
        st.subheader("1. Region Selection")
        region_options = ["Global", "Netherlands", "Germany", "France", "Belgium"]
        selected_region = st.selectbox(
            "Select Region:",
            region_options,
            index=0,
            key="region"
        )
        
        # 2. Source Selection
        st.subheader("2. Source Selection")
        source_type = st.radio(
            "Select source type:",
            ["Repository URL", "Upload Files"],
            key="source_type"
        )
        
        # 3. Source Details
        st.subheader("3. Source Details")
        
        if source_type == "Repository URL":
            # Repository provider selection
            repo_provider = st.radio(
                "Repository Provider:",
                ["GitHub", "BitBucket", "Azure DevOps"],
                horizontal=True,
                key="repo_provider"
            )
            
            # Repository URL input field with clear labeling
            st.markdown("**Repository URL:** (Required)")
            repo_url = st.text_input(
                "Repository URL",
                placeholder=f"Example: https://{repo_provider.lower()}.com/username/repo",
                key="repo_url"
            )
            
            # Branch input field
            st.markdown("**Branch:**")
            branch = st.text_input(
                "Branch",
                value="main",
                key="branch"
            )
            
            # For file upload option, set placeholder
            uploaded_files = []
        else:
            # File upload interface
            st.markdown("**Upload Files:**")
            uploaded_files = st.file_uploader(
                "Upload code files:",
                accept_multiple_files=True,
                key="files"
            )
            
            if uploaded_files:
                st.success(f"Uploaded {len(uploaded_files)} files")
            
            # For repository option, set placeholders
            repo_url = ""
            branch = "main"
        
        # 4. Scan Options
        st.subheader("4. Scan Options")
        
        # Use two columns for options
        opt_col1, opt_col2 = st.columns(2)
        
        with opt_col1:
            scan_deps = st.checkbox("Dependencies", value=True, key="scan_deps")
            scan_iac = st.checkbox("Infrastructure", value=True, key="scan_iac")
        
        with opt_col2:
            scan_secrets = st.checkbox("Secrets", value=True, key="scan_secrets")
        
        # PCI DSS Requirements filter
        with st.expander("PCI DSS Requirements Filter"):
            st.markdown("**Select specific requirements to focus on:**")
            
            # Create columns for the requirements
            req_col1, req_col2 = st.columns(2)
            
            with req_col1:
                req1 = st.checkbox("Req 1: Network Security", key="req1")
                req2 = st.checkbox("Req 2: Default Settings", key="req2")
                req3 = st.checkbox("Req 3: Stored Data", key="req3")
                req4 = st.checkbox("Req 4: Encryption", key="req4")
                req5 = st.checkbox("Req 5: Malware", key="req5")
                req6 = st.checkbox("Req 6: Secure Systems", key="req6")
            
            with req_col2:
                req7 = st.checkbox("Req 7: Access Control", key="req7")
                req8 = st.checkbox("Req 8: Authentication", key="req8")
                req9 = st.checkbox("Req 9: Physical Security", key="req9")
                req10 = st.checkbox("Req 10: Monitoring", key="req10")
                req11 = st.checkbox("Req 11: Testing", key="req11")
                req12 = st.checkbox("Req 12: Policy", key="req12")
        
        # 5. Output Format
        st.subheader("5. Output Format")
        output_formats = st.multiselect(
            "Select output formats:",
            ["PDF Report", "CSV Export", "JSON Export"],
            default=["PDF Report"],
            key="formats"
        )
        
        # 6. Start Scan Button
        st.subheader("6. Start Scan")
        scan_button = st.button(
            "Start PCI DSS Compliance Scan",
            type="primary",
            use_container_width=True,
            key="scan_button"
        )
    
    # Results column (RIGHT SIDE)
    with results_col:
        st.markdown("## Results")
        
        # Process scan button click
        if scan_button:
            # Validate inputs
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
                
                # Create requirements dictionary
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
                
                # Create scan scope
                scan_scope = ["SAST (Static Application Security Testing)"]
                if scan_deps:
                    scan_scope.append("SCA (Software Composition Analysis)")
                if scan_iac:
                    scan_scope.append("IaC (Infrastructure-as-Code) Scanning")
                if scan_secrets:
                    scan_scope.append("Secrets Detection")
                
                try:
                    # Progress callback
                    def update_progress(current, total, message):
                        progress_bar.progress(current / total)
                        status_text.text(message)
                    
                    # Initialize scanner
                    scanner = MockPCIDSSScanner(
                        region=selected_region,
                        progress_callback=update_progress
                    )
                    
                    # Prepare scan parameters
                    scan_params = {
                        "repo_url": repo_url,
                        "branch": branch,
                        "scan_scope": scan_scope,
                        "requirements": requirements,
                        "output_formats": output_formats
                    }
                    
                    # Run scan
                    with st.spinner("Running PCI DSS compliance scan..."):
                        scan_results = scanner.scan(**scan_params)
                    
                    # Save results in session state
                    st.session_state.scan_results = scan_results
                    
                    # Update progress
                    progress_bar.progress(1.0)
                    status_text.success("Scan completed successfully!")
                    
                    # Rerun to refresh UI
                    st.rerun()
                
                except Exception as e:
                    status_text.error(f"Error during scan: {str(e)}")
                    st.exception(e)
        
        # Display results if available
        if 'scan_results' in st.session_state:
            scan_results = st.session_state.scan_results
            
            # Create tabs for results display
            summary_tab, details_tab, visuals_tab = st.tabs(["Summary", "Detailed Findings", "Visualizations"])
            
            # Summary tab
            with summary_tab:
                st.subheader("Scan Results Summary")
                
                # Source information
                st.write(f"**Repository:** {scan_results.get('repo_url')}")
                st.write(f"**Branch:** {scan_results.get('branch')}")
                st.write(f"**Region:** {scan_results.get('region')}")
                
                # Results metrics
                col1, col2, col3, col4 = st.columns(4)
                
                # Get metrics
                compliance_score = scan_results.get("compliance_score", 0)
                high_risk = scan_results.get("high_risk_count", 0)
                medium_risk = scan_results.get("medium_risk_count", 0)
                low_risk = scan_results.get("low_risk_count", 0)
                
                # Display metrics
                with col1:
                    st.metric("Compliance Score", f"{compliance_score}%")
                
                with col2:
                    st.metric("High Risk", high_risk, delta=None, delta_color="inverse")
                
                with col3:
                    st.metric("Medium Risk", medium_risk, delta=None, delta_color="inverse")
                
                with col4:
                    st.metric("Low Risk", low_risk, delta=None, delta_color="inverse")
                
                # Top recommendations
                st.subheader("Key Recommendations")
                recommendations = scan_results.get("recommendations", [])
                
                if recommendations:
                    for i, rec in enumerate(recommendations):
                        st.markdown(f"**{i+1}.** {rec}")
                else:
                    st.info("No recommendations available")
            
            # Details tab
            with details_tab:
                st.subheader("Detailed Findings")
                findings = scan_results.get("findings", [])
                
                if findings:
                    # Create dataframe
                    findings_df = pd.DataFrame(findings)
                    
                    # Apply styling
                    def highlight_risk(val):
                        if val == "High":
                            return 'background-color: #FFCCCC'
                        elif val == "Medium":
                            return 'background-color: #FFFFCC'
                        elif val == "Low":
                            return 'background-color: #CCFFCC'
                        return ''
                    
                    # Style and display dataframe
                    styled_df = findings_df.style.applymap(highlight_risk, subset=['risk_level'])
                    st.dataframe(styled_df, use_container_width=True)
                    
                    # Export options
                    st.download_button(
                        "Export to CSV",
                        data=findings_df.to_csv(index=False),
                        file_name=f"pcidss_findings_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No findings detected in the scan")
            
            # Visualizations tab
            with visuals_tab:
                st.subheader("PCI DSS Compliance Visualizations")
                
                # Category data
                pci_categories = scan_results.get("pci_categories", {})
                
                if pci_categories:
                    # Create dataframe
                    categories_df = pd.DataFrame({
                        "Category": list(pci_categories.keys()),
                        "Findings": list(pci_categories.values())
                    })
                    
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
                    
                    # Risk distribution
                    risk_counts = {
                        "High": scan_results.get("high_risk_count", 0),
                        "Medium": scan_results.get("medium_risk_count", 0),
                        "Low": scan_results.get("low_risk_count", 0)
                    }
                    
                    # Create pie chart
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
        else:
            st.info(
                "Configure scan options in the left panel and click 'Start PCI DSS Compliance Scan' "
                "to begin. Results will appear here after scanning is complete."
            )

if __name__ == "__main__":
    main()