"""
Validation Helpers - Centralized validation logic for DPIA forms

Consolidates all validation patterns to eliminate duplication and 
provide consistent error handling across the application.
"""

import re
from typing import Dict, List, Tuple, Optional
import streamlit as st

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class FormValidator:
    """Centralized form validation with consistent error handling"""
    
    @staticmethod
    def validate_project_info(project_name: str, organization: str, 
                            department: str = "", contact_email: str = "") -> Tuple[bool, List[str]]:
        """
        Validate project information fields
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Required field validation
        if not project_name or not project_name.strip():
            errors.append("Project name is required")
        elif len(project_name.strip()) < 3:
            errors.append("Project name must be at least 3 characters")
        elif len(project_name.strip()) > 100:
            errors.append("Project name must be less than 100 characters")
            
        if not organization or not organization.strip():
            errors.append("Organization is required")
        elif len(organization.strip()) < 2:
            errors.append("Organization name must be at least 2 characters")
        elif len(organization.strip()) > 100:
            errors.append("Organization name must be less than 100 characters")
        
        # Optional field validation
        if contact_email and contact_email.strip():
            if not FormValidator._is_valid_email(contact_email.strip()):
                errors.append("Please enter a valid email address")
        
        if department and len(department.strip()) > 100:
            errors.append("Department name must be less than 100 characters")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_assessment_answers(answers: Dict[str, str]) -> Tuple[bool, List[str]]:
        """
        Validate assessment answers
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        if not answers:
            errors.append("No assessment answers provided")
            return False, errors
        
        # Check for required project information
        required_fields = ['project_name', 'organization']
        for field in required_fields:
            if field not in answers or not answers[field]:
                errors.append(f"Missing required field: {field.replace('_', ' ').title()}")
        
        # Validate answer format
        question_answers = {k: v for k, v in answers.items() 
                          if k not in ['project_name', 'organization', 'department', 'contact_email']}
        
        if not question_answers:
            errors.append("At least one assessment question must be answered")
        
        # Validate individual answers
        valid_answers = ['Yes', 'No', 'Partially', 'N/A']
        for question_key, answer in question_answers.items():
            if answer not in valid_answers:
                errors.append(f"Invalid answer for {question_key}: must be one of {valid_answers}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_signature_data(signature_name: str, signature_date: str, 
                              signature_role: str = "") -> Tuple[bool, List[str]]:
        """
        Validate digital signature data
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        if not signature_name or not signature_name.strip():
            errors.append("Signature name is required")
        elif len(signature_name.strip()) < 2:
            errors.append("Signature name must be at least 2 characters")
        elif len(signature_name.strip()) > 50:
            errors.append("Signature name must be less than 50 characters")
        
        if not signature_date or not signature_date.strip():
            errors.append("Signature date is required")
        
        if signature_role and len(signature_role.strip()) > 50:
            errors.append("Signature role must be less than 50 characters")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Validate email format using regex"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """
        Sanitize user input to prevent XSS and other injection attacks
        
        Args:
            text: Raw user input
            
        Returns:
            Sanitized text safe for storage and display
        """
        if not text:
            return ""
        
        # Remove potentially dangerous characters
        text = str(text).strip()
        
        # Replace HTML entities
        replacements = {
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
            '&': '&amp;'
        }
        
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        
        return text
    
    @staticmethod
    def validate_risk_calculation_data(answers: Dict[str, str]) -> Tuple[bool, List[str]]:
        """
        Validate data before risk calculation
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        if not answers:
            errors.append("No assessment data provided for risk calculation")
            return False, errors
        
        # Count answered questions (excluding project info)
        question_answers = {k: v for k, v in answers.items() 
                          if k not in ['project_name', 'organization', 'department', 'contact_email']}
        
        if len(question_answers) < 5:
            errors.append("At least 5 assessment questions must be answered for risk calculation")
        
        # Check for unanswered questions
        unanswered = [k for k, v in question_answers.items() if not v or v == ""]
        if unanswered:
            errors.append(f"The following questions are unanswered: {', '.join(unanswered)}")
        
        return len(errors) == 0, errors

class UIValidator:
    """UI-specific validation helpers for Streamlit components"""
    
    @staticmethod
    def show_validation_messages(errors: List[str], message_type: str = "error") -> None:
        """
        Display validation messages in Streamlit UI
        
        Args:
            errors: List of error messages
            message_type: Type of message ('error', 'warning', 'info', 'success')
        """
        if not errors:
            return
        
        message_func = getattr(st, message_type, st.error)
        
        if len(errors) == 1:
            message_func(errors[0])
        else:
            message_content = "Please fix the following issues:\n" + "\n".join(f"• {error}" for error in errors)
            message_func(message_content)
    
    @staticmethod
    def create_progress_indicator(current_step: int, total_steps: int, 
                                step_names: List[str] = None) -> None:
        """
        Create a visual progress indicator
        
        Args:
            current_step: Current step number (1-based)
            total_steps: Total number of steps
            step_names: Optional list of step names
        """
        progress_percent = (current_step - 1) / total_steps if total_steps > 0 else 0
        
        st.progress(progress_percent)
        
        if step_names and len(step_names) >= current_step:
            st.caption(f"Step {current_step} of {total_steps}: {step_names[current_step - 1]}")
        else:
            st.caption(f"Step {current_step} of {total_steps}")
    
    @staticmethod
    def create_validation_summary(is_valid: bool, errors: List[str]) -> Dict[str, any]:
        """
        Create a validation summary for UI display
        
        Returns:
            Dictionary with validation status and formatted messages
        """
        return {
            'is_valid': is_valid,
            'error_count': len(errors),
            'errors': errors,
            'status_color': 'green' if is_valid else 'red',
            'status_icon': '✅' if is_valid else '❌',
            'status_text': 'Valid' if is_valid else 'Invalid'
        }

class DataValidator:
    """Data validation helpers for business logic"""
    
    @staticmethod
    def validate_assessment_data_structure(data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate the structure of assessment data before database operations
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        required_keys = ['assessment_id', 'project_name', 'organization', 'created_date']
        
        for key in required_keys:
            if key not in data:
                errors.append(f"Missing required field: {key}")
        
        # Validate data types
        if 'risk_score' in data and not isinstance(data['risk_score'], (int, float)):
            errors.append("Risk score must be a number")
        
        if 'risk_score' in data and (data['risk_score'] < 0 or data['risk_score'] > 100):
            errors.append("Risk score must be between 0 and 100")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_json_data(json_data: str) -> Tuple[bool, str]:
        """
        Validate JSON data format
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            import json
            json.loads(json_data)
            return True, ""
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON format: {str(e)}"
        except Exception as e:
            return False, f"JSON validation error: {str(e)}"