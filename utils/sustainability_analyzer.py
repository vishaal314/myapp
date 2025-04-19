"""
Sustainability and cost savings analyzer for DataGuardian Pro.

This module calculates sustainability scores and potential cost savings
based on scan results and privacy compliance status.
"""
import math
import random
from typing import Dict, Any, List, Tuple, Optional
import pandas as pd
import numpy as np

# Default storage costs per GB per month in euros
DEFAULT_STORAGE_COSTS = {
    'standard': 0.023,  # Standard storage
    'premium': 0.046,   # Premium storage
    'archive': 0.005    # Archive storage
}

# Default processing costs per hour in euros
DEFAULT_PROCESSING_COSTS = {
    'standard': 0.0521,  # Standard compute
    'premium': 0.1225    # Premium compute
}

# Default GDPR fine potential (average for Article 83 violations)
DEFAULT_GDPR_FINE_POTENTIAL = 2000000  # 2 million euros base

# Default hourly labor cost for data privacy professionals in euros
DEFAULT_LABOR_COST = 75.0

# Industry benchmarks for sustainability scores
INDUSTRY_BENCHMARKS = {
    'technology': 68,
    'finance': 72,
    'healthcare': 65,
    'retail': 60,
    'manufacturing': 58,
    'energy': 63,
    'public': 70,
    'education': 67,
    'average': 65
}

class SustainabilityAnalyzer:
    """
    Analyzes scan results and compliance status to calculate sustainability
    scores and potential cost savings.
    """
    
    def __init__(self, scan_results: Optional[Dict[str, Any]] = None, 
                 industry: str = 'average',
                 storage_costs: Optional[Dict[str, float]] = None,
                 processing_costs: Optional[Dict[str, float]] = None,
                 labor_cost: float = DEFAULT_LABOR_COST,
                 gdpr_fine_potential: float = DEFAULT_GDPR_FINE_POTENTIAL):
        """
        Initialize the sustainability analyzer.
        
        Args:
            scan_results: Dictionary of scan results (if available)
            industry: Industry sector for benchmarking
            storage_costs: Custom storage costs per GB per month
            processing_costs: Custom processing costs per hour
            labor_cost: Hourly labor cost for data privacy professionals
            gdpr_fine_potential: Potential GDPR fine for the organization
        """
        self.scan_results = scan_results
        self.industry = industry.lower()
        self.storage_costs = storage_costs or DEFAULT_STORAGE_COSTS
        self.processing_costs = processing_costs or DEFAULT_PROCESSING_COSTS
        self.labor_cost = labor_cost
        self.gdpr_fine_potential = gdpr_fine_potential
        
        # Default weights for sustainability score components
        self.weights = {
            'storage_efficiency': 0.25,
            'processing_efficiency': 0.20,
            'data_minimization': 0.20,
            'green_hosting': 0.15,
            'privacy_by_design': 0.10,
            'data_lifecycle': 0.10
        }
    
    def calculate_sustainability_score(self) -> Dict[str, Any]:
        """
        Calculate the overall sustainability score and component scores.
        
        Returns:
            Dictionary containing the overall score and component scores
        """
        # Calculate component scores
        storage_score = self._calculate_storage_efficiency()
        processing_score = self._calculate_processing_efficiency()
        minimization_score = self._calculate_data_minimization()
        hosting_score = self._calculate_green_hosting()
        privacy_score = self._calculate_privacy_by_design()
        lifecycle_score = self._calculate_data_lifecycle()
        
        # Calculate weighted score
        overall_score = (
            storage_score * self.weights['storage_efficiency'] +
            processing_score * self.weights['processing_efficiency'] +
            minimization_score * self.weights['data_minimization'] +
            hosting_score * self.weights['green_hosting'] +
            privacy_score * self.weights['privacy_by_design'] +
            lifecycle_score * self.weights['data_lifecycle']
        )
        
        # Round to nearest integer
        overall_score = round(overall_score)
        
        # Compare to industry benchmark
        benchmark = INDUSTRY_BENCHMARKS.get(self.industry, INDUSTRY_BENCHMARKS['average'])
        comparison = overall_score - benchmark
        
        # Determine status
        if overall_score >= 80:
            status = 'Excellent'
            color = '#4CAF50'  # Green
        elif overall_score >= 70:
            status = 'Good'
            color = '#8BC34A'  # Light Green
        elif overall_score >= 60:
            status = 'Average'
            color = '#FFC107'  # Amber
        elif overall_score >= 50:
            status = 'Below Average'
            color = '#FF9800'  # Orange
        else:
            status = 'Poor'
            color = '#F44336'  # Red
        
        return {
            'overall_score': overall_score,
            'components': {
                'storage_efficiency': storage_score,
                'processing_efficiency': processing_score,
                'data_minimization': minimization_score,
                'green_hosting': hosting_score,
                'privacy_by_design': privacy_score,
                'data_lifecycle': lifecycle_score
            },
            'benchmark': benchmark,
            'comparison': comparison,
            'status': status,
            'color': color
        }
    
    def calculate_cost_savings(self) -> Dict[str, Any]:
        """
        Calculate potential cost savings from improved privacy practices.
        
        Returns:
            Dictionary containing savings by category and total savings
        """
        # Calculate individual savings components
        storage_savings = self._calculate_storage_savings()
        processing_savings = self._calculate_processing_savings()
        compliance_savings = self._calculate_compliance_risk_savings()
        efficiency_savings = self._calculate_operational_efficiency_savings()
        breach_savings = self._calculate_breach_prevention_savings()
        
        # Calculate total annual savings
        total_savings = (
            storage_savings +
            processing_savings +
            compliance_savings +
            efficiency_savings +
            breach_savings
        )
        
        return {
            'storage': storage_savings,
            'processing': processing_savings,
            'compliance_risk': compliance_savings,
            'operational_efficiency': efficiency_savings,
            'breach_prevention': breach_savings,
            'total': total_savings
        }
    
    def get_recommendations(self) -> List[Dict[str, str]]:
        """
        Get recommendations for improving sustainability and cost savings.
        
        Returns:
            List of recommendation dictionaries with category, title, and description
        """
        # Score component values to determine recommendations
        scores = self.calculate_sustainability_score()['components']
        
        recommendations = []
        
        # Add recommendations based on lowest scores
        if scores['storage_efficiency'] < 70:
            recommendations.append({
                'category': 'storage',
                'title': 'Optimize Data Storage',
                'description': 'Implement deduplication and compression to reduce storage requirements. Consider archiving older data and removing unnecessary duplicates.'
            })
        
        if scores['processing_efficiency'] < 70:
            recommendations.append({
                'category': 'processing',
                'title': 'Improve Processing Efficiency',
                'description': 'Optimize data processing workflows to reduce computational requirements. Consider batch processing and more efficient algorithms.'
            })
        
        if scores['data_minimization'] < 70:
            recommendations.append({
                'category': 'minimization',
                'title': 'Implement Data Minimization',
                'description': 'Reduce unnecessary data collection and storage. Implement privacy by design principles to collect only what is needed.'
            })
        
        if scores['green_hosting'] < 70:
            recommendations.append({
                'category': 'hosting',
                'title': 'Switch to Green Hosting',
                'description': 'Consider migrating to cloud providers with renewable energy commitments or carbon-neutral operations.'
            })
        
        if scores['privacy_by_design'] < 70:
            recommendations.append({
                'category': 'privacy',
                'title': 'Enhance Privacy by Design',
                'description': 'Integrate privacy considerations into the development lifecycle from the start rather than as an afterthought.'
            })
        
        if scores['data_lifecycle'] < 70:
            recommendations.append({
                'category': 'lifecycle',
                'title': 'Improve Data Lifecycle Management',
                'description': 'Implement automated data retention and deletion policies to ensure data is not kept longer than necessary.'
            })
        
        # If all scores are good, provide general improvement recommendations
        if not recommendations:
            recommendations.append({
                'category': 'general',
                'title': 'Maintain Excellence',
                'description': 'Continue current practices and consider pioneering new sustainable data practices in your industry.'
            })
        
        return recommendations
    
    def _calculate_storage_efficiency(self) -> float:
        """
        Calculate storage efficiency score.
        
        Returns:
            Score from 0-100
        """
        # In a real implementation, this would analyze actual storage data
        # For now, we'll use a placeholder calculation based on scan findings
        if self.scan_results and 'total_pii_found' in self.scan_results:
            # More PII findings may indicate less efficient storage
            base_score = 85 - min(self.scan_results['total_pii_found'] * 0.5, 30)
        else:
            # Default base score
            base_score = 70
        
        # Add some variability
        return max(0, min(100, base_score + random.uniform(-5, 5)))
    
    def _calculate_processing_efficiency(self) -> float:
        """
        Calculate processing efficiency score.
        
        Returns:
            Score from 0-100
        """
        # In a real implementation, this would analyze processing patterns
        if self.scan_results and 'high_risk_count' in self.scan_results:
            # Higher risk items may indicate less efficient processing
            base_score = 80 - min(self.scan_results['high_risk_count'] * 2, 25)
        else:
            # Default base score
            base_score = 65
        
        # Add some variability
        return max(0, min(100, base_score + random.uniform(-5, 5)))
    
    def _calculate_data_minimization(self) -> float:
        """
        Calculate data minimization score.
        
        Returns:
            Score from 0-100
        """
        # In a real implementation, this would analyze data collection practices
        if self.scan_results and 'total_pii_found' in self.scan_results:
            # More PII findings may indicate less data minimization
            base_score = 90 - min(self.scan_results['total_pii_found'] * 0.4, 35)
        else:
            # Default base score
            base_score = 60
        
        # Add some variability
        return max(0, min(100, base_score + random.uniform(-5, 5)))
    
    def _calculate_green_hosting(self) -> float:
        """
        Calculate green hosting score.
        
        Returns:
            Score from 0-100
        """
        # In a real implementation, this would check hosting provider info
        # For now, we'll use a placeholder average score
        base_score = 75
        
        # Add some variability
        return max(0, min(100, base_score + random.uniform(-8, 8)))
    
    def _calculate_privacy_by_design(self) -> float:
        """
        Calculate privacy by design score.
        
        Returns:
            Score from 0-100
        """
        # In a real implementation, this would analyze dev practices
        if self.scan_results and 'high_risk_count' in self.scan_results:
            # More high-risk items may indicate less privacy by design
            base_score = 85 - min(self.scan_results['high_risk_count'] * 3, 40)
        else:
            # Default base score
            base_score = 65
        
        # Add some variability
        return max(0, min(100, base_score + random.uniform(-7, 7)))
    
    def _calculate_data_lifecycle(self) -> float:
        """
        Calculate data lifecycle management score.
        
        Returns:
            Score from 0-100
        """
        # In a real implementation, this would analyze data retention practices
        # For now, we'll use a placeholder score
        base_score = 70
        
        # Add some variability
        return max(0, min(100, base_score + random.uniform(-10, 10)))
    
    def _calculate_storage_savings(self) -> float:
        """
        Calculate potential annual storage cost savings.
        
        Returns:
            Annual savings in euros
        """
        # Estimate unnecessary data storage in GB
        if self.scan_results and 'total_pii_found' in self.scan_results:
            # Rough estimate: each PII finding might represent 0.1-1 GB of unnecessary data
            unnecessary_gb = self.scan_results['total_pii_found'] * random.uniform(0.1, 1.0)
        else:
            # Default estimate
            unnecessary_gb = 50
        
        # Calculate annual cost per GB
        annual_cost_per_gb = self.storage_costs['standard'] * 12  # 12 months
        
        # Calculate total savings
        savings = unnecessary_gb * annual_cost_per_gb
        
        # Add organizational scale factor
        org_scale_factor = 10  # Adjust based on organization size
        
        return savings * org_scale_factor
    
    def _calculate_processing_savings(self) -> float:
        """
        Calculate potential annual processing cost savings.
        
        Returns:
            Annual savings in euros
        """
        # Estimate redundant processing hours
        if self.scan_results and 'high_risk_count' in self.scan_results:
            # Rough estimate: each high-risk finding might represent inefficiency
            redundant_hours = self.scan_results['high_risk_count'] * random.uniform(5, 15)
        else:
            # Default estimate
            redundant_hours = 100
        
        # Calculate monthly compute costs
        monthly_savings = redundant_hours * self.processing_costs['standard']
        
        # Calculate annual savings
        annual_savings = monthly_savings * 12
        
        # Add organizational scale factor
        org_scale_factor = 10  # Adjust based on organization size
        
        return annual_savings * org_scale_factor
    
    def _calculate_compliance_risk_savings(self) -> float:
        """
        Calculate potential compliance risk reduction savings.
        
        Returns:
            Annual risk reduction value in euros
        """
        # Calculate baseline risk (% of fine)
        if self.scan_results and 'high_risk_count' in self.scan_results:
            baseline_risk = min(0.30, self.scan_results['high_risk_count'] * 0.01)
        else:
            # Default baseline risk
            baseline_risk = 0.15
        
        # Calculate new risk after improvements
        new_risk = baseline_risk * 0.5  # Assuming 50% risk reduction
        
        # Calculate risk reduction
        risk_reduction = baseline_risk - new_risk
        
        # Calculate savings (risk reduction × potential fine)
        savings = risk_reduction * self.gdpr_fine_potential
        
        # Risk adjustment factor (probability of fine in a year)
        risk_factor = 0.05  # 5% chance of fine in a year
        
        return savings * risk_factor
    
    def _calculate_operational_efficiency_savings(self) -> float:
        """
        Calculate potential operational efficiency savings.
        
        Returns:
            Annual savings in euros
        """
        # Estimate hours saved per month
        if self.scan_results and 'total_pii_found' in self.scan_results:
            hours_saved = 10 + (self.scan_results['total_pii_found'] * 0.2)
        else:
            # Default estimate
            hours_saved = 20
        
        # Calculate monthly savings
        monthly_savings = hours_saved * self.labor_cost
        
        # Calculate annual savings
        annual_savings = monthly_savings * 12
        
        return annual_savings
    
    def _calculate_breach_prevention_savings(self) -> float:
        """
        Calculate potential breach prevention savings.
        
        Returns:
            Annual savings in euros
        """
        # Average breach cost in euros
        avg_breach_cost = 3800000  # 3.8 million euros
        
        # Calculate baseline breach probability
        if self.scan_results and 'high_risk_count' in self.scan_results:
            baseline_probability = min(0.20, 0.05 + (self.scan_results['high_risk_count'] * 0.005))
        else:
            # Default baseline probability
            baseline_probability = 0.10
        
        # Calculate new probability after improvements
        new_probability = baseline_probability * 0.7  # Assuming 30% reduction
        
        # Calculate probability reduction
        probability_reduction = baseline_probability - new_probability
        
        # Calculate expected savings
        savings = probability_reduction * avg_breach_cost
        
        return savings

def get_sustainability_banner_html(analyzer: SustainabilityAnalyzer) -> str:
    """
    Generate an HTML banner highlighting sustainability and cost savings.
    
    Args:
        analyzer: SustainabilityAnalyzer instance with calculated metrics
        
    Returns:
        HTML string for the banner
    """
    # Calculate metrics
    sustainability = analyzer.calculate_sustainability_score()
    savings = analyzer.calculate_cost_savings()
    
    # Format total savings with commas and 2 decimal places
    total_savings_formatted = f"€{savings['total']:,.2f}"
    
    # Determine sustainability status color
    status_color = sustainability['color']
    
    # Create HTML for the banner with a more professional design
    html = f"""
    <div style="background: linear-gradient(120deg, #f7f9fa 0%, #e9f2f6 100%); padding: 25px; 
               border-radius: 12px; margin: 20px 0; box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08); border: 1px solid #e0e6ed;">
        
        <div style="display: flex; align-items: center; margin-bottom: 15px;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-right: 10px;">
                <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="#1976D2"/>
                <path d="M2 17L12 22L22 17M2 12L12 17L22 12" stroke="#1976D2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <h3 style="margin: 0; color: #1e3a8a; font-family: 'Segoe UI', Arial, sans-serif; font-weight: 600; letter-spacing: 0.3px;">
                Privacy & Compliance Analytics
            </h3>
        </div>
        
        <div style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: 20px; margin-top: 15px;">
            <div style="background-color: white; padding: 20px; border-radius: 10px; flex: 1; min-width: 220px; text-align: center; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04); border: 1px solid #f0f0f0;">
                <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 5px;">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-right: 6px;">
                        <path d="M12 8V12L15 15M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="#1976D2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    <h4 style="margin: 0; color: #1976D2; font-family: 'Segoe UI', Arial, sans-serif; font-size: 16px;">Annual Cost Efficiency</h4>
                </div>
                <p style="font-size: 26px; font-weight: 600; color: #2E7D32; margin: 15px 0 10px 0; font-family: 'Segoe UI', Arial, sans-serif;">{total_savings_formatted}</p>
                <p style="margin-bottom: 0; color: #6b7280; font-size: 0.85em; font-family: 'Segoe UI', Arial, sans-serif;">Potential annual savings through privacy optimization</p>
            </div>
            
            <div style="background-color: white; padding: 20px; border-radius: 10px; flex: 1; min-width: 220px; text-align: center; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04); border: 1px solid #f0f0f0;">
                <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 5px;">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-right: 6px;">
                        <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="#1976D2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    <h4 style="margin: 0; color: #1976D2; font-family: 'Segoe UI', Arial, sans-serif; font-size: 16px;">Sustainability Rating</h4>
                </div>
                <div style="position: relative; width: 90px; height: 90px; margin: 10px auto; background-color: {status_color}; border-radius: 50%; display: flex; justify-content: center; align-items: center; box-shadow: 0 3px 6px rgba(0,0,0,0.1);">
                    <span style="color: white; font-size: 28px; font-weight: 600; font-family: 'Segoe UI', Arial, sans-serif;">{sustainability['overall_score']}</span>
                </div>
                <p style="margin-bottom: 0; color: #6b7280; font-size: 0.85em; font-family: 'Segoe UI', Arial, sans-serif;">Current rating: <span style="color: {status_color}; font-weight: 600;">{sustainability['status']}</span></p>
            </div>
            
            <div style="background-color: white; padding: 20px; border-radius: 10px; flex: 1; min-width: 220px; text-align: center; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04); border: 1px solid #f0f0f0;">
                <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 5px;">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-right: 6px;">
                        <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" stroke="#1976D2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    <h4 style="margin: 0; color: #1976D2; font-family: 'Segoe UI', Arial, sans-serif; font-size: 16px;">Compliance Risk</h4>
                </div>
                <p style="font-size: 26px; font-weight: 600; color: #E53935; margin: 15px 0 10px 0; font-family: 'Segoe UI', Arial, sans-serif;">€{savings['compliance_risk']:,.2f}</p>
                <p style="margin-bottom: 0; color: #6b7280; font-size: 0.85em; font-family: 'Segoe UI', Arial, sans-serif;">Estimated GDPR fine exposure reduction</p>
            </div>
        </div>
        
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 18px; padding-top: 12px; border-top: 1px solid #e5e7eb;">
            <p style="color: #4b5563; font-family: 'Segoe UI', Arial, sans-serif; font-size: 14px; margin: 0;">
                Improve your sustainability score to increase operational efficiency and reduce compliance risk.
            </p>
            <a href="#" style="text-decoration: none;">
                <button style="background-color: #1E40AF; color: white; border: none; padding: 8px 16px; font-size: 14px; font-weight: 500; border-radius: 6px; cursor: pointer; font-family: 'Segoe UI', Arial, sans-serif; display: flex; align-items: center; transition: all 0.2s ease;">
                    <span>View Full Analysis</span>
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-left: 6px;">
                        <path d="M9 5l7 7-7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </button>
            </a>
        </div>
    </div>
    """
    
    return html