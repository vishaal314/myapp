# Report Generation Configuration
# DataGuardian Pro - Report Settings

# PDF Report Limits
PDF_MAX_FINDINGS = 10  # Maximum findings to include in PDF reports to prevent oversized documents
PDF_MAX_FILE_SIZE_MB = 5  # Maximum PDF file size in MB

# HTML Report Settings
HTML_MAX_FINDINGS = 50  # Maximum findings to include in HTML reports
HTML_INCLUDE_CHARTS = True  # Include charts and visualizations in HTML reports

# Report Styling
REPORT_THEME = "professional"  # Options: professional, modern, minimal
INCLUDE_COMPANY_BRANDING = True  # Include DataGuardian Pro branding

# Export Settings
FILENAME_DATE_FORMAT = "%Y%m%d_%H%M%S"  # Timestamp format for report filenames
INCLUDE_SCAN_ID_IN_FILENAME = True  # Include scan ID in generated filenames

# Performance Settings
REPORT_GENERATION_TIMEOUT = 30  # Seconds before report generation times out
ENABLE_REPORT_CACHING = True  # Cache generated reports for faster re-downloads