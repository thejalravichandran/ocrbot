# OCR Workflow for Chatbot

This directory contains the text extraction logic for our OCR Chatbot. The primary script here is `test_ocr.py`, which provides a reusable wrapper around the `pytesseract` library to extract text from images.

## Prerequisites

Before running the OCR workflow, you must have the following installed:

1. **Python Dependencies**:
   You need to install the Python wrappers for Tesseract and the image processing library.
   ```bash
   pip install pytesseract Pillow
   ```

2. **Tesseract OCR Executable**:
   You must have the actual Tesseract engine installed on your underlying operating system.
   
   * **Mac OS**: 
     ```bash
     brew install tesseract
     ```
   * **Windows**:
     Download the Tesseract installer from [UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) and install it. Note the installation path (typically `C:\Program Files\Tesseract-OCR\tesseract.exe`).
   * **Linux (Ubuntu/Debian)**:
     ```bash
     sudo apt-get install tesseract-ocr
     ```

## How to use `test_ocr.py`

### 1. As a Standalone Test Script
You can manually run the script to quickly test text extraction on a sample image.

* Open the file and look for the `if __name__ == "__main__":` block at the bottom.
* Update `SAMPLE_IMAGE_PATH` to point to a valid image on your system.
* If you are on Windows, ensure `TESSERACT_EXE_PATH` is correct. If you are on a Mac or Linux, you can usually pass `tesseract_cmd=None` to the function (since Tesseract is added to your system `PATH` automatically).
* Run the file:
  ```bash
  python test_ocr.py
  ```

### 2. As an Imported Module
The `perform_ocr` function is designed to be easily integrated into the chatbot's main logic (like a message handler or an API endpoint). It accepts an image path and safely returns the extracted text without crashing the main application if the image is missing or an error occurs. 

**Example Integration:**
```python
from ocr.test_ocr import perform_ocr

# Example: Processing an image sent by a user to the chatbot
image_file = "path/to/user/uploaded_image.png"

# Note: tesseract_cmd is omitted/None since the system PATH usually handles it on Mac
extracted_text = perform_ocr(
    image_path=image_file,
    tesseract_cmd=None 
)

if extracted_text:
    print("Successfully read text:", extracted_text)
    # Pass extracted_text to the LLM or chatbot response generator...
else:
    print("Failed to read text from the image.")
```

## Error Handling
The `perform_ocr` function implements basic safety measures:
- **File Validation**: It checks if the image exists at the given path (`os.path.exists()`) before attempting to open it.
- **Exception Catching**: It wraps the Pillow `Image.open()` and Tesseract `image_to_string()` operations in a `try...except` block, preventing application crashes on corrupted images or missing dependencies.
