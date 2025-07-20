"""
Settings Manager for DataGuardian Pro
Comprehensive user preferences, API configurations, and compliance settings management
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from cryptography.fernet import Fernet
import os
import streamlit as st

logger = logging.getLogger(__name__)

class SettingsManager:
    """Centralized settings management system"""
    
    def __init__(self):
        self.db = self._get_database_connection()
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        self._initialize_settings_table()
    
    def _get_database_connection(self):
        """Get database connection for settings storage"""
        try:
            from utils.database_manager import DatabaseManager
            return DatabaseManager()
        except Exception as e:
            logger.warning(f"Database connection failed, using session storage: {e}")
            return None
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for sensitive settings"""
        key_file = ".settings_key"
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def _initialize_settings_table(self):
        """Initialize database table for settings storage"""
        if not self.db:
            return
            
        try:
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS user_settings (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    category VARCHAR(100) NOT NULL,
                    setting_key VARCHAR(255) NOT NULL,
                    setting_value TEXT,
                    encrypted BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, category, setting_key)
                )
            """)
            logger.info("Settings table initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize settings table: {e}")
    
    def get_user_settings(self, user_id: str, category: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve user settings from database or session"""
        if not self.db:
            # Fallback to session storage
            session_key = f"settings_{user_id}"
            if category:
                session_key = f"settings_{user_id}_{category}"
            return st.session_state.get(session_key, {})
        
        try:
            if category:
                query = """
                    SELECT setting_key, setting_value, encrypted
                    FROM user_settings 
                    WHERE user_id = %s AND category = %s
                """
                results = self.db.fetch_query(query, (user_id, category))
            else:
                query = """
                    SELECT category, setting_key, setting_value, encrypted
                    FROM user_settings 
                    WHERE user_id = %s
                """
                results = self.db.fetch_query(query, (user_id,))
            
            settings = {}
            for row in results:
                if category:
                    key, value, encrypted = row
                    if encrypted:
                        try:
                            value = self.cipher.decrypt(value.encode()).decode()
                        except Exception:
                            logger.warning(f"Failed to decrypt setting {key}")
                            continue
                    settings[key] = json.loads(value) if value.startswith('{') or value.startswith('[') else value
                else:
                    cat, key, value, encrypted = row
                    if cat not in settings:
                        settings[cat] = {}
                    if encrypted:
                        try:
                            value = self.cipher.decrypt(value.encode()).decode()
                        except Exception:
                            continue
                    settings[cat][key] = json.loads(value) if value.startswith('{') or value.startswith('[') else value
            
            return settings
            
        except Exception as e:
            logger.error(f"Error retrieving user settings: {e}")
            return {}
    
    def save_user_setting(self, user_id: str, category: str, setting_key: str, 
                         setting_value: Any, encrypted: bool = False) -> bool:
        """Save individual user setting"""
        if not self.db:
            # Fallback to session storage
            session_key = f"settings_{user_id}_{category}"
            if session_key not in st.session_state:
                st.session_state[session_key] = {}
            st.session_state[session_key][setting_key] = setting_value
            return True
        
        try:
            # Serialize complex objects
            if isinstance(setting_value, (dict, list)):
                value_str = json.dumps(setting_value)
            else:
                value_str = str(setting_value)
            
            # Encrypt sensitive data
            if encrypted:
                value_str = self.cipher.encrypt(value_str.encode()).decode()
            
            query = """
                INSERT INTO user_settings (user_id, category, setting_key, setting_value, encrypted)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (user_id, category, setting_key) 
                DO UPDATE SET 
                    setting_value = EXCLUDED.setting_value,
                    encrypted = EXCLUDED.encrypted,
                    updated_at = CURRENT_TIMESTAMP
            """
            
            self.db.execute_query(query, (user_id, category, setting_key, value_str, encrypted))
            logger.info(f"Saved setting {category}.{setting_key} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving user setting: {e}")
            return False
    
    def get_default_settings(self) -> Dict[str, Dict[str, Any]]:
        """Get default settings structure"""
        return {
            "profile": {
                "language": "en",
                "theme": "light",
                "region": "Netherlands",
                "timezone": "Europe/Amsterdam",
                "email_notifications": True,
                "desktop_notifications": False
            },
            "api_keys": {
                "openai_api_key": "",
                "stripe_secret_key": "",
                "stripe_publishable_key": "",
                "webhook_endpoints": []
            },
            "compliance": {
                "gdpr_region": "Netherlands",
                "data_residency": "EU",
                "retention_days": 365,
                "audit_logging": True,
                "breach_notifications": True,
                "dpo_contact": "",
                "privacy_policy_url": ""
            },
            "scanners": {
                "default_scanner": "code",
                "max_concurrent": 3,
                "timeout_seconds": 300,
                "file_size_limit_mb": 100,
                "supported_formats": ["py", "js", "java", "cs", "php", "rb"],
                "scan_depth": "deep",
                "custom_patterns": []
            },
            "reports": {
                "default_format": "html",
                "auto_download": True,
                "email_delivery": False,
                "include_remediation": True,
                "template": "professional",
                "language": "en"
            },
            "security": {
                "session_timeout_minutes": 60,
                "two_factor_enabled": False,
                "login_alerts": True,
                "password_expiry_days": 90,
                "audit_log_retention": 730,
                "ip_restrictions": []
            }
        }
    
    def initialize_user_settings(self, user_id: str) -> bool:
        """Initialize user settings with defaults"""
        try:
            defaults = self.get_default_settings()
            
            for category, settings in defaults.items():
                for key, value in settings.items():
                    # Only set if not already exists
                    existing = self.get_user_settings(user_id, category)
                    if key not in existing:
                        # Determine if setting should be encrypted
                        encrypted = category == "api_keys" and "key" in key.lower()
                        self.save_user_setting(user_id, category, key, value, encrypted)
            
            logger.info(f"Initialized settings for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing user settings: {e}")
            return False
    
    def validate_api_key(self, api_key: str, service: str) -> Dict[str, Any]:
        """Validate API key for specific service"""
        validation_result = {
            "valid": False,
            "message": "",
            "details": {}
        }
        
        try:
            if service == "openai":
                if api_key.startswith("sk-"):
                    # Test OpenAI API connection
                    import openai
                    client = openai.OpenAI(api_key=api_key)
                    response = client.models.list()
                    validation_result["valid"] = True
                    validation_result["message"] = "OpenAI API key is valid"
                    validation_result["details"]["models_available"] = len(response.data)
                else:
                    validation_result["message"] = "Invalid OpenAI API key format"
            
            elif service == "stripe":
                if api_key.startswith("sk_"):
                    # Test Stripe API connection
                    import stripe
                    stripe.api_key = api_key
                    account = stripe.Account.retrieve()
                    validation_result["valid"] = True
                    validation_result["message"] = "Stripe API key is valid"
                    validation_result["details"]["account_id"] = account.id
                else:
                    validation_result["message"] = "Invalid Stripe API key format"
            
            else:
                validation_result["message"] = f"Unknown service: {service}"
                
        except Exception as e:
            validation_result["message"] = f"API validation failed: {str(e)}"
            
        return validation_result
    
    def export_settings(self, user_id: str, include_sensitive: bool = False) -> Dict[str, Any]:
        """Export user settings for backup or migration"""
        try:
            settings = self.get_user_settings(user_id)
            
            if not include_sensitive and "api_keys" in settings:
                # Mask sensitive values
                for key in settings["api_keys"]:
                    if isinstance(settings["api_keys"][key], str) and settings["api_keys"][key]:
                        settings["api_keys"][key] = "***MASKED***"
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "settings": settings,
                "version": "1.0"
            }
            
            return export_data
            
        except Exception as e:
            logger.error(f"Error exporting settings: {e}")
            return {}
    
    def import_settings(self, user_id: str, import_data: Dict[str, Any]) -> bool:
        """Import user settings from backup"""
        try:
            if "settings" not in import_data:
                logger.error("Invalid import data format")
                return False
            
            settings = import_data["settings"]
            
            for category, category_settings in settings.items():
                for key, value in category_settings.items():
                    # Skip masked values
                    if value == "***MASKED***":
                        continue
                    
                    encrypted = category == "api_keys" and "key" in key.lower()
                    self.save_user_setting(user_id, category, key, value, encrypted)
            
            logger.info(f"Successfully imported settings for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error importing settings: {e}")
            return False
    
    def get_audit_log(self, user_id: str, category: Optional[str] = None, 
                     days: int = 30) -> List[Dict[str, Any]]:
        """Get settings change audit log"""
        if not self.db:
            return []
            
        try:
            query = """
                SELECT category, setting_key, created_at, updated_at
                FROM user_settings 
                WHERE user_id = %s 
                AND updated_at >= CURRENT_TIMESTAMP - INTERVAL '%s days'
            """
            params = [user_id, days]
            
            if category:
                query += " AND category = %s"
                params.append(category)
            
            query += " ORDER BY updated_at DESC"
            
            results = self.db.fetch_query(query, params)
            
            audit_log = []
            for row in results:
                audit_log.append({
                    "category": row[0],
                    "setting_key": row[1],
                    "created_at": row[2].isoformat(),
                    "updated_at": row[3].isoformat()
                })
            
            return audit_log
            
        except Exception as e:
            logger.error(f"Error retrieving audit log: {e}")
            return []