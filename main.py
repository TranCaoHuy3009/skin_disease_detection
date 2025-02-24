# main.py

import streamlit as st
from loguru import logger
from src.components.login import render_login
from src.components.patient_list import render_patient_list
from src.components.patient_detail import render_patient_detail
from src.components.patient_form import render_patient_form
from src.utils.session import init_session_state, is_authenticated, reset_session_state_at_home_page

# Set page config
st.set_page_config(
    page_title="Skin Disease Detection",
    page_icon="🏥",
    layout="wide"
)

def main():
    # Initialize session state
    init_session_state()
    
    # Check authentication
    if not is_authenticated():
        logger.debug(f"Session state at login page:\n{st.session_state}")
        render_login()
    else:
        # Sidebar navigation
        with st.sidebar:
            st.title("Navigation")
            
            if st.button("Home"):
                st.session_state.current_page = 'home'
                st.session_state.selected_patient_id = None
                st.rerun()
                
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.rerun()
        
        # Main content
        if st.session_state.current_page == 'home':
            reset_session_state_at_home_page()
            logger.debug(f"Session state at home page:\n{st.session_state}")
            st.title("Skin Disease Detection")
            render_patient_list()
            
        elif st.session_state.current_page == 'new_patient':
            logger.debug(f"Session state at new patient page:\n{st.session_state}")
            st.title("New Patient")
            render_patient_form()
            # st.write("New patient form coming soon...")
            if st.button("Back to Patient List"):
                st.session_state.current_page = 'home'
                st.rerun()
                
        elif st.session_state.current_page == 'patient_detail':
            logger.debug(f"Session state at patient detail page:\n{st.session_state}")
            st.title("Patient Profile")
            st.write(f"Viewing patient: {st.session_state.selected_patient_name}")
            render_patient_detail()
            if st.button("Back to Patient List"):
                st.session_state.current_page = 'home'
                st.session_state.selected_patient_id = None
                st.rerun()

if __name__ == "__main__":
    main()
