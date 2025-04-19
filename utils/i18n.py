"""
Internationalization module for DataGuardian Pro.
Provides multilingual support for the application UI.
"""
import os
import json
from typing import Dict, Any, Optional
import streamlit as st

# Available languages
LANGUAGES = {
    'en': 'English',
    'nl': 'Nederlands'
}

# Global variable to hold translations
_translations = {}
_current_language = 'en'

def load_translations(lang_code: str) -> Dict[str, Any]:
    """
    Load translation strings for the specified language.
    
    Args:
        lang_code: The language code (e.g., 'en', 'nl')
        
    Returns:
        Dictionary of translation strings
    """
    global _translations, _current_language
    
    # Ensure lang_code is a string
    lang_code = str(lang_code) if lang_code is not None else 'en'
    
    # Default to English if the language is not supported
    if lang_code not in LANGUAGES:
        lang_code = 'en'
    
    # Set current language
    _current_language = lang_code
    
    # If translations already loaded, return them
    if lang_code in _translations:
        return _translations[lang_code]
    
    # Define path to translation file
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    translation_file = os.path.join(base_dir, 'translations', f'{lang_code}.json')
    
    # Check if translation file exists
    if not os.path.exists(translation_file):
        # Create empty translation file for language
        if lang_code != 'en':
            # First load English as fallback
            english_file = os.path.join(base_dir, 'translations', 'en.json')
            if os.path.exists(english_file):
                with open(english_file, 'r', encoding='utf-8') as f:
                    _translations['en'] = json.load(f)
            else:
                _translations['en'] = {}
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(translation_file), exist_ok=True)
            
            # Create empty file with same keys as English
            with open(translation_file, 'w', encoding='utf-8') as f:
                json.dump(_translations['en'], f, ensure_ascii=False, indent=2)
            
            # Return English translations as fallback
            return _translations['en']
        else:
            # Create empty English translation file
            os.makedirs(os.path.dirname(translation_file), exist_ok=True)
            with open(translation_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            _translations[lang_code] = {}
            return {}
    
    # Load translations from file
    try:
        with open(translation_file, 'r', encoding='utf-8') as f:
            _translations[lang_code] = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        _translations[lang_code] = {}
    
    return _translations[lang_code]

def set_language(lang_code: Optional[str] = None) -> None:
    """
    Set the current language for the application.
    
    Args:
        lang_code: The language code (e.g., 'en', 'nl')
    """
    if not lang_code:
        # Get language from session state if available
        lang_code = st.session_state.get('language', 'en')
    
    # Ensure lang_code is a string
    lang_code_str = str(lang_code)
    
    # Load translations for the language
    load_translations(lang_code_str)
    
    # Update session state
    st.session_state.language = lang_code_str

def get_text(key: str, default: Optional[str] = None) -> str:
    """
    Get the translated text for a key.
    
    Args:
        key: The translation key (e.g., 'app.title')
        default: Default text if translation is not found
        
    Returns:
        Translated text
    """
    global _translations, _current_language
    
    # If translations are not loaded, load them
    if _current_language not in _translations:
        load_translations(_current_language)
    
    # Get translation for key
    text = _translations.get(_current_language, {}).get(key)
    
    # If not found, try English as fallback
    if text is None and _current_language != 'en':
        if 'en' not in _translations:
            load_translations('en')
        text = _translations.get('en', {}).get(key)
    
    # If still not found, use default or key itself
    if text is None:
        text = default if default is not None else key
    
    return text

# Shorthand function for get_text
def _(key: str, default: Optional[str] = None) -> str:
    """
    Shorthand function for get_text.
    
    Args:
        key: The translation key (e.g., 'app.title')
        default: Default text if translation is not found
        
    Returns:
        Translated text
    """
    return get_text(key, default)

def language_selector(key_suffix: str = None) -> None:
    """
    Display a language selector in the Streamlit UI.
    Updates the language when changed immediately.
    
    Args:
        key_suffix: A suffix to ensure unique keys for multiple language selectors
                   If None, a random suffix will be generated
    """
    import uuid
    # Create a unique key if none provided
    if key_suffix is None:
        key_suffix = str(uuid.uuid4())[:8]
        
    # Create a selectbox for language selection with guaranteed unique key
    current_lang = st.session_state.get('language', 'en')
    selector_key = f"lang_selector_{key_suffix}"
    
    # Define callback for language change
    def on_language_change():
        new_lang = st.session_state[selector_key]
        if new_lang != current_lang:
            st.session_state.language = new_lang
            set_language(new_lang)
            st.rerun()
    
    # Use the selectbox with on_change parameter to trigger immediate update
    selected_lang = st.selectbox(
        "🌐 Language / Taal",
        options=list(LANGUAGES.keys()),
        format_func=lambda x: LANGUAGES.get(x, x),
        index=list(LANGUAGES.keys()).index(current_lang) if current_lang in LANGUAGES else 0,
        key=selector_key,
        on_change=on_language_change
    )

# Initialize translations
def initialize() -> None:
    """
    Initialize the internationalization module.
    Load translations for the current language.
    """
    current_lang = st.session_state.get('language', 'en')
    set_language(current_lang)