import io
import base64
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import json
try:
    import streamlit as st
except ImportError:
    # Fallback for testing environments where streamlit might not be available
    class StreamlitMock:
        session_state = {"language": "en"}
    st = StreamlitMock()

# Import translation utilities
try:
    from utils.i18n import _
except ImportError:
    # Fallback translation function if module not available
    def _(key, default=None):
        return default

def save_html_report(scan_data: Dict[str, Any], output_dir: str = "reports") -> str:
    """
    Save a HTML report for a scan result.
    
    Args:
        scan_data: The scan result data
        output_dir: Directory to save the report
        
    Returns:
        Path to the saved HTML file
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate a filename based on scan data
    scan_id = scan_data.get('scan_id', f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    scan_type = scan_data.get('scan_type', 'Unknown').replace(" ", "_")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Get current language from session state
    current_lang = st.session_state.get('language', 'en')
    
    # Change filename based on language
    if current_lang == 'nl':
        filename = f"AVG_Rapport_{scan_type}_{scan_id}_{timestamp}.html"
    else:
        filename = f"GDPR_Report_{scan_type}_{scan_id}_{timestamp}.html"
        
    file_path = os.path.join(output_dir, filename)
    
    # Create HTML content
    html_content = generate_html_report(scan_data)
    
    # Write to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return file_path

def get_html_report_as_base64(scan_data: Dict[str, Any]) -> str:
    """
    Generate a base64-encoded HTML report for a scan result.
    
    Args:
        scan_data: The scan result data
        
    Returns:
        Base64-encoded HTML report
    """
    # Generate HTML content
    html_content = generate_html_report(scan_data)
    
    # Encode as base64
    encoded_content = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
    
    return encoded_content

def generate_html_report(scan_data: Dict[str, Any]) -> str:
    """
    Generate a HTML report for a scan result using unified system.
    
    Args:
        scan_data: The scan result data
        
    Returns:
        HTML report as a string
    """
    from services.unified_html_report_generator import generate_unified_html_report
    return generate_unified_html_report(scan_data)
    
    # Extract basic scan info
    scan_id = scan_data.get('scan_id', 'Unknown')
    scan_type = scan_data.get('scan_type', 'Unknown')
    region = scan_data.get('region', 'Unknown')
    timestamp = scan_data.get('timestamp', 'Unknown')
    
    # Check if this is an AI model scan
    is_ai_model_scan = scan_type.lower() == 'ai model' or 'ai_model' in str(scan_type).lower()
    
    # Get URL information - for AI Model scans, use repository_url
    if is_ai_model_scan:
        url = scan_data.get('repository_url', scan_data.get('model_name', scan_data.get('hub_url', scan_data.get('api_endpoint', 'Not available'))))
    else:
        url = scan_data.get('url', scan_data.get('domain', 'Not available'))
    
    # Import logging for debugging
    import logging
    
    # For AI Model reports, calculate counts directly from findings
    if is_ai_model_scan and 'findings' in scan_data:
        # Count findings by risk level
        findings = scan_data.get('findings', [])
        high_risk = 0
        medium_risk = 0
        low_risk = 0
        
        logging.info(f"HTML Report: Calculating AI model risk counts from {len(findings)} findings")
        
        for finding in findings:
            risk_level = finding.get('risk_level', 'low')
            # Ensure risk_level is a string and normalized to lowercase for comparison
            if isinstance(risk_level, str):
                risk_level_lower = risk_level.lower()
            else:
                risk_level_lower = str(risk_level).lower()
                
            # Count based on risk level
            if risk_level_lower == 'high':
                high_risk += 1
            elif risk_level_lower == 'medium':
                medium_risk += 1
            else:
                low_risk += 1
                
        # Set total findings count
        total_pii = len(findings)
        
        # Update the scan_data with calculated counts to ensure consistency
        scan_data['total_pii_found'] = total_pii
        scan_data['high_risk_count'] = high_risk
        scan_data['medium_risk_count'] = medium_risk
        scan_data['low_risk_count'] = low_risk
        
        logging.info(f"HTML Report: Calculated AI model counts - Total: {total_pii}, High: {high_risk}, Medium: {medium_risk}, Low: {low_risk}")
    else:
        # Use existing counts from the scan data
        total_pii = scan_data.get('total_pii_found', 0)
        high_risk = scan_data.get('high_risk_count', 0)
        medium_risk = scan_data.get('medium_risk_count', 0)
        low_risk = scan_data.get('low_risk_count', 0)
    
    # Format timestamp
    if timestamp != 'Unknown':
        try:
            if current_lang == 'nl':
                # Dutch date format
                timestamp = datetime.fromisoformat(timestamp).strftime('%d-%m-%Y %H:%M:%S')
            else:
                timestamp = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        except:
            pass
    
    # Prepare PII types data
    pii_types = scan_data.get('pii_types', {})
    pii_types_labels = list(pii_types.keys())
    pii_types_values = list(pii_types.values())
    
    # Prepare risk levels data with translations
    if current_lang == 'nl':
        risk_levels = {
            'Hoog': high_risk,
            'Gemiddeld': medium_risk,
            'Laag': low_risk
        }
    else:
        risk_levels = {
            'High': high_risk,
            'Medium': medium_risk,
            'Low': low_risk
        }
    risk_labels = list(risk_levels.keys())
    risk_values = list(risk_levels.values())
    
    # Create findings table data
    findings = scan_data.get('findings', [])
    findings_table_rows = ""
    
    # Import logging for debugging (already imported above)
    logging.info(f"Generating HTML report for scan type: {scan_type}, AI model scan: {is_ai_model_scan}")
    
    for finding in findings:
        risk_level = finding.get('risk_level', 'Unknown')
        
        # Ensure risk_level is a string and normalized to lowercase for comparison
        if isinstance(risk_level, str):
            risk_level_lower = risk_level.lower()
        else:
            risk_level_lower = str(risk_level).lower()
        
        # Determine risk level color and translate risk level if needed
        if risk_level_lower == 'high' or risk_level_lower == 'hoog':
            risk_color = '#ffcdd2'
            risk_level_display = 'Hoog' if current_lang == 'nl' else 'High'
        elif risk_level_lower == 'medium' or risk_level_lower == 'gemiddeld':
            risk_color = '#fff9c4'
            risk_level_display = 'Gemiddeld' if current_lang == 'nl' else 'Medium'
        elif risk_level_lower == 'low' or risk_level_lower == 'laag':
            risk_color = '#e8f5e9'
            risk_level_display = 'Laag' if current_lang == 'nl' else 'Low'
        else:
            risk_color = '#e0e0e0'
            risk_level_display = 'Onbekend' if current_lang == 'nl' else 'Unknown'
        
        # Log the finding for debugging
        logging.info(f"Processing finding: {finding.get('type', 'Unknown')} - {risk_level_display}")
        
        # Handle AI model findings differently as they have a different structure
        if is_ai_model_scan:
            # Check if this finding has recommendations or remediation path
            has_recommendations = 'details' in finding and 'recommendations' in finding.get('details', {})
            has_remediation = 'details' in finding and 'remediation_path' in finding.get('details', {})
            
            # Create recommendation list HTML if available
            recommendation_html = ""
            if has_recommendations:
                recommendation_list = finding.get('details', {}).get('recommendations', [])
                if recommendation_list:
                    recommendation_html = "<div class='finding-recommendations'><strong>Recommendations:</strong><ul>"
                    for rec in recommendation_list:
                        recommendation_html += f"<li>{rec}</li>"
                    recommendation_html += "</ul></div>"
            
            # Create remediation path HTML if available
            remediation_html = ""
            if has_remediation:
                remediation_path = finding.get('details', {}).get('remediation_path', "")
                if remediation_path:
                    remediation_html = f"<div class='finding-remediation'><strong>Remediation:</strong> {remediation_path}</div>"
            
            findings_table_rows += f"""
            <tr style="background-color: {risk_color}">
                <td>{finding.get('type', 'Unknown')}</td>
                <td>{finding.get('category', 'Unknown')}</td>
                <td>{finding.get('location', 'Unknown')}</td>
                <td>{risk_level_display}</td>
                <td>
                    <div>{finding.get('description', 'Unknown')}</div>
                    {recommendation_html}
                    {remediation_html}
                </td>
            </tr>
            """
        else:
            # Standard findings structure
            findings_table_rows += f"""
            <tr style="background-color: {risk_color}">
                <td>{finding.get('type', 'Unknown')}</td>
                <td>{finding.get('value', 'Unknown')}</td>
                <td>{finding.get('location', 'Unknown')}</td>
                <td>{risk_level_display}</td>
                <td>{finding.get('reason', 'Unknown')}</td>
            </tr>
            """
    
    # Recommendations
    recommendations = scan_data.get('recommendations', [])
    recommendations_html = ""
    for rec in recommendations:
        priority = rec.get('priority', 'Medium')
        
        # Translate priority level and determine color
        if priority == 'High' or priority == 'Hoog':
            priority_color = '#ffcdd2'
            priority_display = 'Hoog' if current_lang == 'nl' else 'High'
        elif priority == 'Medium' or priority == 'Gemiddeld':
            priority_color = '#fff9c4'
            priority_display = 'Gemiddeld' if current_lang == 'nl' else 'Medium'
        elif priority == 'Low' or priority == 'Laag':
            priority_color = '#e8f5e9'
            priority_display = 'Laag' if current_lang == 'nl' else 'Low'
        else:
            priority_color = '#e0e0e0'
            priority_display = 'Onbekend' if current_lang == 'nl' else 'Unknown'
        
        steps_html = ""
        for step in rec.get('steps', []):
            steps_html += f"<li>{step}</li>"
        
        # Translate label for "Steps" and "Priority"
        steps_label = "Stappen" if current_lang == 'nl' else "Steps"
        priority_label = "Prioriteit" if current_lang == 'nl' else "Priority"
        
        recommendations_html += f"""
        <div class="recommendation" style="margin-bottom: 20px; padding: 15px; border-radius: 4px; background-color: {priority_color};">
            <h4>{rec.get('title', 'Recommendation')}</h4>
            <p><strong>{priority_label}:</strong> {priority_display}</p>
            <p>{rec.get('description', '')}</p>
            <h5>{steps_label}:</h5>
            <ul>
                {steps_html}
            </ul>
        </div>
        """
    
    # Prepare data for JavaScript charts
    pii_types_data = json.dumps({
        'labels': pii_types_labels,
        'values': pii_types_values
    })
    
    risk_levels_data = json.dumps({
        'labels': risk_labels,
        'values': risk_values
    })
    
    # Set language-specific translations for section titles and labels
    if current_lang == 'nl':
        # Dutch translations
        html_lang = 'nl'
        report_title = 'AVG-compliance Scan Rapport'
        generated_on = 'Gegenereerd op'
        scan_id_label = 'Scan ID'
        
        summary_title = 'Samenvatting'
        scan_type_label = 'Scan Type'
        region_label = 'Regio'
        date_time_label = 'Datum & Tijd'
        url_label = 'URL/Domein'
        total_pii_label = 'Totaal PII Items Gevonden'
        high_risk_label = 'Hoog Risico Items'
        
        risk_assessment_title = 'Risicobeoordeling'
        total_pii_header = 'Totaal PII'
        high_risk_header = 'Hoog Risico'
        medium_risk_header = 'Gemiddeld Risico'
        low_risk_header = 'Laag Risico'
        total_pii_desc = 'Totaal gedetecteerde PII items'
        high_risk_desc = 'Hoog risico items'
        medium_risk_desc = 'Gemiddeld risico items'
        low_risk_desc = 'Laag risico items'
        
        data_analysis_title = 'Gegevensanalyse'
        pii_distribution_title = 'PII Types Verdeling'
        risk_distribution_title = 'Risico Niveau Verdeling'
        
        findings_title = 'Bevindingen'
        pii_type_header = 'PII Type'
        value_header = 'Waarde'
        location_header = 'Locatie'
        risk_level_header = 'Risico Niveau'
        reason_header = 'Reden'
        
        recommendations_title = 'Aanbevelingen'
        general_recommendations_title = 'Algemene AVG Aanbevelingen'
        no_recommendations = 'Geen specifieke aanbevelingen beschikbaar voor deze scan.'
        recommendation_1 = 'Zorg voor een juiste juridische basis voor de verwerking van alle geïdentificeerde PII.'
        recommendation_2 = 'Documenteer alle verwerkingsactiviteiten zoals vereist door AVG Artikel 30.'
        recommendation_3 = 'Herzie het data retentiebeleid om ervoor te zorgen dat PII niet langer dan nodig wordt bewaard.'
        recommendation_4 = 'Implementeer passende technische en organisatorische maatregelen om PII te beveiligen.'
        
        metadata_title = 'Metadata'
        timestamp_label = 'Tijdstempel'
        
        disclaimer_text = 'Disclaimer: Dit rapport wordt uitsluitend ter informatie verstrekt en mag niet worden beschouwd als juridisch advies. De bevindingen in dit rapport zijn gebaseerd op geautomatiseerde scans en identificeren mogelijk niet alle AVG-relevante persoonsgegevens. Wij raden aan om een gekwalificeerde juridische professional te raadplegen voor specifieke AVG-compliance richtlijnen.'
    else:
        # English translations
        html_lang = 'en'
        report_title = 'GDPR Compliance Scan Report'
        generated_on = 'Generated on'
        scan_id_label = 'Scan ID'
        
        summary_title = 'Summary'
        scan_type_label = 'Scan Type'
        region_label = 'Region'
        date_time_label = 'Date & Time'
        url_label = 'URL/Domain'
        total_pii_label = 'Total PII Items Found'
        high_risk_label = 'High Risk Items'
        
        risk_assessment_title = 'Risk Assessment'
        total_pii_header = 'Total PII'
        high_risk_header = 'High Risk'
        medium_risk_header = 'Medium Risk'
        low_risk_header = 'Low Risk'
        total_pii_desc = 'Total PII items detected'
        high_risk_desc = 'High risk items'
        medium_risk_desc = 'Medium risk items'
        low_risk_desc = 'Low risk items'
        
        data_analysis_title = 'Data Analysis'
        pii_distribution_title = 'PII Types Distribution'
        risk_distribution_title = 'Risk Level Distribution'
        
        findings_title = 'Findings'
        pii_type_header = 'PII Type'
        value_header = 'Value'
        location_header = 'Location'
        risk_level_header = 'Risk Level'
        reason_header = 'Reason'
        
        recommendations_title = 'Recommendations'
        general_recommendations_title = 'General GDPR Recommendations'
        no_recommendations = 'No specific recommendations available for this scan.'
        recommendation_1 = 'Ensure you have proper legal basis for processing all identified PII.'
        recommendation_2 = 'Document all processing activities as required by GDPR Article 30.'
        recommendation_3 = 'Review data retention policies to ensure PII is not kept longer than necessary.'
        recommendation_4 = 'Implement appropriate technical and organizational measures to secure PII.'
        
        metadata_title = 'Metadata'
        timestamp_label = 'Timestamp'
        
        disclaimer_text = 'Disclaimer: This report is provided for informational purposes only and should not be considered legal advice. The findings in this report are based on automated scanning and may not identify all GDPR-relevant personal data. We recommend consulting with a qualified legal professional for specific GDPR compliance guidance.'
    
    # Format current date/time according to locale
    if current_lang == 'nl':
        current_datetime = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    else:
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Build the HTML content
    html_content = f"""<!DOCTYPE html>
<html lang="{html_lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report_title} - {scan_id}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/tablesorter@2.31.3/dist/js/jquery.tablesorter.combined.min.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/tablesorter@2.31.3/dist/css/theme.blue.min.css">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background-color: #f5f5f5;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin-top: 0;
            color: #2c3e50;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        table, th, td {{
            border: 1px solid #ddd;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        .chart-container {{
            width: 100%;
            max-width: 600px;
            margin: 0 auto 20px auto;
        }}
        .metrics {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 20px;
        }}
        .metric-card {{
            flex: 1;
            min-width: 200px;
            padding: 15px;
            background-color: #f5f5f5;
            border-radius: 5px;
            text-align: center;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        }}
        .risk-high {{
            color: #d32f2f;
        }}
        .risk-medium {{
            color: #f57c00;
        }}
        .risk-low {{
            color: #388e3c;
        }}
        .tablesorter-blue .tablesorter-header {{
            background-color: #2c3e50;
            color: white;
        }}
        .finding-recommendations {{
            margin-top: 10px;
            padding: 10px;
            background-color: #f8f9fa;
            border-left: 3px solid #4682b4;
            font-size: 0.9em;
        }}
        .finding-recommendations ul {{
            margin: 5px 0 5px 20px;
            padding: 0;
        }}
        .finding-recommendations li {{
            margin-bottom: 3px;
        }}
        .finding-remediation {{
            margin-top: 10px;
            padding: 10px;
            background-color: #e6f7ff;
            border-left: 3px solid #1e90ff;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{report_title}</h1>
        <p><strong>{generated_on}:</strong> {current_datetime}</p>
        <p><strong>{scan_id_label}:</strong> {scan_id}</p>
    </div>
    
    <div class="section">
        <h2>{summary_title}</h2>
        <table>
            <tr>
                <th>{scan_type_label}</th>
                <td>{scan_type}</td>
            </tr>
            <tr>
                <th>{region_label}</th>
                <td>{region}</td>
            </tr>
            <tr>
                <th>{date_time_label}</th>
                <td>{timestamp}</td>
            </tr>
            <tr>
                <th>{url_label}</th>
                <td>{url}</td>
            </tr>
            <tr>
                <th>{total_pii_label}</th>
                <td>{total_pii}</td>
            </tr>
            <tr>
                <th>{high_risk_label}</th>
                <td>{high_risk}</td>
            </tr>
        </table>
    </div>
    
    <div class="section">
        <h2>{risk_assessment_title}</h2>
        <div class="metrics">
            <div class="metric-card">
                <h3>{total_pii_header}</h3>
                <div class="metric-value">{total_pii}</div>
                <p>{total_pii_desc}</p>
            </div>
            <div class="metric-card">
                <h3>{high_risk_header}</h3>
                <div class="metric-value risk-high">{high_risk}</div>
                <p>{high_risk_desc}</p>
            </div>
            <div class="metric-card">
                <h3>{medium_risk_header}</h3>
                <div class="metric-value risk-medium">{medium_risk}</div>
                <p>{medium_risk_desc}</p>
            </div>
            <div class="metric-card">
                <h3>{low_risk_header}</h3>
                <div class="metric-value risk-low">{low_risk}</div>
                <p>{low_risk_desc}</p>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>{data_analysis_title}</h2>
        <div class="chart-container">
            <h3>{pii_distribution_title}</h3>
            <canvas id="piiTypesChart"></canvas>
        </div>
        
        <div class="chart-container">
            <h3>{risk_distribution_title}</h3>
            <canvas id="riskLevelsChart"></canvas>
        </div>
    </div>
    
    <div class="section">
        <h2>{findings_title}</h2>
        <table id="findingsTable" class="tablesorter">
            <thead>
                <tr>
                    <th>{pii_type_header}</th>
                    <th>{is_ai_model_scan and "Category" or value_header}</th>
                    <th>{location_header}</th>
                    <th>{risk_level_header}</th>
                    <th>{is_ai_model_scan and "Description" or reason_header}</th>
                </tr>
            </thead>
            <tbody>
                {findings_table_rows}
            </tbody>
        </table>
    </div>
    
    <!-- Professional Certificate-Style Layout for Sustainability Reports -->
    {f'''
    <div style="background: linear-gradient(135deg, #f0fdf4, #ecfdf5); padding: 0; margin: 0;">
        <!-- Certificate Header -->
        <div style="background: white; border: 3px solid #059669; border-radius: 15px; margin: 20px; padding: 30px; position: relative; box-shadow: 0 8px 25px rgba(0,0,0,0.15);">
            <!-- Certificate Border Pattern -->
            <div style="position: absolute; top: 10px; left: 10px; right: 10px; bottom: 10px; border: 2px solid #10b981; border-radius: 10px; background: linear-gradient(45deg, #f0fdf4 25%, transparent 25%), linear-gradient(-45deg, #f0fdf4 25%, transparent 25%), linear-gradient(45deg, transparent 75%, #f0fdf4 75%), linear-gradient(-45deg, transparent 75%, #f0fdf4 75%); background-size: 20px 20px; background-position: 0 0, 0 10px, 10px -10px, -10px 0px;"></div>
            
            <!-- Certificate Seal -->
            <div style="position: absolute; top: 30px; right: 50px; width: 80px; height: 80px; background: linear-gradient(135deg, #059669, #10b981); border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 15px rgba(5, 150, 105, 0.4);">
                <div style="color: white; font-size: 24px; font-weight: bold;">✓</div>
            </div>
            
            <!-- Certificate Title -->
            <div style="text-align: center; position: relative; z-index: 10;">
                <h1 style="color: #166534; font-size: 28px; margin-bottom: 10px; font-family: 'Times New Roman', serif; letter-spacing: 2px;">
                    SUSTAINABILITY COMPLIANCE CERTIFICATE
                </h1>
                <h2 style="color: #059669; font-size: 16px; margin-bottom: 30px; font-weight: normal;">
                    DataGuardian Pro Enterprise Certification
                </h2>
                
                <p style="font-size: 14px; color: #374151; margin: 20px 0;">This certifies that</p>
                <h3 style="color: #166534; font-size: 20px; margin: 10px 0; font-weight: bold; text-decoration: underline;">
                    {scan_data.get("repository_url", scan_data.get("url", "Repository Analysis"))}
                </h3>
                <p style="font-size: 14px; color: #374151; margin: 20px 0;">has been assessed for environmental sustainability compliance</p>
                
                <p style="font-size: 12px; color: #6b7280; margin-top: 30px;">
                    Certified on {datetime.now().strftime("%B %d, %Y")}
                </p>
            </div>
        </div>
        
        <!-- Professional Score Dashboard -->
        <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 30px; margin: 30px 20px;">
            <!-- Score Card -->
            <div style="background: white; border-radius: 15px; padding: 30px; text-align: center; box-shadow: 0 6px 20px rgba(0,0,0,0.1); border: 2px solid #e2e8f0;">
                <div style="background: {"linear-gradient(135deg, #10b981, #059669)" if scan_data.get("sustainability_score", 0) >= 80 else "linear-gradient(135deg, #f59e0b, #d97706)" if scan_data.get("sustainability_score", 0) >= 60 else "linear-gradient(135deg, #ef4444, #dc2626)"}; color: white; padding: 40px 20px; border-radius: 10px; margin-bottom: 20px;">
                    <div style="font-size: 48px; font-weight: bold; margin-bottom: 10px;">
                        {int(scan_data.get("sustainability_score", 0))}
                    </div>
                    <div style="font-size: 16px; font-weight: bold; letter-spacing: 2px;">
                        SUSTAINABILITY SCORE
                    </div>
                </div>
                
                <div style="text-align: left; margin-top: 20px;">
                    <div style="margin-bottom: 15px;">
                        <strong style="color: #1f2937;">Annual CO₂ Emissions:</strong><br>
                        <span style="color: #dc2626; font-size: 18px; font-weight: bold;">
                            {scan_data.get("carbon_footprint", {}).get("carbon_emissions_kg_annually", 0):.1f} kg
                        </span>
                    </div>
                    <div>
                        <strong style="color: #1f2937;">Energy Waste:</strong><br>
                        <span style="color: #dc2626; font-size: 18px; font-weight: bold;">
                            {scan_data.get("carbon_footprint", {}).get("total_energy_waste_kwh_annually", 0):.1f} kWh/yr
                        </span>
                    </div>
                </div>
            </div>
            
            <!-- Environmental Impact Visualization -->
            <div style="background: white; border-radius: 15px; padding: 30px; box-shadow: 0 6px 20px rgba(0,0,0,0.1); border: 2px solid #e2e8f0;">
                <h3 style="color: #166534; text-align: center; margin-bottom: 30px; font-size: 18px;">
                    Environmental Impact Analysis
                </h3>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 40px; margin-bottom: 30px;">
                    <!-- Current Impact Bar -->
                    <div style="text-align: center;">
                        <div style="background: #dc2626; height: {min(120, (scan_data.get("carbon_footprint", {}).get("carbon_emissions_kg_annually", 0) / max(scan_data.get("carbon_footprint", {}).get("carbon_emissions_kg_annually", 0), 1)) * 120)}px; width: 60px; margin: 0 auto 15px; border-radius: 5px; display: flex; align-items: end; justify-content: center; color: white; font-weight: bold; padding: 10px 0;">
                        </div>
                        <div style="font-weight: bold; color: #374151; margin-bottom: 5px;">Current Impact</div>
                        <div style="font-size: 12px; color: #6b7280;">
                            {scan_data.get("carbon_footprint", {}).get("carbon_emissions_kg_annually", 0):.1f} kg CO₂
                        </div>
                    </div>
                    
                    <!-- Potential Reduction Bar -->
                    <div style="text-align: center;">
                        <div style="background: #10b981; height: {min(120, (scan_data.get("carbon_footprint", {}).get("potential_savings", {}).get("carbon_kg_annually", 0) / max(scan_data.get("carbon_footprint", {}).get("carbon_emissions_kg_annually", 0), 1)) * 120)}px; width: 60px; margin: 0 auto 15px; border-radius: 5px; display: flex; align-items: end; justify-content: center; color: white; font-weight: bold; padding: 10px 0;">
                        </div>
                        <div style="font-weight: bold; color: #374151; margin-bottom: 5px;">Potential Reduction</div>
                        <div style="font-size: 12px; color: #6b7280;">
                            {scan_data.get("carbon_footprint", {}).get("potential_savings", {}).get("carbon_kg_annually", 0):.1f} kg CO₂
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Professional Summary Table -->
        <div style="margin: 30px 20px;">
            <div style="background: white; border-radius: 15px; padding: 30px; box-shadow: 0 6px 20px rgba(0,0,0,0.1); border: 2px solid #e2e8f0;">
                <h3 style="color: #166534; text-align: center; margin-bottom: 30px; font-size: 20px;">
                    Environmental Impact Summary
                </h3>
                
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                    <thead>
                        <tr style="background: linear-gradient(135deg, #059669, #10b981);">
                            <th style="padding: 20px; text-align: left; color: white; font-weight: bold; border-radius: 8px 0 0 0;">Metric</th>
                            <th style="padding: 20px; text-align: center; color: white; font-weight: bold;">Current Impact</th>
                            <th style="padding: 20px; text-align: center; color: white; font-weight: bold; border-radius: 0 8px 0 0;">Potential Improvement</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr style="background-color: #f0fdf4;">
                            <td style="padding: 15px; color: #065f46; font-weight: 500; border-bottom: 1px solid #bbf7d0;">Annual CO₂ Emissions</td>
                            <td style="padding: 15px; text-align: center; color: #065f46; border-bottom: 1px solid #bbf7d0;">
                                {scan_data.get("carbon_footprint", {}).get("carbon_emissions_kg_annually", 0):.2f} kg
                            </td>
                            <td style="padding: 15px; text-align: center; color: #065f46; border-bottom: 1px solid #bbf7d0;">
                                -{scan_data.get("carbon_footprint", {}).get("potential_savings", {}).get("carbon_kg_annually", 0):.2f} kg
                            </td>
                        </tr>
                        <tr style="background-color: #ecfdf5;">
                            <td style="padding: 15px; color: #065f46; font-weight: 500; border-bottom: 1px solid #bbf7d0;">Energy Consumption</td>
                            <td style="padding: 15px; text-align: center; color: #065f46; border-bottom: 1px solid #bbf7d0;">
                                {scan_data.get("carbon_footprint", {}).get("total_energy_waste_kwh_annually", 0):.1f} kWh/year
                            </td>
                            <td style="padding: 15px; text-align: center; color: #065f46; border-bottom: 1px solid #bbf7d0;">
                                -{scan_data.get("carbon_footprint", {}).get("potential_savings", {}).get("energy_kwh_annually", 0):.1f} kWh/year
                            </td>
                        </tr>
                        <tr style="background-color: #f0fdf4;">
                            <td style="padding: 15px; color: #065f46; font-weight: 500; border-bottom: 1px solid #bbf7d0;">Tree Equivalent</td>
                            <td style="padding: 15px; text-align: center; color: #065f46; border-bottom: 1px solid #bbf7d0;">
                                {scan_data.get("carbon_footprint", {}).get("carbon_emissions_kg_annually", 0)/22:.1f} trees needed
                            </td>
                            <td style="padding: 15px; text-align: center; color: #065f46; border-bottom: 1px solid #bbf7d0;">
                                +{scan_data.get("carbon_footprint", {}).get("potential_savings", {}).get("trees_equivalent", 0):.1f} trees saved
                            </td>
                        </tr>
                        <tr style="background-color: #ecfdf5;">
                            <td style="padding: 15px; color: #065f46; font-weight: 500;">Annual Cost Impact</td>
                            <td style="padding: 15px; text-align: center; color: #065f46;">
                                ${scan_data.get("carbon_footprint", {}).get("cost_impact_usd_annually", 0):.2f}
                            </td>
                            <td style="padding: 15px; text-align: center; color: #065f46;">
                                -${scan_data.get("carbon_footprint", {}).get("potential_savings", {}).get("cost_usd_annually", 0):.2f}
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Certificate Footer -->
        <div style="background: white; border-radius: 15px; margin: 30px 20px; padding: 30px; text-align: center; box-shadow: 0 6px 20px rgba(0,0,0,0.1); border: 2px solid #e2e8f0;">
            <p style="color: #374151; font-size: 12px; line-height: 1.6; max-width: 600px; margin: 0 auto;">
                This sustainability assessment was conducted on {timestamp} using DataGuardian Pro's advanced environmental impact analysis. 
                The assessment evaluated code efficiency, energy consumption patterns, and carbon footprint optimization opportunities.
            </p>
            <div style="margin-top: 30px; padding-top: 20px; border-top: 2px solid #e5e7eb;">
                <p style="color: #6b7280; font-size: 11px; margin: 5px 0;">
                    <strong>DataGuardian Pro Enterprise Certification Authority</strong>
                </p>
                <p style="color: #6b7280; font-size: 10px; margin: 0;">
                    Enterprise Privacy & Sustainability Compliance Platform
                </p>
            </div>
        </div>
    </div>
    ''' if 'sustainability' in scan_type.lower() and 'carbon_footprint' in scan_data else '')

    # Generate website report content
    website_content = ""
    if scan_type.lower() == 'website':
        # Helper function to generate findings table
        def generate_findings_table():
            if 'findings' in scan_data and scan_data['findings']:
                findings_rows = ""
                for i, finding in enumerate(scan_data.get('findings', [])[:20]):
                    severity = finding.get('severity', 'Low')
                    severity_color = '#ef4444' if severity.lower() == 'high' else '#f59e0b' if severity.lower() == 'medium' else '#10b981'
                    bg_color = '#fef2f2' if i % 2 == 0 else '#fef7f7'
                    
                    findings_rows += f'''
                    <tr style="background-color: {bg_color};">
                        <td style="border: 1px solid #fecaca; padding: 12px; color: #7f1d1d; font-weight: 500;">{finding.get('type', 'Unknown')}</td>
                        <td style="border: 1px solid #fecaca; padding: 12px; color: #7f1d1d;">
                            <span style="background: {severity_color}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;">
                                {severity}
                            </span>
                        </td>
                        <td style="border: 1px solid #fecaca; padding: 12px; color: #7f1d1d;">{(finding.get('description', '')[:80] + '...' if len(finding.get('description', '')) > 80 else finding.get('description', ''))}</td>
                        <td style="border: 1px solid #fecaca; padding: 12px; color: #7f1d1d; font-size: 12px;">{(finding.get('url', '')[:30] + '...' if len(finding.get('url', '')) > 30 else finding.get('url', ''))}</td>
                    </tr>'''
                
                return f'''
                <div style="background: white; border-radius: 15px; padding: 30px; margin: 20px 0; box-shadow: 0 6px 20px rgba(0,0,0,0.1); border: 2px solid #e2e8f0;">
                    <h2 style="color: #dc2626; margin-bottom: 20px;">🔍 Privacy Findings</h2>
                    <div style="overflow-x: auto;">
                        <table style="width: 100%; border-collapse: collapse; margin: 15px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                            <thead>
                                <tr style="background: linear-gradient(135deg, #dc2626, #b91c1c);">
                                    <th style="border: 1px solid #fecaca; padding: 15px; text-align: left; color: white; font-weight: bold;">Type</th>
                                    <th style="border: 1px solid #fecaca; padding: 15px; text-align: left; color: white; font-weight: bold;">Severity</th>
                                    <th style="border: 1px solid #fecaca; padding: 15px; text-align: left; color: white; font-weight: bold;">Description</th>
                                    <th style="border: 1px solid #fecaca; padding: 15px; text-align: left; color: white; font-weight: bold;">URL</th>
                                </tr>
                            </thead>
                            <tbody>
                                {findings_rows}
                            </tbody>
                        </table>
                    </div>
                    <p style="color: #6b7280; font-style: italic; margin-top: 15px;">Showing {min(20, len(scan_data.get('findings', [])))} of {len(scan_data.get('findings', []))} total findings</p>
                </div>'''
            return ""
        
        # Helper function to generate detailed cookie analysis
        def generate_cookie_analysis():
            if 'cookies' in scan_data and scan_data['cookies']:
                cookie_categories = scan_data.get('cookie_categories', {})
                cookies = scan_data.get('cookies', {})
                
                # Generate category breakdown
                category_rows = ""
                for category, count in cookie_categories.items():
                    category_rows += f'''
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px; padding: 8px 0; border-bottom: 1px solid #fde68a;">
                        <span style="color: #92400e; font-weight: 500;">{category.title()}</span>
                        <span style="color: #92400e; font-weight: bold;">{count}</span>
                    </div>'''
                
                # Generate detailed cookie table
                cookie_rows = ""
                for i, (name, cookie_data) in enumerate(list(cookies.items())[:15]):
                    bg_color = '#fef3c7' if i % 2 == 0 else '#fde68a'
                    purpose = cookie_data.get('purpose', 'Unknown')[:30] + ('...' if len(cookie_data.get('purpose', '')) > 30 else '')
                    
                    cookie_rows += f'''
                    <tr style="background-color: {bg_color};">
                        <td style="border: 1px solid #fde68a; padding: 12px; color: #92400e; font-weight: 500;">{name}</td>
                        <td style="border: 1px solid #fde68a; padding: 12px; color: #92400e;">{cookie_data.get('category', 'Unknown')}</td>
                        <td style="border: 1px solid #fde68a; padding: 12px; color: #92400e;">{purpose}</td>
                        <td style="border: 1px solid #fde68a; padding: 12px; color: #92400e;">{'Yes' if cookie_data.get('persistent', True) else 'No'}</td>
                        <td style="border: 1px solid #fde68a; padding: 12px; color: #92400e;">{cookie_data.get('expiry', 'Session')}</td>
                    </tr>'''
                
                session_count = sum(1 for cookie in cookies.values() if not cookie.get('persistent', True))
                persistent_count = sum(1 for cookie in cookies.values() if cookie.get('persistent', True))
                
                return f'''
                <div style="background: white; border-radius: 15px; padding: 30px; margin: 20px 0; box-shadow: 0 6px 20px rgba(0,0,0,0.1); border: 2px solid #e2e8f0;">
                    <h2 style="color: #f59e0b; margin-bottom: 20px;">🍪 In-Depth Cookie Analysis</h2>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 30px;">
                        <div>
                            <h3 style="color: #92400e; margin-bottom: 15px;">Cookie Categories</h3>
                            <div style="background: #fef3c7; padding: 20px; border-radius: 10px;">
                                {category_rows}
                            </div>
                        </div>
                        
                        <div>
                            <h3 style="color: #92400e; margin-bottom: 15px;">Cookie Summary</h3>
                            <div style="background: #fef3c7; padding: 20px; border-radius: 10px;">
                                <div style="margin-bottom: 10px;">
                                    <strong style="color: #92400e;">Total Cookies:</strong>
                                    <span style="color: #78350f;">{len(cookies)}</span>
                                </div>
                                <div style="margin-bottom: 10px;">
                                    <strong style="color: #92400e;">Session Cookies:</strong>
                                    <span style="color: #78350f;">{session_count}</span>
                                </div>
                                <div>
                                    <strong style="color: #92400e;">Persistent Cookies:</strong>
                                    <span style="color: #78350f;">{persistent_count}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <h3 style="color: #92400e; margin-bottom: 15px;">Detailed Cookie Inventory</h3>
                    <div style="overflow-x: auto;">
                        <table style="width: 100%; border-collapse: collapse; margin: 15px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                            <thead>
                                <tr style="background: linear-gradient(135deg, #f59e0b, #d97706);">
                                    <th style="border: 1px solid #fde68a; padding: 15px; text-align: left; color: white; font-weight: bold;">Name</th>
                                    <th style="border: 1px solid #fde68a; padding: 15px; text-align: left; color: white; font-weight: bold;">Category</th>
                                    <th style="border: 1px solid #fde68a; padding: 15px; text-align: left; color: white; font-weight: bold;">Purpose</th>
                                    <th style="border: 1px solid #fde68a; padding: 15px; text-align: left; color: white; font-weight: bold;">Persistent</th>
                                    <th style="border: 1px solid #fde68a; padding: 15px; text-align: left; color: white; font-weight: bold;">Expiry</th>
                                </tr>
                            </thead>
                            <tbody>
                                {cookie_rows}
                            </tbody>
                        </table>
                    </div>
                    <p style="color: #6b7280; font-style: italic; margin-top: 15px;">Showing {min(15, len(cookies))} of {len(cookies)} total cookies</p>
                </div>'''
            return ""
        
        # Helper function to generate tracker analysis
        def generate_tracker_analysis():
            if 'trackers' in scan_data and scan_data['trackers']:
                tracker_rows = ""
                for i, tracker in enumerate(scan_data.get('trackers', [])[:15]):
                    bg_color = '#f3e8ff' if i % 2 == 0 else '#faf5ff'
                    risk = tracker.get('privacy_risk', 'Low')
                    risk_color = '#ef4444' if risk.lower() == 'high' else '#f59e0b' if risk.lower() == 'medium' else '#10b981'
                    
                    tracker_rows += f'''
                    <tr style="background-color: {bg_color};">
                        <td style="border: 1px solid #ddd6fe; padding: 12px; color: #581c87; font-weight: 500;">{tracker.get('name', 'Unknown')}</td>
                        <td style="border: 1px solid #ddd6fe; padding: 12px; color: #581c87;">{tracker.get('type', 'Unknown')}</td>
                        <td style="border: 1px solid #ddd6fe; padding: 12px; color: #581c87;">{(tracker.get('purpose', 'Unknown')[:40] + '...' if len(tracker.get('purpose', '')) > 40 else tracker.get('purpose', 'Unknown'))}</td>
                        <td style="border: 1px solid #ddd6fe; padding: 12px; color: #581c87;">
                            <span style="background: {risk_color}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;">
                                {risk}
                            </span>
                        </td>
                    </tr>'''
                
                return f'''
                <div style="background: white; border-radius: 15px; padding: 30px; margin: 20px 0; box-shadow: 0 6px 20px rgba(0,0,0,0.1); border: 2px solid #e2e8f0;">
                    <h2 style="color: #7c3aed; margin-bottom: 20px;">📊 Tracking Analysis</h2>
                    <div style="overflow-x: auto;">
                        <table style="width: 100%; border-collapse: collapse; margin: 15px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                            <thead>
                                <tr style="background: linear-gradient(135deg, #7c3aed, #6d28d9);">
                                    <th style="border: 1px solid #ddd6fe; padding: 15px; text-align: left; color: white; font-weight: bold;">Name</th>
                                    <th style="border: 1px solid #ddd6fe; padding: 15px; text-align: left; color: white; font-weight: bold;">Type</th>
                                    <th style="border: 1px solid #ddd6fe; padding: 15px; text-align: left; color: white; font-weight: bold;">Purpose</th>
                                    <th style="border: 1px solid #ddd6fe; padding: 15px; text-align: left; color: white; font-weight: bold;">Privacy Risk</th>
                                </tr>
                            </thead>
                            <tbody>
                                {tracker_rows}
                            </tbody>
                        </table>
                    </div>
                    <p style="color: #6b7280; font-style: italic; margin-top: 15px;">Showing {min(15, len(scan_data.get('trackers', [])))} of {len(scan_data.get('trackers', []))} total trackers</p>
                </div>'''
            return ""
        
        website_content = f'''
        <div style="margin: 30px 0;">
            <h1 style="color: #1e40af; text-align: center; margin-bottom: 30px; font-size: 28px;">
                🌐 Website Privacy Compliance Report
            </h1>
            
            <div style="background: white; border-radius: 15px; padding: 30px; margin: 20px 0; box-shadow: 0 6px 20px rgba(0,0,0,0.1); border: 2px solid #e2e8f0;">
                <h2 style="color: #1e40af; margin-bottom: 20px;">📊 Scan Overview</h2>
                
                <div style="background: linear-gradient(135deg, #f0f9ff, #e0f2fe); padding: 20px; border-radius: 10px; margin-bottom: 25px;">
                    <h3 style="color: #0c4a6e; margin: 0 0 15px 0;">Scanned Website:</h3>
                    <p style="color: #0369a1; font-size: 18px; font-weight: bold; margin: 0;">
                        {scan_data.get('url', scan_data.get('base_domain', 'Website Analysis'))}
                    </p>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 25px 0;">
                    <div style="background: linear-gradient(135deg, #3b82f6, #1d4ed8); color: white; padding: 25px; border-radius: 10px; text-align: center;">
                        <h3 style="margin: 0 0 10px 0; font-size: 16px;">Pages Scanned</h3>
                        <div style="font-size: 32px; font-weight: bold;">
                            {scan_data.get('stats', {}).get('pages_scanned', 0)}
                        </div>
                    </div>
                    
                    <div style="background: linear-gradient(135deg, #dc2626, #b91c1c); color: white; padding: 25px; border-radius: 10px; text-align: center;">
                        <h3 style="margin: 0 0 10px 0; font-size: 16px;">Total Findings</h3>
                        <div style="font-size: 32px; font-weight: bold;">
                            {scan_data.get('stats', {}).get('total_findings', 0)}
                        </div>
                    </div>
                    
                    <div style="background: linear-gradient(135deg, #f59e0b, #d97706); color: white; padding: 25px; border-radius: 10px; text-align: center;">
                        <h3 style="margin: 0 0 10px 0; font-size: 16px;">Cookies Found</h3>
                        <div style="font-size: 32px; font-weight: bold;">
                            {scan_data.get('stats', {}).get('total_cookies', 0)}
                        </div>
                    </div>
                    
                    <div style="background: linear-gradient(135deg, #7c3aed, #6d28d9); color: white; padding: 25px; border-radius: 10px; text-align: center;">
                        <h3 style="margin: 0 0 10px 0; font-size: 16px;">Trackers Detected</h3>
                        <div style="font-size: 32px; font-weight: bold;">
                            {scan_data.get('stats', {}).get('total_trackers', 0)}
                        </div>
                    </div>
                </div>
                
                <div style="background: #f8fafc; padding: 20px; border-radius: 10px; margin: 25px 0;">
                    <h3 style="color: #374151; margin-bottom: 15px;">Additional Scan Details</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                        <div>
                            <strong style="color: #1f2937;">Scan Duration:</strong>
                            <span style="color: #4b5563;">{scan_data.get('duration_seconds', 0):.1f} seconds</span>
                        </div>
                        <div>
                            <strong style="color: #1f2937;">Scan Timestamp:</strong>
                            <span style="color: #4b5563;">{scan_data.get('scan_time', timestamp)}</span>
                        </div>
                    </div>
                </div>
            </div>
            
            {generate_findings_table()}
            {generate_cookie_analysis()}
            {generate_tracker_analysis()}
            
            <div style="background: white; border-radius: 15px; margin: 30px 0; padding: 30px; text-align: center; box-shadow: 0 6px 20px rgba(0,0,0,0.1); border: 2px solid #e2e8f0;">
                <p style="color: #374151; font-size: 12px; line-height: 1.6; max-width: 600px; margin: 0 auto;">
                    This website privacy assessment was conducted on {timestamp} using DataGuardian Pro's comprehensive 
                    website scanner. The assessment analyzed privacy compliance, cookie usage, tracker detection, and GDPR compliance requirements.
                </p>
                <div style="margin-top: 30px; padding-top: 20px; border-top: 2px solid #e5e7eb;">
                    <p style="color: #6b7280; font-size: 11px; margin: 5px 0;">
                        <strong>DataGuardian Pro Enterprise Certification Authority</strong>
                    </p>
                    <p style="color: #6b7280; font-size: 10px; margin: 0;">
                        Enterprise Privacy & Compliance Platform
                    </p>
                </div>
            </div>
        </div>'''
    
    html_content += website_content
    
    html_content += f"""
    <div class="section">
        <h2>{recommendations_title}</h2>
        {recommendations_html if recommendations_html else f"<p>{no_recommendations}</p>"}
        
        <h3>{general_recommendations_title}</h3>
        <ul>
            <li>{recommendation_1}</li>
            <li>{recommendation_2}</li>
            <li>{recommendation_3}</li>
            <li>{recommendation_4}</li>
        </ul>
    </div>
    
    <div class="section">
        <h2>{metadata_title}</h2>
        <table>
            <tr>
                <th>{scan_id_label}</th>
                <td>{scan_id}</td>
            </tr>
            <tr>
                <th>{scan_type_label}</th>
                <td>{scan_type}</td>
            </tr>
            <tr>
                <th>{region_label}</th>
                <td>{region}</td>
            </tr>
            <tr>
                <th>{timestamp_label}</th>
                <td>{timestamp}</td>
            </tr>
            <tr>
                <th>{url_label}</th>
                <td>{url}</td>
            </tr>
        </table>
        
        <p style="font-size: 12px; color: #777; margin-top: 30px;">
            {disclaimer_text}
        </p>
    </div>
    
    <script>
        // Initialize tablesorter
        $(document).ready(function() {{ 
            $("#findingsTable").tablesorter({{
                theme: 'blue',
                widgets: ['zebra', 'filter'],
                widgetOptions: {{
                    zebra: ['even', 'odd'],
                }}
            }}); 
        }});
        
        // Initialize charts
        const piiTypesData = {pii_types_data};
        const riskLevelsData = {risk_levels_data};
        
        // Define chart labels based on language
        const chartLabels = {{
            count: '{_('chart.count', 'Count') if current_lang == 'en' else 'Aantal'}',
            riskLevels: '{_('chart.risk_levels', 'Risk Levels') if current_lang == 'en' else 'Risico Niveaus'}'
        }};
        
        // PII Types Chart
        const piiTypesCtx = document.getElementById('piiTypesChart').getContext('2d');
        new Chart(piiTypesCtx, {{
            type: 'bar',
            data: {{
                labels: piiTypesData.labels,
                datasets: [{{
                    label: chartLabels.count,
                    data: piiTypesData.values,
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
        
        // Risk Levels Chart
        const riskLevelsCtx = document.getElementById('riskLevelsChart').getContext('2d');
        new Chart(riskLevelsCtx, {{
            type: 'pie',
            data: {{
                labels: riskLevelsData.labels,
                datasets: [{{
                    label: chartLabels.riskLevels,
                    data: riskLevelsData.values,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.6)',
                        'rgba(255, 205, 86, 0.6)',
                        'rgba(75, 192, 192, 0.6)'
                    ],
                    borderColor: [
                        'rgb(255, 99, 132)',
                        'rgb(255, 205, 86)',
                        'rgb(75, 192, 192)'
                    ],
                    borderWidth: 1
                }}]
            }}
        }});
    </script>
</body>
</html>"""
    
    return html_content