"""
Unified Translation System for DataGuardian Pro
Standardizes translation handling across UI and report generation.
"""

import streamlit as st
from typing import Dict, Optional, Any
import logging
from utils.i18n import get_text

# Translation cache for performance optimization
_translation_cache: Dict[str, str] = {}

class UnifiedTranslation:
    """Unified translation handler for consistent translation across the application."""
    
    def __init__(self):
        self.current_language = 'en'
        self._update_language()
    
    def _update_language(self):
        """Update current language from session state."""
        self.current_language = st.session_state.get('language', 'en')
    
    def get(self, key: str, default: str = "", context: str = "") -> str:
        """
        Get translated text with caching and context support.
        
        Args:
            key: Translation key (e.g., 'report.title')
            default: Default text if translation not found
            context: Optional context for specialized translations
            
        Returns:
            Translated text
        """
        self._update_language()
        
        # Create cache key
        cache_key = f"{self.current_language}:{context}:{key}"
        
        # Check cache first
        if cache_key in _translation_cache:
            return _translation_cache[cache_key]
        
        # Get translation
        if self.current_language == 'nl':
            # Add context prefix if provided
            full_key = f"{context}.{key}" if context else key
            translated_text = get_text(full_key, default)
        else:
            translated_text = default
        
        # Cache the result
        _translation_cache[cache_key] = translated_text
        
        return translated_text
    
    def clear_cache(self):
        """Clear the translation cache."""
        global _translation_cache
        _translation_cache.clear()
    
    # Convenience methods for different contexts
    def ui(self, key: str, default: str = "") -> str:
        """Get UI translation."""
        return self.get(key, default, "")
    
    def report(self, key: str, default: str = "") -> str:
        """Get report translation."""
        return self.get(key, default, "report")
    
    def technical(self, key: str, default: str = "") -> str:
        """Get technical terms translation."""
        return self.get(key, default, "technical_terms")
    
    def scanner(self, key: str, default: str = "") -> str:
        """Get scanner-specific translation."""
        return self.get(key, default, "scan")
    
    def dpia(self, key: str, default: str = "") -> str:
        """Get DPIA-specific translation."""
        return self.get(key, default, "dpia")
    
    def ai_act(self, key: str, default: str = "") -> str:
        """Get AI Act translation."""
        return self.get(key, default, "ai_act")

# Global translation instance
_translator = None

def get_translator() -> UnifiedTranslation:
    """Get the global translator instance."""
    global _translator
    if _translator is None:
        _translator = UnifiedTranslation()
    return _translator

def t(key: str, default: str = "", context: str = "") -> str:
    """
    Unified translation function for use across the application.
    
    Args:
        key: Translation key
        default: Default text
        context: Translation context (report, ui, technical, etc.)
        
    Returns:
        Translated text
    """
    translator = get_translator()
    return translator.get(key, default, context)

# Convenience functions for specific contexts
def t_ui(key: str, default: str = "") -> str:
    """UI translation shorthand."""
    return t(key, default, "")

def t_report(key: str, default: str = "") -> str:
    """Report translation shorthand.""" 
    return t(key, default, "report")

def t_technical(key: str, default: str = "") -> str:
    """Technical terms translation shorthand."""
    return t(key, default, "technical_terms")

def t_scanner(key: str, default: str = "") -> str:
    """Scanner translation shorthand."""
    return t(key, default, "scan")

def clear_translation_cache():
    """Clear the global translation cache."""
    translator = get_translator()
    translator.clear_cache()

# Translation validation for development
def validate_translation_keys(required_keys: list, context: str = "") -> Dict[str, bool]:
    """
    Validate that translation keys exist.
    
    Args:
        required_keys: List of keys to validate
        context: Translation context
        
    Returns:
        Dictionary mapping keys to availability status
    """
    translator = get_translator()
    validation_results = {}
    
    for key in required_keys:
        # Check if translation exists by comparing with default
        translated = translator.get(key, f"__MISSING__{key}", context)
        validation_results[key] = not translated.startswith("__MISSING__")
    
    return validation_results

# Report-specific translation mappings
REPORT_TRANSLATION_KEYS = {
    # Header and basic info
    'title': 'DataGuardian Pro Rapport',
    'comprehensive_report': 'Uitgebreid Rapport',
    'scan_type': 'Scantype',
    'scan_id': 'Scan ID',
    'generated_on': 'Gegenereerd op',
    'region': 'Regio',
    
    # Executive summary
    'executive_summary': 'Managementsamenvatting',
    'files_scanned': 'Bestanden gescand',
    'pages_scanned': 'Pagina\'s gescand',
    'total_findings': 'Totaal bevindingen',
    'lines_analyzed': 'Regels geanalyseerd',
    'content_analysis': 'Inhoudsanalyse',
    'critical': 'Kritiek',
    'critical_issues': 'Kritieke problemen',
    
    # Findings
    'detailed_findings': 'Gedetailleerde bevindingen',
    'no_issues_found': 'Geen problemen gevonden in de analyse',
    'type': 'Type',
    'severity': 'Ernst',
    'file_resource': 'Bestand/Resource',
    'location_details': 'Locatiedetails',
    'description_column': 'Beschrijving',
    'impact': 'Impact',
    'action_required': 'Actie vereist',
    
    # Footer
    'generated_by': 'Gegenereerd door',
    'dataGuardian_pro': 'DataGuardian Pro',
    'privacy_compliance_platform': 'Enterprise Privacy & Duurzaamheid Nalevingsplatform',
    
    # Risk levels and categories
    'high_privacy_risk': 'Hoog privacyrisico',
    'medium_privacy_risk': 'Gemiddeld privacyrisico',
    'low_privacy_risk': 'Laag privacyrisico',
    'security_vulnerability': 'Beveiligingskwetsbaarheid',
    'compliance_issue': 'Nalevingsprobleem',
    'data_breach_risk': 'Datalekrisico',
    
    # Scanner-specific terms
    'gdpr_compliance_report': 'GDPR Nalevingsrapport',
    'website_privacy_report': 'Website Privacyrapport',
    'code_security_report': 'Code Beveiligingsrapport',
    'ai_model_compliance': 'AI Model Naleving',
    'sustainability_report': 'Duurzaamheidsrapport',
    'dpia_assessment': 'DPIA Beoordeling'
}

def add_missing_translation_keys():
    """Add missing report translation keys to the Dutch translation file."""
    try:
        import json
        
        # Load existing Dutch translations
        with open('translations/nl.json', 'r', encoding='utf-8') as f:
            nl_translations = json.load(f)
        
        # Ensure report section exists
        if 'report' not in nl_translations:
            nl_translations['report'] = {}
        
        # Add missing keys
        keys_added = 0
        for key, value in REPORT_TRANSLATION_KEYS.items():
            if key not in nl_translations['report']:
                nl_translations['report'][key] = value
                keys_added += 1
        
        # Save updated translations
        if keys_added > 0:
            with open('translations/nl.json', 'w', encoding='utf-8') as f:
                json.dump(nl_translations, f, ensure_ascii=False, indent=2)
            
            logging.info(f"Added {keys_added} missing translation keys to nl.json")
            
            # Clear cache to force reload
            clear_translation_cache()
            
        return keys_added
        
    except Exception as e:
        logging.error(f"Failed to add missing translation keys: {e}")
        return 0

# Initialize missing keys on import
add_missing_translation_keys()