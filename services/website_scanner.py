"""
Website Scanner for DataGuardian Pro.
This scanner detects PII, cookies, trackers, and vulnerabilities in websites.
"""
import re
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import random
from typing import Dict, List, Any, Optional, Callable, Tuple
import tldextract
import trafilatura
from datetime import datetime
import json

class WebsiteScanner:
    """
    A scanner that detects PII and privacy issues in websites.
    """
    
    def __init__(self, languages: List[str] = None, region: str = "Netherlands", 
                 rate_limit: int = 10, max_pages: int = 20, 
                 cookies_enabled: bool = True, js_enabled: bool = True,
                 user_agent: str = None):
        """
        Initialize the website scanner.
        
        Args:
            languages: List of languages used on the website
            region: The region for which GDPR rules are applied
            rate_limit: Maximum requests per minute
            max_pages: Maximum number of pages to scan
            cookies_enabled: Whether to collect and analyze cookies
            js_enabled: Whether to analyze JavaScript
            user_agent: Custom user agent string
        """
        self.languages = languages or ["English"]
        self.region = region
        self.rate_limit = max(1, min(rate_limit, 60))  # 1-60 requests per minute
        self.max_pages = max(1, min(max_pages, 100))  # 1-100 pages
        self.cookies_enabled = cookies_enabled
        self.js_enabled = js_enabled
        
        # Set user agent
        self.user_agent = user_agent or (
            "Mozilla/5.0 (compatible; DataGuardianPro/1.0; "
            "+https://dataguardian.pro/bot)"
        )
        
        # Rate limiting delay
        self.request_delay = 60.0 / self.rate_limit
        
        # Tracking
        self.visited_urls = set()
        self.progress_callback = None
        self.current_progress = 0
        self.total_pages = 0
        
        # PII detection patterns
        self.pii_patterns = {
            'Email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'Phone': r'\b(\+\d{1,3}[\s.-])?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',
            'Credit Card': r'\b(?:\d{4}[- ]?){3}\d{4}\b',
            'BSN': r'\b\d{9}\b',
            'IP Address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
            'Address': r'\b\d+\s+[A-Za-z]+\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Highway|Hwy|Parkway|Pkwy)\b',
            'PostalCode': r'\b\d{5}(?:[-\s]\d{4})?\b'
        }
        
        # Vulnerability patterns
        self.vulnerability_patterns = {
            'XSS': [
                r'document\.write\s*\(.*?\)',
                r'\.innerHTML\s*=',
                r'eval\s*\(',
                r'setTimeout\s*\(\s*[\'"`]',
                r'document\.cookie'
            ],
            'CSRF': [
                r'<form[^>]*>(?:(?!csrf).)*?</form>',
                r'<!-- CSRF TOKEN MISSING -->',
                r'<!-- MISSING CSRF PROTECTION -->'
            ],
            'Insecure Cookies': [
                r'document\.cookie\s*=\s*[\'"`][^;]*?[\'"`]',
                r'setCookie\([^,]+,[^,]+,\s*\{[^}]*?secure:\s*false[^}]*?\}'
            ],
            'Sensitive URL': [
                r'(password|login|admin|token|key|credential)=[^&]+',
                r'secret=[^&]+'
            ]
        }
    
    def set_progress_callback(self, callback_function: Callable[[int, int, str], None]) -> None:
        """
        Set a callback function to report progress during long-running scans.
        
        Args:
            callback_function: Function that takes (current_progress, total_pages, current_url)
        """
        self.progress_callback = callback_function
    
    def scan_website(self, url: str, include_text: bool = True, include_images: bool = True,
                    include_forms: bool = True, include_metadata: bool = True,
                    detect_pii: bool = True, detect_cookies: bool = True,
                    detect_trackers: bool = True, analyze_privacy_policy: bool = True) -> Dict[str, Any]:
        """
        Scan a website for PII and privacy issues.
        
        Args:
            url: Base URL of the website to scan
            include_text: Whether to extract and scan text content
            include_images: Whether to analyze images
            include_forms: Whether to scan form fields
            include_metadata: Whether to extract metadata
            detect_pii: Whether to detect PII in content
            detect_cookies: Whether to analyze cookies
            detect_trackers: Whether to detect trackers
            analyze_privacy_policy: Whether to analyze privacy policy
            
        Returns:
            Dictionary containing scan results
        """
        # Normalize URL
        if not url.startswith('http'):
            url = 'https://' + url
        
        # Extract domain
        domain_info = tldextract.extract(url)
        domain = f"{domain_info.domain}.{domain_info.suffix}"
        
        # Initialize results
        results = {
            'url': url,
            'domain': domain,
            'scan_timestamp': datetime.now().isoformat(),
            'scan_type': 'website_scan',
            'region': self.region,
            'findings': [],
            'pii_types': {},
            'risk_levels': {'High': 0, 'Medium': 0, 'Low': 0},
            'total_pii_found': 0,
            'high_risk_count': 0,
            'medium_risk_count': 0,
            'low_risk_count': 0,
            'pages_scanned': 0,
            'total_findings': 0
        }
        
        # Reset tracking
        self.visited_urls = set()
        self.current_progress = 0
        self.total_pages = min(self.max_pages, 20)  # Start with 20, adjust as we discover pages
        
        try:
            # Get site metadata
            site_metadata = self._get_site_metadata(url)
            results['site_metadata'] = site_metadata
            
            # First scan the main URL
            self._scan_url(url, results, include_text, include_images, include_forms, include_metadata,
                          detect_pii, detect_cookies, detect_trackers)
            
            # If privacy policy URL is detected and analysis is requested
            if analyze_privacy_policy and 'privacy_policy_url' in site_metadata:
                privacy_url = site_metadata['privacy_policy_url']
                privacy_findings = self._analyze_privacy_policy(privacy_url)
                results['privacy_policy_analysis'] = privacy_findings
            
            # Update final counts
            results['pages_scanned'] = len(self.visited_urls)
            results['total_findings'] = len(results['findings'])
            
            # Log completion
            if self.progress_callback:
                self.progress_callback(self.total_pages, self.total_pages, "Scan complete")
            
        except Exception as e:
            # Add error information
            results['error'] = str(e)
            results['error_type'] = type(e).__name__
        
        return results
    
    def _scan_url(self, url: str, results: Dict[str, Any], include_text: bool, include_images: bool,
                 include_forms: bool, include_metadata: bool, detect_pii: bool, 
                 detect_cookies: bool, detect_trackers: bool) -> None:
        """
        Scan a single URL and update results.
        
        Args:
            url: URL to scan
            results: Results dictionary to update
            include_text, include_images, etc.: Feature flags
        """
        # Skip if already visited or max pages reached
        if url in self.visited_urls or len(self.visited_urls) >= self.max_pages:
            return
        
        # Mark as visited
        self.visited_urls.add(url)
        
        # Rate limiting
        time.sleep(self.request_delay)
        
        # Update progress
        self.current_progress = len(self.visited_urls)
        if self.progress_callback:
            self.progress_callback(self.current_progress, self.total_pages, url)
        
        try:
            # Get page content
            headers = {'User-Agent': self.user_agent}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Extract text using trafilatura for better content extraction
            text_content = ""
            html_content = response.text
            
            if include_text:
                try:
                    text_content = trafilatura.extract(html_content)
                    
                    # Fallback to BeautifulSoup if trafilatura fails
                    if not text_content:
                        soup = BeautifulSoup(html_content, 'html.parser')
                        text_content = soup.get_text(separator=' ', strip=True)
                    
                    # Scan text for PII if requested
                    if detect_pii and text_content:
                        pii_findings = self._scan_text_for_pii(text_content, url)
                        results['findings'].extend(pii_findings)
                        
                        # Update PII types and risk levels
                        for finding in pii_findings:
                            pii_type = finding['type']
                            risk_level = finding['risk_level']
                            
                            # Update PII types count
                            if pii_type not in results['pii_types']:
                                results['pii_types'][pii_type] = 0
                            results['pii_types'][pii_type] += 1
                            
                            # Update risk level counts
                            results['risk_levels'][risk_level] += 1
                            
                            # Update total PII count
                            results['total_pii_found'] += 1
                            
                            # Update risk counts
                            if risk_level == 'High':
                                results['high_risk_count'] += 1
                            elif risk_level == 'Medium':
                                results['medium_risk_count'] += 1
                            elif risk_level == 'Low':
                                results['low_risk_count'] += 1
                
                except Exception as e:
                    results.setdefault('errors', []).append({
                        'type': 'text_extraction',
                        'url': url,
                        'message': str(e)
                    })
            
            # Create soup for further analysis
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Scan forms if requested
            if include_forms:
                form_findings = self._scan_forms(soup, url)
                results['findings'].extend(form_findings)
                
                # Update counts
                for finding in form_findings:
                    risk_level = finding['risk_level']
                    results['risk_levels'][risk_level] += 1
                    results['total_pii_found'] += 1
                    
                    if risk_level == 'High':
                        results['high_risk_count'] += 1
                    elif risk_level == 'Medium':
                        results['medium_risk_count'] += 1
                    elif risk_level == 'Low':
                        results['low_risk_count'] += 1
            
            # Detect JavaScript vulnerabilities
            if self.js_enabled:
                js_findings = self._scan_javascript(soup, url)
                results['findings'].extend(js_findings)
                
                # Update counts
                for finding in js_findings:
                    risk_level = finding['risk_level']
                    results['risk_levels'][risk_level] += 1
                    
                    if risk_level == 'High':
                        results['high_risk_count'] += 1
                    elif risk_level == 'Medium':
                        results['medium_risk_count'] += 1
                    elif risk_level == 'Low':
                        results['low_risk_count'] += 1
            
            # Detect cookies if requested
            if detect_cookies and self.cookies_enabled:
                cookie_findings = self._analyze_cookies(response.cookies, url)
                results['findings'].extend(cookie_findings)
                
                # Update counts
                for finding in cookie_findings:
                    risk_level = finding['risk_level']
                    results['risk_levels'][risk_level] += 1
                    
                    if risk_level == 'High':
                        results['high_risk_count'] += 1
                    elif risk_level == 'Medium':
                        results['medium_risk_count'] += 1
                    elif risk_level == 'Low':
                        results['low_risk_count'] += 1
            
            # Detect trackers if requested
            if detect_trackers:
                tracker_findings = self._detect_trackers(soup, url)
                results['findings'].extend(tracker_findings)
                
                # Update counts
                for finding in tracker_findings:
                    risk_level = finding['risk_level']
                    results['risk_levels'][risk_level] += 1
                    
                    if risk_level == 'High':
                        results['high_risk_count'] += 1
                    elif risk_level == 'Medium':
                        results['medium_risk_count'] += 1
                    elif risk_level == 'Low':
                        results['low_risk_count'] += 1
            
            # Extract links for further scanning (limited to same domain)
            if len(self.visited_urls) < self.max_pages:
                links = soup.find_all('a', href=True)
                
                # Extract domain of current URL
                base_domain = tldextract.extract(url).registered_domain
                
                for link in links:
                    href = link['href']
                    
                    # Normalize URL
                    if href.startswith('/'):
                        # Relative URL
                        next_url = urllib.parse.urljoin(url, href)
                    elif href.startswith('http'):
                        # Absolute URL
                        next_url = href
                    else:
                        # Anchor or other non-URL
                        continue
                    
                    # Check if URL is in the same domain
                    link_domain = tldextract.extract(next_url).registered_domain
                    if link_domain == base_domain and next_url not in self.visited_urls:
                        # Recursively scan URL
                        self._scan_url(next_url, results, include_text, include_images,
                                      include_forms, include_metadata, detect_pii,
                                      detect_cookies, detect_trackers)
        
        except requests.RequestException as e:
            # Add error information
            results.setdefault('errors', []).append({
                'type': 'request',
                'url': url,
                'message': str(e)
            })
    
    def _get_site_metadata(self, url: str) -> Dict[str, Any]:
        """
        Get metadata about the site.
        
        Args:
            url: Base URL of the website
            
        Returns:
            Dictionary with site metadata
        """
        metadata = {
            'url': url,
            'scan_time': datetime.now().isoformat()
        }
        
        try:
            # Get response
            headers = {'User-Agent': self.user_agent}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get title
            title = soup.title.string if soup.title else 'No title'
            metadata['title'] = title.strip() if title else 'No title'
            
            # Get meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                metadata['description'] = meta_desc['content'].strip()
            
            # Get meta keywords
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords and meta_keywords.get('content'):
                metadata['keywords'] = meta_keywords['content'].strip().split(',')
            
            # Check for privacy policy link
            privacy_links = soup.find_all('a', string=re.compile(r'privacy|Privacy|PRIVACY'))
            if privacy_links:
                href = privacy_links[0].get('href')
                if href:
                    if href.startswith('/'):
                        metadata['privacy_policy_url'] = urllib.parse.urljoin(url, href)
                    elif href.startswith('http'):
                        metadata['privacy_policy_url'] = href
                    else:
                        metadata['privacy_policy_url'] = urllib.parse.urljoin(url, href)
            
            # Check for cookie policy link
            cookie_links = soup.find_all('a', string=re.compile(r'cookie|Cookie|COOKIE'))
            if cookie_links:
                href = cookie_links[0].get('href')
                if href:
                    if href.startswith('/'):
                        metadata['cookie_policy_url'] = urllib.parse.urljoin(url, href)
                    elif href.startswith('http'):
                        metadata['cookie_policy_url'] = href
                    else:
                        metadata['cookie_policy_url'] = urllib.parse.urljoin(url, href)
            
            # Get server header
            if 'Server' in response.headers:
                metadata['server'] = response.headers['Server']
            
            # Check HTTPS
            metadata['https'] = url.startswith('https')
            
            # Check for security headers
            security_headers = {
                'Strict-Transport-Security': False,
                'Content-Security-Policy': False,
                'X-Content-Type-Options': False,
                'X-Frame-Options': False,
                'X-XSS-Protection': False
            }
            
            for header in security_headers:
                security_headers[header] = header in response.headers
            
            metadata['security_headers'] = security_headers
            
        except Exception as e:
            metadata['error'] = str(e)
            metadata['error_type'] = type(e).__name__
        
        return metadata
    
    def _scan_text_for_pii(self, text: str, url: str) -> List[Dict[str, Any]]:
        """
        Scan text content for PII.
        
        Args:
            text: Text content to scan
            url: Original URL for reference
            
        Returns:
            List of PII findings
        """
        findings = []
        
        # Strip text to basic content, joining broken lines
        normalized_text = re.sub(r'\s+', ' ', text).strip()
        
        # Scan for each PII type
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.finditer(pattern, normalized_text)
            
            for match in matches:
                # Determine risk level
                risk_level = self._get_risk_level(pii_type)
                
                # Create finding
                finding = {
                    'type': pii_type,
                    'value': self._redact_pii(match.group(), pii_type),
                    'location': f'URL: {url}',
                    'risk_level': risk_level,
                    'reason': self._get_reason(pii_type, risk_level)
                }
                
                findings.append(finding)
        
        return findings
    
    def _scan_forms(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """
        Scan forms for PII collection fields.
        
        Args:
            soup: BeautifulSoup instance for the page
            url: Original URL for reference
            
        Returns:
            List of form field findings
        """
        findings = []
        
        # Find all forms
        forms = soup.find_all('form')
        
        for form_idx, form in enumerate(forms, 1):
            form_action = form.get('action', 'No action')
            form_method = form.get('method', 'get').lower()
            
            # Check for sensitive form with GET method
            if form_method == 'get':
                # Check if it contains password field
                has_password = bool(form.find('input', {'type': 'password'}))
                if has_password:
                    findings.append({
                        'type': 'Vulnerability:InsecureFormMethod',
                        'value': 'Form uses GET method for sensitive data',
                        'location': f'URL: {url}, Form #{form_idx}',
                        'risk_level': 'High',
                        'reason': 'Sensitive form data should not be sent via GET method, which could expose data in URLs and logs'
                    })
            
            # Check for CSRF protection
            has_csrf_token = bool(form.find('input', {'name': re.compile(r'csrf|token', re.I)}))
            if not has_csrf_token and form_method == 'post':
                findings.append({
                    'type': 'Vulnerability:CSRF',
                    'value': 'Form lacks CSRF protection',
                    'location': f'URL: {url}, Form #{form_idx}',
                    'risk_level': 'Medium',
                    'reason': 'Forms without CSRF tokens are vulnerable to cross-site request forgery attacks'
                })
            
            # Check for PII collection fields
            input_fields = form.find_all('input')
            for field in input_fields:
                field_type = field.get('type', 'text').lower()
                field_name = field.get('name', '').lower()
                field_id = field.get('id', '').lower()
                
                # Check for PII collection without SSL
                if not url.startswith('https'):
                    if field_type in ['text', 'email', 'tel'] or any(pii in field_name or pii in field_id for pii in 
                                                                  ['email', 'phone', 'mobile', 'address', 'postcode', 'zip']):
                        findings.append({
                            'type': 'Vulnerability:InsecureFormTransmission',
                            'value': f'Collecting {field_type} data without HTTPS',
                            'location': f'URL: {url}, Form #{form_idx}, Field {field_name or field_id}',
                            'risk_level': 'High',
                            'reason': 'Transmitting personal data without encryption violates GDPR security requirements'
                        })
                
                # Check for specific PII fields
                if field_type == 'text' or field_type == '':
                    for pii_type, keywords in {
                        'Email': ['email', 'e-mail', 'mail'],
                        'Phone': ['phone', 'tel', 'mobile', 'cell'],
                        'Address': ['address', 'street', 'city', 'town'],
                        'PostalCode': ['zip', 'postal', 'postcode'],
                        'Name': ['name', 'firstname', 'lastname', 'fullname'],
                        'BSN': ['bsn', 'ssn', 'social', 'national']
                    }.items():
                        if any(kw in field_name or kw in field_id for kw in keywords):
                            risk_level = self._get_risk_level(pii_type)
                            findings.append({
                                'type': f'Form Collection:{pii_type}',
                                'value': f'Form collecting {pii_type}',
                                'location': f'URL: {url}, Form #{form_idx}, Field {field_name or field_id}',
                                'risk_level': risk_level,
                                'reason': f'Form is collecting {pii_type} data which is subject to GDPR regulations'
                            })
        
        return findings
    
    def _scan_javascript(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """
        Scan JavaScript code for vulnerabilities.
        
        Args:
            soup: BeautifulSoup instance for the page
            url: Original URL for reference
            
        Returns:
            List of JavaScript vulnerability findings
        """
        findings = []
        
        # Find all script tags
        scripts = soup.find_all('script')
        
        for script_idx, script in enumerate(scripts, 1):
            # Skip external scripts
            if script.get('src'):
                continue
            
            # Get script content
            script_content = script.string
            if not script_content:
                continue
            
            # Check for vulnerabilities
            for vuln_type, patterns in self.vulnerability_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, script_content)
                    
                    for match in matches:
                        risk_level = 'High' if vuln_type in ['XSS', 'Vulnerability:Xss'] else 'Medium'
                        
                        # Create finding
                        finding = {
                            'type': f'Vulnerability:{vuln_type}',
                            'value': match.group()[:100] + ('...' if len(match.group()) > 100 else ''),
                            'location': f'URL: {url}, Script #{script_idx}',
                            'risk_level': risk_level,
                            'reason': self._get_vulnerability_reason(vuln_type)
                        }
                        
                        findings.append(finding)
        
        return findings
    
    def _analyze_cookies(self, cookies, url: str) -> List[Dict[str, Any]]:
        """
        Analyze cookies for privacy issues.
        
        Args:
            cookies: Cookie jar from requests
            url: Original URL for reference
            
        Returns:
            List of cookie-related findings
        """
        findings = []
        
        for cookie in cookies:
            # Check for secure flag on HTTPS site
            if url.startswith('https') and not cookie.secure:
                findings.append({
                    'type': 'Vulnerability:InsecureCookie',
                    'value': f'Cookie {cookie.name} missing Secure flag',
                    'location': f'URL: {url}',
                    'risk_level': 'Medium',
                    'reason': 'Cookies on HTTPS sites should have the Secure flag to prevent transmission over HTTP'
                })
            
            # Check for HttpOnly flag
            if not cookie.has_nonstandard_attr('HttpOnly'):
                findings.append({
                    'type': 'Vulnerability:InsecureCookie',
                    'value': f'Cookie {cookie.name} missing HttpOnly flag',
                    'location': f'URL: {url}',
                    'risk_level': 'Medium',
                    'reason': 'Cookies should have the HttpOnly flag to prevent access from JavaScript'
                })
            
            # Check for SameSite attribute
            if not cookie.has_nonstandard_attr('SameSite'):
                findings.append({
                    'type': 'Vulnerability:InsecureCookie',
                    'value': f'Cookie {cookie.name} missing SameSite attribute',
                    'location': f'URL: {url}',
                    'risk_level': 'Low',
                    'reason': 'Cookies should have SameSite attribute to prevent CSRF attacks'
                })
            
            # Check for suspicious cookie names
            suspicious_names = ['auth', 'session', 'token', 'id', 'user', 'key', 'pass']
            if any(sus in cookie.name.lower() for sus in suspicious_names):
                findings.append({
                    'type': 'PotentialPII:Cookie',
                    'value': f'Potentially sensitive cookie: {cookie.name}',
                    'location': f'URL: {url}',
                    'risk_level': 'Medium',
                    'reason': 'Cookie may contain PII or authentication data'
                })
        
        return findings
    
    def _detect_trackers(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """
        Detect tracking scripts and pixels.
        
        Args:
            soup: BeautifulSoup instance for the page
            url: Original URL for reference
            
        Returns:
            List of tracker findings
        """
        findings = []
        
        # Common tracker domains
        trackers = {
            'Google Analytics': ['google-analytics.com', 'analytics.google.com', 'www.google-analytics.com'],
            'Google Tag Manager': ['googletagmanager.com', 'www.googletagmanager.com'],
            'Facebook Pixel': ['connect.facebook.net', 'facebook.com/tr'],
            'Twitter': ['static.ads-twitter.com', 'analytics.twitter.com'],
            'LinkedIn': ['snap.licdn.com', 'px.ads.linkedin.com'],
            'Hotjar': ['static.hotjar.com', 'script.hotjar.com'],
            'Adobe Analytics': ['assets.adobedtm.com', 'omniture.com'],
            'HubSpot': ['js.hs-scripts.com', 'track.hubspot.com'],
            'Matomo/Piwik': ['matomo.php', 'piwik.php', 'piwik.js'],
            'Mixpanel': ['api.mixpanel.com', 'cdn.mxpnl.com']
        }
        
        # Check script sources
        scripts = soup.find_all('script', src=True)
        for script in scripts:
            src = script['src']
            for tracker_name, domains in trackers.items():
                if any(domain in src for domain in domains):
                    findings.append({
                        'type': 'Tracker',
                        'value': f'{tracker_name} detected',
                        'location': f'URL: {url}, Script: {src}',
                        'risk_level': 'Medium',
                        'reason': 'Tracking technologies require proper notice and potentially consent under GDPR'
                    })
        
        # Check img tags for tracking pixels
        imgs = soup.find_all('img')
        for img in imgs:
            src = img.get('src', '')
            for tracker_name, domains in trackers.items():
                if any(domain in src for domain in domains):
                    findings.append({
                        'type': 'Tracker',
                        'value': f'{tracker_name} pixel detected',
                        'location': f'URL: {url}, Image: {src}',
                        'risk_level': 'Medium',
                        'reason': 'Tracking pixels require proper notice and potentially consent under GDPR'
                    })
        
        # Check for iframes (potentially containing trackers)
        iframes = soup.find_all('iframe')
        for iframe in iframes:
            src = iframe.get('src', '')
            for tracker_name, domains in trackers.items():
                if any(domain in src for domain in domains):
                    findings.append({
                        'type': 'Tracker',
                        'value': f'{tracker_name} iframe detected',
                        'location': f'URL: {url}, iFrame: {src}',
                        'risk_level': 'Medium',
                        'reason': 'Embedded frames with trackers require proper notice and potentially consent under GDPR'
                    })
        
        return findings
    
    def _analyze_privacy_policy(self, url: str) -> Dict[str, Any]:
        """
        Analyze privacy policy for GDPR compliance.
        
        Args:
            url: Privacy policy URL
            
        Returns:
            Dictionary with privacy policy analysis
        """
        try:
            headers = {'User-Agent': self.user_agent}
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Extract text using trafilatura for better content extraction
            text_content = trafilatura.extract(response.text)
            
            # Fallback to BeautifulSoup if trafilatura fails
            if not text_content:
                soup = BeautifulSoup(response.text, 'html.parser')
                text_content = soup.get_text(separator=' ', strip=True)
            
            # Define required GDPR elements
            gdpr_elements = {
                'data_controller': ['data controller', 'controller of your data', 'responsible for your data'],
                'contact_info': ['contact us', 'contact information', 'reach us at'],
                'dpo_contact': ['data protection officer', 'DPO', 'privacy officer'],
                'purposes': ['purpose', 'why we collect', 'how we use'],
                'legal_basis': ['legal basis', 'lawful basis', 'grounds for processing'],
                'recipients': ['recipient', 'third part', 'share your data', 'disclose your data'],
                'retention': ['retention', 'how long', 'store your data', 'keep your data'],
                'rights': ['your rights', 'right to access', 'right to erasure', 'right to object'],
                'complaint': ['complaint', 'supervisory authority', 'data protection authority'],
                'automated_decision': ['automated decision', 'profiling', 'automatic processing'],
                'international_transfers': ['transfer', 'outside the EU', 'outside the EEA']
            }
            
            # Check for each GDPR element
            found_elements = {}
            
            for element, keywords in gdpr_elements.items():
                found = False
                for keyword in keywords:
                    if re.search(r'\b' + re.escape(keyword) + r'\b', text_content, re.IGNORECASE):
                        found = True
                        break
                found_elements[element] = found
            
            # Calculate compliance score
            total_elements = len(gdpr_elements)
            found_count = sum(1 for found in found_elements.values() if found)
            compliance_score = int((found_count / total_elements) * 100)
            
            # Determine compliance level
            if compliance_score >= 90:
                compliance_level = "Excellent"
            elif compliance_score >= 75:
                compliance_level = "Good"
            elif compliance_score >= 50:
                compliance_level = "Moderate"
            elif compliance_score >= 30:
                compliance_level = "Poor"
            else:
                compliance_level = "Critical"
            
            return {
                'url': url,
                'elements_found': found_elements,
                'compliance_score': compliance_score,
                'compliance_level': compliance_level,
                'total_words': len(text_content.split()),
                'missing_elements': [element for element, found in found_elements.items() if not found]
            }
        
        except Exception as e:
            return {
                'url': url,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def _get_risk_level(self, pii_type: str) -> str:
        """
        Determine risk level based on PII type.
        
        Args:
            pii_type: The type of PII
            
        Returns:
            Risk level (High, Medium, Low)
        """
        # High risk PII types
        high_risk = ['Credit Card', 'BSN', 'Passport']
        
        # Medium risk PII types
        medium_risk = ['Email', 'Phone', 'Address', 'IP Address']
        
        # Determine risk level
        if pii_type in high_risk or pii_type.startswith('Vulnerability:'):
            return 'High'
        elif pii_type in medium_risk or pii_type.startswith('PotentialPII:'):
            return 'Medium'
        else:
            return 'Low'
    
    def _redact_pii(self, value: str, pii_type: str) -> str:
        """
        Redact PII data for safe storage.
        
        Args:
            value: The PII value
            pii_type: The type of PII
            
        Returns:
            Redacted PII value
        """
        if pii_type == 'Email':
            parts = value.split('@')
            if len(parts) == 2:
                username = parts[0]
                domain = parts[1]
                if len(username) > 2:
                    redacted_username = username[0] + '*' * (len(username) - 2) + username[-1]
                else:
                    redacted_username = '*' * len(username)
                return f"{redacted_username}@{domain}"
        elif pii_type == 'Phone':
            if len(value) > 4:
                return '*' * (len(value) - 4) + value[-4:]
        elif pii_type == 'Credit Card':
            if len(value) > 4:
                return '*' * (len(value) - 4) + value[-4:]
        elif pii_type == 'BSN':
            if len(value) > 2:
                return '*' * (len(value) - 2) + value[-2:]
        
        # For other types or if redaction logic fails, use generic redaction
        if len(value) > 4:
            return value[:2] + '*' * (len(value) - 4) + value[-2:]
        else:
            return '*' * len(value)
    
    def _get_reason(self, pii_type: str, risk_level: str) -> str:
        """
        Get a reason explanation for the PII finding.
        
        Args:
            pii_type: The type of PII found
            risk_level: The risk level (Low, Medium, High)
            
        Returns:
            A string explaining why this PII is a concern
        """
        reasons = {
            'Email': "Email addresses are personal data under GDPR and require proper handling",
            'Phone': "Phone numbers are personal data under GDPR and can be used to contact individuals directly",
            'Credit Card': "Credit card information is financial data requiring special protection under GDPR",
            'BSN': "BSN (Dutch Social Security Number) is sensitive personal data with strict GDPR requirements",
            'IP Address': "IP addresses are considered personal data under GDPR as they can identify individuals",
            'Address': "Physical addresses are personal data under GDPR and can locate individuals",
            'PostalCode': "Postal codes combined with other data can identify individuals and are subject to GDPR",
            'Name': "Names are basic personal identifiers protected under GDPR"
        }
        
        # Return specific reason if available, otherwise generic by risk level
        if pii_type in reasons:
            return reasons[pii_type]
        elif pii_type.startswith('Vulnerability:'):
            return self._get_vulnerability_reason(pii_type.split(':')[1])
        elif risk_level == 'High':
            return "High-risk personal data requiring special protection under GDPR"
        elif risk_level == 'Medium':
            return "Medium-risk personal data subject to GDPR regulations"
        else:
            return "Personal data with potential privacy implications under GDPR"
    
    def _get_vulnerability_reason(self, vuln_type: str) -> str:
        """
        Get a reason explanation for a vulnerability finding.
        
        Args:
            vuln_type: The type of vulnerability
            
        Returns:
            A string explaining the vulnerability concern
        """
        reasons = {
            'XSS': "Cross-site scripting vulnerabilities can lead to theft of sensitive data and session hijacking",
            'Xss': "Cross-site scripting vulnerabilities can lead to theft of sensitive data and session hijacking",
            'CSRF': "Cross-site request forgery vulnerabilities can force users to perform unwanted actions",
            'Csrf': "Cross-site request forgery vulnerabilities can force users to perform unwanted actions",
            'InsecureCookie': "Insecure cookies can expose session data and lead to session hijacking",
            'Insecure Cookies': "Insecure cookies can expose session data and lead to session hijacking",
            'InsecureFormMethod': "Insecure form methods can expose sensitive data in URLs and server logs",
            'InsecureFormTransmission': "Transmitting personal data without encryption violates GDPR security requirements",
            'SensitiveURL': "Sensitive data in URLs can be exposed in browser history, server logs, and referrer headers"
        }
        
        return reasons.get(vuln_type, "Security vulnerability that may compromise personal data or system integrity")