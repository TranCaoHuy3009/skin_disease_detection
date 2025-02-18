import streamlit as st

def init_session_state():
    """Initialize session state variables."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None

def set_authenticated(username: str):
    """Set the session as authenticated."""
    st.session_state.authenticated = True
    st.session_state.username = username

def clear_session():
    """Clear the session state."""
    st.session_state.authenticated = False
    st.session_state.username = None

def is_authenticated() -> bool:
    """Check if the user is authenticated."""
    return st.session_state.authenticated