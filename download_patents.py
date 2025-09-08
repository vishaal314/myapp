#!/usr/bin/env python3
"""
Simple download interface for patent PDF documents
"""

import streamlit as st
import os

def main():
    st.set_page_config(
        page_title="Patent Documents Download",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("📄 Patent Documents Download")
    st.markdown("### AI Model Scanner - Netherlands Patent Application")
    st.markdown("---")
    
    # PDF files information
    pdf_files = [
        {
            'name': 'Patent_Description.pdf',
            'title': '📋 Patent Description',
            'description': 'Complete technical description of the AI Model Scanner invention'
        },
        {
            'name': 'Patent_Conclusions.pdf', 
            'title': '📝 Patent Conclusions (Conclusies)',
            'description': '15 patent claims in Dutch language for Netherlands filing'
        },
        {
            'name': 'Patent_Drawings.pdf',
            'title': '🎨 Patent Drawings & Formulas', 
            'description': 'System architecture diagrams and mathematical formulas'
        },
        {
            'name': 'Patent_Extract.pdf',
            'title': '📊 Patent Extract Summary',
            'description': 'Executive summary with key technical specifications'
        }
    ]
    
    # Create download interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Available Documents:")
        
        for pdf in pdf_files:
            if os.path.exists(pdf['name']):
                file_size = os.path.getsize(pdf['name'])
                file_size_kb = round(file_size / 1024, 1)
                
                with st.container():
                    st.markdown(f"**{pdf['title']}**")
                    st.markdown(f"*{pdf['description']}*")
                    st.markdown(f"📦 File size: {file_size_kb} KB")
                    
                    # Download button
                    with open(pdf['name'], 'rb') as file:
                        st.download_button(
                            label=f"📥 Download {pdf['name']}",
                            data=file.read(),
                            file_name=pdf['name'],
                            mime='application/pdf',
                            key=pdf['name']
                        )
                    st.markdown("---")
            else:
                st.warning(f"❌ {pdf['name']} not found")
    
    with col2:
        st.markdown("### Filing Information:")
        st.info("""
        **Netherlands Patent Office**  
        🌐 https://mijnoctrooi.rvo.nl/bpp-portal/nl/
        
        **Filing Fees:**  
        💶 Application: €80  
        💶 Search: €794  
        💶 **Total: €874**
        
        **Required Authentication:**  
        🔐 DigiD login required
        """)
        
        st.success("""
        ✅ **Patent Ready!**  
        All documents formatted for Netherlands Patent Office submission.
        """)

if __name__ == "__main__":
    main()