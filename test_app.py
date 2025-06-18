import streamlit as st

# Simple test app to verify Streamlit is working
st.set_page_config(
    page_title="DataGuardian Pro Test",
    page_icon="🔒",
    layout="wide"
)

st.title("DataGuardian Pro - Test Mode")
st.write("If you can see this, Streamlit is working correctly.")

# Test basic functionality
if st.button("Test Button"):
    st.success("Button clicked successfully!")

# Test session state
if 'counter' not in st.session_state:
    st.session_state.counter = 0

if st.button("Increment Counter"):
    st.session_state.counter += 1

st.write(f"Counter: {st.session_state.counter}")