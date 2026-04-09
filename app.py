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

# --- 2. FIREBASE BAĞLANTISI (ZIRHLI) ---
db = None

if not firebase_admin._apps:
    try:
        # Secrets'tan JSON metnini al ve temizle
        fb_creds_raw = st.secrets["FIREBASE_JSON"].strip()
        
        # JSON'ı sözlüğe çevir
        fb_creds_dict = json.loads(fb_creds_raw)
        
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
    st.error("🔑 Groq API Key bulunamadı!")
    st.stop()

MODEL_NAME = "llama-3.1-8b-instant"

# --- 4. MODERN UI (CSS) ---
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top left, #020617, #0f172a); color: #f8fafc; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: rgba(30, 41, 59, 0.4);
        border-radius: 10px 10px 0px 0px;
        color: #94a3b8;
    }
    .stTabs [aria-selected="true"] { background: linear-gradient(45deg, #2563eb, #7c3aed) !important; color: white !important; }
    .header-card { background: rgba(15, 23, 42, 0.6); padding: 1.5rem; border-radius: 1rem; text-align: center; border-bottom: 2px solid #3b82f6; margin-bottom: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="header-card"><h1 style="color:white;">UltraAI Super-Asistan</h1><p style="color:#94a3b8;">Hafızalı, Akıllı ve Profesyonel Çalışma Platformu</p></div>', unsafe_allow_html=True)

# --- SESSION STATE ---
if 'final_content' not in st.session_state: st.session_state.final_content = ""

# --- SEKMELER ---
tab1, tab2, tab3, tab4 = st.tabs(["📥 Giriş", "📝 Özetle", "🎯 Test", "📜 Geçmiş"])

# --- TAB 1: GİRİŞ ---
with tab1:
    st.subheader("📚 Materyal Ekle")
    method = st.radio("Yöntem:", ["Metin Yapıştır", "PDF Yükle"], horizontal=True)
    
    if method == "Metin Yapıştır":
        st.session_state.final_content = st.text_area("Ders notlarını buraya bırak kanka:", height=300)
    else:
        file = st.file_uploader("PDF Dosyanı Seç", type="pdf")
        if file:
            with pdfplumber.open(file) as p:
                st.session_state.final_content = "\n".join([page.extract_text() for page in p.pages if page.extract_text()])
            st.success("✅ PDF başarıyla okundu!")

# --- TAB 2: ÖZETLE VE KAYDET ---
with tab2:
    if st.session_state.final_content:
        tone = st.select_slider("Anlatım Tarzı:", options=["Basit", "Akademik", "Sınav Odaklı"])
        if st.button("🚀 Özeti Hazırla ve Buluta Kaydet"):
            with st.spinner('Yapay zeka notlarını işliyor...'):
                try:
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Üslup: {tone}. Önemli yerleri vurgulayarak özetle:\n\n{st.session_state.final_content[:10000]}"}],
                        model=MODEL_NAME
                    )
                    summary = res.choices[0].message.content
                    
                    # Firebase'e Kaydet
                    if db is not None:
                        db.collection('ozetler').add({
                            'baslik': st.session_state.final_content[:40].replace('\n', ' ') + "...",
                            'icerik': summary,
                            'tarih': time.time()
                        })
                    
                    st.markdown("### 📝 Hazırlanan Özet")
                    st.info(summary)
                except Exception as e:
                    st.error(f"Hata oluştu: {e}")
    else:
        st.warning("⚠️ Özet çıkarmak için önce 'Giriş' sekmesinden veri eklemelisin.")

# --- TAB 3: TEST ÇÖZ ---
with tab3:
    if st.session_state.final_content:
        if st.button("🎲 Soruları Üret"):
            with st.spinner('Sorular hazırlanıyor...'):
                try:
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Bu notlardan 5 test sorusu ve cevap anahtarı çıkar:\n\n{st.session_state.final_content[:10000]}"}],
                        model=MODEL_NAME
                    )
                    st.success(res.choices[0].message.content)
                except Exception as e:
                    st.error(f"Hata: {e}")
    else:
        st.warning("⚠️ Önce veri ekle kanka.")

# --- TAB 4: GEÇM
