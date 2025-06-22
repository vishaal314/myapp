"""
DPIA Report Generator

Generates professional DPIA reports from collected data in memory.
Supports PDF, HTML, and JSON formats with legal compliance analysis.
"""

import json
from datetime import datetime
from typing import Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import io

class DPIAReportGenerator:
    """
    Generates comprehensive DPIA reports from collected data.
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom styles for the report."""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2E86AB'),
            spaceAfter=20
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1565C0'),
            spaceAfter=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='RiskHigh',
            parent=self.styles['Normal'],
            textColor=colors.red,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='RiskMedium',
            parent=self.styles['Normal'],
            textColor=colors.orange,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='RiskLow',
            parent=self.styles['Normal'],
            textColor=colors.green,
            fontName='Helvetica-Bold'
        ))
    
    def generate_pdf_report(self, report_data: Dict[str, Any]) -> bytes:
        """Generate PDF report from DPIA data."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        
        # Build the report content
        story = []
        
        # Title and header
        self._add_header(story, report_data)
        
        # Executive summary
        self._add_executive_summary(story, report_data)
        
        # Organization information
        self._add_organization_section(story, report_data)
        
        # Processing description
        self._add_processing_section(story, report_data)
        
        # Risk assessment
        self._add_risk_section(story, report_data)
        
        # Compliance analysis
        self._add_compliance_section(story, report_data)
        
        # Recommendations
        self._add_recommendations_section(story, report_data)
        
        # Legal assessment
        self._add_legal_section(story, report_data)
        
        # Conclusion
        self._add_conclusion_section(story, report_data)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _add_header(self, story: list, report_data: Dict[str, Any]):
        """Add report header."""
        exec_summary = report_data.get('executive_summary', {})
        
        story.append(Paragraph("Data Protection Impact Assessment Report", self.styles['CustomTitle']))
        story.append(Paragraph(f"<b>Organization:</b> {exec_summary.get('organization', 'N/A')}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Assessment Date:</b> {exec_summary.get('assessment_date', 'N/A')}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Report ID:</b> {report_data.get('report_id', 'N/A')}", self.styles['Normal']))
        story.append(Spacer(1, 20))
    
    def _add_executive_summary(self, story: list, report_data: Dict[str, Any]):
        """Add executive summary section."""
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        exec_summary = report_data.get('executive_summary', {})
        risk_level = exec_summary.get('overall_risk_level', 'medium')
        
        # Risk level with color coding
        risk_style = self.styles[f'Risk{risk_level.capitalize()}'] if risk_level in ['high', 'medium', 'low'] else self.styles['Normal']
        story.append(Paragraph(f"<b>Overall Risk Level:</b> ", self.styles['Normal']))
        story.append(Paragraph(f"{risk_level.upper()}", risk_style))
        
        story.append(Paragraph(f"<b>DPIA Required:</b> {'Yes' if exec_summary.get('dpia_required', True) else 'No'}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Compliance Status:</b> {exec_summary.get('compliance_status', 'Unknown')}", self.styles['Normal']))
        story.append(Spacer(1, 12))
    
    def _add_organization_section(self, story: list, report_data: Dict[str, Any]):
        """Add organization information section."""
        story.append(Paragraph("1. Organization Information", self.styles['SectionHeader']))
        
        org_info = report_data.get('organization_info', {})
        if org_info:
            for key, value in org_info.items():
                if value:
                    formatted_key = key.replace('_', ' ').title()
                    story.append(Paragraph(f"<b>{formatted_key}:</b> {value}", self.styles['Normal']))
        else:
            story.append(Paragraph("No organization information available.", self.styles['Normal']))
        
        story.append(Spacer(1, 12))
    
    def _add_processing_section(self, story: list, report_data: Dict[str, Any]):
        """Add processing description section."""
        story.append(Paragraph("2. Data Processing Description", self.styles['SectionHeader']))
        
        processing = report_data.get('processing_description', {})
        if processing:
            if processing.get('processing_purpose'):
                story.append(Paragraph(f"<b>Purpose:</b> {processing['processing_purpose']}", self.styles['Normal']))
            
            if processing.get('data_categories'):
                story.append(Paragraph("<b>Data Categories:</b>", self.styles['Normal']))
                for category in processing['data_categories']:
                    story.append(Paragraph(f"• {category}", self.styles['Normal']))
            
            if processing.get('data_subjects'):
                story.append(Paragraph("<b>Data Subjects:</b>", self.styles['Normal']))
                for subject in processing['data_subjects']:
                    story.append(Paragraph(f"• {subject}", self.styles['Normal']))
        else:
            story.append(Paragraph("No processing description available.", self.styles['Normal']))
        
        story.append(Spacer(1, 12))
    
    def _add_risk_section(self, story: list, report_data: Dict[str, Any]):
        """Add risk assessment section."""
        story.append(Paragraph("3. Risk Assessment", self.styles['SectionHeader']))
        
        risk_summary = report_data.get('risk_summary', {})
        if risk_summary:
            # Overall risk
            overall_risk = risk_summary.get('overall_risk', 'medium')
            risk_style = self.styles[f'Risk{overall_risk.capitalize()}'] if overall_risk in ['high', 'medium', 'low'] else self.styles['Normal']
            story.append(Paragraph(f"<b>Overall Risk Level:</b> ", self.styles['Normal']))
            story.append(Paragraph(f"{overall_risk.upper()}", risk_style))
            
            # High risk factors
            high_risk_factors = risk_summary.get('high_risk_factors', [])
            if high_risk_factors:
                story.append(Paragraph("<b>High Risk Factors Identified:</b>", self.styles['Normal']))
                for factor in high_risk_factors:
                    story.append(Paragraph(f"⚠ {factor}", self.styles['RiskHigh']))
            
            # Risk count
            risk_count = risk_summary.get('risk_count', {})
            if risk_count:
                story.append(Paragraph("<b>Risk Distribution:</b>", self.styles['Normal']))
                story.append(Paragraph(f"High Risk Issues: {risk_count.get('high', 0)}", self.styles['RiskHigh']))
                story.append(Paragraph(f"Medium Risk Issues: {risk_count.get('medium', 0)}", self.styles['RiskMedium']))
                story.append(Paragraph(f"Low Risk Issues: {risk_count.get('low', 0)}", self.styles['RiskLow']))
        else:
            story.append(Paragraph("No risk assessment data available.", self.styles['Normal']))
        
        story.append(Spacer(1, 12))
    
    def _add_compliance_section(self, story: list, report_data: Dict[str, Any]):
        """Add compliance analysis section."""
        story.append(Paragraph("4. Compliance Analysis", self.styles['SectionHeader']))
        
        compliance = report_data.get('compliance_analysis', {})
        if compliance:
            # Create compliance table
            compliance_data = [
                ['Regulation', 'Score', 'Status'],
                ['GDPR', f"{compliance.get('gdpr_score', 0)}%", 'Compliant' if compliance.get('gdpr_score', 0) >= 80 else 'Non-Compliant'],
                ['Dutch UAVG', f"{compliance.get('uavg_score', 0)}%", 'Compliant' if compliance.get('uavg_score', 0) >= 80 else 'Non-Compliant'],
                ['EU AI Act', f"{compliance.get('ai_act_score', 0)}%", 'Compliant' if compliance.get('ai_act_score', 0) >= 80 else 'Non-Compliant']
            ]
            
            compliance_table = Table(compliance_data, colWidths=[2*inch, 1*inch, 1.5*inch])
            compliance_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(compliance_table)
            story.append(Spacer(1, 12))
            
            # Overall status
            can_proceed = compliance.get('can_proceed', False)
            status_style = self.styles['RiskLow'] if can_proceed else self.styles['RiskHigh']
            story.append(Paragraph(f"<b>Can Proceed with Processing:</b> ", self.styles['Normal']))
            story.append(Paragraph(f"{'YES' if can_proceed else 'NO'}", status_style))
        else:
            story.append(Paragraph("No compliance analysis available.", self.styles['Normal']))
        
        story.append(Spacer(1, 12))
    
    def _add_recommendations_section(self, story: list, report_data: Dict[str, Any]):
        """Add recommendations section."""
        story.append(Paragraph("5. Recommendations", self.styles['SectionHeader']))
        
        recommendations = report_data.get('recommendations', [])
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                priority = rec.get('priority', 'medium')
                priority_style = self.styles[f'Risk{priority.capitalize()}'] if priority in ['high', 'medium', 'low'] else self.styles['Normal']
                
                story.append(Paragraph(f"<b>{i}. {rec.get('category', 'General')} [{priority.upper()} PRIORITY]</b>", priority_style))
                story.append(Paragraph(f"{rec.get('recommendation', 'No recommendation provided')}", self.styles['Normal']))
                if rec.get('regulation'):
                    story.append(Paragraph(f"<i>Legal basis: {rec['regulation']}</i>", self.styles['Normal']))
                story.append(Spacer(1, 8))
        else:
            story.append(Paragraph("No specific recommendations generated.", self.styles['Normal']))
        
        story.append(Spacer(1, 12))
    
    def _add_legal_section(self, story: list, report_data: Dict[str, Any]):
        """Add legal assessment section."""
        story.append(Paragraph("6. Legal Assessment", self.styles['SectionHeader']))
        
        legal_assessment = report_data.get('legal_assessment', {})
        if legal_assessment:
            story.append(Paragraph(f"<b>GDPR Compliance Score:</b> {legal_assessment.get('gdpr_compliance_score', 0)}%", self.styles['Normal']))
            story.append(Paragraph(f"<b>UAVG Compliance Score:</b> {legal_assessment.get('uavg_compliance_score', 0)}%", self.styles['Normal']))
            story.append(Paragraph(f"<b>EU AI Act Score:</b> {legal_assessment.get('eu_ai_act_score', 0)}%", self.styles['Normal']))
            
            police_act = legal_assessment.get('police_act_compliance', False)
            story.append(Paragraph(f"<b>Police Act Compliance:</b> {'Yes' if police_act else 'No'}", self.styles['Normal']))
        else:
            story.append(Paragraph("No legal assessment data available.", self.styles['Normal']))
        
        story.append(Spacer(1, 12))
    
    def _add_conclusion_section(self, story: list, report_data: Dict[str, Any]):
        """Add conclusion section."""
        story.append(Paragraph("7. Conclusion", self.styles['SectionHeader']))
        
        conclusion = report_data.get('conclusion', {})
        if conclusion:
            can_proceed = conclusion.get('can_proceed', False)
            status_style = self.styles['RiskLow'] if can_proceed else self.styles['RiskHigh']
            
            story.append(Paragraph("Based on this DPIA assessment:", self.styles['Normal']))
            story.append(Paragraph(f"<b>Processing can proceed:</b> ", self.styles['Normal']))
            story.append(Paragraph(f"{'YES' if can_proceed else 'NO'}", status_style))
            
            if conclusion.get('additional_measures_required'):
                story.append(Paragraph("<b>Additional measures required:</b> Yes", self.styles['RiskMedium']))
            
            if conclusion.get('review_required'):
                story.append(Paragraph("<b>Regular review required:</b> Yes", self.styles['RiskMedium']))
            
            if conclusion.get('dpo_consultation_required'):
                story.append(Paragraph("<b>DPO consultation required:</b> Yes", self.styles['Normal']))
        else:
            story.append(Paragraph("No conclusion data available.", self.styles['Normal']))
        
        # Footer
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.styles['Normal']))
        story.append(Paragraph("This report is generated based on the information provided and should be reviewed by a qualified data protection professional.", self.styles['Normal']))
    
    def generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML report from DPIA data."""
        exec_summary = report_data.get('executive_summary', {})
        compliance = report_data.get('compliance_analysis', {})
        risk_summary = report_data.get('risk_summary', {})
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>DPIA Report - {exec_summary.get('organization', 'Organization')}</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 1000px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #2E86AB, #1565C0); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; margin: -30px -30px 30px -30px; }}
                .section {{ margin: 30px 0; padding: 20px; border-left: 4px solid #2E86AB; background-color: #f9f9f9; }}
                .metric {{ display: inline-block; margin: 10px; padding: 15px; background-color: #e3f2fd; border-radius: 8px; text-align: center; }}
                .risk-high {{ color: #d32f2f; font-weight: bold; }}
                .risk-medium {{ color: #f57c00; font-weight: bold; }}
                .risk-low {{ color: #388e3c; font-weight: bold; }}
                .compliance-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                .compliance-table th, .compliance-table td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                .compliance-table th {{ background-color: #2E86AB; color: white; }}
                .recommendation {{ background-color: #fff3e0; padding: 15px; margin: 10px 0; border-left: 4px solid #ff9800; }}
                .footer {{ margin-top: 40px; padding-top: 20px; border-top: 2px solid #2E86AB; font-size: 0.9em; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Data Protection Impact Assessment Report</h1>
                    <h2>{exec_summary.get('organization', 'Organization Name')}</h2>
                    <p>Assessment Date: {exec_summary.get('assessment_date', 'Unknown Date')}</p>
                    <p>Report ID: {report_data.get('report_id', 'Unknown')}</p>
                </div>
                
                <div class="section">
                    <h2>Executive Summary</h2>
                    <div class="metric">
                        <strong>Overall Risk Level</strong><br>
                        <span class="risk-{exec_summary.get('overall_risk_level', 'medium')}">{exec_summary.get('overall_risk_level', 'Medium').upper()}</span>
                    </div>
                    <div class="metric">
                        <strong>DPIA Required</strong><br>
                        {'Yes' if exec_summary.get('dpia_required', True) else 'No'}
                    </div>
                    <div class="metric">
                        <strong>Can Proceed</strong><br>
                        <span class="{'risk-low' if compliance.get('can_proceed', False) else 'risk-high'}">
                            {'Yes' if compliance.get('can_proceed', False) else 'No'}
                        </span>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Compliance Analysis</h2>
                    <table class="compliance-table">
                        <tr>
                            <th>Regulation</th>
                            <th>Score</th>
                            <th>Status</th>
                        </tr>
                        <tr>
                            <td>GDPR</td>
                            <td>{compliance.get('gdpr_score', 0)}%</td>
                            <td class="{'risk-low' if compliance.get('gdpr_score', 0) >= 80 else 'risk-high'}">
                                {'Compliant' if compliance.get('gdpr_score', 0) >= 80 else 'Non-Compliant'}
                            </td>
                        </tr>
                        <tr>
                            <td>Dutch UAVG</td>
                            <td>{compliance.get('uavg_score', 0)}%</td>
                            <td class="{'risk-low' if compliance.get('uavg_score', 0) >= 80 else 'risk-high'}">
                                {'Compliant' if compliance.get('uavg_score', 0) >= 80 else 'Non-Compliant'}
                            </td>
                        </tr>
                        <tr>
                            <td>EU AI Act</td>
                            <td>{compliance.get('ai_act_score', 0)}%</td>
                            <td class="{'risk-low' if compliance.get('ai_act_score', 0) >= 80 else 'risk-high'}">
                                {'Compliant' if compliance.get('ai_act_score', 0) >= 80 else 'Non-Compliant'}
                            </td>
                        </tr>
                    </table>
                </div>
        """
        
        # Add risk factors
        high_risk_factors = risk_summary.get('high_risk_factors', [])
        if high_risk_factors:
            html += """
                <div class="section">
                    <h2>High Risk Factors Identified</h2>
                    <ul>
            """
            for factor in high_risk_factors:
                html += f'<li class="risk-high">⚠ {factor}</li>'
            html += "</ul></div>"
        
        # Add recommendations
        recommendations = report_data.get('recommendations', [])
        if recommendations:
            html += """
                <div class="section">
                    <h2>Recommendations</h2>
            """
            for i, rec in enumerate(recommendations, 1):
                priority_class = f"risk-{rec.get('priority', 'medium')}"
                html += f"""
                    <div class="recommendation">
                        <h4 class="{priority_class}">{i}. {rec.get('category', 'General')} [{rec.get('priority', 'medium').upper()} PRIORITY]</h4>
                        <p>{rec.get('recommendation', 'No recommendation provided')}</p>
                        {f"<small><i>Legal basis: {rec['regulation']}</i></small>" if rec.get('regulation') else ''}
                    </div>
                """
            html += "</div>"
        
        # Add conclusion
        conclusion = report_data.get('conclusion', {})
        if conclusion:
            html += f"""
                <div class="section">
                    <h2>Conclusion</h2>
                    <p><strong>Processing can proceed:</strong> 
                        <span class="{'risk-low' if conclusion.get('can_proceed', False) else 'risk-high'}">
                            {'YES' if conclusion.get('can_proceed', False) else 'NO'}
                        </span>
                    </p>
                    {'<p><strong>Additional measures required:</strong> <span class="risk-medium">Yes</span></p>' if conclusion.get('additional_measures_required') else ''}
                    {'<p><strong>Regular review required:</strong> <span class="risk-medium">Yes</span></p>' if conclusion.get('review_required') else ''}
                    {'<p><strong>DPO consultation required:</strong> Yes</p>' if conclusion.get('dpo_consultation_required') else ''}
                </div>
            """
        
        html += f"""
                <div class="footer">
                    <p><strong>Report Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>DPIA Version:</strong> {report_data.get('dpia_version', '2.0')}</p>
                    <p><em>This report is generated based on the information provided and should be reviewed by a qualified data protection professional.</em></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def generate_json_report(self, report_data: Dict[str, Any]) -> str:
        """Generate JSON report from DPIA data."""
        return json.dumps(report_data, indent=2, default=str)