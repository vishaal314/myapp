#!/usr/bin/env python3
"""
DataGuardian Pro - Logging Configuration
Central configuration for all logging settings
"""

import os
from pathlib import Path

# Logging Configuration
LOG_CONFIG = {
    # Log levels
    'DEFAULT_LEVEL': os.getenv('LOG_LEVEL', 'INFO').upper(),
    'CONSOLE_LEVEL': os.getenv('CONSOLE_LOG_LEVEL', 'INFO').upper(),
    'FILE_LEVEL': os.getenv('FILE_LOG_LEVEL', 'DEBUG').upper(),
    
    # Log directories
    'LOG_DIR': Path(os.getenv('LOG_DIR', 'logs')),
    'ARCHIVE_DIR': Path(os.getenv('LOG_ARCHIVE_DIR', 'logs/archive')),
    
    # Rotation settings
    'MAX_FILE_SIZE': int(os.getenv('LOG_MAX_FILE_SIZE', '10485760')),  # 10MB
    'BACKUP_COUNT': int(os.getenv('LOG_BACKUP_COUNT', '5')),
    'ROTATION_INTERVAL': os.getenv('LOG_ROTATION_INTERVAL', 'midnight'),
    
    # Retention settings
    'ARCHIVE_AFTER_DAYS': int(os.getenv('LOG_ARCHIVE_AFTER_DAYS', '7')),
    'DELETE_AFTER_DAYS': int(os.getenv('LOG_DELETE_AFTER_DAYS', '30')),
    
    # Format settings
    'USE_JSON_FORMAT': os.getenv('LOG_USE_JSON', 'true').lower() == 'true',
    'INCLUDE_TRACEBACK': os.getenv('LOG_INCLUDE_TRACEBACK', 'true').lower() == 'true',
    
    # Performance settings
    'ASYNC_LOGGING': os.getenv('LOG_ASYNC', 'false').lower() == 'true',
    'BUFFER_SIZE': int(os.getenv('LOG_BUFFER_SIZE', '1024')),
    
    # Scanner-specific settings
    'SCANNER_LOG_LEVEL': os.getenv('SCANNER_LOG_LEVEL', 'INFO').upper(),
    'LOG_PII_DETECTIONS': os.getenv('LOG_PII_DETECTIONS', 'true').lower() == 'true',
    'LOG_PERFORMANCE_METRICS': os.getenv('LOG_PERFORMANCE_METRICS', 'true').lower() == 'true',
    
    # Security settings
    'MASK_SENSITIVE_DATA': os.getenv('LOG_MASK_SENSITIVE', 'true').lower() == 'true',
    'LOG_USER_ACTIONS': os.getenv('LOG_USER_ACTIONS', 'true').lower() == 'true',
    
    # Third-party logging levels
    'THIRD_PARTY_LEVELS': {
        'stripe': 'WARNING',
        'urllib3': 'WARNING',
        'requests': 'WARNING',
        'streamlit': 'WARNING',
        'matplotlib': 'WARNING',
        'PIL': 'WARNING'
    }
}

# Category-specific settings
CATEGORY_CONFIG = {
    'scanner': {
        'file_prefix': 'scanner',
        'max_size': LOG_CONFIG['MAX_FILE_SIZE'],
        'backup_count': LOG_CONFIG['BACKUP_COUNT'],
        'level': LOG_CONFIG['SCANNER_LOG_LEVEL']
    },
    'license': {
        'file_prefix': 'license',
        'max_size': LOG_CONFIG['MAX_FILE_SIZE'] // 2,  # 5MB
        'backup_count': 3,
        'level': 'INFO'
    },
    'security': {
        'file_prefix': 'security',
        'max_size': LOG_CONFIG['MAX_FILE_SIZE'],
        'backup_count': 10,  # Keep more security logs
        'level': 'INFO'
    },
    'performance': {
        'file_prefix': 'performance',
        'max_size': LOG_CONFIG['MAX_FILE_SIZE'],
        'backup_count': 3,
        'level': 'INFO'
    },
    'system': {
        'file_prefix': 'system',
        'max_size': LOG_CONFIG['MAX_FILE_SIZE'],
        'backup_count': 5,
        'level': 'INFO'
    }
}

# Create log directory
LOG_CONFIG['LOG_DIR'].mkdir(exist_ok=True)
LOG_CONFIG['ARCHIVE_DIR'].mkdir(parents=True, exist_ok=True)