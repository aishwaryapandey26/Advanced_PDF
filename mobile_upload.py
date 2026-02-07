import streamlit as st
from PIL import Image
import os
from io import BytesIO
from helpers import save_bytes_to_folder, record_history  # your helper functions

st.header("📸 Camera / Mobile Upload to PDF")

st.write("Scan this QR code with your phone to upload images from camera or gallery:")

# Replace with your deployed mobile_upload page
app_url = st.secrets.get("APP_URL", "https://your-deployed-app/mobile_upload")

import qrcode

# Generate QR code
qr = qrcode.QRCode(box_size=8, border=2)
qr.add_data(app_url)
qr.make(fit=True)
img_qr = qr.make_image(fill_color="black", back_color="white")

# Display QR code on laptop
buf = BytesIO()
img_qr.save(buf, format="PNG")
buf.seek(0)
st.image(buf, caption="Scan to upload from your phone", width=250)

# ------------------ Display uploaded images ------------------
UPLOAD_DIR = "mobile_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

uploaded_files = []
for f in os.listdir(UPLOAD_DIR):
    path = os.path.join(UPLOAD_DIR, f)
    if os.path.isfile(path):
        uploaded_files.append(path)

if uploaded_files:
    st.write("Uploaded images (from mobile):")
    cols = st.columns(len(uploaded_files))
    images = []
    for i, path in enumerate(uploaded_files):
        img = Image.open(path)
        images.append(img)
        with cols[i % len(cols)]:
            st.image(img, caption=os.path.basename(path), width=200)

    # Merge button
    if st.button("Merge Uploaded Images to PDF"):
        pdf_bytes = BytesIO()
        images[0].save(pdf_bytes, format="PDF", save_all=True, append_images=images[1:])
        pdf_bytes.seek(0)
        filename = f"images_merged.pdf"
        save_bytes_to_folder(pdf_bytes.getvalue(), UPLOAD_DIR, filename)
        record_history(filename, "images_merge")
        st.success("✅ PDF created successfully!")
        st.download_button(
            "⬇️ Download Merged PDF",
            pdf_bytes,
            file_name=filename
        )
