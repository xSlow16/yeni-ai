import streamlit as st
from groq import Groq
import pdfplumber
import io

# --- API AYARI ---
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="UltraAI | Student Dashboard", layout="wide", page_icon="🎓")

# --- GELİŞMİŞ UI (CSS) ---
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top left, #0f172a, #020617); color: #e2e8f0; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: rgba(30, 41, 59, 0.5);
        border-radius: 10px 10px 0px 0px;
        color: #94a3b8;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] { background-color: #3b82f6 !important; color: white !important; }
    .header-card { background: rgba(30, 41, 59, 0.5); padding: 1.5rem; border-radius: 1rem; text-align: center; margin-bottom: 2rem; border-bottom: 3px solid #3b82f6; }
    .main-title { font-size: 3rem; font-weight: 800; background: linear-gradient(to right, #60a5fa, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="header-card"><h1 class="main-title">UltraAI Dashboard</h1><p>Akıllı Not Yönetimi ve Sınav Hazırlık Merkezi</p></div>', unsafe_allow_html=True)

if not GROQ_API_KEY:
    st.error("🔑 API Key bulunamadı! Lütfen Secrets kısmına ekle.")
    st.stop()

# --- OTURUM HAFIZASI (SESSION STATE) ---
if 'final_content' not in st.session_state:
    st.session_state.final_content = ""

# --- SEKMELER ---
tab1, tab2, tab3 = st.tabs(["📥 Not Yükleme", "📝 Akıllı Özet", "🎯 Soru Bankası"])

# --- TAB 1: NOT YÜKLEME ---
with tab1:
    st.subheader("📚 Çalışma Materyallerini Hazırla")
    col_input, col_settings = st.columns([2, 1])
    
    with col_input:
        option = st.radio("Dosya Türü:", ["Metin Yapıştır", "PDF Yükle"], horizontal=True)
        if option == "Metin Yapıştır":
            input_text = st.text_area("Notlarını buraya bırak kanka:", height=300, placeholder="Örn: Osmanlı Devleti Duraklama Dönemi...")
            if input_text:
                st.session_state.final_content = input_text
        else:
            uploaded_pdf = st.file_uploader("PDF Dosyanı Seç", type=["pdf"])
            if uploaded_pdf:
                try:
                    with pdfplumber.open(uploaded_pdf) as pdf:
                        full_text = ""
                        for page in pdf.pages:
                            text = page.extract_text()
                            if text:
                                full_text += text + "\n"
                        st.session_state.final_content = full_text
                    st.success(f"✅ PDF yüklendi! ({len(st.session_state.final_content)} karakter)")
                except Exception as e:
                    st.error(f"PDF okuma hatası: {e}")

    with col_settings:
        tone = st.select_slider("Anlatım Stili:", options=["Basit", "Akademik", "Sınav Odaklı"])
        if st.button("🗑️ Tüm Veriyi Temizle"):
            st.session_state.final_content = ""
            st.rerun()

# --- TAB 2: AKILLI ÖZET ---
with tab2:
    if st.session_state.final_content:
        st.subheader("📝 Yapay Zeka Özeti")
        if st.button("✨ Özeti Hazırla"):
            try:
                with st.spinner('Analiz ediliyor...'):
                    # Kota dostu kesme
                    safe_text = st.session_state.final_content[:10000]
                    completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": f"Sen bir eğitim asistanısın. Üslubun {tone} olsun. Önemli yerleri kalın yap."},
                            {"role": "user", "content": f"Bu ders notlarını hiyerarşik maddelerle özetle:\n\n{safe_text}"}
                        ],
                        model="llama-3.1-8b-instant",
                    )
                    st.info(completion.choices[0].message.content)
            except Exception as e:
                st.error("Bir sorun oluştu. Kota dolmuş olabilir, lütfen bir az bekleyip tekrar dene.")
    else:
        st.warning("⚠️ Özet için önce 'Not Yükleme' sekmesinden veri eklemelisin kanka.")

# --- TAB 3: SORU BANKASI ---
with tab3:
    if st.session_state.final_content:
        st.subheader("🎯 Kendini Test Et")
        q_count = st.slider("Soru Sayısı", 3, 10, 5)
        if st.button("🎲 Soruları Üret"):
            try:
                with st.spinner('Sorular hazırlanıyor...'):
                    safe_text = st.session_state.final_content[:10000]
                    completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": f"Sen bir öğretmensin. Üslubun {tone} olsun."},
                            {"role": "user", "content": f"Bu notlardan {q_count} tane test sorusu ve en alta cevap anahtarı hazırla:\n\n{safe_text}"}
                        ],
                        model="llama-3.1-8b-instant",
                    )
                    st.success(completion.choices[0].message.content)
            except Exception as e:
                st.error("Soru hazırlarken bir hata oluştu. Biraz bekleyip tekrar deneyebilirsin.")
    else:
        st.warning("⚠️ Soru bankası için önce 'Not Yükleme' sekmesinden veri eklemelisin.")
