import streamlit as st
from groq import Groq
import pdfplumber
import io

# --- API AYARI ---
# Buraya Groq'tan aldığın API Key'i yapıştır kanka
GROQ_API_KEY = "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" 
client = Groq(api_key=GROQ_API_KEY)

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Ultra Asistan Cloud", layout="wide", page_icon="🌐")

# --- MODERN TASARIM (CSS) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #f1f5f9; }
    .main-title { font-size: 50px; font-weight: 800; text-align: center; background: -webkit-linear-gradient(#00c6ff, #007BFF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .stTextArea textarea { background-color: rgba(30, 41, 59, 0.7); color: #fff !important; border-radius: 15px; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background: linear-gradient(45deg, #007BFF, #00d4ff); color: white; font-weight: bold; border: none; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">🚀 ULTRA ASİSTAN CLOUD</div>', unsafe_allow_html=True)
st.write("<p style='text-align: center;'>7/24 Açık • Ücretsiz • Jet Hızında</p>", unsafe_allow_html=True)

option = st.radio("Yöntem seç:", ("Metin Yapıştır", "PDF Yükle"), horizontal=True)

final_content = ""

if option == "Metin Yapıştır":
    final_content = st.text_area("Notları bırak kanka:", height=200)
elif option == "PDF Yükle":
    uploaded_pdf = st.file_uploader("PDF Seç", type=["pdf"])
    if uploaded_pdf:
        with pdfplumber.open(uploaded_pdf) as pdf:
            final_content = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])

if final_content:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✨ ÖZETLE"):
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": f"Aşağıdaki notları Türkçe ve maddeler halinde özetle:\n\n{final_content}"}],
                model="llama3-8b-8192",
            )
            st.info(chat_completion.choices[0].message.content)
    with col2:
        if st.button("❓ SORU HAZIRLA"):
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": f"Aşağıdaki notlardan 5 tane Türkçe test sorusu ve cevaplarını hazırla:\n\n{final_content}"}],
                model="llama3-8b-8192",
            )
            st.success(chat_completion.choices[0].message.content)