"""
Unified HTML Report Generator for DataGuardian Pro
Consolidates all HTML report generation into a single, standardized system.
"""

import streamlit as st
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from utils.unified_translation import t_report, t_technical, t_ui
from services.enhanced_finding_generator import enhance_findings_for_report

logger = logging.getLogger(__name__)

class UnifiedHTMLReportGenerator:
    """Consolidated HTML report generator with unified translation support."""
    
    def __init__(self):
        self.current_language = 'en'
        self._update_language()
    
    def _update_language(self):
        """Update current language from session state."""
        self.current_language = st.session_state.get('language', 'en')
    
    def generate_html_report(self, scan_result: Dict[str, Any]) -> str:
        """
        Generate a unified HTML report for any scanner type.
        
        Args:
            scan_result: Scan result data
            
        Returns:
            Complete HTML report as string
        """
        self._update_language()
        
        # Extract basic scan information
        scan_type = scan_result.get('scan_type', 'Unknown')
        scan_id = scan_result.get('scan_id', 'Unknown')
        timestamp = scan_result.get('timestamp', datetime.now().isoformat())
        region = scan_result.get('region', 'Netherlands')
        
        # Format timestamp based on language
        formatted_timestamp = self._format_timestamp(timestamp)
        
        # Extract metrics
        metrics = self._extract_metrics(scan_result)
        
        # Enhance findings with specific context and actionable recommendations
        original_findings = scan_result.get('findings', [])
        enhanced_findings = enhance_findings_for_report(
            scanner_type=scan_type.lower().replace(' ', '_'),
            findings=original_findings,
            region=region
        )
        
        # Generate findings HTML with enhanced findings
        findings_html = self._generate_findings_html(enhanced_findings)
        
        # Generate scanner-specific content
        scanner_content = self._generate_scanner_specific_content(scan_result)
        
        # Build complete HTML
        html_content = f"""
<!DOCTYPE html>
<html lang="{self.current_language}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{t_report('dataGuardian_pro', 'DataGuardian Pro')} - {scan_type} {t_report('comprehensive_report', 'Report')}</title>
    {self._get_unified_css()}
</head>
<body>
    <div class="container">
        {self._generate_header(scan_type, scan_id, formatted_timestamp, region)}
        {self._generate_executive_summary(metrics)}
        {scanner_content}
        {self._generate_findings_section(findings_html)}
        {self._generate_footer(scan_id, formatted_timestamp)}
    </div>
</body>
</html>
        """
        
        return html_content.strip()
    
    def _format_timestamp(self, timestamp: str) -> str:
        """Format timestamp based on current language."""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            if self.current_language == 'nl':
                return dt.strftime('%d-%m-%Y %H:%M:%S')
            else:
                return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return str(timestamp)
    
    def _extract_metrics(self, scan_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and standardize metrics from scan result."""
        # Handle different metric naming conventions
        summary = scan_result.get('summary', {})
        
        metrics = {
            'files_scanned': (
                summary.get('scanned_files') or 
                scan_result.get('files_scanned') or 
                scan_result.get('pages_scanned') or 
                scan_result.get('images_processed') or 0
            ),
            'lines_analyzed': (
                summary.get('lines_analyzed') or 
                scan_result.get('lines_analyzed') or 
                scan_result.get('content_analysis') or 
                scan_result.get('text_extracted') or 0
            ),
            'total_findings': len(scan_result.get('findings', [])),
            'critical_count': len([f for f in scan_result.get('findings', []) if f.get('severity') == 'Critical']),
            'high_risk_count': (
                summary.get('high_risk_count') or 
                scan_result.get('high_risk_count') or
                len([f for f in scan_result.get('findings', []) if f.get('severity') == 'High'])
            ),
            'medium_risk_count': (
                summary.get('medium_risk_count') or 
                scan_result.get('medium_risk_count') or
                len([f for f in scan_result.get('findings', []) if f.get('severity') == 'Medium'])
            ),
            'low_risk_count': (
                summary.get('low_risk_count') or 
                scan_result.get('low_risk_count') or
                len([f for f in scan_result.get('findings', []) if f.get('severity') == 'Low'])
            ),
            'compliance_score': (
                summary.get('overall_compliance_score') or 
                scan_result.get('compliance_score') or 
                self._calculate_compliance_score(scan_result)
            )
        }
        
        return metrics
    
    def _calculate_compliance_score(self, scan_result: Dict[str, Any]) -> int:
        """Calculate compliance score based on findings."""
        findings = scan_result.get('findings', [])
        if not findings:
            return 100
        
        # Count severity levels
        critical = len([f for f in findings if f.get('severity') == 'Critical'])
        high = len([f for f in findings if f.get('severity') == 'High'])
        medium = len([f for f in findings if f.get('severity') == 'Medium'])
        low = len([f for f in findings if f.get('severity') == 'Low'])
        
        # Calculate penalty
        penalty = (critical * 25) + (high * 15) + (medium * 10) + (low * 5)
        score = max(0, 100 - penalty)
        
        return score
    
    def _get_unified_css(self) -> str:
        """Get unified CSS styles for all report types."""
        return """
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #1f77b4, #2196F3);
            color: white;
            padding: 30px;
            border-radius: 10px 10px 0 0;
            margin-bottom: 0;
        }
        .header h1 {
            margin: 0 0 10px 0;
            font-size: 2.2em;
            font-weight: 300;
        }
        .header p {
            margin: 5px 0;
            opacity: 0.9;
            font-size: 1.1em;
        }
        .summary {
            margin: 30px;
            padding: 25px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 5px solid #28a745;
        }
        .summary h2 {
            margin-top: 0;
            color: #2c5282;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #1f77b4;
            margin: 10px 0;
        }
        .metric-label {
            font-size: 14px;
            color: #6b7280;
        }
        .findings {
            margin: 30px;
        }
        .findings h2 {
            color: #2c5282;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
        }
        .finding {
            margin: 15px 0;
            padding: 20px;
            border-left: 4px solid #dc3545;
            background: #fff;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .finding.critical {
            border-left-color: #dc3545;
            background: #fef2f2;
        }
        .finding.high {
            border-left-color: #fd7e14;
            background: #fef3e8;
        }
        .finding.medium {
            border-left-color: #ffc107;
            background: #fffbeb;
        }
        .finding.low {
            border-left-color: #28a745;
            background: #f0fdf4;
        }
        .finding-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .finding-type {
            font-weight: 600;
            color: #374151;
        }
        .finding-severity {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }
        .severity-critical {
            background: #dc3545;
            color: white;
        }
        .severity-high {
            background: #fd7e14;
            color: white;
        }
        .severity-medium {
            background: #ffc107;
            color: #000;
        }
        .severity-low {
            background: #28a745;
            color: white;
        }
        .finding-description {
            color: #4b5563;
            line-height: 1.6;
        }
        .finding-location {
            font-family: 'Courier New', monospace;
            background: #f3f4f6;
            padding: 8px;
            border-radius: 4px;
            font-size: 13px;
            margin: 10px 0;
        }
        .scanner-specific {
            margin: 30px;
            padding: 25px;
            background: #e8f5e8;
            border-radius: 10px;
        }
        .footer {
            margin-top: 0;
            padding: 20px 30px;
            background: #6c757d;
            color: white;
            text-align: center;
        }
        .footer p {
            margin: 5px 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        th, td {
            padding: 15px;
            border: 1px solid #dee2e6;
            text-align: left;
        }
        th {
            background: #6c757d;
            color: white;
            font-weight: 600;
        }
        .compliance-score {
            font-size: 2em;
            font-weight: bold;
            text-align: center;
            padding: 20px;
        }
        .score-excellent { color: #28a745; }
        .score-good { color: #17a2b8; }
        .score-warning { color: #ffc107; }
        .score-danger { color: #dc3545; }
        
        /* Enhanced findings styles */
        .enhanced-finding {
            margin: 20px 0;
            border-radius: 8px;
        }
        .finding-content {
            margin-top: 15px;
        }
        .finding-content > div {
            margin: 10px 0;
            padding: 8px 0;
        }
        .finding-context, .business-impact {
            background: rgba(0,0,0,0.02);
            border-radius: 4px;
            padding: 12px;
            margin: 10px 0;
        }
        .compliance-section {
            background: #e3f2fd;
            border-radius: 6px;
            padding: 15px;
            margin: 15px 0;
        }
        .compliance-section h4 {
            margin: 0 0 10px 0;
            color: #1565c0;
        }
        .compliance-list {
            list-style: none;
            padding: 0;
        }
        .compliance-list li {
            padding: 4px 0;
            padding-left: 20px;
            position: relative;
        }
        .compliance-list li::before {
            content: "⚖️";
            position: absolute;
            left: 0;
        }
        .recommendations-section {
            background: #f3e5f5;
            border-radius: 6px;
            padding: 15px;
            margin: 15px 0;
        }
        .recommendations-section h4 {
            margin: 0 0 15px 0;
            color: #7b1fa2;
        }
        .recommendation {
            background: white;
            border-radius: 4px;
            padding: 12px;
            margin: 10px 0;
            border-left: 4px solid #9c27b0;
        }
        .recommendation-header {
            font-weight: bold;
            color: #4a148c;
            margin-bottom: 8px;
        }
        .recommendation-details {
            font-size: 0.9em;
            color: #666;
            margin: 6px 0;
        }
        .recommendation-priority {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }
        .priority-critical {
            background: #ffebee;
            color: #c62828;
        }
        .priority-high {
            background: #fff3e0;
            color: #ef6c00;
        }
        .priority-medium {
            background: #fffde7;
            color: #f57f17;
        }
        .priority-low {
            background: #e8f5e8;
            color: #2e7d32;
        }
    </style>
        """
    
    def _generate_header(self, scan_type: str, scan_id: str, timestamp: str, region: str) -> str:
        """Generate report header."""
        return f"""
        <div class="header">
            <h1>🛡️ {t_report('dataGuardian_pro', 'DataGuardian Pro')} {t_report('comprehensive_report', 'Comprehensive Report')}</h1>
            <p><strong>{t_report('scan_type', 'Scan Type')}:</strong> {scan_type}</p>
            <p><strong>{t_report('scan_id', 'Scan ID')}:</strong> {scan_id[:8]}...</p>
            <p><strong>{t_report('generated_on', 'Generated')}:</strong> {timestamp}</p>
            <p><strong>{t_report('region', 'Region')}:</strong> {region}</p>
        </div>
        """
    
    def _generate_executive_summary(self, metrics: Dict[str, Any]) -> str:
        """Generate executive summary section."""
        score = metrics.get('compliance_score', 0)
        score_class = self._get_score_class(score)
        
        return f"""
        <div class="summary">
            <h2>📊 {t_report('executive_summary', 'Executive Summary')}</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{metrics.get('files_scanned', 0):,}</div>
                    <div class="metric-label">{t_report('files_scanned', 'Files Scanned')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{metrics.get('total_findings', 0):,}</div>
                    <div class="metric-label">{t_report('total_findings', 'Total Findings')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{metrics.get('critical_count', 0):,}</div>
                    <div class="metric-label">{t_report('critical_issues', 'Critical Issues')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{metrics.get('high_risk_count', 0):,}</div>
                    <div class="metric-label">{t_technical('high_risk', 'High Risk Issues')}</div>
                </div>
            </div>
            <div class="compliance-score {score_class}">
                {t_technical('compliance_score', 'Compliance Score')}: {score}%
            </div>
        </div>
        """
    
    def _get_score_class(self, score: int) -> str:
        """Get CSS class for compliance score."""
        if score >= 90:
            return 'score-excellent'
        elif score >= 75:
            return 'score-good'
        elif score >= 50:
            return 'score-warning'
        else:
            return 'score-danger'
    
    def _generate_findings_section(self, findings_html: str) -> str:
        """Generate findings section."""
        return f"""
        <div class="findings">
            <h2>🔍 {t_report('detailed_findings', 'Detailed Findings')}</h2>
            {findings_html}
        </div>
        """
    
    def _generate_findings_html(self, findings: List[Dict[str, Any]]) -> str:
        """Generate HTML for enhanced findings list with actionable recommendations."""
        if not findings:
            return f"<p>✅ {t_report('no_issues_found', 'No issues found in the analysis.')}</p>"
        
        findings_html = ""
        for finding in findings:
            # Handle both enhanced and original findings
            severity = finding.get('severity', finding.get('risk_level', 'Low')).lower()
            finding_type = finding.get('title', finding.get('type', finding.get('category', 'Unknown')))
            description = finding.get('description', finding.get('message', 'No description available'))
            location = finding.get('location', 'Unknown')
            
            # Enhanced finding fields
            context = finding.get('context', '')
            business_impact = finding.get('business_impact', '')
            gdpr_articles = finding.get('gdpr_articles', [])
            compliance_requirements = finding.get('compliance_requirements', [])
            recommendations = finding.get('recommendations', [])
            remediation_priority = finding.get('remediation_priority', '')
            estimated_effort = finding.get('estimated_effort', '')
            data_classification = finding.get('data_classification', '')
            
            # Build enhanced finding HTML
            findings_html += f"""
            <div class="finding enhanced-finding {severity}">
                <div class="finding-header">
                    <span class="finding-type">{finding_type}</span>
                    <span class="finding-severity severity-{severity}">{finding.get('severity', finding.get('risk_level', 'Low'))}</span>
                </div>
                
                <div class="finding-content">
                    <div class="finding-description">
                        <strong>Description:</strong> {description}
                    </div>
                    
                    {f'<div class="finding-context"><strong>Context:</strong> {context}</div>' if context else ''}
                    
                    <div class="finding-location">
                        <strong>{t_report('location_details', 'Location')}:</strong> {location}
                    </div>
                    
                    {f'<div class="finding-classification"><strong>Data Classification:</strong> {data_classification}</div>' if data_classification else ''}
                    
                    {f'<div class="business-impact"><strong>Business Impact:</strong> {business_impact}</div>' if business_impact else ''}
                    
                    {f'<div class="remediation-priority"><strong>Priority:</strong> {remediation_priority}</div>' if remediation_priority else ''}
                    
                    {f'<div class="estimated-effort"><strong>Estimated Effort:</strong> {estimated_effort}</div>' if estimated_effort else ''}
                    
                    {self._generate_compliance_section(gdpr_articles, compliance_requirements)}
                    
                    {self._generate_recommendations_section(recommendations)}
                </div>
            </div>
            """
        
        return findings_html
    
    def _generate_scanner_specific_content(self, scan_result: Dict[str, Any]) -> str:
        """Generate scanner-specific content sections."""
        scan_type = scan_result.get('scan_type', '').lower()
        
        if 'sustainability' in scan_type:
            return self._generate_sustainability_content(scan_result)
        elif 'website' in scan_type:
            return self._generate_website_content(scan_result)
        elif 'ai' in scan_type or 'model' in scan_type:
            return self._generate_ai_model_content(scan_result)
        elif 'dpia' in scan_type:
            return self._generate_dpia_content(scan_result)
        else:
            return ""
    
    def _generate_sustainability_content(self, scan_result: Dict[str, Any]) -> str:
        """Generate sustainability-specific metrics."""
        co2_emissions = scan_result.get('co2_emissions', 'N/A')
        energy_consumption = scan_result.get('energy_consumption', 'N/A')
        cost_savings = scan_result.get('cost_savings_potential', 'N/A')
        
        return f"""
        <div class="scanner-specific">
            <h2>🌱 {t_report('sustainability_report', 'Sustainability Metrics')}</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{co2_emissions}</div>
                    <div class="metric-label">CO₂ Emissions/Month</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{energy_consumption}</div>
                    <div class="metric-label">Energy Consumption</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{cost_savings}</div>
                    <div class="metric-label">Potential Cost Savings</div>
                </div>
            </div>
        </div>
        """
    
    def _generate_website_content(self, scan_result: Dict[str, Any]) -> str:
        """Generate website-specific compliance content."""
        cookies_found = scan_result.get('cookies_found', 0)
        trackers_detected = scan_result.get('trackers_detected', 0)
        
        return f"""
        <div class="scanner-specific">
            <h2>🌐 {t_report('website_privacy_report', 'Website Privacy Analysis')}</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{cookies_found}</div>
                    <div class="metric-label">Cookies Found</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{trackers_detected}</div>
                    <div class="metric-label">Trackers Detected</div>
                </div>
            </div>
        </div>
        """
    
    def _generate_compliance_section(self, gdpr_articles: List[str], compliance_requirements: List[str]) -> str:
        """Generate compliance requirements section."""
        if not gdpr_articles and not compliance_requirements:
            return ""
        
        articles_html = ""
        if gdpr_articles:
            articles_html = "<ul class='compliance-list'>"
            for article in gdpr_articles[:3]:  # Limit to first 3 for readability
                articles_html += f"<li>{article}</li>"
            articles_html += "</ul>"
        
        requirements_html = ""
        if compliance_requirements:
            requirements_html = "<ul class='compliance-list'>"
            for requirement in compliance_requirements[:3]:  # Limit to first 3
                requirements_html += f"<li>{requirement}</li>"
            requirements_html += "</ul>"
        
        return f"""
        <div class="compliance-section">
            <h4>⚖️ Compliance Requirements</h4>
            {articles_html}
            {requirements_html}
        </div>
        """
    
    def _generate_recommendations_section(self, recommendations: List[Dict[str, Any]]) -> str:
        """Generate actionable recommendations section."""
        if not recommendations:
            return ""
        
        recommendations_html = ""
        for rec in recommendations[:3]:  # Limit to first 3 for readability
            priority = rec.get('priority', 'Medium').lower()
            priority_class = f"priority-{priority}"
            
            recommendations_html += f"""
            <div class="recommendation">
                <div class="recommendation-header">
                    {rec.get('action', 'Action Required')}
                    <span class="recommendation-priority {priority_class}">{rec.get('priority', 'Medium')}</span>
                </div>
                <div class="recommendation-details">
                    <strong>Description:</strong> {rec.get('description', 'No description available')}
                </div>
                <div class="recommendation-details">
                    <strong>Implementation:</strong> {rec.get('implementation', 'Implementation details not specified')}
                </div>
                <div class="recommendation-details">
                    <strong>Effort:</strong> {rec.get('effort_estimate', 'Not estimated')} | 
                    <strong>Verification:</strong> {rec.get('verification', 'Verification method not specified')}
                </div>
            </div>
            """
        
        return f"""
        <div class="recommendations-section">
            <h4>💡 Actionable Recommendations</h4>
            {recommendations_html}
        </div>
        """

    def _generate_ai_model_content(self, scan_result: Dict[str, Any]) -> str:
        """Generate AI model-specific compliance content."""
        model_framework = scan_result.get('model_framework', 'Unknown')
        ai_act_compliance = scan_result.get('ai_act_compliance', 'Not assessed')
        
        return f"""
        <div class="scanner-specific">
            <h2>🤖 {t_report('ai_model_compliance', 'AI Model Compliance')}</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{model_framework}</div>
                    <div class="metric-label">Model Framework</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{ai_act_compliance}</div>
                    <div class="metric-label">AI Act 2025 Status</div>
                </div>
            </div>
        </div>
        """
    
    def _generate_dpia_content(self, scan_result: Dict[str, Any]) -> str:
        """Generate DPIA-specific content."""
        risk_score = scan_result.get('risk_score', 'Unknown')
        overall_risk_level = scan_result.get('overall_risk_level', 'Unknown')
        
        return f"""
        <div class="scanner-specific">
            <h2>⚖️ {t_report('dpia_assessment', 'DPIA Assessment')}</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{risk_score}</div>
                    <div class="metric-label">Risk Score</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{overall_risk_level}</div>
                    <div class="metric-label">Risk Level</div>
                </div>
            </div>
        </div>
        """
    
    def _generate_footer(self, scan_id: str, timestamp: str) -> str:
        """Generate report footer."""
        return f"""
        <div class="footer">
            <p>{t_report('generated_by', 'Generated by')} {t_report('dataGuardian_pro', 'DataGuardian Pro')} - {t_report('privacy_compliance_platform', 'Enterprise Privacy & Sustainability Compliance Platform')}</p>
            <p>Report ID: {scan_id} | {t_report('generated_on', 'Generated')}: {timestamp}</p>
        </div>
        """

# Global instance for unified report generation
_unified_generator = None

def get_unified_generator() -> UnifiedHTMLReportGenerator:
    """Get the global unified HTML report generator."""
    global _unified_generator
    if _unified_generator is None:
        _unified_generator = UnifiedHTMLReportGenerator()
    return _unified_generator

def generate_unified_html_report(scan_result: Dict[str, Any]) -> str:
    """
    Generate a unified HTML report using the global generator.
    
    Args:
        scan_result: Scan result data
        
    Returns:
        Complete HTML report as string
    """
    generator = get_unified_generator()
    return generator.generate_html_report(scan_result)

def generate_comprehensive_report(scan_result: Dict[str, Any]) -> str:
    """
    Generate a comprehensive HTML report (alias for backward compatibility).
    
    Args:
        scan_result: Scan result data
        
    Returns:
        Complete HTML report as string
    """
    return generate_unified_html_report(scan_result)