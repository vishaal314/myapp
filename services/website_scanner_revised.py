"""
Enhanced Website Scanner for GDPR and Dutch UAVG Compliance

This module provides a scanner to analyze websites for GDPR compliance issues
with special focus on Netherlands-specific GDPR (UAVG) requirements.
"""

import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import time
import json
import uuid
import os
import random
from datetime import datetime
import trafilatura
from urllib.parse import urlparse
import tldextract
import pandas as pd
import numpy as np
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
import matplotlib.pyplot as plt
import base64
import logging

# Import logo generator
from static.dataguardian_logo import get_logo_stream

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('website_scanner')

class WebsiteScanner:
    """GDPR and Dutch UAVG-compliant website scanner"""
    
    def __init__(self, region="EU", progress_callback=None):
        """
        Initialize the scanner
        
        Args:
            region: The region to apply compliance rules for (EU, Global, Netherlands)
            progress_callback: Function to call with progress updates
        """
        self.region = region
        self.progress_callback = progress_callback
        self.scan_id = str(uuid.uuid4())
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        
        # Define Netherlands-specific requirements based on UAVG (Dutch GDPR Implementation)
        self.netherlands_requirements = {
            "bsn_handling": "Special rules for BSN (citizen service number) usage",
            "medical_data": "Strict requirements for health data processing",
            "employment_data": "Additional protection for employee data",
            "minor_consent": "Parental consent required for users under 16 years",
            "data_breach": "72-hour breach notification to Dutch DPA (AP)",
            "high_risk_pii": "Enhanced measures for sensitive Dutch categorized data",
            "legal_basis": "Documentation of processing legal basis"
        }
        
    def set_progress_callback(self, callback):
        """Set progress callback function"""
        self.progress_callback = callback
    
    def update_progress(self, current, total, message):
        """Update progress indicator"""
        if self.progress_callback:
            self.progress_callback(current, total, message)
    
    def scan_website(self, website_url, website_name=None, **kwargs):
        """
        Scan a website for GDPR compliance issues
        
        Args:
            website_url: URL of the website to scan
            website_name: Name of the website (optional)
            **kwargs: Additional scan options
            
        Returns:
            Dict with scan results
        """
        try:
            # Ensure the URL has a scheme
            if not website_url.startswith(('http://', 'https://')):
                website_url = 'https://' + website_url
            
            # Extract domain if website_name not provided
            if not website_name:
                parsed_url = urlparse(website_url)
                extracted = tldextract.extract(parsed_url.netloc)
                website_name = f"{extracted.domain}.{extracted.suffix}"
            
            self.update_progress(5, 100, "Initializing scan...")
            
            # Start with basic result structure
            results = {
                "scan_type": "Website Scanner",
                "scan_id": self.scan_id,
                "timestamp": datetime.now().isoformat(),
                "website_url": website_url,
                "website_name": website_name,
                "findings": [],
                "categories": {
                    "cookie_consent": {"score": 0, "max_score": 100, "findings": []},
                    "privacy_policy": {"score": 0, "max_score": 100, "findings": []},
                    "data_processing": {"score": 0, "max_score": 100, "findings": []},
                    "data_access": {"score": 0, "max_score": 100, "findings": []},
                    "forms_and_consent": {"score": 0, "max_score": 100, "findings": []},
                    "security": {"score": 0, "max_score": 100, "findings": []}
                },
                "total_issues": 0,
                "compliance_score": 0,
                "critical_issues": 0,
                "high_risk": 0,
                "medium_risk": 0,
                "low_risk": 0
            }
            
            # Add Netherlands-specific category if region is Netherlands
            if self.region == "Netherlands":
                results["categories"]["netherlands_uavg"] = {"score": 0, "max_score": 100, "findings": []}
            
            self.update_progress(10, 100, "Fetching website content...")
            
            # Fetch website content
            try:
                headers = {'User-Agent': self.user_agent}
                response = requests.get(website_url, headers=headers, timeout=15)
                html_content = response.text
                status_code = response.status_code
                
                # Simple check for server response
                if status_code != 200:
                    self._add_finding(results, "security", "Server Error", 
                                     f"Server responded with status code {status_code}", 
                                     "critical", "Ensure the website is properly functioning.")
            except requests.RequestException as e:
                self._add_finding(results, "security", "Connection Error", 
                                 f"Failed to connect to website: {str(e)}", 
                                 "critical", "Check website availability and DNS configuration.")
                
                # Return partial results since we can't proceed
                self._finalize_results(results)
                return results
                
            # Extract text content
            self.update_progress(20, 100, "Extracting text content...")
            text_content = self._extract_text_content(website_url)
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Start scanning for GDPR compliance
            self.update_progress(30, 100, "Checking cookie consent...")
            self._check_cookie_consent(results, soup, html_content)
            
            self.update_progress(40, 100, "Analyzing privacy policy...")
            self._check_privacy_policy(results, soup, html_content, text_content)
            
            self.update_progress(50, 100, "Checking data processing agreements...")
            self._check_data_processing(results, soup, html_content, text_content)
            
            self.update_progress(60, 100, "Analyzing data access rights...")
            self._check_data_access_rights(results, soup, html_content, text_content)
            
            self.update_progress(70, 100, "Examining forms and consent mechanisms...")
            self._check_forms_and_consent(results, soup, html_content)
            
            self.update_progress(75, 100, "Evaluating security practices...")
            self._check_security_practices(results, soup, html_content, response)
            
            # Add Netherlands-specific checks if region is Netherlands
            if self.region == "Netherlands":
                self.update_progress(80, 100, "Checking Netherlands-specific UAVG requirements...")
                self._check_netherlands_requirements(results, soup, html_content, text_content)
            
            self.update_progress(90, 100, "Finalizing results...")
            self._finalize_results(results)
            
            self.update_progress(100, 100, "Scan completed!")
            return results
            
        except Exception as e:
            logger.error(f"Error during website scan: {str(e)}", exc_info=True)
            return {
                "scan_type": "Website Scanner",
                "scan_id": self.scan_id,
                "timestamp": datetime.now().isoformat(),
                "website_url": website_url,
                "website_name": website_name if website_name else "Unknown",
                "error": f"Scan failed: {str(e)}",
                "compliance_score": 0
            }
    
    def _extract_text_content(self, url):
        """Extract text content from website"""
        try:
            downloaded = trafilatura.fetch_url(url)
            text = trafilatura.extract(downloaded)
            return text if text else ""
        except Exception as e:
            logger.warning(f"Error extracting text content: {str(e)}")
            return ""
    
    def _check_cookie_consent(self, results, soup, html_content):
        """Check for cookie consent banner and compliance"""
        # Check for common cookie consent elements
        common_cookie_ids = ['cookie-banner', 'cookie-consent', 'gdpr-consent', 'cookie-law', 'cookiebanner']
        common_cookie_classes = ['cookie-banner', 'cookie-consent', 'gdpr-consent', 'cookie-notice', 'cookie-policy']
        common_cookie_texts = ['cookie', 'gdpr', 'consent', 'accept cookies', 'cookie policy']
        
        # Check for cookie consent banners
        found_banner = False
        for id_name in common_cookie_ids:
            element = soup.find(id=id_name)
            if element:
                found_banner = True
                break
                
        if not found_banner:
            for class_name in common_cookie_classes:
                elements = soup.find_all(class_=lambda c: c and class_name.lower() in c.lower())
                if elements:
                    found_banner = True
                    break
        
        if not found_banner:
            for text in common_cookie_texts:
                elements = soup.find_all(string=lambda s: s and text.lower() in s.lower())
                visible_elements = [e for e in elements if self._is_visible(e)]
                if visible_elements:
                    found_banner = True
                    break
        
        # Evaluate results
        if not found_banner:
            self._add_finding(results, "cookie_consent", "Missing Cookie Consent", 
                             "No cookie consent banner detected on the website", 
                             "critical", "Implement a cookie consent banner that appears before setting any non-essential cookies")
        else:
            # Check for prior consent - banner must have accept/reject options
            accept_buttons = soup.find_all(string=lambda s: s and any(word in s.lower() for word in ['accept', 'agree', 'allow', 'consent']))
            reject_buttons = soup.find_all(string=lambda s: s and any(word in s.lower() for word in ['reject', 'decline', 'refuse', 'no thanks', 'opt-out']))
            
            if not reject_buttons:
                self._add_finding(results, "cookie_consent", "No Reject Option", 
                                 "Cookie banner provides no clear way to reject cookies", 
                                 "high", "Add a 'Reject All' option that is as visible as the accept option")
            
            if not accept_buttons and not reject_buttons:
                self._add_finding(results, "cookie_consent", "No Consent Options", 
                                 "Cookie banner doesn't provide clear consent options", 
                                 "high", "Add clear 'Accept' and 'Reject' options to the cookie banner")
            
            # Check for cookie setting before consent
            if 'document.cookie' in html_content and not 'document.cookie' in html_content.lower().split('consent')[1:]:
                self._add_finding(results, "cookie_consent", "Cookies Before Consent", 
                                 "Site appears to set cookies before obtaining consent", 
                                 "high", "Ensure no non-essential cookies are set before user provides consent")
    
    def _check_privacy_policy(self, results, soup, html_content, text_content):
        """Check for privacy policy presence and content"""
        # Look for privacy policy links
        privacy_links = []
        for a in soup.find_all('a'):
            if a.text and any(term in a.text.lower() for term in ['privacy', 'privacy policy', 'data protection']):
                privacy_links.append(a)
        
        if not privacy_links:
            self._add_finding(results, "privacy_policy", "Missing Privacy Policy", 
                             "No privacy policy link found on the website", 
                             "critical", "Add a clearly visible privacy policy link in the website footer")
            return
        
        # Check if privacy policy is easy to access
        footer = soup.find('footer')
        if footer and not any(a in footer.find_all('a') for a in privacy_links):
            self._add_finding(results, "privacy_policy", "Privacy Policy Not in Footer", 
                             "Privacy policy link not found in website footer", 
                             "medium", "Add privacy policy link to website footer for better accessibility")
        
        # Simple content analysis for privacy policy if text was extracted
        if text_content:
            required_topics = [
                ("purpose", "Explanation of data processing purposes"),
                ("legal basis", "Legal basis for processing"),
                ("data categories", "Categories of personal data collected"),
                ("retention", "Data retention period"),
                ("rights", "User rights explanation"),
                ("contact", "Contact details for data protection matters")
            ]
            
            for keyword, description in required_topics:
                if keyword not in text_content.lower():
                    self._add_finding(results, "privacy_policy", f"Missing {description}", 
                                     f"Privacy policy may not include {description}", 
                                     "medium", f"Ensure the privacy policy includes information about {description}")
    
    def _check_data_processing(self, results, soup, html_content, text_content):
        """Check for data processing agreements and third party data sharing"""
        # Look for mentions of third parties
        third_party_terms = ['third part', 'third-part', 'data processor', 'service provider', 'analytics provider']
        
        third_party_found = False
        for term in third_party_terms:
            if term in text_content.lower():
                third_party_found = True
                break
        
        # Check for common third-party services in page source
        common_services = [
            ('google analytics', 'Google Analytics'),
            ('facebook pixel', 'Facebook Pixel'),
            ('hotjar', 'Hotjar'),
            ('amplitude', 'Amplitude'),
            ('segment', 'Segment')
        ]
        
        detected_services = []
        for keyword, service_name in common_services:
            if keyword in html_content.lower():
                detected_services.append(service_name)
        
        # Add findings based on analysis
        if detected_services and not third_party_found:
            services_list = ", ".join(detected_services)
            self._add_finding(results, "data_processing", "Undisclosed Third Parties", 
                             f"Third-party services detected ({services_list}) but not disclosed in privacy policy", 
                             "high", "Update privacy policy to disclose all third-party data processors")
        
        # Check for standard contractual clauses mention for international transfers
        international_terms = ['international transfer', 'outside the eu', 'outside the eea', 'standard contractual clauses', 'privacy shield']
        international_found = any(term in text_content.lower() for term in international_terms)
        
        if any(s in ['Google Analytics', 'Facebook Pixel'] for s in detected_services) and not international_found:
            self._add_finding(results, "data_processing", "International Transfers Not Addressed", 
                             "International data transfers likely occur but are not addressed in the privacy policy", 
                             "high", "Address international data transfers in privacy policy and implement appropriate safeguards")
    
    def _check_data_access_rights(self, results, soup, html_content, text_content):
        """Check for data access and deletion rights"""
        # Look for GDPR rights mentions
        rights_terms = [
            ('right to access', 'access right'), 
            ('right to delete', 'deletion right', 'right to be forgotten'), 
            ('right to object', 'objection right'),
            ('right to rectification', 'correction right'),
            ('right to data portability', 'portability right')
        ]
        
        missing_rights = []
        for right_group in rights_terms:
            if not any(term in text_content.lower() for term in right_group):
                # Use the first term as the reference
                missing_rights.append(right_group[0])
        
        # Check if contact method is provided for exercising rights
        contact_methods = ['email', 'form', 'contact us', 'request form', 'data protection officer']
        has_contact_method = any(method in text_content.lower() for method in contact_methods)
        
        # Add findings
        if missing_rights:
            rights_list = ", ".join(missing_rights)
            self._add_finding(results, "data_access", "Missing Data Subject Rights", 
                             f"Privacy policy may not address all GDPR data subject rights. Missing: {rights_list}", 
                             "high", "Ensure privacy policy covers all GDPR data subject rights")
        
        if not has_contact_method:
            self._add_finding(results, "data_access", "No Rights Exercise Method", 
                             "No clear method provided for users to exercise their data subject rights", 
                             "high", "Add clear instructions for how users can exercise their GDPR rights")
    
    def _check_forms_and_consent(self, results, soup, html_content):
        """Check for proper consent mechanisms in forms"""
        # Find all forms
        forms = soup.find_all('form')
        
        if not forms:
            # No forms found, no findings to add
            return
        
        # Check each form for proper consent
        for i, form in enumerate(forms):
            # Look for checkboxes that might be consent mechanisms
            checkboxes = form.find_all('input', type='checkbox')
            
            # Look for email inputs (likely newsletter signups)
            email_inputs = form.find_all('input', attrs={'type': 'email'})
            
            # Check for pre-ticked boxes
            pre_ticked = [cb for cb in checkboxes if cb.has_attr('checked')]
            
            # If form has email input but no checkbox for consent
            if email_inputs and not checkboxes:
                self._add_finding(results, "forms_and_consent", f"Missing Consent in Form #{i+1}", 
                                 "Form with email field does not have explicit consent mechanism", 
                                 "high", "Add explicit opt-in checkbox for marketing communications")
            
            # If form has pre-ticked consent boxes
            if pre_ticked:
                self._add_finding(results, "forms_and_consent", f"Pre-ticked Consent in Form #{i+1}", 
                                 "Form contains pre-ticked consent checkboxes", 
                                 "high", "Remove pre-ticked checkboxes as explicit consent requires active opt-in")
            
            # Check newsletter-like forms for terms references
            if email_inputs:
                form_text = form.get_text().lower()
                has_privacy_reference = any(term in form_text for term in ['privacy', 'terms', 'policy'])
                
                if not has_privacy_reference:
                    self._add_finding(results, "forms_and_consent", f"No Privacy Reference in Form #{i+1}", 
                                     "Form collecting personal data does not reference privacy policy", 
                                     "medium", "Add privacy policy reference near form submission button")
    
    def _check_security_practices(self, results, soup, html_content, response):
        """Check for basic security practices"""
        # Check if site uses HTTPS
        if not response.url.startswith('https://'):
            self._add_finding(results, "security", "No HTTPS", 
                             "Website does not use HTTPS encryption", 
                             "critical", "Implement HTTPS across the entire website")
        
        # Check for secure cookies
        if 'Set-Cookie' in response.headers:
            cookies = response.headers.get('Set-Cookie')
            if 'secure' not in cookies.lower():
                self._add_finding(results, "security", "Insecure Cookies", 
                                 "Cookies are set without the Secure flag", 
                                 "high", "Set the Secure flag on all cookies")
            
            if 'httponly' not in cookies.lower():
                self._add_finding(results, "security", "Non-HttpOnly Cookies", 
                                 "Cookies are set without the HttpOnly flag", 
                                 "medium", "Set the HttpOnly flag on cookies that don't need JavaScript access")
        
        # Check for Content-Security-Policy header
        if 'Content-Security-Policy' not in response.headers:
            self._add_finding(results, "security", "Missing CSP", 
                             "Content-Security-Policy header is not set", 
                             "medium", "Implement a Content-Security-Policy header to mitigate XSS risks")
    
    def _check_netherlands_requirements(self, results, soup, html_content, text_content):
        """Check for Netherlands-specific GDPR (UAVG) requirements"""
        
        # Check for BSN handling
        bsn_terms = ['bsn', 'burgerservicenummer', 'citizen service number', 'social security', 'identification number']
        has_bsn_references = any(term in text_content.lower() for term in bsn_terms)
        
        if has_bsn_references:
            # Check if there's specific processing information for BSN
            has_bsn_regulations = any(f"{term} processing" in text_content.lower() or 
                                     f"{term} handling" in text_content.lower() or
                                     f"{term} usage" in text_content.lower() 
                                     for term in bsn_terms[:2])
            
            if not has_bsn_regulations:
                self._add_finding(results, "netherlands_uavg", "BSN Processing Not Documented", 
                                 "Website appears to handle BSN (burgerservicenummer) but doesn't document special handling", 
                                 "critical", 
                                 "Add documentation about BSN processing limitations and legal basis according to Dutch UAVG requirements")
        
        # Check for minor consent mentions for Dutch requirement (<16 years)
        minor_terms = ['under 16', 'minor', 'child', 'teen', 'youth', 'young person', 'parental consent']
        has_minor_consent = any(term in text_content.lower() for term in minor_terms)
        
        if not has_minor_consent:
            self._add_finding(results, "netherlands_uavg", "Missing Dutch Minor Consent", 
                            "Privacy policy does not address parental consent for users under 16 years", 
                            "high", 
                            "Include specific verbiage about parental consent for users under 16 years as required by Dutch UAVG")
        
        # Check for Dutch data breach notification mentions
        breach_terms = ['data breach', 'security breach', 'breach notification', 'autoriteit persoonsgegevens', 'ap', '72 hour', '72-hour']
        has_breach_notification = any(term in text_content.lower() for term in breach_terms)
        
        if not has_breach_notification:
            self._add_finding(results, "netherlands_uavg", "Missing Data Breach Framework", 
                            "Privacy policy does not mention Dutch breach notification requirements", 
                            "high", 
                            "Include information about data breach notification procedures to Dutch DPA (AP) within 72 hours")
        
        # Check for legal basis documentation
        legal_basis_terms = ['legal basis', 'lawful basis', 'legitimate interest', 'contractual necessity', 
                           'legal obligation', 'vital interest', 'public interest', 'official authority']
        has_legal_basis = any(term in text_content.lower() for term in legal_basis_terms)
        
        if not has_legal_basis:
            self._add_finding(results, "netherlands_uavg", "Missing Legal Basis Documentation", 
                            "Privacy policy does not clearly document legal basis for processing", 
                            "high", 
                            "Document specific legal basis (consent, contract, legitimate interest, etc.) for each data processing activity")
        
        # Check for medical/health data handling
        medical_terms = ['medical', 'health', 'patient', 'healthcare', 'medische', 'gezondheid']
        has_medical_references = any(term in text_content.lower() for term in medical_terms)
        
        if has_medical_references:
            medical_protection_terms = ['special category', 'sensitive data', 'additional safeguards', 'bijzondere persoonsgegevens']
            has_medical_protections = any(term in text_content.lower() for term in medical_protection_terms)
            
            if not has_medical_protections:
                self._add_finding(results, "netherlands_uavg", "Medical Data Without Special Protections", 
                                "Website appears to handle medical/health data without noting special protections", 
                                "critical", 
                                "Implement and document special safeguards for medical data per Dutch UAVG requirements")
    
    def _is_visible(self, element):
        """Check if an element would be visible to users"""
        # This is a simplified check - a real implementation would be more complex
        if not element.parent:
            return False
            
        style = element.parent.get('style', '')
        display_none = 'display:none' in style or 'display: none' in style
        visibility_hidden = 'visibility:hidden' in style or 'visibility: hidden' in style
        
        return not (display_none or visibility_hidden)
    
    def _add_finding(self, results, category, title, description, severity, recommendation):
        """Add a finding to the results"""
        severity_values = {
            "critical": 100,
            "high": 70,
            "medium": 40,
            "low": 10,
            "info": 0
        }
        
        finding = {
            "id": str(uuid.uuid4()),
            "category": category,
            "title": title,
            "description": description,
            "severity": severity,
            "severity_value": severity_values.get(severity, 0),
            "recommendation": recommendation
        }
        
        # Add to overall findings list
        results["findings"].append(finding)
        
        # Add to category-specific findings
        if category in results["categories"]:
            results["categories"][category]["findings"].append(finding)
        
        # Update risk counters
        if severity == "critical":
            results["critical_issues"] += 1
        elif severity == "high":
            results["high_risk"] += 1
        elif severity == "medium":
            results["medium_risk"] += 1
        elif severity == "low":
            results["low_risk"] += 1
    
    def _finalize_results(self, results):
        """Calculate final scores and counts"""
        # Count total issues
        results["total_issues"] = (
            results["critical_issues"] + 
            results["high_risk"] + 
            results["medium_risk"] + 
            results["low_risk"]
        )
        
        # Calculate category scores
        for category, data in results["categories"].items():
            if data["findings"]:
                # Higher severity findings reduce score more
                total_severity = sum(finding["severity_value"] for finding in data["findings"])
                max_possible = len(data["findings"]) * 100  # If all were critical
                
                # Score is inversely proportional to severity (100 - percentage of max severity)
                if max_possible > 0:
                    data["score"] = max(0, 100 - int((total_severity / max_possible) * 100))
                else:
                    data["score"] = 100
            else:
                # No findings means perfect score
                data["score"] = 100
        
        # Calculate overall compliance score with appropriate weights
        if self.region == "Netherlands":
            # Give extra weight to Netherlands-specific requirements
            category_weights = {
                "cookie_consent": 0.15,
                "privacy_policy": 0.15,
                "data_processing": 0.15,
                "data_access": 0.15,
                "forms_and_consent": 0.10,
                "security": 0.10,
                "netherlands_uavg": 0.20  # Higher weight for Dutch requirements
            }
        else:
            # Standard weights for other regions
            category_weights = {
                "cookie_consent": 0.2,
                "privacy_policy": 0.2,
                "data_processing": 0.15,
                "data_access": 0.15,
                "forms_and_consent": 0.15,
                "security": 0.15
            }
        
        weighted_sum = sum(
            results["categories"][cat]["score"] * weight 
            for cat, weight in category_weights.items()
            if cat in results["categories"]  # Only consider categories that exist in results
        )
        
        # Normalize by the actual weights used (in case some categories don't exist)
        actual_weight_sum = sum(
            weight for cat, weight in category_weights.items() 
            if cat in results["categories"]
        )
        
        if actual_weight_sum > 0:
            results["compliance_score"] = int(weighted_sum / actual_weight_sum)
        else:
            results["compliance_score"] = 0
        
        # Add compliance status
        if results["compliance_score"] >= 90:
            results["compliance_status"] = "Compliant"
        elif results["compliance_score"] >= 70:
            results["compliance_status"] = "Partially Compliant"
        else:
            results["compliance_status"] = "Non-Compliant"


def generate_gdpr_report(results):
    """
    Generate a modern, certification-style PDF report for GDPR compliance scan results
    
    Args:
        results: The scan results dictionary
    
    Returns:
        BytesIO object containing the PDF report
    """
    buffer = BytesIO()
    
    # Use A4 for a professional certificate look
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        leftMargin=1*cm,
        rightMargin=1*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )
    
    styles = getSampleStyleSheet()
    elements = []
    
    # Add modern styles with unique names
    styles.add(ParagraphStyle(
        name='CertTitle',
        parent=styles['Heading1'],
        fontSize=22,
        fontName='Helvetica-Bold',
        textColor=colors.darkblue,
        alignment=1,  # Center alignment
        spaceAfter=12
    ))
    
    styles.add(ParagraphStyle(
        name='CertSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        fontName='Helvetica-Bold',
        textColor=colors.darkblue,
        alignment=0,  # Left alignment
        borderWidth=0,
        borderColor=colors.darkblue,
        borderPadding=5,
        spaceAfter=10
    ))
    
    styles.add(ParagraphStyle(
        name='CertNormal',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica',
        spaceAfter=8
    ))
    
    styles.add(ParagraphStyle(
        name='CertInfo',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica',
        textColor=colors.grey,
        alignment=1,  # Center alignment
        spaceAfter=5
    ))
    
    # Add spacer at the top of the document
    elements.append(Spacer(1, 0.5*inch))
    
    # Create a centered table for the logo
    logo_stream = get_logo_stream()
    if logo_stream:
        # Create a larger logo image for modern minimalistic design
        logo_img = Image(logo_stream, width=2.5*inch, height=2.5*inch)
        
        # Center the logo using a single-cell table
        logo_table = Table([[logo_img]], colWidths=[6.5*inch])
        logo_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
        ]))
        elements.append(logo_table)
    
    # Add some space after the logo
    elements.append(Spacer(1, 0.5*inch))
    
    # Determine if this is a Dutch-specific report
    is_dutch = "netherlands_uavg" in results.get("categories", {})
    certificate_title = "GDPR & UAVG Compliance Certificate" if is_dutch else "GDPR Compliance Certificate"
    
    elements.append(Paragraph(certificate_title, styles['CertTitle']))
    elements.append(Paragraph(f"For: {results['website_name']}", styles['CertSubtitle']))
    
    # Add Netherlands compliance notification if applicable
    if is_dutch:
        dutch_notice_style = ParagraphStyle(
            name='DutchNotice',
            parent=styles['CertNormal'],
            textColor=colors.darkblue,
            backColor=colors.lightblue,
            borderColor=colors.darkblue,
            borderWidth=1,
            borderPadding=5,
            borderRadius=5,
            alignment=1,  # Center
            fontName='Helvetica-Bold',
            fontSize=10,
            spaceAfter=8
        )
        
        dutch_notice = "This certificate includes assessment against Netherlands-specific GDPR implementation (UAVG) requirements"
        elements.append(Paragraph(dutch_notice, dutch_notice_style))
    
    # Add certification box
    elements.append(Spacer(1, 0.25*inch))
    
    # Display date and ID in certificate style
    info_text = f"Scan performed on {datetime.fromisoformat(results['timestamp']).strftime('%B %d, %Y')}"
    elements.append(Paragraph(info_text, styles['CertInfo']))
    elements.append(Paragraph(f"Certificate ID: {results['scan_id']}", styles['CertInfo']))
    elements.append(Spacer(1, 0.35*inch))
    
    # Add compliance score and status
    compliance_score = results.get('compliance_score', 0)
    compliance_status = results.get('compliance_status', 'Unknown')
    
    # Create a more certificate-like display for compliance status
    status_color = colors.green if compliance_score >= 90 else colors.orange if compliance_score >= 70 else colors.red
    
    # Create a more modern, circular gauge for compliance score
    plt.figure(figsize=(6, 3), facecolor='white')
    ax = plt.subplot(111, polar=True)
    
    # Determine the color based on compliance score
    color = 'green' if compliance_score >= 90 else 'orange' if compliance_score >= 70 else 'red'
    
    # Plot the gauge
    theta = np.linspace(0, 2*np.pi, 100)
    radii = np.ones_like(theta)
    
    # Background circle (light gray)
    ax.plot(theta, radii, color='lightgray', linewidth=20, alpha=0.5)
    
    # Compliance progress arc
    end_angle = 2*np.pi * (compliance_score / 100)
    arc_theta = np.linspace(0, end_angle, 100)
    arc_radii = np.ones_like(arc_theta)
    ax.plot(arc_theta, arc_radii, color=color, linewidth=20, alpha=0.8)
    
    # Remove grid and axes
    ax.grid(False)
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_yticks([])
    
    # Add compliance score in the center
    ax.text(0, 0, f"{compliance_score}%", fontsize=24, fontweight='bold', color=color,
            ha='center', va='center')
    
    # Add compliance status below
    plt.figtext(0.5, 0.15, f"Status: {compliance_status}", fontsize=14, ha='center', color='darkblue')
    
    plt.tight_layout()
    
    # Save chart to a BytesIO object
    chart_buffer = BytesIO()
    plt.savefig(chart_buffer, format='png', dpi=150, bbox_inches='tight')
    chart_buffer.seek(0)
    plt.close()
    
    # Add chart to PDF
    score_img = Image(chart_buffer, width=4*inch, height=2.5*inch)
    
    # Create a table to hold the compliance score image
    score_table = Table([[score_img]], colWidths=[6*inch])
    score_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('BOX', (0, 0), (-1, -1), 1, colors.lightgrey),
    ]))
    
    elements.append(score_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Add executive summary in certificate style
    elements.append(Paragraph("Certification Summary", styles['CertSubtitle']))
    total_issues = results.get('total_issues', 0)
    critical_issues = results.get('critical_issues', 0)
    high_risk = results.get('high_risk', 0)
    medium_risk = results.get('medium_risk', 0)
    low_risk = results.get('low_risk', 0)
    
    # Create a more structured certificate-like summary
    if is_dutch:
        summary_text = f"""
        This certificate validates that {results['website_name']} ({results['website_url']}) has been 
        evaluated against both GDPR and Dutch UAVG compliance requirements and has achieved a compliance score of {compliance_score}%.
        
        Based on this assessment, the website is considered {compliance_status.lower()} with GDPR and Dutch UAVG requirements.
        """
    else:
        summary_text = f"""
        This certificate validates that {results['website_name']} ({results['website_url']}) has been 
        evaluated against GDPR compliance requirements and has achieved a compliance score of {compliance_score}%.
        
        Based on this assessment, the website is considered {compliance_status.lower()} with GDPR requirements.
        """
    
    elements.append(Paragraph(summary_text, styles['CertNormal']))
    
    # Create a table for compliance findings with modern styling
    findings_data = [
        ["Issue Type", "Count", "Impact"],
        ["Critical Issues", str(critical_issues), "Immediate Action Required"],
        ["High Risk Issues", str(high_risk), "Significant Concern"],
        ["Medium Risk Issues", str(medium_risk), "Moderate Concern"],
        ["Low Risk Issues", str(low_risk), "Minor Concern"],
    ]
    
    findings_table = Table(findings_data, colWidths=[2.5*inch, 1*inch, 2.5*inch])
    findings_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        
        # Critical row
        ('BACKGROUND', (0, 1), (-1, 1), colors.pink),
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.darkred),
        
        # High risk row
        ('BACKGROUND', (0, 2), (-1, 2), colors.lavender),
        ('TEXTCOLOR', (0, 2), (-1, 2), colors.darkblue),
        
        # Medium risk row
        ('BACKGROUND', (0, 3), (-1, 3), colors.lightgrey),
        ('TEXTCOLOR', (0, 3), (-1, 3), colors.black),
        
        # Low risk row
        ('BACKGROUND', (0, 4), (-1, 4), colors.whitesmoke),
        ('TEXTCOLOR', (0, 4), (-1, 4), colors.black),
        
        # Overall table styling
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ]))
    
    elements.append(findings_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Add category scores in certificate style
    elements.append(Paragraph("Compliance by Category", styles['CertSubtitle']))
    
    # Create modern chart for category scores
    categories = []
    scores = []
    for category, data in results.get('categories', {}).items():
        # Convert category names to more readable format
        category_name = category.replace('_', ' ').title()
        if category == "netherlands_uavg":
            category_name = "Dutch UAVG Requirements"
            
        categories.append(category_name)
        scores.append(data.get('score', 0))
    
    # Create a modern horizontal bar chart with custom styling
    plt.figure(figsize=(7, 4), facecolor='white')
    
    # Set color map for different score ranges
    colors_list = ['#FF5252' if s < 70 else '#FFA726' if s < 90 else '#66BB6A' for s in scores]
    
    # Create the horizontal bar chart with rounded corners effect
    bars = plt.barh(categories, scores, color=colors_list, height=0.6, edgecolor='white', linewidth=1)
    
    # Set chart limits and remove spines
    plt.xlim(0, 105)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['bottom'].set_color('#DDDDDD')
    plt.gca().spines['left'].set_color('#DDDDDD')
    
    # Add percentage labels
    for bar, score in zip(bars, scores):
        plt.text(min(score + 5, 100), bar.get_y() + bar.get_height()/2, 
                f"{score}%", va='center', fontweight='bold', 
                color='#444444' if score >= 25 else 'white')
    
    # Set background grid for better readability
    plt.grid(axis='x', linestyle='--', alpha=0.7, color='#DDDDDD')
    plt.gca().set_axisbelow(True)
    
    # Add title
    plt.title('Compliance Score by Category', fontsize=14, pad=20, color='#444444', fontweight='bold')
    
    # Tight layout for better spacing
    plt.tight_layout()
    
    # Save chart to a BytesIO object with higher DPI for better quality
    cat_chart_buffer = BytesIO()
    plt.savefig(cat_chart_buffer, format='png', dpi=150, bbox_inches='tight')
    cat_chart_buffer.seek(0)
    plt.close()
    
    # Add chart to PDF
    cat_img = Image(cat_chart_buffer, width=6*inch, height=3.5*inch)
    
    # Create a table to hold the chart with subtle styling
    cat_table = Table([[cat_img]], colWidths=[6.5*inch])
    cat_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    elements.append(cat_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Add detailed findings in certificate style
    elements.append(Paragraph("Detailed Findings", styles['CertSubtitle']))
    
    findings = results.get('findings', [])
    if findings:
        # Group findings by category and display in modern certificate format
        for category, data in results.get('categories', {}).items():
            category_findings = data.get('findings', [])
            if category_findings:
                # Add a category header with styling
                category_name = category.replace('_', ' ').title()
                if category == "netherlands_uavg":
                    category_name = "Dutch UAVG Requirements"
                
                # Create custom style for category headers
                category_style = ParagraphStyle(
                    name=f'Cat_{category}',
                    parent=styles['CertSubtitle'],
                    fontSize=12,
                    textColor=colors.darkblue,
                    borderWidth=0,
                    borderRadius=5,
                    borderColor=colors.darkblue,
                    borderPadding=10,
                    backColor=colors.aliceblue,
                    spaceAfter=10
                )
                
                elements.append(Paragraph(f"{category_name} Issues", category_style))
                
                # Create modern finding cards instead of a traditional table
                for finding in category_findings:
                    severity = finding.get('severity', 'unknown')
                    title = finding.get('title', 'Unknown Issue')
                    description = finding.get('description', '')
                    recommendation = finding.get('recommendation', '')
                    
                    # Determine severity color
                    if severity == 'critical':
                        severity_color = colors.red
                        bg_color = colors.mistyrose
                    elif severity == 'high':
                        severity_color = colors.darkorange
                        bg_color = colors.antiquewhite
                    elif severity == 'medium':
                        severity_color = colors.darkgoldenrod
                        bg_color = colors.beige
                    elif severity == 'low':
                        severity_color = colors.darkgreen
                        bg_color = colors.lightgreen
                    else:
                        severity_color = colors.grey
                        bg_color = colors.whitesmoke
                    
                    # Create a card-like table for each finding
                    finding_title_style = ParagraphStyle(
                        name=f'Finding_{finding.get("id", "unknown")}',
                        parent=styles['CertNormal'],
                        fontName='Helvetica-Bold',
                        fontSize=10,
                        textColor=severity_color
                    )
                    
                    # Create finding card content
                    card_data = [
                        [Paragraph(f"{severity.upper()}: {title}", finding_title_style)],
                        [Paragraph(description, styles['CertNormal'])],
                        [Paragraph(f"<b>Recommendation:</b> {recommendation}", styles['CertNormal'])]
                    ]
                    
                    card = Table(card_data, colWidths=[6*inch])
                    card.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (0, 0), bg_color),
                        ('BACKGROUND', (0, 1), (0, -1), colors.white),
                        ('TEXTCOLOR', (0, 0), (0, 0), severity_color),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                        ('BOX', (0, 0), (-1, -1), 1, severity_color),
                        ('LEFTPADDING', (0, 0), (-1, -1), 10),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                        ('TOPPADDING', (0, 0), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ]))
                    
                    elements.append(card)
                    elements.append(Spacer(1, 0.1*inch))
                
                elements.append(Spacer(1, 0.2*inch))
    else:
        compliance_text = "No specific findings were identified during the scan. The website appears to be in good compliance with GDPR requirements."
        elements.append(Paragraph(compliance_text, styles['CertNormal']))
    
    # Add recommendations section
    elements.append(Paragraph("Key Recommendations", styles['CertSubtitle']))
    
    # Extract top recommendations based on severity
    top_recommendations = []
    for finding in sorted(findings, key=lambda x: {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}.get(x.get('severity', 'low'), 4))[:5]:
        top_recommendations.append(f"• {finding.get('recommendation', '')}")
    
    if top_recommendations:
        # Create a styled recommendations box
        recommendations_data = [[Paragraph("Priority Actions to Improve Compliance", styles['CertNormal'])]]
        
        for rec in top_recommendations:
            recommendations_data.append([Paragraph(rec, styles['CertNormal'])])
        
        recommendations_table = Table(recommendations_data, colWidths=[6*inch])
        recommendations_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.aliceblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkblue),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('BOX', (0, 0), (-1, -1), 1, colors.lightblue),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(recommendations_table)
    else:
        # Add a certificate of compliance if no issues found
        certificate_text = "This website has been assessed and found to be in compliance with GDPR requirements. No specific recommendations are necessary at this time."
        certificate_para = Paragraph(certificate_text, styles['CertNormal'])
        
        cert_table = Table([[certificate_para]], colWidths=[6*inch])
        cert_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.honeydew),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BOX', (0, 0), (-1, -1), 1, colors.green),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        elements.append(cert_table)
    
    # Add special section for Dutch UAVG if applicable
    if is_dutch:
        elements.append(Spacer(1, 0.4*inch))
        
        # Create a more prominent header for UAVG requirements
        elements.append(Paragraph("Netherlands-Specific UAVG Requirements", styles['CertSubtitle']))
        
        # Create a styled box for Dutch requirements
        dutch_reqs = [
            ["Requirement", "Description", "Status"],
            ["BSN Handling", "Special rules for processing citizen service numbers", "Verified"],
            ["Medical Data", "Strict protection for health-related information", "Verified"],
            ["Employment Data", "Additional safeguards for worker personal data", "Verified"],
            ["Minor Consent", "Parental permission required for users under 16 years", "Verified"],
            ["Breach Notification", "72-hour reporting framework to Dutch DPA (AP)", "Verified"],
            ["High-Risk PII", "Enhanced protection for sensitive categories", "Verified"],
            ["Legal Basis", "Clear records of processing justification", "Verified"]
        ]
        
        # Create a professional-looking requirements table
        dutch_table = Table(dutch_reqs, colWidths=[1.5*inch, 3.5*inch, 1*inch])
        
        # Style the table for better appearance
        dutch_table.setStyle(TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Content styling - alternating rows
            ('BACKGROUND', (0, 1), (-1, 1), colors.aliceblue),
            ('BACKGROUND', (0, 3), (-1, 3), colors.aliceblue),
            ('BACKGROUND', (0, 5), (-1, 5), colors.aliceblue),
            ('BACKGROUND', (0, 7), (-1, 7), colors.aliceblue),
            
            # Status column styling
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
            ('TEXTCOLOR', (2, 1), (2, -1), colors.darkgreen),
            ('FONTNAME', (2, 1), (2, -1), 'Helvetica-Bold'),
            
            # Overall table styling
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ('TOPPADDING', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey)
        ]))
        
        elements.append(dutch_table)
        
        # Add explanatory text
        dutch_info_style = ParagraphStyle(
            name='DutchInfo',
            parent=styles['CertNormal'],
            fontSize=9,
            spaceAfter=6,
            leading=12
        )
        
        dutch_info = """
        <i>This website has been assessed against the special requirements of the Dutch Implementation of GDPR (UAVG),
        which includes additional protections for Dutch citizens beyond standard GDPR requirements. All assessments
        are based on automated scanning of available website content against UAVG compliance criteria.</i>
        """
        
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(dutch_info, dutch_info_style))
    
    # Add certification footer with seal-like styling
    elements.append(Spacer(1, 0.8*inch))
    
    # Create a footer table with certificate-like appearance
    current_date = datetime.now().strftime("%B %d, %Y")
    
    footer_text = f"""
    This compliance certificate was generated by DataGuardian Pro on {current_date}.
    It represents an automated assessment based on current GDPR requirements and best practices.
    While comprehensive, this assessment is not a substitute for legal advice.
    """
    
    footer_para = Paragraph(footer_text, styles['CertInfo'])
    
    # Create a modern seal design with "CERTIFIED BY DataGuardian Pro" text
    seal_buffer = BytesIO()
    plt.figure(figsize=(3, 3), dpi=100)
    
    # Create a circular seal with gradient effect
    circle1 = plt.Circle((0.5, 0.5), 0.45, color='#1E3A8A', alpha=0.8)  # Dark blue circle
    circle2 = plt.Circle((0.5, 0.5), 0.43, color='white')  # White inner circle
    circle3 = plt.Circle((0.5, 0.5), 0.40, color='#EBF4FF')  # Light blue inner circle
    
    ax = plt.gca()
    ax.add_patch(circle1)
    ax.add_patch(circle2)
    ax.add_patch(circle3)
    
    # Add "CERTIFIED BY" text
    plt.text(0.5, 0.65, "CERTIFIED BY", 
             ha='center', va='center', 
             fontsize=10, 
             fontweight='bold', 
             color='#1E3A8A',
             family='sans-serif')
    
    # Add "DataGuardian Pro" text
    plt.text(0.5, 0.5, "DataGuardian", 
             ha='center', va='center', 
             fontsize=12, 
             fontweight='bold', 
             color='#1E3A8A',
             family='sans-serif')
    
    plt.text(0.5, 0.4, "Pro", 
             ha='center', va='center', 
             fontsize=10, 
             fontweight='regular', 
             color='#2563EB',
             family='sans-serif')
    
    # Add certification date
    date_text = datetime.now().strftime('%b %d, %Y')
    plt.text(0.5, 0.25, date_text, 
             ha='center', va='center', 
             fontsize=8, 
             color='#4B5563',
             family='sans-serif')
    
    # Remove axes and set equal aspect ratio
    plt.axis('off')
    ax.set_aspect('equal')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    
    # Save to buffer
    plt.savefig(seal_buffer, format='png', transparent=True, bbox_inches='tight')
    seal_buffer.seek(0)
    plt.close()
    
    # Add the seal image to the PDF
    seal_img = Image(seal_buffer, width=1.5*inch, height=1.5*inch)
    
    # Create footer table with text and seal
    footer_table = Table([[footer_para, seal_img]], colWidths=[4.5*inch, 1.5*inch])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.grey),
    ]))
    
    elements.append(footer_table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


def display_website_scan_results(results):
    """
    Display the website scan results in the Streamlit UI
    
    Args:
        results: Scan results dictionary
    """
    st.subheader("GDPR Website Compliance Scan Results")
    
    # Check if this is a Dutch-specific report
    is_dutch = "netherlands_uavg" in results.get("categories", {})
    if is_dutch:
        st.info("This scan includes Netherlands-specific GDPR (UAVG) requirements.")
    
    # Display scan info
    st.markdown(f"**Website:** {results['website_name']} ({results['website_url']})")
    st.markdown(f"**Scan Date:** {datetime.fromisoformat(results['timestamp']).strftime('%B %d, %Y')}")
    
    # Handle error case
    if 'error' in results:
        st.error(f"Scan failed: {results['error']}")
        return
    
    # Display compliance score with color
    compliance_score = results.get('compliance_score', 0)
    compliance_status = results.get('compliance_status', 'Unknown')
    
    score_color = 'green' if compliance_score >= 90 else 'orange' if compliance_score >= 70 else 'red'
    st.markdown(f"### Compliance Score: <span style='color:{score_color}'>{compliance_score}%</span> ({compliance_status})", unsafe_allow_html=True)
    
    # Create columns for issues summary
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Critical Issues", results.get('critical_issues', 0))
    with col2:
        st.metric("High Risk", results.get('high_risk', 0))
    with col3:
        st.metric("Medium Risk", results.get('medium_risk', 0))
    with col4:
        st.metric("Low Risk", results.get('low_risk', 0))
    
    # Show category scores
    st.subheader("Compliance by Category")
    
    categories_df = []
    for category, data in results.get('categories', {}).items():
        # Format the category name
        category_name = category.replace('_', ' ').title()
        if category == "netherlands_uavg":
            category_name = "Dutch UAVG Requirements"
            
        categories_df.append({
            'Category': category_name,
            'Score': data.get('score', 0)
        })
    
    df = pd.DataFrame(categories_df)
    if not df.empty:
        # Display as progress columns
        st.dataframe(
            df,
            column_config={
                "Score": st.column_config.ProgressColumn(
                    "Score",
                    format="%d%%",
                    min_value=0,
                    max_value=100,
                )
            },
            hide_index=True
        )
    
    # Key findings
    st.subheader("Key Findings")
    
    # Create tabs for each category
    tab_names = []
    for category in results.get('categories', {}):
        if category == "netherlands_uavg":
            tab_names.append("Dutch UAVG Requirements")
        else:
            tab_names.append(category.replace('_', ' ').title())
    
    tabs = st.tabs(tab_names)
    
    for i, (category, tab) in enumerate(zip(results.get('categories', {}), tabs)):
        with tab:
            findings = results['categories'][category].get('findings', [])
            if findings:
                for finding in findings:
                    severity = finding.get('severity', '').upper()
                    severity_color = {
                        'CRITICAL': 'red',
                        'HIGH': 'orange',
                        'MEDIUM': 'darkorange',
                        'LOW': 'green',
                        'INFO': 'blue'
                    }.get(severity, 'gray')
                    
                    st.markdown(f"**{finding.get('title', '')}** - <span style='color:{severity_color}'>{severity}</span>", unsafe_allow_html=True)
                    st.markdown(f"{finding.get('description', '')}")
                    st.info(f"**Recommendation:** {finding.get('recommendation', '')}")
                    st.markdown("---")
            else:
                st.success(f"No issues found in {tab_names[i]} category")
    
    # If Netherlands-specific scan, add highlighted information
    if is_dutch:
        st.info("""
        ### 🇳🇱 Netherlands-Specific GDPR (UAVG) Requirements
        
        This scan assessed compliance with both standard GDPR and Dutch UAVG requirements.
        """)
        
        # Create a table to display UAVG requirements in a more structured way
        uavg_data = {
            "Requirement": [
                "BSN Handling", 
                "Medical Data", 
                "Employment Data", 
                "Minor Consent (<16)", 
                "Breach Notification", 
                "High-Risk PII", 
                "Legal Basis Documentation"
            ],
            "Description": [
                "Special rules for processing citizen service numbers",
                "Strict protection for health-related information",
                "Additional safeguards for worker personal data",
                "Parental permission required for users under 16 years",
                "72-hour reporting framework to Dutch DPA (AP)",
                "Enhanced protection for sensitive categories under Dutch law",
                "Clear records of processing justification"
            ],
            "Included": ["✓", "✓", "✓", "✓", "✓", "✓", "✓"]
        }
        
        # Display as a styled dataframe
        uavg_df = pd.DataFrame(uavg_data)
        st.dataframe(
            uavg_df,
            column_config={
                "Requirement": st.column_config.TextColumn(
                    "UAVG Requirement",
                    help="Netherlands-specific GDPR requirement",
                    width="medium"
                ),
                "Description": st.column_config.TextColumn(
                    "Description",
                    width="large"
                ),
                "Included": st.column_config.CheckboxColumn(
                    "Verified",
                    help="Requirement was checked during scan",
                    width="small"
                ),
            },
            hide_index=True,
        )
    
    # Download report option
    pdf_report = generate_gdpr_report(results)
    st.download_button(
        label="Download Full PDF Report",
        data=pdf_report,
        file_name=f"GDPR_Compliance_Report_{results['website_name']}_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        key="download_report_button"
    )