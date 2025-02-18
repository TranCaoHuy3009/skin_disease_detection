import psycopg2
from datetime import datetime, timedelta
import random
from psycopg2.extras import RealDictCursor
from config import DATABASE_URL
import json
import os
import glob

from src.utils.common import generate_patient_id

def get_image_paths():
    """Get list of all image files from images folder"""
    image_pattern = os.path.join('local_files', 'images', '*')
    image_files = glob.glob(image_pattern)
    if not image_files:
        raise Exception("No images found in local_files/images/ directory")
    return image_files

def clear_existing_data(cur):
    """Clear all existing data from the tables in the correct order"""
    try:
        # Delete in reverse order of dependencies
        cur.execute("DELETE FROM detection_images;")
        cur.execute("DELETE FROM detection_sessions;")
        cur.execute("DELETE FROM patients;")
        print("Successfully cleared existing data!")
    except Exception as e:
        print(f"Error clearing existing data: {e}")
        raise

def insert_dummy_data():
    conn = None
    cur = None
    try:
        # Get available image paths
        image_paths = get_image_paths()
        
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # First, clear existing data
        clear_existing_data(cur)

        # Get the admin user's ID
        cur.execute("SELECT user_id FROM users WHERE username = 'admin_user'")
        admin_user = cur.fetchone()
        if not admin_user:
            print("Admin user not found!")
            return
        
        doctor_id = admin_user['user_id']

        # Sample patient data
        patients = [
            {
                "user_id": doctor_id,
                "patient_id": generate_patient_id(),
                "name": "John Smith",
                "sex": "Male",
                "date_of_birth": "1985-03-15",
                "phone": "123-456-7890",
                "address": "123 Main St, City",
                "past_medical_history": "History of hypertension",
                "present_illness_history": "Skin rash for 2 weeks"
            },
            {
                "user_id": doctor_id,
                "patient_id": generate_patient_id(),
                "name": "Mary Johnson",
                "sex": "Female",
                "date_of_birth": "1992-07-22",
                "phone": "234-567-8901",
                "address": "456 Oak Ave, Town",
                "past_medical_history": "None",
                "present_illness_history": "Itchy skin patches"
            },
            {
                "user_id": doctor_id,
                "patient_id": generate_patient_id(),
                "name": "David Wilson",
                "sex": "Male",
                "date_of_birth": "1978-11-30",
                "phone": "345-678-9012",
                "address": "789 Pine Rd, Village",
                "past_medical_history": "Asthma",
                "present_illness_history": "Skin lesions"
            },
            {
                "user_id": doctor_id,
                "patient_id": generate_patient_id(),
                "name": "Sarah Brown",
                "sex": "Female",
                "date_of_birth": "1990-05-18",
                "phone": "456-789-0123",
                "address": "321 Elm St, County",
                "past_medical_history": "Eczema",
                "present_illness_history": "Skin inflammation"
            },
            {
                "user_id": doctor_id,
                "patient_id": generate_patient_id(),
                "name": "Michael Davis",
                "sex": "Male",
                "date_of_birth": "1982-09-25",
                "phone": "567-890-1234",
                "address": "654 Maple Dr, State",
                "past_medical_history": "None",
                "present_illness_history": "First skin symptoms"
            },
            {
                "user_id": doctor_id,
                "patient_id": generate_patient_id(),
                "name": "Emma Wilson",
                "sex": "Female",
                "date_of_birth": "1995-12-03",
                "phone": "678-901-2345",
                "address": "789 Birch Ln, City",
                "past_medical_history": "Allergies",
                "present_illness_history": "Recurring rash"
            },
            {
                "user_id": doctor_id,
                "patient_id": generate_patient_id(),
                "name": "James Taylor",
                "sex": "Male",
                "date_of_birth": "1975-08-14",
                "phone": "789-012-3456",
                "address": "432 Cedar St, Town",
                "past_medical_history": "Diabetes",
                "present_illness_history": "Skin irritation"
            },
            {
                "user_id": doctor_id,
                "patient_id": generate_patient_id(),
                "name": "Olivia Martin",
                "sex": "Female",
                "date_of_birth": "1988-04-29",
                "phone": "890-123-4567",
                "address": "567 Walnut Ave, Village",
                "past_medical_history": "None",
                "present_illness_history": "Skin patches"
            },
            {
                "user_id": doctor_id,
                "patient_id": generate_patient_id(),
                "name": "William Anderson",
                "sex": "Male",
                "date_of_birth": "1980-01-10",
                "phone": "901-234-5678",
                "address": "890 Pine St, County",
                "past_medical_history": "Hypertension",
                "present_illness_history": "Skin condition"
            },
            {
                "user_id": doctor_id,
                "patient_id": generate_patient_id(),
                "name": "Sophia Clarke",
                "sex": "Female",
                "date_of_birth": "1993-06-07",
                "phone": "012-345-6789",
                "address": "123 Oak Rd, State",
                "past_medical_history": "Asthma",
                "present_illness_history": "Skin problems"
            }
        ]

        # Insert patients
        for patient in patients:
            query = """
                INSERT INTO patients (
                    user_id, patient_id, name, sex, date_of_birth, 
                    phone, address, past_medical_history, present_illness_history
                ) VALUES (
                    %(user_id)s, %(patient_id)s, %(name)s, %(sex)s, %(date_of_birth)s, 
                    %(phone)s, %(address)s, %(past_medical_history)s, %(present_illness_history)s
                ) RETURNING id;
            """
            cur.execute(query, patient)
            patient_id = cur.fetchone()['id']

            # Create detection sessions for each patient
            for i in range(random.randint(1, 3)):
                # Create detection session
                session_query = """
                    INSERT INTO detection_sessions (
                        patient_id, user_id, detection_date,
                        detection_result, diagnostic_result, follow_up_plan
                    ) VALUES (
                        %s, %s, %s, %s::jsonb, %s, %s
                    ) RETURNING id;
                """
                
                detection_date = datetime.now() - timedelta(days=random.randint(1, 30))
                
                # Generate detection result
                detection_result = json.dumps({
                    'confidence': round(random.uniform(0.7, 0.99), 2),
                    'detection': 'Atopic Dermatitis'
                })

                diagnostic_result = "Patient presents with erythematous, scaly patches typical of atopic dermatitis. Lesions are primarily located on flexural areas. Moderate pruritis reported."
                follow_up_plan = f"1. Continue current treatment regimen\n2. Follow up in {random.randint(1, 4)} weeks\n3. Return sooner if symptoms worsen"

                cur.execute(session_query, (
                    patient_id,
                    doctor_id,
                    detection_date,
                    detection_result,
                    diagnostic_result,
                    follow_up_plan
                ))
                
                session_id = cur.fetchone()['id']

                # Add detection images for each session
                for j in range(random.randint(2, 4)):
                    image_query = """
                        INSERT INTO detection_images (
                            detection_session_id, image_path
                        ) VALUES (
                            %s, %s
                        );
                    """
                    
                    # Randomly select an image path
                    random_image_path = random.choice(image_paths)
                    
                    cur.execute(image_query, (
                        session_id,
                        random_image_path
                    ))

        conn.commit()
        print("Successfully inserted dummy data!")

    except Exception as e:
        print(f"Error inserting dummy data: {e}")
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    insert_dummy_data()