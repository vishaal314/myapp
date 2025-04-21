"""
DPIA Assessment Tool

A clean, step-by-step implementation of a Data Protection Impact Assessment (DPIA) form
based on GDPR Article 35 requirements. This follows a structured workflow with 7 key steps
to identify, assess, and mitigate data protection risks.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import datetime
import os
import uuid
from typing import Dict, List, Any, Optional, Tuple

class DPIAScanner:
    """DPIA Scanner class to handle assessment logic"""
    
    def __init__(self, language='en'):
        self.language = language
        self.risk_levels = {
            "low": {"color": "#10b981", "description": "Low risk - minimal impact on individuals"},
            "medium": {"color": "#f97316", "description": "Medium risk - potential impact requiring attention"},
            "high": {"color": "#ef4444", "description": "High risk - significant impact requiring mitigation"}
        }
    
    def perform_assessment(self, answers: Dict[str, Any]) -> Dict[str, Any]:
        """Process DPIA answers and produce risk assessment results"""
        
        # Calculate risk scores for each category
        risk_scores = {}
        all_findings = []
        
        # Process each step's responses
        for step, step_data in answers.items():
            if step == "admin_info" or not isinstance(step_data, dict):
                continue
                
            risk_score = 0
            findings = []
            
            # Calculate risks based on responses
            for question, response in step_data.items():
                if question.startswith("question_") and isinstance(response, dict):
                    answer_value = response.get("value", 0)
                    risk_score += answer_value
                    
                    # Add to findings if medium or high risk
                    if answer_value >= 2:  # Medium (2) or High (3) risk
                        risk_level = "high" if answer_value == 3 else "medium"
                        findings.append({
                            "question": response.get("question", question),
                            "risk_level": risk_level,
                            "details": response.get("details", ""),
                            "recommendation": self._generate_recommendation(step, question, risk_level)
                        })
            
            # Store risk score and findings for this category
            risk_scores[step] = risk_score
            all_findings.extend(findings)
        
        # Calculate overall risk level
        total_score = sum(risk_scores.values())
        max_possible = len(risk_scores) * 10  # Assuming max 10 points per category
        risk_percentage = (total_score / max_possible) * 100 if max_possible > 0 else 0
        
        if risk_percentage >= 70:
            overall_risk = "High"
        elif risk_percentage >= 40:
            overall_risk = "Medium"
        else:
            overall_risk = "Low"
        
        # Determine if formal DPIA is required
        dpia_required = overall_risk == "High" or len([f for f in all_findings if f["risk_level"] == "high"]) >= 2
        
        # Prepare complete assessment results
        assessment_results = {
            "timestamp": datetime.datetime.now().isoformat(),
            "assessment_id": str(uuid.uuid4()),
            "risk_scores": risk_scores,
            "risk_percentage": risk_percentage,
            "overall_risk_level": overall_risk,
            "dpia_required": dpia_required,
            "findings": all_findings,
            "high_risk_findings": [f for f in all_findings if f["risk_level"] == "high"],
            "medium_risk_findings": [f for f in all_findings if f["risk_level"] == "medium"],
            "recommendations": self._generate_key_recommendations(all_findings)
        }
        
        return assessment_results
    
    def _generate_recommendation(self, step: str, question: str, risk_level: str) -> str:
        """Generate a recommendation based on the step, question and risk level"""
        
        # Basic recommendations based on step
        recommendations = {
            "step1": "Conduct a more detailed screening to confirm if a DPIA is necessary.",
            "step2": "Provide a more comprehensive description of the data processing activities.",
            "step3": "Review the necessity and proportionality of your processing activities.",
            "step4": "Implement additional controls to mitigate identified privacy risks.",
            "step5": "Strengthen your technical and organizational measures to protect personal data.",
            "step6": "Consider consultation with your supervisory authority.",
            "step7": "Update your project plan to incorporate DPIA findings and measures."
        }
        
        # For high risks, add stronger language
        if risk_level == "high":
            return f"PRIORITY ACTION NEEDED: {recommendations.get(step, 'Review and address this high-risk issue.')}"
        
        return recommendations.get(step, "Review this area to ensure GDPR compliance.")
    
    def _generate_key_recommendations(self, findings: List[Dict[str, Any]]) -> List[str]:
        """Generate key recommendations based on findings"""
        
        if not findings:
            return ["No significant privacy risks identified. Maintain current data protection practices."]
        
        # Get unique recommendations, prioritizing high risks
        high_recommendations = set([f["recommendation"] for f in findings if f["risk_level"] == "high"])
        medium_recommendations = set([f["recommendation"] for f in findings if f["risk_level"] == "medium"])
        
        # Combine recommendations with high risks first
        all_recommendations = list(high_recommendations) + [r for r in medium_recommendations if r not in high_recommendations]
        
        # Limit to top 5 recommendations 
        return all_recommendations[:5]


def run_dpia_assessment():
    """Run a clean, step-by-step DPIA assessment following GDPR guidelines"""
    
    st.title("Data Protection Impact Assessment (DPIA)")
    
    # Initialize scanner
    scanner = DPIAScanner(language='en')
    
    # Check if we should display results
    if st.session_state.get("dpia_display_results", False):
        results = st.session_state.get("dpia_results", {})
        report_data = st.session_state.get("dpia_report_data", {})
        display_assessment_results(results, report_data, scanner)
        return
    
    # Initialize session state for answers if not already present
    if "dpia_answers" not in st.session_state:
        st.session_state.dpia_answers = {
            "admin_info": {
                "project_name": "",
                "organization": "",
                "dpia_lead": "",
                "date": datetime.datetime.now().strftime("%Y-%m-%d")
            },
            "step1": {},  # Identify Need
            "step2": {},  # Describe Processing
            "step3": {},  # Necessity & Proportionality
            "step4": {},  # Risk Assessment
            "step5": {},  # Mitigation Measures
            "step6": {},  # Sign-Off & Outcomes 
            "step7": {}   # Integration into Project
        }
    
    # Introduction to DPIA
    with st.expander("✅ What is a DPIA?", expanded=True):
        st.markdown("""
        A Data Protection Impact Assessment (DPIA) is a process required under the General Data Protection Regulation (GDPR) 
        to identify and minimize data protection risks in data processing activities—particularly those likely to 
        result in high risk to individuals' rights and freedoms.
        
        **🔗 DPIA & GDPR: Legal Relevance**  
        Under Article 35 of the GDPR, a DPIA is mandatory when data processing:
        
        * Involves systematic and extensive profiling
        * Involves large-scale processing of special categories (e.g., health data)
        * Includes monitoring of publicly accessible areas
        
        Failing to conduct a required DPIA can lead to administrative fines of up to €10 million or 2% of annual global turnover.
        """)
    
    # Create tabs for the 7 steps of DPIA
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "Admin Info", 
        "Step 1: Identify Need", 
        "Step 2: Describe Processing",
        "Step 3: Necessity & Proportionality", 
        "Step 4: Identify Risks",
        "Step 5: Mitigation Measures", 
        "Step 6: Sign-Off",
        "Step 7: Integration"
    ])
    
    # Admin Info Tab
    with tab1:
        st.header("Project Information")
        st.write("Please provide details about your project and organization.")
        
        admin_info = st.session_state.dpia_answers["admin_info"]
        
        col1, col2 = st.columns(2)
        with col1:
            admin_info["project_name"] = st.text_input("Project/Processing Name", 
                                                       value=admin_info.get("project_name", ""),
                                                       placeholder="e.g., CRM Overhaul – Customer Insight Engine")
            admin_info["organization"] = st.text_input("Organization", 
                                                      value=admin_info.get("organization", ""),
                                                      placeholder="e.g., ACME Ltd.")
        
        with col2:
            admin_info["dpia_lead"] = st.text_input("DPIA Lead", 
                                                   value=admin_info.get("dpia_lead", ""),
                                                   placeholder="e.g., Jane Smith, Data Protection Officer")
            # Handle date input safely
            try:
                if isinstance(admin_info.get("date"), str):
                    default_date = datetime.datetime.strptime(admin_info.get("date"), "%Y-%m-%d").date()
                elif isinstance(admin_info.get("date"), datetime.date):
                    default_date = admin_info.get("date")
                else:
                    default_date = datetime.datetime.now().date()
            except Exception:
                default_date = datetime.datetime.now().date()
                
            admin_info["date"] = st.date_input("Date", value=default_date)
            
        # Update session state
        st.session_state.dpia_answers["admin_info"] = admin_info
    
    # Step 1: Identify Need
    with tab2:
        st.header("Step 1: Identify the Need for a DPIA")
        st.write("Answer these screening questions to determine if a DPIA is necessary.")
        
        step1 = st.session_state.dpia_answers["step1"]
        
        # Screening questions with yes/no/unknown options
        screening_questions = [
            {"id": "question_1", "text": "Will personal data be processed?"},
            {"id": "question_2", "text": "Is the processing new or significantly changed?"},
            {"id": "question_3", "text": "Could the processing impact the rights of individuals?"},
            {"id": "question_4", "text": "Does the processing involve large-scale data?"},
            {"id": "question_5", "text": "Does the processing involve automated decision-making or profiling?"},
            {"id": "question_6", "text": "Does the processing involve special category data (e.g., health)?"},
            {"id": "question_7", "text": "Does the processing involve monitoring publicly accessible areas?"},
            {"id": "question_8", "text": "Does the processing involve data concerning vulnerable individuals?"},
            {"id": "question_9", "text": "Does the processing use new technologies?"},
            {"id": "question_10", "text": "Will the processing involve transferring data outside the EU?"}
        ]
        
        for question in screening_questions:
            q_id = question["id"]
            if q_id not in step1:
                step1[q_id] = {"question": question["text"], "value": 0, "details": ""}
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(question["text"])
            with col2:
                options = {0: "No", 1: "Unknown", 3: "Yes"}  # Using risk values (0=Low, 1=Medium, 3=High)
                option_values = [0, 1, 3]
                
                # Safely determine the index
                try:
                    current_value = step1[q_id]["value"]
                    if current_value in option_values:
                        index = option_values.index(current_value)
                    else:
                        index = 0
                except (ValueError, KeyError, TypeError):
                    index = 0
                
                step1[q_id]["value"] = st.selectbox(
                    label=f"Answer for {q_id}",
                    options=option_values,
                    format_func=lambda x: options.get(x, "Unknown"),
                    index=index,
                    label_visibility="collapsed",
                    key=f"step1_{q_id}_selectbox"
                )
            
            # If answered Yes, provide notes field
            if step1[q_id]["value"] == 3:
                step1[q_id]["details"] = st.text_area(
                    f"Additional details for: {question['text']}", 
                    value=step1[q_id].get("details", ""),
                    placeholder="Provide additional details..."
                )
                st.markdown("---")
            
        # Automatic recommendation based on screening
        yes_count = sum(1 for q in step1.values() if isinstance(q, dict) and q.get("value") == 3)
        if yes_count >= 2:
            st.warning("⚠️ Based on your answers, a full DPIA is likely required. Please continue with the assessment.")
        elif yes_count > 0:
            st.info("ℹ️ Based on your answers, a DPIA may be required. Continue to evaluate further.")
        elif step1:  # Only show if at least some questions have been answered
            st.success("✅ Based on your answers, a full DPIA may not be required, but documentation of this decision is recommended.")
        
        # Update session state
        st.session_state.dpia_answers["step1"] = step1
    
    # Step 2: Describe Processing
    with tab3:
        st.header("Step 2: Describe the Processing")
        st.write("Provide details about the data processing activities.")
        
        step2 = st.session_state.dpia_answers["step2"]
        
        processing_questions = [
            {"id": "question_1", "text": "What is the purpose of the data processing?"},
            {"id": "question_2", "text": "What personal data will be processed?"},
            {"id": "question_3", "text": "Who are the data subjects?"},
            {"id": "question_4", "text": "What is the source of the data?"},
            {"id": "question_5", "text": "Who has access to the data (internally and externally)?"},
            {"id": "question_6", "text": "Where will the data be stored?"},
            {"id": "question_7", "text": "How long will the data be retained?"},
            {"id": "question_8", "text": "What is the legal basis for processing?"},
            {"id": "question_9", "text": "What data processors are involved?"},
            {"id": "question_10", "text": "Are there any cross-border data transfers?"}
        ]
        
        for question in processing_questions:
            q_id = question["id"]
            if q_id not in step2:
                step2[q_id] = {"question": question["text"], "value": 0, "details": ""}
            
            st.subheader(question["text"])
            step2[q_id]["details"] = st.text_area(
                label=f"Answer for {q_id}",
                value=step2[q_id].get("details", ""),
                placeholder="Provide details...",
                label_visibility="collapsed",
                key=f"step2_{q_id}_details"
            )
            
            # Assess risk based on completeness
            if step2[q_id]["details"]:
                answer_length = len(step2[q_id]["details"])
                if answer_length > 100:
                    step2[q_id]["value"] = 0  # Low risk - comprehensive answer
                elif answer_length > 30:
                    step2[q_id]["value"] = 1  # Medium risk - acceptable but brief
                else:
                    step2[q_id]["value"] = 2  # Medium-high risk - too brief
            else:
                step2[q_id]["value"] = 3  # High risk - no answer
            
            st.markdown("---")
        
        # Update session state
        st.session_state.dpia_answers["step2"] = step2
    
    # Step 3: Necessity & Proportionality
    with tab4:
        st.header("Step 3: Assess Necessity & Proportionality")
        st.write("Evaluate whether your processing is necessary and proportionate to your purposes.")
        
        step3 = st.session_state.dpia_answers["step3"]
        
        proportionality_questions = [
            {"id": "question_1", "text": "Is the processing necessary for your purpose?"},
            {"id": "question_2", "text": "Could the same purpose be achieved without this processing or with less data?"},
            {"id": "question_3", "text": "Is the data minimized (only what's necessary is collected)?"},
            {"id": "question_4", "text": "How does the processing impact individuals' privacy?"},
            {"id": "question_5", "text": "Is the processing transparent to data subjects?"},
            {"id": "question_6", "text": "How are data subject rights guaranteed?"},
            {"id": "question_7", "text": "Are data retention periods appropriate?"},
            {"id": "question_8", "text": "Have you documented lawful basis for all processing activities?"}
        ]
        
        for question in proportionality_questions:
            q_id = question["id"]
            if q_id not in step3:
                step3[q_id] = {"question": question["text"], "value": 0, "details": ""}
            
            st.subheader(question["text"])
            
            # Risk assessment for this question
            risk_options = {
                0: "Low Risk",
                1: "Medium Risk", 
                2: "Medium-High Risk",
                3: "High Risk"
            }
            
            col1, col2 = st.columns([3, 1])
            with col1:
                step3[q_id]["details"] = st.text_area(
                    label=f"Details for {q_id}",
                    value=step3[q_id].get("details", ""),
                    placeholder="Provide your assessment...",
                    height=100,
                    key=f"step3_{q_id}_details"
                )
            
            with col2:
                option_values = list(risk_options.keys())
                
                # Safely determine the index
                try:
                    current_value = step3[q_id]["value"]
                    if current_value in option_values:
                        index = option_values.index(current_value)
                    else:
                        index = 0
                except (ValueError, KeyError, TypeError):
                    index = 0
                
                step3[q_id]["value"] = st.selectbox(
                    label=f"Risk level for {q_id}",
                    options=option_values,
                    format_func=lambda x: risk_options.get(x, "Unknown"),
                    index=index,
                    key=f"step3_{q_id}_risk_level"
                )
                
                # Color-coded risk level display
                risk_colors = {0: "#10b981", 1: "#f97316", 2: "#f97316", 3: "#ef4444"}
                st.markdown(f"""
                <div style="background-color: {risk_colors[step3[q_id]['value']]}; 
                            color: white; 
                            padding: 5px 10px; 
                            border-radius: 5px; 
                            text-align: center;">
                    {risk_options[step3[q_id]['value']]}
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
        
        # Update session state
        st.session_state.dpia_answers["step3"] = step3
    
    # Step 4: Identify Risks
    with tab5:
        st.header("Step 4: Identify and Assess Risks")
        st.write("Identify potential privacy risks and assess their likelihood and severity.")
        
        step4 = st.session_state.dpia_answers["step4"]
        
        risk_categories = [
            {"id": "question_1", "text": "Risk of unauthorized access to personal data"},
            {"id": "question_2", "text": "Risk of data breach or loss"},
            {"id": "question_3", "text": "Risk of data inaccuracy or quality issues"},
            {"id": "question_4", "text": "Risk of processing beyond original purpose"},
            {"id": "question_5", "text": "Risk of automated decision-making/profiling impact"},
            {"id": "question_6", "text": "Risk of inability to exercise data subject rights"},
            {"id": "question_7", "text": "Risk of non-compliance with retention policies"},
            {"id": "question_8", "text": "Risk of inadequate data security measures"}
        ]
        
        for risk in risk_categories:
            r_id = risk["id"]
            if r_id not in step4:
                step4[r_id] = {"question": risk["text"], "value": 0, "likelihood": 0, "impact": 0, "details": ""}
            
            st.subheader(risk["text"])
            
            # Set up columns for likelihood and impact
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                step4[r_id]["details"] = st.text_area(
                    label=f"Details for {r_id}",
                    value=step4[r_id].get("details", ""),
                    placeholder="Describe this risk in your context...",
                    height=100,
                    key=f"step4_{r_id}_details"
                )
            
            # Likelihood assessment
            with col2:
                likelihood_options = {0: "Unlikely", 1: "Possible", 2: "Likely", 3: "Very Likely"}
                option_values = list(likelihood_options.keys())
                
                # Safely determine the index
                try:
                    current_value = step4[r_id]["likelihood"]
                    if current_value in option_values:
                        index = option_values.index(current_value)
                    else:
                        index = 0
                except (ValueError, KeyError, TypeError):
                    index = 0
                
                step4[r_id]["likelihood"] = st.selectbox(
                    label="Likelihood",
                    options=option_values,
                    format_func=lambda x: likelihood_options.get(x, "Unknown"),
                    index=index,
                    key=f"step4_{r_id}_likelihood"
                )
            
            # Impact assessment
            with col3:
                impact_options = {0: "Minimal", 1: "Moderate", 2: "Significant", 3: "Severe"}
                option_values = list(impact_options.keys())
                
                # Safely determine the index
                try:
                    current_value = step4[r_id]["impact"]
                    if current_value in option_values:
                        index = option_values.index(current_value)
                    else:
                        index = 0
                except (ValueError, KeyError, TypeError):
                    index = 0
                
                step4[r_id]["impact"] = st.selectbox(
                    label="Impact",
                    options=option_values,
                    format_func=lambda x: impact_options.get(x, "Unknown"),
                    index=index,
                    key=f"step4_{r_id}_impact"
                )
            
            # Calculate overall risk value (simple multiplication of likelihood and impact)
            risk_value = step4[r_id]["likelihood"] * step4[r_id]["impact"]
            
            # Map to risk level (0-2: Low, 3-5: Medium, 6-9: High)
            if risk_value >= 6:
                step4[r_id]["value"] = 3  # High
            elif risk_value >= 3:
                step4[r_id]["value"] = 2  # Medium
            else:
                step4[r_id]["value"] = 0  # Low
            
            # Display overall risk level
            risk_level_map = {0: "Low", 2: "Medium", 3: "High"}
            risk_color_map = {0: "#10b981", 2: "#f97316", 3: "#ef4444"}
            risk_level = risk_level_map.get(step4[r_id]["value"], "Unknown")
            risk_color = risk_color_map.get(step4[r_id]["value"], "#cccccc")
            
            st.markdown(f"""
            <div style="background-color: {risk_color}; 
                        color: white; 
                        padding: 8px 15px; 
                        border-radius: 5px; 
                        margin-top: 10px;
                        text-align: center;">
                <strong>Overall Risk: {risk_level}</strong>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
        
        # Update session state
        st.session_state.dpia_answers["step4"] = step4
    
    # Step 5: Mitigation Measures
    with tab6:
        st.header("Step 5: Identify Mitigation Measures")
        st.write("Define measures to mitigate identified risks.")
        
        step5 = st.session_state.dpia_answers["step5"]
        
        # If we have identified risks, show them for mitigation planning
        high_risks = []
        medium_risks = []
        
        for step in ["step1", "step2", "step3", "step4"]:
            for q_id, q_data in st.session_state.dpia_answers.get(step, {}).items():
                if isinstance(q_data, dict) and "value" in q_data and "question" in q_data:
                    if q_data["value"] == 3:  # High risk
                        high_risks.append({"step": step, "id": q_id, "text": q_data["question"]})
                    elif q_data["value"] in [1, 2]:  # Medium risk
                        medium_risks.append({"step": step, "id": q_id, "text": q_data["question"]})
        
        # Display identified risks that need mitigation
        if high_risks:
            st.subheader("High Risks Requiring Mitigation")
            for idx, risk in enumerate(high_risks):
                risk_id = f"high_{idx+1}"
                if risk_id not in step5:
                    step5[risk_id] = {"question": risk["text"], "value": 0, "measure": "", "owner": "", "deadline": ""}
                
                st.write(f"**{risk['text']}**")
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    step5[risk_id]["measure"] = st.text_area(
                        label=f"Mitigation measure for {risk_id}",
                        value=step5[risk_id].get("measure", ""),
                        placeholder="Describe how this risk will be mitigated...",
                        height=100,
                        key=f"step5_{risk_id}_measure"
                    )
                
                with col2:
                    step5[risk_id]["owner"] = st.text_input(
                        label="Responsible Party",
                        value=step5[risk_id].get("owner", ""),
                        placeholder="e.g., IT Security",
                        key=f"step5_{risk_id}_owner"
                    )
                
                with col3:
                    # Properly handle date values by checking the type
                    deadline_value = step5[risk_id].get("deadline")
                    if deadline_value:
                        # If it's already a date object, use it directly
                        if isinstance(deadline_value, (datetime.date, datetime.datetime)):
                            date_value = deadline_value
                        # If it's a string, parse it
                        elif isinstance(deadline_value, str):
                            try:
                                date_value = datetime.datetime.strptime(deadline_value, "%Y-%m-%d").date()
                            except ValueError:
                                date_value = datetime.datetime.now().date()
                        else:
                            date_value = datetime.datetime.now().date()
                    else:
                        date_value = datetime.datetime.now().date()
                        
                    step5[risk_id]["deadline"] = st.date_input(
                        label="Target Date",
                        value=date_value,
                        key=f"step5_{risk_id}_deadline"
                    )
                
                # Assess measure effectiveness
                if step5[risk_id]["measure"]:
                    measure_length = len(step5[risk_id]["measure"])
                    if measure_length > 100 and step5[risk_id]["owner"] and step5[risk_id]["deadline"]:
                        step5[risk_id]["value"] = 0  # Effective mitigation
                    elif measure_length > 50:
                        step5[risk_id]["value"] = 1  # Somewhat effective
                    else:
                        step5[risk_id]["value"] = 2  # Less effective
                else:
                    step5[risk_id]["value"] = 3  # No mitigation
                
                st.markdown("---")
        
        if medium_risks:
            st.subheader("Medium Risks")
            for idx, risk in enumerate(medium_risks):
                risk_id = f"medium_{idx+1}"
                if risk_id not in step5:
                    step5[risk_id] = {"question": risk["text"], "value": 0, "measure": ""}
                
                st.write(f"**{risk['text']}**")
                step5[risk_id]["measure"] = st.text_area(
                    label=f"Mitigation measure for {risk_id}",
                    value=step5[risk_id].get("measure", ""),
                    placeholder="Describe how this risk will be mitigated...",
                    height=100,
                    key=f"step5_{risk_id}_measure"
                )
                
                # Assess measure effectiveness
                if step5[risk_id]["measure"]:
                    measure_length = len(step5[risk_id]["measure"])
                    if measure_length > 50:
                        step5[risk_id]["value"] = 0  # Effective mitigation
                    elif measure_length > 20:
                        step5[risk_id]["value"] = 1  # Somewhat effective
                    else:
                        step5[risk_id]["value"] = 2  # Less effective
                else:
                    step5[risk_id]["value"] = 3  # No mitigation
                
                st.markdown("---")
        
        if not high_risks and not medium_risks:
            st.info("No high or medium risks identified in previous steps. Consider general data protection measures.")
            
            # General mitigation measures
            general_measures = [
                {"id": "general_1", "text": "Data protection by design and default measures"},
                {"id": "general_2", "text": "Staff training and awareness"},
                {"id": "general_3", "text": "Data security measures"},
                {"id": "general_4", "text": "Data subject rights procedures"}
            ]
            
            for measure in general_measures:
                m_id = measure["id"]
                if m_id not in step5:
                    step5[m_id] = {"question": measure["text"], "value": 0, "measure": ""}
                
                st.write(f"**{measure['text']}**")
                step5[m_id]["measure"] = st.text_area(
                    label=f"Implementation details for {m_id}",
                    value=step5[m_id].get("measure", ""),
                    placeholder="Describe how this will be implemented...",
                    height=100,
                    key=f"step5_{m_id}_measure"
                )
                
                st.markdown("---")
        
        # Update session state
        st.session_state.dpia_answers["step5"] = step5
    
    # Step 6: Sign-Off & Outcomes
    with tab7:
        st.header("Step 6: Sign-Off & Outcomes")
        st.write("Document the decision and outcome of the DPIA.")
        
        step6 = st.session_state.dpia_answers["step6"]
        
        # Decision outcome
        decision_options = ["Proceed with processing", "Proceed with modifications", "Consult supervisory authority", "Do not proceed"]
        
        if "decision" not in step6:
            step6["decision"] = decision_options[0]
        
        # Safely determine the index
        try:
            current_decision = step6["decision"]
            if current_decision in decision_options:
                index = decision_options.index(current_decision)
            else:
                index = 0
        except (ValueError, KeyError, TypeError):
            index = 0
            
        step6["decision"] = st.selectbox(
            "DPIA Decision",
            options=decision_options,
            index=index,
            key="step6_decision_selectbox"
        )
        
        # Decision rationale
        step6["rationale"] = st.text_area(
            "Decision Rationale",
            value=step6.get("rationale", ""),
            placeholder="Explain the reasoning behind this decision...",
            height=150,
            key="step6_rationale"
        )
        
        # Approvers section
        st.subheader("Approvers")
        
        if "approvers" not in step6:
            step6["approvers"] = [{"name": "", "role": "", "date": datetime.datetime.now().strftime("%Y-%m-%d")}]
        
        for i, approver in enumerate(step6["approvers"]):
            col1, col2, col3, col4 = st.columns([2, 2, 1, 0.5])
            
            with col1:
                approver["name"] = st.text_input(
                    f"Name {i+1}",
                    value=approver.get("name", ""),
                    placeholder="e.g., Jane Smith",
                    key=f"step6_approver_{i}_name"
                )
            
            with col2:
                approver["role"] = st.text_input(
                    f"Role {i+1}",
                    value=approver.get("role", ""),
                    placeholder="e.g., Data Protection Officer",
                    key=f"step6_approver_{i}_role"
                )
            
            with col3:
                # Properly handle date values by checking the type
                date_value = approver.get("date")
                if date_value:
                    # If it's already a date object, use it directly
                    if isinstance(date_value, (datetime.date, datetime.datetime)):
                        approver_date = date_value
                    # If it's a string, parse it
                    elif isinstance(date_value, str):
                        try:
                            approver_date = datetime.datetime.strptime(date_value, "%Y-%m-%d").date()
                        except ValueError:
                            approver_date = datetime.datetime.now().date()
                    else:
                        approver_date = datetime.datetime.now().date()
                else:
                    approver_date = datetime.datetime.now().date()
                
                approver["date"] = st.date_input(
                    f"Date {i+1}",
                    value=approver_date,
                    key=f"step6_approver_{i}_date"
                )
            
            with col4:
                if i > 0 and st.button("✕", key=f"remove_approver_{i}"):
                    step6["approvers"].pop(i)
                    st.rerun()
        
        # Add more approvers
        if st.button("Add Another Approver", key="step6_add_approver_button"):
            step6["approvers"].append({"name": "", "role": "", "date": datetime.datetime.now().strftime("%Y-%m-%d")})
        
        # Consultation with supervisory authority required?
        st.subheader("Supervisory Authority Consultation")
        
        if "authority_consultation" not in step6:
            step6["authority_consultation"] = "No"
        
        step6["authority_consultation"] = st.radio(
            "Is consultation with the supervisory authority required?",
            options=["No", "Yes"],
            index=0 if step6["authority_consultation"] == "No" else 1,
            key="step6_authority_consultation_radio"
        )
        
        if step6["authority_consultation"] == "Yes":
            if "authority_details" not in step6:
                step6["authority_details"] = ""
            
            step6["authority_details"] = st.text_area(
                "Consultation Details",
                value=step6.get("authority_details", ""),
                placeholder="Provide details about the consultation process...",
                height=150,
                key="step6_authority_details"
            )
        
        # Update session state
        st.session_state.dpia_answers["step6"] = step6
    
    # Step 7: Integration into Project Plan
    with tab8:
        st.header("Step 7: Integration into Project Plan")
        st.write("Detail how DPIA findings will be integrated into your project lifecycle.")
        
        step7 = st.session_state.dpia_answers["step7"]
        
        # Project timeline integration
        if "timeline_integration" not in step7:
            step7["timeline_integration"] = ""
        
        step7["timeline_integration"] = st.text_area(
            "How will DPIA findings be integrated into the project timeline?",
            value=step7.get("timeline_integration", ""),
            placeholder="Describe integration with key project milestones...",
            height=150,
            key="step7_timeline_integration"
        )
        
        # Responsible parties
        if "responsible_parties" not in step7:
            step7["responsible_parties"] = ""
        
        step7["responsible_parties"] = st.text_area(
            "Who is responsible for implementing DPIA recommendations?",
            value=step7.get("responsible_parties", ""),
            placeholder="List roles and responsibilities...",
            height=150,
            key="step7_responsible_parties"
        )
        
        # Review schedule
        st.subheader("DPIA Review Schedule")
        
        if "review_schedule" not in step7:
            step7["review_schedule"] = "6 months"
        
        review_options = ["3 months", "6 months", "1 year", "2 years", "When significant changes occur"]
        
        # Safely determine the index
        try:
            current_value = step7["review_schedule"]
            if current_value in review_options:
                index = review_options.index(current_value)
            else:
                index = 1  # Default to "6 months"
        except (ValueError, KeyError, TypeError):
            index = 1
        
        step7["review_schedule"] = st.selectbox(
            "When will this DPIA be reviewed?",
            options=review_options,
            index=index,
            key="step7_review_schedule_selectbox"
        )
        
        # Next review date
        if "next_review_date" not in step7:
            step7["next_review_date"] = (datetime.datetime.now() + datetime.timedelta(days=180)).strftime("%Y-%m-%d")
        
        # Properly handle date values by checking the type
        next_review_date = step7.get("next_review_date")
        if next_review_date:
            # If it's already a date object, use it directly
            if isinstance(next_review_date, (datetime.date, datetime.datetime)):
                review_date = next_review_date
            # If it's a string, parse it
            elif isinstance(next_review_date, str):
                try:
                    review_date = datetime.datetime.strptime(next_review_date, "%Y-%m-%d").date()
                except ValueError:
                    review_date = (datetime.datetime.now() + datetime.timedelta(days=180)).date()
            else:
                review_date = (datetime.datetime.now() + datetime.timedelta(days=180)).date()
        else:
            review_date = (datetime.datetime.now() + datetime.timedelta(days=180)).date()
            
        step7["next_review_date"] = st.date_input(
            "Next Review Date",
            value=review_date,
            key="step7_next_review_date"
        )
        
        # Lessons learned
        if "lessons_learned" not in step7:
            step7["lessons_learned"] = ""
        
        step7["lessons_learned"] = st.text_area(
            "Lessons Learned from DPIA Process",
            value=step7.get("lessons_learned", ""),
            placeholder="Note any lessons from conducting this DPIA that could improve future assessments...",
            height=150,
            key="step7_lessons_learned"
        )
        
        # Update session state
        st.session_state.dpia_answers["step7"] = step7
    
    # Submit button at the bottom
    st.markdown("---")
    st.markdown("<h2 style='text-align: center;'>Submit Your DPIA Assessment</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Click the button below to submit your completed assessment for analysis</p>", unsafe_allow_html=True)
    
    # Create a more prominent submit button
    st.markdown("""
    <style>
    div[data-testid="stButton"] > button {
        background-color: #0e84b5;
        color: white;
        font-weight: bold;
        padding: 0.75rem 1.5rem;
        font-size: 1.1rem;
        border-radius: 0.5rem;
        margin: 1rem auto;
        display: block;
        width: 50%;
    }
    div[data-testid="stButton"] > button:hover {
        background-color: #0056b3;
        border-color: #0056b3;
    }
    </style>
    """, unsafe_allow_html=True)
    
    submit_button = st.button("Submit DPIA Assessment", type="primary", key="submit_dpia_button")
    
    # Info text under the button
    st.markdown("<p style='text-align: center; font-style: italic; color: #666;'>All sections should be completed before submission</p>", unsafe_allow_html=True)
    
    if submit_button:
        try:
            # Show progress indicator
            st.info("Processing your assessment... Please wait.")
            
            # Progress bar
            progress_bar = st.progress(0)
            progress_bar.progress(10, "Preparing assessment data...")
            
            # Process the assessment
            with st.spinner("Analyzing data protection risks..."):
                # Get a copy of the answers
                answers = st.session_state.dpia_answers.copy()
                
                progress_bar.progress(30, "Validating input data...")
                
                # Perform the assessment
                assessment_results = scanner.perform_assessment(answers=answers)
                
                progress_bar.progress(60, "Generating recommendations...")
                
                # Generate report data with enhanced structure
                report_data = {
                    "admin_info": answers.get("admin_info", {}),
                    "project_name": answers.get("admin_info", {}).get("project_name", "Unnamed Project"),
                    "organization": answers.get("admin_info", {}).get("organization", ""),
                    "dpia_lead": answers.get("admin_info", {}).get("dpia_lead", ""),
                    "date": answers.get("admin_info", {}).get("date", datetime.datetime.now().strftime("%Y-%m-%d")),
                    "report_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "sections": {
                        "introduction": {
                            "title": "1. Introduction",
                            "content": f"This DPIA was conducted for {answers.get('admin_info', {}).get('project_name', 'the project')} by {answers.get('admin_info', {}).get('dpia_lead', 'the assessment team')}."
                        },
                        "processing_description": {
                            "title": "2. Processing Description",
                            "content": "\n".join([f"{q['question']}: {q['details']}" for q in answers.get("step2", {}).values() if isinstance(q, dict) and "details" in q])
                        },
                        "necessity": {
                            "title": "3. Necessity & Proportionality",
                            "content": "\n".join([f"{q['question']}: {q['details']}" for q in answers.get("step3", {}).values() if isinstance(q, dict) and "details" in q])
                        },
                        "risks": {
                            "title": "4. Risk Assessment",
                            "content": "\n".join([f"{q['question']} - Risk Level: {['Low', 'Medium', 'Medium-High', 'High'][q['value']] if q['value'] < 4 else 'High'}" for q in answers.get("step4", {}).values() if isinstance(q, dict) and "value" in q])
                        },
                        "mitigation": {
                            "title": "5. Mitigation Measures",
                            "content": "\n".join([f"{q['question']}: {q['measure']}" for q in answers.get("step5", {}).values() if isinstance(q, dict) and "measure" in q])
                        },
                        "consultation": {
                            "title": "6. Consultation",
                            "content": f"Consultation with supervisory authority: {answers.get('step6', {}).get('authority_consultation', 'No')}\n{answers.get('step6', {}).get('authority_details', '')}"
                        },
                        "decision": {
                            "title": "7. Decision",
                            "content": f"Decision: {answers.get('step6', {}).get('decision', 'Unknown')}\nRationale: {answers.get('step6', {}).get('rationale', '')}"
                        }
                    }
                }
                
                progress_bar.progress(80, "Finalizing assessment...")
                
                # Save results and report to session state
                st.session_state.dpia_results = assessment_results
                st.session_state.dpia_report_data = report_data
                st.session_state.dpia_display_results = True
                
                progress_bar.progress(100, "Assessment complete!")
                
                # Rerun to show results
                st.rerun()
            
        except Exception as e:
            import traceback
            st.error(f"Error processing assessment: {str(e)}")
            st.code(traceback.format_exc())
            st.warning("Please try again or contact support if the issue persists.")


def display_assessment_results(results: Dict[str, Any], report_data: Dict[str, Any], scanner: DPIAScanner):
    """Display the DPIA assessment results with comprehensive report visualization"""
    
    st.title("DPIA Assessment Results")
    
    # Display header with report structure info
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; border-left: 4px solid #4caf50;">
        <h3 style="margin-top: 0; color: #3a7144;">DPIA Report Generated</h3>
        <p style="margin: 0;">This report follows the standard 7-section DPIA structure and presents the assessment findings in a clear, organized format.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get key information
    admin_info = report_data.get("admin_info", {})
    risk_level = results["overall_risk_level"]
    risk_color = {
        "High": "#ef4444",
        "Medium": "#f97316",
        "Low": "#10b981"
    }.get(risk_level, "#ef4444")
    
    # Display report header info
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; flex-wrap: wrap;">
        <div style="flex: 2; min-width: 300px;">
            <h2 style="margin: 0;">{admin_info.get('project_name', 'Project DPIA')}</h2>
            <p style="margin: 0;">Organization: <strong>{admin_info.get('organization', 'Not specified')}</strong></p>
            <p style="margin: 0;">DPIA Lead: <strong>{admin_info.get('dpia_lead', 'Not specified')}</strong></p>
            <p style="margin: 0;">Date: <strong>{admin_info.get('date', datetime.datetime.now().strftime('%Y-%m-%d'))}</strong></p>
        </div>
        <div style="flex: 1; min-width: 200px; padding: 10px; background-color: {risk_color}; color: white; border-radius: 5px; text-align: center;">
            <h3 style="margin: 0;">Overall Risk Level</h3>
            <h2 style="margin: 5px 0; font-size: 1.8em;">{risk_level}</h2>
            <p style="margin: 0;">DPIA Required: <strong>{"Yes" if results.get("dpia_required", False) else "No"}</strong></p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Risk score visualization
    st.subheader("Risk Assessment Summary")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create a radar chart for the risk categories
        risk_scores = results.get("risk_scores", {})
        
        if risk_scores:
            categories = []
            scores = []
            for step, score in risk_scores.items():
                step_name = {
                    "step1": "Need Identification", 
                    "step2": "Processing Description",
                    "step3": "Necessity & Proportionality", 
                    "step4": "Risk Assessment",
                    "step5": "Mitigation Measures", 
                    "step6": "Sign-Off",
                    "step7": "Integration"
                }.get(step, step)
                
                categories.append(step_name)
                scores.append(score)
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=scores,
                theta=categories,
                fill='toself',
                name='Risk Score',
                line_color='rgba(220, 70, 50, 0.8)',
                fillcolor='rgba(220, 70, 50, 0.2)'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, max(scores) + 2]
                    )),
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Display risk percentage as a gauge
        risk_percentage = results.get("risk_percentage", 0)
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk_percentage,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Risk Percentage"},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': "darkgray"},
                'steps': [
                    {'range': [0, 40], 'color': "green"},
                    {'range': [40, 70], 'color': "orange"},
                    {'range': [70, 100], 'color': "red"},
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': risk_percentage
                }
            }
        ))
        
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)
    
    # Tab layout for detailed results sections
    tab1, tab2, tab3, tab4 = st.tabs(["Key Findings", "Detailed Report", "Risks & Mitigation", "Next Steps"])
    
    # Tab 1: Key Findings
    with tab1:
        st.subheader("Key Findings")
        
        # Display high risk findings
        high_risks = results.get("high_risk_findings", [])
        if high_risks:
            st.markdown(f"""
            <div style="background-color: #FFEDED; padding: 15px; border-radius: 5px; margin-bottom: 20px; border-left: 4px solid #ef4444;">
                <h4 style="margin-top: 0; color: #ef4444;">High Risk Items ({len(high_risks)})</h4>
            </div>
            """, unsafe_allow_html=True)
            
            for risk in high_risks:
                st.markdown(f"""
                <div style="margin-left: 20px; margin-bottom: 15px; border-left: 3px solid #ef4444; padding-left: 10px;">
                    <p><strong>{risk.get('question', 'Unknown risk')}</strong></p>
                    <p style="margin-top: 5px; color: #555;">{risk.get('details', '')}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Display medium risk findings
        medium_risks = results.get("medium_risk_findings", [])
        if medium_risks:
            st.markdown(f"""
            <div style="background-color: #FFF7ED; padding: 15px; border-radius: 5px; margin-bottom: 20px; border-left: 4px solid #f97316; margin-top: 20px;">
                <h4 style="margin-top: 0; color: #f97316;">Medium Risk Items ({len(medium_risks)})</h4>
            </div>
            """, unsafe_allow_html=True)
            
            for risk in medium_risks:
                st.markdown(f"""
                <div style="margin-left: 20px; margin-bottom: 15px; border-left: 3px solid #f97316; padding-left: 10px;">
                    <p><strong>{risk.get('question', 'Unknown risk')}</strong></p>
                    <p style="margin-top: 5px; color: #555;">{risk.get('details', '')}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Display recommendations
        recommendations = results.get("recommendations", [])
        if recommendations:
            st.markdown("""
            <div style="background-color: #ECFDF5; padding: 15px; border-radius: 5px; margin-bottom: 20px; border-left: 4px solid #10b981; margin-top: 20px;">
                <h4 style="margin-top: 0; color: #047857;">Key Recommendations</h4>
            </div>
            """, unsafe_allow_html=True)
            
            for idx, recommendation in enumerate(recommendations):
                st.markdown(f"""
                <div style="margin-left: 20px; margin-bottom: 15px;">
                    <p><strong>{idx+1}.</strong> {recommendation}</p>
                </div>
                """, unsafe_allow_html=True)
        
        if not high_risks and not medium_risks:
            st.success("No significant privacy risks were identified. Continue to maintain good data protection practices.")
    
    # Tab 2: Detailed Report
    with tab2:
        st.subheader("Detailed DPIA Report")
        
        # Get all report sections
        sections = report_data.get("sections", {})
        
        # Display each section
        for section_key, section_data in sections.items():
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                <h4 style="margin: 0; color: #3f51b5;">{section_data.get('title', 'Section')}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            content = section_data.get('content', '')
            
            # Format the content with line breaks
            formatted_content = content.replace('\n', '<br>')
            
            st.markdown(f"""
            <div style="margin-left: 20px; margin-bottom: 20px;">
                <p>{formatted_content}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Tab 3: Risks & Mitigation
    with tab3:
        st.subheader("Risks & Mitigation Measures")
        
        # Create a dataframe to display risks and mitigation measures
        all_risks = []
        
        # Add high risks
        for risk in results.get("high_risk_findings", []):
            # Find mitigation for this risk
            mitigation = ""
            for step5_key, step5_data in st.session_state.dpia_answers.get("step5", {}).items():
                if isinstance(step5_data, dict) and step5_data.get("question", "") == risk.get("question", ""):
                    mitigation = step5_data.get("measure", "")
                    break
            
            all_risks.append({
                "Risk": risk.get("question", "Unknown"),
                "Risk Level": "High",
                "Details": risk.get("details", ""),
                "Mitigation": mitigation
            })
        
        # Add medium risks
        for risk in results.get("medium_risk_findings", []):
            # Find mitigation for this risk
            mitigation = ""
            for step5_key, step5_data in st.session_state.dpia_answers.get("step5", {}).items():
                if isinstance(step5_data, dict) and step5_data.get("question", "") == risk.get("question", ""):
                    mitigation = step5_data.get("measure", "")
                    break
            
            all_risks.append({
                "Risk": risk.get("question", "Unknown"),
                "Risk Level": "Medium",
                "Details": risk.get("details", ""),
                "Mitigation": mitigation
            })
        
        if all_risks:
            risks_df = pd.DataFrame(all_risks)
            
            # Function to highlight risk level
            def highlight_risk_level(val):
                color = "#FFFFFF"
                if val == "High":
                    color = "#FFEDED"
                elif val == "Medium":
                    color = "#FFF7ED"
                return f'background-color: {color}'
            
            # Display the styled dataframe
            st.dataframe(risks_df.style.applymap(highlight_risk_level, subset=['Risk Level']), 
                         use_container_width=True,
                         hide_index=True)
        else:
            st.info("No significant risks were identified that require mitigation measures.")
    
    # Tab 4: Next Steps
    with tab4:
        st.subheader("Next Steps")
        
        # Get decision information
        decision = st.session_state.dpia_answers.get("step6", {}).get("decision", "Not specified")
        decision_rationale = st.session_state.dpia_answers.get("step6", {}).get("rationale", "")
        
        # Display decision information
        st.markdown(f"""
        <div style="background-color: #f0f9ff; padding: 15px; border-radius: 5px; margin-bottom: 20px; border-left: 4px solid #3b82f6;">
            <h4 style="margin-top: 0; color: #1e40af;">Decision: {decision}</h4>
            <p style="margin-bottom: 0;">{decision_rationale}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Get integration information
        review_schedule = st.session_state.dpia_answers.get("step7", {}).get("review_schedule", "Not specified")
        next_review_date = st.session_state.dpia_answers.get("step7", {}).get("next_review_date", "")
        
        # Display next steps
        st.markdown("""
        <h4>Recommended Actions</h4>
        """, unsafe_allow_html=True)
        
        action_items = []
        
        # Add action item for high risks
        if len(results.get("high_risk_findings", [])) > 0:
            action_items.append("Implement mitigation measures for all high-risk findings immediately")
        
        # Add action item for medium risks
        if len(results.get("medium_risk_findings", [])) > 0:
            action_items.append("Address medium-risk findings according to the timeline specified")
        
        # Add action item for authority consultation if needed
        if st.session_state.dpia_answers.get("step6", {}).get("authority_consultation", "No") == "Yes":
            action_items.append("Proceed with supervisory authority consultation as indicated")
        
        # Add action item for review schedule
        action_items.append(f"Plan for DPIA review in {review_schedule} (Next review: {next_review_date})")
        
        # Add action item if decision requires modifications
        if decision == "Proceed with modifications":
            action_items.append("Implement required modifications before proceeding with processing")
        
        # Add action item for project plan integration
        action_items.append("Integrate DPIA findings into project documentation and execution")
        
        # Display action items
        for item in action_items:
            st.markdown(f"""
            <div style="margin-bottom: 10px; margin-left: 20px;">
                <p>● {item}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Action buttons at the bottom
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Download Full Report", use_container_width=True):
            st.info("Report download functionality would be implemented here")
    
    with col2:
        if st.button("🔄 Start New Assessment", use_container_width=True):
            # Clear session state for a new assessment
            st.session_state.dpia_answers = {}
            st.session_state.dpia_results = {}
            st.session_state.dpia_report_data = {}
            st.session_state.dpia_display_results = False
            st.rerun()
    
    with col3:
        if st.button("📱 Share Results", use_container_width=True):
            st.info("Sharing functionality would be implemented here")