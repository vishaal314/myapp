import dns.resolver
import whois
from typing import Dict, Any, List, Optional
import trafilatura
import requests
import re
from datetime import datetime
import ssl
import socket

class DomainScanner:
    """
    A scanner for domain and website analysis that detects security issues and PII.
    """
    
    def __init__(self, region: str = "Netherlands"):
        """
        Initialize the domain scanner.
        
        Args:
            region: The region for which to apply GDPR rules
        """
        self.region = region
        self.pii_patterns = {
            'Email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'Phone': r'\b(?:\+\d{1,3}[-.\s]?)?(?:\(?\d{1,3}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{3,4}\b',
            'IP Address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'Social Security Number': r'\b\d{3}-\d{2}-\d{4}\b',
            'Credit Card': r'\b(?:\d{4}[- ]?){3}\d{4}\b',
            'Dutch BSN': r'\b\d{9}\b',
            'URL': r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+',
            'Password': r'(?i)(?:password|passwd|pwd)[\s:=]+\S+',
            'API Key': r'(?i)(?:api|access|auth)[\s_-]*(?:key|token|secret)[\s:=]+\S+',
            'Name': r'\b(?:[A-Z][a-z]+\s){1,2}(?:[A-Z][a-z]+)\b'
        }
    
    def scan_domain(self, domain: str) -> Dict[str, Any]:
        """
        Scan a domain for GDPR compliance issues, security issues, and PII.
        
        Args:
            domain: The domain to scan (e.g., example.com)
            
        Returns:
            Dictionary containing scan results
        """
        results = {
            'domain': domain,
            'scan_type': 'Domain Scan',
            'timestamp': datetime.now().isoformat(),
            'region': self.region,
            'findings': [],
            'pii_types': {},
            'risk_levels': {'High': 0, 'Medium': 0, 'Low': 0},
            'total_pii_found': 0,
            'high_risk_count': 0,
            'medium_risk_count': 0,
            'low_risk_count': 0,
            'security_issues': []
        }
        
        # Run domain checks
        domain_info = self._check_domain_info(domain)
        results['domain_info'] = domain_info
        
        # Run security checks
        security_checks = self._check_security(domain)
        results['security_checks'] = security_checks
        
        # Check for website content
        try:
            # Get website content
            website_text = self._get_website_content(domain)
            results['content_size'] = len(website_text) if website_text else 0
            
            # Scan for PII
            if website_text:
                pii_findings = self._scan_text_for_pii(website_text, f"https://{domain}")
                
                # Update findings
                results['findings'].extend(pii_findings)
                
                # Count PII types and risk levels
                for finding in pii_findings:
                    pii_type = finding['type']
                    risk_level = finding['risk_level']
                    
                    # Update PII types count
                    if pii_type not in results['pii_types']:
                        results['pii_types'][pii_type] = 0
                    results['pii_types'][pii_type] += 1
                    
                    # Update risk levels count
                    results['risk_levels'][risk_level] += 1
                    
                    # Update totals
                    results['total_pii_found'] += 1
                    
                    if risk_level == 'High':
                        results['high_risk_count'] += 1
                    elif risk_level == 'Medium':
                        results['medium_risk_count'] += 1
                    else:
                        results['low_risk_count'] += 1
        except Exception as e:
            results['errors'] = str(e)
        
        # Check security issues and add them as findings
        for issue in security_checks.get('issues', []):
            finding = {
                'type': 'Security Issue',
                'value': issue['issue'],
                'location': domain,
                'risk_level': issue['risk_level'],
                'reason': issue['description']
            }
            results['findings'].append(finding)
            
            # Update risk counts
            results['risk_levels'][issue['risk_level']] += 1
            results['total_pii_found'] += 1
            
            if issue['risk_level'] == 'High':
                results['high_risk_count'] += 1
            elif issue['risk_level'] == 'Medium':
                results['medium_risk_count'] += 1
            else:
                results['low_risk_count'] += 1
        
        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(results)
        
        return results
    
    def _check_domain_info(self, domain: str) -> Dict[str, Any]:
        """
        Check domain registration information.
        
        Args:
            domain: The domain to check
            
        Returns:
            Dictionary with domain information
        """
        try:
            # Get WHOIS information
            w = whois.whois(domain)
            
            # Process the information
            domain_info = {
                'registrar': w.registrar if hasattr(w, 'registrar') else 'Unknown',
                'creation_date': w.creation_date.strftime('%Y-%m-%d') if hasattr(w, 'creation_date') and w.creation_date else 'Unknown',
                'expiration_date': w.expiration_date.strftime('%Y-%m-%d') if hasattr(w, 'expiration_date') and w.expiration_date else 'Unknown',
                'last_updated': w.updated_date.strftime('%Y-%m-%d') if hasattr(w, 'updated_date') and w.updated_date else 'Unknown',
                'name_servers': w.name_servers if hasattr(w, 'name_servers') else [],
                'status': w.status if hasattr(w, 'status') else 'Unknown',
                'is_registered': True
            }
            
            return domain_info
        except Exception as e:
            return {
                'error': str(e),
                'is_registered': False
            }
    
    def _check_security(self, domain: str) -> Dict[str, Any]:
        """
        Check for security issues with a domain.
        
        Args:
            domain: The domain to check
            
        Returns:
            Dictionary with security information
        """
        security_info = {
            'ssl_valid': False,
            'hsts_enabled': False,
            'issues': []
        }
        
        # Check DNS records
        try:
            # Try to get DNS records
            dns_records = dns.resolver.resolve(domain, 'A')
            ip_addresses = [record.address for record in dns_records]
            security_info['ip_addresses'] = ip_addresses
        except Exception:
            security_info['ip_addresses'] = []
            security_info['issues'].append({
                'issue': 'DNS Resolution Failed',
                'description': 'Unable to resolve the domain to IP addresses.',
                'risk_level': 'Medium'
            })
        
        # Check SSL certificate
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Parse certificate info
                    security_info['ssl_valid'] = True
                    
                    # Get expiration date
                    for item in cert['subject']:
                        for key, value in item:
                            if key == 'commonName':
                                security_info['ssl_common_name'] = value
                    
                    # Check if certificate is close to expiration
                    not_after = cert['notAfter']
                    expiry_date = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
                    days_to_expiry = (expiry_date - datetime.now()).days
                    
                    security_info['ssl_expiry_days'] = days_to_expiry
                    
                    if days_to_expiry < 30:
                        security_info['issues'].append({
                            'issue': 'Certificate Near Expiry',
                            'description': f'The SSL certificate will expire in {days_to_expiry} days.',
                            'risk_level': 'Medium'
                        })
        except Exception as e:
            security_info['issues'].append({
                'issue': 'SSL Certificate Invalid',
                'description': f'The domain does not have a valid SSL certificate: {str(e)}',
                'risk_level': 'High'
            })
        
        # Check HSTS header
        try:
            response = requests.get(f"https://{domain}", timeout=10)
            if 'Strict-Transport-Security' in response.headers:
                security_info['hsts_enabled'] = True
            else:
                security_info['issues'].append({
                    'issue': 'Missing HSTS Header',
                    'description': 'The website does not implement HTTP Strict Transport Security.',
                    'risk_level': 'Medium'
                })
        except Exception:
            # Already reported SSL issue, so we don't add another one
            pass
        
        return security_info
    
    def _get_website_content(self, domain: str) -> str:
        """
        Extract text content from a website.
        
        Args:
            domain: The domain to extract content from
            
        Returns:
            Text content of the website
        """
        try:
            # Send a request to the website
            url = f"https://{domain}"
            downloaded = trafilatura.fetch_url(url)
            
            if downloaded:
                text = trafilatura.extract(downloaded)
                return text or ""
            
            # Try HTTP if HTTPS fails
            url = f"http://{domain}"
            downloaded = trafilatura.fetch_url(url)
            
            if downloaded:
                text = trafilatura.extract(downloaded)
                return text or ""
            
            return ""
        except Exception as e:
            # Error extracting content from domain - log for debugging if needed
            pass
            return ""
    
    def _scan_text_for_pii(self, text: str, source_url: str) -> List[Dict[str, Any]]:
        """
        Scan text content for PII.
        
        Args:
            text: The text content to scan
            source_url: The URL where the text was found
            
        Returns:
            List of PII findings
        """
        findings = []
        
        # Scan for each PII type
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                # Get the matched text
                value = match.group(0)
                
                # Determine risk level based on PII type
                risk_level = self._get_risk_level(pii_type)
                
                # Create a finding
                finding = {
                    'type': pii_type,
                    'value': self._mask_sensitive_value(value, pii_type),
                    'location': source_url,
                    'risk_level': risk_level,
                    'reason': self._get_reason(pii_type, risk_level)
                }
                
                findings.append(finding)
        
        return findings
    
    def _get_risk_level(self, pii_type: str) -> str:
        """
        Determine the risk level based on PII type.
        
        Args:
            pii_type: The type of PII
            
        Returns:
            Risk level ('High', 'Medium', or 'Low')
        """
        high_risk_types = ['Social Security Number', 'Credit Card', 'Dutch BSN', 'Password', 'API Key']
        medium_risk_types = ['Email', 'Phone', 'IP Address']
        
        if pii_type in high_risk_types:
            return 'High'
        elif pii_type in medium_risk_types:
            return 'Medium'
        else:
            return 'Low'
    
    def _mask_sensitive_value(self, value: str, pii_type: str) -> str:
        """
        Mask sensitive values for display.
        
        Args:
            value: The original value
            pii_type: The type of PII
            
        Returns:
            Masked value
        """
        if pii_type in ['Credit Card', 'Social Security Number', 'Dutch BSN']:
            # Mask all but the last 4 characters
            masked = '*' * (len(value) - 4) + value[-4:]
            return masked
        elif pii_type in ['Email']:
            # Mask username part of email
            parts = value.split('@')
            if len(parts) == 2:
                username, domain = parts
                masked_username = username[0] + '*' * (len(username) - 1)
                return f"{masked_username}@{domain}"
        elif pii_type in ['Phone']:
            # Mask middle part of phone number
            if len(value) > 4:
                return value[:3] + '*' * (len(value) - 7) + value[-4:]
        elif pii_type in ['Password', 'API Key']:
            # Completely mask these
            return '*' * len(value)
        
        # For other types, return as is
        return value
    
    def _get_reason(self, pii_type: str, risk_level: str) -> str:
        """
        Get a reason explanation for the PII finding.
        
        Args:
            pii_type: The type of PII found
            risk_level: The risk level (Low, Medium, High)
            
        Returns:
            A string explaining why this PII is a concern
        """
        if pii_type == 'Email':
            return "Email addresses are personal data under GDPR Art. 4. They can uniquely identify an individual and must be protected."
        elif pii_type == 'Phone':
            return "Phone numbers are personal data that can directly identify an individual and are subject to GDPR protection."
        elif pii_type == 'IP Address':
            return "IP addresses are considered personal data under GDPR as they can be used to identify a user's location and online behavior."
        elif pii_type == 'Social Security Number':
            return "SSNs are sensitive personal identifiers that must be strictly protected. Unauthorized disclosure risks identity theft."
        elif pii_type == 'Credit Card':
            return "Credit card numbers are financial data requiring strong protection. Disclosure violates PCI DSS and GDPR requirements."
        elif pii_type == 'Dutch BSN':
            return "The Dutch Citizen Service Number (BSN) is highly protected under UAVG and requires specific legal basis for processing."
        elif pii_type == 'Password':
            return "Plaintext passwords represent a significant security risk. All passwords should be properly hashed and salted."
        elif pii_type == 'API Key':
            return "API keys should never be exposed as they can grant access to services and potentially to personal data."
        elif pii_type == 'Name':
            return "Personal names are personal data under GDPR and can identify an individual, especially when combined with other data."
        elif pii_type == 'URL':
            return "URLs may contain personal data or session identifiers that could compromise user privacy."
        elif pii_type == 'Security Issue':
            return "Security vulnerabilities may expose personal data and lead to GDPR compliance issues."
        else:
            return f"This type of personal data ({pii_type}) requires protection under GDPR to prevent unauthorized access or disclosure."
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on scan results.
        
        Args:
            results: The scan results
            
        Returns:
            List of recommendation objects
        """
        recommendations = []
        
        # Security recommendations
        if not results.get('security_checks', {}).get('ssl_valid', False):
            recommendations.append({
                'title': 'Implement SSL/TLS',
                'priority': 'High',
                'description': 'The website does not have a valid SSL certificate, which is required for protecting personal data in transit.',
                'steps': [
                    'Obtain an SSL certificate from a trusted certificate authority',
                    'Install the certificate on your web server',
                    'Configure your server to redirect HTTP to HTTPS',
                    'Implement HTTP Strict Transport Security (HSTS)'
                ]
            })
        
        # Cookie recommendations
        recommendations.append({
            'title': 'Implement Cookie Consent',
            'priority': 'High',
            'description': 'Ensure your website has a proper cookie consent mechanism in compliance with GDPR.',
            'steps': [
                'Audit all cookies used on your website',
                'Categorize cookies as necessary or optional',
                'Implement a cookie consent banner that allows users to give explicit consent',
                'Ensure no non-necessary cookies are set before consent is obtained',
                'Document your cookie policy clearly'
            ]
        })
        
        # Privacy policy recommendations
        recommendations.append({
            'title': 'Update Privacy Policy',
            'priority': 'Medium',
            'description': 'Ensure your privacy policy complies with GDPR requirements.',
            'steps': [
                'Clearly identify what personal data is collected',
                'Explain the legal basis for processing each type of data',
                'Describe data retention periods',
                'Include information about user rights',
                'Make the policy easily accessible on your website'
            ]
        })
        
        # PII-specific recommendations
        pii_types = results.get('pii_types', {})
        
        if 'Email' in pii_types or 'Phone' in pii_types or 'Name' in pii_types:
            recommendations.append({
                'title': 'Secure Contact Information',
                'priority': 'Medium',
                'description': 'Contact information on your website should be protected from scraping and unauthorized access.',
                'steps': [
                    'Use contact forms instead of displaying email addresses directly',
                    'Consider using images or JavaScript to obfuscate contact details',
                    'Implement rate limiting to prevent scraping',
                    'Document the purpose and legal basis for collecting contact information'
                ]
            })
        
        if results.get('high_risk_count', 0) > 0:
            recommendations.append({
                'title': 'Address High-Risk PII Exposure',
                'priority': 'High',
                'description': 'High-risk personal data requires immediate attention to ensure compliance.',
                'steps': [
                    'Remove or mask exposed high-risk PII from public access',
                    'Implement encryption for sensitive data storage',
                    'Review access controls to sensitive information',
                    'Consider conducting a Data Protection Impact Assessment (DPIA)'
                ]
            })
        
        return recommendations