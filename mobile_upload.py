import streamlit as st
import os
from datetime import datetime
from PIL import Image

# Setup
st.set_page_config(page_title="Mobile Upload", layout="centered")
st.header("📱 Upload Images from Phone")

UPLOAD_DIR = "mobile_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.write("📷 Tap below to take a photo or select from your gallery:")

# HTML input that triggers camera/gallery on mobile
st.markdown("""
<h2 style="text-align:center; color:blue;">📸 Tap the button below to open your camera or gallery</h2>
<center>
<input type="file" accept="image/*" capture="environment" multiple style="font-size:20px; padding:10px;">
</center>
""", unsafe_allow_html=True)

# Fallback: Streamlit uploader for compatibility
uploaded_files = st.file_uploader(
    "Or choose images manually",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

# Save uploaded images
if uploaded_files:
    for file in uploaded_files:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(UPLOAD_DIR, f"{timestamp}_{file.name}")
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
    st.success(f"{len(uploaded_files)} image(s) uploaded successfully!")

# Display uploaded images live
uploaded_paths = [os.path.join(UPLOAD_DIR, f) for f in os.listdir(UPLOAD_DIR)]
if uploaded_paths:
    cols = st.columns(len(uploaded_paths))
    for i, path in enumerate(uploaded_paths):
        img = Image.open(path)
        with cols[i % len(cols)]:
            st.image(img, caption=os.path.basename(path), width=150)
