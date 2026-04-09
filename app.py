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
    /* Ana Arka Plan */
    .stApp {
        background: radial-gradient(circle at top left, #0f172a, #020617);
        color: #e2e8f0;
    }
    
    /* Header Kartı */
    .header-card {
        background: rgba(30, 41, 59, 0.5);
        padding: 2rem;
        border-radius: 1.5rem;
        border: 1px solid rgba(59, 130, 246, 0.2);
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px -15px rgba(0, 0, 0, 0.5);
    }
    
    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(to right, #60a5fa, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
    }

    /* Kart Yapıları */
    .stCard {
        background: rgba(30, 41, 59, 0.3);
        padding: 1.5rem;
        border-radius: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 1rem;
    }

    /* Custom Butonlar */
    .stButton>button {
        width: 100%;
        border-radius: 0.75rem;
        padding: 0.75rem;
        font-weight: 600;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        border: none;
        color: white;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
    }

    /* Yan Menü Düzenlemeleri */
    .css-1d391kg { background-color: #0f172a; }
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
    st.warning("⚠️ Sistem meşgul, lütfen daha sonra tekrar deneyiniz (API Key Eksik).")
    st.stop()

# --- ANA PANEL ---
col_main, col_side = st.columns([2, 1])

with col_side:
    st.markdown("### 📥 Giriş Yöntemi")
    option = st.selectbox("Notlarını nasıl iletmek istersin?", ["Metin Olarak", "PDF Dosyası"], label_visibility="collapsed")
    
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
    st.markdown("### ⚙️ Ayarlar")
    tone = st.select_slider("Anlatım Dili", options=["Basit", "Akademik", "Sınav Odaklı"])

with col_main:
    if final_content:
        st.markdown("### 🧠 Yapay Zeka İşlemleri")
        c1, c2 = st.columns(2)
        
        # PROMPT MÜHENDİSLİĞİ (Daha net özetler için)
        base_prompt = f"Sen profesyonel bir eğitim asistanısın. Anlatım dilin {tone} olmalı."
        
        with c1:
            if st.button("📝 Profesyonel Özet Çıkar"):
                with st.spinner('Bilgiler işleniyor...'):
                    completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": base_prompt},
                            {"role": "user", "content": f"Aşağıdaki ders notlarını bir öğrencinin en kolay anlayacağı şekilde, önemli kavramları kalın (bold) yaparak ve hiyerarşik maddeler kullanarak özetle:\n\n{final_content}"}
                        ],
                        model="llama3-70b-8192", # Daha zeki olan 70B modeline geçtik
                    )
                    st.markdown("#### 📝 Çalışma Özeti")
                    st.info(completion.choices[0].message.content)

        with c2:
            if st.button("🎯 Sınav Soruları Hazırla"):
                with st.spinner('Sorular üretiliyor...'):
                    completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": base_prompt},
                            {"role": "user", "content": f"Aşağıdaki notlara dayalı olarak; 3 çoktan seçmeli, 2 açık uçlu soru hazırla. Sorular kavrama ve analiz düzeyinde olsun. En alta cevap anahtarını ekle:\n\n{final_content}"}
                        ],
                        model="llama3-70b-8192",
                    )
                    st.markdown("#### ✍️ Pratik Soruları")
                    st.success(completion.choices[0].message.content)
    else:
        st.info("👋 Başlamak için yan menüden ders notlarını ekle kanka. Senin için en iyi özeti hazırlayacağım!")

# --- FOOTER ---
st.markdown("---")
st.caption("© 2026 UltraAI Pro - Yerel Güç, Küresel Zeka")
