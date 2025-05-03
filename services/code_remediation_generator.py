"""
Code Remediation Generator

This module provides AI-powered code remediation suggestions for GDPR compliance issues.
It generates language-specific code snippets to fix common issues like missing consent,
improper data handling, and inadequate purpose specification.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
import openai

# Configure logger
logger = logging.getLogger(__name__)

# Initialize OpenAI client with API key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Map of language file extensions to language names
LANGUAGE_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript (React)",
    ".ts": "TypeScript",
    ".tsx": "TypeScript (React)",
    ".java": "Java",
    ".php": "PHP",
    ".rb": "Ruby",
    ".cs": "C#",
    ".go": "Go",
    ".swift": "Swift",
    ".kt": "Kotlin"
}

def detect_language(file_path: str) -> str:
    """
    Detect programming language from file extension.
    
    Args:
        file_path: Path to the source code file
        
    Returns:
        Detected language name or "Unknown"
    """
    _, ext = os.path.splitext(file_path.lower())
    return LANGUAGE_MAP.get(ext, "Unknown")

def generate_consent_remediation(finding: Dict[str, Any], code_context: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate code remediation suggestions for consent-related issues.
    
    Args:
        finding: The finding dict containing issue details
        code_context: Optional code snippet showing the problematic code
        
    Returns:
        Dictionary with remediation suggestions for different languages
    """
    # Determine the issue type and language
    issue_type = finding.get('type', '')
    file_path = finding.get('file_name', '')
    language = detect_language(file_path)
    
    # Extract relevant information
    data_type = finding.get('value', 'personal data')
    location = finding.get('location', '')
    line_number = finding.get('line_no', finding.get('line', ''))
    
    # Generate remediation based on issue type and language
    try:
        # The newest OpenAI model is "gpt-4o" which was released May 13, 2024
        # do not change this unless explicitly requested by the user
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a GDPR compliance expert specializing in code remediation. "
                             + "Generate specific, practical code snippets to fix GDPR consent and purpose issues. "
                             + "Focus on providing complete, ready-to-use code examples that show both the problem and the solution."
                },
                {
                    "role": "user",
                    "content": f"Generate code remediation for a GDPR {issue_type} issue in {language}. "
                             + f"The issue involves {data_type} at {location}. "
                             + f"Original code context: '''{code_context}'''. "
                             + f"Provide specific code examples for: "
                             + f"1. Proper consent collection "
                             + f"2. Purpose specification "
                             + f"3. Data minimization. "
                             + f"Format your response as JSON with these keys: "
                             + f"{{\"consent_code\": \"...\", \"purpose_code\": \"...\", \"minimization_code\": \"...\", \"explanation\": \"...\"}} "
                             + f"Each code snippet should be complete and ready-to-use with proper legal basis documentation."
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
            max_tokens=1500
        )
        
        # Parse the JSON response
        remediation_data = json.loads(response.choices[0].message.content)
        
        # Add language information to the result
        remediation_data["language"] = language
        remediation_data["issue_type"] = issue_type
        
        return remediation_data
        
    except Exception as e:
        logger.error(f"Error generating remediation: {str(e)}")
        return {
            "language": language,
            "issue_type": issue_type,
            "consent_code": "# Error generating remediation code",
            "purpose_code": "# Error generating remediation code",
            "minimization_code": "# Error generating remediation code",
            "explanation": f"Failed to generate remediation due to: {str(e)}"
        }

def get_code_context(file_path: str, line_number: int, context_lines: int = 5) -> str:
    """
    Extract code context from a file around a specific line number.
    
    Args:
        file_path: Path to the source code file
        line_number: Line number where the issue was found
        context_lines: Number of lines before and after to include
        
    Returns:
        String with the extracted code context
    """
    try:
        if not os.path.exists(file_path):
            return ""
            
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            all_lines = f.readlines()
            
        # Convert line_number to integer if it's a string
        if isinstance(line_number, str):
            try:
                line_number = int(line_number.strip())
            except ValueError:
                line_number = 1
                
        # Ensure line_number is at least 1
        line_number = max(1, line_number)
        
        # Handle zero-based indexing
        line_idx = line_number - 1
        
        # Calculate start and end line indices for context
        start_idx = max(0, line_idx - context_lines)
        end_idx = min(len(all_lines) - 1, line_idx + context_lines)
        
        # Extract the context lines
        context = ''.join(all_lines[start_idx:end_idx + 1])
        
        return context
    except Exception as e:
        logger.error(f"Error extracting code context: {str(e)}")
        return ""

def analyze_consent_issues(findings: List[Dict[str, Any]], repo_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Analyze GDPR findings for consent issues and generate remediation suggestions.
    
    Args:
        findings: List of findings from the code scanner
        repo_path: Optional base path to the repository
        
    Returns:
        List of findings with added remediation suggestions
    """
    enhanced_findings = []
    
    for finding in findings:
        # Skip if not a consent or legal basis related issue
        if not is_consent_related(finding):
            enhanced_findings.append(finding)
            continue
            
        # Get file path
        file_path = finding.get('file_name', '')
        if repo_path and not file_path.startswith('/'):
            file_path = os.path.join(repo_path, file_path)
            
        # Get line number
        line_number = finding.get('line_no', finding.get('line', 1))
        
        # Extract code context
        code_context = get_code_context(file_path, line_number)
        
        # Generate remediation suggestions
        remediation = generate_consent_remediation(finding, code_context)
        
        # Add remediation to the finding
        finding['remediation'] = remediation
        
        enhanced_findings.append(finding)
    
    return enhanced_findings

def is_consent_related(finding: Dict[str, Any]) -> bool:
    """
    Check if a finding is related to consent or legal basis issues.
    
    Args:
        finding: The finding dict to check
        
    Returns:
        True if the finding is consent-related, False otherwise
    """
    # Get finding type and description
    finding_type = finding.get('type', '').lower()
    description = finding.get('description', '').lower()
    reason = finding.get('reason', '').lower()
    value = str(finding.get('value', '')).lower()
    
    # Keywords related to consent and legal basis
    consent_keywords = [
        'consent', 'legal basis', 'lawful basis', 'gdpr art', 'gdpr article', 
        'opt-in', 'opt in', 'permission', 'cookie', 'tracking', 'pii', 
        'personal data', 'data subject', 'privacy', 'personal information',
        'sensitive data', 'data protection'
    ]
    
    # Check if any consent keywords are in the finding's fields
    for keyword in consent_keywords:
        if (keyword in finding_type or 
            keyword in description or 
            keyword in reason or 
            keyword in value):
            return True
    
    # Check for specific finding types that are always consent-related
    consent_finding_types = [
        'email', 'phone', 'credit_card', 'address', 'personal_id', 'passport',
        'ssn', 'bank_account', 'ip_address', 'location', 'health', 'biometric',
        'facial_recognition', 'racial_origin', 'political_opinion', 'religious_belief',
        'api_key', 'auth'
    ]
    
    for type_keyword in consent_finding_types:
        if type_keyword in finding_type:
            return True
    
    return False

def get_language_specific_remediation(finding: Dict[str, Any], language: str) -> Dict[str, Any]:
    """
    Extract language-specific remediation code from a finding.
    
    Args:
        finding: The finding containing remediation suggestions
        language: Target programming language
        
    Returns:
        Dictionary with remediation code for the specified language or fallback
    """
    # Get the remediation data
    remediation = finding.get('remediation', {})
    
    # If no remediation data available, return empty
    if not remediation:
        return {
            "consent_code": "",
            "purpose_code": "",
            "minimization_code": "",
            "explanation": "No remediation suggestions available."
        }
    
    # Get actual language from remediation
    actual_language = remediation.get('language', 'Unknown')
    
    # If languages match, return the remediation
    if actual_language.lower() == language.lower():
        return remediation
    
    # Otherwise, try to generate language-specific remediation
    # This would involve calling generate_consent_remediation again with a different language
    # For now, just return the existing remediation with a note
    remediation['explanation'] = f"NOTE: This code is in {actual_language}, not {language}. " + remediation.get('explanation', '')
    
    return remediation