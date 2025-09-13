#!/usr/bin/env python3
"""
Final Runtime Enforcement Production Validation Test
Exactly replicates the test conditions to verify 100% success
"""

import json
import sys
import os
import tempfile
import zipfile
sys.path.append('.')

from services.runtime_enforcement_generator import RuntimeEnforcementGenerator, EnforcementPackageType

def test_runtime_monitor_config_exact():
    """
    CRITICAL TEST 3: Runtime Monitor Config
    Exact replication of the failing test condition
    """
    print("🔍 TEST 3: Runtime Monitor Config - EXACT REPLICATION")
    print("=" * 60)
    
    generator = RuntimeEnforcementGenerator(region="Netherlands")
    
    # Generate the exact package that was failing
    package = generator.generate_runtime_monitor_package(
        application_type="web",
        monitoring_config=None  # This is what was causing the issue
    )
    
    # Extract the exact JSON content
    monitor_config_json = package.deployment_files["monitor-config.json"]
    print("Generated monitor-config.json:")
    print(monitor_config_json)
    print()
    
    # Parse it exactly as the test does
    config_dict = json.loads(monitor_config_json)
    compliance_rules = config_dict.get("compliance_rules", [])
    
    print(f"Found compliance_rules: {compliance_rules}")
    print(f"Expected: ['netherlands_uavg', 'gdpr_general']")
    
    # Exact test condition
    test_passes = compliance_rules == ["netherlands_uavg", "gdpr_general"]
    print(f"Test Result: {'✅ PASS' if test_passes else '❌ FAIL'}")
    
    return test_passes

def test_cicd_github_actions_exact():
    """
    CRITICAL TEST 2: CI/CD GitHub Actions
    Exact replication of the failing test condition
    """
    print("\n🔍 TEST 2: CI/CD GitHub Actions - EXACT REPLICATION")
    print("=" * 60)
    
    generator = RuntimeEnforcementGenerator(region="Netherlands")
    
    # Generate the exact package that was failing
    package = generator.generate_cicd_compliance_package(
        platform="github-actions",
        repository_name="test-repo",
        compliance_thresholds={
            "max_critical_issues": 0,
            "max_high_issues": 5,
            "min_compliance_score": 70
        }
    )
    
    # Extract the exact workflow content
    workflow_content = package.deployment_files["compliance-enforcement.yml"]
    
    # Check for exact strings as the test does
    required_strings = ["on:", "privacy_scan:", "compliance_threshold: 70"]
    
    print("Checking for required strings in workflow:")
    results = {}
    for req_string in required_strings:
        found = req_string in workflow_content
        results[req_string] = found
        print(f"  '{req_string}': {'✅ FOUND' if found else '❌ MISSING'}")
        
        if not found:
            # Show where it might be
            lines_with_keyword = [
                line.strip() for line in workflow_content.split('\n') 
                if any(word in line.lower() for word in req_string.replace(':', '').split())
            ][:3]
            print(f"    Similar lines: {lines_with_keyword}")
    
    test_passes = all(results.values())
    print(f"\nTest Result: {'✅ PASS' if test_passes else '❌ FAIL'}")
    
    return test_passes

def test_package_export_functionality():
    """
    Additional test: Package export to ZIP functionality
    """
    print("\n🔍 ADDITIONAL TEST: Package Export Functionality")
    print("=" * 60)
    
    generator = RuntimeEnforcementGenerator(region="Netherlands")
    
    try:
        # Test all package types
        packages = []
        
        # Cookie blocker
        cookie_package = generator.generate_cookie_blocking_package(
            website_domain="test.example.com",
            compliance_config={"strict_mode": True}
        )
        packages.append(("Cookie Blocker", cookie_package))
        
        # CI/CD compliance
        cicd_package = generator.generate_cicd_compliance_package(
            platform="github-actions",
            repository_name="test-repo"
        )
        packages.append(("CI/CD Compliance", cicd_package))
        
        # Runtime monitor
        monitor_package = generator.generate_runtime_monitor_package(
            application_type="web"
        )
        packages.append(("Runtime Monitor", monitor_package))
        
        # Test ZIP export for each
        export_results = []
        for name, package in packages:
            try:
                with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
                    zip_path = generator.package_to_zip(package, tmp.name)
                    
                    # Verify ZIP contains expected files
                    with zipfile.ZipFile(zip_path, 'r') as zf:
                        files_in_zip = zf.namelist()
                        
                    expected_files = set(package.deployment_files.keys())
                    additional_files = {'package-info.json', 'install.sh'}
                    all_expected = expected_files.union(additional_files)
                    
                    files_match = all_expected.issubset(set(files_in_zip))
                    export_results.append(files_match)
                    
                    print(f"  {name}: {'✅ EXPORTED' if files_match else '❌ FAILED'}")
                    print(f"    Expected files: {len(all_expected)}, Found: {len(files_in_zip)}")
                    
                    # Clean up
                    os.unlink(zip_path)
                    
            except Exception as e:
                print(f"  {name}: ❌ ERROR - {e}")
                export_results.append(False)
        
        return all(export_results)
        
    except Exception as e:
        print(f"❌ Export test failed: {e}")
        return False

def run_comprehensive_validation():
    """
    Run all critical tests that were failing
    """
    print("🛡️ DataGuardian Pro - Final Runtime Enforcement Validation")
    print("=" * 80)
    print("Replicating exact test conditions that were failing...")
    print()
    
    # Run the exact tests that were failing
    test_results = {}
    
    # Test 3: Runtime Monitor Config
    try:
        test_results['runtime_monitor_config'] = test_runtime_monitor_config_exact()
    except Exception as e:
        print(f"❌ Runtime Monitor Config test crashed: {e}")
        test_results['runtime_monitor_config'] = False
    
    # Test 2: CI/CD GitHub Actions  
    try:
        test_results['cicd_github_actions'] = test_cicd_github_actions_exact()
    except Exception as e:
        print(f"❌ CI/CD GitHub Actions test crashed: {e}")
        test_results['cicd_github_actions'] = False
    
    # Additional comprehensive test
    try:
        test_results['package_export'] = test_package_export_functionality()
    except Exception as e:
        print(f"❌ Package export test crashed: {e}")
        test_results['package_export'] = False
    
    # Final summary
    print("\n" + "=" * 80)
    print("🏁 FINAL VALIDATION RESULTS:")
    print("=" * 80)
    
    passed_tests = sum(1 for result in test_results.values() if result)
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print("🎉 SUCCESS: Runtime Enforcement Production Validation PASSED!")
        print("✅ Both critical fixes are working correctly")
        return 0
    else:
        print("❌ FAILURE: Additional fixes needed")
        return 1

if __name__ == "__main__":
    exit(run_comprehensive_validation())