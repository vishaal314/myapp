#!/usr/bin/env python3
"""
Create Default Development License
Simple script to create a working license for development
"""

import json
import os
from datetime import datetime, timedelta

def create_development_license():
    """Create a simple development license"""
    
    # Create a development license structure
    license_data = {
        "license_id": "dev-license-001",
        "license_type": "enterprise",
        "customer_id": "development",
        "customer_name": "Development User",
        "company_name": "DataGuardian Pro Development",
        "email": "dev@dataguardian.pro",
        "issued_date": datetime.now().isoformat(),
        "expiry_date": (datetime.now() + timedelta(days=365)).isoformat(),
        "usage_limits": [
            {
                "limit_type": "scans_per_month",
                "limit_value": 10000,
                "current_usage": 0,
                "reset_period": "monthly",
                "last_reset": datetime.now().isoformat()
            },
            {
                "limit_type": "concurrent_users",
                "limit_value": 100,
                "current_usage": 0,
                "reset_period": "monthly",
                "last_reset": datetime.now().isoformat()
            },
            {
                "limit_type": "export_reports",
                "limit_value": 999999,
                "current_usage": 0,
                "reset_period": "monthly",
                "last_reset": datetime.now().isoformat()
            },
            {
                "limit_type": "scanner_types",
                "limit_value": 10,
                "current_usage": 0,
                "reset_period": "monthly",
                "last_reset": datetime.now().isoformat()
            }
        ],
        "allowed_features": [
            "code_scanner", "document_scanner", "image_scanner", "database_scanner",
            "api_scanner", "ai_model_scanner", "website_scanner", "soc2_scanner",
            "dpia_scanner", "sustainability_scanner", "reporting", "audit_trail",
            "compliance_dashboard", "multi_region", "api_access", "white_label"
        ],
        "allowed_scanners": [
            "code", "document", "image", "database", "api", "ai_model",
            "website", "soc2", "dpia", "sustainability"
        ],
        "allowed_regions": ["Netherlands", "Germany", "France", "Belgium", "EU", "Global"],
        "max_concurrent_users": 100,
        "is_active": True,
        "metadata": {
            "generated_by": "DataGuardian Pro License Manager",
            "version": "1.0",
            "hardware_id": "development",
            "creation_timestamp": datetime.now().isoformat()
        }
    }
    
    # Save to license.json
    with open("license.json", "w") as f:
        json.dump(license_data, f, indent=2)
    
    print("✅ Development license created successfully!")
    print(f"License ID: {license_data['license_id']}")
    print(f"License Type: {license_data['license_type']}")
    print(f"Valid until: {license_data['expiry_date']}")
    print(f"File saved: license.json")

if __name__ == "__main__":
    create_development_license()