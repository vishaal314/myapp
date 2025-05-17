"""
Standalone DPIA Report Generator

This module provides a completely standalone DPIA reporting interface that saves
reports directly to the database without relying on the scan submission process.
This is designed to work around the form submission issues in the main app.
"""

import streamlit as st
import uuid
import json
import traceback
from datetime import datetime
from typing import Dict, List, Any
import os

# Import database functionality
from services.dpia_scanner import DPIAScanner, generate_dpia_report
from services.report_generator import generate_report as generate_pdf_report
from services.results_aggregator import ResultsAggregator

# Initialize database connection
results_aggregator = None

def init_db_connection():
    """Initialize connection to the database for saving reports"""
    global results_aggregator
    if results_aggregator is None:
        try:
            results_aggregator = ResultsAggregator()
            return True
        except Exception as e:
            st.error(f"Error connecting to database: {str(e)}")
            st.code(traceback.format_exc())
            return False
    return True

def save_assessment_to_db(assessment_results):
    """Save assessment results to the database"""
    global results_aggregator
    
    if not init_db_connection():
        return False
    
    try:
        # Create a scan entry structure that matches what the database expects
        scan_entry = {
            "scan_id": assessment_results.get("scan_id", str(uuid.uuid4())),
            "scan_type": "dpia",
            "timestamp": assessment_results.get("timestamp", datetime.now().isoformat()),
            "status": "completed",
            "findings": [],
            "summary": {
                "risk_level": assessment_results.get("overall_risk_level", "Medium"),
                "score": assessment_results.get("overall_percentage", 5.0),
                "dpia_required": assessment_results.get("dpia_required", True),
                "category_scores": assessment_results.get("category_scores", {}),
                "recommendations": assessment_results.get("recommendations", [])
            },
            "metadata": {
                "scan_source": "dpia_online_report",
                "language": "en",
                "answers": assessment_results.get("answers", {})
            },
            "report_data": assessment_results
        }
        
        # Save to database
        success = results_aggregator.save_scan_results(scan_entry)
        return success
    except Exception as e:
        st.error(f"Error saving to database: {str(e)}")
        st.code(traceback.format_exc())
        return False

def run_dpia_online_report():
    """Run a standalone DPIA reporting interface that saves directly to the database"""
    
    st.title("DPIA Online Assessment")
    st.markdown("""
    <div style="background-color: #e0f7fa; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #00bcd4;">
        <h3 style="color: #00838f; margin-top: 0; margin-bottom: 10px;">Standalone DPIA Reporting Tool</h3>
        <p style="margin: 0;">This is a direct reporting tool that bypasses the scan pipeline to improve stability.
        Completed assessments are saved directly to the database for later reference.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Debug options for development
    with st.expander("Debug Options", expanded=False):
        if st.checkbox("Show Session State", value=False):
            st.write(dict((k, v) for k, v in st.session_state.items() if not k.startswith('_')))
        
        if st.button("Clear State"):
            for key in list(st.session_state.keys()):
                if key.startswith('dpia_online_') or key in ['assessment_results', 'report_data', 'display_results']:
                    del st.session_state[key]
            st.success("Session state reset")
            st.rerun()
    
    # Initialize scanner
    try:
        scanner = DPIAScanner(language='en')
        assessment_categories = scanner._get_assessment_categories()
    except Exception as e:
        st.error(f"Error initializing scanner: {str(e)}")
        st.code(traceback.format_exc())
        return
    
    # Check if we're in results display mode
    if 'dpia_online_display_results' in st.session_state and st.session_state.dpia_online_display_results:
        display_assessment_results(st.session_state.dpia_online_results, st.session_state.dpia_online_report_data, scanner)
        
        if st.button("Start New Assessment", type="primary"):
            for key in st.session_state.keys():
                if key.startswith('dpia_online_'):
                    del st.session_state[key]
            st.rerun()
        return
    
    # Initialize answers in session state
    if 'dpia_online_answers' not in st.session_state:
        st.session_state.dpia_online_answers = {}
    
    # Ensure all answer categories are properly initialized
    for category, meta in assessment_categories.items():
        question_count = len(meta.get('questions', []))
        prev_answers = st.session_state.dpia_online_answers.get(category, [])
        st.session_state.dpia_online_answers[category] = [
            prev_answers[i] if i < len(prev_answers) and isinstance(prev_answers[i], int) and 0 <= prev_answers[i] <= 2 else 0
            for i in range(question_count)
        ]
    
    # Assessment form instructions
    st.info("Complete all questions below and submit to generate your DPIA report.")
    
    # Create tabs for each category
    category_tabs = st.tabs([assessment_categories[cat]['name'] for cat in assessment_categories])
    
    # Create form content in each tab
    for i, category in enumerate(assessment_categories):
        with category_tabs[i]:
            st.markdown(f"### {assessment_categories[category]['name']}")
            st.markdown(f"*{assessment_categories[category]['description']}*")
            st.markdown("---")
            
            # Show questions for this category
            for q_idx, question_text in enumerate(assessment_categories[category]['questions']):
                st.markdown(f"**{question_text}**")
                
                options = ["No", "Partially", "Yes"]
                stored_value = st.session_state.dpia_online_answers[category][q_idx]
                
                # Safe index
                index = stored_value if isinstance(stored_value, int) and 0 <= stored_value < len(options) else 0
                
                answer = st.radio(
                    "Answer:",
                    options,
                    index=index,
                    key=f"dpia_online_radio_{category}_{q_idx}",
                    horizontal=True,
                    label_visibility="collapsed"
                )
                
                st.session_state.dpia_online_answers[category][q_idx] = options.index(answer)
                st.markdown("---")
    
    # Submission area with clear instructions
    st.subheader("Submit Assessment")
    st.markdown("Click the button below to process your assessment and generate a report.")
    
    # Prevent double-clicking issues by tracking submission state
    if 'is_processing' not in st.session_state:
        st.session_state.is_processing = False
        
    # Add a submit button with disabled state during processing
    submit_button = st.button("Process & Generate Report", 
                             type="primary", 
                             use_container_width=True,
                             disabled=st.session_state.is_processing)
    
    if submit_button:
        st.session_state.is_processing = True
        
        # Create a progress bar and status display for better user feedback
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.write("Starting assessment processing...")
        
        try:
            # Step 1: Prepare assessment data
            progress_bar.progress(0.1)
            status_text.write("Step 1/6: Preparing assessment data...")
            
            # Create a deep copy of the answers
            answers = {}
            for category, values in st.session_state.dpia_online_answers.items():
                answers[category] = list(values)
            
            # Display the answers being processed
            with st.expander("Processing Details", expanded=False):
                st.write("Processing answers:")
                st.json(answers)
                
                # Calculate our own score for verification
                st.write("Calculating preliminary scores...")
                total_score = 0
                high_risk_count = 0
                medium_risk_count = 0
                low_risk_count = 0
                total_questions = 0
                
                for category, answer_values in answers.items():
                    category_score = sum(answer_values)
                    max_possible = len(answer_values) * 2
                    percentage = (category_score / max_possible) * 10
                    
                    if percentage >= 7:
                        risk_level = "High"
                        high_risk_count += 1
                    elif percentage >= 4:
                        risk_level = "Medium"
                        medium_risk_count += 1
                    else:
                        risk_level = "Low"
                        low_risk_count += 1
                    
                    total_score += category_score
                    total_questions += len(answer_values)
                
                max_total = total_questions * 2
                overall_percentage = (total_score / max_total) * 10 if max_total > 0 else 0
                
                if overall_percentage >= 7:
                    overall_risk = "High"
                elif overall_percentage >= 4:
                    overall_risk = "Medium"
                else:
                    overall_risk = "Low"
                
                st.write(f"Preliminary calculation: Overall Risk = {overall_risk}, Score = {overall_percentage:.1f}/10")
            
            # Create a fallback result in case the scanner fails
            progress_bar.progress(0.3)
            status_text.write("Step 2/6: Preparing safe fallback assessment...")
            
            # Generate safe fallback results using our own calculation
            scan_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            fallback_results = {
                'scan_id': scan_id,
                'timestamp': timestamp,
                'overall_risk_level': overall_risk,
                'overall_percentage': overall_percentage,
                'dpia_required': overall_percentage >= 5.0,
                'category_scores': {},
                'recommendations': [],
                'answers': answers
            }
            
            # Add category scores to fallback results
            for category, answer_values in answers.items():
                category_score = sum(answer_values)
                max_possible = len(answer_values) * 2
                percentage = (category_score / max_possible) * 10
                risk_level = "High" if percentage >= 7 else ("Medium" if percentage >= 4 else "Low")
                
                fallback_results['category_scores'][category] = {
                    'score': category_score,
                    'max_possible': max_possible,
                    'percentage': percentage,
                    'risk_level': risk_level
                }
            
            # Process assessment with scanner, with error handling
            progress_bar.progress(0.5)
            status_text.write("Step 3/6: Generating official assessment...")
            
            try:
                assessment_results = scanner.perform_assessment(answers=answers)
                
                # Add required metadata if missing
                if 'scan_id' not in assessment_results:
                    assessment_results['scan_id'] = scan_id
                if 'timestamp' not in assessment_results:
                    assessment_results['timestamp'] = timestamp
                if 'answers' not in assessment_results:
                    assessment_results['answers'] = answers
            except Exception as scan_error:
                st.warning(f"Scanner error: {str(scan_error)}. Using fallback calculations.")
                assessment_results = fallback_results
            
            # Generate report data with error handling
            progress_bar.progress(0.7)
            status_text.write("Step 4/6: Generating report data...")
            
            try:
                report_data = generate_dpia_report(assessment_results)
            except Exception as report_error:
                st.warning(f"Report generation error: {str(report_error)}. Using simplified report.")
                # Create a simplified report if the generator fails
                report_data = {
                    'scan_id': assessment_results['scan_id'],
                    'timestamp': assessment_results['timestamp'],
                    'risk_level': assessment_results['overall_risk_level'],
                    'score': assessment_results['overall_percentage'],
                    'category_scores': assessment_results['category_scores'],
                    'dpia_required': assessment_results['dpia_required'],
                    'recommendations': assessment_results.get('recommendations', []),
                    'title': 'DPIA Assessment Report',
                    'sections': [
                        {'title': 'Overview', 'content': f"Overall Risk: {assessment_results['overall_risk_level']}"},
                        {'title': 'Categories', 'content': 'See risk analysis by category for details.'}
                    ]
                }
            
            # Save to database with error handling
            progress_bar.progress(0.9)
            status_text.write("Step 5/6: Saving to database...")
            
            db_success = False
            try:
                db_success = save_assessment_to_db(assessment_results)
                if db_success:
                    st.success("Assessment saved to database!")
                else:
                    st.warning("Database save operation did not complete. Results will still be available.")
            except Exception as db_error:
                st.warning(f"Database error: {str(db_error)}. Results will be available but not saved permanently.")
            
            # Store results in session state
            progress_bar.progress(1.0)
            status_text.write("Step 6/6: Finalizing...")
            
            # Reset processing flag first to avoid state issues
            st.session_state.is_processing = False
            
            # Then store results
            st.session_state.dpia_online_results = assessment_results
            st.session_state.dpia_online_report_data = report_data
            st.session_state.dpia_online_display_results = True
            
            # Show success message
            st.success("✅ Assessment completed successfully!")
            st.info("Click the button below to view your assessment results.")
            
            if st.button("View Results", type="primary"):
                st.rerun()
                
        except Exception as e:
            # Handle unexpected errors
            st.error(f"Error processing assessment: {str(e)}")
            st.write("Error details:")
            st.code(traceback.format_exc())
            
            # Reset processing flag so user can try again
            st.session_state.is_processing = False
            
            # Add recovery option
            if st.button("Try Again", type="primary"):
                st.rerun()

def display_assessment_results(results, report_data, scanner):
    """Display the DPIA assessment results with visualizations"""
    
    st.title("DPIA Assessment Results")
    
    # Overall risk level visualization
    risk_level = results["overall_risk_level"]
    risk_color = {
        "High": "#ef4444",
        "Medium": "#f97316",
        "Low": "#10b981"
    }.get(risk_level, "#ef4444")
    
    # Display overall risk with clear visual indicators
    st.markdown(f"""
    <div style="background-color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;
              box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h2 style="margin-top: 0;">Overall Risk Level</h2>
        <div style="display: flex; align-items: center; margin-bottom: 15px;">
            <div style="width: 20px; height: 20px; border-radius: 50%; 
                    background-color: {risk_color}; margin-right: 10px;"></div>
            <span style="font-size: 24px; font-weight: 600;">{risk_level}</span>
        </div>
        <div style="display: flex; align-items: center; margin-top: 10px;">
            <div style="flex: 1;">
                <h3>DPIA Required</h3>
                <p style="font-size: 18px; font-weight: 500;">
                    {"Yes" if results["dpia_required"] else "No"}
                </p>
            </div>
            <div style="flex: 1;">
                <h3>Risk Score</h3>
                <p style="font-size: 18px; font-weight: 500;">
                    {results["overall_percentage"]:.1f}/10
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Category scores visualization
    st.subheader("Risk Analysis by Category")
    
    for category, scores in results["category_scores"].items():
        category_name = scanner.assessment_categories[category]["name"]
        percentage = scores["percentage"]
        risk_level = scores["risk_level"]
        risk_color = {
            "High": "#ef4444",
            "Medium": "#f97316",
            "Low": "#10b981"
        }.get(risk_level, "#ef4444")
        
        # Create a visual progress bar for each category
        st.markdown(f"""
        <div style="margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                <span style="font-weight: 500;">{category_name}</span>
                <span style="color: {risk_color}; font-weight: 500;">{risk_level}</span>
            </div>
            <div style="height: 8px; background-color: #f3f4f6; border-radius: 4px; overflow: hidden;">
                <div style="width: {percentage*10}%; height: 100%; background-color: {risk_color};"></div>
            </div>
            <div style="display: flex; justify-content: flex-end; margin-top: 2px;">
                <span style="font-size: 12px; color: #6b7280;">{percentage:.1f}/10</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Recommendations
    st.subheader("Key Findings & Recommendations")
    
    if results.get("recommendations", []):
        for i, recommendation in enumerate(results["recommendations"][:5]):  # Show top 5
            severity = recommendation["severity"]
            category = recommendation["category"]
            description = recommendation["description"]
            
            risk_color = {
                "High": "#ef4444",
                "Medium": "#f97316",
                "Low": "#10b981"
            }.get(severity, "#ef4444")
            
            # Display each recommendation with visual severity indicator
            st.markdown(f"""
            <div style="background-color: white; padding: 15px; border-radius: 8px; margin-bottom: 10px;
                      box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-left: 4px solid {risk_color};">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span style="font-weight: 500; color: #4b5563;">{category}</span>
                    <span style="color: {risk_color}; font-weight: 500;">{severity}</span>
                </div>
                <p style="margin: 0;">{description}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No specific recommendations were generated.")
    
    # Generate and offer PDF report for download
    st.subheader("Download Full Report")
    st.write("The complete report includes detailed findings, all recommendations, and compliance guidance.")
    
    try:
        report_filename = f"dpia_report_{results['scan_id']}.pdf"
        
        with st.spinner("Generating PDF report..."):
            pdf_data = generate_pdf_report(report_data)
        
        st.success("✅ Report generated successfully! Click below to download.")
        
        # Download button
        st.download_button(
            label="📄 Download DPIA Report PDF",
            data=pdf_data,
            file_name=report_filename,
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Error generating report: {str(e)}")
        st.code(traceback.format_exc())

if __name__ == "__main__":
    run_dpia_online_report()