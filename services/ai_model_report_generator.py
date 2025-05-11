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

# Helper function to determine security level based on risk score
def get_security_level(risk_score: int) -> str:
    """
    Determine the security certification level based on risk score
    
    Args:
        risk_score: The risk score (0-100)
        
    Returns:
        Security level string
    """
    if risk_score < 25:
        return "AAA (Excellent)"
    elif risk_score < 50:
        return "AA (Very Good)"
    elif risk_score < 75:
        return "A (Good)"
    else:
        return "B (Needs Improvement)"

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
        # Labels are handled manually with the legend instead of using pie.labels
        # since the Pie object doesn't support labels properly
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
        # Return empty PDF bytes rather than None to avoid type errors
        return b''
    
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
    
    # Create a professional certificate-style header
    # First, create a header table with logo and title
    try:
        # Try multiple paths for logo
        logo_paths = [
            os.path.join(os.getcwd(), "static", "logo.png"),
            os.path.join(os.getcwd(), "static", "logo.svg"),
            os.path.join(os.getcwd(), "static", "logo.jpg")
        ]
        
        logo_image = None
        for path in logo_paths:
            if os.path.exists(path):
                # Create larger logo for certificate style
                logo_image = Image(path, width=2.5*inch, height=1*inch)
                break
                
        if logo_image:
            # Create a centered table for logo and title
            header_data = [[logo_image]]
            header_table = Table(header_data, colWidths=[6*inch])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(header_table)
        else:
            logger.warning("Logo file not found in any of the expected locations")
            # Create text-based header as fallback with certificate styling
            header_text = Paragraph(
                '<font size="24" color="#4f46e5"><b>DataGuardian Pro</b></font>', 
                styles['Title']
            )
            elements.append(header_text)
    except Exception as e:
        logger.error(f"Error adding logo: {str(e)}")
        # Create text-based header as fallback
        header_text = Paragraph(
            '<font size="24" color="#4f46e5"><b>DataGuardian Pro</b></font>', 
            styles['Title']
        )
        elements.append(header_text)
    
    # Add certificate-like title with decorative elements
    elements.append(Spacer(1, 0.3*inch))
    
    elements.append(Paragraph(
        '<font size="18">AI Model Security Certification</font>', 
        ParagraphStyle(
            'CertificateTitle',
            parent=styles['Title'],
            alignment=1,  # Center alignment
            textColor=HexColor(BRANDING_COLORS["primary"]),
        )
    ))
    
    # Add decorative line
    elements.append(Spacer(1, 0.1*inch))
    line = Drawing(400, 10)
    line.add(Line(
        50, 5, 350, 5, 
        strokeColor=HexColor(BRANDING_COLORS["secondary"]),
        strokeWidth=2
    ))
    elements.append(line)
    
    # Add report subtitle
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph(
        f"Risk Analysis Report • Generated on {timestamp_str}", 
        ParagraphStyle(
            'CertificateSubtitle',
            parent=subtitle_style,
            alignment=1,  # Center alignment
        )
    ))
    
    # Add horizontal line
    elements.append(Spacer(1, 0.1*inch))
    elements.append(HorizontalRule())
    elements.append(Spacer(1, 0.2*inch))
    
    # Executive summary section with certificate-like styling
    elements.append(
        Paragraph(
            '<font size="14" color="#4f46e5">Executive Summary</font>',
            ParagraphStyle(
                'CertHeading',
                parent=heading_style,
                alignment=1,  # Center
                spaceBefore=12,
                spaceAfter=10,
            )
        )
    )
    
    # Create a boxed summary
    elements.append(Spacer(1, 0.1*inch))
    
    # Summary text with proper formatting (without para tags that cause issues)
    summary_text = f"""
    This document certifies that a comprehensive AI model risk assessment has been conducted
    on <b>{timestamp_str}</b> by <b>DataGuardian Pro</b>.
    
    The assessment evaluated a <b>{model_type}</b> model from <b>{model_source}</b> for privacy risks,
    bias concerns, and explainability issues in accordance with industry best practices and regulatory guidelines.
    
    The analysis identified a total of <b>{len(findings)}</b> findings across multiple risk categories,
    resulting in a risk score of <b>{risk_score}/100</b>.
    """
    
    # Create boxed summary
    summary_style = ParagraphStyle(
        'SummaryText',
        parent=body_style,
        alignment=1,  # Center
        borderWidth=1,
        borderColor=HexColor(BRANDING_COLORS["secondary"]),
        borderPadding=10,
        backColor=HexColor("#F8FAFC"),  # Light background for the box
        spaceBefore=5,
        spaceAfter=15,
    )
    elements.append(Paragraph(summary_text, summary_style))
    
    # Create certification details with a clean, modern table
    cert_data = []
    
    # Title row
    cert_data.append([Paragraph("<b>CERTIFICATION DETAILS</b>",
                     ParagraphStyle('TableHeader', parent=body_style, alignment=1))])
    
    # Details in two-column format
    details = [
        ["Certificate ID", scan_id],
        ["Model Type", model_type],
        ["Security Level", get_security_level(risk_score)],
        ["Certification Date", timestamp_str],
        ["Validity Period", "1 year from issue date"],
    ]
    
    # Add repository information if available
    if model_source == "Repository URL":
        details.append(["Repository URL", scan_data.get('repository_url', 'Not specified')])
        details.append(["Branch", scan_data.get('branch', 'Not specified')])
    
    # Create a nice 2-column layout with alternating colors
    for i, (label, value) in enumerate(details):
        bg_color = "#F8FAFC" if i % 2 == 0 else "#FFFFFF"  # Alternating row colors
        cert_data.append([
            Table(
                [[
                    Paragraph(f"<b>{label}:</b>", body_style),
                    Paragraph(f"{value}", body_style)
                ]], 
                colWidths=[1.5*inch, 4*inch],
                style=TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), HexColor(bg_color)),
                    ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
                    ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ])
            )
        ])
    
    # Assemble the entire certification details table
    cert_table = Table(cert_data, colWidths=[6*inch])
    cert_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 1, HexColor(BRANDING_COLORS["primary"])),
        ('LINEBELOW', (0, 0), (-1, 0), 1, HexColor(BRANDING_COLORS["primary"])),
        ('BACKGROUND', (0, 0), (-1, 0), HexColor(BRANDING_COLORS["primary"])),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ]))
    elements.append(cert_table)
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
    
    # Recommendations section with modern design
    elements.append(Spacer(1, 0.3*inch))
    elements.append(
        Paragraph(
            '<font size="14" color="#4f46e5">Expert Recommendations</font>',
            ParagraphStyle(
                'RecommendationsHeading',
                parent=heading_style,
                alignment=1,  # Center
                spaceBefore=12,
                spaceAfter=10,
            )
        )
    )
    
    # Add visual separator
    elements.append(Spacer(1, 0.1*inch))
    separator = Drawing(400, 10)
    separator.add(Line(
        50, 5, 350, 5, 
        strokeColor=HexColor(BRANDING_COLORS["secondary"]),
        strokeWidth=1
    ))
    elements.append(separator)
    elements.append(Spacer(1, 0.2*inch))
    
    # Generate AI-specific recommendations based on findings
    # Group recommendations by category for a more structured approach
    recommendation_categories = {
        "Privacy & Compliance": [],
        "Model Security": [], 
        "Fairness & Ethics": [],
        "Explainability": [],
        "High Priority Actions": []
    }
    
    # Add privacy recommendations
    if pii_detected:
        recommendation_categories["Privacy & Compliance"].extend([
            "Implement data minimization techniques to remove unnecessary PII from the model",
            "Conduct a comprehensive Data Protection Impact Assessment (DPIA)",
            "Apply differential privacy with appropriate epsilon values for training data"
        ])
    else:
        recommendation_categories["Privacy & Compliance"].append(
            "Continue monitoring for potential PII leakage in model outputs"
        )
    
    # Add bias recommendations
    if bias_detected:
        recommendation_categories["Fairness & Ethics"].extend([
            "Implement algorithmic fairness techniques like adversarial debiasing",
            "Ensure demographically balanced representative training datasets",
            "Apply fairness constraints during model training process"
        ])
    else:
        recommendation_categories["Fairness & Ethics"].append(
            "Maintain bias monitoring processes for future model versions"
        )
    
    # Add explainability recommendations
    if explainability_score < 75:
        recommendation_categories["Explainability"].extend([
            "Implement SHAP or LIME for local explanations of individual predictions",
            "Consider more interpretable model architectures where appropriate",
            "Create model cards documenting training data, performance metrics and limitations"
        ])
    else:
        recommendation_categories["Explainability"].append(
            "Enhance documentation of model decisions for non-technical stakeholders"
        )
    
    # Add security recommendations
    recommendation_categories["Model Security"].extend([
        "Implement model API access controls with proper authentication",
        "Apply rate limiting to prevent model extraction attacks",
        "Establish monitoring for adversarial inputs and unusual query patterns"
    ])
    
    # Add high priority recommendations based on critical/high findings
    high_findings = [f for f in findings if f.get('risk_level', '').lower() in ['high', 'critical']]
    if high_findings:
        for finding in high_findings[:3]:  # Add recommendations for up to 3 high findings
            category = finding.get('category', 'high-risk issue')
            desc = finding.get('description', '')
            recommendation_categories["High Priority Actions"].append(f"Address {category}: {desc}")
    
    # Always add some default recommendations to Model Security category
    recommendation_categories["Model Security"].extend([
        "Maintain current privacy and security controls",
        "Continue monitoring model performance and behavior",
        "Implement a regular model review process"
    ])
    
    # Add recommendations to report by category
    for category, recs in recommendation_categories.items():
        if recs:  # Only show categories with recommendations
            # Category header with modern styling
            category_style = ParagraphStyle(
                'CategoryStyle',
                parent=body_style,
                fontName='Helvetica-Bold',
                fontSize=10,
                textColor=HexColor(BRANDING_COLORS["primary"]),
                spaceBefore=10,
                spaceAfter=5
            )
            elements.append(Paragraph(f"{category}", category_style))
            
            # Recommendations with modern styling
            for i, rec in enumerate(recs, 1):
                bullet_style = ParagraphStyle(
                    'BulletStyle',
                    parent=body_style,
                    leftIndent=15,
                    spaceBefore=2,
                    spaceAfter=2
                )
                elements.append(Paragraph(f"• {rec}", bullet_style))
    
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
        # Use page number but don't reference pageCount which isn't available
        canvas.drawString(inch, 0.5 * inch, f"Page {canvas.getPageNumber()}")
        canvas.drawRightString(7 * inch, 0.5 * inch, "DataGuardian Pro")
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
        # Return empty PDF bytes rather than None to avoid type errors
        return b''

class HorizontalRule(Flowable):
    """Custom flowable to draw a horizontal rule"""
    
    def __init__(self, width=None, thickness=0.5, color=None):
        Flowable.__init__(self)
        # Store a numeric width or None to be calculated later
        self.width = width
        self.use_full_width = width is None
        self.thickness = thickness
        self.color = color or HexColor(BRANDING_COLORS["primary"])
        
    def wrap(self, availWidth, availHeight):
        # Calculate width based on available width if needed
        if self.use_full_width:
            self.width = availWidth
        
        # Make sure width is always an int
        calculated_width = int(self.width) if self.width is not None else int(availWidth)
        calculated_height = int(self.thickness)
        
        # Return tuple of integers
        return (calculated_width, calculated_height)
        
    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 0, self.width, 0)