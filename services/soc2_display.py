"""
SOC2 Display Utilities

This module provides specialized display functions for SOC2 scan results.
"""

import streamlit as st
import pandas as pd

def display_soc2_findings(scan_results):
    """
    Display SOC2 findings with TSC criteria mapping.
    
    Args:
        scan_results: Dictionary containing SOC2 scan results
    """
    # Display findings table
    st.subheader("Compliance Findings")
    if 'findings' in scan_results and scan_results['findings']:
        findings_df = pd.DataFrame([
            {
                "Risk": f.get("risk_level", "Unknown").upper(),
                "Category": f.get("category", "Unknown").capitalize(),
                "Description": f.get("description", "No description"),
                "File": f.get("file", "Unknown"),
                "Line": f.get("line", "N/A"),
                "SOC2 TSC": ", ".join(f.get("soc2_tsc_criteria", []))
            }
            for f in scan_results['findings'][:10]  # Show top 10 findings
        ])
        st.dataframe(findings_df, use_container_width=True)
        
        if len(scan_results['findings']) > 10:
            st.info(f"Showing 10 of {len(scan_results['findings'])} findings. Download the PDF report for complete results.")
            
    # Display SOC2 TSC Checklist
    if 'soc2_tsc_checklist' in scan_results:
        st.subheader("SOC2 Trust Services Criteria Checklist")
        
        # Create tabs for each SOC2 category
        checklist = scan_results['soc2_tsc_checklist']
        categories = ["security", "availability", "processing_integrity", "confidentiality", "privacy"]
        
        soc2_tabs = st.tabs([c.capitalize() for c in categories])
        
        for i, category in enumerate(categories):
            with soc2_tabs[i]:
                # Filter criteria for this category
                category_criteria = {k: v for k, v in checklist.items() if v.get("category") == category}
                if not category_criteria:
                    st.info(f"No {category.capitalize()} criteria assessed.")
                    continue
                    
                # Create dataframe for this category
                criteria_data = []
                for criterion, details in category_criteria.items():
                    criteria_data.append({
                        "Criterion": criterion,
                        "Description": details.get("description", ""),
                        "Status": details.get("status", "not_assessed").upper(),
                        "Violations": len(details.get("violations", []))
                    })
                
                # Sort by criterion
                criteria_data.sort(key=lambda x: x["Criterion"])
                
                # Create dataframe
                df = pd.DataFrame(criteria_data)
                st.dataframe(df, use_container_width=True)
                
                # Summary for this category
                statuses = [details.get("status", "not_assessed") for details in category_criteria.values()]
                passed = statuses.count("passed")
                failed = statuses.count("failed")
                warning = statuses.count("warning")
                info = statuses.count("info")
                
                st.write(f"**Summary**: {passed} Passed, {failed} Failed, {warning} Warning, {info} Info")
                
                # Show violations if any criteria failed
                if failed > 0 or warning > 0:
                    with st.expander("View Violations"):
                        for criterion, details in category_criteria.items():
                            violations = details.get("violations", [])
                            if violations:
                                st.markdown(f"**{criterion}**: {details.get('description', '')}")
                                for v in violations:
                                    st.markdown(f"- **{v.get('risk_level', '').upper()}**: {v.get('description', '')} in `{v.get('file', '')}:{v.get('line', '')}`")
                                st.markdown("---")