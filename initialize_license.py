#!/usr/bin/env python3
"""
Initialize License System for DataGuardian Pro
Creates a default license for development/testing purposes
"""

import os
import json
import sys
from datetime import datetime, timedelta
from services.license_manager import LicenseManager, LicenseType, UsageLimitType

def create_default_license():
    """Create a default license for development purposes"""
    try:
        # Initialize license manager
        license_manager = LicenseManager()
        
        # Create a development license
        print("Creating development license...")
        
        license_config = license_manager.generate_license(
            license_type=LicenseType.ENTERPRISE,
            customer_id="dev_user_001",
            customer_name="Development User",
            company_name="DataGuardian Pro Development",
            email="dev@dataguardian.pro",
            validity_days=365,
            custom_limits={
                "scans_per_month": 10000,
                "concurrent_users": 100,
                "allowed_scanners": ["all"],
                "allowed_regions": ["all"],
                "max_reports": 1000
            }
        )
        
        print(f"✅ License created successfully!")
        print(f"License ID: {license_config.license_id}")
        print(f"License Type: {license_config.license_type.value}")
        print(f"Valid until: {license_config.expiry_date}")
        print(f"Customer: {license_config.customer_name}")
        print(f"Company: {license_config.company_name}")
        
        # Save the license
        license_manager.save_license(license_config)
        print("✅ License saved successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating license: {e}")
        return False

def verify_license():
    """Verify the created license"""
    try:
        from services.license_manager import check_license
        
        is_valid, message = check_license()
        
        if is_valid:
            print("✅ License verification successful!")
            print(f"Status: {message}")
            return True
        else:
            print(f"❌ License verification failed: {message}")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying license: {e}")
        return False

def main():
    """Main function"""
    print("DataGuardian Pro License Initialization")
    print("=" * 50)
    
    # Create default license
    if create_default_license():
        print("\n" + "=" * 50)
        print("Verifying created license...")
        
        if verify_license():
            print("\n✅ License system initialized successfully!")
            print("You can now run the application without license errors.")
        else:
            print("\n❌ License verification failed!")
            sys.exit(1)
    else:
        print("\n❌ Failed to create license!")
        sys.exit(1)

if __name__ == "__main__":
    main()