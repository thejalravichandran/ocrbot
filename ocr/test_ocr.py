import os
import pytesseract
from PIL import Image

def perform_ocr(image_path: str, tesseract_cmd: str = None) -> str:
    """
    Performs Optical Character Recognition (OCR) on an image using Tesseract.

    Args:
        image_path (str): The absolute or relative path to the image file.
        tesseract_cmd (str, optional): The path to the tesseract executable.
            If None, pytesseract will assume tesseract is in your system's PATH.

    Returns:
        str: The extracted text from the image. Returns an empty string if it fails.
    """
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    if not os.path.exists(image_path):
        print(f"Error: The file at {image_path} does not exist.")
        return ""

    try:
        # Load the image
        image = Image.open(image_path)
        
        # Perform OCR
        extracted_text = pytesseract.image_to_string(image)
        return extracted_text

    except Exception as e:
        print(f"An error occurred while processing the image: {e}")
        return ""

if __name__ == "__main__":
    # -------------------------------------------------------------------
    # Configuration
    # Note: On a Mac, Tesseract is usually available in the system PATH
    # (e.g., /usr/local/bin/tesseract or /opt/homebrew/bin/tesseract),
    # so `TESSERACT_EXE_PATH` might be set to None.
    # -------------------------------------------------------------------
    TESSERACT_EXE_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    SAMPLE_IMAGE_PATH = r"C:\Users\User\Pictures\Screenshots\Screenshot 2024-12-13 230153.png"
    
    print(f"Starting OCR extraction for: {SAMPLE_IMAGE_PATH}")
    
    text = perform_ocr(
        image_path=SAMPLE_IMAGE_PATH,
        tesseract_cmd=TESSERACT_EXE_PATH
    )
    
    print("\n--- Extracted Text ---")
    print(text)
    print("----------------------\n")
