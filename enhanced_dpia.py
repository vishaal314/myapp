"""
Enhanced DPIA Form

This is a comprehensive standalone DPIA form that doesn't require selecting any repository.
It collects information provided by the user and generates a privacy DPIA scan report
based on user-selected actions on the form.
"""

import streamlit as st
import uuid
import json
import os
import traceback
import pandas as pd
from datetime import datetime
from services.dpia_scanner import DPIAScanner
from services.report_generator import generate_dpia_report, generate_pdf_report
from services.results_aggregator import ResultsAggregator

# Initialize components
scanner = DPIAScanner()
results_aggregator = ResultsAggregator()

def init_db_connection():
    """Initialize connection to the database for saving reports"""
    # This would normally connect to the database
    return True

def save_assessment_to_db(assessment_results):
    """Save assessment results to the database"""
    try:
        # Normally we'd save to a real database here
        scan_id = assessment_results.get('scan_id', str(uuid.uuid4()))
        results_aggregator.save_scan_result(assessment_results)
        return True
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return False

def extract_text_from_document(uploaded_file):
    """
    Extract text from an uploaded document.
    Supports PDF, DOCX, TXT, etc.
    """
    try:
        # Create a temp directory if it doesn't exist
        temp_dir = os.path.join(os.getcwd(), "temp_" + str(uuid.uuid4()))
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save the uploaded file
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Get file extension
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        # Extract text based on file type
        if ext == '.pdf':
            try:
                import PyPDF2
                with open(file_path, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    text = ""
                    for page_num in range(len(pdf_reader.pages)):
                        text += pdf_reader.pages[page_num].extract_text()
                return text
            except Exception as e:
                st.warning(f"Error extracting text from PDF: {str(e)}")
                return ""
                
        elif ext in ['.docx', '.doc']:
            try:
                import textract
                text = textract.process(file_path).decode('utf-8')
                return text
            except Exception as e:
                st.warning(f"Error extracting text from document: {str(e)}")
                return ""
                
        elif ext == '.txt':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as txt_file:
                return txt_file.read()
                
        elif ext == '.csv':
            try:
                df = pd.read_csv(file_path)
                return df.to_string()
            except Exception as e:
                st.warning(f"Error reading CSV: {str(e)}")
                return ""
                
        elif ext == '.json':
            try:
                with open(file_path, 'r', encoding='utf-8') as json_file:
                    data = json.load(json_file)
                return json.dumps(data, indent=2)
            except Exception as e:
                st.warning(f"Error reading JSON: {str(e)}")
                return ""
        
        else:
            try:
                import textract
                text = textract.process(file_path).decode('utf-8')
                return text
            except Exception as e:
                st.warning(f"Unsupported file type or error extracting text: {str(e)}")
                return ""
    
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return ""
    finally:
        # Clean up temporary file
        try:
            os.remove(file_path)
            os.rmdir(temp_dir)
        except:
            pass

def run_enhanced_dpia():
    """Run a comprehensive standalone DPIA form."""
    
    st.title("Enhanced DPIA Assessment")
    st.write("This is a comprehensive DPIA form that collects information provided by the user and generates a privacy DPIA scan report.")
    
    # Initialize session state variables if they don't exist
    if 'enhanced_dpia_answers' not in st.session_state:
        st.session_state.enhanced_dpia_answers = {
            "data_categories": [0, 0, 0, 0, 0],
            "processing_activities": [0, 0, 0, 0, 0],
            "rights_freedoms": [0, 0, 0, 0, 0],
            "data_sharing": [0, 0, 0, 0, 0],
            "security_measures": [0, 0, 0, 0, 0]
        }
    
    if 'enhanced_dpia_display_results' not in st.session_state:
        st.session_state.enhanced_dpia_display_results = False
    
    if 'enhanced_dpia_results' not in st.session_state:
        st.session_state.enhanced_dpia_results = None
    
    if 'enhanced_dpia_report_data' not in st.session_state:
        st.session_state.enhanced_dpia_report_data = None
    
    if 'enhanced_dpia_admin_info' not in st.session_state:
        st.session_state.enhanced_dpia_admin_info = {
            "project_name": "",
            "contact_person": "",
            "department": "",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "description": "",
            "purpose": ""
        }
    
    if 'extracted_document_text' not in st.session_state:
        st.session_state.extracted_document_text = ""
    
    # Show results if they exist
    if st.session_state.enhanced_dpia_display_results and st.session_state.enhanced_dpia_results:
        display_assessment_results(
            st.session_state.enhanced_dpia_results,
            st.session_state.enhanced_dpia_report_data,
            scanner
        )
        
        if st.button("Start New Assessment", type="primary"):
            st.session_state.enhanced_dpia_display_results = False
            st.session_state.enhanced_dpia_results = None
            st.session_state.enhanced_dpia_report_data = None
            st.rerun()
            
        return
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["Administrative Information", "Document Upload", "Assessment Questions", "Review & Submit"])
    
    with tab1:
        st.subheader("Administrative Information")
        st.write("Please provide the administrative details of your project.")
        
        # Administrative information form
        st.session_state.enhanced_dpia_admin_info["project_name"] = st.text_input(
            "Project Name", 
            value=st.session_state.enhanced_dpia_admin_info["project_name"]
        )
        
        st.session_state.enhanced_dpia_admin_info["contact_person"] = st.text_input(
            "Contact Person",
            value=st.session_state.enhanced_dpia_admin_info["contact_person"]
        )
        
        st.session_state.enhanced_dpia_admin_info["department"] = st.text_input(
            "Department/Unit",
            value=st.session_state.enhanced_dpia_admin_info["department"]
        )
        
        st.session_state.enhanced_dpia_admin_info["date"] = st.date_input(
            "Assessment Date",
            value=datetime.strptime(st.session_state.enhanced_dpia_admin_info["date"], "%Y-%m-%d") if st.session_state.enhanced_dpia_admin_info["date"] else datetime.now()
        ).strftime("%Y-%m-%d")
        
        st.session_state.enhanced_dpia_admin_info["description"] = st.text_area(
            "Project Description",
            value=st.session_state.enhanced_dpia_admin_info["description"],
            height=150
        )
        
        st.session_state.enhanced_dpia_admin_info["purpose"] = st.text_area(
            "Purpose of Data Processing",
            value=st.session_state.enhanced_dpia_admin_info["purpose"],
            height=150
        )
    
    with tab2:
        st.subheader("Document Upload (Optional)")
        st.write("Upload relevant documents to extract information for the DPIA assessment.")
        
        # Document upload section
        uploaded_file = st.file_uploader(
            "Upload Document (PDF, DOCX, TXT, etc.)",
            type=["pdf", "docx", "doc", "txt", "csv", "json", "xlsx"]
        )
        
        if uploaded_file:
            if st.button("Extract Information"):
                with st.spinner("Extracting information from document..."):
                    extracted_text = extract_text_from_document(uploaded_file)
                    st.session_state.extracted_document_text = extracted_text
                    
                    if extracted_text:
                        st.success(f"Successfully extracted information from {uploaded_file.name}")
                        with st.expander("View Extracted Text"):
                            st.text(extracted_text[:5000] + ("..." if len(extracted_text) > 5000 else ""))
                    else:
                        st.error(f"Failed to extract information from {uploaded_file.name}")
        
        # Display previously extracted text if available
        if st.session_state.extracted_document_text:
            st.subheader("Extracted Document Information")
            st.markdown("""
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; 
                        margin-bottom: 15px; border-left: 4px solid #1E88E5;">
                <p style="color: #555; margin: 0;">The following information has been extracted from your uploaded document. 
                You can use this as a reference when filling out the assessment questions.</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("View Extracted Text"):
                st.text(st.session_state.extracted_document_text[:5000] + 
                       ("..." if len(st.session_state.extracted_document_text) > 5000 else ""))
    
    with tab3:
        st.subheader("DPIA Assessment Questionnaire")
        st.write("Please answer the following questions to assess your data processing activities.")
        
        # Instructions
        st.markdown("""
        ## Assessment Questions
        For each question, select:
        - "No" if the condition does not apply
        - "Partially" if the condition somewhat applies
        - "Yes" if the condition fully applies
        
        Your answers will be used to assess the level of risk associated with your data processing activities.
        """)
        
        # Display categories and questions using static entry fields with improved error handling
        with st.form("enhanced_dpia_form", clear_on_submit=False):  # Prevent clearing form on submission
            # Add a note about form stability
            st.markdown("""
            <div style="background-color: #e8f4f8; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #2196F3;">
                <h3 style="color: #0d47a1; margin-top: 0; margin-bottom: 10px;">Anti-Crash Protection Enabled</h3>
                <p style="margin: 0;">To ensure form stability, your answers are automatically saved as you select them. 
                If you encounter any issues, your progress is preserved and you can pick up where you left off.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Process each category in a try/except block to prevent entire form crash
            for category, questions in scanner.assessment_categories.items():
                try:
                    st.subheader(questions["name"])
                    st.write(questions["description"])
                    
                    # Make sure the category exists in answers
                    if category not in st.session_state.enhanced_dpia_answers:
                        st.session_state.enhanced_dpia_answers[category] = [0] * len(questions["questions"])
                    
                    # Ensure the category list has the right length
                    if len(st.session_state.enhanced_dpia_answers[category]) < len(questions["questions"]):
                        st.session_state.enhanced_dpia_answers[category].extend(
                            [0] * (len(questions["questions"]) - len(st.session_state.enhanced_dpia_answers[category]))
                        )
                    
                    # Display each question with a simple number input
                    for q_idx, question in enumerate(questions["questions"]):
                        try:
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"{q_idx+1}. {question}")
                            
                            with col2:
                                # Default to the current value if it exists
                                current_val = 0
                                if len(st.session_state.enhanced_dpia_answers[category]) > q_idx:
                                    current_val = st.session_state.enhanced_dpia_answers[category][q_idx]
                                
                                # Use number input instead of selectbox for maximum stability
                                # Number inputs have proven to be more stable than selectboxes
                                answer_value = st.number_input(
                                    f"Answer for question {q_idx+1} (0=No, 1=Partially, 2=Yes)",
                                    min_value=0,
                                    max_value=2,
                                    value=int(current_val),
                                    step=1,
                                    key=f"enhanced_dpia_{category}_{q_idx}",
                                    help="0=No, 1=Partially, 2=Yes"
                                )
                                
                                # Store the answer immediately after selection
                                if len(st.session_state.enhanced_dpia_answers[category]) <= q_idx:
                                    st.session_state.enhanced_dpia_answers[category].append(int(answer_value))
                                else:
                                    st.session_state.enhanced_dpia_answers[category][q_idx] = int(answer_value)
                        except Exception as q_error:
                            # If a question fails, log the error but continue with other questions
                            st.warning(f"Error displaying question {q_idx+1}: {str(q_error)}")
                            continue
                        
                        st.markdown("---")
                except Exception as cat_error:
                    # If a category fails, log the error but continue with other categories
                    st.error(f"Error processing category {category}: {str(cat_error)}")
                    continue
            
            # Submit button inside the form with clear instructions
            st.markdown("""
            <div style="background-color: #e8f8ef; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #4CAF50;">
                <p style="margin: 0;">Click the button below to process your assessment and generate a report. 
                Your answers have already been saved.</p>
            </div>
            """, unsafe_allow_html=True)
            
            submit_button = st.form_submit_button("Process & Generate Report", type="primary", help="Click to generate your DPIA report based on your answers")
    
    with tab4:
        st.subheader("Review & Submit")
        st.write("Review your information before submitting the DPIA assessment.")
        
        # Display summary of administrative information
        st.markdown("### Administrative Information")
        for key, value in st.session_state.enhanced_dpia_admin_info.items():
            st.write(f"**{key.replace('_', ' ').title()}:** {value}")
        
        # Display summary of assessment answers
        st.markdown("### Assessment Answers Summary")
        for category, questions in scanner.assessment_categories.items():
            st.markdown(f"**{questions['name']}**")
            
            if category in st.session_state.enhanced_dpia_answers:
                answer_count = {
                    "No": 0,
                    "Partially": 0,
                    "Yes": 0
                }
                
                for answer in st.session_state.enhanced_dpia_answers[category]:
                    if answer == 0:
                        answer_count["No"] += 1
                    elif answer == 1:
                        answer_count["Partially"] += 1
                    else:
                        answer_count["Yes"] += 1
                
                for answer_type, count in answer_count.items():
                    st.write(f"- {answer_type}: {count}")
            
            st.markdown("---")
        
        # Final submit button
        if st.button("Generate DPIA Report", type="primary"):
            process_dpia_assessment()
    
    # Handle form submission if submit button was clicked
    if submit_button:
        process_dpia_assessment()

def process_dpia_assessment():
    """Process the DPIA assessment and generate results with enhanced error handling."""
    
    # Early termination if already processing - this is critical
    if st.session_state.get("is_processing", False):
        st.warning("Assessment is already being processed. Please wait...")
        st.stop()
    
    # Use a state lock mechanism to prevent form crashes
    try:
        st.session_state.is_processing = True
        
        # Add notification about processing start with improved styling
        st.markdown("""
        <div style="padding: 12px 20px; background-color: #e3f2fd; border: 1px solid #bbdefb; 
                  border-radius: 4px; margin-bottom: 20px;">
            <p style="margin: 0; color: #1565c0; display: flex; align-items: center;">
            <span style="margin-right: 10px; font-size: 20px;">⚙️</span>
            <span><strong>Processing Started:</strong> Your assessment is now being processed. 
            This may take a few moments. Please do not refresh the page.</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
    except Exception as lock_error:
        st.error(f"Error initializing processing: {str(lock_error)}")
        st.session_state.is_processing = False
        st.stop()
    
    # Create a progress bar and status display
    progress_bar = st.progress(0)
    status_text = st.empty()
    status_text.write("Starting assessment processing...")
    
    try:
        # Step 1: Prepare assessment data
        progress_bar.progress(0.1)
        status_text.write("Step 1/6: Preparing assessment data...")
        
        # Create a deep copy of the answers
        answers = {}
        for category, values in st.session_state.enhanced_dpia_answers.items():
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
            'answers': answers,
            'admin_info': st.session_state.enhanced_dpia_admin_info,
            'extracted_document_text': st.session_state.extracted_document_text
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
            
            # Add administrative information
            assessment_results['admin_info'] = st.session_state.enhanced_dpia_admin_info
            assessment_results['extracted_document_text'] = st.session_state.extracted_document_text
            
        except Exception as scan_error:
            st.warning(f"Scanner error: {str(scan_error)}. Using fallback calculations.")
            assessment_results = fallback_results
        
        # Generate report data with error handling
        progress_bar.progress(0.7)
        status_text.write("Step 4/6: Generating report data...")
        
        try:
            report_data = generate_dpia_report(assessment_results)
            
            # Add admin info to report data
            report_data['admin_info'] = st.session_state.enhanced_dpia_admin_info
            
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
                'admin_info': st.session_state.enhanced_dpia_admin_info,
                'sections': [
                    {'title': 'Overview', 'content': f"Overall Risk: {assessment_results['overall_risk_level']}"},
                    {'title': 'Categories', 'content': 'See risk analysis by category for details.'},
                    {'title': 'Project Information', 'content': f"Project Name: {st.session_state.enhanced_dpia_admin_info['project_name']}\nPurpose: {st.session_state.enhanced_dpia_admin_info['purpose']}"}
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
        
        # Store results (processing flag will be reset in finally block)
        st.session_state.enhanced_dpia_results = assessment_results
        st.session_state.enhanced_dpia_report_data = report_data
        st.session_state.enhanced_dpia_display_results = True
        
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
        
        # Add recovery option (processing flag will be reset in finally block)
        if st.button("Try Again", type="primary"):
            if not st.session_state.get("is_processing", False):
                st.rerun()
    finally:
        # Always ensure processing flag is reset when done, no matter what happened
        st.session_state.is_processing = False

def display_assessment_results(results, report_data, scanner):
    """Display the DPIA assessment results with visualizations"""
    
    st.title("DPIA Assessment Results")
    
    # Display administrative information
    st.markdown("""
    <div style="background-color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;
              box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h2 style="margin-top: 0;">Project Information</h2>
    """, unsafe_allow_html=True)
    
    admin_info = results.get('admin_info', {})
    for key, value in admin_info.items():
        st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
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
        
        st.markdown(f"""
        <div style="background-color: white; padding: 15px; border-radius: 8px; margin-bottom: 15px;
                  box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-left: 5px solid {risk_color};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="margin: 0; color: #333;">{category_name}</h3>
                    <p style="margin: 5px 0 0 0; color: #666;">Risk Level: {risk_level}</p>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 22px; font-weight: 600; color: {risk_color};">
                        {percentage:.1f}/10
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Key findings and recommendations
    st.subheader("Key Findings & Recommendations")
    
    if 'recommendations' in results and results['recommendations']:
        for idx, recommendation in enumerate(results['recommendations']):
            st.markdown(f"""
            <div style="background-color: white; padding: 15px; border-radius: 8px; margin-bottom: 10px;
                      box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <p style="margin: 0;"><strong>{idx+1}.</strong> {recommendation}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No specific recommendations generated based on the assessment.")
    
    # Generate PDF Report
    st.subheader("Download Report")
    
    if st.button("Generate PDF Report"):
        try:
            pdf_content = generate_pdf_report(report_data)
            
            # Create a download button for the PDF
            st.download_button(
                label="Download DPIA Report PDF",
                data=pdf_content,
                file_name=f"dpia_report_{results['scan_id'][:8]}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Error generating PDF report: {str(e)}")
    
    # Create a new assessment button
    st.button("Create New Assessment", type="primary", on_click=lambda: reset_assessment())

def reset_assessment():
    """Reset the assessment state to start a new one"""
    st.session_state.enhanced_dpia_display_results = False
    st.session_state.enhanced_dpia_results = None
    st.session_state.enhanced_dpia_report_data = None
    st.session_state.enhanced_dpia_answers = {
        "data_categories": [0, 0, 0, 0, 0],
        "processing_activities": [0, 0, 0, 0, 0],
        "rights_freedoms": [0, 0, 0, 0, 0],
        "data_sharing": [0, 0, 0, 0, 0],
        "security_measures": [0, 0, 0, 0, 0]
    }
    st.rerun()