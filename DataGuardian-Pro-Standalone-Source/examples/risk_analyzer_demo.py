"""
Demo of the Smart AI-powered risk severity color-coding system.
Run this file to test the risk analyzer with example data.
"""
import sys
import os
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import risk analyzer
from utils.risk_analyzer import RiskAnalyzer, get_severity_color, colorize_finding, get_risk_color_gradient

# Example findings from different scan types
def load_example_findings():
    """Load example findings for different scan types"""
    # Code scan findings (example with source code vulnerabilities)
    code_findings = [
        {
            'type': 'Vulnerability:SQL Injection',
            'value': 'SELECT * FROM users WHERE id = " + user_id',
            'location': 'File: app.py, Line 42',
            'risk_level': 'High',
            'reason': 'SQL injection vulnerability can lead to data breach'
        },
        {
            'type': 'Vulnerability:XSS',
            'value': '<div>" + user_input + "</div>',
            'location': 'File: templates/page.html, Line 23',
            'risk_level': 'High',
            'reason': 'Cross-site scripting vulnerability can lead to session hijacking'
        },
        {
            'type': 'Credentials',
            'value': 'password = "admin123"',
            'location': 'File: config.py, Line 15',
            'risk_level': 'High',
            'reason': 'Hardcoded credentials can lead to unauthorized access'
        },
        {
            'type': 'Email',
            'value': 'john.doe@example.com',
            'location': 'File: users.py, Line 78',
            'risk_level': 'Medium',
            'reason': 'Email addresses are personal data under GDPR'
        },
        {
            'type': 'Email',
            'value': 'jane.smith@example.com',
            'location': 'File: users.py, Line 79',
            'risk_level': 'Medium',
            'reason': 'Email addresses are personal data under GDPR'
        },
        {
            'type': 'Email',
            'value': 'support@company.com',
            'location': 'File: config.py, Line 25',
            'risk_level': 'Low',
            'reason': 'Company email addresses are lower risk but still personal data'
        },
        {
            'type': 'API Key',
            'value': 'sk_test_abcdefghijklmnopqrstuvwxyz1234',
            'location': 'File: payment.py, Line 10',
            'risk_level': 'High',
            'reason': 'API keys should not be hardcoded in source code'
        }
    ]
    
    # Website scan findings (example with website vulnerabilities)
    website_findings = [
        {
            'type': 'Vulnerability:XSS',
            'value': 'document.write("<h2>Welcome, " + username + "!</h2>");',
            'location': 'URL: https://example.com/welcome, Line 15',
            'risk_level': 'High',
            'reason': 'Cross-site scripting vulnerability can lead to session hijacking'
        },
        {
            'type': 'Credit Card',
            'value': '4111-1111-1111-1111',
            'location': 'URL: https://example.com/checkout, Line 25',
            'risk_level': 'High',
            'reason': 'Credit card numbers should not be exposed in website content'
        },
        {
            'type': 'Email',
            'value': 'info@example.com',
            'location': 'URL: https://example.com/contact, Line 30',
            'risk_level': 'Medium',
            'reason': 'Email addresses are personal data under GDPR'
        },
        {
            'type': 'Vulnerability:CSRF',
            'value': '<form action="/transfer" method="POST">',
            'location': 'URL: https://example.com/account, Line 50',
            'risk_level': 'Medium',
            'reason': 'CSRF vulnerability can lead to unauthorized actions'
        },
        {
            'type': 'Vulnerability:Insecure Cookies',
            'value': 'document.cookie = "session_id=12345; path=/";',
            'location': 'URL: https://example.com/, Line 40',
            'risk_level': 'Medium',
            'reason': 'Insecure cookies can lead to session hijacking'
        },
        {
            'type': 'IP Address',
            'value': '192.168.1.1',
            'location': 'URL: https://example.com/admin, Line 10',
            'risk_level': 'Low',
            'reason': 'Internal IP addresses are personal data under GDPR'
        }
    ]
    
    # Document scan findings (example with sensitive personal data)
    document_findings = [
        {
            'type': 'Credit Card',
            'value': '5555-5555-5555-4444',
            'location': 'Document: contract.pdf, Page 5',
            'risk_level': 'High',
            'reason': 'Credit card numbers are high-risk financial data'
        },
        {
            'type': 'BSN',
            'value': '123456782',
            'location': 'Document: employees.xlsx, Row 8',
            'risk_level': 'High',
            'reason': 'BSN (Dutch SSN) is highly sensitive personal data'
        },
        {
            'type': 'Passport Number',
            'value': 'NW123456',
            'location': 'Document: travel.docx, Page 2',
            'risk_level': 'High',
            'reason': 'Passport numbers are sensitive identification data'
        },
        {
            'type': 'Medical Data',
            'value': 'Diagnosed with Type 2 Diabetes',
            'location': 'Document: medical_records.pdf, Page 10',
            'risk_level': 'High',
            'reason': 'Medical data is special category data under GDPR Art. 9'
        },
        {
            'type': 'Date of Birth',
            'value': '1980-01-15',
            'location': 'Document: employees.xlsx, Row 8',
            'risk_level': 'Medium',
            'reason': 'Date of birth is personal data and can be used for identity theft'
        },
        {
            'type': 'Address',
            'value': '123 Main Street, Amsterdam',
            'location': 'Document: customers.csv, Row 15',
            'risk_level': 'Medium',
            'reason': 'Physical addresses are personal data under GDPR'
        },
        {
            'type': 'Address',
            'value': '456 High Street, Rotterdam',
            'location': 'Document: customers.csv, Row 16',
            'risk_level': 'Medium',
            'reason': 'Physical addresses are personal data under GDPR'
        },
        {
            'type': 'Phone',
            'value': '+31 20 123 4567',
            'location': 'Document: contacts.xlsx, Row 5',
            'risk_level': 'Medium',
            'reason': 'Phone numbers are personal data under GDPR'
        },
        {
            'type': 'Email',
            'value': 'personal@example.com',
            'location': 'Document: contacts.xlsx, Row 5',
            'risk_level': 'Medium',
            'reason': 'Email addresses are personal data under GDPR'
        },
        {
            'type': 'Email',
            'value': 'another@example.com',
            'location': 'Document: contacts.xlsx, Row 6',
            'risk_level': 'Medium',
            'reason': 'Email addresses are personal data under GDPR'
        }
    ]
    
    # Database scan findings (example with sensitive database data)
    database_findings = [
        {
            'type': 'Credit Card',
            'value': '4111-1111-1111-1111',
            'location': 'Table: payments, Column: card_number',
            'risk_level': 'High',
            'reason': 'Unencrypted credit card data violates PCI DSS and GDPR'
        },
        {
            'type': 'BSN',
            'value': '123456782',
            'location': 'Table: employees, Column: bsn',
            'risk_level': 'High',
            'reason': 'BSN (Dutch SSN) requires special safeguards'
        },
        {
            'type': 'Vulnerability:Insecure Storage',
            'value': 'Passwords stored in plaintext',
            'location': 'Table: users, Column: password',
            'risk_level': 'Critical',
            'reason': 'Plaintext passwords can lead to account compromise'
        },
        {
            'type': 'Vulnerability:Encryption Missing',
            'value': 'No encryption for financial data',
            'location': 'Table: transactions, Database: financial',
            'risk_level': 'High',
            'reason': 'Financial data must be encrypted under GDPR'
        },
        {
            'type': 'Vulnerability:Excess Privilege',
            'value': 'User has excessive database privileges',
            'location': 'Database: customer_data, User: app_user',
            'risk_level': 'Medium',
            'reason': 'Principle of least privilege violation'
        },
        {
            'type': 'Email',
            'value': 'john.doe@example.com',
            'location': 'Table: users, Column: email',
            'risk_level': 'Medium',
            'reason': 'Email addresses are personal data under GDPR'
        },
        {
            'type': 'Phone',
            'value': '+31 20 123 4567',
            'location': 'Table: users, Column: phone',
            'risk_level': 'Medium',
            'reason': 'Phone numbers are personal data under GDPR'
        }
    ]
    
    return {
        'code_findings': code_findings,
        'website_findings': website_findings,
        'document_findings': document_findings,
        'database_findings': database_findings
    }

def print_colored(text, color_code):
    """Print colored text to the console."""
    print(f"\033[{color_code}m{text}\033[0m")

def print_severity(severity, message):
    """Print message with color based on severity."""
    colors = {
        'critical': '91',  # Bright red
        'high': '31',      # Red
        'medium': '33',    # Yellow
        'low': '32',       # Green
        'info': '36'       # Cyan
    }
    color = colors.get(severity.lower(), '0')
    print_colored(f"[{severity.upper()}] {message}", color)

def display_color_scale():
    """Display the risk color scale."""
    print("\nRISK SEVERITY COLOR SCALE:")
    severities = ['critical', 'high', 'medium', 'low', 'info', 'safe']
    for severity in severities:
        color = get_severity_color(severity)
        print(f"{severity.upper()}: {color}")
    
    print("\nRISK SCORE COLOR GRADIENT:")
    scores = [0, 25, 50, 75, 100]
    for score in scores:
        color = get_risk_color_gradient(score)
        print(f"Score {score}: {color}")

def analyze_and_print_results(findings, scan_type, title):
    """Analyze findings and print the results."""
    print("\n" + "=" * 80)
    print_colored(f"SMART AI RISK ANALYSIS: {title}", '1;34')
    print("=" * 80)
    
    # Initialize risk analyzer
    risk_analyzer = RiskAnalyzer(scan_type=scan_type)
    
    # Analyze the findings
    summary, enhanced_findings = risk_analyzer.analyze_findings(findings)
    
    # Print the summary
    print(f"\nTotal findings: {summary['total_findings']}")
    print(f"Risk score: {summary['risk_score']}/100")
    print(f"Severity level: {summary['severity_level'].upper()}")
    print(f"Severity color: {summary['severity_color']}")
    
    print("\nRisk distribution:")
    for severity, count in summary['risk_distribution'].items():
        if count > 0:
            print_severity(severity, f"{count} findings")
    
    print("\nType distribution:")
    for pii_type, count in list(summary['type_distribution'].items())[:5]:  # Show top 5
        print(f"- {pii_type}: {count}")
    
    # Print the top findings by smart score
    print("\nTOP 5 MOST SEVERE FINDINGS (by Smart Score):")
    for i, finding in enumerate(enhanced_findings[:5], 1):
        print_severity(
            finding['smart_severity'],
            f"Finding #{i}: {finding['type']} - Score: {finding['smart_score']:.2f} "
            f"(Weight: {finding.get('context_weight', 1.0):.1f}, "
            f"Concentration: {finding.get('concentration_factor', 1.0):.1f}, "
            f"Clustering: {finding.get('clustering_factor', 1.0):.1f})"
        )

def main():
    """Main function to run the demo."""
    print("\n" + "=" * 80)
    print_colored("SMART AI-POWERED RISK SEVERITY COLOR-CODING SYSTEM DEMO", '1;35')
    print("=" * 80)
    print("\nThis demo shows how the Smart AI risk analyzer assigns severity levels")
    print("and color codes to findings based on context, concentration, and clustering.")
    
    # Display the color scale
    display_color_scale()
    
    # Load example findings
    findings = load_example_findings()
    
    # Analyze and print results for each scan type
    analyze_and_print_results(findings['code_findings'], 'code_scan', "CODE SCAN")
    analyze_and_print_results(findings['website_findings'], 'website_scan', "WEBSITE SCAN")
    analyze_and_print_results(findings['document_findings'], 'blob_scan', "DOCUMENT SCAN")
    analyze_and_print_results(findings['database_findings'], 'database_scan', "DATABASE SCAN")
    
    print("\n" + "=" * 80)
    print_colored("SMART AI RISK SEVERITY ANALYSIS COMPLETE", '1;35')
    print("=" * 80)

if __name__ == "__main__":
    main()