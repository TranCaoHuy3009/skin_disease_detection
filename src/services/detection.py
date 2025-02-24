import psycopg2
from loguru import logger
from psycopg2.extras import RealDictCursor
from config import DATABASE_URL
from datetime import datetime

def update_detection_session(detection_session_id, user_id, session_data):
    """
    Update detection session details.
    
    Args:
        detection_session_id: UUID of the detection session
        user_id: UUID of the doctor updating the session
        session_data: Dictionary containing session details to update
            {
                'detection_result': dict,
                'diagnostic_result': str,
                'follow_up_plan': str,
                'detection_date': datetime,
                'detection_images': list  # Optional - list of new images to add
            }
    Returns:
        Updated detection session data if successful, None otherwise
    """
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Start transaction
        conn.autocommit = False
        
        # Update detection session details
        query = """
        UPDATE detection_sessions
        SET 
            diagnostic_result = COALESCE(%s, diagnostic_result),
            follow_up_plan = COALESCE(%s, follow_up_plan),
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s AND user_id = %s
        RETURNING *
        """
        
        cur.execute(query, (
            session_data.get('diagnostic_result'),
            session_data.get('follow_up_plan'),
            detection_session_id,
            user_id
        ))
        
        updated_session = cur.fetchone()
        
        # If new images are provided, add them to detection_images table
        if session_data.get('detection_images'):
            images_query = """
            INSERT INTO detection_images (
                detection_session_id,
                image_path,
                created_at
            ) VALUES (%s, %s, CURRENT_TIMESTAMP)
            RETURNING id, image_path, created_at
            """
            
            new_images = []
            for image_path in session_data['detection_images']:
                cur.execute(images_query, (detection_session_id, image_path))
                new_images.append(cur.fetchone())
            
            # Add new images to the updated session data
            if updated_session:
                updated_session['detection_images'] = new_images
        
        # If update successful, fetch all images for this session
        if updated_session:
            images_query = """
            SELECT 
                id,
                image_path,
                created_at
            FROM detection_images
            WHERE detection_session_id = %s
            ORDER BY created_at DESC
            """
            
            cur.execute(images_query, (detection_session_id,))
            updated_session['detection_images'] = cur.fetchall()
        
        # Commit transaction
        conn.commit()
        
        return updated_session
        
    except Exception as e:
        logger.error(f"Error updating detection session: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def create_detection_session(patient_id, user_id, session_data):
    """
    Create a new detection session for a patient.
    
    Args:
        patient_id: UUID of the patient
        user_id: UUID of the doctor
        session_data: Dictionary containing session details
            {
                'detection_result': dict,
                'diagnostic_result': str,
                'follow_up_plan': str,
                'detection_date': datetime,
                'detection_images': list  # List of image paths
            }
    Returns:
        Newly created detection session data if successful, None otherwise
    """
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Start transaction
        conn.autocommit = False
        
        # Create detection session
        query = """
        INSERT INTO detection_sessions (
            patient_id,
            user_id,
            detection_result,
            diagnostic_result,
            follow_up_plan,
            detection_date,
            created_at,
            updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        RETURNING *
        """
        
        cur.execute(query, (
            patient_id,
            user_id,
            session_data.get('detection_result'),
            session_data.get('diagnostic_result'),
            session_data.get('follow_up_plan'),
            session_data.get('detection_date', datetime.now())
        ))
        
        new_session = cur.fetchone()
        
        # If images are provided, add them to detection_images table
        if session_data.get('detection_images'):
            images_query = """
            INSERT INTO detection_images (
                detection_session_id,
                image_path,
                created_at
            ) VALUES (%s, %s, CURRENT_TIMESTAMP)
            RETURNING id, image_path, created_at
            """
            
            new_images = []
            for image_path in session_data['detection_images']:
                cur.execute(images_query, (new_session['id'], image_path))
                new_images.append(cur.fetchone())
            
            new_session['detection_images'] = new_images
        
        # Commit transaction
        conn.commit()
        
        return new_session
        
    except Exception as e:
        logger.error(f"Error creating detection session: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def delete_detection_session(detection_session_id, user_id):
    """
    Delete a detection session from the database.
    
    Args:
        detection_session_id: UUID of the session to delete
        user_id: UUID of the doctor deleting the session
    
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
        DELETE FROM detection_sessions 
        WHERE id = %s AND user_id = %s
        """
        
        cur.execute(query, (detection_session_id, user_id))
        conn.commit()
        return True
        
    except Exception as e:
        logger.error(f"Error deleting detection session: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()