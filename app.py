import streamlit as st
from groq import Groq
import pdfplumber
import firebase_admin
from firebase_admin import credentials, firestore
import json
import time

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="UltraAI | Akıllı Hafıza v5.0", layout="wide", page_icon="🎓")

# --- 2. FIREBASE BAĞLANTISI (PADDING HATASI ENGELLEYİCİ) ---
db = None

if not firebase_admin._apps:
    try:
        # Secrets'tan ham metni çek (Tek satır JSON bekliyoruz)
        fb_creds_raw = st.secrets["FIREBASE_JSON"]
        
        # Metni sözlüğe çevir
        fb_creds_dict = json.loads(fb_creds_raw)
        
        # Private Key içindeki \n karakterlerini gerçek alt satırlara dönüştür
        if "private_key" in fb_creds_dict:
            fb_creds_dict["private_key"] = fb_creds_dict["private_key"].replace("\\n", "\n")
        
        cred = credentials.Certificate(fb_creds_dict)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        st.toast("✅ Bulut hafızası bağlandı!", icon="☁️")
    except Exception as e:
        st.error(f"⚠️ Firebase bağlantı hatası: {e}")
        st.info("İpucu: Secrets kısmındaki FIREBASE_JSON içeriğinin tek bir satırda ve tırnak içinde olduğundan emin ol kanka.")
else:
    db = firestore.client()

# --- 3. API VE MODEL AYARLARI ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("🔑 Groq API Key bulunamadı! Secrets kısmına ekle kanka.")
    st.stop()

MODEL_NAME = "llama-3.1-8b-instant"

# --- 4. MODERN UI (CSS) ---
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top left, #020617, #0f172a); color: #f8fafc; }
    .header-card { background: rgba(15, 23, 42, 0.6); padding: 1.5rem; border-radius: 1rem; text-align: center; border-bottom: 2px solid #3b82f6; margin-bottom: 2rem; }
    .stTabs [aria-selected="true"] { background: linear-gradient(45deg, #2563eb, #7c3aed) !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="header-card"><h1 style="color:white;">UltraAI Super-Asistan</h1><p style="color:#94a3b8;">Hafızalı ve Profesyonel Çalışma Platformu</p></div>', unsafe_allow_html=True)

if 'final_content' not in st.session_state: 
    st.session_state.final_content = ""

tab1, tab2, tab3, tab4 = st.tabs(["📥 Giriş", "📝 Özetle", "🎯 Test", "📜 Geçmiş"])

# --- GİRİŞ ---
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

# --- ÖZETLE ---
with tab2:
    if st.session_state.final_content:
        if st.button("🚀 Özeti Hazırla ve Kaydet"):
            with st.spinner('İşleniyor...'):
                try:
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Önemli yerleri vurgulayarak özetle:\n\n{st.session_state.final_content[:10000]}"}],
                        model=MODEL_NAME
                    )
                    summary = res.choices[0].message.content
                    if db is not None:
                        db.collection('ozetler').add({
                            'baslik': st.session_state.final_content[:40].replace('\n', ' ') + "...",
                            'icerik': summary,
                            'tarih': time.time()
                        })
                        st.success("✅ Kaydedildi!")
                    st.info(summary)
                except Exception as e:
                    st.error(f"Hata: {e}")
    else:
        st.warning("⚠️ Önce veri ekle.")

# --- TEST ---
with tab3:
    if st.session_state.final_content:
        if st.button("🎲 Soruları Üret"):
            res = client.chat.completions.create(
                messages=[{"role": "user", "content": f"Bu notlardan 5 test sorusu çıkar:\n\n{st.session_state.final_content[:10000]}"}],
                model=MODEL_NAME
            )
            st.write(res.choices[0].message.content)

# --- GEÇMİŞ ---
with tab4:
    st.subheader("📜 Kayıtlı Notların")
    if db is not None:
        try:
            docs = db.collection('ozetler').order_by('tarih', direction=firestore.Query.DESCENDING).limit(15).stream()
            for doc in docs:
                data = doc.to_dict()
                with st.expander(f"📅 {data.get('baslik')}"):
                    st.write(data.get('icerik'))
                    if st.button("🗑️ Sil", key=doc.id):
                        db.collection('ozetler').document(doc.id).delete()
                        st.rerun()
        except Exception as e:
            st.error(f"Veri çekme hatası: {e}")
