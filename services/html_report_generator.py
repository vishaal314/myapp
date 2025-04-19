import io
import base64
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import json

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
            timestamp = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        except:
            pass
    
    # Prepare PII types data
    pii_types = scan_data.get('pii_types', {})
    pii_types_labels = list(pii_types.keys())
    pii_types_values = list(pii_types.values())
    
    # Prepare risk levels data
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
        risk_color = '#ffcdd2' if risk_level == 'High' else '#fff9c4' if risk_level == 'Medium' else '#e8f5e9'
        
        findings_table_rows += f"""
        <tr style="background-color: {risk_color}">
            <td>{finding.get('type', 'Unknown')}</td>
            <td>{finding.get('value', 'Unknown')}</td>
            <td>{finding.get('location', 'Unknown')}</td>
            <td>{risk_level}</td>
            <td>{finding.get('reason', 'Unknown')}</td>
        </tr>
        """
    
    # Recommendations
    recommendations = scan_data.get('recommendations', [])
    recommendations_html = ""
    for rec in recommendations:
        priority = rec.get('priority', 'Medium')
        priority_color = '#ffcdd2' if priority == 'High' else '#fff9c4' if priority == 'Medium' else '#e8f5e9'
        
        steps_html = ""
        for step in rec.get('steps', []):
            steps_html += f"<li>{step}</li>"
        
        recommendations_html += f"""
        <div class="recommendation" style="margin-bottom: 20px; padding: 15px; border-radius: 4px; background-color: {priority_color};">
            <h4>{rec.get('title', 'Recommendation')}</h4>
            <p><strong>Priority:</strong> {priority}</p>
            <p>{rec.get('description', '')}</p>
            <h5>Steps:</h5>
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
    
    # Build the HTML content
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GDPR Compliance Report - {scan_id}</title>
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
        <h1>GDPR Compliance Scan Report</h1>
        <p><strong>Generated on:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Scan ID:</strong> {scan_id}</p>
    </div>
    
    <div class="section">
        <h2>Summary</h2>
        <table>
            <tr>
                <th>Scan Type</th>
                <td>{scan_type}</td>
            </tr>
            <tr>
                <th>Region</th>
                <td>{region}</td>
            </tr>
            <tr>
                <th>Date & Time</th>
                <td>{timestamp}</td>
            </tr>
            <tr>
                <th>URL/Domain</th>
                <td>{url}</td>
            </tr>
            <tr>
                <th>Total PII Items Found</th>
                <td>{total_pii}</td>
            </tr>
            <tr>
                <th>High Risk Items</th>
                <td>{high_risk}</td>
            </tr>
        </table>
    </div>
    
    <div class="section">
        <h2>Risk Assessment</h2>
        <div class="metrics">
            <div class="metric-card">
                <h3>Total PII</h3>
                <div class="metric-value">{total_pii}</div>
                <p>Total PII items detected</p>
            </div>
            <div class="metric-card">
                <h3>High Risk</h3>
                <div class="metric-value risk-high">{high_risk}</div>
                <p>High risk items</p>
            </div>
            <div class="metric-card">
                <h3>Medium Risk</h3>
                <div class="metric-value risk-medium">{medium_risk}</div>
                <p>Medium risk items</p>
            </div>
            <div class="metric-card">
                <h3>Low Risk</h3>
                <div class="metric-value risk-low">{low_risk}</div>
                <p>Low risk items</p>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>Data Analysis</h2>
        <div class="chart-container">
            <h3>PII Types Distribution</h3>
            <canvas id="piiTypesChart"></canvas>
        </div>
        
        <div class="chart-container">
            <h3>Risk Level Distribution</h3>
            <canvas id="riskLevelsChart"></canvas>
        </div>
    </div>
    
    <div class="section">
        <h2>Findings</h2>
        <table id="findingsTable" class="tablesorter">
            <thead>
                <tr>
                    <th>PII Type</th>
                    <th>Value</th>
                    <th>Location</th>
                    <th>Risk Level</th>
                    <th>Reason</th>
                </tr>
            </thead>
            <tbody>
                {findings_table_rows}
            </tbody>
        </table>
    </div>
    
    <div class="section">
        <h2>Recommendations</h2>
        {recommendations_html if recommendations_html else "<p>No specific recommendations available for this scan.</p>"}
        
        <h3>General GDPR Recommendations</h3>
        <ul>
            <li>Ensure you have proper legal basis for processing all identified PII.</li>
            <li>Document all processing activities as required by GDPR Article 30.</li>
            <li>Review data retention policies to ensure PII is not kept longer than necessary.</li>
            <li>Implement appropriate technical and organizational measures to secure PII.</li>
        </ul>
    </div>
    
    <div class="section">
        <h2>Metadata</h2>
        <table>
            <tr>
                <th>Scan ID</th>
                <td>{scan_id}</td>
            </tr>
            <tr>
                <th>Scan Type</th>
                <td>{scan_type}</td>
            </tr>
            <tr>
                <th>Region</th>
                <td>{region}</td>
            </tr>
            <tr>
                <th>Timestamp</th>
                <td>{timestamp}</td>
            </tr>
            <tr>
                <th>URL/Domain</th>
                <td>{url}</td>
            </tr>
        </table>
        
        <p style="font-size: 12px; color: #777; margin-top: 30px;">
            Disclaimer: This report is provided for informational purposes only and should not 
            be considered legal advice. The findings in this report are based on automated 
            scanning and may not identify all GDPR-relevant personal data. We recommend 
            consulting with a qualified legal professional for specific GDPR compliance guidance.
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
        
        // PII Types Chart
        const piiTypesCtx = document.getElementById('piiTypesChart').getContext('2d');
        new Chart(piiTypesCtx, {{
            type: 'bar',
            data: {{
                labels: piiTypesData.labels,
                datasets: [{{
                    label: 'Count',
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
                    label: 'Risk Levels',
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