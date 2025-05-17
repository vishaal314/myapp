"""
Simple DPIA (Data Protection Impact Assessment) Tool

This standalone application provides a simplified DPIA form 
that helps organizations assess data protection risks.
"""

import streamlit as st
import uuid
from datetime import datetime, timedelta
import json
import io
import base64

# Basic translation function
def _(key, default=None):
    """Simple translation function"""
    translations = {
        'en': {
            'scan.dpia_assessment': 'Data Protection Impact Assessment (DPIA)',
            'scan.dpia_processing': 'Processing DPIA assessment...',
            'scan.report_generated': 'Report Generated',
            'scan.high_risk': 'High Risk',
            'scan.medium_risk': 'Medium Risk',
            'scan.low_risk': 'Low Risk',
            'scan.risk_level': 'Risk Level',
            'scan.recommendations': 'Recommendations',
            'scan.dpia_report': 'DPIA Report',
            'scan.download_report': 'Download Report',
        }
    }
    
    language = st.session_state.get('language', 'en')
    if language not in translations:
        language = 'en'
        
    return translations[language].get(key, default if default else key)

class DPIAScanner:
    """DPIA Scanner class to handle assessment logic"""
    
    def __init__(self, language='en'):
        self.language = language
        
    def _get_assessment_categories(self):
        """Get assessment categories and questions"""
        return {
            "data_nature": {
                "name": "Nature of Data Processing",
                "description": "Questions about what personal data you're processing and how",
                "questions": [
                    "We process special category data (race, religion, health, etc.)",
                    "We process personal data of vulnerable individuals (e.g., children)",
                    "We process personal data on a large scale",
                    "We combine data from multiple sources",
                    "We use innovative technologies or processing methods"
                ]
            },
            "data_control": {
                "name": "Control and Consent",
                "description": "Questions about individual control and consent",
                "questions": [
                    "Data subjects can easily withdraw consent",
                    "We have a lawful basis for all processing activities",
                    "We have systems to respond to data subject access requests",
                    "We have transparent privacy notices",
                    "We conduct regular data protection training"
                ]
            },
            "security_measures": {
                "name": "Security and Protection Measures",
                "description": "Questions about your security controls",
                "questions": [
                    "We have strong access controls to personal data",
                    "We encrypt personal data during storage and transmission",
                    "We have data breach detection and response plans",
                    "We conduct regular security audits",
                    "We have data minimization and retention policies"
                ]
            }
        }
        
    def perform_assessment(self, answers):
        """Process DPIA answers and produce risk assessment results"""
        results = {
            "scan_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "overall_score": 0,
            "risk_level": "low",
            "category_scores": {},
            "findings": [],
            "recommendations": []
        }
        
        categories = self._get_assessment_categories()
        total_score = 0
        max_score = 0
        
        for category, category_answers in answers.items():
            if category not in categories:
                continue
                
            cat_questions = categories[category]['questions']
            cat_score = 0
            questions_answered = 0
            
            for i, answer_value in enumerate(category_answers):
                if i >= len(cat_questions):
                    continue
                    
                # For category "data_nature", high score means higher risk
                if category == "data_nature":
                    risk_value = answer_value
                    if answer_value > 0:  # any non-zero value indicates some risk
                        severity = "high" if answer_value == 2 else "medium"
                        results["findings"].append({
                            "category": category,
                            "question_idx": i,
                            "severity": severity,
                            "description": f"Risk identified: {cat_questions[i]}"
                        })
                else:
                    # For other categories, low score means higher risk (inverse scoring)
                    risk_value = 2 - answer_value
                    if risk_value > 0:  # any non-zero value indicates some risk
                        severity = "high" if risk_value == 2 else "medium"
                        results["findings"].append({
                            "category": category,
                            "question_idx": i,
                            "severity": severity,
                            "description": f"Compliance gap: {cat_questions[i]}"
                        })
                
                cat_score += risk_value
                questions_answered += 1
                
            if questions_answered > 0:
                # Calculate score as percentage of maximum possible risk
                category_risk_score = (cat_score / (questions_answered * 2)) * 100
                results["category_scores"][category] = round(category_risk_score)
                total_score += cat_score
                max_score += questions_answered * 2
        
        # Calculate overall score
        if max_score > 0:
            overall_risk_percentage = (total_score / max_score) * 100
            results["overall_score"] = round(overall_risk_percentage)
            
            # Determine overall risk level
            if overall_risk_percentage >= 70:
                results["risk_level"] = "high"
            elif overall_risk_percentage >= 40:
                results["risk_level"] = "medium"
            else:
                results["risk_level"] = "low"
        
        # Generate recommendations
        self._generate_recommendations(results)
        
        return results
    
    def _generate_recommendations(self, results):
        """Generate recommendations based on findings"""
        high_risks = [f for f in results["findings"] if f["severity"] == "high"]
        medium_risks = [f for f in results["findings"] if f["severity"] == "medium"]
        
        # Add recommendations for high risks
        if high_risks:
            results["recommendations"].append({
                "priority": "high",
                "action": "Conduct a full DPIA with your Data Protection Officer"
            })
            results["recommendations"].append({
                "priority": "high",
                "action": "Review and remediate all high-risk findings immediately"
            })
        
        # Add category-specific recommendations
        categories = self._get_assessment_categories()
        for category in categories:
            if category in results["category_scores"] and results["category_scores"][category] >= 50:
                if category == "data_nature":
                    results["recommendations"].append({
                        "priority": "medium",
                        "action": "Review your data inventory and minimize sensitive data collection"
                    })
                elif category == "data_control":
                    results["recommendations"].append({
                        "priority": "medium",
                        "action": "Enhance transparency and user control mechanisms"
                    })
                elif category == "security_measures":
                    results["recommendations"].append({
                        "priority": "medium",
                        "action": "Strengthen your security controls and encryption methods"
                    })
        
        # General recommendations
        if results["risk_level"] != "low":
            results["recommendations"].append({
                "priority": "medium",
                "action": "Implement a regular DPIA review process"
            })
            
        results["recommendations"].append({
            "priority": "low",
            "action": "Document all data processing activities in detail"
        })

def generate_dpia_report(assessment_results):
    """Generate a report from DPIA assessment results"""
    report_data = {
        "title": "Data Protection Impact Assessment (DPIA) Report",
        "generated_date": datetime.now().strftime("%Y-%m-%d"),
        "overall_risk": assessment_results["risk_level"],
        "overall_score": assessment_results["overall_score"],
        "categories": [],
        "findings": [],
        "recommendations": []
    }
    
    # Add category scores
    for category, score in assessment_results.get("category_scores", {}).items():
        cat_risk = "high" if score >= 70 else "medium" if score >= 40 else "low"
        report_data["categories"].append({
            "name": category.replace("_", " ").title(),
            "score": score,
            "risk_level": cat_risk
        })
    
    # Add findings
    for finding in assessment_results.get("findings", []):
        report_data["findings"].append({
            "category": finding["category"].replace("_", " ").title(),
            "severity": finding["severity"],
            "description": finding["description"]
        })
    
    # Add recommendations
    for rec in assessment_results.get("recommendations", []):
        report_data["recommendations"].append({
            "priority": rec["priority"],
            "action": rec["action"]
        })
    
    return report_data

def show_dpia_results(results, report_data, scanner):
    """Display the DPIA assessment results with visualizations"""
    st.success(f"✅ {_('scan.report_generated')}")
    
    # Display overall risk level with colorful indicator
    risk_level = results["risk_level"]
    risk_color = "#FF4B4B" if risk_level == "high" else "#FFA421" if risk_level == "medium" else "#4BD964"
    
    st.markdown(f"""
    <div style="background-color: {risk_color}; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
        <h2 style="color: white; margin: 0;">{_('scan.risk_level')}: {_(f'scan.{risk_level}_risk')}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Display category scores
    st.subheader("Risk Assessment by Category")
    
    for category in report_data["categories"]:
        score = category["score"]
        cat_color = "#FF4B4B" if score >= 70 else "#FFA421" if score >= 40 else "#4BD964"
        
        st.markdown(f"""
        <div style="margin-bottom: 10px;">
            <span style="font-weight: bold;">{category["name"]}</span>
            <div style="background-color: #E0E0E0; height: 20px; border-radius: 10px; margin-top: 5px;">
                <div style="background-color: {cat_color}; width: {score}%; height: 20px; border-radius: 10px;">
                    <span style="padding-left: 10px; color: white; font-weight: bold;">{score}%</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Display findings
    if report_data["findings"]:
        st.subheader("Key Findings")
        
        for finding in report_data["findings"]:
            severity = finding["severity"]
            icon = "🔴" if severity == "high" else "🟠" if severity == "medium" else "🟢"
            
            st.markdown(f"{icon} **{finding['category']}**: {finding['description']}")
    
    # Display recommendations
    if report_data["recommendations"]:
        st.subheader(_("scan.recommendations"))
        
        for rec in report_data["recommendations"]:
            priority = rec["priority"]
            icon = "🔴" if priority == "high" else "🟠" if priority == "medium" else "🟢"
            
            st.markdown(f"{icon} {rec['action']}")
    
    # Create a download link for the report
    report_json = json.dumps(report_data, indent=2)
    
    st.download_button(
        label=_("scan.download_report"),
        data=report_json,
        file_name=f"dpia_report_{datetime.now().strftime('%Y%m%d')}.json",
        mime="application/json",
        key="download_dpia_report",
        help="Download the DPIA report as a JSON file"
    )
    
    # Reset button
    if st.button("Start New Assessment", type="primary"):
        for key in ['dpia_form_submitted', 'dpia_results', 'dpia_report_data', 'ultra_simple_dpia_answers']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

def run_simple_dpia():
    """Run a simplified DPIA assessment"""
    st.title(_("scan.dpia_assessment"))
    
    scanner = DPIAScanner(language=st.session_state.get('language', 'en'))
    assessment_categories = scanner._get_assessment_categories()
    
    if 'ultra_simple_dpia_answers' not in st.session_state:
        st.session_state.ultra_simple_dpia_answers = {}
        for category in assessment_categories:
            question_count = len(assessment_categories[category]['questions'])
            st.session_state.ultra_simple_dpia_answers[category] = [0] * question_count
    
    st.markdown("""
    ### What is a DPIA?
    
    A Data Protection Impact Assessment (DPIA) helps you identify and minimize data protection risks in your project or system.
    This simplified assessment will guide you through key questions to evaluate privacy risks.
    """)
    
    st.info("📝 Please answer all questions in each category to complete the assessment.")
    
    answers = {}
    
    with st.form("simple_dpia_form"):
        st.markdown("""
        ## Assessment Instructions
        
        Please answer all questions in each category below. Select values using the dropdown menus:
        - **No**: The statement doesn't apply to your processing activities
        - **Partially**: The statement partially applies to your processing activities
        - **Yes**: The statement fully applies to your processing activities
        
        Click the Submit button at the bottom when you've completed all questions.
        """)
        
        tabs = st.tabs([assessment_categories[cat]['name'] for cat in assessment_categories])
        
        for i, category in enumerate(assessment_categories):
            with tabs[i]:
                st.markdown(f"### {assessment_categories[category]['name']}")
                st.markdown(f"*{assessment_categories[category]['description']}*")
                st.markdown("---")
                
                category_answers = []
                for q_idx, question in enumerate(assessment_categories[category]['questions']):
                    current_val = st.session_state.ultra_simple_dpia_answers[category][q_idx]
                    key = f"simple_{category}_{q_idx}"
                    options = ["No", "Partially", "Yes"]
                    st.markdown(f"**Q{q_idx+1}: {question}**")
                    selected = st.selectbox(
                        "Select answer:", 
                        options,
                        index=current_val,
                        key=key,
                        label_visibility="collapsed"
                    )
                    value = options.index(selected)
                    st.session_state.ultra_simple_dpia_answers[category][q_idx] = value
                    category_answers.append(value)
                    st.markdown("---")
                answers[category] = category_answers
        
        submit = st.form_submit_button("Submit DPIA Assessment", type="primary", use_container_width=True)

    if submit:
        # Validate that all questions are answered
        incomplete = False
        for category in assessment_categories:
            if len(answers.get(category, [])) != len(assessment_categories[category]['questions']):
                incomplete = True
                break
                
        if incomplete:
            st.error("❌ Please complete all questions in each category before submitting.")
            return
        
        st.session_state.ultra_simple_dpia_form_submitted = True
        for category in assessment_categories:
            if category in answers:
                st.session_state.ultra_simple_dpia_answers[category] = answers[category]
        st.rerun()

    if 'ultra_simple_dpia_form_submitted' in st.session_state and st.session_state.ultra_simple_dpia_form_submitted:
        del st.session_state.ultra_simple_dpia_form_submitted
        try:
            with st.spinner(_("scan.dpia_processing")):
                assessment_results = scanner.perform_assessment(
                    answers=st.session_state.ultra_simple_dpia_answers.copy()
                )

                # Ensure essential fields
                assessment_results.setdefault("scan_id", str(uuid.uuid4()))
                assessment_results.setdefault("timestamp", datetime.utcnow().isoformat())

                report_data = generate_dpia_report(assessment_results)

                st.session_state.dpia_results = assessment_results
                st.session_state.dpia_report_data = report_data
                st.session_state.dpia_form_submitted = True

            show_dpia_results(
                st.session_state.dpia_results,
                st.session_state.dpia_report_data,
                scanner
            )
        
        except Exception as e:
            st.error(f"Error processing DPIA assessment: {str(e)}")
            st.exception(e)

    elif 'dpia_form_submitted' in st.session_state and st.session_state.dpia_form_submitted:
        try:
            show_dpia_results(
                st.session_state.dpia_results,
                st.session_state.dpia_report_data,
                scanner
            )
        except Exception as e:
            st.error(f"Error displaying DPIA results: {str(e)}")
            if st.button("Retry Assessment", type="primary"):
                for key in ['dpia_form_submitted', 'dpia_results', 'dpia_report_data']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

def main():
    """Main entry point for the application"""
    st.set_page_config(
        page_title="DPIA Assessment Tool",
        page_icon="🔒",
        layout="wide"
    )
    
    # Initialize session state
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    
    # App header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("Data Protection Impact Assessment (DPIA) Tool")
        st.markdown("A simplified tool for conducting Data Protection Impact Assessments")
    
    # Run the DPIA form
    run_simple_dpia()

if __name__ == "__main__":
    main()