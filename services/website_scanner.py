"""
Website Scanner for GDPR Compliance

This module provides a scanner to analyze websites for GDPR compliance issues.
It checks for cookie consent banners, privacy policies, data processing agreements,
and other key GDPR requirements.
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
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
import matplotlib.pyplot as plt
import base64
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('website_scanner')

class WebsiteScanner:
    """GDPR-compliant website scanner"""
    
    def __init__(self, region="EU", progress_callback=None):
        """
        Initialize the scanner
        
        Args:
            region: The region to apply compliance rules for (EU, Global)
            progress_callback: Function to call with progress updates
        """
        self.region = region
        self.progress_callback = progress_callback
        self.scan_id = str(uuid.uuid4())
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        
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
            
            self.update_progress(80, 100, "Evaluating security practices...")
            self._check_security_practices(results, soup, html_content, response)
            
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
        
        # Calculate overall compliance score (weighted average of category scores)
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
        )
        
        results["compliance_score"] = int(weighted_sum)
        
        # Add compliance status
        if results["compliance_score"] >= 90:
            results["compliance_status"] = "Compliant"
        elif results["compliance_score"] >= 70:
            results["compliance_status"] = "Partially Compliant"
        else:
            results["compliance_status"] = "Non-Compliant"


def generate_gdpr_report(results):
    """
    Generate a PDF report for GDPR compliance scan results
    
    Args:
        results: The scan results dictionary
    
    Returns:
        BytesIO object containing the PDF report
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []
    
    # Add custom styles
    styles.add(ParagraphStyle(
        name='Title',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=12
    ))
    
    styles.add(ParagraphStyle(
        name='Subtitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10
    ))
    
    styles.add(ParagraphStyle(
        name='Normal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    ))
    
    # Add title
    elements.append(Paragraph(f"GDPR Compliance Report: {results['website_name']}", styles['Title']))
    elements.append(Paragraph(f"Scan Date: {datetime.fromisoformat(results['timestamp']).strftime('%B %d, %Y')}", styles['Normal']))
    elements.append(Paragraph(f"Scan ID: {results['scan_id']}", styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Add compliance score and status
    compliance_score = results.get('compliance_score', 0)
    compliance_status = results.get('compliance_status', 'Unknown')
    
    # Create chart for compliance score
    plt.figure(figsize=(5, 2))
    plt.barh(["Compliance Score"], [compliance_score], color='green' if compliance_score >= 70 else 'orange' if compliance_score >= 50 else 'red')
    plt.xlim(0, 100)
    for i, v in enumerate([compliance_score]):
        plt.text(v + 3, i, f"{v}%", va='center')
    plt.tight_layout()
    
    # Save chart to a BytesIO object
    chart_buffer = BytesIO()
    plt.savefig(chart_buffer, format='png')
    chart_buffer.seek(0)
    plt.close()
    
    # Add chart to PDF
    img = Image(chart_buffer, width=4*inch, height=1.5*inch)
    elements.append(img)
    elements.append(Spacer(1, 0.1*inch))
    
    # Add compliance status table
    status_color = 'green' if compliance_score >= 90 else 'orange' if compliance_score >= 70 else 'red'
    status_data = [
        ["Compliance Status", compliance_status]
    ]
    status_table = Table(status_data, colWidths=[2*inch, 3*inch])
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, 0), colors.black),
        ('BACKGROUND', (1, 0), (1, 0), getattr(colors, status_color)),
        ('TEXTCOLOR', (1, 0), (1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(status_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Add executive summary
    elements.append(Paragraph("Executive Summary", styles['Subtitle']))
    total_issues = results.get('total_issues', 0)
    critical_issues = results.get('critical_issues', 0)
    high_risk = results.get('high_risk', 0)
    medium_risk = results.get('medium_risk', 0)
    low_risk = results.get('low_risk', 0)
    
    summary_text = f"""
    This report presents the findings of a GDPR compliance scan conducted on {results['website_name']} ({results['website_url']}).
    The overall compliance score is {compliance_score}%, which indicates a {compliance_status.lower()} level of GDPR readiness.
    
    The scan identified a total of {total_issues} compliance issues:
    - {critical_issues} critical issues
    - {high_risk} high-risk issues
    - {medium_risk} medium-risk issues
    - {low_risk} low-risk issues
    
    Please review the detailed findings and recommendations below to improve GDPR compliance.
    """
    elements.append(Paragraph(summary_text, styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Add category scores
    elements.append(Paragraph("Compliance by Category", styles['Subtitle']))
    
    # Create chart for category scores
    categories = []
    scores = []
    for category, data in results.get('categories', {}).items():
        categories.append(category.replace('_', ' ').title())
        scores.append(data.get('score', 0))
    
    plt.figure(figsize=(6, 3))
    bars = plt.barh(categories, scores, color=['green' if s >= 90 else 'orange' if s >= 70 else 'red' for s in scores])
    plt.xlim(0, 100)
    for bar, score in zip(bars, scores):
        plt.text(score + 3, bar.get_y() + bar.get_height()/2, f"{score}%", va='center')
    plt.tight_layout()
    
    # Save chart to a BytesIO object
    cat_chart_buffer = BytesIO()
    plt.savefig(cat_chart_buffer, format='png')
    cat_chart_buffer.seek(0)
    plt.close()
    
    # Add chart to PDF
    cat_img = Image(cat_chart_buffer, width=5*inch, height=3*inch)
    elements.append(cat_img)
    elements.append(Spacer(1, 0.2*inch))
    
    # Add detailed findings
    elements.append(Paragraph("Detailed Findings", styles['Subtitle']))
    
    findings = results.get('findings', [])
    if findings:
        for category, data in results.get('categories', {}).items():
            category_findings = data.get('findings', [])
            if category_findings:
                elements.append(Paragraph(f"{category.replace('_', ' ').title()} Issues", styles['Subtitle']))
                
                findings_data = [["Severity", "Finding", "Recommendation"]]
                for finding in category_findings:
                    severity = finding.get('severity', 'unknown')
                    title = finding.get('title', 'Unknown Issue')
                    description = finding.get('description', '')
                    recommendation = finding.get('recommendation', '')
                    
                    findings_data.append([
                        severity.upper(),
                        f"{title}\n{description}",
                        recommendation
                    ])
                
                findings_table = Table(findings_data, colWidths=[1*inch, 2.5*inch, 2.5*inch])
                
                # Add styling to table
                table_style = [
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                    ('BACKGROUND', (0, 1), (0, -1), colors.whitesmoke),
                    ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                ]
                
                # Add severity-specific colors
                for i, row in enumerate(findings_data[1:], 1):
                    severity = row[0].lower()
                    if severity == 'critical':
                        table_style.append(('TEXTCOLOR', (0, i), (0, i), colors.red))
                    elif severity == 'high':
                        table_style.append(('TEXTCOLOR', (0, i), (0, i), colors.orange))
                    elif severity == 'medium':
                        table_style.append(('TEXTCOLOR', (0, i), (0, i), colors.darkgoldenrod))
                    elif severity == 'low':
                        table_style.append(('TEXTCOLOR', (0, i), (0, i), colors.green))
                
                findings_table.setStyle(TableStyle(table_style))
                elements.append(findings_table)
                elements.append(Spacer(1, 0.2*inch))
    else:
        elements.append(Paragraph("No specific findings were identified during the scan.", styles['Normal']))
    
    # Add recommendations section
    elements.append(Paragraph("Key Recommendations", styles['Subtitle']))
    
    # Extract top recommendations based on severity
    top_recommendations = []
    for finding in sorted(findings, key=lambda x: {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}.get(x.get('severity', 'low'), 4))[:5]:
        top_recommendations.append(f"• {finding.get('recommendation', '')}")
    
    if top_recommendations:
        for rec in top_recommendations:
            elements.append(Paragraph(rec, styles['Normal']))
    else:
        elements.append(Paragraph("No specific recommendations available.", styles['Normal']))
    
    # Add certification footer
    elements.append(Spacer(1, 0.5*inch))
    disclaimer_text = """
    Disclaimer: This report provides an assessment of GDPR compliance based on automated scanning. 
    It is not a substitute for legal advice. The findings should be reviewed by a qualified data protection professional.
    """
    elements.append(Paragraph(disclaimer_text, styles['Normal']))
    
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
        categories_df.append({
            'Category': category.replace('_', ' ').title(),
            'Score': data.get('score', 0)
        })
    
    df = pd.DataFrame(categories_df)
    if not df.empty:
        # Add color coding to scores
        def color_score(val):
            color = 'green' if val >= 90 else 'orange' if val >= 70 else 'red'
            return f'background-color: {color}; color: white'
        
        # Apply styling and display
        styled_df = df.style.format({'Score': '{:0.0f}%'}).applymap(color_score, subset=['Score'])
        st.dataframe(styled_df)
    
    # Key findings
    st.subheader("Key Findings")
    
    tabs = st.tabs([cat.replace('_', ' ').title() for cat in results.get('categories', {})])
    
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
                st.success(f"No issues found in {category.replace('_', ' ').title()} category")
    
    # Download report option
    pdf_report = generate_gdpr_report(results)
    st.download_button(
        label="Download Full PDF Report",
        data=pdf_report,
        file_name=f"GDPR_Compliance_Report_{results['website_name']}_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        key="download_report_button"
    )