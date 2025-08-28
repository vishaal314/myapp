"""
Competitive Pricing Analysis for DataGuardian Pro
Optimized pricing strategy based on Netherlands market research
"""

from services.cost_savings_calculator import CostSavingsCalculator
from typing import Dict, List, Any

def get_optimized_pricing_strategy() -> Dict[str, Any]:
    """
    Return the complete optimized pricing strategy with competitive analysis
    
    Key Insights:
    - OneTrust: €11,500-€65,000/year (median €25K)
    - BigID/Varonis: €50K-€150K+ annually  
    - SME tools: €120-€2,400/year (basic features only)
    - Market gap: No comprehensive solution between €2,400-€11,500
    """
    
    calculator = CostSavingsCalculator()
    pricing_tiers = calculator.pricing_tiers
    
    return {
        "strategy_overview": {
            "market_positioning": "Premium value - Enterprise features at SME prices",
            "competitive_advantage": "85-95% cost savings vs OneTrust/BigID",
            "target_market": "Netherlands SMEs and enterprises seeking OneTrust alternative",
            "unique_value": "Only solution with Exact Online integration + BSN detection"
        },
        
        "pricing_tiers": pricing_tiers,
        
        "revenue_projections": {
            "year_1": {
                "startup_customers": {"count": 150, "arr": 73500, "tier": "€490/year"},
                "growth_customers": {"count": 80, "arr": 119200, "tier": "€1,490/year"},
                "scale_customers": {"count": 25, "arr": 99750, "tier": "€3,990/year"},
                "enterprise_customers": {"count": 8, "arr": 71920, "tier": "€8,990/year"},
                "standalone_licenses": {"count": 3, "arr": 52500, "tier": "€15K + €2.5K maintenance"},
                "total_arr": 416870,
                "monthly_recurring": 34739
            },
            "year_2": {
                "total_customers": 350,
                "total_arr": 850000,
                "monthly_recurring": 70833,
                "growth_rate": "104%"
            }
        },
        
        "competitive_comparison": {
            "onetrust": {
                "typical_cost": 25000,
                "our_equivalent": 3990,  # Scale tier
                "savings": 21010,
                "savings_percentage": "84% cheaper"
            },
            "bigid_varonis": {
                "typical_cost": 75000,
                "our_equivalent": 8990,  # Enterprise tier
                "savings": 66010,
                "savings_percentage": "88% cheaper"
            },
            "sme_tools_plus_consultant": {
                "typical_cost": 8500,  # €200/month + implementation
                "our_equivalent": 1490,  # Growth tier
                "savings": 7010,
                "savings_percentage": "82% cheaper"
            }
        },
        
        "value_justification": {
            "netherlands_specialization": [
                "BSN detection and validation",
                "KvK number compliance", 
                "Dutch AP authority integration",
                "UAVG-specific compliance rules",
                "Exact Online connector (60% Netherlands SME market)"
            ],
            "enterprise_features": [
                "Microsoft 365 enterprise connector",
                "Advanced AI scanning with EU AI Act compliance",
                "Real-time compliance monitoring",
                "Professional compliance certificates",
                "Multi-language support (Dutch/English)"
            ],
            "cost_effectiveness": [
                "95% cost savings vs OneTrust enterprise",
                "88% cheaper than BigID/Varonis stack",
                "ROI: 400-1400% in first year",
                "Payback period: 1-3 months"
            ]
        }
    }

def analyze_customer_segment_pricing(company_size: str, employees: int, annual_revenue: float) -> Dict[str, Any]:
    """Analyze optimal pricing for specific customer segment"""
    
    # Determine customer segment
    if employees <= 25 or annual_revenue <= 1000000:
        segment = "startup"
        competitive_alternative = "Basic compliance tools + consultant"
    elif employees <= 100 or annual_revenue <= 10000000:
        segment = "growth" 
        competitive_alternative = "Mid-tier tools + implementation services"
    elif employees <= 500 or annual_revenue <= 50000000:
        segment = "scale"
        competitive_alternative = "OneTrust basic package"
    else:
        segment = "enterprise"
        competitive_alternative = "OneTrust enterprise + BigID modules"
    
    calculator = CostSavingsCalculator()
    roi_analysis = calculator.calculate_competitive_advantage(segment, annual_revenue)
    
    return {
        "segment": segment,
        "recommended_pricing": roi_analysis,
        "competitive_alternative": competitive_alternative,
        "value_drivers": [
            f"Save {roi_analysis['cost_advantage']} vs competitors",
            f"{roi_analysis['roi_percentage']}% ROI in first year",
            f"Payback in {roi_analysis['payback_period_months']} months",
            "Netherlands-specific compliance features",
            "Enterprise-grade scanning capabilities"
        ]
    }

def get_netherlands_market_opportunity() -> Dict[str, Any]:
    """Calculate Netherlands market opportunity and pricing strategy"""
    
    return {
        "market_size": {
            "total_netherlands_enterprises": 1170000,  # CBS data
            "target_segments": {
                "sme_25_250": {"companies": 58500, "addressable": 23400},  # 40% addressable
                "enterprise_250_plus": {"companies": 11700, "addressable": 5850},  # 50% addressable
                "government_agencies": {"entities": 2500, "addressable": 750}  # 30% addressable
            },
            "total_addressable_market": 30000
        },
        
        "revenue_potential": {
            "conservative_penetration": {
                "sme_penetration": "1%",  # 234 companies at €1,490/year
                "enterprise_penetration": "2%",  # 117 companies at €8,990/year  
                "government_penetration": "4%",  # 30 licenses at €15K
                "total_arr": 1400430
            },
            "optimistic_penetration": {
                "sme_penetration": "3%",  # 702 companies
                "enterprise_penetration": "5%",  # 293 companies
                "government_penetration": "10%",  # 75 licenses
                "total_arr": 4180470
            }
        },
        
        "competitive_positioning": {
            "key_differentiators": [
                "Only solution with native Exact Online integration",
                "Netherlands-specific BSN and KvK detection",
                "85-95% cost savings vs international competitors",
                "Local data residency and Dutch AP compliance",
                "Multi-language Dutch/English interface"
            ],
            "go_to_market": [
                "Target Exact Online user base (60% of NL SMEs)",
                "Partner with Dutch accounting firms and consultants", 
                "Focus on GDPR penalty avoidance messaging",
                "Emphasize data sovereignty and local compliance"
            ]
        }
    }

if __name__ == "__main__":
    # Demo the pricing analysis
    strategy = get_optimized_pricing_strategy()
    print("DataGuardian Pro Optimized Pricing Strategy")
    print("=" * 50)
    
    for tier_name, tier_data in strategy["pricing_tiers"].items():
        print(f"\n{tier_data['name']} ({tier_data['employees']} employees)")
        if 'monthly_price' in tier_data:
            print(f"  Monthly: €{tier_data['monthly_price']}")
            print(f"  Annual: €{tier_data['annual_price']} (2 months free)")
        else:
            print(f"  License: €{tier_data['one_time_price']}")
            print(f"  Annual Maintenance: €{tier_data['annual_maintenance']}")
        print(f"  Competitor Cost: €{tier_data['competitor_cost']}")
        print(f"  Savings: €{tier_data['savings_vs_competitor']} ({round((tier_data['savings_vs_competitor']/tier_data['competitor_cost'])*100)}% cheaper)")