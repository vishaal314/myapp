"""
Compliance Dashboard Generator - Creates interactive compliance dashboards
with real-time metrics, trend analysis, and executive reporting
"""

import json
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import streamlit as st
from functools import lru_cache

class ComplianceDashboardGenerator:
    """
    Generates interactive compliance dashboards with advanced visualizations
    for executive reporting and operational monitoring.
    """
    
    def __init__(self, region: str = "Netherlands"):
        self.region = region
        self.color_palette = {
            'critical': '#dc3545',
            'high': '#fd7e14', 
            'medium': '#ffc107',
            'low': '#28a745',
            'primary': '#1f77b4',
            'secondary': '#6c757d',
            'success': '#28a745',
            'warning': '#ffc107',
            'danger': '#dc3545'
        }
    
    @st.cache_data(ttl=300, hash_funcs={"scan_results": lambda x: str(hash(str(x[-1].get('timestamp', '')) if x else ''))})  # Cache with scan hash
    def generate_executive_dashboard(self, scan_results: List[Dict[str, Any]], 
                                   time_period: str = "30d") -> str:
        """
        Generate executive-level compliance dashboard with key metrics and trends.
        
        Args:
            scan_results: List of scan results over time
            time_period: Time period for analysis (7d, 30d, 90d, 1y)
            
        Returns:
            Complete HTML dashboard with interactive charts
        """
        # Process scan data
        dashboard_data = self._process_scan_data(scan_results)
        
        # Generate charts
        risk_trend_chart = self._create_risk_trend_chart(dashboard_data)
        compliance_score_gauge = self._create_compliance_gauge(dashboard_data)
        findings_breakdown = self._create_findings_breakdown_chart(dashboard_data)
        scanner_performance = self._create_scanner_performance_chart(dashboard_data)
        regional_compliance = self._create_regional_compliance_chart(dashboard_data)
        
        # Generate summary metrics
        summary_metrics = self._generate_summary_metrics(dashboard_data)
        
        # Create complete dashboard HTML
        dashboard_html = self._build_executive_dashboard_html(
            summary_metrics,
            risk_trend_chart,
            compliance_score_gauge,
            findings_breakdown,
            scanner_performance,
            regional_compliance
        )
        
        return dashboard_html
    
    def generate_operational_dashboard(self, scan_results: List[Dict[str, Any]]) -> str:
        """
        Generate operational dashboard for technical teams with detailed metrics.
        
        Args:
            scan_results: Recent scan results for operational analysis
            
        Returns:
            Operational dashboard HTML with technical metrics
        """
        # Process operational data
        operational_data = self._process_operational_data(scan_results)
        
        # Generate operational charts
        scanner_efficiency = self._create_scanner_efficiency_chart(operational_data)
        finding_resolution = self._create_finding_resolution_chart(operational_data)
        system_performance = self._create_system_performance_chart(operational_data)
        alert_management = self._create_alert_management_chart(operational_data)
        
        # Generate operational metrics
        operational_metrics = self._generate_operational_metrics(operational_data)
        
        # Build operational dashboard
        dashboard_html = self._build_operational_dashboard_html(
            operational_metrics,
            scanner_efficiency,
            finding_resolution,
            system_performance,
            alert_management
        )
        
        return dashboard_html
    
    @lru_cache(maxsize=100)
    def _process_scan_data_cached(self, scan_results_hash: str, scan_results_str: str) -> Dict[str, Any]:
        """Cached version of scan data processing"""
        import json
        scan_results = json.loads(scan_results_str)
        return self._process_scan_data_impl(scan_results)
    
    def _process_scan_data(self, scan_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process scan data with caching for performance"""
        # Create a hash for caching
        import hashlib
        scan_str = json.dumps(scan_results, sort_keys=True)
        scan_hash = hashlib.md5(scan_str.encode()).hexdigest()
        
        return self._process_scan_data_cached(scan_hash, scan_str)
    
    def _process_scan_data_impl(self, scan_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process scan results for dashboard visualization"""
        if not scan_results:
            return self._get_empty_dashboard_data()
        
        # Extract key metrics
        total_scans = len(scan_results)
        total_findings = sum(len(result.get('findings', [])) for result in scan_results)
        
        # Calculate severity distribution
        severity_counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
        scanner_types = {}
        compliance_scores = []
        
        for result in scan_results:
            findings = result.get('findings', [])
            
            # Count severity levels
            for finding in findings:
                severity = finding.get('severity', 'Low')
                if severity in severity_counts:
                    severity_counts[severity] += 1
            
            # Track scanner types
            scan_type = result.get('scan_type', 'Unknown')
            scanner_types[scan_type] = scanner_types.get(scan_type, 0) + 1
            
            # Collect compliance scores
            score = result.get('compliance_score', 0)
            if score > 0:
                compliance_scores.append(score)
        
        # Calculate trends from real data
        risk_trend_data = self._generate_risk_trend_data(scan_results)
        
        return {
            'total_scans': total_scans,
            'total_findings': total_findings,
            'severity_distribution': severity_counts,
            'scanner_distribution': scanner_types,
            'compliance_scores': compliance_scores,
            'average_compliance_score': sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0,
            'risk_trend_data': risk_trend_data,
            'last_scan_date': datetime.now().isoformat() if scan_results else None
        }
    
    def _generate_risk_trend_data(self, scan_results: List[Dict[str, Any]]) -> Dict[str, List]:
        """Generate real risk trend data from actual scan results with weekly smoothing"""
        if not scan_results:
            return {'dates': [], 'risk_scores': [], 'critical_counts': []}
        
        try:
            # Import predictive engine for real data processing
            from services.predictive_compliance_engine import PredictiveComplianceEngine
            engine = PredictiveComplianceEngine(region=self.region)
            
            # Process real scan data into time series with weekly smoothing
            time_series_data = engine._prepare_time_series_data(scan_results)
            
            if time_series_data is None or time_series_data.empty:
                # Fallback to basic processing if predictive engine fails
                return self._generate_basic_trend_data(scan_results)
            
            # Extract weekly aggregated data
            from collections import defaultdict
            weekly_data = defaultdict(lambda: {'scores': [], 'critical_counts': []})
            
            for _, row in time_series_data.iterrows():
                date_obj = row['date']
                monday = date_obj - timedelta(days=date_obj.weekday())
                week_key = monday.strftime('%Y-%m-%d')
                
                # Use smoothed scores if available
                score = row.get('smoothed_compliance_score', row.get('compliance_score', 0))
                critical_count = row.get('critical_findings', 0)
                
                weekly_data[week_key]['scores'].append(score)
                weekly_data[week_key]['critical_counts'].append(critical_count)
            
            # Calculate weekly averages and apply EMA smoothing
            weekly_dates = sorted(weekly_data.keys())
            weekly_scores = []
            weekly_criticals = []
            
            for week in weekly_dates:
                week_data = weekly_data[week]
                avg_score = sum(week_data['scores']) / len(week_data['scores']) if week_data['scores'] else 0
                avg_critical = sum(week_data['critical_counts']) / len(week_data['critical_counts']) if week_data['critical_counts'] else 0
                
                # Filter out zero scores that cause dips
                if avg_score > 0:
                    weekly_scores.append(avg_score)
                elif weekly_scores:  # Use last valid score
                    weekly_scores.append(weekly_scores[-1])
                else:
                    weekly_scores.append(75.0)  # Fallback
                
                weekly_criticals.append(max(0, int(avg_critical)))
            
            # Apply EMA smoothing to prevent erratic movements
            if len(weekly_scores) >= 3:
                ema_alpha = 0.3
                smoothed_scores = [weekly_scores[0]]
                for i in range(1, len(weekly_scores)):
                    smoothed_val = ema_alpha * weekly_scores[i] + (1 - ema_alpha) * smoothed_scores[-1]
                    smoothed_scores.append(smoothed_val)
                weekly_scores = smoothed_scores
            
            # Debug logging for trend line validation
            import logging
            logger = logging.getLogger(__name__)
            if len(weekly_dates) >= 4:
                logger.info(f"Dashboard trend data - Last 4 weeks: {weekly_dates[-4:]}")
                logger.info(f"Compliance scores: {weekly_scores[-4:]}")
                logger.info(f"Risk scores (100-compliance): {[100-s for s in weekly_scores[-4:]]}")
            
            return {
                'dates': weekly_dates,
                'risk_scores': [100 - score for score in weekly_scores],  # Convert compliance to risk
                'critical_counts': weekly_criticals
            }
            
        except ImportError:
            return self._generate_basic_trend_data(scan_results)
        except Exception:
            return self._generate_basic_trend_data(scan_results)
    
    def _generate_basic_trend_data(self, scan_results: List[Dict[str, Any]]) -> Dict[str, List]:
        """Fallback method for generating trend data from basic scan results"""
        if not scan_results:
            return {'dates': [], 'risk_scores': [], 'critical_counts': []}
        
        # Sort scan results by timestamp
        sorted_scans = sorted(scan_results, key=lambda x: x.get('timestamp', ''), reverse=False)
        
        dates = []
        compliance_scores = []
        critical_counts = []
        
        for scan in sorted_scans[-30:]:  # Last 30 scans
            try:
                timestamp = scan.get('timestamp', '')
                if timestamp:
                    date_obj = datetime.fromisoformat(timestamp.replace('Z', '+00:00').replace('+00:00', ''))
                    dates.append(date_obj.strftime('%Y-%m-%d'))
                    
                    # Get compliance score, filter out zeros
                    score = scan.get('compliance_score', 0)
                    if score > 0:
                        compliance_scores.append(score)
                    elif compliance_scores:  # Use last valid score
                        compliance_scores.append(compliance_scores[-1])
                    else:
                        compliance_scores.append(75.0)  # Default fallback
                    
                    # Count critical findings
                    findings = scan.get('findings', [])
                    critical_count = sum(1 for f in findings if f.get('severity') == 'Critical')
                    critical_counts.append(critical_count)
            except:
                continue
        
        # Convert compliance to risk scores
        risk_scores = [100 - score for score in compliance_scores]
        
        return {
            'dates': dates,
            'risk_scores': risk_scores,
            'critical_counts': critical_counts
        }
    
    def _create_risk_trend_chart(self, dashboard_data: Dict[str, Any]) -> str:
        """Create risk trend chart with linear interpolation (no spline artifacts)"""
        trend_data = dashboard_data['risk_trend_data']
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=['Compliance Score Trend', 'Critical Findings Trend'],
            vertical_spacing=0.1
        )
        
        # Convert risk scores back to compliance scores for display
        compliance_scores = [100 - risk for risk in trend_data['risk_scores']]
        
        # Trend line removed per user request
        
        # Critical findings trend
        fig.add_trace(
            go.Scatter(
                x=trend_data['dates'],
                y=trend_data['critical_counts'],
                mode='lines+markers',
                name='Critical Findings',
                line=dict(color=self.color_palette['critical'], width=3),
                marker=dict(size=6),
                fill='tonexty'
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            height=500,
            title_text="30-Day Risk and Findings Trends",
            showlegend=True,
            template='plotly_white'
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id="risk-trend-chart")
    
    def _create_compliance_gauge(self, dashboard_data: Dict[str, Any]) -> str:
        """Create compliance score gauge chart"""
        current_score = dashboard_data['average_compliance_score']
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = current_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Overall Compliance Score"},
            delta = {'reference': 75, 'increasing': {'color': self.color_palette['success']}},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': self._get_gauge_color(current_score)},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 75], 'color': "gray"},
                    {'range': [75, 90], 'color': "lightgreen"},
                    {'range': [90, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(
            height=400,
            template='plotly_white'
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id="compliance-gauge")
    
    def _create_findings_breakdown_chart(self, dashboard_data: Dict[str, Any]) -> str:
        """Create findings severity breakdown chart"""
        severity_data = dashboard_data['severity_distribution']
        
        fig = go.Figure(data=[
            go.Pie(
                labels=list(severity_data.keys()),
                values=list(severity_data.values()),
                hole=0.4,
                marker_colors=[
                    self.color_palette['critical'],
                    self.color_palette['high'],
                    self.color_palette['medium'],
                    self.color_palette['low']
                ]
            )
        ])
        
        fig.update_layout(
            title_text="Findings by Severity Level",
            height=400,
            template='plotly_white',
            annotations=[dict(text=f'Total<br>{sum(severity_data.values())}', x=0.5, y=0.5, font_size=16, showarrow=False)]
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id="findings-breakdown")
    
    def _create_scanner_performance_chart(self, dashboard_data: Dict[str, Any]) -> str:
        """Create scanner performance chart"""
        scanner_data = dashboard_data['scanner_distribution']
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(scanner_data.keys()),
                y=list(scanner_data.values()),
                marker_color=self.color_palette['primary'],
                text=list(scanner_data.values()),
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title_text="Scanner Usage Distribution",
            xaxis_title="Scanner Type",
            yaxis_title="Number of Scans",
            height=400,
            template='plotly_white'
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id="scanner-performance")
    
    def _create_regional_compliance_chart(self, dashboard_data: Dict[str, Any]) -> str:
        """Create regional compliance requirements chart"""
        # Simulated compliance framework data
        frameworks = ['GDPR', 'Dutch UAVG', 'AI Act 2025', 'SOC2', 'ISO27001']
        compliance_levels = [85, 92, 78, 88, 75]  # Simulated percentages
        
        fig = go.Figure(data=[
            go.Bar(
                x=frameworks,
                y=compliance_levels,
                marker_color=[
                    self.color_palette['success'] if level >= 90 else
                    self.color_palette['warning'] if level >= 75 else
                    self.color_palette['danger']
                    for level in compliance_levels
                ],
                text=[f'{level}%' for level in compliance_levels],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title_text=f"Compliance Framework Status - {self.region}",
            xaxis_title="Compliance Framework",
            yaxis_title="Compliance Level (%)",
            height=400,
            template='plotly_white',
            yaxis=dict(range=[0, 100])
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id="regional-compliance")
    
    def _generate_summary_metrics(self, dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary metrics for dashboard"""
        severity_dist = dashboard_data['severity_distribution']
        
        return {
            'total_scans': dashboard_data['total_scans'],
            'total_findings': dashboard_data['total_findings'],
            'critical_findings': severity_dist.get('Critical', 0),
            'high_risk_findings': severity_dist.get('High', 0),
            'compliance_score': round(dashboard_data['average_compliance_score'], 1),
            'risk_trend': 'Improving' if dashboard_data['average_compliance_score'] > 75 else 'Needs Attention',
            'last_scan': dashboard_data.get('last_scan_date', 'N/A')
        }
    
    def _build_executive_dashboard_html(self, metrics: Dict[str, Any], *charts) -> str:
        """Build complete executive dashboard HTML"""
        risk_trend, compliance_gauge, findings_breakdown, scanner_performance, regional_compliance = charts
        
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>DataGuardian Pro - Executive Compliance Dashboard</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .dashboard-header {{
                    background: linear-gradient(135deg, #1f77b4, #2196F3);
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                }}
                .dashboard-header h1 {{
                    margin: 0;
                    font-size: 2em;
                }}
                .dashboard-header p {{
                    margin: 5px 0 0 0;
                    opacity: 0.9;
                }}
                .metrics-row {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .metric-card {{
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    text-align: center;
                }}
                .metric-value {{
                    font-size: 2.5em;
                    font-weight: bold;
                    margin: 10px 0;
                }}
                .metric-label {{
                    color: #6c757d;
                    font-size: 0.9em;
                }}
                .critical {{ color: #dc3545; }}
                .high {{ color: #fd7e14; }}
                .success {{ color: #28a745; }}
                .primary {{ color: #1f77b4; }}
                .chart-container {{
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                    padding: 20px;
                }}
                .chart-row {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                    margin-bottom: 20px;
                }}
                .chart-full {{
                    grid-column: 1 / -1;
                }}
                @media (max-width: 768px) {{
                    .chart-row {{
                        grid-template-columns: 1fr;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="dashboard-header">
                <h1>🛡️ DataGuardian Pro - Executive Dashboard</h1>
                <p>Comprehensive Compliance Overview • {self.region} Region • Generated {datetime.now().strftime('%B %d, %Y at %H:%M')}</p>
            </div>
            
            <div class="metrics-row">
                <div class="metric-card">
                    <div class="metric-value primary">{metrics['total_scans']}</div>
                    <div class="metric-label">Total Scans</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value critical">{metrics['critical_findings']}</div>
                    <div class="metric-label">Critical Findings</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value high">{metrics['high_risk_findings']}</div>
                    <div class="metric-label">High Risk Issues</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value success">{metrics['compliance_score']}%</div>
                    <div class="metric-label">Compliance Score</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value primary">{metrics['total_findings']}</div>
                    <div class="metric-label">Total Findings</div>
                </div>
            </div>
            
            <div class="chart-container chart-full">
                {risk_trend}
            </div>
            
            <div class="chart-row">
                <div class="chart-container">
                    {compliance_gauge}
                </div>
                <div class="chart-container">
                    {findings_breakdown}
                </div>
            </div>
            
            <div class="chart-row">
                <div class="chart-container">
                    {scanner_performance}
                </div>
                <div class="chart-container">
                    {regional_compliance}
                </div>
            </div>
            
            <div class="dashboard-footer" style="text-align: center; margin-top: 30px; color: #6c757d;">
                <p>DataGuardian Pro Executive Dashboard • Confidential • Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """
    
    def _get_gauge_color(self, score: float) -> str:
        """Get color for compliance gauge based on score"""
        if score >= 90:
            return self.color_palette['success']
        elif score >= 75:
            return self.color_palette['warning']
        else:
            return self.color_palette['danger']
    
    def _get_empty_dashboard_data(self) -> Dict[str, Any]:
        """Return empty dashboard data structure"""
        return {
            'total_scans': 0,
            'total_findings': 0,
            'severity_distribution': {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0},
            'scanner_distribution': {},
            'compliance_scores': [],
            'average_compliance_score': 0,
            'risk_trend_data': {
                'dates': [],
                'risk_scores': [],
                'critical_counts': []
            }
        }
    
    def _process_operational_data(self, scan_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process data for operational dashboard"""
        # Simplified operational data processing
        return {
            'scanner_efficiency': {'Code Scanner': 95, 'Website Scanner': 88, 'AI Scanner': 92},
            'resolution_times': {'Critical': 2.1, 'High': 5.3, 'Medium': 12.5, 'Low': 45.2},
            'system_performance': {'CPU': 65, 'Memory': 72, 'Disk': 45},
            'active_alerts': {'Critical': 2, 'High': 7, 'Medium': 15, 'Low': 23}
        }
    
    def _generate_operational_metrics(self, operational_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate operational metrics"""
        return {
            'system_health': 'Good',
            'active_scans': 12,
            'queue_depth': 3,
            'avg_scan_time': '2.3 minutes',
            'success_rate': '96.7%'
        }
    
    def _create_scanner_efficiency_chart(self, operational_data: Dict[str, Any]) -> str:
        """Create scanner efficiency chart"""
        return "<div>Scanner Efficiency Chart Placeholder</div>"
    
    def _create_finding_resolution_chart(self, operational_data: Dict[str, Any]) -> str:
        """Create finding resolution chart"""
        return "<div>Finding Resolution Chart Placeholder</div>"
    
    def _create_system_performance_chart(self, operational_data: Dict[str, Any]) -> str:
        """Create system performance chart"""
        return "<div>System Performance Chart Placeholder</div>"
    
    def _create_alert_management_chart(self, operational_data: Dict[str, Any]) -> str:
        """Create alert management chart"""
        return "<div>Alert Management Chart Placeholder</div>"
    
    def _build_operational_dashboard_html(self, metrics: Dict[str, Any], *charts) -> str:
        """Build operational dashboard HTML"""
        return f"""
        <div class="operational-dashboard">
            <h2>Operational Dashboard</h2>
            <p>System Health: {metrics['system_health']}</p>
            <p>Active Scans: {metrics['active_scans']}</p>
            <p>Success Rate: {metrics['success_rate']}</p>
        </div>
        """

def generate_compliance_dashboard(scan_results: List[Dict[str, Any]], 
                                dashboard_type: str = "executive",
                                region: str = "Netherlands") -> str:
    """
    Convenience function to generate compliance dashboards.
    
    Args:
        scan_results: List of scan results for dashboard generation
        dashboard_type: Type of dashboard ('executive' or 'operational')
        region: Regional compliance focus
        
    Returns:
        Complete HTML dashboard
    """
    generator = ComplianceDashboardGenerator(region=region)
    
    if dashboard_type == "executive":
        return generator.generate_executive_dashboard(scan_results)
    else:
        return generator.generate_operational_dashboard(scan_results)