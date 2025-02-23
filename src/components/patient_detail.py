from datetime import datetime
from loguru import logger
import json
import streamlit as st
import pandas as pd
import random

from src.services.patient import get_patient_full_details, update_patient_details
from src.services.detection import create_detection_session
from src.utils.common import save_uploaded_file
from config import USER_ID

def render_patient_detail():
    """Render detailed patient information page."""
    # Add Font Awesome CSS
    st.markdown("""
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        """, unsafe_allow_html=True)
    
    patient_id = st.session_state.get('selected_patient_id')
    logger.debug(f"Selected patient ID: {patient_id}")
    
    if not patient_id:
        st.error("No patient selected")
        return
    
    patient = get_patient_full_details(patient_id, user_id=USER_ID)
    logger.debug(f"Patient details: {patient}")
    
    if not patient:
        st.error("Patient not found")
        return

    # st.markdown("## Patient Information Dashboard")
    
    # Top Container
    top_container = st.container()
    with top_container:
        left_col, right_col = st.columns(2)
        
        with left_col:
            st.markdown("### Basic Information")
            render_patient_info(patient)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with right_col:
            st.markdown("### Medical History")
            render_medical_history(patient)
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Bottom Container - Detection Sessions
    bottom_container = st.container()
    with bottom_container:
        st.markdown("### Detection Sessions")
        render_detection_sessions(patient)
        st.markdown('</div>', unsafe_allow_html=True)

def render_patient_info(patient):
    """Display and allow editing of patient basic information."""
    col1, col2 = st.columns(2)

    with col1:
        current_sex = patient.get('sex', 'Male')
        
        # CSS for the avatar and layout
        st.markdown("""
            <style>
            .avatar-wrapper {
                display: flex;
                justify-content: center;
                align-items: center;
                width: 100%;
                padding: 50px 0;
            }
            .avatar-container {
                width: 180px;
                height: 180px;
                background-color: #f3f4f6;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            }
            .male-avatar { background: linear-gradient(45deg, #3B82F6, #60A5FA); }
            .female-avatar { background: linear-gradient(45deg, #EC4899, #F472B6); }
            .other-avatar { background: linear-gradient(45deg, #6B7280, #9CA3AF); }
            .avatar-image {
                width: 65%;
                height: 65%;
                filter: brightness(0) invert(1);
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Avatar section
        avatar_html = get_avatar_html(current_sex)
        st.markdown(avatar_html, unsafe_allow_html=True)
    
    with col2:
        name = st.text_input("Name", value=patient.get('name', ''))
        dob = st.date_input("Date of Birth", 
            value=patient.get('date_of_birth', datetime.now().date()),
            min_value=datetime(1900, 1, 1).date(),
            max_value=datetime.now().date()
        )
        phone = st.text_input("Phone", value=patient.get('phone', ''))
        sex = st.selectbox("Sex", 
            options=['Male', 'Female', 'Other'], 
            index=['Male', 'Female', 'Other'].index(patient.get('sex', 'Male'))
        )
        address = st.text_input("Address", value=patient.get('address', ''))
    
    if st.button("Update Patient Information", key="update_patient_info"):
        update_data = {
            'name': name,
            'sex': sex,
            'date_of_birth': dob,
            'phone': phone,
            'address': address
        }
        
        updated_patient = update_patient_details(
            user_id=USER_ID,
            patient_id=patient['id'],
            patient_data=update_data,
        )
        
        if updated_patient:
            st.success("Patient information updated successfully!")
        else:
            st.error("Failed to update patient information")

def render_medical_history(patient):
    """Display and allow editing of patient medical history."""
    past_history = st.text_area(
        "Past Medical History", 
        value=patient.get('past_medical_history', ''),
        height=164
    )
    
    present_history = st.text_area(
        "Present Illness History", 
        value=patient.get('present_illness_history', ''),
        height=164
    )
    
    if st.button("Update Medical History", key="update_medical_history"):
        update_data = {
            'name': patient['name'],
            'sex': patient['sex'],
            'date_of_birth': patient['dob'],
            'past_medical_history': past_history,
            'present_illness_history': present_history
        }
        
        updated_patient = update_patient_details(
            user_id=USER_ID,
            patient_id=patient['id'],
            patient_data=update_data,
        )
        
        if updated_patient:
            st.success("Medical history updated successfully!")
        else:
            st.error("Failed to update medical history")

def render_detection_sessions(patient):
    """Display patient detection sessions in a table format with image previews."""
    # Display existing detection sessions
    detection_sessions = patient.get('detection_sessions', [])
    
    if not detection_sessions:
        st.info("No detection sessions found for this patient")
        return

    # Rest of the display code remains the same...
    st.markdown("""
        <style>
        .header-row {
            background-color: #f0f2f6;
            padding: 10px;
            font-weight: bold;
            border-bottom: 2px solid #e0e0e0;
        }
        .table-row {
            border-bottom: 1px solid #e0e0e0;
            padding: 8px 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Create header row
    header_cols = st.columns([3, 1, 2, 3, 3])
    headers = ['Images', 'Date', 'Detection Result', 'Diagnostic Result', 'Follow-up Plan']
    
    for col, header in zip(header_cols, headers):
        with col:
            st.markdown(f"**{header}**")
    
    st.markdown("---")
    
    # Display table rows
    for index, session in enumerate(detection_sessions):
        detection_images = session.get('detection_images', [])
        
        cols = st.columns([3, 1, 2, 3, 3])
        
        with cols[0]:
            if detection_images:
                if st.button(f"View {len(detection_images)} images", key=f"img_btn_{index}"):
                    gallery_cols = st.columns(len(detection_images))
                    for img_idx, img in enumerate(detection_images):
                        with gallery_cols[img_idx]:
                            st.write(f"Image {img_idx + 1}")
                            st.image(img['image_path'], use_container_width=False)
            else:
                st.write("No images")
        
        with cols[1]:
            date_str = session['detection_date']
            formatted_date = date_str.strftime('%Y-%m-%d')
            st.write(formatted_date)
        
        with cols[2]:
            if session.get('detection_result'):
                with st.expander("View Results"):
                    st.json(session['detection_result'])
            else:
                st.write("No results yet")
        
        with cols[3]:
            st.write(session.get('diagnostic_result', 'No diagnosis'))
        
        with cols[4]:
            st.write(session.get('follow_up_plan', 'No plan'))
        
        st.markdown("---")

def get_avatar_html(sex):
    """Generate avatar HTML based on sex."""
    avatar_html = '<div class="avatar-wrapper"><div class="avatar-container '
    
    if sex == 'Male':
        avatar_html += 'male-avatar">'
        avatar_html += """
            <svg class="avatar-image" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" fill="currentColor"/>
            </svg>
        """
    elif sex == 'Female':
        avatar_html += 'female-avatar">'
        avatar_html += """
            <svg class="avatar-image" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M10 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" fill="currentColor"/>
            </svg>
        """
    else:
        avatar_html += 'other-avatar">'
        avatar_html += """
            <svg class="avatar-image" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 6a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7z" fill="currentColor"/>
            </svg>
        """
    
    avatar_html += '</div></div>'
    return avatar_html