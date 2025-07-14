"""
Document Report Generator for DataGuardian Pro

This module generates professional certificate-style reports for document scans,
matching the comprehensive reporting structure of the Image Scanner.
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_document_html_report(scan_results: Dict[str, Any]) -> str:
    """
    Generate a comprehensive HTML report for document scan results.
    
    Args:
        scan_results: Dictionary containing document scan results
        
    Returns:
        HTML report as string
    """
    # Extract scan metadata
    metadata = scan_results.get('metadata', {})
    findings = scan_results.get('findings', [])
    risk_summary = scan_results.get('risk_summary', {})
    documents_scanned = len(scan_results.get('document_results', []))
    
    # Calculate statistics including critical risk
    total_findings = len(findings)
    critical_risk_count = len([f for f in findings if f.get('risk_level') == 'Critical'])
    high_risk_count = len([f for f in findings if f.get('risk_level') == 'High'])
    medium_risk_count = len([f for f in findings if f.get('risk_level') == 'Medium'])
    low_risk_count = len([f for f in findings if f.get('risk_level') == 'Low'])
    
    # Generate timestamp
    scan_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DataGuardian Pro - Document Compliance Report</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                background-color: #f8fafc;
                color: #2d3748;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 2rem;
                border-radius: 15px;
                text-align: center;
                margin-bottom: 2rem;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            }}
            .certificate-seal {{
                width: 80px;
                height: 80px;
                background: rgba(255,255,255,0.2);
                border-radius: 50%;
                margin: 0 auto 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 2em;
                backdrop-filter: blur(10px);
            }}
            .header h1 {{
                margin: 0;
                font-size: 2.5em;
                font-weight: 700;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }}
            .header p {{
                margin: 10px 0 0 0;
                font-size: 1.2em;
                opacity: 0.9;
            }}
            .summary-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 2rem;
            }}
            .summary-card {{
                background: white;
                padding: 1.5rem;
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                text-align: center;
                border-left: 4px solid #667eea;
            }}
            .summary-card.high-risk {{
                border-left-color: #e53e3e;
            }}
            .summary-card.medium-risk {{
                border-left-color: #ed8936;
            }}
            .summary-card.low-risk {{
                border-left-color: #38a169;
            }}
            .summary-card h3 {{
                margin: 0 0 10px 0;
                color: #4a5568;
                font-size: 0.9em;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .summary-card .number {{
                font-size: 2.5em;
                font-weight: bold;
                color: #2d3748;
                margin: 0;
            }}
            .section {{
                background: white;
                padding: 2rem;
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                margin-bottom: 2rem;
            }}
            .section h2 {{
                margin: 0 0 1.5rem 0;
                color: #2d3748;
                border-bottom: 2px solid #e2e8f0;
                padding-bottom: 10px;
                font-size: 1.5em;
            }}
            .findings-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 1rem;
            }}
            .findings-table th,
            .findings-table td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #e2e8f0;
            }}
            .findings-table th {{
                background-color: #f7fafc;
                font-weight: 600;
                color: #4a5568;
            }}
            .risk-badge {{
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.8em;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .risk-high {{
                background-color: #fed7d7;
                color: #c53030;
            }}
            .risk-medium {{
                background-color: #feebc8;
                color: #d69e2e;
            }}
            .risk-low {{
                background-color: #c6f6d5;
                color: #2f855a;
            }}
            .gdpr-categories {{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin-top: 1rem;
            }}
            .gdpr-category {{
                background: #edf2f7;
                color: #4a5568;
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 0.9em;
                font-weight: 500;
            }}
            .footer {{
                text-align: center;
                margin-top: 3rem;
                padding: 2rem;
                background: #2d3748;
                color: white;
                border-radius: 12px;
            }}
            .footer p {{
                margin: 5px 0;
                opacity: 0.8;
            }}
            .compliance-note {{
                background: #e6fffa;
                border-left: 4px solid #38b2ac;
                padding: 1rem;
                margin: 1rem 0;
                border-radius: 4px;
            }}
            @media print {{
                body {{ background: white; }}
                .header {{ background: #667eea !important; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="certificate-seal">🛡️</div>
            <h1>DataGuardian Pro</h1>
            <p>Document Privacy Compliance Certificate</p>
            <p>Generated on {scan_date}</p>
        </div>

        <div class="summary-grid">
            <div class="summary-card">
                <h3>Documents Scanned</h3>
                <div class="number">{documents_scanned}</div>
            </div>
            <div class="summary-card">
                <h3>Total Findings</h3>
                <div class="number">{total_findings}</div>
            </div>
            <div class="summary-card high-risk">
                <h3>High Risk</h3>
                <div class="number">{high_risk_count}</div>
            </div>
            <div class="summary-card medium-risk">
                <h3>Medium Risk</h3>
                <div class="number">{medium_risk_count}</div>
            </div>
            <div class="summary-card low-risk">
                <h3>Low Risk</h3>
                <div class="number">{low_risk_count}</div>
            </div>
        </div>

        <div class="section">
            <h2>📋 Scan Overview</h2>
            <p><strong>Scan Type:</strong> Document Privacy Assessment</p>
            <p><strong>Region:</strong> {metadata.get('region', 'Netherlands')}</p>
            <p><strong>Compliance Framework:</strong> GDPR / Dutch UAVG</p>
            <p><strong>Risk Level:</strong> 
                <span class="risk-badge risk-{risk_summary.get('level', 'low').lower()}">{risk_summary.get('level', 'Low')}</span>
            </p>
        </div>
    """
    
    if findings:
        html_content += """
        <div class="section">
            <h2>🔍 Detailed Findings</h2>
            <table class="findings-table">
                <thead>
                    <tr>
                        <th>Document</th>
                        <th>PII Type</th>
                        <th>Value</th>
                        <th>Location</th>
                        <th>Risk Level</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for finding in findings[:50]:  # Limit to first 50 findings
            pii_type = finding.get('type', 'Unknown')
            value = finding.get('value', 'N/A')[:50] + '...' if len(finding.get('value', '')) > 50 else finding.get('value', 'N/A')
            location = finding.get('location', 'Unknown')
            risk_level = finding.get('risk_level', 'Medium')
            source = finding.get('source', 'Unknown')
            
            html_content += f"""
                    <tr>
                        <td>{os.path.basename(source)}</td>
                        <td>{pii_type}</td>
                        <td><code>{value}</code></td>
                        <td>{location}</td>
                        <td><span class="risk-badge risk-{risk_level.lower()}">{risk_level}</span></td>
                    </tr>
            """
        
        if len(findings) > 50:
            html_content += f"""
                    <tr>
                        <td colspan="5" style="text-align: center; font-style: italic; color: #666;">
                            ... and {len(findings) - 50} more findings (download full report for complete details)
                        </td>
                    </tr>
            """
        
        html_content += """
                </tbody>
            </table>
        </div>
        """
    
    # GDPR Categories section
    all_gdpr_categories = set()
    for result in scan_results.get('document_results', []):
        all_gdpr_categories.update(result.get('gdpr_categories', []))
    
    if all_gdpr_categories:
        html_content += """
        <div class="section">
            <h2>⚖️ GDPR Data Categories</h2>
            <div class="gdpr-categories">
        """
        for category in sorted(all_gdpr_categories):
            html_content += f'<div class="gdpr-category">{category}</div>'
        
        html_content += """
            </div>
        </div>
        """
    
    # Compliance Notes section
    all_compliance_notes = []
    for result in scan_results.get('document_results', []):
        all_compliance_notes.extend(result.get('compliance_notes', []))
    
    if all_compliance_notes:
        html_content += """
        <div class="section">
            <h2>📝 Compliance Notes</h2>
        """
        for note in sorted(set(all_compliance_notes))[:10]:  # Unique notes, max 10
            html_content += f'<div class="compliance-note">{note}</div>'
        
        html_content += """
        </div>
        """
    
    html_content += f"""
        <div class="footer">
            <p><strong>DataGuardian Pro</strong> - Enterprise Privacy Compliance Platform</p>
            <p>Report generated on {scan_date}</p>
            <p>© 2025 GDPR Scan Engine - Secure • Compliant • Reliable</p>
        </div>
    </body>
    </html>
    """
    
    return html_content

def generate_document_pdf_report(scan_results: Dict[str, Any]) -> bytes:
    """
    Generate a professional PDF report for document scan results.
    
    Args:
        scan_results: Dictionary containing document scan results
        
    Returns:
        PDF content as bytes
    """
    import io
    try:
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2d3748'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=14,
            spaceAfter=20,
            textColor=colors.HexColor('#4a5568'),
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=12,
            textColor=colors.HexColor('#2d3748'),
            fontName='Helvetica-Bold'
        )
        
        # Header
        story.append(Paragraph("🛡️ DataGuardian Pro", title_style))
        story.append(Paragraph("Document Privacy Compliance Certificate", subtitle_style))
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", subtitle_style))
        story.append(Spacer(1, 20))
        
        # Summary section
        findings = scan_results.get('findings', [])
        documents_scanned = len(scan_results.get('document_results', []))
        risk_summary = scan_results.get('risk_summary', {})
        
        summary_data = [
            ['Metric', 'Value'],
            ['Documents Scanned', str(documents_scanned)],
            ['Total Findings', str(len(findings))],
            ['High Risk Findings', str(len([f for f in findings if f.get('risk_level') == 'High']))],
            ['Medium Risk Findings', str(len([f for f in findings if f.get('risk_level') == 'Medium']))],
            ['Low Risk Findings', str(len([f for f in findings if f.get('risk_level') == 'Low']))],
            ['Overall Risk Level', risk_summary.get('level', 'Low')]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f7fafc')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0'))
        ]))
        
        story.append(Paragraph("📊 Scan Summary", section_style))
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Findings section (if any)
        if findings:
            story.append(Paragraph("🔍 Key Findings", section_style))
            
            findings_data = [['Document', 'PII Type', 'Risk Level', 'Location']]
            for finding in findings[:20]:  # Limit to first 20 findings
                source = os.path.basename(finding.get('source', 'Unknown'))[:30]
                pii_type = finding.get('type', 'Unknown')[:20]
                risk_level = finding.get('risk_level', 'Medium')
                location = finding.get('location', 'Unknown')[:30]
                
                findings_data.append([source, pii_type, risk_level, location])
            
            findings_table = Table(findings_data, colWidths=[1.5*inch, 1.5*inch, 1*inch, 2*inch])
            findings_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f7fafc')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0'))
            ]))
            
            story.append(findings_table)
            
            if len(findings) > 20:
                story.append(Spacer(1, 10))
                story.append(Paragraph(f"<i>... and {len(findings) - 20} more findings</i>", styles['Normal']))
        
        # GDPR Categories
        all_gdpr_categories = set()
        for result in scan_results.get('document_results', []):
            all_gdpr_categories.update(result.get('gdpr_categories', []))
        
        if all_gdpr_categories:
            story.append(Spacer(1, 20))
            story.append(Paragraph("⚖️ GDPR Data Categories", section_style))
            for category in sorted(all_gdpr_categories):
                story.append(Paragraph(f"• {category}", styles['Normal']))
        
        # Compliance Notes
        all_compliance_notes = []
        for result in scan_results.get('document_results', []):
            all_compliance_notes.extend(result.get('compliance_notes', []))
        
        if all_compliance_notes:
            story.append(Spacer(1, 20))
            story.append(Paragraph("📝 Compliance Notes", section_style))
            for note in sorted(set(all_compliance_notes))[:10]:
                story.append(Paragraph(f"• {note}", styles['Normal']))
        
        # Footer
        story.append(Spacer(1, 40))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#4a5568'),
            alignment=TA_CENTER
        )
        
        story.append(Paragraph("DataGuardian Pro - Enterprise Privacy Compliance Platform", footer_style))
        story.append(Paragraph("© 2025 GDPR Scan Engine - Secure • Compliant • Reliable", footer_style))
        
        # Build the PDF
        doc.build(story)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        logger.info("Generated PDF report successfully")
        return pdf_bytes
        
    except Exception as e:
        logger.error(f"Error generating PDF report: {str(e)}")
        raise

def create_document_scanner(region: str = "Netherlands"):
    """Factory function to create DocumentScanner instance for compatibility."""
    from services.blob_scanner import BlobScanner
    return BlobScanner(region=region)