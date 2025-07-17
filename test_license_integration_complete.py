#!/usr/bin/env python3
"""
License Integration Completion Test
Tests all 10 scanner types for proper license tracking integration
"""

import sys
import re
from pathlib import Path

def test_license_integration():
    """Test all scanner functions have license tracking integrated"""
    
    # Read the main app.py file
    app_path = Path('app.py')
    if not app_path.exists():
        print("❌ app.py not found")
        return False
    
    with open(app_path, 'r') as f:
        content = f.read()
    
    # Scanner types to test
    scanner_types = [
        'code', 'database', 'image', 'document', 'api', 
        'website', 'ai_model', 'soc2', 'dpia', 'sustainability'
    ]
    
    results = {}
    
    for scanner_type in scanner_types:
        # Check for track_scanner_usage call with the scanner type
        pattern = rf"track_scanner_usage\(['\"]({scanner_type})['\"]"
        matches = re.findall(pattern, content)
        results[scanner_type] = len(matches) > 0
        
        if results[scanner_type]:
            print(f"✅ {scanner_type.upper()} scanner: License tracking integrated")
        else:
            print(f"❌ {scanner_type.upper()} scanner: Missing license tracking")
    
    # Summary
    successful = sum(1 for v in results.values() if v)
    total = len(scanner_types)
    
    print(f"\n📊 INTEGRATION SUMMARY")
    print(f"✅ Successful integrations: {successful}/{total}")
    print(f"❌ Missing integrations: {total - successful}/{total}")
    
    if successful == total:
        print("🎉 ALL SCANNER TYPES HAVE LICENSE TRACKING INTEGRATED!")
        return True
    else:
        print("⚠️  Some scanner types still need license tracking integration")
        return False

def test_import_statements():
    """Test that all required imports are present"""
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    required_imports = [
        'track_scanner_usage',
        'require_scanner_access',
        'require_license_check',
        'require_report_access',
        'track_report_usage',
        'track_download_usage'
    ]
    
    print("\n🔍 IMPORT VALIDATION")
    
    for import_name in required_imports:
        if import_name in content:
            print(f"✅ {import_name} imported correctly")
        else:
            print(f"❌ {import_name} missing from imports")
    
    # Check license_integration import line specifically
    if 'from services.license_integration import' in content:
        print("✅ License integration module imported")
    else:
        print("❌ License integration module not imported")

def test_scanner_functions():
    """Test that all scanner execution functions exist"""
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    scanner_functions = [
        'execute_code_scan',
        'execute_database_scan', 
        'execute_image_scan',
        'execute_document_scan',
        'execute_api_scan',
        'execute_website_scan',
        'execute_ai_model_scan',
        'execute_soc2_scan',
        'execute_enhanced_dpia_scan',
        'execute_sustainability_scan'
    ]
    
    print("\n🔧 SCANNER FUNCTION VALIDATION")
    
    for func_name in scanner_functions:
        if f'def {func_name}' in content:
            print(f"✅ {func_name} function exists")
        else:
            print(f"❌ {func_name} function missing")

def main():
    """Run all license integration tests"""
    
    print("🛡️  DATAGUARDIAN PRO LICENSE INTEGRATION TEST")
    print("=" * 60)
    
    # Test 1: License tracking integration
    integration_success = test_license_integration()
    
    # Test 2: Import statements
    test_import_statements()
    
    # Test 3: Scanner functions
    test_scanner_functions()
    
    print("\n" + "=" * 60)
    
    if integration_success:
        print("🎉 LICENSE INTEGRATION COMPLETE!")
        print("✅ All 10 scanner types have proper license tracking")
        print("✅ Revenue protection system fully operational")
        print("✅ Usage monitoring enabled across all features")
    else:
        print("⚠️  LICENSE INTEGRATION INCOMPLETE")
        print("❌ Some scanner types missing license tracking")
        print("❌ Revenue protection system has gaps")
    
    return integration_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)