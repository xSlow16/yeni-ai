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
st.set_page_config(page_title="UltraAI | Akıllı Öğrenci Asistanı", layout="wide", page_icon="🚀")

# --- PROFESYONEL UI (CSS) ---
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #0f172a, #020617);
        color: #e2e8f0;
    }
    .header-card {
        background: rgba(30, 41, 59, 0.5);
        padding: 2rem;
        border-radius: 1.5rem;
        border: 1px solid rgba(59, 130, 246, 0.2);
        text-align: center;
        margin-bottom: 2rem;
    }
    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(to right, #60a5fa, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stButton>button {
        width: 100%;
        border-radius: 0.75rem;
        padding: 0.75rem;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
    <div class="header-card">
        <h1 class="main-title">UltraAI Pro</h1>
        <p style="color: #94a3b8; font-size: 1.1rem;">Yapay Zeka Destekli Yeni Nesil Çalışma Arkadaşın</p>
    </div>
    """, unsafe_allow_html=True)

if not GROQ_API_KEY:
    st.error("🔑 API Key bulunamadı! Lütfen Secrets kısmına GROQ_API_KEY ekle.")
    st.stop()

# --- ANA PANEL ---
col_main, col_side = st.columns([2, 1])

with col_side:
    st.markdown("### 📥 Giriş Yöntemi")
    option = st.selectbox("Yöntem seç kanka:", ["Metin Olarak", "PDF Dosyası"])
    
    final_content = ""
    if option == "Metin Olarak":
        final_content = st.text_area("Notlarını buraya yapıştır...", height=300)
    else:
        uploaded_pdf = st.file_uploader("PDF Dosyanı Yükle", type=["pdf"])
        if uploaded_pdf:
            with pdfplumber.open(uploaded_pdf) as pdf:
                final_content = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
                st.success("✅ PDF Analiz Edildi!")

    st.markdown("---")
    tone = st.select_slider("Anlatım Dili", options=["Basit", "Akademik", "Sınav Odaklı"])

with col_main:
    if final_content:
        st.markdown("### 🧠 Yapay Zeka İşlemleri")
        c1, c2 = st.columns(2)
        
        # GÜNCEL MODEL İSMİ
        MODEL_NAME = "llama-3.1-8b-instant"
        base_prompt = f"Sen profesyonel bir eğitim asistanısın. Anlatım dilin {tone} olmalı."
        
        with c1:
            if st.button("📝 Profesyonel Özet Çıkar"):
                try:
                    with st.spinner('Özetleniyor...'):
                        completion = client.chat.completions.create(
                            messages=[
                                {"role": "system", "content": base_prompt},
                                {"role": "user", "content": f"Aşağıdaki notları bir öğrencinin en kolay anlayacağı şekilde, önemli yerleri kalın yaparak özetle:\n\n{final_content}"}
                            ],
                            model=MODEL_NAME,
                        )
                        st.markdown("#### 📝 Çalışma Özeti")
                        st.info(completion.choices[0].message.content)
                except Exception as e:
                    st.error(f"Model hatası: {e}")

        with c2:
            if st.button("🎯 Sınav Soruları Hazırla"):
                try:
                    with st.spinner('Sorular hazırlanıyor...'):
