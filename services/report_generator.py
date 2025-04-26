import io
import os
import streamlit as st
from typing import Dict, Any, List, Optional
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.colors import HexColor, toColor
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, Flowable, KeepTogether, CondPageBreak, Image, Frame, FrameBreak, NextPageTemplate, PageTemplate
from reportlab.graphics.shapes import Drawing, Circle, Rect, Line, String, Wedge
from reportlab.graphics.charts.barcharts import VerticalBarChart, HorizontalBarChart
from reportlab.graphics.charts.piecharts import Pie, LegendedPie
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics import renderPDF
from reportlab.graphics.widgets.markers import makeMarker
# Import translation utilities
from utils.i18n import get_text, _

class RiskMeter(Flowable):
    """A custom flowable that creates a risk meter/gauge."""
    
    def __init__(self, risk_level, risk_level_for_meter=None, language='en'):
        Flowable.__init__(self)
        self.risk_level = risk_level
        # Use the meter-specific risk level if provided (for language compatibility)
        self.risk_level_for_meter = risk_level_for_meter if risk_level_for_meter else risk_level
        self.language = language
        self.width = 250
        self.height = 100
    
    def draw(self):
        # Drawing with width and height
        d = Drawing(self.width, self.height)
        
        # Background arc
        arc = Wedge(self.width/2, 20, 50, 0, 180, fillColor=colors.lightgrey)
        d.add(arc)
        
        # Risk level indicator (change angle based on risk level)
        angle = 0
        if self.risk_level_for_meter == "Low":
            angle = 45
            indicator_color = colors.green
        elif self.risk_level_for_meter == "Medium":
            angle = 90
            indicator_color = colors.orange
        elif self.risk_level_for_meter == "High":
            angle = 135
            indicator_color = colors.red
        else: # None
            angle = 0
            indicator_color = colors.blue
            
        # Draw the indicator (a small filled circle)
        rad_angle = angle * 3.14159 / 180  # Convert to radians
        x = self.width/2 + 50 * np.cos(rad_angle)
        y = 20 + 50 * np.sin(rad_angle)
        
        # Add indicator needle line
        line = Line(self.width/2, 20, x, y, strokeColor=indicator_color, strokeWidth=2)
        d.add(line)
        
        # Add indicator circle
        circle = Circle(x, y, 5, fillColor=indicator_color, strokeColor=None)
        d.add(circle)
        
        # Add risk labels in appropriate language
        if self.language == 'nl':
            d.add(String(self.width/6, 75, "Laag", fontSize=9, fillColor=colors.green))
            d.add(String(self.width/2, 85, "Gemiddeld", fontSize=9, fillColor=colors.orange))
            d.add(String(4*self.width/5, 75, "Hoog", fontSize=9, fillColor=colors.red))
            risk_text = f"{self.risk_level} Risico"
        else:
            d.add(String(self.width/6, 75, "Low", fontSize=9, fillColor=colors.green))
            d.add(String(self.width/2, 85, "Medium", fontSize=9, fillColor=colors.orange))
            d.add(String(4*self.width/5, 75, "High", fontSize=9, fillColor=colors.red))
            risk_text = f"{self.risk_level} Risk"
        
        # Add risk level text
        d.add(String(self.width/2-20, 10, risk_text, fontSize=12, fillColor=indicator_color))
        
        # Draw the entire drawing
        renderPDF.draw(d, self.canv, 0, 0)

class ComplianceBanner(Flowable):
    """A custom flowable that creates a right banner about GDPR fine protection."""
    
    def __init__(self, compliance_level, language='en'):
        Flowable.__init__(self)
        self.compliance_level = compliance_level
        self.language = language
        self.width = 510  # For US Letter page with margins
        self.height = 70
    
    def draw(self):
        # Drawing with width and height
        d = Drawing(self.width, self.height)
        
        # Banner rectangle
        rect = Rect(0, 0, self.width, self.height, 
                   fillColor=HexColor('#e8f4f8'), 
                   strokeColor=HexColor('#3498db'),
                   strokeWidth=1)
        d.add(rect)
        
        # GDPR shield icon
        shield_x = 40
        shield_y = 35
        shield_width = 30
        shield_height = 40
        
        # Draw shield outline
        shield = Wedge(shield_x, shield_y, shield_width/2, 0, 180, 
                      fillColor=HexColor('#3498db'))
        d.add(shield)
        
        # Draw shield bottom
        rect = Rect(shield_x - shield_width/2, shield_y - shield_height/2, 
                   shield_width, shield_height/2, 
                   fillColor=HexColor('#3498db'),
                   strokeColor=None)
        d.add(rect)
        
        # Add EU stars symbol
        star_color = colors.yellow
        star_radius = 2
        center_x = shield_x
        center_y = shield_y - 5
        
        # Draw a circle of stars
        for i in range(6):
            angle = i * 60 * 3.14159 / 180
            star_x = center_x + 10 * np.cos(angle)
            star_y = center_y + 10 * np.sin(angle)
            star = Circle(star_x, star_y, star_radius, 
                         fillColor=star_color, 
                         strokeColor=None)
            d.add(star)
        
        # Add banner text - translated
        if self.language == 'nl':
            title_text = "AVG (GDPR) Nalevingsbescherming"
        else:
            title_text = "GDPR Compliance Protection"
            
        title = String(shield_x + 50, shield_y + 15, 
                      title_text, 
                      fontSize=14, 
                      fillColor=HexColor('#2c3e50'))
        d.add(title)
        
        # Add subtitle based on compliance level - translated
        if self.language == 'nl':
            if self.compliance_level == "Hoog" or self.compliance_level == "High":
                subtitle_text = "Uw organisatie is goed beschermd tegen mogelijke AVG-boetes"
                subtitle_color = HexColor('#27ae60')  # Green
            elif self.compliance_level == "Gemiddeld" or self.compliance_level == "Medium":
                subtitle_text = "Er bestaat enig risico op AVG-boetes - pak de gemarkeerde problemen aan"
                subtitle_color = HexColor('#f39c12')  # Orange
            else:
                subtitle_text = "Hoog risico op mogelijke AVG-boetes - onmiddellijke actie vereist"
                subtitle_color = HexColor('#e74c3c')  # Red
        else:
            if self.compliance_level == "High":
                subtitle_text = "Your organization is well-protected against potential GDPR fines"
                subtitle_color = HexColor('#27ae60')  # Green
            elif self.compliance_level == "Medium":
                subtitle_text = "Some risk of GDPR fines exists - address highlighted issues"
                subtitle_color = HexColor('#f39c12')  # Orange
            else:
                subtitle_text = "High risk of potential GDPR fines - immediate action required"
                subtitle_color = HexColor('#e74c3c')  # Red
            
        subtitle = String(shield_x + 50, shield_y - 5, 
                         subtitle_text, 
                         fontSize=10, 
                         fillColor=subtitle_color)
        d.add(subtitle)
        
        # Add fine amount - translated
        if self.language == 'nl':
            fine_text_str = "Mogelijke boetes tot €20 miljoen of 4% van de wereldwijde omzet"
        else:
            fine_text_str = "Potential fines up to €20 million or 4% of global revenue"
            
        fine_text = String(shield_x + 50, shield_y - 20, 
                          fine_text_str, 
                          fontSize=8, 
                          fillColor=HexColor('#7f8c8d'))
        d.add(fine_text)
        
        # Draw the entire drawing
        renderPDF.draw(d, self.canv, 0, 0)

class SustainabilityMeter(Flowable):
    """A custom flowable that creates a sustainability compliance meter."""
    
    def __init__(self, sustainability_score, language='en'):
        Flowable.__init__(self)
        self.sustainability_score = min(max(sustainability_score, 0), 100)  # Ensure between 0-100
        self.language = language
        self.width = 250
        self.height = 80
    
    def draw(self):
        # Drawing with width and height
        d = Drawing(self.width, self.height)
        
        # Title with language support
        if self.language == 'nl':
            title_text = "Gegevens Duurzaamheidsindex"
        else:
            title_text = "Data Sustainability Index"
            
        title = String(10, self.height - 15, 
                      title_text, 
                      fontSize=12, 
                      fillColor=HexColor('#2c3e50'))
        d.add(title)
        
        # Background bar
        bar_height = 15
        bar_y = self.height - 40
        background = Rect(10, bar_y, self.width - 20, bar_height, 
                         fillColor=HexColor('#ecf0f1'), 
                         strokeColor=None)
        d.add(background)
        
        # Calculate progress width
        progress_width = (self.width - 20) * (self.sustainability_score / 100)
        
        # Determine color based on score with language support for status text
        if self.sustainability_score >= 75:
            color = HexColor('#27ae60')  # Green
            status = "Uitstekend" if self.language == 'nl' else "Excellent"
        elif self.sustainability_score >= 50:
            color = HexColor('#2ecc71')  # Light green
            status = "Goed" if self.language == 'nl' else "Good"
        elif self.sustainability_score >= 25:
            color = HexColor('#f39c12')  # Orange
            status = "Redelijk" if self.language == 'nl' else "Fair"
        else:
            color = HexColor('#e74c3c')  # Red
            status = "Slecht" if self.language == 'nl' else "Poor"
        
        # Progress bar
        progress = Rect(10, bar_y, progress_width, bar_height, 
                       fillColor=color, 
                       strokeColor=None)
        d.add(progress)
        
        # Score text
        score_text = String(self.width - 30, bar_y + 3, 
                           f"{self.sustainability_score}%", 
                           fontSize=10, 
                           fillColor=colors.white if self.sustainability_score > 50 else colors.black)
        d.add(score_text)
        
        # Status text with language support
        status_prefix = "Status: "
        status_text = String(10, bar_y - 15, 
                            f"{status_prefix}{status}", 
                            fontSize=10, 
                            fillColor=color)
        d.add(status_text)
        
        # Description text with language support
        if self.language == 'nl':
            description_text = "Meet gegevensminimalisatie, bewaartermijnen & verwerkingsefficiëntie"
        else:
            description_text = "Measures data minimization, retention policies & processing efficiency"
            
        description = String(10, bar_y - 30, 
                            description_text, 
                            fontSize=8, 
                            fillColor=HexColor('#7f8c8d'))
        d.add(description)
        
        # Draw the entire drawing
        renderPDF.draw(d, self.canv, 0, 0)

def create_pie_chart(data, title, colors_dict=None):
    """Creates a pie chart drawing"""
    drawing = Drawing(400, 200)
    
    # Create the pie chart
    pie = Pie()
    pie.x = 150
    pie.y = 50
    pie.width = 100
    pie.height = 100
    
    # Set data
    pie.data = list(data.values())
    pie.labels = list(data.keys())
    
    # Set colors based on keys if provided
    if colors_dict:
        pie_colors = []
        for key in data.keys():
            if key in colors_dict:
                pie_colors.append(colors_dict[key])
            else:
                pie_colors.append(toColor(colors.lightblue))
        pie.slices.strokeWidth = 0.5
        pie.slices.strokeColor = colors.white
        pie.slices.fillColor = pie_colors
    
    drawing.add(pie)
    
    # Add title
    title_label = Label()
    title_label.setText(title)
    title_label.x = 200
    title_label.y = 180
    title_label.textAnchor = 'middle'
    title_label.fontSize = 14
    drawing.add(title_label)
    
    # Add legend
    drawing.add(Pie.LegendSwatchMarker())
    
    return drawing

def create_bar_chart(data, title, max_value=None):
    """Creates a horizontal bar chart drawing"""
    drawing = Drawing(400, 200 + 15 * len(data))
    
    # Create the bar chart
    chart = HorizontalBarChart()
    chart.x = 100
    chart.y = 50
    chart.height = 15 * len(data) + 20
    chart.width = 250
    
    # Set data and categories
    chart.data = [list(data.values())]
    chart.categoryAxis.categoryNames = list(data.keys())
    
    # Set max value if provided, otherwise calculate from data
    if max_value:
        chart.valueAxis.valueMax = max_value
    else:
        chart.valueAxis.valueMax = max(data.values()) * 1.1 or 10
    
    # Set the colors based on value
    for i, value in enumerate(data.values()):
        chart.bars[0][i].fillColor = colors.steelblue
    
    # Make it look nicer
    chart.valueAxis.visibleGrid = True
    chart.valueAxis.gridStrokeColor = colors.lightgrey
    chart.valueAxis.visibleAxis = True
    chart.categoryAxis.visibleTicks = False
    chart.categoryAxis.labels.boxAnchor = 'w'
    
    drawing.add(chart)
    
    # Add title
    title_label = Label()
    title_label.setText(title)
    title_label.x = 225
    title_label.y = chart.height + 70
    title_label.textAnchor = 'middle'
    title_label.fontSize = 14
    drawing.add(title_label)
    
    return drawing

def generate_pdf_report(scan_data: Dict[str, Any], 
                   include_details: bool = True,
                   include_charts: bool = True,
                   include_metadata: bool = True,
                   include_recommendations: bool = True,
                   report_format: str = "standard") -> bytes:
    """
    Generate a PDF report for a scan result.
    
    Args:
        scan_data: The scan result data
        include_details: Whether to include detailed findings
        include_charts: Whether to include charts
        include_metadata: Whether to include scan metadata
        include_recommendations: Whether to include recommendations
        report_format: Report format type ("standard", "executive", "detailed", "dpia")
        
    Returns:
        The PDF report as bytes
    """
    return _generate_report_internal(
        scan_data=scan_data,
        include_details=include_details,
        include_charts=include_charts,
        include_metadata=include_metadata,
        include_recommendations=include_recommendations,
        report_format=report_format
    )

def generate_dpia_report(scan_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a comprehensive DPIA report from assessment results.
    This function processes and enriches the DPIA assessment data.
    
    Args:
        scan_data: The DPIA assessment data with scores and findings
        
    Returns:
        Enriched DPIA report data
    """
    # Create a copy of the scan data to avoid modifying the original
    report_data = scan_data.copy()
    
    # Add report generation timestamp
    report_data['report_generated_at'] = datetime.now().isoformat()
    
    # Add report format info
    report_data['report_type'] = 'dpia'
    report_data['report_version'] = '1.0'
    
    # Calculate risk summary if not already present
    if 'risk_summary' not in report_data:
        high_risk = report_data.get('high_risk_count', 0) + report_data.get('file_high_risk_count', 0)
        medium_risk = report_data.get('medium_risk_count', 0) + report_data.get('file_medium_risk_count', 0)
        low_risk = report_data.get('low_risk_count', 0) + report_data.get('file_low_risk_count', 0)
        
        report_data['risk_summary'] = {
            'high': high_risk,
            'medium': medium_risk,
            'low': low_risk,
            'total': high_risk + medium_risk + low_risk
        }
    
    # Add compliance decision info
    report_data['compliance_status'] = 'Compliant' if not report_data.get('dpia_required', False) else 'Action Required'
    
    # Add executive summary
    language = report_data.get('language', 'en')
    if language == 'nl':
        if report_data.get('overall_risk_level') == 'High':
            summary = "Deze beoordeling geeft aan dat er een hoog risico bestaat voor de rechten en vrijheden van betrokkenen. Een formele DPIA is vereist volgens Artikel 35 van de AVG. Onmiddellijke actie is nodig om risico's te beperken en aan de regelgeving te voldoen."
        elif report_data.get('overall_risk_level') == 'Medium':
            summary = "Deze beoordeling toont een gemiddeld risiconiveau voor de rechten en vrijheden van betrokkenen. Hoewel een formele DPIA mogelijk niet vereist is, is het raadzaam om de geïdentificeerde risico's aan te pakken en verdere beoordeling te overwegen."
        else:
            summary = "Deze beoordeling geeft aan dat er een laag risico bestaat voor de rechten en vrijheden van betrokkenen. Een formele DPIA lijkt niet vereist volgens Artikel 35 van de AVG, maar blijf gegevensbeschermingsprincipes toepassen op alle verwerkingsactiviteiten."
    else:
        if report_data.get('overall_risk_level') == 'High':
            summary = "This assessment indicates a high risk to the rights and freedoms of data subjects. A formal DPIA is required under Article 35 of GDPR. Immediate action is needed to mitigate risks and comply with regulations."
        elif report_data.get('overall_risk_level') == 'Medium':
            summary = "This assessment shows a medium level of risk to the rights and freedoms of data subjects. While a formal DPIA may not be required, it is advisable to address the identified risks and consider further assessment."
        else:
            summary = "This assessment indicates a low risk to the rights and freedoms of data subjects. A formal DPIA does not appear to be required under Article 35 of GDPR, but continue to apply data protection principles to all processing activities."
    
    report_data['executive_summary'] = summary
    
    # Generate action plan based on recommendations
    if 'recommendations' in report_data and report_data['recommendations']:
        # Sort recommendations by severity (high to low)
        severity_order = {'High': 0, 'Medium': 1, 'Low': 2}
        sorted_recommendations = sorted(
            report_data['recommendations'], 
            key=lambda x: severity_order.get(x.get('severity', 'Low'), 3)
        )
        
        # Create action plan
        action_plan = []
        for i, rec in enumerate(sorted_recommendations):
            action = {
                'id': i + 1,
                'recommendation': rec.get('description', 'No description'),
                'category': rec.get('category', 'General'),
                'priority': rec.get('severity', 'Low'),
                'status': 'Pending'
            }
            action_plan.append(action)
        
        report_data['action_plan'] = action_plan
    
    return report_data

def generate_report(scan_data: Dict[str, Any], 
                   include_details: bool = True,
                   include_charts: bool = True,
                   include_metadata: bool = True,
                   include_recommendations: bool = True,
                   report_format: Optional[str] = None) -> bytes:
    """
    Generate a PDF report for a scan result.
    Auto-detects scan type and uses appropriate report format.
    
    Args:
        scan_data: The scan result data
        include_details: Whether to include detailed findings
        include_charts: Whether to include charts
        include_metadata: Whether to include scan metadata
        include_recommendations: Whether to include recommendations
        report_format: Optional explicit report format to use (e.g., "ai_model")
        
    Returns:
        The PDF report as bytes
    """
    # Ensure we have valid input
    if not scan_data or not isinstance(scan_data, dict):
        # Create basic error report if scan_data is invalid
        buffer = io.BytesIO()
        
        # Create a PDF document
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Add error title
        story.append(Paragraph("Error: Invalid Scan Data", styles['Title']))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("The scan data provided was invalid or missing. Cannot generate report.", styles['Normal']))
        story.append(Spacer(1, 0.25*inch))
        story.append(Paragraph(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        
        # Build the PDF document
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    try:
        # Add debug logging
        import logging
        
        # Get scan type to determine report format - use provided format if specified
        if report_format:
            scan_type = report_format
            logging.info(f"Using provided report format: {report_format}")
        else:
            scan_type = scan_data.get('scan_type', 'Unknown')
            logging.info(f"Detected scan type: {scan_type}")
        
        # Log key data structure elements for debugging
        logging.info(f"Report generation: scan_data keys: {list(scan_data.keys())}")
        if 'findings' in scan_data:
            logging.info(f"Report generation: found {len(scan_data['findings'])} findings")
        
        # Use appropriate report format based on scan type
        if 'ai_model' in scan_type.lower():
            report_format = "ai_model"
            logging.info("Using AI Model report format")
        elif 'sustainability' in scan_type.lower() or 'github' in scan_type.lower() or 'code efficiency' in scan_type.lower():
            report_format = "sustainability"
            logging.info("Using Sustainability report format")
        else:
            report_format = "standard"
            logging.info("Using standard report format")
            
        return _generate_report_internal(
            scan_data=scan_data,
            include_details=include_details,
            include_charts=include_charts,
            include_metadata=include_metadata,
            include_recommendations=include_recommendations,
            report_format=report_format
        )
    except Exception as e:
        # Create basic error report if something goes wrong
        buffer = io.BytesIO()
        
        # Create a PDF document with error details
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Add error title
        story.append(Paragraph("Error: Report Generation Failed", styles['Title']))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(f"An error occurred while generating the report: {str(e)}", styles['Normal']))
        story.append(Spacer(1, 0.25*inch))
        story.append(Paragraph(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        
        # Build the PDF document
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

def _generate_report_internal(scan_data: Dict[str, Any], 
                   include_details: bool = True,
                   include_charts: bool = True,
                   include_metadata: bool = True,
                   include_recommendations: bool = True,
                   report_format: str = "standard") -> bytes:
    """
    Generate a PDF report for a scan result.
    
    Args:
        scan_data: The scan result data
        include_details: Whether to include detailed findings
        include_charts: Whether to include charts
        include_metadata: Whether to include scan metadata
        include_recommendations: Whether to include recommendations
        
    Returns:
        The PDF report as bytes
    """
    buffer = io.BytesIO()
    
    # Get current language from session state
    current_lang = st.session_state.get('language', 'en')
    
    # Create PDF document with custom page templates
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=72,
        bottomMargin=36
    )
    
    # Define company logo/branding
    # logo_path = "logo.jpg"  # Path to your logo file
    # if os.path.exists(logo_path):
    #     logo = Image(logo_path, width=1.5*inch, height=0.75*inch)
    # else:
    #     logo = None
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=HexColor('#2c3e50'),
        spaceAfter=12,
        alignment=1 # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=HexColor('#3498db'),
        spaceAfter=6,
        spaceBefore=12,
        borderWidth=0,
        borderRadius=5,
        borderPadding=5,
        borderColor=HexColor('#3498db')
    )
    
    subheading_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=HexColor('#2980b9'),
        spaceAfter=6
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceBefore=6,
        spaceAfter=6
    )
    
    # Custom styles
    warning_style = ParagraphStyle(
        'Warning',
        parent=normal_style,
        backgroundColor=HexColor('#fff3cd'),
        textColor=HexColor('#856404'),
        borderColor=HexColor('#ffeeba'),
        borderWidth=1,
        borderRadius=5,
        borderPadding=5
    )
    
    danger_style = ParagraphStyle(
        'Danger',
        parent=normal_style,
        backgroundColor=HexColor('#f8d7da'),
        textColor=HexColor('#721c24'),
        borderColor=HexColor('#f5c6cb'),
        borderWidth=1,
        borderRadius=5,
        borderPadding=5
    )
    
    info_style = ParagraphStyle(
        'Info',
        parent=normal_style,
        backgroundColor=HexColor('#d1ecf1'),
        textColor=HexColor('#0c5460'),
        borderColor=HexColor('#bee5eb'),
        borderWidth=1,
        borderRadius=5,
        borderPadding=5
    )
    
    # Content elements
    elements = []
    
    # Title with company name - use translation
    elements.append(Paragraph(_('app.title', 'DataGuardian Pro'), title_style))
    
    # Subtitle with translation based on language
    if report_format == "ai_model":
        if current_lang == 'nl':
            subtitle = _('report.subtitle.ai_model', 'AI Model Risico Analyse Rapport')
        else:
            subtitle = _('report.subtitle.ai_model', 'AI Model Risk Analysis Report')
    else:
        if current_lang == 'nl':
            subtitle = _('report.subtitle', 'GDPR Compliance Scan Rapport')
        else:
            subtitle = _('report.subtitle', 'GDPR Compliance Scan Report')
    elements.append(Paragraph(subtitle, subheading_style))
    
    # Current date with nice formatting - localized date format
    if current_lang == 'nl':
        # Dutch date format
        current_date = datetime.now().strftime('%d %B %Y %H:%M')
        date_prefix = _('report.generated_on', 'Gegenereerd op:')
    else:
        # English date format
        current_date = datetime.now().strftime('%B %d, %Y %H:%M')
        date_prefix = _('report.generated_on', 'Generated on:')
        
    date_style = ParagraphStyle(
        'DateStyle', 
        parent=normal_style,
        alignment=1, # Center
        textColor=HexColor('#7f8c8d')
    )
    elements.append(Paragraph(f"{date_prefix} {current_date}", date_style))
    elements.append(Spacer(1, 24))
    
    # Scan ID with badge-like styling
    scan_id = scan_data.get('scan_id', 'Unknown')
    scan_date = datetime.now().strftime('%Y%m%d')
    scan_type = scan_data.get('scan_type', 'Unknown')
    
    # Create a fancy scan ID display
    display_scan_id = f"{scan_type[:3].upper()}-{scan_date}-{scan_id[:6]}"
    
    scan_id_style = ParagraphStyle(
        'ScanIdStyle',
        parent=normal_style,
        alignment=1, # Center
        backgroundColor=HexColor('#e8f4f8'),
        borderColor=HexColor('#b8daff'),
        borderWidth=1,
        borderPadding=5,
        borderRadius=5
    )
    
    # Translate scan ID label based on language
    scan_id_label = _('report.scan_id', 'Scan ID')
    elements.append(Paragraph(f"{scan_id_label}: {display_scan_id}", scan_id_style))
    elements.append(Spacer(1, 24))
    
    # Executive Summary - styled as a highlight box with translation
    if current_lang == 'nl':
        exec_summary_title = _('report.executive_summary', 'Samenvatting')
    else:
        exec_summary_title = _('report.executive_summary', 'Executive Summary')
    elements.append(Paragraph(exec_summary_title, heading_style))
    
    # Summary data
    scan_type = scan_data.get('scan_type', 'Unknown')
    region = scan_data.get('region', 'Unknown')
    timestamp = scan_data.get('timestamp', 'Unknown')
    
    # For AI Model reports, calculate counts directly from findings
    if report_format == "ai_model" and 'findings' in scan_data:
        # Count findings by risk level
        findings = scan_data.get('findings', [])
        high_risk = 0
        medium_risk = 0
        low_risk = 0
        
        # Import logging for debugging
        import logging
        logging.info(f"Calculating AI model risk counts from {len(findings)} findings")
        
        for finding in findings:
            risk_level = finding.get('risk_level', 'low')
            # Ensure risk_level is a string and normalized to lowercase for comparison
            if isinstance(risk_level, str):
                risk_level_lower = risk_level.lower()
            else:
                risk_level_lower = str(risk_level).lower()
                
            # Count based on risk level
            if risk_level_lower == 'high':
                high_risk += 1
            elif risk_level_lower == 'medium':
                medium_risk += 1
            else:
                low_risk += 1
                
        # Set total findings count
        total_pii = len(findings)
        
        # Update the scan_data with calculated counts
        scan_data['total_pii_found'] = total_pii
        scan_data['high_risk_count'] = high_risk
        scan_data['medium_risk_count'] = medium_risk
        scan_data['low_risk_count'] = low_risk
        
        logging.info(f"Calculated AI model counts - Total: {total_pii}, High: {high_risk}, Medium: {medium_risk}, Low: {low_risk}")
    else:
        # Use existing counts from the scan data
        total_pii = scan_data.get('total_pii_found', 0)
        high_risk = scan_data.get('high_risk_count', 0)
        medium_risk = scan_data.get('medium_risk_count', 0)
        low_risk = scan_data.get('low_risk_count', 0)
    
    # Get URL information
    url = scan_data.get('url', scan_data.get('domain', 'Not available'))
    
    if timestamp != 'Unknown':
        try:
            if current_lang == 'nl':
                # Dutch date format
                timestamp = datetime.fromisoformat(timestamp).strftime('%d-%m-%Y %H:%M:%S')
            else:
                timestamp = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        except:
            pass
    
    # Executive summary text with translation
    if report_format == "ai_model":
        # Extract AI model specific data
        model_source = scan_data.get('model_source', 'Unknown')
        model_name = scan_data.get('model_name', scan_data.get('repository_path', 'Unknown Model'))
        
        if current_lang == 'nl':
            summary_text = f"""
            Dit rapport presenteert de bevindingen van een AI Model risico analyse uitgevoerd op <b>{model_name}</b> 
            van bron <b>{model_source}</b> op <b>{timestamp}</b>. De scan heeft in totaal <b>{total_pii}</b> instanties van 
            persoonlijk identificeerbare informatie (PII) geïdentificeerd met <b>{high_risk}</b> hoog-risico items.
            """
        else:
            summary_text = f"""
            This report presents the findings of an AI Model risk analysis conducted on <b>{model_name}</b> 
            from source <b>{model_source}</b> on <b>{timestamp}</b>. The scan identified a total of <b>{total_pii}</b> instances of 
            personally identifiable information (PII) with <b>{high_risk}</b> high-risk items.
            """
    else:
        if current_lang == 'nl':
            summary_text = f"""
            Dit rapport presenteert de bevindingen van een GDPR compliance scan uitgevoerd op <b>{url}</b> 
            op <b>{timestamp}</b>. De scan heeft in totaal <b>{total_pii}</b> instanties van 
            persoonlijk identificeerbare informatie (PII) geïdentificeerd met <b>{high_risk}</b> hoog-risico items.
            """
        else:
            summary_text = f"""
            This report presents the findings of a GDPR compliance scan conducted on <b>{url}</b> 
            on <b>{timestamp}</b>. The scan identified a total of <b>{total_pii}</b> instances of 
            personally identifiable information (PII) with <b>{high_risk}</b> high-risk items.
            """
    
    elements.append(Paragraph(summary_text, info_style))
    elements.append(Spacer(1, 12))
    
    # Summary table with modern styling
    # Create data for the summary table with nicer labels - translated
    if report_format == "ai_model":
        # Extract AI model specific data
        model_source = scan_data.get('model_source', 'Unknown')
        model_name = scan_data.get('model_name', scan_data.get('repository_path', 'Unknown Model'))
        repository_url = scan_data.get('repository_url', 'N/A')
        repository_path = scan_data.get('repository_path', 'N/A')
        
        if current_lang == 'nl':
            summary_data = [
                [_('report.scan_type', 'Scan Type'), scan_type],
                [_('report.region', 'Regio'), region],
                [_('report.date_time', 'Datum & Tijd'), timestamp],
                [_('report.model_source', 'Model Bron'), model_source],
                [_('report.model_name', 'Model Naam'), model_name],
                [_('report.repository_url', 'Repository URL'), repository_url if repository_url != 'N/A' else 'Niet beschikbaar'],
                [_('report.repository_path', 'Repository Pad'), repository_path if repository_path != 'N/A' else 'Niet beschikbaar'],
                [_('report.total_pii', 'Totaal PII Items Gevonden'), str(total_pii)],
                [_('report.high_risk', 'Hoog Risico Items'), str(high_risk)],
                [_('report.medium_risk', 'Gemiddeld Risico Items'), str(medium_risk)],
                [_('report.low_risk', 'Laag Risico Items'), str(low_risk)]
            ]
        else:
            summary_data = [
                [_('report.scan_type', 'Scan Type'), scan_type],
                [_('report.region', 'Region'), region],
                [_('report.date_time', 'Date & Time'), timestamp],
                [_('report.model_source', 'Model Source'), model_source],
                [_('report.model_name', 'Model Name'), model_name],
                [_('report.repository_url', 'Repository URL'), repository_url if repository_url != 'N/A' else 'Not available'],
                [_('report.repository_path', 'Repository Path'), repository_path if repository_path != 'N/A' else 'Not available'],
                [_('report.total_pii', 'Total PII Items Found'), str(total_pii)],
                [_('report.high_risk', 'High Risk Items'), str(high_risk)],
                [_('report.medium_risk', 'Medium Risk Items'), str(medium_risk)],
                [_('report.low_risk', 'Low Risk Items'), str(low_risk)]
            ]
    else:
        if current_lang == 'nl':
            summary_data = [
                [_('report.scan_type', 'Scan Type'), scan_type],
                [_('report.region', 'Regio'), region],
                [_('report.date_time', 'Datum & Tijd'), timestamp],
                [_('report.scanned_url', 'Gescande URL/Domein'), url],
                [_('report.total_pii', 'Totaal PII Items Gevonden'), str(total_pii)],
                [_('report.high_risk', 'Hoog Risico Items'), str(high_risk)],
                [_('report.medium_risk', 'Gemiddeld Risico Items'), str(medium_risk)],
                [_('report.low_risk', 'Laag Risico Items'), str(low_risk)]
            ]
        else:
            summary_data = [
                [_('report.scan_type', 'Scan Type'), scan_type],
                [_('report.region', 'Region'), region],
                [_('report.date_time', 'Date & Time'), timestamp],
                [_('report.scanned_url', 'Scanned URL/Domain'), url],
                [_('report.total_pii', 'Total PII Items Found'), str(total_pii)],
                [_('report.high_risk', 'High Risk Items'), str(high_risk)],
                [_('report.medium_risk', 'Medium Risk Items'), str(medium_risk)],
                [_('report.low_risk', 'Low Risk Items'), str(low_risk)]
            ]
    
    # Create a more visually appealing table
    summary_table = Table(summary_data, colWidths=[150, 300])
    
    # Define table style based on report format
    if report_format == "ai_model":
        table_style = [
            # Header row styling
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#f2f9fe')),
            ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#2c3e50')),
            # Content styling
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#dfe6e9')),
            # Highlight certain rows
            ('BACKGROUND', (1, 3), (1, 6), HexColor('#e3f2fd')),  # Model info rows
            ('BACKGROUND', (1, 7), (1, 7), HexColor('#eaf2f8')),  # Total PII row
            # Risk level colors
            ('BACKGROUND', (1, 8), (1, 8), HexColor('#fadbd8')),  # High risk row
            ('BACKGROUND', (1, 9), (1, 9), HexColor('#fef9e7')),  # Medium risk row
            ('BACKGROUND', (1, 10), (1, 10), HexColor('#e9f7ef')),  # Low risk row
        ]
    else:
        table_style = [
            # Header row styling
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#f2f9fe')),
            ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#2c3e50')),
            # Content styling
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#dfe6e9')),
            # Highlight certain rows
            ('BACKGROUND', (1, 4), (1, 4), HexColor('#eaf2f8')),  # Total PII row
            # Risk level colors
            ('BACKGROUND', (1, 5), (1, 5), HexColor('#fadbd8')),  # High risk row
            ('BACKGROUND', (1, 6), (1, 6), HexColor('#fef9e7')),  # Medium risk row
            ('BACKGROUND', (1, 7), (1, 7), HexColor('#e9f7ef')),  # Low risk row
        ]
    
    summary_table.setStyle(TableStyle(table_style))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 20))
    
    # Risk assessment section with visual indicator and GDPR fine protection banner
    # Translate risk assessment title
    if current_lang == 'nl':
        risk_assessment_title = _('report.risk_assessment', 'Risicobeoordeling')
    else:
        risk_assessment_title = _('report.risk_assessment', 'Risk Assessment')
    elements.append(Paragraph(risk_assessment_title, heading_style))
    
    # Determine overall risk level with appropriate translations
    if high_risk > 10:
        if current_lang == 'nl':
            risk_level = "Hoog"
            risk_level_for_meter = "High"  # Keep English for the meter component
            compliance_level = "Laag"
            risk_text = "Deze scan heeft een groot aantal hoog-risico PII-items geïdentificeerd. Onmiddellijke actie wordt aanbevolen om GDPR-naleving te waarborgen en gevoelige gegevens te beschermen."
        else:
            risk_level = "High"
            risk_level_for_meter = "High"
            compliance_level = "Low"
            risk_text = "This scan has identified a high number of high-risk PII items. Immediate action is recommended to ensure GDPR compliance and protect sensitive data."
        sustainability_score = 20  # Low sustainability score due to high risk
    elif high_risk > 0:
        if current_lang == 'nl':
            risk_level = "Gemiddeld"
            risk_level_for_meter = "Medium"  # Keep English for the meter component
            compliance_level = "Gemiddeld"
            risk_text = "Deze scan heeft enkele hoog-risico PII-items geïdentificeerd die direct moeten worden aangepakt om doorlopende GDPR-naleving te waarborgen."
        else:
            risk_level = "Medium"
            risk_level_for_meter = "Medium"
            compliance_level = "Medium"
            risk_text = "This scan has identified some high-risk PII items that should be addressed promptly to ensure ongoing GDPR compliance."
        sustainability_score = 50  # Medium sustainability score
    elif total_pii > 0:
        if current_lang == 'nl':
            risk_level = "Laag"
            risk_level_for_meter = "Low"  # Keep English for the meter component
            compliance_level = "Hoog"
            risk_text = "Deze scan heeft PII-items geïdentificeerd, maar geen daarvan is geclassificeerd als hoog risico. Bekijk de items voor GDPR-naleving, maar er is geen dringende actie vereist."
        else:
            risk_level = "Low"
            risk_level_for_meter = "Low"
            compliance_level = "High"
            risk_text = "This scan has identified PII items, but none are classified as high risk. Review the items for GDPR compliance, but no urgent action is required."
        sustainability_score = 75  # Good sustainability score
    else:
        if current_lang == 'nl':
            risk_level = "Geen"
            risk_level_for_meter = "None"  # Keep English for the meter component
            compliance_level = "Hoog"
            risk_text = "Er zijn geen PII-items gevonden in deze scan. Blijf monitoren om GDPR-naleving te behouden."
        else:
            risk_level = "None"
            risk_level_for_meter = "None"
            compliance_level = "High"
            risk_text = "No PII items were found in this scan. Continue monitoring to maintain GDPR compliance."
        sustainability_score = 90  # Excellent sustainability score
    
    # Add GDPR fine protection banner with language support
    gdpr_banner = ComplianceBanner(compliance_level, language=current_lang)
    elements.append(gdpr_banner)
    elements.append(Spacer(1, 12))
    
    # Add custom risk meter visual with language support
    # Make sure we use proper language parameter for the components to determine labels
    risk_meter = RiskMeter(risk_level, risk_level_for_meter, language=current_lang)
    elements.append(risk_meter)
    elements.append(Spacer(1, 12))
    
    # Risk level paragraph with styled text
    elements.append(Paragraph(risk_text, normal_style))
    elements.append(Spacer(1, 12))
    
    # Add sustainability compliance section - translated
    if current_lang == 'nl':
        sustainability_title = _('report.sustainability_compliance', 'Gegevens Duurzaamheid Naleving')
    else:
        sustainability_title = _('report.sustainability_compliance', 'Data Sustainability Compliance')
    elements.append(Paragraph(sustainability_title, subheading_style))
    elements.append(Spacer(1, 6))
    
    # Add description of what sustainability means in this context - translated
    if current_lang == 'nl':
        sustainability_desc = """
        Gegevensduurzaamheid meet hoe efficiënt uw organisatie persoonlijke gegevens beheert in overeenstemming met de AVG-principes 
        van gegevensminimalisatie, bewaartermijnen en doelbinding. Een hogere score duidt op betere 
        langetermijnpraktijken voor gegevensbeheer.
        """
    else:
        sustainability_desc = """
        Data sustainability measures how efficiently your organization manages personal data in compliance with GDPR principles of 
        data minimization, storage limitation, and purpose limitation. A higher score indicates better long-term data governance practices.
        """
    elements.append(Paragraph(sustainability_desc, normal_style))
    elements.append(Spacer(1, 6))
    
    # Add the sustainability meter with language support
    sustainability_meter = SustainabilityMeter(sustainability_score, language=current_lang)
    elements.append(sustainability_meter)
    elements.append(Spacer(1, 12))
    
    # Include detailed findings if requested
    if include_details:
        elements.append(PageBreak())
        
        # Translate detailed findings heading
        if current_lang == 'nl':
            detailed_findings_title = _('report.detailed_findings', 'Gedetailleerde Bevindingen')
        else:
            detailed_findings_title = _('report.detailed_findings', 'Detailed Findings')
        elements.append(Paragraph(detailed_findings_title, heading_style))
        
        # For AI Model reports, display findings from the findings array directly
        if report_format == "ai_model" and 'findings' in scan_data and scan_data['findings']:
            # Create a table for AI model findings
            ai_findings = scan_data['findings']
            ai_finding_items = []
            
            # Log findings for debugging purposes
            import logging
            logging.info(f"Processing AI model findings for report. Found {len(ai_findings)} findings.")
            
            for finding in ai_findings:
                # Translate risk level for display if needed
                original_risk_level = finding.get('risk_level', 'low')
                
                # Ensure risk_level is lowercase for consistent comparison
                if isinstance(original_risk_level, str):
                    original_risk_level = original_risk_level.lower()
                
                if current_lang == 'nl' and original_risk_level in ['high', 'medium', 'low']:
                    if original_risk_level == 'high':
                        displayed_risk_level = 'Hoog'
                    elif original_risk_level == 'medium':
                        displayed_risk_level = 'Gemiddeld'
                    else:
                        displayed_risk_level = 'Laag'
                else:
                    # Convert to title case for better display
                    if isinstance(original_risk_level, str):
                        displayed_risk_level = original_risk_level.title()
                    else:
                        displayed_risk_level = str(original_risk_level).title()
                
                # Create a data row for this finding
                finding_data = [
                    finding.get('type', 'Unknown'),
                    finding.get('category', 'Unknown'),
                    finding.get('description', 'Unknown'),
                    finding.get('location', 'Unknown'),
                    displayed_risk_level
                ]
                ai_finding_items.append(finding_data)
                
                # Log finding details for debugging
                logging.info(f"Processing finding: {finding.get('type', 'Unknown')} - {displayed_risk_level}")
            
            if ai_finding_items:
                # Create detailed findings table with translated headers
                if current_lang == 'nl':
                    table_headers = ['Type', 'Categorie', 'Beschrijving', 'Locatie', 'Risiconiveau']
                else:
                    table_headers = ['Type', 'Category', 'Description', 'Location', 'Risk Level']
                    
                detailed_data = [table_headers]
                detailed_data.extend(ai_finding_items)
                
                # Create a properly sized table for AI model findings
                detailed_table = Table(detailed_data, colWidths=[80, 80, 180, 80, 50])
                
                # Define row styles based on risk level
                row_styles = []
                for i, item in enumerate(ai_finding_items, 1):  # Starting from 1 to account for header
                    risk_level = item[4]
                    # Check for both Dutch and English risk levels
                    if risk_level in ['High', 'Hoog']:
                        bg_color = colors.pink
                    elif risk_level in ['Medium', 'Gemiddeld']:
                        bg_color = colors.lightgoldenrodyellow
                    else:  # Low or Laag
                        bg_color = colors.white
                    
                    row_styles.append(('BACKGROUND', (0, i), (-1, i), bg_color))
                
                # Apply table styles
                table_style = [
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),  # Smaller font for detailed table
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP')
                ]
                
                # Add risk-based row styles
                table_style.extend(row_styles)
                
                detailed_table.setStyle(TableStyle(table_style))
                
                elements.append(detailed_table)
            else:
                # Translate "No detailed findings" message
                if current_lang == 'nl':
                    no_findings_msg = "Geen gedetailleerde bevindingen beschikbaar."
                else:
                    no_findings_msg = "No detailed findings available."
                elements.append(Paragraph(no_findings_msg, normal_style))
        
        # For standard reports, extract PII items from the detailed_results structure
        elif 'detailed_results' in scan_data and scan_data['detailed_results']:
            # Extract all PII items from all files
            all_pii_items = []
            for file_result in scan_data['detailed_results']:
                file_name = file_result.get('file_name', 'Unknown')
                
                for pii_item in file_result.get('pii_found', []):
                    # Translate risk level for display if needed
                    original_risk_level = pii_item.get('risk_level', 'Unknown')
                    if current_lang == 'nl' and original_risk_level in ['High', 'Medium', 'Low']:
                        if original_risk_level == 'High':
                            displayed_risk_level = 'Hoog'
                        elif original_risk_level == 'Medium':
                            displayed_risk_level = 'Gemiddeld'
                        else:
                            displayed_risk_level = 'Laag'
                    else:
                        displayed_risk_level = original_risk_level
                    
                    pii_item_data = [
                        file_name,
                        pii_item.get('type', 'Unknown'),
                        pii_item.get('value', 'Unknown'),
                        pii_item.get('location', 'Unknown'),
                        displayed_risk_level
                    ]
                    all_pii_items.append(pii_item_data)
            
            if all_pii_items:
                # Create detailed findings table with translated headers
                if current_lang == 'nl':
                    table_headers = ['Bestand', 'PII Type', 'Waarde', 'Locatie', 'Risiconiveau']
                else:
                    table_headers = ['File', 'PII Type', 'Value', 'Location', 'Risk Level']
                    
                detailed_data = [table_headers]
                detailed_data.extend(all_pii_items)
                
                detailed_table = Table(detailed_data, colWidths=[80, 80, 150, 80, 80])
                
                # Define row styles based on risk level
                row_styles = []
                for i, item in enumerate(all_pii_items, 1):  # Starting from 1 to account for header
                    risk_level = item[4]
                    # Check for both Dutch and English risk levels
                    if risk_level in ['High', 'Hoog']:
                        bg_color = colors.pink
                    elif risk_level in ['Medium', 'Gemiddeld']:
                        bg_color = colors.lightgoldenrodyellow
                    else:  # Low or Laag
                        bg_color = colors.white
                    
                    row_styles.append(('BACKGROUND', (0, i), (-1, i), bg_color))
                
                # Apply table styles
                table_style = [
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),  # Smaller font for detailed table
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP')
                ]
                
                # Add risk-based row styles
                table_style.extend(row_styles)
                
                detailed_table.setStyle(TableStyle(table_style))
                
                elements.append(detailed_table)
            else:
                # Translate "No detailed findings" message
                if current_lang == 'nl':
                    no_findings_msg = "Geen gedetailleerde bevindingen beschikbaar."
                else:
                    no_findings_msg = "No detailed findings available."
                elements.append(Paragraph(no_findings_msg, normal_style))
        else:
            # Translate "No detailed findings" message
            if current_lang == 'nl':
                no_findings_msg = "Geen gedetailleerde bevindingen beschikbaar."
            else:
                no_findings_msg = "No detailed findings available."
            elements.append(Paragraph(no_findings_msg, normal_style))
    
    # Include recommendations if requested
    if include_recommendations:
        elements.append(PageBreak())
        
        # Translate recommendations heading
        if current_lang == 'nl':
            recommendations_title = _('report.recommendations', 'Aanbevelingen & Volgende Stappen')
        else:
            recommendations_title = _('report.recommendations', 'Recommendations & Next Steps')
        elements.append(Paragraph(recommendations_title, heading_style))
        
        # General recommendations with translation
        if report_format == "ai_model":
            # AI Model specific recommendations
            if current_lang == 'nl':
                recommendations = [
                    "Zorg voor een juiste rechtsgrond voor het verwerken van alle geïdentificeerde PII in AI-modellen.",
                    "Documenteer het gebruik van persoonlijke gegevens in modeltraining zoals vereist door AVG artikel 30.",
                    "Implementeer regelmatige audits van AI-modellen om onbedoelde persoonlijke gegevensverwerking te detecteren.",
                    "Pas gegevensminimalisatie toe in trainingsgegevens om GDPR-naleving voor AI-systemen te waarborgen.",
                    "Overweeg synthetische gegevens of gepseudonimiseerde datasets voor toekomstige modelontwikkeling."
                ]
            else:
                recommendations = [
                    "Ensure proper legal basis for processing all identified PII in AI models.",
                    "Document the use of personal data in model training as required by GDPR Article 30.",
                    "Implement regular audits of AI models to detect unintended personal data processing.",
                    "Apply data minimization in training data to ensure GDPR compliance for AI systems.",
                    "Consider synthetic data or pseudonymized datasets for future model development."
                ]
        else:
            # Standard recommendations
            if current_lang == 'nl':
                recommendations = [
                    "Zorg voor een juiste rechtsgrond voor het verwerken van alle geïdentificeerde PII.",
                    "Documenteer alle verwerkingsactiviteiten zoals vereist door AVG artikel 30.",
                    "Evalueer het beleid voor gegevensbewaring om ervoor te zorgen dat PII niet langer dan nodig wordt bewaard.",
                    "Implementeer passende technische en organisatorische maatregelen om PII te beveiligen."
                ]
            else:
                recommendations = [
                    "Ensure you have proper legal basis for processing all identified PII.",
                    "Document all processing activities as required by GDPR Article 30.",
                    "Review data retention policies to ensure PII is not kept longer than necessary.",
                    "Implement appropriate technical and organizational measures to secure PII."
                ]
        
        for recommendation in recommendations:
            elements.append(Paragraph(f"• {recommendation}", normal_style))
        
        elements.append(Spacer(1, 12))
        
        # Risk-specific recommendations with translation
        if high_risk > 0:
            if current_lang == 'nl':
                high_risk_title = _('report.high_risk_recommendations', 'Aanbevelingen voor Hoog-Risico Items')
            else:
                high_risk_title = _('report.high_risk_recommendations', 'High-Risk Item Recommendations')
            elements.append(Paragraph(high_risk_title, subheading_style))
            
            if report_format == "ai_model":
                # AI Model-specific high risk recommendations
                if current_lang == 'nl':
                    high_risk_recommendations = [
                        "Voer een DPIA uit specifiek voor het AI-model en de gerelateerde gegevensverwerking.",
                        "Verwijder of herzie trainingsdata die persoonlijke informatie met hoog risico bevat.",
                        "Implementeer additionele beschermende maatregelen voor AI-modellen die gevoelige gegevens verwerken.",
                        "Documenteer risicobeperkende strategieën en houd toezicht op modelgedrag.",
                        "Overweeg differentiële privacy technieken om identificeerbare informatie in het model te beschermen."
                    ]
                else:
                    high_risk_recommendations = [
                        "Conduct a DPIA specific to the AI model and its related data processing.",
                        "Remove or revise training data containing high-risk personal information.",
                        "Implement additional safeguards for AI models processing sensitive data.",
                        "Document risk mitigation strategies and monitor model behavior.",
                        "Consider differential privacy techniques to protect identifiable information in the model."
                    ]
            else:
                # Standard high risk recommendations
                if current_lang == 'nl':
                    high_risk_recommendations = [
                        "Voer een gegevensbeschermingseffectbeoordeling (DPIA) uit voor verwerkingsactiviteiten met een hoog risico.",
                        "Beoordeel en versterk toegangscontroles voor systemen die PII met een hoog risico bevatten.",
                        "Overweeg pseudonimisering of versleuteling voor gegevens met een hoog risico.",
                        "Zorg ervoor dat verwerkers die deze gegevens hanteren passende gegevensverwerkingsovereenkomsten hebben."
                    ]
                else:
                    high_risk_recommendations = [
                        "Conduct a Data Protection Impact Assessment (DPIA) for high-risk processing activities.",
                        "Review and strengthen access controls for systems containing high-risk PII.",
                        "Consider pseudonymization or encryption for high-risk data.",
                        "Ensure processors handling this data have appropriate data processing agreements."
                    ]
            
            for recommendation in high_risk_recommendations:
                elements.append(Paragraph(f"• {recommendation}", danger_style))
            
            elements.append(Spacer(1, 12))
        
        # Region-specific recommendations with translation
        if region == "Netherlands":
            if current_lang == 'nl':
                nl_rec_title = _('report.nl_recommendations', 'Nederland-Specifieke Aanbevelingen')
            else:
                nl_rec_title = _('report.nl_recommendations', 'Netherlands-Specific Recommendations')
            elements.append(Paragraph(nl_rec_title, subheading_style))
            
            if current_lang == 'nl':
                nl_recommendations = [
                    "Zorg voor toestemming van ouders voor het verwerken van persoonsgegevens van kinderen onder de 16 jaar.",
                    "Volg de richtlijnen van de Nederlandse Autoriteit Persoonsgegevens voor het melden van datalekken binnen 72 uur.",
                    "Houd u aan de specifieke regels met betrekking tot BSN-verwerking onder de UAVG.",
                    "Implementeer passende controles voor het verwerken van medische gegevens volgens UAVG-vereisten."
                ]
            else:
                nl_recommendations = [
                    "Ensure parental consent for processing personal data of children under 16.",
                    "Follow Dutch DPA (Autoriteit Persoonsgegevens) guidelines for breach notification within 72 hours.",
                    "Adhere to specific rules regarding BSN processing under UAVG.",
                    "Implement appropriate controls for processing medical data as per UAVG requirements."
                ]
            
            for recommendation in nl_recommendations:
                elements.append(Paragraph(f"• {recommendation}", normal_style))
                
        # Sustainability recommendations with translation
        if current_lang == 'nl':
            sustainability_title = _('report.sustainability_recommendations', 'Aanbevelingen voor Gegevensduurzaamheid')
        else:
            sustainability_title = _('report.sustainability_recommendations', 'Data Sustainability Recommendations')
        elements.append(Paragraph(sustainability_title, subheading_style))
        
        if current_lang == 'nl':
            sustainability_recommendations = [
                "Implementeer praktijken voor gegevensminimalisatie om alleen noodzakelijke persoonsgegevens te verzamelen.",
                "Stel duidelijke bewaartermijnen voor gegevens en geautomatiseerde verwijderingsprocessen vast.",
                "Controleer en schoon databases regelmatig om overbodige of verouderde gegevens te verwijderen.",
                "Ontwerp systemen met privacy-by-design principes om duurzaamheid te verbeteren.",
                "Overweeg optimalisatie van gegevensopslag om de milieu-impact van datacenters te verminderen."
            ]
        else:
            sustainability_recommendations = [
                "Implement data minimization practices to collect only necessary personal data.",
                "Establish clear data retention periods and automated deletion processes.",
                "Regularly audit and clean databases to remove redundant or obsolete data.",
                "Design systems with privacy by design principles to improve sustainability.",
                "Consider data storage optimization to reduce environmental impact of data centers."
            ]
        
        # Use a custom style for sustainability recommendations with green accents
        sustainability_style = ParagraphStyle(
            'Sustainability',
            parent=normal_style,
            textColor=HexColor('#2ecc71'),
            leftIndent=10,
            borderColor=HexColor('#2ecc71'),
            borderWidth=0,
            borderPadding=0,
            borderRadius=0,
            spaceBefore=2,
            spaceAfter=2
        )
        
        for recommendation in sustainability_recommendations:
            elements.append(Paragraph(f"• {recommendation}", sustainability_style))
    
    # Include metadata if requested
    if include_metadata:
        elements.append(PageBreak())
        
        # Translate metadata heading
        if current_lang == 'nl':
            metadata_title = _('report.metadata', 'Scan Metadata')
            metadata_title = 'Scan Metadata' if metadata_title == 'Scan Metadata' else 'Scan Metagegevens'
        else:
            metadata_title = _('report.metadata', 'Scan Metadata')
        elements.append(Paragraph(metadata_title, heading_style))
        
        # Collect metadata with translated labels
        if report_format == "ai_model":
            # Extract AI model specific data
            model_source = scan_data.get('model_source', 'Unknown')
            model_name = scan_data.get('model_name', scan_data.get('repository_path', 'Unknown Model'))
            repository_url = scan_data.get('repository_url', 'N/A')
            repository_path = scan_data.get('repository_path', 'N/A')
            
            if current_lang == 'nl':
                metadata_labels = {
                    'Scan ID': scan_id,
                    'Scan Type': scan_type,
                    'Regio': region,
                    'Tijdstempel': timestamp,
                    'Model Bron': model_source,
                    'Model Naam': model_name,
                    'Repository URL': repository_url if repository_url != 'N/A' else 'Niet beschikbaar',
                    'Repository Pad': repository_path if repository_path != 'N/A' else 'Niet beschikbaar',
                    'Gebruikersnaam': scan_data.get('username', 'Onbekend'),
                    'Bestanden Gescand': scan_data.get('file_count', 0)
                }
            else:
                metadata_labels = {
                    'Scan ID': scan_id,
                    'Scan Type': scan_type,
                    'Region': region,
                    'Timestamp': timestamp,
                    'Model Source': model_source,
                    'Model Name': model_name,
                    'Repository URL': repository_url if repository_url != 'N/A' else 'Not available',
                    'Repository Path': repository_path if repository_path != 'N/A' else 'Not available',
                    'Username': scan_data.get('username', 'Unknown'),
                    'Files Scanned': scan_data.get('file_count', 0)
                }
        else:
            if current_lang == 'nl':
                metadata_labels = {
                    'Scan ID': scan_id,
                    'Scan Type': scan_type,
                    'Regio': region,
                    'Tijdstempel': timestamp,
                    'URL/Domein': url,
                    'Gebruikersnaam': scan_data.get('username', 'Onbekend'),
                    'Bestanden Gescand': scan_data.get('file_count', 0)
                }
            else:
                metadata_labels = {
                    'Scan ID': scan_id,
                    'Scan Type': scan_type,
                    'Region': region,
                    'Timestamp': timestamp,
                    'URL/Domain': url,
                    'Username': scan_data.get('username', 'Unknown'),
                    'Files Scanned': scan_data.get('file_count', 0)
                }
        
        # Create metadata table
        metadata_data = []
        for key, value in metadata_labels.items():
            if value == 'Unknown' and current_lang == 'nl':
                value = 'Onbekend'
            metadata_data.append([key, str(value)])
        
        metadata_table = Table(metadata_data, colWidths=[150, 300])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        elements.append(metadata_table)
        
        # Disclaimer
        elements.append(Spacer(1, 20))
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=normal_style,
            fontSize=8,
            textColor=colors.grey
        )
        
        # Translate disclaimer text
        if current_lang == 'nl':
            disclaimer_text = (
                "Disclaimer: Dit rapport wordt uitsluitend ter informatie verstrekt en mag niet "
                "worden beschouwd als juridisch advies. De bevindingen in dit rapport zijn gebaseerd op "
                "geautomatiseerde scanning en identificeren mogelijk niet alle AVG-relevante persoonsgegevens. "
                "Wij raden u aan een gekwalificeerde juridische professional te raadplegen voor specifieke "
                "AVG-nalevingsbegeleiding."
            )
        else:
            disclaimer_text = (
                "Disclaimer: This report is provided for informational purposes only and should not "
                "be considered legal advice. The findings in this report are based on automated "
                "scanning and may not identify all GDPR-relevant personal data. We recommend "
                "consulting with a qualified legal professional for specific GDPR compliance guidance."
            )
        
        
        elements.append(Paragraph(disclaimer_text, disclaimer_style))
    
    # Special handling for sustainability reports
    if report_format == "sustainability":
        # Add sustainability specific report content
        _add_sustainability_report_content(
            elements, 
            scan_data, 
            styles, 
            heading_style, 
            subheading_style, 
            normal_style, 
            current_lang, 
            include_details, 
            include_charts, 
            include_recommendations
        )
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes
    
def _add_sustainability_report_content(elements, scan_data, styles, heading_style, subheading_style, normal_style, current_lang, include_details=True, include_charts=True, include_recommendations=True):
    """
    Add sustainability-specific content to the report PDF.
    
    Args:
        elements: The list of reportlab elements to add to
        scan_data: The sustainability scan data
        styles: The reportlab styles dictionary
        heading_style: The heading style
        subheading_style: The subheading style
        normal_style: The normal text style
        current_lang: The current language (e.g., 'en', 'nl')
        include_details: Whether to include detailed findings
        include_charts: Whether to include charts
        include_recommendations: Whether to include recommendations
    """
    # Import needed components
    from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.colors import HexColor
    
    # Add a page break before sustainability content
    elements.append(PageBreak())
    
    # Add sustainability section title
    if current_lang == 'nl':
        sustainability_title = "Duurzaamheidsanalyse"
    else:
        sustainability_title = "Sustainability Analysis"
    elements.append(Paragraph(sustainability_title, heading_style))
    elements.append(Spacer(1, 0.25*inch))
    
    # Extract scan type and key metrics
    scan_type = scan_data.get('scan_type', 'Unknown')
    sustainability_score = scan_data.get('sustainability_score', 0)
    
    # Repository information for GitHub scans
    if 'github' in scan_type.lower() or 'repository' in scan_type.lower() or 'code efficiency' in scan_type.lower():
        repo_url = scan_data.get('repo_url', 'Not specified')
        branch = scan_data.get('branch', 'main')
        
        repo_info_style = styles['Normal'].clone('RepoInfo', spaceBefore=6, spaceAfter=6)
        
        if current_lang == 'nl':
            elements.append(Paragraph(f"<b>Repository URL:</b> {repo_url}", repo_info_style))
            elements.append(Paragraph(f"<b>Branch:</b> {branch}", repo_info_style))
        else:
            elements.append(Paragraph(f"<b>Repository URL:</b> {repo_url}", repo_info_style))
            elements.append(Paragraph(f"<b>Branch:</b> {branch}", repo_info_style))
    
    # Add sustainability score visualization
    elements.append(Spacer(1, 0.1*inch))
    if current_lang == 'nl':
        elements.append(Paragraph("<b>Duurzaamheidsscore</b>", subheading_style))
    else:
        elements.append(Paragraph("<b>Sustainability Score</b>", subheading_style))
    
    # Create a score table with color coding
    score_color = '#10b981'  # Default green
    if sustainability_score < 40:
        score_color = '#ef4444'  # Red for low scores
    elif sustainability_score < 70:
        score_color = '#f97316'  # Orange for medium scores
    
    score_table_data = [[f"<font color='{score_color}'><b>{sustainability_score}/100</b></font>"]]
    score_table = Table(score_table_data, colWidths=[1.5*inch])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), HexColor('#f8f9fa')),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
        ('TEXTCOLOR', (0, 0), (0, 0), HexColor(score_color)),
        ('FONTSIZE', (0, 0), (0, 0), 16),
        ('BOTTOMPADDING', (0, 0), (0, 0), 10),
        ('TOPPADDING', (0, 0), (0, 0), 10),
        ('BOX', (0, 0), (0, 0), 1, HexColor('#e9ecef')),
        ('ROUNDEDCORNERS', [5, 5, 5, 5]),
    ]))
    elements.append(score_table)
    elements.append(Spacer(1, 0.15*inch))
    
    # Findings section
    elements.append(Spacer(1, 0.15*inch))
    if current_lang == 'nl':
        elements.append(Paragraph("<b>Bevindingen</b>", subheading_style))
    else:
        elements.append(Paragraph("<b>Findings</b>", subheading_style))
    
    # Group findings by risk level
    findings = scan_data.get('findings', [])
    risk_levels = {
        'high': [],
        'medium': [],
        'low': []
    }
    
    for finding in findings:
        risk_level = finding.get('risk_level', 'low').lower()
        if risk_level in risk_levels:
            risk_levels[risk_level].append(finding)
    
    # Add findings tables by risk level
    if risk_levels['high']:
        if current_lang == 'nl':
            elements.append(Paragraph("Hoog Risico Items", normal_style))
        else:
            elements.append(Paragraph("High Risk Items", normal_style))
        
        high_risk_data = [["Description", "Location", "Recommendation"]]
        for finding in risk_levels['high']:
            high_risk_data.append([
                finding.get('description', 'No description'),
                finding.get('location', 'Unknown'),
                finding.get('recommendation', 'No recommendation')
            ])
        
        high_risk_table = Table(high_risk_data, colWidths=[2.5*inch, 1.5*inch, 2.5*inch])
        high_risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#ef4444')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#d2d6de')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
        ]))
        elements.append(high_risk_table)
        elements.append(Spacer(1, 0.15*inch))
    
    if risk_levels['medium']:
        if current_lang == 'nl':
            elements.append(Paragraph("Gemiddeld Risico Items", normal_style))
        else:
            elements.append(Paragraph("Medium Risk Items", normal_style))
        
        medium_risk_data = [["Description", "Location", "Recommendation"]]
        for finding in risk_levels['medium']:
            medium_risk_data.append([
                finding.get('description', 'No description'),
                finding.get('location', 'Unknown'),
                finding.get('recommendation', 'No recommendation')
            ])
        
        medium_risk_table = Table(medium_risk_data, colWidths=[2.5*inch, 1.5*inch, 2.5*inch])
        medium_risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#f97316')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#d2d6de')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
        ]))
        elements.append(medium_risk_table)
        elements.append(Spacer(1, 0.15*inch))
    
    if risk_levels['low']:
        if current_lang == 'nl':
            elements.append(Paragraph("Laag Risico Items", normal_style))
        else:
            elements.append(Paragraph("Low Risk Items", normal_style))
        
        low_risk_data = [["Description", "Location", "Recommendation"]]
        for finding in risk_levels['low']:
            low_risk_data.append([
                finding.get('description', 'No description'),
                finding.get('location', 'Unknown'),
                finding.get('recommendation', 'No recommendation')
            ])
        
        low_risk_table = Table(low_risk_data, colWidths=[2.5*inch, 1.5*inch, 2.5*inch])
        low_risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#10b981')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#d2d6de')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
        ]))
        elements.append(low_risk_table)
        elements.append(Spacer(1, 0.15*inch))
    
    # Add recommendations section
    if include_recommendations:
        elements.append(PageBreak())
        if current_lang == 'nl':
            elements.append(Paragraph("<b>Aanbevelingen</b>", subheading_style))
        else:
            elements.append(Paragraph("<b>Recommendations</b>", subheading_style))
        
        recommendations = scan_data.get('recommendations', [])
        if recommendations:
            recommendation_style = normal_style.clone('RecommendationStyle', 
                                                    leftIndent=10, 
                                                    spaceBefore=4, 
                                                    spaceAfter=4)
            
            for i, rec in enumerate(recommendations):
                rec_description = rec.get('description', 'No description')
                rec_severity = rec.get('severity', 'Low')
                rec_category = rec.get('category', 'General')
                
                # Color-coded severity
                severity_color = '#10b981'  # Green for Low
                if rec_severity.lower() == 'high':
                    severity_color = '#ef4444'  # Red
                elif rec_severity.lower() == 'medium':
                    severity_color = '#f97316'  # Orange
                
                elements.append(Paragraph(f"<b>{i+1}. {rec_description}</b>", recommendation_style))
                elements.append(Paragraph(f"<b>Severity:</b> <font color='{severity_color}'>{rec_severity}</font> | <b>Category:</b> {rec_category}", recommendation_style))
                
                # Add steps if available
                steps = rec.get('steps', [])
                if steps:
                    steps_style = normal_style.clone('StepsStyle', 
                                                leftIndent=20, 
                                                spaceBefore=2, 
                                                spaceAfter=2)
                    for step in steps:
                        elements.append(Paragraph(f"• {step}", steps_style))
                
                elements.append(Spacer(1, 0.1*inch))
        else:
            if current_lang == 'nl':
                elements.append(Paragraph("Geen specifieke aanbevelingen beschikbaar.", normal_style))
            else:
                elements.append(Paragraph("No specific recommendations available.", normal_style))
    
    # If it's a GitHub repository scan, add code stats
    if ('github' in scan_type.lower() or 'repository' in scan_type.lower() or 'code efficiency' in scan_type.lower()) and include_details:
        elements.append(PageBreak())
        if current_lang == 'nl':
            elements.append(Paragraph("<b>Code Statistieken</b>", subheading_style))
        else:
            elements.append(Paragraph("<b>Code Statistics</b>", subheading_style))
        
        code_stats = scan_data.get('code_stats', {})
        if code_stats:
            code_stats_data = []
            if current_lang == 'nl':
                code_stats_data = [
                    ["Totaal Bestanden", str(code_stats.get('total_files', 0))],
                    ["Repository Grootte", f"{code_stats.get('total_size_mb', 0):.2f} MB"],
                    ["Gemiddelde Bestandsgrootte", f"{code_stats.get('avg_file_size_kb', 0):.2f} KB"],
                ]
            else:
                code_stats_data = [
                    ["Total Files", str(code_stats.get('total_files', 0))],
                    ["Repository Size", f"{code_stats.get('total_size_mb', 0):.2f} MB"],
                    ["Average File Size", f"{code_stats.get('avg_file_size_kb', 0):.2f} KB"],
                ]
            
            code_stats_table = Table(code_stats_data, colWidths=[2*inch, 2*inch])
            code_stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#d2d6de')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(code_stats_table)
            elements.append(Spacer(1, 0.15*inch))
            
            # Add language breakdown if available
            language_breakdown = code_stats.get('language_breakdown', {})
            if language_breakdown:
                if current_lang == 'nl':
                    elements.append(Paragraph("<b>Taal Verdeling</b>", normal_style))
                else:
                    elements.append(Paragraph("<b>Language Breakdown</b>", normal_style))
                
                language_data = [["Language", "Files", "Size (MB)"]]
                for lang, stats in language_breakdown.items():
                    language_data.append([
                        lang,
                        str(stats.get('file_count', 0)),
                        f"{stats.get('size_mb', 0):.2f}"
                    ])
                
                language_table = Table(language_data, colWidths=[2*inch, 1*inch, 1*inch])
                language_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#f0f0f0')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#d2d6de')),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                ]))
                elements.append(language_table)
        else:
            if current_lang == 'nl':
                elements.append(Paragraph("Geen code statistieken beschikbaar.", normal_style))
            else:
                elements.append(Paragraph("No code statistics available.", normal_style))
        
        # Add unused imports section if available
        unused_imports = scan_data.get('unused_imports', [])
        if unused_imports:
            elements.append(Spacer(1, 0.15*inch))
            if current_lang == 'nl':
                elements.append(Paragraph("<b>Ongebruikte Imports</b>", normal_style))
            else:
                elements.append(Paragraph("<b>Unused Imports</b>", normal_style))
            
            unused_data = [["File", "Import"]]
            for unused in unused_imports:
                unused_data.append([
                    unused.get('file', 'Unknown'),
                    unused.get('import', 'Unknown')
                ])
            
            unused_table = Table(unused_data, colWidths=[3*inch, 3*inch])
            unused_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#f0f0f0')),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#d2d6de')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            elements.append(unused_table)
        
        # Add large files section if available
        large_files = scan_data.get('large_files', [])
        if large_files:
            elements.append(Spacer(1, 0.15*inch))
            if current_lang == 'nl':
                elements.append(Paragraph("<b>Grote Bestanden</b>", normal_style))
            else:
                elements.append(Paragraph("<b>Large Files</b>", normal_style))
            
            large_data = [["File", "Size (MB)", "Category"]]
            for large_file in large_files:
                large_data.append([
                    large_file.get('file', 'Unknown'),
                    f"{large_file.get('size_mb', 0):.2f}",
                    large_file.get('category', 'Unknown')
                ])
            
            large_table = Table(large_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
            large_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#f0f0f0')),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#d2d6de')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            elements.append(large_table)
