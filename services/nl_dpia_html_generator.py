"""
Netherlands DPIA HTML Report Generator

Generates comprehensive HTML reports for DPIA assessments with:
- Professional styling and layout
- Netherlands jurisdiction compliance display
- GDPR, UAVG, and Police Act compliance analysis
- Downloadable via URL link
"""

import os
import json
from datetime import datetime
from typing import Dict, Any
import uuid

class NetherlandsDPIAHTMLGenerator:
    """
    Generates professional HTML reports for Netherlands DPIA assessments.
    """
    
    def __init__(self):
        self.reports_dir = "reports/dpia"
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def generate_html_report(self, assessment_data: Dict[str, Any]) -> str:
        """
        Generate comprehensive HTML report from assessment data.
        
        Returns:
            File path of generated HTML report
        """
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            assessment_id = assessment_data.get('assessment_id', 'unknown')
            filename = f"NL_DPIA_Report_{assessment_id}_{timestamp}.html"
            file_path = os.path.join(self.reports_dir, filename)
            
            # Generate HTML content
            html_content = self._generate_html_content(assessment_data)
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return file_path
            
        except Exception as e:
            raise Exception(f"Failed to generate HTML report: {str(e)}")
    
    def _generate_html_content(self, assessment: Dict[str, Any]) -> str:
        """Generate complete HTML content for the report."""
        
        # Parse JSON fields safely
        def safe_json_parse(field_value, default=None):
            if isinstance(field_value, str):
                try:
                    return json.loads(field_value)
                except:
                    return default or []
            return field_value or (default or [])
        
        data_categories = safe_json_parse(assessment.get('data_categories'))
        data_subjects = safe_json_parse(assessment.get('data_subjects'))
        privacy_risks = safe_json_parse(assessment.get('privacy_risks'))
        vulnerable_groups = safe_json_parse(assessment.get('vulnerable_groups'))
        access_controls = safe_json_parse(assessment.get('access_controls'))
        dutch_sector_codes = safe_json_parse(assessment.get('dutch_sector_codes'))
        mitigation_measures = safe_json_parse(assessment.get('mitigation_measures'))
        responsible_parties = safe_json_parse(assessment.get('responsible_parties'))
        recommendations = safe_json_parse(assessment.get('recommendations'))
        
        # Risk level styling
        risk_level = assessment.get('overall_risk_level', 'medium')
        risk_color = {
            'low': '#4CAF50',
            'medium': '#FF9800', 
            'high': '#F44336'
        }.get(risk_level, '#FF9800')
        
        # Compliance status
        can_proceed = assessment.get('can_proceed', False)
        proceed_color = '#4CAF50' if can_proceed else '#F44336'
        proceed_text = 'YES' if can_proceed else 'NO'
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🇳🇱 Netherlands DPIA Assessment Report - {assessment.get('organization_name', 'Organization')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
            position: relative;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Ccircle cx='30' cy='30' r='4'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E") repeat;
        }}
        
        .header-content {{
            position: relative;
            z-index: 1;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .header .subtitle {{
            font-size: 1.1rem;
            opacity: 0.9;
            margin-bottom: 20px;
        }}
        
        .header .org-name {{
            font-size: 1.5rem;
            background: rgba(255,255,255,0.2);
            padding: 10px 20px;
            border-radius: 25px;
            display: inline-block;
            margin-bottom: 15px;
        }}
        
        .header .meta-info {{
            font-size: 0.95rem;
            opacity: 0.8;
        }}
        
        .content {{
            padding: 40px 30px;
        }}
        
        .executive-summary {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            text-align: center;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .metric-card {{
            background: rgba(255,255,255,0.95);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .metric-card h3 {{
            font-size: 0.9rem;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
            opacity: 0.7;
        }}
        
        .metric-card .value {{
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .section {{
            margin: 40px 0;
            background: #f8f9fa;
            border-radius: 12px;
            padding: 30px;
            border-left: 5px solid #1e3c72;
        }}
        
        .section h2 {{
            color: #1e3c72;
            margin-bottom: 20px;
            font-size: 1.5rem;
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 10px;
        }}
        
        .compliance-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .compliance-table th {{
            background: #1e3c72;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        
        .compliance-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .compliance-table tr:last-child td {{
            border-bottom: none;
        }}
        
        .compliance-table tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        
        .score {{
            font-weight: bold;
            padding: 5px 12px;
            border-radius: 20px;
            color: white;
        }}
        
        .score.high {{
            background: #4CAF50;
        }}
        
        .score.medium {{
            background: #FF9800;
        }}
        
        .score.low {{
            background: #F44336;
        }}
        
        .risk-indicator {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            color: white;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .recommendations {{
            background: white;
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .recommendation-item {{
            border-left: 4px solid;
            padding: 20px;
            margin: 10px 0;
            background: #f8f9fa;
        }}
        
        .recommendation-item.critical {{
            border-left-color: #dc3545;
            background: #fff5f5;
        }}
        
        .recommendation-item.high {{
            border-left-color: #fd7e14;
            background: #fff8f1;
        }}
        
        .recommendation-item.medium {{
            border-left-color: #ffc107;
            background: #fffdf0;
        }}
        
        .recommendation-item.low {{
            border-left-color: #198754;
            background: #f0fff4;
        }}
        
        .recommendation-priority {{
            font-size: 0.8rem;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }}
        
        .list-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }}
        
        .list-item {{
            background: white;
            padding: 12px;
            border-radius: 6px;
            border-left: 3px solid #1e3c72;
        }}
        
        .yes-no {{
            font-weight: bold;
            padding: 4px 8px;
            border-radius: 15px;
            font-size: 0.9rem;
        }}
        
        .yes {{
            background: #d4edda;
            color: #155724;
        }}
        
        .no {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .footer {{
            background: #343a40;
            color: white;
            padding: 30px;
            text-align: center;
            font-size: 0.9rem;
        }}
        
        .footer .disclaimer {{
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            font-style: italic;
        }}
        
        .nl-flag {{
            font-size: 1.5rem;
            margin-right: 10px;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            
            .container {{
                box-shadow: none;
                border-radius: 0;
            }}
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 2rem;
            }}
            
            .metrics-grid {{
                grid-template-columns: 1fr 1fr;
            }}
            
            .content {{
                padding: 20px 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-content">
                <h1><span class="nl-flag">🇳🇱</span>Netherlands DPIA Assessment Report</h1>
                <div class="subtitle">GDPR • Dutch UAVG • Police Act Compliance Analysis</div>
                <div class="org-name">{assessment.get('organization_name', 'Organization Name')}</div>
                <div class="meta-info">
                    <strong>Assessment ID:</strong> {assessment.get('assessment_id', 'N/A')} | 
                    <strong>Generated:</strong> {datetime.now().strftime('%B %d, %Y at %H:%M')} | 
                    <strong>Jurisdiction:</strong> {assessment.get('org_jurisdiction', 'Netherlands')}
                </div>
            </div>
        </div>
        
        <div class="content">
            <div class="executive-summary">
                <h2>Executive Summary</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3>Overall Risk Level</h3>
                        <div class="value risk-indicator" style="background-color: {risk_color}">
                            {risk_level.upper()}
                        </div>
                    </div>
                    <div class="metric-card">
                        <h3>Can Proceed</h3>
                        <div class="value" style="color: {proceed_color}">
                            {proceed_text}
                        </div>
                    </div>
                    <div class="metric-card">
                        <h3>GDPR Score</h3>
                        <div class="value" style="color: {'#4CAF50' if assessment.get('gdpr_score', 0) >= 80 else '#F44336'}">
                            {assessment.get('gdpr_score', 0)}%
                        </div>
                    </div>
                    <div class="metric-card">
                        <h3>UAVG Score</h3>
                        <div class="value" style="color: {'#4CAF50' if assessment.get('uavg_score', 0) >= 80 else '#F44336'}">
                            {assessment.get('uavg_score', 0)}%
                        </div>
                    </div>
                </div>
                <p style="margin-top: 20px; font-size: 1.1rem;">
                    This assessment evaluates data processing activities for compliance with European GDPR, 
                    Dutch UAVG implementation, and Netherlands-specific legal requirements including the Police Act.
                </p>
            </div>
            
            <div class="section">
                <h2>1. Organization Information</h2>
                <div class="list-grid">
                    <div class="list-item">
                        <strong>Organization:</strong> {assessment.get('organization_name', 'N/A')}
                    </div>
                    <div class="list-item">
                        <strong>DPO Contact:</strong> {assessment.get('org_dpo_contact', 'N/A')}
                    </div>
                    <div class="list-item">
                        <strong>Industry:</strong> {assessment.get('org_industry', 'N/A')}
                    </div>
                    <div class="list-item">
                        <strong>Employee Count:</strong> {assessment.get('org_employee_count', 'N/A')}
                    </div>
                    <div class="list-item">
                        <strong>Data Controller:</strong> 
                        <span class="yes-no {'yes' if assessment.get('org_is_controller') else 'no'}">
                            {'Yes' if assessment.get('org_is_controller') else 'No'}
                        </span>
                    </div>
                    <div class="list-item">
                        <strong>Data Processor:</strong> 
                        <span class="yes-no {'yes' if assessment.get('org_is_processor') else 'no'}">
                            {'Yes' if assessment.get('org_is_processor') else 'No'}
                        </span>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>2. Data Processing Description</h2>
                <p><strong>Purpose:</strong> {assessment.get('processing_purpose', 'N/A')}</p>
                <p><strong>Description:</strong> {assessment.get('processing_description', 'N/A')}</p>
                
                {'<h3>Data Categories</h3><div class="list-grid">' + ''.join([f'<div class="list-item">{cat}</div>' for cat in data_categories]) + '</div>' if data_categories else '<p>No data categories specified.</p>'}
                
                {'<h3>Data Subjects</h3><div class="list-grid">' + ''.join([f'<div class="list-item">{subj}</div>' for subj in data_subjects]) + '</div>' if data_subjects else '<p>No data subjects specified.</p>'}
                
                <div style="margin-top: 20px;">
                    <strong>Retention Period:</strong> {assessment.get('retention_period', 'N/A')}<br>
                    <strong>Automated Decisions:</strong> 
                    <span class="yes-no {'yes' if assessment.get('automated_decisions') else 'no'}">
                        {'Yes' if assessment.get('automated_decisions') else 'No'}
                    </span><br>
                    <strong>Profiling:</strong> 
                    <span class="yes-no {'yes' if assessment.get('profiling') else 'no'}">
                        {'Yes' if assessment.get('profiling') else 'No'}
                    </span><br>
                    <strong>AI System Used:</strong> 
                    <span class="yes-no {'yes' if assessment.get('ai_system_used') else 'no'}">
                        {'Yes' if assessment.get('ai_system_used') else 'No'}
                    </span>
                </div>
            </div>
            
            <div class="section">
                <h2>3. Legal Basis & Compliance</h2>
                <p><strong>GDPR Legal Basis:</strong> {assessment.get('gdpr_legal_basis', 'N/A')}</p>
                {f'<p><strong>Legitimate Interest Details:</strong> {assessment.get("legitimate_interest_details", "N/A")}</p>' if assessment.get('legitimate_interest_details') else ''}
                {f'<p><strong>Consent Mechanism:</strong> {assessment.get("consent_mechanism", "N/A")}</p>' if assessment.get('consent_mechanism') else ''}
                
                <h3>Special Data Categories</h3>
                <div class="list-grid">
                    <div class="list-item">
                        <strong>Special Categories (Art. 9):</strong> 
                        <span class="yes-no {'yes' if assessment.get('special_categories') else 'no'}">
                            {'Yes' if assessment.get('special_categories') else 'No'}
                        </span>
                    </div>
                    <div class="list-item">
                        <strong>Criminal Data (Art. 10):</strong> 
                        <span class="yes-no {'yes' if assessment.get('criminal_data') else 'no'}">
                            {'Yes' if assessment.get('criminal_data') else 'No'}
                        </span>
                    </div>
                    <div class="list-item">
                        <strong>Children's Data:</strong> 
                        <span class="yes-no {'yes' if assessment.get('children_data') else 'no'}">
                            {'Yes' if assessment.get('children_data') else 'No'}
                        </span>
                    </div>
                    <div class="list-item">
                        <strong>Cross-border Transfer:</strong> 
                        <span class="yes-no {'yes' if assessment.get('cross_border_transfer') else 'no'}">
                            {'Yes' if assessment.get('cross_border_transfer') else 'No'}
                        </span>
                    </div>
                </div>
                {f'<p><strong>Transfer Mechanism:</strong> {assessment.get("adequacy_decision", "N/A")}</p>' if assessment.get('cross_border_transfer') else ''}
            </div>
            
            <div class="section">
                <h2>4. Privacy Risk Assessment</h2>
                <div class="list-grid">
                    <div class="list-item">
                        <strong>Breach Likelihood:</strong> 
                        <span class="score {assessment.get('breach_likelihood', 'medium')}">{assessment.get('breach_likelihood', 'Medium').title()}</span>
                    </div>
                    <div class="list-item">
                        <strong>Breach Impact:</strong> 
                        <span class="score {assessment.get('breach_impact', 'medium')}">{assessment.get('breach_impact', 'Medium').title()}</span>
                    </div>
                    <div class="list-item">
                        <strong>Discrimination Risk:</strong> 
                        <span class="score {assessment.get('discrimination_risk', 'medium')}">{assessment.get('discrimination_risk', 'Medium').title()}</span>
                    </div>
                    <div class="list-item">
                        <strong>Surveillance Concerns:</strong> 
                        <span class="yes-no {'yes' if assessment.get('surveillance_concerns') else 'no'}">
                            {'Yes' if assessment.get('surveillance_concerns') else 'No'}
                        </span>
                    </div>
                </div>
                
                {'<h3>Identified Privacy Risks</h3><div class="list-grid">' + ''.join([f'<div class="list-item">{risk}</div>' for risk in privacy_risks]) + '</div>' if privacy_risks else '<p>No specific privacy risks identified.</p>'}
                
                {'<h3>Vulnerable Groups</h3><div class="list-grid">' + ''.join([f'<div class="list-item">{group}</div>' for group in vulnerable_groups]) + '</div>' if vulnerable_groups else '<p>No vulnerable groups identified.</p>'}
            </div>
            
            <div class="section">
                <h2>5. Technical & Organizational Measures</h2>
                <h3>Technical Security Measures</h3>
                <div class="list-grid">
                    <div class="list-item">
                        <strong>Encryption at Rest:</strong> 
                        <span class="yes-no {'yes' if assessment.get('encryption_at_rest') else 'no'}">
                            {'Yes' if assessment.get('encryption_at_rest') else 'No'}
                        </span>
                    </div>
                    <div class="list-item">
                        <strong>Encryption in Transit:</strong> 
                        <span class="yes-no {'yes' if assessment.get('encryption_in_transit') else 'no'}">
                            {'Yes' if assessment.get('encryption_in_transit') else 'No'}
                        </span>
                    </div>
                    <div class="list-item">
                        <strong>Audit Logging:</strong> 
                        <span class="yes-no {'yes' if assessment.get('audit_logging') else 'no'}">
                            {'Yes' if assessment.get('audit_logging') else 'No'}
                        </span>
                    </div>
                    <div class="list-item">
                        <strong>Data Minimization:</strong> 
                        <span class="yes-no {'yes' if assessment.get('data_minimization') else 'no'}">
                            {'Yes' if assessment.get('data_minimization') else 'No'}
                        </span>
                    </div>
                    <div class="list-item">
                        <strong>Pseudonymization:</strong> 
                        <span class="yes-no {'yes' if assessment.get('pseudonymization') else 'no'}">
                            {'Yes' if assessment.get('pseudonymization') else 'No'}
                        </span>
                    </div>
                    <div class="list-item">
                        <strong>Anonymization:</strong> 
                        <span class="yes-no {'yes' if assessment.get('anonymization') else 'no'}">
                            {'Yes' if assessment.get('anonymization') else 'No'}
                        </span>
                    </div>
                </div>
                
                {'<h3>Access Controls</h3><div class="list-grid">' + ''.join([f'<div class="list-item">{control}</div>' for control in access_controls]) + '</div>' if access_controls else '<p>No access controls specified.</p>'}
                
                <h3>Organizational Measures</h3>
                <div class="list-grid">
                    <div class="list-item">
                        <strong>Staff Training:</strong> 
                        <span class="yes-no {'yes' if assessment.get('staff_training') else 'no'}">
                            {'Yes' if assessment.get('staff_training') else 'No'}
                        </span>
                    </div>
                    <div class="list-item">
                        <strong>Backup Procedures:</strong> {assessment.get('backup_procedures', 'N/A')}
                    </div>
                    <div class="list-item">
                        <strong>Incident Response:</strong> {assessment.get('incident_response', 'N/A')}
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>6. Netherlands-Specific Compliance</h2>
                <h3>Dutch UAVG & Local Requirements</h3>
                <div class="list-grid">
                    <div class="list-item">
                        <strong>UAVG Compliant:</strong> 
                        <span class="yes-no {'yes' if assessment.get('uavg_compliant') else 'no'}">
                            {'Yes' if assessment.get('uavg_compliant') else 'No'}
                        </span>
                    </div>
                    <div class="list-item">
                        <strong>Dutch DPA Notification:</strong> 
                        <span class="yes-no {'yes' if assessment.get('dutch_dpa_notification') else 'no'}">
                            {'Yes' if assessment.get('dutch_dpa_notification') else 'No'}
                        </span>
                    </div>
                    <div class="list-item">
                        <strong>BSN Processing:</strong> 
                        <span class="yes-no {'yes' if assessment.get('bsn_processing') else 'no'}">
                            {'Yes' if assessment.get('bsn_processing') else 'No'}
                        </span>
                    </div>
                    <div class="list-item">
                        <strong>Municipal Processing:</strong> 
                        <span class="yes-no {'yes' if assessment.get('municipal_processing') else 'no'}">
                            {'Yes' if assessment.get('municipal_processing') else 'No'}
                        </span>
                    </div>
                    <div class="list-item">
                        <strong>Healthcare BSN:</strong> 
                        <span class="yes-no {'yes' if assessment.get('healthcare_bsn') else 'no'}">
                            {'Yes' if assessment.get('healthcare_bsn') else 'No'}
                        </span>
                    </div>
                </div>
                
                <h3>Dutch Police Act Compliance</h3>
                <div class="list-grid">
                    <div class="list-item">
                        <strong>Police Act Applicable:</strong> 
                        <span class="yes-no {'yes' if assessment.get('police_act_applicable') else 'no'}">
                            {'Yes' if assessment.get('police_act_applicable') else 'No'}
                        </span>
                    </div>
                    <div class="list-item">
                        <strong>Police Act Compliant:</strong> 
                        <span class="yes-no {'yes' if assessment.get('police_act_compliant') else 'no'}">
                            {'Yes' if assessment.get('police_act_compliant') else 'No'}
                        </span>
                    </div>
                </div>
                {f'<p><strong>Police Processing Purpose:</strong> {assessment.get("police_processing_purpose", "N/A")}</p>' if assessment.get('police_act_applicable') else ''}
                
                {'<h3>Dutch Sector Codes</h3><div class="list-grid">' + ''.join([f'<div class="list-item">{code}</div>' for code in dutch_sector_codes]) + '</div>' if dutch_sector_codes else '<p>No sector codes specified.</p>'}
            </div>
            
            <div class="section">
                <h2>7. Compliance Analysis</h2>
                <table class="compliance-table">
                    <thead>
                        <tr>
                            <th>Regulation</th>
                            <th>Score</th>
                            <th>Status</th>
                            <th>Requirements</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>EU GDPR</strong></td>
                            <td><span class="score {'high' if assessment.get('gdpr_score', 0) >= 80 else 'medium' if assessment.get('gdpr_score', 0) >= 60 else 'low'}">{assessment.get('gdpr_score', 0)}%</span></td>
                            <td>{'Compliant' if assessment.get('gdpr_score', 0) >= 80 else 'Needs Improvement'}</td>
                            <td>General Data Protection Regulation</td>
                        </tr>
                        <tr>
                            <td><strong>Dutch UAVG</strong></td>
                            <td><span class="score {'high' if assessment.get('uavg_score', 0) >= 80 else 'medium' if assessment.get('uavg_score', 0) >= 60 else 'low'}">{assessment.get('uavg_score', 0)}%</span></td>
                            <td>{'Compliant' if assessment.get('uavg_score', 0) >= 80 else 'Needs Improvement'}</td>
                            <td>Dutch GDPR Implementation Act</td>
                        </tr>
                        <tr>
                            <td><strong>Police Act</strong></td>
                            <td><span class="yes-no {'yes' if assessment.get('police_act_compliant') else 'no'}">{'Compliant' if assessment.get('police_act_compliant') else 'N/A' if not assessment.get('police_act_applicable') else 'Non-Compliant'}</span></td>
                            <td>{'Compliant' if assessment.get('police_act_compliant') else 'N/A' if not assessment.get('police_act_applicable') else 'Non-Compliant'}</td>
                            <td>Dutch Police Act (Politiewet) 2012</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <div class="section">
                <h2>8. Mitigation Measures</h2>
                {'<div class="list-grid">' + ''.join([f'<div class="list-item">{measure}</div>' for measure in mitigation_measures]) + '</div>' if mitigation_measures else '<p>No mitigation measures specified.</p>'}
                
                <div style="margin-top: 20px;">
                    <p><strong>Implementation Timeline:</strong> {assessment.get('implementation_timeline', 'N/A')}</p>
                    <p><strong>Review Schedule:</strong> {assessment.get('review_schedule', 'N/A')}</p>
                    <p><strong>Monitoring Procedures:</strong> {assessment.get('monitoring_procedures', 'N/A')}</p>
                </div>
                
                {'<h3>Responsible Parties</h3><div class="list-grid">' + ''.join([f'<div class="list-item">{party}</div>' for party in responsible_parties]) + '</div>' if responsible_parties else '<p>No responsible parties specified.</p>'}
            </div>
            
            <div class="section">
                <h2>9. Recommendations</h2>
                <div class="recommendations">
        """
        
        # Add recommendations if available
        if recommendations and len(recommendations) > 0:
            for i, rec in enumerate(recommendations, 1):
                priority = rec.get('priority', 'medium')
                category = rec.get('category', 'General')
                recommendation = rec.get('recommendation', 'No recommendation provided')
                legal_basis = rec.get('legal_basis', 'N/A')
                
                html_content += f"""
                    <div class="recommendation-item {priority}">
                        <div class="recommendation-priority {priority}">{priority.upper()} PRIORITY</div>
                        <h4>{i}. {category}</h4>
                        <p>{recommendation}</p>
                        <small><strong>Legal basis:</strong> {legal_basis}</small>
                    </div>
                """
        else:
            html_content += '<p>No specific recommendations generated.</p>'
        
        html_content += f"""
                </div>
            </div>
            
            <div class="section">
                <h2>10. Final Assessment & Conclusion</h2>
                <div class="executive-summary">
                    <h3>Assessment Conclusion</h3>
                    <div style="font-size: 1.2rem; margin: 20px 0;">
                        <strong>Processing can proceed:</strong> 
                        <span style="color: {proceed_color}; font-size: 1.5rem; font-weight: bold;">
                            {proceed_text}
                        </span>
                    </div>
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <h3>Overall Risk</h3>
                            <div class="value risk-indicator" style="background-color: {risk_color}">
                                {risk_level.upper()}
                            </div>
                        </div>
                        <div class="metric-card">
                            <h3>DPIA Required</h3>
                            <div class="value">
                                {'YES' if assessment.get('dpia_required', True) else 'NO'}
                            </div>
                        </div>
                        <div class="metric-card">
                            <h3>Compliance Score</h3>
                            <div class="value" style="color: {'#4CAF50' if assessment.get('compliance_score', 0) >= 80 else '#F44336'}">
                                {assessment.get('compliance_score', 0)}%
                            </div>
                        </div>
                        <div class="metric-card">
                            <h3>Recommendations</h3>
                            <div class="value">
                                {len(recommendations) if recommendations else 0}
                            </div>
                        </div>
                    </div>
                    
                    <div style="text-align: left; margin-top: 30px; padding: 20px; background: rgba(255,255,255,0.2); border-radius: 8px;">
                        <h4>Key Points:</h4>
                        <ul style="margin: 10px 0; padding-left: 20px;">
                            <li>GDPR Compliance: {assessment.get('gdpr_score', 0)}% ({'Compliant' if assessment.get('gdpr_score', 0) >= 80 else 'Needs Improvement'})</li>
                            <li>Dutch UAVG Compliance: {assessment.get('uavg_score', 0)}% ({'Compliant' if assessment.get('uavg_score', 0) >= 80 else 'Needs Improvement'})</li>
                            <li>Overall Risk Level: {risk_level.title()}</li>
                            <li>{'Additional measures required before processing' if not can_proceed else 'Processing may proceed with current measures'}</li>
                            <li>{'Regular review and monitoring recommended' if risk_level != 'low' else 'Standard monitoring procedures sufficient'}</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <div>
                <strong>🇳🇱 Netherlands DPIA Assessment Report</strong><br>
                Generated by DataGuardian Pro | Assessment ID: {assessment.get('assessment_id', 'N/A')}<br>
                Date: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')} (CET)
            </div>
            
            <div class="disclaimer">
                <strong>Legal Disclaimer:</strong><br>
                This report is generated based on the information provided and should be reviewed by a qualified 
                data protection professional. It does not constitute legal advice. Organizations should consult 
                with legal experts familiar with Dutch and EU data protection law before making final decisions 
                about data processing activities. This assessment is valid as of the date of generation and 
                should be reviewed regularly as circumstances and regulations change.
                <br><br>
                <strong>Compliance Standards:</strong> EU GDPR, Dutch UAVG, Netherlands Police Act (Politiewet), 
                Dutch Personal Records Database Act, Netherlands jurisdiction requirements.
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        return html_content
    
    def get_report_url(self, file_path: str) -> str:
        """
        Generate a URL for accessing the HTML report.
        
        Args:
            file_path: Path to the generated HTML file
            
        Returns:
            URL for accessing the report
        """
        # In a real deployment, this would be the actual server URL
        # For now, we'll return a relative path that can be served
        filename = os.path.basename(file_path)
        return f"/reports/dpia/{filename}"