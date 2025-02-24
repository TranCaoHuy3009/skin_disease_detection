import streamlit as st

def init_session_state():
    """Initialize session state variables."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    if 'selected_patient_id' not in st.session_state:
        st.session_state.selected_patient_id = None
    if 'selected_patient_name' not in st.session_state:
        st.session_state.selected_patient_name = None

def reset_session_state_at_home_page():
    """Reset session state variables except for username and authenticated."""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    if 'selected_patient_id' in st.session_state:
        st.session_state.selected_patient_id = None
    if 'selected_patient_name' in st.session_state:
        st.session_state.selected_patient_name = None
    if 'edited_session' in st.session_state:
        st.session_state.edited_session = None
    if 'edited_session_index' in st.session_state:
        st.session_state.edited_session_index = None
    if 'deleted_session' in st.session_state:
        st.session_state.deleted_session = None

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