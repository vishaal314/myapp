"""
PCI DSS Scanner Fix for Integration

This is the fixed PCI DSS scanner code that will be integrated into the main app.py.
This version uses the successful two-column layout that properly displays the repository URL field.
"""

def get_pcidss_fix_code():
    """Returns the fixed PCI DSS scanner code for app.py integration"""
    
    return """                    elif scan_type == _("scan.pcidss"):
                        # Import PCI DSS scanner components
                        from services.pcidss_scanner import PCIDSSScanner
                        from services.report_generator import generate_report
                        from services.report_templates.pcidss_report_template import generate_pcidss_report
                        
                        # Initialize uploaded_files variable to prevent errors
                        uploaded_files = []
                        
                        # PCI DSS scanner UI with enhanced design
                        st.title(_("scan.pcidss_title", "PCI DSS Compliance Scanner"))
                        
                        # Display enhanced description with clear value proposition
                        st.write(_(
                            "scan.pcidss_description", 
                            "Scan your codebase for Payment Card Industry Data Security Standard (PCI DSS) compliance issues. "
                            "This scanner identifies security vulnerabilities, exposures, and configuration issues that could "
                            "impact your ability to securely process, store, or transmit credit card data."
                        ))
                        
                        # Add more detailed info about what PCI DSS scanning does
                        st.info(_(
                            "scan.pcidss_info",
                            "PCI DSS scanning analyzes your code against the 12 PCI DSS requirements to identify "
                            "potential compliance issues. The scanner detects insecure coding patterns, vulnerable "
                            "dependencies, and configurations that could put cardholder data at risk."
                        ))
                        
                        # Show trial status notice
                        st.markdown('''
                        <div style="padding: 10px; border-radius: 5px; background-color: #f0f2f6; margin-bottom: 20px;">
                            <span style="font-weight: bold;">Free Trial:</span> 3 days left
                        </div>
                        ''', unsafe_allow_html=True)
                        
                        # Create two columns for better UI organization
                        left_col, right_col = st.columns([1, 1.5])
                        
                        # Left column for configuration
                        with left_col:
                            # 1. Region Selection
                            st.subheader("1. Region Selection")
                            region_options = ["Global", "Netherlands", "Germany", "France", "Belgium"]
                            selected_region = st.selectbox(
                                "Select Region:",
                                region_options,
                                index=0,
                                key="pcidss_region_fixed"
                            )
                            
                            # 2. Source Configuration
                            st.subheader("2. Source Configuration")
                            source_type = st.radio(
                                "Select Source Type:",
                                ["Repository URL", "Upload Files"],
                                key="pcidss_source_type_fixed"
                            )
                            
                            # Repository Details
                            if source_type == "Repository URL":
                                # Repository provider selection
                                repo_provider = st.radio(
                                    "Repository Provider:",
                                    ["GitHub", "BitBucket", "Azure DevOps"],
                                    horizontal=True,
                                    key="pcidss_repo_provider_fixed"
                                )
                                
                                # Repository URL input field
                                st.markdown("**Repository URL:** (Required)")
                                repo_url = st.text_input(
                                    "Enter the repository URL",
                                    placeholder=f"Example: https://{repo_provider.lower()}.com/username/repo",
                                    key="pcidss_repo_url_fixed"
                                )
                                
                                # Branch field
                                st.markdown("**Branch:**")
                                branch = st.text_input(
                                    "Branch name",
                                    value="main",
                                    key="pcidss_branch_fixed"
                                )
                                
                                # Private repository options
                                with st.expander("Private Repository?"):
                                    use_token = st.checkbox("Use access token", key="pcidss_use_token")
                                    
                                    if use_token:
                                        token = st.text_input(
                                            "Access Token:",
                                            type="password",
                                            key="pcidss_token"
                                        )
                                    else:
                                        token = None
                            else:
                                # File upload
                                uploaded_files = st.file_uploader(
                                    "Upload code files to scan:",
                                    accept_multiple_files=True,
                                    key="pcidss_files_fixed"
                                )
                                
                                if uploaded_files:
                                    st.success(f"Uploaded {len(uploaded_files)} files")
                                
                                # Set variables to default values for file mode
                                repo_url = None
                                branch = "main"
                                token = None
                            
                            # 3. Scan Options
                            st.subheader("3. Scan Options")
                            
                            # Create columns for options
                            opt_col1, opt_col2 = st.columns(2)
                            
                            with opt_col1:
                                scan_dependencies = st.checkbox(
                                    "Scan Dependencies",
                                    value=True,
                                    key="pcidss_deps_fixed"
                                )
                                scan_iac = st.checkbox(
                                    "Scan Infrastructure",
                                    value=True,
                                    key="pcidss_iac_fixed"
                                )
                            
                            with opt_col2:
                                scan_secrets = st.checkbox(
                                    "Detect Secrets",
                                    value=True,
                                    key="pcidss_secrets_fixed"
                                )
                            
                            # PCI DSS Requirements filter
                            with st.expander("PCI DSS Requirements Filter"):
                                st.markdown("**Select specific requirements to focus on:**")
                                
                                # Two columns for requirements selection
                                req_col1, req_col2 = st.columns(2)
                                
                                with req_col1:
                                    req1 = st.checkbox("Req 1: Network Security", key="pcidss_req1_fixed")
                                    req2 = st.checkbox("Req 2: Default Settings", key="pcidss_req2_fixed")
                                    req3 = st.checkbox("Req 3: Data Storage", key="pcidss_req3_fixed")
                                    req4 = st.checkbox("Req 4: Encryption", key="pcidss_req4_fixed")
                                    req5 = st.checkbox("Req 5: Malware", key="pcidss_req5_fixed")
                                    req6 = st.checkbox("Req 6: Systems", key="pcidss_req6_fixed")
                                
                                with req_col2:
                                    req7 = st.checkbox("Req 7: Access Control", key="pcidss_req7_fixed")
                                    req8 = st.checkbox("Req 8: Authentication", key="pcidss_req8_fixed")
                                    req9 = st.checkbox("Req 9: Physical Access", key="pcidss_req9_fixed")
                                    req10 = st.checkbox("Req 10: Monitoring", key="pcidss_req10_fixed")
                                    req11 = st.checkbox("Req 11: Testing", key="pcidss_req11_fixed")
                                    req12 = st.checkbox("Req 12: Policy", key="pcidss_req12_fixed")
                            
                            # 4. Output Format
                            st.subheader("4. Output Format")
                            output_formats = st.multiselect(
                                "Select output formats:",
                                ["PDF Report", "CSV Export", "JSON Export"],
                                default=["PDF Report"],
                                key="pcidss_output_fixed"
                            )
                            
                            # 5. Start Scan
                            st.subheader("5. Start Scan")
                            scan_button = st.button(
                                "Start PCI DSS Scan",
                                type="primary",
                                use_container_width=True,
                                key="pcidss_scan_button_fixed"
                            )
                        
                        # Right column for results
                        with right_col:
                            st.subheader("Scan Results")
                            
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
                                    scan_progress = st.progress(0)
                                    scan_status = st.empty()
                                    scan_status.text("Initializing scan...")
                                    
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
                                    scan_scope = ["SAST (Static Application Security Testing)"]
                                    if scan_dependencies:
                                        scan_scope.append("SCA (Software Composition Analysis)")
                                    if scan_iac:
                                        scan_scope.append("IaC (Infrastructure-as-Code) Scanning")
                                    if scan_secrets:
                                        scan_scope.append("Secrets Detection")
                                    
                                    try:
                                        # Initialize scanner
                                        scanner = PCIDSSScanner(
                                            region=selected_region,
                                            progress_callback=lambda current, total, message: (
                                                scan_progress.progress(current / total),
                                                scan_status.text(message)
                                            )
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
                                        
                                        # Run the scan
                                        with st.spinner("Running PCI DSS compliance scan..."):
                                            scan_results = scanner.scan(**scan_params)
                                        
                                        # Store results in session state
                                        st.session_state.pcidss_scan_results = scan_results
                                        
                                        # Add to scan history
                                        if 'history' not in st.session_state:
                                            st.session_state.history = {}
                                        
                                        history_id = f"pcidss_{int(time.time())}"
                                        st.session_state.history[history_id] = {
                                            'type': 'PCI DSS',
                                            'data': scan_results,
                                            'timestamp': datetime.now().isoformat(),
                                            'repository': repo_url if repo_url else "File Upload"
                                        }
                                        
                                        # Show completion message
                                        scan_progress.progress(1.0)
                                        scan_status.success("Scan completed successfully!")
                                        
                                        # Force rerun to update UI
                                        st.rerun()
                                    
                                    except Exception as e:
                                        scan_status.error(f"Error scanning: {str(e)}")
                                        st.exception(e)
                            
                            # Display results if available
                            if 'pcidss_scan_results' in st.session_state:
                                # Create tabs for results
                                results_tabs = st.tabs(["Summary", "Findings", "Visualizations"])
                                
                                # Get results
                                scan_results = st.session_state.pcidss_scan_results
                                
                                # Summary tab
                                with results_tabs[0]:
                                    # Show source information
                                    if source_type == "Repository URL":
                                        st.write(f"**Repository:** {scan_results.get('repo_url')}")
                                        st.write(f"**Branch:** {scan_results.get('branch', 'main')}")
                                    else:
                                        st.write("**Source:** Uploaded Files")
                                    
                                    st.write(f"**Region:** {scan_results.get('region', 'Global')}")
                                    
                                    # Display metrics
                                    metrics_cols = st.columns(4)
                                    
                                    # Get metric values
                                    compliance_score = scan_results.get("compliance_score", 0)
                                    high_risk = scan_results.get("high_risk_count", 0)
                                    medium_risk = scan_results.get("medium_risk_count", 0)
                                    low_risk = scan_results.get("low_risk_count", 0)
                                    
                                    # Color coding
                                    if compliance_score >= 80:
                                        compliance_status = "✓ Good"
                                        delta_color = "normal"
                                    elif compliance_score >= 60:
                                        compliance_status = "⚠ Warning"
                                        delta_color = "off"
                                    else:
                                        compliance_status = "❌ Critical"
                                        delta_color = "inverse"
                                    
                                    # Display metrics
                                    with metrics_cols[0]:
                                        st.metric(
                                            "Compliance Score",
                                            f"{compliance_score}%",
                                            delta=compliance_status,
                                            delta_color=delta_color
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
                                            delta_color="inverse"
                                        )
                                    
                                    with metrics_cols[3]:
                                        st.metric(
                                            "Low Risk",
                                            low_risk,
                                            delta=None,
                                            delta_color="inverse"
                                        )
                                    
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
                                
                                # Findings tab
                                with results_tabs[1]:
                                    st.subheader("Detailed Findings")
                                    findings = scan_results.get("findings", [])
                                    
                                    if findings:
                                        # Create dataframe
                                        findings_df = pd.DataFrame(findings)
                                        
                                        # Ensure required columns exist
                                        required_cols = ["type", "location", "risk_level", "pci_requirement", "description"]
                                        for col in required_cols:
                                            if col not in findings_df.columns:
                                                findings_df[col] = ""
                                        
                                        # Select and rename columns
                                        display_df = findings_df[required_cols].rename(columns={
                                            "type": "Type",
                                            "location": "Location",
                                            "risk_level": "Risk Level",
                                            "pci_requirement": "PCI Requirement",
                                            "description": "Description"
                                        })
                                        
                                        # Style based on risk level
                                        def highlight_risk(val):
                                            if val == "High":
                                                return 'background-color: #FFCCCC'
                                            elif val == "Medium":
                                                return 'background-color: #FFFFCC'
                                            elif val == "Low":
                                                return 'background-color: #CCFFCC'
                                            return ''
                                        
                                        # Apply styling
                                        styled_df = display_df.style.applymap(highlight_risk, subset=['Risk Level'])
                                        
                                        # Display dataframe
                                        st.dataframe(styled_df, use_container_width=True)
                                        
                                        # Export option
                                        if "CSV Export" in output_formats:
                                            st.download_button(
                                                "Export to CSV",
                                                data=display_df.to_csv(index=False),
                                                file_name=f"pcidss_findings_{datetime.now().strftime('%Y%m%d')}.csv",
                                                mime="text/csv",
                                                key="pcidss_csv_download"
                                            )
                                    else:
                                        st.info("No findings detected in the scan")
                                
                                # Visualizations tab
                                with results_tabs[2]:
                                    st.subheader("Compliance Visualizations")
                                    
                                    # PCI categories visualization
                                    pci_categories = scan_results.get("pci_categories", {})
                                    
                                    if pci_categories:
                                        # Create bar chart dataframe
                                        categories_df = pd.DataFrame({
                                            "Category": list(pci_categories.keys()),
                                            "Findings": list(pci_categories.values())
                                        })
                                        
                                        # Sort by findings count
                                        categories_df = categories_df.sort_values("Findings", ascending=False)
                                        
                                        # Create and display chart
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
                                        
                                        # Risk level distribution visualization
                                        risk_counts = {
                                            "High": high_risk,
                                            "Medium": medium_risk,
                                            "Low": low_risk
                                        }
                                        
                                        # Only show pie chart if there are findings
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
                                
                                # Download report section
                                st.markdown("---")
                                st.subheader("Download Report")
                                
                                # Generate report if PDF selected
                                if "PDF Report" in output_formats:
                                    try:
                                        # Generate report
                                        report_data = generate_pcidss_report(scan_results)
                                        
                                        # Create download button
                                        report_filename = f"pcidss_report_{datetime.now().strftime('%Y%m%d')}.pdf"
                                        st.download_button(
                                            "📥 Download PCI DSS Compliance Report",
                                            data=report_data,
                                            file_name=report_filename,
                                            mime="application/pdf",
                                            key="pcidss_pdf_download"
                                        )
                                    except Exception as e:
                                        st.error(f"Error generating report: {str(e)}")
                            else:
                                # Instructions when no scan has been run
                                st.info(
                                    "Configure scan options on the left and click 'Start PCI DSS Scan' to begin scanning. "
                                    "Results will appear here after the scan is complete."
                                )"""