"""
Report Generation Service

Generates PDF and HTML reports for scan results including fraud detection findings.
"""

import streamlit as st
from typing import Dict, Any, Optional
from datetime import datetime
import json


def generate_pdf_report(scan_results: Dict[str, Any], filename: str = "scan_report.pdf") -> Optional[bytes]:
    """
    Generate PDF report from scan results.
    
    Args:
        scan_results: Complete scan results with findings
        filename: Output filename
    
    Returns:
        PDF bytes or None if generation fails
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from io import BytesIO
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1976D2'),
            spaceAfter=30,
        )
        story.append(Paragraph("📄 Scan Report", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Metadata
        metadata_data = [
            ["Report Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["Scan Type", scan_results.get('scan_type', 'Unknown')],
            ["Files/Items Scanned", str(scan_results.get('files_scanned', scan_results.get('endpoints_scanned', 0)))],
            ["Total Findings", str(len(scan_results.get('findings', [])))],
        ]
        
        metadata_table = Table(metadata_data)
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(metadata_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Findings summary
        story.append(Paragraph("Findings Summary", styles['Heading2']))
        findings = scan_results.get('findings', [])
        
        if findings:
            findings_data = [["Type", "Severity", "Description"]]
            for finding in findings[:10]:  # Limit to first 10 for PDF
                findings_data.append([
                    str(finding.get('type', 'Unknown'))[:30],
                    str(finding.get('severity', finding.get('risk_level', 'Medium')))[:15],
                    str(finding.get('description', 'No description'))[:40]
                ])
            
            findings_table = Table(findings_data)
            findings_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            story.append(findings_table)
        else:
            story.append(Paragraph("No findings detected.", styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
        
    except Exception as e:
        st.error(f"PDF generation failed: {str(e)}")
        return None


def generate_html_report(scan_results: Dict[str, Any], filename: str = "scan_report.html") -> Optional[str]:
    """
    Generate HTML report from scan results.
    
    Args:
        scan_results: Complete scan results with findings
        filename: Output filename
    
    Returns:
        HTML string or None if generation fails
    """
    try:
        findings = scan_results.get('findings', [])
        scan_type = scan_results.get('scan_type', 'Unknown')
        files_scanned = scan_results.get('files_scanned', scan_results.get('endpoints_scanned', 0))
        
        findings_html = ""
        for finding in findings:
            severity = finding.get('severity', finding.get('risk_level', 'Medium'))
            severity_color = {
                'Critical': '#F44336',
                'High': '#FF6F00',
                'Medium': '#FF9800',
                'Low': '#4CAF50'
            }.get(severity, '#9E9E9E')
            
            findings_html += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #ddd;">
                    {finding.get('type', 'Unknown')}
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #ddd;">
                    <span style="background: {severity_color}; color: white; padding: 4px 8px; 
                                border-radius: 4px; font-size: 12px; font-weight: bold;">
                        {severity}
                    </span>
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #ddd;">
                    {finding.get('description', 'No description')}
                </td>
            </tr>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Scan Report</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 40px;
                    background: #f5f5f5;
                }}
                .container {{
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #1976D2;
                    border-bottom: 2px solid #1976D2;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #333;
                    margin-top: 30px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 15px;
                }}
                th {{
                    background: #1976D2;
                    color: white;
                    padding: 12px;
                    text-align: left;
                    font-weight: bold;
                }}
                td {{
                    padding: 12px;
                    border-bottom: 1px solid #ddd;
                }}
                .metadata {{
                    background: #f9f9f9;
                    padding: 15px;
                    border-left: 4px solid #1976D2;
                    border-radius: 4px;
                    margin-bottom: 20px;
                }}
                .metadata p {{
                    margin: 8px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📄 Scan Report</h1>
                
                <div class="metadata">
                    <p><strong>Report Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>Scan Type:</strong> {scan_type}</p>
                    <p><strong>Files/Items Scanned:</strong> {files_scanned}</p>
                    <p><strong>Total Findings:</strong> {len(findings)}</p>
                </div>
                
                <h2>Findings</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Type</th>
                            <th>Severity</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        {findings_html if findings_html else '<tr><td colspan="3">No findings detected.</td></tr>'}
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """
        
        return html
        
    except Exception as e:
        st.error(f"HTML generation failed: {str(e)}")
        return None
