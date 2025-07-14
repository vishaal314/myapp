import os
import io
import base64
import logging
from typing import Dict, Any
import streamlit as st
from services.gdpr_report_generator import generate_gdpr_report
from utils.i18n import get_text

logger = logging.getLogger(__name__)


def generate_html_report(scan_result: Dict[str, Any]) -> str:
    try:
        # Get current language from session state
        lang = st.session_state.get('language', 'en')
        
        def t(key, default_text=""):
            """Translation helper using the app's translation system"""
            if key.startswith('report.'):
                return get_text(key, default_text)
            else:
                # For backwards compatibility, try to map common terms
                term_mapping = {
                    'GDPR Compliance Report': get_text('report.title', 'GDPR Compliance Report'),
                    'Repository': get_text('report.repository', 'Repository'),
                    'Branch': get_text('report.branch', 'Branch'),
                    'Scan ID': get_text('report.scan_id', 'Scan ID'),
                    'Executive Summary': get_text('report.executive_summary', 'Executive Summary'),
                    'This report presents the results of a GDPR compliance scan conducted on the repository.': get_text('report.description', 'This report presents the results of a GDPR compliance scan conducted on the repository.'),
                    'The scan analyzed': get_text('report.scan_analyzed', 'The scan analyzed'),
                    'files out of a total of': get_text('report.files_total', 'files out of a total of'),
                    'files in the repository.': get_text('report.files_in_repo', 'files in the repository.'),
                    'The scan identified': get_text('report.scan_identified', 'The scan identified'),
                    'instances of potential personal data or compliance issues': get_text('report.compliance_issues', 'instances of potential personal data or compliance issues'),
                    'high-risk findings': get_text('technical_terms.high_risk', 'high-risk findings'),
                    'medium-risk findings': get_text('technical_terms.medium_risk', 'medium-risk findings'),
                    'low-risk findings': get_text('technical_terms.low_risk', 'low-risk findings'),
                    'Overall compliance score': get_text('technical_terms.compliance_score', 'Overall compliance score'),
                    'Detailed Findings': get_text('technical_terms.findings', 'Detailed Findings'),
                    'High Risk Findings': get_text('report.high_risk_findings', 'High Risk Findings'),
                    'Medium Risk Findings': get_text('report.medium_risk_findings', 'Medium Risk Findings'),
                    'Low Risk Findings': get_text('report.low_risk_findings', 'Low Risk Findings'),
                    'Type': get_text('report.type', 'Type'),
                    'Location': get_text('report.location', 'Location'),
                    'Description': get_text('report.description_column', 'Description'),
                    'Recommendations for Compliance': get_text('technical_terms.recommendations', 'Recommendations for Compliance'),
                    'Generated on': get_text('report.generated_on', 'Generated on'),
                    'Error generating report': get_text('report.error', 'Error generating report')
                }
                return term_mapping.get(key, default_text or key)

        # Extract summary data
        summary = scan_result.get('summary', {})
        files_scanned = summary.get('scanned_files',
                                    scan_result.get('files_scanned', 0))
        files_skipped = summary.get('skipped_files',
                                    scan_result.get('files_skipped', 0))
        pii_instances = summary.get('pii_instances',
                                    scan_result.get('total_pii_found', 0))
        high_risk = summary.get('high_risk_count',
                                scan_result.get('high_risk_count', 0))
        medium_risk = summary.get('medium_risk_count',
                                  scan_result.get('medium_risk_count', 0))
        low_risk = summary.get('low_risk_count',
                               scan_result.get('low_risk_count', 0))
        overall_score = summary.get(
            'overall_compliance_score',
            100 - (high_risk * 15 + medium_risk * 7 + low_risk * 3))

        findings = scan_result.get('formatted_findings',
                                   scan_result.get('findings', []))
        repo_url = scan_result.get(
            'repository_url', scan_result.get('repo_url',
                                              'Unknown Repository'))

        # Set language for HTML document
        html_lang = "nl" if lang == "nl" else "en"
        
        html = f"""
        <!DOCTYPE html>
        <html lang="{html_lang}">
        <head>
            <meta charset="UTF-8">
            <title>{t('GDPR Compliance Report')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #2563EB; }}
                h2 {{ color: #1f2937; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; }}
                .summary {{ background-color: #f9fafb; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .high-risk {{ color: #dc2626; }}
                .medium-risk {{ color: #d97706; }}
                .low-risk {{ color: #059669; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #d1d5db; padding: 12px; text-align: left; }}
                th {{ background-color: #f3f4f6; font-weight: bold; }}
            </style>
        </head>
        <body>
            <h1>{t('GDPR Compliance Report')}</h1>
            <h2>{t('Repository')}: {repo_url}</h2>
            <p><strong>{t('Branch')}:</strong> {scan_result.get('branch', 'Unknown')}</p>
            <p><strong>{t('Scan ID')}:</strong> {scan_result.get('scan_id', 'Unknown')}</p>
            
            <div class="summary">
                <h2>{t('Executive Summary')}</h2>
                <p>{t('This report presents the results of a GDPR compliance scan conducted on the repository.')}</p>
                <p>{t('The scan analyzed')} {files_scanned} {t('files out of a total of')} {files_scanned + files_skipped} {t('files in the repository.')}</p>
                <p>{t('The scan identified')} {pii_instances} {t('instances of potential personal data or compliance issues')}:</p>
                <ul>
                    <li><strong class="high-risk">{high_risk}</strong> {t('high-risk findings')}</li>
                    <li><strong class="medium-risk">{medium_risk}</strong> {t('medium-risk findings')}</li>
                    <li><strong class="low-risk">{low_risk}</strong> {t('low-risk findings')}</li>
                </ul>
                <p><strong>{t('Overall compliance score')}:</strong> {int(overall_score)}/100</p>
            </div>
            
            <h2>{t('Detailed Findings')}</h2>
        """

        def render_findings(title, risk_class, items):
            if not items:
                return ''
            html_block = f"<h3 class='{risk_class}'>{t(title)}</h3><table><tr><th>{t('Type')}</th><th>{t('Location')}</th><th>{t('Description')}</th></tr>"
            for f in items:
                location = f.get('location', 'Unknown')
                line = f.get('line', 0)
                location_text = f"{location} (Line {line})" if line > 0 else location
                html_block += f"<tr><td>{f.get('type', 'Unknown')}</td><td>{location_text}</td><td>{f.get('description', 'No description')}</td></tr>"
            html_block += "</table>"
            return html_block

        # Add Netherlands-specific compliance section if applicable
        nl_findings = [f for f in findings if f.get('gdpr_principle') == 'netherlands_specific']
        if nl_findings:
            html += f"""
            <div class="netherlands-section" style="background-color: #fef3c7; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #f59e0b;">
                <h2 style="color: #92400e;">{t('Dutch GDPR (UAVG) Specific Compliance' if lang == 'en' else 'UAVG-specifieke naleving')}</h2>
                <p>{t('The following findings are specific to Dutch GDPR (UAVG) requirements:' if lang == 'en' else 'De volgende bevindingen zijn specifiek voor Nederlandse UAVG-vereisten:')}</p>
                {render_findings('Netherlands-Specific Findings' if lang == 'en' else 'UAVG-specifieke bevindingen', 'netherlands', nl_findings)}
            </div>
            """

        html += render_findings(
            'High Risk Findings', 'high-risk',
            [f for f in findings if f.get('risk_level') == 'High' and f.get('gdpr_principle') != 'netherlands_specific'])
        html += render_findings(
            'Medium Risk Findings', 'medium-risk',
            [f for f in findings if f.get('risk_level') == 'Medium' and f.get('gdpr_principle') != 'netherlands_specific'])
        html += render_findings(
            'Low Risk Findings', 'low-risk',
            [f for f in findings if f.get('risk_level') == 'Low' and f.get('gdpr_principle') != 'netherlands_specific'])

        html += f"""
            <div style="background-color: #f0f9ff; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #0ea5e9;">
                <h2 style="color: #0c4a6e;">{t('Recommendations for Compliance')}</h2>
                <ul>
        """

        recommendations = set()
        for f in findings:
            r = f.get('recommendation', f.get('remediation', ''))
            if r:
                recommendations.add(r)

        # Add default recommendations if none found
        if not recommendations:
            if lang == 'nl':
                recommendations.update([
                    "Implementeer juiste dataminimalisatietechnieken om ervoor te zorgen dat alleen noodzakelijke persoonsgegevens worden verwerkt.",
                    "Gebruik veilige opslag- en transmissiemethoden voor alle persoonsgegevens.",
                    "Voeg juiste toestemmingsmechanismen toe voordat persoonsgegevens worden verwerkt."
                ])
            else:
                recommendations.update([
                    "Implement proper data minimization techniques to ensure only necessary personal data is processed.",
                    "Use secure storage and transmission methods for all personal data.",
                    "Add proper consent mechanisms before processing personal data."
                ])

        for r in recommendations:
            html += f"<li>{r}</li>"

        html += f"""
                </ul>
            </div>
            <div style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #6b7280;">
                <p><strong>{t('Generated on')}:</strong> {scan_result.get('scan_timestamp', scan_result.get('timestamp', 'Unknown'))}</p>
                <p>DataGuardian Pro - Enterprise Privacy Compliance Platform</p>
            </div>
        </body>
        </html>
        """
        return html

    except Exception as e:
        logger.error(f"Error generating HTML report: {e}")
        error_msg = get_text('report.error', 'Error generating report') if 'get_text' in globals() else 'Error generating report'
        return f"<h1>{error_msg}:</h1> <p>{e}</p>"


def get_report_download_link(scan_result: Dict[str, Any],
                             format_type: str = "pdf") -> str:
    try:
        if format_type == "pdf":
            success, report_path, report_content = generate_gdpr_report(
                scan_result)
            if success and report_content:
                b64_content = base64.b64encode(report_content).decode()
                filename = f"gdpr_compliance_report_{scan_result.get('scan_id', 'scan')}.pdf"
                href = f'<a href="data:application/pdf;base64,{b64_content}" download="{filename}">Download GDPR Compliance Report (PDF)</a>'
                return href
            return "Error generating PDF report"

        elif format_type == "html":
            html_report = generate_html_report(scan_result)
            b64_content = base64.b64encode(html_report.encode()).decode()
            filename = f"gdpr_compliance_report_{scan_result.get('scan_id', 'scan')}.html"
            href = f'<a href="data:text/html;base64,{b64_content}" download="{filename}">Download GDPR Compliance Report (HTML)</a>'
            return href
        else:
            return "Unsupported format type"
    except Exception as e:
        logger.error(f"Error generating download link: {str(e)}")
        return f"Error generating report: {str(e)}"
