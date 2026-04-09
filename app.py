import streamlit as st
from groq import Groq
import pdfplumber

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Grok AI | Akıllı Navigatör", layout="wide", page_icon="⚡")

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
        border-left: 5px solid #3b82f6; margin-bottom: 1rem; font-size: 0.95rem;
    }
    .topic-tag {
        background: #1e293b; border: 1px solid #3b82f6; color: #3b82f6;
        padding: 2px 8px; border-radius: 5px; font-size: 0.85rem; margin-right: 5px;
        display: inline-block; margin-bottom: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>⚡ Grok AI v3.4</h1><p>İçerik Analizi ve Konu Navigasyonu</p></div>', unsafe_allow_html=True)

if 'final_content' not in st.session_state: 
    st.session_state.final_content = ""
if 'quick_analysis' not in st.session_state:
    st.session_state.quick_analysis = "Analiz bekliyor..."
if 'topic_list' not in st.session_state:
    st.session_state.topic_list = []

# --- SIDEBAR (ANALİZ VE KONU BAŞLIKLARI) ---
with st.sidebar:
    st.title("🔍 İçerik Keşfi")
    
    # 1. Analiz Kısmı
    st.markdown("### 📝 Kısa Özet")
    st.markdown(f'<div class="analysis-card">{st.session_state.quick_analysis}</div>', unsafe_allow_html=True)
    
    # 2. Konu Başlıkları Kısmı
    st.markdown("### 📌 Ana Başlıklar")
    if st.session_state.topic_list:
        for topic in st.session_state.topic_list:
            st.markdown(f'<span class="topic-tag"># {topic}</span>', unsafe_allow_html=True)
    else:
        st.write("Henüz başlık tespit edilmedi.")

    st.markdown("---")
    if st.session_state.final_content and st.button("🔄 Analizi & Başlıkları Yenile"):
        with st.spinner('Grok AI haritayı çıkarıyor...'):
            try:
                # Hem analiz hem başlıklar için tek bir çağrı yapıp JSON gibi ayırıyoruz
                res = client.chat.completions.create(
                    messages=[{"role": "system", "content": "Sen bir Türk eğitim asistanısın. Sadece Türkçe cevap ver. Cevabını şu formatta ver: ANALİZ: [analiz cümlesi] BAŞLIKLAR: [başlık1, başlık2, başlık3]"},
                              {"role": "user", "content": f"Şu metni analiz et ve en önemli 5 konu başlığını çıkar:\n\n{st.session_state.final_content[:5000]}"}],
                    model=MODEL_NAME
                )
                output = res.choices[0].message.content
                
                # Basit parçalama mantığı
                if "ANALİZ:" in output and "BAŞLIKLAR:" in output:
                    st.session_state.quick_analysis = output.split("ANALİZ:")[1].split("BAŞLIKLAR:")[0].strip()
                    topics_raw = output.split("BAŞLIKLAR:")[1].strip()
                    st.session_state.topic_list = [t.strip() for t in topics_raw.split(",")]
                
                st.rerun()
            except:
                st.toast("Veriler güncellenemedi kanka.", icon="⚠️")

# --- ANA SEKMELER (Giriş, Özet, Test, Kartlar aynı kalıyor) ---
tab1, tab2, tab3, tab4 = st.tabs(["📥 Yükleme", "📝 Akıllı Özet", "🎯 Test Hazırla", "🃏 Flashcards"])

with tab1:
    method = st.radio("Yöntem:", ["Metin Yapıştır", "PDF Yükle"], horizontal=True)
    if method == "Metin Yapıştır":
        st.session_state.final_content = st.text_area("Notlar:", value=st.session_state.final_content, height=350, key="text_input")
    else:
        file = st.file_uploader("PDF Seç", type="pdf")
        if file:
            with pdfplumber.open(file) as p:
                st.session_state.final_content = "\n".join([page.extract_text() for page in p.pages if page.extract_text()])
            st.toast("✅ Yüklendi! Yan panelden analizi yenileyebilirsin.", icon="📄")

# Diğer sekmeler (Özet, Test, Flashcards) v3.3'teki gibi devam eder...
# (Kodun geri kalanı v3.3 ile aynı olduğu için uzatmamak adına buraya eklemiyorum, 
# ama v3.3'teki ilgili kısımları buraya yapıştırabilirsin kanka.)

with tab2:
    if st.session_state.final_content:
        if st.button("🚀 Özeti Hazırla"):
            with st.spinner('Grok AI özetliyor...'):
                try:
                    res = client.chat.completions.create(
                        messages=[{"role": "system", "content": "Sen bir Türk eğitim asistanısın. Sadece Türkçe özet çıkar."},
                                  {"role": "user", "content": f"Önemli yerleri vurgulayarak özetle:\n\n{st.session_state.final_content[:14000]}"}],
                        model=MODEL_NAME
                    )
                    st.info(res.choices[0].message.content)
                except: st.toast("Hata!", icon="❌")
    else: st.warning("Önce materyal yükle.")

with tab3:
    if st.session_state.final_content:
        q_count = st.slider("Soru Adedi:", 1, 20, 5)
        if st.button(f"🎲 {q_count} Soru Hazırla"):
            with st.spinner('Hazırlanıyor...'):
                try:
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Metne dayalı {q_count} test sorusu ve cevap anahtarı hazırla:\n\n{st.session_state.final_content[:11000]}"}],
                        model=MODEL_NAME
                    )
                    st.write(res.choices[0].message.content)
                except: st.toast("Hata!", icon="❌")
    else: st.warning("Veri yok.")

with tab4:
    if st.session_state.final_content:
        if st.button("🎴 Kartları Oluştur"):
            with st.spinner('Hazırlanıyor...'):
                try:
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Metinden 5 adet çalışma kartı çıkar:\n\n{st.session_state.final_content[:10000]}"}],
                        model=MODEL_NAME
                    )
                    st.write(res.choices[0].message.content)
                except: st.toast("Hata!", icon="❌")
