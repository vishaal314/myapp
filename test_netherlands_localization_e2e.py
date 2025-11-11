#!/usr/bin/env python3
"""
END-TO-END NETHERLANDS LOCALIZATION VERIFICATION TEST
Tests all Netherlands-specific features and Dutch language support
"""

import json
import re
from typing import Dict, List, Any
from datetime import datetime

print("=" * 80)
print("NETHERLANDS LOCALIZATION - END-TO-END VERIFICATION TEST")
print("=" * 80)
print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Track all test results
test_results = {
    'translation_files': {},
    'dutch_language': {},
    'netherlands_pii': {},
    'uavg_compliance': {},
    'report_generation': {},
    'ui_components': {}
}

gaps = []

# ============================================================================
# TEST 1: TRANSLATION FILES VALIDATION
# ============================================================================

print("TEST 1: TRANSLATION FILES VALIDATION")
print("-" * 80)

try:
    # Load English translations
    with open('translations/en.json', 'r', encoding='utf-8') as f:
        en_translations = json.load(f)
    print(f"✅ English translations loaded: {len(str(en_translations))} chars")
    test_results['translation_files']['english_loaded'] = True
    
    # Load Dutch translations
    with open('translations/nl.json', 'r', encoding='utf-8') as f:
        nl_content = f.read()
        nl_translations = json.load(open('translations/nl.json', 'r', encoding='utf-8'))
    print(f"✅ Dutch translations loaded: {len(str(nl_translations))} chars")
    test_results['translation_files']['dutch_loaded'] = True
    
    # Check coverage
    en_keys = list(en_translations.keys())
    nl_keys = list(nl_translations.keys())
    
    print(f"\nTranslation Coverage:")
    print(f"  English sections: {len(en_keys)}")
    print(f"  Dutch sections: {len(nl_keys)}")
    print(f"  English top keys: {en_keys[:10]}")
    print(f"  Dutch top keys: {nl_keys[:10]}")
    
    # Check for Netherlands-specific sections
    nl_specific_sections = ['netherlands_regulatory', 'dpia', 'ai_act']
    for section in nl_specific_sections:
        if section in nl_translations:
            print(f"  ✅ {section}: Present")
            test_results['translation_files'][f'section_{section}'] = True
        else:
            print(f"  ❌ {section}: Missing")
            test_results['translation_files'][f'section_{section}'] = False
            gaps.append(f"Missing translation section: {section}")
    
except json.JSONDecodeError as e:
    print(f"❌ JSON Error in translations: {e}")
    print(f"   Line {e.lineno}, Column {e.colno}")
    test_results['translation_files']['valid_json'] = False
    gaps.append(f"JSON syntax error in translations/nl.json at line {e.lineno}")
except Exception as e:
    print(f"❌ Error loading translations: {e}")
    test_results['translation_files']['error'] = str(e)
    gaps.append(f"Translation file error: {e}")

print()

# ============================================================================
# TEST 2: NETHERLANDS-SPECIFIC PII DETECTION
# ============================================================================

print("TEST 2: NETHERLANDS-SPECIFIC PII DETECTION")
print("-" * 80)

try:
    from utils.pii_detection import identify_pii_in_text
    
    # Test BSN detection
    test_text_bsn = "BSN: 123456782 and burgerservicenummer 987654321"
    bsn_findings = identify_pii_in_text(test_text_bsn, region="Netherlands")
    bsn_count = sum(1 for f in bsn_findings if f.get('type') == 'BSN')
    
    print(f"BSN Detection Test:")
    print(f"  Test text: '{test_text_bsn}'")
    print(f"  BSN findings: {bsn_count}")
    
    if bsn_count > 0:
        print(f"  ✅ BSN detection working")
        test_results['netherlands_pii']['bsn_detection'] = True
    else:
        print(f"  ❌ BSN detection not working")
        test_results['netherlands_pii']['bsn_detection'] = False
        gaps.append("BSN detection not finding Dutch social security numbers")
    
    # Test Dutch phone numbers
    test_text_phone = "+31 6 12345678 and +31-20-1234567"
    phone_findings = identify_pii_in_text(test_text_phone, region="Netherlands")
    phone_count = sum(1 for f in phone_findings if 'Dutch' in f.get('type', '') or 'Phone' in f.get('type', ''))
    
    print(f"\nDutch Phone Detection Test:")
    print(f"  Test text: '{test_text_phone}'")
    print(f"  Phone findings: {phone_count}")
    
    if phone_count > 0:
        print(f"  ✅ Dutch phone detection working")
        test_results['netherlands_pii']['phone_detection'] = True
    else:
        print(f"  ⚠️ Dutch phone detection may need enhancement")
        test_results['netherlands_pii']['phone_detection'] = False
        gaps.append("Dutch phone number detection incomplete")
    
    # Test Dutch postal codes
    test_text_postal = "Address: 1234 AB Amsterdam"
    postal_findings = identify_pii_in_text(test_text_postal, region="Netherlands")
    postal_count = sum(1 for f in postal_findings if 'Address' in f.get('type', '') or 'Dutch' in f.get('description', ''))
    
    print(f"\nDutch Postal Code Detection Test:")
    print(f"  Test text: '{test_text_postal}'")
    print(f"  Postal findings: {postal_count}")
    
    if postal_count > 0:
        print(f"  ✅ Dutch postal code detection working")
        test_results['netherlands_pii']['postal_detection'] = True
    else:
        print(f"  ⚠️ Dutch postal code detection may need enhancement")
        test_results['netherlands_pii']['postal_detection'] = False
    
    # Test .nl email addresses
    test_text_email = "Contact: info@example.nl and support@company.nl"
    email_findings = identify_pii_in_text(test_text_email, region="Netherlands")
    email_count = sum(1 for f in email_findings if 'EMAIL' in f.get('type', ''))
    
    print(f"\nDutch Email Detection Test:")
    print(f"  Test text: '{test_text_email}'")
    print(f"  Email findings: {email_count}")
    
    if email_count > 0:
        print(f"  ✅ Email detection working (.nl domains)")
        test_results['netherlands_pii']['email_detection'] = True
    else:
        print(f"  ❌ Email detection not working")
        test_results['netherlands_pii']['email_detection'] = False
        gaps.append("Email detection not finding .nl addresses")

except Exception as e:
    print(f"❌ Error in PII detection tests: {e}")
    import traceback
    traceback.print_exc()

print()

# ============================================================================
# TEST 3: UAVG COMPLIANCE FEATURES
# ============================================================================

print("TEST 3: UAVG COMPLIANCE FEATURES")
print("-" * 80)

try:
    from utils.netherlands_uavg_compliance import detect_uavg_compliance_gaps
    
    # Test UAVG compliance detection
    test_content = """
    This system processes BSN numbers for healthcare providers.
    We use cookies for analytics and marketing.
    Biometric processing includes facial recognition.
    """
    
    uavg_findings = detect_uavg_compliance_gaps(test_content)
    
    print(f"UAVG Compliance Detection Test:")
    print(f"  Test content analyzed: {len(test_content)} chars")
    print(f"  UAVG findings: {len(uavg_findings)}")
    
    if uavg_findings:
        print(f"  ✅ UAVG compliance detection working")
        for i, finding in enumerate(uavg_findings[:3], 1):
            print(f"  {i}. {finding.get('type')}: {finding.get('severity')}")
        test_results['uavg_compliance']['detection_working'] = True
    else:
        print(f"  ⚠️ No UAVG findings detected (may need more specific content)")
        test_results['uavg_compliance']['detection_working'] = False
    
    # Check for AP guidelines
    ap_content = "ai decision making without human oversight"
    ap_findings = detect_uavg_compliance_gaps(ap_content)
    ap_count = sum(1 for f in ap_findings if 'AP_GUIDELINES' in f.get('type', ''))
    
    print(f"\nAP Guidelines 2024-2025 Test:")
    print(f"  AP findings: {ap_count}")
    
    if ap_count > 0:
        print(f"  ✅ AP Guidelines detection working")
        test_results['uavg_compliance']['ap_guidelines'] = True
    else:
        print(f"  ⚠️ AP Guidelines detection may need verification")
        test_results['uavg_compliance']['ap_guidelines'] = False

except Exception as e:
    print(f"❌ Error in UAVG compliance tests: {e}")
    import traceback
    traceback.print_exc()

print()

# ============================================================================
# TEST 4: DUTCH LANGUAGE UI COMPONENTS
# ============================================================================

print("TEST 4: DUTCH LANGUAGE UI COMPONENTS")
print("-" * 80)

try:
    # Check if language switcher exists
    import os
    if os.path.exists('utils/animated_language_switcher.py'):
        print(f"✅ Language switcher component exists")
        test_results['ui_components']['language_switcher'] = True
        
        # Check for Dutch flag
        with open('utils/animated_language_switcher.py', 'r') as f:
            content = f.read()
            if "'nl'" in content and "🇳🇱" in content:
                print(f"✅ Dutch flag emoji configured")
                test_results['ui_components']['dutch_flag'] = True
            else:
                print(f"⚠️ Dutch flag may not be configured")
                test_results['ui_components']['dutch_flag'] = False
    else:
        print(f"❌ Language switcher not found")
        test_results['ui_components']['language_switcher'] = False
        gaps.append("Language switcher component missing")
    
    # Check for Dutch in supported languages
    if os.path.exists('utils/i18n.py'):
        with open('utils/i18n.py', 'r') as f:
            content = f.read()
            if "'nl': 'Nederlands'" in content:
                print(f"✅ Dutch language registered in i18n")
                test_results['ui_components']['dutch_in_i18n'] = True
            else:
                print(f"❌ Dutch language not registered")
                test_results['ui_components']['dutch_in_i18n'] = False
                gaps.append("Dutch language not in LANGUAGES dict")

except Exception as e:
    print(f"❌ Error checking UI components: {e}")

print()

# ============================================================================
# TEST 5: REPORT GENERATION IN DUTCH
# ============================================================================

print("TEST 5: REPORT GENERATION IN DUTCH")
print("-" * 80)

try:
    # Check report generator
    import os
    if os.path.exists('services/report_generator.py'):
        with open('services/report_generator.py', 'r') as f:
            content = f.read()
            
            # Check for Dutch language support
            if "language == 'nl'" in content or "lang == 'nl'" in content:
                print(f"✅ Report generator supports Dutch language")
                test_results['report_generation']['dutch_support'] = True
            else:
                print(f"⚠️ Report generator may not have Dutch support")
                test_results['report_generation']['dutch_support'] = False
                gaps.append("Report generator missing Dutch language conditional")
            
            # Check for UAVG references
            if 'UAVG' in content or 'uavg' in content.lower():
                print(f"✅ Report generator includes UAVG references")
                test_results['report_generation']['uavg_references'] = True
            else:
                print(f"⚠️ Report generator may not include UAVG compliance")
                test_results['report_generation']['uavg_references'] = False
    
    # Check certificate generator
    if os.path.exists('services/certificate_generator.py'):
        with open('services/certificate_generator.py', 'r') as f:
            content = f.read()
            
            if "'nl'" in content or 'Dutch' in content:
                print(f"✅ Certificate generator supports Dutch")
                test_results['report_generation']['dutch_certificates'] = True
            else:
                print(f"⚠️ Certificate generator may not support Dutch")
                test_results['report_generation']['dutch_certificates'] = False

except Exception as e:
    print(f"❌ Error checking report generation: {e}")

print()

# ============================================================================
# TEST 6: NETHERLANDS MARKET FEATURES
# ============================================================================

print("TEST 6: NETHERLANDS MARKET-SPECIFIC FEATURES")
print("-" * 80)

nl_features = {
    'Netherlands GDPR module': 'utils/netherlands_gdpr.py',
    'UAVG compliance module': 'utils/netherlands_uavg_compliance.py',
    'Dutch pricing config': 'config/pricing_config.py',
    'AI Act calculator': 'utils/ai_act_calculator.py'
}

for feature_name, file_path in nl_features.items():
    if os.path.exists(file_path):
        print(f"✅ {feature_name}: Present")
        test_results['ui_components'][feature_name] = True
    else:
        print(f"❌ {feature_name}: Missing")
        test_results['ui_components'][feature_name] = False
        gaps.append(f"Missing feature: {feature_name}")

print()

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print("=" * 80)
print("NETHERLANDS LOCALIZATION - TEST SUMMARY")
print("=" * 80)

# Calculate totals
all_tests = []
for category, tests in test_results.items():
    for test_name, result in tests.items():
        if isinstance(result, bool):
            all_tests.append(result)

total_tests = len(all_tests)
passed_tests = sum(all_tests)
verification_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

print()
print(f"OVERALL RESULTS:")
print(f"  Total Tests: {total_tests}")
print(f"  Passed: {passed_tests}")
print(f"  Failed: {total_tests - passed_tests}")
print(f"  Verification Rate: {verification_rate:.1f}%")
print()

# Summary by category
print("RESULTS BY CATEGORY:")
for category, tests in test_results.items():
    category_tests = [v for v in tests.values() if isinstance(v, bool)]
    if category_tests:
        category_passed = sum(category_tests)
        category_total = len(category_tests)
        category_rate = (category_passed / category_total * 100)
        status = "✅" if category_rate >= 80 else "⚠️" if category_rate >= 60 else "❌"
        print(f"  {status} {category}: {category_passed}/{category_total} ({category_rate:.1f}%)")

print()

# List all gaps
if gaps:
    print("IDENTIFIED GAPS:")
    for i, gap in enumerate(gaps, 1):
        print(f"  {i}. {gap}")
else:
    print("🎉 NO GAPS IDENTIFIED - Netherlands localization is complete!")

print()

# Recommendations
print("RECOMMENDATIONS:")
if verification_rate >= 90:
    print("  ✅ Netherlands localization is excellent!")
    print("  ✅ Ready for Dutch market deployment")
elif verification_rate >= 75:
    print("  ⚠️ Good coverage, minor improvements needed")
    print(f"  📋 Address {len(gaps)} identified gaps")
else:
    print("  ❌ Significant localization work needed")
    print(f"  📋 Address {len(gaps)} critical gaps before deployment")

print()

# Save results
import json
results_file = 'netherlands_localization_test_results.json'
with open(results_file, 'w') as f:
    json.dump({
        'test_date': datetime.now().isoformat(),
        'verification_rate': f"{verification_rate:.1f}%",
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'results_by_category': test_results,
        'gaps': gaps
    }, f, indent=2)

print(f"📄 Results saved to: {results_file}")
print()
print("=" * 80)
print(f"Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)
