"""
EU AI Act 2025 HTML Report Generator

This module generates comprehensive HTML reports specifically for EU AI Act 2025
compliance assessment with complete coverage of all regulatory requirements
including prohibited practices, high-risk systems, transparency obligations,
fundamental rights impact assessment, and algorithmic accountability.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List

def generate_eu_ai_act_html_report(scan_data: Dict[str, Any], language: str = 'en') -> str:
    """
    Generate a comprehensive HTML report for EU AI Act 2025 compliance assessment.
    
    Args:
        scan_data: Dictionary containing AI model scan results with EU AI Act findings
        language: Language code for translations ('en' or 'nl')
        
    Returns:
        HTML report as string with complete EU AI Act 2025 coverage
    """
    
    # Load translations for the selected language
    def get_translation(key: str, default: str = '') -> str:
        """Get translation for the given key"""
        try:
            # Load translations file
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            translation_file = os.path.join(base_dir, 'translations', f'{language}.json')
            
            if os.path.exists(translation_file):
                with open(translation_file, 'r', encoding='utf-8') as f:
                    translations = json.load(f)
                
                # Navigate nested keys (e.g., 'eu_ai_act_report.title')
                keys = key.split('.')
                value = translations
                for k in keys:
                    if isinstance(value, dict) and k in value:
                        value = value[k]
                    else:
                        return default
                return value if isinstance(value, str) else default
            else:
                return default
        except Exception:
            return default
    
    # Translation helper function
    def _(key: str, default: str = '') -> str:
        return get_translation(key, default)
    
    # Extract key AI Act compliance data
    ai_model_info = scan_data.get('ai_model_info', {})
    ai_system_name = ai_model_info.get('name', scan_data.get('model_name', 'AI System Under Assessment'))
    model_source = scan_data.get('model_source', 'Unknown')
    scan_time = scan_data.get('timestamp', datetime.now().isoformat())
    findings = scan_data.get('findings', [])
    ai_act_findings = [f for f in findings if 'AI_ACT' in f.get('type', '')]
    
    # Format timestamp
    try:
        if isinstance(scan_time, str):
            timestamp = datetime.fromisoformat(scan_time.replace('Z', '+00:00')).strftime('%B %d, %Y at %I:%M %p UTC')
        else:
            timestamp = scan_time.strftime('%B %d, %Y at %I:%M %p UTC')
    except:
        timestamp = str(scan_time)
    
    # Calculate AI Act compliance metrics
    compliance_metrics = scan_data.get('compliance_metrics', {})
    ai_act_compliance = compliance_metrics.get('ai_act_compliance', 'Assessment Required')
    ai_risk_level = compliance_metrics.get('ai_act_risk_level', 'Assessment Required')
    compliance_score = compliance_metrics.get('compliance_score', 0)
    model_framework = compliance_metrics.get('model_framework', 'Unknown')
    
    # Analyze AI Act violation types
    prohibited_practices = len([f for f in ai_act_findings if f.get('type') == 'AI_ACT_PROHIBITED'])
    high_risk_violations = len([f for f in ai_act_findings if f.get('type') == 'AI_ACT_HIGH_RISK'])
    transparency_violations = len([f for f in ai_act_findings if f.get('type') == 'AI_ACT_TRANSPARENCY'])
    fundamental_rights_violations = len([f for f in ai_act_findings if f.get('type') == 'AI_ACT_FUNDAMENTAL_RIGHTS'])
    accountability_violations = len([f for f in ai_act_findings if f.get('type') == 'AI_ACT_ACCOUNTABILITY'])
    
    # Determine overall AI Act risk level with translations
    if prohibited_practices > 0:
        overall_risk = _('eu_ai_act_report.risk_classifications.prohibited_immediate', 'Prohibited - Immediate Action Required')
        risk_color = "#7f1d1d"
        risk_bg = "#fef2f2"
    elif high_risk_violations > 2 or fundamental_rights_violations > 1:
        overall_risk = _('eu_ai_act_report.risk_classifications.high_risk_compliance', 'High Risk - Compliance Required')
        risk_color = "#dc2626"
        risk_bg = "#fef2f2"
    elif high_risk_violations > 0 or transparency_violations > 1:
        overall_risk = _('eu_ai_act_report.risk_classifications.medium_risk_assessment', 'Medium Risk - Assessment Required')
        risk_color = "#ea580c"
        risk_bg = "#fff7ed"
    else:
        overall_risk = _('eu_ai_act_report.risk_classifications.limited_risk_monitoring', 'Limited Risk - Monitoring Required')
        risk_color = "#16a34a"
        risk_bg = "#f0fdf4"
    
    # Generate AI Act requirements coverage section
    ai_act_requirements_html = f"""
    <div style="background: white; border-radius: 15px; padding: 30px; margin: 20px 0; box-shadow: 0 6px 20px rgba(0,0,0,0.1);">
        <h2 style="color: #1e40af; margin-bottom: 25px; display: flex; align-items: center;">
            🇪🇺 {_('eu_ai_act_report.eu_ai_act_requirements', 'EU AI Act 2025 Requirements Coverage')}
        </h2>
        <div style="background: #f0f9ff; padding: 20px; border-radius: 10px; border-left: 4px solid #0ea5e9; margin-bottom: 25px;">
            <h3 style="color: #0c4a6e; margin: 0 0 10px 0;">{_('eu_ai_act_report.regulatory_status', 'Regulatory Status')}</h3>
            <p style="color: #075985; margin: 0; line-height: 1.6;">
                {_('eu_ai_act_report.regulatory_status_text', '<strong>EU Artificial Intelligence Act (Regulation 2024/1689)</strong><br>• Prohibited practices: Enforced since February 2, 2025<br>• GPAI model rules: Enforced since August 2, 2025<br>• High-risk systems: Full enforcement by August 2, 2027<br>• Maximum penalties: €35M or 7% global turnover<br>• Enforcement Authority: National supervisory authorities in each EU Member State')}
            </p>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px;">
            <div style="background: {'#fef2f2' if prohibited_practices > 0 else '#f0fdf4'}; padding: 20px; border-radius: 10px; border-left: 4px solid {'#dc2626' if prohibited_practices > 0 else '#16a34a'};">
                <h4 style="color: {'#dc2626' if prohibited_practices > 0 else '#16a34a'}; margin: 0 0 10px 0;">🚫 {_('eu_ai_act_report.article_5_prohibited', 'Article 5 - Prohibited Practices')}</h4>
                <div style="font-size: 24px; font-weight: bold; color: {'#dc2626' if prohibited_practices > 0 else '#16a34a'};">{prohibited_practices}</div>
                <p style="color: #6b7280; font-size: 12px; margin: 5px 0 0 0;">{_('eu_ai_act_report.violations_detected', 'Violations Detected')}</p>
                <p style="color: #4b5563; font-size: 11px; margin: 10px 0 0 0;">{_('eu_ai_act_report.prohibited_practices_desc', 'Subliminal techniques, social scoring, mass surveillance')}</p>
            </div>
            
            <div style="background: {'#fef2f2' if high_risk_violations > 0 else '#f0fdf4'}; padding: 20px; border-radius: 10px; border-left: 4px solid {'#ea580c' if high_risk_violations > 0 else '#16a34a'};">
                <h4 style="color: {'#ea580c' if high_risk_violations > 0 else '#16a34a'}; margin: 0 0 10px 0;">⚠️ {_('eu_ai_act_report.annex_iii_high_risk', 'Annex III - High-Risk Systems')}</h4>
                <div style="font-size: 24px; font-weight: bold; color: {'#ea580c' if high_risk_violations > 0 else '#16a34a'};">{high_risk_violations}</div>
                <p style="color: #6b7280; font-size: 12px; margin: 5px 0 0 0;">{_('eu_ai_act_report.issues_identified', 'Issues Identified')}</p>
                <p style="color: #4b5563; font-size: 11px; margin: 10px 0 0 0;">{_('eu_ai_act_report.high_risk_desc', 'Biometric ID, employment, education, healthcare AI')}</p>
            </div>
            
            <div style="background: {'#fff7ed' if transparency_violations > 0 else '#f0fdf4'}; padding: 20px; border-radius: 10px; border-left: 4px solid {'#d97706' if transparency_violations > 0 else '#16a34a'};">
                <h4 style="color: {'#d97706' if transparency_violations > 0 else '#16a34a'}; margin: 0 0 10px 0;">👁️ {_('eu_ai_act_report.article_13_transparency', 'Article 13 - Transparency')}</h4>
                <div style="font-size: 24px; font-weight: bold; color: {'#d97706' if transparency_violations > 0 else '#16a34a'};">{transparency_violations}</div>
                <p style="color: #6b7280; font-size: 12px; margin: 5px 0 0 0;">{_('eu_ai_act_report.disclosure_issues', 'Disclosure Issues')}</p>
                <p style="color: #4b5563; font-size: 11px; margin: 10px 0 0 0;">{_('eu_ai_act_report.transparency_desc', 'Human-AI interaction disclosure requirements')}</p>
            </div>
            
            <div style="background: {'#fef2f2' if fundamental_rights_violations > 0 else '#f0fdf4'}; padding: 20px; border-radius: 10px; border-left: 4px solid {'#dc2626' if fundamental_rights_violations > 0 else '#16a34a'};">
                <h4 style="color: {'#dc2626' if fundamental_rights_violations > 0 else '#16a34a'}; margin: 0 0 10px 0;">⚖️ {_('eu_ai_act_report.article_29_fundamental_rights', 'Article 29 - Fundamental Rights')}</h4>
                <div style="font-size: 24px; font-weight: bold; color: {'#dc2626' if fundamental_rights_violations > 0 else '#16a34a'};">{fundamental_rights_violations}</div>
                <p style="color: #6b7280; font-size: 12px; margin: 5px 0 0 0;">{_('eu_ai_act_report.rights_impact', 'Rights Impact')}</p>
                <p style="color: #4b5563; font-size: 11px; margin: 10px 0 0 0;">{_('eu_ai_act_report.fundamental_rights_desc', 'Privacy, non-discrimination, freedom of expression')}</p>
            </div>
            
            <div style="background: {'#fff7ed' if accountability_violations > 0 else '#f0fdf4'}; padding: 20px; border-radius: 10px; border-left: 4px solid {'#d97706' if accountability_violations > 0 else '#16a34a'};">
                <h4 style="color: {'#d97706' if accountability_violations > 0 else '#16a34a'}; margin: 0 0 10px 0;">📊 {_('eu_ai_act_report.articles_14_15_accountability', 'Articles 14-15 - Accountability')}</h4>
                <div style="font-size: 24px; font-weight: bold; color: {'#d97706' if accountability_violations > 0 else '#16a34a'};">{accountability_violations}</div>
                <p style="color: #6b7280; font-size: 12px; margin: 5px 0 0 0;">{_('eu_ai_act_report.governance_issues', 'Governance Issues')}</p>
                <p style="color: #4b5563; font-size: 11px; margin: 10px 0 0 0;">{_('eu_ai_act_report.accountability_desc', 'Algorithmic governance, audit trails, explainability')}</p>
            </div>
        </div>
    </div>"""
    
    # Generate detailed findings section for AI Act violations
    ai_act_findings_html = ""
    if ai_act_findings:
        findings_rows = ""
        for i, finding in enumerate(ai_act_findings):
            bg_color = '#f9fafb' if i % 2 == 0 else '#ffffff'
            violation_type = finding.get('type', '').replace('AI_ACT_', '').replace('_', ' ').title()
            risk_level = finding.get('risk_level', 'Medium')
            
            risk_colors = {
                'Critical': '#dc2626',
                'High': '#ea580c',
                'Medium': '#d97706',
                'Low': '#16a34a'
            }
            risk_color = risk_colors.get(risk_level, '#6b7280')
            
            regulation = finding.get('regulation', 'EU AI Act')
            description = finding.get('description', 'No description available')
            location = finding.get('location', 'System-wide')
            
            findings_rows += f"""
            <tr style="background-color: {bg_color};">
                <td style="padding: 15px; border-bottom: 1px solid #e5e7eb;">
                    <span style="background: {risk_color}; color: white; padding: 6px 10px; border-radius: 12px; font-size: 11px; font-weight: 500;">
                        {risk_level}
                    </span>
                </td>
                <td style="padding: 15px; border-bottom: 1px solid #e5e7eb; color: #374151; font-weight: 500;">
                    {violation_type}
                </td>
                <td style="padding: 15px; border-bottom: 1px solid #e5e7eb; color: #4b5563; font-size: 13px;">
                    <strong>{regulation}</strong><br>
                    {description[:150]}{'...' if len(description) > 150 else ''}
                </td>
                <td style="padding: 15px; border-bottom: 1px solid #e5e7eb; color: #6b7280; font-size: 12px;">
                    {location}
                </td>
            </tr>"""
        
        ai_act_findings_html = f"""
        <div style="background: white; border-radius: 15px; padding: 30px; margin: 20px 0; box-shadow: 0 6px 20px rgba(0,0,0,0.1);">
            <h2 style="color: #dc2626; margin-bottom: 25px; display: flex; align-items: center;">
                🔍 EU AI Act 2025 Compliance Findings
            </h2>
            <div style="background: #fef2f2; padding: 15px; border-radius: 8px; margin-bottom: 25px; border-left: 4px solid #dc2626;">
                <p style="color: #991b1b; margin: 0; font-weight: 500;">
                    ⚠️ <strong>{len(ai_act_findings)} EU AI Act compliance issues detected</strong> - Immediate review and remediation recommended
                </p>
            </div>
            <div style="overflow-x: auto;">
                <table style="width: 100%; border-collapse: collapse; min-width: 700px;">
                    <thead>
                        <tr style="background: linear-gradient(135deg, #1e40af, #3b82f6); color: white;">
                            <th style="padding: 15px; text-align: left; font-weight: 600; width: 100px;">Risk Level</th>
                            <th style="padding: 15px; text-align: left; font-weight: 600; width: 150px;">Violation Type</th>
                            <th style="padding: 15px; text-align: left; font-weight: 600;">Regulatory Requirement</th>
                            <th style="padding: 15px; text-align: left; font-weight: 600; width: 120px;">Location</th>
                        </tr>
                    </thead>
                    <tbody>
                        {findings_rows}
                    </tbody>
                </table>
            </div>
            <p style="color: #6b7280; font-style: italic; margin-top: 20px; text-align: center;">
                Showing {len(ai_act_findings)} AI Act compliance findings - Full regulatory compliance assessment conducted
            </p>
        </div>"""
    
    # Generate remediation recommendations
    remediation_html = f"""
    <div style="background: white; border-radius: 15px; padding: 30px; margin: 20px 0; box-shadow: 0 6px 20px rgba(0,0,0,0.1);">
        <h2 style="color: #059669; margin-bottom: 25px; display: flex; align-items: center;">
            🛡️ EU AI Act 2025 Compliance Recommendations
        </h2>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
            <div style="background: #f0f9ff; padding: 20px; border-radius: 10px; border-left: 4px solid #0ea5e9;">
                <h4 style="color: #0c4a6e; margin: 0 0 15px 0;">📋 Immediate Actions</h4>
                <ul style="color: #075985; margin: 0; padding-left: 20px; line-height: 1.6;">
                    <li>Conduct comprehensive AI system inventory</li>
                    <li>Classify AI systems by risk level (prohibited, high-risk, limited risk)</li>
                    <li>Implement transparency disclosures for user-facing AI</li>
                    <li>Establish fundamental rights impact assessment procedures</li>
                </ul>
            </div>
            
            <div style="background: #f0fdf4; padding: 20px; border-radius: 10px; border-left: 4px solid #16a34a;">
                <h4 style="color: #166534; margin: 0 0 15px 0;">🏛️ Governance Framework</h4>
                <ul style="color: #15803d; margin: 0; padding-left: 20px; line-height: 1.6;">
                    <li>Appoint AI governance officer and compliance team</li>
                    <li>Establish AI ethics committee with diverse representation</li>
                    <li>Create algorithmic accountability policies</li>
                    <li>Implement regular AI system auditing procedures</li>
                </ul>
            </div>
            
            <div style="background: #fff7ed; padding: 20px; border-radius: 10px; border-left: 4px solid #ea580c;">
                <h4 style="color: #c2410c; margin: 0 0 15px 0;">⚖️ Legal Compliance</h4>
                <ul style="color: #c2410c; margin: 0; padding-left: 20px; line-height: 1.6;">
                    <li>Review and update privacy policies for AI disclosure</li>
                    <li>Ensure data processing agreements cover AI use</li>
                    <li>Implement user consent mechanisms for AI processing</li>
                    <li>Establish procedures for handling AI-related complaints</li>
                </ul>
            </div>
            
            <div style="background: #f5f3ff; padding: 20px; border-radius: 10px; border-left: 4px solid #8b5cf6;">
                <h4 style="color: #7c3aed; margin: 0 0 15px 0;">🔧 Technical Measures</h4>
                <ul style="color: #7c3aed; margin: 0; padding-left: 20px; line-height: 1.6;">
                    <li>Implement explainable AI mechanisms where required</li>
                    <li>Establish model monitoring and drift detection</li>
                    <li>Create audit trails for AI decision-making</li>
                    <li>Implement bias detection and mitigation measures</li>
                </ul>
            </div>
        </div>
        
        <div style="background: #f8fafc; padding: 20px; border-radius: 10px; margin-top: 25px;">
            <h4 style="color: #374151; margin: 0 0 15px 0;">📈 Implementation Timeline</h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                <div style="text-align: center; padding: 15px;">
                    <div style="background: #dc2626; color: white; padding: 8px; border-radius: 6px; font-weight: bold; margin-bottom: 8px;">Week 1-2</div>
                    <p style="color: #4b5563; font-size: 12px; margin: 0;">Risk assessment & system inventory</p>
                </div>
                <div style="text-align: center; padding: 15px;">
                    <div style="background: #ea580c; color: white; padding: 8px; border-radius: 6px; font-weight: bold; margin-bottom: 8px;">Week 3-6</div>
                    <p style="color: #4b5563; font-size: 12px; margin: 0;">Governance framework setup</p>
                </div>
                <div style="background: #d97706; color: white; padding: 8px; border-radius: 6px; font-weight: bold; margin-bottom: 8px;">Month 2-3</div>
                    <p style="color: #4b5563; font-size: 12px; margin: 0;">Technical implementation</p>
                </div>
                <div style="text-align: center; padding: 15px;">
                    <div style="background: #16a34a; color: white; padding: 8px; border-radius: 6px; font-weight: bold; margin-bottom: 8px;">Ongoing</div>
                    <p style="color: #4b5563; font-size: 12px; margin: 0;">Monitoring & compliance</p>
                </div>
            </div>
        </div>
    </div>"""
    
    # Generate complete HTML report
    lang_attr = 'nl' if language == 'nl' else 'en'
    return f"""<!DOCTYPE html>
<html lang="{lang_attr}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{_('eu_ai_act_report.title', 'EU AI Act 2025 Compliance Assessment')} - {ai_system_name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f8fafc; color: #1f2937; line-height: 1.6; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e5e7eb; }}
        th {{ background: #f9fafb; font-weight: 600; color: #374151; }}
        .certification-seal {{ 
            position: absolute; 
            top: 20px; 
            right: 20px; 
            width: 80px; 
            height: 80px; 
            background: linear-gradient(135deg, #1e40af, #3b82f6); 
            border-radius: 50%; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            color: white; 
            font-weight: bold; 
            font-size: 12px; 
            text-align: center;
            box-shadow: 0 4px 15px rgba(30, 64, 175, 0.3);
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header Section -->
        <div style="background: linear-gradient(135deg, #1e40af, #3b82f6); color: white; padding: 40px; border-radius: 15px; margin-bottom: 30px; position: relative; overflow: hidden;">
            <div class="certification-seal">
                🇪🇺<br>{_('eu_ai_act_report.certification_seal', 'AI ACT 2025')}
            </div>
            <h1 style="font-size: 32px; margin-bottom: 10px; font-weight: 700;">{_('eu_ai_act_report.title', 'EU AI Act 2025 Compliance Assessment')}</h1>
            <p style="font-size: 18px; opacity: 0.9; margin-bottom: 20px;">{_('eu_ai_act_report.subtitle', 'Comprehensive regulatory compliance analysis for')} {ai_system_name}</p>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 30px;">
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; text-align: center; backdrop-filter: blur(10px);">
                    <div style="font-size: 24px; font-weight: bold;">{len(ai_act_findings)}</div>
                    <div style="font-size: 14px; opacity: 0.8;">{_('eu_ai_act_report.ai_act_findings', 'AI Act Findings')}</div>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; text-align: center; backdrop-filter: blur(10px);">
                    <div style="font-size: 24px; font-weight: bold;">{compliance_score}%</div>
                    <div style="font-size: 14px; opacity: 0.8;">{_('eu_ai_act_report.compliance_score', 'Compliance Score')}</div>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; text-align: center; backdrop-filter: blur(10px);">
                    <div style="font-size: 18px; font-weight: bold; color: {risk_color};">{ai_risk_level}</div>
                    <div style="font-size: 14px; opacity: 0.8;">{_('eu_ai_act_report.ai_act_risk_level', 'AI Act Risk Level')}</div>
                </div>
            </div>
        </div>
        
        <!-- System Overview -->
        <div style="background: white; border-radius: 15px; padding: 30px; margin: 20px 0; box-shadow: 0 6px 20px rgba(0,0,0,0.1);">
            <h2 style="color: #1e40af; margin-bottom: 20px;">🤖 AI System Overview</h2>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 25px;">
                <div style="background: {risk_bg}; padding: 20px; border-radius: 10px; text-align: center; border-left: 4px solid {risk_color};">
                    <h3 style="color: {risk_color}; margin: 0; font-size: 16px;">{overall_risk}</h3>
                    <p style="color: #6b7280; margin: 5px 0 0 0; font-size: 12px;">Overall Assessment</p>
                </div>
                <div style="background: #f0f9ff; padding: 20px; border-radius: 10px; text-align: center; border-left: 4px solid #0ea5e9;">
                    <h3 style="color: #0ea5e9; margin: 0; font-size: 16px;">{model_framework}</h3>
                    <p style="color: #6b7280; margin: 5px 0 0 0; font-size: 12px;">AI Framework</p>
                </div>
                <div style="background: #f5f3ff; padding: 20px; border-radius: 10px; text-align: center; border-left: 4px solid #8b5cf6;">
                    <h3 style="color: #8b5cf6; margin: 0; font-size: 16px;">{model_source}</h3>
                    <p style="color: #6b7280; margin: 5px 0 0 0; font-size: 12px;">Model Source</p>
                </div>
            </div>
            
            <div style="background: #f8fafc; padding: 20px; border-radius: 10px;">
                <h3 style="color: #374151; margin-bottom: 15px;">Assessment Summary</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                    <p style="color: #6b7280; margin: 0;"><strong>AI System:</strong> {ai_system_name}</p>
                    <p style="color: #6b7280; margin: 0;"><strong>Assessment Date:</strong> {timestamp}</p>
                    <p style="color: #6b7280; margin: 0;"><strong>Compliance Status:</strong> <span style="color: {risk_color}; font-weight: bold;">{ai_act_compliance}</span></p>
                    <p style="color: #6b7280; margin: 0;"><strong>Regulation:</strong> EU AI Act (Regulation 2024/1689)</p>
                </div>
            </div>
        </div>
        
        {ai_act_requirements_html}
        {ai_act_findings_html}
        {remediation_html}
        
        <!-- Enforcement and Penalties Section -->
        <div style="background: white; border-radius: 15px; padding: 30px; margin: 20px 0; box-shadow: 0 6px 20px rgba(0,0,0,0.1);">
            <h2 style="color: #dc2626; margin-bottom: 25px; display: flex; align-items: center;">
                ⚖️ EU AI Act Enforcement & Penalties
            </h2>
            
            <div style="background: #fef2f2; padding: 20px; border-radius: 10px; border-left: 4px solid #dc2626; margin-bottom: 25px;">
                <h3 style="color: #991b1b; margin: 0 0 15px 0;">💰 Administrative Fines</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
                    <div style="background: white; padding: 15px; border-radius: 8px;">
                        <div style="font-size: 20px; font-weight: bold; color: #dc2626;">€35M or 7% turnover</div>
                        <p style="color: #6b7280; font-size: 12px; margin: 5px 0 0 0;">Prohibited AI practices (Article 5)</p>
                    </div>
                    <div style="background: white; padding: 15px; border-radius: 8px;">
                        <div style="font-size: 20px; font-weight: bold; color: #ea580c;">€15M or 3% turnover</div>
                        <p style="color: #6b7280; font-size: 12px; margin: 5px 0 0 0;">High-risk system violations</p>
                    </div>
                    <div style="background: white; padding: 15px; border-radius: 8px;">
                        <div style="font-size: 20px; font-weight: bold; color: #d97706;">€7.5M or 1.5% turnover</div>
                        <p style="color: #6b7280; font-size: 12px; margin: 5px 0 0 0;">Other AI Act violations</p>
                    </div>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                <div style="background: #fff7ed; padding: 20px; border-radius: 10px;">
                    <h4 style="color: #ea580c; margin: 0 0 15px 0;">🏛️ Enforcement Authorities</h4>
                    <ul style="color: #c2410c; margin: 0; padding-left: 20px; line-height: 1.6;">
                        <li>National supervisory authorities in each EU Member State</li>
                        <li>European Artificial Intelligence Board (coordination)</li>
                        <li>Market surveillance authorities (product compliance)</li>
                        <li>Data protection authorities (privacy compliance)</li>
                    </ul>
                </div>
                
                <div style="background: #f0f9ff; padding: 20px; border-radius: 10px;">
                    <h4 style="color: #0ea5e9; margin: 0 0 15px 0;">📋 Compliance Obligations</h4>
                    <ul style="color: #0c4a6e; margin: 0; padding-left: 20px; line-height: 1.6;">
                        <li>Risk management systems for high-risk AI</li>
                        <li>Conformity assessments before market placement</li>
                        <li>Post-market monitoring and reporting</li>
                        <li>Transparency and information obligations</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <!-- Certification Footer -->
        <div style="background: white; border-radius: 15px; margin: 20px 0; padding: 30px; text-align: center; box-shadow: 0 6px 20px rgba(0,0,0,0.1);">
            <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 20px;">
                <div style="width: 60px; height: 60px; background: linear-gradient(135deg, #1e40af, #3b82f6); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 20px;">
                    <span style="color: white; font-weight: bold; font-size: 20px;">✓</span>
                </div>
                <div style="text-align: left;">
                    <h3 style="color: #1e40af; margin: 0;">EU AI Act 2025 Certified Assessment</h3>
                    <p style="color: #6b7280; margin: 5px 0 0 0; font-size: 14px;">Complete regulatory compliance evaluation</p>
                </div>
            </div>
            
            <p style="color: #374151; font-size: 12px; line-height: 1.6; max-width: 600px; margin: 0 auto 20px auto;">
                This EU AI Act 2025 compliance assessment was conducted on {timestamp} using DataGuardian Pro's comprehensive 
                AI compliance scanner. The assessment covers all requirements of the EU Artificial Intelligence Act (Regulation 2024/1689)
                including prohibited practices, high-risk system obligations, transparency requirements, and fundamental rights protections.
            </p>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 2px solid #e5e7eb;">
                <p style="color: #6b7280; font-size: 11px; margin: 5px 0;">
                    <strong>DataGuardian Pro Enterprise Certification Authority</strong>
                </p>
                <p style="color: #6b7280; font-size: 10px; margin: 0;">
                    EU AI Act 2025 Compliance & Risk Assessment Platform
                </p>
            </div>
        </div>
    </div>
</body>
</html>"""