import pytesseract
from pdf2image import convert_from_bytes, convert_from_path
import os
import csv
import streamlit as st
import PIL.Image as PILImage
import concurrent.futures
import requests
import json
from fuzzywuzzy import fuzz

# Function to extract images from the uploaded PDF
def extract_images_from_pdf(pdf_file=None, pdf_path=None, poppler_path=None, page_range=None):
    try:
        image_paths = []
        # Create a permanent directory relative to the script for images
        output_dir = "extracted_images"
        os.makedirs(output_dir, exist_ok=True)

        if pdf_file:
            images = convert_from_bytes(pdf_file.read(), first_page=page_range[0] if page_range else 1, 
                                        last_page=page_range[1] if page_range else None, poppler_path=poppler_path)
        elif pdf_path:
            images = convert_from_path(pdf_path, first_page=page_range[0] if page_range else 1, 
                                        last_page=page_range[1] if page_range else None, poppler_path=poppler_path)
        else:
            st.error("No PDF source provided!")
            return []

        for i, image in enumerate(images):
            image_path = os.path.join(output_dir, f"page_{i + 1}.png")
            image.save(image_path, 'PNG')
            image_paths.append(image_path)

        return image_paths
    except Exception as e:
        st.error(f"Error extracting images from PDF: {e}")
        return []

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

# Function to summarize text using an LLM (Ollama)
def summarize_text_with_llm_stream(text, model="llama3"):
    try:
        url = "http://localhost:11434/api/generate"
        prompt = f"Analyze the following text and provide a very concise summary (2-3 sentences max) of its context or architecture:\n\n{text[:3000]}"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True # Enabled streaming for real-time word-by-word UI rendering
        }
        
        response = requests.post(url, json=payload, stream=True, timeout=300)
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                result = json.loads(line.decode('utf-8'))
                if "response" in result:
                    yield result["response"]
    except Exception as e:
        yield f"Error communicating with Ollama: {e}"

# Function to save extracted text to CSV behind the scenes
def save_text_to_csv(image_paths, text_data, csv_filename):
    try:
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Image", "Text"])
            for image_path, text in zip(image_paths, text_data):
                writer.writerow([image_path, text])
    except Exception as e:
        st.error(f"Error saving text to CSV: {e}")

# Function to find all matches for the query in the extracted data
def find_all_matches(query, extracted_data, threshold=50):
    matches = []
    query = query.lower()

    for entry in extracted_data:
        similarity = fuzz.partial_ratio(query, entry["text"].lower())
        if similarity >= threshold:
            matches.append({
                "image_path": entry["image"],
                "text": entry["text"],
                "similarity": similarity
            })
    # Sort matches by highest similarity
    matches = sorted(matches, key=lambda x: x["similarity"], reverse=True)
    return matches

# Function to answer specific user queries based on extracted context using LLM
def answer_query_with_llm_stream(query, context, model="llama3"):
    try:
        url = "http://localhost:11434/api/generate"
        prompt = f"You are a highly capable AI assistant interpreting an extracted document. The user asked: '{query}'.\n\nBased ONLY on the following raw, messy OCR text extracted from the matched page, provide a clear, organized, and helpful answer. If the text looks like disjointed words from a flowchart, diagram, or table, try to infer the workflow and explain it logically using bullet points or clear steps. Keep your overall answer under 5 sentences.\n\nRAW TEXT CONTEXT:\n{context[:3000]}"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True # Streaming the response directly to the UI
        }
        
        response = requests.post(url, json=payload, stream=True, timeout=300)
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                result = json.loads(line.decode('utf-8'))
                if "response" in result:
                    yield result["response"]
    except Exception as e:
        yield f"Error communicating with Ollama: {e}"

# Streamlit UI
def main():
    st.set_page_config(page_title="PDF Intelligence Bot", layout="wide")
    st.title("📄 PDF Intelligence Bot")
    
    # Initialize session state for holding extraction results
    if "extracted_data" not in st.session_state:
        st.session_state["extracted_data"] = []

    # ----------------------------------------------------
    # EXTRACT & SUMMARIZE LOGIC
    # ----------------------------------------------------
    st.write("Upload a PDF file to extract text and generate an AI summary.")
    pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    output_csv = "ocr_images.csv"
    page_range_input = st.text_input("Page range (optional, e.g., 1-5):")
    page_range = [int(i) for i in page_range_input.split('-')] if page_range_input else None

    if st.button("Extract PDF Data"):
        if not pdf_file:
            st.error("Please upload a PDF file first.")
        else:
            image_paths = extract_images_from_pdf(pdf_file=pdf_file, pdf_path=None, 
                                                        poppler_path=None, page_range=page_range)

            if not image_paths:
                st.error("Failed to extract images from PDF.")
            else:
                with st.spinner('Extracting text via OCR...'):
                    extracted_text = extract_text_from_images_parallel(image_paths)

                if not extracted_text or all(text.strip() == "" for text in extracted_text):
                    st.warning("No text could be extracted. Please check PDF quality.")
                else:
                    # Save the text in the background
                    save_text_to_csv(image_paths, extracted_text, output_csv)

                    # Parse extracted text & images into session state so the Query Bot can use it!
                    st.session_state["extracted_data"] = [
                        {"image": img_path, "text": text_chunk} 
                        for img_path, text_chunk in zip(image_paths, extracted_text)
                    ]

                    st.success(f"Extraction completed! Successfully loaded {len(image_paths)} pages into bot memory.")
                    
                    st.subheader("🤖 AI Document Summary")
                    full_text = "\n".join(extracted_text)
                    with st.spinner('Generating summary (streaming response)...'):
                        st.write_stream(summarize_text_with_llm_stream(full_text))

                    st.write("---")
                    with st.expander("Preview Raw Extracted Text"):
                        for i, text in enumerate(extracted_text):
                            st.write(f"**Page {i + 1}:**\n{text[:500]}...") 

    st.divider()

    # ----------------------------------------------------
    # QUERY BOT LOGIC
    # ----------------------------------------------------
    st.header("🔍 Query Bot (Search Memory)")
    st.write("Ask any question against the document you just extracted!")

    if not st.session_state["extracted_data"]:
        st.info("👈 No data loaded yet. Please upload and extract a PDF above to begin searching.")
    else:
        st.success(f"Bot Memory Active! Looking across {len(st.session_state['extracted_data'])} generated pages.")
        query = st.text_input("What are you looking for?")

        if query:
            with st.spinner("Searching pages..."):
                matches = find_all_matches(query, st.session_state["extracted_data"])

            if matches:
                st.subheader("Top Match Found:")
                # We only process the absolute best match through the LLM to keep generation speeds fast
                best_match = matches[0]
                
                with st.container():
                    st.write(f"**Best Match Similarity Score:** {best_match['similarity']}%")
                    
                    # Layout with columns to show Image and Text side by side
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        try:
                            img = PILImage.open(best_match['image_path'])
                            # Fixed deprecation warning by changing use_column_width to use_container_width
                            st.image(img, caption=os.path.basename(best_match['image_path']), use_container_width=True)
                        except Exception as e:
                            st.warning(f"Could not load preview image: {str(e)}")
                    
                    with col2:
                        st.write("🤖 **AI Intelligent Breakdown:**")
                        # Stream the AI explanation based on the user's specific query and the messy text
                        with st.spinner("AI is analyzing the diagram text..."):
                            st.write_stream(answer_query_with_llm_stream(query, best_match['text']))
                            
                        with st.expander("View Raw Messy Text"):
                            st.info(f"{best_match['text'][:1000]}...")
                    
                    st.divider()

                # Show simpler text snippets for any other runner-up matches without triggering heavy LLM generation
                if len(matches) > 1:
                    st.write("### Other Relevant Pages:")
                    for runner_up in matches[1:3]: # Show up to 2 runner-ups
                        st.write(f"**Page:** {os.path.basename(runner_up['image_path'])} (Score: {runner_up['similarity']}%)")
            else:
                st.warning("No relevant matches found for this query. Try different keywords.")

if __name__ == "__main__":
    main()
