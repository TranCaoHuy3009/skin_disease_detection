import qrcode
import cv2
import numpy as np

def generate_qr(text, filename="qr_code.png"):
    """
    Generate a QR code from text and save it as an image
    
    Args:
        text (str): The text to encode in the QR code
        filename (str): The filename to save the QR code image (default: qr_code.png)
    
    Returns:
        str: Path to the saved QR code image
    """
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # Add data
    qr.add_data(text)
    qr.make(fit=True)
    
    # Create an image from the QR Code
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # Save the image
    qr_image.save(filename)
    return filename

def read_qr(image_path):
    """
    Read a QR code from an image using OpenCV
    
    Args:
        image_path (str): Path to the image containing the QR code
    
    Returns:
        str: Decoded text from the QR code
    """
    # Read the image
    image = cv2.imread(image_path)
    
    # Initialize the QR code detector
    qr_detector = cv2.QRCodeDetector()
    
    # Detect and decode the QR code
    data, bbox, straight_qrcode = qr_detector.detectAndDecode(image)
    
    if bbox is not None:
        return data
    else:
        return "No QR code found"
