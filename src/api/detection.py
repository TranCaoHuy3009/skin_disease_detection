from fastapi import FastAPI, File, UploadFile, Form
from typing import List
from loguru import logger
import json
import os
from datetime import datetime
from src.services.detection import create_detection_session
from src.services.patient import get_patient_full_details
from config import USER_ID

detection_api = FastAPI()

UPLOAD_DIR = "local_files/images"

@detection_api.post("/api/detection/{patient_id}")
async def create_detection(
    patient_id: str,
    images: List[UploadFile] = File(...),
    detection_result: str = Form(...)
):
    try:
        # Get patient UUID using patient_id first
        patient = get_patient_full_details(patient_id, user_id=USER_ID)
        if not patient:
            return {"error": "Patient not found"}
        
        patient_uuid = patient['id']  # Get UUID from patient details
        
        # Save uploaded images
        saved_image_paths = []
        for image in images:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{patient_uuid}_{timestamp}_{image.filename}"  # Use UUID in filename
            filepath = os.path.join(UPLOAD_DIR, filename)
            
            with open(filepath, "wb") as f:
                content = await image.read()
                f.write(content)
            saved_image_paths.append(filepath)

        detection_data = json.loads(detection_result)
        
        session_data = {
            "detection_images": saved_image_paths,
            "detection_result": json.dumps(detection_data),
            "detection_date": datetime.now()
        }

        # Pass UUID instead of patient_id
        result = create_detection_session(
            patient_id=patient_uuid,  # Use UUID here
            user_id=USER_ID,
            session_data=session_data
        )
        if not result:
            {"error": "Failed to create detection session"}

        return {"message": "Detection session created", "session_id": result["id"]}

    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        return {"error": str(e)}