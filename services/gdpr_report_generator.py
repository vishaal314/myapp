"""
GDPR Report Generator

This module provides functionality to generate comprehensive GDPR compliance reports
in PDF format for repository scan results.
"""

import os
import time
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Configure logging
logger = logging.getLogger(__name__)

class GDPRReportGenerator:
    """
    Generates comprehensive GDPR compliance reports for repository scan results.
    """
    
    def __init__(self, output_dir: str = "reports"):
        """
        Initialize the report generator.
        
        Args:
            output_dir: Directory where reports will be saved
        """
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Initialize styles
        self.styles = getSampleStyleSheet()
        self._initialize_custom_styles()
    
    def _initialize_custom_styles(self):
        """Initialize custom paragraph styles for the report."""
        # Add custom styles
        self.styles.add(ParagraphStyle(
            name='Title',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=12,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=10,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=8,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='HighRisk',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.red
        ))
        
        self.styles.add(ParagraphStyle(
            name='MediumRisk',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.orange
        ))
        
        self.styles.add(ParagraphStyle(
            name='LowRisk',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.green
        ))
    
    def generate_pdf_report(self, scan_result: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Generate a PDF report for a repository scan result.
        
        Args:
            scan_result: The scan result dictionary
            
        Returns:
            Tuple containing:
                - Success flag (True/False)
                - Path to the generated report or error message
        """
        try:
            # Generate a filename based on scan ID and timestamp
            scan_id = scan_result.get('scan_id', f"scan_{int(time.time())}")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"gdpr_report_{scan_id}_{timestamp}.pdf"
            report_path = os.path.join(self.output_dir, filename)
            
            # Create the PDF document
            doc = SimpleDocTemplate(
                report_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Build the content
            content = []
            
            # Add title and metadata
            self._add_title_section(content, scan_result)
            
            # Add summary section
            self._add_summary_section(content, scan_result)
            
            # Add detailed findings
            self._add_findings_section(content, scan_result)
            
            # Add GDPR principles section
            self._add_gdpr_principles_section(content, scan_result)
            
            # Add recommendations
            self._add_recommendations_section(content, scan_result)
            
            # Add Netherlands-specific compliance section
            self._add_netherlands_compliance_section(content, scan_result)
            
            # Build the PDF
            doc.build(content)
            
            logger.info(f"Generated GDPR compliance report: {report_path}")
            return True, report_path
            
        except Exception as e:
            error_msg = f"Error generating PDF report: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def _add_title_section(self, content: List, scan_result: Dict[str, Any]):
        """Add the title section to the report."""
        # Title
        content.append(Paragraph("GDPR Compliance Scan Report", self.styles['Title']))
        content.append(Spacer(1, 0.25 * inch))
        
        # Subtitle with repository info
        repo_url = scan_result.get('repository_url', scan_result.get('repo_url', 'Unknown Repository'))
        content.append(Paragraph(f"Repository: {repo_url}", self.styles['Subtitle']))
        content.append(Spacer(1, 0.1 * inch))
        
        # Metadata
        scan_timestamp = scan_result.get('scan_timestamp', scan_result.get('timestamp', datetime.now().isoformat()))
        if isinstance(scan_timestamp, str):
            try:
                # Try to parse and format the timestamp
                dt = datetime.fromisoformat(scan_timestamp.replace('Z', '+00:00'))
                scan_timestamp = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
            except:
                # Keep as is if parsing fails
                pass
        
        metadata = [
            ["Scan Date:", scan_timestamp],
            ["Scan ID:", scan_result.get('scan_id', 'Unknown')],
            ["Branch:", scan_result.get('branch', 'Unknown')],
            ["Report Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        ]
        
        metadata_table = Table(metadata, colWidths=[1.5 * inch, 4 * inch])
        metadata_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.white),
        ]))
        
        content.append(metadata_table)
        content.append(Spacer(1, 0.5 * inch))
    
    def _add_summary_section(self, content: List, scan_result: Dict[str, Any]):
        """Add the summary section to the report."""
        content.append(Paragraph("Executive Summary", self.styles['SectionTitle']))
        content.append(Spacer(1, 0.1 * inch))
        
        # Extract summary data
        summary = scan_result.get('summary', {})
        files_scanned = summary.get('scanned_files', scan_result.get('files_scanned', 0))
        files_skipped = summary.get('skipped_files', scan_result.get('files_skipped', 0))
        pii_instances = summary.get('pii_instances', scan_result.get('total_pii_found', 0))
        high_risk = summary.get('high_risk_count', scan_result.get('high_risk_count', 0))
        medium_risk = summary.get('medium_risk_count', scan_result.get('medium_risk_count', 0))
        low_risk = summary.get('low_risk_count', scan_result.get('low_risk_count', 0))
        overall_score = summary.get('overall_compliance_score', 100 - (high_risk * 15 + medium_risk * 7 + low_risk * 3))
        
        # Create summary text
        summary_text = f"""
        This report presents the results of a GDPR compliance scan conducted on the repository.
        The scan analyzed {files_scanned} files out of a total of {files_scanned + files_skipped} files in the repository.
        
        The scan identified {pii_instances} instances of potential personal data or compliance issues:
        - {high_risk} high-risk findings
        - {medium_risk} medium-risk findings
        - {low_risk} low-risk findings
        
        Overall compliance score: {int(overall_score)}/100
        """
        
        content.append(Paragraph(summary_text, self.styles['Normal']))
        content.append(Spacer(1, 0.25 * inch))
        
        # Add compliance score table with color coding
        score_color = colors.green
        if overall_score < 70:
            score_color = colors.orange
        if overall_score < 50:
            score_color = colors.red
            
        score_data = [
            ["Overall Compliance Score", f"{int(overall_score)}/100"]
        ]
        
        score_table = Table(score_data, colWidths=[3 * inch, 2 * inch])
        score_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (1, 0), (1, 0), 14),
            ('TEXTCOLOR', (1, 0), (1, 0), score_color),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        content.append(score_table)
        content.append(Spacer(1, 0.5 * inch))
    
    def _add_findings_section(self, content: List, scan_result: Dict[str, Any]):
        """Add the detailed findings section to the report."""
        content.append(Paragraph("Detailed Findings", self.styles['SectionTitle']))
        content.append(Spacer(1, 0.1 * inch))
        
        # Get findings
        findings = scan_result.get('formatted_findings', [])
        if not findings:
            # Try to get raw findings
            raw_findings = scan_result.get('findings', [])
            findings = []
            
            # Process raw findings to formatted findings if needed
            for finding in raw_findings:
                if isinstance(finding, dict) and 'type' in finding:
                    risk_level = finding.get('risk_level', 'medium')
                    findings.append({
                        'type': finding.get('type', 'Unknown'),
                        'value': finding.get('value', ''),
                        'location': finding.get('file_path', 'Unknown'),
                        'line': finding.get('line_number', 0),
                        'risk_level': risk_level,
                        'gdpr_principle': finding.get('gdpr_principle', 'data_minimization'),
                        'description': finding.get('description', 'Potential GDPR compliance issue')
                    })
        
        if not findings:
            content.append(Paragraph("No specific findings were identified.", self.styles['Normal']))
            content.append(Spacer(1, 0.25 * inch))
            return
        
        # Group findings by risk level
        high_risk_findings = [f for f in findings if f.get('risk_level') == 'high']
        medium_risk_findings = [f for f in findings if f.get('risk_level') == 'medium']
        low_risk_findings = [f for f in findings if f.get('risk_level') == 'low']
        
        # Add high risk findings
        if high_risk_findings:
            content.append(Paragraph("High Risk Findings", self.styles['HighRisk']))
            content.append(Spacer(1, 0.1 * inch))
            
            findings_data = [["Type", "Location", "Description"]]
            for finding in high_risk_findings:
                findings_data.append([
                    finding.get('type', 'Unknown'),
                    f"{finding.get('location', 'Unknown')} (Line {finding.get('line', 0)})",
                    finding.get('description', 'No description')
                ])
            
            findings_table = Table(findings_data, colWidths=[1.5 * inch, 2 * inch, 3 * inch])
            findings_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 1), (0, -1), colors.red),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('WORDWRAP', (0, 0), (-1, -1), True),
            ]))
            
            content.append(findings_table)
            content.append(Spacer(1, 0.25 * inch))
        
        # Add medium risk findings
        if medium_risk_findings:
            content.append(Paragraph("Medium Risk Findings", self.styles['MediumRisk']))
            content.append(Spacer(1, 0.1 * inch))
            
            findings_data = [["Type", "Location", "Description"]]
            for finding in medium_risk_findings:
                findings_data.append([
                    finding.get('type', 'Unknown'),
                    f"{finding.get('location', 'Unknown')} (Line {finding.get('line', 0)})",
                    finding.get('description', 'No description')
                ])
            
            findings_table = Table(findings_data, colWidths=[1.5 * inch, 2 * inch, 3 * inch])
            findings_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 1), (0, -1), colors.orange),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('WORDWRAP', (0, 0), (-1, -1), True),
            ]))
            
            content.append(findings_table)
            content.append(Spacer(1, 0.25 * inch))
            
        # Add low risk findings (limit to 5 to avoid overwhelming)
        if low_risk_findings:
            content.append(Paragraph("Low Risk Findings", self.styles['LowRisk']))
            content.append(Spacer(1, 0.1 * inch))
            
            # Limit to 5 low risk findings to avoid overwhelming the report
            limited_low_risk = low_risk_findings[:5]
            
            findings_data = [["Type", "Location", "Description"]]
            for finding in limited_low_risk:
                findings_data.append([
                    finding.get('type', 'Unknown'),
                    f"{finding.get('location', 'Unknown')} (Line {finding.get('line', 0)})",
                    finding.get('description', 'No description')
                ])
            
            findings_table = Table(findings_data, colWidths=[1.5 * inch, 2 * inch, 3 * inch])
            findings_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 1), (0, -1), colors.green),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('WORDWRAP', (0, 0), (-1, -1), True),
            ]))
            
            content.append(findings_table)
            
            if len(low_risk_findings) > 5:
                content.append(Spacer(1, 0.1 * inch))
                more_text = f"... and {len(low_risk_findings) - 5} more low-risk findings."
                content.append(Paragraph(more_text, self.styles['Normal']))
            
            content.append(Spacer(1, 0.25 * inch))
    
    def _add_gdpr_principles_section(self, content: List, scan_result: Dict[str, Any]):
        """Add the GDPR principles section to the report."""
        content.append(Paragraph("GDPR Principles Analysis", self.styles['SectionTitle']))
        content.append(Spacer(1, 0.1 * inch))
        
        # Get affected GDPR principles from summary or findings
        principles = set()
        summary = scan_result.get('summary', {})
        principles_list = summary.get('gdpr_principles_affected', [])
        if principles_list:
            principles.update(principles_list)
        
        # Extract principles from findings if needed
        if not principles:
            findings = scan_result.get('formatted_findings', scan_result.get('findings', []))
            for finding in findings:
                if isinstance(finding, dict):
                    principle = finding.get('gdpr_principle')
                    if principle:
                        principles.add(principle)
        
        # Define all GDPR principles and their descriptions
        all_principles = {
            'lawfulness': {
                'title': 'Lawfulness, Fairness and Transparency',
                'description': 'Personal data must be processed lawfully, fairly and in a transparent manner.',
                'affected': 'lawfulness' in principles,
                'article': 'Art. 5(1)(a)'
            },
            'purpose_limitation': {
                'title': 'Purpose Limitation',
                'description': 'Personal data must be collected for specified, explicit and legitimate purposes.',
                'affected': 'purpose_limitation' in principles,
                'article': 'Art. 5(1)(b)'
            },
            'data_minimization': {
                'title': 'Data Minimization',
                'description': 'Personal data must be adequate, relevant and limited to what is necessary.',
                'affected': 'data_minimization' in principles,
                'article': 'Art. 5(1)(c)'
            },
            'accuracy': {
                'title': 'Accuracy',
                'description': 'Personal data must be accurate and kept up to date.',
                'affected': 'accuracy' in principles,
                'article': 'Art. 5(1)(d)'
            },
            'storage_limitation': {
                'title': 'Storage Limitation',
                'description': 'Personal data must be kept in a form which permits identification for no longer than necessary.',
                'affected': 'storage_limitation' in principles,
                'article': 'Art. 5(1)(e)'
            },
            'integrity_confidentiality': {
                'title': 'Integrity and Confidentiality',
                'description': 'Personal data must be processed in a secure manner.',
                'affected': 'integrity_confidentiality' in principles,
                'article': 'Art. 5(1)(f)'
            },
            'accountability': {
                'title': 'Accountability',
                'description': 'The controller shall be responsible for, and be able to demonstrate compliance.',
                'affected': 'accountability' in principles,
                'article': 'Art. 5(2)'
            }
        }
        
        # If no principles were identified, assume data_minimization as default
        if not principles:
            all_principles['data_minimization']['affected'] = True
        
        # Create principles table
        principles_data = [["GDPR Principle", "Article", "Status", "Description"]]
        
        for key, principle in all_principles.items():
            status = "❌ Affected" if principle['affected'] else "✓ Compliant"
            status_color = colors.red if principle['affected'] else colors.green
            
            principles_data.append([
                principle['title'],
                principle['article'],
                status,
                principle['description']
            ])
        
        principles_table = Table(principles_data, colWidths=[1.5 * inch, 0.8 * inch, 1 * inch, 3.2 * inch])
        principles_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('WORDWRAP', (0, 0), (-1, -1), True),
        ]))
        
        # Apply conditional formatting based on affected status
        for i, (_, principle) in enumerate(all_principles.items(), 1):
            if principle['affected']:
                principles_table.setStyle(TableStyle([
                    ('TEXTCOLOR', (2, i), (2, i), colors.red),
                    ('BACKGROUND', (0, i), (-1, i), colors.lightyellow),
                ]))
            else:
                principles_table.setStyle(TableStyle([
                    ('TEXTCOLOR', (2, i), (2, i), colors.green),
                ]))
        
        content.append(principles_table)
        content.append(Spacer(1, 0.5 * inch))
    
    def _add_recommendations_section(self, content: List, scan_result: Dict[str, Any]):
        """Add the recommendations section to the report."""
        content.append(Paragraph("Recommendations for Compliance", self.styles['SectionTitle']))
        content.append(Spacer(1, 0.1 * inch))
        
        # Collect recommendations from findings
        recommendations = set()
        findings = scan_result.get('formatted_findings', scan_result.get('findings', []))
        
        for finding in findings:
            if isinstance(finding, dict):
                # Try different keys that might contain recommendations
                recommendation = finding.get('recommendation', finding.get('remediation', ''))
                if recommendation:
                    recommendations.add(recommendation)
        
        # Add standard recommendations if none found
        if not recommendations:
            recommendations = {
                "Implement proper data minimization techniques to ensure only necessary personal data is processed.",
                "Use secure storage and transmission methods for all personal data.",
                "Implement data retention policies to ensure data is not stored longer than necessary.",
                "Add proper consent mechanisms before processing personal data.",
                "Review and document the legal basis for all personal data processing activities."
            }
        
        # Create a bulleted list of recommendations
        for recommendation in recommendations:
            content.append(Paragraph(f"• {recommendation}", self.styles['Normal']))
            content.append(Spacer(1, 0.1 * inch))
        
        content.append(Spacer(1, 0.25 * inch))
    
    def _add_netherlands_compliance_section(self, content: List, scan_result: Dict[str, Any]):
        """Add Netherlands-specific compliance section to the report."""
        content.append(Paragraph("Dutch GDPR (UAVG) Specific Compliance", self.styles['SectionTitle']))
        content.append(Spacer(1, 0.1 * inch))
        
        # Check for Netherlands-specific issues
        netherlands_issues = False
        findings = scan_result.get('formatted_findings', scan_result.get('findings', []))
        
        for finding in findings:
            if isinstance(finding, dict):
                if finding.get('type') in ['BSN', 'MEDICAL_DATA', 'MINOR_CONSENT']:
                    netherlands_issues = True
                    break
        
        # Check summary for netherlands_specific_issues flag
        summary = scan_result.get('summary', {})
        if 'netherlands_specific_issues' in summary and summary['netherlands_specific_issues']:
            netherlands_issues = True
        
        if netherlands_issues:
            content.append(Paragraph("⚠️ This repository may contain data that requires special handling under Dutch GDPR implementation (UAVG).", self.styles['HighRisk']))
            content.append(Spacer(1, 0.1 * inch))
        else:
            content.append(Paragraph("✓ No Netherlands-specific GDPR compliance issues detected.", self.styles['LowRisk']))
            content.append(Spacer(1, 0.1 * inch))
        
        # Add Netherlands-specific requirements table
        nl_requirements = [
            ["Requirement", "Description", "Relevant When"],
            ["BSN Processing", "The Dutch Citizen Service Number (BSN) may only be processed when explicitly authorized by law.", "Processing government or healthcare data"],
            ["Medical Data", "Medical data requires explicit consent and additional safeguards under UAVG Article 30.", "Processing health-related information"],
            ["Minors Consent", "Consent for data processing for children under 16 must be given by parents/guardians.", "Services targeting minors"],
            ["Data Breach", "The Dutch DPA (AP) requires notification within 72 hours for significant breaches.", "Any data breach involving personal data"]
        ]
        
        nl_table = Table(nl_requirements, colWidths=[1.2 * inch, 3 * inch, 2.3 * inch])
        nl_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('WORDWRAP', (0, 0), (-1, -1), True),
        ]))
        
        content.append(nl_table)
        content.append(Spacer(1, 0.5 * inch))

def generate_gdpr_report(scan_result: Dict[str, Any], output_dir: str = "reports") -> Tuple[bool, str, Optional[bytes]]:
    """
    Generate a GDPR compliance report for a scan result.
    
    Args:
        scan_result: Scan result dictionary
        output_dir: Directory to save the report
        
    Returns:
        Tuple containing:
            - Success flag (True/False)
            - Path to the report or error message
            - PDF content as bytes (for download) or None if failed
    """
    try:
        report_generator = GDPRReportGenerator(output_dir)
        success, report_path = report_generator.generate_pdf_report(scan_result)
        
        if success:
            # Read the file content for download
            with open(report_path, 'rb') as f:
                pdf_content = f.read()
            return success, report_path, pdf_content
        else:
            return success, report_path, None
    except Exception as e:
        error_msg = f"Error generating GDPR report: {str(e)}"
        logger.error(error_msg)
        return False, error_msg, None