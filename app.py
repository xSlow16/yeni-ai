import streamlit as st
from groq import Groq
import pdfplumber
from fpdf import FPDF
import firebase_admin
from firebase_admin import credentials, firestore
import json
import time

# --- 1. SAYFA AYARI (Her zaman en üstte olmalı) ---
st.set_page_config(page_title="UltraAI | Akıllı Hafıza", layout="wide")

# --- 2. FIREBASE BAĞLANTISI (BURAYA YAZIYORSUN) ---
db = None 

if not firebase_admin._apps:
    try:
        fb_creds_raw = st.secrets["FIREBASE_JSON"]
        fb_creds_dict = json.loads(fb_creds_raw.strip())
        cred = credentials.Certificate(fb_creds_dict)
        firebase_admin.initialize_app(cred)
        db = firestore.client() 
        st.success("⚡ Bulut hafızası aktif!")
    except Exception as e:
        st.error(f"⚠️ Firebase bağlantı hatası: {e}")
else:
    db = firestore.client()

# --- 3. API AYARI ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 4. UI VE DİĞER KODLAR (BURADAN DEVAM EDİYOR) ---
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top left, #020617, #0f172a); color: #f8fafc; }
    </style>
    """, unsafe_allow_html=True)

# ... (Kodun geri kalanı aynı şekilde devam ediyor)
