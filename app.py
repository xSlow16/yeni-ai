import streamlit as st
from groq import Groq
import pdfplumber

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Grok AI | İçerik Analizi", layout="wide", page_icon="⚡")

# --- 2. API AYARLARI ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("🔑 API Key bulunamadı!")
    st.stop()

MODEL_NAME = "llama-3.1-8b-instant"

# --- 3. MODERN UI ---
st.markdown("""
    <style>
    .stApp { background: #0f172a; color: #f8fafc; }
    .main-header { 
        background: linear-gradient(90deg, #1e293b, #334155); 
        padding: 2rem; border-radius: 1.5rem; text-align: center; 
        border: 1px solid #3b82f6; margin-bottom: 2rem;
    }
    .analysis-card {
        background: rgba(30, 41, 59, 0.7); padding: 1.2rem; border-radius: 1rem;
        border-left: 5px solid #3b82f6; margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>⚡ Grok AI v3.2</h1><p>İçeriği Keşfet, Bilgiye Hükmet</p></div>', unsafe_allow_html=True)

if 'final_content' not in st.session_state: 
    st.session_state.final_content = ""
if 'quick_analysis' not in st.session_state:
    st.session_state.quick_analysis = "Materyal yüklediğinde analiz burada görünecek kanka."

# --- SIDEBAR (AKILLI İÇERİK ANALİZİ) ---
with st.sidebar:
    st.title("🔍 Akıllı İçerik Analizi")
    st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
    st.write(st.session_state.quick_analysis)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.final_content and st.button("🔄 Analizi Yenile"):
        with st.spinner('Grok AI inceliyor...'):
            try:
                res = client.chat.completions.create(
                    messages=[{"role": "user", "content": f"Aşağıdaki metni 2-3 kısa cümlede analiz et. Konusu nedir ve ana teması nedir belirt:\n\n{st.session_state.final_content[:5000]}"}],
                    model=MODEL_NAME
                )
                st.session_state.quick_analysis = res.choices[0].message.content
                st.rerun()
            except:
                st.toast("Analiz yapılamadı kanka.", icon="⚠️")

# --- ANA SEKMELER ---
tab1, tab2, tab3, tab4 = st.tabs(["📥 Yükleme", "📝 Akıllı Özet", "🎯 Test Hazırla", "🃏 Flashcards"])

# --- TAB 1: YÜKLEME ---
with tab1:
    method = st.radio("Yükleme Tipi:", ["Metin Yapıştır", "PDF Yükle"], horizontal=True)
    if method == "Metin Yapıştır":
        st.session_state.final_content = st.text_area("Notlar:", value=st.session_state.final_content, height=350, key="text_input")
    else:
        file = st.file_uploader("Dosya Seç", type="pdf")
        if file:
            with pdfplumber.open(file) as p:
                st.session_state.final_content = "\n".join([page.extract_text() for page in p.pages if page.extract_text()])
            st.toast("✅ İçerik yüklendi! Yan panelden analizi görebilirsin.", icon="📄")

# --- TAB 2: ÖZETLE ---
with tab2:
    if st.session_state.final_content:
        if st.button("🚀 Özeti Hazırla"):
            with st.spinner('Grok AI özetliyor...'):
                try:
                    safe_text = st.session_state.final_content[:14000]
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Önemli yerleri vurgulayarak özetle:\n\n{safe_text}"}],
                        model=MODEL_NAME
                    )
                    st.info(res.choices[0].message.content)
                except:
                    st.toast("Dosya çok büyük kanka!", icon="❌")
    else:
        st.warning("Önce materyal yükle kanka.")

# --- TAB 3: TEST ---
with tab3:
    if st.session_state.final_content:
        q_count = st.slider("Soru Adedi:", 1, 20, 5)
        if st.button(f"🎲 {q_count} Soru Hazırla"):
            with st.spinner('Sorular hazırlanıyor...'):
                try:
                    safe_text = st.session_state.final_content[:11000]
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Metne dayalı {q_count} test sorusu ve cevap anahtarı hazırla:\n\n{safe_text}"}],
                        model=MODEL_NAME
                    )
                    st.write(res.choices[0].message.content)
                except:
                    st.toast("Metin çok uzun, sorular hazırlanamadı!", icon="❌")
    else:
        st.warning("Veri yok.")

# --- TAB 4: FLASHCARDS ---
with tab4:
    if st.session_state.final_content:
        if st.button("🎴 Kartları Oluştur"):
            with st.spinner('Kartlar hazırlanıyor...'):
                try:
                    safe_text = st.session_state.final_content[:10000]
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Bu metinden 5 adet 'Terim: Açıklama' şeklinde kart çıkar:\n\n{safe_text}"}],
                        model=MODEL_NAME
                    )
                    cards = res.choices[0].message.content.split('\n')
                    for card in cards:
                        if ":" in card:
                            term, desc = card.split(":", 1)
                            st.info(f"**{term.strip()}** \n\n {desc.strip()}")
                except:
                    st.toast("Kart hazırlarken bir sorun çıktı.", icon="⚠️")
    else:
        st.warning("Veri yüklemedin kanka.")
