import os
import io
import base64
import logging
from typing import Dict, Any
import streamlit as st
from services.gdpr_report_generator import generate_gdpr_report
from utils.i18n import get_text
from config.report_config import PDF_MAX_FINDINGS, FILENAME_DATE_FORMAT
from config.translation_mappings import REPORT_TRANSLATION_MAPPINGS

logger = logging.getLogger(__name__)


def generate_html_report(scan_result: Dict[str, Any]) -> str:
    """Generate HTML report using unified translation system"""
    try:
        from services.unified_html_report_generator import generate_unified_html_report
        return generate_unified_html_report(scan_result)
    except ImportError:
        logger.warning("Unified HTML report generator not available, using fallback")
        return generate_fallback_html_report(scan_result)


def generate_fallback_html_report(scan_result: Dict[str, Any]) -> str:
    """Generate a simple HTML report as fallback when unified generator fails."""
    
    # Extract basic information
    scan_id = scan_result.get('scan_id', 'unknown')
    scan_type = scan_result.get('scan_type', 'Unknown Scanner')
    timestamp = scan_result.get('timestamp', 'Unknown')
    region = scan_result.get('region', 'Netherlands')
    
    # Extract findings
    findings = scan_result.get('findings', [])
    total_findings = len(findings)
    
    # Count findings by severity
    critical_count = len([f for f in findings if f.get('severity') == 'Critical'])
    high_count = len([f for f in findings if f.get('severity') == 'High'])
    medium_count = len([f for f in findings if f.get('severity') == 'Medium'])
    low_count = len([f for f in findings if f.get('severity') == 'Low'])
    
    # Calculate compliance score
    compliance_score = scan_result.get('compliance_score', 0)
    if compliance_score == 0 and total_findings > 0:
        # Calculate based on findings if not provided
        penalty = (critical_count * 25) + (high_count * 15) + (medium_count * 7) + (low_count * 3)
        compliance_score = max(0, 100 - penalty)
    
    # Generate findings HTML
    findings_html = ""
    if findings:
        findings_html = "<table><tr><th>Type</th><th>Severity</th><th>Location</th><th>Description</th></tr>"
        for finding in findings[:50]:  # Limit to first 50 findings
            finding_type = finding.get('type', 'Unknown')
            severity = finding.get('severity', 'Unknown')
            location = finding.get('location', finding.get('file', 'Unknown'))
            description = finding.get('description', 'No description available')
            
            # Color code severity
            severity_color = {
                'Critical': '#dc2626',
                'High': '#d97706', 
                'Medium': '#7b1fa2',
                'Low': '#059669'
            }.get(severity, '#6b7280')
            
            findings_html += f"""
            <tr>
                <td>{finding_type}</td>
                <td style="color: {severity_color}; font-weight: bold;">{severity}</td>
                <td>{location}</td>
                <td>{description}</td>
            </tr>
            """
        findings_html += "</table>"
    else:
        findings_html = "<p>No findings detected.</p>"
    
    # Build complete HTML report
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DataGuardian Pro - {scan_type} Report</title>
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                margin: 40px; 
                line-height: 1.6;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 30px;
            }}
            .summary {{
                background-color: #f8f9fa;
                padding: 25px;
                border-radius: 8px;
                margin: 20px 0;
                border-left: 5px solid #2563eb;
            }}
            .metrics {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }}
            .metric {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .metric-value {{
                font-size: 2em;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .critical {{ color: #dc2626; }}
            .high {{ color: #d97706; }}
            .medium {{ color: #7b1fa2; }}
            .low {{ color: #059669; }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                background: white;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            th, td {{
                border: 1px solid #e5e7eb;
                padding: 12px;
                text-align: left;
            }}
            th {{
                background-color: #f3f4f6;
                font-weight: bold;
            }}
            tr:nth-child(even) {{
                background-color: #f9fafb;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>DataGuardian Pro - {scan_type}</h1>
            <p><strong>Scan ID:</strong> {scan_id}</p>
            <p><strong>Region:</strong> {region}</p>
            <p><strong>Generated:</strong> {timestamp}</p>
        </div>
        
        <div class="summary">
            <h2>Executive Summary</h2>
            <p>This report presents the results of a comprehensive privacy compliance scan. 
            The analysis identified <strong>{total_findings}</strong> findings across various compliance categories.</p>
            <p><strong>Overall Compliance Score: {compliance_score}%</strong></p>
        </div>
        
        <div class="metrics">
            <div class="metric">
                <div class="metric-value critical">{critical_count}</div>
                <div>Critical Findings</div>
            </div>
            <div class="metric">
                <div class="metric-value high">{high_count}</div>
                <div>High Risk Findings</div>
            </div>
            <div class="metric">
                <div class="metric-value medium">{medium_count}</div>
                <div>Medium Risk Findings</div>
            </div>
            <div class="metric">
                <div class="metric-value low">{low_count}</div>
                <div>Low Risk Findings</div>
            </div>
        </div>
        
        <h2>Detailed Findings</h2>
        {findings_html}
        
        <div style="margin-top: 50px; padding: 20px; background-color: #f1f5f9; border-radius: 8px;">
            <p><em>This report was generated by DataGuardian Pro - Enterprise Privacy Compliance Platform</em></p>
            <p><em>For more information, visit: dataguardian.pro</em></p>
        </div>
    </body>
    </html>
    """
    
    return html


def generate_pdf_report(scan_result: Dict[str, Any]) -> bytes:
    """Generate PDF report from scan results."""
    try:
        # Try to use the existing PDF generator
        from services.gdpr_report_generator import generate_gdpr_report
        success, report_path, report_content = generate_gdpr_report(scan_result)
        if success and report_content:
            return report_content
        else:
            return generate_fallback_pdf_report(scan_result)
    except ImportError:
        logger.warning("Enhanced PDF generator not available, using fallback")
        return generate_fallback_pdf_report(scan_result)


def generate_fallback_pdf_report(scan_result: Dict[str, Any]) -> bytes:
    """Generate a simple PDF report as fallback."""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        
        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2563eb')
        )
        
        scan_type = scan_result.get('scan_type', 'Unknown Scanner')
        story.append(Paragraph(f"DataGuardian Pro - {scan_type}", title_style))
        story.append(Spacer(1, 20))
        
        # Basic information
        info_data = [
            ['Scan ID:', scan_result.get('scan_id', 'unknown')],
            ['Region:', scan_result.get('region', 'Netherlands')],
            ['Generated:', scan_result.get('timestamp', 'Unknown')],
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb'))
        ]))
        story.append(info_table)
        story.append(Spacer(1, 30))
        
        # Summary section
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        findings = scan_result.get('findings', [])
        total_findings = len(findings)
        compliance_score = scan_result.get('compliance_score', 0)
        
        summary_text = f"""
        This report presents the results of a comprehensive privacy compliance scan.
        The analysis identified <b>{total_findings}</b> findings across various compliance categories.
        <br/><br/>
        <b>Overall Compliance Score: {compliance_score}%</b>
        """
        story.append(Paragraph(summary_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Findings summary
        if findings:
            critical_count = len([f for f in findings if f.get('severity') == 'Critical'])
            high_count = len([f for f in findings if f.get('severity') == 'High'])
            medium_count = len([f for f in findings if f.get('severity') == 'Medium'])
            low_count = len([f for f in findings if f.get('severity') == 'Low'])
            
            summary_data = [
                ['Severity', 'Count'],
                ['Critical', str(critical_count)],
                ['High', str(high_count)],
                ['Medium', str(medium_count)],
                ['Low', str(low_count)],
            ]
            
            summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb'))
            ]))
            story.append(summary_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
        
    except ImportError:
        logger.error("ReportLab not available for PDF generation")
        # Return a simple text-based "PDF" as last resort
        content = f"""
DataGuardian Pro - {scan_result.get('scan_type', 'Unknown Scanner')}
Scan ID: {scan_result.get('scan_id', 'unknown')}
Generated: {scan_result.get('timestamp', 'Unknown')}

Total Findings: {len(scan_result.get('findings', []))}
Compliance Score: {scan_result.get('compliance_score', 0)}%

This is a fallback text report. Please ensure ReportLab is installed for proper PDF generation.
"""
        return content.encode('utf-8')