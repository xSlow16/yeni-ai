import streamlit as st
from groq import Groq
import pdfplumber

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="UltraAI | Kişiselleştirilmiş Test", layout="wide", page_icon="🎓")

# --- 2. API AYARLARI ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("🔑 Groq API Key bulunamadı! Secrets kısmına ekle kanka.")
    st.stop()

MODEL_NAME = "llama-3.1-8b-instant"

# --- 3. MODERN UI (CSS) ---
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top left, #020617, #0f172a); color: #f8fafc; }
    .header-card { 
        background: rgba(15, 23, 42, 0.6); 
        padding: 1.5rem; border-radius: 1rem; text-align: center; 
        border-bottom: 2px solid #3b82f6; margin-bottom: 2rem; 
    }
    .stButton>button { 
        width: 100%; border-radius: 10px; height: 3rem; 
        background: linear-gradient(45deg, #2563eb, #7c3aed); 
        color: white; border: none; font-weight: bold;
    }
    .stSlider [data-baseweb="slider"] { margin-bottom: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="header-card"><h1 style="color:white;">UltraAI Lite</h1><p style="color:#94a3b8;">Kişiselleştirilmiş Özetleme ve Test Hazırlama Sistemi</p></div>', unsafe_allow_html=True)

# --- OTURUM YÖNETİMİ ---
if 'final_content' not in st.session_state: 
    st.session_state.final_content = ""

# --- SEKMELER ---
tab1, tab2, tab3 = st.tabs(["📥 Materyal Yükle", "📝 Özet Çıkar", "🎯 Test Çöz"])

# --- TAB 1: GİRİŞ ---
with tab1:
    st.subheader("📚 Çalışma Materyali")
    method = st.radio("Yöntem seç kanka:", ["Metin Yapıştır", "PDF Dosyası Yükle"], horizontal=True)
    
    if method == "Metin Yapıştır":
        st.session_state.final_content = st.text_area("Notlarını buraya yapıştır:", value=st.session_state.final_content, height=400, key="text_input")
    else:
        file = st.file_uploader("PDF seç", type="pdf")
        if file:
            with pdfplumber.open(file) as p:
                st.session_state.final_content = "\n".join([page.extract_text() for page in p.pages if page.extract_text()])
            st.success("✅ PDF içeriği başarıyla hafızaya alındı!")

# --- TAB 2: ÖZETLE ---
with tab2:
    if st.session_state.final_content:
        st.subheader("📝 Yapay Zeka Özeti")
        if st.button("🚀 Özeti Şimdi Oluştur"):
            with st.spinner('Analiz ediliyor...'):
                try:
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Aşağıdaki notları önemli noktaları vurgulayarak özetle:\n\n{st.session_state.final_content}"}],
                        model=MODEL_NAME
                    )
                    st.markdown("### ✍️ Hazırlanan Notlar")
                    st.info(res.choices[0].message.content)
                except Exception as e:
                    st.error(f"Hata: {e}")
    else:
        st.warning("⚠️ Özet çıkarmak için önce materyal yüklemelisin.")

# --- TAB 3: TEST (MANUEL SORU SAYISI EKLENDİ) ---
with tab3:
    if st.session_state.final_content:
        st.subheader("🎯 Kendini Sına")
        
        # Kullanıcı buradan soru sayısını belirliyor
        question_count = st.slider("Kaç soru hazırlayalım kanka?", min_value=1, max_value=20, value=5)
        
        if st.button(f"🎲 {question_count} Soru Hazırla"):
            with st.spinner(f'{question_count} adet soru hazırlanıyor...'):
                try:
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Bu metne dayalı {question_count} adet çoktan seçmeli test sorusu ve en altta cevap anahtarı hazırla:\n\n{st.session_state.final_content}"}],
                        model=MODEL_NAME
                    )
                    st.success(f"İşte senin için hazırladığım {question_count} soru!")
                    st.write(res.choices[0].message.content)
                except Exception as e:
                    st.error(f"Hata: {e}")
    else:
        st.warning("⚠️ Önce materyal yükle kanka.")
