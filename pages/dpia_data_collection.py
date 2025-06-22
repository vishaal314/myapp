"""
DPIA Data Collection Interface

Streamlit interface for collecting DPIA assessment data from users,
storing it in memory, and generating comprehensive reports.
"""

import streamlit as st
from datetime import datetime
from services.dpia_data_collector import DPIADataCollector
# Report generator import with fallback
try:
    from services.dpia_report_generator import DPIAReportGenerator
    REPORT_GENERATOR_AVAILABLE = True
except ImportError:
    REPORT_GENERATOR_AVAILABLE = False
    DPIAReportGenerator = None

def run_dpia_data_collection():
    """Main DPIA data collection interface."""
    st.title("DPIA Data Collection & Reporting")
    st.markdown("Complete Data Protection Impact Assessment with memory-based data collection")
    
    # Initialize collector
    collector = DPIADataCollector()
    
    # Progress tracking
    completed_sections = collector.get_collected_sections()
    progress = len(completed_sections) / 7  # 7 total sections
    
    st.progress(progress)
    st.markdown(f"**Progress:** {len(completed_sections)}/7 sections completed")
    
    # Create tabs for different sections
    tabs = st.tabs([
        "1. Organization", "2. Processing", "3. Legal Basis", 
        "4. Risk Assessment", "5. Technical Measures", "6. Dutch Compliance", 
        "7. Mitigation & Report"
    ])
    
    with tabs[0]:
        collect_organization_info(collector)
    
    with tabs[1]:
        collect_processing_description(collector)
    
    with tabs[2]:
        collect_legal_basis(collector)
    
    with tabs[3]:
        collect_risk_assessment(collector)
    
    with tabs[4]:
        collect_technical_measures(collector)
    
    with tabs[5]:
        collect_dutch_compliance(collector)
    
    with tabs[6]:
        generate_final_report(collector)

def collect_organization_info(collector: DPIADataCollector):
    """Collect organization information."""
    st.subheader("Organization Information")
    
    with st.form("organization_form"):
        org_name = st.text_input("Organization Name", placeholder="Enter your organization name")
        dpo_contact = st.text_input("Data Protection Officer Contact", placeholder="DPO email or phone")
        industry = st.selectbox("Industry Sector", [
            "Financial Services", "Healthcare", "Technology", "Education", 
            "Government", "Retail", "Manufacturing", "Other"
        ])
        employee_count = st.selectbox("Number of Employees", [
            "1-10", "11-50", "51-200", "201-1000", "1000+"
        ])
        
        col1, col2 = st.columns(2)
        with col1:
            is_controller = st.checkbox("Data Controller", value=True)
        with col2:
            is_processor = st.checkbox("Data Processor", value=False)
        
        jurisdiction = st.selectbox("Primary Jurisdiction", [
            "Netherlands", "European Union", "United Kingdom", "United States", "Other"
        ])
        
        if st.form_submit_button("Save Organization Info", type="primary"):
            org_data = {
                'name': org_name,
                'dpo_contact': dpo_contact,
                'industry': industry,
                'employee_count': employee_count,
                'controller': is_controller,
                'processor': is_processor,
                'jurisdiction': jurisdiction
            }
            
            data_id = collector.collect_organization_info(org_data)
            st.success(f"Organization information saved! (ID: {data_id[:8]})")

def collect_processing_description(collector: DPIADataCollector):
    """Collect data processing description."""
    st.subheader("Data Processing Description")
    
    with st.form("processing_form"):
        purpose = st.text_area("Processing Purpose", 
                              placeholder="Describe the main purpose of data processing")
        description = st.text_area("Detailed Description", 
                                  placeholder="Provide detailed description of processing activities")
        
        st.markdown("**Data Categories**")
        data_categories = st.multiselect("Select data categories processed:", [
            "Personal identifiers (name, email, phone)",
            "Financial data",
            "Health data",
            "Biometric data",
            "Location data",
            "Behavioral data",
            "Professional data",
            "Criminal conviction data",
            "Political opinions",
            "Other sensitive data"
        ])
        
        st.markdown("**Data Subjects**")
        data_subjects = st.multiselect("Select data subject categories:", [
            "Customers/Clients",
            "Employees",
            "Website visitors",
            "Children (under 16)",
            "Vulnerable adults",
            "Public officials",
            "Third parties",
            "Other"
        ])
        
        retention = st.text_input("Data Retention Period", 
                                 placeholder="e.g., 5 years, until account deletion")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            automated_decisions = st.checkbox("Automated Decision Making")
        with col2:
            profiling = st.checkbox("Profiling Activities")
        with col3:
            ai_system = st.checkbox("AI System Used")
        
        if st.form_submit_button("Save Processing Description", type="primary"):
            processing_data = {
                'purpose': purpose,
                'description': description,
                'data_categories': data_categories,
                'data_subjects': data_subjects,
                'retention': retention,
                'automated_decisions': automated_decisions,
                'profiling': profiling,
                'ai_system': ai_system
            }
            
            data_id = collector.collect_processing_description(processing_data)
            st.success(f"Processing description saved! (ID: {data_id[:8]})")

def collect_legal_basis(collector: DPIADataCollector):
    """Collect legal basis information."""
    st.subheader("Legal Basis Analysis")
    
    with st.form("legal_basis_form"):
        gdpr_basis = st.selectbox("Primary GDPR Legal Basis", [
            "Consent (Article 6(1)(a))",
            "Contract (Article 6(1)(b))",
            "Legal obligation (Article 6(1)(c))",
            "Vital interests (Article 6(1)(d))",
            "Public task (Article 6(1)(e))",
            "Legitimate interests (Article 6(1)(f))"
        ])
        
        if "Legitimate interests" in gdpr_basis:
            legitimate_interest = st.text_area("Legitimate Interest Details",
                                              placeholder="Describe the legitimate interest and balancing test")
        else:
            legitimate_interest = ""
        
        if "Consent" in gdpr_basis:
            consent_mechanism = st.text_area("Consent Mechanism",
                                           placeholder="Describe how consent is obtained and managed")
        else:
            consent_mechanism = ""
        
        col1, col2, col3 = st.columns(3)
        with col1:
            special_categories = st.checkbox("Special Category Data (Article 9)")
        with col2:
            criminal_data = st.checkbox("Criminal Conviction Data (Article 10)")
        with col3:
            children_data = st.checkbox("Children's Data (under 16)")
        
        cross_border = st.checkbox("Cross-border Data Transfer")
        if cross_border:
            adequacy_decision = st.selectbox("Transfer Mechanism", [
                "Adequacy Decision",
                "Standard Contractual Clauses",
                "Binding Corporate Rules",
                "Certification",
                "Other"
            ])
        else:
            adequacy_decision = ""
        
        if st.form_submit_button("Save Legal Basis", type="primary"):
            legal_data = {
                'gdpr_basis': gdpr_basis,
                'legitimate_interest': legitimate_interest,
                'consent_mechanism': consent_mechanism,
                'special_categories': special_categories,
                'criminal_data': criminal_data,
                'children_data': children_data,
                'cross_border': cross_border,
                'adequacy_decision': adequacy_decision
            }
            
            data_id = collector.collect_legal_basis(legal_data)
            st.success(f"Legal basis saved! (ID: {data_id[:8]})")

def collect_risk_assessment(collector: DPIADataCollector):
    """Collect risk assessment data."""
    st.subheader("Privacy Risk Assessment")
    
    with st.form("risk_assessment_form"):
        st.markdown("**Privacy Risks**")
        privacy_risks = st.multiselect("Identify potential privacy risks:", [
            "Unauthorized access to personal data",
            "Data breach or loss",
            "Discrimination or bias",
            "Surveillance or monitoring concerns",
            "Loss of control over personal data",
            "Identity theft",
            "Reputation damage",
            "Economic loss",
            "Physical harm",
            "Psychological harm"
        ])
        
        col1, col2 = st.columns(2)
        with col1:
            breach_likelihood = st.selectbox("Data Breach Likelihood", ["low", "medium", "high"])
            discrimination_risk = st.selectbox("Discrimination Risk", ["low", "medium", "high"])
        with col2:
            breach_impact = st.selectbox("Data Breach Impact", ["low", "medium", "high"])
            surveillance = st.checkbox("Surveillance Concerns")
        
        vulnerable_groups = st.multiselect("Vulnerable Groups Affected:", [
            "Children",
            "Elderly",
            "Disabled persons",
            "Minorities",
            "Employees",
            "Patients",
            "Other vulnerable individuals"
        ])
        
        st.markdown("**Rights Impact Assessment**")
        rights_impact = {}
        rights_list = [
            "Right to information",
            "Right of access",
            "Right to rectification",
            "Right to erasure",
            "Right to restrict processing",
            "Right to data portability",
            "Right to object"
        ]
        
        for right in rights_list:
            impact = st.selectbox(f"{right} impact:", ["none", "low", "medium", "high"], 
                                key=f"rights_{right}")
            rights_impact[right] = impact
        
        if st.form_submit_button("Save Risk Assessment", type="primary"):
            risk_data = {
                'privacy_risks': privacy_risks,
                'breach_likelihood': breach_likelihood,
                'breach_impact': breach_impact,
                'discrimination_risk': discrimination_risk,
                'surveillance': surveillance,
                'vulnerable_groups': vulnerable_groups,
                'rights_impact': rights_impact
            }
            
            data_id = collector.collect_risk_assessment(risk_data)
            st.success(f"Risk assessment saved! (ID: {data_id[:8]})")

def collect_technical_measures(collector: DPIADataCollector):
    """Collect technical and organizational measures."""
    st.subheader("Technical & Organizational Measures")
    
    with st.form("technical_measures_form"):
        st.markdown("**Technical Safeguards**")
        col1, col2 = st.columns(2)
        with col1:
            encryption_rest = st.checkbox("Encryption at Rest")
            access_controls = st.multiselect("Access Controls:", [
                "Role-based access control",
                "Multi-factor authentication",
                "Regular access reviews",
                "Privileged access management"
            ])
            data_minimization = st.checkbox("Data Minimization")
            anonymization = st.checkbox("Anonymization")
        
        with col2:
            encryption_transit = st.checkbox("Encryption in Transit")
            audit_logging = st.checkbox("Audit Logging")
            pseudonymization = st.checkbox("Pseudonymization")
            staff_training = st.checkbox("Staff Training Program")
        
        backup_procedures = st.text_area("Backup Procedures",
                                        placeholder="Describe backup and recovery procedures")
        incident_response = st.text_area("Incident Response Plan",
                                        placeholder="Describe incident response procedures")
        
        if st.form_submit_button("Save Technical Measures", type="primary"):
            tech_data = {
                'encryption_rest': encryption_rest,
                'encryption_transit': encryption_transit,
                'access_controls': access_controls,
                'audit_logging': audit_logging,
                'data_minimization': data_minimization,
                'pseudonymization': pseudonymization,
                'anonymization': anonymization,
                'backup_procedures': backup_procedures,
                'incident_response': incident_response,
                'staff_training': staff_training
            }
            
            data_id = collector.collect_technical_measures(tech_data)
            st.success(f"Technical measures saved! (ID: {data_id[:8]})")

def collect_dutch_compliance(collector: DPIADataCollector):
    """Collect Netherlands-specific compliance data."""
    st.subheader("Dutch GDPR (UAVG) & Local Compliance")
    
    with st.form("dutch_compliance_form"):
        col1, col2 = st.columns(2)
        with col1:
            uavg_compliant = st.checkbox("UAVG Compliant Design")
            dpa_notification = st.checkbox("Dutch DPA Notification Required")
            bsn_processing = st.checkbox("BSN (Social Security Number) Processing")
            municipal = st.checkbox("Municipal Data Processing")
        
        with col2:
            police_act = st.checkbox("Police Act (Politiewet) Applicable")
            healthcare_bsn = st.checkbox("Healthcare BSN Processing")
        
        if police_act:
            police_purpose = st.text_area("Police Processing Purpose",
                                         placeholder="Describe law enforcement processing purpose")
        else:
            police_purpose = ""
        
        sector_codes = st.multiselect("Applicable Dutch Sector Codes:", [
            "Financial sector",
            "Healthcare sector", 
            "Education sector",
            "Government sector",
            "Telecommunications",
            "Other"
        ])
        
        if st.form_submit_button("Save Dutch Compliance", type="primary"):
            dutch_data = {
                'uavg_compliant': uavg_compliant,
                'dpa_notification': dpa_notification,
                'police_act': police_act,
                'police_purpose': police_purpose,
                'bsn_processing': bsn_processing,
                'sector_codes': sector_codes,
                'municipal': municipal,
                'healthcare_bsn': healthcare_bsn
            }
            
            data_id = collector.collect_dutch_compliance(dutch_data)
            st.success(f"Dutch compliance data saved! (ID: {data_id[:8]})")

def generate_final_report(collector: DPIADataCollector):
    """Generate and display final DPIA report."""
    st.subheader("Generate DPIA Report")
    
    # Check completion status
    is_complete = collector.is_assessment_complete()
    completed_sections = collector.get_collected_sections()
    
    if is_complete:
        st.success("✅ All required sections completed!")
    else:
        st.warning(f"⚠️ {len(completed_sections)}/5 required sections completed")
        missing = set(['organization_info', 'processing_description', 'legal_basis', 
                      'risk_assessment', 'technical_measures']) - set(completed_sections)
        st.write(f"Missing sections: {', '.join(missing)}")
    
    # Show collected data summary
    st.markdown("### Collected Data Summary")
    for section in completed_sections:
        st.write(f"✅ {section.replace('_', ' ').title()}")
    
    # Mitigation measures form
    with st.form("mitigation_form"):
        st.markdown("**Mitigation Measures**")
        
        measures = st.text_area("Proposed Mitigation Measures",
                               placeholder="List specific measures to address identified risks")
        timeline = st.text_input("Implementation Timeline",
                                placeholder="e.g., 6 months, Q2 2024")
        responsible = st.text_input("Responsible Parties",
                                   placeholder="e.g., IT Team, DPO, Management")
        monitoring = st.text_area("Monitoring Procedures",
                                 placeholder="How will effectiveness be monitored?")
        review_schedule = st.text_input("Review Schedule",
                                       placeholder="e.g., Annual, Every 6 months")
        
        if st.form_submit_button("Save Mitigation Measures", type="secondary"):
            mitigation_data = {
                'measures': measures.split('\n') if measures else [],
                'timeline': timeline,
                'responsible': responsible.split(',') if responsible else [],
                'monitoring': monitoring,
                'review_schedule': review_schedule
            }
            
            data_id = collector.collect_mitigation_measures(mitigation_data)
            st.success(f"Mitigation measures saved! (ID: {data_id[:8]})")
    
    # Generate report button
    if st.button("Generate Complete DPIA Report", type="primary", disabled=not is_complete):
        with st.spinner("Generating comprehensive DPIA report..."):
            report_data = collector.generate_dpia_report()
            
            # Display report summary
            display_report_summary(report_data)
            
            # Generate downloadable report
            generate_downloadable_report(report_data)

def display_report_summary(report_data: Dict):
    """Display summary of generated report."""
    st.markdown("### DPIA Report Generated Successfully")
    
    exec_summary = report_data.get('executive_summary', {})
    risk_summary = report_data.get('risk_summary', {})
    compliance = report_data.get('compliance_analysis', {})
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        risk_level = exec_summary.get('overall_risk_level', 'Unknown').upper()
        risk_color = {"HIGH": "red", "MEDIUM": "orange", "LOW": "green"}.get(risk_level, "gray")
        st.metric("Overall Risk", risk_level)
    with col2:
        gdpr_score = compliance.get('gdpr_score', 0)
        st.metric("GDPR Score", f"{gdpr_score}%", delta=f"{gdpr_score-80}%" if gdpr_score >= 80 else None)
    with col3:
        uavg_score = compliance.get('uavg_score', 0) 
        st.metric("UAVG Score", f"{uavg_score}%", delta=f"{uavg_score-80}%" if uavg_score >= 80 else None)
    with col4:
        can_proceed = compliance.get('can_proceed', False)
        st.metric("Can Proceed", "YES" if can_proceed else "NO")
    
    # Risk factors
    if risk_summary.get('high_risk_factors'):
        st.markdown("### High Risk Factors Identified")
        for factor in risk_summary['high_risk_factors']:
            st.write(f"⚠️ {factor}")
    
    # Recommendations
    recommendations = report_data.get('recommendations', [])
    if recommendations:
        st.markdown("### Key Recommendations")
        for rec in recommendations[:5]:  # Show top 5
            priority_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            st.write(f"{priority_color.get(rec.get('priority', 'low'), '🔵')} **{rec.get('category')}**: {rec.get('recommendation')}")

def generate_downloadable_report(report_data: Dict):
    """Generate downloadable report files."""
    st.markdown("### Download Reports")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # JSON report
        import json
        json_report = json.dumps(report_data, indent=2, default=str)
        st.download_button(
            label="Download JSON Report",
            data=json_report,
            file_name=f"DPIA_Report_{report_data['report_id'][:8]}.json",
            mime="application/json"
        )
    
    with col2:
        # HTML report
        html_report = generate_html_report(report_data)
        st.download_button(
            label="Download HTML Report",
            data=html_report,
            file_name=f"DPIA_Report_{report_data['report_id'][:8]}.html",
            mime="text/html"
        )
    
    with col3:
        # PDF report (if generator available)
        if REPORT_GENERATOR_AVAILABLE:
            generator = DPIAReportGenerator()
            try:
                pdf_bytes = generator.generate_pdf_report(report_data)
                st.download_button(
                    label="Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"DPIA_Report_{report_data['report_id'][:8]}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"PDF generation failed: {str(e)}")
        else:
            st.info("PDF generator not available")

def generate_html_report(report_data: Dict) -> str:
    """Generate HTML version of DPIA report."""
    exec_summary = report_data.get('executive_summary', {})
    compliance = report_data.get('compliance_analysis', {})
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>DPIA Report - {exec_summary.get('organization', 'Organization')}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background-color: #2E86AB; color: white; padding: 20px; text-align: center; }}
            .section {{ margin: 20px 0; padding: 15px; border-left: 4px solid #2E86AB; }}
            .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #f5f5f5; }}
            .risk-high {{ color: #d32f2f; }}
            .risk-medium {{ color: #f57c00; }}
            .risk-low {{ color: #388e3c; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Data Protection Impact Assessment Report</h1>
            <h2>{exec_summary.get('organization', 'Organization Name')}</h2>
            <p>Generated on: {exec_summary.get('assessment_date', 'Unknown Date')}</p>
        </div>
        
        <div class="section">
            <h2>Executive Summary</h2>
            <div class="metric">
                <strong>Overall Risk Level:</strong> 
                <span class="risk-{exec_summary.get('overall_risk_level', 'medium')}">{exec_summary.get('overall_risk_level', 'Medium').upper()}</span>
            </div>
            <div class="metric">
                <strong>DPIA Required:</strong> {'Yes' if exec_summary.get('dpia_required', True) else 'No'}
            </div>
            <div class="metric">
                <strong>GDPR Compliance:</strong> {compliance.get('gdpr_score', 0)}%
            </div>
            <div class="metric">
                <strong>Can Proceed:</strong> {'Yes' if compliance.get('can_proceed', False) else 'No'}
            </div>
        </div>
        
        <div class="section">
            <h2>Compliance Analysis</h2>
            <p><strong>GDPR Compliance Score:</strong> {compliance.get('gdpr_score', 0)}%</p>
            <p><strong>Dutch UAVG Score:</strong> {compliance.get('uavg_score', 0)}%</p>
            <p><strong>EU AI Act Score:</strong> {compliance.get('ai_act_score', 0)}%</p>
        </div>
        
        <div class="section">
            <h2>Recommendations</h2>
            <ul>
    """
    
    for rec in report_data.get('recommendations', []):
        html += f'<li><strong>{rec.get("category")}:</strong> {rec.get("recommendation")}</li>'
    
    html += """
            </ul>
        </div>
        
        <div class="section">
            <h2>Report Details</h2>
            <p><strong>Report ID:</strong> {}</p>
            <p><strong>Generated At:</strong> {}</p>
            <p><strong>DPIA Version:</strong> {}</p>
        </div>
    </body>
    </html>
    """.format(
        report_data.get('report_id', 'Unknown'),
        report_data.get('generated_at', 'Unknown'),
        report_data.get('dpia_version', '2.0')
    )
    
    return html

if __name__ == "__main__":
    run_dpia_data_collection()