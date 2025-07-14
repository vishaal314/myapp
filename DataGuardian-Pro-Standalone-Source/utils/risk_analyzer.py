"""
Smart AI-powered risk severity analysis and color-coding system.
"""
import re
import json
import math
from typing import Dict, List, Any, Tuple, Optional
import hashlib

# Define risk severity levels with their corresponding colors
SEVERITY_COLORS = {
    'critical': '#FF2A2A',  # Bright red
    'high': '#FF5C5C',      # Red
    'medium': '#FFA726',    # Orange
    'low': '#FFEB3B',       # Yellow
    'info': '#2196F3',      # Blue
    'safe': '#4CAF50'       # Green
}

# Context weights for different scan types
CONTEXT_WEIGHTS = {
    'code_scan': {
        'credentials': 1.5,         # Credentials in code are very dangerous
        'sql_injection': 1.4,       # SQL injection is dangerous
        'xss': 1.3,                 # XSS is dangerous
        'insecure_auth': 1.3,       # Insecure auth is dangerous
        'path_traversal': 1.2,      # Path traversal is dangerous
        'insecure_deserialization': 1.3,  # Insecure deserialization is dangerous
        'csrf': 1.1,                # CSRF is dangerous
        'insecure_cookies': 1.0,    # Insecure cookies
        'Email': 0.7,               # Emails in code 
        'Phone': 0.6,               # Phone numbers in code
        'Address': 0.7,             # Addresses in code
        'Name': 0.5                 # Names in code
    },
    'website_scan': {
        'Email': 0.9,               # Emails on websites
        'Phone': 0.8,               # Phone numbers on websites
        'Address': 0.8,             # Addresses on websites
        'Name': 0.6,                # Names on websites
        'IP Address': 1.0,          # IP addresses on websites
        'xss': 1.4,                 # XSS on websites is very bad
        'csrf': 1.3,                # CSRF on websites is very bad
        'insecure_cookies': 1.2,    # Insecure cookies on websites
        'sensitive_url': 1.1        # Sensitive URLs
    },
    'blob_scan': {
        'Credit Card': 1.5,         # Credit cards in documents are high risk
        'BSN': 1.5,                 # BSN numbers in documents are high risk
        'Passport Number': 1.5,     # Passport numbers in documents are high risk
        'Financial Data': 1.4,      # Financial data in documents
        'Medical Data': 1.4,        # Medical data in documents
        'Date of Birth': 1.2,       # DOB in documents
        'Email': 0.8,               # Emails in documents
        'Phone': 0.7,               # Phone numbers in documents
        'Address': 0.8,             # Addresses in documents
        'Name': 0.6                 # Names in documents
    },
    'database_scan': {
        'Credit Card': 1.6,         # Credit cards in databases are very high risk
        'BSN': 1.6,                 # BSN numbers in databases are very high risk
        'Passport Number': 1.6,     # Passport numbers in databases are very high risk
        'Financial Data': 1.5,      # Financial data in databases
        'Medical Data': 1.5,        # Medical data in databases
        'Date of Birth': 1.3,       # DOB in databases
        'insecure_storage': 1.4,    # Insecure storage in databases
        'encryption_missing': 1.5,  # Missing encryption
        'excess_privilege': 1.3     # Excess privileges
    }
}

# Default weights if specific context not found
DEFAULT_WEIGHTS = {
    'Credit Card': 1.5,
    'BSN': 1.5,
    'Passport Number': 1.5,
    'Financial Data': 1.4,
    'Medical Data': 1.4,
    'Date of Birth': 1.2,
    'Email': 0.8,
    'Phone': 0.7,
    'Address': 0.8,
    'Name': 0.6,
    'IP Address': 0.7,
    'Username': 0.7,
    'Password': 1.3,
    'Credentials': 1.4,
    'Vulnerability': 1.3
}

# PII data concentration thresholds
CONCENTRATION_THRESHOLDS = {
    'low': 0.02,      # 2% of findings are of the same type
    'medium': 0.05,   # 5% of findings are of the same type
    'high': 0.10      # 10% of findings are of the same type
}

class RiskAnalyzer:
    """
    Smart AI-powered risk severity analyzer that uses context-aware
    analysis to calculate risk levels and provide color coding.
    """
    
    def __init__(self, scan_type: str = 'code_scan'):
        """
        Initialize the risk analyzer.
        
        Args:
            scan_type: The type of scan being analyzed
        """
        self.scan_type = scan_type
        self.weights = CONTEXT_WEIGHTS.get(scan_type, DEFAULT_WEIGHTS)
    
    def analyze_findings(self, findings: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Analyze findings from a scan and calculate smart severity levels.
        
        Args:
            findings: List of findings from a scan
            
        Returns:
            Tuple containing summary statistics and enhanced findings with smart severity
        """
        if not findings:
            return {'risk_score': 0, 'severity_level': 'safe'}, []
        
        # First pass: collect statistics
        type_counts = {}
        risk_counts = {'High': 0, 'Medium': 0, 'Low': 0}
        location_clusters = {}
        
        # Keep track of the number of findings and unique finding types
        total_findings = len(findings)
        total_score = 0
        
        for finding in findings:
            # Count by type
            finding_type = finding.get('type', 'Unknown')
            type_counts[finding_type] = type_counts.get(finding_type, 0) + 1
            
            # Count by risk level
            risk_level = finding.get('risk_level', 'Low')
            risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
            
            # Track location clusters
            location = finding.get('location', '')
            if location:
                location_cluster = re.sub(r'Line \d+', 'Line X', location)
                location_clusters[location_cluster] = location_clusters.get(location_cluster, 0) + 1
        
        # Second pass: apply smart severity
        enhanced_findings = []
        for finding in findings:
            finding_type = finding.get('type', 'Unknown')
            original_risk = finding.get('risk_level', 'Low')
            
            # Calculate type concentration (what % of findings are this type)
            concentration = type_counts[finding_type] / total_findings if total_findings > 0 else 0
            
            # Calculate base score based on risk level
            base_score = {'High': 3, 'Medium': 2, 'Low': 1}.get(original_risk, 1)
            
            # Apply context weight
            if finding_type.startswith('Vulnerability:'):
                # Extract vulnerability type from "Vulnerability:Type"
                vuln_type = finding_type.split(':', 1)[1].strip().lower().replace(' ', '_')
                weight = self.weights.get(vuln_type, 1.3)  # Default weight for vulnerabilities
            else:
                weight = self.weights.get(finding_type, DEFAULT_WEIGHTS.get(finding_type, 1.0))
            
            # Adjust for concentration
            concentration_factor = 1.0
            if concentration >= CONCENTRATION_THRESHOLDS['high']:
                concentration_factor = 1.3
            elif concentration >= CONCENTRATION_THRESHOLDS['medium']:
                concentration_factor = 1.2
            elif concentration >= CONCENTRATION_THRESHOLDS['low']:
                concentration_factor = 1.1
            
            # Adjust for clustering (multiple findings in same area)
            clustering_factor = 1.0
            location = finding.get('location', '')
            if location:
                location_cluster = re.sub(r'Line \d+', 'Line X', location)
                cluster_size = location_clusters.get(location_cluster, 0)
                if cluster_size >= 5:
                    clustering_factor = 1.3
                elif cluster_size >= 3:
                    clustering_factor = 1.2
                elif cluster_size >= 2:
                    clustering_factor = 1.1
            
            # Calculate final smart score
            smart_score = base_score * weight * concentration_factor * clustering_factor
            
            # Determine smart severity level
            if smart_score >= 4.5:
                smart_severity = 'critical'
            elif smart_score >= 3.5:
                smart_severity = 'high'
            elif smart_score >= 2.5:
                smart_severity = 'medium'
            elif smart_score >= 1.5:
                smart_severity = 'low'
            else:
                smart_severity = 'info'
            
            # Get color code
            color = SEVERITY_COLORS.get(smart_severity, '#777777')
            
            # Create enhanced finding
            enhanced_finding = finding.copy()
            enhanced_finding.update({
                'smart_score': round(smart_score, 2),
                'smart_severity': smart_severity,
                'color': color,
                'context_weight': weight,
                'concentration_factor': concentration_factor,
                'clustering_factor': clustering_factor
            })
            
            enhanced_findings.append(enhanced_finding)
            total_score += smart_score
        
        # Calculate overall risk score
        avg_score = total_score / len(enhanced_findings) if enhanced_findings else 0
        normalized_score = min(100, round(avg_score * 20))
        
        # Determine overall severity level
        if normalized_score >= 80:
            severity_level = 'critical'
        elif normalized_score >= 60:
            severity_level = 'high'
        elif normalized_score >= 40:
            severity_level = 'medium'
        elif normalized_score >= 20:
            severity_level = 'low'
        else:
            severity_level = 'info'
        
        # Sort enhanced findings by smart_score (highest first)
        enhanced_findings.sort(key=lambda x: x.get('smart_score', 0), reverse=True)
        
        # Create summary statistics
        summary = {
            'risk_score': normalized_score,
            'severity_level': severity_level,
            'severity_color': SEVERITY_COLORS.get(severity_level, '#777777'),
            'total_findings': total_findings,
            'risk_counts': risk_counts,
            'risk_distribution': {
                'critical': len([f for f in enhanced_findings if f.get('smart_severity') == 'critical']),
                'high': len([f for f in enhanced_findings if f.get('smart_severity') == 'high']),
                'medium': len([f for f in enhanced_findings if f.get('smart_severity') == 'medium']),
                'low': len([f for f in enhanced_findings if f.get('smart_severity') == 'low']),
                'info': len([f for f in enhanced_findings if f.get('smart_severity') == 'info'])
            },
            'type_distribution': {k: v for k, v in sorted(
                type_counts.items(), key=lambda item: item[1], reverse=True
            )}
        }
        
        return summary, enhanced_findings

def get_severity_color(severity: str) -> str:
    """
    Get color code for a severity level.
    
    Args:
        severity: Severity level string
        
    Returns:
        Hex color code
    """
    return SEVERITY_COLORS.get(severity.lower(), '#777777')

def colorize_finding(finding: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add color information to a finding based on its risk level.
    
    Args:
        finding: Finding dictionary
        
    Returns:
        Finding with color information added
    """
    # Get risk level and map to color
    risk_level = finding.get('risk_level', 'Low').lower()
    smart_severity = finding.get('smart_severity', risk_level).lower()
    
    # Map standard risk levels to severity levels
    if 'smart_severity' not in finding:
        if risk_level == 'high':
            smart_severity = 'high'
        elif risk_level == 'medium':
            smart_severity = 'medium'
        elif risk_level == 'low':
            smart_severity = 'low'
        else:
            smart_severity = 'info'
    
    # Get color
    color = SEVERITY_COLORS.get(smart_severity, '#777777')
    
    # Add color to finding
    enhanced = finding.copy()
    enhanced['color'] = color
    enhanced['smart_severity'] = smart_severity
    
    return enhanced

def get_risk_color_gradient(score: float, min_score: float = 0, max_score: float = 100) -> str:
    """
    Get a color on a gradient from green to red based on a risk score.
    
    Args:
        score: Risk score
        min_score: Minimum possible score
        max_score: Maximum possible score
        
    Returns:
        Hex color code
    """
    # Normalize score to 0-1 range
    normalized = (score - min_score) / (max_score - min_score)
    normalized = max(0, min(1, normalized))  # Ensure in range [0,1]
    
    # Convert to hue (120 for green, 0 for red)
    hue = (1 - normalized) * 120
    
    # Convert HSV to RGB
    h = hue / 60
    s = 0.8  # Saturation
    v = 0.9  # Value
    
    c = v * s
    x = c * (1 - abs(h % 2 - 1))
    m = v - c
    
    if h < 1:
        r, g, b = c, x, 0
    elif h < 2:
        r, g, b = x, c, 0
    elif h < 3:
        r, g, b = 0, c, x
    elif h < 4:
        r, g, b = 0, x, c
    elif h < 5:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    
    r, g, b = int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)
    
    return f'#{r:02x}{g:02x}{b:02x}'

def generate_color_scale(num_steps: int = 5) -> List[str]:
    """
    Generate a color scale from green to red with the specified number of steps.
    
    Args:
        num_steps: Number of colors in the scale
        
    Returns:
        List of hex color codes
    """
    return [get_risk_color_gradient(i * (100 / (num_steps - 1))) for i in range(num_steps)]