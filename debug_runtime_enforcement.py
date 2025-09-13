#!/usr/bin/env python3
"""
Debug script for Runtime Enforcement Generator
Identifies exact content issues in generated packages
"""

import json
import sys
import os
sys.path.append('.')

from services.runtime_enforcement_generator import RuntimeEnforcementGenerator, EnforcementPackageType

def debug_runtime_monitor_config():
    """Debug runtime monitor config generation"""
    print("🔍 DEBUG: Runtime Monitor Config Generation")
    print("=" * 60)
    
    generator = RuntimeEnforcementGenerator(region="Netherlands")
    
    # Test with default config
    print("\n1. Testing with default monitoring_config=None:")
    package = generator.generate_runtime_monitor_package(
        application_type="web",
        monitoring_config=None
    )
    
    monitor_config_content = package.deployment_files["monitor-config.json"]
    print(f"Generated monitor-config.json content:")
    print(monitor_config_content)
    print()
    
    # Parse and check compliance_rules
    config_dict = json.loads(monitor_config_content)
    compliance_rules = config_dict.get('compliance_rules', 'MISSING')
    print(f"Found compliance_rules: {compliance_rules}")
    print(f"Type: {type(compliance_rules)}")
    print(f"Length: {len(compliance_rules) if isinstance(compliance_rules, list) else 'N/A'}")
    
    # Test with custom config  
    print("\n2. Testing with custom monitoring_config:")
    package2 = generator.generate_runtime_monitor_package(
        application_type="web",
        monitoring_config={"monitor_cookies": True, "custom_setting": "test"}
    )
    
    monitor_config_content2 = package2.deployment_files["monitor-config.json"]
    print(f"Generated monitor-config.json with custom config:")
    print(monitor_config_content2)
    
    config_dict2 = json.loads(monitor_config_content2)
    compliance_rules2 = config_dict2.get('compliance_rules', 'MISSING')
    print(f"Found compliance_rules in custom config: {compliance_rules2}")
    
    return compliance_rules == ["netherlands_uavg", "gdpr_general"]

def debug_github_actions_workflow():
    """Debug GitHub Actions workflow generation"""
    print("\n🔍 DEBUG: GitHub Actions Workflow Generation")
    print("=" * 60)
    
    generator = RuntimeEnforcementGenerator(region="Netherlands")
    
    package = generator.generate_cicd_compliance_package(
        platform="github-actions",
        repository_name="test-repo",
        compliance_thresholds={
            "max_critical_issues": 0,
            "max_high_issues": 5,
            "min_compliance_score": 70
        }
    )
    
    workflow_content = package.deployment_files["compliance-enforcement.yml"]
    print("Generated GitHub Actions workflow content:")
    print("=" * 40)
    print(workflow_content[:2000])  # First 2000 chars
    print("=" * 40)
    
    # Check for required strings
    required_strings = ["on:", "privacy_scan:", "compliance_threshold: 70"]
    
    results = {}
    for req_string in required_strings:
        found = req_string in workflow_content
        results[req_string] = found
        print(f"✅ Found '{req_string}': {found}")
        
        if not found:
            # Try to find similar strings
            if req_string == "on:":
                similar = [line.strip() for line in workflow_content.split('\n') if 'on' in line.lower()][:3]
                print(f"   Similar lines: {similar}")
            elif req_string == "privacy_scan:":
                similar = [line.strip() for line in workflow_content.split('\n') if 'privacy' in line.lower() or 'scan' in line.lower()][:3]  
                print(f"   Similar lines: {similar}")
            elif req_string == "compliance_threshold: 70":
                similar = [line.strip() for line in workflow_content.split('\n') if 'compliance' in line.lower() or '70' in line][:3]
                print(f"   Similar lines: {similar}")
    
    return all(results.values())

def debug_package_generation_process():
    """Debug the complete package generation process"""
    print("\n🔍 DEBUG: Complete Package Generation Process")
    print("=" * 60)
    
    generator = RuntimeEnforcementGenerator(region="Netherlands")
    
    # Test all package types
    package_types = [
        (EnforcementPackageType.COOKIE_BLOCKER, {
            'website_domain': 'test.nl'
        }),
        (EnforcementPackageType.CICD_COMPLIANCE, {
            'platform': 'github-actions',
            'repository_name': 'test-repo'
        }),
        (EnforcementPackageType.RUNTIME_MONITOR, {
            'application_type': 'web'
        })
    ]
    
    for package_type, kwargs in package_types:
        print(f"\nGenerating {package_type.value}...")
        try:
            package = generator.generate_enforcement_package(package_type, **kwargs)
            print(f"✅ Successfully generated: {package.name}")
            print(f"   Files: {list(package.deployment_files.keys())}")
            print(f"   Compliance rules: {package.compliance_rules}")
            
            # Check specific content for each type
            if package_type == EnforcementPackageType.RUNTIME_MONITOR:
                config = json.loads(package.deployment_files["monitor-config.json"])
                print(f"   Monitor compliance_rules: {config.get('compliance_rules', 'MISSING')}")
            elif package_type == EnforcementPackageType.CICD_COMPLIANCE:
                workflow = package.deployment_files["compliance-enforcement.yml"]
                has_required = all(s in workflow for s in ["on:", "privacy_scan:", "compliance_threshold: 70"])
                print(f"   Has required GitHub strings: {has_required}")
                
        except Exception as e:
            print(f"❌ Failed to generate {package_type.value}: {e}")

def main():
    """Run all debug tests"""
    print("🛡️ DataGuardian Pro - Runtime Enforcement Debug")
    print("=" * 80)
    
    results = {}
    
    # Debug runtime monitor config
    try:
        results['runtime_monitor'] = debug_runtime_monitor_config()
    except Exception as e:
        print(f"❌ Runtime monitor debug failed: {e}")
        results['runtime_monitor'] = False
    
    # Debug GitHub Actions workflow
    try:
        results['github_actions'] = debug_github_actions_workflow()
    except Exception as e:
        print(f"❌ GitHub Actions debug failed: {e}")
        results['github_actions'] = False
    
    # Debug complete process
    try:
        debug_package_generation_process()
    except Exception as e:
        print(f"❌ Package generation debug failed: {e}")
    
    # Summary
    print("\n" + "=" * 80)
    print("🔍 DEBUG SUMMARY:")
    print(f"Runtime Monitor Config Fixed: {results.get('runtime_monitor', False)}")
    print(f"GitHub Actions Workflow Fixed: {results.get('github_actions', False)}")
    
    if all(results.values()):
        print("✅ ALL CRITICAL FIXES APPEAR TO BE WORKING!")
        return 0
    else:
        print("❌ CRITICAL FIXES STILL NEEDED")
        return 1

if __name__ == "__main__":
    exit(main())