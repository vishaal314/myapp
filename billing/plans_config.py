"""
Subscription Plans Configuration for DataGuardian Pro

This module defines the subscription plans and their attributes for the application.
Plans include pricing, features, limitations, and associated Stripe product IDs.
"""

import os

# Define plan tiers
PLAN_TIERS = ["basic", "premium", "gold"]

# Define subscription plans with Stripe product and price IDs
SUBSCRIPTION_PLANS = {
    "basic": {
        "name": "Basic",
        "description": "Essential compliance scanning for small teams",
        "price": 49,
        "unit": "month",
        "features": [
            "Basic Privacy Scans",
            "5 repositories",
            "Weekly scans (10/month)",
            "Email support",
            "Basic PDF reports"
        ],
        "limitations": {
            "repositories": 5,
            "scans_per_month": 10,
            "report_retention_days": 30,
            "custom_policies": False,
            "team_members": 2
        },
        "color": "blue", 
        "icon": "🔍",
        "stripe_product_id": os.environ.get("STRIPE_BASIC_PRODUCT_ID", "prod_basic"),
        "stripe_price_id": os.environ.get("STRIPE_BASIC_PRICE_ID", "price_basic")
    },
    "premium": {
        "name": "Premium",
        "description": "Advanced compliance for growing organizations",
        "price": 99,
        "unit": "month",
        "features": [
            "All Basic features",
            "20 repositories",
            "Daily scans (30/month)",
            "SOC2 compliance",
            "Priority support",
            "Advanced reporting"
        ],
        "limitations": {
            "repositories": 20,
            "scans_per_month": 30,
            "report_retention_days": 90,
            "custom_policies": True,
            "team_members": 5
        },
        "color": "indigo",
        "icon": "⚡",
        "stripe_product_id": os.environ.get("STRIPE_PREMIUM_PRODUCT_ID", "prod_premium"),
        "stripe_price_id": os.environ.get("STRIPE_PREMIUM_PRICE_ID", "price_premium")
    },
    "gold": {
        "name": "Gold",
        "description": "Enterprise-grade compliance solution",
        "price": 199,
        "unit": "month",
        "features": [
            "All Premium features",
            "Unlimited repositories",
            "Continuous scanning",
            "Custom compliance policies",
            "Dedicated support agent",
            "White-labeled reports",
            "API access"
        ],
        "limitations": {
            "repositories": float('inf'),  # Unlimited
            "scans_per_month": float('inf'),  # Unlimited
            "report_retention_days": 365,
            "custom_policies": True,
            "team_members": 10
        },
        "color": "amber",
        "icon": "👑",
        "stripe_product_id": os.environ.get("STRIPE_GOLD_PRODUCT_ID", "prod_gold"),
        "stripe_price_id": os.environ.get("STRIPE_GOLD_PRICE_ID", "price_gold")
    }
}

# Mapping from Stripe price ID to plan tier for webhook processing
PRICE_ID_TO_TIER = {
    plan_data["stripe_price_id"]: tier
    for tier, plan_data in SUBSCRIPTION_PLANS.items()
}

def get_plan_by_tier(tier):
    """Get the plan configuration for a specific tier"""
    return SUBSCRIPTION_PLANS.get(tier, SUBSCRIPTION_PLANS["basic"])

def get_plan_by_price_id(price_id):
    """Get the plan tier based on a Stripe price ID"""
    tier = PRICE_ID_TO_TIER.get(price_id)
    if tier:
        return tier, SUBSCRIPTION_PLANS[tier]
    return "basic", SUBSCRIPTION_PLANS["basic"]

def is_feature_available(tier, feature_name):
    """Check if a specific feature is available in the given tier"""
    plan = get_plan_by_tier(tier)
    
    # Check if it's a standard feature
    for feature in plan["features"]:
        if feature_name.lower() in feature.lower():
            return True
    
    # Check in limitations with boolean values
    if feature_name in plan["limitations"]:
        return bool(plan["limitations"][feature_name])
    
    return False

def get_limit(tier, limit_name):
    """Get the numeric limit for a specific feature in the given tier"""
    plan = get_plan_by_tier(tier)
    return plan["limitations"].get(limit_name, 0)