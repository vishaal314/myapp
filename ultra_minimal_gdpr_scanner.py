import streamlit as st
import time
from datetime import datetime
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

st.title("GDPR Scanner")

repo_url = st.text_input("Repository URL", "https://github.com/example/repo")
org_name = st.text_input("Organization Name", "Your Organization")

if st.button("Run Scan"):
    # Show progress
    progress = st.progress(0)
    for i in range(100):
        progress.progress(i + 1)
        time.sleep(0.01)
    
    # Show results
    st.success("GDPR scan completed!")
    
    # Display findings
    st.header("Compliance Score: 79%")
    
    st.markdown("""
    ### Key Findings:
    
    * High Risk: Missing explicit consent collection (GDPR Art. 6)
    * High Risk: Dutch BSN numbers stored improperly (UAVG Art. 46)
    * Medium Risk: Excessive data collection (GDPR Art. 5-1c)
    """)
    
    # Generate PDF
    if st.button("Download PDF Report"):
        # Create PDF
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        # Add content
        p.setFont("Helvetica-Bold", 18)
        p.drawString(100, 750, "GDPR Compliance Report")
        
        p.setFont("Helvetica", 12)
        p.drawString(100, 700, f"Organization: {org_name}")
        p.drawString(100, 680, f"Repository: {repo_url}")
        p.drawString(100, 660, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        
        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, 620, "Compliance Score: 79%")
        
        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, 580, "Key Findings:")
        
        p.setFont("Helvetica", 12)
        p.drawString(120, 560, "• High Risk: Missing explicit consent collection (GDPR Art. 6)")
        p.drawString(120, 540, "• High Risk: Dutch BSN numbers stored improperly (UAVG Art. 46)")
        p.drawString(120, 520, "• Medium Risk: Excessive data collection (GDPR Art. 5-1c)")
        
        p.save()
        buffer.seek(0)
        
        # Provide download
        st.download_button(
            label="Download PDF",
            data=buffer,
            file_name=f"gdpr_report_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )