"""
GDPR HTML Report Generator

A simple Streamlit app that generates an HTML report for GDPR compliance results.
"""

import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="GDPR HTML Report Generator",
    page_icon="📊",
    layout="centered"
)

st.title("GDPR HTML Report Generator")
st.markdown("Generate an HTML report from your GDPR scan results with one click.")

# Mock scan results (in a real app, this would come from a database or API)
results = {
    "compliance_score": 75,
    "high_risk": 2,
    "total_findings": 8,
    "scan_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "repository_info": {
        "url": "https://github.com/example/repo",
        "branch": "main"
    },
    "compliance_scores": {
        "Lawfulness, Fairness and Transparency": 70,
        "Purpose Limitation": 80,
        "Data Minimization": 65,
        "Accuracy": 85,
        "Storage Limitation": 75,
        "Integrity and Confidentiality": 85,
        "Accountability": 65
    },
    "findings": [
        {
            "principle": "Data Minimization",
            "severity": "high",
            "description": "User data is stored longer than necessary without clear purpose",
            "remediation": "Implement data retention policies"
        },
        {
            "principle": "Lawfulness, Fairness and Transparency",
            "severity": "medium",
            "description": "Privacy policy does not clearly explain data processing purposes",
            "remediation": "Update privacy policy with specific processing purposes"
        },
        {
            "principle": "Accountability",
            "severity": "high",
            "description": "No data processing records maintained",
            "remediation": "Implement data processing documentation"
        }
    ]
}

if st.button("Generate & Download HTML Report", type="primary", use_container_width=True):
    with st.spinner("Creating HTML report..."):
        # Generate HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>GDPR Compliance Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                h1 {{ color: #2c3e50; text-align: center; }}
                h2 {{ color: #3498db; margin-top: 30px; }}
                h3 {{ color: #2980b9; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #3498db; color: white; }}
                tr:hover {{ background-color: #f5f5f5; }}
                .high {{ color: #e74c3c; font-weight: bold; }}
                .medium {{ color: #f39c12; font-weight: bold; }}
                .low {{ color: #27ae60; font-weight: bold; }}
                .summary {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; }}
                .metrics {{ display: flex; flex-wrap: wrap; margin: 20px 0; }}
                .metric {{ flex: 1; min-width: 200px; padding: 15px; margin: 10px; background-color: #ecf0f1; border-radius: 5px; text-align: center; }}
                .metric .value {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
                .progress-bar {{ 
                    height: 10px; 
                    background-color: #ecf0f1; 
                    border-radius: 5px; 
                    margin-top: 5px;
                }}
                .progress {{ 
                    height: 100%; 
                    background-color: #3498db; 
                    border-radius: 5px; 
                }}
                footer {{ margin-top: 50px; text-align: center; color: #7f8c8d; font-size: 14px; }}
            </style>
        </head>
        <body>
            <h1>GDPR Compliance Report</h1>
            
            <div class="summary">
                <h2>Executive Summary</h2>
                <p>This report presents the findings of a GDPR compliance assessment conducted on {results.get('scan_date')}.</p>
                
                <div class="metrics">
                    <div class="metric">
                        <div>Overall Compliance</div>
                        <div class="value">{results.get('compliance_score')}%</div>
                        <div class="progress-bar">
                            <div class="progress" style="width: {results.get('compliance_score')}%;"></div>
                        </div>
                    </div>
                    
                    <div class="metric">
                        <div>High Risk Findings</div>
                        <div class="value">{results.get('high_risk')}</div>
                    </div>
                    
                    <div class="metric">
                        <div>Total Findings</div>
                        <div class="value">{results.get('total_findings')}</div>
                    </div>
                </div>
            </div>
            
            <h2>Compliance by GDPR Principle</h2>
            <table>
                <tr>
                    <th>GDPR Principle</th>
                    <th>Compliance Score</th>
                    <th>Status</th>
                </tr>
        """
        
        # Add principle scores to the table
        if "compliance_scores" in results and isinstance(results["compliance_scores"], dict):
            for principle, score in results["compliance_scores"].items():
                status_class = "high" if score >= 80 else "medium" if score >= 60 else "low"
                status_text = "Good" if score >= 80 else "Needs Improvement" if score >= 60 else "Critical"
                html_content += f"""
                <tr>
                    <td>{principle}</td>
                    <td>{score}%</td>
                    <td class="{status_class}">{status_text}</td>
                </tr>
                """
        
        # Calculate average score
        avg_score = sum(results["compliance_scores"].values()) / len(results["compliance_scores"])
        
        html_content += f"""
                <tr>
                    <th>Overall Compliance</th>
                    <th>{avg_score:.1f}%</th>
                    <th class="{("high" if avg_score >= 80 else "medium" if avg_score >= 60 else "low")}">{("Good" if avg_score >= 80 else "Needs Improvement" if avg_score >= 60 else "Critical")}</th>
                </tr>
            </table>
            
            <h2>Key Findings</h2>
        """
        
        # Add findings
        if "findings" in results and isinstance(results["findings"], list) and results["findings"]:
            for i, finding in enumerate(results["findings"]):
                if isinstance(finding, dict):
                    principle = finding.get("principle", "Unknown")
                    severity = finding.get("severity", "medium")
                    description = finding.get("description", "No description provided")
                    remediation = finding.get("remediation", "No remediation suggested")
                    
                    html_content += f"""
                    <h3>{i+1}. {principle} <span class="{severity}">({severity.upper()})</span></h3>
                    <p><strong>Description:</strong> {description}</p>
                    <p><strong>Remediation:</strong> {remediation}</p>
                    """
        else:
            html_content += "<p>No specific findings were detected in this scan.</p>"
        
        # Add repository info 
        if "repository_info" in results and isinstance(results["repository_info"], dict):
            repo_url = results["repository_info"].get("url", "Unknown")
            branch = results["repository_info"].get("branch", "main")
            
            html_content += f"""
            <h2>Scan Information</h2>
            <p><strong>Repository:</strong> {repo_url}</p>
            <p><strong>Branch:</strong> {branch}</p>
            <p><strong>Scan Date:</strong> {results.get('scan_date')}</p>
            """
        
        # Add next steps section
        html_content += """
            <h2>Next Steps</h2>
            <ol>
                <li>Review the findings and prioritize remediation efforts</li>
                <li>Address high-risk issues first</li>
                <li>Implement data protection by design principles</li>
                <li>Schedule a follow-up scan to track progress</li>
            </ol>
            
            <footer>
                <p>Generated by DataGuardian Pro on """ + datetime.now().strftime('%Y-%m-%d') + """</p>
            </footer>
        </body>
        </html>
        """
        
        # Show success message
        st.success("✅ HTML report generated successfully!")
        
        # Create download button
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"GDPR_Compliance_Report_{timestamp}.html"
        
        st.download_button(
            label="📥 Download HTML Report",
            data=html_content,
            file_name=filename,
            mime="text/html",
            key="download_html_report",
            use_container_width=True
        )
        
        # Preview
        with st.expander("Preview Report"):
            st.markdown(
                f'<iframe srcdoc="{html_content.replace(chr(34), chr(39))}" width="100%" height="500" frameborder="0"></iframe>',
                unsafe_allow_html=True
            )

# Show mock data for reference
with st.expander("View Mock Data (For Development)"):
    st.json(results)