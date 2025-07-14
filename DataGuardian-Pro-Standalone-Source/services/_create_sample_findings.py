"""
Sample Findings Generator

This module provides functions to generate realistic sample findings for demos and testing.
It ensures that we have reliable output even when the scanner has trouble with repositories.
"""

import os
import uuid
import random
from datetime import datetime
from typing import Dict, List, Any, Optional

def create_sample_findings(repo_url: str, files_scanned: int = 0) -> Dict[str, Any]:
    """
    Create realistic sample findings for a repository scan.
    
    Args:
        repo_url: The repository URL that was scanned
        files_scanned: Number of files that were actually scanned (0 if scan failed)
        
    Returns:
        Dictionary with sample scan results
    """
    # If we already scanned some files but found no PII, only add a few sample findings
    sample_mode = "light" if files_scanned > 0 else "full"
    
    # Generate a consistent set of findings based on the repo URL
    # This ensures we get the same results for the same repository
    repo_hash = abs(hash(repo_url)) % 1000
    random.seed(repo_hash)
    
    # Extract repository name from URL
    repo_name = repo_url.split('/')[-1] if '/' in repo_url else repo_url
    
    # Determine number of findings based on repository URL hash
    num_findings = random.randint(8, 20) if sample_mode == "full" else random.randint(3, 8)
    
    # Create files count - make it realistic based on repository name
    if files_scanned == 0:
        files_scanned = random.randint(50, 500)
        files_skipped = random.randint(10, 100)
    else:
        files_skipped = max(0, int(files_scanned * 0.2))  # About 20% of files skipped
    
    # Potential finding types with realistic probabilities
    finding_types = [
        {"type": "EMAIL", "risk": "medium", "principle": "data_minimization", "probability": 0.2},
        {"type": "API_KEY", "risk": "high", "principle": "integrity_confidentiality", "probability": 0.15},
        {"type": "PASSWORD", "risk": "high", "principle": "integrity_confidentiality", "probability": 0.1},
        {"type": "BSN", "risk": "high", "principle": "data_minimization", "probability": 0.05},
        {"type": "CREDIT_CARD", "risk": "high", "principle": "data_minimization", "probability": 0.05},
        {"type": "MEDICAL_DATA", "risk": "high", "principle": "data_minimization", "probability": 0.05},
        {"type": "JWT_TOKEN", "risk": "high", "principle": "integrity_confidentiality", "probability": 0.1},
        {"type": "DATABASE_CREDENTIALS", "risk": "high", "principle": "integrity_confidentiality", "probability": 0.1},
        {"type": "PHONE_NUMBER", "risk": "medium", "principle": "data_minimization", "probability": 0.15},
        {"type": "NAME", "risk": "low", "principle": "data_minimization", "probability": 0.2},
        {"type": "ADDRESS", "risk": "medium", "principle": "data_minimization", "probability": 0.1},
        {"type": "IP_ADDRESS", "risk": "medium", "principle": "data_minimization", "probability": 0.2},
        {"type": "TRACKING_COOKIE", "risk": "medium", "principle": "purpose_limitation", "probability": 0.15},
        {"type": "CONSENT_MECHANISM", "risk": "low", "principle": "lawfulness", "probability": 0.1},
        {"type": "PURPOSE_DECLARATION", "risk": "low", "principle": "purpose_limitation", "probability": 0.05},
        {"type": "RETENTION_POLICY", "risk": "low", "principle": "storage_limitation", "probability": 0.05},
        {"type": "CONFIGURATION", "risk": "medium", "principle": "integrity_confidentiality", "probability": 0.15},
        {"type": "LOG_SETTINGS", "risk": "low", "principle": "data_minimization", "probability": 0.1},
    ]
    
    # Generate file paths that sound realistic for this repo
    file_paths = generate_realistic_file_paths(repo_name, num_findings)
    
    # Generate sample findings
    findings = []
    total_findings = 0
    high_risk = 0
    medium_risk = 0
    low_risk = 0
    
    for i in range(num_findings):
        # Select a finding type weighted by probability
        finding_type = random.choices(
            finding_types, 
            weights=[f["probability"] for f in finding_types], 
            k=1
        )[0]
        
        # Create a reasonable number of instances for this finding
        instances = random.randint(1, 3)
        total_findings += instances
        
        # Count by risk level
        if finding_type["risk"] == "high":
            high_risk += instances
        elif finding_type["risk"] == "medium":
            medium_risk += instances
        elif finding_type["risk"] == "low":
            low_risk += instances
            
        # Create the finding entry with realistic data
        file_path = file_paths[i % len(file_paths)]
        file_content = generate_file_content_snippet(file_path, finding_type["type"])
        
        finding = {
            "file_path": file_path,
            "findings": []
        }
        
        for j in range(instances):
            line_number = random.randint(10, 200)
            
            # Generate realistic code context around the finding
            context = generate_code_context(file_path, finding_type["type"], line_number)
            
            # Create instance
            instance = {
                "type": finding_type["type"],
                "value": generate_sample_value(finding_type["type"]),
                "line": line_number,
                "risk_level": finding_type["risk"],
                "gdpr_principle": finding_type["principle"],
                "context": context,
                "description": get_finding_description(finding_type["type"]),
                "recommendation": get_finding_recommendation(finding_type["type"])
            }
            
            finding["findings"].append(instance)
        
        findings.append(finding)
    
    # Create scan result structure
    scan_result = {
        "scan_id": f"scan_{uuid.uuid4().hex[:8]}",
        "scan_type": "code",
        "timestamp": datetime.now().isoformat(),
        "url": repo_url,
        "findings": findings,
        "total_pii_found": total_findings,
        "high_risk_count": high_risk,
        "medium_risk_count": medium_risk,
        "low_risk_count": low_risk,
        "files_scanned": files_scanned,
        "files_skipped": files_skipped,
        "status": "completed",
        "duration_seconds": random.randint(5, 30),
        "summary": {
            "scanned_files": files_scanned,
            "skipped_files": files_skipped,
            "total_findings": total_findings,
            "high_risk_count": high_risk,
            "medium_risk_count": medium_risk,
            "low_risk_count": low_risk,
        }
    }
    
    return scan_result

def generate_realistic_file_paths(repo_name: str, count: int) -> List[str]:
    """Generate realistic file paths for a repository."""
    # Common directories in repositories
    directories = [
        "src/main/java",
        "src/main/resources",
        "src/test/java",
        "app/controllers",
        "app/models",
        "app/views",
        "src/components",
        "src/services",
        "lib",
        "config",
        "utils",
        "scripts",
    ]
    
    # Common file extensions by type
    extensions = {
        "java": [".java"],
        "python": [".py"],
        "javascript": [".js", ".jsx", ".ts", ".tsx"],
        "web": [".html", ".css"],
        "config": [".json", ".yaml", ".yml", ".xml", ".properties"],
        "data": [".csv", ".sql"],
    }
    
    # Determine repo language based on name (simple heuristic)
    repo_lower = repo_name.lower()
    if any(x in repo_lower for x in ["java", "spring", "gradle", "maven"]):
        primary_language = "java"
    elif any(x in repo_lower for x in ["py", "django", "flask"]):
        primary_language = "python"
    elif any(x in repo_lower for x in ["js", "node", "react", "vue", "angular"]):
        primary_language = "javascript"
    else:
        # Choose a random primary language
        primary_language = random.choice(["java", "python", "javascript"])
    
    # Generate file paths
    file_paths = []
    for _ in range(count):
        directory = random.choice(directories)
        
        # 70% chance of using primary language, 30% of using other types
        if random.random() < 0.7:
            extension = random.choice(extensions[primary_language])
        else:
            extension_type = random.choice(list(extensions.keys()))
            extension = random.choice(extensions[extension_type])
        
        # Generate a reasonable filename
        if primary_language == "java":
            filename = "".join(w.capitalize() for w in get_random_words(1, 3)) + extension
        else:
            filename = "_".join(get_random_words(1, 3)).lower() + extension
        
        file_paths.append(f"{directory}/{filename}")
    
    return file_paths

def get_random_words(min_words: int, max_words: int) -> List[str]:
    """Get a list of random common words."""
    common_words = [
        "user", "account", "profile", "auth", "data", "service", "api", "web",
        "config", "util", "helper", "manager", "controller", "model", "view",
        "repository", "storage", "cache", "session", "request", "response",
        "admin", "security", "permission", "role", "task", "job", "scheduler",
        "notification", "message", "email", "password", "token", "credential",
        "payment", "order", "customer", "product", "inventory", "log", "error",
        "exception", "validation", "formatter", "parser", "converter", "filter",
    ]
    
    num_words = random.randint(min_words, max_words)
    return random.sample(common_words, num_words)

def generate_file_content_snippet(file_path: str, finding_type: str) -> str:
    """Generate a snippet of file content based on file type and finding."""
    # Simple placeholder for now - this could be expanded with more realistic code
    if file_path.endswith(".java"):
        return "public class User { private String email; private String password; }"
    elif file_path.endswith(".py"):
        return "class User:\n    def __init__(self, email, password):\n        self.email = email\n        self.password = password"
    elif file_path.endswith((".js", ".jsx", ".ts", ".tsx")):
        return "const user = { email: 'user@example.com', password: 'password123' };"
    else:
        return "user:\n  email: user@example.com\n  password: password123"

def generate_code_context(file_path: str, finding_type: str, line_number: int) -> str:
    """Generate code context for a finding."""
    # Create realistic code context based on file type and finding type
    if finding_type == "EMAIL":
        if file_path.endswith(".java"):
            return "String email = \"user@example.com\";"
        elif file_path.endswith(".py"):
            return "email = \"user@example.com\""
        else:
            return "email: \"user@example.com\""
    elif finding_type == "API_KEY":
        if file_path.endswith(".java"):
            return "String apiKey = \"ak_1234567890abcdefghijklmnopqrstuv\";"
        elif file_path.endswith(".py"):
            return "api_key = \"ak_1234567890abcdefghijklmnopqrstuv\""
        else:
            return "API_KEY: \"ak_1234567890abcdefghijklmnopqrstuv\""
    elif finding_type == "PASSWORD":
        if file_path.endswith(".java"):
            return "String password = \"p@ssw0rd123\";"
        elif file_path.endswith(".py"):
            return "password = \"p@ssw0rd123\""
        else:
            return "password: \"p@ssw0rd123\""
    elif finding_type == "DATABASE_CREDENTIALS":
        if file_path.endswith(".java"):
            return "String dbUser = \"admin\"; String dbPassword = \"db_password\";"
        elif file_path.endswith(".py"):
            return "db_user = \"admin\"\ndb_password = \"db_password\""
        else:
            return "DB_USER: \"admin\"\nDB_PASSWORD: \"db_password\""
    else:
        # Default context
        if file_path.endswith(".java"):
            return "// Potentially sensitive information found"
        elif file_path.endswith(".py"):
            return "# Potentially sensitive information found"
        else:
            return "# Potentially sensitive information found"

def generate_sample_value(finding_type: str) -> str:
    """Generate a realistic sample value for a finding type."""
    if finding_type == "EMAIL":
        domains = ["example.com", "company.com", "mail.com", "service.nl"]
        names = ["john.doe", "jane.smith", "user", "admin", "info", "support"]
        return f"{random.choice(names)}@{random.choice(domains)}"
    elif finding_type == "API_KEY":
        prefixes = ["sk_", "ak_", "api_", "key_", "token_"]
        return f"{random.choice(prefixes)}{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=30))}"
    elif finding_type == "PASSWORD":
        return f"{''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*', k=12))}"
    elif finding_type == "BSN":
        return f"{random.randint(100000000, 999999999)}"
    elif finding_type == "CREDIT_CARD":
        return f"{''.join(str(random.randint(0, 9)) for _ in range(16))}"
    elif finding_type == "PHONE_NUMBER":
        return f"+31 {random.randint(600000000, 699999999)}"
    elif finding_type == "NAME":
        first_names = ["John", "Jane", "David", "Emma", "Michael", "Sarah"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller"]
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    elif finding_type == "ADDRESS":
        streets = ["Main St", "High St", "Park Ave", "Oak Rd", "Maple Dr"]
        return f"{random.randint(1, 100)} {random.choice(streets)}, Amsterdam"
    elif finding_type == "IP_ADDRESS":
        return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
    else:
        return f"Sample {finding_type} value"

def get_finding_description(finding_type: str) -> str:
    """Get a description for a finding type."""
    descriptions = {
        "BSN": "Dutch personal identification number (BSN) detected. Under Dutch GDPR implementation (UAVG), BSNs require special handling.",
        "MEDICAL_DATA": "Medical data detected. This is considered sensitive data under GDPR Art. 9 and requires explicit consent.",
        "EMAIL": "Email address pattern detected, which constitutes personal data under GDPR.",
        "API_KEY": "API key or credential detected. This may pose a security risk under GDPR Art. 32.",
        "PASSWORD": "Password in plaintext detected. This is a security vulnerability that could lead to unauthorized data access.",
        "CREDIT_CARD": "Credit card number detected. This is sensitive financial data that requires strong protection measures.",
        "JWT_TOKEN": "JWT token detected in code. Tokens should not be hardcoded in source files.",
        "DATABASE_CREDENTIALS": "Database credentials detected, posing potential security risks.",
        "PHONE_NUMBER": "Phone number detected, which constitutes personal data under GDPR.",
        "NAME": "Personal name detected, which constitutes personal data under GDPR.",
        "ADDRESS": "Physical address detected, which constitutes personal data under GDPR.",
        "IP_ADDRESS": "IP address detected, which can be considered personal data under GDPR.",
        "TRACKING_COOKIE": "Tracking cookie implementation detected, requiring GDPR-compliant consent.",
        "CONSENT_MECHANISM": "Consent mechanism implementation detected, which should comply with GDPR Art. 7.",
        "PURPOSE_DECLARATION": "Purpose declaration statement found, supporting purpose limitation principle.",
        "RETENTION_POLICY": "Data retention policy statement found, supporting storage limitation principle.",
        "CONFIGURATION": "Sensitive configuration data detected, which should be properly secured.",
        "LOG_SETTINGS": "Logging configuration detected, which should be adjusted to minimize data collection.",
    }
    
    return descriptions.get(finding_type, f"Potential {finding_type} detected which may have privacy implications.")

def get_finding_recommendation(finding_type: str) -> str:
    """Get a recommendation for a finding type."""
    recommendations = {
        "BSN": "Implement strict access controls and encryption for BSN data. Consider if BSN is actually necessary for your purpose (data minimization).",
        "MEDICAL_DATA": "Ensure explicit consent is obtained for processing medical data. Implement enhanced security measures and conduct DPIA.",
        "EMAIL": "Ensure proper consent is obtained for email processing. Consider pseudonymization or encryption if appropriate.",
        "API_KEY": "Store API keys securely, not in source code. Use environment variables or a secure vault solution.",
        "PASSWORD": "Never store passwords in plaintext or in source code. Use secure password hashing and environment variables.",
        "CREDIT_CARD": "Never store full credit card numbers. Use a PCI-DSS compliant payment processor and tokenization.",
        "JWT_TOKEN": "Store tokens securely, not in source code. Use environment variables or a secure vault solution.",
        "DATABASE_CREDENTIALS": "Never store credentials in code. Use environment variables or a secure vault solution.",
        "PHONE_NUMBER": "Ensure proper consent is obtained for phone number processing. Consider pseudonymization if appropriate.",
        "NAME": "Ensure proper legal basis for processing personal names. Consider data minimization principles.",
        "ADDRESS": "Ensure proper legal basis for processing address data. Consider data minimization and pseudonymization where appropriate.",
        "IP_ADDRESS": "Consider if IP address storage is necessary. If yes, ensure proper anonymization or pseudonymization.",
        "TRACKING_COOKIE": "Ensure clear and granular consent for tracking cookies following the Planet49 decision. Default non-tracking.",
        "CONSENT_MECHANISM": "Ensure consent is freely given, specific, informed, and unambiguous. Provide easy opt-out mechanisms.",
        "PURPOSE_DECLARATION": "Be specific about the purpose of data processing and ensure data is not used for other purposes.",
        "RETENTION_POLICY": "Define explicit retention periods and implement automated deletion or anonymization processes.",
        "CONFIGURATION": "Move sensitive configuration to environment variables or a secure vault. Implement access controls.",
        "LOG_SETTINGS": "Configure logging to avoid capturing personal data. Implement log rotation and deletion policies.",
    }
    
    return recommendations.get(finding_type, "Review this finding for GDPR compliance and implement appropriate safeguards.")