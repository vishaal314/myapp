"""
SOC2 Display Utilities

This module provides specialized display functions for SOC2 scan results.
"""

import streamlit as st
import pandas as pd

def display_soc2_findings(scan_results):
    """
    Display SOC2 findings with TSC criteria mapping.
    
    Args:
        scan_results: Dictionary containing SOC2 scan results
    """
    # Display findings table with enhanced TSC mapping
    st.subheader("Compliance Findings")
    if 'findings' in scan_results and scan_results['findings']:
        findings_df = pd.DataFrame([
            {
                "Risk": f.get("risk_level", "Unknown").upper(),
                "Category": f.get("category", "Unknown").capitalize(),
                "Description": f.get("description", "No description"),
                "File": f.get("file", "Unknown"),
                "Line": f.get("line", "N/A"),
                "SOC2 TSC": ", ".join(f.get("soc2_tsc_criteria", []))
            }
            for f in scan_results['findings'][:10]  # Show top 10 findings
        ])
        st.dataframe(findings_df, use_container_width=True)
        
        if len(scan_results['findings']) > 10:
            st.info(f"Showing 10 of {len(scan_results['findings'])} findings. Download the PDF report for complete results.")
            
        # Add detailed TSC mapping explanation without using an expander to avoid nesting issues
        st.markdown("### SOC2 Trust Services Criteria Details")
        st.markdown("""
        #### SOC2 Trust Services Criteria Explained
        
        Each finding is mapped to specific SOC2 Trust Services Criteria to help you understand 
        how it impacts your compliance posture:
        
        - **CC**: Common Criteria (Security)
        - **A**: Availability
        - **PI**: Processing Integrity
        - **C**: Confidentiality
        - **P**: Privacy
        
        For example, a finding mapped to **CC6.1** means it impacts the "Logical and Physical Access Controls"
        criteria under the Security category.
        
        #### Remediation Prioritization
        
        When addressing findings, prioritize based on these criteria:
        
        1. **CC (Security)** - Critical foundation for all other controls
        2. **C (Confidentiality)** - Protects sensitive data from unauthorized disclosure
        3. **A (Availability)** - Ensures systems are operational when needed
        4. **PI (Processing Integrity)** - Ensures data processing is complete and accurate
        5. **P (Privacy)** - Addresses personal data protection requirements
        """)
            
    # Display SOC2 TSC Checklist
    if 'soc2_tsc_checklist' in scan_results:
        st.subheader("SOC2 Trust Services Criteria Checklist")
        
        # Create tabs for each SOC2 category
        checklist = scan_results['soc2_tsc_checklist']
        categories = ["security", "availability", "processing_integrity", "confidentiality", "privacy"]
        
        soc2_tabs = st.tabs([c.capitalize() for c in categories])
        
        for i, category in enumerate(categories):
            with soc2_tabs[i]:
                # Filter criteria for this category
                category_criteria = {k: v for k, v in checklist.items() if v.get("category") == category}
                if not category_criteria:
                    st.info(f"No {category.capitalize()} criteria assessed.")
                    continue
                    
                # Create dataframe for this category
                criteria_data = []
                for criterion, details in category_criteria.items():
                    criteria_data.append({
                        "Criterion": criterion,
                        "Description": details.get("description", ""),
                        "Status": details.get("status", "not_assessed").upper(),
                        "Violations": len(details.get("violations", []))
                    })
                
                # Sort by criterion
                criteria_data.sort(key=lambda x: x["Criterion"])
                
                # Create dataframe
                df = pd.DataFrame(criteria_data)
                st.dataframe(df, use_container_width=True)
                
                # Summary for this category
                statuses = [details.get("status", "not_assessed") for details in category_criteria.values()]
                passed = statuses.count("passed")
                failed = statuses.count("failed")
                warning = statuses.count("warning")
                info = statuses.count("info")
                
                st.write(f"**Summary**: {passed} Passed, {failed} Failed, {warning} Warning, {info} Info")
                
                # Show violations if any criteria failed
                if failed > 0 or warning > 0:
                    st.markdown("#### Violations")
                    violations_list = []
                    
                    for criterion, details in category_criteria.items():
                        violations = details.get("violations", [])
                        if violations:
                            st.markdown(f"**{criterion}**: {details.get('description', '')}")
                            for v in violations:
                                st.markdown(f"- **{v.get('risk_level', '').upper()}**: {v.get('description', '')} in `{v.get('file', '')}:{v.get('line', '')}`")
                            st.markdown("---")

def run_soc2_display_standalone():
    """
    Run a standalone SOC2 display page.
    This can be imported and called directly from app.py
    """
    st.title("SOC2 Compliance Results")
    
    if 'soc2_scan_results' not in st.session_state:
        st.warning("No SOC2 scan results found. Please run a SOC2 scan first.")
        return
        
    scan_results = st.session_state.soc2_scan_results
    
    # Show repository info
    st.write(f"**Repository:** {scan_results.get('repo_url')}")
    if 'project' in scan_results:
        st.write(f"**Project:** {scan_results.get('project')}")
    st.write(f"**Branch:** {scan_results.get('branch', 'main')}")
    
    # Extract metrics
    compliance_score = scan_results.get("compliance_score", 0)
    high_risk = scan_results.get("high_risk_count", 0)
    medium_risk = scan_results.get("medium_risk_count", 0)
    low_risk = scan_results.get("low_risk_count", 0)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Color coding based on compliance score
    if compliance_score >= 80:
        compliance_color_css = "green"
        compliance_status = "✓ Good" 
    elif compliance_score >= 60:
        compliance_color_css = "orange"
        compliance_status = "⚠️ Needs Review"
    else:
        compliance_color_css = "red"
        compliance_status = "✗ Critical"
        
    with col1:
        st.metric("Compliance Score", f"{compliance_score}/100")
        st.markdown(f"<div style='text-align: center; color: {compliance_color_css};'>{compliance_status}</div>", unsafe_allow_html=True)
    
    with col2:
        st.metric("High Risk Issues", high_risk, delta_color="inverse")
    
    with col3:
        st.metric("Medium Risk Issues", medium_risk, delta_color="inverse")
        
    with col4:
        st.metric("Low Risk Issues", low_risk, delta_color="inverse")
    
    # Use the display function
    display_soc2_findings(scan_results)
    
    # Report options
    st.markdown("### Report Options")
    report_tabs = st.tabs(["Download Reports", "View Full Report"])
    
    with report_tabs[0]:
        col1, col2 = st.columns(2)
        
        with col1:
            # PDF Download button
            if st.button("Generate PDF Report", type="primary"):
                from services.report_generator import generate_report
                import base64
                from datetime import datetime
                
                with st.spinner("Generating PDF report..."):
                    # Generate PDF report
                    pdf_bytes = generate_report(scan_results)
                    
                    # Provide download link
                    b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                    pdf_filename = f"soc2_compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{pdf_filename}">Download SOC2 Compliance Report PDF</a>'
                    st.markdown(href, unsafe_allow_html=True)
        
        with col2:
            # HTML Download button
            if st.button("Generate HTML Report", type="primary"):
                from services.html_report_generator import get_html_report_as_base64
                import base64
                from datetime import datetime
                
                with st.spinner("Generating HTML report..."):
                    # Generate HTML report
                    # First adapt scan_results to the HTML report format
                    html_compatible_results = {
                        'scan_id': scan_results.get('scan_id', f"soc2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                        'scan_type': 'SOC2',
                        'timestamp': datetime.now().isoformat(),
                        'region': scan_results.get('region', 'Global'),
                        'url': scan_results.get('repo_url', 'Not available'),
                        'findings': scan_results.get('findings', []),
                        'total_pii_found': len(scan_results.get('findings', [])),
                        'high_risk_count': scan_results.get('high_risk_count', 0),
                        'medium_risk_count': scan_results.get('medium_risk_count', 0),
                        'low_risk_count': scan_results.get('low_risk_count', 0),
                        'pii_types': {'SOC2 Findings': len(scan_results.get('findings', []))},
                        'recommendations': [
                            {
                                'title': 'Address High Risk SOC2 Findings',
                                'priority': 'High',
                                'description': 'Focus on high-risk SOC2 issues to improve your compliance posture.',
                                'steps': ['Review all high-risk findings', 'Prioritize based on TSC criteria impact', 'Develop remediation plans']
                            },
                            {
                                'title': 'Improve SOC2 Documentation',
                                'priority': 'Medium',
                                'description': 'Ensure all SOC2 control procedures are properly documented.',
                                'steps': ['Update control documentation', 'Cross-reference with TSC criteria', 'Review with compliance team']
                            }
                        ]
                    }
                    
                    # Get base64 encoded HTML
                    html_base64 = get_html_report_as_base64(html_compatible_results)
                    
                    # Provide download link
                    html_filename = f"soc2_compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                    href = f'<a href="data:text/html;base64,{html_base64}" download="{html_filename}">Download SOC2 Compliance Report HTML</a>'
                    st.markdown(href, unsafe_allow_html=True)
    
    with report_tabs[1]:
        # Full Report viewing option
        if st.button("Show Detailed Report"):
            with st.spinner("Generating detailed report view..."):
                st.markdown("## Detailed SOC2 Compliance Report")
                
                # Repository information 
                st.markdown("### Repository Information")
                st.markdown(f"**Repository:** {scan_results.get('repo_url')}")
                if 'project' in scan_results:
                    st.markdown(f"**Project:** {scan_results.get('project')}")
                st.markdown(f"**Branch:** {scan_results.get('branch', 'main')}")
                
                # Compliance Score
                compliance_score = scan_results.get("compliance_score", 0)
                if compliance_score >= 80:
                    compliance_color = "green"
                    compliance_status = "✓ Good" 
                elif compliance_score >= 60:
                    compliance_color = "orange"
                    compliance_status = "⚠️ Needs Review"
                else:
                    compliance_color = "red"
                    compliance_status = "✗ Critical"
                    
                st.markdown(f"### Compliance Score: <span style='color:{compliance_color};'>{compliance_score}/100</span> ({compliance_status})", unsafe_allow_html=True)
                
                # Risk Distribution
                st.markdown("### Risk Distribution")
                high_risk = scan_results.get("high_risk_count", 0)
                medium_risk = scan_results.get("medium_risk_count", 0)
                low_risk = scan_results.get("low_risk_count", 0)
                
                import pandas as pd
                import plotly.express as px
                
                risk_df = pd.DataFrame({
                    "Risk Level": ["High", "Medium", "Low"],
                    "Count": [high_risk, medium_risk, low_risk]
                })
                
                fig = px.pie(risk_df, values="Count", names="Risk Level", 
                             color="Risk Level", 
                             color_discrete_map={"High": "red", "Medium": "orange", "Low": "green"},
                             title="Risk Distribution")
                
                st.plotly_chart(fig)
                
                # Display full findings table
                st.markdown("### Complete Findings List")
                
                if 'findings' in scan_results and scan_results['findings']:
                    findings_df = pd.DataFrame([
                        {
                            "Risk": f.get("risk_level", "Unknown").upper(),
                            "Category": f.get("category", "Unknown").capitalize(),
                            "Description": f.get("description", "No description"),
                            "File": f.get("file", "Unknown"),
                            "Line": f.get("line", "N/A"),
                            "SOC2 TSC": ", ".join(f.get("soc2_tsc_criteria", []))
                        }
                        for f in scan_results['findings']
                    ])
                    st.dataframe(findings_df, use_container_width=True)
                
                # Display SOC2 TSC Criteria Checklist (complete)
                if 'soc2_tsc_checklist' in scan_results:
                    st.markdown("### SOC2 Trust Services Criteria Checklist")
                    
                    # Create tabs for each SOC2 category
                    checklist = scan_results['soc2_tsc_checklist']
                    categories = ["security", "availability", "processing_integrity", "confidentiality", "privacy"]
                    category_tabs = st.tabs([c.capitalize() for c in categories])
                    
                    for i, category in enumerate(categories):
                        with category_tabs[i]:
                            # Filter criteria for this category
                            category_criteria = {k: v for k, v in checklist.items() if v.get("category") == category}
                            if not category_criteria:
                                st.info(f"No {category.capitalize()} criteria assessed.")
                                continue
                                
                            # Create dataframe for criteria in this category
                            criteria_data = []
                            for criterion, details in category_criteria.items():
                                status = details.get("status", "not_assessed").upper()
                                if status == "FAILED":
                                    status_color = "red"
                                elif status == "WARNING":
                                    status_color = "orange"
                                elif status == "PASSED":
                                    status_color = "green"
                                else:
                                    status_color = "gray"
                                
                                criteria_data.append({
                                    "Criterion": criterion,
                                    "Description": details.get("description", ""),
                                    "Status": f"<span style='color:{status_color};'>{status}</span>",
                                    "Violations": len(details.get("violations", []))
                                })
                            
                            # Sort by criterion
                            criteria_data.sort(key=lambda x: x["Criterion"])
                            
                            # Convert to DataFrame
                            criteria_df = pd.DataFrame(criteria_data)
                            st.write(criteria_df.to_html(escape=False), unsafe_allow_html=True)
                            
                            # Display violations if any
                            violations = []
                            for criterion, details in category_criteria.items():
                                for v in details.get("violations", []):
                                    violations.append({
                                        "Criterion": criterion,
                                        "Risk Level": v.get("risk_level", "").upper(),
                                        "Description": v.get("description", ""),
                                        "File": v.get("file", ""),
                                        "Line": v.get("line", "")
                                    })
                            
                            if violations:
                                st.markdown("#### Violations")
                                violations_df = pd.DataFrame(violations)
                                st.dataframe(violations_df, use_container_width=True)
                
                # Recommendations section
                st.markdown("### Recommendations")
                
                # Based on high-risk findings
                if high_risk > 0:
                    st.markdown("""
                    #### High Priority Recommendations
                    
                    1. Address all high-risk findings immediately to improve your SOC2 compliance posture
                    2. Prioritize items related to Security (CC) criteria as they form the foundation for other controls
                    3. Schedule a technical review meeting to discuss remediation plans
                    4. Implement proper access controls and authentication mechanisms for sensitive operations
                    """)
                
                if medium_risk > 0:
                    st.markdown("""
                    #### Medium Priority Recommendations
                    
                    1. Establish a timeline for addressing medium-risk findings
                    2. Review documentation practices for affected controls
                    3. Consider implementing automated testing for these controls
                    """)
                
                # SOC2 Implementation Guidance
                st.markdown("""
                #### SOC2 Implementation Guidance
                
                1. **Documentation**: Ensure all policies and procedures are formally documented and regularly updated
                2. **Risk Assessment**: Conduct regular risk assessments to identify new threats and vulnerabilities
                3. **Training**: Provide security awareness training to all personnel
                4. **Monitoring**: Implement continuous monitoring of controls to ensure ongoing compliance
                5. **Testing**: Regularly test controls to validate effectiveness
                """)
                
                # Add a timestamp for the report
                from datetime import datetime
                st.markdown(f"*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")