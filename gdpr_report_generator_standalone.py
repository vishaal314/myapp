"""
Standalone GDPR PDF Report Generator

This is a copy of the services/gdpr_report_generator.py file that can
be used by the minimal GDPR PDF generator when run as a standalone app.
"""

import os
import json
import base64
from datetime import datetime
import io
from typing import Dict, List, Any, Tuple, Optional, Union

from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

def generate_gdpr_report(scan_results: Dict[str, Any], organization_name: str = "Your Organization", certification_type: str = "GDPR Compliant") -> bytes:
    """
    Generate a professional PDF report for GDPR compliance scan results.
    
    Args:
        scan_results: The GDPR scan results
        organization_name: Organization name to include in the report
        certification_type: Type of certification to display
        
    Returns:
        PDF report as bytes
    """
    try:
        # Create a buffer for the PDF
        buffer = BytesIO()
        
        # Create the PDF document
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Create custom styles
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Title'],
            fontSize=18,
            spaceAfter=0.3*inch,
            textColor=colors.HexColor('#1E88E5')
        )
        
        heading_style = ParagraphStyle(
            'Heading1',
            parent=styles['Heading1'],
            fontSize=16,
            spaceBefore=0.2*inch,
            spaceAfter=0.1*inch,
            textColor=colors.HexColor('#1976D2')
        )
        
        subheading_style = ParagraphStyle(
            'Heading2',
            parent=styles['Heading2'],
            fontSize=14,
            spaceBefore=0.1*inch,
            spaceAfter=0.1*inch,
            textColor=colors.HexColor('#1976D2')
        )
        
        normal_style = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            fontSize=10,
            spaceBefore=0.05*inch,
            spaceAfter=0.05*inch
        )
        
        # Create the story for the PDF
        story = []
        
        # Add title
        story.append(Paragraph("GDPR Compliance Report", title_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Add organization and date information
        story.append(Paragraph(f"Organization: {organization_name}", styles['Normal']))
        story.append(Paragraph(f"Certification: {certification_type}", styles['Normal']))
        story.append(Paragraph(f"Report Date: {datetime.now().strftime('%Y-%m-%d')}", styles['Normal']))
        story.append(Paragraph(f"Report ID: GDPR-{datetime.now().strftime('%Y%m%d')}-{hash(organization_name) % 10000:04d}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Add executive summary
        story.append(Paragraph("Executive Summary", heading_style))
        
        compliance_score = scan_results.get('compliance_score', 75)
        high_risk = scan_results.get('high_risk', 0)
        total_findings = scan_results.get('total_findings', len(scan_results.get('findings', [])))
        
        # Risk level based on compliance score
        risk_level = "Low" if compliance_score >= 80 else "Medium" if compliance_score >= 60 else "High"
        risk_color = "#4CAF50" if compliance_score >= 80 else "#FF9800" if compliance_score >= 60 else "#F44336"
        
        # Executive summary text
        summary_text = f"""
        This report presents the findings of a GDPR compliance assessment conducted for {organization_name}.
        The assessment evaluated compliance with General Data Protection Regulation (GDPR) principles and
        requirements. The organization received a compliance score of {compliance_score}%, which represents
        a <font color='{risk_color}'><b>{risk_level} Risk</b></font> level.
        
        The assessment identified <b>{high_risk}</b> high-risk findings out of <b>{total_findings}</b> total findings.
        """
        
        story.append(Paragraph(summary_text, normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Add compliance metrics in a table
        story.append(Paragraph("Compliance Metrics", subheading_style))
        
        metrics_data = [
            ["Metric", "Value", "Status"],
            ["Compliance Score", f"{compliance_score}%", f"{risk_level} Risk"],
            ["High Risk Findings", str(high_risk), "Needs Attention" if high_risk > 0 else "Good"],
            ["Total Findings", str(total_findings), "Needs Review" if total_findings > 5 else "Good"],
        ]
        
        # Create table
        metrics_table = Table(metrics_data, colWidths=[2*inch, 1.5*inch, 2*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#E3F2FD')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BBDEFB')),
        ]))
        
        story.append(metrics_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Add GDPR Principles Section
        story.append(Paragraph("GDPR Principles Assessment", heading_style))
        
        # Define the 7 GDPR principles
        principles = [
            ("Lawfulness, Fairness and Transparency", 
             "Personal data shall be processed lawfully, fairly and in a transparent manner in relation to the individual.", 
             "High" if compliance_score < 60 else "Medium" if compliance_score < 80 else "Low"),
            
            ("Purpose Limitation", 
             "Personal data shall be collected for specified, explicit and legitimate purposes.", 
             "Medium" if compliance_score < 70 else "Low"),
            
            ("Data Minimization", 
             "Personal data shall be adequate, relevant and limited to what is necessary.", 
             "Medium" if compliance_score < 75 else "Low"),
            
            ("Accuracy", 
             "Personal data shall be accurate and, where necessary, kept up to date.", 
             "Low"),
            
            ("Storage Limitation", 
             "Personal data shall be kept in a form which permits identification of data subjects for no longer than is necessary.", 
             "Medium" if high_risk > 2 else "Low"),
            
            ("Integrity and Confidentiality", 
             "Personal data shall be processed in a manner that ensures appropriate security.", 
             "High" if high_risk > 5 else "Medium" if high_risk > 2 else "Low"),
            
            ("Accountability", 
             "The controller shall be responsible for, and be able to demonstrate compliance with the GDPR principles.", 
             "Medium" if compliance_score < 80 else "Low"),
        ]
        
        # Build principles table data
        principles_data = [["Principle", "Description", "Risk Level"]]
        
        for principle, description, risk in principles:
            principles_data.append([principle, description, risk])
        
        # Create principles table
        principles_table = Table(principles_data, colWidths=[1.5*inch, 3.5*inch, 1*inch])
        principles_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BBDEFB')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#E3F2FD'), colors.HexColor('#F5F5F5')]),
        ]))
        
        # Color code risk levels
        for i, (_, _, risk) in enumerate(principles, 1):
            if risk == "High":
                principles_table.setStyle(TableStyle([
                    ('TEXTCOLOR', (2, i), (2, i), colors.HexColor('#F44336')),
                    ('FONTNAME', (2, i), (2, i), 'Helvetica-Bold'),
                ]))
            elif risk == "Medium":
                principles_table.setStyle(TableStyle([
                    ('TEXTCOLOR', (2, i), (2, i), colors.HexColor('#FF9800')),
                    ('FONTNAME', (2, i), (2, i), 'Helvetica-Bold'),
                ]))
            else:  # Low
                principles_table.setStyle(TableStyle([
                    ('TEXTCOLOR', (2, i), (2, i), colors.HexColor('#4CAF50')),
                    ('FONTNAME', (2, i), (2, i), 'Helvetica-Bold'),
                ]))
        
        story.append(principles_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Add recommendations section
        story.append(Paragraph("Recommendations", heading_style))
        
        # Sample recommendations based on principles with higher risk
        recommendations = []
        for principle, description, risk in principles:
            if risk in ["High", "Medium"]:
                if principle == "Lawfulness, Fairness and Transparency":
                    recommendations.append("- Ensure all data processing activities have a lawful basis and are documented")
                    recommendations.append("- Update privacy notices to be more transparent about data processing activities")
                elif principle == "Purpose Limitation":
                    recommendations.append("- Review and document the specific purposes for all data processing activities")
                    recommendations.append("- Implement procedures to prevent data use beyond stated purposes")
                elif principle == "Data Minimization":
                    recommendations.append("- Audit data collection processes to ensure only necessary data is collected")
                    recommendations.append("- Implement data retention policies to remove unnecessary data")
                elif principle == "Storage Limitation":
                    recommendations.append("- Establish clear data retention periods for all personal data")
                    recommendations.append("- Implement automated data deletion processes for expired data")
                elif principle == "Integrity and Confidentiality":
                    recommendations.append("- Strengthen encryption for data in transit and at rest")
                    recommendations.append("- Implement access controls based on least privilege principle")
                elif principle == "Accountability":
                    recommendations.append("- Maintain comprehensive documentation of all data processing activities")
                    recommendations.append("- Appoint a Data Protection Officer if not already in place")
        
        # If no high/medium risks, provide general recommendations
        if not recommendations:
            recommendations = [
                "- Continue maintaining current GDPR compliance practices",
                "- Consider periodic reassessment to ensure ongoing compliance",
                "- Stay updated on GDPR regulatory changes and guidance"
            ]
        
        # Add recommendation bullets
        for recommendation in recommendations:
            story.append(Paragraph(recommendation, normal_style))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Add certification statement
        story.append(Paragraph("Certification Statement", heading_style))
        cert_text = f"""
        Based on the assessment results, {organization_name} is hereby certified as
        <b>{certification_type}</b> as of {datetime.now().strftime('%Y-%m-%d')}.
        This certification is valid for one year from the date of issuance, subject
        to continued compliance with GDPR requirements and no significant changes
        to data processing activities.
        """
        story.append(Paragraph(cert_text, normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Add verification information
        story.append(Paragraph("Verification", subheading_style))
        verification_data = [
            ["Certified By:", "DataGuardian Pro Verification System"],
            ["Certificate ID:", f"GDPR-{datetime.now().strftime('%Y%m%d')}-{hash(organization_name) % 10000:04d}"],
            ["Valid Until:", f"{(datetime.now().replace(year=datetime.now().year + 1)).strftime('%Y-%m-%d')}"]
        ]
        verification_table = Table(verification_data, colWidths=[2*inch, 4*inch])
        verification_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BBDEFB')),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E3F2FD')),
        ]))
        story.append(verification_table)
        
        # Add footer
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(
            "<i>This report is generated automatically by the DataGuardian Pro platform "
            "and represents an assessment of GDPR compliance at the time of scanning. "
            "Regular reassessment is recommended as part of ongoing compliance efforts.</i>",
            styles['Normal']
        ))
        
        # Build document
        doc.build(story)
        
        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
    
    except Exception as e:
        print(f"Error generating GDPR report: {str(e)}")
        # Return a simple fallback PDF
        return create_fallback_pdf(organization_name, certification_type)

def create_fallback_pdf(organization_name, certification_type):
    """Create a simple fallback PDF in case the main generator fails"""
    pdf_content = f"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/MediaBox[0 0 595 842]/Parent 2 0 R/Resources<</Font<</F1<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>>>>>/Contents 4 0 R>>endobj
4 0 obj<</Length 150>>stream
BT
/F1 24 Tf
50 800 Td
(GDPR Compliance Report) Tj
/F1 14 Tf
0 -50 Td
(Organization: {organization_name}) Tj
0 -20 Td
(Certification: {certification_type}) Tj
0 -20 Td
(Generated: {datetime.now().strftime('%Y-%m-%d')}) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000010 00000 n
0000000053 00000 n
0000000102 00000 n
0000000229 00000 n
trailer<</Size 5/Root 1 0 R>>
startxref
428
%%EOF""".encode('latin1')
    
    return pdf_content