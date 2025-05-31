import os
import io
import base64
import logging
from typing import Dict, Any
from langdetect import detect
from googletrans import Translator
import streamlit as st
from services.gdpr_report_generator import generate_gdpr_report

logger = logging.getLogger(__name__)


# Translation helper
def translate_text(text: str, lang: str, translator: Translator) -> str:
    try:
        if lang == 'en':
            return text
        return translator.translate(text, dest=lang).text
    except Exception as e:
        logger.warning(f"Translation failed for '{text}' to '{lang}': {e}")
        return text


def generate_html_report(scan_result: Dict[str, Any]) -> str:
    try:
        translator = Translator()
        detected_lang = detect(
            scan_result.get('repository_url', '') or 'English')

        def t(text):
            return translate_text(text, detected_lang, translator)

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

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{t('GDPR Compliance Report')}</title>
        </head>
        <body>
            <h1>{t('GDPR Compliance Report')}</h1>
            <h2>{t('Repository')}: {repo_url}</h2>
            <p>{t('Branch')}: {scan_result.get('branch', 'Unknown')}</p>
            <p>{t('Scan ID')}: {scan_result.get('scan_id', 'Unknown')}</p>
            <h2>{t('Executive Summary')}</h2>
            <p>{t('This report presents the results of a GDPR compliance scan conducted on the repository.')}</p>
            <p>{t('The scan analyzed')} {files_scanned} {t('files out of a total of')} {files_scanned + files_skipped} {t('files in the repository.')}</p>
            <p>{t('The scan identified')} {pii_instances} {t('instances of potential personal data or compliance issues')}:</p>
            <ul>
                <li><strong>{high_risk}</strong> {t('high-risk findings')}</li>
                <li><strong>{medium_risk}</strong> {t('medium-risk findings')}</li>
                <li><strong>{low_risk}</strong> {t('low-risk findings')}</li>
            </ul>
            <p>{t('Overall compliance score')}: <strong>{int(overall_score)}/100</strong></p>
            <h2>{t('Detailed Findings')}</h2>
        """

        def render_findings(title, risk_class, items):
            if not items:
                return ''
            html_block = f"<h3>{t(title)}</h3><table border='1'><tr><th>{t('Type')}</th><th>{t('Location')}</th><th>{t('Description')}</th></tr>"
            for f in items:
                html_block += f"<tr><td>{f.get('type', 'Unknown')}</td><td>{f.get('location', 'Unknown')} (Line {f.get('line', 0)})</td><td>{f.get('description', 'No description')}</td></tr>"
            html_block += "</table>"
            return html_block

        html += render_findings(
            'High Risk Findings', 'high-risk',
            [f for f in findings if f.get('risk_level') == 'high'])
        html += render_findings(
            'Medium Risk Findings', 'medium-risk',
            [f for f in findings if f.get('risk_level') == 'medium'])
        html += render_findings(
            'Low Risk Findings', 'low-risk',
            [f for f in findings if f.get('risk_level') == 'low'])

        html += f"""
            <h2>{t('Recommendations for Compliance')}</h2>
            <ul>
        """

        recommendations = set()
        for f in findings:
            r = f.get('recommendation', f.get('remediation', ''))
            if r:
                recommendations.add(r)

        if not recommendations:
            recommendations.update([
                t("Implement proper data minimization techniques to ensure only necessary personal data is processed."
                  ),
                t("Use secure storage and transmission methods for all personal data."
                  ),
                t("Add proper consent mechanisms before processing personal data."
                  )
            ])

        for r in recommendations:
            html += f"<li>{r}</li>"

        html += f"""
            </ul>
            <p>{t('Generated on')}: {scan_result.get('scan_timestamp', scan_result.get('timestamp', 'Unknown'))}</p>
        </body>
        </html>
        """
        return html

    except Exception as e:
        logger.error(f"Error generating HTML report: {e}")
        return f"<h1>{t('Error generating report')}:</h1> <p>{e}</p>"


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
