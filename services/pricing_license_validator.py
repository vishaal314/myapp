#!/usr/bin/env python3
"""
Copyright (c) 2025 DataGuardian Pro B.V.
All rights reserved.

Pricing-License Alignment Validator
Ensures consistency between pricing configuration and license management
"""

from typing import Dict, List, Any, Optional
import logging
from enum import Enum

from config.pricing_config import PricingTier, get_pricing_config
from services.license_manager import LicenseType, LicenseManager

logger = logging.getLogger(__name__)

class PricingLicenseValidator:
    """Validates alignment between pricing and license systems"""
    
    def __init__(self):
        self.pricing_config = get_pricing_config()
        self.license_manager = LicenseManager()
        self.tier_mapping = self._initialize_tier_mapping()
    
    def _initialize_tier_mapping(self) -> Dict[str, str]:
        """Map pricing tiers to license types"""
        return {
            PricingTier.STARTUP.value: LicenseType.STARTUP.value,
            PricingTier.PROFESSIONAL.value: LicenseType.PROFESSIONAL.value,
            PricingTier.GROWTH.value: LicenseType.GROWTH.value,
            PricingTier.SCALE.value: LicenseType.SCALE.value,
            PricingTier.ENTERPRISE.value: LicenseType.ENTERPRISE.value,
            PricingTier.GOVERNMENT.value: LicenseType.GOVERNMENT.value
        }
    
    def validate_tier_alignment(self) -> Dict[str, Any]:
        """Validate that pricing tiers align with license types"""
        validation_results = {
            "aligned": True,
            "issues": [],
            "tier_validations": {}
        }
        
        for pricing_tier, license_type in self.tier_mapping.items():
            tier_validation = self._validate_single_tier(pricing_tier, license_type)
            validation_results["tier_validations"][pricing_tier] = tier_validation
            
            if not tier_validation["aligned"]:
                validation_results["aligned"] = False
                validation_results["issues"].extend(tier_validation["issues"])
        
        return validation_results
    
    def _validate_single_tier(self, pricing_tier: str, license_type: str) -> Dict[str, Any]:
        """Validate alignment for a single pricing tier"""
        result = {
            "aligned": True,
            "issues": [],
            "pricing_data": {},
            "license_data": {}
        }
        
        try:
            # Get pricing data
            pricing_data = self.pricing_config.pricing_data["tiers"].get(pricing_tier)
            if not pricing_data:
                result["aligned"] = False
                result["issues"].append(f"Pricing tier {pricing_tier} not found")
                return result
            
            # Get expected license limits based on pricing
            expected_scans = pricing_data.get("max_scans_monthly", 0)
            expected_data_sources = pricing_data.get("max_data_sources", 0)
            
            result["pricing_data"] = {
                "monthly_price": pricing_data.get("monthly_price"),
                "max_scans_monthly": expected_scans,
                "max_data_sources": expected_data_sources,
                "support_level": pricing_data.get("support_level"),
                "sla_hours": pricing_data.get("sla_hours")
            }
            
            # Validate license type exists
            try:
                license_enum = LicenseType(license_type)
                result["license_data"]["license_type"] = license_type
                result["license_data"]["exists"] = True
            except ValueError:
                result["aligned"] = False
                result["issues"].append(f"License type {license_type} not found in LicenseType enum")
                result["license_data"]["exists"] = False
            
            # Cross-validate scan limits
            self._validate_scan_limits(pricing_tier, expected_scans, result)
            
            # Validate feature alignment
            self._validate_feature_alignment(pricing_tier, license_type, result)
            
        except Exception as e:
            result["aligned"] = False
            result["issues"].append(f"Validation error: {str(e)}")
            logger.error(f"Error validating tier {pricing_tier}: {e}")
        
        return result
    
    def _validate_scan_limits(self, pricing_tier: str, expected_scans: Any, result: Dict[str, Any]):
        """Validate scan limits alignment"""
        if isinstance(expected_scans, str) and expected_scans == "unlimited":
            expected_scans = 999999
        elif isinstance(expected_scans, int):
            pass
        else:
            result["issues"].append(f"Invalid scan limit format for {pricing_tier}: {expected_scans}")
            return
        
        # Check if license limits match pricing expectations
        result["license_data"]["expected_scan_limit"] = expected_scans
        
        # Validate reasonable limits
        pricing_price = result["pricing_data"].get("monthly_price", 0)
        if pricing_price > 0:
            scans_per_euro = expected_scans / pricing_price if expected_scans != 999999 else "unlimited"
            result["license_data"]["value_ratio"] = scans_per_euro
            
            # Flag unrealistic ratios (should be reasonable value per euro)
            if isinstance(scans_per_euro, (int, float)) and scans_per_euro < 1:
                result["issues"].append(f"Low value ratio for {pricing_tier}: {scans_per_euro:.2f} scans per euro")
    
    def _validate_feature_alignment(self, pricing_tier: str, license_type: str, result: Dict[str, Any]):
        """Validate feature availability alignment"""
        try:
            # Get features from pricing config
            pricing_features = self.pricing_config.get_features_for_tier(
                PricingTier(pricing_tier)
            )
            
            # Expected features based on pricing tier
            expected_features = {
                PricingTier.STARTUP.value: [
                    "basic_pii_scanning", "gdpr_compliance_reports", 
                    "netherlands_bsn_detection", "eu_ai_act_compliance"
                ],
                PricingTier.PROFESSIONAL.value: [
                    "basic_pii_scanning", "enterprise_connectors",
                    "compliance_certificates", "dpia_automation"
                ],
                PricingTier.GROWTH.value: [
                    "enterprise_connectors", "microsoft365_integration",
                    "quarterly_business_reviews", "dedicated_support"
                ],
                PricingTier.SCALE.value: [
                    "api_access", "white_label_deployment", "custom_integrations"
                ],
                PricingTier.ENTERPRISE.value: [
                    "legal_consultation", "regulatory_change_monitoring"
                ]
            }
            
            tier_expected = expected_features.get(pricing_tier, [])
            missing_features = [f for f in tier_expected if f not in pricing_features]
            
            result["license_data"]["available_features"] = len(pricing_features)
            result["license_data"]["expected_key_features"] = tier_expected
            result["license_data"]["missing_features"] = missing_features
            
            if missing_features:
                result["issues"].append(
                    f"Missing key features for {pricing_tier}: {', '.join(missing_features)}"
                )
                
        except Exception as e:
            result["issues"].append(f"Feature validation error: {str(e)}")
    
    def get_tier_recommendations(self) -> Dict[str, List[str]]:
        """Get recommendations for improving tier alignment"""
        recommendations = {
            "pricing_improvements": [],
            "license_improvements": [],
            "value_optimizations": []
        }
        
        validation = self.validate_tier_alignment()
        
        for tier, tier_data in validation["tier_validations"].items():
            if not tier_data["aligned"]:
                for issue in tier_data["issues"]:
                    if "scan limit" in issue.lower():
                        recommendations["license_improvements"].append(
                            f"Adjust scan limits for {tier} tier: {issue}"
                        )
                    elif "feature" in issue.lower():
                        recommendations["pricing_improvements"].append(
                            f"Add missing features to {tier} tier: {issue}"
                        )
                    elif "value ratio" in issue.lower():
                        recommendations["value_optimizations"].append(
                            f"Improve value proposition for {tier} tier: {issue}"
                        )
        
        # Add general recommendations
        if not validation["aligned"]:
            recommendations["pricing_improvements"].append(
                "Ensure all pricing tiers have corresponding license types"
            )
            recommendations["license_improvements"].append(
                "Update license limits to match pricing tier expectations"
            )
            recommendations["value_optimizations"].append(
                "Verify customer value proposition meets pricing expectations"
            )
        
        return recommendations
    
    def generate_alignment_report(self) -> str:
        """Generate a comprehensive alignment report"""
        validation = self.validate_tier_alignment()
        recommendations = self.get_tier_recommendations()
        
        report = []
        report.append("# Pricing-License Alignment Report")
        report.append(f"**Overall Status**: {'✅ ALIGNED' if validation['aligned'] else '❌ MISALIGNED'}")
        report.append("")
        
        # Tier-by-tier analysis
        report.append("## Tier Analysis")
        for tier, data in validation["tier_validations"].items():
            status = "✅" if data["aligned"] else "❌"
            report.append(f"### {tier.title()} Tier {status}")
            
            if "pricing_data" in data:
                pricing = data["pricing_data"]
                report.append(f"- **Price**: €{pricing.get('monthly_price', 0)}/month")
                report.append(f"- **Scans**: {pricing.get('max_scans_monthly', 0)}/month")
                report.append(f"- **Support SLA**: {pricing.get('sla_hours', 0)} hours")
            
            if data["issues"]:
                report.append("**Issues:**")
                for issue in data["issues"]:
                    report.append(f"- {issue}")
            
            report.append("")
        
        # Recommendations
        if recommendations["pricing_improvements"]:
            report.append("## Pricing Improvements")
            for rec in recommendations["pricing_improvements"]:
                report.append(f"- {rec}")
            report.append("")
        
        if recommendations["license_improvements"]:
            report.append("## License Improvements")
            for rec in recommendations["license_improvements"]:
                report.append(f"- {rec}")
            report.append("")
        
        if recommendations["value_optimizations"]:
            report.append("## Value Optimizations")
            for rec in recommendations["value_optimizations"]:
                report.append(f"- {rec}")
        
        return "\n".join(report)

# Validation helper functions
def validate_pricing_license_alignment() -> bool:
    """Quick validation check"""
    validator = PricingLicenseValidator()
    result = validator.validate_tier_alignment()
    return result["aligned"]

def get_alignment_issues() -> List[str]:
    """Get list of alignment issues"""
    validator = PricingLicenseValidator()
    result = validator.validate_tier_alignment()
    return result["issues"]

def print_alignment_report():
    """Print comprehensive alignment report"""
    validator = PricingLicenseValidator()
    report = validator.generate_alignment_report()
    print(report)

if __name__ == "__main__":
    print_alignment_report()