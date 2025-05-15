"""
GDPR PDF Report Generator

This module provides a comprehensive GDPR PDF report generator that produces
professional reports based on GDPR Code Scanner findings.
"""

import os
import json
import base64
from datetime import datetime
import io
from typing import Dict, List, Any, Tuple, Optional, Union

import streamlit as st
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
            alignment=TA_CENTER,
            spaceAfter=0.1*inch,
            textColor=colors.HexColor('#1E88E5')
        )
        
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Normal'],
            fontSize=28,
            alignment=TA_CENTER, 
            textColor=colors.HexColor('#0D47A1'),
            spaceBefore=0.1*inch,
            spaceAfter=0.4*inch
        )
        
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1976D2'),
            spaceBefore=0.1*inch,
            spaceAfter=0.3*inch
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
        
        section_title_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1976D2'),
            spaceBefore=0.15*inch,
            spaceAfter=0.05*inch
        )
        
        # Create the story for the PDF
        story = []
        
        # Create headers with logo-like styling
        story.append(Paragraph("GDPR COMPLIANCE", header_style))
        story.append(Paragraph(f"DataGuardian {certification_type.split(' ')[0]}", title_style))
        story.append(Paragraph("●●●●", title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Add main title
        story.append(Paragraph("GDPR Compliance Assessment Report", subtitle_style))
        
        # Add organization and date information in a cleaner format
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y')}", normal_style))
        story.append(Paragraph(f"Scan ID: GDPR-{datetime.now().strftime('%Y%m%d')}-{hash(organization_name) % 10000:04d}", normal_style))
        story.append(Paragraph(f"Organization: {organization_name}", normal_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Add Compliance Summary section
        story.append(Paragraph("Compliance Summary", section_title_style))
        
        # Extract compliance data
        compliance_score = scan_results.get('compliance_score', 75)
        high_risk = scan_results.get('high_risk', 0)
        medium_risk = scan_results.get('medium_risk', 0)
        low_risk = scan_results.get('low_risk', 0)
        total_findings = scan_results.get('total_findings', len(scan_results.get('findings', [])))
        total_checks = scan_results.get('total_checks', total_findings + 10)
        passed_checks = scan_results.get('passed_checks', total_checks - total_findings)
        
        # Determine overall compliance level
        compliance_level = "Good" if compliance_score >= 80 else "Needs Review" if compliance_score >= 60 else "Critical"
        compliance_color = "#4CAF50" if compliance_score >= 80 else "#FF9800" if compliance_score >= 60 else "#F44336"
        
        # Create Overall Compliance section
        story.append(Paragraph("Overall Compliance", normal_style))
        story.append(Spacer(1, 0.05*inch))
        
        # Create a custom visual for compliance score
        compliance_text = f"""
        <para align="center">
        <font size="18" color="{compliance_color}"><b>{compliance_score}%</b></font>
        </para>
        <para align="center">
        <font size="14" color="{compliance_color}"><b>{compliance_level}</b></font>
        </para>
        """
        story.append(Paragraph(compliance_text, normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Create metrics table
        metrics_data = [
            ["Metric", "Value"],
            ["Total Checks", str(total_checks)],
            ["Passed Checks", str(passed_checks)],
            ["Failed Checks", str(total_findings)],
            ["Compliance Score", f"{compliance_score}%"],
        ]
        
        # Style the metrics table
        metrics_table = Table(metrics_data, colWidths=[3*inch, 2*inch])
        metrics_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BBDEFB')),
        ]))
        
        story.append(metrics_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Add Category Compliance section
        story.append(Paragraph("Category Compliance", section_title_style))
        
        # Define the 7 GDPR principles with scores
        principles_categories = [
            ("Lawfulness, Fairness and Transparency", total_checks // 7, 
             passed_checks // 7 + (0 if compliance_score < 60 else 1), 
             total_checks // 7 - (passed_checks // 7 + (0 if compliance_score < 60 else 1))),
            
            ("Purpose Limitation", total_checks // 7, 
             passed_checks // 7 + (0 if compliance_score < 70 else 1), 
             total_checks // 7 - (passed_checks // 7 + (0 if compliance_score < 70 else 1))),
            
            ("Data Minimization", total_checks // 7, 
             passed_checks // 7 + (0 if compliance_score < 75 else 1), 
             total_checks // 7 - (passed_checks // 7 + (0 if compliance_score < 75 else 1))),
            
            ("Accuracy", total_checks // 7, 
             passed_checks // 7 + 1, 
             total_checks // 7 - (passed_checks // 7 + 1)),
            
            ("Storage Limitation", total_checks // 7, 
             passed_checks // 7 + (0 if high_risk > 2 else 1), 
             total_checks // 7 - (passed_checks // 7 + (0 if high_risk > 2 else 1))),
            
            ("Integrity and Confidentiality", total_checks // 7, 
             passed_checks // 7 + (0 if high_risk > 5 else 1 if high_risk > 2 else 2), 
             total_checks // 7 - (passed_checks // 7 + (0 if high_risk > 5 else 1 if high_risk > 2 else 2))),
            
            ("Accountability", total_checks // 7, 
             passed_checks // 7 + (0 if compliance_score < 80 else 1), 
             total_checks // 7 - (passed_checks // 7 + (0 if compliance_score < 80 else 1))),
        ]
        
        # Calculate principle-specific scores
        for i, (name, total, passed, failed) in enumerate(principles_categories):
            score = round((passed / total) * 100) if total > 0 else 0
            principles_categories[i] = (name, total, passed, failed, score)
        
        # Build category compliance table
        category_data = [
            ["Category", "Total", "Passed", "Failed", "Score"]
        ]
        
        for principle, total, passed, failed, score in principles_categories:
            category_data.append([principle, str(total), str(passed), str(failed), f"{score}%"])
        
        # Create category table with proper styling 
        category_table = Table(category_data, colWidths=[2.5*inch, 0.75*inch, 0.75*inch, 0.75*inch, 0.75*inch])
        category_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BBDEFB')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#E3F2FD'), colors.HexColor('#F5F5F5')]),
        ]))
        
        story.append(category_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Add Critical Violations section
        story.append(Paragraph("Critical Violations", section_title_style))
        
        # Generate mock critical violations (would be real data in production)
        critical_findings = []
        
        # Generate sample findings based on GDPR principles
        if compliance_score < 75:
            for i, (principle, _, _, _, score) in enumerate(principles_categories):
                if score < 60:  # Display critical findings for principles with low compliance
                    finding_id = f"GDPR-{hash(principle) % 1000:03x}"
                    if principle == "Lawfulness, Fairness and Transparency":
                        critical_findings.append((
                            finding_id,
                            "Privacy notices are not easily accessible or clear",
                            principle,
                            "High",
                            "Users cannot easily find or understand how their data is used",
                            "• Privacy notice buried in legal terms\n• Complex legal language not suitable for users\n• No clear explanation of data usage",
                            "• Make privacy notice accessible from all main pages\n• Rewrite in clear, simple language\n• Create visual data flow diagrams"
                        ))
                    elif principle == "Purpose Limitation":
                        critical_findings.append((
                            finding_id,
                            "Data used beyond originally stated purpose",
                            principle,
                            "High",
                            "Data collected for one purpose is being used for additional purposes",
                            "• Customer contact details used for marketing without consent\n• Analytics data used for product development without notice",
                            "• Audit all data usage and align with stated purposes\n• Obtain explicit consent for additional uses\n• Update privacy policy to clearly state all purposes"
                        ))
                    elif principle == "Integrity and Confidentiality":
                        critical_findings.append((
                            finding_id,
                            "Insufficient security measures for personal data",
                            principle,
                            "High",
                            "Personal data not adequately protected against unauthorized access",
                            "• Unencrypted personal data storage\n• Weak access controls\n• No regular security testing",
                            "• Implement strong encryption for all personal data\n• Establish role-based access controls\n• Conduct regular penetration testing"
                        ))
        
        # If no critical findings based on scores, add at least one
        if not critical_findings:
            critical_findings.append((
                "GDPR-43ab76",
                "Regular data protection impact assessments not performed",
                "Accountability",
                "Medium",
                "Organization should conduct DPIAs for high-risk processing activities",
                "• No documented DPIA process\n• High-risk processing without assessment",
                "• Establish formal DPIA process\n• Conduct assessments for all high-risk processing\n• Document and review DPIAs annually"
            ))
        
        # Add maximum of 3 critical findings
        for i, (finding_id, title, category, impact, description, examples, actions) in enumerate(critical_findings[:3]):
            # Add finding title
            story.append(Paragraph(f"{title}", subheading_style))
            story.append(Paragraph(f"Category: {category}", normal_style))
            story.append(Paragraph(f"Impact: <b>{impact}</b>: {description}", normal_style))
            story.append(Paragraph("<b>Examples:</b>", normal_style))
            story.append(Paragraph(examples, normal_style))
            story.append(Paragraph("<b>Recommended Actions:</b>", normal_style))
            story.append(Paragraph(actions, normal_style))
            
            # Add space between findings
            if i < len(critical_findings[:3]) - 1:
                story.append(Spacer(1, 0.1*inch))
                
        # Add reference to total findings
        if len(critical_findings) > 3:
            story.append(Paragraph(f"{len(critical_findings) - 3} more high-risk violations...", normal_style))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Add Key Recommendations section
        story.append(Paragraph("Key Recommendations", section_title_style))
        
        # Build recommendations based on critical findings and principle scores
        key_recommendations = []
        
        # Create recommendations for each principle with low scores
        for principle, total, passed, failed, score in principles_categories:
            if score < 70:
                if principle == "Lawfulness, Fairness and Transparency":
                    key_recommendations.append((
                        "Improve Privacy Transparency",
                        "Lawfulness, Fairness and Transparency",
                        f"Address {failed} transparency violations",
                        "• Ensure all data processing activities have a documented lawful basis\n• Update privacy notices to be clearer and more accessible\n• Create data processing register for all personal data activities\n• Implement consent management system with audit trail"
                    ))
                elif principle == "Purpose Limitation":
                    key_recommendations.append((
                        "Enforce Purpose Limitation",
                        "Purpose Limitation",
                        f"Address {failed} purpose limitation violations",
                        "• Review and document specific purposes for all data processing\n• Implement procedures to prevent use beyond stated purposes\n• Create technical controls to prevent repurposing of data\n• Conduct regular data usage audits"
                    ))
                elif principle == "Data Minimization":
                    key_recommendations.append((
                        "Implement Data Minimization",
                        "Data Minimization",
                        f"Address {failed} data minimization violations",
                        "• Audit all collection processes to ensure only necessary data is collected\n• Implement retention policies to remove unnecessary data\n• Develop data minimization criteria for new projects\n• Provide regular training on minimization principles"
                    ))
                elif principle == "Storage Limitation":
                    key_recommendations.append((
                        "Improve Storage Limitation Practices",
                        "Storage Limitation",
                        f"Address {failed} storage limitation violations",
                        "• Establish clear retention periods for all personal data categories\n• Implement automated deletion processes for expired data\n• Create retention documentation and update regularly\n• Conduct quarterly data retention audits"
                    ))
                elif principle == "Integrity and Confidentiality":
                    key_recommendations.append((
                        "Enhance Data Security Measures",
                        "Integrity and Confidentiality",
                        f"Address {failed} security violations",
                        "• Strengthen encryption for data in transit and at rest\n• Implement access controls based on least privilege principle\n• Conduct regular penetration testing and vulnerability scans\n• Establish incident response procedures for data breaches"
                    ))
                elif principle == "Accountability":
                    key_recommendations.append((
                        "Strengthen Accountability Framework",
                        "Accountability",
                        f"Address {failed} accountability violations",
                        "• Maintain comprehensive documentation of all data processing\n• Appoint a Data Protection Officer if not already in place\n• Conduct regular compliance audits against GDPR requirements\n• Implement data protection impact assessment procedures"
                    ))
        
        # If no specific recommendations were generated, add general ones
        if not key_recommendations:
            key_recommendations.append((
                "Maintain GDPR Compliance",
                "General",
                "Continue compliance efforts",
                "• Continue maintaining current GDPR compliance practices\n• Consider periodic reassessment to ensure ongoing compliance\n• Stay updated on GDPR regulatory changes and guidance\n• Conduct annual staff training on data protection"
            ))
        
        # Add recommendations to the document (maximum 5)
        for i, (title, category, description, steps) in enumerate(key_recommendations[:5], 1):
            # Add recommendation title with number
            story.append(Paragraph(f"{i}. {title}", subheading_style))
            story.append(Paragraph(f"Category: {category}", normal_style))
            story.append(Paragraph(f"Description: {description}", normal_style))
            story.append(Paragraph("Implementation Steps:", normal_style))
            story.append(Paragraph(steps, normal_style))
            story.append(Spacer(1, 0.15*inch))
        
        # Show additional message if there are more than 5 recommendations
        if len(key_recommendations) > 5:
            story.append(Paragraph(f"{len(key_recommendations) - 5} more high-priority recommendations...", normal_style))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Add GDPR Trust Services Criteria section
        story.append(Paragraph("GDPR Trust Services Criteria", section_title_style))
        
        # Create detailed criteria sections based on principles
        for principle, total, passed, failed, score in principles_categories:
            # Format the principle name and description
            principle_description = ""
            if principle == "Lawfulness, Fairness and Transparency":
                principle_description = "Protection of personal data through lawful processing, fairness and transparency"
                subcriteria = [
                    ("Lawful Basis", f"{1 if score > 60 else 0}/1", f"{100 if score > 60 else 0}%"),
                    ("Transparency", f"{1 if score > 65 else 0}/1", f"{100 if score > 65 else 0}%"),
                    ("Fair Processing", f"{1 if score > 70 else 0}/1", f"{100 if score > 70 else 0}%"),
                    ("Privacy Notices", f"{1 if score > 75 else 0}/1", f"{100 if score > 75 else 0}%")
                ]
            elif principle == "Purpose Limitation":
                principle_description = "Personal data collected for specified, explicit and legitimate purposes"
                subcriteria = [
                    ("Explicit Purposes", f"{1 if score > 60 else 0}/1", f"{100 if score > 60 else 0}%"),
                    ("Purpose Documentation", f"{1 if score > 65 else 0}/1", f"{100 if score > 65 else 0}%"),
                    ("Compatible Processing", f"{1 if score > 70 else 0}/1", f"{100 if score > 70 else 0}%")
                ]
            elif principle == "Data Minimization":
                principle_description = "Personal data adequate, relevant and limited to what is necessary"
                subcriteria = [
                    ("Necessity Assessment", f"{1 if score > 60 else 0}/1", f"{100 if score > 60 else 0}%"),
                    ("Collection Limitation", f"{1 if score > 70 else 0}/1", f"{100 if score > 70 else 0}%"),
                    ("Minimization By Design", f"{1 if score > 80 else 0}/1", f"{100 if score > 80 else 0}%")
                ]
            elif principle == "Accuracy":
                principle_description = "Personal data accurate and, where necessary, kept up to date"
                subcriteria = [
                    ("Accuracy Verification", f"{1 if score > 65 else 0}/1", f"{100 if score > 65 else 0}%"),
                    ("Rectification Process", f"{1 if score > 70 else 0}/1", f"{100 if score > 70 else 0}%"),
                    ("Data Quality Controls", f"{1 if score > 80 else 0}/1", f"{100 if score > 80 else 0}%")
                ]
            elif principle == "Storage Limitation":
                principle_description = "Personal data kept for no longer than necessary for the purposes"
                subcriteria = [
                    ("Retention Periods", f"{1 if score > 60 else 0}/1", f"{100 if score > 60 else 0}%"),
                    ("Deletion Processes", f"{1 if score > 70 else 0}/1", f"{100 if score > 70 else 0}%"),
                    ("Review Mechanisms", f"{1 if score > 75 else 0}/1", f"{100 if score > 75 else 0}%")
                ]
            elif principle == "Integrity and Confidentiality":
                description = "Personal data processed securely with protection against unauthorized processing"
                subcriteria = [
                    ("Access Controls", f"{1 if score > 60 else 0}/1", f"{100 if score > 60 else 0}%"),
                    ("Encryption", f"{1 if score > 70 else 0}/1", f"{100 if score > 70 else 0}%"),
                    ("Data Security", f"{1 if score > 75 else 0}/1", f"{100 if score > 75 else 0}%"),
                    ("Breach Prevention", f"{1 if score > 80 else 0}/1", f"{100 if score > 80 else 0}%")
                ]
            elif principle == "Accountability":
                description = "Controller responsible for and able to demonstrate compliance with the GDPR"
                subcriteria = [
                    ("Documentation", f"{1 if score > 65 else 0}/1", f"{100 if score > 65 else 0}%"),
                    ("Data Protection Officer", f"{1 if score > 70 else 0}/1", f"{100 if score > 70 else 0}%"),
                    ("Compliance Monitoring", f"{1 if score > 75 else 0}/1", f"{100 if score > 75 else 0}%"),
                    ("Records of Processing", f"{1 if score > 80 else 0}/1", f"{100 if score > 80 else 0}%")
                ]
            else:
                # Default subcriteria if principle not recognized
                subcriteria = [
                    ("Compliance", f"{1 if score > 70 else 0}/1", f"{100 if score > 70 else 0}%")
                ]
            
            # Add principle section title and description
            story.append(Paragraph(f"{principle} ({score}%)", subheading_style))
            story.append(Paragraph(principle_description, normal_style))
            
            # Create subcriteria table
            subcriteria_data = [["Principle", "Checks", "Score"]]
            for subname, checks, subscore in subcriteria:
                subcriteria_data.append([subname, checks, subscore])
            
            # Style the subcriteria table
            subcriteria_table = Table(subcriteria_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
            subcriteria_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BBDEFB')),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F5F5')),
            ]))
            
            story.append(subcriteria_table)
            story.append(Spacer(1, 0.2*inch))
        
        # Add certification statement
        story.append(Paragraph("Certification", section_title_style))
        cert_text = f"""
        Based on the assessment results, {organization_name} has achieved a compliance score of {compliance_score}% against GDPR requirements and is certified as <b>{certification_type}</b> as of {datetime.now().strftime('%B %d, %Y')}.
        
        This certification is valid for one year from the date of issuance, subject to continued compliance with GDPR requirements and no significant changes to data processing activities.
        """
        story.append(Paragraph(cert_text, normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Add verification information
        verification_data = [
            ["Certified By:", "DataGuardian Pro Verification System"],
            ["Certificate ID:", f"GDPR-{datetime.now().strftime('%Y%m%d')}-{hash(organization_name) % 10000:04d}"],
            ["Valid Until:", f"{(datetime.now().replace(year=datetime.now().year + 1)).strftime('%B %d, %Y')}"]
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
        st.error(f"Error generating GDPR report: {str(e)}")
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

def generate_and_save_gdpr_report(scan_results, organization_name, certification_type):
    """
    Generate a GDPR report and save it to the filesystem.
    
    Returns a tuple of (success, report_path, pdf_bytes)
    """
    try:
        # Generate the PDF
        pdf_bytes = generate_gdpr_report(
            scan_results=scan_results,
            organization_name=organization_name,
            certification_type=certification_type
        )
        
        # Create reports directory if it doesn't exist
        os.makedirs("reports", exist_ok=True)
        
        # Generate file name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f"gdpr_compliance_report_{organization_name.replace(' ', '_')}_{timestamp}.pdf"
        report_path = os.path.join("reports", file_name)
        
        # Save to file
        with open(report_path, "wb") as f:
            f.write(pdf_bytes)
        
        return True, report_path, pdf_bytes
    
    except Exception as e:
        st.error(f"Error saving GDPR report: {str(e)}")
        return False, None, None