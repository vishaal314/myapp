"""
Code Remediation Generator

This module uses AI to analyze code compliance issues and generate remediation suggestions
based on the programming language and context of the finding.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Tuple
import time
import re
from openai import OpenAI

# Configure logger
logger = logging.getLogger(__name__)

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = None
if OPENAI_API_KEY:
    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("OpenAI client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {str(e)}")
else:
    logger.warning("OPENAI_API_KEY environment variable not set")

# Language detection mapping
LANGUAGE_EXTENSIONS = {
    '.py': 'Python',
    '.js': 'JavaScript',
    '.jsx': 'JavaScript (React)',
    '.ts': 'TypeScript',
    '.tsx': 'TypeScript (React)',
    '.java': 'Java',
    '.cs': 'C#',
    '.go': 'Go',
    '.rb': 'Ruby',
    '.php': 'PHP',
    '.rs': 'Rust',
    '.swift': 'Swift',
    '.c': 'C',
    '.cpp': 'C++',
    '.h': 'C/C++ Header',
    '.sh': 'Shell',
    '.ps1': 'PowerShell',
}

# Templates for GDPR compliance fixes
REMEDIATION_TEMPLATES = {
    'consent': {
        'Python': """
# Example of proper consent implementation
def collect_user_data(user_id, data_type, purpose):
    # Check if user has provided consent for this purpose
    if has_user_consent(user_id, data_type, purpose):
        # Process data with clear purpose
        result = process_data_for_purpose(user_id, data_type, purpose)
        # Log the processing for accountability
        log_data_processing(user_id, data_type, purpose)
        return result
    else:
        # Handle lack of consent appropriately
        logger.info(f"User {user_id} has not provided consent for {data_type} processing for {purpose}")
        return None
        """,
        'JavaScript': """
// Example of proper consent implementation
function collectUserData(userId, dataType, purpose) {
  // Check if user has provided consent for this purpose
  if (hasUserConsent(userId, dataType, purpose)) {
    // Process data with clear purpose
    const result = processDataForPurpose(userId, dataType, purpose);
    // Log the processing for accountability
    logDataProcessing(userId, dataType, purpose);
    return result;
  } else {
    // Handle lack of consent appropriately
    console.log(`User ${userId} has not provided consent for ${dataType} processing for ${purpose}`);
    return null;
  }
}
        """,
        'Java': """
// Example of proper consent implementation
public class ConsentManager {
    public Object collectUserData(String userId, String dataType, String purpose) {
        // Check if user has provided consent for this purpose
        if (hasUserConsent(userId, dataType, purpose)) {
            // Process data with clear purpose
            Object result = processDataForPurpose(userId, dataType, purpose);
            // Log the processing for accountability
            logDataProcessing(userId, dataType, purpose);
            return result;
        } else {
            // Handle lack of consent appropriately
            logger.info("User " + userId + " has not provided consent for " + dataType + " processing for " + purpose);
            return null;
        }
    }
}
        """
    },
    'purpose': {
        'Python': """
# Example of proper purpose specification
def process_user_location(user_id, location_data):
    # Define clear purpose for processing
    purpose = "navigation assistance"
    
    # Verify consent for this specific purpose
    if has_consent_for_purpose(user_id, "location", purpose):
        # Document the purpose in logs
        logger.info(f"Processing location data for user {user_id} for purpose: {purpose}")
        
        # Only use data for the stated purpose
        navigation_result = generate_navigation(location_data)
        
        # Don't use for other purposes like analytics or marketing
        return navigation_result
    else:
        return None
        """,
        'JavaScript': """
// Example of proper purpose specification
function processUserLocation(userId, locationData) {
  // Define clear purpose for processing
  const purpose = "navigation assistance";
  
  // Verify consent for this specific purpose
  if (hasConsentForPurpose(userId, "location", purpose)) {
    // Document the purpose in logs
    console.log(`Processing location data for user ${userId} for purpose: ${purpose}`);
    
    // Only use data for the stated purpose
    const navigationResult = generateNavigation(locationData);
    
    // Don't use for other purposes like analytics or marketing
    return navigationResult;
  } else {
    return null;
  }
}
        """,
        'Java': """
// Example of proper purpose specification
public class LocationProcessor {
    public Object processUserLocation(String userId, Object locationData) {
        // Define clear purpose for processing
        String purpose = "navigation assistance";
        
        // Verify consent for this specific purpose
        if (hasConsentForPurpose(userId, "location", purpose)) {
            // Document the purpose in logs
            logger.info("Processing location data for user " + userId + " for purpose: " + purpose);
            
            // Only use data for the stated purpose
            Object navigationResult = generateNavigation(locationData);
            
            // Don't use for other purposes like analytics or marketing
            return navigationResult;
        } else {
            return null;
        }
    }
}
        """
    }
}

def detect_language(file_path: str) -> str:
    """
    Detect programming language from file extension.
    
    Args:
        file_path: Path to the source file
        
    Returns:
        Detected programming language or 'Unknown'
    """
    _, ext = os.path.splitext(file_path)
    return LANGUAGE_EXTENSIONS.get(ext.lower(), 'Unknown')

def extract_code_context(file_path: str, line_number: int, context_lines: int = 10) -> str:
    """
    Extract code context around the specified line number.
    
    Args:
        file_path: Path to the source file
        line_number: Line number where the issue was found
        context_lines: Number of lines of context (before and after)
        
    Returns:
        Code context string
    """
    try:
        if not os.path.exists(file_path):
            return ""
            
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
            
        start_line = max(0, line_number - context_lines - 1)
        end_line = min(len(lines), line_number + context_lines)
        
        return ''.join(lines[start_line:end_line])
    except Exception as e:
        logger.error(f"Error extracting code context: {str(e)}")
        return ""

def is_consent_related(finding: Dict[str, Any]) -> bool:
    """
    Check if a finding is related to consent or purpose issues.
    
    Args:
        finding: Dictionary containing finding information
        
    Returns:
        True if the finding is related to consent or purpose, False otherwise
    """
    # Check if the finding type indicates a consent issue
    if finding.get('type', '') in ['missing_consent', 'missing_purpose']:
        return True
        
    # Check if description contains consent-related keywords
    description = finding.get('description', '').lower()
    title = finding.get('title', '').lower()
    
    consent_keywords = [
        'consent', 'permission', 'opt-in', 'legal basis', 'gdpr', 'purpose', 
        'data processing', 'personal data', 'data collection'
    ]
    
    return any(keyword in description or keyword in title for keyword in consent_keywords)

def get_language_specific_remediation(language: str, issue_type: str) -> str:
    """
    Get a language-specific remediation template for a given issue type.
    
    Args:
        language: Programming language of the code
        issue_type: Type of issue (e.g., 'consent', 'purpose')
        
    Returns:
        Template code or empty string
    """
    # Map detected language to available templates
    if language not in ['Python', 'JavaScript', 'Java']:
        language = 'Python'  # Default to Python if language is not supported
        
    # Map issue type to available templates
    if 'consent' in issue_type.lower():
        template_key = 'consent'
    elif 'purpose' in issue_type.lower():
        template_key = 'purpose'
    else:
        template_key = 'consent'  # Default
        
    return REMEDIATION_TEMPLATES.get(template_key, {}).get(language, "")

def generate_ai_remediation(code_context: str, issue_description: str, language: str) -> str:
    """
    Generate AI-powered remediation suggestion using OpenAI.
    
    Args:
        code_context: The problematic code with context
        issue_description: Description of the issue
        language: Programming language of the code
        
    Returns:
        AI-generated remediation suggestion
    """
    if not openai_client:
        logger.warning("OpenAI client not available, using template-based remediation")
        return get_language_specific_remediation(language, issue_description)
        
    try:
        # Construct the prompt for the AI
        prompt = f"""You are a GDPR compliance expert helping developers fix code issues.

Issue: {issue_description}

Code Context:
```{language}
{code_context}
```

Please provide a specific code fix that implements proper GDPR compliance for this issue. 
Focus on implementing proper consent mechanisms, purpose specification, and data minimization.
Your solution should follow {language} best practices and include comments explaining the compliance aspects.
Provide ONLY the code solution, no additional explanations."""

        # Get response from OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            messages=[
                {"role": "system", "content": "You are a GDPR compliance code expert that provides accurate, production-ready code fixes."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.2,  # Low temperature for more focused responses
        )
        
        # Extract the code suggestion
        suggestion = response.choices[0].message.content.strip()
        
        # If the suggestion is wrapped in code blocks, extract just the code
        if suggestion.startswith("```") and suggestion.endswith("```"):
            # Extract language identifier if present
            lines = suggestion.split("\n")
            if len(lines) > 1 and not lines[0].endswith("```"):
                suggestion = "\n".join(lines[1:-1])
            else:
                suggestion = "\n".join(lines[1:-1])
                
        return suggestion
        
    except Exception as e:
        logger.error(f"Error generating AI remediation: {str(e)}")
        # Fall back to template-based remediation
        return get_language_specific_remediation(language, issue_description)

def analyze_consent_issues(findings: List[Dict[str, Any]], repo_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Analyze findings for consent issues and generate remediation suggestions.
    
    Args:
        findings: List of findings from the scanner
        repo_path: Base path to the repository
        
    Returns:
        Enhanced findings with remediation suggestions
    """
    enhanced_findings = []
    
    for finding in findings:
        # Copy the finding to avoid modifying the original
        enhanced_finding = finding.copy()
        
        # Skip if not a consent-related issue
        if not is_consent_related(finding):
            enhanced_findings.append(enhanced_finding)
            continue
        
        try:
            # Extract file path and line number
            file_path = finding.get('file_name', '')
            line_number = finding.get('line_no', 0)
            
            # Make full path if repo_path is provided
            full_path = os.path.join(repo_path, file_path) if repo_path else file_path
            
            # Detect language
            language = detect_language(file_path)
            
            # Get code context
            code_context = extract_code_context(full_path, line_number)
            
            # Generate remediation suggestion
            issue_description = finding.get('description', '')
            
            if code_context:
                remediation = generate_ai_remediation(code_context, issue_description, language)
            else:
                # Fall back to template if context extraction failed
                remediation = get_language_specific_remediation(language, issue_description)
            
            # Add remediation to the finding
            enhanced_finding['remediation'] = remediation
            enhanced_finding['language'] = language
            enhanced_finding['has_ai_remediation'] = bool(remediation)
            
        except Exception as e:
            logger.error(f"Error analyzing consent issue: {str(e)}")
            # Just use the original finding if enhancement fails
            enhanced_finding = finding
        
        enhanced_findings.append(enhanced_finding)
    
    return enhanced_findings