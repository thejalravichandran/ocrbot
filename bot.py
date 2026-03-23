import csv
import os
from fuzzywuzzy import fuzz
import streamlit as st
from PIL import Image

# Function to load the extracted text and image paths from the provided CSV file path
def load_extracted_text(csv_path, image_folder_path):
    extracted_data = []
    try:
        with open(csv_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                image_path = os.path.join(image_folder_path, os.path.basename(row["Image"]))
                extracted_data.append({"image": image_path, "text": row["Text"]})
        return extracted_data
    except Exception as e:
        st.error(f"Error loading extracted text from CSV: {e}")
        return []

# Function to find all matches for the query in the extracted data
def find_all_matches(query, extracted_data, threshold=50):
    matches = []
    query = query.lower()

    for entry in extracted_data:
        text = entry["text"]
        image_path = entry["image"]

        similarity = fuzz.partial_ratio(query, text.lower())

        if similarity >= threshold:
            matches.append({
                "image": os.path.basename(image_path),
                "text": text,
                "similarity": similarity,
                "image_path": image_path
            })

    return matches

# Function to summarize information
def summarize_information(text):
    return text[:500] + "..."

# Function to explain the image based on the extracted text
def explain_image(text):
    explanation = "This image likely refers to: " + text.split(".")[0]
    return explanation

# Streamlit interface
def main():
    st.title("Query Bot")
    st.write("Ask me anything based on the document content!")

    # CSV file path input and Image folder path input
    csv_path = st.text_input("Enter the path of the CSV file with extracted text:")
    image_folder_path = st.text_input("Enter the path of the image folder:")

    if csv_path and image_folder_path:
        extracted_data = load_extracted_text(csv_path, image_folder_path)

        if not extracted_data:
            st.write("No extracted text found. Please ensure the CSV file is correctly populated.")
            return

        query = st.text_input("Your question:")

        if query:
            matches = find_all_matches(query, extracted_data)

            if matches:
                st.subheader("Matches Found:")
                for match in matches:
                    st.write(f"**Match found on Page:** {match['image']}")
                    st.write(f"**Text:** {summarize_information(match['text'])}")
                    st.write(f"**Similarity Score:** {match['similarity']}")

                    try:
                        img = Image.open(match['image_path'])
                        st.image(img, caption=os.path.basename(match['image_path']), use_column_width=True)
                        st.write(f"**Explanation of the Image:** {explain_image(match['text'])}")
                    except Exception as e:
                        st.write(f"Could not load image {match['image_path']}: {e}")
                    st.markdown("---")
            else:
                st.write("No relevant matches found for this query. Please try a more specific question.")
    else:
        st.write("Please enter both the CSV file path and image folder path.")

if __name__ == "__main__":
    main()
