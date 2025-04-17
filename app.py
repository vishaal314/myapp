import streamlit as st
import pandas as pd
import plotly.express as px
import os
import uuid
from datetime import datetime
import json
import base64
from io import BytesIO

from services.code_scanner import CodeScanner
from services.blob_scanner import BlobScanner
from services.results_aggregator import ResultsAggregator
from services.report_generator import generate_report
from services.auth import authenticate, is_authenticated, logout
from utils.gdpr_rules import REGIONS, get_region_rules

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'role' not in st.session_state:
    st.session_state.role = None
if 'current_scan_id' not in st.session_state:
    st.session_state.current_scan_id = None
if 'scan_results' not in st.session_state:
    st.session_state.scan_results = None

# Set page config
st.set_page_config(
    page_title="GDPR Scan Engine",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Authentication sidebar
with st.sidebar:
    st.title("GDPR Scan Engine")
    
    if not st.session_state.logged_in:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.button("Login")
        
        if login_button:
            user_data = authenticate(username, password)
            if user_data:
                st.session_state.logged_in = True
                st.session_state.username = user_data["username"]
                st.session_state.role = user_data["role"]
                st.success(f"Logged in as {username}")
                st.rerun()
            else:
                st.error("Invalid credentials")
    else:
        st.success(f"Logged in as {st.session_state.username}")
        st.write(f"Role: {st.session_state.role}")
        if st.button("Logout"):
            logout()
            st.rerun()
    
    st.markdown("---")
    st.write("© 2023 GDPR Scan Engine")

# Main content
if not st.session_state.logged_in:
    st.title("Welcome to GDPR Scan Engine")
    st.write("Please login to access the dashboard")
    
    # Show product info
    st.subheader("About GDPR Scan Engine")
    st.write("""
    Our GDPR Scan Engine identifies and reports on GDPR-relevant Personally Identifiable Information (PII) 
    across multiple sources, with a focus on Dutch-specific rules (UAVG), consent management, and legal 
    basis documentation.
    """)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🔍 PII Detection")
        st.write("Scan code, documents, and more for personal information")
    with col2:
        st.markdown("### 📊 Risk Assessment")
        st.write("Get detailed reports on GDPR compliance risks")
    with col3:
        st.markdown("### 🇳🇱 Region-Specific")
        st.write("Support for Dutch GDPR regulations (UAVG)")

else:
    # Initialize aggregator
    results_aggregator = ResultsAggregator()
    
    # Navigation
    nav_options = ["Dashboard", "New Scan", "Scan History", "Reports"]
    selected_nav = st.sidebar.radio("Navigation", nav_options)
    
    if selected_nav == "Dashboard":
        st.title("GDPR Compliance Dashboard")
        
        # Summary metrics
        all_scans = results_aggregator.get_all_scans(st.session_state.username)
        
        if all_scans and len(all_scans) > 0:
            total_scans = len(all_scans)
            total_pii = sum(scan.get('total_pii_found', 0) for scan in all_scans)
            high_risk_items = sum(scan.get('high_risk_count', 0) for scan in all_scans)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Scans", total_scans)
            col2.metric("Total PII Found", total_pii)
            col3.metric("High Risk Items", high_risk_items)
            
            # Recent scans
            st.subheader("Recent Scans")
            recent_scans = all_scans[-5:] if len(all_scans) > 5 else all_scans
            recent_scans_df = pd.DataFrame(recent_scans)
            if 'timestamp' in recent_scans_df.columns:
                recent_scans_df['timestamp'] = pd.to_datetime(recent_scans_df['timestamp'])
                recent_scans_df = recent_scans_df.sort_values('timestamp', ascending=False)
            
            if not recent_scans_df.empty:
                display_cols = ['scan_id', 'scan_type', 'timestamp', 'total_pii_found', 'high_risk_count', 'region']
                display_cols = [col for col in display_cols if col in recent_scans_df.columns]
                st.dataframe(recent_scans_df[display_cols])
            
                # PII Types Distribution
                st.subheader("PII Types Distribution")
                
                # Aggregate PII types from all scans
                pii_counts = {}
                for scan in all_scans:
                    if 'pii_types' in scan:
                        for pii_type, count in scan['pii_types'].items():
                            pii_counts[pii_type] = pii_counts.get(pii_type, 0) + count
                
                if pii_counts:
                    pii_df = pd.DataFrame(list(pii_counts.items()), columns=['PII Type', 'Count'])
                    fig = px.bar(pii_df, x='PII Type', y='Count', color='PII Type')
                    st.plotly_chart(fig, use_container_width=True)
                
                # Risk Level Distribution
                st.subheader("Risk Level Distribution")
                risk_counts = {'Low': 0, 'Medium': 0, 'High': 0}
                for scan in all_scans:
                    if 'risk_levels' in scan:
                        for risk, count in scan['risk_levels'].items():
                            if risk in risk_counts:
                                risk_counts[risk] += count
                
                risk_df = pd.DataFrame(list(risk_counts.items()), columns=['Risk Level', 'Count'])
                fig = px.pie(risk_df, values='Count', names='Risk Level', color='Risk Level',
                             color_discrete_map={'Low': 'green', 'Medium': 'orange', 'High': 'red'})
                st.plotly_chart(fig, use_container_width=True)
                
                # Scan Types
                st.subheader("Scan Types")
                scan_type_counts = {}
                for scan in all_scans:
                    scan_type = scan.get('scan_type', 'Unknown')
                    scan_type_counts[scan_type] = scan_type_counts.get(scan_type, 0) + 1
                
                scan_type_df = pd.DataFrame(list(scan_type_counts.items()), columns=['Scan Type', 'Count'])
                fig = px.bar(scan_type_df, x='Scan Type', y='Count', color='Scan Type')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No scan data available yet. Start a new scan to see results.")
        else:
            st.info("No scan data available yet. Start a new scan to see results.")
    
    elif selected_nav == "New Scan":
        st.title("Start a New GDPR Scan")
        
        # Scan configuration form
        scan_type = st.selectbox("Scan Type", ["Code Scan", "Document Scan"])
        region = st.selectbox("Region", list(REGIONS.keys()))
        
        # Additional configurations
        with st.expander("Advanced Configuration"):
            include_comments = st.checkbox("Include Comments in Code Scan", value=True)
            
            if scan_type == "Code Scan":
                file_extensions = st.multiselect("File Extensions", 
                                               [".py", ".js", ".java", ".php", ".cs", ".go", ".rb", ".ts", ".html", ".xml", ".json"],
                                               default=[".py", ".js", ".java", ".php"])
            else:  # Document Scan
                file_types = st.multiselect("Document Types",
                                          ["PDF", "DOCX", "TXT", "CSV", "XLSX"],
                                          default=["PDF", "DOCX", "TXT"])
        
        # File uploader
        uploaded_files = st.file_uploader(
            f"Upload {'Code Files' if scan_type == 'Code Scan' else 'Documents'}", 
            accept_multiple_files=True
        )
        
        # Scan button
        if st.button("Start Scan"):
            if not uploaded_files:
                st.error("Please upload at least one file to scan.")
            else:
                # Generate a unique scan ID
                scan_id = str(uuid.uuid4())
                st.session_state.current_scan_id = scan_id
                
                # Show progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Save uploaded files to temp directory
                temp_dir = f"temp_{scan_id}"
                os.makedirs(temp_dir, exist_ok=True)
                
                file_paths = []
                for i, uploaded_file in enumerate(uploaded_files):
                    progress = (i + 1) / (2 * len(uploaded_files))
                    progress_bar.progress(progress)
                    status_text.text(f"Processing file {i+1}/{len(uploaded_files)}: {uploaded_file.name}")
                    
                    # Save file
                    file_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    file_paths.append(file_path)
                
                # Initialize scanner based on type
                if scan_type == "Code Scan":
                    scanner = CodeScanner(
                        extensions=file_extensions if 'file_extensions' in locals() else [".py", ".js", ".java", ".php"],
                        include_comments=include_comments,
                        region=region
                    )
                else:  # Document Scan
                    scanner = BlobScanner(
                        file_types=file_types if 'file_types' in locals() else ["PDF", "DOCX", "TXT"],
                        region=region
                    )
                
                # Run scan
                scan_results = []
                for i, file_path in enumerate(file_paths):
                    progress = 0.5 + (i + 1) / (2 * len(file_paths))
                    progress_bar.progress(progress)
                    status_text.text(f"Scanning file {i+1}/{len(file_paths)}: {os.path.basename(file_path)}")
                    
                    try:
                        result = scanner.scan_file(file_path)
                        scan_results.append(result)
                    except Exception as e:
                        st.error(f"Error scanning {os.path.basename(file_path)}: {str(e)}")
                
                # Aggregate and save results
                timestamp = datetime.now().isoformat()
                
                # Count PIIs by type and risk level
                pii_types = {}
                risk_levels = {"Low": 0, "Medium": 0, "High": 0}
                total_pii_found = 0
                high_risk_count = 0
                
                for result in scan_results:
                    for pii_item in result.get('pii_found', []):
                        pii_type = pii_item.get('type', 'Unknown')
                        risk_level = pii_item.get('risk_level', 'Medium')
                        
                        pii_types[pii_type] = pii_types.get(pii_type, 0) + 1
                        risk_levels[risk_level] = risk_levels.get(risk_level, 0) + 1
                        total_pii_found += 1
                        
                        if risk_level == "High":
                            high_risk_count += 1
                
                # Create aggregated scan result
                aggregated_result = {
                    'scan_id': scan_id,
                    'username': st.session_state.username,
                    'timestamp': timestamp,
                    'scan_type': scan_type,
                    'region': region,
                    'file_count': len(file_paths),
                    'total_pii_found': total_pii_found,
                    'high_risk_count': high_risk_count,
                    'pii_types': pii_types,
                    'risk_levels': risk_levels,
                    'detailed_results': scan_results
                }
                
                # Save to database
                results_aggregator.save_scan_result(aggregated_result)
                
                # Store in session state for immediate display
                st.session_state.scan_results = aggregated_result
                
                # Clean up temp files
                for file_path in file_paths:
                    try:
                        os.remove(file_path)
                    except:
                        pass
                
                try:
                    os.rmdir(temp_dir)
                except:
                    pass
                
                # Show completion
                progress_bar.progress(1.0)
                status_text.text("Scan completed!")
                
                st.success(f"Scan completed successfully! Scan ID: {scan_id}")
                st.info("Navigate to 'Scan History' to view detailed results")
        
    elif selected_nav == "Scan History":
        st.title("Scan History")
        
        # Get all scans for the user
        all_scans = results_aggregator.get_all_scans(st.session_state.username)
        
        if all_scans and len(all_scans) > 0:
            # Convert to DataFrame for display
            scans_df = pd.DataFrame(all_scans)
            if 'timestamp' in scans_df.columns:
                scans_df['timestamp'] = pd.to_datetime(scans_df['timestamp'])
                scans_df = scans_df.sort_values('timestamp', ascending=False)
            
            # Select columns to display
            display_cols = ['scan_id', 'timestamp', 'scan_type', 'region', 'file_count', 'total_pii_found', 'high_risk_count']
            display_cols = [col for col in display_cols if col in scans_df.columns]
            
            # Rename columns for better display
            display_df = scans_df[display_cols].copy()
            column_map = {
                'scan_id': 'Scan ID',
                'timestamp': 'Date & Time',
                'scan_type': 'Scan Type',
                'region': 'Region',
                'file_count': 'Files Scanned',
                'total_pii_found': 'Total PII Found',
                'high_risk_count': 'High Risk Items'
            }
            display_df.rename(columns=column_map, inplace=True)
            
            # Display scan history table
            st.dataframe(display_df, use_container_width=True)
            
            # Allow user to select a scan to view details
            selected_scan_id = st.selectbox(
                "Select a scan to view details",
                options=scans_df['scan_id'].tolist(),
                format_func=lambda x: f"{x} - {scans_df[scans_df['scan_id']==x]['timestamp'].iloc[0]} ({scans_df[scans_df['scan_id']==x]['scan_type'].iloc[0]})"
            )
            
            if selected_scan_id:
                # Get the selected scan details
                selected_scan = results_aggregator.get_scan_by_id(selected_scan_id)
                
                if selected_scan:
                    st.subheader(f"Scan Details: {selected_scan_id}")
                    
                    # Display metadata
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Scan Type", selected_scan.get('scan_type', 'N/A'))
                    col2.metric("Region", selected_scan.get('region', 'N/A'))
                    col3.metric("Files Scanned", selected_scan.get('file_count', 0))
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total PII Found", selected_scan.get('total_pii_found', 0))
                    col2.metric("High Risk Items", selected_scan.get('high_risk_count', 0))
                    timestamp = selected_scan.get('timestamp', 'N/A')
                    if timestamp != 'N/A':
                        try:
                            timestamp = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            pass
                    col3.metric("Date & Time", timestamp)
                    
                    # PII Types breakdown
                    if 'pii_types' in selected_scan and selected_scan['pii_types']:
                        st.subheader("PII Types Found")
                        pii_df = pd.DataFrame(list(selected_scan['pii_types'].items()), columns=['PII Type', 'Count'])
                        fig = px.bar(pii_df, x='PII Type', y='Count', color='PII Type')
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Risk levels breakdown
                    if 'risk_levels' in selected_scan and selected_scan['risk_levels']:
                        st.subheader("Risk Level Distribution")
                        risk_df = pd.DataFrame(list(selected_scan['risk_levels'].items()), columns=['Risk Level', 'Count'])
                        fig = px.pie(risk_df, values='Count', names='Risk Level', color='Risk Level',
                                    color_discrete_map={'Low': 'green', 'Medium': 'orange', 'High': 'red'})
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Detailed findings
                    if 'detailed_results' in selected_scan and selected_scan['detailed_results']:
                        st.subheader("Detailed Findings")
                        
                        # Extract all PII items from all files
                        all_pii_items = []
                        for file_result in selected_scan['detailed_results']:
                            file_name = file_result.get('file_name', 'Unknown')
                            for pii_item in file_result.get('pii_found', []):
                                pii_item['file_name'] = file_name
                                all_pii_items.append(pii_item)
                        
                        if all_pii_items:
                            # Convert to DataFrame
                            pii_items_df = pd.DataFrame(all_pii_items)
                            
                            # Select columns to display
                            cols_to_display = ['file_name', 'type', 'value', 'location', 'risk_level', 'reason']
                            cols_to_display = [col for col in cols_to_display if col in pii_items_df.columns]
                            
                            # Rename columns for better display
                            column_map = {
                                'file_name': 'File',
                                'type': 'PII Type',
                                'value': 'Value',
                                'location': 'Location',
                                'risk_level': 'Risk Level',
                                'reason': 'Reason'
                            }
                            pii_items_df = pii_items_df[cols_to_display].rename(columns=column_map)
                            
                            # Apply styling based on risk level
                            def highlight_risk(val):
                                if val == 'High':
                                    return 'background-color: #ffcccc'
                                elif val == 'Medium':
                                    return 'background-color: #ffffcc'
                                elif val == 'Low':
                                    return 'background-color: #ccffcc'
                                return ''
                            
                            # Display the styled DataFrame
                            if 'Risk Level' in pii_items_df.columns:
                                styled_df = pii_items_df.style.applymap(highlight_risk, subset=['Risk Level'])
                                st.dataframe(styled_df, use_container_width=True)
                            else:
                                st.dataframe(pii_items_df, use_container_width=True)
                        else:
                            st.info("No PII items found in this scan.")
                    
                    # Generate report button
                    if st.button("Generate PDF Report"):
                        st.session_state.current_scan_id = selected_scan_id
                        pdf_bytes = generate_report(selected_scan)
                        
                        # Create download link
                        b64_pdf = base64.b64encode(pdf_bytes).decode()
                        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="GDPR_Scan_Report_{selected_scan_id}.pdf">Download PDF Report</a>'
                        st.markdown(href, unsafe_allow_html=True)
        else:
            st.info("No scan history available. Start a new scan to see results here.")
    
    elif selected_nav == "Reports":
        st.title("GDPR Compliance Reports")
        
        # Get all scans
        all_scans = results_aggregator.get_all_scans(st.session_state.username)
        
        if all_scans and len(all_scans) > 0:
            # Create a select box for scan selection
            scan_options = []
            for scan in all_scans:
                scan_id = scan.get('scan_id', 'Unknown')
                timestamp = scan.get('timestamp', 'Unknown')
                scan_type = scan.get('scan_type', 'Unknown')
                
                if timestamp != 'Unknown':
                    try:
                        timestamp = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        pass
                
                scan_options.append({
                    'scan_id': scan_id,
                    'display': f"{timestamp} - {scan_type} (ID: {scan_id})"
                })
            
            selected_scan = st.selectbox(
                "Select a scan to generate a report",
                options=range(len(scan_options)),
                format_func=lambda i: scan_options[i]['display']
            )
            
            selected_scan_id = scan_options[selected_scan]['scan_id']
            scan_data = results_aggregator.get_scan_by_id(selected_scan_id)
            
            if scan_data:
                # Report generation options
                st.subheader("Report Options")
                
                col1, col2 = st.columns(2)
                with col1:
                    include_details = st.checkbox("Include Detailed Findings", value=True)
                    include_charts = st.checkbox("Include Charts", value=True)
                
                with col2:
                    include_metadata = st.checkbox("Include Scan Metadata", value=True)
                    include_recommendations = st.checkbox("Include Recommendations", value=True)
                
                # Generate report
                if st.button("Generate Report"):
                    with st.spinner("Generating report..."):
                        pdf_bytes = generate_report(
                            scan_data,
                            include_details=include_details,
                            include_charts=include_charts,
                            include_metadata=include_metadata,
                            include_recommendations=include_recommendations
                        )
                        
                        # Create download link
                        b64_pdf = base64.b64encode(pdf_bytes).decode()
                        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="GDPR_Scan_Report_{selected_scan_id}.pdf">Download PDF Report</a>'
                        st.markdown(href, unsafe_allow_html=True)
                        
                        st.success("Report generated successfully!")
                
                # Report preview (if available from a previous generation)
                if 'current_scan_id' in st.session_state and st.session_state.current_scan_id == selected_scan_id and 'pdf_bytes' in locals():
                    st.subheader("Report Preview")
                    st.write("Preview not available. Please download the report to view.")
            else:
                st.error(f"Could not find scan with ID: {selected_scan_id}")
        else:
            st.info("No scan history available to generate reports. Start a new scan first.")

