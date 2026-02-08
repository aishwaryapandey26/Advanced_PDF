import streamlit as st
from streamlit_option_menu import option_menu
from PyPDF2 import PdfReader, PdfWriter
import fitz  # PyMuPDF
from io import BytesIO
from PIL import Image
import base64
import streamlit.components.v1 as components
import os, json, datetime, time, uuid

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
        ["Home", "Merge PDF", "Split PDF", "Saved Files", "PDF Search", "PDF Tools", "PDF Conversion", "Security & Privacy", "Analytics", "About"],
        icons=["house", "layers", "scissors", "clock", "search", "tools", "file-earmark-text", "shield-lock", "bar-chart", "info-circle"]
    )

# ---------------- HOME ----------------
if selected == "Home":
    st.title("📄 PDF Utility Dashboard")
    st.write("Merge, split, search, annotate, convert, secure, and analyze PDFs efficiently.")

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
        st.image(img, caption=f"Page {i+1}", width=None)

# ---------------- PDF TOOLS / ANNOTATIONS ----------------
elif selected == "PDF Tools":
    st.header("🛠 PDF Annotation & Markup Tools")

    pdf_file = st.file_uploader("Upload PDF", type="pdf")
    if pdf_file:
        import base64

        # Save temporarily
        temp_filename = os.path.join(SAVED_DIR, f"temp_{uuid.uuid4().hex}.pdf")
        with open(temp_filename, "wb") as f:
            f.write(pdf_file.read())

        st.write("Use the tools to annotate your PDF. When done, click **Download** to save your changes.")

        html_code = f"""
        <div id="viewer" style="width:100%;height:90vh;"></div>

        <script src="https://www.pdftron.com/webviewer/lib/webviewer.min.js"></script>

        <script>
            WebViewer({{
                path: 'https://www.pdftron.com/webviewer/lib',
                initialDoc: '{temp_filename}',
                enableAnnotations: true,
                fullAPI: true
            }}, document.getElementById('viewer')).then(instance => {{
                const Annotations = instance.Annotations;
                const documentViewer = instance.documentViewer;

                const saveButton = document.createElement('button');
                saveButton.innerText = "Download Annotated PDF";
                saveButton.style.position = "absolute";
                saveButton.style.top = "10px";
                saveButton.style.right = "10px";
                saveButton.style.zIndex = 1000;

                saveButton.onclick = async () => {{
                    const xfdfString = await instance.annotationManager.exportAnnotations();
                    const doc = await instance.Core.PDFNet.PDFDoc.createFromURL('{temp_filename}');
                    await instance.Core.PDFNet.AnnotManager.importAnnotations(xfdfString, doc);
                    const data = await doc.saveMemoryBuffer(instance.Core.PDFNet.SDFDocSaveOptions.e_linearized);
                    const blob = new Blob([data], {{ type: 'application/pdf' }});
                    const link = document.createElement('a');
                    link.href = URL.createObjectURL(blob);
                    link.download = 'annotated.pdf';
                    link.click();
                }};
                document.body.appendChild(saveButton);
            }});
        </script>
        """

        import streamlit.components.v1 as components
        components.html(html_code, height=800)

# ---------------- PDF CONVERSIONS ----------------
elif selected == "PDF Conversion":
    st.header("📑 PDF Conversion Tools")
    # PDF → Images / JPG
    file = st.file_uploader("Upload PDF", type="pdf")
    if file:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        if st.button("Convert PDF → Images"):
            images = []
            for i,page in enumerate(doc):
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width,pix.height], pix.samples)
                images.append(img)
                st.image(img, caption=f"Page {i+1}", width=300)
            # Save as ZIP / optional
        # Word/Excel → PDF (requires python-docx, openpyxl, pandas)
        st.write("**Word / Excel → PDF** feature coming soon…")

# ---------------- SECURITY & PRIVACY ----------------
elif selected == "Security & Privacy":
    st.header("🔒 Security & Privacy Features")
    file = st.file_uploader("Upload PDF", type="pdf")
    if file:
        reader = PdfReader(file)
        password = st.text_input("Set Password for PDF")
        if st.button("Encrypt PDF") and password:
            writer = PdfWriter()
            for p in reader.pages:
                writer.add_page(p)
            writer.encrypt(password)
            output = BytesIO()
            writer.write(output)
            output.seek(0)
            st.download_button("Download Encrypted PDF", output, file_name="encrypted.pdf")
        st.write("Other features like redaction, watermark coming soon…")

# ---------------- ANALYTICS DASHBOARD ----------------
elif selected == "Analytics":
    st.header("📊 PDF Analytics Dashboard")
    history = get_history()
    st.write("Number of PDFs:", len(history))
    st.write("Recent Actions:")
    for h in history[:10]:
        st.write(f"{h['timestamp']} → {h['filename']} ({h['action']})")
    # Future: page counts, image counts, annotation counts

# ---------------- ABOUT ----------------
elif selected == "About":
    st.header("ℹ️ About")
    st.write("""
    **PDF Utility Tool**
    
    Features:
    - Merge, Split, Search, Annotate, Reorder
    - Conversion Tools (PDF → JPG, Word/Excel → PDF)
    - Security & Privacy (Password Protect, Redact, Watermark)
    - Analytics Dashboard
    - AI-Powered PDF Analyzer (future)
    
    Built using **Streamlit, PyMuPDF, PyPDF2, PIL**
    """)
