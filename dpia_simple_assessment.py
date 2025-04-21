"""
Simplified DPIA Assessment for Testing

This file contains a simplified version of the DPIA assessment functionality
for testing and debugging purposes.
"""

import streamlit as st
import uuid
from datetime import datetime
from typing import Dict, List, Any

def perform_simple_assessment(answers: Dict[str, List[int]]) -> Dict[str, Any]:
    """
    Simplified version of perform_assessment for testing.
    
    Args:
        answers: Dictionary mapping category names to lists of answer values (0-2)
                0 = No, 1 = Partially, 2 = Yes
    
    Returns:
        Assessment results including risk scores and recommendations
    """
    st.write("Starting simplified assessment...")
    
    # Define risk thresholds
    risk_thresholds = {
        'high': 7,
        'medium': 4,
        'low': 0
    }
    
    # Calculate scores for each category and overall
    category_scores = {}
    total_score = 0
    high_risk_count = 0
    medium_risk_count = 0
    low_risk_count = 0
    total_questions = 0
    
    st.write(f"Processing answers: {answers}")
    
    # Process each category
    for category, answer_values in answers.items():
        # Calculate category score (sum of all answers in category)
        category_score = sum(answer_values)
        max_possible = len(answer_values) * 2  # Max points per question is 2
        percentage = (category_score / max_possible) * 10  # Convert to 0-10 scale
        
        # Determine risk level for category
        if percentage >= risk_thresholds['high']:
            risk_level = "High"
            high_risk_count += 1
        elif percentage >= risk_thresholds['medium']:
            risk_level = "Medium"
            medium_risk_count += 1
        else:
            risk_level = "Low"
            low_risk_count += 1
        
        category_scores[category] = {
            "score": category_score,
            "max_possible": max_possible,
            "percentage": percentage,
            "risk_level": risk_level
        }
        
        total_score += category_score
        total_questions += len(answer_values)
    
    # Calculate overall risk score
    max_total = total_questions * 2
    overall_percentage = (total_score / max_total) * 10 if max_total > 0 else 0
    
    if overall_percentage >= risk_thresholds['high']:
        overall_risk = "High"
    elif overall_percentage >= risk_thresholds['medium']:
        overall_risk = "Medium"
    else:
        overall_risk = "Low"
    
    # Generate simplified recommendations
    recommendations = []
    
    # Add general recommendation about DPIA requirement
    if high_risk_count > 0:
        recommendations.append({
            "category": "General",
            "severity": "High",
            "description": "A formal DPIA is required under Article 35 of GDPR due to high-risk processing."
        })
    
    # Create dummy recommendations for each high/medium risk category
    for category, scores in category_scores.items():
        if scores["risk_level"] != "Low":
            recommendations.append({
                "category": category,
                "severity": scores["risk_level"],
                "description": f"Address risk factors in the {category} category."
            })
    
    # Create results object
    results = {
        "scan_id": str(uuid.uuid4()),
        "scan_type": "DPIA",
        "timestamp": datetime.now().isoformat(),
        "overall_score": total_score,
        "overall_percentage": overall_percentage,
        "overall_risk_level": overall_risk,
        "category_scores": category_scores,
        "high_risk_count": high_risk_count,
        "medium_risk_count": medium_risk_count,
        "low_risk_count": low_risk_count,
        "recommendations": recommendations,
        "dpia_required": overall_risk == "High" or high_risk_count >= 2,
        "language": "en"
    }
    
    st.write("Assessment completed successfully!")
    st.write(f"Result keys: {results.keys()}")
    
    return results

def run_simplified_assessment_page():
    """Run a simple page to test the DPIA assessment functionality."""
    st.title("DPIA Simple Assessment Test")
    
    # Initialize sample answers if needed
    if "simple_dpia_answers" not in st.session_state:
        st.session_state.simple_dpia_answers = {
            "data_category": [1, 1, 2, 0, 1],
            "processing_activity": [0, 1, 1, 2, 0],
            "rights_impact": [1, 1, 0, 0, 2],
            "data_sharing": [0, 1, 1, 0, 1],
            "security_measures": [1, 1, 2, 0, 1]
        }
    
    # Display simple form for testing
    with st.form("test_dpia_form"):
        st.write("This is a simplified DPIA form for testing the assessment functionality.")
        st.write("The form contains predefined answers. Just click submit to test the assessment.")
        
        # Show the current answers
        st.write("Current test answers:")
        st.json(st.session_state.simple_dpia_answers)
        
        submit = st.form_submit_button("Run Test Assessment")
    
    if submit:
        try:
            st.session_state.test_assessment_results = perform_simple_assessment(
                st.session_state.simple_dpia_answers
            )
            st.session_state.test_completed = True
        except Exception as e:
            st.error(f"Error during test assessment: {str(e)}")
            st.exception(e)
    
    # Display results if available
    if "test_completed" in st.session_state and st.session_state.test_completed:
        st.success("Test assessment completed!")
        results = st.session_state.test_assessment_results
        
        st.subheader("Assessment Results")
        st.write(f"Overall Risk Level: {results['overall_risk_level']}")
        st.write(f"Risk Score: {results['overall_percentage']:.1f}/10")
        st.write(f"DPIA Required: {'Yes' if results['dpia_required'] else 'No'}")
        
        st.subheader("Category Scores")
        for category, scores in results["category_scores"].items():
            st.write(f"- {category}: {scores['risk_level']} ({scores['percentage']:.1f}/10)")
        
        st.subheader("Recommendations")
        for recommendation in results["recommendations"]:
            st.write(f"- [{recommendation['severity']}] {recommendation['category']}: {recommendation['description']}")

if __name__ == "__main__":
    run_simplified_assessment_page()