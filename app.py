import streamlit as st
import json
import os
from docx import Document
import requests
import base64

# --- GitHub repo details from environment variables ---
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = os.environ.get("GITHUB_REPO")
GITHUB_FILE = os.environ.get("GITHUB_FILE")

# GitHub API base URL
GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE}"

# --- Function: Load file from GitHub ---
def load_error_db_from_github():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    res = requests.get(GITHUB_API, headers=headers)
    if res.status_code == 200:
        content = res.json()
        data = base64.b64decode(content["content"]).decode("utf-8")
        return json.loads(data), content["sha"]
    else:
        # If file doesn't exist or unauthorized, return empty dict
        return {}, None

# Local file path
LOCAL_JSON_FILE = "error_data.json"

# --- Load DB ---
if os.path.exists(LOCAL_JSON_FILE):
    # Load from local file if available
    with open(LOCAL_JSON_FILE, "r", encoding="utf-8") as f:
        error_db = json.load(f)
    file_sha = None
else:
    # Otherwise load from GitHub
    error_db, file_sha = load_error_db_from_github()

# --- File uploader ---
uploaded_files = st.file_uploader("Upload Word Documents", type=["docx"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        doc = Document(uploaded_file)
        title = doc.paragraphs[0].text.strip() if doc.paragraphs else uploaded_file.name
        content = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        error_db[title] = content

    # Save locally after upload only
    with open(LOCAL_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(error_db, f, ensure_ascii=False, indent=4)
    st.success("✅ Data stored locally in error_data.json!")

# --- Search ---
search_title = st.text_input("Enter the error title to search")

if search_title:
    if search_title in error_db:
        st.subheader(f"📄 {search_title}")
        steps = error_db[search_title].split("\n")
        for i, step in enumerate(steps, 1):
            if step.strip():
                st.markdown(f"**{i})** {step.strip()}")
    else:
        st.warning("No details found for this title.")
