"""
License Manager for DataGuardian Pro
Comprehensive licensing and usage control system
"""

import os
import json
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from cryptography.fernet import Fernet
import base64

logger = logging.getLogger(__name__)

class LicenseType(Enum):
    """License types for different deployment models"""
    TRIAL = "trial"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    STANDALONE = "standalone"
    SAAS = "saas"
    CUSTOM = "custom"

class UsageLimitType(Enum):
    """Types of usage limits"""
    SCANS_PER_MONTH = "scans_per_month"
    SCANS_PER_DAY = "scans_per_day"
    CONCURRENT_USERS = "concurrent_users"
    API_CALLS = "api_calls"
    STORAGE_MB = "storage_mb"
    EXPORT_REPORTS = "export_reports"
    SCANNER_TYPES = "scanner_types"
    REGIONS = "regions"

@dataclass
class UsageLimit:
    """Usage limit configuration"""
    limit_type: UsageLimitType
    limit_value: int
    current_usage: int = 0
    reset_period: str = "monthly"  # daily, weekly, monthly, yearly
    last_reset: Optional[datetime] = None

@dataclass
class LicenseConfig:
    """License configuration"""
    license_id: str
    license_type: LicenseType
    customer_id: str
    customer_name: str
    company_name: str
    email: str
    issued_date: datetime
    expiry_date: datetime
    usage_limits: List[UsageLimit]
    allowed_features: List[str]
    allowed_scanners: List[str]
    allowed_regions: List[str]
    max_concurrent_users: int
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None

class LicenseManager:
    """Comprehensive license management system"""
    
    def __init__(self, license_file: str = "license.json", encrypt_license: bool = False):
        self.license_file = license_file
        self.encrypt_license = encrypt_license
        self.current_license: Optional[LicenseConfig] = None
        self.usage_tracker: Dict[str, Any] = {}
        self.session_tracker: Dict[str, datetime] = {}
        
        # Generate or load encryption key only if encryption is enabled
        if self.encrypt_license:
            self.encryption_key = self._get_encryption_key()
        
        # Load existing license
        self.load_license()
    
    def _get_encryption_key(self) -> bytes:
        """Get or generate encryption key"""
        key_file = ".license_key"
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def _encrypt_data(self, data: str) -> str:
        """Encrypt license data"""
        if not self.encrypt_license:
            return data
        
        f = Fernet(self.encryption_key)
        encrypted = f.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt license data"""
        if not self.encrypt_license:
            return encrypted_data
        
        try:
            f = Fernet(self.encryption_key)
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            decrypted = f.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt license data: {e}")
            return ""
    
    def generate_license(self, 
                        license_type: LicenseType,
                        customer_id: str,
                        customer_name: str,
                        company_name: str,
                        email: str,
                        validity_days: int = 365,
                        custom_limits: Optional[Dict[str, int]] = None) -> LicenseConfig:
        """Generate a new license"""
        
        # Default usage limits based on license type
        default_limits = {
            LicenseType.TRIAL: {
                UsageLimitType.SCANS_PER_MONTH: 50,
                UsageLimitType.CONCURRENT_USERS: 2,
                UsageLimitType.EXPORT_REPORTS: 10,
                UsageLimitType.SCANNER_TYPES: 5
            },
            LicenseType.BASIC: {
                UsageLimitType.SCANS_PER_MONTH: 500,
                UsageLimitType.CONCURRENT_USERS: 5,
                UsageLimitType.EXPORT_REPORTS: 100,
                UsageLimitType.SCANNER_TYPES: 10
            },
            LicenseType.PROFESSIONAL: {
                UsageLimitType.SCANS_PER_MONTH: 2000,
                UsageLimitType.CONCURRENT_USERS: 15,
                UsageLimitType.EXPORT_REPORTS: 500,
                UsageLimitType.SCANNER_TYPES: 10
            },
            LicenseType.ENTERPRISE: {
                UsageLimitType.SCANS_PER_MONTH: 10000,
                UsageLimitType.CONCURRENT_USERS: 50,
                UsageLimitType.EXPORT_REPORTS: 999999,
                UsageLimitType.SCANNER_TYPES: 10
            },
            LicenseType.STANDALONE: {
                UsageLimitType.SCANS_PER_MONTH: 999999,
                UsageLimitType.CONCURRENT_USERS: 999999,
                UsageLimitType.EXPORT_REPORTS: 999999,
                UsageLimitType.SCANNER_TYPES: 10
            }
        }
        
        # Create usage limits
        limits = default_limits.get(license_type, default_limits[LicenseType.TRIAL]).copy()
        if custom_limits:
            for limit_type, limit_value in custom_limits.items():
                if isinstance(limit_type, str):
                    # Convert string to UsageLimitType enum
                    limit_type = UsageLimitType(limit_type)
                limits[limit_type] = limit_value
        
        usage_limits = []
        for limit_type, limit_value in limits.items():
            usage_limits.append(UsageLimit(
                limit_type=limit_type,
                limit_value=limit_value,
                current_usage=0,
                reset_period="monthly",
                last_reset=datetime.now()
            ))
        
        # Define features and scanners based on license type
        all_features = [
            "code_scanner", "document_scanner", "image_scanner", "database_scanner",
            "api_scanner", "ai_model_scanner", "website_scanner", "soc2_scanner",
            "dpia_scanner", "sustainability_scanner", "reporting", "audit_trail",
            "compliance_dashboard", "multi_region", "api_access", "white_label"
        ]
        
        all_scanners = [
            "code", "document", "image", "database", "api", "ai_model",
            "website", "soc2", "dpia", "sustainability"
        ]
        
        all_regions = ["Netherlands", "Germany", "France", "Belgium", "EU", "Global"]
        
        # Configure features based on license type
        if license_type == LicenseType.TRIAL:
            allowed_features = all_features[:8]  # Limited features
            allowed_scanners = all_scanners[:5]  # Limited scanners
            allowed_regions = ["Netherlands"]
            max_concurrent = 2
        elif license_type == LicenseType.BASIC:
            allowed_features = all_features[:12]
            allowed_scanners = all_scanners
            allowed_regions = ["Netherlands", "Germany"]
            max_concurrent = 5
        elif license_type == LicenseType.PROFESSIONAL:
            allowed_features = all_features[:14]
            allowed_scanners = all_scanners
            allowed_regions = all_regions[:4]
            max_concurrent = 15
        elif license_type == LicenseType.ENTERPRISE:
            allowed_features = all_features
            allowed_scanners = all_scanners
            allowed_regions = all_regions
            max_concurrent = 50
        else:  # STANDALONE
            allowed_features = all_features
            allowed_scanners = all_scanners
            allowed_regions = all_regions
            max_concurrent = 999999
        
        # Generate license
        license_config = LicenseConfig(
            license_id=str(uuid.uuid4()),
            license_type=license_type,
            customer_id=customer_id,
            customer_name=customer_name,
            company_name=company_name,
            email=email,
            issued_date=datetime.now(),
            expiry_date=datetime.now() + timedelta(days=validity_days),
            usage_limits=usage_limits,
            allowed_features=allowed_features,
            allowed_scanners=allowed_scanners,
            allowed_regions=allowed_regions,
            max_concurrent_users=max_concurrent,
            is_active=True,
            metadata={
                "generated_by": "DataGuardian Pro License Manager",
                "version": "1.0",
                "hardware_id": self._get_hardware_id(),
                "creation_timestamp": datetime.now().isoformat()
            }
        )
        
        return license_config
    
    def _get_hardware_id(self) -> str:
        """Generate hardware-specific ID for license binding"""
        import platform
        import subprocess
        
        # Get system information
        system_info = {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "machine": platform.machine(),
            "node": platform.node()
        }
        
        # Try to get MAC address
        try:
            import uuid
            mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) 
                                  for i in range(0, 8*6, 8)][::-1])
            system_info["mac"] = mac_address
        except:
            pass
        
        # Create hash of system info
        info_string = json.dumps(system_info, sort_keys=True)
        return hashlib.sha256(info_string.encode()).hexdigest()[:16]
    
    def save_license(self, license_config: LicenseConfig) -> bool:
        """Save license to file"""
        try:
            # Convert to dictionary
            license_dict = {
                "license_id": license_config.license_id,
                "license_type": license_config.license_type.value,
                "customer_id": license_config.customer_id,
                "customer_name": license_config.customer_name,
                "company_name": license_config.company_name,
                "email": license_config.email,
                "issued_date": license_config.issued_date.isoformat(),
                "expiry_date": license_config.expiry_date.isoformat(),
                "usage_limits": [
                    {
                        "limit_type": limit.limit_type.value,
                        "limit_value": limit.limit_value,
                        "current_usage": limit.current_usage,
                        "reset_period": limit.reset_period,
                        "last_reset": limit.last_reset.isoformat() if limit.last_reset else None
                    }
                    for limit in license_config.usage_limits
                ],
                "allowed_features": license_config.allowed_features,
                "allowed_scanners": license_config.allowed_scanners,
                "allowed_regions": license_config.allowed_regions,
                "max_concurrent_users": license_config.max_concurrent_users,
                "is_active": license_config.is_active,
                "metadata": license_config.metadata or {}
            }
            
            # Convert to JSON
            json_data = json.dumps(license_dict, indent=2)
            
            # Encrypt if needed
            if self.encrypt_license:
                json_data = self._encrypt_data(json_data)
            
            # Save to file
            with open(self.license_file, 'w') as f:
                f.write(json_data)
            
            self.current_license = license_config
            logger.info(f"License saved: {license_config.license_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save license: {e}")
            return False
    
    def load_license(self) -> Optional[LicenseConfig]:
        """Load license from file"""
        try:
            if not os.path.exists(self.license_file):
                return None
            
            with open(self.license_file, 'r') as f:
                json_data = f.read()
            
            # Decrypt if needed
            if self.encrypt_license:
                json_data = self._decrypt_data(json_data)
                if not json_data:
                    return None
            
            # Parse JSON
            license_dict = json.loads(json_data)
            
            # Convert usage limits
            usage_limits = []
            for limit_dict in license_dict.get("usage_limits", []):
                usage_limits.append(UsageLimit(
                    limit_type=UsageLimitType(limit_dict["limit_type"]),
                    limit_value=limit_dict["limit_value"],
                    current_usage=limit_dict["current_usage"],
                    reset_period=limit_dict["reset_period"],
                    last_reset=datetime.fromisoformat(limit_dict["last_reset"]) if limit_dict["last_reset"] else None
                ))
            
            # Create license config
            license_config = LicenseConfig(
                license_id=license_dict["license_id"],
                license_type=LicenseType(license_dict["license_type"]),
                customer_id=license_dict["customer_id"],
                customer_name=license_dict["customer_name"],
                company_name=license_dict["company_name"],
                email=license_dict["email"],
                issued_date=datetime.fromisoformat(license_dict["issued_date"]),
                expiry_date=datetime.fromisoformat(license_dict["expiry_date"]),
                usage_limits=usage_limits,
                allowed_features=license_dict["allowed_features"],
                allowed_scanners=license_dict["allowed_scanners"],
                allowed_regions=license_dict["allowed_regions"],
                max_concurrent_users=license_dict["max_concurrent_users"],
                is_active=license_dict["is_active"],
                metadata=license_dict.get("metadata", {})
            )
            
            self.current_license = license_config
            logger.info(f"License loaded: {license_config.license_id}")
            return license_config
            
        except Exception as e:
            logger.error(f"Failed to load license: {e}")
            return None
    
    def validate_license(self) -> Tuple[bool, str]:
        """Validate current license"""
        if not self.current_license:
            return False, "No license found"
        
        # Check if license is active
        if not self.current_license.is_active:
            return False, "License is deactivated"
        
        # Check expiry date
        if datetime.now() > self.current_license.expiry_date:
            return False, "License has expired"
        
        # Check hardware binding (for standalone licenses)
        if self.current_license.license_type == LicenseType.STANDALONE:
            current_hardware_id = self._get_hardware_id()
            stored_hardware_id = (self.current_license.metadata or {}).get("hardware_id")
            if stored_hardware_id and current_hardware_id != stored_hardware_id:
                return False, "License is bound to different hardware"
        
        return True, "License is valid"
    
    def check_feature_access(self, feature: str) -> bool:
        """Check if feature is allowed"""
        if not self.current_license:
            return False
        
        is_valid, _ = self.validate_license()
        if not is_valid:
            return False
        
        return feature in (self.current_license.allowed_features or [])
    
    def check_scanner_access(self, scanner_type: str) -> bool:
        """Check if scanner is allowed"""
        if not self.current_license:
            return False
        
        is_valid, _ = self.validate_license()
        if not is_valid:
            return False
        
        return scanner_type in self.current_license.allowed_scanners
    
    def check_region_access(self, region: str) -> bool:
        """Check if region is allowed"""
        if not self.current_license:
            return False
        
        is_valid, _ = self.validate_license()
        if not is_valid:
            return False
        
        return region in self.current_license.allowed_regions
    
    def check_usage_limit(self, limit_type: UsageLimitType) -> Tuple[bool, int, int]:
        """Check usage limit - returns (allowed, current, limit)"""
        if not self.current_license:
            return False, 0, 0
        
        is_valid, _ = self.validate_license()
        if not is_valid:
            return False, 0, 0
        
        # Find the limit
        for limit in self.current_license.usage_limits:
            if limit.limit_type == limit_type:
                # Check if reset is needed
                self._check_reset_usage(limit)
                return limit.current_usage < limit.limit_value, limit.current_usage, limit.limit_value
        
        return True, 0, 999999  # No limit set
    
    def _check_reset_usage(self, limit: UsageLimit):
        """Check if usage should be reset based on period"""
        if not limit.last_reset:
            limit.last_reset = datetime.now()
            return
        
        now = datetime.now()
        should_reset = False
        
        if limit.reset_period == "daily":
            should_reset = now.date() > limit.last_reset.date()
        elif limit.reset_period == "weekly":
            should_reset = now.isocalendar()[1] > limit.last_reset.isocalendar()[1]
        elif limit.reset_period == "monthly":
            should_reset = now.month > limit.last_reset.month or now.year > limit.last_reset.year
        elif limit.reset_period == "yearly":
            should_reset = now.year > limit.last_reset.year
        
        if should_reset:
            limit.current_usage = 0
            limit.last_reset = now
            if self.current_license:
                self.save_license(self.current_license)
    
    def increment_usage(self, limit_type: UsageLimitType, amount: int = 1) -> bool:
        """Increment usage counter"""
        if not self.current_license:
            return False
        
        for limit in self.current_license.usage_limits:
            if limit.limit_type == limit_type:
                limit.current_usage += amount
                if self.current_license:
                    self.save_license(self.current_license)
                return True
        
        return True  # No limit set
    
    def get_license_info(self) -> Dict[str, Any]:
        """Get license information"""
        if not self.current_license:
            return {"status": "No license"}
        
        is_valid, message = self.validate_license()
        
        usage_info = {}
        for limit in self.current_license.usage_limits:
            self._check_reset_usage(limit)
            usage_info[limit.limit_type.value] = {
                "current": limit.current_usage,
                "limit": limit.limit_value,
                "percentage": (limit.current_usage / limit.limit_value) * 100 if limit.limit_value > 0 else 0
            }
        
        return {
            "status": "Valid" if is_valid else "Invalid",
            "message": message,
            "license_id": self.current_license.license_id,
            "license_type": self.current_license.license_type.value,
            "customer_name": self.current_license.customer_name,
            "company_name": self.current_license.company_name,
            "expiry_date": self.current_license.expiry_date.isoformat(),
            "days_remaining": (self.current_license.expiry_date - datetime.now()).days,
            "allowed_features": self.current_license.allowed_features,
            "allowed_scanners": self.current_license.allowed_scanners,
            "allowed_regions": self.current_license.allowed_regions,
            "max_concurrent_users": self.current_license.max_concurrent_users,
            "usage": usage_info
        }
    
    def track_session(self, user_id: str) -> bool:
        """Track user session for concurrent user limits"""
        current_sessions = len([
            session_id for session_id, last_activity in self.session_tracker.items()
            if datetime.now() - last_activity < timedelta(hours=1)  # 1 hour timeout
        ])
        
        if self.current_license and current_sessions >= self.current_license.max_concurrent_users:
            return False
        
        self.session_tracker[user_id] = datetime.now()
        return True
    
    def cleanup_sessions(self):
        """Clean up expired sessions"""
        cutoff_time = datetime.now() - timedelta(hours=1)
        expired_sessions = [
            session_id for session_id, last_activity in self.session_tracker.items()
            if last_activity < cutoff_time
        ]
        
        for session_id in expired_sessions:
            del self.session_tracker[session_id]

# Global license manager instance
license_manager = LicenseManager()

# Convenience functions
def check_license() -> Tuple[bool, str]:
    """Check if license is valid"""
    return license_manager.validate_license()

def check_feature(feature: str) -> bool:
    """Check if feature is allowed"""
    return license_manager.check_feature_access(feature)

def check_scanner(scanner_type: str) -> bool:
    """Check if scanner is allowed"""
    return license_manager.check_scanner_access(scanner_type)

def check_region(region: str) -> bool:
    """Check if region is allowed"""
    return license_manager.check_region_access(region)

def check_usage(limit_type: UsageLimitType) -> Tuple[bool, int, int]:
    """Check usage limit"""
    return license_manager.check_usage_limit(limit_type)

def increment_usage(limit_type: UsageLimitType, amount: int = 1) -> bool:
    """Increment usage counter"""
    return license_manager.increment_usage(limit_type, amount)

def get_license_info() -> Dict[str, Any]:
    """Get license information"""
    return license_manager.get_license_info()

def track_user_session(user_id: str) -> bool:
    """Track user session"""
    return license_manager.track_session(user_id)