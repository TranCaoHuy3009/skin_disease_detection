import streamlit as st
import pandas as pd
from datetime import datetime
from loguru import logger

from src.services.patient import get_all_patients
from src.utils.common import format_datetime
from config import USER_ID

def render_patient_list():
    """Render the patient list table component."""
    # Create header with title and New Patient button on the same line
    col1, col2 = st.columns([6, 1])
    with col1:
        st.write("### Patient List")
    with col2:
        if st.button("➕ New Patient", use_container_width=True):
            st.session_state.current_page = "new_patient"
            st.rerun()

    # Add some spacing
    st.write("")

    # Fetch patients data
    patients = get_all_patients(user_id=USER_ID)
    if not patients:
        st.info("No patients found. Create a new patient to get started.")
        return

    # Convert to DataFrame and format dates
    df = pd.DataFrame(patients)

    # Format datetime columns
    if not df.empty and "Created Date" in df.columns:
        df["Created Date"] = pd.to_datetime(df["Created Date"]).dt.strftime("%Y-%m-%d %H:%M")
        df["Updated Date"] = pd.to_datetime(df["Updated Date"]).dt.strftime("%Y-%m-%d %H:%M")

    # Ensure correct column order
    columns_order = ['Name'] + [col for col in df.columns if col not in ['Name', 'id']]
    display_columns = columns_order  # Excluding 'id' from display
    logger.debug(f"Display columns: {display_columns}")

    # Create column headers with proper widths
    cols = st.columns([2 if col == 'Name' else 1 for col in display_columns])
    
    # Display column headers
    for col, header in zip(cols, display_columns):
        col.write(f"**{header}**")
    
    # Display rows with clickable names
    for idx, row in df.iterrows():
        row_cols = st.columns([2 if col == 'Name' else 1 for col in display_columns])
        
        # Handle Name column with button
        with row_cols[0]:
            if st.button(str(row['Name']), key=f"patient_{row['id']}", use_container_width=True):
                st.session_state.current_page = "patient_detail"
                st.session_state.selected_patient_id = row['ID']
                st.session_state.selected_patient_name = row['Name']
                st.rerun()
        
        # Display other columns
        col_index = 1
        for col in display_columns[1:]:  # Skip Name as it's already handled
            with row_cols[col_index]:
                st.write(str(row[col]))
            col_index += 1

    # Add some spacing at the bottom
    st.write("")