"""
Interactive language switcher with country flag animations for DataGuardian.
Provides a visually appealing way to switch between supported languages.
"""
import streamlit as st
import base64
from typing import Dict, Any, Optional
import uuid
import json
import os
from utils.i18n import set_language, LANGUAGES

# Flag emoji codes for supported languages
FLAG_EMOJIS = {
    'en': '🇬🇧',
    'nl': '🇳🇱',
    # Add more languages as they become supported
    'fr': '🇫🇷',
    'de': '🇩🇪',
    'es': '🇪🇸',
    'it': '🇮🇹',
    'pt': '🇵🇹',
}

# SVG flag base64 data (small simplified versions for better performance)
FLAG_SVG = {
    'en': """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 60 30">
        <clipPath id="a"><path d="M0 0v30h60V0z"/></clipPath>
        <clipPath id="b"><path d="M30 15h30v15zv15H0zH0V0zV0h30z"/></clipPath>
        <g clip-path="url(#a)">
            <path d="M0 0v30h60V0z" fill="#012169"/>
            <path d="M0 0l60 30m0-30L0 30" stroke="#fff" stroke-width="6"/>
            <path d="M0 0l60 30m0-30L0 30" clip-path="url(#b)" stroke="#C8102E" stroke-width="4"/>
            <path d="M30 0v30M0 15h60" stroke="#fff" stroke-width="10"/>
            <path d="M30 0v30M0 15h60" stroke="#C8102E" stroke-width="6"/>
        </g>
    </svg>
    """,
    'nl': """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 9 6">
        <rect fill="#21468B" width="9" height="6"/>
        <rect fill="#FFF" width="9" height="4"/>
        <rect fill="#AE1C28" width="9" height="2"/>
    </svg>
    """,
    # Add more flags as languages are supported
}

# Animation CSS for language flags
FLAG_ANIMATION_CSS = """
<style>
    @keyframes flag-wave {
        0% { transform: rotate(0deg); }
        10% { transform: rotate(-3deg); }
        20% { transform: rotate(3deg); }
        30% { transform: rotate(-3deg); }
        40% { transform: rotate(3deg); }
        50% { transform: rotate(0deg); }
        100% { transform: rotate(0deg); }
    }
    
    .flag-icon {
        display: inline-block;
        width: 24px; 
        height: 24px;
        margin-right: 8px;
        vertical-align: middle;
        transition: transform 0.3s ease;
    }
    
    .flag-icon:hover {
        animation: flag-wave 2s ease;
    }
    
    .lang-button {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 8px 12px;
        margin: 5px;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        min-width: 120px;
    }
    
    .lang-button:hover {
        background-color: #e9ecef;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .lang-button.selected {
        background-color: #4285F4;
        color: white;
        border-color: #4285F4;
    }
    
    .lang-button.selected:hover {
        background-color: #3367D6;
    }
    
    .lang-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        margin-bottom: 15px;
    }
    
    .lang-name {
        margin-left: 5px;
        font-weight: 500;
    }
    
    .apply-button {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        display: block;
        margin: 10px auto;
    }
    
    .apply-button:hover {
        background-color: #45a049;
        transform: scale(1.05);
    }
    
    .apply-button:disabled {
        background-color: #cccccc;
        cursor: not-allowed;
        transform: none;
    }
    
    .language-title {
        text-align: center;
        font-size: 16px;
        font-weight: 500;
        margin-bottom: 10px;
        color: #333;
    }
    
    .language-animation-container {
        overflow: hidden;
        margin-bottom: 15px;
    }
    
    @keyframes slide-in {
        0% { transform: translateY(-20px); opacity: 0; }
        100% { transform: translateY(0); opacity: 1; }
    }
    
    .animated-entry {
        animation: slide-in 0.5s ease forwards;
    }
</style>
"""

def get_flag_icon(lang_code: str) -> str:
    """
    Get the SVG flag icon for a language.
    
    Args:
        lang_code: The language code
        
    Returns:
        HTML string with the flag icon
    """
    if lang_code in FLAG_SVG:
        # Use SVG for better quality
        return f'<div class="flag-icon">{FLAG_SVG[lang_code]}</div>'
    elif lang_code in FLAG_EMOJIS:
        # Fallback to emoji
        return f'<span class="flag-icon" style="font-size: 20px;">{FLAG_EMOJIS[lang_code]}</span>'
    else:
        # Default icon for unsupported languages
        return '<span class="flag-icon">🌐</span>'

def animated_language_switcher(
    key_suffix: Optional[str] = None, 
    show_title: bool = True,
    use_buttons: bool = True
) -> None:
    """
    Display an animated language selector with flag icons.
    
    Args:
        key_suffix: Optional suffix for unique widget keys
        show_title: Whether to show the language selector title
        use_buttons: Whether to use buttons instead of a dropdown
    """
    # Create a unique key suffix if none provided
    if key_suffix is None:
        key_suffix = str(uuid.uuid4())[:8]
    
    # Current language from session state with fallback
    current_lang = st.session_state.get('language', 'en')
    if current_lang not in LANGUAGES:
        current_lang = 'en'
        st.session_state['language'] = 'en'
    
    # Insert CSS for animations
    st.markdown(FLAG_ANIMATION_CSS, unsafe_allow_html=True)
    
    # Container for language selector
    with st.container():
        # Optional title
        if show_title:
            st.markdown('<p class="language-title">🌐 Select Your Language</p>', unsafe_allow_html=True)
        
        # Use simple radio buttons (more reliable than custom buttons)
        if use_buttons:
            # Create a more compact layout with horizontal radio buttons
            lang_options = []
            lang_display = {}
            
            for lang_code, lang_name in LANGUAGES.items():
                flag_emoji = FLAG_EMOJIS.get(lang_code, '🌐')
                lang_options.append(lang_code)
                lang_display[lang_code] = f"{flag_emoji} {lang_name}"
            
            # Use a horizontal radio button instead of individual buttons
            selected_lang = st.radio(
                label="",
                options=lang_options,
                format_func=lambda x: lang_display[x],
                horizontal=True,
                index=lang_options.index(current_lang) if current_lang in lang_options else 0,
                key=f"lang_radio_{key_suffix}",
                label_visibility="collapsed"
            )
            
            # If language changed, update it
            if selected_lang != current_lang:
                # Update language in session state
                st.session_state.language = selected_lang
                
                # Load translations for new language
                from utils.i18n import set_language
                set_language(selected_lang)
                
                # Force rerun of app to update all UI elements
                st.rerun()
        
        # Dropdown-based selector (fallback)
        else:
            current_index = list(LANGUAGES.keys()).index(current_lang) if current_lang in LANGUAGES else 0
            selected_lang = st.selectbox(
                "🌐 Language / Taal",
                options=list(LANGUAGES.keys()),
                format_func=lambda x: f"{FLAG_EMOJIS.get(x, '🌐')} {LANGUAGES.get(x, x)}",
                index=current_index,
                key=f"lang_dropdown_{key_suffix}"
            )
            
            if selected_lang != current_lang:
                if st.button(
                    f"Apply Language Change", 
                    key=f"apply_lang_change_{key_suffix}",
                    type="primary"
                ):
                    # Update language in session state and force it to persist
                    st.session_state.language = selected_lang
                    st.session_state['language'] = selected_lang  # Ensure it's set both ways
                    
                    # Load translations for new language
                    from utils.i18n import set_language
                    set_language(selected_lang)
                    
                    # Force rerun of app
                    st.rerun()

def get_welcome_message_animation() -> str:
    """
    Generate HTML/CSS for an animated welcome message in multiple languages.
    
    Returns:
        HTML string with animated welcome message
    """
    welcome_messages = {
        'en': 'Welcome to DataGuardian',
        'nl': 'Welkom bij DataGuardian',
        'fr': 'Bienvenue à DataGuardian',
        'de': 'Willkommen bei DataGuardian',
        'es': 'Bienvenido a DataGuardian',
        'it': 'Benvenuto a DataGuardian',
        'pt': 'Bem-vindo ao DataGuardian'
    }
    
    # CSS with embedded animation (no JavaScript needed)
    welcome_css = """
    <style>
        .welcome-animation-container {
            margin: 20px auto;
            max-width: 500px;
            background: linear-gradient(to right, #f8f9fa, #f1f3f5);
            border-radius: 12px;
            padding: 18px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            overflow: hidden;
            position: relative;
            height: 60px;
        }
        
        .welcome-message {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            font-weight: 600;
            color: #1e3a8a;
            opacity: 0;
        }
        
        /* Animation for English */
        .welcome-message[lang="en"] {
            animation: fade-en 14s infinite;
        }
        
        /* Animation for Dutch */
        .welcome-message[lang="nl"] {
            animation: fade-nl 14s infinite;
        }
        
        @keyframes fade-en {
            0%, 43%, 100% { opacity: 0; transform: translateY(20px); }
            7%, 36% { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes fade-nl {
            50%, 93% { opacity: 0; transform: translateY(20px); }
            57%, 86% { opacity: 1; transform: translateY(0); }
        }
        
        /* Flag icon enhancements */
        .welcome-message .flag-icon {
            width: 28px;
            height: 28px;
            margin-right: 12px;
        }
    </style>
    """
    
    # Only show the two main supported languages
    welcome_html = '<div class="welcome-animation-container">'
    
    # Add only English and Dutch to prevent issues
    lang_to_show = ['en', 'nl']
    for lang_code in lang_to_show:
        if lang_code in welcome_messages:
            flag = get_flag_icon(lang_code)
            message = welcome_messages[lang_code]
            welcome_html += f'<div class="welcome-message" lang="{lang_code}">{flag} {message}</div>'
    
    welcome_html += '</div>'
    
    return welcome_css + welcome_html