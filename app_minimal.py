import streamlit as st
import os
import uuid
import logging
from datetime import datetime

# Test minimal app without pandas/numpy
st.set_page_config(
    page_title="DataGuardian Pro",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("DataGuardian Pro - Test Version")
st.write("Testing basic functionality without pandas/numpy dependencies")

# Test the image scanner without pandas
if st.button("Test Image Scanner"):
    st.success("Basic functionality working!")
    
# Add minimal file uploader
uploaded_files = st.file_uploader("Choose images", accept_multiple_files=True, type=["png", "jpg", "jpeg"])

if uploaded_files:
    st.write(f"Uploaded {len(uploaded_files)} files")
    for file in uploaded_files:
        st.write(f"- {file.name}")