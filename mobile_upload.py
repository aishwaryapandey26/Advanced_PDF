import streamlit as st
import os
from datetime import datetime

st.set_page_config(page_title="Mobile Upload", layout="centered")
st.header("📱 Upload Images from Phone")

UPLOAD_DIR = "mobile_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.write("Take a photo or select from gallery:")

st.markdown("""
<input type="file" accept="image/*" capture="environment" multiple id="upload_input">
<script>
document.getElementById('upload_input').addEventListener('change', function() {
    const file_list = this.files;
    const reader = new FileReader();
    for (let i = 0; i < file_list.length; i++) {
        const file = file_list[i];
        const fr = new FileReader();
        fr.onload = function(e) {
            fetch('/', {
                method: 'POST',
                body: e.target.result
            });
        };
        fr.readAsArrayBuffer(file);
    }
});
</script>
""", unsafe_allow_html=True)

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
