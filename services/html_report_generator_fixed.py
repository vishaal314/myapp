"""
HTML Report Generator for DataGuardian Pro

This module generates HTML reports for scan results with proper syntax
and comprehensive website scanning support including in-depth cookie analysis.
"""

import os
import base64
from typing import Dict, Any

try:
    import streamlit as st
except ImportError:
    # Mock streamlit for environments where it's not available
    class StreamlitMock:
        session_state = {"language": "en"}
    
    st = StreamlitMock()

# Mock translation function for standalone usage
def _(key, default=None):
    return default or key.split('.')[-1].replace('_', ' ').title()

def save_html_report(scan_data: Dict[str, Any], output_dir: str = "reports") -> str:
    """
    Save a HTML report for a scan result.
    
    Args:
        scan_data: The scan result data
        output_dir: Directory to save the report
        
    Returns:
        Path to the saved HTML file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename
    scan_id = scan_data.get('scan_id', 'unknown')
    filename = f"report_{scan_id}.html"
    
    # Handle datetime objects that might not be JSON serializable
    if 'timestamp' in scan_data and hasattr(scan_data['timestamp'], 'isoformat'):
        scan_data['timestamp'] = scan_data['timestamp'].isoformat()
        
    file_path = os.path.join(output_dir, filename)
    
    # Create HTML content
    html_content = generate_html_report(scan_data)
    
    # Write to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return file_path

def get_html_report_as_base64(scan_data: Dict[str, Any]) -> str:
    """
    Generate a base64-encoded HTML report for a scan result.
    
    Args:
        scan_data: The scan result data
        
    Returns:
        Base64-encoded HTML report
    """
    html_content = generate_html_report(scan_data)
    html_bytes = html_content.encode('utf-8')
    return base64.b64encode(html_bytes).decode('utf-8')

def generate_html_report(scan_data: Dict[str, Any]) -> str:
    """
    Generate a HTML report for a scan result.
    
    Args:
        scan_data: The scan result data
        
    Returns:
        HTML report as a string
    """
    # Get current language from session state
    current_lang = st.session_state.get('language', 'en')
    
    # Extract basic scan info
    scan_id = scan_data.get('scan_id', 'Unknown')
    scan_type = scan_data.get('scan_type', 'Unknown')
    region = scan_data.get('region', 'Unknown')
    timestamp = scan_data.get('timestamp', 'Unknown')
    
    # Check if this is a website scan
    is_website_scan = scan_type.lower() == 'website'
    
    # Generate website-specific content
    website_content = ""
    if is_website_scan:
        website_content = generate_website_report_content(scan_data, timestamp)
    
    # Basic HTML structure with website content
    html_content = f"""<!DOCTYPE html>
<html lang="{current_lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DataGuardian Pro - Website Privacy Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #1e40af, #3b82f6);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .content {{
            padding: 0;
        }}
        .metric-card {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .metric-label {{
            font-size: 16px;
            color: #6b7280;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border: 1px solid #e5e7eb;
        }}
        th {{
            background: #f9fafb;
            font-weight: 600;
        }}
        .severity-high {{ background: #fef2f2; color: #dc2626; }}
        .severity-medium {{ background: #fef3c7; color: #d97706; }}
        .severity-low {{ background: #f0fdf4; color: #16a34a; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌐 Website Privacy Compliance Report</h1>
            <p>DataGuardian Pro Enterprise Privacy Assessment</p>
        </div>
        <div class="content">
            {website_content}
        </div>
    </div>
</body>
</html>"""
    
    return html_content

def generate_website_report_content(scan_data: Dict[str, Any], timestamp: str) -> str:
    """Generate comprehensive website report content with in-depth cookie analysis."""
    
    # Extract data
    url = scan_data.get('url', scan_data.get('base_domain', 'Website Analysis'))
    stats = scan_data.get('stats', {})
    findings = scan_data.get('findings', [])
    cookies = scan_data.get('cookies', {})
    cookie_categories = scan_data.get('cookie_categories', {})
    trackers = scan_data.get('trackers', [])
    
    # Generate findings table
    findings_html = ""
    if findings:
        findings_rows = ""
        for i, finding in enumerate(findings[:20]):
            severity = finding.get('severity', 'Low')
            severity_class = f"severity-{severity.lower()}"
            bg_color = '#fef2f2' if i % 2 == 0 else '#fef7f7'
            
            findings_rows += f"""
            <tr style="background-color: {bg_color};">
                <td>{finding.get('type', 'Unknown')}</td>
                <td><span class="{severity_class}" style="padding: 4px 8px; border-radius: 4px; font-size: 12px;">{severity}</span></td>
                <td>{(finding.get('description', '')[:80] + '...' if len(finding.get('description', '')) > 80 else finding.get('description', ''))}</td>
                <td style="font-size: 12px;">{(finding.get('url', '')[:30] + '...' if len(finding.get('url', '')) > 30 else finding.get('url', ''))}</td>
            </tr>"""
        
        findings_html = f"""
        <div style="background: white; border-radius: 15px; padding: 30px; margin: 20px; box-shadow: 0 6px 20px rgba(0,0,0,0.1);">
            <h2 style="color: #dc2626; margin-bottom: 20px;">🔍 Privacy Findings</h2>
            <table>
                <thead>
                    <tr style="background: linear-gradient(135deg, #dc2626, #b91c1c); color: white;">
                        <th>Type</th>
                        <th>Severity</th>
                        <th>Description</th>
                        <th>URL</th>
                    </tr>
                </thead>
                <tbody>
                    {findings_rows}
                </tbody>
            </table>
            <p style="color: #6b7280; font-style: italic; margin-top: 15px;">Showing {min(20, len(findings))} of {len(findings)} total findings</p>
        </div>"""
    
    # Generate comprehensive cookie analysis
    cookie_html = ""
    if cookies:
        # Category breakdown
        category_rows = ""
        for category, count in cookie_categories.items():
            category_rows += f"""
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px; padding: 8px 0; border-bottom: 1px solid #fde68a;">
                <span style="color: #92400e; font-weight: 500;">{category.title()}</span>
                <span style="color: #92400e; font-weight: bold;">{count}</span>
            </div>"""
        
        # Detailed cookie table
        cookie_rows = ""
        for i, (name, cookie_data) in enumerate(list(cookies.items())[:15]):
            bg_color = '#fef3c7' if i % 2 == 0 else '#fde68a'
            purpose = cookie_data.get('purpose', 'Unknown')[:30] + ('...' if len(cookie_data.get('purpose', '')) > 30 else '')
            
            cookie_rows += f"""
            <tr style="background-color: {bg_color};">
                <td style="font-weight: 500;">{name}</td>
                <td>{cookie_data.get('category', 'Unknown')}</td>
                <td>{purpose}</td>
                <td>{'Yes' if cookie_data.get('persistent', True) else 'No'}</td>
                <td>{cookie_data.get('expiry', 'Session')}</td>
            </tr>"""
        
        session_count = sum(1 for cookie in cookies.values() if not cookie.get('persistent', True))
        persistent_count = sum(1 for cookie in cookies.values() if cookie.get('persistent', True))
        
        cookie_html = f"""
        <div style="background: white; border-radius: 15px; padding: 30px; margin: 20px; box-shadow: 0 6px 20px rgba(0,0,0,0.1);">
            <h2 style="color: #f59e0b; margin-bottom: 20px;">🍪 In-Depth Cookie Analysis</h2>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 30px;">
                <div>
                    <h3 style="color: #92400e; margin-bottom: 15px;">Cookie Categories</h3>
                    <div style="background: #fef3c7; padding: 20px; border-radius: 10px;">
                        {category_rows}
                    </div>
                </div>
                
                <div>
                    <h3 style="color: #92400e; margin-bottom: 15px;">Cookie Summary</h3>
                    <div style="background: #fef3c7; padding: 20px; border-radius: 10px;">
                        <div style="margin-bottom: 10px;">
                            <strong style="color: #92400e;">Total Cookies:</strong>
                            <span style="color: #78350f;">{len(cookies)}</span>
                        </div>
                        <div style="margin-bottom: 10px;">
                            <strong style="color: #92400e;">Session Cookies:</strong>
                            <span style="color: #78350f;">{session_count}</span>
                        </div>
                        <div>
                            <strong style="color: #92400e;">Persistent Cookies:</strong>
                            <span style="color: #78350f;">{persistent_count}</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <h3 style="color: #92400e; margin-bottom: 15px;">Detailed Cookie Inventory</h3>
            <table>
                <thead>
                    <tr style="background: linear-gradient(135deg, #f59e0b, #d97706); color: white;">
                        <th>Name</th>
                        <th>Category</th>
                        <th>Purpose</th>
                        <th>Persistent</th>
                        <th>Expiry</th>
                    </tr>
                </thead>
                <tbody>
                    {cookie_rows}
                </tbody>
            </table>
            <p style="color: #6b7280; font-style: italic; margin-top: 15px;">Showing {min(15, len(cookies))} of {len(cookies)} total cookies</p>
        </div>"""
    
    # Generate tracker analysis
    tracker_html = ""
    if trackers:
        tracker_rows = ""
        for i, tracker in enumerate(trackers[:15]):
            bg_color = '#f3e8ff' if i % 2 == 0 else '#faf5ff'
            risk = tracker.get('privacy_risk', 'Low')
            risk_class = f"severity-{risk.lower()}"
            
            tracker_rows += f"""
            <tr style="background-color: {bg_color};">
                <td style="font-weight: 500;">{tracker.get('name', 'Unknown')}</td>
                <td>{tracker.get('type', 'Unknown')}</td>
                <td>{(tracker.get('purpose', 'Unknown')[:40] + '...' if len(tracker.get('purpose', '')) > 40 else tracker.get('purpose', 'Unknown'))}</td>
                <td><span class="{risk_class}" style="padding: 4px 8px; border-radius: 4px; font-size: 12px;">{risk}</span></td>
            </tr>"""
        
        tracker_html = f"""
        <div style="background: white; border-radius: 15px; padding: 30px; margin: 20px; box-shadow: 0 6px 20px rgba(0,0,0,0.1);">
            <h2 style="color: #7c3aed; margin-bottom: 20px;">📊 Tracking Analysis</h2>
            <table>
                <thead>
                    <tr style="background: linear-gradient(135deg, #7c3aed, #6d28d9); color: white;">
                        <th>Name</th>
                        <th>Type</th>
                        <th>Purpose</th>
                        <th>Privacy Risk</th>
                    </tr>
                </thead>
                <tbody>
                    {tracker_rows}
                </tbody>
            </table>
            <p style="color: #6b7280; font-style: italic; margin-top: 15px;">Showing {min(15, len(trackers))} of {len(trackers)} total trackers</p>
        </div>"""
    
    return f"""
    <div style="background: white; border-radius: 15px; padding: 30px; margin: 20px; box-shadow: 0 6px 20px rgba(0,0,0,0.1);">
        <h2 style="color: #1e40af; margin-bottom: 20px;">📊 Scan Overview</h2>
        
        <div style="background: linear-gradient(135deg, #f0f9ff, #e0f2fe); padding: 20px; border-radius: 10px; margin-bottom: 25px;">
            <h3 style="color: #0c4a6e; margin: 0 0 15px 0;">Scanned Website:</h3>
            <p style="color: #0369a1; font-size: 18px; font-weight: bold; margin: 0;">{url}</p>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 25px 0;">
            <div class="metric-card" style="background: linear-gradient(135deg, #3b82f6, #1d4ed8); color: white;">
                <div class="metric-value">{stats.get('pages_scanned', 0)}</div>
                <div class="metric-label" style="color: white;">Pages Scanned</div>
            </div>
            
            <div class="metric-card" style="background: linear-gradient(135deg, #dc2626, #b91c1c); color: white;">
                <div class="metric-value">{stats.get('total_findings', 0)}</div>
                <div class="metric-label" style="color: white;">Total Findings</div>
            </div>
            
            <div class="metric-card" style="background: linear-gradient(135deg, #f59e0b, #d97706); color: white;">
                <div class="metric-value">{stats.get('total_cookies', 0)}</div>
                <div class="metric-label" style="color: white;">Cookies Found</div>
            </div>
            
            <div class="metric-card" style="background: linear-gradient(135deg, #7c3aed, #6d28d9); color: white;">
                <div class="metric-value">{stats.get('total_trackers', 0)}</div>
                <div class="metric-label" style="color: white;">Trackers Detected</div>
            </div>
        </div>
        
        <div style="background: #f8fafc; padding: 20px; border-radius: 10px; margin: 25px 0;">
            <h3 style="color: #374151; margin-bottom: 15px;">Additional Scan Details</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                    <strong style="color: #1f2937;">Scan Duration:</strong>
                    <span style="color: #4b5563;">{scan_data.get('duration_seconds', 0):.1f} seconds</span>
                </div>
                <div>
                    <strong style="color: #1f2937;">Scan Timestamp:</strong>
                    <span style="color: #4b5563;">{scan_data.get('scan_time', timestamp)}</span>
                </div>
            </div>
        </div>
    </div>
    
    {findings_html}
    {cookie_html}
    {tracker_html}
    
    <div style="background: white; border-radius: 15px; margin: 20px; padding: 30px; text-align: center; box-shadow: 0 6px 20px rgba(0,0,0,0.1);">
        <p style="color: #374151; font-size: 12px; line-height: 1.6; max-width: 600px; margin: 0 auto;">
            This website privacy assessment was conducted on {timestamp} using DataGuardian Pro's comprehensive 
            website scanner. The assessment analyzed privacy compliance, cookie usage, tracker detection, and GDPR compliance requirements.
        </p>
        <div style="margin-top: 30px; padding-top: 20px; border-top: 2px solid #e5e7eb;">
            <p style="color: #6b7280; font-size: 11px; margin: 5px 0;">
                <strong>DataGuardian Pro Enterprise Certification Authority</strong>
            </p>
            <p style="color: #6b7280; font-size: 10px; margin: 0;">
                Enterprise Privacy & Compliance Platform
            </p>
        </div>
    </div>"""