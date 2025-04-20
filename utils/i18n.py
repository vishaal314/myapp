"""
Internationalization module for DataGuardian.
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
    Enhanced with redundant storage for robustness.
    
    Args:
        lang_code: The language code (e.g., 'en', 'nl')
    """
    global _current_language
    
    if not lang_code:
        # Priority chain for finding language
        if '_persistent_language' in st.session_state:
            lang_code = st.session_state['_persistent_language']
        elif 'language' in st.session_state:
            lang_code = st.session_state['language']
        elif 'pre_login_language' in st.session_state:
            lang_code = st.session_state['pre_login_language']
        elif 'backup_language' in st.session_state:
            lang_code = st.session_state['backup_language']
        else:
            lang_code = 'en'  # Default fallback
    
    # Ensure lang_code is a string and valid
    lang_code_str = str(lang_code)
    
    # Validate language is supported
    if lang_code_str not in LANGUAGES:
        print(f"SET_LANGUAGE - Invalid language: {lang_code_str}, falling back to 'en'")
        lang_code_str = 'en'
    
    # Log the set operation for debugging
    print(f"SET_LANGUAGE - Setting language to: {lang_code_str}")
    
    # Update module-level global variable
    _current_language = lang_code_str
    
    # Load translations for the language
    load_translations(lang_code_str)
    
    # Update ALL session state locations for maximum redundancy
    st.session_state['language'] = lang_code_str
    st.session_state['_persistent_language'] = lang_code_str
    st.session_state['pre_login_language'] = lang_code_str
    st.session_state['backup_language'] = lang_code_str

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
    
    # Split the key into parts (e.g., 'app.title' -> ['app', 'title'])
    parts = key.split('.')
    
    # Get the translation dictionary for current language
    lang_dict = _translations.get(_current_language, {})
    
    # Navigate through nested dictionaries based on key parts
    text = None
    current_dict = lang_dict
    for i, part in enumerate(parts):
        # If we're at the last part, get the value
        if i == len(parts) - 1:
            text = current_dict.get(part)
            break
            
        # Navigate to next level if it exists
        if part in current_dict and isinstance(current_dict[part], dict):
            current_dict = current_dict[part]
        else:
            # Break if we can't navigate further
            break
    
    # If not found, try English as fallback
    if text is None and _current_language != 'en':
        if 'en' not in _translations:
            load_translations('en')
            
        # Try to find translation in English
        current_dict = _translations.get('en', {})
        for i, part in enumerate(parts):
            # If we're at the last part, get the value
            if i == len(parts) - 1:
                text = current_dict.get(part)
                break
                
            # Navigate to next level if it exists
            if part in current_dict and isinstance(current_dict[part], dict):
                current_dict = current_dict[part]
            else:
                # Break if we can't navigate further
                break
    
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
    Now with enhanced refresh mechanism to ensure all translations are applied.
    
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
    
    # Define callback for language change - with enhanced persistence
    def on_language_change():
        new_lang = st.session_state[selector_key]
        if new_lang != current_lang:
            print(f"LANGUAGE CHANGE: {current_lang} -> {new_lang}")
            
            # Store language in ALL possible locations for redundant persistence
            st.session_state['language'] = new_lang
            st.session_state['_persistent_language'] = new_lang
            st.session_state['pre_login_language'] = new_lang
            st.session_state['backup_language'] = new_lang
            st.session_state['force_language_after_login'] = new_lang
            
            # Also log the language change for debugging
            print(f"LANGUAGE SELECTOR - Changed language to: {new_lang}")
            
            # Set reload translations flag to force full reinitialization
            st.session_state['reload_translations'] = True
            
            # Reset translations cache completely
            global _translations
            _translations = {}
            
            # Load translations for new language immediately
            set_language(new_lang)
            
            # Force complete reinitialization
            initialize()
            
            # Force rerun of app to update all UI elements
            st.rerun()  # Force immediate rerun
    
    # Create a compact container for the language selector
    with st.container():
        # Use the selectbox with on_change parameter to trigger immediate update
        selected_lang = st.selectbox(
            "🌐 Language / Taal",
            options=list(LANGUAGES.keys()),
            format_func=lambda x: LANGUAGES.get(x, x),
            index=list(LANGUAGES.keys()).index(current_lang) if current_lang in LANGUAGES else 0,
            key=selector_key,
            on_change=on_language_change
        )
        
        # Add a secondary way to change language with a button for more reliable updates
        cols = st.columns([3, 1])
        with cols[1]:
            if selected_lang != current_lang:
                if st.button("✓ Apply", key=f"apply_lang_{key_suffix}"):
                    print(f"APPLY BUTTON - Language change: {current_lang} -> {selected_lang}")
                    
                    # Store language redundantly in ALL possible locations
                    st.session_state['language'] = selected_lang
                    st.session_state['_persistent_language'] = selected_lang
                    st.session_state['pre_login_language'] = selected_lang
                    st.session_state['backup_language'] = selected_lang
                    st.session_state['force_language_after_login'] = selected_lang
                    
                    # Set reload translations flag to force full reinitialization
                    st.session_state['reload_translations'] = True
                    
                    # Clear existing translations completely
                    global _translations
                    _translations = {}
                    
                    # Load translations directly
                    set_language(selected_lang)
                    
                    # Force full reinitialization
                    initialize()
                    
                    # Force rerun
                    st.rerun()

# Initialize translations - COMPLETELY FIXED VERSION
def initialize() -> None:
    """
    Initialize the internationalization module.
    Load translations for the current language.
    Handles both initial app load and language switching.
    """
    global _translations, _current_language
    
    # LANGUAGE PRIORITY CHAIN:
    # 1. force_language_after_login (highest - set during auth)
    # 2. _persistent_language (persistent across all state changes)
    # 3. language (standard location)
    # 4. pre_login_language (stored before login)
    # 5. backup_language (extra backup)
    # 6. 'en' (default fallback)
    
    # Check all possible storage locations in priority order
    if 'force_language_after_login' in st.session_state:
        current_lang = st.session_state.pop('force_language_after_login')
        print(f"INIT - Force Language Available: {current_lang}")
    elif '_persistent_language' in st.session_state:
        current_lang = st.session_state.get('_persistent_language')
        print(f"INIT - Using _persistent_language: {current_lang}")
    elif 'language' in st.session_state:
        current_lang = st.session_state.get('language')
        print(f"INIT - Using language: {current_lang}")
    elif 'pre_login_language' in st.session_state:
        current_lang = st.session_state.get('pre_login_language')
        print(f"INIT - Using pre_login_language: {current_lang}")
    elif 'backup_language' in st.session_state:
        current_lang = st.session_state.get('backup_language')
        print(f"INIT - Using backup_language: {current_lang}")
    else:
        # Ultimate fallback
        current_lang = 'en'
        print(f"INIT - No language found, using default: {current_lang}")
    
    # Validate the language is supported
    if current_lang not in LANGUAGES:
        print(f"INIT - Invalid language: {current_lang}, falling back to 'en'")
        current_lang = 'en'
    
    # Apply language to ALL storage locations for redundancy
    st.session_state['language'] = current_lang
    st.session_state['_persistent_language'] = current_lang
    st.session_state['pre_login_language'] = current_lang
    st.session_state['backup_language'] = current_lang
    
    # Completely reset all translations to force reload
    # This is critical for proper translation after auth changes
    _translations = {}  
    
    # Set the current language module variable
    _current_language = current_lang
    
    # Load primary language translations
    load_translations(current_lang)
    
    # Always load English as fallback for missing keys
    if current_lang != 'en':
        load_translations('en')
    
    # Log initialization for debugging
    print(f"INIT - Successfully initialized translations for: {current_lang}")