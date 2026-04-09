import streamlit as st
from groq import Groq
import pdfplumber
import re

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Grok AI | Pro Çalışma Alanı", layout="wide", page_icon="⚡")

# --- 2. API AYARLARI ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("🔑 API Key eksik!")
    st.stop()

MODEL_NAME = "llama-3.1-8b-instant"

# --- 3. Gelişmiş UI Tasarımı ---
st.markdown("""
    <style>
    .stApp { background: #0f172a; color: #f8fafc; }
    .main-header { 
        background: linear-gradient(90deg, #1e293b, #334155); 
        padding: 2rem; border-radius: 1.5rem; text-align: center; 
        border: 1px solid #3b82f6; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #1e293b; padding: 1rem; border-radius: 0.75rem;
        border: 1px solid #475569; text-align: center;
    }
    .stTabs [aria-selected="true"] { 
        background: #3b82f6 !important; border-radius: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="main-header"><h1>⚡ Grok AI v3.0</h1><p>Ders Çalışmayı Sanata Dönüştür</p></div>', unsafe_allow_html=True)

if 'final_content' not in st.session_state: 
    st.session_state.final_content = ""

# --- YAN PANEL (İSTATİSTİKLER) ---
with st.sidebar:
    st.title("📊 Metin Analizi")
    if st.session_state.final_content:
        words = len(st.session_state.final_content.split())
        reading_time = max(1, round(words / 200))
        st.markdown(f"""
        <div class="metric-card">
            <h3>📖 Kelime Sayısı</h3>
            <p style="font-size: 20px; color: #3b82f6;">{words}</p>
        </div><br>
        <div class="metric-card">
            <h3>⏱️ Okuma Süresi</h3>
            <p style="font-size: 20px; color: #10b981;">~{reading_time} Dakika</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Henüz veri yok kanka.")

# --- ANA SEKMELER ---
tab1, tab2, tab3, tab4 = st.tabs(["📥 Yükleme", "📝 Akıllı Özet", "🎯 Test Hazırla", "🃏 Flashcards"])

# --- TAB 1: YÜKLEME ---
with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        method = st.radio("Yükleme Tipi:", ["Metin Yapıştır", "PDF Yükle"], horizontal=True)
        if method == "Metin Yapıştır":
            st.session_state.final_content = st.text_area("Notlar:", value=st.session_state.final_content, height=350, key="text_input")
        else:
            file = st.file_uploader("Dosya Seç", type="pdf")
            if file:
                with pdfplumber.open(file) as p:
                    st.session_state.final_content = "\n".join([page.extract_text() for page in p.pages if page.extract_text()])
                st.success("✅ İçerik Grok AI tarafından işlendi!")
    with col2:
        st.info("💡 **Grok AI Tavsiyesi:** Özet çıkarmadan önce metnin tam yüklendiğinden emin ol kanka. PDF yüklediysen yukarıdaki karakter sayısını kontrol et.")

# --- TAB 2: ÖZET ---
with tab2:
    if st.session_state.final_content:
        if st.button("🚀 Derinlemesine Analiz Et"):
            with st.spinner('Grok AI zekası devrede...'):
                try:
                    safe_text = st.session_state.final_content[:14000]
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Aşağıdaki metni: 1. Ana Fikir, 2. Önemli Detaylar, 3. Önemli İsimler/Tarihler başlıkları altında özetle:\n\n{safe_text}"}],
                        model=MODEL_NAME
                    )
                    st.markdown(res.choices[0].message.content)
                except Exception as e:
                    st.error("Dosya boyutu çok büyük, lütfen bölerek dene kanka!")
    else:
        st.warning("Veri yüklemedin kanka.")

# --- TAB 3: TEST ---
with tab3:
    if st.session_state.final_content:
        q_count = st.slider("Soru Adedi:", 1, 20, 5)
        if st.button(f"🎲 {q_count} Soru Üret"):
            with st.spinner('Sorular hazırlanıyor...'):
                try:
                    safe_text = st.session_state.final_content[:11000]
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Metne dayalı {q_count} adet test sorusu ve cevap anahtarı oluştur:\n\n{safe_text}"}],
                        model=MODEL_NAME
                    )
                    st.write(res.choices[0].message.content)
                except:
                    st.error("Bir sorun çıktı, metin çok uzun olabilir.")

# --- TAB 4: FLASHCARDS (YENİ!) ---
with tab4:
    st.subheader("🃏 Hızlı Tekrar Kartları")
    st.write("Sınavdan önce hızlıca göz atman gereken terimler ve anlamları.")
    if st.session_state.final_content:
        if st.button("🎴 Kartları Hazırla"):
            with st.spinner('Kilit bilgiler çıkarılıyor...'):
                try:
                    safe_text = st.session_state.final_content[:10000]
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Bu metinden 5 adet 'Terim: Açıklama' şeklinde kısa çalışma kartı çıkar:\n\n{safe_text}"}],
                        model=MODEL_NAME
                    )
                    cards = res.choices[0].message.content.split('\n')
                    for card in cards:
                        if ":" in card:
                            term, desc = card.split(":", 1)
                            st.info(f"**{term.strip()}** \n\n {desc.strip()}")
                except:
                    st.error("Hata oluştu kanka.")
    else:
        st.warning("Veri yok.")
