"""
Test script for the Smart AI-powered risk severity color-coding system.
"""
import os
import sys
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.code_scanner import CodeScanner
from utils.risk_analyzer import RiskAnalyzer

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

def main():
    """Test the risk analyzer with the vulnerability samples."""
    print("=" * 80)
    print_colored("TESTING SMART AI-POWERED RISK SEVERITY ANALYSIS", '1;34')
    print("=" * 80)
    
    # Test code scanning
    print("\n[1] Testing Code Scanner with vulnerability samples...")
    code_scanner = CodeScanner(region="Netherlands")
    code_results = code_scanner.scan_file(os.path.join(os.path.dirname(__file__), 'intentional_vulnerabilities.py'))
    
    # Initialize risk analyzer
    risk_analyzer = RiskAnalyzer(scan_type='code_scan')
    
    # Analyze the findings
    summary, enhanced_findings = risk_analyzer.analyze_findings(code_results.get('pii_found', []))
    
    # Print the summary
    print("\nSCAN SUMMARY:")
    print(f"Total findings: {summary['total_findings']}")
    print(f"Risk score: {summary['risk_score']}/100")
    print(f"Severity level: {summary['severity_level'].upper()}")
    print("\nRisk distribution:")
    for severity, count in summary['risk_distribution'].items():
        if count > 0:
            print_severity(severity, f"{count} findings")
    
    # Print the top 5 most severe findings
    print("\nTOP 5 MOST SEVERE FINDINGS:")
    for i, finding in enumerate(enhanced_findings[:5], 1):
        print_severity(
            finding['smart_severity'],
            f"Finding #{i}: {finding['type']} - {finding['value'][:50]}... (Score: {finding['smart_score']})"
        )
    
    # Test document scanning (simulated)
    print("\n[2] Testing Document Scanner with user data sample...")
    with open(os.path.join(os.path.dirname(__file__), 'user_data.json'), 'r') as f:
        user_data = f.read()
    
    # Simulate document scan findings
    doc_findings = [
        {
            'type': 'Credit Card',
            'value': '4111-1111-1111-1111',
            'location': 'Line 10 (code)',
            'risk_level': 'High'
        },
        {
            'type': 'Email',
            'value': 'john.doe@example.com',
            'location': 'Line 5 (code)',
            'risk_level': 'Medium'
        },
        {
            'type': 'BSN',
            'value': '123456782',
            'location': 'Line 8 (code)',
            'risk_level': 'High'
        },
        {
            'type': 'Medical Data',
            'value': 'Type 2 Diabetes',
            'location': 'Line 15 (code)',
            'risk_level': 'High'
        },
        {
            'type': 'API Key',
            'value': 'sk_test_51ABC123XYZ456',
            'location': 'Line 30 (code)',
            'risk_level': 'High'
        }
    ]
    
    # Analyze the document findings
    doc_analyzer = RiskAnalyzer(scan_type='blob_scan')
    doc_summary, doc_enhanced = doc_analyzer.analyze_findings(doc_findings)
    
    # Print the summary
    print("\nDOCUMENT SCAN SUMMARY:")
    print(f"Total findings: {doc_summary['total_findings']}")
    print(f"Risk score: {doc_summary['risk_score']}/100")
    print(f"Severity level: {doc_summary['severity_level'].upper()}")
    
    # Print the enhanced findings
    print("\nENHANCED FINDINGS:")
    for i, finding in enumerate(doc_enhanced, 1):
        print_severity(
            finding['smart_severity'],
            f"Finding #{i}: {finding['type']} - Context weight: {finding['context_weight']}, "
            f"Concentration factor: {finding['concentration_factor']}, "
            f"Smart score: {finding['smart_score']}"
        )
    
    # Test website scanning (simulated)
    print("\n[3] Testing Website Scanner with vulnerability samples...")
    # Simulate website scan findings
    web_findings = [
        {
            'type': 'Vulnerability:Xss',
            'value': 'document.write("<h2>Welcome, " + username + "!</h2>");',
            'location': 'Line 15 (code)',
            'risk_level': 'High'
        },
        {
            'type': 'Credit Card',
            'value': '4111-1111-1111-1111',
            'location': 'Line 25 (code)',
            'risk_level': 'High'
        },
        {
            'type': 'BSN',
            'value': '123456782',
            'location': 'Line 24 (code)',
            'risk_level': 'High'
        },
        {
            'type': 'Vulnerability:Csrf',
            'value': '<!-- INTENTIONAL VULNERABILITY: No CSRF token -->',
            'location': 'Line 50 (code)',
            'risk_level': 'Medium'
        },
        {
            'type': 'Vulnerability:Insecure Cookies',
            'value': 'document.cookie = "session_id=12345; path=/";',
            'location': 'Line 40 (code)',
            'risk_level': 'Medium'
        }
    ]
    
    # Analyze the website findings
    web_analyzer = RiskAnalyzer(scan_type='website_scan')
    web_summary, web_enhanced = web_analyzer.analyze_findings(web_findings)
    
    # Print the summary
    print("\nWEBSITE SCAN SUMMARY:")
    print(f"Total findings: {web_summary['total_findings']}")
    print(f"Risk score: {web_summary['risk_score']}/100")
    print(f"Severity level: {web_summary['severity_level'].upper()}")
    
    # Print the enhanced findings sorted by smart score
    print("\nENHANCED FINDINGS (SORTED BY SEVERITY):")
    for i, finding in enumerate(web_enhanced, 1):
        print_severity(
            finding['smart_severity'],
            f"Finding #{i}: {finding['type']} - Smart score: {finding['smart_score']}, "
            f"Color: {finding['color']}"
        )
    
    print("\n" + "=" * 80)
    print_colored("SMART AI-POWERED RISK SEVERITY ANALYSIS COMPLETE", '1;34')
    print("=" * 80)

if __name__ == "__main__":
    main()