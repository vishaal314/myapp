import io
from typing import Dict, Any, List, Optional
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak

def generate_report(scan_data: Dict[str, Any], 
                   include_details: bool = True,
                   include_charts: bool = True,
                   include_metadata: bool = True,
                   include_recommendations: bool = True) -> bytes:
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
    
    # Create PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading1']
    subheading_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Custom styles
    warning_style = ParagraphStyle(
        'Warning',
        parent=normal_style,
        textColor=colors.orange
    )
    
    danger_style = ParagraphStyle(
        'Danger',
        parent=normal_style,
        textColor=colors.red
    )
    
    # Content elements
    elements = []
    
    # Title
    elements.append(Paragraph('GDPR Compliance Scan Report', title_style))
    
    # Current date
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    elements.append(Paragraph(f"Generated on: {current_date}", normal_style))
    elements.append(Spacer(1, 12))
    
    # Scan ID
    scan_id = scan_data.get('scan_id', 'Unknown')
    elements.append(Paragraph(f"Scan ID: {scan_id}", normal_style))
    elements.append(Spacer(1, 20))
    
    # Summary section
    elements.append(Paragraph('Summary', heading_style))
    
    # Summary data
    scan_type = scan_data.get('scan_type', 'Unknown')
    region = scan_data.get('region', 'Unknown')
    total_pii = scan_data.get('total_pii_found', 0)
    high_risk = scan_data.get('high_risk_count', 0)
    timestamp = scan_data.get('timestamp', 'Unknown')
    
    # Get URL information
    url = scan_data.get('url', scan_data.get('domain', 'Not available'))
    
    if timestamp != 'Unknown':
        try:
            timestamp = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        except:
            pass
    
    # Summary table
    summary_data = [
        ['Scan Type', scan_type],
        ['Region', region],
        ['Date & Time', timestamp],
        ['Scanned URL/Domain', url],
        ['Total PII Items Found', str(total_pii)],
        ['High Risk Items', str(high_risk)]
    ]
    
    summary_table = Table(summary_data, colWidths=[150, 300])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 20))
    
    # Risk assessment
    elements.append(Paragraph('Risk Assessment', heading_style))
    
    # Determine overall risk level
    if high_risk > 10:
        risk_level = "High"
        risk_color = colors.red
        risk_text = "This scan has identified a high number of high-risk PII items. Immediate action is recommended."
    elif high_risk > 0:
        risk_level = "Medium"
        risk_color = colors.orange
        risk_text = "This scan has identified some high-risk PII items that should be addressed."
    elif total_pii > 0:
        risk_level = "Low"
        risk_color = colors.green
        risk_text = "This scan has identified PII items, but none are classified as high risk."
    else:
        risk_level = "None"
        risk_color = colors.green
        risk_text = "No PII items were found in this scan."
    
    # Risk level paragraph
    risk_style = ParagraphStyle(
        'Risk',
        parent=normal_style,
        textColor=risk_color,
        fontSize=12,
        fontName='Helvetica-Bold'
    )
    
    elements.append(Paragraph(f"Overall Risk Level: {risk_level}", risk_style))
    elements.append(Paragraph(risk_text, normal_style))
    elements.append(Spacer(1, 12))
    
    # Include charts if requested
    if include_charts and (
        ('pii_types' in scan_data and scan_data['pii_types']) or
        ('risk_levels' in scan_data and scan_data['risk_levels'])
    ):
        elements.append(Paragraph('Data Analysis', heading_style))
        
        # Create charts in memory
        if 'pii_types' in scan_data and scan_data['pii_types']:
            # PII types chart
            elements.append(Paragraph('PII Types Distribution', subheading_style))
            
            # Create PII types table
            pii_types = scan_data.get('pii_types', {})
            if pii_types:
                pii_data = [['PII Type', 'Count']]
                for pii_type, count in pii_types.items():
                    pii_data.append([pii_type, str(count)])
                
                pii_table = Table(pii_data, colWidths=[300, 150])
                pii_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey)
                ]))
                
                elements.append(pii_table)
                elements.append(Spacer(1, 12))
        
        if 'risk_levels' in scan_data and scan_data['risk_levels']:
            # Risk levels chart
            elements.append(Paragraph('Risk Level Distribution', subheading_style))
            
            # Create risk levels table
            risk_levels = scan_data.get('risk_levels', {})
            if risk_levels:
                risk_data = [['Risk Level', 'Count']]
                for risk_level, count in risk_levels.items():
                    risk_data.append([risk_level, str(count)])
                
                risk_table = Table(risk_data, colWidths=[300, 150])
                risk_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey)
                ]))
                
                elements.append(risk_table)
                elements.append(Spacer(1, 12))
    
    # Include detailed findings if requested
    if include_details and 'detailed_results' in scan_data and scan_data['detailed_results']:
        elements.append(PageBreak())
        elements.append(Paragraph('Detailed Findings', heading_style))
        
        # Extract all PII items from all files
        all_pii_items = []
        for file_result in scan_data['detailed_results']:
            file_name = file_result.get('file_name', 'Unknown')
            
            for pii_item in file_result.get('pii_found', []):
                pii_item_data = [
                    file_name,
                    pii_item.get('type', 'Unknown'),
                    pii_item.get('value', 'Unknown'),
                    pii_item.get('location', 'Unknown'),
                    pii_item.get('risk_level', 'Unknown')
                ]
                all_pii_items.append(pii_item_data)
        
        if all_pii_items:
            # Create detailed findings table
            detailed_data = [['File', 'PII Type', 'Value', 'Location', 'Risk Level']]
            detailed_data.extend(all_pii_items)
            
            detailed_table = Table(detailed_data, colWidths=[80, 80, 150, 80, 80])
            
            # Define row styles based on risk level
            row_styles = []
            for i, item in enumerate(all_pii_items, 1):  # Starting from 1 to account for header
                risk_level = item[4]
                if risk_level == 'High':
                    bg_color = colors.pink
                elif risk_level == 'Medium':
                    bg_color = colors.lightgoldenrodyellow
                else:  # Low
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
            elements.append(Paragraph("No detailed findings available.", normal_style))
    
    # Include recommendations if requested
    if include_recommendations:
        elements.append(PageBreak())
        elements.append(Paragraph('Recommendations & Next Steps', heading_style))
        
        # General recommendations
        recommendations = [
            "Ensure you have proper legal basis for processing all identified PII.",
            "Document all processing activities as required by GDPR Article 30.",
            "Review data retention policies to ensure PII is not kept longer than necessary.",
            "Implement appropriate technical and organizational measures to secure PII."
        ]
        
        for recommendation in recommendations:
            elements.append(Paragraph(f"• {recommendation}", normal_style))
        
        elements.append(Spacer(1, 12))
        
        # Risk-specific recommendations
        if high_risk > 0:
            elements.append(Paragraph('High-Risk Item Recommendations', subheading_style))
            
            high_risk_recommendations = [
                "Conduct a Data Protection Impact Assessment (DPIA) for high-risk processing activities.",
                "Review and strengthen access controls for systems containing high-risk PII.",
                "Consider pseudonymization or encryption for high-risk data.",
                "Ensure processors handling this data have appropriate data processing agreements."
            ]
            
            for recommendation in high_risk_recommendations:
                elements.append(Paragraph(f"• {recommendation}", danger_style))
            
            elements.append(Spacer(1, 12))
        
        # Region-specific recommendations
        if region == "Netherlands":
            elements.append(Paragraph('Netherlands-Specific Recommendations', subheading_style))
            
            nl_recommendations = [
                "Ensure parental consent for processing personal data of children under 16.",
                "Follow Dutch DPA (Autoriteit Persoonsgegevens) guidelines for breach notification within 72 hours.",
                "Adhere to specific rules regarding BSN processing under UAVG.",
                "Implement appropriate controls for processing medical data as per UAVG requirements."
            ]
            
            for recommendation in nl_recommendations:
                elements.append(Paragraph(f"• {recommendation}", normal_style))
    
    # Include metadata if requested
    if include_metadata:
        elements.append(PageBreak())
        elements.append(Paragraph('Scan Metadata', heading_style))
        
        # Collect metadata
        metadata = {
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
        for key, value in metadata.items():
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
        
        disclaimer_text = (
            "Disclaimer: This report is provided for informational purposes only and should not "
            "be considered legal advice. The findings in this report are based on automated "
            "scanning and may not identify all GDPR-relevant personal data. We recommend "
            "consulting with a qualified legal professional for specific GDPR compliance guidance."
        )
        
        elements.append(Paragraph(disclaimer_text, disclaimer_style))
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes
