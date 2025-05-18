"""
Website Scanner module for comprehensive privacy compliance scanning of websites.

This module simulates a real visitor journey, analyzing pageviews and actions
to provide detailed reports on data collection, tracking pixels, cookies,
and consent choices across a website.
"""

import os
import re
import json
import time
import logging
import requests
import fnmatch
import hashlib
import tldextract
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from trafilatura import fetch_url, extract
import whois
import dns.resolver

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebsiteScanner:
    """
    A comprehensive scanner that analyzes websites for privacy compliance issues,
    tracking technologies, cookies, and consent mechanisms.
    """
    
    def __init__(self, max_pages=100, max_depth=3, crawl_delay=1, 
                 save_screenshots=False, simulate_user=True, check_ssl=True,
                 check_dns=True, region="Netherlands"):
        """
        Initialize the website scanner.
        
        Args:
            max_pages: Maximum number of pages to scan (default: 100)
            max_depth: Maximum depth of crawling (default: 3)
            crawl_delay: Delay between requests in seconds (default: 1)
            save_screenshots: Whether to save screenshots of pages (default: False)
            simulate_user: Whether to simulate user interactions (default: True)
            check_ssl: Whether to check SSL/TLS configuration (default: True)
            check_dns: Whether to check DNS records (default: True)
            region: Region for applying GDPR rules (default: "Netherlands")
        """
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.crawl_delay = crawl_delay
        self.save_screenshots = save_screenshots
        self.simulate_user = simulate_user
        self.check_ssl = check_ssl
        self.check_dns = check_dns
        self.region = region
        
        # Session with headers that mimic a real browser
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',  # Do Not Track header
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Initialize tracking databases
        self._load_tracking_databases()
        
        # Known consent management platforms
        self.consent_platforms = [
            {'name': 'OneTrust', 'patterns': ['otSDKStub', 'OneTrust', 'onetrust', 'optanon']},
            {'name': 'TrustArc', 'patterns': ['truste', 'TrustArc', 'trustarc.com']},
            {'name': 'Cookiebot', 'patterns': ['cookiebot', 'Cookiebot', 'CookieDeclaration']},
            {'name': 'CookiePro', 'patterns': ['cookiepro', 'CookiePro']},
            {'name': 'Osano', 'patterns': ['osano', 'Osano', 'osano.com']},
            {'name': 'Quantcast Choice', 'patterns': ['quantcast', 'Quantcast', 'quantcast.mgr.consensu.org']},
            {'name': 'CivicUK', 'patterns': ['civicuk', 'CivicUK', 'civic-cookie-control']},
            {'name': 'CookieYes', 'patterns': ['cookieyes', 'CookieYes']},
            {'name': 'GDPR Cookie Consent', 'patterns': ['gdpr-cookie-consent', 'gdpr_cookie_consent', 'GDPRCookieConsent']},
            {'name': 'Didomi', 'patterns': ['didomi', 'Didomi']},
            {'name': 'Termly', 'patterns': ['termly', 'Termly']},
            {'name': 'Usercentrics', 'patterns': ['usercentrics', 'Usercentrics']},
            {'name': 'iubenda', 'patterns': ['iubenda', 'Iubenda']},
            {'name': 'Complianz', 'patterns': ['complianz', 'Complianz']},
            {'name': 'CookieHub', 'patterns': ['cookiehub', 'CookieHub']},
            {'name': 'Consent Manager', 'patterns': ['consent-manager', 'ConsentManager']},
            {'name': 'Seers CMP', 'patterns': ['seers', 'Seers', 'seersco.io']},
            {'name': 'Onetrust Banner', 'patterns': ['onetrust-banner', 'OneTrustBanner']}
        ]
        
        # Known cookie categories
        self.cookie_categories = {
            'essential': ['session', 'csrf', 'security', 'auth', 'login', 'cookie_notice', 'gdpr'],
            'functional': ['preferences', 'settings', 'language', 'timezone', 'region', 'country', 'user_settings'],
            'analytics': ['ga', 'google', 'analytics', '_ga', '_gid', '_gat', 'utma', 'utmb', 'utmc', 'utmz', 'utmv', 'utmk'],
            'advertising': ['ad', 'ads', 'advert', 'doubleclick', 'google_ad', 'facebook', 'fb', 'twitter', 'linkedin'],
            'social': ['facebook', 'twitter', 'linkedin', 'pinterest', 'instagram', 'youtube', 'vimeo', 'tumblr']
        }
        
        # Progress tracking
        self.progress_callback = None
        self.is_running = False
    
    def _load_tracking_databases(self):
        """Load known tracking databases from JSON files"""
        
        # Define default trackers if database files don't exist
        self.known_trackers = {
            'Google Analytics': {
                'domains': ['google-analytics.com', 'analytics.google.com'],
                'patterns': ['ga', 'gtag', 'gtm', 'analytics']
            },
            'Google Tag Manager': {
                'domains': ['googletagmanager.com', 'tagmanager.google.com'],
                'patterns': ['gtm', 'tagmanager']
            },
            'Facebook Pixel': {
                'domains': ['facebook.com', 'facebook.net', 'fbcdn.net'],
                'patterns': ['fbq', 'fbevents', 'facebook-jssdk']
            },
            'LinkedIn Insight': {
                'domains': ['linkedin.com', 'licdn.com'],
                'patterns': ['_linkedin_partner_id', 'linkedin_data_partner']
            },
            'Twitter Pixel': {
                'domains': ['twitter.com', 'ads-twitter.com'],
                'patterns': ['twq', 'twitter_pixel']
            },
            'HotJar': {
                'domains': ['hotjar.com', 'hotjar.io'],
                'patterns': ['hjLaunchSurvey', 'hjSiteSettings', 'hjUserAttributes']
            },
            'Mixpanel': {
                'domains': ['mixpanel.com'],
                'patterns': ['mixpanel']
            },
            'Hubspot': {
                'domains': ['hs-scripts.com', 'hubspot.com'],
                'patterns': ['hs-script', 'hubspot']
            },
            'Intercom': {
                'domains': ['intercom.io', 'intercom.com'],
                'patterns': ['intercom']
            },
            'Segment': {
                'domains': ['segment.io', 'segment.com'],
                'patterns': ['segment']
            },
            'Amplitude': {
                'domains': ['amplitude.com'],
                'patterns': ['amplitude']
            },
            'Crazy Egg': {
                'domains': ['crazyegg.com'],
                'patterns': ['crazyegg', 'cetrk']
            },
            'FullStory': {
                'domains': ['fullstory.com'],
                'patterns': ['fullstory', 'FS']
            },
            'Lucky Orange': {
                'domains': ['luckyorange.com', 'luckyorange.net'],
                'patterns': ['LuckyOrange', 'LOTC']
            },
            'Mouseflow': {
                'domains': ['mouseflow.com'],
                'patterns': ['mouseflow', 'MF']
            },
            'Optimizely': {
                'domains': ['optimizely.com'],
                'patterns': ['optimizely']
            },
            'VWO': {
                'domains': ['visualwebsiteoptimizer.com', 'vwo.com'],
                'patterns': ['vwo', '_vis_opt']
            },
            'Matomo': {
                'domains': ['matomo.org', 'matomo.cloud'],
                'patterns': ['matomo', 'piwik']
            },
            'Adobe Analytics': {
                'domains': ['omtrdc.net', 'adobe.com'],
                'patterns': ['s_code', 's.trackingServer', 'sc.omtrdc']
            }
        }
        
        # Try to load trackers from a JSON file if it exists
        try:
            trackers_path = os.path.join('data', 'trackers_database.json')
            if os.path.exists(trackers_path):
                with open(trackers_path, 'r') as f:
                    self.known_trackers = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load trackers database: {str(e)}")
    
    def set_progress_callback(self, callback_function):
        """
        Set a callback function for progress updates during website scanning.
        
        Args:
            callback_function: A function that takes current, total, and current URL
        """
        self.progress_callback = callback_function
    
    def scan_website(self, url: str, follow_links: bool = True) -> Dict[str, Any]:
        """
        Perform a comprehensive scan of a website.
        
        Args:
            url: The URL of the website to scan
            follow_links: Whether to follow links during crawling (default: True)
            
        Returns:
            Dictionary with comprehensive scan results
        """
        # Initialize scan data
        self.start_time = datetime.now()
        self.is_running = True
        
        # Generate a unique scan ID
        scan_id = hashlib.md5(f"{url}:{self.start_time.isoformat()}".encode()).hexdigest()[:10]
        
        # Parse and normalize the starting URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = f"https://{url}"
            parsed_url = urlparse(url)
        
        base_domain = parsed_url.netloc
        base_url = f"{parsed_url.scheme}://{base_domain}"
        
        # Initialize scan data structures
        visited_urls = set()
        pages_data = []
        findings = []
        cookies = {}
        trackers = {}
        all_links = set()
        same_domain_links = set()
        external_links = set()
        
        # Queue for BFS crawling
        queue = [(url, 0)]  # (url, depth)
        
        # Perform domain registration and DNS checks
        domain_info = self._check_domain_info(base_domain)
        
        # Scan the website by following links
        page_count = 0
        
        # Report initial progress
        if self.progress_callback:
            self.progress_callback(0, self.max_pages, url)
        
        while queue and page_count < self.max_pages and self.is_running:
            current_url, depth = queue.pop(0)
            
            # Skip if URL already visited or depth exceeded
            if current_url in visited_urls or depth > self.max_depth:
                continue
            
            visited_urls.add(current_url)
            
            # Scan the current page
            logger.info(f"Scanning page: {current_url}")
            
            try:
                # Respect crawl delay
                time.sleep(self.crawl_delay)
                
                # Fetch the page
                response = self.session.get(current_url, timeout=10)
                
                # Skip non-HTML responses
                if 'text/html' not in response.headers.get('Content-Type', ''):
                    continue
                
                # Analyze the page
                page_data = self._analyze_page(current_url, response.text, depth)
                pages_data.append(page_data)
                
                # Extract and analyze cookies
                page_cookies = self._extract_cookies(response)
                for cookie_name, cookie_data in page_cookies.items():
                    cookies[cookie_name] = cookie_data
                
                # Find trackers
                page_trackers = page_data.get('trackers', [])
                for tracker in page_trackers:
                    tracker_name = tracker.get('name')
                    if tracker_name:
                        trackers[tracker_name] = tracker
                
                # Add findings from the page
                page_findings = page_data.get('findings', [])
                findings.extend(page_findings)
                
                # Update links
                all_links.update(page_data.get('all_links', []))
                same_domain_links.update(page_data.get('same_domain_links', []))
                external_links.update(page_data.get('external_links', []))
                
                # Follow links if enabled
                if follow_links and depth < self.max_depth:
                    for link in page_data.get('same_domain_links', []):
                        if link not in visited_urls:
                            queue.append((link, depth + 1))
                
                # Increment page count
                page_count += 1
                
                # Report progress
                if self.progress_callback:
                    self.progress_callback(page_count, self.max_pages, current_url)
                    
            except Exception as e:
                logger.error(f"Error scanning {current_url}: {str(e)}")
                findings.append({
                    'type': 'error',
                    'url': current_url,
                    'description': f"Failed to scan page: {str(e)}",
                    'severity': 'Medium'
                })
        
        # Check SSL/TLS configuration
        ssl_info = None
        if self.check_ssl:
            ssl_info = self._check_ssl(base_url)
        
        # Summarize findings
        self.is_running = False
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        # Generate statistics
        stats = {
            'pages_scanned': page_count,
            'total_cookies': len(cookies),
            'total_trackers': len(trackers),
            'total_findings': len(findings),
            'total_links': len(all_links),
            'internal_links': len(same_domain_links),
            'external_links': len(external_links),
            'scan_duration_seconds': duration
        }
        
        # Categorize cookies
        cookie_categories = self._categorize_cookies(cookies)
        
        # Generate the final scan results
        scan_results = {
            'scan_id': scan_id,
            'scan_time': self.start_time.isoformat(),
            'completion_time': end_time.isoformat(),
            'duration_seconds': duration,
            'url': url,
            'base_domain': base_domain,
            'pages_data': pages_data,
            'findings': findings,
            'cookies': cookies,
            'cookie_categories': cookie_categories,
            'trackers': list(trackers.values()),
            'links': {
                'all': list(all_links),
                'internal': list(same_domain_links),
                'external': list(external_links)
            },
            'domain_info': domain_info,
            'ssl_info': ssl_info,
            'stats': stats,
            'scan_type': 'website'
        }
        
        return scan_results
    
    def _analyze_page(self, url: str, html_content: str, depth: int) -> Dict[str, Any]:
        """
        Analyze a single webpage for privacy issues.
        
        Args:
            url: The URL of the page
            html_content: The HTML content of the page
            depth: The crawl depth
            
        Returns:
            Dictionary with page analysis results
        """
        # Parse the URL
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract page title and metadata
        title = soup.title.text.strip() if soup.title else "No title"
        
        meta_description = None
        meta_tags = []
        for meta in soup.find_all('meta'):
            meta_dict = {key: meta.get(key) for key in meta.attrs}
            meta_tags.append(meta_dict)
            if meta.get('name') == 'description':
                meta_description = meta.get('content', '')
        
        # Extract links
        all_links = set()
        same_domain_links = set()
        external_links = set()
        
        for link in soup.find_all('a', href=True):
            href = link.get('href').strip()
            
            # Skip empty links, anchors, javascript, and mailto
            if not href or href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
                continue
            
            # Normalize the URL
            absolute_url = urljoin(url, href)
            parsed_link = urlparse(absolute_url)
            
            # Skip non-HTTP(S) links
            if parsed_link.scheme not in ('http', 'https'):
                continue
            
            clean_url = f"{parsed_link.scheme}://{parsed_link.netloc}{parsed_link.path}"
            if parsed_link.query:
                clean_url += f"?{parsed_link.query}"
                
            all_links.add(clean_url)
            
            # Classify as internal or external
            if parsed_link.netloc == domain:
                same_domain_links.add(clean_url)
            else:
                external_links.add(clean_url)
        
        # Detect trackers and cookies in the JavaScript
        scripts = soup.find_all('script')
        trackers = []
        findings = []
        
        # Check for inline scripts containing tracker patterns
        for script in scripts:
            # Check for src attribute
            src = script.get('src', '')
            if src:
                # Check external script sources against known trackers
                for tracker_name, tracker_info in self.known_trackers.items():
                    for domain_pattern in tracker_info['domains']:
                        if domain_pattern in src:
                            trackers.append({
                                'name': tracker_name,
                                'url': src,
                                'type': 'external',
                                'found_on': url
                            })
                            findings.append({
                                'type': 'tracker',
                                'subtype': tracker_name,
                                'url': url,
                                'element': src,
                                'description': f"External tracker script from {tracker_name}",
                                'severity': 'Medium',
                                'gdpr_article': 'Art. 6(1)(a), Art. 7'
                            })
                            break
            
            # Check inline script content for tracker patterns
            elif script.string:
                script_content = script.string
                for tracker_name, tracker_info in self.known_trackers.items():
                    for pattern in tracker_info['patterns']:
                        if pattern in script_content:
                            trackers.append({
                                'name': tracker_name,
                                'type': 'inline',
                                'found_on': url
                            })
                            findings.append({
                                'type': 'tracker',
                                'subtype': tracker_name,
                                'url': url,
                                'element': f"Inline script containing '{pattern}'",
                                'description': f"Inline tracker script for {tracker_name}",
                                'severity': 'Medium',
                                'gdpr_article': 'Art. 6(1)(a), Art. 7'
                            })
                            break
        
        # Detect consent management platforms
        consent_management = []
        for platform in self.consent_platforms:
            for pattern in platform['patterns']:
                if pattern in html_content:
                    consent_management.append({
                        'name': platform['name'],
                        'found_on': url
                    })
                    findings.append({
                        'type': 'consent_management',
                        'subtype': platform['name'],
                        'url': url,
                        'description': f"Using {platform['name']} consent management platform",
                        'severity': 'Info',
                        'gdpr_article': 'Art. 7, Art. 13'
                    })
                    break
        
        # Check for tracking pixels
        img_tags = soup.find_all('img')
        tracking_pixels = []
        
        for img in img_tags:
            src = img.get('src', '')
            height = img.get('height', '')
            width = img.get('width', '')
            
            # Check for 1x1 pixel images or known tracking domains
            if (height == '1' and width == '1') or ('pixel' in src.lower()):
                tracking_pixels.append({
                    'url': src,
                    'found_on': url
                })
                findings.append({
                    'type': 'tracking_pixel',
                    'url': url,
                    'element': src,
                    'description': f"Tracking pixel detected: {src}",
                    'severity': 'Medium',
                    'gdpr_article': 'Art. 6(1)(a), Art. 7'
                })
        
        # Extract main text content
        try:
            main_content = extract(html_content) or "No content extracted"
        except:
            main_content = "Failed to extract content"
        
        # Check for privacy-related content
        privacy_terms = {
            'privacy_policy': ['privacy', 'privacy policy', 'privacy statement', 'data policy', 'data protection'],
            'cookie_policy': ['cookie', 'cookie policy', 'cookie statement', 'cookie notice', 'cookie preferences'],
            'terms_of_service': ['terms', 'terms of service', 'terms of use', 'terms and conditions', 'legal'],
            'gdpr': ['gdpr', 'general data protection regulation', 'data protection', 'eu regulation']
        }
        
        privacy_links = {}
        
        for link in soup.find_all('a', href=True):
            href = link.get('href').strip()
            text = link.get_text().lower()
            
            for policy_type, terms in privacy_terms.items():
                if any(term in text for term in terms):
                    absolute_url = urljoin(url, href)
                    privacy_links[policy_type] = absolute_url
                    break
        
        # Check for cookie banner
        cookie_banner = None
        cookie_banner_selectors = [
            '#cookie-banner', '.cookie-banner', '#cookieBanner', '.cookieBanner',
            '#cookie-notice', '.cookie-notice', '#cookieNotice', '.cookieNotice',
            '#gdpr-banner', '.gdpr-banner', '#gdprBanner', '.gdprBanner',
            '#cookie-consent', '.cookie-consent', '#cookieConsent', '.cookieConsent',
            '[class*="cookie"]', '[id*="cookie"]', '[class*="gdpr"]', '[id*="gdpr"]',
            '[class*="consent"]', '[id*="consent"]'
        ]
        
        for selector in cookie_banner_selectors:
            elements = soup.select(selector)
            if elements:
                cookie_banner = {
                    'found': True,
                    'selector': selector,
                    'count': len(elements),
                    'text': elements[0].get_text()[:200] + '...' if len(elements[0].get_text()) > 200 else elements[0].get_text()
                }
                break
        
        # Return the page analysis results
        return {
            'url': url,
            'depth': depth,
            'title': title,
            'meta_description': meta_description,
            'meta_tags': meta_tags,
            'all_links': all_links,
            'same_domain_links': same_domain_links,
            'external_links': external_links,
            'trackers': trackers,
            'consent_management': consent_management,
            'tracking_pixels': tracking_pixels,
            'privacy_links': privacy_links,
            'cookie_banner': cookie_banner,
            'main_content_sample': main_content[:1000] + '...' if len(main_content) > 1000 else main_content,
            'findings': findings
        }
    
    def _extract_cookies(self, response) -> Dict[str, Any]:
        """
        Extract cookies from a response.
        
        Args:
            response: The HTTP response object
            
        Returns:
            Dictionary of cookies with metadata
        """
        cookies = {}
        
        for cookie in response.cookies:
            # Skip if cookie already processed
            if cookie.name in cookies:
                continue
                
            # Analyze cookie properties
            secure = cookie.secure
            httponly = cookie.has_nonstandard_attr('httponly')
            samesite = cookie.get_nonstandard_attr('samesite', None)
            
            expiry = None
            if cookie.expires:
                try:
                    expiry = datetime.fromtimestamp(cookie.expires).isoformat()
                except:
                    expiry = str(cookie.expires)
            
            # Categorize the cookie
            category = self._categorize_cookie(cookie.name, cookie.domain)
            
            # Evaluate cookie compliance
            compliance_issues = []
            if not secure:
                compliance_issues.append("Cookie not marked as Secure")
            if not httponly and category == 'essential':
                compliance_issues.append("Essential cookie not marked as HttpOnly")
            if not samesite and category != 'essential':
                compliance_issues.append("Missing SameSite attribute")
            if category in ['advertising', 'analytics'] and not samesite == 'None':
                compliance_issues.append("Tracking cookie should use SameSite=None")
            
            # Add cookie data
            cookies[cookie.name] = {
                'name': cookie.name,
                'domain': cookie.domain,
                'path': cookie.path,
                'value_length': len(cookie.value),
                'secure': secure,
                'httponly': httponly,
                'samesite': samesite,
                'expiry': expiry,
                'session': cookie.expires is None,
                'category': category,
                'compliance_issues': compliance_issues
            }
        
        return cookies
    
    def _categorize_cookie(self, name: str, domain: str = None) -> str:
        """
        Categorize a cookie based on its name and domain.
        
        Args:
            name: Cookie name
            domain: Cookie domain (optional)
            
        Returns:
            Category name (essential, functional, analytics, advertising, social, or unknown)
        """
        name_lower = name.lower()
        
        # First check by domain, then by name
        if domain:
            domain_lower = domain.lower()
            if any(tracker in domain_lower for tracker in ['google-analytics', 'analytics.google']):
                return 'analytics'
            if any(tracker in domain_lower for tracker in ['doubleclick', 'googleadservices']):
                return 'advertising'
            if any(social in domain_lower for social in ['facebook', 'twitter', 'linkedin', 'instagram']):
                return 'social'
        
        # Check by cookie name against known categories
        for category, patterns in self.cookie_categories.items():
            for pattern in patterns:
                if pattern in name_lower:
                    return category
        
        # Return unknown if no match
        return 'unknown'
    
    def _categorize_cookies(self, cookies: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Categorize all cookies.
        
        Args:
            cookies: Dictionary of cookie data
            
        Returns:
            Dictionary with categories and cookie names
        """
        categories = {
            'essential': [],
            'functional': [],
            'analytics': [],
            'advertising': [],
            'social': [],
            'unknown': []
        }
        
        for cookie_name, cookie_data in cookies.items():
            category = cookie_data.get('category', 'unknown')
            categories.setdefault(category, []).append(cookie_name)
        
        return categories
    
    def _check_domain_info(self, domain: str) -> Dict[str, Any]:
        """
        Check domain registration information.
        
        Args:
            domain: The domain name to check
            
        Returns:
            Dictionary with domain registration information
        """
        # Extract the base domain without subdomains
        extracted = tldextract.extract(domain)
        base_domain = f"{extracted.domain}.{extracted.suffix}"
        
        domain_info = {
            'domain': base_domain,
            'registration': None,
            'registrar': None,
            'creation_date': None,
            'expiration_date': None,
            'dns_records': {}
        }
        
        # Get WHOIS information
        try:
            w = whois.whois(base_domain)
            domain_info['registration'] = {
                'registrar': w.registrar,
                'creation_date': w.creation_date.isoformat() if hasattr(w, 'creation_date') and w.creation_date else None,
                'expiration_date': w.expiration_date.isoformat() if hasattr(w, 'expiration_date') and w.expiration_date else None,
                'name_servers': w.name_servers if hasattr(w, 'name_servers') else None
            }
        except Exception as e:
            logger.warning(f"Failed to get WHOIS information for {base_domain}: {str(e)}")
            domain_info['registration'] = {'error': str(e)}
        
        # Get DNS records if enabled
        if self.check_dns:
            try:
                # Get A records
                try:
                    answers = dns.resolver.resolve(base_domain, 'A')
                    domain_info['dns_records']['A'] = [answer.address for answer in answers]
                except Exception as e:
                    logger.warning(f"Failed to get A records for {base_domain}: {str(e)}")
                
                # Get MX records
                try:
                    answers = dns.resolver.resolve(base_domain, 'MX')
                    domain_info['dns_records']['MX'] = [str(answer.exchange) for answer in answers]
                except Exception as e:
                    logger.warning(f"Failed to get MX records for {base_domain}: {str(e)}")
                
                # Get TXT records
                try:
                    answers = dns.resolver.resolve(base_domain, 'TXT')
                    domain_info['dns_records']['TXT'] = [str(answer) for answer in answers]
                except Exception as e:
                    logger.warning(f"Failed to get TXT records for {base_domain}: {str(e)}")
            except Exception as e:
                logger.warning(f"Failed to get DNS records for {base_domain}: {str(e)}")
        
        return domain_info
    
    def _check_ssl(self, url: str) -> Dict[str, Any]:
        """
        Check SSL/TLS configuration.
        
        Args:
            url: The URL to check SSL for
            
        Returns:
            Dictionary with SSL/TLS information
        """
        ssl_info = {
            'enabled': False,
            'certificate': None,
            'expiry': None,
            'issuer': None,
            'protocols': [],
            'issues': []
        }
        
        try:
            response = requests.get(url, verify=True, timeout=10)
            
            # Check if HTTPS is enabled
            ssl_info['enabled'] = response.url.startswith('https://')
            
            if ssl_info['enabled']:
                # Unfortunately, requests doesn't provide detailed SSL/TLS info
                # Here we would need to use a library like pyOpenSSL or subprocess to openssl
                # For now, just mark that SSL is enabled
                ssl_info['certificate'] = "Valid (details not available)"
            else:
                ssl_info['issues'].append("HTTPS not enabled")
                
        except requests.exceptions.SSLError as e:
            ssl_info['issues'].append(f"SSL Error: {str(e)}")
        except Exception as e:
            ssl_info['issues'].append(f"Error checking SSL: {str(e)}")
        
        return ssl_info
    
    def cancel_scan(self):
        """Cancel the current scan if running"""
        self.is_running = False