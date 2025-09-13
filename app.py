import streamlit as st
import json
import os
from docx import Document

# File where retrieved data will be stored permanently
DB_FILE = "error_data.json"

# Load stored data
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r", encoding="utf-8") as f:
        error_db = json.load(f)
else:
    error_db = {}

# Upload multiple Word files
uploaded_files = st.file_uploader("Upload Word Documents", type=["docx"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        doc = Document(uploaded_file)
        content = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

        # Use first line as the title (or you can adjust logic)
        title = doc.paragraphs[0].text.strip()
        error_db[title] = content

    # Save updated database permanently
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(error_db, f, ensure_ascii=False, indent=4)

    st.success("Files uploaded and stored permanently!")

# Search functionality
search_title = st.text_input("Enter the error title to search")

if search_title:
    if search_title in error_db:
        st.subheader(f"Result for: {search_title}")
        st.text(error_db[search_title])  # shows exact steps as-is
    else:
        st.warning("No details found for this title.")
