"""
DataGuardian Pro Pricing Configuration
Flexible pricing system supporting multiple tiers and regions
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

class PricingTier(Enum):
    """Pricing tier levels"""
    STARTUP = "startup"
    GROWTH = "growth" 
    SCALE = "scale"
    ENTERPRISE = "enterprise"
    GOVERNMENT = "government"

class BillingCycle(Enum):
    """Billing cycle options"""
    MONTHLY = "monthly"
    ANNUAL = "annual"
    ONE_TIME = "one_time"

class PricingConfig:
    """Centralized pricing configuration with flexible updates"""
    
    def __init__(self, region: str = "Netherlands"):
        self.region = region
        self.currency = "EUR"
        self.pricing_data = self._load_pricing_configuration()
        self.features_matrix = self._load_features_matrix()
        self.discounts = self._load_discount_rules()
    
    def _load_pricing_configuration(self) -> Dict[str, Any]:
        """Load current pricing configuration - easily updatable"""
        return {
            "version": "2.0",
            "last_updated": "2025-08-28",
            "effective_date": "2025-09-01",
            
            "tiers": {
                PricingTier.STARTUP.value: {
                    "name": "Startup Essential",
                    "description": "Perfect for small businesses getting started with GDPR compliance",
                    "target_employees": "1-25",
                    "target_revenue": "< €1M",
                    "monthly_price": 49,
                    "annual_price": 490,  # 2 months free
                    "setup_fee": 0,
                    "max_scans_monthly": 50,
                    "max_data_sources": 5,
                    "support_level": "email",
                    "sla_hours": 48
                },
                
                PricingTier.GROWTH.value: {
                    "name": "Growth Professional",
                    "description": "Comprehensive compliance for growing companies",
                    "target_employees": "25-100", 
                    "target_revenue": "€1M - €10M",
                    "monthly_price": 149,
                    "annual_price": 1490,  # 2 months free
                    "setup_fee": 0,
                    "max_scans_monthly": 200,
                    "max_data_sources": 25,
                    "support_level": "priority",
                    "sla_hours": 24,
                    "most_popular": True
                },
                
                PricingTier.SCALE.value: {
                    "name": "Scale Enterprise",
                    "description": "Advanced compliance for scaling enterprises",
                    "target_employees": "100-500",
                    "target_revenue": "€10M - €50M", 
                    "monthly_price": 399,
                    "annual_price": 3990,  # 2 months free
                    "setup_fee": 500,
                    "max_scans_monthly": 1000,
                    "max_data_sources": 100,
                    "support_level": "dedicated",
                    "sla_hours": 8,
                    "includes_onboarding": True
                },
                
                PricingTier.ENTERPRISE.value: {
                    "name": "Enterprise Ultimate",
                    "description": "Full-scale compliance for large enterprises",
                    "target_employees": "500+",
                    "target_revenue": "€50M+",
                    "monthly_price": 899,
                    "annual_price": 8990,  # 2 months free
                    "setup_fee": 1500,
                    "max_scans_monthly": "unlimited",
                    "max_data_sources": "unlimited", 
                    "support_level": "white_glove",
                    "sla_hours": 4,
                    "includes_onboarding": True,
                    "custom_integrations": True
                },
                
                PricingTier.GOVERNMENT.value: {
                    "name": "Government & Enterprise License",
                    "description": "On-premises deployment for government and large enterprises",
                    "target_employees": "Any",
                    "target_revenue": "Any",
                    "license_price": 15000,
                    "annual_maintenance": 2500,
                    "billing_cycle": BillingCycle.ONE_TIME.value,
                    "deployment": "on_premises",
                    "source_code_access": True,
                    "custom_development": True,
                    "support_level": "enterprise",
                    "sla_hours": 2
                }
            }
        }
    
    def _load_features_matrix(self) -> Dict[str, Dict[str, bool]]:
        """Define features available per tier"""
        return {
            "core_features": {
                "basic_pii_scanning": [PricingTier.STARTUP.value, PricingTier.GROWTH.value, PricingTier.SCALE.value, PricingTier.ENTERPRISE.value, PricingTier.GOVERNMENT.value],
                "gdpr_compliance_reports": [PricingTier.STARTUP.value, PricingTier.GROWTH.value, PricingTier.SCALE.value, PricingTier.ENTERPRISE.value, PricingTier.GOVERNMENT.value],
                "netherlands_bsn_detection": [PricingTier.STARTUP.value, PricingTier.GROWTH.value, PricingTier.SCALE.value, PricingTier.ENTERPRISE.value, PricingTier.GOVERNMENT.value],
                "multi_language_support": [PricingTier.STARTUP.value, PricingTier.GROWTH.value, PricingTier.SCALE.value, PricingTier.ENTERPRISE.value, PricingTier.GOVERNMENT.value]
            },
            
            "advanced_scanners": {
                "enterprise_connectors": [PricingTier.GROWTH.value, PricingTier.SCALE.value, PricingTier.ENTERPRISE.value, PricingTier.GOVERNMENT.value],
                "microsoft365_integration": [PricingTier.GROWTH.value, PricingTier.SCALE.value, PricingTier.ENTERPRISE.value, PricingTier.GOVERNMENT.value], 
                "exact_online_connector": [PricingTier.GROWTH.value, PricingTier.SCALE.value, PricingTier.ENTERPRISE.value, PricingTier.GOVERNMENT.value],
                "google_workspace_integration": [PricingTier.GROWTH.value, PricingTier.SCALE.value, PricingTier.ENTERPRISE.value, PricingTier.GOVERNMENT.value],
                "ai_model_scanning": [PricingTier.SCALE.value, PricingTier.ENTERPRISE.value, PricingTier.GOVERNMENT.value],
                "advanced_ai_analysis": [PricingTier.SCALE.value, PricingTier.ENTERPRISE.value, PricingTier.GOVERNMENT.value]
            },
            
            "compliance_features": {
                "compliance_certificates": [PricingTier.GROWTH.value, PricingTier.SCALE.value, PricingTier.ENTERPRISE.value, PricingTier.GOVERNMENT.value],
                "dpia_automation": [PricingTier.SCALE.value, PricingTier.ENTERPRISE.value, PricingTier.GOVERNMENT.value],
                "eu_ai_act_compliance": [PricingTier.SCALE.value, PricingTier.ENTERPRISE.value, PricingTier.GOVERNMENT.value],
                "cost_savings_calculator": [PricingTier.GROWTH.value, PricingTier.SCALE.value, PricingTier.ENTERPRISE.value, PricingTier.GOVERNMENT.value]
            },
            
            "enterprise_features": {
                "api_access": [PricingTier.ENTERPRISE.value, PricingTier.GOVERNMENT.value],
                "white_label_deployment": [PricingTier.ENTERPRISE.value, PricingTier.GOVERNMENT.value],
                "custom_integrations": [PricingTier.SCALE.value, PricingTier.ENTERPRISE.value, PricingTier.GOVERNMENT.value],
                "dedicated_support": [PricingTier.SCALE.value, PricingTier.ENTERPRISE.value, PricingTier.GOVERNMENT.value],
                "on_premises_deployment": [PricingTier.GOVERNMENT.value],
                "source_code_access": [PricingTier.GOVERNMENT.value]
            }
        }
    
    def _load_discount_rules(self) -> Dict[str, Any]:
        """Define discount rules and promotional offers"""
        return {
            "annual_discount": {
                "description": "2 months free on annual billing",
                "discount_months": 2,
                "min_tier": PricingTier.STARTUP.value
            },
            
            "volume_discounts": {
                "multi_year": {
                    "2_year": 0.10,  # 10% discount
                    "3_year": 0.15,  # 15% discount
                },
                "multiple_licenses": {
                    "3-5_licenses": 0.05,   # 5% discount
                    "6-10_licenses": 0.10,  # 10% discount
                    "11+_licenses": 0.15    # 15% discount
                }
            },
            
            "promotional": {
                "early_adopter": {
                    "discount": 0.20,  # 20% off first year
                    "valid_until": "2025-12-31",
                    "description": "Early adopter discount"
                },
                "exact_online_users": {
                    "discount": 0.15,  # 15% off for Exact Online customers
                    "description": "Exact Online customer special pricing",
                    "verification_required": True
                }
            }
        }
    
    def get_tier_pricing(self, tier: PricingTier, billing_cycle: BillingCycle = BillingCycle.MONTHLY) -> Dict[str, Any]:
        """Get pricing for specific tier and billing cycle"""
        tier_data = self.pricing_data["tiers"].get(tier.value)
        if not tier_data:
            raise ValueError(f"Invalid pricing tier: {tier.value}")
        
        pricing = {
            "tier": tier.value,
            "name": tier_data["name"],
            "description": tier_data["description"],
            "billing_cycle": billing_cycle.value,
            "currency": self.currency
        }
        
        if billing_cycle == BillingCycle.MONTHLY:
            pricing["price"] = tier_data["monthly_price"]
            pricing["billing_frequency"] = "monthly"
        elif billing_cycle == BillingCycle.ANNUAL:
            pricing["price"] = tier_data["annual_price"]
            pricing["billing_frequency"] = "annual"
            pricing["savings"] = (tier_data["monthly_price"] * 12) - tier_data["annual_price"]
            pricing["discount_percentage"] = round((pricing["savings"] / (tier_data["monthly_price"] * 12)) * 100)
        elif billing_cycle == BillingCycle.ONE_TIME and tier == PricingTier.GOVERNMENT:
            pricing["price"] = tier_data["license_price"]
            pricing["maintenance_fee"] = tier_data["annual_maintenance"]
            pricing["billing_frequency"] = "one_time"
        
        return pricing
    
    def get_features_for_tier(self, tier: PricingTier) -> List[str]:
        """Get list of features available for specific tier"""
        available_features = []
        
        for category, features in self.features_matrix.items():
            for feature, tiers in features.items():
                if tier.value in tiers:
                    available_features.append(feature)
        
        return available_features
    
    def calculate_pricing_with_discounts(self, tier: PricingTier, billing_cycle: BillingCycle, 
                                       discount_code: Optional[str] = None,
                                       quantity: int = 1) -> Dict[str, Any]:
        """Calculate final pricing with applicable discounts"""
        
        base_pricing = self.get_tier_pricing(tier, billing_cycle)
        base_price = base_pricing["price"]
        
        discounts_applied = []
        total_discount = 0
        
        # Volume discount
        if quantity > 1:
            volume_rules = self.discounts["volume_discounts"]["multiple_licenses"]
            if quantity >= 11:
                discount = volume_rules["11+_licenses"]
                discounts_applied.append(f"Volume discount (11+ licenses): {discount*100}%")
                total_discount += discount
            elif quantity >= 6:
                discount = volume_rules["6-10_licenses"] 
                discounts_applied.append(f"Volume discount (6-10 licenses): {discount*100}%")
                total_discount += discount
            elif quantity >= 3:
                discount = volume_rules["3-5_licenses"]
                discounts_applied.append(f"Volume discount (3-5 licenses): {discount*100}%")
                total_discount += discount
        
        # Promotional discount
        if discount_code:
            promo = self.discounts["promotional"].get(discount_code)
            if promo:
                # Check validity
                if "valid_until" in promo:
                    valid_until = datetime.strptime(promo["valid_until"], "%Y-%m-%d")
                    if datetime.now() <= valid_until:
                        total_discount += promo["discount"]
                        discounts_applied.append(f"{promo['description']}: {promo['discount']*100}%")
                else:
                    total_discount += promo["discount"]
                    discounts_applied.append(f"{promo['description']}: {promo['discount']*100}%")
        
        # Cap total discount at 40%
        total_discount = min(total_discount, 0.40)
        
        final_price = base_price * (1 - total_discount) * quantity
        discount_amount = (base_price * quantity) - final_price
        
        return {
            **base_pricing,
            "quantity": quantity,
            "base_total": base_price * quantity,
            "discount_percentage": round(total_discount * 100, 1),
            "discount_amount": round(discount_amount, 2),
            "final_price": round(final_price, 2),
            "discounts_applied": discounts_applied,
            "per_unit_price": round(final_price / quantity, 2)
        }
    
    def get_competitive_comparison(self, tier: PricingTier) -> Dict[str, Any]:
        """Get competitive pricing comparison"""
        tier_data = self.pricing_data["tiers"].get(tier.value)
        
        competitor_costs = {
            PricingTier.STARTUP.value: {"onetrust": 5000, "basic_tools": 2500},
            PricingTier.GROWTH.value: {"onetrust": 15000, "mid_tier": 8500},
            PricingTier.SCALE.value: {"onetrust": 25000, "bigid": 40000},
            PricingTier.ENTERPRISE.value: {"onetrust": 65000, "bigid_stack": 100000},
            PricingTier.GOVERNMENT.value: {"enterprise_deployment": 150000}
        }
        
        our_price = tier_data.get("annual_price", tier_data.get("license_price", 0))
        competitors = competitor_costs.get(tier.value, {})
        
        comparisons = []
        for competitor, cost in competitors.items():
            savings = cost - our_price
            percentage = round((savings / cost) * 100, 1)
            comparisons.append({
                "competitor": competitor.replace("_", " ").title(),
                "competitor_cost": cost,
                "our_price": our_price,
                "savings": savings,
                "savings_percentage": percentage
            })
        
        return {
            "tier": tier.value,
            "our_annual_price": our_price,
            "comparisons": comparisons
        }
    
    def update_pricing(self, updates: Dict[str, Any]) -> bool:
        """Update pricing configuration (for admin use)"""
        try:
            # Update version and timestamp
            self.pricing_data["version"] = str(float(self.pricing_data["version"]) + 0.1)
            self.pricing_data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            
            # Apply updates
            if "tiers" in updates:
                for tier_name, tier_updates in updates["tiers"].items():
                    if tier_name in self.pricing_data["tiers"]:
                        self.pricing_data["tiers"][tier_name].update(tier_updates)
            
            if "discounts" in updates:
                self.discounts.update(updates["discounts"])
            
            return True
        except Exception as e:
            print(f"Error updating pricing: {e}")
            return False

# Global pricing instance
_pricing_config = None

def get_pricing_config(region: str = "Netherlands") -> PricingConfig:
    """Get global pricing configuration instance"""
    global _pricing_config
    if _pricing_config is None or _pricing_config.region != region:
        _pricing_config = PricingConfig(region)
    return _pricing_config

# Convenience functions for common operations
def get_all_tiers() -> List[Dict[str, Any]]:
    """Get all pricing tiers"""
    config = get_pricing_config()
    return [config.get_tier_pricing(tier) for tier in PricingTier if tier != PricingTier.GOVERNMENT]

def get_tier_features(tier_name: str) -> List[str]:
    """Get features for tier by name"""
    config = get_pricing_config()
    tier = PricingTier(tier_name)
    return config.get_features_for_tier(tier)

def calculate_savings_vs_competitors(tier_name: str) -> Dict[str, Any]:
    """Calculate savings vs competitors for tier"""
    config = get_pricing_config() 
    tier = PricingTier(tier_name)
    return config.get_competitive_comparison(tier)