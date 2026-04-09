import streamlit as st
from groq import Groq
import pdfplumber

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Grok AI | Titan v4.0", layout="wide", page_icon="🚀")

# --- 2. API AYARLARI ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("🔑 API Key eksik!")
    st.stop()

MODEL_NAME = "llama-3.1-8b-instant"

# --- 3. Gelişmiş Tasarım (Glassmorphism & Gradient) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #f8fafc; }
    .main-header { 
        background: rgba(255, 255, 255, 0.05); 
        backdrop-filter: blur(10px);
        padding: 3rem; border-radius: 2rem; text-align: center; 
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        margin-bottom: 2.5rem;
    }
    .analysis-card {
        background: rgba(59, 130, 246, 0.1); padding: 1.5rem; border-radius: 1rem;
        border-left: 6px solid #3b82f6; margin-bottom: 1.5rem;
    }
    .topic-tag {
        background: rgba(124, 58, 237, 0.2); border: 1px solid #7c3aed; color: #a78bfa;
        padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; margin: 3px;
        display: inline-block;
    }
    .stButton>button {
        background: linear-gradient(45deg, #3b82f6, #7c3aed);
        border: none; color: white; transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 5px 15px rgba(124, 58, 237, 0.4); }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="main-header"><h1>🚀 Grok AI Titan v4.0</h1><p>Yapay Zeka Destekli Hibrit Öğrenme İstasyonu</p></div>', unsafe_allow_html=True)

if 'final_content' not in st.session_state: 
    st.session_state.final_content = ""
if 'quick_analysis' not in st.session_state:
    st.session_state.quick_analysis = "Analiz için materyal bekleniyor..."
if 'topic_list' not in st.session_state:
    st.session_state.topic_list = []

# --- SIDEBAR (ZENGİNLEŞTİRİLMİŞ ANALİZ) ---
with st.sidebar:
    st.title("🧭 İçerik Rehberi")
    st.markdown("### 🧬 Metin DNA'sı")
    st.markdown(f'<div class="analysis-card">{st.session_state.quick_analysis}</div>', unsafe_allow_html=True)
    
    st.markdown("### 🏷️ Anahtar Kavramlar")
    if st.session_state.topic_list:
        for topic in st.session_state.topic_list:
            st.markdown(f'<span class="topic-tag">#{topic}</span>', unsafe_allow_html=True)
    
    st.markdown("---")
    if st.session_state.final_content and st.button("🛰️ Derin Analiz Yap"):
        with st.spinner('Grok AI veriyi parçalıyor...'):
            try:
                res = client.chat.completions.create(
                    messages=[{"role": "system", "content": "Sen profesyonel bir eğitim koçusun. Sadece Türkçe cevap ver. Format: ANALİZ: [özet] BAŞLIKLAR: [virgülle ayrılmış 5 kavram]"},
                              {"role": "user", "content": f"Şu metni analiz et:\n\n{st.session_state.final_content[:5000]}"}],
                    model=MODEL_NAME
                )
                output = res.choices[0].message.content
                if "ANALİZ:" in output and "BAŞLIKLAR:" in output:
                    st.session_state.quick_analysis = output.split("ANALİZ:")[1].split("BAŞLIKLAR:")[0].strip()
                    st.session_state.topic_list = output.split("BAŞLIKLAR:")[1].strip().split(",")
                st.rerun()
            except: st.toast("Bağlantı hatası kanka!", icon="⚠️")

# --- ANA SEKMELER ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📥 Yükleme", "📝 Akıllı Özet", "🎯 Sınav Modu", "🃏 Kartlar", "💡 Hoca Notu"])

with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        method = st.radio("Metod:", ["Metin", "PDF"], horizontal=True)
        if method == "Metin":
            st.session_state.final_content = st.text_area("İçerik:", value=st.session_state.final_content, height=350)
        else:
            file = st.file_uploader("PDF", type="pdf")
            if file:
                with pdfplumber.open(file) as p:
                    st.session_state.final_content = "\n".join([page.extract_text() for page in p.pages if page.extract_text()])
                st.toast("✅ Veri Akışı Sağlandı!", icon="🧠")
    with col2:
        st.markdown("### 📌 Nasıl Kullanılır?\n1. Materyali yükle.\n2. Yan panelden **Derin Analiz**'i başlat.\n3. Sekmelerden hedefine uygun olanı seç!")

with tab2:
    if st.session_state.final_content:
        if st.button("🔥 Profesyonel Özet Çıkar"):
            with st.spinner('Mürekkep akıyor...'):
                try:
                    res = client.chat.completions.create(
                        messages=[{"role": "system", "content": "Sadece Türkçe ve akademik bir dille özetle."},
                                  {"role": "user", "content": f"Aşağıdaki metni hiyerarşik bir yapıda özetle:\n\n{st.session_state.final_content[:14000]}"}],
                        model=MODEL_NAME
                    )
                    st.markdown("### 📋 Hazırlanan Ders Notu")
                    st.markdown(res.choices[0].message.content)
                except: st.toast("Hata!", icon="❌")
    else: st.warning("İçerik boş kanka.")

with tab3:
    if st.session_state.final_content:
        q_count = st.slider("Zorluk Seviyesi (Soru Sayısı):", 1, 20, 5)
        if st.button("📝 Testi Başlat"):
            with st.spinner('Sorular mühürleniyor...'):
                try:
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Metne dayalı {q_count} adet zorlayıcı test sorusu hazırlaki:\n\n{st.session_state.final_content[:11000]}"}],
                        model=MODEL_NAME
                    )
                    st.write(res.choices[0].message.content)
                except: st.toast("Hata!", icon="❌")

with tab4:
    if st.session_state.final_content:
        if st.button("🎴 Ezber Kartlarını Bas"):
            with st.spinner('Kartlar karıştırılıyor...'):
                try:
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"5 adet 'Soru: Cevap' şeklinde kısa kart oluştur:\n\n{st.session_state.final_content[:10000]}"}],
                        model=MODEL_NAME
                    )
                    st.markdown(res.choices[0].message.content)
                except: st.toast("Hata!", icon="❌")

# --- YENİ: TAB 5 - HOCA NOTU ---
with tab5:
    st.subheader("👨‍🏫 Hoca Bu Metinden Ne Sorar?")
    st.write("Grok AI metni bir öğretmen gözüyle analiz eder ve çıkması en muhtemel yerleri söyler.")
    if st.session_state.final_content:
        if st.button("🔍 Kritik Noktaları Bul"):
            with st.spinner('Sınav kağıdı analiz ediliyor...'):
                try:
                    res = client.chat.completions.create(
                        messages=[{"role": "system", "content": "Sen 20 yıllık bir öğretmensin. Metinden sınavda çıkması muhtemel 3 yeri 'Buraya Dikkat!' başlığıyla açıkla."},
                                  {"role": "user", "content": st.session_state.final_content[:8000]}],
                        model=MODEL_NAME
                    )
                    st.success(res.choices[0].message.content)
                except: st.toast("Analiz başarısız.", icon="❌")
    else: st.warning("Veri yüklemedin kanka.")
