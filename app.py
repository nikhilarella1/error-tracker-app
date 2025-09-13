import streamlit as st
import json
import os
from docx import Document
import requests
import base64

# GitHub repo details from secrets
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_REPO = st.secrets["GITHUB_REPO"]
GITHUB_FILE = st.secrets["GITHUB_FILE"]

# GitHub API base URL
GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE}"

# --- Function: Load file from GitHub ---
def load_error_db():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    res = requests.get(GITHUB_API, headers=headers)
    if res.status_code == 200:
        content = res.json()
        data = base64.b64decode(content["content"]).decode("utf-8")
        return json.loads(data), content["sha"]
    else:
        return {}, None

# --- Function: Save file to GitHub ---
def save_error_db(data, sha=None):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    message = "Update error_data.json from Streamlit app"
    content = base64.b64encode(json.dumps(data, ensure_ascii=False, indent=4).encode("utf-8")).decode("utf-8")

    payload = {
        "message": message,
        "content": content,
        "branch": "main"
    }
    if sha:
        payload["sha"] = sha

    res = requests.put(GITHUB_API, headers=headers, json=payload)
    if res.status_code not in [200, 201]:
        st.error(f"❌ Failed to save data: {res.json()}")
    else:
        st.success("✅ Data saved to GitHub permanently!")

# --- Load DB at startup ---
error_db, file_sha = load_error_db()

# --- File uploader ---
uploaded_files = st.file_uploader("Upload Word Documents", type=["docx"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        doc = Document(uploaded_file)
        content = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        title = doc.paragraphs[0].text.strip()
        error_db[title] = content

    save_error_db(error_db, file_sha)

# --- Search ---
search_title = st.text_input("Enter the error title to search")

if search_title:
    if search_title in error_db:
        st.subheader(f"📄 {search_title}")
        # Format into steps
        steps = error_db[search_title].split("\n")
        for i, step in enumerate(steps, 1):
            if step.strip():
                st.markdown(f"**{i})** {step.strip()}")
    else:
        st.warning("No details found for this title.")
