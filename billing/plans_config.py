"""
Subscription Plans Configuration for DataGuardian Pro

This module defines the subscription plans and pricing for the application.
"""

# Define available subscription plans and their features
SUBSCRIPTION_PLANS = {
    "basic": {
        "name": "Basic",
        "price": 9.99,
        "currency": "EUR",
        "description": "Essential compliance scanning for small businesses",
        "features": [
            "5 GDPR Scans per month",
            "Basic reporting",
            "Email support",
            "Dashboard access",
            "Single user account"
        ],
        "max_users": 1,
        "scan_limits": {
            "gdpr": 5,
            "soc2": 0,
            "ai_model": 0
        }
    },
    "professional": {
        "name": "Professional",
        "price": 49.99,
        "currency": "EUR",
        "description": "Advanced compliance for growing businesses",
        "features": [
            "20 GDPR Scans per month",
            "10 SOC2 Scans per month",
            "Advanced reporting",
            "Priority email support",
            "Dashboard access",
            "Up to 5 user accounts",
            "Compliance certificate generation"
        ],
        "max_users": 5,
        "scan_limits": {
            "gdpr": 20,
            "soc2": 10,
            "ai_model": 0
        }
    },
    "enterprise": {
        "name": "Enterprise",
        "price": 99.99,
        "currency": "EUR",
        "description": "Complete compliance solution for organizations",
        "features": [
            "Unlimited GDPR Scans",
            "Unlimited SOC2 Scans",
            "Advanced AI Model Scans",
            "Premium reporting with risk analysis",
            "24/7 Priority support",
            "Full dashboard access",
            "Unlimited user accounts",
            "Compliance certificate generation",
            "Custom compliance policy development",
            "Dedicated compliance officer"
        ],
        "max_users": float('inf'),  # Unlimited users
        "scan_limits": {
            "gdpr": float('inf'),  # Unlimited
            "soc2": float('inf'),  # Unlimited
            "ai_model": float('inf')  # Unlimited
        }
    },
    "gold": {  # Gold is an alias for Enterprise
        "name": "Gold",
        "price": 99.99,
        "currency": "EUR",
        "description": "Complete compliance solution for organizations",
        "features": [
            "Unlimited GDPR Scans",
            "Unlimited SOC2 Scans",
            "Advanced AI Model Scans",
            "Premium reporting with risk analysis",
            "24/7 Priority support",
            "Full dashboard access",
            "Unlimited user accounts",
            "Compliance certificate generation",
            "Custom compliance policy development",
            "Dedicated compliance officer"
        ],
        "max_users": float('inf'),  # Unlimited users
        "scan_limits": {
            "gdpr": float('inf'),  # Unlimited
            "soc2": float('inf'),  # Unlimited
            "ai_model": float('inf')  # Unlimited
        }
    }
}

# Define trial plan details
TRIAL_PLAN = {
    "duration_days": 14,
    "plan": "professional"  # Trial users get Professional features
}

# Define payment method types and their display settings
PAYMENT_METHODS = {
    "card": {
        "display_name": "Credit Card",
        "icon": "💳",
        "supported_brands": ["visa", "mastercard", "amex"]
    },
    "ideal": {
        "display_name": "iDEAL (Netherlands)",
        "icon": "🏦",
        "supported_banks": [
            "ABN AMRO",
            "ASN Bank",
            "Bunq",
            "Handelsbanken",
            "ING Bank",
            "Knab",
            "Moneyou",
            "Rabobank",
            "RegioBank",
            "SNS Bank",
            "Triodos Bank",
            "Van Lanschot"
        ]
    }
}

# Format functions for displaying prices
def format_price(amount, currency="EUR"):
    """Format a price amount with currency symbol"""
    if currency == "EUR":
        return f"€{amount:.2f}"
    elif currency == "USD":
        return f"${amount:.2f}"
    else:
        return f"{amount:.2f} {currency}"