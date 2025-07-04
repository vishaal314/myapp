import streamlit as st

# Configure page FIRST
st.set_page_config(
    page_title="DataGuardian Pro",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple landing page test
def main():
    st.title("🛡️ DataGuardian Pro")
    st.subheader("Enterprise Privacy Compliance Platform")
    
    st.write("Testing basic functionality...")
    
    # Basic test
    if st.button("Test Button"):
        st.success("App is working!")
    
    st.write("If you see this message, the basic app structure is working.")

if __name__ == "__main__":
    main()