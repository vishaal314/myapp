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
    Generate a HTML report for a scan result.
    
    Args:
        scan_data: The scan result data
        
    Returns:
        HTML report as a string
    """
    # Get current language from session state
    current_lang = st.session_state.get('language', 'en')
    
    # Extract basic scan info
    scan_id = scan_data.get('scan_id', 'Unknown')
    scan_type = scan_data.get('scan_type', 'Unknown')
    region = scan_data.get('region', 'Unknown')
    total_pii = scan_data.get('total_pii_found', 0)
    high_risk = scan_data.get('high_risk_count', 0)
    medium_risk = scan_data.get('medium_risk_count', 0)
    low_risk = scan_data.get('low_risk_count', 0)
    timestamp = scan_data.get('timestamp', 'Unknown')
    url = scan_data.get('url', scan_data.get('domain', 'Not available'))
    
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
    for finding in findings:
        risk_level = finding.get('risk_level', 'Unknown')
        
        # Determine risk level color and translate risk level if needed
        if risk_level == 'High' or risk_level == 'Hoog':
            risk_color = '#ffcdd2'
            risk_level_display = 'Hoog' if current_lang == 'nl' else 'High'
        elif risk_level == 'Medium' or risk_level == 'Gemiddeld':
            risk_color = '#fff9c4'
            risk_level_display = 'Gemiddeld' if current_lang == 'nl' else 'Medium'
        elif risk_level == 'Low' or risk_level == 'Laag':
            risk_color = '#e8f5e9'
            risk_level_display = 'Laag' if current_lang == 'nl' else 'Low'
        else:
            risk_color = '#e0e0e0'
            risk_level_display = 'Onbekend' if current_lang == 'nl' else 'Unknown'
        
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
                    <th>{value_header}</th>
                    <th>{location_header}</th>
                    <th>{risk_level_header}</th>
                    <th>{reason_header}</th>
                </tr>
            </thead>
            <tbody>
                {findings_table_rows}
            </tbody>
        </table>
    </div>
    
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