"""
Translation Utilities

This module provides translation utilities for the application.
It's designed to work with multiple languages and provides a fallback mechanism.
"""

def _(key, default=None):
    """
    Translation function.
    
    Args:
        key: The translation key to look up
        default: Default text to use if the key is not found
        
    Returns:
        The translated string or the default/key
    """
    # Simple implementation that just returns the key or default
    # In a real app, this would look up the key in a translation dictionary
    return default if default is not None else key