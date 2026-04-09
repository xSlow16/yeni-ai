import streamlit as st
from groq import Groq
import pdfplumber
from fpdf import FPDF
import io

# --- KÜTÜPHANE KONTROL ---
# Terminale: pip install fpdf

# --- API AYARI ---
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="UltraAI Pro | Hepsi Bir Arada", layout="wide", page_icon="⚡")

# --- GÜNCEL UI (CSS) ---
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top left, #020617, #0f172a); color: #f8fafc; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        background-color: rgba(30, 41, 59, 0.4);
        border-radius: 12px;
        color: #94a3b8;
        padding: 0 25px;
        transition: 0.3s;
    }
    .stTabs [aria-selected="true"] { background: linear-gradient(45deg, #2563eb, #7c3aed) !important; color: white !important; }
    .header-card { background: rgba(15, 23, 42, 0.6); padding: 2rem; border-radius: 1.5rem; text-align: center; border: 1px solid rgba(59, 130, 246, 0.3); margin-bottom: 2rem; }
    .main-title { font-size: 3.5rem; font-weight: 800; background: linear-gradient(to right, #38bdf8, #818cf8, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    </style>
    """, unsafe_allow_html=True)

# --- PDF OLUŞTURMA FONKSİYONU ---
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Türkçe karakter sorununu önlemek için latin-1 temizliği yapıyoruz (Basit versiyon)
    clean_text = text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest='S').encode('latin-1')

# --- HEADER ---
st.markdown('<div class="header-card"><h1 class="main-title">UltraAI Super-Asistan</h1><p>Ses, Metin ve PDF: Tam Donanımlı Öğrenme Deneyimi</p></div>', unsafe_allow_html=True)

if not GROQ_API_KEY:
    st.error("🔑 API Key eksik!")
    st.stop()

# --- OTURUM HAFIZASI ---
if 'final_content' not in st.session_state: st.session_state.final_content = ""
if 'summary_result' not in st.session_state: st.session_state.summary_result = ""
if 'quiz_result' not in st.session_state: st.session_state.quiz_result = ""

# --- SEKMELER ---
tab1, tab2, tab3, tab4 = st.tabs(["📥 Kaynak Ekle", "🎙️ Sesli Not (Beta)", "📝 Akıllı Özet", "🎯 Test Çöz"])

# --- TAB 1: KAYNAK EKLE ---
with tab1:
    col_l, col_r = st.columns([2,1])
    with col_l:
        source_type = st.radio("Kaynak Seç:", ["Metin", "PDF"], horizontal=True)
        if source_type == "Metin":
            txt = st.text_area("Notlar:", height=250)
            if txt: st.session_state.final_content = txt
        else:
            file = st.file_uploader("PDF Yükle", type=["pdf"])
            if file:
                with pdfplumber.open(file) as p:
                    st.session_state.final_content = "\n".join([page.extract_text() for page in p.pages if page.extract_text()])
                st.success("PDF Hazır!")
    with col_r:
        st.write("📊 **İstatistikler**")
        st.write(f"Karakter Sayısı: {len(st.session_state.final_content)}")
        if st.button("🧹 Her Şeyi Sıfırla"):
            st.session_state.clear()
            st.rerun()

# --- TAB 2: SESLİ NOT ---
with tab2:
    st.subheader("🎙️ Dersteki Ses Kaydını Metne Dönüştür")
    audio_file = st.file_uploader("Ses Dosyası Yükle (mp3/wav)", type=["mp3", "wav"])
    if audio_file:
        st.info("Bu özellik için OpenAI Whisper veya Groq Whisper API entegrasyonu gerekiyor. Şimdilik metin üzerinden devam ediyoruz.")

# --- TAB 3: AKILLI ÖZET ---
with tab3:
    if st.session_state.final_content:
        tone = st.selectbox("Anlatım:", ["Basit", "Akademik", "Özetin Özeti"])
        if st.button("🚀 Özeti Başlat"):
            with st.spinner('Analiz ediliyor...'):
                res = client.chat.completions.create(
                    messages=[{"role": "user", "content": f"Üslup {tone}. Şu notları özetle:\n\n{st.session_state.final_content[:10000]}"}],
                    model="llama-3.1-8b-instant"
                )
                st.session_state.summary_result = res.choices[0].message.content
        
        if st.session_state.summary_result:
            st.markdown(st.session_state.summary_result)
            # PDF İndirme Butonu
            pdf_bytes = create_pdf(st.session_state.summary_result)
            st.download_button("📥 Özeti PDF Olarak İndir", data=pdf_bytes, file_name="ozet.pdf", mime="application/pdf")
    else:
        st.warning("Önce veri ekle kanka.")

# --- TAB 4: TEST ÇÖZ ---
with tab4:
    if st.session_state.final_content:
        if st.button("🎲 Soru Üret"):
            with st.spinner('Sorular hazırlanıyor...'):
                res = client.chat.completions.create(
                    messages=[{"role": "user", "content": f"Bu notlardan 5 test sorusu çıkar:\n\n{st.session_state.final_content[:10000]}"}],
                    model="llama-3.1-8b-instant"
                )
                st.session_state.quiz_result = res.choices[0].message.content
        
        if st.session_state.quiz_result:
            st.markdown(st.session_state.quiz_result)
            # PDF İndirme Butonu
            quiz_pdf = create_pdf(st.session_state.quiz_result)
            st.download_button("📥 Soruları PDF Olarak İndir", data=quiz_pdf, file_name="test.pdf", mime="application/pdf")
