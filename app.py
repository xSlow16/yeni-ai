import streamlit as st
from groq import Groq
import pdfplumber

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="UltraAI | Kesintisiz Özet", layout="wide", page_icon="🎓")

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

st.markdown('<div class="header-card"><h1>UltraAI v2</h1><p>Limitlere Takılmayan Akıllı Asistan</p></div>', unsafe_allow_html=True)

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
                st.session_state.final_content = text
            st.success(f"✅ PDF yüklendi! (Toplam karakter: {len(text)})")

# --- TAB 2: ÖZETLE (GÜVENLİ KIRPMA) ---
with tab2:
    if st.session_state.final_content:
        if st.button("🚀 Özeti Oluştur"):
            with st.spinner('Limitler kontrol ediliyor ve özetleniyor...'):
                try:
                    # 15.000 karakter yaklaşık 4500-5000 token yapar, 6000 sınırının altında kalırız.
                    # Eğer metin çok uzunsa ortadan bir kısmını atlayıp başı ve sonu birleştiriyoruz
                    full_text = st.session_state.final_content
                    if len(full_text) > 15000:
                        safe_text = full_text[:10000] + "\n...[METİN ÇOK UZUN OLDUĞU İÇİN BİR KISMI ATLANDI]...\n" + full_text[-5000:]
                    else:
                        safe_text = full_text
                    
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Aşağıdaki notları önemli noktaları vurgulayarak özetle:\n\n{safe_text}"}],
                        model=MODEL_NAME
                    )
                    st.info(res.choices[0].message.content)
                except Exception as e:
                    st.error(f"Hata: {e}")
    else:
        st.warning("⚠️ Önce materyal yükle.")

# --- TAB 3: TEST (GÜVENLİ KIRPMA) ---
with tab3:
    if st.session_state.final_content:
        question_count = st.slider("Soru sayısı:", 1, 20, 5)
        if st.button(f"🎲 {question_count} Soru Hazırla"):
            with st.spinner('Sorular hazırlanıyor...'):
                try:
                    full_text = st.session_state.final_content
                    # Test için daha dar bir pencere kullanıyoruz ki yanıt (output) tokenları için de yer kalsın
                    safe_text_test = full_text[:12000]
                    
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Bu metne dayalı {question_count} adet test sorusu ve cevap anahtarı hazırla:\n\n{safe_text_test}"}],
                        model=MODEL_NAME
                    )
                    st.write(res.choices[0].message.content)
                except Exception as e:
                    st.error(f"Hata: {e}")
