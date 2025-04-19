"""
Interactive language switcher with country flag animations for DataGuardian Pro.
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
    
    # Current language from session state
    current_lang = st.session_state.get('language', 'en')
    
    # Insert CSS for animations
    st.markdown(FLAG_ANIMATION_CSS, unsafe_allow_html=True)
    
    # Container for language selector
    with st.container():
        # Optional title
        if show_title:
            st.markdown('<p class="language-title">🌐 Select Your Language / Selecteer je taal</p>', unsafe_allow_html=True)
        
        # Apply animations container
        st.markdown('<div class="language-animation-container">', unsafe_allow_html=True)
        
        # Button-based selector
        if use_buttons:
            # Container for language buttons
            st.markdown('<div class="lang-container animated-entry">', unsafe_allow_html=True)
            
            # Create column layout for buttons
            cols = st.columns(len(LANGUAGES))
            
            # Keep track of selected language
            if f"selected_lang_{key_suffix}" not in st.session_state:
                st.session_state[f"selected_lang_{key_suffix}"] = current_lang
            
            # Create buttons for each language
            for i, (lang_code, lang_name) in enumerate(LANGUAGES.items()):
                with cols[i]:
                    is_selected = st.session_state[f"selected_lang_{key_suffix}"] == lang_code
                    selected_class = "selected" if is_selected else ""
                    
                    # Create button HTML
                    button_html = f"""
                    <button 
                        class="lang-button {selected_class}" 
                        onclick="document.getElementById('lang_input_{key_suffix}').value='{lang_code}'; document.dispatchEvent(new Event('input_change_{key_suffix}'));">
                        {get_flag_icon(lang_code)}
                        <span class="lang-name">{lang_name}</span>
                    </button>
                    """
                    st.markdown(button_html, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Hidden input to store selected language
            st.markdown(
                f"""
                <input id="lang_input_{key_suffix}" type="hidden" value="{current_lang}">
                <script>
                    // Custom event handler to update Streamlit on button click
                    document.addEventListener('input_change_{key_suffix}', function() {{
                        var input = document.getElementById('lang_input_{key_suffix}');
                        var event = new Event('change');
                        input.dispatchEvent(event);
                    }}, false);
                </script>
                """, 
                unsafe_allow_html=True
            )
            
            # Create a streamlit element that will be updated by JavaScript
            language_value = st.text_input(
                "Hidden Language Selector", 
                value=current_lang,
                label_visibility="collapsed",
                key=f"hidden_lang_input_{key_suffix}"
            )
            
            # Update session state when language changes
            if language_value != current_lang:
                st.session_state[f"selected_lang_{key_suffix}"] = language_value
        
        # Dropdown-based selector (fallback)
        else:
            selected_lang = st.selectbox(
                "Select Language / Selecteer Taal",
                options=list(LANGUAGES.keys()),
                format_func=lambda x: f"{FLAG_EMOJIS.get(x, '🌐')} {LANGUAGES.get(x, x)}",
                index=list(LANGUAGES.keys()).index(current_lang) if current_lang in LANGUAGES else 0,
                key=f"lang_dropdown_{key_suffix}",
                label_visibility="collapsed"
            )
            st.session_state[f"selected_lang_{key_suffix}"] = selected_lang
        
        # Apply button
        if st.session_state[f"selected_lang_{key_suffix}"] != current_lang:
            selected_lang = st.session_state[f"selected_lang_{key_suffix}"]
            
            # Get language names for display
            from_lang = LANGUAGES.get(current_lang, current_lang)
            to_lang = LANGUAGES.get(selected_lang, selected_lang)
            
            # Show apply button
            if st.button(
                f"Apply: Change from {from_lang} to {to_lang}", 
                key=f"apply_lang_change_{key_suffix}",
                type="primary"
            ):
                # Update language in session state
                st.session_state.language = selected_lang
                # Load translations for new language
                set_language(selected_lang)
                # Force rerun of app
                st.rerun()
        
        # Close animations container
        st.markdown('</div>', unsafe_allow_html=True)

def get_welcome_message_animation() -> str:
    """
    Generate HTML/CSS for an animated welcome message in multiple languages.
    
    Returns:
        HTML string with animated welcome message
    """
    welcome_messages = {
        'en': 'Welcome to DataGuardian Pro',
        'nl': 'Welkom bij DataGuardian Pro',
        'fr': 'Bienvenue à DataGuardian Pro',
        'de': 'Willkommen bei DataGuardian Pro',
        'es': 'Bienvenido a DataGuardian Pro',
        'it': 'Benvenuto a DataGuardian Pro',
        'pt': 'Bem-vindo ao DataGuardian Pro'
    }
    
    # Only show supported languages
    welcome_html = '<div class="welcome-animation-container">'
    
    for lang_code, message in welcome_messages.items():
        if lang_code in LANGUAGES:
            flag = get_flag_icon(lang_code)
            welcome_html += f'<div class="welcome-message" lang="{lang_code}">{flag} {message}</div>'
    
    welcome_html += '</div>'
    
    # Add CSS for animations
    welcome_css = """
    <style>
        .welcome-animation-container {
            margin: 20px auto;
            max-width: 500px;
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            position: relative;
            height: 50px;
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
            font-size: 18px;
            font-weight: 600;
            color: #1e3a8a;
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.5s ease;
        }
        
        @keyframes welcome-cycle {
            0%, 100% { opacity: 0; transform: translateY(20px); }
            3%, 14% { opacity: 1; transform: translateY(0); }
            17%, 97% { opacity: 0; transform: translateY(-20px); }
        }
    </style>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const messages = document.querySelectorAll('.welcome-message');
            const duration = 3; // seconds per language
            const totalDuration = duration * messages.length;
            
            messages.forEach((msg, index) => {
                const delay = index * duration;
                const percentage = (delay / totalDuration) * 100;
                const percentageEnd = ((delay + duration) / totalDuration) * 100;
                
                msg.style.animation = `welcome-cycle ${totalDuration}s infinite`;
                msg.style.animationDelay = `-${delay}s`;
            });
        });
    </script>
    """
    
    return welcome_css + welcome_html