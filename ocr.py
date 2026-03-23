import pytesseract
from pdf2image import convert_from_bytes, convert_from_path
import os
import csv
import tempfile
import streamlit as st
from PIL import Image
import concurrent.futures

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Function to extract images from the uploaded PDF
def extract_images_from_pdf(pdf_file=None, pdf_path=None, poppler_path=None, page_range=None):
    try:
        image_paths = []
        temp_dir = tempfile.TemporaryDirectory()  # Temporary directory to save images

        if pdf_file:
            # If file is uploaded via Streamlit (bytes)
            images = convert_from_bytes(pdf_file.read(), first_page=page_range[0] if page_range else 1, 
                                        last_page=page_range[1] if page_range else None, poppler_path=poppler_path)
        elif pdf_path:
            # If file path is given manually
            images = convert_from_path(pdf_path, first_page=page_range[0] if page_range else 1, 
                                        last_page=page_range[1] if page_range else None, poppler_path=poppler_path)
        else:
            st.error("No PDF source provided!")
            return [], None

        for i, image in enumerate(images):
            image_path = os.path.join(temp_dir.name, f"page_{i + 1}.png")
            image.save(image_path, 'PNG')
            image_paths.append(image_path)

        return image_paths, temp_dir
    except Exception as e:
        st.error(f"Error extracting images from PDF: {e}")
        return [], None

# Function to extract text from a single image
def extract_text_from_image(image_path):
    try:
        text = pytesseract.image_to_string(image_path)
        return text
    except Exception as e:
        st.error(f"Error extracting text from image {image_path}: {e}")
        return ""

# Function to extract text from images in parallel
def extract_text_from_images_parallel(image_paths):
    extracted_text = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(extract_text_from_image, image_paths)
        extracted_text.extend(results)
    return extracted_text

# Function to save extracted text to CSV
def save_text_to_csv(image_paths, text_data, csv_filename):
    try:
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Image", "Text"])
            for image_path, text in zip(image_paths, text_data):
                writer.writerow([image_path, text])
        st.success(f"Extracted text successfully saved to {csv_filename}")
    except Exception as e:
        st.error(f"Error saving text to CSV: {e}")

# Streamlit UI
def main():
    st.title("PDF Text Extracting Bot")
    st.write("You can either drag and drop a PDF file or specify a file path to extract text.")
    
    # Option to upload PDF
    pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    # Manual PDF path input
    manual_pdf_path = st.text_input("Or provide a manual PDF file path (optional):", 
                                    value=r"C:\path\to\your\pdf_file.pdf")

    # Poppler path input
    poppler_path = st.text_input("Poppler path (optional):", 
                                 value=r"C:\Users\User\Downloads\Release-24.08.0-0 (1)\poppler-24.08.0\Library\bin")

    output_csv = st.text_input("Output CSV file path:", 
                               value=r"C:\Users\User\Desktop\pdfqnachatbotoffline\ocr_images.csv")

    # Page range input
    page_range = st.text_input("Page range (optional, e.g., 1-5):")
    page_range = [int(i) for i in page_range.split('-')] if page_range else None

    if st.button("Extract Text"):
        # Check if PDF file is uploaded or manual path is provided
        if not pdf_file and not manual_pdf_path:
            st.error("Please upload a PDF file or provide a manual file path.")
            return

        # Extract images from PDF
        image_paths, temp_dir = extract_images_from_pdf(pdf_file=pdf_file, pdf_path=manual_pdf_path, 
                                                        poppler_path=poppler_path, page_range=page_range)

        if not image_paths:
            st.error("Failed to extract images. Check the PDF file or path.")
            return

        # Display progress bar for extracting text
        with st.spinner('Extracting text from images...'):
            # Extract text from images concurrently
            extracted_text = extract_text_from_images_parallel(image_paths)

        if not extracted_text or all(text.strip() == "" for text in extracted_text):
            st.warning("No text could be extracted. Please check the PDF quality or Tesseract setup.")
            return

        # Save text to CSV
        save_text_to_csv(image_paths, extracted_text, output_csv)

        st.success("Text extraction completed! You can now analyze the results.")
        st.write("Preview of Extracted Text:")
        for i, text in enumerate(extracted_text):
            st.write(f"**Page {i + 1}:**\n{text[:500]}...")  # Display first 500 characters

if __name__ == "__main__":
    main()
