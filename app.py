import streamlit as st
from groq import Groq
import pdfplumber
from fpdf import FPDF
import firebase_admin
from firebase_admin import credentials, firestore
import json
import time

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="UltraAI | Akıllı Hafıza v5.0", layout="wide", page_icon="🎓")

# --- 2. FIREBASE BAĞLANTISI (ZIRHLI VE TAMİRCİ VERSİYON) ---
db = None

if not firebase_admin._apps:
    try:
        # Secrets'tan JSON metnini al
        fb_creds_raw = st.secrets["FIREBASE_JSON"].strip()
        fb_creds_dict = json.loads(fb_creds_raw)
        
        # Private Key içindeki \n ve karakter hatalarını otomatik düzelt
        if "private_key" in fb_creds_dict:
            p_key = fb_creds_dict["private_key"]
            # Önce çift ters bölüleri tekilleştir, sonra hatalı boşlukları temizle
            p_key = p_key.replace("\\n", "\n")
            fb_creds_dict["private_key"] = p_key
        
        # Firebase'i başlat
        cred = credentials.Certificate(fb_creds_dict)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        st.toast("✅ Bulut hafızası bağlandı!", icon="☁️")
    except Exception as e:
        st.error(f"⚠️ Firebase bağlantı hatası: {e}")
        st.info("İpucu: Secrets kısmındaki FIREBASE_JSON içeriğini kontrol et kanka.")
else:
    db = firestore.client()

# --- 3. API VE MODEL AYARLARI ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("🔑 Groq API Key bulunamadı! Lütfen Secrets'a ekle kanka.")
    st.stop()

MODEL_NAME = "llama-3.1-
