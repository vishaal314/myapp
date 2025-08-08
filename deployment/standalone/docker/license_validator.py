"""
DataGuardian Pro - License Validator
Validates license keys for standalone deployments
"""

import os
import hashlib
import json
import datetime
from typing import Dict, Optional, Tuple
from cryptography.fernet import Fernet
import base64

class LicenseValidator:
    """Validates and manages DataGuardian Pro licenses"""
    
    def __init__(self, license_file: str = None):
        self.license_file = license_file or os.getenv('LICENSE_FILE', '/app/licenses/license.key')
        self.license_data = None
        self.is_valid = False
        self.features = {}
        self.limits = {}
        
    def validate_license(self) -> Tuple[bool, str]:
        """
        Validate the license file and extract permissions
        Returns: (is_valid, message)
        """
        try:
            if not os.path.exists(self.license_file):
                return self._create_demo_license()
            
            with open(self.license_file, 'r') as f:
                license_content = f.read().strip()
            
            # Check if it's a demo license
            if license_content.startswith('DEMO_LICENSE'):
                return self._validate_demo_license(license_content)
            
            # Validate production license
            return self._validate_production_license(license_content)
            
        except Exception as e:
            return False, f"License validation error: {str(e)}"
    
    def _create_demo_license(self) -> Tuple[bool, str]:
        """Create a 30-day demo license"""
        try:
            os.makedirs(os.path.dirname(self.license_file), exist_ok=True)
            
            demo_content = f"""DEMO_LICENSE_30_DAYS_{datetime.datetime.now().strftime('%Y%m%d')}
DataGuardian Pro Demo License
Valid until: {(datetime.datetime.now() + datetime.timedelta(days=30)).strftime('%Y-%m-%d')}
Features: All scanners enabled
Users: Up to 5 concurrent
Scans: Up to 100 per month
Support: Community only"""
            
            with open(self.license_file, 'w') as f:
                f.write(demo_content)
            
            return self._validate_demo_license(demo_content)
            
        except Exception as e:
            return False, f"Failed to create demo license: {str(e)}"
    
    def _validate_demo_license(self, content: str) -> Tuple[bool, str]:
        """Validate demo license"""
        lines = content.split('\n')
        
        if len(lines) < 3:
            return False, "Invalid demo license format"
        
        # Extract expiration date
        for line in lines:
            if line.startswith('Valid until:'):
                try:
                    expiry_str = line.split(': ')[1]
                    expiry_date = datetime.datetime.strptime(expiry_str, '%Y-%m-%d')
                    
                    if datetime.datetime.now() > expiry_date:
                        return False, f"Demo license expired on {expiry_str}"
                    
                    # Set demo limits
                    self.features = {
                        'code_scanner': True,
                        'api_scanner': True,
                        'dpia_scanner': True,
                        'ai_scanner': True,
                        'website_scanner': True,
                        'database_scanner': True,
                        'image_scanner': True,
                        'blob_scanner': True,
                        'soc2_scanner': True,
                        'sustainability_scanner': True
                    }
                    
                    self.limits = {
                        'max_users': 5,
                        'max_scans_per_month': 100,
                        'support_level': 'community',
                        'expires': expiry_date,
                        'license_type': 'demo'
                    }
                    
                    self.is_valid = True
                    remaining_days = (expiry_date - datetime.datetime.now()).days
                    return True, f"Demo license valid ({remaining_days} days remaining)"
                    
                except ValueError:
                    return False, "Invalid expiration date format"
        
        return False, "No expiration date found in demo license"
    
    def _validate_production_license(self, content: str) -> Tuple[bool, str]:
        """Validate production license (encrypted)"""
        try:
            # For demo purposes, we'll use a simple validation
            # In production, this would use proper encryption/signing
            
            if self._verify_license_signature(content):
                license_data = self._decrypt_license(content)
                
                if license_data:
                    self.features = license_data.get('features', {})
                    self.limits = license_data.get('limits', {})
                    
                    # Check expiration
                    if 'expires' in self.limits:
                        expiry_date = datetime.datetime.fromisoformat(self.limits['expires'])
                        if datetime.datetime.now() > expiry_date:
                            return False, "License has expired"
                    
                    self.is_valid = True
                    return True, "Valid production license"
                else:
                    return False, "Failed to decrypt license"
            else:
                return False, "Invalid license signature"
                
        except Exception as e:
            return False, f"Production license validation failed: {str(e)}"
    
    def _verify_license_signature(self, content: str) -> bool:
        """Verify license signature (simplified for demo)"""
        # In production, this would verify a cryptographic signature
        return len(content) > 50 and 'DataGuardian' in content
    
    def _decrypt_license(self, content: str) -> Optional[Dict]:
        """Decrypt license content (simplified for demo)"""
        # In production, this would use proper encryption
        # For demo, return enterprise features
        return {
            'features': {
                'code_scanner': True,
                'api_scanner': True,
                'dpia_scanner': True,
                'ai_scanner': True,
                'website_scanner': True,
                'database_scanner': True,
                'image_scanner': True,
                'blob_scanner': True,
                'soc2_scanner': True,
                'sustainability_scanner': True
            },
            'limits': {
                'max_users': 1000,
                'max_scans_per_month': 100000,
                'support_level': 'enterprise',
                'license_type': 'enterprise'
            }
        }
    
    def get_feature_status(self, feature: str) -> bool:
        """Check if a feature is enabled"""
        return self.features.get(feature, False)
    
    def get_usage_limits(self) -> Dict:
        """Get usage limits"""
        return self.limits.copy()
    
    def is_feature_available(self, feature: str) -> Tuple[bool, str]:
        """
        Check if a feature is available and why
        Returns: (available, reason)
        """
        if not self.is_valid:
            return False, "Invalid or missing license"
        
        if not self.features.get(feature, False):
            return False, f"Feature '{feature}' not included in license"
        
        return True, "Feature available"
    
    def get_license_info(self) -> Dict:
        """Get complete license information"""
        return {
            'valid': self.is_valid,
            'features': self.features,
            'limits': self.limits,
            'license_file': self.license_file
        }

# Global license validator instance
_license_validator = None

def get_license_validator() -> LicenseValidator:
    """Get the global license validator instance"""
    global _license_validator
    if _license_validator is None:
        _license_validator = LicenseValidator()
        _license_validator.validate_license()
    return _license_validator

def check_feature_license(feature: str) -> Tuple[bool, str]:
    """Quick check if a feature is licensed"""
    validator = get_license_validator()
    return validator.is_feature_available(feature)

def get_license_status() -> Dict:
    """Get current license status"""
    validator = get_license_validator()
    return validator.get_license_info()