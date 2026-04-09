import streamlit as st
from groq import Groq
import pdfplumber
from fpdf import FPDF
import firebase_admin
from firebase_admin import credentials, firestore
import json
import time

# --- FIREBASE BAĞLANTISI ---
# Not: JSON bilgilerini Streamlit Secrets'a "FIREBASE_JSON" adıyla eklemelisin
if not firebase_admin._apps:
    try:
        fb_creds = json.loads(st.secrets["FIREBASE_JSON"])
        cred = credentials.Certificate(fb_creds)
        firebase_admin.initialize_app(cred)
    except:
        st.error("Firebase bağlantısı kurulamadı. Lütfen Secrets ayarlarını kontrol et kanka.")

db = firestore.client()

# --- API AYARI ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="UltraAI | Akıllı Hafıza", layout="wide")

# --- UI GÜNCELLEMESİ ---
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top left, #020617, #0f172a); color: #f8fafc; }
    .history-card { 
        background: rgba(30, 41, 59, 0.4); 
        padding: 15px; 
        border-radius: 12px; 
        border-left: 5px solid #3b82f6;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- OTURUM YÖNETİMİ ---
if 'final_content' not in st.session_state: st.session_state.final_content = ""

# --- SEKMELER ---
tab1, tab2, tab3, tab4 = st.tabs(["📥 Giriş", "📝 Özetle", "🎯 Test", "📜 Geçmiş"])

# --- TAB 1: GİRİŞ ---
with tab1:
    st.subheader("📚 Yeni İçerik Ekle")
    input_type = st.radio("Yöntem:", ["Metin", "PDF"], horizontal=True)
    if input_type == "Metin":
        st.session_state.final_content = st.text_area("Notlar:", height=200)
    else:
        file = st.file_uploader("PDF Yükle", type="pdf")
        if file:
            with pdfplumber.open(file) as p:
                st.session_state.final_content = "\n".join([page.extract_text() for page in p.pages if page.extract_text()])

# --- TAB 2: ÖZETLE VE KAYDET ---
with tab2:
    if st.session_state.final_content:
        if st.button("🚀 Özeti Hazırla ve Buluta Kaydet"):
            with st.spinner('AI çalışıyor...'):
                res = client.chat.completions.create(
                    messages=[{"role": "user", "content": f"Özetle:\n\n{st.session_state.final_content[:8000]}"}],
                    model="llama-3.1-8b-instant"
                )
                summary = res.choices[0].message.content
                
                # Firebase'e Kaydet
                doc_ref = db.collection('ozetler').document()
                doc_ref.set({
                    'baslik': st.session_state.final_content[:30] + "...",
                    'icerik': summary,
                    'tarih': time.time()
                })
                st.success("✅ Özet hazırlandı ve geçmişe kaydedildi!")
                st.markdown(summary)
    else:
        st.warning("Önce veri yükle kanka.")

# --- TAB 4: GEÇMİŞ (HISTORY) ---
with tab4:
    st.subheader("📜 Kayıtlı Notların")
    docs = db.collection('ozetler').order_by('tarih', direction=firestore.Query.DESCENDING).limit(10).stream()
    
    for doc in docs:
        data = doc.to_dict()
        with st.expander(f"📅 {data['baslik']}"):
            st.write(data['icerik'])
            if st.button("🗑️ Sil", key=doc.id):
                db.collection('ozetler').document(doc.id).delete()
                st.rerun()
