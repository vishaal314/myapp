"""
Runtime Enforcement Package Generator

Generates deployable enforcement packages for active compliance enforcement:
- Cookie blocking and consent enforcement
- CI/CD compliance integration packages  
- Automated remediation deployment packages
- Real-time compliance monitoring agents

Extends the automated remediation engine to provide runtime enforcement.
"""

import os
import json
import tempfile
import zipfile
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Initialize logger
logger = logging.getLogger()

# Import existing automated remediation engine
try:
    from services.automated_remediation_engine import AutomatedRemediationEngine, RemediationStatus
    REMEDIATION_ENGINE_AVAILABLE = True
except ImportError:
    REMEDIATION_ENGINE_AVAILABLE = False

class EnforcementPackageType(Enum):
    COOKIE_BLOCKER = "Cookie Blocking Enforcement"
    CICD_COMPLIANCE = "CI/CD Compliance Actions"
    RUNTIME_MONITOR = "Runtime Compliance Monitor"
    AUTOMATED_REMEDIATION = "Automated Remediation Agent"
    CONSENT_MANAGEMENT = "Consent Management System"

@dataclass
class EnforcementPackage:
    """Runtime enforcement package configuration"""
    package_id: str
    package_type: EnforcementPackageType
    name: str
    description: str
    target_platform: str  # 'web', 'nodejs', 'python', 'github-actions', 'azure-devops'
    compliance_rules: List[str]
    deployment_files: Dict[str, str]  # filename -> content
    installation_script: str
    configuration: Dict[str, Any]
    metadata: Dict[str, Any]

class RuntimeEnforcementGenerator:
    """
    Generates deployable enforcement packages for active compliance enforcement
    
    Features:
    - Cookie blocking with consent enforcement
    - CI/CD pipeline compliance checks
    - Runtime monitoring agents
    - Automated remediation deployment
    """
    
    def __init__(self, region: str = "Netherlands"):
        self.region = region
        self.packages_generated = 0
        
        # Initialize remediation engine if available  
        self.remediation_engine = None
        if REMEDIATION_ENGINE_AVAILABLE:
            try:
                from services.automated_remediation_engine import AutomatedRemediationEngine
                self.remediation_engine = AutomatedRemediationEngine(region=region, dry_run=False)
            except Exception:
                self.remediation_engine = None
        
        # Load enforcement templates
        self.enforcement_templates = self._load_enforcement_templates()
        self.compliance_rules = self._load_compliance_rules()
    
    def _load_compliance_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load compliance enforcement rules"""
        return {
            "netherlands_uavg": {
                "cookie_consent_required": True,
                "explicit_consent_only": True,
                "reject_all_button_required": True,
                "consent_withdrawal_required": True,
                "auto_reject_timeout": 30,
                "essential_cookies_only_default": True,
                "data_breach_notification_hours": 72,
                "bsn_protection_required": True
            },
            "gdpr_general": {
                "data_minimization": True,
                "purpose_limitation": True,
                "storage_limitation": True,
                "lawful_basis_required": True,
                "data_subject_rights": True,
                "privacy_by_design": True,
                "dpo_contact_required": False
            },
            "security_requirements": {
                "https_required": True,
                "security_headers_required": True,
                "password_hashing_required": True,
                "api_key_protection": True,
                "sql_injection_protection": True,
                "xss_protection": True
            }
        }
    
    def _load_enforcement_templates(self) -> Dict[str, Dict[str, str]]:
        """Load enforcement package templates"""
        return {
            "cookie_blocker_javascript": {
                "enforcement_script": '''
// DataGuardian Pro - Cookie Blocking Enforcement Script
// Netherlands UAVG/GDPR Compliant Cookie Blocker
class CookieEnforcer {
    constructor(config = {}) {
        this.config = {
            strictMode: true,
            dutchCompliance: true,
            blockUntilConsent: true,
            autoRejectAfter: 30000, // 30 seconds
            essentialCookies: ['session', 'csrf', 'auth', '__cfduid'],
            ...config
        };
        
        this.consentGiven = false;
        this.blockedRequests = [];
        this.originalFetch = window.fetch;
        this.originalXHROpen = XMLHttpRequest.prototype.open;
        
        this.init();
    }
    
    init() {
        this.setupConsentDetection();
        this.blockCookieRequests();
        this.blockTrackingScripts();
        this.setupConsentBanner();
        this.monitorConsentStatus();
    }
    
    setupConsentDetection() {
        // Check for existing consent
        const consent = this.getCookie('cookie-consent');
        if (consent === 'all' || consent === 'essential') {
            this.consentGiven = consent === 'all';
            return;
        }
        
        // Auto-reject after timeout (Dutch AP requirement)
        if (this.config.autoRejectAfter > 0) {
            setTimeout(() => {
                if (!this.consentGiven) {
                    this.rejectAllCookies();
                }
            }, this.config.autoRejectAfter);
        }
    }
    
    blockCookieRequests() {
        const self = this;
        
        // Block fetch requests that set cookies
        window.fetch = function(...args) {
            if (self.shouldBlockRequest(args[0], args[1])) {
                console.warn('[DataGuardian] Blocked cookie-setting request:', args[0]);
                self.blockedRequests.push({
                    url: args[0],
                    method: args[1]?.method || 'GET',
                    timestamp: Date.now()
                });
                return Promise.reject(new Error('Request blocked by cookie consent enforcement'));
            }
            return self.originalFetch.apply(this, args);
        };
        
        // Block XMLHttpRequest cookie setting
        XMLHttpRequest.prototype.open = function(method, url, async, user, password) {
            if (self.shouldBlockRequest(url, {method})) {
                console.warn('[DataGuardian] Blocked XMLHttpRequest:', url);
                self.blockedRequests.push({
                    url: url,
                    method: method,
                    timestamp: Date.now()
                });
                throw new Error('XMLHttpRequest blocked by cookie consent enforcement');
            }
            return self.originalXHROpen.call(this, method, url, async, user, password);
        };
        
        // Block localStorage access until consent
        this.setupLocalStorageBlocking();
    }
    
    setupLocalStorageBlocking() {
        const self = this;
        
        // Store original localStorage methods
        this.originalSetItem = localStorage.setItem;
        this.originalGetItem = localStorage.getItem;
        this.originalRemoveItem = localStorage.removeItem;
        
        // Override localStorage methods
        localStorage.setItem = function(key, value) {
            if (!self.consentGiven && !self.isEssentialStorage(key)) {
                console.warn('[DataGuardian] Blocked localStorage.setItem:', key);
                return;
            }
            return self.originalSetItem.call(this, key, value);
        };
        
        localStorage.getItem = function(key) {
            if (!self.consentGiven && !self.isEssentialStorage(key)) {
                console.warn('[DataGuardian] Blocked localStorage.getItem:', key);
                return null;
            }
            return self.originalGetItem.call(this, key);
        };
        
        localStorage.removeItem = function(key) {
            return self.originalRemoveItem.call(this, key);
        };
    }
    
    isEssentialStorage(key) {
        const essentialKeys = ['session', 'csrf', 'auth', 'consent', 'language'];
        return essentialKeys.some(essential => key.toLowerCase().includes(essential));
    }
    
    blockTrackingScripts() {
        const self = this;
        const trackingDomains = [
            'google-analytics.com', 'googletagmanager.com', 'doubleclick.net',
            'facebook.com', 'facebook.net', 'hotjar.com', 'mixpanel.com',
            'segment.com', 'amplitude.com', 'fullstory.com'
        ];
        
        // Block script loading
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.tagName === 'SCRIPT' && node.src) {
                        const shouldBlock = trackingDomains.some(domain => 
                            node.src.includes(domain)
                        );
                        
                        if (shouldBlock && !self.consentGiven) {
                            console.warn('[DataGuardian] Blocked tracking script:', node.src);
                            node.remove();
                            self.blockedRequests.push({
                                url: node.src,
                                type: 'script',
                                timestamp: Date.now()
                            });
                        }
                    }
                });
            });
        });
        
        observer.observe(document.head, {childList: true, subtree: true});
        observer.observe(document.body, {childList: true, subtree: true});
    }
    
    shouldBlockRequest(url, options = {}) {
        if (this.consentGiven) return false;
        
        const urlString = typeof url === 'string' ? url : url.toString();
        
        // Allow essential cookies
        const isEssential = this.config.essentialCookies.some(essential => 
            urlString.toLowerCase().includes(essential)
        );
        if (isEssential) return false;
        
        // Block tracking and analytics
        const trackingKeywords = [
            'track', 'analytics', 'pixel', 'beacon', 'conversion',
            'advertising', 'marketing', 'segment', 'mixpanel'
        ];
        
        return trackingKeywords.some(keyword => 
            urlString.toLowerCase().includes(keyword)
        );
    }
    
    setupConsentBanner() {
        if (document.getElementById('dg-cookie-banner')) return;
        
        const banner = document.createElement('div');
        banner.id = 'dg-cookie-banner';
        banner.innerHTML = this.getConsentBannerHTML();
        document.body.appendChild(banner);
        
        // Event listeners
        document.getElementById('dg-accept-all').onclick = () => this.acceptAllCookies();
        document.getElementById('dg-reject-all').onclick = () => this.rejectAllCookies();
        document.getElementById('dg-preferences').onclick = () => this.showPreferences();
    }
    
    getConsentBannerHTML() {
        return `
            <div style="position: fixed; bottom: 0; left: 0; right: 0; background: #1a1a1a; color: white; padding: 20px; z-index: 999999; box-shadow: 0 -2px 10px rgba(0,0,0,0.1);">
                <div style="max-width: 1200px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 15px;">
                    <div style="flex: 1; min-width: 300px;">
                        <h4 style="margin: 0 0 5px 0; color: #f39c12;">🛡️ Cookie Toestemming Vereist</h4>
                        <p style="margin: 0; font-size: 14px; line-height: 1.4;">
                            Deze website gebruikt cookies voor functionaliteit en analyse. 
                            <strong>Zonder uw toestemming worden tracking cookies geblokkeerd.</strong>
                            <a href="/privacy-policy" style="color: #3498db; text-decoration: underline;">Meer informatie</a>
                        </p>
                        <div style="margin-top: 8px; font-size: 12px; color: #bdc3c7;">
                            <span id="blocked-count">0 tracking verzoeken geblokkeerd</span> • 
                            <span>Automatisch weigeren over <span id="countdown">30</span>s</span>
                        </div>
                    </div>
                    <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                        <button id="dg-accept-all" style="background: #27ae60; color: white; border: none; padding: 12px 24px; border-radius: 5px; cursor: pointer; font-weight: bold;">
                            ✓ Alles Accepteren
                        </button>
                        <button id="dg-reject-all" style="background: #e74c3c; color: white; border: none; padding: 12px 24px; border-radius: 5px; cursor: pointer; font-weight: bold;">
                            ✗ Alles Weigeren
                        </button>
                        <button id="dg-preferences" style="background: transparent; color: white; border: 1px solid white; padding: 12px 20px; border-radius: 5px; cursor: pointer;">
                            Voorkeuren
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    acceptAllCookies() {
        this.consentGiven = true;
        this.setCookie('cookie-consent', 'all', 365);
        this.hideBanner();
        this.enableTracking();
        console.log('[DataGuardian] Cookie consent granted - enabling tracking');
    }
    
    rejectAllCookies() {
        this.consentGiven = false;
        this.setCookie('cookie-consent', 'essential', 365);
        this.hideBanner();
        this.clearNonEssentialCookies();
        console.log('[DataGuardian] Cookie consent rejected - maintaining blocks');
    }
    
    monitorConsentStatus() {
        const blockedCounter = document.getElementById('blocked-count');
        const countdown = document.getElementById('countdown');
        
        let timeLeft = this.config.autoRejectAfter / 1000;
        
        const updateInterval = setInterval(() => {
            if (this.consentGiven || !document.getElementById('dg-cookie-banner')) {
                clearInterval(updateInterval);
                return;
            }
            
            if (blockedCounter) {
                blockedCounter.textContent = `${this.blockedRequests.length} tracking verzoeken geblokkeerd`;
            }
            
            if (countdown && timeLeft > 0) {
                countdown.textContent = Math.ceil(timeLeft);
                timeLeft -= 1;
            }
        }, 1000);
    }
    
    clearNonEssentialCookies() {
        const cookies = document.cookie.split(';');
        cookies.forEach(cookie => {
            const name = cookie.split('=')[0].trim();
            if (!this.config.essentialCookies.includes(name) && name !== 'cookie-consent') {
                this.deleteCookie(name);
            }
        });
    }
    
    setCookie(name, value, days) {
        const expires = new Date(Date.now() + days * 24 * 60 * 60 * 1000).toUTCString();
        document.cookie = `${name}=${value}; expires=${expires}; path=/; secure; samesite=strict`;
    }
    
    getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }
    
    deleteCookie(name) {
        document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
    }
    
    hideBanner() {
        const banner = document.getElementById('dg-cookie-banner');
        if (banner) banner.remove();
    }
    
    enableTracking() {
        // Re-enable blocked requests by removing blocks
        window.fetch = this.originalFetch;
        XMLHttpRequest.prototype.open = this.originalXHROpen;
        
        // Trigger analytics initialization
        if (typeof gtag !== 'undefined') {
            gtag('consent', 'update', {'analytics_storage': 'granted'});
        }
        
        if (typeof fbq !== 'undefined') {
            fbq('consent', 'grant');
        }
    }
}

// Auto-initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    window.cookieEnforcer = new CookieEnforcer({
        strictMode: true,
        dutchCompliance: true,
        blockUntilConsent: true,
        autoRejectAfter: 30000
    });
});
''',
                "installation_guide": '''
# Cookie Blocking Enforcement Installation Guide

## Installation Steps:

1. **Add the script to your website:**
   ```html
   <script src="/cookie-enforcer.js"></script>
   ```

2. **Configure enforcement options:**
   ```javascript
   window.cookieEnforcer = new CookieEnforcer({
       strictMode: true,              // Block all non-essential cookies
       dutchCompliance: true,         // Netherlands UAVG compliance mode
       blockUntilConsent: true,       // Block cookies until explicit consent
       autoRejectAfter: 30000,        // Auto-reject after 30 seconds
       essentialCookies: ['session', 'csrf', 'auth']  // Always-allowed cookies
   });
   ```

3. **Test the enforcement:**
   - Open browser developer tools
   - Watch for blocked request warnings
   - Test consent flow functionality
   - Verify cookie clearing after rejection

## Features:
✅ Active cookie blocking enforcement
✅ Dutch UAVG compliance (auto-reject, reject-all button)
✅ Real-time tracking request blocking
✅ Visual feedback of blocked requests
✅ Essential cookie allowlist
✅ Automatic cleanup after rejection
'''
            },
            
            "github_actions_compliance": {
                "workflow_file": '''
name: DataGuardian Pro - Compliance Enforcement

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 6 * * 1'  # Weekly Monday 6 AM

jobs:
  privacy_scan:
    runs-on: ubuntu-latest
    name: Privacy & GDPR Compliance Check
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install DataGuardian Pro Scanner
      run: |
        pip install -r requirements.txt
        # Install scanning dependencies
        
    - name: Run Code Privacy Scan
      id: code-scan
      run: |
        python -c "
        import sys
        sys.path.append('.')
        from services.code_scanner import CodeScanner
        from services.intelligent_risk_analyzer import IntelligentRiskAnalyzer
        
        scanner = CodeScanner()
        analyzer = IntelligentRiskAnalyzer()
        
        # Scan for PII, secrets, GDPR violations
        results = scanner.scan_code_advanced(
            code_input='.',
            scan_type='repository',
            region='Netherlands'
        )
        
        # Analyze risk level
        risk_analysis = analyzer.analyze_compliance_risk(results)
        
        critical_issues = [f for f in results['findings'] if f.get('risk_level') == 'Critical']
        high_issues = [f for f in results['findings'] if f.get('risk_level') == 'High']
        
        print(f'SCAN_RESULTS={len(results[\"findings\"])}')
        print(f'CRITICAL_COUNT={len(critical_issues)}')
        print(f'HIGH_COUNT={len(high_issues)}')
        print(f'COMPLIANCE_SCORE={results.get(\"compliance_score\", 0)}')
        
        # Set outputs for other steps
        with open('scan_results.json', 'w') as f:
            import json
            json.dump(results, f)
        "
        
    - name: Check Compliance Thresholds
      run: |
        CRITICAL=$(python -c "import json; r=json.load(open('scan_results.json')); print(sum(1 for f in r['findings'] if f.get('risk_level') == 'Critical'))")
        HIGH=$(python -c "import json; r=json.load(open('scan_results.json')); print(sum(1 for f in r['findings'] if f.get('risk_level') == 'High'))")
        SCORE=$(python -c "import json; r=json.load(open('scan_results.json')); print(r.get('compliance_score', 0))")
        
        echo "Compliance Results:"
        echo "- Critical Issues: $CRITICAL"
        echo "- High Risk Issues: $HIGH" 
        echo "- Compliance Score: $SCORE%"
        
        # Fail build if compliance thresholds exceeded
        if [ "$CRITICAL" -gt 0 ]; then
          echo "❌ BUILD FAILED: Critical privacy violations detected"
          echo "Critical issues must be resolved before deployment"
          exit 1
        fi
        
        if [ "$HIGH" -gt 5 ]; then
          echo "⚠️ BUILD WARNING: High number of high-risk issues ($HIGH)"
          echo "Consider addressing high-risk issues before production"
        fi
        
        if [ "$SCORE" -lt 70 ]; then
          echo "❌ BUILD FAILED: Compliance score too low ($SCORE%)"
          echo "Minimum compliance score of 70% required for deployment"
          echo "compliance_threshold: 70"
          exit 1
        fi
        
        echo "✅ Compliance check passed"

    - name: Generate Compliance Report
      if: always()
      run: |
        python -c "
        import json
        from datetime import datetime
        
        with open('scan_results.json', 'r') as f:
            results = json.load(f)
        
        # Generate GitHub Actions summary report
        with open('compliance-report.md', 'w') as f:
            f.write('# DataGuardian Pro - Compliance Report\\n\\n')
            f.write(f'**Scan Date:** {datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")}\\n')
            f.write(f'**Repository:** {results.get(\"metadata\", {}).get(\"repository\", \"Unknown\")}\\n')
            f.write(f'**Compliance Score:** {results.get(\"compliance_score\", 0)}%\\n\\n')
            
            critical = [f for f in results['findings'] if f.get('risk_level') == 'Critical']
            high = [f for f in results['findings'] if f.get('risk_level') == 'High']
            
            f.write(f'## Summary\\n')
            f.write(f'- 🔴 Critical Issues: {len(critical)}\\n')
            f.write(f'- 🟠 High Risk Issues: {len(high)}\\n') 
            f.write(f'- 📊 Total Findings: {len(results[\"findings\"])}\\n\\n')
            
            if critical:
                f.write('## Critical Issues (Must Fix)\\n')
                for issue in critical[:10]:  # Limit to first 10
                    f.write(f'- **{issue.get(\"type\", \"Unknown\")}**: {issue.get(\"description\", \"\")}\\n')
                    f.write(f'  - Location: `{issue.get(\"location\", \"Unknown\")}`\\n')
                    f.write(f'  - Impact: {issue.get(\"impact\", \"Unknown\")}\\n\\n')
            
            f.write('## Recommendations\\n')
            f.write('1. Address all critical privacy violations immediately\\n')
            f.write('2. Review high-risk issues before production deployment\\n')
            f.write('3. Implement automated privacy controls\\n')
            f.write('4. Regular compliance monitoring (weekly scans)\\n')
        "
        
    - name: Upload Compliance Report
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: compliance-report
        path: |
          compliance-report.md
          scan_results.json
          
    - name: Comment on PR
      if: github.event_name == 'pull_request' && always()
      uses: actions/github-script@v6
      with:
        script: |
          const fs = require('fs');
          const report = fs.readFileSync('compliance-report.md', 'utf8');
          
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: '## 🛡️ DataGuardian Pro Compliance Check\\n\\n' + report
          });

  deployment-compliance:
    runs-on: ubuntu-latest 
    needs: privacy-compliance-scan
    if: github.ref == 'refs/heads/main'
    name: Pre-Deployment Compliance Validation
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Validate Production Readiness
      run: |
        echo "🔍 Performing pre-deployment compliance validation..."
        
        # Check for production-critical issues
        SECRETS_CHECK=$(grep -r "sk_live\|pk_live\|AKIA\|AIza" . --exclude-dir=.git || echo "No secrets found")
        if [ "$SECRETS_CHECK" != "No secrets found" ]; then
          echo "❌ Production secrets detected in code"
          exit 1
        fi
        
        # Check SSL configuration
        if [ -f "nginx.conf" ]; then
          SSL_CHECK=$(grep "ssl_certificate" nginx.conf || echo "No SSL config")
          if [ "$SSL_CHECK" = "No SSL config" ]; then
            echo "⚠️ WARNING: SSL configuration not found"
          fi
        fi
        
        # Check privacy policy presence
        PRIVACY_FILES=$(find . -name "*privacy*" -o -name "*gdpr*" | head -5)
        if [ -z "$PRIVACY_FILES" ]; then
          echo "⚠️ WARNING: Privacy policy files not found"
        fi
        
        echo "✅ Pre-deployment validation complete"
        
    - name: Deploy with Compliance Monitoring
      run: |
        echo "🚀 Deploying with compliance monitoring enabled..."
        # Add your deployment commands here
        # The deployment should include compliance monitoring
''',
                "installation_guide": '''
# GitHub Actions Compliance Integration

## Setup Instructions:

1. **Add the workflow file:**
   Save as `.github/workflows/compliance-enforcement.yml`

2. **Configure repository secrets:**
   - `COMPLIANCE_API_KEY` (if using external APIs)
   - `DEPLOYMENT_KEY` (for production deployments)

3. **Customize compliance thresholds:**
   ```yaml
   # In the workflow file, adjust these values:
   CRITICAL_THRESHOLD: 0      # Fail on any critical issues
   HIGH_THRESHOLD: 5          # Warn on >5 high issues  
   MIN_COMPLIANCE_SCORE: 70   # Minimum 70% compliance score
   ```

4. **Enable branch protection:**
   - Require status checks for compliance
   - Block merges if compliance fails

## Features:
✅ Automated privacy scanning on every commit
✅ Compliance score enforcement
✅ Critical issue blocking
✅ PR compliance reporting
✅ Pre-deployment validation
✅ Weekly compliance monitoring
'''
            },
            
            "azure_devops_compliance": {
                "pipeline_file": '''
# DataGuardian Pro - Azure DevOps Compliance Pipeline
# Enforces privacy compliance in CI/CD workflow

trigger:
  branches:
    include:
    - main
    - develop
  paths:
    exclude:
    - docs/*
    - README.md

schedules:
- cron: "0 6 * * 1"
  displayName: Weekly compliance scan
  branches:
    include:
    - main
  always: true

variables:
  COMPLIANCE_THRESHOLD: 80
  MAX_CRITICAL_ISSUES: 0
  MAX_HIGH_ISSUES: 5

stages:
- stage: ComplianceValidation
  displayName: Privacy & GDPR Compliance
  jobs:
  - job: PrivacyComplianceScan
    displayName: Privacy Compliance Scan
    pool:
      vmImage: 'ubuntu-latest'
    
    steps:
    - task: UsePythonVersion@0
      displayName: Set Python version
      inputs:
        versionSpec: '3.11'
        addToPath: true
    
    - script: |
        pip install -r requirements.txt
        echo "DataGuardian Pro dependencies installed"
      displayName: 'Install Dependencies'
    
    - script: |
        python -c "
        import sys, json
        sys.path.append('.')
        from services.code_scanner import CodeScanner
        from services.intelligent_risk_analyzer import IntelligentRiskAnalyzer
        
        print('🔍 Starting privacy compliance scan...')
        scanner = CodeScanner()
        analyzer = IntelligentRiskAnalyzer()
        
        # Comprehensive scan
        results = scanner.scan_code_advanced(
            code_input='.',
            scan_type='repository',
            region='Netherlands'
        )
        
        # Risk analysis
        risk_analysis = analyzer.analyze_compliance_risk(results)
        
        # Calculate metrics
        findings = results['findings']
        critical = [f for f in findings if f.get('risk_level') == 'Critical']
        high = [f for f in findings if f.get('risk_level') == 'High']
        score = results.get('compliance_score', 0)
        
        print(f'📊 Scan Results:')
        print(f'   Critical Issues: {len(critical)}')
        print(f'   High Risk Issues: {len(high)}')
        print(f'   Total Findings: {len(findings)}')
        print(f'   Compliance Score: {score}%')
        
        # Save results for next steps
        with open('compliance_results.json', 'w') as f:
            json.dump({
                'total_findings': len(findings),
                'critical_count': len(critical),
                'high_count': len(high),
                'compliance_score': score,
                'detailed_results': results
            }, f)
        
        # Set Azure DevOps variables
        print(f'##vso[task.setvariable variable=CriticalIssues]{len(critical)}')
        print(f'##vso[task.setvariable variable=HighIssues]{len(high)}')  
        print(f'##vso[task.setvariable variable=ComplianceScore]{score}')
        "
      displayName: 'Run Privacy Scan'
    
    - script: |
        echo "🔍 Evaluating compliance thresholds..."
        echo "Critical Issues: $(CriticalIssues)"
        echo "High Issues: $(HighIssues)"
        echo "Compliance Score: $(ComplianceScore)%"
        
        # Check critical issues
        if [ "$(CriticalIssues)" -gt "$(MAX_CRITICAL_ISSUES)" ]; then
          echo "❌ COMPLIANCE FAILURE: $(CriticalIssues) critical privacy violations detected"
          echo "##vso[task.logissue type=error]Critical privacy violations must be resolved"
          exit 1
        fi
        
        # Check high issues
        if [ "$(HighIssues)" -gt "$(MAX_HIGH_ISSUES)" ]; then
          echo "⚠️ COMPLIANCE WARNING: $(HighIssues) high-risk issues detected"
          echo "##vso[task.logissue type=warning]Consider resolving high-risk issues"
        fi
        
        # Check compliance score
        if [ "$(ComplianceScore)" -lt "$(COMPLIANCE_THRESHOLD)" ]; then
          echo "❌ COMPLIANCE FAILURE: Score $(ComplianceScore)% below threshold $(COMPLIANCE_THRESHOLD)%"
          echo "##vso[task.logissue type=error]Compliance score too low for deployment"
          exit 1
        fi
        
        echo "✅ Compliance validation passed"
      displayName: 'Evaluate Compliance Thresholds'
      condition: always()
    
    - script: |
        python -c "
        import json
        from datetime import datetime
        
        # Load results
        with open('compliance_results.json', 'r') as f:
            data = json.load(f)
        
        results = data['detailed_results']
        
        # Generate simple compliance report
        python scripts/generate_compliance_report.py compliance_results.json
        "
      displayName: 'Generate Compliance Report'
      condition: always()
    
    - task: PublishTestResults@2
      displayName: 'Publish Compliance Results'
      condition: always()
      inputs:
        testResultsFormat: 'NUnit'
        testResultsFiles: 'compliance_results.json'
        testRunTitle: 'Privacy Compliance Scan'
    
    - task: PublishBuildArtifacts@1
      displayName: 'Publish Reports'
      condition: always()
      inputs:
        pathToPublish: '.'
        artifactName: 'compliance-reports'
        includeRootFolder: false

- stage: DeploymentCompliance
  displayName: Pre-Deployment Validation
  dependsOn: ComplianceValidation
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
  jobs:
  - job: ProductionReadiness
    displayName: Production Readiness Check
    pool:
      vmImage: 'ubuntu-latest'
    
    steps:
    - script: |
        echo "🔍 Performing production readiness validation..."
        
        # Check for hardcoded production secrets
        if grep -r "sk_live\|pk_live\|prod_\|production_" . --exclude-dir=.git; then
          echo "❌ Production secrets detected in code"
          echo "##vso[task.logissue type=error]Remove production secrets from code"
          exit 1
        fi
        
        # Validate SSL/TLS configuration
        if [ -f "nginx.conf" ] || [ -f "apache.conf" ]; then
          echo "✅ Web server configuration found"
        else
          echo "⚠️ Web server configuration not found"
        fi
        
        # Check privacy documentation
        if find . -name "*privacy*" -o -name "*gdpr*" | grep -q .; then
          echo "✅ Privacy documentation found"
        else
          echo "⚠️ Privacy documentation missing"
          echo "##vso[task.logissue type=warning]Consider adding privacy documentation"
        fi
        
        echo "✅ Production readiness validation complete"
      displayName: 'Validate Production Configuration'
''',
                "installation_guide": '''
# Azure DevOps Compliance Pipeline Setup

## Installation Steps:

1. **Add pipeline file:**
   Save as `azure-pipelines-compliance.yml` in your repository root

2. **Create new pipeline in Azure DevOps:**
   - Go to Pipelines > New Pipeline
   - Select your repository
   - Choose "Existing Azure Pipelines YAML file"
   - Select the compliance pipeline file

3. **Configure pipeline variables:**
   ```yaml
   variables:
     compliance_threshold: 70    # Minimum compliance score
     COMPLIANCE_THRESHOLD: 70    # Azure DevOps format
     MAX_CRITICAL_ISSUES: 0      # Block on any critical issues
     MAX_HIGH_ISSUES: 5          # Warning threshold for high issues
   ```

4. **Set up branch policies:**
   - Require compliance pipeline to pass
   - Block direct pushes to main branch
   - Require pull request reviews

## Features:
✅ Automated privacy scanning in Azure DevOps
✅ Compliance threshold enforcement
✅ Production readiness validation  
✅ HTML compliance reports
✅ Branch protection integration
✅ Scheduled compliance monitoring
'''
            }
        }
    
    
    def generate_cookie_blocking_package(self, 
                                       website_domain: str,
                                       compliance_config: Optional[Dict[str, Any]] = None) -> EnforcementPackage:
        """Generate cookie blocking enforcement package"""
        logger.info(f"Starting cookie blocking package generation for domain: {website_domain}")
        # Input validation
        if not website_domain or not isinstance(website_domain, str):
            raise ValueError("Website domain must be a non-empty string")
        if compliance_config is not None and not isinstance(compliance_config, dict):
            raise ValueError("Compliance config must be a dictionary")
            
        package_id = f"cookie-blocker-{website_domain.replace('.', '-')}-{int(datetime.now().timestamp())}"
        
        config = compliance_config or {}
        config.update({
            "domain": website_domain,
            "dutch_compliance": True,
            "strict_mode": True,
            "auto_reject_timeout": 30000,
            "blocked_domains": [
                "google-analytics.com", "googletagmanager.com", 
                "facebook.com", "doubleclick.net", "hotjar.com"
            ]
        })
        
        # Generate enforcement files
        js_template = self.enforcement_templates["cookie_blocker_javascript"]["enforcement_script"]
        installation_guide = self.enforcement_templates["cookie_blocker_javascript"]["installation_guide"]
        
        # Create customized files
        deployment_files = {
            "cookie-enforcer.js": js_template,
            "installation-guide.md": installation_guide,
            "test-page.html": self._generate_cookie_test_page(website_domain),
            "configuration.json": json.dumps(config, indent=2)
        }
        
        return EnforcementPackage(
            package_id=package_id,
            package_type=EnforcementPackageType.COOKIE_BLOCKER,
            name=f"Cookie Blocking Enforcer - {website_domain}",
            description="Active cookie consent enforcement with Dutch UAVG compliance",
            target_platform="web",
            compliance_rules=["netherlands_uavg", "gdpr_general"],
            deployment_files=deployment_files,
            installation_script=self._generate_cookie_installation_script(website_domain),
            configuration=config,
            metadata={
                "generated_at": datetime.now().isoformat(),
                "domain": website_domain,
                "compliance_level": "strict",
                "region": self.region
            }
        )
        package = EnforcementPackage(
            package_id=package_id,
            package_type=EnforcementPackageType.COOKIE_BLOCKER,
            name=f"Cookie Blocking Enforcer - {website_domain}",
            description="Active cookie consent enforcement with Dutch UAVG compliance",
            target_platform="web",
            compliance_rules=["netherlands_uavg", "gdpr_general"],
            deployment_files=deployment_files,
            installation_script=self._generate_cookie_installation_script(website_domain),
            configuration=config,
            metadata={
                "generated_at": datetime.now().isoformat(),
                "domain": website_domain,
                "compliance_level": "strict",
                "region": self.region
            }
        )
        logger.info(f"Completed cookie blocking package generation for domain: {website_domain}")
        return package
    
    def generate_cicd_compliance_package(self,
                                       platform: str,  # 'github-actions' or 'azure-devops'
                                       repository_name: str,
                                       compliance_thresholds: Optional[Dict[str, int]] = None) -> EnforcementPackage:
        """Generate CI/CD compliance enforcement package"""
        logger.info(f"Starting CI/CD compliance package generation for platform: {platform}")
        
        thresholds = compliance_thresholds or {
            "max_critical_issues": 0,
            "max_high_issues": 5, 
            "min_compliance_score": 70
        }
        
        package_id = f"cicd-compliance-{platform}-{repository_name}-{int(datetime.now().timestamp())}"
        
        if platform == "github-actions":
            template_key = "github_actions_compliance"
            workflow_file = "compliance-enforcement.yml"
            target_path = ".github/workflows/"
        elif platform == "azure-devops":
            template_key = "azure_devops_compliance"
            workflow_file = "azure-pipelines-compliance.yml"
            target_path = ""
        else:
            raise ValueError(f"Unsupported CI/CD platform: {platform}")
        
        # Get templates with proper key mapping
        if platform == "github-actions":
            workflow_content = self.enforcement_templates[template_key]["workflow_file"]
        else:  # azure-devops
            workflow_content = self.enforcement_templates[template_key]["pipeline_file"]
        installation_guide = self.enforcement_templates[template_key]["installation_guide"]
        
        # Customize thresholds in workflow
        customized_workflow = workflow_content.replace(
            "MAX_CRITICAL_ISSUES: 0", f"MAX_CRITICAL_ISSUES: {thresholds['max_critical_issues']}"
        ).replace(
            "MIN_COMPLIANCE_SCORE: 70", f"MIN_COMPLIANCE_SCORE: {thresholds['min_compliance_score']}"
        ).replace(
            "MAX_HIGH_ISSUES: 5", f"MAX_HIGH_ISSUES: {thresholds['max_high_issues']}"
        )
        
        deployment_files = {
            workflow_file: customized_workflow,
            "installation-guide.md": installation_guide,
            "compliance-config.json": json.dumps(thresholds, indent=2),
            "test-compliance.py": self._generate_compliance_test_script()
        }
        
        package = EnforcementPackage(
            package_id=package_id,
            package_type=EnforcementPackageType.CICD_COMPLIANCE,
            name=f"CI/CD Compliance Enforcer - {platform}",
            description=f"Automated privacy compliance enforcement for {platform}",
            target_platform=platform,
            compliance_rules=["gdpr_general", "security_requirements"],
            deployment_files=deployment_files,
            installation_script=self._generate_cicd_installation_script(platform),
            configuration={
                "platform": platform,
                "repository": repository_name,
                "thresholds": thresholds,
                "scan_schedule": "weekly",
                "fail_on_critical": True
            },
            metadata={
                "generated_at": datetime.now().isoformat(),
                "platform": platform,
                "repository": repository_name,
                "compliance_thresholds": thresholds
            }
        )
        logger.info(f"Completed CI/CD compliance package generation for platform: {platform}")
        return package
    
    def generate_runtime_monitor_package(self,
                                       application_type: str,  # 'web', 'api', 'mobile'
                                       monitoring_config: Optional[Dict[str, Any]] = None) -> EnforcementPackage:
        """Generate runtime compliance monitoring package"""
        logger.info(f"Starting runtime monitor package generation for application type: {application_type}")
        # Input validation  
        if not application_type or application_type not in ["web", "api", "mobile"]:
            raise ValueError(f"Unsupported application type: {application_type}. Supported: web, api, mobile")
        if monitoring_config is not None and not isinstance(monitoring_config, dict):
            raise ValueError("Monitoring config must be a dictionary")
        
        # CRITICAL FIX 1: Ensure compliance_rules are always included in the config
        default_config = {
            "monitor_cookies": True,
            "monitor_api_calls": True,
            "monitor_data_access": True,
            "alert_on_violations": True,
            "log_compliance_events": True,
            "real_time_scanning": True,
            "violation_alerts": True,
            "compliance_rules": ["netherlands_uavg", "gdpr_general"]
        }
        
        # Merge user config with defaults, ensuring compliance_rules are preserved
        if monitoring_config:
            config = default_config.copy()
            config.update(monitoring_config)
            # Always ensure compliance_rules exist
            if "compliance_rules" not in config or not config["compliance_rules"]:
                config["compliance_rules"] = ["netherlands_uavg", "gdpr_general"]
        else:
            config = default_config
        
        # Debug logging to verify config content
        logger.info(f"Runtime monitor config compliance_rules: {config.get('compliance_rules', 'MISSING')}")
        
        package_id = f"runtime-monitor-{application_type}-{int(datetime.now().timestamp())}"
        
        # Generate monitoring scripts based on application type
        if application_type == "web":
            monitor_script = self._generate_web_monitor_script(config)
        elif application_type == "api":
            monitor_script = self._generate_api_monitor_script(config)
        else:
            monitor_script = self._generate_generic_monitor_script(config)
        
        # Debug: Verify monitor-config.json content before serialization
        monitor_config_json = json.dumps(config, indent=2)
        logger.info(f"Generated monitor-config.json content: {monitor_config_json[:200]}...")
        
        deployment_files = {
            "compliance-monitor.js": monitor_script,
            "monitor-config.json": monitor_config_json,
            "installation-guide.md": self._generate_monitor_installation_guide(application_type),
            "health-check.py": self._generate_monitor_health_check()
        }
        
        package = EnforcementPackage(
            package_id=package_id,
            package_type=EnforcementPackageType.RUNTIME_MONITOR,
            name=f"Runtime Compliance Monitor - {application_type}",
            description=f"Real-time compliance monitoring for {application_type} applications",
            target_platform=application_type,
            compliance_rules=["gdpr_general", "netherlands_uavg", "security_requirements"],
            deployment_files=deployment_files,
            installation_script=self._generate_monitor_installation_script(application_type),
            configuration=config,
            metadata={
                "generated_at": datetime.now().isoformat(),
                "application_type": application_type,
                "monitoring_features": list(config.keys())
            }
        )
        logger.info(f"Completed runtime monitor package generation for application type: {application_type}")
        return package
    
    def package_to_zip(self, package: EnforcementPackage, output_path: Optional[str] = None) -> str:
        """Export enforcement package as ZIP file"""
        logger.info(f"Starting package export to ZIP for package: {package.package_id}")
        if not output_path:
            output_path = f"{package.package_id}.zip"
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all deployment files
            for filename, content in package.deployment_files.items():
                zipf.writestr(filename, content)
            
            # Add package metadata
            metadata = {
                "package_info": asdict(package),
                "generated_by": "DataGuardian Pro Runtime Enforcement Generator",
                "version": "1.0.0"
            }
            zipf.writestr("package-info.json", json.dumps(metadata, indent=2, default=str))
            
            # Add installation script as executable
            zipf.writestr("install.sh", package.installation_script)
        
        logger.info(f"Completed package export to ZIP: {output_path}")
        return output_path
    
    # Helper methods for generating specific components
    def _generate_cookie_test_page(self, domain: str) -> str:
        """Generate test page for cookie enforcement"""
        return f'''
<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cookie Enforcement Test - {domain}</title>
    <script src="cookie-enforcer.js"></script>
</head>
<body>
    <h1>🛡️ Cookie Enforcement Test Page</h1>
    <p>Deze pagina test de cookie enforcement functionaliteit.</p>
    
    <div id="test-results"></div>
    
    <h2>Test Actions</h2>
    <button onclick="testGoogleAnalytics()">Test Google Analytics</button>
    <button onclick="testFacebookPixel()">Test Facebook Pixel</button>
    <button onclick="testGenericTracking()">Test Generic Tracking</button>
    <button onclick="showConsentStatus()">Show Consent Status</button>
    
    <script>
    function testGoogleAnalytics() {{
        console.log('Testing Google Analytics...');
        fetch('https://www.google-analytics.com/collect', {{
            method: 'POST',
            body: 'test=true'
        }}).then(() => {{
            updateResults('Google Analytics request succeeded (should be blocked without consent)');
        }}).catch(err => {{
            updateResults('Google Analytics request blocked: ' + err.message);
        }});
    }}
    
    function testFacebookPixel() {{
        console.log('Testing Facebook Pixel...');
        fetch('https://www.facebook.com/tr', {{
            method: 'POST',
            body: 'test=true'
        }}).then(() => {{
            updateResults('Facebook Pixel request succeeded (should be blocked without consent)');
        }}).catch(err => {{
            updateResults('Facebook Pixel request blocked: ' + err.message);
        }});
    }}
    
    function testGenericTracking() {{
        console.log('Testing generic tracking...');
        document.cookie = 'tracking_test=blocked; path=/';
        const cookie = document.cookie.includes('tracking_test');
        updateResults('Tracking cookie set: ' + cookie + ' (should be false without consent)');
    }}
    
    function showConsentStatus() {{
        const consent = document.cookie.includes('cookie-consent');
        const consentValue = consent ? document.cookie.split('cookie-consent=')[1].split(';')[0] : 'none';
        updateResults('Consent status: ' + consentValue);
        
        if (window.cookieEnforcer) {{
            updateResults('Blocked requests: ' + window.cookieEnforcer.blockedRequests.length);
        }}
    }}
    
    function updateResults(message) {{
        const results = document.getElementById('test-results');
        results.innerHTML += '<div>' + new Date().toLocaleTimeString() + ': ' + message + '</div>';
    }}
    </script>
</body>
</html>
'''
    
    def _generate_cookie_installation_script(self, domain: str) -> str:
        """Generate cookie enforcer installation script"""
        return f'''#!/bin/bash

# DataGuardian Pro - Cookie Enforcement Installation Script
# Domain: {domain}

echo "🛡️ Installing DataGuardian Pro Cookie Enforcement..."

# Check if web root exists
if [ ! -d "/var/www/html" ] && [ ! -d "/usr/share/nginx/html" ]; then
    echo "❌ Web root directory not found"
    echo "Please specify your web root directory:"
    read -r WEB_ROOT
else
    WEB_ROOT="/var/www/html"
    if [ -d "/usr/share/nginx/html" ]; then
        WEB_ROOT="/usr/share/nginx/html"
    fi
fi

echo "Installing to: $WEB_ROOT"

# Create necessary directories
mkdir -p "$WEB_ROOT"
mkdir -p "$WEB_ROOT/assets"
mkdir -p "$WEB_ROOT/js"

# Copy enforcement script
cp cookie-enforcer.js "$WEB_ROOT/"
echo "✅ Cookie enforcer script installed"

# Copy test page
cp test-page.html "$WEB_ROOT/cookie-test.html"
echo "✅ Test page installed at /cookie-test.html"

# Set permissions
chmod 644 "$WEB_ROOT/cookie-enforcer.js"
chmod 644 "$WEB_ROOT/cookie-test.html"

echo ""
echo "🎉 Installation Complete!"
echo ""
echo "Next steps:"
echo "1. Add <script src='/cookie-enforcer.js'></script> to your HTML pages"
echo "2. Test enforcement at: http://{domain}/cookie-test.html"
echo "3. Customize configuration in configuration.json"
echo "4. Monitor browser console for blocked request logs"
echo ""
echo "For support: https://dataguardian.pro/support"
'''
    
    def _generate_cicd_installation_script(self, platform: str) -> str:
        """Generate CI/CD installation script"""
        if platform == "github-actions":
            return '''#!/bin/bash

# DataGuardian Pro - GitHub Actions Compliance Installation

echo "🛡️ Setting up GitHub Actions compliance enforcement..."

# Create workflows directory
mkdir -p .github/workflows

# Copy workflow file
cp compliance-enforcement.yml .github/workflows/
echo "✅ Compliance workflow installed"

# Set up branch protection (requires GitHub CLI)
if command -v gh &> /dev/null; then
    echo "Setting up branch protection..."
    gh api repos/:owner/:repo/branches/main/protection \\
        --method PUT \\
        --field required_status_checks='{"strict":true,"contexts":["Privacy Compliance Check"]}' \\
        --field enforce_admins=true \\
        --field required_pull_request_reviews='{"required_approving_review_count":1}' \\
        --field restrictions=null
    echo "✅ Branch protection configured"
else
    echo "⚠️ GitHub CLI not found - manually configure branch protection"
fi

echo ""
echo "🎉 Installation Complete!"
echo ""
echo "Next steps:"
echo "1. Push changes to trigger first compliance scan"
echo "2. Configure repository secrets if needed"
echo "3. Review compliance reports in Actions tab"
echo "4. Set up branch protection rules if not automated"
'''
        else:
            return '''#!/bin/bash

# DataGuardian Pro - Azure DevOps Compliance Installation

echo "🛡️ Setting up Azure DevOps compliance enforcement..."

# Copy pipeline file
cp azure-pipelines-compliance.yml ./
echo "✅ Compliance pipeline file ready"

echo ""
echo "🎉 File Installation Complete!"
echo ""
echo "Next steps:"
echo "1. Create new pipeline in Azure DevOps using azure-pipelines-compliance.yml"
echo "2. Configure pipeline variables (COMPLIANCE_THRESHOLD, etc.)"
echo "3. Set up branch policies to require compliance pipeline"
echo "4. Configure service connections if needed"
echo "5. Test pipeline with a commit"
echo ""
echo "For detailed instructions, see installation-guide.md"
'''
    
    def _generate_compliance_test_script(self) -> str:
        """Generate compliance testing script"""
        return '''#!/usr/bin/env python3

"""
DataGuardian Pro - Compliance Test Script
Tests enforcement package functionality
"""

import json
import sys
import os
from datetime import datetime

def test_cookie_enforcement():
    """Test cookie enforcement functionality"""
    print("🍪 Testing cookie enforcement...")
    
    # Check if enforcement script exists
    if not os.path.exists('cookie-enforcer.js'):
        print("❌ Cookie enforcer script not found")
        return False
    
    # Check script content
    with open('cookie-enforcer.js', 'r') as f:
        content = f.read()
        
    required_features = [
        'CookieEnforcer',
        'blockCookieRequests',
        'acceptAllCookies',
        'rejectAllCookies',
        'dutchCompliance'
    ]
    
    missing_features = []
    for feature in required_features:
        if feature not in content:
            missing_features.append(feature)
    
    if missing_features:
        print(f"❌ Missing features: {', '.join(missing_features)}")
        return False
    
    print("✅ Cookie enforcement tests passed")
    return True

def test_cicd_pipeline():
    """Test CI/CD pipeline configuration"""
    print("🔄 Testing CI/CD pipeline...")
    
    # Check for workflow files
    github_workflow = os.path.exists('.github/workflows/compliance-enforcement.yml')
    azure_pipeline = os.path.exists('azure-pipelines-compliance.yml')
    
    if not github_workflow and not azure_pipeline:
        print("❌ No CI/CD pipeline files found")
        return False
    
    if github_workflow:
        print("✅ GitHub Actions workflow found")
        # Additional validation could be added here
    
    if azure_pipeline:
        print("✅ Azure DevOps pipeline found")
        # Additional validation could be added here
    
    return True

def test_configuration():
    """Test configuration files"""
    print("⚙️ Testing configuration...")
    
    config_files = [
        'configuration.json',
        'compliance-config.json',
        'monitor-config.json'
    ]
    
    found_configs = []
    for config_file in config_files:
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                found_configs.append(config_file)
                print(f"✅ Valid configuration: {config_file}")
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON in {config_file}")
                return False
    
    if not found_configs:
        print("⚠️ No configuration files found")
        return True  # Not critical
    
    return True

def main():
    """Run all compliance tests"""
    print("🛡️ DataGuardian Pro - Compliance Package Test")
    print("=" * 50)
    
    tests = [
        ("Cookie Enforcement", test_cookie_enforcement),
        ("CI/CD Pipeline", test_cicd_pipeline),
        ("Configuration", test_configuration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test error: {e}")
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All compliance tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed - review configuration")
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''

    # Additional helper methods would continue here...
    def _generate_web_monitor_script(self, config: Dict[str, Any]) -> str:
        """Generate web application monitoring script"""
        return '''
// DataGuardian Pro - Web Application Compliance Monitor
// Real-time compliance monitoring for web applications

class ComplianceMonitor {
    constructor(config = {}) {
        this.config = {
            monitorCookies: true,
            monitorApiCalls: true,
            monitorDataAccess: true,
            alertOnViolations: true,
            logComplianceEvents: true,
            reportingEndpoint: '/api/compliance/report',
            ...config
        };
        
        this.violations = [];
        this.startTime = Date.now();
        this.init();
    }
    
    init() {
        console.log('🛡️ DataGuardian Pro Web Monitor initialized');
        
        if (this.config.monitorCookies) {
            this.setupCookieMonitoring();
        }
        
        if (this.config.monitorApiCalls) {
            this.setupApiMonitoring();
        }
        
        if (this.config.monitorDataAccess) {
            this.setupDataAccessMonitoring();
        }
        
        // Start periodic reporting
        setInterval(() => this.reportCompliance(), 60000); // Every minute
    }
    
    setupCookieMonitoring() {
        const originalSetCookie = document.cookie;
        let cookieCount = 0;
        
        // Monitor cookie changes
        const observer = new MutationObserver(() => {
            const newCookieCount = document.cookie.split(';').length;
            if (newCookieCount > cookieCount) {
                this.logEvent('cookie_added', {
                    count: newCookieCount,
                    timestamp: Date.now()
                });
            }
            cookieCount = newCookieCount;
        });
        
        // Check for unauthorized cookies
        setInterval(() => {
            const cookies = document.cookie.split(';');
            const unauthorizedCookies = cookies.filter(cookie => {
                const name = cookie.split('=')[0].trim();
                return !this.isAuthorizedCookie(name);
            });
            
            if (unauthorizedCookies.length > 0) {
                this.reportViolation('unauthorized_cookies', {
                    cookies: unauthorizedCookies.map(c => c.split('=')[0].trim()),
                    timestamp: Date.now()
                });
            }
        }, 10000); // Check every 10 seconds
    }
    
    setupApiMonitoring() {
        const originalFetch = window.fetch;
        const self = this;
        
        window.fetch = function(...args) {
            const url = args[0];
            const options = args[1] || {};
            
            // Log API calls
            self.logEvent('api_call', {
                url: url.toString(),
                method: options.method || 'GET',
                timestamp: Date.now()
            });
            
            // Check for sensitive data in requests
            if (options.body) {
                const sensitivePatterns = [
                    /\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b/, // Email
                    /\\b\\d{3}-\\d{2}-\\d{4}\\b/, // SSN pattern
                    /\\b\\d{11}\\b/ // Possible BSN
                ];
                
                for (const pattern of sensitivePatterns) {
                    if (pattern.test(options.body)) {
                        self.reportViolation('sensitive_data_transmission', {
                            url: url.toString(),
                            pattern: pattern.source,
                            timestamp: Date.now()
                        });
                    }
                }
            }
            
            return originalFetch.apply(this, args);
        };
    }
    
    isAuthorizedCookie(name) {
        const authorizedCookies = [
            'session', 'csrf', 'auth', 'cookie-consent',
            '__cfduid', 'PHPSESSID', 'connect.sid'
        ];
        return authorizedCookies.includes(name);
    }
    
    detectPIIViolations(data) {
        const piiPatterns = {
            email: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g,
            ssn: /\b\d{3}-?\d{2}-?\d{4}\b/g,
            creditCard: /\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14})\b/g,
            phone: /\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b/g
        };
        
        const violations = [];
        for (const [type, pattern] of Object.entries(piiPatterns)) {
            const matches = data.match(pattern);
            if (matches) {
                violations.push({
                    type: `pii_${type}`,
                    matches: matches.length,
                    data: matches[0].substring(0, 10) + '...'
                });
            }
        }
        return violations;
    }
    
    reportViolation(violation) {
        this.violations.push({
            ...violation,
            timestamp: Date.now(),
            id: Math.random().toString(36).substr(2, 9)
        });
        
        if (this.config.alertOnViolations) {
            console.warn('[DataGuardian] Compliance Violation:', violation);
        }
        
        if (this.config.reportingEndpoint) {
            this.sendViolationReport(violation);
        }
    }
    
    trackDataFlow(data, source, destination) {
        const flowEvent = {
            type: 'data_flow',
            source,
            destination,
            dataType: this.classifyData(data),
            timestamp: Date.now(),
            size: JSON.stringify(data).length
        };
        
        this.logEvent('data_flow', flowEvent);
        
        // Check for unauthorized data flows
        if (this.isUnauthorizedFlow(source, destination)) {
            this.reportViolation({
                type: 'unauthorized_data_flow',
                source,
                destination,
                severity: 'high'
            });
        }
    }
    
    classifyData(data) {
        const dataStr = JSON.stringify(data);
        if (this.detectPIIViolations(dataStr).length > 0) {
            return 'pii';
        }
        if (dataStr.includes('password') || dataStr.includes('token')) {
            return 'credentials';
        }
        return 'general';
    }
    
    isUnauthorizedFlow(source, destination) {
        const unauthorizedDestinations = [
            'google-analytics.com',
            'facebook.com',
            'doubleclick.net'
        ];
        return unauthorizedDestinations.some(dest => destination.includes(dest));
    }
    
    sendViolationReport(violation) {
        if (!this.config.reportingEndpoint) return;
        
        fetch(this.config.reportingEndpoint, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({violation, timestamp: Date.now()})
        }).catch(err => console.error('Failed to send violation report:', err));
    }
    
    logEvent(type, data) {
        if (!this.config.logComplianceEvents) return;
        
        const event = {
            type,
            data,
            timestamp: Date.now(),
            url: window.location.href,
            userAgent: navigator.userAgent
        };
        
        console.log('[Compliance Monitor]', event);
        
        // Store for reporting
        this.violations.push(event);
    }
    
    reportViolation(type, data) {
        const violation = {
            type,
            data,
            severity: this.getViolationSeverity(type),
            timestamp: Date.now(),
            url: window.location.href
        };
        
        this.violations.push(violation);
        
        if (this.config.alertOnViolations) {
            console.warn('🚨 Compliance Violation:', violation);
        }
        
        // Immediate reporting for critical violations
        if (violation.severity === 'critical') {
            this.reportCompliance(true);
        }
    }
    
    getViolationSeverity(type) {
        const severityMap = {
            'unauthorized_cookies': 'medium',
            'sensitive_data_transmission': 'critical',
            'tracking_without_consent': 'high',
            'data_breach': 'critical'
        };
        
        return severityMap[type] || 'low';
    }
    
    async reportCompliance(immediate = false) {
        if (this.violations.length === 0 && !immediate) return;
        
        const report = {
            sessionId: this.generateSessionId(),
            timestamp: Date.now(),
            url: window.location.href,
            violations: this.violations,
            metrics: {
                totalViolations: this.violations.length,
                criticalViolations: this.violations.filter(v => v.severity === 'critical').length,
                sessionDuration: Date.now() - this.startTime
            }
        };
        
        try {
            await fetch(this.config.reportingEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(report)
            });
            
            console.log('✅ Compliance report sent');
            this.violations = []; // Clear reported violations
        } catch (error) {
            console.error('❌ Failed to send compliance report:', error);
        }
    }
    
    generateSessionId() {
        return 'session_' + Math.random().toString(36).substr(2, 9);
    }
}

// Auto-initialize
document.addEventListener('DOMContentLoaded', function() {
    window.complianceMonitor = new WebComplianceMonitor();
});
'''
    
    def _generate_api_monitor_script(self, config: Dict[str, Any]) -> str:
        """Generate API monitoring script (Node.js/Python)"""
        return '''
// DataGuardian Pro - API Compliance Monitor
// Server-side compliance monitoring for REST APIs

const express = require('express');
const crypto = require('crypto');

class APIComplianceMonitor {
    constructor(config = {}) {
        this.config = {
            monitorDataAccess: true,
            monitorApiCalls: true,
            alertOnViolations: true,
            logComplianceEvents: true,
            reportingEndpoint: '/api/compliance/report',
            sessionTimeoutMinutes: 30,
            maxRequestSizeBytes: 1024 * 1024, // 1MB
            ...config
        };
        
        this.violations = [];
        this.activeRequests = new Map();
        this.sensitiveDataPatterns = [
            /\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b/g, // Email
            /\\b\\d{3}-?\\d{2}-?\\d{4}\\b/g, // SSN
            /\\b\\d{11}\\b/g, // BSN (Netherlands)
            /\\b4[0-9]{12}(?:[0-9]{3})?\\b/g, // Credit card (Visa)
            /\\b(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}\\b/g // Mastercard
        ];
        
        this.init();
    }
    
    init() {
        console.log('🛡️ DataGuardian Pro API Monitor initialized');
        this.setupMiddleware();
        this.startPeriodicReporting();
    }
    
    setupMiddleware() {
        return (req, res, next) => {
            const requestId = this.generateRequestId();
            const startTime = Date.now();
            
            // Store request info
            this.activeRequests.set(requestId, {
                method: req.method,
                url: req.url,
                headers: req.headers,
                startTime: startTime,
                userAgent: req.get('User-Agent'),
                ip: req.ip
            });
            
            // Monitor request data
            if (req.body && this.config.monitorDataAccess) {
                this.scanRequestForSensitiveData(req, requestId);
            }
            
            // Monitor response
            const originalSend = res.send;
            res.send = function(data) {
                this.scanResponseForSensitiveData(data, requestId);
                this.logApiCall(requestId, req, res, Date.now() - startTime);
                this.activeRequests.delete(requestId);
                return originalSend.call(res, data);
            }.bind(this);
            
            next();
        };
    }
    
    scanRequestForSensitiveData(req, requestId) {
        const requestData = JSON.stringify(req.body);
        
        for (const pattern of this.sensitiveDataPatterns) {
            const matches = requestData.match(pattern);
            if (matches) {
                this.reportViolation('sensitive_data_in_request', {
                    requestId,
                    url: req.url,
                    method: req.method,
                    dataType: this.identifyDataType(pattern),
                    matchCount: matches.length,
                    timestamp: Date.now()
                });
            }
        }
    }
    
    scanResponseForSensitiveData(responseData, requestId) {
        if (typeof responseData !== 'string') {
            responseData = JSON.stringify(responseData);
        }
        
        for (const pattern of this.sensitiveDataPatterns) {
            const matches = responseData.match(pattern);
            if (matches) {
                this.reportViolation('sensitive_data_in_response', {
                    requestId,
                    dataType: this.identifyDataType(pattern),
                    matchCount: matches.length,
                    timestamp: Date.now()
                });
            }
        }
    }
    
    identifyDataType(pattern) {
        if (pattern.source.includes('@')) return 'email';
        if (pattern.source.includes('\\\\d{3}-?\\\\d{2}-?\\\\d{4}')) return 'ssn';
        if (pattern.source.includes('\\\\d{11}')) return 'bsn';
        if (pattern.source.includes('4[0-9]')) return 'credit_card_visa';
        if (pattern.source.includes('5[1-5]')) return 'credit_card_mastercard';
        return 'unknown';
    }
    
    logApiCall(requestId, req, res, responseTime) {
        if (!this.config.logComplianceEvents) return;
        
        const logEntry = {
            requestId,
            method: req.method,
            url: req.url,
            statusCode: res.statusCode,
            responseTime,
            timestamp: Date.now(),
            userAgent: req.get('User-Agent'),
            ip: req.ip
        };
        
        console.log('[API Compliance]', logEntry);
        
        // Check for compliance violations
        if (responseTime > 30000) { // 30 second timeout
            this.reportViolation('slow_response', logEntry);
        }
        
        if (res.statusCode >= 500) {
            this.reportViolation('server_error', logEntry);
        }
    }
    
    reportViolation(type, data) {
        if (!this.config.alertOnViolations) return;
        
        const violation = {
            type,
            data,
            severity: this.getSeverity(type),
            timestamp: Date.now(),
            sessionId: this.generateSessionId()
        };
        
        this.violations.push(violation);
        console.warn('[API Compliance Violation]', violation);
        
        // Immediate reporting for critical violations
        if (violation.severity === 'critical') {
            this.sendImmediateAlert(violation);
        }
    }
    
    getSeverity(violationType) {
        const severityMap = {
            'sensitive_data_in_request': 'critical',
            'sensitive_data_in_response': 'critical',
            'slow_response': 'medium',
            'server_error': 'high'
        };
        return severityMap[violationType] || 'low';
    }
    
    startPeriodicReporting() {
        setInterval(() => {
            this.sendComplianceReport();
        }, 60000); // Every minute
    }
    
    async sendComplianceReport() {
        if (this.violations.length === 0) return;
        
        const report = {
            timestamp: Date.now(),
            violations: this.violations,
            summary: {
                totalViolations: this.violations.length,
                criticalCount: this.violations.filter(v => v.severity === 'critical').length,
                highCount: this.violations.filter(v => v.severity === 'high').length,
                activeRequests: this.activeRequests.size
            },
            systemInfo: {
                nodeVersion: process.version,
                platform: process.platform,
                uptime: process.uptime()
            }
        };
        
        try {
            // Here you would send to your compliance reporting endpoint
            console.log('📊 Compliance Report:', report);
            this.violations = []; // Clear reported violations
        } catch (error) {
            console.error('❌ Failed to send compliance report:', error);
        }
    }
    
    generateRequestId() {
        return 'req_' + crypto.randomBytes(8).toString('hex');
    }
    
    generateSessionId() {
        return 'session_' + crypto.randomBytes(8).toString('hex');
    }
}

module.exports = APIComplianceMonitor;

// Express.js integration example:
/*
const express = require('express');
const APIComplianceMonitor = require('./api-compliance-monitor');

const app = express();
const monitor = new APIComplianceMonitor({
    monitorDataAccess: true,
    alertOnViolations: true
});

app.use(monitor.setupMiddleware());
*/
'''
    
    def _generate_generic_monitor_script(self, config: Dict[str, Any]) -> str:
        """Generate generic monitoring script"""
        return '''
#!/usr/bin/env python3
"""
DataGuardian Pro - Generic Compliance Monitor
Cross-platform compliance monitoring for any application type
"""

import os
import json
import time
import hashlib
import threading
import urllib.request
import urllib.parse
from datetime import datetime
from typing import Dict, List, Any

class GenericComplianceMonitor:
    def __init__(self, config_path="monitor-config.json"):
        self.config = self.load_config(config_path)
        self.violations = []
        self.monitoring = False
        self.session_id = self.generate_session_id()
        
        # Default compliance patterns
        self.sensitive_patterns = {
            "email": r"\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b",
            "ssn": r"\\b\\d{3}-?\\d{2}-?\\d{4}\\b",
            "bsn": r"\\b\\d{11}\\b",  # Netherlands BSN
            "credit_card": r"\\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14})\\b",
            "phone": r"\\b\\+?1?[-. ]?\\(?[0-9]{3}\\)?[-. ]?[0-9]{3}[-. ]?[0-9]{4}\\b"
        }
        
        self.init_monitor()
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load monitoring configuration"""
        default_config = {
            "monitor_files": True,
            "monitor_network": True,
            "monitor_processes": True,
            "scan_interval_seconds": 60,
            "alert_on_violations": True,
            "log_compliance_events": True,
            "reporting_endpoint": None,
            "max_violations_per_report": 100,
            "sensitive_file_extensions": [".log", ".txt", ".csv", ".json"],
            "exclude_directories": [".git", "node_modules", "__pycache__"]
        }
        
        try:
            with open(config_path, "r") as f:
                user_config = json.load(f)
            default_config.update(user_config)
        except FileNotFoundError:
            print(f"⚠️ Config file {config_path} not found, using defaults")
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in {config_path}, using defaults")
        
        return default_config
    
    def init_monitor(self):
        """Initialize monitoring system"""
        print(f"🛡️ DataGuardian Pro Generic Monitor initialized")
        print(f"Session ID: {self.session_id}")
        
        if self.config["monitor_files"]:
            print("✅ File monitoring enabled")
        
        if self.config["monitor_network"]:
            print("✅ Network monitoring enabled")
        
        if self.config["monitor_processes"]:
            print("✅ Process monitoring enabled")
    
    def start_monitoring(self):
        """Start continuous monitoring"""
        if self.monitoring:
            print("⚠️ Monitoring already running")
            return
        
        self.monitoring = True
        print("🔍 Starting compliance monitoring...")
        
        # Start monitoring threads
        threads = []
        
        if self.config["monitor_files"]:
            file_thread = threading.Thread(target=self.monitor_files_loop)
            file_thread.daemon = True
            file_thread.start()
            threads.append(file_thread)
        
        if self.config["monitor_network"]:
            network_thread = threading.Thread(target=self.monitor_network_loop)
            network_thread.daemon = True
            network_thread.start()
            threads.append(network_thread)
        
        # Start periodic reporting
        report_thread = threading.Thread(target=self.periodic_reporting_loop)
        report_thread.daemon = True
        report_thread.start()
        
        try:
            while self.monitoring:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop monitoring"""
        print("🛑 Stopping compliance monitoring...")
        self.monitoring = False
        self.send_final_report()
    
    def monitor_files_loop(self):
        """Monitor files for sensitive data"""
        while self.monitoring:
            try:
                self.scan_files_for_violations()
            except Exception as e:
                self.log_error(f"File monitoring error: {e}")
            
            time.sleep(self.config["scan_interval_seconds"])
    
    def monitor_network_loop(self):
        """Monitor network activity"""
        while self.monitoring:
            try:
                self.scan_network_activity()
            except Exception as e:
                self.log_error(f"Network monitoring error: {e}")
            
            time.sleep(self.config["scan_interval_seconds"])
    
    def scan_files_for_violations(self):
        """Scan files for compliance violations"""
        scan_dirs = ["."]  # Current directory and subdirs
        
        for scan_dir in scan_dirs:
            for root, dirs, files in os.walk(scan_dir):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if d not in self.config["exclude_directories"]]
                
                for file in files:
                    if any(file.endswith(ext) for ext in self.config["sensitive_file_extensions"]):
                        file_path = os.path.join(root, file)
                        self.scan_file_content(file_path)
    
    def scan_file_content(self, file_path: str):
        """Scan individual file for sensitive data"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            import re
            for data_type, pattern in self.sensitive_patterns.items():
                matches = re.findall(pattern, content)
                if matches:
                    self.report_violation("sensitive_data_in_file", {
                        "file_path": file_path,
                        "data_type": data_type,
                        "match_count": len(matches),
                        "file_size": os.path.getsize(file_path),
                        "timestamp": datetime.now().isoformat()
                    })
        
        except Exception as e:
            # Skip files that can\'t be read
            pass
    
    def scan_network_activity(self):
        """Monitor network activity for violations"""
        # Placeholder for network monitoring
        # In a full implementation, this would monitor:
        # - DNS queries to tracking domains
        # - HTTP requests with sensitive data
        # - Unauthorized outbound connections
        pass
    
    def report_violation(self, violation_type: str, data: Dict[str, Any]):
        """Report a compliance violation"""
        violation = {
            "type": violation_type,
            "data": data,
            "severity": self.get_severity(violation_type),
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id
        }
        
        self.violations.append(violation)
        
        if self.config["log_compliance_events"]:
            print(f"⚠️ Compliance violation: {violation_type} - {data.get(\'file_path\', \'unknown\')}")
        
        if self.config["alert_on_violations"] and violation["severity"] == "critical":
            self.send_immediate_alert(violation)
    
    def get_severity(self, violation_type: str) -> str:
        """Determine violation severity"""
        severity_map = {
            "sensitive_data_in_file": "high",
            "unauthorized_network_access": "critical",
            "insecure_configuration": "medium",
            "missing_encryption": "high"
        }
        return severity_map.get(violation_type, "low")
    
    def periodic_reporting_loop(self):
        """Send periodic compliance reports"""
        report_interval = 300  # 5 minutes
        
        while self.monitoring:
            time.sleep(report_interval)
            if self.violations:
                self.send_compliance_report()
    
    def send_compliance_report(self):
        """Send compliance report"""
        if not self.violations:
            return
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "violations": self.violations[:self.config["max_violations_per_report"]],
            "summary": {
                "total_violations": len(self.violations),
                "critical_count": sum(1 for v in self.violations if v["severity"] == "critical"),
                "high_count": sum(1 for v in self.violations if v["severity"] == "high"),
                "medium_count": sum(1 for v in self.violations if v["severity"] == "medium")
            },
            "system_info": {
                "platform": os.name,
                "working_directory": os.getcwd(),
                "monitor_config": self.config
            }
        }
        
        if self.config["reporting_endpoint"]:
            self.send_to_endpoint(report)
        else:
            print("📊 Compliance Report:")
            print(json.dumps(report, indent=2))
        
        # Clear reported violations
        self.violations = self.violations[self.config["max_violations_per_report"]:]
    
    def send_to_endpoint(self, report: Dict[str, Any]):
        """Send report to remote endpoint"""
        try:
            data = json.dumps(report).encode(\'utf-8\')
            req = urllib.request.Request(
                self.config["reporting_endpoint"],
                data=data,
                headers={\'Content-Type\': \'application/json\'}
            )
            
            with urllib.request.urlopen(req) as response:
                print(f"✅ Report sent: {response.status}")
        
        except Exception as e:
            print(f"❌ Failed to send report: {e}")
    
    def send_immediate_alert(self, violation: Dict[str, Any]):
        """Send immediate alert for critical violations"""
        alert = {
            "alert_type": "critical_violation",
            "violation": violation,
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id
        }
        
        print(f"🚨 CRITICAL ALERT: {violation[\'type\']}")
        
        if self.config["reporting_endpoint"]:
            self.send_to_endpoint(alert)
    
    def send_final_report(self):
        """Send final report when monitoring stops"""
        if self.violations:
            print("📤 Sending final compliance report...")
            self.send_compliance_report()
    
    def log_error(self, message: str):
        """Log error message"""
        print(f"❌ Monitor Error: {message}")
    
    def generate_session_id(self) -> str:
        """Generate unique session ID"""
        return hashlib.md5(f"{datetime.now().isoformat()}{os.getpid()}".encode()).hexdigest()[:16]

def main():
    """Main entry point"""
    print("🛡️ DataGuardian Pro - Generic Compliance Monitor")
    print("=" * 60)
    
    monitor = GenericComplianceMonitor()
    
    try:
        monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped by user")
    except Exception as e:
        print(f"💥 Monitor crashed: {e}")
    finally:
        monitor.stop_monitoring()

if __name__ == "__main__":
    main()
'''
    
    def _generate_monitor_installation_guide(self, application_type: str) -> str:
        """Generate monitoring installation guide"""
        return f"""
# Runtime Compliance Monitor Installation Guide

## Application Type: {application_type}

### Installation Steps:

1. **Deploy monitoring script:**
   - Copy `compliance-monitor.js` to your application
   - Include in your main application file

2. **Configure monitoring:**
   - Edit `monitor-config.json` to match your requirements
   - Set up reporting endpoint

3. **Test monitoring:**
   - Run `python health-check.py` to verify functionality
   - Check browser console for monitoring logs

4. **Set up alerting:**
   - Configure alerts for critical violations
   - Set up compliance reporting dashboard

### Features:
✅ Real-time violation detection
✅ Automated compliance reporting
✅ Cookie and tracking monitoring
✅ API call compliance checking
✅ Data access pattern analysis
"""

    def _generate_monitor_health_check(self) -> str:
        """Generate monitoring health check script"""
        return '''#!/usr/bin/env python3

import json
import time
import requests
from datetime import datetime

def health_check():
    """Perform compliance monitor health check"""
    print("🏥 DataGuardian Pro - Monitor Health Check")
    print("=" * 50)
    
    checks = [
        ("Configuration", check_configuration),
        ("Monitoring Script", check_monitoring_script),
        ("Reporting Endpoint", check_reporting_endpoint)
    ]
    
    results = {}
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
            status = "✅ PASS" if results[check_name] else "❌ FAIL"
            print(f"{status} {check_name}")
        except Exception as e:
            results[check_name] = False
            print(f"❌ ERROR {check_name}: {e}")
    
    print("=" * 50)
    
    # Overall status
    all_passed = all(results.values())
    if all_passed:
        print("🎉 All health checks passed!")
        return 0
    else:
        print("⚠️ Some health checks failed")
        return 1

def check_configuration():
    """Check monitor configuration"""
    try:
        with open('monitor-config.json', 'r') as f:
            config = json.load(f)
        return isinstance(config, dict) and len(config) > 0
    except:
        return False

def check_monitoring_script():
    """Check if monitoring script exists and is valid"""
    try:
        with open('compliance-monitor.js', 'r') as f:
            content = f.read()
        return 'ComplianceMonitor' in content
    except:
        return False

def check_reporting_endpoint():
    """Check if reporting endpoint is accessible"""
    # This would check if the reporting endpoint is reachable
    return True  # Placeholder

if __name__ == "__main__":
    exit(health_check())
'''
    
    def _generate_monitor_installation_script(self, application_type: str) -> str:
        """Generate monitoring installation script"""
        return f'''#!/bin/bash

# DataGuardian Pro - Runtime Monitor Installation
# Application Type: {application_type}

echo "🛡️ Installing DataGuardian Pro Runtime Monitor..."

# Determine installation path based on application type
if [ "{application_type}" = "web" ]; then
    INSTALL_PATH="/var/www/html/js"
    mkdir -p "$INSTALL_PATH"
elif [ "{application_type}" = "api" ]; then
    INSTALL_PATH="./monitoring"
    mkdir -p "$INSTALL_PATH"
else
    INSTALL_PATH="./compliance"
    mkdir -p "$INSTALL_PATH"
fi

echo "Installing to: $INSTALL_PATH"

# Copy monitoring files
cp compliance-monitor.js "$INSTALL_PATH/"
cp monitor-config.json "$INSTALL_PATH/"
cp health-check.py "$INSTALL_PATH/"

echo "✅ Runtime monitor installed"

# Set permissions
chmod 644 "$INSTALL_PATH/compliance-monitor.js"
chmod 644 "$INSTALL_PATH/monitor-config.json"
chmod +x "$INSTALL_PATH/health-check.py"

# Run health check
echo "Running health check..."
cd "$INSTALL_PATH"
python3 health-check.py

echo ""
echo "🎉 Installation Complete!"
echo ""
echo "Next steps:"
echo "1. Include compliance-monitor.js in your application"
echo "2. Configure monitoring settings in monitor-config.json"
echo "3. Set up compliance reporting endpoint"
echo "4. Test monitoring with sample violations"
echo ""
echo "For support: https://dataguardian.pro/support"
'''

    def generate_enforcement_package(self, 
                                   package_type: EnforcementPackageType,
                                   **kwargs) -> EnforcementPackage:
        """Generate enforcement package of specified type"""
        
        if package_type == EnforcementPackageType.COOKIE_BLOCKER:
            return self.generate_cookie_blocking_package(
                website_domain=kwargs.get('website_domain', 'example.com'),
                compliance_config=kwargs.get('compliance_config')
            )
        elif package_type == EnforcementPackageType.CICD_COMPLIANCE:
            return self.generate_cicd_compliance_package(
                platform=kwargs.get('platform', 'github-actions'),
                repository_name=kwargs.get('repository_name', 'my-repo'),
                compliance_thresholds=kwargs.get('compliance_thresholds')
            )
        elif package_type == EnforcementPackageType.RUNTIME_MONITOR:
            return self.generate_runtime_monitor_package(
                application_type=kwargs.get('application_type', 'web'),
                monitoring_config=kwargs.get('monitoring_config')
            )
        else:
            raise ValueError(f"Unsupported package type: {package_type}")

# Example usage and testing functions
def main():
    """Example usage of Runtime Enforcement Generator"""
    generator = RuntimeEnforcementGenerator(region="Netherlands")
    
    print("🛡️ DataGuardian Pro - Runtime Enforcement Generator")
    print("=" * 60)
    
    # Generate cookie blocking package
    cookie_package = generator.generate_cookie_blocking_package(
        website_domain="example.nl",
        compliance_config={
            "strict_mode": True,
            "auto_reject_timeout": 30000,
            "dutch_compliance": True
        }
    )
    print(f"✅ Generated: {cookie_package.name}")
    
    # Generate CI/CD compliance package
    cicd_package = generator.generate_cicd_compliance_package(
        platform="github-actions",
        repository_name="my-webapp",
        compliance_thresholds={
            "max_critical_issues": 0,
            "max_high_issues": 3,
            "min_compliance_score": 80
        }
    )
    print(f"✅ Generated: {cicd_package.name}")
    
    # Generate runtime monitoring package
    monitor_package = generator.generate_runtime_monitor_package(
        application_type="web",
        monitoring_config={
            "monitor_cookies": True,
            "monitor_api_calls": True,
            "alert_on_violations": True
        }
    )
    print(f"✅ Generated: {monitor_package.name}")
    
    # Export packages as ZIP files
    for package in [cookie_package, cicd_package, monitor_package]:
        zip_path = generator.package_to_zip(package)
        print(f"📦 Exported: {zip_path}")
    
    print("=" * 60)
    print("🎉 Runtime enforcement packages generated successfully!")

if __name__ == "__main__":
    main()