import streamlit as st

# Simple test to verify landing page components work
st.title("Landing Page Test")

# Test basic HTML rendering
st.markdown("""
<div style="background-color: #f0f8ff; padding: 20px; border-radius: 10px;">
    <h2 style="color: #1e3a8a;">DataGuardian Pro</h2>
    <p>Test HTML rendering for landing page</p>
</div>
""", unsafe_allow_html=True)

# Test the landing page function
try:
    from utils.landing_page import display_landing_page_grid
    st.write("Landing page module imported successfully")
    
    # Try to call the function
    display_landing_page_grid()
    st.success("Landing page function executed successfully")
    
except Exception as e:
    st.error(f"Error importing or executing landing page: {str(e)}")
    import traceback
    st.code(traceback.format_exc())