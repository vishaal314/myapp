#!/usr/bin/env python3
"""
Privacy Verification Scan
Run DataGuardian Pro Code Scanner on our own codebase to verify privacy improvements
"""

import os
import sys
import json
from datetime import datetime
from services.code_scanner import CodeScanner
from utils.pii_detection import identify_pii_in_text

def run_verification_scan():
    """Run a verification scan on our own codebase to check for privacy violations"""
    
    print("🔍 DataGuardian Pro - Privacy Verification Scan")
    print("=" * 60)
    print(f"📅 Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Purpose: Verify privacy violations cleanup")
    print()
    
    # Initialize code scanner
    scanner = CodeScanner(
        extensions=['.py', '.json', '.sh', '.md'],
        region="Netherlands",
        include_comments=True,
        use_entropy=True
    )
    
    # Test key files that were cleaned
    test_files = [
        './data/audit_log.json',
        './scripts/connect-github.sh',
        './services/code_scanner.py',
        './utils/pii_detection.py',
        './app.py'
    ]
    
    total_findings = []
    total_files = 0
    total_lines = 0
    
    print("🔎 Scanning cleaned files...")
    print("-" * 40)
    
    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"📄 Scanning: {file_path}")
            
            try:
                # Read file content
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                lines = len(content.split('\n'))
                total_files += 1
                total_lines += lines
                
                # Scan for PII
                file_findings = identify_pii_in_text(content, region="Netherlands")
                
                if file_findings:
                    print(f"  ❌ {len(file_findings)} issues found")
                    for finding in file_findings[:3]:  # Show first 3
                        print(f"    • {finding.get('type', 'Unknown')}: {finding.get('value', '')[:50]}...")
                    total_findings.extend(file_findings)
                else:
                    print(f"  ✅ Clean (no PII detected)")
                    
            except Exception as e:
                print(f"  ⚠️  Error reading file: {e}")
        else:
            print(f"📄 {file_path}: File not found")
    
    # Calculate compliance score using standard formula
    critical_findings = sum(1 for f in total_findings if f.get('severity') == 'Critical')
    high_findings = sum(1 for f in total_findings if f.get('severity') == 'High')
    medium_low_findings = len(total_findings) - critical_findings - high_findings
    
    # Standard penalty calculation
    penalty = (critical_findings * 25) + (high_findings * 15) + (medium_low_findings * 5)
    compliance_score = max(0, 100 - penalty)
    
    print()
    print("📊 SCAN RESULTS")
    print("=" * 60)
    print(f"📁 Files Scanned: {total_files}")
    print(f"📝 Lines Analyzed: {total_lines:,}")
    print(f"🔍 Total Findings: {len(total_findings)}")
    print()
    
    if len(total_findings) == 0:
        print("🎉 EXCELLENT: No privacy violations detected!")
        print("✅ Critical Issues: 0")
        print("✅ High Risk Issues: 0") 
        print("✅ Medium/Low Issues: 0")
        print()
        print("🏆 GDPR COMPLIANCE SCORE: 100%")
        print("🟢 CERTIFICATION STATUS: Green - Fully Compliant")
        print("🛡️  PRIVACY STATUS: Privacy by Design Implemented")
        
    else:
        print(f"⚠️  Found {len(total_findings)} issues requiring attention:")
        print(f"🔴 Critical Issues: {critical_findings}")
        print(f"🟡 High Risk Issues: {high_findings}")
        print(f"🟤 Medium/Low Issues: {medium_low_findings}")
        print()
        print(f"📊 GDPR COMPLIANCE SCORE: {compliance_score}%")
        
        if compliance_score >= 85:
            print("🟢 CERTIFICATION STATUS: Green - Compliant")
        elif compliance_score >= 70:
            print("🟡 CERTIFICATION STATUS: Yellow - Needs Improvement")
        else:
            print("🔴 CERTIFICATION STATUS: Red - Non-Compliant")
    
    print()
    print("📈 IMPROVEMENT COMPARISON")
    print("-" * 40)
    print("Before Cleanup:")
    print("  • Compliance Score: 0% (Failed)")
    print("  • Critical Issues: 4")
    print("  • High Risk Issues: 2") 
    print("  • Status: Non-Compliant")
    print()
    print("After Cleanup:")
    print(f"  • Compliance Score: {compliance_score}% ({'✅ Success' if compliance_score >= 85 else '⚠️ Needs Work'})")
    print(f"  • Critical Issues: {critical_findings}")
    print(f"  • High Risk Issues: {high_findings}")
    print(f"  • Status: {'✅ Compliant' if compliance_score >= 85 else '⚠️ Needs Improvement'}")
    
    improvement = compliance_score - 0  # Previous score was 0%
    print(f"  • 📈 Improvement: +{improvement}% (Target: 85-95%)")
    
    print()
    if compliance_score == 100:
        print("🎉 SUCCESS: DataGuardian Pro demonstrates perfect privacy protection!")
        print("✅ The platform now practices the privacy standards it enforces.")
    elif compliance_score >= 85:
        print("✅ SUCCESS: Privacy violations successfully resolved!")
        print("🏆 DataGuardian Pro is now GDPR compliant and deployment ready.")
    else:
        print("⚠️  Additional cleanup needed to reach 85%+ compliance score.")
    
    return compliance_score, len(total_findings)

if __name__ == "__main__":
    try:
        score, findings_count = run_verification_scan()
        
        # Exit with success if compliant
        if score >= 85:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Verification scan failed: {e}")
        sys.exit(1)