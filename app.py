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

# --- UI (CSS) ---
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top left, #0f172a, #020617); color: #e2e8f0; }
    .header-card { background: rgba(30, 41, 59, 0.5); padding: 2rem; border-radius: 1.5rem; text-align: center; margin-bottom: 2rem; }
    .main-title { font-size: 3.5rem; font-weight: 800; background: linear-gradient(to right, #60a5fa, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .stButton>button { width: 100%; border-radius: 0.75rem; background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; border: none; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="header-card"><h1 class="main-title">UltraAI Pro</h1></div>', unsafe_allow_html=True)

if not GROQ_API_KEY:
    st.error("🔑 API Key bulunamadı!")
    st.stop()

# --- YARDIMCI FONKSİON: METNİ PARÇALA ---
def get_chunks(text, size=4000):
    # Ücretsiz kota sınırı (6000) olduğu için metni 4000 karakterlik parçalara böleriz
    return [text[i:i+size] for i in range(0, len(text), size)]

# --- ANA PANEL ---
col_main, col_side = st.columns([2, 1])

with col_side:
    st.markdown("### 📥 Giriş")
    option = st.selectbox("Yöntem:", ["Metin Olarak", "PDF Dosyası"])
    final_content = ""
    if option == "Metin Olarak":
        final_content = st.text_area("Notları yapıştır:", height=300)
    else:
        uploaded_pdf = st.file_uploader("PDF Yükle", type=["pdf"])
        if uploaded_pdf:
            with pdfplumber.open(uploaded_pdf) as pdf:
                final_content = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
                st.success(f"✅ {len(final_content)} karakter okundu.")

    tone = st.select_slider("Anlatım", options=["Basit", "Akademik", "Sınav Odaklı"])

with col_main:
    if final_content:
        # Eğer metin çok uzunsa sadece ilk kısmını al veya parçalara uyarısı ver
        if len(final_content) > 15000:
            st.warning("⚠️ Notların çok uzun! Ücretsiz kota nedeniyle metnin sadece bir kısmını işleyebiliyorum.")
            processed_text = final_content[:12000] # Güvenli sınır
        else:
            processed_text = final_content

        c1, c2 = st.columns(2)
        MODEL_NAME = "llama-3.1-8b-instant"
        base_prompt = f"Sen profesyonel bir eğitim asistanısın. Dil: {tone}."
        
        with c1:
            if st.button("📝 Özet Çıkar"):
                try:
                    with st.spinner('İşleniyor...'):
                        completion = client.chat.completions.create(
                            messages=[
                                {"role": "system", "content": base_prompt},
                                {"role": "user", "content": f"Önemli yerleri vurgulayarak özetle:\n\n{processed_text}"}
                            ],
                            model=MODEL_NAME,
                        )
                        st.info(completion.choices[0].message.content)
                except Exception as e:
                    st.error("Kota doldu! 1 dakika bekleyip tekrar dene kanka.")

        with c2:
            if st.button("🎯 Soru Hazırla"):
                try:
                    with st.spinner('Hazırlanıyor...'):
                        completion = client.chat.completions.create(
                            messages=[
                                {"role": "system", "content": base_prompt},
                                {"role": "user", "content": f"Bu notlardan 5 test sorusu çıkar:\n\n{processed_text}"}
                            ],
                            model=MODEL_NAME,
                        )
                        st.success(completion.choices[0].message.content)
                except Exception as e:
                    st.error("Kota doldu! Biraz bekle kanka.")
    else:
        st.info("👋 Notlarını bekliyorum!")
