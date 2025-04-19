"""
Internationalization (i18n) utility for DataGuardian Pro.
Supports multiple languages for the application.
"""
import json
import os
from typing import Dict, Any, Optional

# Available languages
LANGUAGES = {
    'en': 'English',
    'nl': 'Nederlands'
}

# Default language
DEFAULT_LANGUAGE = 'en'

# Path to translations directory
TRANSLATIONS_DIR = 'translations'

# Cached translations
_translations: Dict[str, Dict[str, str]] = {}

def load_translations(lang_code: str) -> Dict[str, str]:
    """
    Load translations for the specified language code.
    
    Args:
        lang_code: The language code to load
        
    Returns:
        Dictionary of translations for the language
    """
    global _translations
    
    # Return from cache if already loaded
    if lang_code in _translations:
        return _translations[lang_code]
    
    # Ensure translations directory exists
    os.makedirs(TRANSLATIONS_DIR, exist_ok=True)
    
    # Path to translation file
    file_path = os.path.join(TRANSLATIONS_DIR, f"{lang_code}.json")
    
    # Create default file if it doesn't exist
    if not os.path.exists(file_path):
        if lang_code == DEFAULT_LANGUAGE:
            # Create an empty English file as the base
            with open(file_path, 'w') as f:
                json.dump({}, f, indent=2)
            _translations[lang_code] = {}
            return {}
        else:
            # For non-default languages, return the default language translations
            return load_translations(DEFAULT_LANGUAGE)
    
    # Load translations from file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            translations = json.load(f)
            _translations[lang_code] = translations
            return translations
    except Exception as e:
        print(f"Error loading translations for {lang_code}: {str(e)}")
        # Fall back to default language
        if lang_code != DEFAULT_LANGUAGE:
            return load_translations(DEFAULT_LANGUAGE)
        else:
            return {}

def save_translations(lang_code: str, translations: Dict[str, str]) -> None:
    """
    Save translations for the specified language code.
    
    Args:
        lang_code: The language code to save
        translations: Dictionary of translations to save
    """
    # Ensure translations directory exists
    os.makedirs(TRANSLATIONS_DIR, exist_ok=True)
    
    # Path to translation file
    file_path = os.path.join(TRANSLATIONS_DIR, f"{lang_code}.json")
    
    # Save translations to file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(translations, f, indent=2, ensure_ascii=False)
        # Update cache
        _translations[lang_code] = translations
    except Exception as e:
        print(f"Error saving translations for {lang_code}: {str(e)}")

def get_text(key: str, lang_code: Optional[str] = None) -> str:
    """
    Get translated text for a key in the specified language.
    
    Args:
        key: The text key to translate
        lang_code: The language code (defaults to current language)
        
    Returns:
        Translated text or the key itself if not found
    """
    if lang_code is None:
        import streamlit as st
        # Get language from session state or default
        lang_code = st.session_state.get('language', DEFAULT_LANGUAGE)
    
    # Get translations for language
    translations = load_translations(lang_code)
    
    # Return translation or key if not found
    if key in translations:
        return translations[key]
    else:
        # If not found in selected language, try default language
        if lang_code != DEFAULT_LANGUAGE:
            default_translations = load_translations(DEFAULT_LANGUAGE)
            if key in default_translations:
                return default_translations[key]
        
        # Add missing key to default language
        if lang_code == DEFAULT_LANGUAGE:
            default_translations = load_translations(DEFAULT_LANGUAGE)
            if key not in default_translations:
                default_translations[key] = key
                save_translations(DEFAULT_LANGUAGE, default_translations)
        
        return key

def set_language(lang_code: str) -> None:
    """
    Set the current language for the application.
    
    Args:
        lang_code: The language code to set
    """
    import streamlit as st
    
    if lang_code in LANGUAGES:
        st.session_state['language'] = lang_code

# Alias for get_text for shorter usage
_ = get_text