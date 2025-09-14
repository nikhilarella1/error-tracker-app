import streamlit as st
import json
import os
from docx import Document
import requests
import base64

# --- GitHub repo details from environment variables ---
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = os.environ.get("GITHUB_REPO")
GITHUB_FILE = os.environ.get("GITHUB_FILE", "error_data.json")

# GitHub API URL
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
def save_error_db(error_db, file_sha=None):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    content = base64.b64encode(json.dumps(error_db, indent=2).encode()).decode()
    data = {"message": "Update error DB", "content": content}
    if file_sha:
        data["sha"] = file_sha

    res = requests.put(GITHUB_API, headers=headers, json=data)
    if res.status_code in (200, 201):
        st.success("✅ Data saved to GitHub!")
    else:
        try:
            st.error(f"❌ Failed: {res.json()}")
        except:
            st.error(f"❌ Failed: {res.status_code} - {res.text}")

# --- Load DB ---
error_db, file_sha = load_error_db()

# --- File uploader ---
uploaded_files = st.file_uploader("Upload Word Documents", type=["docx"], accept_multiple_files=True)
if uploaded_files:
    for uploaded_file in uploaded_files:
        doc = Document(uploaded_file)
        title = doc.paragraphs[0].text.strip() if doc.paragraphs else uploaded_file.name
        content = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        error_db[title] = content

    save_error_db(error_db, file_sha)

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
