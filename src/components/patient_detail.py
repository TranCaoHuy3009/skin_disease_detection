from datetime import datetime
from loguru import logger
import os
import streamlit as st

from src.services.patient import get_patient_full_details, update_patient_details, delete_patient
from src.services.detection import update_detection_session, delete_detection_session
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
    
    if not patient:
        st.error("Patient not found")
        return

    # Add navigation/delete icons
    nav_container = st.container()
    with nav_container:
        col1, col2, col3 = st.columns([1, 1, 20])
        with col1:
            if st.button("🔄", help="Refresh patient details"):
                st.rerun()
        with col2:
            if st.button("🗑️", help="Delete patient"):
                st.session_state.delete_confirmation = True

    # Handle delete confirmation
    if st.session_state.get('delete_confirmation', False):
        with st.container():
            st.warning(f"Are you sure you want to delete patient: {patient['name']}?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes, Delete", key="confirm_delete"):
                    success = delete_patient(patient_id, USER_ID)
                    if success:
                        st.success("Patient deleted successfully!")
                        st.session_state.delete_confirmation = False
                        st.session_state.current_page = "patient_list"
                        st.rerun()
                    else:
                        st.error("Failed to delete patient")
            with col2:
                if st.button("Cancel", key="cancel_delete"):
                    st.session_state.delete_confirmation = False
                    st.rerun()
    
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
        qr_code_path = f"local_files/qr_code/{patient['patient_id']}.png"
        if os.path.exists(qr_code_path):
            col1.markdown("<div style='text-align: center; margin-top: 30px;'>", unsafe_allow_html=True)
            col1.image(qr_code_path, width=300)
            col1.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error("QR Code not found")
    
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
        .delete-btn {
            font-size: 14px;  /* Smaller font size for delete icon */
            padding: 0px 8px;
            line-height: 1;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Update header columns to include delete button column
    header_cols = st.columns([3, 1, 2, 3, 3, 0.5, 0.5])
    headers = ['Images', 'Date', 'Detection Result', 'Diagnostic Result', 'Follow-up Plan', '', '']  # Empty header for delete button
    
    for col, header in zip(header_cols, headers):
        if header != "":
            with col:
                st.markdown(f"**{header}**")
    
    st.markdown("---")
    
    # Display table rows
    for index, session in enumerate(detection_sessions):
        detection_images = session.get('detection_images', [])
        
        # Update columns to match header
        cols = st.columns([3, 1, 2, 3, 3, 0.5, 0.5])
        
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

        with cols[5]:
            if st.button("✏️", key=f"edit_session_{session['id']}", help="Edit session"):
                st.session_state["edited_session"] = session['id']
                st.session_state["edited_session_index"] = index

        with cols[6]:
            if st.button("🗑️", key=f"delete_session_{session['id']}", help="Delete session"):
                st.session_state["deleted_session"] = session['id']

    # Edit Dialog
    edited_session = st.session_state.get("edited_session", None)
    if edited_session:
        logger.debug(f"Edited session: {edited_session}")
        with st.container():
            st.markdown("### Edit Session Details")
            
            col1, col2 = st.columns(2)
            with col1:
                temp_diagnostic = st.text_area(
                    "Diagnostic Result",
                    value=detection_sessions[st.session_state["edited_session_index"]].get('diagnostic_result', ''),
                    height=150,
                    key=f"edit_diagnostic_{edited_session}"
                )
            
            with col2:
                temp_followup = st.text_area(
                    "Follow-up Plan",
                    value=detection_sessions[st.session_state["edited_session_index"]].get('follow_up_plan', ''),
                    height=150,
                    key=f"edit_followup_{edited_session}"
                )

            updated_data = {
                'diagnostic_result': temp_diagnostic,
                'follow_up_plan': temp_followup,
            }
            col1, col2, col3 = st.columns([0.6, 0.8, 10])
            with col1:
                if st.button("Save", key=f"save_edit_{edited_session}"):
                    update_detection_session(edited_session, USER_ID, updated_data)
                    st.session_state["edited_session"] = None
                    st.rerun()
            
            with col2:
                if st.button("Cancel", key=f"cancel_edit_{edited_session}"):
                    st.session_state["edited_session"] = None
                    st.rerun()
    
    # Handle delete confirmation
    deleted_session = st.session_state.get("deleted_session", None)
    if deleted_session:
        logger.debug(f"Deleted session: {deleted_session}")
        with st.container():
            st.warning("Are you sure you want to delete this detection session?")
            
            col1, col2, col3 = st.columns([0.6, 0.8, 10])
            with col1:
                if st.button("Yes", key=f"confirm_delete_session_{session['id']}"):
                    delete_detection_session(deleted_session, USER_ID)
                    st.session_state[f"deleted_session"] = None
                    st.rerun()
            
            with col2:
                if st.button("Cancel", key=f"cancel_delete_session_{session['id']}"):
                    st.session_state[f"deleted_session"] = None
                    st.rerun()
        
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