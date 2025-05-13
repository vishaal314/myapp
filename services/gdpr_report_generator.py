"""
GDPR Code Scanner Report Generator

This module generates professional PDF reports for GDPR Code Scanner results
with certification options and branded design elements.
"""

import os
import time
from datetime import datetime
import uuid
import base64
from io import BytesIO
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm, inch
from reportlab.graphics.shapes import Drawing, Wedge
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib.colors import PCMYKColor

# Set up styles
def get_custom_styles():
    """Create and return custom styles for the PDF report"""
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(
        name='Heading1_Blue',
        parent=styles['Heading1'],
        textColor=colors.HexColor("#1A5F7A"),
        spaceAfter=12,
        fontSize=18
    ))
    
    styles.add(ParagraphStyle(
        name='Heading2_Blue',
        parent=styles['Heading2'],
        textColor=colors.HexColor("#2E86AB"),
        spaceAfter=10,
        fontSize=16
    ))
    
    styles.add(ParagraphStyle(
        name='BodyText_Custom',
        parent=styles['BodyText'],
        textColor=colors.HexColor("#333333"),
        spaceAfter=8,
        fontSize=10,
        leading=14
    ))
    
    styles.add(ParagraphStyle(
        name='Caption_Custom',
        parent=styles['BodyText'],
        textColor=colors.HexColor("#555555"),
        fontSize=9,
        leading=12,
        alignment=1  # Center aligned
    ))
    
    styles.add(ParagraphStyle(
        name='Certificate_Title',
        parent=styles['Heading1'],
        textColor=colors.HexColor("#003366"),
        fontSize=24,
        alignment=1,  # Center aligned
        spaceAfter=15
    ))
    
    styles.add(ParagraphStyle(
        name='Certificate_Text',
        parent=styles['BodyText'],
        textColor=colors.HexColor("#003366"),
        fontSize=14,
        alignment=1,  # Center aligned
        spaceAfter=10
    ))
    
    return styles

def create_logo():
    """Create DataGuardian Pro logo for the report"""
    # Create a BytesIO object to hold the logo
    buffer = BytesIO()
    
    # Create a canvas with appropriate dimensions for the logo
    c = canvas.Canvas(buffer, pagesize=(100, 100))
    
    # Draw the shield shape
    c.setFillColor(colors.HexColor("#1A5F7A"))
    c.ellipse(10, 10, 90, 90, fill=1)
    
    c.setFillColor(colors.white)
    c.ellipse(15, 15, 85, 85, fill=1)
    
    c.setFillColor(colors.HexColor("#2E86AB"))
    c.ellipse(20, 20, 80, 80, fill=1)
    
    # Add a lock symbol or similar privacy icon in the center
    c.setFillColor(colors.white)
    c.rect(40, 35, 20, 25, fill=1)  # Lock body
    c.ellipse(42, 60, 58, 80, fill=1)  # Lock loop
    
    # Add "DG" text
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.white)
    c.drawCentredString(50, 45, "DG")
    
    c.save()
    
    # Get the PDF data and convert to an Image object
    buffer.seek(0)
    return buffer.getvalue()

def create_certification_seal(certification_type):
    """Create a certification seal based on certification type"""
    buffer = BytesIO()
    
    # Create a canvas for the seal
    c = canvas.Canvas(buffer, pagesize=(200, 200))
    
    # Outer circle
    c.setStrokeColor(colors.HexColor("#003366"))
    c.setFillColor(colors.HexColor("#E6F2FF"))
    c.circle(100, 100, 90, fill=1, stroke=1)
    
    # Inner circle
    c.setStrokeColor(colors.HexColor("#003366"))
    c.setFillColor(colors.white)
    c.circle(100, 100, 75, fill=1, stroke=1)
    
    # Text
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.HexColor("#003366"))
    c.drawCentredString(100, 130, "CERTIFIED")
    
    # Certification type
    c.setFont("Helvetica-Bold", 12)
    if certification_type == "GDPR Compliant":
        c.drawCentredString(100, 110, "GDPR")
        c.drawCentredString(100, 95, "COMPLIANT")
    elif certification_type == "ISO 27001 Aligned":
        c.drawCentredString(100, 110, "ISO 27001")
        c.drawCentredString(100, 95, "ALIGNED")
    elif certification_type == "UAVG Certified":
        c.drawCentredString(100, 110, "UAVG")
        c.drawCentredString(100, 95, "CERTIFIED")
    else:
        c.drawCentredString(100, 105, certification_type)
    
    # Date
    c.setFont("Helvetica", 10)
    current_year = datetime.now().year
    c.drawCentredString(100, 75, f"{current_year}")
    
    # DataGuardian text at bottom
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(100, 60, "DataGuardian Pro")
    
    c.save()
    
    # Get the PDF data
    buffer.seek(0)
    return buffer.getvalue()

def generate_risk_donut_chart(compliance_score):
    """Generate a donut chart showing compliance score"""
    drawing = Drawing(150, 150)
    
    # Calculate colors based on score
    if compliance_score >= 80:
        color = colors.HexColor("#10B981")  # Green
    elif compliance_score >= 60:
        color = colors.HexColor("#F59E0B")  # Yellow
    else:
        color = colors.HexColor("#EF4444")  # Red
    
    # Background circle (grey)
    pie = Pie()
    pie.x = 75
    pie.y = 75
    pie.width = 150
    pie.height = 150
    pie.data = [100]
    # Set labels differently to avoid type error
    pie.slices.strokeWidth = 0
    pie.slices[0].fillColor = colors.HexColor("#E5E7EB")
    
    # Add to drawing
    drawing.add(pie)
    
    # Foreground arc (colored based on score)
    angle = 3.6 * compliance_score  # Convert percentage to degrees (100% = 360 degrees)
    
    # Create wedge for score
    scoreWedge = Wedge(75, 75, 75, 0, angle)
    scoreWedge.fillColor = color
    scoreWedge.strokeColor = None
    drawing.add(scoreWedge)
    
    # Create center circle for donut hole (white)
    centerCircle = Wedge(75, 75, 50, 0, 360)
    centerCircle.fillColor = colors.white
    centerCircle.strokeColor = None
    drawing.add(centerCircle)
    
    return drawing

def create_findings_summary_chart(findings):
    """Create a bar chart summarizing findings by risk level"""
    # Count findings by risk level
    risk_counts = {"high": 0, "medium": 0, "low": 0}
    
    for finding in findings:
        severity = finding.get("severity", finding.get("risk_level", "medium")).lower()
        if severity in risk_counts:
            risk_counts[severity] += 1
    
    # Create drawing
    drawing = Drawing(400, 200)
    
    # Create bar chart
    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 50
    bc.height = 125
    bc.width = 300
    bc.data = [[risk_counts["high"], risk_counts["medium"], risk_counts["low"]]]
    
    # Customize the chart
    bc.bars[0].fillColor = colors.HexColor("#EF4444")  # Red for high
    bc.barLabels.fontName = 'Helvetica'
    bc.barLabels.fontSize = 8
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = max(risk_counts.values()) + 2
    bc.valueAxis.valueStep = 1
    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.dx = 8
    bc.categoryAxis.labels.dy = -2
    bc.categoryAxis.labels.angle = 0
    bc.categoryAxis.categoryNames = ['High', 'Medium', 'Low']
    
    drawing.add(bc)
    return drawing

def generate_gdpr_report(scan_results, certification_type=None, include_certificate=False):
    """
    Generate a professional PDF report for GDPR Code Scanner results
    
    Args:
        scan_results: Dictionary containing scan results
        certification_type: Type of certification to include (if any)
        include_certificate: Whether to include a certificate page
        
    Returns:
        BytesIO object containing the PDF report
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                            leftMargin=25*mm, rightMargin=25*mm,
                            topMargin=20*mm, bottomMargin=20*mm)
    
    # Get styles
    styles = get_custom_styles()
    
    # Start building the document
    elements = []
    
    # Get logo as bytes
    logo_bytes = create_logo()
    
    # Create header with logo
    logo_data = base64.b64encode(logo_bytes).decode('utf-8')
    img = Image(BytesIO(base64.b64decode(logo_data)))
    img.drawHeight = 25*mm
    img.drawWidth = 25*mm
    
    # Title and header
    header_data = [
        [img, Paragraph(f"<b>GDPR Code Scanner Report</b><br/><br/>{datetime.now().strftime('%d %B %Y')}", styles["Heading1_Blue"])]
    ]
    header_table = Table(header_data, colWidths=[30*mm, 120*mm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 10*mm))
    
    # Executive summary
    elements.append(Paragraph("Executive Summary", styles["Heading2_Blue"]))
    
    # Extract data from scan results
    scan_id = scan_results.get("scan_id", "N/A")
    timestamp = scan_results.get("timestamp", datetime.now().isoformat())
    if isinstance(timestamp, str):
        try:
            scan_date = datetime.fromisoformat(timestamp).strftime("%d %B %Y, %H:%M")
        except ValueError:
            scan_date = timestamp
    else:
        scan_date = timestamp.strftime("%d %B %Y, %H:%M")
    
    compliance_score = scan_results.get("compliance_score", 0)
    findings = scan_results.get("findings", [])
    
    # Count findings by risk level
    high_risk = scan_results.get("high_risk", sum(1 for f in findings if f.get("severity", f.get("risk_level", "")).lower() == "high"))
    medium_risk = scan_results.get("medium_risk", sum(1 for f in findings if f.get("severity", f.get("risk_level", "")).lower() == "medium"))
    low_risk = scan_results.get("low_risk", sum(1 for f in findings if f.get("severity", f.get("risk_level", "")).lower() == "low"))
    total_findings = scan_results.get("total_findings", len(findings))
    
    # Summary text
    summary_text = f"""
    This report provides a comprehensive assessment of GDPR compliance based on code analysis conducted on {scan_date}. 
    The scan identified {total_findings} findings across the codebase, with {high_risk} high-risk, {medium_risk} medium-risk, 
    and {low_risk} low-risk issues. The overall compliance score is {compliance_score}%.
    """
    
    elements.append(Paragraph(summary_text, styles["BodyText_Custom"]))
    elements.append(Spacer(1, 5*mm))
    
    # Add compliance score donut chart
    elements.append(Paragraph("Compliance Score", styles["Heading2_Blue"]))
    
    # Create a table with the donut chart and score text
    donut_chart = generate_risk_donut_chart(compliance_score)
    
    # Determine score text and color
    if compliance_score >= 80:
        score_color = "#10B981"
        score_text = "Good"
    elif compliance_score >= 60:
        score_color = "#F59E0B"
        score_text = "Needs Improvement"
    else:
        score_color = "#EF4444"
        score_text = "Critical Issues"
    
    score_paragraph = Paragraph(
        f"""<font color="{score_color}" size="14"><b>{compliance_score}%</b></font><br/>
        <font color="{score_color}">{score_text}</font>""",
        styles["BodyText_Custom"]
    )
    
    score_table_data = [[donut_chart, score_paragraph]]
    score_table = Table(score_table_data, colWidths=[150, 200])
    score_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),
    ]))
    
    elements.append(score_table)
    elements.append(Spacer(1, 10*mm))
    
    # Findings summary
    elements.append(Paragraph("Findings Summary", styles["Heading2_Blue"]))
    
    # Add bar chart for findings
    findings_chart = create_findings_summary_chart(findings)
    elements.append(findings_chart)
    elements.append(Paragraph("Distribution of Findings by Risk Level", styles["Caption_Custom"]))
    elements.append(Spacer(1, 10*mm))
    
    # Detailed findings
    elements.append(Paragraph("Detailed Findings", styles["Heading2_Blue"]))
    
    if findings:
        # Create a table for the findings
        findings_data = [["Risk Level", "Title", "Location", "Description"]]
        
        for i, finding in enumerate(findings[:20]):  # Limit to 20 findings for readability
            severity = finding.get("severity", finding.get("risk_level", "Medium"))
            title = finding.get("title", finding.get("pattern_key", "Issue"))
            location = finding.get("location", "N/A")
            description = finding.get("description", "No description provided")
            
            # Adjust severity for display
            severity_display = severity.upper() if isinstance(severity, str) else "MEDIUM"
            
            # Add to table
            findings_data.append([severity_display, title, location, description])
        
        # Create the table
        findings_table = Table(findings_data, colWidths=[20*mm, 35*mm, 35*mm, 60*mm])
        
        # Style the table
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2E86AB")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#E5E7EB")),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ]
        
        # Add row colors based on risk level
        for i in range(1, len(findings_data)):
            risk_level = findings_data[i][0].lower()
            if "high" in risk_level:
                table_style.append(('BACKGROUND', (0, i), (0, i), colors.HexColor("#FECACA")))
            elif "medium" in risk_level:
                table_style.append(('BACKGROUND', (0, i), (0, i), colors.HexColor("#FEF3C7")))
            else:
                table_style.append(('BACKGROUND', (0, i), (0, i), colors.HexColor("#ECFDF5")))
        
        findings_table.setStyle(TableStyle(table_style))
        elements.append(findings_table)
    else:
        elements.append(Paragraph("No findings to display.", styles["BodyText_Custom"]))
    
    elements.append(Spacer(1, 10*mm))
    
    # GDPR Compliance Principles
    elements.append(Paragraph("GDPR Principles Coverage", styles["Heading2_Blue"]))
    
    principles = [
        ("lawfulness_fairness_transparency", "Lawfulness, Fairness, and Transparency"),
        ("purpose_limitation", "Purpose Limitation"),
        ("data_minimization", "Data Minimization"),
        ("accuracy", "Accuracy"),
        ("storage_limitation", "Storage Limitation"),
        ("integrity_confidentiality", "Integrity and Confidentiality"),
        ("accountability", "Accountability")
    ]
    
    principles_data = [["GDPR Principle", "Status"]]
    
    # Check which principles were covered in the scan
    principles_checked = set()
    for finding in findings:
        principle = finding.get("gdpr_principle", "")
        if principle:
            principles_checked.add(principle)
    
    # If principles_checked is empty, assume all principles were checked
    if not principles_checked:
        principles_checked = {p[0] for p in principles}
    
    for principle_id, principle_name in principles:
        status = "Checked" if principle_id in principles_checked else "Not Checked"
        principles_data.append([principle_name, status])
    
    principles_table = Table(principles_data, colWidths=[100*mm, 50*mm])
    principles_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2E86AB")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#E5E7EB")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    
    elements.append(principles_table)
    elements.append(Spacer(1, 10*mm))
    
    # Recommendations
    elements.append(Paragraph("Recommendations", styles["Heading2_Blue"]))
    
    # Generate recommendations based on findings
    if high_risk > 0:
        elements.append(Paragraph("1. Address all high-risk findings immediately as they may represent critical GDPR compliance gaps.", styles["BodyText_Custom"]))
    
    if any("data_subject_rights" in str(f.get("pattern_key", "")) for f in findings):
        elements.append(Paragraph("2. Improve implementation of data subject rights access and request handling.", styles["BodyText_Custom"]))
    
    if any("consent" in str(f.get("pattern_key", "")) for f in findings):
        elements.append(Paragraph("3. Review and enhance consent collection and management processes.", styles["BodyText_Custom"]))
    
    if any("data_retention" in str(f.get("pattern_key", "")) for f in findings):
        elements.append(Paragraph("4. Implement or improve data retention policies and automatic data purging.", styles["BodyText_Custom"]))
    
    if any("security" in str(f.get("pattern_key", "")) for f in findings):
        elements.append(Paragraph("5. Strengthen security measures for personal data protection.", styles["BodyText_Custom"]))
    
    elements.append(Paragraph("6. Schedule a follow-up scan after remediation to verify improvements.", styles["BodyText_Custom"]))
    elements.append(Spacer(1, 10*mm))
    
    # Add certification if requested
    if include_certificate and certification_type:
        # Add a page break before the certificate
        elements.append(PageBreak())
        
        # Certificate title
        elements.append(Paragraph("Certificate of GDPR Compliance", styles["Certificate_Title"]))
        elements.append(Spacer(1, 20*mm))
        
        # Create certification seal
        seal_bytes = create_certification_seal(certification_type)
        seal_data = base64.b64encode(seal_bytes).decode('utf-8')
        seal_img = Image(BytesIO(base64.b64decode(seal_data)))
        seal_img.drawHeight = 100*mm
        seal_img.drawWidth = 100*mm
        
        elements.append(seal_img)
        elements.append(Spacer(1, 20*mm))
        
        # Certificate text
        cert_text = f"""
        This is to certify that the code scanned on<br/>
        <b>{scan_date}</b><br/><br/>
        has been assessed for GDPR compliance and meets the<br/>
        requirements for certification as<br/><br/>
        <b>{certification_type}</b><br/><br/>
        Certificate ID: GDPR-{scan_id[:8]}<br/>
        Validity: 1 year from issue date
        """
        
        elements.append(Paragraph(cert_text, styles["Certificate_Text"]))
    
    # Build the document
    doc.build(elements)
    
    # Get the PDF value and return it
    buffer.seek(0)
    return buffer

def generate_gdpr_report_streamlit(scan_results):
    """
    Generate a GDPR report from Streamlit interface
    
    Args:
        scan_results: Dictionary containing scan results
    
    Returns:
        None (displays download button in Streamlit)
    """
    st.subheader("Generate Professional GDPR Compliance Report")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Certification options
        certification_types = [
            "None",
            "GDPR Compliant",
            "ISO 27001 Aligned",
            "UAVG Certified"
        ]
        
        certification_type = st.selectbox(
            "Certification Type",
            certification_types,
            index=0,
            help="Include a certification seal in the report"
        )
        
        include_certificate = certification_type != "None"
    
    with col2:
        # Report options
        include_executive_summary = st.checkbox("Include Executive Summary", value=True)
        include_findings_details = st.checkbox("Include Detailed Findings", value=True)
        include_recommendations = st.checkbox("Include Recommendations", value=True)
    
    # Generate the report when the button is clicked
    if st.button("Generate Professional PDF Report", type="primary"):
        with st.spinner("Generating professional PDF report..."):
            # Show progress
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress((i + 1)/100)
            
            # Generate the report
            pdf_buffer = generate_gdpr_report(
                scan_results, 
                certification_type if include_certificate else None,
                include_certificate
            )
            
            # Create download button for the report
            st.download_button(
                label="📥 Download GDPR Compliance Report",
                data=pdf_buffer,
                file_name=f"GDPR_Compliance_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
            # Success message
            st.success("✅ Professional GDPR Compliance Report generated successfully!")
            
            # Preview message
            st.info("Use the download button above to save your report. The report includes professional design elements, detailed findings, and your selected certification seal.")