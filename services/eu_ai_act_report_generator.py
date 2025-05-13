"""
EU AI Act 2025 Report Generator

This module generates detailed PDF reports for EU AI Act 2025 compliance assessments.
It creates professionally formatted reports with sections detailing:
- Risk categorization
- Prohibited practices assessment
- Mandatory requirements for high-risk systems
- GPAI requirements for foundation models
- Compliance recommendations and action plans
"""

import io
import os
import uuid
import logging
import math
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
from reportlab.graphics.shapes import Drawing, Circle, Rect, Line, String, Wedge, Polygon
from reportlab.graphics.charts.barcharts import VerticalBarChart, HorizontalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics import renderPDF

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Company brand colors
BRAND_COLORS = {
    "primary": "#1E88E5",     # Main brand blue
    "secondary": "#26A69A",   # Teal accent
    "accent": "#FF8F00",      # Orange accent
    "critical": "#D32F2F",    # Red for critical issues
    "high": "#F44336",        # Light red for high issues
    "medium": "#FF9800",      # Orange for medium issues
    "low": "#4CAF50",         # Green for low issues
    "info": "#2196F3",        # Blue for info
    "text": "#212121",        # Near black for text
    "background": "#FFFFFF",  # White background
    "lightgray": "#EEEEEE"    # Light gray for alternating rows
}

# Modern color palette for enhanced reports
MODERN_COLORS = {
    "primary": "#1E40AF",     # Deep blue
    "secondary": "#3B82F6",   # Bright blue
    "text": "#1F2937",        # Dark gray
    "light_text": "#6B7280",  # Medium gray
    "critical": "#DC2626",    # Red
    "high": "#F59E0B",        # Amber
    "medium": "#10B981",      # Green
    "low": "#0EA5E9",         # Light blue
    "info": "#6366F1",        # Indigo
    "background": "#F9FAFB",  # Light gray
    "border": "#E5E7EB",      # Border gray
    "highlight": "#EFF6FF"    # Light blue highlight
}

def create_eu_ai_act_report(analysis_results: Dict[str, Any]) -> bytes:
    """
    Generate a PDF report for EU AI Act compliance assessment
    
    Args:
        analysis_results: The analysis results data
        
    Returns:
        PDF report as bytes
    """
    logger.info("Generating EU AI Act 2025 compliance report")
    
    try:
        # Create a buffer to receive PDF data
        buffer = io.BytesIO()
        
        # Create the PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
            title=f"EU AI Act Compliance Report - {analysis_results.get('model_name', 'AI Model')}",
            author="DataGuardian Pro"
        )
        
        # Define modern styles for a clean, visually appealing report
        # Get base styles
        baseStyles = getSampleStyleSheet()
        
        # Create a fresh StyleSheet for modern design
        styles = getSampleStyleSheet()
        
        # Define modern colors
        MODERN_COLORS = {
            "primary": "#1E40AF",     # Deep blue
            "secondary": "#3B82F6",   # Bright blue
            "text": "#1F2937",        # Dark gray
            "light_text": "#6B7280",  # Medium gray
            "critical": "#DC2626",    # Red
            "high": "#F59E0B",        # Amber
            "medium": "#10B981",      # Green
            "low": "#0EA5E9",         # Light blue
            "info": "#6366F1",        # Indigo
            "background": "#F9FAFB",  # Light gray
            "border": "#E5E7EB",      # Border gray
            "highlight": "#EFF6FF"    # Light blue highlight
        }
        
        # Create modern styles for the report
        try:
            # Main heading style
            styles.add(ParagraphStyle(
                name='CustomHeading1',
                fontName='Helvetica-Bold',
                fontSize=20,
                leading=24,
                textColor=HexColor(MODERN_COLORS["primary"]),
                spaceBefore=16,
                spaceAfter=12,
                alignment=0  # Left aligned
            ))
            
            # Subheading style
            styles.add(ParagraphStyle(
                name='CustomHeading2',
                fontName='Helvetica-Bold',
                fontSize=16,
                leading=20,
                textColor=HexColor(MODERN_COLORS["secondary"]),
                spaceBefore=14,
                spaceAfter=10,
                alignment=0  # Left aligned
            ))
            
            # Section heading
            styles.add(ParagraphStyle(
                name='SectionHeading',
                fontName='Helvetica-Bold',
                fontSize=14,
                leading=18,
                textColor=HexColor(MODERN_COLORS["text"]),
                spaceBefore=12,
                spaceAfter=8,
                alignment=0  # Left aligned
            ))
            
            # Standard text
            styles.add(ParagraphStyle(
                name='Normal',
                fontName='Helvetica',
                fontSize=11,
                leading=15,
                textColor=HexColor(MODERN_COLORS["text"]),
                spaceBefore=6,
                spaceAfter=6
            ))
            
            # Bold text
            styles.add(ParagraphStyle(
                name='Bold',
                fontName='Helvetica-Bold',
                fontSize=11,
                leading=15,
                textColor=HexColor(MODERN_COLORS["text"]),
                spaceBefore=6,
                spaceAfter=6
            ))
            
            # Status styles
            styles.add(ParagraphStyle(
                name='Critical',
                fontName='Helvetica-Bold',
                fontSize=11,
                leading=15,
                textColor=HexColor(MODERN_COLORS["critical"])
            ))
            
            styles.add(ParagraphStyle(
                name='Warning',
                fontName='Helvetica-Bold',
                fontSize=11,
                leading=15,
                textColor=HexColor(MODERN_COLORS["high"])
            ))
            
            styles.add(ParagraphStyle(
                name='Info',
                fontName='Helvetica',
                fontSize=11,
                leading=15,
                textColor=HexColor(MODERN_COLORS["info"])
            ))
            
            # Caption style for images and charts
            styles.add(ParagraphStyle(
                name='Caption',
                fontName='Helvetica-Oblique',
                fontSize=10,
                leading=14,
                textColor=HexColor(MODERN_COLORS["light_text"]),
                alignment=1  # Center aligned
            ))
            
        except Exception as style_error:
            logger.warning(f"Error adding modern styles: {str(style_error)}")
        
        # Create story (content)
        story = []
        
        # Add report elements
        _add_report_header(story, styles, analysis_results)
        _add_executive_summary(story, styles, analysis_results)
        _add_risk_categorization(story, styles, analysis_results)
        
        # Add appropriate sections based on risk category
        risk_category = analysis_results.get("risk_category", "minimal_risk")
        
        # Add prohibited practices section if findings exist
        prohibited_findings = analysis_results.get("prohibited_practice_findings", [])
        if prohibited_findings:
            _add_prohibited_practices(story, styles, analysis_results)
        
        # Add mandatory requirements for high-risk systems
        if risk_category in ["high_risk", "prohibited"]:
            _add_mandatory_requirements(story, styles, analysis_results)
        
        # Add GPAI requirements for foundation models
        if risk_category == "general_purpose":
            _add_gpai_requirements(story, styles, analysis_results)
        
        # Add recommendations and action plan
        _add_recommendations(story, styles, analysis_results)
        
        # Add compliance checklist
        _add_compliance_checklist(story, styles, analysis_results)
        
        # Build the PDF
        doc.build(story)
        
        # Get the PDF data
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        # Save a copy to reports directory
        try:
            os.makedirs("reports", exist_ok=True)
            report_filename = f"eu_ai_act_report_{analysis_results.get('analysis_id', uuid.uuid4().hex)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            report_path = os.path.join("reports", report_filename)
            
            with open(report_path, "wb") as f:
                f.write(pdf_bytes)
                
            logger.info(f"EU AI Act report saved to: {report_path}")
            
            # Update analysis results with report path
            analysis_results['report_path'] = report_path
            
        except Exception as save_error:
            logger.error(f"Error saving report to file: {str(save_error)}")
        
        return pdf_bytes
    except Exception as e:
        logger.error(f"Error generating EU AI Act report: {str(e)}")
        # Return empty bytes to avoid breaking the flow
        return b''

def _add_report_header(story, styles, analysis_results):
    """Add modern report header with logo and title"""
    # Create a logo (simple graphical element since we're not using images)
    logo_width = 60
    logo_height = 60
    
    # Create a simple geometric logo with DataGuardian Pro shield design
    logo = Drawing(logo_width, logo_height)
    
    # Shield outline
    shield = Rect(5, 5, 50, 50, fillColor=HexColor(MODERN_COLORS["primary"]), 
                 strokeColor=HexColor(MODERN_COLORS["secondary"]), strokeWidth=1)
    logo.add(shield)
    
    # Shield inner design
    inner_shield = Rect(10, 10, 40, 40, fillColor=HexColor(MODERN_COLORS["secondary"]), 
                       strokeColor=None)
    logo.add(inner_shield)
    
    # Shield icon elements (lock symbol)
    lock_body = Rect(22, 20, 16, 15, fillColor=HexColor(MODERN_COLORS["background"]), 
                    strokeColor=HexColor(MODERN_COLORS["primary"]), strokeWidth=1)
    logo.add(lock_body)
    
    lock_loop = Circle(30, 40, 5, fillColor=HexColor(MODERN_COLORS["background"]), 
                     strokeColor=HexColor(MODERN_COLORS["primary"]), strokeWidth=1)
    logo.add(lock_loop)
    
    # Add some text elements to the logo
    # logo.add(String(15, 25, "DP", fontName="Helvetica-Bold", fontSize=10, 
    #                fillColor=HexColor(MODERN_COLORS["primary"])))
    
    # Title block with modern styling
    title = f"EU AI Act 2025 Compliance Assessment"
    subtitle = f"Model: {analysis_results.get('model_name', 'AI Model')}"
    date_str = datetime.now().strftime("%d %B %Y")
    scan_id = analysis_results.get('analysis_id', 'N/A')
    
    # Create a modern header container
    header_width = int(doc_width(100))
    header_background = Rect(0, 0, header_width, 90, 
                           fillColor=HexColor(MODERN_COLORS["background"]), 
                           strokeColor=None)
    header_drawing = Drawing(header_width, 90)
    header_drawing.add(header_background)
    
    # Add a colored stripe at the bottom
    accent_stripe = Rect(0, 0, header_width, 5, 
                       fillColor=HexColor(MODERN_COLORS["secondary"]), 
                       strokeColor=None)
    header_drawing.add(accent_stripe)
    
    # Create a table for the header with logo
    data = [
        [logo, 
         Paragraph(f'<font name="Helvetica-Bold" size="20" color="{MODERN_COLORS["primary"]}">{title}</font>', styles['Normal']), 
         Paragraph(f'<font size="9" color="{MODERN_COLORS["light_text"]}">DataGuardian Pro</font>', styles['Normal'])],
        [None, 
         Paragraph(f'<font size="14" color="{MODERN_COLORS["secondary"]}">{subtitle}</font>', styles['Normal']), 
         Paragraph(f'<font size="9" color="{MODERN_COLORS["light_text"]}">Report Date: {date_str}<br/>ID: {scan_id}</font>', styles['Normal'])]
    ]
    
    header_table = Table(data, colWidths=[logo_width + 20, doc_width(55), doc_width(25)])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('SPAN', (0, 0), (0, 1)),  # Make logo cell span both rows
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BACKGROUND', (0, 0), (-1, -1), HexColor(MODERN_COLORS["background"])),
    ]))
    
    # Add the header with background to the story
    story.append(header_drawing)
    story.append(header_table)
    
    # Add a description/introduction paragraph
    intro_text = f"""This report presents the assessment of compliance with the European Union's AI Act 2025 requirements
for the AI system named '{analysis_results.get('model_name', 'AI Model')}'. The assessment evaluates the system against 
relevant compliance criteria based on its risk category and intended use."""
    
    story.append(Paragraph(intro_text, styles['Normal']))
    story.append(Spacer(1, 20))

def _add_executive_summary(story, styles, analysis_results):
    """Add executive summary section with visualizations"""
    # Heading
    story.append(Paragraph("Executive Summary", styles['CustomHeading1']))
    
    # Extract key information
    risk_category = analysis_results.get("risk_category", "minimal_risk")
    risk_details = analysis_results.get("risk_category_details", {})
    compliance_score = analysis_results.get("compliance_score", 0)
    prohibited_count = len(analysis_results.get("prohibited_practice_findings", []))
    
    # Create risk category display name
    risk_category_name = {
        "prohibited": "Prohibited AI Practice",
        "high_risk": "High-Risk AI System",
        "general_purpose": "General Purpose AI System",
        "limited_risk": "Limited Risk AI System",
        "minimal_risk": "Minimal Risk AI System"
    }.get(risk_category, "Unclassified")
    
    # Create compliance status text
    compliance_status = "Non-Compliant" if prohibited_count > 0 else (
        "Partially Compliant" if compliance_score < 80 else "Compliant"
    )
    
    # Create compliance status color for visual elements
    compliance_color_code = MODERN_COLORS["critical"] if prohibited_count > 0 else (
        MODERN_COLORS["high"] if compliance_score < 50 else 
        MODERN_COLORS["medium"] if compliance_score < 80 else 
        MODERN_COLORS["low"]
    )
    
    # Create executive summary layout with two columns
    summary_table_data = [
        [
            # Left column: Summary text
            [
                Paragraph(f"This assessment evaluated compliance with EU AI Act 2025 requirements for the AI system '{analysis_results.get('model_name', 'AI Model')}'.", styles['Normal']),
                Spacer(1, 10),
                Paragraph(f"<b>Risk Category:</b> {risk_category_name}", styles['Bold']),
                Paragraph(f"<b>Compliance Score:</b> {compliance_score}%", styles['Bold']),
                Paragraph(f"<b>Compliance Status:</b> <font color='{compliance_color_code}'>{compliance_status}</font>", styles['Bold']),
            ],
            
            # Right column: Compliance donut chart
            _create_compliance_donut_chart(compliance_score, compliance_color_code)
        ]
    ]
    
    # Create two-column layout
    summary_table = Table(summary_table_data, colWidths=[doc_width(60), doc_width(40)])
    summary_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, -1), HexColor(MODERN_COLORS["background"])),
        ('ROUNDEDCORNERS', [5, 5, 5, 5]),
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 15))
    
    # Create key findings section with box
    findings_elements = []
    
    # Add key findings header
    findings_elements.append(Paragraph("<b>Key Findings</b>", styles['SectionHeading']))
    
    # Create a list of findings based on risk category
    prohibited_text = f"{prohibited_count} prohibited practices identified" if prohibited_count > 0 else "No prohibited practices identified"
    
    findings_list = [prohibited_text]
    
    # Add risk-specific findings
    if risk_category in ["high_risk", "prohibited"]:
        mandatory_req = analysis_results.get("mandatory_requirements_findings", [])
        compliant_count = sum(1 for req in mandatory_req if req.get("compliant", False))
        total_count = len(mandatory_req)
        
        findings_list.append(f"{compliant_count} of {total_count} mandatory requirements fulfilled for high-risk AI systems.")
    
    if risk_category == "general_purpose":
        gpai_req = analysis_results.get("gpai_requirements_findings", [])
        compliant_count = sum(1 for req in gpai_req if req.get("compliant", False))
        total_count = len(gpai_req)
        
        findings_list.append(f"{compliant_count} of {total_count} General Purpose AI requirements fulfilled.")
    
    # Add findings list with modern bullet points
    for finding in findings_list:
        findings_elements.append(Paragraph(f"• {finding}", styles['Normal']))
    
    # Add key areas that need attention (if any)
    if compliance_score < 100:
        findings_elements.append(Spacer(1, 10))
        findings_elements.append(Paragraph("<b>Areas Needing Attention:</b>", styles['Bold']))
        
        # Extract areas with low compliance from findings
        all_findings = []
        if risk_category in ["high_risk", "prohibited"]:
            all_findings.extend(analysis_results.get("mandatory_requirements_findings", []))
        if risk_category == "general_purpose":
            all_findings.extend(analysis_results.get("gpai_requirements_findings", []))
        
        # Find non-compliant items
        non_compliant = [f for f in all_findings if not f.get("compliant", False)][:3]  # Show top 3
        
        if non_compliant:
            for item in non_compliant:
                findings_elements.append(
                    Paragraph(f"• <font color='{MODERN_COLORS['high']}'>{item.get('name', 'Requirement')}</font>", 
                             styles['Normal'])
                )
        else:
            findings_elements.append(
                Paragraph("• Minor improvements needed to achieve full compliance", styles['Normal'])
            )
    
    # Create a findings box with background
    findings_table = Table([[findings_elements]], colWidths=[doc_width(100)])
    findings_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor(MODERN_COLORS["highlight"])),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor(MODERN_COLORS["border"])),
        ('ROUNDEDCORNERS', [5, 5, 5, 5]),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
    ]))
    
    story.append(findings_table)
    
    # Add a horizontal line
    story.append(Spacer(1, 20))
    story.append(HorizontalLine())
    story.append(Spacer(1, 10))


def _create_compliance_donut_chart(compliance_score, color_code):
    """Create a donut chart to visualize compliance score"""
    # Chart dimensions
    width = 200
    height = 200
    
    # Create drawing
    drawing = Drawing(width, height)
    
    # Create donut chart - using integers for x,y as required
    donut = Pie()
    donut.x = int(width/2)
    donut.y = int(height/2)
    donut.width = 150
    donut.height = 150
    donut.data = [compliance_score, 100-compliance_score]
    donut.labels = None
    
    # Determine colors based on compliance score
    if compliance_score >= 80:
        fill_color = HexColor(MODERN_COLORS["medium"])  # Green for good
    elif compliance_score >= 50:
        fill_color = HexColor(MODERN_COLORS["high"])  # Amber for medium
    else:
        fill_color = HexColor(MODERN_COLORS["critical"])  # Red for poor
    
    donut.slices[0].fillColor = fill_color
    donut.slices[1].fillColor = HexColor("#E5E7EB")  # Light gray for remaining
    
    # Style settings
    donut.slices.strokeWidth = 0
    donut.simpleLabels = 0
    donut.slices[1].popout = 0
    donut.slices[0].popout = 0
    
    # Create inner circle for donut effect
    inner_circle = Circle(width/2, height/2, 50, fillColor=HexColor('white'), strokeColor=None)
    
    # Add components to drawing
    drawing.add(donut)
    drawing.add(inner_circle)
    
    # Add compliance score text in the center
    score_text = String(width/2, height/2-10, f"{compliance_score}%", 
                      fontName="Helvetica-Bold", fontSize=22, 
                      fillColor=HexColor(MODERN_COLORS["text"]), 
                      textAnchor="middle")
    drawing.add(score_text)
    
    # Add "Compliance" label
    label_text = String(width/2, height/2+15, "Compliance", 
                      fontName="Helvetica", fontSize=12, 
                      fillColor=HexColor(MODERN_COLORS["light_text"]), 
                      textAnchor="middle")
    drawing.add(label_text)
    
    return drawing

def _add_risk_categorization(story, styles, analysis_results):
    """Add risk categorization section with visual elements"""
    # Heading
    story.append(Paragraph("Risk Categorization", styles['CustomHeading1']))
    
    # Extract risk details
    risk_category = analysis_results.get("risk_category", "minimal_risk")
    risk_details = analysis_results.get("risk_category_details", {})
    
    # Calculate risk level for visualization (1-5)
    risk_level_mapping = {
        "minimal_risk": 1,
        "limited_risk": 2,
        "general_purpose": 3,
        "high_risk": 4,
        "prohibited": 5
    }
    risk_level = risk_level_mapping.get(risk_category, 0)
    
    # Create risk category display name and description with modern styling
    risk_category_info = {
        "prohibited": {
            "name": "Prohibited AI Practice",
            "description": "AI systems that are explicitly prohibited under the EU AI Act",
            "color": MODERN_COLORS["critical"],
            "icon": "⚠️"
        },
        "high_risk": {
            "name": "High-Risk AI System",
            "description": "AI systems with significant potential impact on health, safety, or fundamental rights",
            "color": MODERN_COLORS["high"],
            "icon": "⚠️"
        },
        "general_purpose": {
            "name": "General Purpose AI System",
            "description": "AI systems with general capabilities that can serve various functions",
            "color": MODERN_COLORS["secondary"],
            "icon": "🔍"
        },
        "limited_risk": {
            "name": "Limited Risk AI System",
            "description": "AI systems with transparency obligations but less stringent requirements",
            "color": MODERN_COLORS["low"],
            "icon": "ℹ️"
        },
        "minimal_risk": {
            "name": "Minimal Risk AI System",
            "description": "AI systems that pose minimal risk to rights or safety",
            "color": MODERN_COLORS["medium"],
            "icon": "✓"
        }
    }.get(risk_category, {
        "name": "Unclassified",
        "description": "Risk level could not be determined",
        "color": MODERN_COLORS["light_text"],
        "icon": "❓"
    })
    
    # Create a risk visualization
    risk_visualization = _create_risk_meter(risk_level)
    
    # Create a two-column layout for risk info
    risk_info_elements = [
        [
            # Left column: Risk category information
            [
                Paragraph(f"<font color='{risk_category_info['color']}' size='14'><b>{risk_category_info['icon']} {risk_category_info['name']}</b></font>", styles['Bold']),
                Spacer(1, 5),
                Paragraph(f"{risk_category_info['description']}", styles['Normal']),
                Spacer(1, 10),
                
                # Add category-specific implications
                Paragraph("<b>Implications:</b>", styles['SectionHeading']),
                Paragraph({
                    "prohibited": "Systems in this category are prohibited and cannot be deployed in the EU under any circumstances.",
                    "high_risk": "Systems in this category must comply with all mandatory requirements before deployment in the EU.",
                    "general_purpose": "Systems in this category are subject to specific transparency and evaluation requirements.",
                    "limited_risk": "Systems in this category must meet transparency obligations under the EU AI Act.",
                    "minimal_risk": "Systems in this category have minimal compliance requirements under the EU AI Act."
                }.get(risk_category, "Implications could not be determined."), styles['Normal']),
            ],
            
            # Right column: Risk visualization
            risk_visualization
        ]
    ]
    
    # Create the two-column layout
    risk_info_table = Table(risk_info_elements, colWidths=[doc_width(60), doc_width(40)])
    risk_info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    story.append(risk_info_table)
    story.append(Spacer(1, 15))
    
    # Create risk factors section with clean modern styling
    if "risk_factors" in risk_details and risk_details["risk_factors"]:
        # Create elements for the risk factors box
        risk_factor_elements = []
        
        # Add header
        risk_factor_elements.append(Paragraph("<b>Risk Factors</b>", styles['SectionHeading']))
        risk_factor_elements.append(Spacer(1, 5))
        
        # Add confidence level if available
        confidence = risk_details.get("confidence", 0.5)
        risk_factor_elements.append(
            Paragraph(f"<b>Assessment Confidence:</b> {confidence:.0%}", styles['Bold'])
        )
        risk_factor_elements.append(Spacer(1, 10))
        
        # Add risk factors with icons for better visual appearance
        factor_icons = ["🔍", "⚙️", "📊", "🔐", "⚖️"]  # Different icons for variety
        risk_factors = risk_details.get("risk_factors", [])
        
        for i, factor in enumerate(risk_factors):
            # Use a different icon for each factor (cycling if more factors than icons)
            icon = factor_icons[i % len(factor_icons)]
            risk_factor_elements.append(Paragraph(f"{icon} {factor}", styles['Normal']))
            # Add small space between items
            if i < len(risk_factors) - 1:
                risk_factor_elements.append(Spacer(1, 5))
                
        # Create a visual box with a background color
        risk_factors_table = Table([[risk_factor_elements]], colWidths=[doc_width(100)])
        risk_factors_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor(MODERN_COLORS["highlight"])),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor(MODERN_COLORS["border"])),
            ('ROUNDEDCORNERS', [5, 5, 5, 5]),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))
        
        story.append(risk_factors_table)
    
    # Add a horizontal line
    story.append(Spacer(1, 20))
    story.append(HorizontalLine())
    story.append(Spacer(1, 10))


def _create_risk_meter(risk_level):
    """Create a visual risk meter to show the AI system's risk level"""
    # Chart dimensions
    width = 180
    height = 180
    
    # Create drawing
    drawing = Drawing(width, height)
    
    # Background for risk meter (light gray circle)
    background = Circle(width/2, height/2, 70, 
                      fillColor=HexColor("#F3F4F6"), 
                      strokeColor=HexColor("#E5E7EB"), 
                      strokeWidth=1)
    drawing.add(background)
    
    # Risk level labels and colors
    risk_labels = ["Minimal", "Limited", "General\nPurpose", "High", "Prohibited"]
    risk_colors = [
        HexColor(MODERN_COLORS["medium"]),    # Green - minimal
        HexColor(MODERN_COLORS["low"]),       # Blue - limited
        HexColor(MODERN_COLORS["secondary"]), # Blue - general purpose
        HexColor(MODERN_COLORS["high"]),      # Amber - high
        HexColor(MODERN_COLORS["critical"])   # Red - prohibited
    ]
    
    # Calculate angle for risk level (0 = minimal, 270 = prohibited)
    start_angle = 135
    end_angle = 405
    angle_per_level = (end_angle - start_angle) / 5
    
    # Create risk level wedges
    for i in range(5):
        level_start_angle = start_angle + (i * angle_per_level)
        level_end_angle = level_start_angle + angle_per_level
        
        # Create wedge for this risk level (with degrees for angles)
        wedge = Wedge(width/2, height/2, 70,
                     startAngleDegrees=level_start_angle, 
                     endAngleDegrees=level_end_angle,
                     fillColor=risk_colors[i],
                     strokeColor=None)
        drawing.add(wedge)
        
        # Add label for this risk level
        label_angle = level_start_angle + (angle_per_level / 2)
        label_rad = math.radians(label_angle)
        label_x = width/2 + (math.cos(label_rad) * 85)
        label_y = height/2 + (math.sin(label_rad) * 85)
        
        label = String(label_x, label_y, risk_labels[i], 
                     fontName="Helvetica", fontSize=8, 
                     fillColor=HexColor(MODERN_COLORS["text"]),
                     textAnchor="middle")
        drawing.add(label)
    
    # Create inner white circle for gauge
    inner_circle = Circle(width/2, height/2, 50, 
                        fillColor=HexColor('white'), 
                        strokeColor=None)
    drawing.add(inner_circle)
    
    # Add needle to show current risk level
    if risk_level > 0:
        needle_angle = start_angle + ((risk_level - 0.5) * angle_per_level)
        needle_rad = math.radians(needle_angle)
        needle_x = width/2 + (math.cos(needle_rad) * 60)
        needle_y = height/2 + (math.sin(needle_rad) * 60)
        
        # Draw needle
        needle = Line(width/2, height/2, needle_x, needle_y,
                    strokeColor=HexColor(MODERN_COLORS["text"]),
                    strokeWidth=2)
        drawing.add(needle)
        
        # Add center cap
        center_cap = Circle(width/2, height/2, 5, 
                          fillColor=HexColor(MODERN_COLORS["text"]), 
                          strokeColor=None)
        drawing.add(center_cap)
    
    # Add text in center
    category_text = ["", "Minimal Risk", "Limited Risk", "General Purpose", "High Risk", "Prohibited"][min(risk_level, 5)]
    center_text = String(width/2, height/2 - 15, category_text, 
                       fontName="Helvetica-Bold", fontSize=10, 
                       fillColor=HexColor(MODERN_COLORS["text"]),
                       textAnchor="middle")
    drawing.add(center_text)
    
    return drawing

def _add_prohibited_practices(story, styles, analysis_results):
    """Add prohibited practices section"""
    # Heading
    story.append(Paragraph("Prohibited Practices Assessment", styles['Heading1']))
    
    # Get prohibited findings
    prohibited_findings = analysis_results.get("prohibited_practice_findings", [])
    
    if prohibited_findings:
        # Warning text
        story.append(Paragraph("<b>WARNING: Potential prohibited practices detected!</b>", styles['Critical']))
        story.append(Paragraph("The following practices are prohibited under Article 5 of the EU AI Act:", styles['Normal']))
        story.append(Spacer(1, 10))
        
        # Add each prohibited practice finding
        for i, finding in enumerate(prohibited_findings):
            practice_name = finding.get("name", "Unknown prohibited practice")
            description = finding.get("description", "No description available")
            confidence = finding.get("confidence", 0.5)
            matched_patterns = finding.get("matched_patterns", [])
            remediation = finding.get("remediation", "No remediation advice available")
            
            # Add practice details
            story.append(Paragraph(f"<b>{i+1}. {practice_name}</b>", styles['Warning']))
            story.append(Paragraph(f"<b>Description:</b> {description}", styles['Normal']))
            story.append(Paragraph(f"<b>Confidence:</b> {confidence:.0%}", styles['Normal']))
            
            # Add matched patterns if any
            if matched_patterns:
                story.append(Paragraph("<b>Detected indicators:</b>", styles['Normal']))
                for pattern in matched_patterns:
                    story.append(Paragraph(f"• {pattern}", styles['Normal']))
            
            # Add remediation advice
            story.append(Paragraph("<b>Remediation:</b>", styles['Normal']))
            story.append(Paragraph(remediation, styles['Normal']))
            
            story.append(Spacer(1, 10))
    else:
        # No prohibited practices found
        story.append(Paragraph("No prohibited practices were identified in this assessment.", styles['Info']))
    
    # Add a horizontal line
    story.append(HorizontalLine())
    story.append(Spacer(1, 10))

def _add_mandatory_requirements(story, styles, analysis_results):
    """Add mandatory requirements for high-risk systems section"""
    # Heading
    story.append(Paragraph("Mandatory Requirements Assessment", styles['CustomHeading1']))
    story.append(Paragraph("High-risk AI systems must comply with the following mandatory requirements:", styles['Normal']))
    story.append(Spacer(1, 10))
    
    # Get mandatory requirements findings
    mandatory_findings = analysis_results.get("mandatory_requirements_findings", [])
    
    if mandatory_findings:
        # Create a table for requirements
        table_data = [["Requirement", "Status", "Compliance"]]
        
        for finding in mandatory_findings:
            requirement_name = finding.get("name", "Unknown")
            is_compliant = finding.get("compliant", False)
            compliance_pct = finding.get("compliance_percentage", 0)
            
            # Status text and color
            status_text = "Compliant" if is_compliant else "Not Compliant"
            status_color = BRAND_COLORS["low"] if is_compliant else BRAND_COLORS["high"]
            
            # Add row to table
            table_data.append([
                requirement_name,
                Paragraph(f'<font color="{status_color}">{status_text}</font>', styles['Normal']),
                f"{compliance_pct:.0%}"
            ])
        
        # Create the table
        col_widths = [doc_width(50), doc_width(30), doc_width(20)]
        requirements_table = Table(table_data, colWidths=col_widths)
        
        # Style the table
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), toColor(BRAND_COLORS["primary"])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 7),
            ('TOPPADDING', (0, 0), (-1, 0), 7),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, toColor(BRAND_COLORS["lightgray"])),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
        
        # Add alternating row colors
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                table_style.add('BACKGROUND', (0, i), (-1, i), toColor(BRAND_COLORS["lightgray"]))
        
        requirements_table.setStyle(table_style)
        story.append(requirements_table)
        story.append(Spacer(1, 15))
        
        # Add details for non-compliant requirements
        non_compliant = [r for r in mandatory_findings if not r.get("compliant", False)]
        if non_compliant:
            story.append(Paragraph("Detailed Non-Compliance Issues:", styles['Heading2']))
            
            for finding in non_compliant:
                requirement_name = finding.get("name", "Unknown")
                description = finding.get("description", "")
                checks = finding.get("checks", [])
                
                story.append(Paragraph(f"<b>{requirement_name}</b>", styles['Bold']))
                story.append(Paragraph(description, styles['Normal']))
                
                # Add non-compliant checks
                non_compliant_checks = [c for c in checks if not c.get("compliant", False)]
                if non_compliant_checks:
                    story.append(Paragraph("<b>Missing components:</b>", styles['Normal']))
                    for check in non_compliant_checks:
                        check_name = check.get("name", "Unknown check")
                        recommendation = check.get("recommendation", "No recommendation available")
                        story.append(Paragraph(f"• <b>{check_name}:</b> {recommendation}", styles['Normal']))
                
                story.append(Spacer(1, 10))
    else:
        # No findings available
        story.append(Paragraph("No mandatory requirements assessment available.", styles['Info']))
    
    # Add a horizontal line
    story.append(HorizontalLine())
    story.append(Spacer(1, 10))

def _add_gpai_requirements(story, styles, analysis_results):
    """Add GPAI requirements section"""
    # Heading
    story.append(Paragraph("General Purpose AI Requirements", styles['CustomHeading1']))
    story.append(Paragraph("Foundation models and general purpose AI systems must comply with the following requirements:", styles['Normal']))
    story.append(Spacer(1, 10))
    
    # Get GPAI requirements findings
    gpai_findings = analysis_results.get("gpai_requirements_findings", [])
    
    if gpai_findings:
        # Create a table for requirements
        table_data = [["Requirement", "Status", "Compliance"]]
        
        for finding in gpai_findings:
            requirement_name = finding.get("name", "Unknown")
            is_compliant = finding.get("compliant", False)
            compliance_pct = finding.get("compliance_percentage", 0)
            
            # Status text and color
            status_text = "Compliant" if is_compliant else "Not Compliant"
            status_color = BRAND_COLORS["low"] if is_compliant else BRAND_COLORS["high"]
            
            # Add row to table
            table_data.append([
                requirement_name,
                Paragraph(f'<font color="{status_color}">{status_text}</font>', styles['Normal']),
                f"{compliance_pct:.0%}"
            ])
        
        # Create the table
        col_widths = [doc_width(50), doc_width(30), doc_width(20)]
        requirements_table = Table(table_data, colWidths=col_widths)
        
        # Style the table
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), toColor(BRAND_COLORS["secondary"])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 7),
            ('TOPPADDING', (0, 0), (-1, 0), 7),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, toColor(BRAND_COLORS["lightgray"])),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
        
        # Add alternating row colors
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                table_style.add('BACKGROUND', (0, i), (-1, i), toColor(BRAND_COLORS["lightgray"]))
        
        requirements_table.setStyle(table_style)
        story.append(requirements_table)
        story.append(Spacer(1, 15))
        
        # Add details for non-compliant requirements
        non_compliant = [r for r in gpai_findings if not r.get("compliant", False)]
        if non_compliant:
            story.append(Paragraph("Detailed Non-Compliance Issues:", styles['Heading2']))
            
            for finding in non_compliant:
                requirement_name = finding.get("name", "Unknown")
                description = finding.get("description", "")
                checks = finding.get("checks", [])
                
                story.append(Paragraph(f"<b>{requirement_name}</b>", styles['Bold']))
                story.append(Paragraph(description, styles['Normal']))
                
                # Add non-compliant checks
                non_compliant_checks = [c for c in checks if not c.get("compliant", False)]
                if non_compliant_checks:
                    story.append(Paragraph("<b>Missing components:</b>", styles['Normal']))
                    for check in non_compliant_checks:
                        check_name = check.get("name", "Unknown check")
                        recommendation = check.get("recommendation", "No recommendation available")
                        story.append(Paragraph(f"• <b>{check_name}:</b> {recommendation}", styles['Normal']))
                
                story.append(Spacer(1, 10))
    else:
        # No findings available
        story.append(Paragraph("No GPAI requirements assessment available.", styles['Info']))
    
    # Add a horizontal line
    story.append(HorizontalLine())
    story.append(Spacer(1, 10))

def _add_recommendations(story, styles, analysis_results):
    """Add recommendations and action plan section"""
    # Heading
    story.append(Paragraph("Recommendations & Action Plan", styles['CustomHeading1']))
    
    # Get recommendations
    recommendations = analysis_results.get("recommendations", [])
    
    if recommendations:
        # Sort recommendations by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_recommendations = sorted(
            recommendations, 
            key=lambda x: priority_order.get(x.get("priority", "medium"), 99)
        )
        
        # Add each recommendation
        for i, rec in enumerate(sorted_recommendations):
            priority = rec.get("priority", "medium")
            priority_color = {
                "critical": BRAND_COLORS["critical"],
                "high": BRAND_COLORS["high"],
                "medium": BRAND_COLORS["medium"],
                "low": BRAND_COLORS["low"]
            }.get(priority, BRAND_COLORS["info"])
            
            title = rec.get("title", "Unknown recommendation")
            description = rec.get("description", "")
            action_items = rec.get("action_items", [])
            
            # Add recommendation title with priority
            story.append(Paragraph(
                f"<b>{i+1}. {title}</b> <font color='{priority_color}'>({priority.upper()})</font>", 
                styles['Bold']
            ))
            
            # Add description
            story.append(Paragraph(description, styles['Normal']))
            
            # Add action items
            if action_items:
                story.append(Paragraph("<b>Action Items:</b>", styles['Normal']))
                for item in action_items:
                    story.append(Paragraph(f"• {item}", styles['Normal']))
            
            story.append(Spacer(1, 10))
    else:
        # No recommendations available
        story.append(Paragraph("No specific recommendations available.", styles['Info']))
    
    # Add a horizontal line
    story.append(HorizontalLine())
    story.append(Spacer(1, 10))

def _add_compliance_checklist(story, styles, analysis_results):
    """Add compliance checklist section"""
    # Heading
    story.append(Paragraph("EU AI Act Compliance Checklist", styles['CustomHeading1']))
    
    # Get risk category and findings
    risk_category = analysis_results.get("risk_category", "minimal_risk")
    compliance_score = analysis_results.get("compliance_score", 0)
    prohibited_findings = analysis_results.get("prohibited_practice_findings", [])
    mandatory_findings = analysis_results.get("mandatory_requirements_findings", [])
    gpai_findings = analysis_results.get("gpai_requirements_findings", [])
    
    # Create checklist data
    checklist_data = [["Requirement", "Status", "Notes"]]
    
    # No prohibited practices check
    prohibited_status = "Failed" if prohibited_findings else "Passed"
    prohibited_color = BRAND_COLORS["critical"] if prohibited_findings else BRAND_COLORS["low"]
    checklist_data.append([
        "No prohibited practices",
        Paragraph(f'<font color="{prohibited_color}">{prohibited_status}</font>', styles['Normal']),
        f"{len(prohibited_findings)} prohibited practices found" if prohibited_findings else "No prohibited practices detected"
    ])
    
    # Risk-specific checks
    if risk_category in ["high_risk", "prohibited"]:
        # Mandatory requirements for high-risk systems
        for req in mandatory_findings:
            req_name = req.get("name", "Unknown")
            is_compliant = req.get("compliant", False)
            compliance_pct = req.get("compliance_percentage", 0)
            
            status = "Passed" if is_compliant else "Failed"
            color = BRAND_COLORS["low"] if is_compliant else BRAND_COLORS["high"]
            
            checklist_data.append([
                req_name,
                Paragraph(f'<font color="{color}">{status}</font>', styles['Normal']),
                f"Compliance: {compliance_pct:.0%}"
            ])
    
    if risk_category == "general_purpose":
        # GPAI requirements
        for req in gpai_findings:
            req_name = req.get("name", "Unknown")
            is_compliant = req.get("compliant", False)
            compliance_pct = req.get("compliance_percentage", 0)
            
            status = "Passed" if is_compliant else "Failed"
            color = BRAND_COLORS["low"] if is_compliant else BRAND_COLORS["high"]
            
            checklist_data.append([
                req_name,
                Paragraph(f'<font color="{color}">{status}</font>', styles['Normal']),
                f"Compliance: {compliance_pct:.0%}"
            ])
    
    # Create the table
    col_widths = [doc_width(50), doc_width(20), doc_width(30)]
    checklist_table = Table(checklist_data, colWidths=col_widths)
    
    # Style the table
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), toColor(BRAND_COLORS["primary"])),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 7),
        ('TOPPADDING', (0, 0), (-1, 0), 7),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, toColor(BRAND_COLORS["lightgray"])),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])
    
    # Add alternating row colors
    for i in range(1, len(checklist_data)):
        if i % 2 == 0:
            table_style.add('BACKGROUND', (0, i), (-1, i), toColor(BRAND_COLORS["lightgray"]))
    
    checklist_table.setStyle(table_style)
    story.append(checklist_table)
    
    # Add final compliance statement
    story.append(Spacer(1, 15))
    
    if compliance_score >= 80 and not prohibited_findings:
        status_text = "COMPLIANT"
        status_color = BRAND_COLORS["low"]
        details = "This AI system meets the EU AI Act 2025 compliance requirements."
    elif prohibited_findings:
        status_text = "NON-COMPLIANT"
        status_color = BRAND_COLORS["critical"]
        details = "This AI system implements prohibited practices and cannot be deployed in the EU."
    else:
        status_text = "PARTIALLY COMPLIANT"
        status_color = BRAND_COLORS["medium"]
        details = "This AI system requires remediation to meet EU AI Act 2025 compliance requirements."
    
    story.append(Paragraph(
        f"<font color='{status_color}'><b>Overall Status: {status_text}</b></font>", 
        styles['Bold']
    ))
    story.append(Paragraph(details, styles['Normal']))

# Helper class for horizontal lines
class HorizontalLine(Flowable):
    """A horizontal line flowable."""
    def __init__(self, width=None, thickness=1, color=BRAND_COLORS["lightgray"]):
        Flowable.__init__(self)
        self.width = width or 500
        self.thickness = thickness
        self.color = toColor(color)
    
    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 0, self.width, 0)

def doc_width(percent):
    """Calculate width based on percentage of A4 page width"""
    a4_width = A4[0]
    usable_width = a4_width - 144  # minus margins
    return usable_width * percent / 100