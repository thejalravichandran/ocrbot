# PDF Text Extracting & AI Summarization Bot

This application is a smart Optical Character Recognition (OCR) chatbot built with **Python** and **Streamlit**. It extracts text from uploaded PDF files (or images) and uses a local **Large Language Model (Llama 3 via Ollama)** to automatically generate context summaries and explain the architecture of technical documents.

## 🚀 Features

*   **PDF text extraction:** Upload any PDF and extract its text page-by-page using Tesseract OCR.
*   **AI Context Summarization:** Automatically summarizes the context or architecture of the extracted text using a local LLM (`llama3`).
*   **Data Export:** Extracted results are safely saved to a clean CSV file (`ocr_images.csv`) for future analysis.
*   **Modern UI:** Interactive web interface with progress spinners built on Streamlit.
*   **Secure & Local:** AI summarization is handled entirely locally via Ollama, ensuring zero data leakage.

## ⚙️ Prerequisites

Before running the application, make sure your system has the following installed:

1.  **Tesseract OCR Engine**
    *   **Mac OS**: `brew install tesseract`
    *   **Windows**: Download the installer from UB-Mannheim.
    *   **Linux**: `sudo apt-get install tesseract-ocr`
2.  **Poppler (for PDF processing)**
    *   **Mac OS**: `brew install poppler`
    *   **Windows / Linux**: Required to convert PDF pages into images format for Tesseract.
3.  **Ollama (for AI Summarization)**
    *   Install Ollama from [ollama.com](https://ollama.com/)
    *   Pull the `llama3` model by running: 
        ```bash
        ollama run llama3
        ```

## 🛠️ Installation & Setup

1.  **Navigate directly into the project folder:**
    ```bash
    cd "ocr chatbot"
    ```

2.  **Activate the Virtual Environment:**
    We use an isolated environment to prevent library conflicts. Wait until the `(mac_env)` prefix appears in your terminal.
    ```bash
    source mac_env/bin/activate
    ```

3.  *(Optional)* **Verify Dependencies:**
    You must have `streamlit`, `pytesseract`, `pdf2image`, `Pillow`, and `requests` installed. If any are missing:
    ```bash
    pip install -r req/requirements.txt
    ```

## 🏃🏽‍♂️ How to Run the Bot

Start the interactive Streamlit application by running:

```bash
# Assuming you are inside the "ocr chatbot" directory
./mac_env/bin/python3 -m streamlit run ocr.py
```

*   The terminal will provide a `Local URL` link (usually `http://localhost:8501`).
*   Open that link in your web browser. 
*   Drag and drop any PDF file to test the extraction and AI summarization!

## 📂 Project Structure

*   `ocr.py` - Main Streamlit web application orchestrating OCR and LLM integration.
*   `bot.py` - Secondary script representing query or search interactions.
*   `ocr_images.csv` - The output file containing image paths and raw extracted text.
*   `mac_env/` - The isolated active Python environment for this application.
*   `ocr/` - Helper module referencing test implementations.

