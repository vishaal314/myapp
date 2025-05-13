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
        
        # Define styles
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='Heading1',
            parent=styles['Heading1'],
            fontSize=18,
            leading=22,
            textColor=toColor(BRAND_COLORS["primary"]),
            spaceAfter=12
        ))
        styles.add(ParagraphStyle(
            name='Heading2',
            parent=styles['Heading2'],
            fontSize=14,
            leading=18,
            textColor=toColor(BRAND_COLORS["primary"]),
            spaceAfter=8
        ))
        styles.add(ParagraphStyle(
            name='Normal',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=toColor(BRAND_COLORS["text"])
        ))
        styles.add(ParagraphStyle(
            name='Bold',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            fontName='Helvetica-Bold',
            textColor=toColor(BRAND_COLORS["text"])
        ))
        styles.add(ParagraphStyle(
            name='Critical',
            parent=styles['Normal'],
            fontSize=11,
            fontName='Helvetica-Bold',
            textColor=toColor(BRAND_COLORS["critical"])
        ))
        styles.add(ParagraphStyle(
            name='Warning',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            textColor=toColor(BRAND_COLORS["high"])
        ))
        styles.add(ParagraphStyle(
            name='Info',
            parent=styles['Normal'],
            textColor=toColor(BRAND_COLORS["info"])
        ))
        
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
    """Add report header with logo and title"""
    # Title block
    title = f"EU AI Act 2025 Compliance Assessment"
    subtitle = f"Model: {analysis_results.get('model_name', 'AI Model')}"
    date_str = datetime.now().strftime("%d %B %Y")
    
    # Create a table for the header
    data = [
        [Paragraph(f'<font size="16"><b>{title}</b></font>', styles['Normal']), 
         Paragraph(f'<font size="10">DataGuardian Pro</font>', styles['Normal'])],
        [Paragraph(f'<font size="12">{subtitle}</font>', styles['Normal']), 
         Paragraph(f'<font size="10">Report Date: {date_str}</font>', styles['Normal'])]
    ]
    
    header_table = Table(data, colWidths=[doc_width(70), doc_width(30)])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LINEBELOW', (0, -1), (-1, -1), 1, toColor(BRAND_COLORS["primary"])),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    story.append(header_table)
    story.append(Spacer(1, 20))

def _add_executive_summary(story, styles, analysis_results):
    """Add executive summary section"""
    # Heading
    story.append(Paragraph("Executive Summary", styles['Heading1']))
    
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
    
    # Create compliance status color
    compliance_color = BRAND_COLORS["critical"] if prohibited_count > 0 else (
        BRAND_COLORS["high"] if compliance_score < 50 else 
        BRAND_COLORS["medium"] if compliance_score < 80 else 
        BRAND_COLORS["low"]
    )
    
    # Summary text
    summary_paragraphs = [
        Paragraph(f"This report presents the assessment of compliance with EU AI Act 2025 requirements for the AI system '{analysis_results.get('model_name', 'AI Model')}'.", styles['Normal']),
        Spacer(1, 10),
        Paragraph(f"<b>Risk Category:</b> {risk_category_name}", styles['Bold']),
        Paragraph(f"<b>Compliance Score:</b> {compliance_score}%", styles['Bold']),
        Paragraph(f"<b>Compliance Status:</b> <font color='{compliance_color}'>{compliance_status}</font>", styles['Bold']),
        Spacer(1, 10)
    ]
    
    # Add key findings
    prohibited_text = f"{prohibited_count} prohibited practices identified" if prohibited_count > 0 else "No prohibited practices identified"
    summary_paragraphs.append(Paragraph("<b>Key Findings:</b>", styles['Bold']))
    
    # Create a list of findings based on risk category
    findings_list = [
        f"{prohibited_text}."
    ]
    
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
    
    # Add findings list
    for finding in findings_list:
        summary_paragraphs.append(Paragraph(f"• {finding}", styles['Normal']))
    
    # Add all paragraphs to story
    for p in summary_paragraphs:
        story.append(p)
    
    # Add a horizontal line
    story.append(HorizontalLine())
    story.append(Spacer(1, 10))

def _add_risk_categorization(story, styles, analysis_results):
    """Add risk categorization section"""
    # Heading
    story.append(Paragraph("Risk Categorization", styles['Heading1']))
    
    # Extract risk details
    risk_category = analysis_results.get("risk_category", "minimal_risk")
    risk_details = analysis_results.get("risk_category_details", {})
    
    # Create risk category display name and description
    risk_category_info = {
        "prohibited": {
            "name": "Prohibited AI Practice",
            "description": "AI systems that are explicitly prohibited under the EU AI Act",
            "color": BRAND_COLORS["critical"]
        },
        "high_risk": {
            "name": "High-Risk AI System",
            "description": "AI systems with significant potential impact on health, safety, or fundamental rights",
            "color": BRAND_COLORS["high"]
        },
        "general_purpose": {
            "name": "General Purpose AI System",
            "description": "AI systems with general capabilities that can serve various functions",
            "color": BRAND_COLORS["medium"]
        },
        "limited_risk": {
            "name": "Limited Risk AI System",
            "description": "AI systems with transparency obligations but less stringent requirements",
            "color": BRAND_COLORS["low"]
        },
        "minimal_risk": {
            "name": "Minimal Risk AI System",
            "description": "AI systems that pose minimal risk to rights or safety",
            "color": BRAND_COLORS["info"]
        }
    }.get(risk_category, {
        "name": "Unclassified",
        "description": "Risk level could not be determined",
        "color": BRAND_COLORS["info"]
    })
    
    # Risk category text
    risk_category_paragraphs = [
        Paragraph(f"<font color='{risk_category_info['color']}'><b>Risk Category: {risk_category_info['name']}</b></font>", styles['Bold']),
        Paragraph(f"{risk_category_info['description']}", styles['Normal']),
        Spacer(1, 10)
    ]
    
    # Add confidence and factors
    confidence = risk_details.get("confidence", 0.5)
    risk_factors = risk_details.get("risk_factors", [])
    
    risk_category_paragraphs.extend([
        Paragraph(f"<b>Confidence:</b> {confidence:.0%}", styles['Normal']),
        Spacer(1, 5),
        Paragraph("<b>Risk Factors:</b>", styles['Normal'])
    ])
    
    # Add risk factors as bullets
    for factor in risk_factors:
        risk_category_paragraphs.append(Paragraph(f"• {factor}", styles['Normal']))
    
    # Add a note about risk category implications
    risk_category_paragraphs.extend([
        Spacer(1, 10),
        Paragraph("<b>Implications:</b>", styles['Bold'])
    ])
    
    # Add category-specific implications
    implications = {
        "prohibited": "Systems in this category are prohibited and cannot be deployed in the EU under any circumstances.",
        "high_risk": "Systems in this category must comply with all mandatory requirements before deployment in the EU.",
        "general_purpose": "Systems in this category are subject to specific transparency and evaluation requirements.",
        "limited_risk": "Systems in this category must meet transparency obligations under the EU AI Act.",
        "minimal_risk": "Systems in this category have minimal compliance requirements under the EU AI Act."
    }.get(risk_category, "Implications could not be determined.")
    
    risk_category_paragraphs.append(Paragraph(implications, styles['Normal']))
    
    # Add all paragraphs to story
    for p in risk_category_paragraphs:
        story.append(p)
    
    # Add a horizontal line
    story.append(HorizontalLine())
    story.append(Spacer(1, 10))

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
    story.append(Paragraph("Mandatory Requirements Assessment", styles['Heading1']))
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
    story.append(Paragraph("General Purpose AI Requirements", styles['Heading1']))
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
    story.append(Paragraph("Recommendations & Action Plan", styles['Heading1']))
    
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
    story.append(Paragraph("EU AI Act Compliance Checklist", styles['Heading1']))
    
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