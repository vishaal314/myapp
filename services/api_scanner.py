"""
API Scanner module for comprehensive privacy compliance and security scanning of REST APIs.

This module analyzes API endpoints for PII exposure, authentication vulnerabilities,
data leakage, GDPR compliance issues, and provides detailed security recommendations.
"""

import os
import re
import json
import time
import logging

# Import centralized logging
try:
    from utils.centralized_logger import get_scanner_logger
    logger = get_scanner_logger("api_scanner")
except ImportError:
    # Fallback to standard logging if centralized logger not available
    logger = logging.getLogger(__name__)
import requests
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from urllib.parse import urlparse, urljoin, parse_qs
import yaml
from requests.auth import HTTPBasicAuth, HTTPDigestAuth

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class APIScanner:
    """
    A comprehensive scanner that analyzes REST APIs for privacy compliance issues,
    security vulnerabilities, PII exposure, and GDPR compliance requirements.
    """
    
    def __init__(self, max_endpoints=50, request_timeout=10, rate_limit_delay=1, 
                 follow_redirects=True, verify_ssl=True, region="Netherlands"):
        """
        Initialize the API scanner.
        
        Args:
            max_endpoints: Maximum number of endpoints to scan (default: 50)
            request_timeout: Timeout for API requests in seconds (default: 10)
            rate_limit_delay: Delay between requests to respect rate limits (default: 1)
            follow_redirects: Whether to follow HTTP redirects (default: True)
            verify_ssl: Whether to verify SSL certificates (default: True)
            region: Region for applying GDPR rules (default: "Netherlands")
        """
        self.max_endpoints = max_endpoints
        self.request_timeout = request_timeout
        self.rate_limit_delay = rate_limit_delay
        self.follow_redirects = follow_redirects
        self.verify_ssl = verify_ssl
        self.region = region
        self.progress_callback = None
        self.is_running = False
        self.start_time = None
        
        # Initialize session with proper headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DataGuardian-API-Scanner/1.0 (Privacy Compliance Scanner)',
            'Accept': 'application/json, application/xml, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9'
        })
        
        # Load PII detection patterns
        self._load_pii_patterns()
        
        # Load common API vulnerabilities database
        self._load_vulnerability_patterns()
        
        # Load authentication methods database
        self._load_auth_methods()
    
    def _load_pii_patterns(self):
        """Load PII detection patterns for API response analysis."""
        self.pii_patterns = {
            'email': {
                'pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                'description': 'Email addresses detected in API response',
                'severity': 'High',
                'gdpr_category': 'Personal Data'
            },
            'phone': {
                'pattern': r'(\+\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
                'description': 'Phone numbers detected in API response',
                'severity': 'High',
                'gdpr_category': 'Personal Data'
            },
            'ssn': {
                'pattern': r'\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b',
                'description': 'Social Security Numbers detected',
                'severity': 'Critical',
                'gdpr_category': 'Special Category Data'
            },
            'credit_card': {
                'pattern': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
                'description': 'Credit card numbers detected',
                'severity': 'Critical',
                'gdpr_category': 'Financial Data'
            },
            'ip_address': {
                'pattern': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
                'description': 'IP addresses detected',
                'severity': 'Medium',
                'gdpr_category': 'Technical Data'
            },
            'api_key': {
                'pattern': r'[Aa][Pp][Ii][-_]?[Kk][Ee][Yy]\s*[:=]\s*["\']?([A-Za-z0-9\-_]{20,})["\']?',
                'description': 'API keys exposed in response',
                'severity': 'Critical',
                'gdpr_category': 'Security Credentials'
            },
            'password': {
                'pattern': r'[Pp]assword\s*[:=]\s*["\']?([^"\'\s]{6,})["\']?',
                'description': 'Passwords exposed in response',
                'severity': 'Critical',
                'gdpr_category': 'Authentication Data'
            }
        }
    
    def _load_vulnerability_patterns(self):
        """Load common API vulnerability patterns."""
        self.vulnerability_patterns = {
            'sql_injection': {
                'payloads': ["' OR '1'='1", "'; DROP TABLE users; --", "' UNION SELECT * FROM users --"],
                'indicators': ['mysql', 'postgresql', 'sql syntax', 'ora-', 'sqlite'],
                'description': 'SQL injection vulnerability detected',
                'severity': 'Critical'
            },
            'xss': {
                'payloads': ['<script>alert("xss")</script>', '"><script>alert(1)</script>', "javascript:alert('xss')"],
                'indicators': ['<script>', 'javascript:', 'onerror=', 'onload='],
                'description': 'Cross-site scripting vulnerability detected',
                'severity': 'High'
            },
            'path_traversal': {
                'payloads': ['../../../etc/passwd', '..\\..\\..\\windows\\system32\\drivers\\etc\\hosts'],
                'indicators': ['/etc/passwd', 'root:x:', 'windows\\system32'],
                'description': 'Path traversal vulnerability detected',
                'severity': 'High'
            },
            'command_injection': {
                'payloads': ['; ls -la', '| whoami', '& dir'],
                'indicators': ['bin/', 'total ', 'drwx', 'administrator', 'system32'],
                'description': 'Command injection vulnerability detected',
                'severity': 'Critical'
            }
        }
    
    def _load_auth_methods(self):
        """Load authentication method analysis patterns."""
        self.auth_methods = {
            'bearer_token': {
                'header': 'Authorization',
                'pattern': r'Bearer\s+([A-Za-z0-9\-_\.]+)',
                'description': 'Bearer token authentication',
                'security_level': 'Medium'
            },
            'basic_auth': {
                'header': 'Authorization',
                'pattern': r'Basic\s+([A-Za-z0-9+/=]+)',
                'description': 'HTTP Basic authentication',
                'security_level': 'Low'
            },
            'api_key_header': {
                'header': 'X-API-Key',
                'pattern': r'([A-Za-z0-9\-_]{20,})',
                'description': 'API key in header',
                'security_level': 'Medium'
            },
            'jwt_token': {
                'header': 'Authorization',
                'pattern': r'Bearer\s+([A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+)',
                'description': 'JWT token authentication',
                'security_level': 'High'
            }
        }
    
    def set_progress_callback(self, callback_function):
        """
        Set a callback function for progress updates during API scanning.
        
        Args:
            callback_function: A function that takes current, total, and current endpoint
        """
        self.progress_callback = callback_function
    
    def scan_api(self, base_url: str, auth_token: Optional[str] = None, openapi_spec: Optional[str] = None, 
                 endpoints: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Perform a comprehensive scan of an API.
        
        Args:
            base_url: The base URL of the API to scan
            auth_token: Authentication token (optional)
            openapi_spec: OpenAPI/Swagger specification URL or content (optional)
            endpoints: List of specific endpoints to scan (optional)
            
        Returns:
            Dictionary with comprehensive scan results
        """
        self.start_time = datetime.now()
        self.is_running = True
        
        # Generate a unique scan ID
        scan_id = hashlib.md5(f"{base_url}:{self.start_time.isoformat()}".encode()).hexdigest()[:10]
        
        # Parse and normalize the base URL
        parsed_url = urlparse(base_url)
        if not parsed_url.scheme:
            base_url = f"https://{base_url}"
            parsed_url = urlparse(base_url)
        
        base_domain = parsed_url.netloc
        
        # Initialize scan data structures
        scanned_endpoints = []
        findings = []
        vulnerabilities = []
        pii_exposures = []
        auth_issues = []
        
        # Set up authentication if provided
        if auth_token:
            if auth_token.startswith('Bearer '):
                self.session.headers['Authorization'] = auth_token
            else:
                self.session.headers['Authorization'] = f'Bearer {auth_token}'
        
        # Discover endpoints
        if openapi_spec:
            discovered_endpoints = self._parse_openapi_spec(openapi_spec, base_url)
        elif endpoints:
            discovered_endpoints = [urljoin(base_url, ep) for ep in endpoints]
        else:
            discovered_endpoints = self._discover_endpoints(base_url)
        
        # Limit the number of endpoints to scan
        discovered_endpoints = discovered_endpoints[:self.max_endpoints]
        
        # Report initial progress
        if self.progress_callback:
            self.progress_callback(0, len(discovered_endpoints), f"Starting API scan of {base_domain}")
        
        # Scan each endpoint
        for i, endpoint_url in enumerate(discovered_endpoints):
            if not self.is_running:
                break
            
            logger.info(f"Scanning endpoint: {endpoint_url}")
            
            try:
                # Respect rate limiting
                time.sleep(self.rate_limit_delay)
                
                # Scan the endpoint
                endpoint_data = self._scan_endpoint(endpoint_url, base_url)
                scanned_endpoints.append(endpoint_data)
                
                # Extract findings
                endpoint_findings = endpoint_data.get('findings', [])
                findings.extend(endpoint_findings)
                
                # Categorize findings
                for finding in endpoint_findings:
                    if finding.get('type') == 'vulnerability':
                        vulnerabilities.append(finding)
                    elif finding.get('type') == 'pii_exposure':
                        pii_exposures.append(finding)
                    elif finding.get('type') == 'auth_issue':
                        auth_issues.append(finding)
                
                # Report progress
                if self.progress_callback:
                    self.progress_callback(i + 1, len(discovered_endpoints), f"Scanned {endpoint_url}")
                
            except Exception as e:
                logger.warning(f"Error scanning endpoint {endpoint_url}: {str(e)}")
                continue
        
        # Perform additional security checks
        ssl_info = self._check_ssl_security(base_url)
        cors_analysis = self._analyze_cors_policy(base_url)
        rate_limiting = self._check_rate_limiting(base_url)
        
        # Calculate completion time
        completion_time = datetime.now()
        duration_seconds = (completion_time - self.start_time).total_seconds()
        
        # Generate comprehensive scan results
        scan_results = {
            'scan_id': scan_id,
            'scan_time': self.start_time.isoformat(),
            'completion_time': completion_time.isoformat(),
            'duration_seconds': duration_seconds,
            'base_url': base_url,
            'base_domain': base_domain,
            'endpoints_scanned': len(scanned_endpoints),
            'endpoints_data': scanned_endpoints,
            'findings': findings,
            'vulnerabilities': vulnerabilities,
            'pii_exposures': pii_exposures,
            'auth_issues': auth_issues,
            'ssl_info': ssl_info,
            'cors_analysis': cors_analysis,
            'rate_limiting': rate_limiting,
            'stats': {
                'total_endpoints': len(discovered_endpoints),
                'successful_scans': len(scanned_endpoints),
                'total_findings': len(findings),
                'critical_findings': len([f for f in findings if f.get('severity') == 'Critical']),
                'high_findings': len([f for f in findings if f.get('severity') == 'High']),
                'medium_findings': len([f for f in findings if f.get('severity') == 'Medium']),
                'low_findings': len([f for f in findings if f.get('severity') == 'Low'])
            },
            'scan_type': 'api'
        }
        
        self.is_running = False
        return scan_results
    
    def _discover_endpoints(self, base_url: str) -> List[str]:
        """
        Discover API endpoints through various methods.
        
        Args:
            base_url: The base URL to discover endpoints from
            
        Returns:
            List of discovered endpoint URLs
        """
        endpoints = set()
        
        # Common API endpoint patterns
        common_endpoints = [
            '/api/v1/users', '/api/v1/user', '/api/users', '/users',
            '/api/v1/auth', '/api/auth', '/auth', '/login',
            '/api/v1/data', '/api/data', '/data',
            '/api/v1/profile', '/api/profile', '/profile',
            '/api/v1/admin', '/api/admin', '/admin',
            '/api/v1/config', '/api/config', '/config',
            '/api/v1/health', '/api/health', '/health',
            '/api/v1/status', '/api/status', '/status',
            '/api/docs', '/docs', '/swagger', '/openapi.json'
        ]
        
        # Try common endpoints
        for endpoint in common_endpoints:
            full_url = urljoin(base_url, endpoint)
            endpoints.add(full_url)
        
        # Try to find OpenAPI/Swagger documentation
        doc_endpoints = ['/swagger.json', '/openapi.json', '/api-docs', '/docs']
        for doc_endpoint in doc_endpoints:
            try:
                response = self.session.get(urljoin(base_url, doc_endpoint), 
                                          timeout=self.request_timeout)
                if response.status_code == 200:
                    spec_endpoints = self._parse_openapi_spec(response.text, base_url)
                    endpoints.update(spec_endpoints)
                    break
            except:
                continue
        
        return list(endpoints)
    
    def _parse_openapi_spec(self, spec_content: str, base_url: str) -> List[str]:
        """
        Parse OpenAPI/Swagger specification to extract endpoints.
        
        Args:
            spec_content: OpenAPI specification content (JSON or YAML)
            base_url: Base URL for the API
            
        Returns:
            List of endpoint URLs
        """
        endpoints = []
        
        try:
            # Try to parse as JSON first
            try:
                spec = json.loads(spec_content)
            except json.JSONDecodeError:
                # Try to parse as YAML
                spec = yaml.safe_load(spec_content)
            
            # Extract paths from OpenAPI spec
            paths = spec.get('paths', {})
            for path, methods in paths.items():
                if isinstance(methods, dict):
                    for method in methods.keys():
                        if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                            endpoint_url = urljoin(base_url, path)
                            endpoints.append(endpoint_url)
        
        except Exception as e:
            logger.warning(f"Failed to parse OpenAPI spec: {str(e)}")
        
        return endpoints
    
    def _scan_endpoint(self, endpoint_url: str, base_url: str) -> Dict[str, Any]:
        """
        Scan a single API endpoint for security issues and PII exposure.
        
        Args:
            endpoint_url: The endpoint URL to scan
            base_url: The base URL of the API
            
        Returns:
            Dictionary with endpoint scan results
        """
        endpoint_data = {
            'url': endpoint_url,
            'methods_tested': [],
            'responses': {},
            'findings': [],
            'pii_detected': [],
            'vulnerabilities': [],
            'auth_required': False,
            'response_time_ms': 0
        }
        
        # Test different HTTP methods
        methods_to_test = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
        
        for method in methods_to_test:
            try:
                start_time = time.time()
                
                # Prepare request data for POST/PUT/PATCH
                request_data = None
                if method in ['POST', 'PUT', 'PATCH']:
                    request_data = {'test': 'data', 'id': 1}
                
                # Make the request
                response = self.session.request(
                    method=method,
                    url=endpoint_url,
                    json=request_data,
                    timeout=self.request_timeout,
                    verify=self.verify_ssl,
                    allow_redirects=self.follow_redirects
                )
                
                response_time = (time.time() - start_time) * 1000
                endpoint_data['response_time_ms'] = max(endpoint_data['response_time_ms'], response_time)
                
                # Store response information
                endpoint_data['methods_tested'].append(method)
                endpoint_data['responses'][method] = {
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'content_type': response.headers.get('content-type', ''),
                    'content_length': len(response.content),
                    'response_time_ms': response_time
                }
                
                # Analyze response for security issues
                self._analyze_response_security(response, method, endpoint_data)
                
                # Check for PII in response
                self._check_pii_exposure(response, method, endpoint_data)
                
                # Test for vulnerabilities if method allows input
                if method in ['GET', 'POST', 'PUT', 'PATCH'] and response.status_code not in [404, 405]:
                    self._test_vulnerabilities(endpoint_url, method, endpoint_data)
                
            except requests.exceptions.Timeout:
                endpoint_data['findings'].append({
                    'type': 'performance',
                    'severity': 'Medium',
                    'description': f'{method} request timed out after {self.request_timeout} seconds',
                    'method': method,
                    'url': endpoint_url
                })
            except requests.exceptions.SSLError:
                endpoint_data['findings'].append({
                    'type': 'ssl_error',
                    'severity': 'High',
                    'description': f'SSL certificate error for {method} request',
                    'method': method,
                    'url': endpoint_url
                })
            except Exception as e:
                logger.debug(f"Error testing {method} on {endpoint_url}: {str(e)}")
                continue
        
        return endpoint_data
    
    def _analyze_response_security(self, response: requests.Response, method: str, endpoint_data: Dict[str, Any]):
        """Analyze HTTP response for security issues."""
        headers = response.headers
        
        # Check for missing security headers
        security_headers = {
            'X-Frame-Options': 'Missing X-Frame-Options header (clickjacking protection)',
            'X-Content-Type-Options': 'Missing X-Content-Type-Options header (MIME sniffing protection)',
            'X-XSS-Protection': 'Missing X-XSS-Protection header (XSS protection)',
            'Strict-Transport-Security': 'Missing HSTS header (HTTPS enforcement)',
            'Content-Security-Policy': 'Missing Content-Security-Policy header (XSS/injection protection)'
        }
        
        for header, description in security_headers.items():
            if header not in headers:
                endpoint_data['findings'].append({
                    'type': 'security_header',
                    'severity': 'Medium',
                    'description': description,
                    'method': method,
                    'url': response.url,
                    'recommendation': f'Add {header} header to improve security'
                })
        
        # Check for information disclosure in headers
        sensitive_headers = ['Server', 'X-Powered-By', 'X-AspNet-Version']
        for header in sensitive_headers:
            if header in headers:
                endpoint_data['findings'].append({
                    'type': 'information_disclosure',
                    'severity': 'Low',
                    'description': f'Server information disclosed in {header} header: {headers[header]}',
                    'method': method,
                    'url': response.url,
                    'recommendation': f'Remove or obfuscate {header} header'
                })
        
        # Check for authentication requirements
        if response.status_code == 401:
            endpoint_data['auth_required'] = True
            endpoint_data['findings'].append({
                'type': 'auth_issue',
                'severity': 'Info',
                'description': 'Endpoint requires authentication',
                'method': method,
                'url': response.url
            })
        elif response.status_code == 403:
            endpoint_data['findings'].append({
                'type': 'auth_issue',
                'severity': 'Medium',
                'description': 'Access forbidden - insufficient permissions',
                'method': method,
                'url': response.url
            })
    
    def _check_pii_exposure(self, response: requests.Response, method: str, endpoint_data: Dict[str, Any]):
        """Check API response for PII exposure."""
        try:
            response_text = response.text
            
            for pii_type, pattern_info in self.pii_patterns.items():
                matches = re.findall(pattern_info['pattern'], response_text, re.IGNORECASE)
                if matches:
                    endpoint_data['pii_detected'].append({
                        'type': pii_type,
                        'count': len(matches),
                        'severity': pattern_info['severity'],
                        'description': pattern_info['description'],
                        'gdpr_category': pattern_info['gdpr_category'],
                        'method': method
                    })
                    
                    endpoint_data['findings'].append({
                        'type': 'pii_exposure',
                        'severity': pattern_info['severity'],
                        'description': f"{pattern_info['description']} ({len(matches)} instances)",
                        'pii_type': pii_type,
                        'method': method,
                        'url': response.url,
                        'gdpr_category': pattern_info['gdpr_category'],
                        'recommendation': f'Implement data masking or removal for {pii_type} in API responses'
                    })
        
        except Exception as e:
            logger.debug(f"Error checking PII exposure: {str(e)}")
    
    def _test_vulnerabilities(self, endpoint_url: str, method: str, endpoint_data: Dict[str, Any]):
        """Test endpoint for common vulnerabilities."""
        for vuln_type, vuln_info in self.vulnerability_patterns.items():
            for payload in vuln_info['payloads']:
                try:
                    # Test vulnerability with payload
                    test_url = endpoint_url
                    request_data = None
                    
                    if method == 'GET':
                        # Add payload to URL parameters
                        test_url = f"{endpoint_url}?test={payload}"
                    elif method in ['POST', 'PUT', 'PATCH']:
                        # Add payload to request body
                        request_data = {'test': payload, 'id': payload}
                    
                    response = self.session.request(
                        method=method,
                        url=test_url,
                        json=request_data,
                        timeout=self.request_timeout,
                        verify=self.verify_ssl
                    )
                    
                    # Check response for vulnerability indicators
                    response_text = response.text.lower()
                    for indicator in vuln_info['indicators']:
                        if indicator in response_text:
                            endpoint_data['vulnerabilities'].append({
                                'type': vuln_type,
                                'severity': vuln_info['severity'],
                                'description': vuln_info['description'],
                                'payload': payload,
                                'indicator': indicator,
                                'method': method
                            })
                            
                            endpoint_data['findings'].append({
                                'type': 'vulnerability',
                                'severity': vuln_info['severity'],
                                'description': f"{vuln_info['description']} with payload: {payload}",
                                'vulnerability_type': vuln_type,
                                'method': method,
                                'url': endpoint_url,
                                'recommendation': f'Implement input validation and sanitization to prevent {vuln_type}'
                            })
                            break
                
                except Exception as e:
                    logger.debug(f"Error testing {vuln_type} vulnerability: {str(e)}")
                    continue
    
    def _check_ssl_security(self, base_url: str) -> Dict[str, Any]:
        """Check SSL/TLS security configuration."""
        ssl_info = {
            'enabled': False,
            'valid_certificate': False,
            'protocol_version': None,
            'cipher_suite': None,
            'issues': []
        }
        
        try:
            parsed_url = urlparse(base_url)
            if parsed_url.scheme == 'https':
                ssl_info['enabled'] = True
                
                # Test SSL connection
                response = self.session.get(base_url, timeout=self.request_timeout, verify=True)
                ssl_info['valid_certificate'] = True
                
            else:
                ssl_info['issues'].append('API does not use HTTPS encryption')
        
        except requests.exceptions.SSLError as e:
            ssl_info['issues'].append(f'SSL certificate error: {str(e)}')
        except Exception as e:
            ssl_info['issues'].append(f'SSL check failed: {str(e)}')
        
        return ssl_info
    
    def _analyze_cors_policy(self, base_url: str) -> Dict[str, Any]:
        """Analyze CORS policy configuration."""
        cors_info = {
            'enabled': False,
            'allow_origins': [],
            'allow_methods': [],
            'allow_headers': [],
            'issues': []
        }
        
        try:
            # Send OPTIONS request to check CORS headers
            response = self.session.options(base_url, timeout=self.request_timeout)
            
            cors_headers = {
                'Access-Control-Allow-Origin': 'allow_origins',
                'Access-Control-Allow-Methods': 'allow_methods',
                'Access-Control-Allow-Headers': 'allow_headers'
            }
            
            for header, key in cors_headers.items():
                if header in response.headers:
                    cors_info['enabled'] = True
                    cors_info[key] = response.headers[header].split(',')
            
            # Check for overly permissive CORS
            if cors_info.get('allow_origins') and '*' in cors_info['allow_origins']:
                cors_info['issues'].append('Overly permissive CORS policy allows all origins')
        
        except Exception as e:
            cors_info['issues'].append(f'CORS analysis failed: {str(e)}')
        
        return cors_info
    
    def _check_rate_limiting(self, base_url: str) -> Dict[str, Any]:
        """Check if rate limiting is implemented."""
        rate_limit_info = {
            'enabled': False,
            'limit_headers': [],
            'issues': []
        }
        
        try:
            # Make multiple rapid requests to test rate limiting
            responses = []
            for i in range(5):
                response = self.session.get(base_url, timeout=self.request_timeout)
                responses.append(response)
                
                # Check for rate limit headers
                rate_headers = ['X-RateLimit-Limit', 'X-RateLimit-Remaining', 'Retry-After']
                for header in rate_headers:
                    if header in response.headers:
                        rate_limit_info['enabled'] = True
                        if header not in rate_limit_info['limit_headers']:
                            rate_limit_info['limit_headers'].append(header)
                
                # Check if we hit rate limit
                if response.status_code == 429:
                    rate_limit_info['enabled'] = True
                    break
            
            if not rate_limit_info['enabled']:
                rate_limit_info['issues'].append('No rate limiting detected - API may be vulnerable to abuse')
        
        except Exception as e:
            rate_limit_info['issues'].append(f'Rate limiting check failed: {str(e)}')
        
        return rate_limit_info
    
    def generate_privacy_recommendations(self, scan_results: Dict[str, Any]) -> List[str]:
        """
        Generate comprehensive privacy compliance recommendations based on scan results.
        
        Args:
            scan_results: Complete API scan results dictionary
            
        Returns:
            List of actionable privacy recommendations
        """
        recommendations = []
        
        # PII exposure recommendations
        pii_exposures = scan_results.get('pii_exposures', [])
        if pii_exposures:
            critical_pii = [p for p in pii_exposures if p.get('severity') == 'Critical']
            if critical_pii:
                recommendations.append(
                    f"Critical: {len(critical_pii)} endpoints expose sensitive PII (SSN, credit cards, passwords). "
                    "Implement immediate data masking and access controls."
                )
            
            high_pii = [p for p in pii_exposures if p.get('severity') == 'High']
            if high_pii:
                recommendations.append(
                    f"High Priority: {len(high_pii)} endpoints expose personal data (emails, phones). "
                    "Review data minimization practices and implement field-level encryption."
                )
        
        # Authentication and authorization recommendations
        auth_issues = scan_results.get('auth_issues', [])
        if auth_issues:
            recommendations.append(
                f"Security Gap: {len(auth_issues)} authentication issues detected. "
                "Implement proper OAuth 2.0 or JWT-based authentication for all sensitive endpoints."
            )
        
        # SSL/TLS recommendations
        ssl_info = scan_results.get('ssl_info', {})
        if not ssl_info.get('enabled'):
            recommendations.append(
                "Critical Security Issue: API does not use HTTPS encryption. "
                "Implement SSL/TLS encryption immediately to protect data in transit."
            )
        elif ssl_info.get('issues'):
            recommendations.append(
                "SSL Configuration Issues: Invalid or misconfigured SSL certificate detected. "
                "Update SSL certificate and verify proper HTTPS implementation."
            )
        
        # Rate limiting recommendations
        rate_limiting = scan_results.get('rate_limiting', {})
        if not rate_limiting.get('enabled'):
            recommendations.append(
                "API Security: No rate limiting detected. Implement rate limiting to prevent "
                "API abuse and ensure service availability."
            )
        
        # CORS policy recommendations
        cors_analysis = scan_results.get('cors_analysis', {})
        if cors_analysis.get('issues'):
            recommendations.append(
                "CORS Security: Overly permissive CORS policy detected. "
                "Restrict allowed origins to only trusted domains."
            )
        
        # Vulnerability recommendations
        vulnerabilities = scan_results.get('vulnerabilities', [])
        if vulnerabilities:
            critical_vulns = [v for v in vulnerabilities if v.get('severity') == 'Critical']
            if critical_vulns:
                recommendations.append(
                    f"Critical Vulnerabilities: {len(critical_vulns)} critical security vulnerabilities found. "
                    "Implement input validation, parameterized queries, and security testing."
                )
        
        # General API security recommendations
        findings = scan_results.get('findings', [])
        security_headers = [f for f in findings if f.get('type') == 'security_header']
        if security_headers:
            recommendations.append(
                f"Security Headers: {len(security_headers)} missing security headers detected. "
                "Implement HSTS, CSP, X-Frame-Options, and other security headers."
            )
        
        # GDPR compliance recommendations
        if pii_exposures or auth_issues:
            recommendations.append(
                "GDPR Compliance: Implement data protection measures including encryption, "
                "access logging, data retention policies, and user consent management."
            )
        
        # API documentation and monitoring
        recommendations.append(
            "Best Practices: Implement API documentation, request/response logging, "
            "monitoring, and regular security assessments to maintain compliance."
        )
        
        if len(recommendations) == 1:  # Only the best practices recommendation
            recommendations.insert(0, 
                "Good Security Posture: Basic API security appears adequate. "
                "Continue regular security assessments and monitoring."
            )
        
        return recommendations
    
    def cancel_scan(self):
        """Cancel the current scan if running."""
        self.is_running = False