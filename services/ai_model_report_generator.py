"""
AI Model Scan Report Generator

This module provides a modern, branded PDF report generator specifically for AI Model scans.
It creates visually appealing reports with company branding, charts, and detailed findings.
"""

import io
import os
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Union

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.colors import HexColor, toColor
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, 
    PageBreak, Flowable, KeepTogether, Preformatted
)
from reportlab.graphics.shapes import Drawing, Circle, Rect, Line, String, Wedge
from reportlab.graphics.charts.barcharts import VerticalBarChart, HorizontalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics import renderPDF

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Add file handler if needed
if not logger.handlers:
    try:
        os.makedirs('logs', exist_ok=True)
        file_handler = logging.FileHandler('logs/ai_model_report.log')
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Error setting up logger: {str(e)}")

# Define color palette for consistent branding
BRANDING_COLORS = {
    "primary": "#4f46e5",     # Primary brand color
    "secondary": "#818cf8",   # Secondary brand color
    "accent": "#3730a3",      # Accent color
    "success": "#10b981",     # Success/low risk
    "warning": "#f59e0b",     # Warning/medium risk
    "danger": "#ef4444",      # Danger/high risk
    "critical": "#991b1b",    # Critical risk
    "text_dark": "#1e293b",   # Dark text color
    "text_light": "#94a3b8",  # Light text color
    "background": "#ffffff",  # Background color
}

# Risk level colors mapping
RISK_COLORS = {
    "low": BRANDING_COLORS["success"],
    "medium": BRANDING_COLORS["warning"],
    "high": BRANDING_COLORS["danger"],
    "critical": BRANDING_COLORS["critical"],
}

class RiskMeter(Flowable):
    """A custom flowable that creates a modern risk gauge with enhanced visualization."""
    
    def __init__(self, risk_score: int, width: int = 250, height: int = 150):
        Flowable.__init__(self)
        self.risk_score = risk_score
        self.width = width
        self.height = height
    
    def draw(self):
        # Drawing with width and height
        d = Drawing(self.width, self.height)
        
        # Determine risk level and styling based on score
        if self.risk_score >= 75:
            main_color = HexColor(RISK_COLORS["critical"])
            risk_text = "Critical"
            angle_start = 180
            angle_end = 240
        elif self.risk_score >= 50:
            main_color = HexColor(RISK_COLORS["high"])
            risk_text = "High"
            angle_start = 120
            angle_end = 180
        elif self.risk_score >= 25:
            main_color = HexColor(RISK_COLORS["medium"])
            risk_text = "Medium"
            angle_start = 60
            angle_end = 120
        else:
            main_color = HexColor(RISK_COLORS["low"])
            risk_text = "Low"
            angle_start = 0
            angle_end = 60
        
        # Create a more modern gauge
        gauge_center_x = self.width / 2
        gauge_center_y = 50
        gauge_radius = 45
        
        # Add background gauge (full semi-circle in light gray)
        bg_arc = Wedge(
            gauge_center_x, gauge_center_y, gauge_radius, 
            0, 240, fillColor=colors.lightgrey
        )
        d.add(bg_arc)
        
        # Add colored segments for risk zones
        # Green zone (0-60°)
        green_segment = Wedge(
            gauge_center_x, gauge_center_y, gauge_radius,
            0, 60, fillColor=HexColor(RISK_COLORS["low"])
        )
        d.add(green_segment)
        
        # Yellow zone (60-120°)
        yellow_segment = Wedge(
            gauge_center_x, gauge_center_y, gauge_radius,
            60, 120, fillColor=HexColor(RISK_COLORS["medium"])
        )
        d.add(yellow_segment)
        
        # Orange zone (120-180°)
        orange_segment = Wedge(
            gauge_center_x, gauge_center_y, gauge_radius,
            120, 180, fillColor=HexColor(RISK_COLORS["high"])
        )
        d.add(orange_segment)
        
        # Red zone (180-240°)
        red_segment = Wedge(
            gauge_center_x, gauge_center_y, gauge_radius,
            180, 240, fillColor=HexColor(RISK_COLORS["critical"])
        )
        d.add(red_segment)
        
        # Add inner white circle for cleaner look
        inner_circle = Circle(
            gauge_center_x, gauge_center_y, gauge_radius - 15,
            fillColor=colors.white, strokeColor=None
        )
        d.add(inner_circle)
        
        # Calculate indicator angle based on risk score (map 0-100 to 0-240 degrees)
        indicator_angle = min(240, (self.risk_score / 100) * 240)
        rad_angle = np.radians(indicator_angle)
        
        # Calculate needle positions
        x = gauge_center_x + (gauge_radius - 5) * np.cos(rad_angle)
        y = gauge_center_y + (gauge_radius - 5) * np.sin(rad_angle)
        
        # Add indicator needle with thicker line
        needle = Line(
            gauge_center_x, gauge_center_y, x, y, 
            strokeColor=main_color, strokeWidth=3
        )
        d.add(needle)
        
        # Add center circle for needle pivot
        pivot = Circle(
            gauge_center_x, gauge_center_y, 8,
            fillColor=main_color, strokeColor=colors.darkgrey
        )
        d.add(pivot)
        
        # Add risk level label
        risk_label = String(
            gauge_center_x, gauge_center_y - 30,
            risk_text,
            fontSize=14,
            fillColor=main_color,
            textAnchor='middle'
        )
        d.add(risk_label)
        
        # Add risk score label
        score_label = String(
            gauge_center_x, gauge_center_y - 50,
            f"Score: {self.risk_score}/100",
            fontSize=10,
            fillColor=HexColor(BRANDING_COLORS["text_dark"]),
            textAnchor='middle'
        )
        d.add(score_label)
        
        # Render the drawing
        renderPDF.draw(d, self.canv, 0, 0)

class PieChartWithLegend(Flowable):
    """Custom flowable to create a pie chart with legend"""
    
    def __init__(self, data: Dict[str, int], title: str, width: int = 250, height: int = 200):
        Flowable.__init__(self)
        self.data = data
        self.title = title
        self.width = width
        self.height = height
    
    def draw(self):
        # Create drawing
        d = Drawing(self.width, self.height)
        
        # Prepare pie chart data
        pie = Pie()
        pie.x = 70
        pie.y = 85
        pie.width = 100
        pie.height = 100
        
        # Extract values and labels
        pie_data = list(self.data.values())
        labels = list(self.data.keys())
        
        # Use brand colors
        colors = [
            HexColor(BRANDING_COLORS["danger"]),
            HexColor(BRANDING_COLORS["warning"]),
            HexColor(BRANDING_COLORS["success"]),
            HexColor(BRANDING_COLORS["primary"])
        ]
        
        pie.data = pie_data
        pie.labels = [f"{l}: {v}" for l, v in zip(labels, pie_data)]
        pie.slices.strokeWidth = 0.5
        for i, color in enumerate(colors[:len(pie_data)]):
            pie.slices[i].fillColor = color
        
        # Add title
        title = String(
            self.width//2, self.height-15,
            self.title,
            fontSize=12,
            fillColor=HexColor(BRANDING_COLORS["text_dark"]),
            textAnchor='middle'
        )
        
        # Add legend manually
        legend_x = 150
        legend_y = 120
        legend_gap = 20
        
        for i, (label, value) in enumerate(self.data.items()):
            # Colored square
            rect = Rect(
                legend_x, legend_y - (i * legend_gap), 
                10, 10, 
                fillColor=colors[i % len(colors)]
            )
            d.add(rect)
            
            # Label text
            text = String(
                legend_x + 15, legend_y - (i * legend_gap) + 3,
                f"{label}: {value}",
                fontSize=9,
                fillColor=HexColor(BRANDING_COLORS["text_dark"])
            )
            d.add(text)
        
        # Add elements to drawing
        d.add(pie)
        d.add(title)
        
        # Render the drawing
        renderPDF.draw(d, self.canv, 0, 0)

def create_ai_model_scan_report(scan_data: Dict[str, Any]) -> bytes:
    """
    Create a modern, professionally designed PDF report for AI Model scan results
    
    Args:
        scan_data: The AI model scan result data
        
    Returns:
        Report as bytes that can be written to a file or served directly
    """
    # Initialize buffer for PDF
    buffer = io.BytesIO()
    
    # Log scan data keys for debugging
    logger.info(f"Creating AI model scan report for scan_id: {scan_data.get('scan_id', 'unknown')}")
    logger.info(f"Available scan data keys: {list(scan_data.keys())}")
    
    # Check for required fields
    if not scan_data or not isinstance(scan_data, dict):
        logger.error("Invalid scan data provided - not a dictionary or None")
        return None
    
    # Ensure all required fields are present
    scan_id = scan_data.get('scan_id', f"AIMOD-{uuid.uuid4().hex[:8]}")
    timestamp = scan_data.get('timestamp', datetime.now().isoformat())
    model_type = scan_data.get('model_type', 'Unknown')
    model_source = scan_data.get('model_source', 'Unknown')
    findings = scan_data.get('findings', [])
    risk_score = scan_data.get('risk_score', 0)
    
    # Format timestamp
    try:
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp)
        else:
            dt = timestamp
        timestamp_str = dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        logger.error(f"Error formatting timestamp: {str(e)}")
        timestamp_str = str(timestamp)
    
    # Count findings by risk level if not already present
    if ('high_risk_count' not in scan_data or 'medium_risk_count' not in scan_data or 
        'low_risk_count' not in scan_data) and findings:
        high_risk = 0
        medium_risk = 0
        low_risk = 0
        critical_risk = 0
        
        for finding in findings:
            risk_level = finding.get('risk_level', 'low')
            if isinstance(risk_level, str):
                risk_level = risk_level.lower()
            if risk_level == 'critical':
                critical_risk += 1
            elif risk_level == 'high':
                high_risk += 1
            elif risk_level == 'medium':
                medium_risk += 1
            else:
                low_risk += 1
        
        scan_data['critical_risk_count'] = critical_risk
        scan_data['high_risk_count'] = high_risk
        scan_data['medium_risk_count'] = medium_risk
        scan_data['low_risk_count'] = low_risk
    else:
        # Use provided risk counts or risk_counts dictionary
        risk_counts = scan_data.get('risk_counts', {})
        high_risk = scan_data.get('high_risk_count', risk_counts.get('high', 0))
        medium_risk = scan_data.get('medium_risk_count', risk_counts.get('medium', 0))
        low_risk = scan_data.get('low_risk_count', risk_counts.get('low', 0))
        critical_risk = scan_data.get('critical_risk_count', risk_counts.get('critical', 0))
    
    # Define document with custom page size (A4 with 0.5 inch margins)
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        leftMargin=0.5*inch,
        rightMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    # Initialize elements to build the PDF
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Create custom styles for the report
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=HexColor(BRANDING_COLORS["primary"]),
        spaceAfter=12,
        alignment=1  # Center alignment
    )
    
    subtitle_style = ParagraphStyle(
        'ReportSubtitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=HexColor(BRANDING_COLORS["text_dark"]),
        spaceAfter=10,
        alignment=1  # Center alignment
    )
    
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=HexColor(BRANDING_COLORS["primary"]),
        spaceBefore=12,
        spaceAfter=6
    )
    
    subheading_style = ParagraphStyle(
        'Subheading',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=HexColor(BRANDING_COLORS["text_dark"]),
        spaceBefore=10,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=HexColor(BRANDING_COLORS["text_dark"]),
        spaceBefore=6,
        spaceAfter=6
    )
    
    # Add logo and header
    try:
        logo_path = os.path.join(os.getcwd(), "static", "logo.png")
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=1.5*inch, height=0.5*inch)
            elements.append(logo)
        else:
            logger.warning(f"Logo file not found at {logo_path}")
            # Create text-based header as fallback
            elements.append(Paragraph("DataGuardian Pro", title_style))
    except Exception as e:
        logger.error(f"Error adding logo: {str(e)}")
        # Create text-based header as fallback
        elements.append(Paragraph("DataGuardian Pro", title_style))
    
    # Add report title
    elements.append(Paragraph("AI Model Risk Analysis Report", title_style))
    elements.append(Paragraph(f"Generated on {timestamp_str}", subtitle_style))
    
    # Add horizontal line
    elements.append(Spacer(1, 0.1*inch))
    elements.append(HorizontalRule())
    elements.append(Spacer(1, 0.2*inch))
    
    # Executive summary section
    elements.append(Paragraph("Executive Summary", heading_style))
    
    # Summary text
    summary_text = f"""
    This report presents the findings of an AI model risk assessment conducted on {timestamp_str}.
    The assessment evaluated a {model_type} model from {model_source} for privacy risks, bias concerns,
    and explainability issues. The analysis identified a total of {len(findings)} findings across
    multiple risk categories.
    """
    elements.append(Paragraph(summary_text, body_style))
    
    # Create 2-column layout for summary metrics
    summary_data = [
        ["Scan ID:", scan_id],
        ["Model Type:", model_type],
        ["Model Source:", model_source],
        ["Scan Date:", timestamp_str],
        ["Risk Score:", f"{risk_score}/100"],
        ["Total Findings:", str(len(findings))],
    ]
    
    # Add repository information if available
    if model_source == "Repository URL":
        summary_data.append(["Repository URL:", scan_data.get('repository_url', 'Not specified')])
        summary_data.append(["Branch:", scan_data.get('branch', 'Not specified')])
    
    # Create summary table
    summary_table = Table(summary_data, colWidths=[1.5*inch, 4*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), HexColor(BRANDING_COLORS["primary"])),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Risk assessment summary with visual meter
    elements.append(Paragraph("Risk Assessment", heading_style))
    
    # Add risk meter gauge
    risk_meter = RiskMeter(risk_score)
    elements.append(risk_meter)
    elements.append(Spacer(1, 0.1*inch))
    
    # Add a summary of key metrics
    elements.append(Paragraph("Key Risk Metrics", subheading_style))
    
    # Prepare data for findings pie chart
    risk_distribution = {
        "Critical": critical_risk,
        "High": high_risk,
        "Medium": medium_risk,
        "Low": low_risk
    }
    
    # Create findings distribution pie chart
    findings_chart = PieChartWithLegend(risk_distribution, "Findings by Risk Level")
    elements.append(findings_chart)
    elements.append(Spacer(1, 0.2*inch))
    
    # PII and bias summary
    pii_detected = scan_data.get("personal_data_detected", False)
    bias_detected = scan_data.get("bias_detected", False)
    explainability_score = scan_data.get("explainability_score", 0)
    
    pii_status = "✓ Detected" if pii_detected else "✗ Not Detected"
    bias_status = "✓ Detected" if bias_detected else "✗ Not Detected"
    
    privacy_data = [
        ["Metric", "Status", "Risk Level"],
        ["Personal Data in Model", pii_status, "High" if pii_detected else "Low"],
        ["Bias/Fairness Issues", bias_status, "High" if bias_detected else "Low"],
        ["Explainability Score", f"{explainability_score}/100", 
         "High" if explainability_score < 50 else "Medium" if explainability_score < 75 else "Low"],
    ]
    
    privacy_table = Table(privacy_data, colWidths=[2*inch, 2*inch, 2*inch])
    privacy_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor(BRANDING_COLORS["primary"])),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (2, 1), (2, 1), 
         HexColor(RISK_COLORS["high"] if pii_detected else RISK_COLORS["low"])),
        ('BACKGROUND', (2, 2), (2, 2), 
         HexColor(RISK_COLORS["high"] if bias_detected else RISK_COLORS["low"])),
        ('BACKGROUND', (2, 3), (2, 3), 
         HexColor(RISK_COLORS["high"] if explainability_score < 50 else 
                 RISK_COLORS["medium"] if explainability_score < 75 else RISK_COLORS["low"])),
        ('TEXTCOLOR', (2, 1), (2, -1), colors.white),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(privacy_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Detailed findings section
    elements.append(Paragraph("Detailed Findings", heading_style))
    
    # Group findings by category for better organization
    finding_categories = {}
    for finding in findings:
        category = finding.get('category', 'Other')
        if category not in finding_categories:
            finding_categories[category] = []
        finding_categories[category].append(finding)
    
    # Process each category
    for category, category_findings in finding_categories.items():
        elements.append(Paragraph(category, subheading_style))
        
        # Create table of findings in this category
        finding_rows = [["ID", "Type", "Description", "Risk Level"]]
        
        for finding in category_findings:
            # Truncate description if too long
            description = finding.get('description', 'No description')
            if len(description) > 100:
                description = description[:97] + "..."
                
            # Format risk level with color
            risk_level = finding.get('risk_level', 'low').lower()
            risk_color = RISK_COLORS.get(risk_level, RISK_COLORS["low"])
            
            finding_rows.append([
                finding.get('id', ''),
                finding.get('type', ''),
                description,
                risk_level.capitalize()
            ])
        
        # Create findings table
        findings_table = Table(finding_rows, colWidths=[0.8*inch, 1.2*inch, 3.5*inch, 0.8*inch])
        findings_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor(BRANDING_COLORS["primary"])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        
        # Apply risk level colors - need to do this row by row
        for i, row in enumerate(finding_rows[1:], 1):
            risk_level = row[3].lower()
            risk_color = RISK_COLORS.get(risk_level, RISK_COLORS["low"])
            findings_table.setStyle(TableStyle([
                ('BACKGROUND', (3, i), (3, i), HexColor(risk_color)),
                ('TEXTCOLOR', (3, i), (3, i), colors.white),
            ]))
        
        elements.append(findings_table)
        elements.append(Spacer(1, 0.1*inch))
    
    # Recommendations section
    elements.append(Paragraph("Recommendations", heading_style))
    
    # Generate recommendations based on findings
    recommendations = []
    if pii_detected:
        recommendations.append("Implement data minimization techniques to remove unnecessary personal data from the model")
        recommendations.append("Conduct a Data Protection Impact Assessment (DPIA) for this AI model")
        recommendations.append("Apply differential privacy to your training process")
    
    if bias_detected:
        recommendations.append("Implement bias mitigation techniques like reweighting or adversarial debiasing")
        recommendations.append("Ensure diverse and representative training data")
        recommendations.append("Use fairness constraints during model training")
    
    if explainability_score < 75:
        recommendations.append("Enhance model transparency with feature importance visualization")
        recommendations.append("Consider using more interpretable model architectures")
        recommendations.append("Implement SHAP or LIME explanations for individual predictions")
    
    # If we have high or critical findings, add specific recommendations
    high_findings = [f for f in findings if f.get('risk_level', '').lower() in ['high', 'critical']]
    if high_findings:
        recommendations.append("Prioritize addressing high and critical risk findings")
        recommendations.append("Conduct regular AI model audits and ethical reviews")
    
    # Add default recommendations if we have none
    if not recommendations:
        recommendations.append("Maintain current privacy and security controls")
        recommendations.append("Continue monitoring model performance and behavior")
        recommendations.append("Implement a regular model review process")
    
    # Add recommendations to report
    for i, recommendation in enumerate(recommendations, 1):
        elements.append(Paragraph(f"{i}. {recommendation}", body_style))
    
    elements.append(Spacer(1, 0.2*inch))
    
    # Add conclusion
    elements.append(Paragraph("Conclusion", heading_style))
    
    conclusion_text = f"""
    This AI model risk assessment identified {len(findings)} findings with a total risk score of {risk_score}/100.
    The model {'has personal data privacy concerns' if pii_detected else 'shows no evidence of personal data exposure'},
    {'exhibits bias issues' if bias_detected else 'shows no significant bias'}, and has an explainability score of
    {explainability_score}/100. By addressing the recommendations provided in this report, you can improve
    the model's compliance, fairness, and transparency.
    """
    elements.append(Paragraph(conclusion_text, body_style))
    
    # Add footer with page numbers
    def add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.drawString(inch, 0.5 * inch, f"Page {doc.page} of {doc.pageCount}")
        canvas.drawRightString(doc.width + inch, 0.5 * inch, "DataGuardian Pro")
        canvas.restoreState()
    
    # Build the PDF document
    try:
        doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
        
        # Get PDF bytes from buffer
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        # Save a copy to reports directory
        try:
            os.makedirs("reports", exist_ok=True)
            report_filename = f"ai_model_scan_{scan_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            report_path = os.path.join("reports", report_filename)
            
            with open(report_path, "wb") as f:
                f.write(pdf_bytes)
                
            logger.info(f"AI model report saved to: {report_path}")
            
            # Update scan data with report path
            scan_data['report_path'] = report_path
            
        except Exception as save_error:
            logger.error(f"Error saving report to file: {str(save_error)}")
        
        return pdf_bytes
    except Exception as build_error:
        logger.error(f"Error building PDF: {str(build_error)}")
        return None

class HorizontalRule(Flowable):
    """Custom flowable to draw a horizontal rule"""
    
    def __init__(self, width=None, thickness=0.5, color=None):
        Flowable.__init__(self)
        self.width = width or '100%'
        self.thickness = thickness
        self.color = color or HexColor(BRANDING_COLORS["primary"])
        
    def wrap(self, availWidth, availHeight):
        if self.width == '100%':
            self.width = availWidth
        return (self.width, self.thickness)
        
    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 0, self.width, 0)