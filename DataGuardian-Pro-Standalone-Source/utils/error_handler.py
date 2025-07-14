"""
Error handling module for DataGuardian Pro.
Provides consistent, user-friendly error messages and error handling utilities.
"""

import streamlit as st
import traceback
import logging
from typing import Optional, Callable, Dict, Any, Tuple, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('dataguardian_error_handler')

# Error message styling
ERROR_STYLES = {
    "info": {
        "icon": "ℹ️",
        "color": "#3498db",
        "bg_color": "#e8f4fc",
        "border_color": "#bde0fc"
    },
    "warning": {
        "icon": "⚠️",
        "color": "#f39c12",
        "bg_color": "#fef5e7",
        "border_color": "#fdebd0"
    },
    "error": {
        "icon": "❌",
        "color": "#e74c3c",
        "bg_color": "#fdedeb",
        "border_color": "#f9cfca"
    },
    "success": {
        "icon": "✅",
        "color": "#2ecc71",
        "bg_color": "#eafaf1",
        "border_color": "#d5f5e3"
    }
}

# Error type to user-friendly translation mapping
ERROR_MESSAGES = {
    # Authentication errors
    "auth_invalid_credentials": {
        "title": "Invalid Credentials",
        "message": "The username or password you entered is incorrect. Please try again.",
        "suggestions": ["Double-check your username and password", "Reset your password if you've forgotten it"]
    },
    "auth_account_locked": {
        "title": "Account Locked",
        "message": "Your account has been temporarily locked due to multiple failed login attempts.",
        "suggestions": ["Wait 15 minutes before trying again", "Contact an administrator for assistance"]
    },
    "auth_permission_denied": {
        "title": "Permission Denied",
        "message": "You don't have permission to access this feature.",
        "suggestions": ["Contact your administrator for access", "Try using a different feature that's available to you"]
    },
    
    # Scan errors
    "scan_invalid_source": {
        "title": "Invalid Scan Source",
        "message": "The source you provided for scanning is invalid or cannot be accessed.",
        "suggestions": ["Check if the path/URL is correct", "Ensure you have proper access permissions", "Try a different source"]
    },
    "scan_timeout": {
        "title": "Scan Timeout",
        "message": "The scan operation took too long to complete and was terminated.",
        "suggestions": ["Try scanning a smaller dataset", "Break up your scan into multiple smaller scans"]
    },
    "scan_invalid_format": {
        "title": "Invalid File Format",
        "message": "One or more files are in an unsupported format.",
        "suggestions": ["Check the list of supported file formats", "Convert your files to a supported format"]
    },
    "scan_service_unavailable": {
        "title": "Scan Service Unavailable",
        "message": "The requested scan service is currently unavailable.",
        "suggestions": ["Try again later", "Check if your subscription includes this service"]
    },
    
    # Data errors
    "data_invalid_input": {
        "title": "Invalid Input",
        "message": "The data you provided is invalid or incomplete.",
        "suggestions": ["Review the required fields and formats", "Check for any missing required information"]
    },
    "data_too_large": {
        "title": "Data Too Large",
        "message": "The data exceeds the maximum size limit.",
        "suggestions": ["Reduce the amount of data", "Split the data into smaller chunks", "Upgrade your subscription for higher limits"]
    },
    "data_storage_full": {
        "title": "Storage Quota Exceeded",
        "message": "Your storage quota has been exceeded.",
        "suggestions": ["Delete old scans to free up space", "Upgrade your subscription for more storage"]
    },
    
    # API errors
    "api_rate_limit": {
        "title": "API Rate Limit Exceeded",
        "message": "You've reached the maximum number of API requests for your current plan.",
        "suggestions": ["Wait before making more requests", "Upgrade your subscription for higher limits"]
    },
    "api_invalid_key": {
        "title": "Invalid API Key",
        "message": "The API key provided is invalid or expired.",
        "suggestions": ["Check your API key", "Generate a new API key"]
    },
    
    # Report errors
    "report_generation_failed": {
        "title": "Report Generation Failed",
        "message": "There was an error generating your report.",
        "suggestions": ["Try again with different report parameters", "Check if the data source is still available"]
    },
    
    # General errors
    "general_unexpected": {
        "title": "Unexpected Error",
        "message": "An unexpected error occurred. Our team has been notified.",
        "suggestions": ["Try again later", "Contact support if the problem persists"]
    },
    "general_maintenance": {
        "title": "System Maintenance",
        "message": "The system is currently undergoing maintenance.",
        "suggestions": ["Try again later", "Check the status page for updates"]
    },
    "general_network": {
        "title": "Network Error",
        "message": "There was a problem with the network connection.",
        "suggestions": ["Check your internet connection", "Try again later"]
    }
}

def show_error_message(error_code: str, 
                       error_type: str = "error", 
                       custom_message: Optional[str] = None,
                       custom_suggestions: Optional[list] = None,
                       exception_details: Optional[Exception] = None) -> None:
    """
    Display a user-friendly error message with the Streamlit interface.
    
    Args:
        error_code: The error code key from the ERROR_MESSAGES dictionary
        error_type: The type of error message ('info', 'warning', 'error', 'success')
        custom_message: Optional custom message to override the default
        custom_suggestions: Optional custom suggestions to override the defaults
        exception_details: Optional exception object for logging details
    """
    # Log the error with exception details if provided
    if exception_details:
        logger.error(f"Error ({error_code}): {str(exception_details)}")
        logger.debug(traceback.format_exc())
    else:
        logger.error(f"Error ({error_code}): {custom_message or ERROR_MESSAGES.get(error_code, {}).get('message', 'Unknown error')}")
    
    # Get the error information
    error_info = ERROR_MESSAGES.get(error_code, {
        "title": "Unknown Error",
        "message": "An unknown error occurred.",
        "suggestions": ["Try again", "Contact support if the problem persists"]
    })
    
    # Use custom message and suggestions if provided
    message = custom_message or error_info["message"]
    suggestions = custom_suggestions or error_info["suggestions"]
    
    # Get style information for the chosen error type
    style = ERROR_STYLES.get(error_type, ERROR_STYLES["error"])
    
    # Create a visually appealing error message with the styling
    error_html = f"""
    <div style="
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: {style['bg_color']};
        border: 1px solid {style['border_color']};
        margin: 1rem 0;
    ">
        <div style="
            display: flex;
            align-items: center;
            margin-bottom: 0.5rem;
            color: {style['color']};
            font-weight: bold;
        ">
            <span style="font-size: 1.5rem; margin-right: 0.5rem;">{style['icon']}</span>
            <span style="font-size: 1.2rem;">{error_info['title']}</span>
        </div>
        <p style="
            margin: 0.5rem 0;
            color: #555;
        ">{message}</p>
        <div style="margin-top: 0.75rem;">
            <p style="
                font-weight: bold;
                margin-bottom: 0.25rem;
                font-size: 0.9rem;
                color: #555;
            ">Suggestions:</p>
            <ul style="
                margin: 0;
                padding-left: 1.5rem;
                color: #555;
            ">
    """
    
    # Add each suggestion as a list item
    for suggestion in suggestions:
        error_html += f"<li style=\"margin-bottom: 0.25rem;\">{suggestion}</li>"
    
    error_html += """
            </ul>
        </div>
    </div>
    """
    
    # Display the error message
    st.markdown(error_html, unsafe_allow_html=True)

def handle_exception(func: Callable) -> Callable:
    """
    Decorator for handling exceptions in Streamlit functions.
    Catches exceptions and displays user-friendly error messages.
    
    Args:
        func: The function to wrap
        
    Returns:
        Wrapped function with exception handling
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_code = getattr(e, 'error_code', 'general_unexpected')
            custom_message = getattr(e, 'custom_message', None)
            custom_suggestions = getattr(e, 'custom_suggestions', None)
            show_error_message(
                error_code=error_code,
                custom_message=custom_message,
                custom_suggestions=custom_suggestions,
                exception_details=e
            )
            # Return None to indicate failure
            return None
    return wrapper

class DataGuardianError(Exception):
    """
    Base exception class for DataGuardian Pro application.
    Includes error code and optional custom message and suggestions.
    """
    def __init__(self, error_code: str = 'general_unexpected', 
                 custom_message: Optional[str] = None,
                 custom_suggestions: Optional[list] = None):
        self.error_code = error_code
        self.custom_message = custom_message
        self.custom_suggestions = custom_suggestions
        super().__init__(custom_message or ERROR_MESSAGES.get(error_code, {}).get('message', 'Unknown error'))

class AuthenticationError(DataGuardianError):
    """Exception raised for authentication errors."""
    pass

class ScanError(DataGuardianError):
    """Exception raised for scan-related errors."""
    pass

class DataError(DataGuardianError):
    """Exception raised for data-related errors."""
    pass

class ApiError(DataGuardianError):
    """Exception raised for API-related errors."""
    pass

class ReportError(DataGuardianError):
    """Exception raised for report generation errors."""
    pass

def safe_execute(func: Callable, 
                 args: tuple = (), 
                 kwargs: dict = {}, 
                 error_code: str = 'general_unexpected',
                 default_return: Any = None) -> Tuple[bool, Any]:
    """
    Safely execute a function and handle any exceptions.
    
    Args:
        func: The function to execute
        args: Positional arguments to pass to the function
        kwargs: Keyword arguments to pass to the function
        error_code: The error code to use if an exception occurs
        default_return: The value to return if an exception occurs
        
    Returns:
        Tuple of (success: bool, result: Any)
    """
    try:
        result = func(*args, **kwargs)
        return True, result
    except Exception as e:
        logger.error(f"Error in safe_execute ({error_code}): {str(e)}")
        logger.debug(traceback.format_exc())
        return False, default_return

def create_error_placeholder(key: Optional[str] = None) -> Any:
    """
    Create a placeholder for displaying errors later.
    
    Args:
        key: Optional unique key for the placeholder
        
    Returns:
        Streamlit placeholder object
    """
    return st.empty()

def update_error_placeholder(placeholder: Any, 
                            error_code: str, 
                            error_type: str = "error", 
                            custom_message: Optional[str] = None,
                            custom_suggestions: Optional[list] = None) -> None:
    """
    Update an error placeholder with an error message.
    
    Args:
        placeholder: The placeholder to update
        error_code: The error code key from the ERROR_MESSAGES dictionary
        error_type: The type of error message ('info', 'warning', 'error', 'success')
        custom_message: Optional custom message to override the default
        custom_suggestions: Optional custom suggestions to override the defaults
    """
    with placeholder:
        show_error_message(
            error_code=error_code,
            error_type=error_type,
            custom_message=custom_message,
            custom_suggestions=custom_suggestions
        )

def clear_error_placeholder(placeholder: Any) -> None:
    """
    Clear an error placeholder.
    
    Args:
        placeholder: The placeholder to clear
    """
    placeholder.empty()

# Success message function
def show_success_message(title: str, message: str) -> None:
    """
    Display a success message.
    
    Args:
        title: The title of the success message
        message: The success message text
    """
    show_error_message(
        error_code="custom_success",
        error_type="success",
        custom_message=message,
        custom_suggestions=[],
        exception_details=None
    )