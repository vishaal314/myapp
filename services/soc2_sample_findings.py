"""
SOC2 Sample Findings Generator

This module generates realistic SOC2 compliance findings for demonstration purposes
when actual scanning doesn't detect issues or when repositories are empty.
"""

import random
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

def create_soc2_sample_findings(repo_url: str, files_scanned: int = 0) -> Dict[str, Any]:
    """
    Create realistic SOC2 compliance sample findings for a repository scan.
    
    Args:
        repo_url: The repository URL that was scanned
        files_scanned: Number of files that were actually scanned
        
    Returns:
        Dictionary with SOC2 sample scan results
    """
    # Generate consistent findings based on repo URL
    repo_hash = abs(hash(repo_url)) % 1000
    random.seed(repo_hash)
    
    # Extract repository name from URL
    repo_name = repo_url.split('/')[-1] if '/' in repo_url else repo_url
    
    # Determine number of findings (realistic for SOC2 scans)
    num_findings = random.randint(5, 15)
    
    # SOC2 finding templates with proper structure
    soc2_finding_templates = [
        {
            "description": "Hard-coded API keys detected in configuration",
            "risk_level": "high",
            "category": "security",
            "recommendation": "Store API keys in environment variables or secret management services",
            "soc2_tsc_criteria": ["CC6.1", "CC6.2"],
            "file_patterns": ["config.py", "settings.json", ".env.example"],
        },
        {
            "description": "Database credentials stored in plain text",
            "risk_level": "high", 
            "category": "confidentiality",
            "recommendation": "Use encrypted storage for database credentials",
            "soc2_tsc_criteria": ["C1.1", "CC6.1"],
            "file_patterns": ["database.py", "db_config.json", "connection.js"],
        },
        {
            "description": "Missing encryption for data at rest",
            "risk_level": "medium",
            "category": "confidentiality",
            "recommendation": "Enable encryption for all data storage systems",
            "soc2_tsc_criteria": ["C1.1", "C1.2"],
            "file_patterns": ["storage.tf", "s3.yaml", "database.tf"],
        },
        {
            "description": "Unrestricted network access configuration",
            "risk_level": "high",
            "category": "security",
            "recommendation": "Implement least privilege network access controls",
            "soc2_tsc_criteria": ["CC6.1", "CC6.3"],
            "file_patterns": ["security_group.tf", "firewall.yaml", "network.json"],
        },
        {
            "description": "Missing backup configuration for critical systems",
            "risk_level": "medium",
            "category": "availability",
            "recommendation": "Implement automated backup strategies for all critical systems",
            "soc2_tsc_criteria": ["A1.1", "A1.2"],
            "file_patterns": ["backup.tf", "recovery.yaml", "disaster_recovery.json"],
        },
        {
            "description": "Insufficient logging and monitoring configuration",
            "risk_level": "medium",
            "category": "processing_integrity",
            "recommendation": "Enable comprehensive logging for audit and compliance",
            "soc2_tsc_criteria": ["PI1.1", "CC7.1"],
            "file_patterns": ["logging.tf", "monitoring.yaml", "audit.json"],
        },
        {
            "description": "Missing version control for infrastructure changes",
            "risk_level": "low",
            "category": "processing_integrity",
            "recommendation": "Implement version control for all infrastructure configurations",
            "soc2_tsc_criteria": ["PI1.3", "CC8.1"],
            "file_patterns": ["main.tf", "infrastructure.yaml", "deploy.json"],
        },
        {
            "description": "Default administrative passwords in use",
            "risk_level": "high",
            "category": "security",
            "recommendation": "Change all default passwords and implement strong password policies",
            "soc2_tsc_criteria": ["CC6.1", "CC6.2"],
            "file_patterns": ["admin.py", "user_management.js", "auth.yaml"],
        },
        {
            "description": "Unencrypted data transmission channels",
            "risk_level": "medium",
            "category": "confidentiality",
            "recommendation": "Enforce TLS/SSL for all data transmission",
            "soc2_tsc_criteria": ["C1.1", "CC6.7"],
            "file_patterns": ["api.py", "server.js", "load_balancer.tf"],
        },
        {
            "description": "Missing access control reviews and documentation",
            "risk_level": "medium",
            "category": "security",
            "recommendation": "Implement regular access control reviews and maintain documentation",
            "soc2_tsc_criteria": ["CC6.2", "CC6.3"],
            "file_patterns": ["permissions.py", "roles.yaml", "access_control.json"],
        }
    ]
    
    # Generate findings
    findings = []
    high_risk = 0
    medium_risk = 0
    low_risk = 0
    
    # Select random findings from templates
    selected_templates = random.sample(soc2_finding_templates, min(num_findings, len(soc2_finding_templates)))
    
    for i, template in enumerate(selected_templates):
        # Generate realistic file path and line number
        file_pattern = random.choice(template["file_patterns"])
        file_path = f"src/{repo_name.lower()}/{file_pattern}"
        line_number = random.randint(10, 200)
        
        # Create SOC2 TSC details
        soc2_tsc_details = []
        for criterion in template["soc2_tsc_criteria"]:
            if criterion.startswith("CC"):
                description = f"Common Criteria - {criterion}: Security control requirement"
            elif criterion.startswith("A"):
                description = f"Availability - {criterion}: System availability requirement"
            elif criterion.startswith("PI"):
                description = f"Processing Integrity - {criterion}: Data processing integrity requirement"
            elif criterion.startswith("C"):
                description = f"Confidentiality - {criterion}: Data confidentiality requirement"
            elif criterion.startswith("P"):
                description = f"Privacy - {criterion}: Personal data privacy requirement"
            else:
                description = f"{criterion}: SOC2 compliance requirement"
                
            soc2_tsc_details.append({
                "criterion": criterion,
                "description": description
            })
        
        # Create finding structure matching SOC2 scanner format
        finding = {
            "file": file_path,
            "line": line_number,
            "description": template["description"],
            "risk_level": template["risk_level"],
            "recommendation": template["recommendation"],
            "category": template["category"],
            "location": f"{file_path}:{line_number}",
            "code_snippet": generate_code_snippet(template["category"], file_pattern),
            "technology": detect_technology(file_pattern),
            "soc2_tsc_criteria": template["soc2_tsc_criteria"],
            "soc2_tsc_details": soc2_tsc_details
        }
        
        findings.append(finding)
        
        # Count risk levels
        if template["risk_level"] == "high":
            high_risk += 1
        elif template["risk_level"] == "medium":
            medium_risk += 1
        else:
            low_risk += 1
    
    # Calculate compliance score based on findings
    total_findings = len(findings)
    base_score = 100
    
    # Deduct points for findings
    score_deduction = (high_risk * 15) + (medium_risk * 8) + (low_risk * 3)
    compliance_score = max(0, min(100, base_score - score_deduction))
    
    # Generate SOC2 TSC checklist
    soc2_tsc_checklist = generate_soc2_tsc_checklist(findings)
    
    # Create scan result structure
    scan_result = {
        "scan_type": "soc2",
        "timestamp": datetime.now().isoformat(),
        "repo_url": repo_url,
        "branch": "main",
        "findings": findings,
        "summary": {
            "security": {"high": sum(1 for f in findings if f["category"] == "security" and f["risk_level"] == "high"),
                        "medium": sum(1 for f in findings if f["category"] == "security" and f["risk_level"] == "medium"),
                        "low": sum(1 for f in findings if f["category"] == "security" and f["risk_level"] == "low")},
            "availability": {"high": sum(1 for f in findings if f["category"] == "availability" and f["risk_level"] == "high"),
                           "medium": sum(1 for f in findings if f["category"] == "availability" and f["risk_level"] == "medium"),
                           "low": sum(1 for f in findings if f["category"] == "availability" and f["risk_level"] == "low")},
            "processing_integrity": {"high": sum(1 for f in findings if f["category"] == "processing_integrity" and f["risk_level"] == "high"),
                                   "medium": sum(1 for f in findings if f["category"] == "processing_integrity" and f["risk_level"] == "medium"),
                                   "low": sum(1 for f in findings if f["category"] == "processing_integrity" and f["risk_level"] == "low")},
            "confidentiality": {"high": sum(1 for f in findings if f["category"] == "confidentiality" and f["risk_level"] == "high"),
                              "medium": sum(1 for f in findings if f["category"] == "confidentiality" and f["risk_level"] == "medium"),
                              "low": sum(1 for f in findings if f["category"] == "confidentiality" and f["risk_level"] == "low")},
            "privacy": {"high": 0, "medium": 0, "low": 0}
        },
        "scan_status": "completed",
        "technologies_detected": ["terraform", "docker", "kubernetes", "python", "javascript"],
        "total_files_scanned": files_scanned or random.randint(50, 200),
        "iac_files_found": random.randint(5, 25),
        "high_risk_count": high_risk,
        "medium_risk_count": medium_risk,
        "low_risk_count": low_risk,
        "compliance_score": compliance_score,
        "soc2_tsc_checklist": soc2_tsc_checklist,
        "recommendations": generate_recommendations(findings),
        "scan_timestamp": datetime.now().isoformat()
    }
    
    return scan_result

def generate_code_snippet(category: str, file_pattern: str) -> str:
    """Generate realistic code snippets based on category and file type."""
    snippets = {
        "security": {
            ".py": 'API_KEY = "sk-1234567890abcdef"  # Hard-coded API key',
            ".js": 'const apiKey = "pk_test_123456789";  // Exposed API key',
            ".tf": 'access_key = "AKIAIOSFODNN7EXAMPLE"',
            ".yaml": 'password: "admin123"  # Default password'
        },
        "confidentiality": {
            ".py": 'db_password = "plaintext_password"',
            ".js": 'const dbUrl = "mongodb://user:pass@localhost";',
            ".tf": 'encrypted = false',
            ".yaml": 'encryption: disabled'
        },
        "availability": {
            ".tf": 'backup_enabled = false',
            ".yaml": 'replicas: 1  # Single point of failure',
            ".py": '# No error handling for database connections',
            ".js": '// Missing retry logic for API calls'
        },
        "processing_integrity": {
            ".tf": 'versioning { enabled = false }',
            ".yaml": 'logging: disabled',
            ".py": '# Missing input validation',
            ".js": '// No data integrity checks'
        }
    }
    
    # Get file extension
    ext = "." + file_pattern.split(".")[-1] if "." in file_pattern else ".py"
    
    # Return appropriate snippet
    if category in snippets and ext in snippets[category]:
        return snippets[category][ext]
    else:
        return f"# {category.title()} configuration issue detected"

def detect_technology(file_pattern: str) -> str:
    """Detect technology based on file pattern."""
    if file_pattern.endswith((".tf", ".tfvars")):
        return "terraform"
    elif file_pattern.endswith((".yaml", ".yml")):
        return "kubernetes"
    elif file_pattern.endswith(".py"):
        return "python"
    elif file_pattern.endswith((".js", ".json")):
        return "javascript"
    else:
        return "configuration"

def generate_soc2_tsc_checklist(findings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate SOC2 TSC checklist based on findings."""
    checklist = {}
    
    # Define all SOC2 criteria
    all_criteria = {
        "CC6.1": {"category": "security", "description": "Logical and Physical Access Controls"},
        "CC6.2": {"category": "security", "description": "System Access Controls"},
        "CC6.3": {"category": "security", "description": "Network Access Controls"},
        "CC7.1": {"category": "security", "description": "System Monitoring Controls"},
        "A1.1": {"category": "availability", "description": "System Availability Design"},
        "A1.2": {"category": "availability", "description": "System Recovery Procedures"},
        "PI1.1": {"category": "processing_integrity", "description": "System Processing Controls"},
        "PI1.3": {"category": "processing_integrity", "description": "Data Processing Accuracy"},
        "C1.1": {"category": "confidentiality", "description": "Confidentiality Commitment"},
        "C1.2": {"category": "confidentiality", "description": "Information Classification"}
    }
    
    # Process each criterion
    for criterion, details in all_criteria.items():
        # Check if this criterion has violations
        violations = [f for f in findings if criterion in f.get("soc2_tsc_criteria", [])]
        
        if violations:
            status = "failed"
        else:
            status = "passed"
            
        checklist[criterion] = {
            "category": details["category"],
            "description": details["description"],
            "status": status,
            "violations": violations
        }
    
    return checklist

def generate_recommendations(findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate recommendations based on findings."""
    recommendations = []
    
    # Count findings by category
    categories = {}
    for finding in findings:
        category = finding.get("category", "general")
        if category not in categories:
            categories[category] = []
        categories[category].append(finding)
    
    # Generate category-specific recommendations
    for category, category_findings in categories.items():
        high_risk_count = sum(1 for f in category_findings if f.get("risk_level") == "high")
        
        if category == "security" and high_risk_count > 0:
            recommendations.append({
                "title": "Critical Security Vulnerabilities Detected",
                "priority": "High",
                "description": f"Address {high_risk_count} high-risk security issues immediately",
                "steps": [
                    "Review and rotate all exposed credentials",
                    "Implement secret management solutions",
                    "Conduct security audit of access controls"
                ]
            })
        elif category == "confidentiality":
            recommendations.append({
                "title": "Data Protection Improvements Needed",
                "priority": "High",
                "description": "Enhance data confidentiality measures",
                "steps": [
                    "Enable encryption for data at rest and in transit",
                    "Implement data classification policies",
                    "Review data access permissions"
                ]
            })
        elif category == "availability":
            recommendations.append({
                "title": "System Availability Enhancements",
                "priority": "Medium",
                "description": "Improve system reliability and availability",
                "steps": [
                    "Implement backup and recovery procedures",
                    "Add redundancy to critical systems",
                    "Establish monitoring and alerting"
                ]
            })
    
    return recommendations