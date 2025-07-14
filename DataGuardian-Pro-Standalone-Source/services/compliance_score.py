"""
Compliance Score Calculation and Visualization Module

This module handles the calculation, tracking, and visualization of compliance scores
based on scan results from various services.
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os
from typing import Dict, List, Any, Optional

import plotly.express as px
import plotly.graph_objects as go

# Make sure services directory exists
if not os.path.exists('services'):
    os.makedirs('services')

# Define data directory
DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

COMPLIANCE_SCORE_FILE = os.path.join(DATA_DIR, 'compliance_scores.json')

class ComplianceScoreManager:
    """
    Manages compliance score calculation, history tracking, and visualization.
    """
    
    def __init__(self):
        """Initialize the compliance score manager."""
        self.score_history = []
        self._load_history()
    
    def _load_history(self) -> None:
        """Load compliance score history from file."""
        try:
            if os.path.exists(COMPLIANCE_SCORE_FILE):
                with open(COMPLIANCE_SCORE_FILE, 'r') as f:
                    self.score_history = json.load(f)
            else:
                self.score_history = []
        except Exception as e:
            # Error loading compliance score history - log for debugging if needed
            pass
            self.score_history = []
    
    def _save_history(self) -> None:
        """Save compliance score history to file."""
        try:
            with open(COMPLIANCE_SCORE_FILE, 'w') as f:
                json.dump(self.score_history, f)
        except Exception as e:
            # Error saving compliance score history - log for debugging if needed
            pass
    
    def calculate_current_score(self) -> Dict[str, Any]:
        """
        Calculate the current compliance score based on recent scan results.
        
        Returns:
            Dict containing overall score and component scores
        """
        # Import here to avoid circular import
        from services.results_aggregator import ResultsAggregator
        
        # Get recent scan results
        aggregator = ResultsAggregator()
        recent_scans = aggregator.get_recent_scans(days=30)
        
        # Initialize component scores
        component_scores = {
            "code": None,
            "blob": None,
            "dpia": None,
            "image": None,
            "website": None,
            "database": None,
            "api": None,
            "cloud": None,
            "ai_model": None
        }
        
        if not recent_scans:
            # If no scans, return default score
            return {
                "timestamp": datetime.now().isoformat(),
                "overall_score": 0,
                "components": component_scores,
                "factors": {
                    "pii_detection": 0,
                    "risk_assessment": 0,
                    "documentation": 0,
                    "data_minimization": 0
                }
            }
        
        # Group scans by type
        scans_by_type = {}
        for scan in recent_scans:
            scan_type = scan.get('scan_type', 'unknown')
            if scan_type not in scans_by_type:
                scans_by_type[scan_type] = []
            scans_by_type[scan_type].append(scan)
        
        # Calculate scores for each component
        for component, scans in scans_by_type.items():
            if component in component_scores:
                # Skip if no scans for this component
                if not scans:
                    continue
                
                # Calculate component score based on:
                # 1. PII found vs total scanned items
                # 2. High risk items percentage
                # 3. Compliance with relevant GDPR principles
                
                # Base metrics
                total_pii = sum(scan.get('total_pii_found', 0) for scan in scans)
                high_risk = sum(scan.get('high_risk_count', 0) for scan in scans)
                medium_risk = sum(scan.get('medium_risk_count', 0) for scan in scans)
                
                # Calculate normalized scores (higher is better)
                if total_pii > 0:
                    # Risk ratio (lower is better)
                    risk_ratio = (high_risk * 1.0 + medium_risk * 0.5) / total_pii
                    risk_score = max(0, 100 - min(100, risk_ratio * 100))
                    
                    # Compliance factor
                    compliance_factor = np.mean([
                        scan.get('compliance_score', 70) for scan in scans 
                        if 'compliance_score' in scan
                    ]) if any('compliance_score' in scan for scan in scans) else 70
                    
                    # Final component score
                    component_scores[component] = int(min(100, (risk_score * 0.7 + compliance_factor * 0.3)))
                else:
                    # If no PII found, it's either not applicable or perfect
                    component_scores[component] = 100
        
        # Calculate overall score as weighted average of component scores
        # Weight factors based on importance for GDPR compliance
        weights = {
            "code": 0.15,
            "blob": 0.10,
            "dpia": 0.25,  # DPIA is critical for GDPR
            "image": 0.05,
            "website": 0.15,
            "database": 0.20,
            "api": 0.05,
            "cloud": 0.03,
            "ai_model": 0.02
        }
        
        # Only include components that have scores
        valid_components = {k: v for k, v in component_scores.items() if v is not None}
        if not valid_components:
            overall_score = 0
        else:
            # Normalize weights for available components
            total_weight = sum(weights[k] for k in valid_components.keys())
            normalized_weights = {k: weights[k]/total_weight for k in valid_components.keys()}
            
            # Calculate weighted average
            overall_score = int(sum(valid_components[k] * normalized_weights[k] for k in valid_components.keys()))
        
        # Calculate factor scores
        factors = {
            "pii_detection": self._calculate_pii_detection_score(recent_scans),
            "risk_assessment": self._calculate_risk_assessment_score(recent_scans),
            "documentation": self._calculate_documentation_score(recent_scans),
            "data_minimization": self._calculate_data_minimization_score(recent_scans)
        }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_score": overall_score,
            "components": component_scores,
            "factors": factors
        }
    
    def _calculate_pii_detection_score(self, scans: List[Dict[str, Any]]) -> int:
        """Calculate PII detection factor score."""
        if not scans:
            return 0
            
        # Based on coverage of different PII types
        pii_types_found = set()
        for scan in scans:
            if 'pii_types' in scan:
                pii_types_found.update(scan['pii_types'].keys())
        
        # Common PII types that should be detected
        common_pii_types = {
            'email', 'phone', 'address', 'name', 'ip_address', 'credit_card',
            'ssn', 'passport', 'drivers_license', 'date_of_birth'
        }
        
        # Calculate coverage
        coverage = len(pii_types_found.intersection(common_pii_types)) / len(common_pii_types)
        return int(min(100, coverage * 100))
    
    def _calculate_risk_assessment_score(self, scans: List[Dict[str, Any]]) -> int:
        """Calculate risk assessment factor score."""
        if not scans:
            return 0
            
        # Based on percentage of scans with risk assessment
        scans_with_risk = sum(1 for scan in scans if 'risk_assessment' in scan)
        return int(min(100, (scans_with_risk / len(scans)) * 100))
    
    def _calculate_documentation_score(self, scans: List[Dict[str, Any]]) -> int:
        """Calculate documentation factor score."""
        if not scans:
            return 0
            
        # Based on documentation completeness
        doc_scores = []
        for scan in scans:
            if 'documentation' in scan:
                doc_scores.append(scan['documentation'].get('completeness', 0))
            else:
                doc_scores.append(0)
                
        return int(min(100, np.mean(doc_scores) if doc_scores else 0))
    
    def _calculate_data_minimization_score(self, scans: List[Dict[str, Any]]) -> int:
        """Calculate data minimization factor score."""
        if not scans:
            return 0
            
        # Based on data minimization indicators
        minimization_scores = []
        for scan in scans:
            # Check for minimization metrics
            if 'data_minimization' in scan:
                minimization_scores.append(scan['data_minimization'].get('score', 0))
            else:
                # Default score based on PII vs necessary data
                total_pii = scan.get('total_pii_found', 0)
                necessary_pii = scan.get('necessary_pii_count', total_pii // 2)  # Estimate if not available
                
                if total_pii == 0:
                    minimization_scores.append(100)  # No PII is perfect minimization
                else:
                    # Lower ratio is better (less unnecessary PII)
                    ratio = min(1.0, necessary_pii / total_pii)
                    minimization_scores.append(int(ratio * 100))
                
        return int(min(100, np.mean(minimization_scores) if minimization_scores else 0))
    
    def update_score(self) -> Dict[str, Any]:
        """
        Calculate and save the current compliance score.
        
        Returns:
            Current score data dict
        """
        # Calculate current score
        current_score = self.calculate_current_score()
        
        # Add to history
        self.score_history.append(current_score)
        
        # Only keep last 365 days of history
        cutoff_date = (datetime.now() - timedelta(days=365)).isoformat()
        self.score_history = [
            score for score in self.score_history 
            if score.get('timestamp', '') >= cutoff_date
        ]
        
        # Save updated history
        self._save_history()
        
        return current_score
    
    def get_score_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get compliance score history for the specified number of days.
        
        Args:
            days: Number of days of history to retrieve
            
        Returns:
            List of score records in chronological order
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        history = [
            score for score in self.score_history 
            if score.get('timestamp', '') >= cutoff_date
        ]
        
        # Sort by timestamp
        history.sort(key=lambda x: x.get('timestamp', ''))
        
        return history
    
    def get_score_trend(self, days: int = 30) -> Dict[str, Any]:
        """
        Calculate the trend in compliance scores over the specified period.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict with trend indicators
        """
        history = self.get_score_history(days)
        
        if not history or len(history) < 2:
            return {
                "direction": "stable",
                "percentage_change": 0,
                "score_change": 0
            }
        
        # Get first and last scores
        first_score = history[0]['overall_score']
        last_score = history[-1]['overall_score']
        
        # Calculate changes
        score_change = last_score - first_score
        
        if first_score == 0:
            percentage_change = 100 if last_score > 0 else 0
        else:
            percentage_change = int((score_change / first_score) * 100)
        
        # Determine direction
        if abs(percentage_change) < 5:
            direction = "stable"
        elif percentage_change > 0:
            direction = "improving"
        else:
            direction = "declining"
        
        return {
            "direction": direction,
            "percentage_change": abs(percentage_change),
            "score_change": score_change
        }
    
    def create_score_timeline_chart(self, days: int = 30) -> go.Figure:
        """
        Create an interactive timeline chart of compliance scores.
        
        Args:
            days: Number of days to show in the chart
            
        Returns:
            Plotly figure object
        """
        history = self.get_score_history(days)
        
        if not history:
            # Create empty chart with message
            fig = go.Figure()
            fig.add_annotation(
                x=0.5, y=0.5,
                text="No compliance score data available",
                showarrow=False,
                font=dict(size=14)
            )
            fig.update_layout(
                title="Compliance Score History",
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
            return fig
        
        # Create dataframe from history
        df = pd.DataFrame([
            {
                'date': datetime.fromisoformat(score['timestamp']),
                'score': score['overall_score']
            }
            for score in history
        ])
        
        # Create line chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['score'],
            mode='lines+markers',
            line=dict(color='#2563EB', width=3),
            marker=dict(size=8, color='#1E40AF'),
            name='Compliance Score'
        ))
        
        # Add threshold lines
        fig.add_shape(
            type="line",
            x0=df['date'].min(),
            y0=80,
            x1=df['date'].max(),
            y1=80,
            line=dict(color="#10B981", width=2, dash="dash"),
            name="Good"
        )
        
        fig.add_shape(
            type="line",
            x0=df['date'].min(),
            y0=60,
            x1=df['date'].max(),
            y1=60,
            line=dict(color="#F59E0B", width=2, dash="dash"),
            name="Warning"
        )
        
        # Add annotations for thresholds
        fig.add_annotation(
            x=df['date'].max(), 
            y=80,
            text="Good",
            showarrow=False,
            font=dict(size=12, color="#10B981"),
            xshift=40
        )
        
        fig.add_annotation(
            x=df['date'].max(), 
            y=60,
            text="Warning",
            showarrow=False,
            font=dict(size=12, color="#F59E0B"),
            xshift=40
        )
        
        # Update layout
        fig.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=30, b=10),
            xaxis=dict(
                title="Date",
                showgrid=True,
                gridcolor="rgba(0,0,0,0.1)"
            ),
            yaxis=dict(
                title="Score",
                range=[0, 100],
                showgrid=True,
                gridcolor="rgba(0,0,0,0.1)"
            ),
            plot_bgcolor="white",
            hoverlabel=dict(
                bgcolor="white",
                font_size=14
            ),
            hovermode="x"
        )
        
        return fig
    
    def create_component_radar_chart(self) -> go.Figure:
        """
        Create a radar chart showing compliance scores by component.
        
        Returns:
            Plotly figure object
        """
        # Get current score
        current_score = self.calculate_current_score()
        components = current_score.get('components', {})
        
        # Filter out None values and create lists for chart
        labels = []
        values = []
        
        for component, score in components.items():
            if score is not None:
                # Convert component name to display name
                display_name = {
                    "code": "Code",
                    "blob": "Documents",
                    "dpia": "DPIA",
                    "image": "Images",
                    "website": "Website",
                    "database": "Database",
                    "api": "API",
                    "cloud": "Cloud",
                    "ai_model": "AI Models"
                }.get(component, component.title())
                
                labels.append(display_name)
                values.append(score)
        
        if not labels:
            # Create empty chart with message
            fig = go.Figure()
            fig.add_annotation(
                x=0.5, y=0.5,
                text="No component data available",
                showarrow=False,
                font=dict(size=14)
            )
            fig.update_layout(
                title="Component Analysis",
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
            return fig
        
        # Create radar chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=labels,
            fill='toself',
            fillcolor='rgba(37, 99, 235, 0.2)',
            line=dict(color='#2563EB', width=2),
            name='Component Scores'
        ))
        
        # Add benchmark score of 80 for reference
        fig.add_trace(go.Scatterpolar(
            r=[80] * len(labels),
            theta=labels,
            fill='none',
            line=dict(color='#10B981', width=2, dash='dash'),
            name='Target (80)'
        ))
        
        # Add warning threshold of 60
        fig.add_trace(go.Scatterpolar(
            r=[60] * len(labels),
            theta=labels,
            fill='none',
            line=dict(color='#F59E0B', width=2, dash='dash'),
            name='Warning (60)'
        ))
        
        # Update layout
        fig.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=30, b=10),
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    showticklabels=True,
                    ticks='',
                    gridcolor="rgba(0,0,0,0.1)",
                    gridwidth=1
                ),
                angularaxis=dict(
                    gridcolor="rgba(0,0,0,0.1)",
                    gridwidth=1
                ),
                bgcolor="white"
            ),
            showlegend=False
        )
        
        return fig
    
    def create_score_gauge_chart(self) -> go.Figure:
        """
        Create a gauge chart showing the current compliance score.
        
        Returns:
            Plotly figure object
        """
        # Get current score
        current_score = self.calculate_current_score()
        score = current_score['overall_score']
        
        # Create gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            domain=dict(x=[0, 1], y=[0, 1]),
            title=dict(text="Compliance Score", font=dict(size=16)),
            gauge=dict(
                axis=dict(range=[0, 100], tickwidth=1, tickcolor="darkblue"),
                bar=dict(color="#2563EB"),
                bgcolor="white",
                borderwidth=2,
                bordercolor="gray",
                steps=[
                    dict(range=[0, 60], color="#EF4444"),
                    dict(range=[60, 80], color="#F59E0B"),
                    dict(range=[80, 100], color="#10B981")
                ],
                threshold=dict(
                    line=dict(color="black", width=4),
                    thickness=0.75,
                    value=score
                )
            )
        ))
        
        # Update layout
        fig.update_layout(
            height=250,
            margin=dict(l=10, r=10, t=50, b=10),
            paper_bgcolor="white"
        )
        
        return fig
    
    def get_score_badge(self, score: Optional[float] = None) -> Dict[str, Any]:
        """
        Generate data for a compliance score badge based on the current score.
        
        Args:
            score: Optional score to use, otherwise uses the current calculated score
            
        Returns:
            Dict with badge details
        """
        if score is None:
            score = self.calculate_current_score()['overall_score']
        
        # Determine badge level and color
        if score >= 80:
            level = "Excellent"
            color = "#10B981"  # Green
            description = "Your compliance practices exceed GDPR requirements."
        elif score >= 70:
            level = "Good"
            color = "#22C55E"  # Light green
            description = "Your compliance practices meet most GDPR requirements."
        elif score >= 60:
            level = "Satisfactory"
            color = "#F59E0B"  # Amber
            description = "Your compliance practices need some improvements."
        elif score >= 50:
            level = "Needs Improvement"
            color = "#F97316"  # Orange
            description = "Your compliance practices require significant improvements."
        else:
            level = "At Risk"
            color = "#EF4444"  # Red
            description = "Your compliance practices are substantially below requirements."
        
        return {
            "level": level,
            "color": color,
            "description": description
        }

def generate_mock_history(days: int = 30) -> None:
    """
    Generate mock compliance score history for testing.
    
    Args:
        days: Number of days of history to generate
    """
    # Start with a base score
    base_score = 65
    
    # Create scores with some variation
    history = []
    for i in range(days):
        # Generate date
        date = (datetime.now() - timedelta(days=days-i)).isoformat()
        
        # Add some randomness to the score progression
        variation = np.random.normal(0, 3)
        trend_factor = i * 0.2  # Slight upward trend
        
        # Combine factors and ensure score stays in bounds
        score = min(100, max(0, int(base_score + variation + trend_factor)))
        
        # Generate component scores
        components = {
            "code": min(100, max(0, int(score + np.random.normal(0, 5)))),
            "blob": min(100, max(0, int(score + np.random.normal(0, 5)))),
            "dpia": min(100, max(0, int(score + np.random.normal(0, 7)))),
            "image": min(100, max(0, int(score + np.random.normal(0, 8)))),
            "website": min(100, max(0, int(score + np.random.normal(0, 6)))),
            "database": min(100, max(0, int(score + np.random.normal(0, 4))))
        }
        
        # Generate factors
        factors = {
            "pii_detection": min(100, max(0, int(score + np.random.normal(0, 10)))),
            "risk_assessment": min(100, max(0, int(score + np.random.normal(0, 8)))),
            "documentation": min(100, max(0, int(score + np.random.normal(0, 12)))),
            "data_minimization": min(100, max(0, int(score + np.random.normal(0, 7))))
        }
        
        # Create score record
        score_record = {
            "timestamp": date,
            "overall_score": score,
            "components": components,
            "factors": factors
        }
        
        history.append(score_record)
    
    # Save to file
    with open(COMPLIANCE_SCORE_FILE, 'w') as f:
        json.dump(history, f)
    
    # Generated {days} days of mock compliance score history.

if __name__ == "__main__":
    # Example usage
    manager = ComplianceScoreManager()
    current_score = manager.update_score()
    # Current compliance score: {current_score['overall_score']}