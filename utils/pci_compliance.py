"""
PCI Compliance Utilities

This module provides utilities for mapping findings to PCI DSS requirements
and working with PCI DSS compliance information.
"""

from typing import Dict, List, Any, Optional

# PCI DSS requirement descriptions (simplified)
PCI_REQUIREMENTS = {
    "1.2.1": "Network security controls limit inbound and outbound traffic to only necessary traffic",
    "1.2.7": "Security controls are defined for systems that provide/support network security services",
    "1.3.1": "Implement a DMZ to separate untrusted networks from systems with cardholder data",
    "1.3.2": "Restrict inbound internet traffic to IP addresses within the DMZ",
    "1.3.4": "Implement anti-spoofing measures to detect and block forged source IP addresses",
    "1.4.1": "Use firewalls on all end-user devices that connect to both the internet and the CDE",
    "2.2.1": "Implement only one primary function per server to prevent functions requiring different security levels from co-existing",
    "2.2.4": "Configure system security parameters to prevent misuse",
    "2.2.5": "Remove unnecessary functionality from systems in the CDE",
    "3.3.3": "Protect stored credentials using strong cryptography",
    "3.4": "Render PAN unreadable anywhere it is stored",
    "3.5": "Document and implement procedures to protect keys used to secure cardholder data",
    "3.6.1": "Fully document key management procedures and implement strong key generation",
    "3.6.3": "Store secret and private keys in a secure form with restricted access",
    "4.1": "Use strong cryptography and security protocols to safeguard sensitive data during transmission",
    "4.2": "Never send unprotected PANs by end-user messaging technologies",
    "6.3.2": "Secure coding techniques are defined, implemented, and verified",
    "6.3.3": "Software security vulnerabilities are identified and addressed",
    "6.3.4": "Apply software patches and security updates in a timely manner",
    "6.5": "Address common coding vulnerabilities in software development",
    "6.5.1": "Injection flaws, particularly SQL injection",
    "6.5.2": "Improper authentication",
    "6.5.3": "Improper session management",
    "6.5.4": "Cross-site scripting (XSS)",
    "6.5.5": "Improper access control",
    "6.5.7": "Cross-site request forgery (CSRF)",
    "6.5.8": "Insecure deserialization",
    "6.5.9": "Proper error handling",
    "6.5.10": "Broken authentication and session management",
    "6.6": "For public-facing web applications, address new threats and vulnerabilities",
    "7.1.1": "Define access needs and privilege assignments for each role",
    "7.1.2": "Restrict access to privileged user IDs to least privileges necessary",
    "7.1.3": "Assign access based on individual personnel's job classification",
    "8.2.3": "Passwords/phrases must meet complexity and strength requirements",
    "8.3.1": "Implement multi-factor authentication for all non-console access to the CDE",
    "10.1": "Implement audit trails to link access to system components to individual users",
    "10.2": "Implement automated audit trails for all system components"
}

# Mapping of vulnerability types to PCI DSS requirements
VULNERABILITY_TO_PCI_MAP = {
    # SAST vulnerabilities
    "SQL Injection": ["6.3.2", "6.5.1"],
    "Command Injection": ["6.3.2", "6.5"],
    "Cross-Site Scripting": ["6.3.2", "6.5.4"],
    "Cross-Site Request Forgery": ["6.3.2", "6.5.7"],
    "Server-Side Request Forgery": ["6.3.2", "6.5.5"],
    "XML External Entity": ["6.3.2", "6.5"],
    "Path Traversal": ["6.3.2", "6.5.5"],
    "Insecure Deserialization": ["6.3.2", "6.5.8"],
    "Weak Cryptography": ["3.6.1", "4.1"],
    "Insecure Hashing Algorithm": ["3.6.1", "4.1"],
    "Insecure Randomness": ["3.6.1"],
    "Improper Error Handling": ["6.5.9"],
    "Injection": ["6.3.2", "6.5.1"],
    "Authentication Issue": ["6.5.2", "8.2.3"],
    "Authorization Issue": ["7.1.1", "7.1.2"],
    "Session Management": ["6.5.3"],
    "Access Control": ["6.5.5", "7.1.3"],
    
    # SCA vulnerabilities
    "Vulnerable Dependency": ["6.3.3", "6.3.4"],
    "Outdated Component": ["6.3.4"],
    "Known Vulnerability": ["6.3.3"],
    "Licensing Issue": ["6.3.3"],
    
    # Secrets Detection
    "Hardcoded Secret": ["3.3.3", "6.3.2"],
    "API Key": ["3.3.3", "6.3.2"],
    "Password": ["3.3.3", "8.2.3"],
    "Credential": ["3.3.3"],
    "High Entropy String": ["3.3.3"],
    "Private Key": ["3.6.3"],
    
    # IaC vulnerabilities
    "Unencrypted Storage": ["3.4", "4.1"],
    "Public Access": ["1.2.1", "1.3.1"],
    "Overly Permissive Security Group": ["1.2.1", "1.3.4"],
    "Insecure Network Configuration": ["1.2.7", "1.3.2"],
    "Weak TLS Configuration": ["4.1"],
    "Plaintext Secrets": ["3.3.3", "3.6.1"],
    "Logging Disabled": ["10.1", "10.2"],
    "Insecure CORS Configuration": ["6.5.9"],
    "Privileged Container": ["2.2.4", "2.2.5"],
    "Host Network Access": ["1.2.1", "2.2.1"],
    "Container Running as Root": ["7.1.2"],
    "Insecure Container Capabilities": ["2.2.4", "7.1.1"],
    "Secret as Environment Variable": ["3.3.3", "3.6.1"],
    "Insecure Workload Configuration": ["6.5", "6.6"]
}

def map_finding_to_pci_requirement(finding_type: str) -> str:
    """
    Map a finding type to the relevant PCI DSS requirements.
    
    Args:
        finding_type: The type of finding
        
    Returns:
        Comma-separated list of PCI DSS requirements
    """
    # Normalize finding type
    finding_type_lower = finding_type.lower()
    
    # Check for exact matches
    for vuln_type, requirements in VULNERABILITY_TO_PCI_MAP.items():
        if vuln_type.lower() in finding_type_lower:
            return ", ".join(requirements)
            
    # Some specific matching for common pattern categories
    if "sql" in finding_type_lower and "inject" in finding_type_lower:
        return "6.3.2, 6.5.1"
    elif "xss" in finding_type_lower:
        return "6.3.2, 6.5.4"
    elif "csrf" in finding_type_lower:
        return "6.3.2, 6.5.7"
    elif "inject" in finding_type_lower:
        return "6.3.2, 6.5.1"
    elif "auth" in finding_type_lower:
        return "6.5.2, 8.2.3"
    elif "session" in finding_type_lower:
        return "6.5.3"
    elif "access" in finding_type_lower or "permission" in finding_type_lower:
        return "6.5.5, 7.1.3"
    elif "crypt" in finding_type_lower or "encrypt" in finding_type_lower:
        return "3.6.1, 4.1"
    elif "hash" in finding_type_lower:
        return "3.6.1, 4.1" 
    elif "secret" in finding_type_lower or "password" in finding_type_lower or "key" in finding_type_lower:
        return "3.3.3, 3.6.3"
    elif "network" in finding_type_lower or "firewall" in finding_type_lower:
        return "1.2.1, 1.3.1"
    elif "log" in finding_type_lower or "audit" in finding_type_lower:
        return "10.1, 10.2"
    elif "vuln" in finding_type_lower:
        return "6.3.3, 6.3.4"
    elif "dependency" in finding_type_lower or "component" in finding_type_lower or "library" in finding_type_lower:
        return "6.3.3, 6.3.4"
    
    # Default to secure coding if no match
    return "6.3.2, 6.3.3"

def get_pci_requirement_description(requirement: str) -> str:
    """
    Get the description of a PCI DSS requirement.
    
    Args:
        requirement: The PCI DSS requirement identifier
        
    Returns:
        Description of the requirement
    """
    return PCI_REQUIREMENTS.get(requirement, "PCI DSS requirement")

def generate_remediation_for_requirement(requirement: str, finding_type: str) -> str:
    """
    Generate remediation guidance based on the PCI DSS requirement.
    
    Args:
        requirement: The PCI DSS requirement identifier
        finding_type: The type of finding
        
    Returns:
        Remediation guidance
    """
    remediation_map = {
        "1.2.1": "Restrict inbound and outbound traffic to only that which is necessary for the cardholder data environment. Use network segmentation and implement 'deny all' by default.",
        "1.2.7": "Review and strengthen security controls for systems providing network security services.",
        "1.3.1": "Implement a DMZ to separate untrusted networks from systems with cardholder data.",
        "1.3.2": "Restrict inbound Internet traffic to only necessary IP addresses within the DMZ.",
        "1.3.4": "Implement anti-spoofing measures to detect and block forged source IP addresses.",
        "1.4.1": "Implement personal firewall software on end-user devices that connect to the Internet and the cardholder data environment.",
        "2.2.1": "Implement one primary function per server to prevent mixing functions with different security requirements.",
        "2.2.4": "Configure system security parameters securely to prevent misuse.",
        "2.2.5": "Remove all unnecessary functionality, such as scripts, drivers, features, subsystems, file systems, and unnecessary web servers.",
        "3.3.3": "Store passwords and other credentials securely using strong cryptography. Move credentials to a secure vault or environment variables instead of hardcoding.",
        "3.4": "Render PAN unreadable by using strong cryptography with associated key management processes and procedures.",
        "3.5": "Document and implement procedures to protect cryptographic keys used for encryption of cardholder data.",
        "3.6.1": "Implement strong key generation processes that provide appropriate entropy and key strength.",
        "3.6.3": "Store cryptographic keys in as few locations as possible, in a secure form with restricted access.",
        "4.1": "Use strong cryptography and security protocols (such as TLS 1.2+, SFTP, etc.) to safeguard sensitive data during transmission.",
        "4.2": "Never send unprotected PANs by end-user messaging technologies like email, instant messaging, or chat.",
        "6.3.2": "Implement secure coding techniques aligned with industry standards. Review code for common vulnerabilities and ensure proper input validation.",
        "6.3.3": "Identify and address security vulnerabilities using automated tools and manual code reviews.",
        "6.3.4": "Apply security patches and updates in a timely manner.",
        "6.5": "Address common coding vulnerabilities in software development to prevent exploitation of code.",
        "6.5.1": "Implement proper input validation and parameterized queries to prevent SQL injection.",
        "6.5.2": "Implement strong authentication mechanisms for all system access.",
        "6.5.3": "Implement secure session management with proper timeout, encryption, and rotation.",
        "6.5.4": "Implement proper output encoding and validate user input to prevent cross-site scripting (XSS).",
        "6.5.5": "Implement proper access controls that validate user permissions for all protected resources.",
        "6.5.7": "Implement anti-CSRF tokens and proper verification to prevent cross-site request forgery (CSRF).",
        "6.5.8": "Implement validation and integrity checks before deserializing data to prevent insecure deserialization.",
        "6.5.9": "Implement proper error handling that doesn't leak sensitive information.",
        "6.5.10": "Implement secure authentication and session management to prevent broken authentication vulnerabilities.",
        "6.6": "Protect public-facing web applications with web application firewalls or regular security assessments.",
        "7.1.1": "Define access requirements for each role and restrict access to only what's needed for job responsibilities.",
        "7.1.2": "Restrict privileged user IDs to the fewest privileges necessary.",
        "7.1.3": "Assign access based on an individual's job classification and function.",
        "8.2.3": "Ensure passwords meet complexity and strength requirements (at least 12 characters with a mix of numeric, alphabetic, and special characters).",
        "8.3.1": "Implement multi-factor authentication for all non-console access to the cardholder data environment.",
        "10.1": "Implement audit trails to link all access to system components to each individual user.",
        "10.2": "Implement automated audit trails for all system components."
    }
    
    return remediation_map.get(requirement, "Follow PCI DSS guidelines and industry best practices to address this issue.")

def get_severity_for_pci_requirement(requirement: str) -> str:
    """
    Determine the severity level for a PCI DSS requirement.
    
    Args:
        requirement: The PCI DSS requirement identifier
        
    Returns:
        Severity level as "High", "Medium", or "Low"
    """
    # Define high-risk requirements
    high_risk_requirements = [
        "3.3.3", "3.4", "3.5", "3.6.1", "3.6.3",  # Encryption and key management
        "4.1", "4.2",  # Transmission protection
        "6.5.1", "6.5.4", "6.5.8",  # Critical vulnerabilities (SQL injection, XSS, insecure deserialization)
        "8.3.1"  # MFA requirements
    ]
    
    # Define medium-risk requirements
    medium_risk_requirements = [
        "1.2.1", "1.2.7", "1.3.1", "1.3.2", "1.3.4", "1.4.1",  # Network security
        "2.2.1", "2.2.4", "2.2.5",  # System components
        "6.3.2", "6.3.3", "6.3.4", "6.5", "6.5.2", "6.5.3", "6.5.5", "6.5.7", "6.5.9", "6.5.10", "6.6",  # Secure development
        "7.1.1", "7.1.2", "7.1.3",  # Access control
        "8.2.3"  # Password requirements
    ]
    
    if requirement in high_risk_requirements:
        return "High"
    elif requirement in medium_risk_requirements:
        return "Medium"
    else:
        return "Low"