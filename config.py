"""
DataGuardian Pro - Configuration Module
"""
import os

# License tiers configuration
LICENSE_TIERS = {
    "free": {
        "name": "Free Trial",
        "price": 0,
        "features": ["Basic scanning", "Up to 10 scans/month"],
        "scanners": ["code", "blob"]
    },
    "professional": {
        "name": "Professional",
        "price": 99,
        "features": ["Advanced scanning", "Unlimited scans", "PDF reports"],
        "scanners": ["code", "blob", "website", "database", "image"]
    },
    "enterprise": {
        "name": "Enterprise",
        "price": 499,
        "features": ["All features", "Priority support", "Custom integration"],
        "scanners": ["all"]
    }
}

# Scanner configurations
SCANNER_LIMITS = {
    "free": {
        "max_scans_per_month": 10,
        "max_file_size_mb": 10
    },
    "professional": {
        "max_scans_per_month": -1,  # unlimited
        "max_file_size_mb": 100
    },
    "enterprise": {
        "max_scans_per_month": -1,
        "max_file_size_mb": 1000
    }
}

# Database configuration
DATABASE_CONFIG = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": os.getenv("PGPORT", "5432"),
    "database": os.getenv("PGDATABASE", "dataguardian"),
    "user": os.getenv("PGUSER", "dataguardian"),
    "password": os.getenv("PGPASSWORD", "changeme")
}

# Application settings
APP_CONFIG = {
    "name": "DataGuardian Pro",
    "version": "2.0.0",
    "environment": os.getenv("ENVIRONMENT", "production"),
    "debug": os.getenv("DEBUG", "False").lower() == "true"
}
