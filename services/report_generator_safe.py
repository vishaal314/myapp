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