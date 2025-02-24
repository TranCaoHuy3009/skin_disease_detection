from datetime import datetime
from loguru import logger
import streamlit as st

from src.services.patient import create_patient
from src.utils.validators import validate_phone_number, validate_required_fields
from src.utils.common import generate_patient_id
from src.utils.qr_code import generate_qr
from config import USER_ID

def render_patient_form():
    """Render the new patient creation form."""
    # Add Font Awesome CSS for icons
    st.markdown("""
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
        .form-container {
            padding: 2rem;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        </style>
    """, unsafe_allow_html=True)

    # Initialize form state if not exists
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {
            'name': '',
            'date_of_birth': datetime.now().date(),
            'sex': 'Male',
            'phone': '',
            'address': '',
            'past_medical_history': '',
            'present_illness_history': ''
        }

    # Create two columns for the form
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Basic Information")
        
        # Patient Name
        name = st.text_input(
            "Patient Name*",
            value=st.session_state.form_data['name'],
            key="patient_name"
        )

        # Date of Birth
        dob = st.date_input(
            "Date of Birth*",
            value=st.session_state.form_data['date_of_birth'],
            min_value=datetime(1900, 1, 1).date(),
            max_value=datetime.now().date(),
            key="patient_dob",
        )

        # Sex Selection
        sex = st.selectbox(
            "Sex*",
            options=['Male', 'Female', 'Other'],
            index=['Male', 'Female', 'Other'].index(st.session_state.form_data['sex']),
            key="patient_sex"
        )

        # Phone Number
        phone = st.text_input(
            "Phone Number*",
            value=st.session_state.form_data['phone'],
            key="patient_phone"
        )

        # Address
        address = st.text_input(
            "Address",
            value=st.session_state.form_data['address'],
            key="patient_address"
        )

    with col2:
        st.markdown("### Medical History")
        
        # Past Medical History
        past_history = st.text_area(
            "Past Medical History",
            value=st.session_state.form_data['past_medical_history'],
            height=164,
            key="past_history"
        )

        # Present Illness History
        present_history = st.text_area(
            "Present Illness History",
            value=st.session_state.form_data['present_illness_history'],
            height=164,
            key="present_history"
        )

    st.markdown("---")

    # Form Actions
    col1, col2 = st.columns([1, 4])
    
    with col1:
        if st.button("Cancel"):
            st.session_state.current_page = 'home'
            st.rerun()

    with col2:
        if st.button("Create Patient", type="primary"):
            # Validate required fields
            required_fields = {
                'name': name,
                'date_of_birth': dob,
                'phone': phone
            }
            
            if not validate_required_fields(required_fields):
                st.error("Please fill in all required fields marked with *")
                return
            
            if not validate_phone_number(phone):
                st.error("Please enter a valid phone number")
                return
            
            # Prepare patient data
            patient_data = {
                'name': name,
                'patient_id': generate_patient_id(),
                'date_of_birth': dob,
                'sex': sex,
                'phone': phone,
                'address': address,
                'past_medical_history': past_history,
                'present_illness_history': present_history
            }
            
            try:
                # Create new patient
                new_patient = create_patient(patient_data, user_id=USER_ID)
                
                if new_patient:
                    st.success("Patient created successfully!")
                    generate_qr(new_patient['patient_id'], f"local_files/qr_code/{new_patient['patient_id']}.png")
                    # Reset form data
                    st.session_state.form_data = {
                        'name': '',
                        'date_of_birth': datetime.now().date(),
                        'sex': 'Male',
                        'phone': '',
                        'address': '',
                        'past_medical_history': '',
                        'present_illness_history': ''
                    }
                    # Redirect to patient list
                    st.session_state.current_page = 'home'
                    st.rerun()
                else:
                    st.error("Failed to create patient")
            
            except Exception as e:
                logger.error(f"Error creating patient: {str(e)}")
                st.error("An error occurred while creating the patient")