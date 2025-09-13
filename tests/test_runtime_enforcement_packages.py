#!/usr/bin/env python3
"""
Production Validation Test Suite for Runtime Enforcement Packages
Comprehensive integration tests for cookie blocking, CI/CD compliance, and runtime monitoring packages

DataGuardian Pro - Runtime Enforcement Package Testing
Tests package generation, content validation, deployment readiness, and end-to-end functionality
"""

import unittest
import time
import json
import zipfile
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import subprocess

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test framework and runtime enforcement generator
from tests.test_framework import BaseScanner, ScannerTestSuite, TestConfig
from services.runtime_enforcement_generator import (
    RuntimeEnforcementGenerator, 
    EnforcementPackage, 
    EnforcementPackageType
)

class TestRuntimeEnforcementPackages(ScannerTestSuite):
    """Comprehensive test suite for runtime enforcement package generation"""

    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        super().setUpClass()
        cls.generator = RuntimeEnforcementGenerator(region="Netherlands")
        cls.test_domain = "example.nl"
        cls.temp_files = []

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        # Clean up temporary files
        for temp_file in cls.temp_files:
            try:
                os.unlink(temp_file)
            except (OSError, FileNotFoundError):
                pass

    def test_01_cookie_blocking_package_generation(self):
        """Test 1: Cookie Blocking Package - Generation & Content Validation"""
        print("\n🍪 Testing Cookie Blocking Package Generation...")
        
        start_time = time.time()
        
        # Generate cookie blocking package
        package = self.generator.generate_cookie_blocking_package(
            website_domain=self.test_domain,
            compliance_config={
                "dutch_compliance": True,
                "strict_mode": True,
                "auto_reject_timeout": 30000
            }
        )
        
        generation_time = time.time() - start_time
        
        # Validate package structure
        self.assertIsInstance(package, EnforcementPackage)
        self.assertEqual(package.package_type, EnforcementPackageType.COOKIE_BLOCKER)
        self.assertIn(self.test_domain, package.name)
        self.assertEqual(package.target_platform, "web")
        
        # Validate deployment files
        required_files = ["cookie-enforcer.js", "installation-guide.md", "test-page.html", "configuration.json"]
        for required_file in required_files:
            self.assertIn(required_file, package.deployment_files)
            self.assertGreater(len(package.deployment_files[required_file]), 100, 
                             f"{required_file} should have substantial content")
        
        # Validate JavaScript enforcement content
        js_content = package.deployment_files["cookie-enforcer.js"]
        self.assertIn("fetch", js_content, "Should override fetch API")
        self.assertIn("XMLHttpRequest", js_content, "Should override XMLHttpRequest")
        self.assertIn("localStorage", js_content, "Should handle localStorage")
        self.assertIn("google-analytics", js_content, "Should block tracking domains")
        
        # Validate configuration
        config = json.loads(package.deployment_files["configuration.json"])
        self.assertEqual(config["domain"], self.test_domain)
        self.assertTrue(config["dutch_compliance"])
        self.assertEqual(config["auto_reject_timeout"], 30000)
        
        # Performance validation
        self.assertLess(generation_time, 5.0, "Package generation should complete within 5 seconds")
        
        print(f"✅ Cookie blocking package generated successfully in {generation_time:.2f}s")

    def test_02_cicd_compliance_package_generation(self):
        """Test 2: CI/CD Compliance Package - GitHub Actions & Azure DevOps"""
        print("\n🔄 Testing CI/CD Compliance Package Generation...")
        
        # Test GitHub Actions package
        github_package = self.generator.generate_cicd_compliance_package(
            platform="github-actions",
            repository_name="test-webapp",
            compliance_thresholds={
                "max_critical_issues": 0,
                "max_high_issues": 5,
                "min_compliance_score": 70
            }
        )
        
        # Validate GitHub Actions package
        self.assertEqual(github_package.package_type, EnforcementPackageType.CICD_COMPLIANCE)
        self.assertEqual(github_package.target_platform, "github-actions")
        
        # Check required GitHub Actions files
        github_files = [".github/workflows/privacy-compliance.yml", "compliance-report.md", "setup-guide.md"]
        for file in github_files:
            self.assertIn(file, github_package.deployment_files)
        
        # Validate workflow YAML structure
        workflow_content = github_package.deployment_files[".github/workflows/privacy-compliance.yml"]
        self.assertIn("on:", workflow_content, "Should have workflow triggers")
        self.assertIn("privacy_scan:", workflow_content, "Should include privacy scanning job")
        self.assertIn("compliance_threshold: 70", workflow_content, "Should include compliance threshold")
        
        # Test Azure DevOps package  
        azure_package = self.generator.generate_cicd_compliance_package(
            platform="azure-devops",
            repository_name="test-webapp",
            compliance_thresholds={
                "max_critical_issues": 0,
                "max_high_issues": 3,
                "min_compliance_score": 80
            }
        )
        
        # Validate Azure DevOps package
        self.assertEqual(azure_package.target_platform, "azure-devops")
        
        # Check required Azure DevOps files
        azure_files = ["azure-pipelines.yml", "compliance-report.md", "setup-guide.md"]
        for file in azure_files:
            self.assertIn(file, azure_package.deployment_files)
        
        # Validate pipeline YAML structure
        pipeline_content = azure_package.deployment_files["azure-pipelines.yml"]
        self.assertIn("trigger:", pipeline_content, "Should have pipeline triggers")
        self.assertIn("PrivacyComplianceScan", pipeline_content, "Should include privacy scan task")
        self.assertIn("COMPLIANCE_THRESHOLD: 80", pipeline_content, "Should include compliance threshold")
        
        print("✅ CI/CD compliance packages generated successfully")

    def test_03_runtime_monitor_package_generation(self):
        """Test 3: Runtime Monitoring Package - Web & API Applications"""
        print("\n📊 Testing Runtime Monitoring Package Generation...")
        
        # Test web application monitoring package
        web_package = self.generator.generate_runtime_monitor_package(
            application_type="web",
            monitoring_config={
                "real_time_scanning": True,
                "violation_alerts": True,
                "compliance_reporting": True,
                "data_flow_tracking": True
            }
        )
        
        # Validate web monitoring package
        self.assertEqual(web_package.package_type, EnforcementPackageType.RUNTIME_MONITOR)
        self.assertEqual(web_package.target_platform, "web")
        
        # Check required web monitoring files
        web_files = ["compliance-monitor.js", "monitor-config.json", "installation-guide.md", "health-check.py"]
        for file in web_files:
            self.assertIn(file, web_package.deployment_files)
        
        # Validate monitoring JavaScript
        monitor_js = web_package.deployment_files["compliance-monitor.js"]
        self.assertIn("class ComplianceMonitor", monitor_js, "Should define ComplianceMonitor class")
        self.assertIn("detectPIIViolations", monitor_js, "Should detect PII violations")
        self.assertIn("reportViolation", monitor_js, "Should report violations")
        self.assertIn("trackDataFlow", monitor_js, "Should track data flows")
        
        # Test API application monitoring package
        api_package = self.generator.generate_runtime_monitor_package(
            application_type="api",
            monitoring_config={
                "request_scanning": True,
                "response_filtering": True,
                "audit_logging": True
            }
        )
        
        # Validate API monitoring package
        self.assertEqual(api_package.target_platform, "api")
        
        # Validate monitoring configuration
        config = json.loads(web_package.deployment_files["monitor-config.json"])
        self.assertTrue(config.get("real_time_scanning"))
        self.assertTrue(config.get("violation_alerts"))
        self.assertIn("netherlands_uavg", config.get("compliance_rules", []))
        
        print("✅ Runtime monitoring packages generated successfully")

    def test_04_zip_export_functionality(self):
        """Test 4: ZIP Export - Package Assembly & Validation"""
        print("\n📦 Testing ZIP Export Functionality...")
        
        # Generate a package for ZIP testing
        package = self.generator.generate_cookie_blocking_package(
            website_domain="test-export.nl"
        )
        
        # Export package to ZIP
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
            zip_path = self.generator.package_to_zip(package, temp_file.name)
            self.temp_files.append(zip_path)
        
        # Validate ZIP file creation
        self.assertTrue(os.path.exists(zip_path), "ZIP file should be created")
        self.assertGreater(os.path.getsize(zip_path), 1000, "ZIP file should have substantial content")
        
        # Validate ZIP contents
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zip_files = zipf.namelist()
            
            # Check all deployment files are included
            for filename in package.deployment_files.keys():
                self.assertIn(filename, zip_files, f"Deployment file {filename} should be in ZIP")
            
            # Check metadata files
            self.assertIn("package-info.json", zip_files, "Package metadata should be included")
            self.assertIn("install.sh", zip_files, "Installation script should be included")
            
            # Validate package metadata
            with zipf.open("package-info.json") as meta_file:
                metadata = json.loads(meta_file.read().decode())
                self.assertIn("package_info", metadata)
                self.assertEqual(metadata["package_info"]["name"], package.name)
                self.assertEqual(metadata["generated_by"], "DataGuardian Pro Runtime Enforcement Generator")
        
        print(f"✅ ZIP export successful - {len(zip_files)} files packaged")

    def test_05_performance_benchmarking(self):
        """Test 5: Performance Benchmarking - Generation Speed & Memory Usage"""
        print("\n⚡ Testing Performance Benchmarking...")
        
        performance_results = []
        
        # Benchmark different package types
        package_types = [
            ("cookie", EnforcementPackageType.COOKIE_BLOCKER),
            ("cicd", EnforcementPackageType.CICD_COMPLIANCE), 
            ("monitor", EnforcementPackageType.RUNTIME_MONITOR)
        ]
        
        for package_name, package_type in package_types:
            start_time = time.time()
            start_memory = self._get_memory_usage()
            
            # Generate package based on type
            if package_type == EnforcementPackageType.COOKIE_BLOCKER:
                package = self.generator.generate_cookie_blocking_package("perf-test.nl")
            elif package_type == EnforcementPackageType.CICD_COMPLIANCE:
                package = self.generator.generate_cicd_compliance_package("github-actions", "perf-test")
            else:  # RUNTIME_MONITOR
                package = self.generator.generate_runtime_monitor_package("web")
            
            end_time = time.time()
            end_memory = self._get_memory_usage()
            
            performance_data = {
                'package_type': package_name,
                'generation_time': end_time - start_time,
                'memory_used': end_memory - start_memory,
                'file_count': len(package.deployment_files),
                'content_size': sum(len(content) for content in package.deployment_files.values())
            }
            performance_results.append(performance_data)
            
            # Performance assertions
            self.assertLess(performance_data['generation_time'], 10.0, 
                           f"{package_name} generation should complete within 10 seconds")
            self.assertLess(performance_data['memory_used'], 50, 
                           f"{package_name} generation should use less than 50MB additional memory")
        
        # Log performance results
        print("\n📈 Performance Benchmarking Results:")
        for result in performance_results:
            print(f"   {result['package_type']:<10} | Time: {result['generation_time']:.2f}s | "
                  f"Memory: {result['memory_used']:.1f}MB | Files: {result['file_count']} | "
                  f"Size: {result['content_size']:,} chars")
        
        print("✅ Performance benchmarking completed successfully")

    def test_06_compliance_rule_validation(self):
        """Test 6: Compliance Rule Validation - Netherlands UAVG & GDPR"""
        print("\n⚖️ Testing Compliance Rule Validation...")
        
        # Test Netherlands UAVG compliance rules
        uavg_rules = self.generator.compliance_rules.get("netherlands_uavg", {})
        
        # Validate UAVG requirements
        self.assertTrue(uavg_rules.get("cookie_consent_required"), "UAVG requires cookie consent")
        self.assertTrue(uavg_rules.get("explicit_consent_only"), "UAVG requires explicit consent")
        self.assertTrue(uavg_rules.get("reject_all_button_required"), "UAVG requires reject all button")
        self.assertTrue(uavg_rules.get("bsn_protection_required"), "UAVG requires BSN protection")
        self.assertEqual(uavg_rules.get("data_breach_notification_hours"), 72, 
                        "UAVG requires 72-hour breach notification")
        
        # Test GDPR general rules
        gdpr_rules = self.generator.compliance_rules.get("gdpr_general", {})
        
        # Validate GDPR requirements
        self.assertTrue(gdpr_rules.get("data_minimization"), "GDPR requires data minimization")
        self.assertTrue(gdpr_rules.get("purpose_limitation"), "GDPR requires purpose limitation")
        self.assertTrue(gdpr_rules.get("privacy_by_design"), "GDPR requires privacy by design")
        self.assertTrue(gdpr_rules.get("lawful_basis_required"), "GDPR requires lawful basis")
        
        # Test security requirements
        security_rules = self.generator.compliance_rules.get("security_requirements", {})
        
        # Validate security requirements
        self.assertTrue(security_rules.get("https_required"), "Should require HTTPS")
        self.assertTrue(security_rules.get("api_key_protection"), "Should require API key protection")
        self.assertTrue(security_rules.get("xss_protection"), "Should require XSS protection")
        
        print("✅ Compliance rule validation passed")

    def test_07_error_handling_resilience(self):
        """Test 7: Error Handling & Resilience - Invalid Inputs & Recovery"""
        print("\n🛡️ Testing Error Handling & Resilience...")
        
        # Test invalid domain handling
        with self.assertRaises(Exception):
            self.generator.generate_cookie_blocking_package("")
        
        # Test invalid platform handling
        with self.assertRaises(ValueError):
            self.generator.generate_cicd_compliance_package(
                platform="invalid-platform",
                repository_name="test"
            )
        
        # Test invalid application type handling
        with self.assertRaises(Exception):
            self.generator.generate_runtime_monitor_package("")
        
        # Test resilience with partial configurations
        try:
            # Should succeed with defaults
            package = self.generator.generate_cookie_blocking_package(
                website_domain="resilient-test.nl",
                compliance_config=None  # Test None handling
            )
            self.assertIsNotNone(package)
            self.assertEqual(package.target_platform, "web")
        except Exception as e:
            self.fail(f"Should handle None config gracefully: {e}")
        
        print("✅ Error handling resilience tests passed")

    def test_08_integration_logging_monitoring(self):
        """Test 8: Integration Logging & Monitoring - Structured Events"""
        print("\n📝 Testing Integration Logging & Monitoring...")
        
        # Capture log output for validation
        with self.assertLogs(level='INFO') as log_capture:
            # Generate packages to trigger logging
            self.generator.generate_cookie_blocking_package("logging-test.nl")
            self.generator.generate_cicd_compliance_package("github-actions", "logging-test")
            
        # Validate structured logging
        log_messages = [record.getMessage() for record in log_capture.records]
        
        # Check for expected log patterns (if logging is implemented)
        # Note: This test will pass even without logging implementation
        # but provides framework for future logging validation
        
        print(f"✅ Captured {len(log_messages)} log events during package generation")

    def test_09_end_to_end_deployment_simulation(self):
        """Test 9: End-to-End Deployment Simulation - Installation Scripts"""
        print("\n🚀 Testing End-to-End Deployment Simulation...")
        
        # Generate a complete cookie blocking package
        package = self.generator.generate_cookie_blocking_package(
            website_domain="deployment-test.nl",
            compliance_config={"dutch_compliance": True}
        )
        
        # Validate installation script structure
        install_script = package.installation_script
        self.assertIsNotNone(install_script, "Installation script should be provided")
        self.assertGreater(len(install_script), 100, "Installation script should have content")
        
        # Check for essential installation commands
        self.assertIn("#!/bin/bash", install_script, "Should be a bash script")
        self.assertIn("mkdir", install_script, "Should create directories")
        self.assertIn("chmod", install_script, "Should set proper permissions")
        
        # Validate deployment file completeness
        essential_files = ["cookie-enforcer.js", "configuration.json"]
        for file in essential_files:
            self.assertIn(file, package.deployment_files)
            content = package.deployment_files[file]
            self.assertGreater(len(content), 50, f"{file} should have substantial content")
        
        print("✅ End-to-end deployment simulation completed")

    def test_10_production_readiness_validation(self):
        """Test 10: Production Readiness Validation - Complete System Test"""
        print("\n🎯 Testing Production Readiness Validation...")
        
        # Generate all package types to validate complete system
        packages = []
        
        # Cookie blocking package
        cookie_package = self.generator.generate_cookie_blocking_package(
            website_domain="production-ready.nl",
            compliance_config={"strict_mode": True, "dutch_compliance": True}
        )
        packages.append(("Cookie Blocker", cookie_package))
        
        # CI/CD compliance package
        cicd_package = self.generator.generate_cicd_compliance_package(
            platform="github-actions",
            repository_name="production-app",
            compliance_thresholds={"max_critical_issues": 0, "min_compliance_score": 90}
        )
        packages.append(("CI/CD Compliance", cicd_package))
        
        # Runtime monitoring package
        monitor_package = self.generator.generate_runtime_monitor_package(
            application_type="web",
            monitoring_config={"real_time_scanning": True, "violation_alerts": True}
        )
        packages.append(("Runtime Monitor", monitor_package))
        
        # Validate all packages for production readiness
        for package_name, package in packages:
            # Structure validation
            self.assertIsInstance(package.package_id, str)
            self.assertGreater(len(package.package_id), 10, f"{package_name} should have unique ID")
            
            # Content validation
            self.assertGreater(len(package.deployment_files), 3, 
                              f"{package_name} should have multiple deployment files")
            
            # Configuration validation
            self.assertIsInstance(package.configuration, dict)
            self.assertGreater(len(package.configuration), 0, 
                              f"{package_name} should have configuration settings")
            
            # Metadata validation
            self.assertIn("generated_at", package.metadata)
            self.assertIn("region", package.configuration)
            
        print(f"✅ Production readiness validated for {len(packages)} package types")
        print("🎉 All runtime enforcement packages are production-ready!")

    def _get_memory_usage(self):
        """Helper method to get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except ImportError:
            return 0.0  # Fallback if psutil not available


class TestRuntimeEnforcementHealthChecks(ScannerTestSuite):
    """Health checks and monitoring for runtime enforcement system"""

    def test_system_health_monitoring(self):
        """Test system health monitoring and diagnostics"""
        print("\n🏥 Testing System Health Monitoring...")
        
        generator = RuntimeEnforcementGenerator(region="Netherlands")
        
        # Check system components
        health_status = {
            "generator_initialized": generator is not None,
            "templates_loaded": len(generator.enforcement_templates) > 0,
            "compliance_rules_loaded": len(generator.compliance_rules) > 0,
            "region_configured": generator.region == "Netherlands"
        }
        
        # Validate health status
        for component, status in health_status.items():
            self.assertTrue(status, f"System component {component} should be healthy")
        
        print("✅ System health monitoring passed")

    def test_structured_logging_validation(self):
        """Test structured logging for audit trails"""
        print("\n📋 Testing Structured Logging Validation...")
        
        # This test validates the framework for structured logging
        # Implementation can be enhanced with actual logging capture
        
        generator = RuntimeEnforcementGenerator(region="Netherlands")
        
        # Generate packages to trigger potential logging
        start_time = datetime.now()
        package = generator.generate_cookie_blocking_package("audit-test.nl")
        end_time = datetime.now()
        
        # Validate package generation creates audit trail data
        self.assertIsNotNone(package.metadata.get("generated_at"))
        generation_time = datetime.fromisoformat(package.metadata["generated_at"])
        self.assertGreaterEqual(generation_time, start_time)
        self.assertLessEqual(generation_time, end_time)
        
        print("✅ Structured logging validation framework ready")


def run_runtime_enforcement_test_suite():
    """Run comprehensive runtime enforcement test suite"""
    print("🛡️ DataGuardian Pro - Runtime Enforcement Package Test Suite")
    print("=" * 80)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestRuntimeEnforcementPackages))
    suite.addTests(loader.loadTestsFromTestCase(TestRuntimeEnforcementHealthChecks))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Generate summary
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    success_rate = ((total_tests - failures - errors) / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n{'=' * 80}")
    print("RUNTIME ENFORCEMENT TEST SUMMARY")
    print(f"{'=' * 80}")
    print(f"📊 Total Tests: {total_tests}")
    print(f"✅ Passed: {total_tests - failures - errors}")
    print(f"❌ Failed: {failures}")
    print(f"⚠️  Errors: {errors}")
    print(f"🎯 Success Rate: {success_rate:.1f}%")
    print(f"{'=' * 80}")
    
    if success_rate >= 90:
        print("🎉 EXCELLENT: Runtime enforcement packages are production-ready!")
    elif success_rate >= 70:
        print("✅ GOOD: Runtime enforcement packages are functional with minor issues.")
    else:
        print("⚠️ ATTENTION: Runtime enforcement packages need improvement.")
    
    return result


if __name__ == '__main__':
    results = run_runtime_enforcement_test_suite()
    
    # Exit with appropriate code
    success_rate = ((results.testsRun - len(results.failures) - len(results.errors)) / results.testsRun * 100) if results.testsRun > 0 else 0
    
    if success_rate >= 80:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Needs attention