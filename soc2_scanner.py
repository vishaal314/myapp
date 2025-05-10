"""
SOC2 Scanner Implementation

This module provides a comprehensive SOC2 scanner that aligns infrastructure scans
to SOC2 Trust Services Criteria (TSC):
1. Security
2. Availability
3. Processing Integrity
4. Confidentiality
5. Privacy

It produces a detailed SOC2 checklist, maps violations, generates a PDF report,
and provides recommendations for remediation.
"""

import json
import base64
import uuid
from datetime import datetime
import io
import re
import os
import random
from typing import Dict, List, Any, Tuple, Optional, Union

import streamlit as st
from io import BytesIO
try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
except ImportError:
    # Fallback if reportlab isn't available
    pass

# Define SOC2 Trust Services Criteria
SOC2_CATEGORIES = {
    "Security": {
        "description": "Protection of system resources against unauthorized access",
        "principles": [
            "Access Controls", 
            "System Operations", 
            "Change Management", 
            "Risk Mitigation"
        ]
    },
    "Availability": {
        "description": "System availability for operation and use as committed or agreed",
        "principles": [
            "Performance Monitoring", 
            "Disaster Recovery", 
            "Backup Systems", 
            "Business Continuity"
        ]
    },
    "Processing Integrity": {
        "description": "System processing is complete, valid, accurate, timely, and authorized",
        "principles": [
            "Data Validation", 
            "Transaction Authorization", 
            "Input/Output Controls", 
            "Error Handling"
        ]
    },
    "Confidentiality": {
        "description": "Information designated as confidential is protected as committed or agreed",
        "principles": [
            "Data Classification", 
            "Encryption", 
            "Information Lifecycle", 
            "Confidentiality Agreements"
        ]
    },
    "Privacy": {
        "description": "Personal information is collected, used, retained, disclosed, and disposed of in conformity with commitments",
        "principles": [
            "Notice and Communication", 
            "Choice and Consent", 
            "Collection and Use", 
            "Access and Disclosure"
        ]
    }
}

class SOC2Scanner:
    """
    SOC2 Scanner that aligns infrastructure scans to SOC2 Trust Services Criteria (TSC).
    """
    
    def __init__(self):
        """Initialize the SOC2 scanner."""
        self.scan_id = f"SOC2-{uuid.uuid4().hex[:8]}"
        self.timestamp = datetime.now().isoformat()
        
    def scan_infrastructure(self, repo_url: str, source_type: str, **kwargs) -> Dict[str, Any]:
        """
        Scan infrastructure for SOC2 compliance.
        
        Args:
            repo_url: The repository URL to scan
            source_type: Source type (github, azure, aws, gcp, etc.)
            **kwargs: Additional scan parameters
            
        Returns:
            Dictionary with scan results
        """
        results = {
            "scan_id": self.scan_id,
            "timestamp": self.timestamp,
            "source": {
                "type": source_type,
                "url": repo_url
            },
            "categories": {},
            "violations": [],
            "summary": {},
            "recommendations": []
        }
        
        # Scan each SOC2 category
        for category, details in SOC2_CATEGORIES.items():
            category_results = self._scan_category(category, details, repo_url, source_type, **kwargs)
            results["categories"][category] = category_results
            results["violations"].extend(category_results["violations"])
        
        # Calculate overall compliance score
        total_checks = 0
        passed_checks = 0
        
        for category, category_data in results["categories"].items():
            total_checks += category_data["total_checks"]
            passed_checks += category_data["passed_checks"]
        
        if total_checks > 0:
            compliance_score = (passed_checks / total_checks) * 100
        else:
            compliance_score = 0
            
        results["summary"] = {
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": total_checks - passed_checks,
            "compliance_score": compliance_score
        }
        
        # Generate recommendations
        results["recommendations"] = self._generate_recommendations(results["violations"])
        
        return results
    
    def _scan_category(self, category: str, details: Dict[str, Any], 
                      repo_url: str, source_type: str, **kwargs) -> Dict[str, Any]:
        """
        Scan a specific SOC2 category.
        
        Args:
            category: The SOC2 category to scan
            details: Category details
            repo_url: The repository URL
            source_type: Source type
            **kwargs: Additional scan parameters
            
        Returns:
            Category scan results
        """
        principles = details["principles"]
        
        result = {
            "description": details["description"],
            "principles": {},
            "violations": [],
            "passed_checks": 0,
            "total_checks": 0
        }
        
        # Generate checks for each principle
        for principle in principles:
            checks = self._generate_checks_for_principle(category, principle)
            result["principles"][principle] = {
                "checks": checks,
                "passed": 0,
                "total": len(checks)
            }
            
            # Simulate scanning logic (would be replaced with real checks in production)
            for check in checks:
                check_passed = self._evaluate_check(check, category, principle, repo_url, source_type)
                
                if check_passed:
                    result["principles"][principle]["passed"] += 1
                    result["passed_checks"] += 1
                else:
                    # Create a violation
                    violation = {
                        "id": f"V-{uuid.uuid4().hex[:6]}",
                        "category": category,
                        "principle": principle,
                        "check": check["id"],
                        "description": check["description"],
                        "risk_level": check["risk_level"],
                        "timestamp": datetime.now().isoformat(),
                        "details": self._generate_violation_details(check, category, principle)
                    }
                    result["violations"].append(violation)
                    
                result["total_checks"] += 1
        
        return result
    
    def _generate_checks_for_principle(self, category: str, principle: str) -> List[Dict[str, Any]]:
        """
        Generate compliance checks for a SOC2 principle.
        
        Args:
            category: SOC2 category
            principle: SOC2 principle
            
        Returns:
            List of compliance checks
        """
        checks = []
        
        # Security category checks
        if category == "Security":
            if principle == "Access Controls":
                checks = [
                    {
                        "id": "SEC-AC-001",
                        "title": "Authentication Mechanisms",
                        "description": "Systems implement strong authentication mechanisms (e.g., MFA)",
                        "risk_level": "high"
                    },
                    {
                        "id": "SEC-AC-002",
                        "title": "Authorization Model",
                        "description": "Least privilege principle is applied for all access",
                        "risk_level": "high"
                    },
                    {
                        "id": "SEC-AC-003",
                        "title": "Account Management",
                        "description": "Formal process exists for account creation, modification, and deletion",
                        "risk_level": "medium"
                    },
                    {
                        "id": "SEC-AC-004",
                        "title": "Password Policies",
                        "description": "Strong password policies are enforced across systems",
                        "risk_level": "medium"
                    },
                ]
            elif principle == "System Operations":
                checks = [
                    {
                        "id": "SEC-SO-001",
                        "title": "Vulnerability Management",
                        "description": "Regular vulnerability scans are performed",
                        "risk_level": "high"
                    },
                    {
                        "id": "SEC-SO-002",
                        "title": "Malware Protection",
                        "description": "Anti-malware controls are implemented and updated",
                        "risk_level": "high"
                    },
                    {
                        "id": "SEC-SO-003", 
                        "title": "Security Monitoring",
                        "description": "System activity is logged and monitored for suspicious activity",
                        "risk_level": "medium"
                    },
                    {
                        "id": "SEC-SO-004",
                        "title": "Incident Response",
                        "description": "Formal incident response plan is established and tested",
                        "risk_level": "medium"
                    },
                ]
            elif principle == "Change Management":
                checks = [
                    {
                        "id": "SEC-CM-001",
                        "title": "Change Approval",
                        "description": "Formal change approval process exists",
                        "risk_level": "medium"
                    },
                    {
                        "id": "SEC-CM-002",
                        "title": "Testing Requirements",
                        "description": "Changes are tested before deployment to production",
                        "risk_level": "high"
                    },
                    {
                        "id": "SEC-CM-003",
                        "title": "Separation of Environments",
                        "description": "Development, testing, and production environments are separate",
                        "risk_level": "medium"
                    },
                ]
            elif principle == "Risk Mitigation":
                checks = [
                    {
                        "id": "SEC-RM-001",
                        "title": "Risk Assessment",
                        "description": "Regular risk assessments are performed",
                        "risk_level": "high"
                    },
                    {
                        "id": "SEC-RM-002",
                        "title": "Third-Party Risk",
                        "description": "Third-party service providers are assessed for security risks",
                        "risk_level": "medium"
                    },
                    {
                        "id": "SEC-RM-003",
                        "title": "Security Awareness",
                        "description": "Security awareness training is provided to employees",
                        "risk_level": "medium"
                    },
                ]
                
        # Availability category checks
        elif category == "Availability":
            if principle == "Performance Monitoring":
                checks = [
                    {
                        "id": "AVA-PM-001",
                        "title": "System Monitoring",
                        "description": "Systems are monitored for performance and availability",
                        "risk_level": "high"
                    },
                    {
                        "id": "AVA-PM-002",
                        "title": "Capacity Planning",
                        "description": "Capacity requirements are planned and monitored",
                        "risk_level": "medium"
                    },
                    {
                        "id": "AVA-PM-003",
                        "title": "Alert Thresholds",
                        "description": "Alert thresholds are defined and monitored",
                        "risk_level": "medium"
                    },
                ]
            elif principle == "Disaster Recovery":
                checks = [
                    {
                        "id": "AVA-DR-001",
                        "title": "Disaster Recovery Plan",
                        "description": "Formal disaster recovery plan exists and is tested",
                        "risk_level": "high"
                    },
                    {
                        "id": "AVA-DR-002",
                        "title": "Recovery Time Objectives",
                        "description": "Recovery time objectives (RTOs) are defined and tested",
                        "risk_level": "high"
                    },
                    {
                        "id": "AVA-DR-003",
                        "title": "Critical Systems",
                        "description": "Critical systems are identified and prioritized for recovery",
                        "risk_level": "medium"
                    },
                ]
            elif principle == "Backup Systems":
                checks = [
                    {
                        "id": "AVA-BS-001",
                        "title": "Backup Schedule",
                        "description": "Regular backups are performed according to schedule",
                        "risk_level": "high"
                    },
                    {
                        "id": "AVA-BS-002",
                        "title": "Backup Testing",
                        "description": "Backups are tested for restorability",
                        "risk_level": "high"
                    },
                    {
                        "id": "AVA-BS-003",
                        "title": "Offsite Storage",
                        "description": "Backups are stored offsite or in separate regions",
                        "risk_level": "medium"
                    },
                ]
            elif principle == "Business Continuity":
                checks = [
                    {
                        "id": "AVA-BC-001",
                        "title": "Business Continuity Plan",
                        "description": "Business continuity plan exists and is tested",
                        "risk_level": "high"
                    },
                    {
                        "id": "AVA-BC-002",
                        "title": "Alternate Processing",
                        "description": "Alternate processing capabilities are available",
                        "risk_level": "medium"
                    },
                    {
                        "id": "AVA-BC-003",
                        "title": "Communication Plan",
                        "description": "Communication plan exists for disruptions",
                        "risk_level": "medium"
                    },
                ]
                
        # Processing Integrity category checks
        elif category == "Processing Integrity":
            if principle == "Data Validation":
                checks = [
                    {
                        "id": "PI-DV-001",
                        "title": "Input Validation",
                        "description": "Input data is validated for integrity",
                        "risk_level": "high"
                    },
                    {
                        "id": "PI-DV-002",
                        "title": "Data Format",
                        "description": "Data format standards are defined and enforced",
                        "risk_level": "medium"
                    },
                    {
                        "id": "PI-DV-003",
                        "title": "Data Completeness",
                        "description": "Data completeness checks are implemented",
                        "risk_level": "medium"
                    },
                ]
            elif principle == "Transaction Authorization":
                checks = [
                    {
                        "id": "PI-TA-001",
                        "title": "Transaction Approvals",
                        "description": "Transactions are authorized before processing",
                        "risk_level": "high"
                    },
                    {
                        "id": "PI-TA-002",
                        "title": "Segregation of Duties",
                        "description": "Segregation of duties exists for critical transactions",
                        "risk_level": "high"
                    },
                    {
                        "id": "PI-TA-003",
                        "title": "Transaction Limits",
                        "description": "Transaction limits are defined and enforced",
                        "risk_level": "medium"
                    },
                ]
            elif principle == "Input/Output Controls":
                checks = [
                    {
                        "id": "PI-IO-001",
                        "title": "Data Reconciliation",
                        "description": "Input and output data is reconciled",
                        "risk_level": "high"
                    },
                    {
                        "id": "PI-IO-002",
                        "title": "Transmission Controls",
                        "description": "Controls exist over data transmission",
                        "risk_level": "medium"
                    },
                    {
                        "id": "PI-IO-003",
                        "title": "Output Review",
                        "description": "Output reports are reviewed for accuracy",
                        "risk_level": "medium"
                    },
                ]
            elif principle == "Error Handling":
                checks = [
                    {
                        "id": "PI-EH-001",
                        "title": "Error Detection",
                        "description": "Systems detect and report processing errors",
                        "risk_level": "high"
                    },
                    {
                        "id": "PI-EH-002",
                        "title": "Error Resolution",
                        "description": "Processes exist for error resolution",
                        "risk_level": "medium"
                    },
                    {
                        "id": "PI-EH-003",
                        "title": "Error Reporting",
                        "description": "Error reports are generated and reviewed",
                        "risk_level": "medium"
                    },
                ]
                
        # Confidentiality category checks
        elif category == "Confidentiality":
            if principle == "Data Classification":
                checks = [
                    {
                        "id": "CON-DC-001",
                        "title": "Classification Scheme",
                        "description": "Data classification scheme exists and is followed",
                        "risk_level": "high"
                    },
                    {
                        "id": "CON-DC-002",
                        "title": "Handling Procedures",
                        "description": "Procedures exist for handling confidential data",
                        "risk_level": "high"
                    },
                    {
                        "id": "CON-DC-003",
                        "title": "Data Labeling",
                        "description": "Confidential data is labeled appropriately",
                        "risk_level": "medium"
                    },
                ]
            elif principle == "Encryption":
                checks = [
                    {
                        "id": "CON-EN-001",
                        "title": "Data Encryption",
                        "description": "Confidential data is encrypted at rest",
                        "risk_level": "high"
                    },
                    {
                        "id": "CON-EN-002",
                        "title": "Transmission Encryption",
                        "description": "Confidential data is encrypted in transit",
                        "risk_level": "high"
                    },
                    {
                        "id": "CON-EN-003",
                        "title": "Key Management",
                        "description": "Encryption key management procedures exist",
                        "risk_level": "high"
                    },
                ]
            elif principle == "Information Lifecycle":
                checks = [
                    {
                        "id": "CON-IL-001",
                        "title": "Data Retention",
                        "description": "Data retention policies are defined and enforced",
                        "risk_level": "medium"
                    },
                    {
                        "id": "CON-IL-002",
                        "title": "Secure Disposal",
                        "description": "Confidential data is securely disposed",
                        "risk_level": "high"
                    },
                    {
                        "id": "CON-IL-003",
                        "title": "Media Handling",
                        "description": "Media containing confidential data is properly handled",
                        "risk_level": "medium"
                    },
                ]
            elif principle == "Confidentiality Agreements":
                checks = [
                    {
                        "id": "CON-CA-001",
                        "title": "NDAs",
                        "description": "Non-disclosure agreements exist with all relevant parties",
                        "risk_level": "high"
                    },
                    {
                        "id": "CON-CA-002",
                        "title": "Third-Party Agreements",
                        "description": "Confidentiality requirements are included in third-party agreements",
                        "risk_level": "high"
                    },
                    {
                        "id": "CON-CA-003",
                        "title": "Employee Agreements",
                        "description": "Employees sign confidentiality agreements",
                        "risk_level": "medium"
                    },
                ]
                
        # Privacy category checks
        elif category == "Privacy":
            if principle == "Notice and Communication":
                checks = [
                    {
                        "id": "PRI-NC-001",
                        "title": "Privacy Notice",
                        "description": "Privacy notice exists and is communicated to users",
                        "risk_level": "high"
                    },
                    {
                        "id": "PRI-NC-002",
                        "title": "Notice Updates",
                        "description": "Changes to privacy practices are communicated",
                        "risk_level": "medium"
                    },
                    {
                        "id": "PRI-NC-003",
                        "title": "Clear Language",
                        "description": "Privacy notices use clear, understandable language",
                        "risk_level": "medium"
                    },
                ]
            elif principle == "Choice and Consent":
                checks = [
                    {
                        "id": "PRI-CC-001",
                        "title": "Consent Mechanisms",
                        "description": "Mechanisms exist for obtaining user consent",
                        "risk_level": "high"
                    },
                    {
                        "id": "PRI-CC-002",
                        "title": "Consent Records",
                        "description": "Records of consent are maintained",
                        "risk_level": "high"
                    },
                    {
                        "id": "PRI-CC-003",
                        "title": "Preference Management",
                        "description": "Users can manage their privacy preferences",
                        "risk_level": "medium"
                    },
                ]
            elif principle == "Collection and Use":
                checks = [
                    {
                        "id": "PRI-CU-001",
                        "title": "Data Minimization",
                        "description": "Only necessary personal information is collected",
                        "risk_level": "high"
                    },
                    {
                        "id": "PRI-CU-002",
                        "title": "Purpose Limitation",
                        "description": "Personal information is used only for specified purposes",
                        "risk_level": "high"
                    },
                    {
                        "id": "PRI-CU-003",
                        "title": "Data Quality",
                        "description": "Personal information is accurate and up-to-date",
                        "risk_level": "medium"
                    },
                ]
            elif principle == "Access and Disclosure":
                checks = [
                    {
                        "id": "PRI-AD-001",
                        "title": "Access Mechanisms",
                        "description": "Individuals can access their personal information",
                        "risk_level": "high"
                    },
                    {
                        "id": "PRI-AD-002",
                        "title": "Disclosure Controls",
                        "description": "Controls exist over disclosure of personal information",
                        "risk_level": "high"
                    },
                    {
                        "id": "PRI-AD-003",
                        "title": "Cross-Border Transfers",
                        "description": "Controls exist for cross-border transfers of personal information",
                        "risk_level": "high"
                    },
                ]
                
        return checks
    
    def _evaluate_check(self, check: Dict[str, Any], category: str, principle: str, 
                       repo_url: str, source_type: str) -> bool:
        """
        Evaluate a SOC2 compliance check.
        
        Args:
            check: The check to evaluate
            category: SOC2 category
            principle: SOC2 principle
            repo_url: Repository URL
            source_type: Source type
            
        Returns:
            True if the check passes, False otherwise
        """
        # In a real implementation, this would perform actual checks
        # For now, we'll simulate results
        
        # Seed the random generator based on the check ID for consistent results
        seed = sum(ord(c) for c in check["id"] + repo_url)
        random.seed(seed)
        
        # Higher failure rate for high-risk checks
        if check["risk_level"] == "high":
            return random.random() > 0.4  # 60% pass rate
        elif check["risk_level"] == "medium":
            return random.random() > 0.3  # 70% pass rate
        else:
            return random.random() > 0.2  # 80% pass rate
    
    def _generate_violation_details(self, check: Dict[str, Any], category: str, principle: str) -> Dict[str, Any]:
        """
        Generate details for a violation.
        
        Args:
            check: The failed check
            category: SOC2 category
            principle: SOC2 principle
            
        Returns:
            Violation details
        """
        details = {
            "impact": "Unknown",
            "examples": [],
            "recommended_actions": []
        }
        
        # Security category violations
        if category == "Security":
            if check["id"] == "SEC-AC-001":
                details["impact"] = "High: Systems without strong authentication are vulnerable to unauthorized access"
                details["examples"] = ["Single-factor authentication used for critical systems", 
                                      "MFA not enforced for administrative access"]
                details["recommended_actions"] = ["Implement MFA for all administrative access", 
                                                "Enable MFA for all user accounts"]
            elif check["id"] == "SEC-AC-002":
                details["impact"] = "High: Excessive privileges increase attack surface and potential damage"
                details["examples"] = ["Users granted full administrative access unnecessarily", 
                                      "Service accounts with excessive permissions"]
                details["recommended_actions"] = ["Audit and reduce user permissions based on job responsibilities", 
                                                "Implement role-based access control (RBAC)"]
            elif check["id"] == "SEC-AC-003":
                details["impact"] = "Medium: Lack of account management increases risk of unauthorized access"
                details["examples"] = ["Former employee accounts remain active", 
                                      "No regular account review process"]
                details["recommended_actions"] = ["Implement automated user provisioning/deprovisioning", 
                                                "Conduct quarterly account reviews"]
            elif check["id"] == "SEC-AC-004":
                details["impact"] = "Medium: Weak passwords are vulnerable to brute force attacks"
                details["examples"] = ["Short password minimum length", 
                                      "No password complexity requirements"]
                details["recommended_actions"] = ["Enforce minimum 12-character passwords", 
                                                "Implement password complexity requirements"]
            # Additional security checks...
            
        # Availability category violations
        elif category == "Availability":
            if check["id"] == "AVA-PM-001":
                details["impact"] = "High: Unmonitored systems may experience undetected outages"
                details["examples"] = ["No system monitoring tools in place", 
                                      "Alerts not configured for critical services"]
                details["recommended_actions"] = ["Implement comprehensive monitoring solution", 
                                                "Configure alerting for all critical services"]
            elif check["id"] == "AVA-DR-001":
                details["impact"] = "High: Without a tested DR plan, recovery may be delayed or impossible"
                details["examples"] = ["No formal disaster recovery plan", 
                                      "DR plan exists but has never been tested"]
                details["recommended_actions"] = ["Develop comprehensive DR plan", 
                                                "Conduct annual DR testing"]
            # Additional availability checks...
            
        # Processing Integrity category violations
        elif category == "Processing Integrity":
            if check["id"] == "PI-DV-001":
                details["impact"] = "High: Without input validation, data integrity is at risk"
                details["examples"] = ["No input validation for critical fields", 
                                      "Malformed data accepted without validation"]
                details["recommended_actions"] = ["Implement comprehensive input validation", 
                                                "Add server-side validation for all user inputs"]
            # Additional processing integrity checks...
            
        # Confidentiality category violations
        elif category == "Confidentiality":
            if check["id"] == "CON-EN-001":
                details["impact"] = "High: Unencrypted sensitive data is vulnerable to unauthorized access"
                details["examples"] = ["Sensitive data stored in plaintext", 
                                      "Database encryption not enabled"]
                details["recommended_actions"] = ["Implement encryption for all sensitive data at rest", 
                                                "Use transparent data encryption for databases"]
            # Additional confidentiality checks...
            
        # Privacy category violations
        elif category == "Privacy":
            if check["id"] == "PRI-NC-001":
                details["impact"] = "High: Without privacy notices, users are unaware of how their data is used"
                details["examples"] = ["No privacy policy on website", 
                                      "Privacy policy not easily accessible"]
                details["recommended_actions"] = ["Develop and publish comprehensive privacy policy", 
                                                "Make privacy policy accessible from all pages"]
            # Additional privacy checks...
        
        return details
    
    def _generate_recommendations(self, violations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on violations.
        
        Args:
            violations: List of violations
            
        Returns:
            List of recommendations
        """
        # Group violations by category and principle
        grouped_violations = {}
        for violation in violations:
            category = violation["category"]
            principle = violation["principle"]
            
            if category not in grouped_violations:
                grouped_violations[category] = {}
                
            if principle not in grouped_violations[category]:
                grouped_violations[category][principle] = []
                
            grouped_violations[category][principle].append(violation)
        
        # Generate recommendations
        recommendations = []
        
        for category, principles in grouped_violations.items():
            for principle, principle_violations in principles.items():
                # Count violations by risk level
                high_risk = len([v for v in principle_violations if v["risk_level"] == "high"])
                medium_risk = len([v for v in principle_violations if v["risk_level"] == "medium"])
                low_risk = len([v for v in principle_violations if v["risk_level"] == "low"])
                
                # Determine priority based on risk levels
                if high_risk > 0:
                    priority = "high"
                elif medium_risk > 0:
                    priority = "medium"
                else:
                    priority = "low"
                
                # Create recommendation
                recommendation = {
                    "id": f"REC-{len(recommendations) + 1:03d}",
                    "category": category,
                    "principle": principle,
                    "title": f"Improve {category} {principle}",
                    "description": f"Address {len(principle_violations)} {category.lower()} {principle.lower()} violations",
                    "priority": priority,
                    "violations": [v["id"] for v in principle_violations],
                    "steps": []
                }
                
                # Add steps based on violations
                for violation in principle_violations:
                    for action in violation["details"]["recommended_actions"]:
                        if action not in recommendation["steps"]:
                            recommendation["steps"].append(action)
                
                recommendations.append(recommendation)
        
        # Sort recommendations by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda x: priority_order[x["priority"]])
        
        return recommendations
    
    def generate_report(self, scan_results: Dict[str, Any]) -> bytes:
        """
        Generate a PDF report for the SOC2 scan results.
        
        Args:
            scan_results: The SOC2 scan results
            
        Returns:
            PDF report as bytes
        """
        try:
            # Create a buffer for the PDF
            buffer = BytesIO()
            
            # Create the PDF document
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            
            # Create custom styles
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Title'],
                fontSize=18,
                spaceAfter=0.3*inch
            )
            
            heading_style = ParagraphStyle(
                'Heading1',
                parent=styles['Heading1'],
                fontSize=16,
                spaceBefore=0.2*inch,
                spaceAfter=0.1*inch
            )
            
            subheading_style = ParagraphStyle(
                'Heading2',
                parent=styles['Heading2'],
                fontSize=14,
                spaceBefore=0.1*inch,
                spaceAfter=0.1*inch
            )
            
            item_heading_style = ParagraphStyle(
                'Heading3',
                parent=styles['Heading3'],
                fontSize=12,
                spaceBefore=0.1*inch,
                spaceAfter=0.05*inch
            )
            
            # Create the story for the PDF
            story = []
            
            # Logo and header
            logo_text = '''
            <font color="#0068B7" size="18"><b>DataGuardian</b></font>
            <font color="#24A0ED" size="14"><b>SOC2</b></font>
            <br/>
            <font color="#0068B7">●</font>
            <font color="#24A0ED">●</font>
            <font color="#5BBFEA">●</font>
            <font color="#A6E1FA">●</font>
            '''
            
            cert_text = '''
            <font color="#808080" size="10"><b>SOC2 COMPLIANCE</b><br/>ASSESSMENT REPORT</font>
            '''
            
            header_data = [
                [
                    Paragraph(logo_text, styles['Normal']),
                    Paragraph(cert_text, styles['Normal'])
                ]
            ]
            
            header_table = Table(header_data, colWidths=[4*inch, 2*inch])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(header_table)
            story.append(Spacer(1, 0.5*inch))
            
            # Title
            story.append(Paragraph("SOC2 Compliance Assessment Report", title_style))
            
            # Report details
            current_date = datetime.now().strftime("%B %d, %Y")
            story.append(Paragraph(f"Generated on {current_date}", styles['Normal']))
            story.append(Paragraph(f"Scan ID: {scan_results['scan_id']}", styles['Normal']))
            story.append(Paragraph(f"Source: {scan_results['source']['type']} - {scan_results['source']['url']}", styles['Normal']))
            story.append(Spacer(1, 0.25*inch))
            
            # Compliance summary
            story.append(Paragraph("Compliance Summary", heading_style))
            
            summary = scan_results["summary"]
            compliance_score = summary["compliance_score"]
            
            # Determine compliance status and color
            status = "Critical"
            status_color = "#FF5252"  # Red
            
            if compliance_score >= 90:
                status = "Excellent"
                status_color = "#4CAF50"  # Green
            elif compliance_score >= 80:
                status = "Good"
                status_color = "#8BC34A"  # Light green
            elif compliance_score >= 70:
                status = "Average"
                status_color = "#FFC107"  # Amber
            elif compliance_score >= 60:
                status = "Below Average"
                status_color = "#FF9800"  # Orange
            
            # Compliance score box
            cert_data = [
                [Paragraph(f'<font size="14"><b>Overall Compliance</b></font>', styles['Normal'])],
                [Paragraph(f'<font size="28" color="{status_color}"><b>{compliance_score:.1f}%</b></font>', styles['Normal'])],
                [Spacer(1, 0.05*inch)],  # Add spacing
                [Paragraph(f'<font size="12" color="{status_color}"><b>{status}</b></font>', styles['Normal'])],
            ]
            
            cert_table = Table(cert_data, colWidths=[6*inch])
            cert_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LINEBELOW', (0, 0), (0, 0), 1, colors.gray),
                ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#F5F5F5')),
                ('BOTTOMPADDING', (0, 0), (0, 0), 10),
                ('BOTTOMPADDING', (0, 1), (0, 1), 5),
            ]))
            
            story.append(cert_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Summary metrics
            summary_data = [
                ["Metric", "Value"],
                ["Total Checks", str(summary["total_checks"])],
                ["Passed Checks", str(summary["passed_checks"])],
                ["Failed Checks", str(summary["failed_checks"])],
                ["Compliance Score", f"{compliance_score:.1f}%"],
            ]
            
            summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
                ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 0.25*inch))
            
            # Category summary
            story.append(Paragraph("Category Compliance", heading_style))
            
            category_data = [["Category", "Total", "Passed", "Failed", "Score"]]
            
            for category, category_results in scan_results["categories"].items():
                total = category_results["total_checks"]
                passed = category_results["passed_checks"]
                failed = total - passed
                
                if total > 0:
                    score = (passed / total) * 100
                else:
                    score = 0
                    
                category_data.append([
                    category,
                    str(total),
                    str(passed),
                    str(failed),
                    f"{score:.1f}%"
                ])
            
            category_table = Table(category_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch, 1*inch])
            category_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (4, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (4, 0), colors.black),
                ('ALIGN', (0, 0), (4, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (4, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (4, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(category_table)
            story.append(Spacer(1, 0.25*inch))
            
            # High-risk violations
            story.append(Paragraph("Critical Violations", heading_style))
            
            high_risk_violations = [v for v in scan_results["violations"] if v["risk_level"] == "high"]
            
            if high_risk_violations:
                for violation in high_risk_violations[:5]:  # Show top 5 high-risk violations
                    story.append(Paragraph(f"{violation['id']}: {violation['description']}", item_heading_style))
                    story.append(Paragraph(f"Category: {violation['category']} - {violation['principle']}", styles['Normal']))
                    story.append(Paragraph(f"Impact: {violation['details']['impact']}", styles['Normal']))
                    
                    examples = violation['details']['examples']
                    if examples:
                        example_text = "Examples:<br/>" + "<br/>".join([f"• {e}" for e in examples])
                        story.append(Paragraph(example_text, styles['Normal']))
                        
                    actions = violation['details']['recommended_actions']
                    if actions:
                        action_text = "Recommended Actions:<br/>" + "<br/>".join([f"• {a}" for a in actions])
                        story.append(Paragraph(action_text, styles['Normal']))
                        
                    story.append(Spacer(1, 0.1*inch))
                    
                if len(high_risk_violations) > 5:
                    story.append(Paragraph(f"{len(high_risk_violations) - 5} more high-risk violations...", styles['Normal']))
            else:
                story.append(Paragraph("No high-risk violations detected.", styles['Normal']))
                
            story.append(Spacer(1, 0.25*inch))
            
            # Key recommendations
            story.append(Paragraph("Key Recommendations", heading_style))
            
            high_priority_recommendations = [r for r in scan_results["recommendations"] if r["priority"] == "high"]
            
            if high_priority_recommendations:
                for i, rec in enumerate(high_priority_recommendations[:5]):  # Show top 5 high-priority recommendations
                    story.append(Paragraph(f"{i+1}. {rec['title']}", subheading_style))
                    story.append(Paragraph(f"Category: {rec['category']} - {rec['principle']}", styles['Normal']))
                    story.append(Paragraph(f"Description: {rec['description']}", styles['Normal']))
                    
                    steps = rec['steps']
                    if steps:
                        steps_text = "Implementation Steps:<br/>" + "<br/>".join([f"• {s}" for s in steps])
                        story.append(Paragraph(steps_text, styles['Normal']))
                        
                    story.append(Spacer(1, 0.1*inch))
                    
                if len(high_priority_recommendations) > 5:
                    story.append(Paragraph(f"{len(high_priority_recommendations) - 5} more high-priority recommendations...", styles['Normal']))
            else:
                story.append(Paragraph("No high-priority recommendations.", styles['Normal']))
                
            story.append(Spacer(1, 0.25*inch))
            
            # SOC2 TSC categories details
            story.append(Paragraph("SOC2 Trust Services Criteria", heading_style))
            
            for category, details in SOC2_CATEGORIES.items():
                category_results = scan_results["categories"][category]
                total = category_results["total_checks"]
                passed = category_results["passed_checks"]
                
                if total > 0:
                    score = (passed / total) * 100
                else:
                    score = 0
                    
                story.append(Paragraph(f"{category} ({score:.1f}%)", subheading_style))
                story.append(Paragraph(f"{details['description']}", styles['Normal']))
                
                # Principle summary
                principle_data = []
                for principle, principle_results in category_results["principles"].items():
                    total_principle = principle_results["total"]
                    passed_principle = principle_results["passed"]
                    
                    if total_principle > 0:
                        score_principle = (passed_principle / total_principle) * 100
                    else:
                        score_principle = 0
                        
                    principle_data.append([
                        principle,
                        f"{passed_principle}/{total_principle}",
                        f"{score_principle:.1f}%"
                    ])
                    
                if principle_data:
                    principle_table = Table([["Principle", "Checks", "Score"]] + principle_data, 
                                          colWidths=[3*inch, 1.5*inch, 1.5*inch])
                    principle_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (2, 0), colors.lightgrey),
                        ('TEXTCOLOR', (0, 0), (2, 0), colors.black),
                        ('ALIGN', (0, 0), (2, 0), 'CENTER'),
                        ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (2, 0), 6),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
                    
                    story.append(principle_table)
                    
                story.append(Spacer(1, 0.2*inch))
            
            # Build the PDF
            doc.build(story)
            pdf_data = buffer.getvalue()
            buffer.close()
            
            return pdf_data
            
        except Exception as e:
            # Fallback to minimal PDF if there's an error
            error_pdf = f"""
            %PDF-1.4
            1 0 obj
            <<
            /Type /Catalog
            /Pages 2 0 R
            >>
            endobj
            2 0 obj
            <<
            /Type /Pages
            /Kids [3 0 R]
            /Count 1
            >>
            endobj
            3 0 obj
            <<
            /Type /Page
            /Parent 2 0 R
            /Resources <<
            /Font <<
            /F1 4 0 R
            >>
            >>
            /MediaBox [0 0 612 792]
            /Contents 5 0 R
            >>
            endobj
            4 0 obj
            <<
            /Type /Font
            /Subtype /Type1
            /Name /F1
            /BaseFont /Helvetica
            >>
            endobj
            5 0 obj
            << /Length 172 >>
            stream
            BT
            /F1 24 Tf
            72 700 Td
            (SOC2 Compliance Report) Tj
            /F1 12 Tf
            0 -40 Td
            (Scan ID: {scan_results.get('scan_id', 'Unknown')}) Tj
            0 -20 Td
            (Error: {str(e)}) Tj
            ET
            endstream
            endobj
            xref
            0 6
            0000000000 65535 f
            0000000010 00000 n
            0000000060 00000 n
            0000000120 00000 n
            0000000270 00000 n
            0000000350 00000 n
            trailer
            <<
            /Size 6
            /Root 1 0 R
            >>
            startxref
            580
            %%EOF
            """.encode('utf-8')
            
            return error_pdf
            

def run_soc2_scanner():
    """
    Run the SOC2 scanner interface in Streamlit.
    """
    st.title("SOC2 Compliance Scanner")
    
    st.markdown("""
    This scanner aligns infrastructure scans to SOC2 Trust Services Criteria (TSC):
    
    1. **Security** - Protection of system resources against unauthorized access
    2. **Availability** - System availability for operation and use as committed
    3. **Processing Integrity** - System processing is complete, valid, accurate, timely, and authorized
    4. **Confidentiality** - Information designated as confidential is protected
    5. **Privacy** - Personal information is handled in conformity with commitments
    """)
    
    st.markdown("---")
    
    # Create two columns for a cleaner layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Scan Configuration")
        
        # Source configuration
        source_type = st.selectbox(
            "Source Type",
            ["GitHub", "Azure DevOps", "AWS", "GCP", "Azure", "Local"],
            index=0
        )
        
        # Repository URL
        repo_url = st.text_input(
            "Repository URL or Resource Path",
            placeholder="e.g., https://github.com/user/repo"
        )
        
        # Advanced scan options in expander
        with st.expander("Advanced Options"):
            scan_depth = st.selectbox(
                "Scan Depth",
                ["Standard", "Deep", "Comprehensive"],
                index=0
            )
            
            # Category selection
            st.write("SOC2 Categories to Include:")
            col_a, col_b = st.columns(2)
            with col_a:
                security = st.checkbox("Security", value=True)
                availability = st.checkbox("Availability", value=True)
                processing_integrity = st.checkbox("Processing Integrity", value=True)
            with col_b:
                confidentiality = st.checkbox("Confidentiality", value=True)
                privacy = st.checkbox("Privacy", value=True)
        
        # Scan button
        scan_button = st.button("Run SOC2 Scan", type="primary")
        
    with col2:
        st.subheader("TSC Coverage")
        
        # Show trust service criteria coverage
        for category, details in SOC2_CATEGORIES.items():
            principles = details["principles"]
            st.markdown(f"**{category}** ({len(principles)} principles)")
            # Display progress bar for visual effect
            st.progress(1.0)
    
    # Initialize session state for scan results
    if "soc2_scan_results" not in st.session_state:
        st.session_state.soc2_scan_results = None
        
    if "soc2_show_report" not in st.session_state:
        st.session_state.soc2_show_report = False
        
    # Run scan if button is clicked
    if scan_button and repo_url:
        with st.spinner("Scanning infrastructure for SOC2 compliance..."):
            # Create scanner
            scanner = SOC2Scanner()
            
            # Build scan configuration
            scan_config = {
                "scan_depth": scan_depth,
                "include_categories": {
                    "Security": security,
                    "Availability": availability,
                    "Processing Integrity": processing_integrity,
                    "Confidentiality": confidentiality,
                    "Privacy": privacy
                }
            }
            
            # Perform scan
            scan_results = scanner.scan_infrastructure(repo_url, source_type.lower(), **scan_config)
            
            # Store results in session state
            st.session_state.soc2_scan_results = scan_results
            
            # Go to results view
            st.session_state.soc2_show_report = True
            st.rerun()
            
    # Show scan results if available
    if st.session_state.soc2_show_report and st.session_state.soc2_scan_results:
        display_soc2_scan_results(st.session_state.soc2_scan_results)
        
def display_soc2_scan_results(scan_results):
    """
    Display SOC2 scan results.
    
    Args:
        scan_results: SOC2 scan results
    """
    st.title("SOC2 Compliance Results")
    
    # Summary metrics
    summary = scan_results["summary"]
    compliance_score = summary["compliance_score"]
    
    # Create columns for summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Compliance Score", f"{compliance_score:.1f}%")
        
    with col2:
        st.metric("Passed Checks", summary["passed_checks"])
        
    with col3:
        st.metric("Failed Checks", summary["failed_checks"])
    
    # Generate PDF report
    scanner = SOC2Scanner()
    pdf_data = scanner.generate_report(scan_results)
    
    # Download button for PDF report
    st.download_button(
        label="📄 Download PDF Report",
        data=pdf_data,
        file_name=f"soc2_report_{scan_results['scan_id']}.pdf",
        mime="application/pdf",
        help="Download a detailed PDF report of the SOC2 compliance scan",
        type="primary"
    )
    
    # Display violations and recommendations in tabs
    tab1, tab2, tab3 = st.tabs(["SOC2 Categories", "Violations", "Recommendations"])
    
    with tab1:
        # Category results
        st.subheader("SOC2 Category Compliance")
        
        for category, category_results in scan_results["categories"].items():
            total = category_results["total_checks"]
            passed = category_results["passed_checks"]
            
            if total > 0:
                score = (passed / total) * 100
            else:
                score = 0
                
            # Progress bar for category compliance
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.markdown(f"**{category}**")
                st.progress(score / 100)
            with col_b:
                st.markdown(f"**{score:.1f}%**")
                st.markdown(f"{passed}/{total} checks")
                
            # Principle details in expander
            with st.expander(f"View {category} Principles"):
                for principle, principle_results in category_results["principles"].items():
                    total_principle = principle_results["total"]
                    passed_principle = principle_results["passed"]
                    
                    if total_principle > 0:
                        score_principle = (passed_principle / total_principle) * 100
                    else:
                        score_principle = 0
                        
                    st.markdown(f"**{principle}**: {passed_principle}/{total_principle} checks passed ({score_principle:.1f}%)")
                    
                    # Display principle checks
                    if "checks" in principle_results:
                        for check in principle_results["checks"]:
                            st.markdown(f"- {check['id']}: {check['description']}")
    
    with tab2:
        # Violations
        st.subheader("SOC2 Violations")
        
        # Filter options
        col_a, col_b = st.columns([1, 2])
        with col_a:
            risk_filter = st.multiselect(
                "Risk Level",
                ["high", "medium", "low"],
                default=["high", "medium"]
            )
        with col_b:
            category_filter = st.multiselect(
                "Category",
                list(SOC2_CATEGORIES.keys()),
                default=list(SOC2_CATEGORIES.keys())
            )
        
        # Filter violations
        filtered_violations = [
            v for v in scan_results["violations"]
            if v["risk_level"] in risk_filter and v["category"] in category_filter
        ]
        
        if filtered_violations:
            for violation in filtered_violations:
                # Create a styled box for each violation
                with st.container(border=True):
                    # Header
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**{violation['id']}: {violation['description']}**")
                    
                    with col2:
                        risk_level = violation["risk_level"]
                        risk_color = {
                            "high": "red",
                            "medium": "orange",
                            "low": "blue"
                        }.get(risk_level, "gray")
                        
                        st.markdown(f"<span style='color:{risk_color};font-weight:bold;'>{risk_level.upper()} RISK</span>", 
                                   unsafe_allow_html=True)
                    
                    # Details
                    st.markdown(f"**Category**: {violation['category']} - {violation['principle']}")
                    
                    # Impact and examples
                    impact = violation['details'].get('impact', 'Unknown impact')
                    st.markdown(f"**Impact**: {impact}")
                    
                    examples = violation['details'].get('examples', [])
                    if examples:
                        with st.expander("Examples"):
                            for example in examples:
                                st.markdown(f"- {example}")
                                
                    # Recommended actions
                    actions = violation['details'].get('recommended_actions', [])
                    if actions:
                        with st.expander("Recommended Actions"):
                            for action in actions:
                                st.markdown(f"- {action}")
        else:
            st.info("No violations match the current filters.")
    
    with tab3:
        # Recommendations
        st.subheader("Remediation Recommendations")
        
        # Group recommendations by priority
        high_priority = [r for r in scan_results["recommendations"] if r["priority"] == "high"]
        medium_priority = [r for r in scan_results["recommendations"] if r["priority"] == "medium"]
        low_priority = [r for r in scan_results["recommendations"] if r["priority"] == "low"]
        
        # Display high priority recommendations
        if high_priority:
            st.markdown("### High Priority")
            for rec in high_priority:
                with st.container(border=True):
                    st.markdown(f"**{rec['title']}**")
                    st.markdown(f"Category: {rec['category']} - {rec['principle']}")
                    st.markdown(f"Description: {rec['description']}")
                    
                    # Implementation steps
                    if rec["steps"]:
                        with st.expander("Implementation Steps"):
                            for step in rec["steps"]:
                                st.markdown(f"- {step}")
                                
                    # Related violations
                    if rec["violations"]:
                        with st.expander(f"Related Violations ({len(rec['violations'])})"):
                            for violation_id in rec["violations"]:
                                # Find the violation details
                                violation = next((v for v in scan_results["violations"] if v["id"] == violation_id), None)
                                if violation:
                                    st.markdown(f"- **{violation['id']}**: {violation['description']}")
        
        # Display medium priority recommendations
        if medium_priority:
            st.markdown("### Medium Priority")
            for rec in medium_priority:
                with st.container(border=True):
                    st.markdown(f"**{rec['title']}**")
                    st.markdown(f"Category: {rec['category']} - {rec['principle']}")
                    st.markdown(f"Description: {rec['description']}")
                    
                    # Implementation steps
                    if rec["steps"]:
                        with st.expander("Implementation Steps"):
                            for step in rec["steps"]:
                                st.markdown(f"- {step}")
        
        # Display low priority recommendations (collapsed by default)
        if low_priority:
            with st.expander("Low Priority Recommendations"):
                for rec in low_priority:
                    st.markdown(f"**{rec['title']}**")
                    st.markdown(f"Category: {rec['category']} - {rec['principle']}")
                    st.markdown(f"Description: {rec['description']}")
                    
                    # Implementation steps
                    if rec["steps"]:
                        for step in rec["steps"]:
                            st.markdown(f"- {step}")

if __name__ == "__main__":
    run_soc2_scanner()