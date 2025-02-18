import random
import os
import uuid
from datetime import datetime


def format_datetime(dt):
    """Format datetime object to string."""
    if dt is None:
        return ""
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
    return dt.strftime("%Y-%m-%d %H:%M")

def generate_patient_id():
    """Generate a unique patient number in format P-YYYYMMDD-XXX"""
    return f"P-{datetime.now().strftime('%Y%m%d')}-{random.randint(1, 999):03d}"

def save_uploaded_file(uploaded_file):
    """
    Save an uploaded file to local_files/upload_images directory
    
    Args:
        uploaded_file: UploadedFile object from Streamlit
    
    Returns:
        str: Path where the file was saved
    """
    # Create directory if it doesn't exist
    upload_dir = os.path.join('local_files', 'images')
    os.makedirs(upload_dir, exist_ok=True)
    
    # Full path where file will be saved
    file_path = os.path.join(upload_dir, uploaded_file.name)
    
    # Save the file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path