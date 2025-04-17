import re
from typing import Dict, List, Any, Optional

def identify_pii_in_text(text: str, region: str = "Netherlands") -> List[Dict[str, Any]]:
    """
    Identify PII in text using regular expressions.
    
    Args:
        text: The text to scan for PII
        region: The region for which to apply PII detection rules
        
    Returns:
        List of dictionaries containing PII information
    """
    pii_items = []
    
    # Email addresses
    pii_items.extend(_find_emails(text))
    
    # Phone numbers
    pii_items.extend(_find_phone_numbers(text))
    
    # Addresses
    pii_items.extend(_find_addresses(text))
    
    # Names
    pii_items.extend(_find_names(text))
    
    # Credit card numbers
    pii_items.extend(_find_credit_cards(text))
    
    # IP addresses
    pii_items.extend(_find_ip_addresses(text))
    
    # Dates of birth
    pii_items.extend(_find_dates_of_birth(text))
    
    # BSN numbers (Dutch citizen service number)
    if region == "Netherlands":
        pii_items.extend(_find_bsn_numbers(text))
    
    # Passport numbers
    pii_items.extend(_find_passport_numbers(text))
    
    # Financial data
    pii_items.extend(_find_financial_data(text))
    
    # Medical data
    pii_items.extend(_find_medical_data(text))
    
    # Usernames and passwords
    pii_items.extend(_find_credentials(text))
    
    return pii_items

def _find_emails(text: str) -> List[Dict[str, Any]]:
    """Find email addresses in text."""
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.finditer(pattern, text)
    
    found = []
    for match in matches:
        found.append({
            'type': 'Email',
            'value': match.group(0)
        })
    
    return found

def _find_phone_numbers(text: str) -> List[Dict[str, Any]]:
    """Find phone numbers in text."""
    # International format
    pattern1 = r'\+\d{1,3}[-.\s]?(\d{1,3}[-.\s]?)?\d{3,}[-.\s]?\d{3,}'
    
    # National format
    pattern2 = r'\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
    
    # European format
    pattern3 = r'\b\d{2,4}[-.\s]?\d{2,4}[-.\s]?\d{2,4}[-.\s]?\d{2,4}\b'
    
    patterns = [pattern1, pattern2, pattern3]
    found = []
    
    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            found.append({
                'type': 'Phone',
                'value': match.group(0)
            })
    
    return found

def _find_addresses(text: str) -> List[Dict[str, Any]]:
    """Find addresses in text."""
    # Simple address pattern for demonstration (would need more complex patterns in production)
    patterns = [
        # Street address with number
        r'\b\d{1,5}\s[A-Za-z0-9\s]{1,50}(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\b',
        
        # European-style address
        r'\b[A-Za-z0-9\s]{1,50}(straat|laan|weg|plein|straße|straße|rue)\s\d{1,5}\b',
        
        # Postal codes
        r'\b\d{5}(-\d{4})?\b',  # US ZIP
        r'\b[A-Z]{1,2}\d{1,2}[A-Z]?\s?\d[A-Z]{2}\b',  # UK Postcode
        r'\b\d{4}\s?[A-Z]{2}\b'  # Dutch Postcode
    ]
    
    found = []
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            found.append({
                'type': 'Address',
                'value': match.group(0)
            })
    
    return found

def _find_names(text: str) -> List[Dict[str, Any]]:
    """Find names in text (simplified approach for demonstration)."""
    # This is a simplified approach and would need more sophisticated NLP in production
    # Looking for title + capitalized words
    pattern = r'\b(Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.)\s[A-Z][a-z]+(\s[A-Z][a-z]+)?\b'
    
    # Also look for common name patterns
    pattern2 = r'\b[A-Z][a-z]+\s(van|de|der|den|von|du|di|le|la|los)\s[A-Z][a-z]+\b'
    
    found = []
    for p in [pattern, pattern2]:
        matches = re.finditer(p, text)
        for match in matches:
            found.append({
                'type': 'Name',
                'value': match.group(0)
            })
    
    return found

def _find_credit_cards(text: str) -> List[Dict[str, Any]]:
    """Find credit card numbers in text."""
    # Match common credit card formats
    patterns = [
        # Visa
        r'\b4[0-9]{12}(?:[0-9]{3})?\b',
        
        # Mastercard
        r'\b5[1-5][0-9]{14}\b',
        
        # Amex
        r'\b3[47][0-9]{13}\b',
        
        # Discover
        r'\b6(?:011|5[0-9]{2})[0-9]{12}\b',
        
        # With spaces or dashes
        r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
    ]
    
    found = []
    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            value = match.group(0)
            # Mask most digits for security
            masked = value[:4] + '*' * (len(value) - 8) + value[-4:]
            found.append({
                'type': 'Credit Card',
                'value': masked
            })
    
    return found

def _find_ip_addresses(text: str) -> List[Dict[str, Any]]:
    """Find IP addresses in text."""
    # IPv4
    pattern1 = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
    
    # IPv6 (simplified)
    pattern2 = r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b'
    
    found = []
    for pattern in [pattern1, pattern2]:
        matches = re.finditer(pattern, text)
        for match in matches:
            found.append({
                'type': 'IP Address',
                'value': match.group(0)
            })
    
    return found

def _find_dates_of_birth(text: str) -> List[Dict[str, Any]]:
    """Find dates of birth in text."""
    # Look for date patterns with context that suggests a birth date
    patterns = [
        # DOB explicit mention
        r'\b(?:DOB|Date\sof\sBirth|Birth\sDate|Born\son)[:=\s-]+([0-9]{1,2}[-/\.][0-9]{1,2}[-/\.][0-9]{2,4})\b',
        
        # Common date formats (with context check)
        r'\bborn\s+(?:on\s+)?([0-9]{1,2}[-/\.][0-9]{1,2}[-/\.][0-9]{2,4})\b',
        r'\bbirth(?:date|day)?\s*(?::|is|on)?\s*([0-9]{1,2}[-/\.][0-9]{1,2}[-/\.][0-9]{2,4})\b'
    ]
    
    found = []
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            # Use the captured group if available, otherwise the whole match
            value = match.group(1) if match.lastindex else match.group(0)
            found.append({
                'type': 'Date of Birth',
                'value': value
            })
    
    return found

def _find_bsn_numbers(text: str) -> List[Dict[str, Any]]:
    """Find Dutch BSN numbers in text."""
    # BSN is a 9-digit number that passes the "11 test"
    # For simplicity, we'll just look for 9-digit numbers mentioned near the term "BSN"
    pattern = r'\b(?:BSN|Burgerservicenummer)(?:[:\s-]+)?(\d{9})\b'
    
    # Also look for 9-digit numbers with dashes or spaces
    pattern2 = r'\b\d{3}[-\s]\d{3}[-\s]\d{3}\b'
    
    found = []
    
    # Check for explicit BSN mentions
    matches = re.finditer(pattern, text, re.IGNORECASE)
    for match in matches:
        bsn = match.group(1) if match.lastindex else match.group(0)
        # Remove non-digits
        bsn = re.sub(r'\D', '', bsn)
        found.append({
            'type': 'BSN',
            'value': bsn
        })
    
    # Check for potential BSN patterns
    matches = re.finditer(pattern2, text)
    for match in matches:
        bsn = re.sub(r'\D', '', match.group(0))
        if _is_valid_bsn(bsn):
            found.append({
                'type': 'BSN',
                'value': bsn
            })
    
    return found

def _is_valid_bsn(bsn: str) -> bool:
    """Check if a number passes the BSN validation ("11 test")."""
    if not bsn.isdigit() or len(bsn) != 9:
        return False
    
    # Apply the "11 test" for BSN
    total = 0
    for i in range(9):
        if i == 8:
            total -= int(bsn[i]) * i
        else:
            total += int(bsn[i]) * (9 - i)
    
    return total % 11 == 0

def _find_passport_numbers(text: str) -> List[Dict[str, Any]]:
    """Find passport numbers in text."""
    # Different passport formats for different countries
    patterns = [
        # Generic passport number mention
        r'\bpassport(?:\s+number)?(?:[:\s#]+)([A-Z0-9]{6,12})\b',
        
        # Dutch passport
        r'\b[A-Z]{2}[0-9]{6}\b',
        
        # Various formats
        r'\b[A-Z]{1,2}[0-9]{6,8}\b'
    ]
    
    found = []
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            # Use the captured group if available, otherwise the whole match
            value = match.group(1) if match.lastindex else match.group(0)
            found.append({
                'type': 'Passport Number',
                'value': value
            })
    
    return found

def _find_financial_data(text: str) -> List[Dict[str, Any]]:
    """Find financial data in text."""
    # Bank account numbers
    patterns = [
        # IBAN
        r'\b[A-Z]{2}[0-9]{2}[A-Z0-9]{4}[0-9]{7}(?:[A-Z0-9]{0,16})?\b',
        
        # Bank account mentions
        r'\baccount(?:\s+number)?(?:[:\s#]+)([0-9]{6,12})\b',
        
        # Dutch bank account
        r'\bNL\d{2}\s?[A-Z]{4}\s?\d{4}\s?\d{4}\s?\d{2}\b'
    ]
    
    found = []
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            # Use the captured group if available, otherwise the whole match
            value = match.group(1) if match.lastindex else match.group(0)
            found.append({
                'type': 'Financial Data',
                'value': value
            })
    
    return found

def _find_medical_data(text: str) -> List[Dict[str, Any]]:
    """Find medical data in text."""
    # Medical terms and contexts
    medical_contexts = [
        r'\b(?:patient|medical|health|diagnosis|treatment|medication|prescription|symptom|disease|doctor|hospital|clinic)\b',
        r'\b(?:MRI|CT scan|X-ray|blood test|examination|surgery|condition|admitted|discharged)\b'
    ]
    
    found = []
    for pattern in medical_contexts:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            # Get a context snippet around the match
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            context = text[start:end]
            
            found.append({
                'type': 'Medical Data',
                'value': match.group(0),
                'context': '...' + context + '...'
            })
    
    return found

def _find_credentials(text: str) -> List[Dict[str, Any]]:
    """Find usernames and passwords in text."""
    patterns = [
        # Username
        r'\busername(?:[:\s]+)([A-Za-z0-9_-]{3,20})\b',
        
        # Username/Password pair
        r'\busername(?:[:\s]+)([A-Za-z0-9_-]{3,20})(?:[,\s]+)password(?:[:\s]+)([^\s,;]{6,20})\b',
        
        # Common login patterns
        r'\blogin(?:[:\s]+)([A-Za-z0-9_-]{3,20})\b',
        r'\buser(?:[:\s]+)([A-Za-z0-9_-]{3,20})\b'
    ]
    
    found = []
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            if match.lastindex == 2:  # Username/password pair
                found.append({
                    'type': 'Username',
                    'value': match.group(1)
                })
                found.append({
                    'type': 'Password',
                    'value': '*******'  # Mask password
                })
            else:
                # Just username
                value = match.group(1) if match.lastindex else match.group(0)
                found.append({
                    'type': 'Username',
                    'value': value
                })
    
    return found
