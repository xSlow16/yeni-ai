import streamlit as st
from groq import Groq
import pdfplumber

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="UltraAI | Akıllı Özet", layout="wide", page_icon="🎓")

# --- 2. API AYARLARI ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("🔑 Groq API Key bulunamadı!")
    st.stop()

MODEL_NAME = "llama-3.1-8b-instant"

# --- 3. MODERN UI ---
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top left, #020617, #0f172a); color: #f8fafc; }
    .header-card { 
        background: rgba(15, 23, 42, 0.6); padding: 1.5rem; border-radius: 1rem; 
        text-align: center; border-bottom: 2px solid #3b82f6; margin-bottom: 2rem; 
    }
    .stButton>button { background: linear-gradient(45deg, #2563eb, #7c3aed); color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="header-card"><h1 style="color:white;">UltraAI Lite</h1><p style="color:#94a3b8;">Hızlı Özetleme ve Test Sistemi</p></div>', unsafe_allow_html=True)

if 'final_content' not in st.session_state: 
    st.session_state.final_content = ""

tab1, tab2, tab3 = st.tabs(["📥 Materyal Yükle", "📝 Özet Çıkar", "🎯 Test Çöz"])

# --- TAB 1: GİRİŞ ---
with tab1:
    st.subheader("📚 Çalışma Materyali")
    method = st.radio("Yöntem:", ["Metin Yapıştır", "PDF Dosyası Yükle"], horizontal=True)
    
    if method == "Metin Yapıştır":
        st.session_state.final_content = st.text_area("Notlarını buraya yapıştır:", value=st.session_state.final_content, height=400, key="text_input")
    else:
        file = st.file_uploader("PDF seç", type="pdf")
        if file:
            with pdfplumber.open(file) as p:
                text = "\n".join([page.extract_text() for page in p.pages if page.extract_text()])
                # PDF'i hafızaya alırken çok uzunsa kullanıcıyı uyaralım
                if len(text) > 20000:
                    st.warning("⚠️ PDF çok uzun! Yapay zeka bu metnin en önemli kısımlarına (ilk 15-20 sayfa civarı) odaklanacak.")
                st.session_state.final_content = text
            st.success("✅ PDF içeriği hafızaya alındı!")

# --- TAB 2: ÖZETLE (KRİTİK GÜNCELLEME) ---
with tab2:
    if st.session_state.final_content:
        if st.button("🚀 Özeti Şimdi Oluştur"):
            with st.spinner('İşleniyor...'):
                try:
                    # Token sınırına takılmamak için metni yaklaşık 5000-5500 kelimeye (token) sınırlıyoruz
                    safe_text = st.session_state.final_content[:18000] 
                    
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Aşağıdaki notları önemli noktaları vurgulayarak özetle. Eğer metin yarıda kesilmişse elindeki kısmın en mantıklı özetini çıkar:\n\n{safe_text}"}],
                        model=MODEL_NAME
                    )
                    st.info(res.choices[0].message.content)
                except Exception as e:
                    st.error(f"Hata: {e}")
    else:
        st.warning("⚠️ Önce materyal yükle kanka.")

# --- TAB 3: TEST ---
with tab3:
    if st.session_state.final_content:
        question_count = st.slider("Soru sayısı:", 1, 20, 5)
        if st.button(f"🎲 {question_count} Soru Hazırla"):
            with st.spinner('Hazırlanıyor...'):
                try:
                    # Test hazırlarken de aynı sınırı uyguluyoruz
                    safe_text_test = st.session_state.final_content[:15000]
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Bu metne dayalı {question_count} adet test sorusu ve cevap anahtarı hazırlayabilir misin?\n\n{safe_text_test}"}],
                        model=MODEL_NAME
                    )
                    st.write(res.choices[0].message.content)
                except Exception as e:
                    st.error(f"Hata: {e}")
