"""
Compliance Score Calculation and Visualization Module

This module handles the calculation, tracking, and visualization of compliance scores
based on scan results from various services.
"""

import numpy as np
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Tuple, Any, Optional

from services.results_aggregator import ResultsAggregator

# File to store historical compliance scores
COMPLIANCE_HISTORY_FILE = "data/compliance_history.json"

# Ensure data directory exists
os.makedirs(os.path.dirname(COMPLIANCE_HISTORY_FILE), exist_ok=True)

class ComplianceScoreManager:
    """
    Manages compliance score calculation, history tracking, and visualization.
    """
    
    def __init__(self):
        """Initialize the compliance score manager."""
        self.results_aggregator = ResultsAggregator()
        self._load_history()
    
    def _load_history(self) -> None:
        """Load compliance score history from file."""
        if os.path.exists(COMPLIANCE_HISTORY_FILE):
            try:
                with open(COMPLIANCE_HISTORY_FILE, 'r') as f:
                    self.history = json.load(f)
            except (json.JSONDecodeError, IOError):
                # Create default history if file is corrupted or can't be read
                self.history = {"scores": []}
        else:
            # Initialize empty history if file doesn't exist
            self.history = {"scores": []}
    
    def _save_history(self) -> None:
        """Save compliance score history to file."""
        try:
            with open(COMPLIANCE_HISTORY_FILE, 'w') as f:
                json.dump(self.history, f)
        except IOError as e:
            print(f"Error saving compliance history: {e}")
    
    def calculate_current_score(self) -> Dict[str, Any]:
        """
        Calculate the current compliance score based on recent scan results.
        
        Returns:
            Dict containing overall score and component scores
        """
        # Get recent scans from the aggregator
        recent_scans = self.results_aggregator.get_recent_scans(limit=20)
        
        if not recent_scans:
            return {
                "overall_score": 0,
                "components": {},
                "timestamp": datetime.now().isoformat()
            }
        
        # Initialize component scores
        components = {
            "code": {"weight": 0.25, "score": 0, "count": 0},
            "blob": {"weight": 0.15, "score": 0, "count": 0},
            "dpia": {"weight": 0.25, "score": 0, "count": 0},
            "image": {"weight": 0.05, "score": 0, "count": 0},
            "website": {"weight": 0.15, "score": 0, "count": 0},
            "database": {"weight": 0.15, "score": 0, "count": 0}
        }
        
        # Process each scan and calculate component scores
        for scan in recent_scans:
            scan_type = scan.get("type", "").lower()
            
            if scan_type in components:
                # Calculate individual scan score
                severity_counts = scan.get("severity_counts", {})
                total_findings = sum(severity_counts.values())
                
                if total_findings > 0:
                    # Higher weights for more severe findings
                    weighted_sum = (
                        severity_counts.get("high", 0) * 3 +
                        severity_counts.get("medium", 0) * 2 +
                        severity_counts.get("low", 0) * 1
                    )
                    # Invert the score: higher number of severe findings = lower score
                    max_weighted_sum = total_findings * 3  # if all were high severity
                    scan_score = max(0, 100 - (weighted_sum / max_weighted_sum * 100))
                    
                    # For DPIA scans, factor in risk assessment
                    if scan_type == "dpia" and "overall_percentage" in scan:
                        dpia_score = scan.get("overall_percentage", 0) * 10  # Convert to 0-100
                        scan_score = (scan_score + dpia_score) / 2
                    
                    # Add to component data
                    components[scan_type]["score"] += scan_score
                    components[scan_type]["count"] += 1
        
        # Calculate final component scores (average)
        component_scores = {}
        for component, data in components.items():
            if data["count"] > 0:
                component_scores[component] = data["score"] / data["count"]
            else:
                component_scores[component] = None  # No data
        
        # Calculate overall weighted score from components
        overall_score = 0
        total_weight = 0
        
        for component, data in components.items():
            if component_scores[component] is not None:
                overall_score += component_scores[component] * data["weight"]
                total_weight += data["weight"]
        
        # Scale overall score by total weight used
        if total_weight > 0:
            overall_score = overall_score / total_weight
        
        return {
            "overall_score": round(overall_score, 1),
            "components": component_scores,
            "timestamp": datetime.now().isoformat()
        }
    
    def update_score(self) -> Dict[str, Any]:
        """
        Calculate and save the current compliance score.
        
        Returns:
            Current score data dict
        """
        current_score = self.calculate_current_score()
        
        # Add to history
        self.history["scores"].append(current_score)
        
        # Limit history size (keep last 100 scores)
        if len(self.history["scores"]) > 100:
            self.history["scores"] = self.history["scores"][-100:]
        
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
        
        # Filter history by date
        recent_scores = [
            score for score in self.history["scores"]
            if score["timestamp"] >= cutoff_date
        ]
        
        return recent_scores
    
    def get_score_trend(self, days: int = 30) -> Dict[str, Any]:
        """
        Calculate the trend in compliance scores over the specified period.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict with trend indicators
        """
        scores = self.get_score_history(days)
        
        if not scores or len(scores) < 2:
            return {
                "direction": "stable",
                "percentage_change": 0,
                "score_change": 0
            }
        
        # Get earliest and most recent scores
        earliest = scores[0]["overall_score"]
        latest = scores[-1]["overall_score"]
        
        # Calculate changes
        score_change = latest - earliest
        
        if earliest > 0:
            percentage_change = (score_change / earliest) * 100
        else:
            percentage_change = 0 if score_change == 0 else 100
        
        # Determine trend direction
        if abs(percentage_change) < 2:  # Less than 2% change is considered stable
            direction = "stable"
        else:
            direction = "improving" if percentage_change > 0 else "declining"
        
        return {
            "direction": direction,
            "percentage_change": round(percentage_change, 1),
            "score_change": round(score_change, 1)
        }
    
    def create_score_timeline_chart(self, days: int = 30) -> go.Figure:
        """
        Create an interactive timeline chart of compliance scores.
        
        Args:
            days: Number of days to show in the chart
            
        Returns:
            Plotly figure object
        """
        scores = self.get_score_history(days)
        
        if not scores:
            # Create empty chart with message
            fig = go.Figure()
            fig.add_annotation(
                text="No compliance score data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=14)
            )
            fig.update_layout(
                title="Compliance Score Timeline",
                height=400
            )
            return fig
        
        # Convert to DataFrame for easier plotting
        df = pd.DataFrame([
            {
                "date": datetime.fromisoformat(score["timestamp"]),
                "score": score["overall_score"]
            }
            for score in scores
        ])
        
        # Create line chart
        fig = px.line(
            df,
            x="date",
            y="score",
            title="Compliance Score Timeline",
            labels={"date": "Date", "score": "Compliance Score"},
            line_shape="spline"
        )
        
        # Add reference lines for score ranges
        fig.add_shape(
            type="rect",
            x0=df["date"].min(),
            x1=df["date"].max(),
            y0=90,
            y1=100,
            fillcolor="rgba(75, 192, 192, 0.2)",
            line=dict(width=0),
            layer="below"
        )
        fig.add_shape(
            type="rect",
            x0=df["date"].min(),
            x1=df["date"].max(),
            y0=70,
            y1=90,
            fillcolor="rgba(255, 206, 86, 0.2)",
            line=dict(width=0),
            layer="below"
        )
        fig.add_shape(
            type="rect",
            x0=df["date"].min(),
            x1=df["date"].max(),
            y0=0,
            y1=70,
            fillcolor="rgba(255, 99, 132, 0.2)",
            line=dict(width=0),
            layer="below"
        )
        
        # Customize layout
        fig.update_layout(
            height=400,
            margin=dict(l=10, r=10, t=40, b=10),
            yaxis=dict(range=[0, 100]),
            xaxis=dict(
                tickformat="%Y-%m-%d",
                tickmode="auto",
                nticks=10
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    def create_component_radar_chart(self) -> go.Figure:
        """
        Create a radar chart showing compliance scores by component.
        
        Returns:
            Plotly figure object
        """
        current_score = self.calculate_current_score()
        components = current_score["components"]
        
        # Component names mapped to display names
        display_names = {
            "code": "Code",
            "blob": "Documents",
            "dpia": "DPIA",
            "image": "Images",
            "website": "Websites",
            "database": "Databases"
        }
        
        # Prepare data for radar chart
        categories = []
        values = []
        
        for component, score in components.items():
            if score is not None:
                categories.append(display_names.get(component, component))
                values.append(score)
        
        if not categories:
            # Create empty chart with message
            fig = go.Figure()
            fig.add_annotation(
                text="No component score data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=14)
            )
            fig.update_layout(
                title="Component Compliance Scores",
                height=400
            )
            return fig
        
        # Create radar chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill="toself",
            name="Current Scores",
            line_color="rgb(75, 192, 192)",
            fillcolor="rgba(75, 192, 192, 0.2)"
        ))
        
        # Add reference for perfect score
        fig.add_trace(go.Scatterpolar(
            r=[100] * len(categories),
            theta=categories,
            fill="none",
            name="Perfect Score",
            line=dict(color="rgba(200, 200, 200, 0.8)", dash="dot")
        ))
        
        # Customize layout
        fig.update_layout(
            title="Component Compliance Scores",
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=True,
            height=400,
            margin=dict(l=10, r=10, t=40, b=10),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    def create_score_gauge_chart(self) -> go.Figure:
        """
        Create a gauge chart showing the current compliance score.
        
        Returns:
            Plotly figure object
        """
        current_score = self.calculate_current_score()
        score = current_score["overall_score"]
        
        # Create gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": "Compliance Score"},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "darkblue"},
                "bar": {"color": "rgba(50, 50, 50, 0.1)"},
                "bgcolor": "white",
                "borderwidth": 2,
                "bordercolor": "gray",
                "steps": [
                    {"range": [0, 70], "color": "rgba(255, 99, 132, 0.6)"},
                    {"range": [70, 90], "color": "rgba(255, 206, 86, 0.6)"},
                    {"range": [90, 100], "color": "rgba(75, 192, 192, 0.6)"}
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": 90
                }
            }
        ))
        
        # Customize layout
        fig.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=10, b=10)
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
            current_score = self.calculate_current_score()
            score = current_score["overall_score"]
        
        # Determine badge level and color
        if score >= 90:
            level = "Excellent"
            color = "#4CAF50"  # Green
            description = "Your compliance practices are excellent."
        elif score >= 80:
            level = "Good"
            color = "#8BC34A"  # Light Green
            description = "Your compliance practices are good with some room for improvement."
        elif score >= 70:
            level = "Satisfactory"
            color = "#FFC107"  # Amber
            description = "Your compliance meets basic requirements but needs improvement."
        elif score >= 60:
            level = "Needs Improvement"
            color = "#FF9800"  # Orange
            description = "Your compliance practices need significant improvement."
        else:
            level = "At Risk"
            color = "#F44336"  # Red
            description = "Your compliance practices need urgent attention."
        
        return {
            "score": score,
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
    manager = ComplianceScoreManager()
    
    # Clear existing history
    manager.history = {"scores": []}
    
    # Start with a base score and add some variability
    base_score = 75
    
    # Generate daily scores with an improving trend
    for i in range(days):
        date = (datetime.now() - timedelta(days=days-i)).isoformat()
        
        # Calculate this day's score with some noise and a small upward trend
        day_score = min(100, base_score + (i * 0.5) + np.random.normal(0, 3))
        
        # Component scores with similar pattern
        components = {
            "code": max(0, min(100, day_score + np.random.normal(0, 5))),
            "blob": max(0, min(100, day_score + np.random.normal(0, 5))),
            "dpia": max(0, min(100, day_score + np.random.normal(0, 5))),
            "image": max(0, min(100, day_score + np.random.normal(0, 5))),
            "website": max(0, min(100, day_score + np.random.normal(0, 5))),
            "database": max(0, min(100, day_score + np.random.normal(0, 5)))
        }
        
        # Add to history
        manager.history["scores"].append({
            "overall_score": round(day_score, 1),
            "components": {k: round(v, 1) for k, v in components.items()},
            "timestamp": date
        })
    
    # Save the mock history
    manager._save_history()