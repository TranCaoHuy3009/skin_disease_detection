# src/components/login.py

import streamlit as st
from src.services.authentication import verify_credentials
from src.utils.session import set_authenticated

def render_login():
    """Render the login form and handle login logic."""
    st.title("Login")
    
    # Center the login form using columns
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Add some spacing
        st.write("")
        st.write("")
        
        # Create a card-like container for the login form
        with st.container():
            st.markdown("### Sign In")
            st.write("Please enter your credentials to continue.")
            
            # Login form
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.button("Login", use_container_width=True):
                if verify_credentials(username, password):
                    set_authenticated(username)
                    st.rerun()  # Updated from experimental_rerun()
                else:
                    st.error("Invalid username or password")
            
            # Add some information about the default account
            st.write("")
            st.markdown("---")