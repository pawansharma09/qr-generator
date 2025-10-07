# streamlit_app.py
import streamlit as st
import requests
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="QR Generator", layout="centered")

st.title("QR Generator (Streamlit → FastAPI)")

# Replace with your deployed Render URL (no trailing slash)
RENDER_URL = st.secrets.get("render_url") if "render_url" in st.secrets else "http://localhost:8000"

with st.form("qr_form"):
    text = st.text_area("Text or URL to encode", value="", height=120)
    initials = st.text_input("Initials (optional — e.g. 'JS')", value="")
    box_size = st.slider("Box size (resolution)", min_value=5, max_value=30, value=10)
    submitted = st.form_submit_button("Generate QR")

if submitted:
    if not text.strip():
        st.error("Please enter some text to encode.")
    else:
        payload = {
            "text": text,
            "initials": initials.strip() or None,
            "box_size": box_size,
            "border": 4
        }
        try:
            with st.spinner("Generating QR..."):
                resp = requests.post(f"{RENDER_URL}/generate", json=payload, timeout=20)
            if resp.status_code == 200:
                img_bytes = resp.content
                st.image(img_bytes, caption="Your QR code (scan or download)", use_column_width=False)
                st.download_button(
                    label="Download PNG",
                    data=img_bytes,
                    file_name="qr.png",
                    mime="image/png"
                )
            else:
                st.error(f"Server error: {resp.status_code} - {resp.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")
