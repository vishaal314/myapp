import os
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('gdpr_scan_engine')

def generate_scan_id() -> str:
    """
    Generate a unique scan ID.
    
    Returns:
        A unique scan ID string
    """
    return str(uuid.uuid4())

def get_timestamp() -> str:
    """
    Get the current timestamp in ISO format.
    
    Returns:
        Current timestamp string
    """
    return datetime.now().isoformat()

def get_region_name(region_code: str) -> str:
    """
    Convert region code to full name.
    
    Args:
        region_code: The region code
        
    Returns:
        Full region name
    """
    region_map = {
        'NL': 'Netherlands',
        'DE': 'Germany',
        'FR': 'France',
        'BE': 'Belgium',
        'Netherlands': 'Netherlands',
        'Germany': 'Germany',
        'France': 'France',
        'Belgium': 'Belgium'
    }
    
    return region_map.get(region_code, region_code)

def save_temp_file(content: Union[str, bytes], prefix: str = 'gdpr_', suffix: str = '') -> str:
    """
    Save content to a temporary file.
    
    Args:
        content: File content (string or bytes)
        prefix: Filename prefix
        suffix: Filename suffix (e.g., file extension)
        
    Returns:
        Path to the temporary file
    """
    temp_dir = 'temp'
    os.makedirs(temp_dir, exist_ok=True)
    
    file_path = os.path.join(temp_dir, f"{prefix}{uuid.uuid4()}{suffix}")
    
    mode = 'wb' if isinstance(content, bytes) else 'w'
    with open(file_path, mode) as f:
        f.write(content)
    
    return file_path

def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Load a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Parsed JSON content
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON file '{file_path}': {str(e)}")
        return {}

def save_json_file(data: Dict[str, Any], file_path: str) -> bool:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save
        file_path: Output file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON file '{file_path}': {str(e)}")
        return False

def clean_temp_files(prefix: str = 'gdpr_') -> None:
    """
    Clean up temporary files.
    
    Args:
        prefix: Filename prefix to match
    """
    temp_dir = 'temp'
    if os.path.exists(temp_dir):
        for filename in os.listdir(temp_dir):
            if filename.startswith(prefix):
                try:
                    os.remove(os.path.join(temp_dir, filename))
                except Exception as e:
                    logger.warning(f"Error deleting temporary file '{filename}': {str(e)}")

def format_risk_level(risk_level: str) -> str:
    """
    Format risk level for display.
    
    Args:
        risk_level: Risk level (Low, Medium, High)
        
    Returns:
        Formatted risk level string
    """
    if risk_level.lower() == 'high':
        return '🔴 High'
    elif risk_level.lower() == 'medium':
        return '🟠 Medium'
    elif risk_level.lower() == 'low':
        return '🟢 Low'
    else:
        return risk_level

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + '...'

def mask_sensitive_value(value: str, keep_start: int = 4, keep_end: int = 4) -> str:
    """
    Mask a sensitive value.
    
    Args:
        value: Value to mask
        keep_start: Number of characters to keep at the start
        keep_end: Number of characters to keep at the end
        
    Returns:
        Masked value
    """
    if not value or len(value) <= (keep_start + keep_end):
        return value
    
    # Keep some characters at the start and end, replace the rest with asterisks
    return value[:keep_start] + '*' * (len(value) - keep_start - keep_end) + value[-keep_end:]
