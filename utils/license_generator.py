"""
License Generator Tool
Generate licenses for different deployment scenarios
"""

import json
import argparse
import sys
from datetime import datetime, timedelta
from services.license_manager import LicenseManager, LicenseType, UsageLimitType

def generate_trial_license(customer_name: str, company_name: str, email: str, days: int = 30):
    """Generate trial license"""
    license_manager = LicenseManager()
    
    license_config = license_manager.generate_license(
        license_type=LicenseType.TRIAL,
        customer_id=f"trial_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        customer_name=customer_name,
        company_name=company_name,
        email=email,
        validity_days=days
    )
    
    return license_config

def generate_standalone_license(customer_name: str, company_name: str, email: str, days: int = 365):
    """Generate standalone license for desktop deployment"""
    license_manager = LicenseManager()
    
    license_config = license_manager.generate_license(
        license_type=LicenseType.STANDALONE,
        customer_id=f"standalone_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        customer_name=customer_name,
        company_name=company_name,
        email=email,
        validity_days=days
    )
    
    return license_config

def generate_enterprise_license(customer_name: str, company_name: str, email: str, 
                               days: int = 365, custom_limits: dict = None):
    """Generate enterprise license with custom limits"""
    license_manager = LicenseManager()
    
    license_config = license_manager.generate_license(
        license_type=LicenseType.ENTERPRISE,
        customer_id=f"enterprise_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        customer_name=customer_name,
        company_name=company_name,
        email=email,
        validity_days=days,
        custom_limits=custom_limits
    )
    
    return license_config

def generate_custom_license(customer_name: str, company_name: str, email: str,
                           license_type: str, days: int = 365, custom_limits: dict = None):
    """Generate custom license"""
    license_manager = LicenseManager()
    
    try:
        license_type_enum = LicenseType(license_type.lower())
    except ValueError:
        raise ValueError(f"Invalid license type: {license_type}")
    
    license_config = license_manager.generate_license(
        license_type=license_type_enum,
        customer_id=f"custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        customer_name=customer_name,
        company_name=company_name,
        email=email,
        validity_days=days,
        custom_limits=custom_limits
    )
    
    return license_config

def save_license_file(license_config, filename: str = None):
    """Save license to file"""
    if not filename:
        filename = f"license_{license_config.license_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    license_manager = LicenseManager()
    license_manager.license_file = filename
    success = license_manager.save_license(license_config)
    
    if success:
        print(f"License saved to: {filename}")
        return filename
    else:
        print("Failed to save license")
        return None

def print_license_info(license_config):
    """Print license information"""
    print("\n" + "="*50)
    print("LICENSE INFORMATION")
    print("="*50)
    print(f"License ID: {license_config.license_id}")
    print(f"Type: {license_config.license_type.value.upper()}")
    print(f"Customer: {license_config.customer_name}")
    print(f"Company: {license_config.company_name}")
    print(f"Email: {license_config.email}")
    print(f"Issued: {license_config.issued_date.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Expires: {license_config.expiry_date.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Days Valid: {(license_config.expiry_date - license_config.issued_date).days}")
    print(f"Max Concurrent Users: {license_config.max_concurrent_users}")
    
    print("\nALLOWED FEATURES:")
    for feature in license_config.allowed_features:
        print(f"  ✓ {feature}")
    
    print("\nALLOWED SCANNERS:")
    for scanner in license_config.allowed_scanners:
        print(f"  ✓ {scanner}")
    
    print("\nALLOWED REGIONS:")
    for region in license_config.allowed_regions:
        print(f"  ✓ {region}")
    
    print("\nUSAGE LIMITS:")
    for limit in license_config.usage_limits:
        print(f"  • {limit.limit_type.value}: {limit.limit_value} per {limit.reset_period}")
    
    print("="*50)

def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description='DataGuardian Pro License Generator')
    parser.add_argument('--type', choices=['trial', 'basic', 'professional', 'enterprise', 'standalone'], 
                       default='trial', help='License type')
    parser.add_argument('--customer', required=True, help='Customer name')
    parser.add_argument('--company', required=True, help='Company name')
    parser.add_argument('--email', required=True, help='Customer email')
    parser.add_argument('--days', type=int, default=365, help='License validity in days')
    parser.add_argument('--output', help='Output filename')
    parser.add_argument('--custom-limits', help='Custom limits as JSON string')
    
    args = parser.parse_args()
    
    # Parse custom limits if provided
    custom_limits = None
    if args.custom_limits:
        try:
            limits_data = json.loads(args.custom_limits)
            custom_limits = {}
            for limit_type, value in limits_data.items():
                try:
                    custom_limits[UsageLimitType(limit_type)] = value
                except ValueError:
                    print(f"Warning: Invalid limit type '{limit_type}' ignored")
        except json.JSONDecodeError:
            print("Error: Invalid JSON in custom limits")
            sys.exit(1)
    
    # Generate license based on type
    try:
        if args.type == 'trial':
            license_config = generate_trial_license(args.customer, args.company, args.email, args.days)
        elif args.type == 'standalone':
            license_config = generate_standalone_license(args.customer, args.company, args.email, args.days)
        elif args.type == 'enterprise':
            license_config = generate_enterprise_license(args.customer, args.company, args.email, args.days, custom_limits)
        else:
            license_config = generate_custom_license(args.customer, args.company, args.email, args.type, args.days, custom_limits)
        
        # Print license info
        print_license_info(license_config)
        
        # Save license
        filename = save_license_file(license_config, args.output)
        
        if filename:
            print(f"\n✅ License generated successfully: {filename}")
        else:
            print("\n❌ Failed to generate license")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error generating license: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()