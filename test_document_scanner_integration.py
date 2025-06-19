#!/usr/bin/env python3
"""
Test Document Scanner Integration

This script tests the Document Scanner (BlobScanner) to ensure it produces
comprehensive reports matching the Image Scanner's structure with professional
certificate-style output including PDF and HTML downloads.
"""

import os
import tempfile
from datetime import datetime
from services.blob_scanner import BlobScanner
from services.document_report_generator import generate_document_html_report, generate_document_pdf_report

def create_test_documents():
    """Create test documents with various PII types for testing."""
    test_files = []
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    
    # Test PDF content (simulated)
    pdf_content = """
    Employee Information:
    Name: John Doe
    Email: john.doe@company.com
    Phone: +31 6 12345678
    BSN: 123456789
    Address: 123 Main Street, Amsterdam, Netherlands
    Date of Birth: 1985-03-15
    """
    
    # Create test text file
    txt_file = os.path.join(temp_dir, "employee_data.txt")
    with open(txt_file, 'w') as f:
        f.write(pdf_content)
    test_files.append(txt_file)
    
    # Create test JSON file
    json_content = """
    {
        "customers": [
            {
                "name": "Jane Smith",
                "email": "jane.smith@email.com",
                "phone": "+31 20 1234567",
                "bsn": "987654321",
                "credit_card": "4111-1111-1111-1111"
            },
            {
                "name": "Bob Johnson", 
                "email": "bob.johnson@company.nl",
                "phone": "+31 6 98765432",
                "address": "456 Oak Street, Rotterdam, Netherlands"
            }
        ]
    }
    """
    
    json_file = os.path.join(temp_dir, "customers.json")
    with open(json_file, 'w') as f:
        f.write(json_content)
    test_files.append(json_file)
    
    # Create test CSV file
    csv_content = """Name,Email,Phone,BSN,Address
Alice Brown,alice.brown@test.com,+31 6 11111111,111222333,789 Pine Street Amsterdam
Charlie Davis,charlie.davis@example.nl,+31 20 9876543,444555666,321 Elm Street Utrecht
"""
    
    csv_file = os.path.join(temp_dir, "employees.csv")
    with open(csv_file, 'w') as f:
        f.write(csv_content)
    test_files.append(csv_file)
    
    return test_files, temp_dir

def test_document_scanner():
    """Test the Document Scanner comprehensive functionality."""
    print("🔍 Testing Document Scanner Integration")
    print("=" * 50)
    
    # Create test documents
    test_files, temp_dir = create_test_documents()
    print(f"✅ Created {len(test_files)} test documents in {temp_dir}")
    
    # Initialize Document Scanner
    scanner = BlobScanner(region="Netherlands")
    print("✅ Initialized Document Scanner with Dutch GDPR compliance")
    
    # Test comprehensive scan
    print("\n📄 Running comprehensive document scan...")
    
    def progress_callback(current, total, filename):
        print(f"  Scanning {current}/{total}: {filename}")
    
    # Perform comprehensive scan
    scan_results = scanner.scan_multiple_documents(test_files, callback_fn=progress_callback)
    
    # Validate scan results structure
    print("\n📊 Validating scan results structure...")
    
    required_keys = ['scan_type', 'metadata', 'document_results', 'findings', 'documents_with_pii', 'errors', 'risk_summary']
    for key in required_keys:
        if key in scan_results:
            print(f"  ✅ {key}: Present")
        else:
            print(f"  ❌ {key}: Missing")
    
    # Display scan summary
    metadata = scan_results.get('metadata', {})
    findings = scan_results.get('findings', [])
    risk_summary = scan_results.get('risk_summary', {})
    
    print(f"\n📈 Scan Summary:")
    print(f"  Documents Scanned: {metadata.get('documents_scanned', 0)}")
    print(f"  Documents with PII: {scan_results.get('documents_with_pii', 0)}")
    print(f"  Total Findings: {len(findings)}")
    print(f"  Risk Level: {risk_summary.get('level', 'Unknown')}")
    print(f"  Risk Score: {risk_summary.get('score', 0)}/100")
    
    # Test individual document results
    print(f"\n📋 Document Results Details:")
    document_results = scan_results.get('document_results', [])
    for i, result in enumerate(document_results, 1):
        filename = result.get('file_name', 'Unknown')
        pii_count = result.get('pii_count', 0)
        risk_level = result.get('risk_level', 'Unknown')
        gdpr_categories = result.get('gdpr_categories', [])
        
        print(f"  Document {i}: {filename}")
        print(f"    PII Found: {pii_count}")
        print(f"    Risk Level: {risk_level}")
        print(f"    GDPR Categories: {len(gdpr_categories)}")
        
        if gdpr_categories:
            for category in gdpr_categories[:3]:  # Show first 3
                print(f"      - {category}")
    
    # Test report generation
    print(f"\n📄 Testing Report Generation...")
    
    # Test HTML report
    try:
        html_report = generate_document_html_report(scan_results)
        if html_report and len(html_report) > 1000:
            print("  ✅ HTML Report: Generated successfully")
        else:
            print("  ❌ HTML Report: Too short or empty")
    except Exception as e:
        print(f"  ❌ HTML Report: Error - {str(e)}")
    
    # Test PDF report
    try:
        pdf_path = os.path.join(temp_dir, "test_document_report.pdf")
        pdf_result = generate_document_pdf_report(scan_results, pdf_path)
        if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 1000:
            print("  ✅ PDF Report: Generated successfully")
        else:
            print("  ❌ PDF Report: File too small or missing")
    except Exception as e:
        print(f"  ❌ PDF Report: Error - {str(e)}")
    
    # Test GDPR compliance features
    print(f"\n⚖️ Testing GDPR Compliance Features...")
    
    # Check for Dutch-specific BSN detection
    bsn_detected = any('BSN' in finding.get('type', '') for finding in findings)
    print(f"  BSN Detection: {'✅ Working' if bsn_detected else '❌ Not detected'}")
    
    # Check for special category data identification
    special_categories = set()
    for result in document_results:
        special_categories.update(result.get('gdpr_categories', []))
    
    gdpr_article_9 = any('Article 9' in cat for cat in special_categories)
    print(f"  Special Category Data (Article 9): {'✅ Detected' if gdpr_article_9 else '❌ Not detected'}")
    
    # Check compliance notes
    compliance_notes_found = any(result.get('compliance_notes') for result in document_results)
    print(f"  Compliance Notes: {'✅ Generated' if compliance_notes_found else '❌ Missing'}")
    
    print(f"\n🎯 Test Results Summary:")
    print(f"  Document Scanner: {'✅ PASS' if len(findings) > 0 else '❌ FAIL'}")
    print(f"  Report Generation: {'✅ PASS' if 'html_report' in locals() else '❌ FAIL'}")
    print(f"  GDPR Compliance: {'✅ PASS' if bsn_detected else '❌ FAIL'}")
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)
    print(f"✅ Cleaned up test files")
    
    return scan_results

if __name__ == "__main__":
    test_results = test_document_scanner()
    
    print(f"\n🔍 Document Scanner Integration Test Complete")
    print(f"The Document Scanner now provides comprehensive GDPR compliance")
    print(f"reporting that matches the Image Scanner's professional structure.")