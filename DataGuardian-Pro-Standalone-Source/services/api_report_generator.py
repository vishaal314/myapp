"""
API Report Generator

This module generates comprehensive HTML and PDF reports for API security
and privacy compliance scan results with professional formatting and
detailed vulnerability analysis.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

def generate_api_html_report(scan_data: Dict[str, Any]) -> str:
    """
    Generate a comprehensive HTML report for API scan results.
    
    Args:
        scan_data: Dictionary containing API scan results
        
    Returns:
        HTML report as string
    """
    
    # Extract key data
    base_url = scan_data.get('base_url', 'Unknown')
    scan_time = scan_data.get('scan_time', datetime.now().isoformat())
    endpoints_scanned = scan_data.get('endpoints_scanned', 0)
    findings = scan_data.get('findings', [])
    pii_exposures = scan_data.get('pii_exposures', [])
    vulnerabilities = scan_data.get('vulnerabilities', [])
    auth_issues = scan_data.get('auth_issues', [])
    stats = scan_data.get('stats', {})
    
    # Format timestamp
    try:
        timestamp = datetime.fromisoformat(scan_time.replace('Z', '+00:00')).strftime('%B %d, %Y at %I:%M %p UTC')
    except:
        timestamp = scan_time
    
    # Generate security overview section
    total_issues = stats.get('total_findings', 0)
    critical_count = stats.get('critical_findings', 0)
    high_count = stats.get('high_findings', 0)
    medium_count = stats.get('medium_findings', 0)
    low_count = stats.get('low_findings', 0)
    
    # Calculate risk level
    if critical_count > 0:
        overall_risk = "Critical"
        risk_color = "#dc2626"
    elif high_count > 0:
        overall_risk = "High"
        risk_color = "#ea580c"
    elif medium_count > 0:
        overall_risk = "Medium"
        risk_color = "#d97706"
    else:
        overall_risk = "Low"
        risk_color = "#16a34a"
    
    # Generate findings section
    findings_html = ""
    if findings:
        findings_rows = ""
        for i, finding in enumerate(findings[:20]):
            bg_color = '#fef2f2' if i % 2 == 0 else '#ffffff'
            severity = finding.get('severity', 'Unknown')
            severity_color = {
                'Critical': '#dc2626',
                'High': '#ea580c', 
                'Medium': '#d97706',
                'Low': '#16a34a'
            }.get(severity, '#6b7280')
            
            findings_rows += f"""
            <tr style="background-color: {bg_color};">
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">
                    <span style="background: {severity_color}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: 500;">
                        {severity}
                    </span>
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; color: #374151; font-weight: 500;">
                    {finding.get('type', 'Unknown').replace('_', ' ').title()}
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; color: #4b5563;">
                    {finding.get('description', 'No description available')[:100]}{'...' if len(finding.get('description', '')) > 100 else ''}
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; color: #6b7280; font-size: 12px;">
                    {finding.get('method', 'N/A')}
                </td>
            </tr>"""
        
        findings_html = f"""
        <div style="background: white; border-radius: 15px; padding: 30px; margin: 20px; box-shadow: 0 6px 20px rgba(0,0,0,0.1);">
            <h2 style="color: #dc2626; margin-bottom: 20px; display: flex; align-items: center;">
                🔍 Security Findings
            </h2>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: linear-gradient(135deg, #dc2626, #b91c1c); color: white;">
                        <th style="padding: 15px; text-align: left; font-weight: 600;">Severity</th>
                        <th style="padding: 15px; text-align: left; font-weight: 600;">Type</th>
                        <th style="padding: 15px; text-align: left; font-weight: 600;">Description</th>
                        <th style="padding: 15px; text-align: left; font-weight: 600;">Method</th>
                    </tr>
                </thead>
                <tbody>
                    {findings_rows}
                </tbody>
            </table>
            <p style="color: #6b7280; font-style: italic; margin-top: 15px;">Showing {min(20, len(findings))} of {len(findings)} total findings</p>
        </div>"""
    
    # Generate PII exposure analysis
    pii_html = ""
    if pii_exposures:
        pii_rows = ""
        for i, pii in enumerate(pii_exposures[:15]):
            bg_color = '#fef3c7' if i % 2 == 0 else '#ffffff'
            pii_type = pii.get('type', 'Unknown').replace('_', ' ').title()
            severity = pii.get('severity', 'Medium')
            severity_color = {
                'Critical': '#dc2626',
                'High': '#ea580c',
                'Medium': '#d97706',
                'Low': '#16a34a'
            }.get(severity, '#6b7280')
            
            pii_rows += f"""
            <tr style="background-color: {bg_color};">
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; font-weight: 500; color: #92400e;">
                    {pii_type}
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">
                    <span style="background: {severity_color}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px;">
                        {severity}
                    </span>
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; color: #92400e; font-weight: 500;">
                    {pii.get('count', 0)}
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; color: #6b7280;">
                    {pii.get('gdpr_category', 'Unknown')}
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; color: #6b7280; font-size: 12px;">
                    {pii.get('method', 'N/A')}
                </td>
            </tr>"""
        
        pii_count = len(pii_exposures)
        critical_pii = len([p for p in pii_exposures if p.get('severity') == 'Critical'])
        
        pii_html = f"""
        <div style="background: white; border-radius: 15px; padding: 30px; margin: 20px; box-shadow: 0 6px 20px rgba(0,0,0,0.1);">
            <h2 style="color: #f59e0b; margin-bottom: 20px;">🛡️ PII Exposure Analysis</h2>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 30px;">
                <div style="background: #fef3c7; padding: 20px; border-radius: 10px; text-align: center;">
                    <h3 style="color: #f59e0b; margin: 0; font-size: 24px;">{pii_count}</h3>
                    <p style="color: #92400e; margin: 5px 0 0 0; font-weight: 500;">Total PII Exposures</p>
                </div>
                <div style="background: #fef2f2; padding: 20px; border-radius: 10px; text-align: center;">
                    <h3 style="color: #dc2626; margin: 0; font-size: 24px;">{critical_pii}</h3>
                    <p style="color: #991b1b; margin: 5px 0 0 0; font-weight: 500;">Critical Exposures</p>
                </div>
                <div style="background: #ecfdf5; padding: 20px; border-radius: 10px; text-align: center;">
                    <h3 style="color: #16a34a; margin: 0; font-size: 24px;">{endpoints_scanned}</h3>
                    <p style="color: #15803d; margin: 5px 0 0 0; font-weight: 500;">Endpoints Scanned</p>
                </div>
            </div>
            
            <div style="background: #fef9c3; padding: 20px; border-radius: 10px;">
                <h3 style="color: #92400e; margin-bottom: 15px;">Detailed PII Inventory</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background: linear-gradient(135deg, #f59e0b, #d97706); color: white;">
                            <th style="padding: 12px; text-align: left;">PII Type</th>
                            <th style="padding: 12px; text-align: left;">Risk Level</th>
                            <th style="padding: 12px; text-align: left;">Count</th>
                            <th style="padding: 12px; text-align: left;">GDPR Category</th>
                            <th style="padding: 12px; text-align: left;">Method</th>
                        </tr>
                    </thead>
                    <tbody>
                        {pii_rows}
                    </tbody>
                </table>
            </div>
            <p style="color: #6b7280; font-style: italic; margin-top: 15px;">Showing {min(15, len(pii_exposures))} of {len(pii_exposures)} total PII exposures</p>
        </div>"""
    
    # Generate vulnerability analysis
    vuln_html = ""
    if vulnerabilities:
        vuln_rows = ""
        for i, vuln in enumerate(vulnerabilities[:15]):
            bg_color = '#f3e8ff' if i % 2 == 0 else '#ffffff'
            severity = vuln.get('severity', 'Medium')
            severity_color = {
                'Critical': '#dc2626',
                'High': '#ea580c',
                'Medium': '#d97706',
                'Low': '#16a34a'
            }.get(severity, '#6b7280')
            
            vuln_rows += f"""
            <tr style="background-color: {bg_color};">
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; font-weight: 500; color: #581c87;">
                    {vuln.get('type', 'Unknown').replace('_', ' ').title()}
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">
                    <span style="background: {severity_color}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px;">
                        {severity}
                    </span>
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; color: #4b5563;">
                    {vuln.get('description', 'No description')[:60]}{'...' if len(vuln.get('description', '')) > 60 else ''}
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; color: #6b7280; font-size: 12px;">
                    {vuln.get('method', 'N/A')}
                </td>
            </tr>"""
        
        vuln_html = f"""
        <div style="background: white; border-radius: 15px; padding: 30px; margin: 20px; box-shadow: 0 6px 20px rgba(0,0,0,0.1);">
            <h2 style="color: #7c3aed; margin-bottom: 20px;">⚠️ Vulnerability Analysis</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: linear-gradient(135deg, #7c3aed, #6d28d9); color: white;">
                        <th style="padding: 12px; text-align: left;">Vulnerability Type</th>
                        <th style="padding: 12px; text-align: left;">Severity</th>
                        <th style="padding: 12px; text-align: left;">Description</th>
                        <th style="padding: 12px; text-align: left;">Method</th>
                    </tr>
                </thead>
                <tbody>
                    {vuln_rows}
                </tbody>
            </table>
            <p style="color: #6b7280; font-style: italic; margin-top: 15px;">Showing {min(15, len(vulnerabilities))} of {len(vulnerabilities)} total vulnerabilities</p>
        </div>"""
    
    # Generate privacy recommendations
    recommendations_html = ""
    try:
        from services.api_scanner import APIScanner
        scanner = APIScanner()
        recommendations = scanner.generate_privacy_recommendations(scan_data)
        
        if recommendations:
            recommendation_items = ""
            for i, rec in enumerate(recommendations[:8]):
                recommendation_items += f"""
                <div style="background: #f0fdf4; border-left: 4px solid #22c55e; padding: 15px; margin-bottom: 15px; border-radius: 0 8px 8px 0;">
                    <div style="display: flex; align-items: start; gap: 10px;">
                        <span style="background: #22c55e; color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold; flex-shrink: 0;">{i+1}</span>
                        <p style="margin: 0; color: #15803d; line-height: 1.5; font-size: 14px;">{rec}</p>
                    </div>
                </div>"""
            
            recommendations_html = f"""
            <div style="background: white; border-radius: 15px; padding: 30px; margin: 20px; box-shadow: 0 6px 20px rgba(0,0,0,0.1);">
                <h2 style="color: #059669; margin-bottom: 20px;">💡 Security & Privacy Recommendations</h2>
                
                <div style="background: #ecfdf5; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                    <h3 style="color: #059669; margin: 0 0 10px 0; font-size: 18px;">Actionable Security Improvements</h3>
                    <p style="color: #047857; margin: 0; font-size: 14px;">
                        Based on comprehensive API analysis including vulnerability testing, PII detection, and security assessments:
                    </p>
                </div>
                
                {recommendation_items}
                
                <div style="background: #f3f4f6; padding: 20px; border-radius: 10px; margin-top: 20px;">
                    <p style="color: #6b7280; font-size: 13px; margin: 0; text-align: center;">
                        <strong>API Security Note:</strong> Regular security testing and monitoring are essential for maintaining secure APIs.
                        Implement these recommendations systematically and document your security measures.
                    </p>
                </div>
            </div>"""
    except Exception:
        recommendations_html = ""
    
    # Generate complete HTML report
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Security & Privacy Assessment Report - {base_url}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f8fafc; color: #1f2937; line-height: 1.6; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e5e7eb; }}
        th {{ background: #f9fafb; font-weight: 600; color: #374151; }}
        .severity-critical {{ background: #dc2626; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; }}
        .severity-high {{ background: #ea580c; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; }}
        .severity-medium {{ background: #d97706; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; }}
        .severity-low {{ background: #16a34a; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header Section -->
        <div style="background: linear-gradient(135deg, #1e40af, #3b82f6); color: white; padding: 40px; border-radius: 15px; margin-bottom: 30px; position: relative; overflow: hidden;">
            <div style="position: absolute; top: 20px; right: 20px; background: rgba(255,255,255,0.2); padding: 10px 15px; border-radius: 50px; backdrop-filter: blur(10px);">
                <span style="font-size: 12px; font-weight: 500;">API SECURITY REPORT</span>
            </div>
            <h1 style="font-size: 32px; margin-bottom: 10px; font-weight: 700;">API Security & Privacy Assessment</h1>
            <p style="font-size: 18px; opacity: 0.9; margin-bottom: 20px;">Comprehensive security analysis for {base_url}</p>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 30px;">
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; text-align: center; backdrop-filter: blur(10px);">
                    <div style="font-size: 24px; font-weight: bold;">{endpoints_scanned}</div>
                    <div style="font-size: 14px; opacity: 0.8;">Endpoints Scanned</div>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; text-align: center; backdrop-filter: blur(10px);">
                    <div style="font-size: 24px; font-weight: bold;">{total_issues}</div>
                    <div style="font-size: 14px; opacity: 0.8;">Security Issues</div>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; text-align: center; backdrop-filter: blur(10px);">
                    <div style="font-size: 24px; font-weight: bold; color: {risk_color};">{overall_risk}</div>
                    <div style="font-size: 14px; opacity: 0.8;">Overall Risk</div>
                </div>
            </div>
        </div>
        
        <!-- Security Overview -->
        <div style="background: white; border-radius: 15px; padding: 30px; margin: 20px; box-shadow: 0 6px 20px rgba(0,0,0,0.1);">
            <h2 style="color: #1e40af; margin-bottom: 20px;">📊 Security Overview</h2>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px;">
                <div style="background: #fef2f2; padding: 20px; border-radius: 10px; text-align: center; border-left: 4px solid #dc2626;">
                    <h3 style="color: #dc2626; margin: 0; font-size: 28px;">{critical_count}</h3>
                    <p style="color: #991b1b; margin: 5px 0 0 0; font-weight: 500;">Critical Issues</p>
                </div>
                <div style="background: #fff7ed; padding: 20px; border-radius: 10px; text-align: center; border-left: 4px solid #ea580c;">
                    <h3 style="color: #ea580c; margin: 0; font-size: 28px;">{high_count}</h3>
                    <p style="color: #c2410c; margin: 5px 0 0 0; font-weight: 500;">High Risk</p>
                </div>
                <div style="background: #fffbeb; padding: 20px; border-radius: 10px; text-align: center; border-left: 4px solid #d97706;">
                    <h3 style="color: #d97706; margin: 0; font-size: 28px;">{medium_count}</h3>
                    <p style="color: #a16207; margin: 5px 0 0 0; font-weight: 500;">Medium Risk</p>
                </div>
                <div style="background: #f0fdf4; padding: 20px; border-radius: 10px; text-align: center; border-left: 4px solid #16a34a;">
                    <h3 style="color: #16a34a; margin: 0; font-size: 28px;">{low_count}</h3>
                    <p style="color: #15803d; margin: 5px 0 0 0; font-weight: 500;">Low Risk</p>
                </div>
            </div>
            
            <div style="background: #f8fafc; padding: 20px; border-radius: 10px;">
                <h3 style="color: #374151; margin-bottom: 10px;">Scan Summary</h3>
                <p style="color: #6b7280; margin-bottom: 10px;"><strong>Target API:</strong> {base_url}</p>
                <p style="color: #6b7280; margin-bottom: 10px;"><strong>Scan Date:</strong> {timestamp}</p>
                <p style="color: #6b7280; margin-bottom: 10px;"><strong>Endpoints Analyzed:</strong> {endpoints_scanned}</p>
                <p style="color: #6b7280;"><strong>Overall Risk Level:</strong> <span style="color: {risk_color}; font-weight: bold;">{overall_risk}</span></p>
            </div>
        </div>
        
        {findings_html}
        {pii_html}
        {vuln_html}
        {recommendations_html}
        
        <!-- Certification Footer -->
        <div style="background: white; border-radius: 15px; margin: 20px; padding: 30px; text-align: center; box-shadow: 0 6px 20px rgba(0,0,0,0.1);">
            <p style="color: #374151; font-size: 12px; line-height: 1.6; max-width: 600px; margin: 0 auto;">
                This API security assessment was conducted on {timestamp} using DataGuardian Pro's comprehensive 
                API scanner. The assessment analyzed security vulnerabilities, PII exposure, authentication issues, and privacy compliance.
            </p>
            <div style="margin-top: 30px; padding-top: 20px; border-top: 2px solid #e5e7eb;">
                <p style="color: #6b7280; font-size: 11px; margin: 5px 0;">
                    <strong>DataGuardian Pro Enterprise Certification Authority</strong>
                </p>
                <p style="color: #6b7280; font-size: 10px; margin: 0;">
                    Enterprise API Security & Privacy Compliance Platform
                </p>
            </div>
        </div>
    </div>
</body>
</html>"""

def generate_api_pdf_report(scan_data: Dict[str, Any], output_path: str) -> str:
    """
    Generate a PDF report for API scan results.
    
    Args:
        scan_data: Dictionary containing API scan results
        output_path: Path where the PDF report should be saved
        
    Returns:
        Path to the generated PDF report
    """
    try:
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        elements = []
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=HexColor('#1e40af'),
            alignment=1
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=HexColor('#374151')
        )
        
        # Extract data
        base_url = scan_data.get('base_url', 'Unknown')
        scan_time = scan_data.get('scan_time', datetime.now().isoformat())
        endpoints_scanned = scan_data.get('endpoints_scanned', 0)
        findings = scan_data.get('findings', [])
        stats = scan_data.get('stats', {})
        
        # Title
        elements.append(Paragraph("API Security & Privacy Assessment Report", title_style))
        elements.append(Spacer(1, 20))
        
        # Summary section
        elements.append(Paragraph("Executive Summary", heading_style))
        summary_data = [
            ['Target API', base_url],
            ['Scan Date', scan_time],
            ['Endpoints Scanned', str(endpoints_scanned)],
            ['Total Issues Found', str(stats.get('total_findings', 0))],
            ['Critical Issues', str(stats.get('critical_findings', 0))],
            ['High Risk Issues', str(stats.get('high_findings', 0))]
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 3.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#374151')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#e5e7eb')),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 30))
        
        # Findings section
        if findings:
            elements.append(Paragraph("Security Findings", heading_style))
            findings_data = [['Severity', 'Type', 'Description']]
            
            for finding in findings[:15]:  # Limit to first 15 findings
                findings_data.append([
                    finding.get('severity', 'Unknown'),
                    finding.get('type', 'Unknown').replace('_', ' ').title(),
                    finding.get('description', 'No description')[:80] + '...' if len(finding.get('description', '')) > 80 else finding.get('description', 'No description')
                ])
            
            findings_table = Table(findings_data, colWidths=[1*inch, 1.5*inch, 3.5*inch])
            findings_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#dc2626')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#fef2f2')),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#fecaca')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(findings_table)
            elements.append(Spacer(1, 20))
        
        # Build PDF
        doc.build(elements)
        return output_path
        
    except Exception as e:
        raise Exception(f"Failed to generate PDF report: {str(e)}")