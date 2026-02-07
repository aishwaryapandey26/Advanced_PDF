import streamlit as st
from streamlit_option_menu import option_menu
from PyPDF2 import PdfReader, PdfWriter
import fitz  # PyMuPDF
from io import BytesIO
from PIL import Image
import base64
import streamlit.components.v1 as components


import os
import json
import datetime
import time
import uuid


import qrcode
from io import BytesIO

st.header("📸 Camera / Mobile Upload to PDF")




# ---------------- CONFIG ----------------
st.set_page_config(page_title="PDF Utility Tool", page_icon="📄", layout="wide")

SAVED_DIR = "saved_pdfs"
HISTORY_FILE = os.path.join(SAVED_DIR, "history.json")

os.makedirs(SAVED_DIR, exist_ok=True)
if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "w") as f:
        json.dump([], f)

# ---------------- HELPERS ----------------
def save_bytes_to_folder(bytes_data, folder, filename):
    path = os.path.join(folder, filename)
    with open(path, "wb") as f:
        f.write(bytes_data)
    return path

def record_history(filename, action):
    entry = {
        "filename": filename,
        "action": action,
        "timestamp": datetime.datetime.now().isoformat()
    }
    with open(HISTORY_FILE, "r+") as f:
        data = json.load(f)
        data.insert(0, entry)
        f.seek(0)
        json.dump(data, f, indent=2)

def get_history():
    with open(HISTORY_FILE) as f:
        return json.load(f)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    selected = option_menu(
        "PDF Utility",
        ["Home", "Merge PDF", "Split PDF", "Saved Files", "PDF Search", "PDF Tools", "Camera Upload", "About"],
        icons=["house", "layers", "scissors", "clock", "search", "tools", "camera", "info-circle"]
    )

# ---------------- HOME ----------------
if selected == "Home":
    st.title("📄 PDF Utility Dashboard")
    st.write("Merge, split, search, reorder, and manage PDFs efficiently.")

# ---------------- MERGE ----------------
elif selected == "Merge PDF":
    st.header("📎 Merge PDFs")
    files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)

    if st.button("Merge & Download") and files:
        writer = PdfWriter()
        for f in files:
            reader = PdfReader(f)
            for p in reader.pages:
                writer.add_page(p)

        output = BytesIO()
        writer.write(output)
        output.seek(0)

        filename = f"merged_{int(time.time())}.pdf"
        save_bytes_to_folder(output.getvalue(), SAVED_DIR, filename)
        record_history(filename, "merge")

        st.download_button("Download Merged PDF", output, file_name=filename)

# ---------------- SPLIT ----------------
elif selected == "Split PDF":
    st.header("✂️ Split PDF")
    file = st.file_uploader("Upload PDF", type="pdf")

    if file:
        reader = PdfReader(file)
        total = len(reader.pages)

        start = st.number_input("Start Page", 1, total, 1)
        end = st.number_input("End Page", 1, total, total)

        if st.button("Split"):
            writer = PdfWriter()
            for i in range(start - 1, end):
                writer.add_page(reader.pages[i])

            output = BytesIO()
            writer.write(output)
            output.seek(0)

            filename = f"split_{start}_{end}.pdf"
            save_bytes_to_folder(output.getvalue(), SAVED_DIR, filename)
            record_history(filename, "split")

            st.download_button("Download Split PDF", output, file_name=filename)

# ---------------- SAVED FILES ----------------
elif selected == "Saved Files":
    st.header("📚 Saved Files")
    history = get_history()

    for h in history:
        col1, col2, col3 = st.columns([5, 3, 1])
        with col1:
            st.write(h["filename"])
        with col2:
            st.write(h["timestamp"])
        with col3:
            path = os.path.join(SAVED_DIR, h["filename"])
            if os.path.exists(path):
                with open(path, "rb") as f:
                    st.download_button("⬇️", f.read(), file_name=h["filename"])

# ---------------- PDF SEARCH ----------------
elif selected == "PDF Search":
    st.header("🔍 Search Text in PDF")
    file = st.file_uploader("Upload PDF", type="pdf")
    query = st.text_input("Search text")

    if file and query:
        doc = fitz.open(stream=file.read(), filetype="pdf")

        for i, page in enumerate(doc):
            words = page.get_text("words")
            rects = [fitz.Rect(w[:4]) for w in words if query.lower() in w[4].lower()]

            if rects:
                for r in rects:
                    page.add_highlight_annot(r)

                pix = page.get_pixmap(matrix=fitz.Matrix(0.6, 0.6))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    st.image(img, caption=f"Page {i + 1}", width=None)

# ---------------- PDF TOOLS ----------------
elif selected == "PDF Tools":
    st.header("🛠 PDF Tools")
    file_tools = st.file_uploader("Upload PDF", type="pdf")  # renamed

    if file_tools:  # all code inside this block
        reader = PdfReader(file_tools)
        metadata = reader.metadata or {}

        # ---- METADATA ----
        st.subheader("📌 Metadata")
        new_author = st.text_input("Author", metadata.get("/Author", ""))
        new_title = st.text_input("Title", metadata.get("/Title", ""))

        if st.button("Save Metadata"):
            writer = PdfWriter()
            for p in reader.pages:
                writer.add_page(p)
            writer.add_metadata({"/Author": new_author, "/Title": new_title})

            output = BytesIO()
            writer.write(output)
            output.seek(0)

            st.download_button("Download Updated PDF", output, file_name="metadata_updated.pdf")

        st.divider()

        # ---- VISUAL PAGE REORDER / DELETE ----
        st.subheader("🧩 Visual Page Reorder / Delete")
        doc = fitz.open(stream=file_tools.read(), filetype="pdf")  # still inside if block

        # Convert pages to images
        images = []
        for i, page in enumerate(doc):
            pix = page.get_pixmap(matrix=fitz.Matrix(0.35, 0.35))
            img_bytes = pix.tobytes("png")
            b64 = base64.b64encode(img_bytes).decode()
            images.append((i, b64))

        # Display sortable pages
        html = "<div class='grid' id='pages'>"
        for idx, b64 in images:
            html += f"""
            <div class="page" data-id="{idx}">
                <img src="data:image/png;base64,{b64}">
                <small>Page {idx+1}</small>
            </div>
            """
        html += "</div>"
        html += """
        <script src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js"></script>
        <script>
        Sortable.create(document.getElementById("pages"), {animation: 150});
        </script>
        """
        components.html(html, height=500)

        if "page_order" not in st.session_state:
            st.session_state.page_order = list(range(len(doc)))

        if st.button("Apply Page Order"):
            writer = PdfWriter()
            for i in st.session_state.page_order:
                writer.add_page(reader.pages[i])

            output = BytesIO()
            writer.write(output)
            output.seek(0)

            st.download_button(
                "⬇️ Download Reordered PDF",
                output,
                file_name="reordered_pages.pdf"
            )

# ---------------- CAMERA UPLOAD ----------------
    from streamlit_autorefresh import st_autorefresh

    # Auto-refresh every 3 seconds
    count = st_autorefresh(interval=3000, key="upload_refresh")

elif selected == "Camera Upload":
    st.header("📸 Camera / Mobile Upload to PDF via QR Code")

    st.write("Scan this QR code with your phone. On your phone, you can take photos or select from gallery. Images will appear here on your laptop in real-time.")

    # Generate a QR code linking to a mobile upload page
    # You need a separate Streamlit page or endpoint for mobile upload
    # For now, let's assume we use the same app with a mobile mode
    app_url = st.secrets.get("APP_URL", "https://advancedpdf-yuu5mabee3vpbmjlpmy2no.streamlit.app/mobile_upload")
    
    qr = qrcode.QRCode(box_size=8, border=2)
    qr.add_data(app_url)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white")

    # Display QR code on laptop
    buf = BytesIO()
    img_qr.save(buf, format="PNG")
    buf.seek(0)
    st.image(buf, caption="Scan to upload from your phone", width=250)

    # ------------------ Real-time upload display ------------------
    st.write("Uploaded images will appear below:")

    # Polling for uploaded images (simulate real-time)
    # We'll use a folder "mobile_uploads" where mobile clients save images
    UPLOAD_DIR = "mobile_uploads"
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    uploaded_files = []
    for f in os.listdir(UPLOAD_DIR):
        path = os.path.join(UPLOAD_DIR, f)
        if os.path.isfile(path):
            uploaded_files.append(path)

    if uploaded_files:
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
            filename = f"images_merged_{int(time.time())}.pdf"
            save_bytes_to_folder(pdf_bytes.getvalue(), SAVED_DIR, filename)
            record_history(filename, "images_merge")
            st.success("✅ PDF created successfully!")
            st.download_button(
                "⬇️ Download Merged PDF",
                pdf_bytes,
                file_name=filename
            )


# ---------------- ABOUT ----------------
elif selected == "About":
    st.header("ℹ️ About")
    st.write("""
    **PDF Utility Tool**
    
    - Merge, Split PDFs
    - Full-text Search with Highlight
    - Visual Page Reorder & Delete
    - Metadata Viewer & Editor
    
    Built using **Streamlit, PyMuPDF, PyPDF2**
    """)
