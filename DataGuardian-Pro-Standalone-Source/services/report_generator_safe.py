import io
import os
import base64
import streamlit as st
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.colors import HexColor, toColor
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Flowable

def generate_report(scan_results: Dict[str, Any], report_type: str = "comprehensive") -> bytes:
    """
    Generate a comprehensive PDF report without matplotlib dependencies.
    
    Args:
        scan_results: Dictionary containing scan results
        report_type: Type of report to generate
    
    Returns:
        PDF report as bytes
    """
    try:
        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            name='ReportTitle',
            parent=styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=1,  # Center alignment
            textColor=colors.HexColor('#1a365d')
        )
        
        story.append(Paragraph("DataGuardian Pro - Scan Report", title_style))
        story.append(Spacer(1, 20))
        
        # Metadata
        metadata = scan_results.get('metadata', {})
        story.append(Paragraph("Scan Information", styles['Heading2']))
        
        info_data = [
            ['Scan Date:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Scan Type:', metadata.get('scan_type', 'Unknown')],
            ['Region:', metadata.get('region', 'Unknown')],
            ['Items Scanned:', str(metadata.get('total_items', 0))]
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 30))
        
        # Summary
        findings = scan_results.get('findings', [])
        risk_summary = scan_results.get('risk_summary', {})
        
        story.append(Paragraph("Summary", styles['Heading2']))
        story.append(Paragraph(f"Total PII findings: {len(findings)}", styles['Normal']))
        story.append(Paragraph(f"Risk level: {risk_summary.get('level', 'Unknown')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Findings
        if findings:
            story.append(Paragraph("Detailed Findings", styles['Heading2']))
            
            findings_data = [['Type', 'Risk Level', 'Confidence', 'Source']]
            
            for finding in findings:
                findings_data.append([
                    finding.get('type', 'Unknown'),
                    finding.get('risk_level', 'Unknown'),
                    f"{finding.get('confidence', 0):.0%}",
                    finding.get('source', 'Unknown')
                ])
            
            findings_table = Table(findings_data, colWidths=[1.5*inch, 1*inch, 1*inch, 2*inch])
            findings_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2b6cb0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            
            story.append(findings_table)
        else:
            story.append(Paragraph("No PII findings detected", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
        
    except Exception as e:
        # Fallback simple report
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = [Paragraph("DataGuardian Pro - Basic Report", getSampleStyleSheet()['Title'])]
        story.append(Paragraph(f"Report generated on {datetime.now()}", getSampleStyleSheet()['Normal']))
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

def create_chart_placeholder() -> str:
    """Create a text-based chart placeholder for reports without matplotlib"""
    return """
    Chart data would be displayed here in the full version.
    This version operates without advanced visualization dependencies.
    """

# Backward compatibility functions
def generate_comprehensive_report(scan_results: Dict[str, Any]) -> bytes:
    return generate_report(scan_results, "comprehensive")

def generate_summary_report(scan_results: Dict[str, Any]) -> bytes:
    return generate_report(scan_results, "summary")

def create_risk_visualization(risk_data: Dict[str, Any]) -> str:
    """Create text-based risk visualization"""
    risk_level = risk_data.get('level', 'Unknown')
    risk_score = risk_data.get('score', 0)
    
    return f"""
    Risk Assessment:
    Level: {risk_level}
    Score: {risk_score}/100
    
    Visual representation would appear here in the full version.
    """

def generate_database_html_report(scan_results: Dict[str, Any]) -> str:
    """
    Generate HTML report for database scan results without numpy/pandas dependencies.
    
    Args:
        scan_results: Dictionary containing database scan results
        
    Returns:
        HTML content as string
    """
    findings = scan_results.get('findings', [])
    metadata = scan_results.get('metadata', {})
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>DataGuardian Pro - Database Security Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ text-align: center; color: #1a365d; }}
            .findings {{ margin: 20px 0; }}
            .finding {{ margin: 15px 0; padding: 15px; border-left: 4px solid #3182ce; background: #f7fafc; }}
            .high-risk {{ border-color: #e53e3e; }}
            .medium-risk {{ border-color: #d69e2e; }}
            .low-risk {{ border-color: #38a169; }}
            .metadata {{ background: #edf2f7; padding: 15px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <h1 class="header">Database Security Analysis Report</h1>
        <div class="metadata">
            <h3>Scan Information</h3>
            <p><strong>Scan Date:</strong> {metadata.get('scan_date', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}</p>
            <p><strong>Database Type:</strong> {metadata.get('db_type', 'Unknown')}</p>
            <p><strong>Total Findings:</strong> {len(findings)}</p>
        </div>
        
        <div class="findings">
            <h3>Security Findings</h3>
    """
    
    for finding in findings:
        risk_class = f"{finding.get('risk_level', 'low').lower()}-risk"
        html_content += f"""
            <div class="finding {risk_class}">
                <h4>{finding.get('type', 'Security Issue')}</h4>
                <p><strong>Risk Level:</strong> {finding.get('risk_level', 'Low')}</p>
                <p><strong>Description:</strong> {finding.get('description', 'No description available')}</p>
                <p><strong>Table:</strong> {finding.get('table', 'N/A')}</p>
                <p><strong>Column:</strong> {finding.get('column', 'N/A')}</p>
            </div>
        """
    
    html_content += """
        </div>
        <footer style="margin-top: 40px; text-align: center; color: #666;">
            <p>Generated by DataGuardian Pro - Enterprise Privacy Compliance Platform</p>
        </footer>
    </body>
    </html>
    """
    
    return html_content