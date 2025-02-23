import psycopg2
from psycopg2.extras import RealDictCursor
from loguru import logger

from config import DATABASE_URL

def get_all_patients(user_id):
    """
    Retrieve all patients for a specific doctor from the database.
    
    Args:
        user_id: UUID of the doctor
    Returns:
        List of patients with their basic information
    """
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                id,
                patient_id as "ID",
                name as "Name",
                sex as "Sex",
                age as "Age",
                created_at as "Created Date",
                updated_at as "Updated Date"
            FROM patients
            WHERE user_id = %s
            ORDER BY created_at DESC
        """
        
        cur.execute(query, (user_id,))
        patients = cur.fetchall()

        return patients
    except Exception as e:
        logger.error(f"Error fetching patients: {e}")
        return []
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def create_patient(patient_data, user_id):
    """
    Create a new patient record in the database.
    
    Args:
        patient_data: Dictionary containing patient information
        user_id: UUID of the doctor creating the patient
    """
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            INSERT INTO patients (
                user_id, patient_id, name, sex, date_of_birth, 
                phone, address, past_medical_history, present_illness_history
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING *
        """
        logger.debug(f"Creating patient with data: {patient_data}")
        
        cur.execute(query, (
            user_id,
            patient_data['patient_id'],
            patient_data['name'],
            patient_data['sex'],
            patient_data['date_of_birth'],
            patient_data.get('phone', ''),
            patient_data.get('address', ''),
            patient_data.get('past_medical_history', ''),
            patient_data.get('present_illness_history', '')
        ))
        
        new_patient = cur.fetchone()
        conn.commit()
        
        return new_patient
    except Exception as e:
        logger.error(f"Error creating patient: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def get_patient_full_details(patient_id, user_id):
    """
    Retrieve comprehensive patient information including:
    - Basic patient details
    - Detection sessions
    - Detection images
    
    Args:
        patient_id: Business identifier of the patient (e.g., 'PT250216513')
        user_id: UUID of the requesting doctor
    """
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # First, get the patient's UUID using the business identifier
        id_query = """
        SELECT id
        FROM patients
        WHERE patient_id = %s AND user_id = %s
        """
        cur.execute(id_query, (patient_id, user_id))
        patient_uuid_record = cur.fetchone()
        
        if not patient_uuid_record:
            return None
            
        patient_uuid = patient_uuid_record['id']
        
        # Fetch patient basic details
        query = """
        SELECT 
            p.id,
            p.patient_id,
            p.name,
            p.sex,
            p.age,
            p.date_of_birth AS dob,
            p.phone,
            p.address,
            p.past_medical_history,
            p.present_illness_history,
            p.created_at,
            p.updated_at
        FROM patients p
        WHERE p.id = %s AND p.user_id = %s
        """
        cur.execute(query, (patient_uuid, user_id))
        patient_details = cur.fetchone()
        
        if not patient_details:
            return None
        
        # Fetch detection sessions using patient UUID
        sessions_query = """
        SELECT 
            id,
            detection_date,
            detection_result,
            diagnostic_result,
            follow_up_plan,
            created_at,
            updated_at
        FROM detection_sessions
        WHERE patient_id = %s AND user_id = %s
        ORDER BY detection_date DESC
        """
        cur.execute(sessions_query, (patient_uuid, user_id))
        patient_details['detection_sessions'] = cur.fetchall()
        
        # Fetch detection images for each session
        for session in patient_details['detection_sessions']:
            images_query = """
            SELECT 
                id,
                image_path,
                created_at
            FROM detection_images
            WHERE detection_session_id = %s
            """
            cur.execute(images_query, (session['id'],))
            session['detection_images'] = cur.fetchall()
        
        return patient_details
    
    except Exception as e:
        logger.error(f"Error fetching patient full details: {e}")
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def update_patient_details(patient_id, user_id, patient_data):
    """
    Update patient details.
    
    Args:
        patient_id: UUID of the patient
        user_id: UUID of the doctor updating the patient
        patient_data: Dictionary containing patient details
    """
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Update patient details
        query = """
        UPDATE patients
        SET 
            name = %s,
            sex = %s,
            date_of_birth = %s,
            phone = %s,
            address = %s,
            past_medical_history = %s,
            present_illness_history = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s AND user_id = %s
        RETURNING *
        """
        
        cur.execute(query, (
            patient_data['name'],
            patient_data['sex'],
            patient_data['date_of_birth'],
            patient_data.get('phone', ''),
            patient_data.get('address', ''),
            patient_data.get('past_medical_history', ''),
            patient_data.get('present_illness_history', ''),
            patient_id,
            user_id
        ))
        
        updated_patient = cur.fetchone()
        conn.commit()
        
        if updated_patient:
            return get_patient_full_details(updated_patient['patient_id'], user_id)
        return None
        
    except Exception as e:
        logger.error(f"Error updating patient details: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()