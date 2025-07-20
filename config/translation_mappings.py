# Translation Mappings for Report Generation
# DataGuardian Pro - Internationalization Support

# Report Translation Mappings
REPORT_TRANSLATION_MAPPINGS = {
    'GDPR Compliance Report': 'report.title',
    'Repository': 'report.repository',
    'Branch': 'report.branch',
    'Scan ID': 'report.scan_id',
    'Executive Summary': 'report.executive_summary',
    'This report presents the results of a GDPR compliance scan conducted on the repository.': 'report.description',
    'The scan analyzed': 'report.scan_analyzed',
    'files out of a total of': 'report.files_total',
    'files in the repository.': 'report.files_in_repo',
    'The scan identified': 'report.scan_identified',
    'instances of potential personal data or compliance issues': 'report.compliance_issues',
    'high-risk findings': 'technical_terms.high_risk',
    'medium-risk findings': 'technical_terms.medium_risk',
    'low-risk findings': 'technical_terms.low_risk',
    'Overall compliance score': 'technical_terms.compliance_score',
    'Detailed Findings': 'technical_terms.findings',
    'High Risk Findings': 'report.high_risk_findings',
    'Medium Risk Findings': 'report.medium_risk_findings',
    'Low Risk Findings': 'report.low_risk_findings',
    'Type': 'report.type',
    'Location': 'report.location',
    'Description': 'report.description_column',
    'Recommendations for Compliance': 'technical_terms.recommendations',
    'Generated on': 'report.generated_on',
    'Error generating report': 'report.error'
}

# Additional Report Terms
REPORT_TERMS = {
    'critical_findings': 'critical_terms.findings',
    'data_protection_officer': 'gdpr_terms.dpo',
    'lawful_basis': 'gdpr_terms.lawful_basis',
    'data_subject_rights': 'gdpr_terms.subject_rights',
    'cross_border_transfer': 'gdpr_terms.transfer',
    'retention_period': 'gdpr_terms.retention',
    'processing_purpose': 'gdpr_terms.purpose'
}

# Scanner-Specific Terms
SCANNER_TERMS = {
    'code_scanner': 'scanners.code',
    'document_scanner': 'scanners.document',
    'website_scanner': 'scanners.website',
    'database_scanner': 'scanners.database',
    'ai_model_scanner': 'scanners.ai_model'
}