import streamlit as st
import os
from datetime import datetime
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="Mobile Upload", layout="centered")
st.header("📱 Upload Images from Phone")

UPLOAD_DIR = "mobile_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.write("📸 Take a photo or select from gallery:")

# This is the key: Streamlit handles camera/gallery automatically
uploaded_files = st.file_uploader(
    "Choose images",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if uploaded_files:
    for file in uploaded_files:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(UPLOAD_DIR, f"{timestamp}_{file.name}")
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
    st.success(f"{len(uploaded_files)} image(s) uploaded successfully!")
