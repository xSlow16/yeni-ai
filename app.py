import streamlit as st
from groq import Groq
import pdfplumber

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="UltraAI | Akıllı Asistan", layout="wide", page_icon="🎓")

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
    .stButton>button { background: linear-gradient(45deg, #2563eb, #7c3aed); color: white; font-weight: bold; border: none; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="header-card"><h1>UltraAI v2.1</h1><p>Daha Anlayışlı, Daha Akıllı</p></div>', unsafe_allow_html=True)

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
            st.success(f"✅ PDF yüklendi!")

# --- TAB 2: ÖZETLE (ÖZEL HATA MESAJLI) ---
with tab2:
    if st.session_state.final_content:
        if st.button("🚀 Özeti Oluştur"):
            with st.spinner('Özetleniyor...'):
                try:
                    # Karakter sınırını biraz daha sıkı tutuyoruz (6000 token için max 12-14k karakter ideal)
                    safe_text = st.session_state.final_content[:14000]
                    
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Önemli yerleri vurgulayarak özetle:\n\n{safe_text}"}],
                        model=MODEL_NAME
                    )
                    st.info(res.choices[0].message.content)
                except Exception as e:
                    # BURASI KRİTİK: Teknik hatayı kullanıcı dostu mesajla değiştiriyoruz
                    if "413" in str(e) or "rate_limit" in str(e):
                        st.error("📂 **Dosya Boyutu Çok Büyük!**")
                        st.warning("Kanka yüklediğin metin Groq limitlerini aşıyor. Lütfen metni parçalara ayırıp yükle ya da PDF'in sadece en önemli sayfalarını kullan.")
                    else:
                        st.error(f"Beklenmedik bir hata oluştu: {e}")
    else:
        st.warning("⚠️ Önce materyal yükle kanka.")

# --- TAB 3: TEST (ÖZEL HATA MESAJLI) ---
with tab3:
    if st.session_state.final_content:
        question_count = st.slider("Soru sayısı:", 1, 20, 5)
        if st.button(f"🎲 {question_count} Soru Hazırla"):
            with st.spinner('Sorular hazırlanıyor...'):
                try:
                    safe_text_test = st.session_state.final_content[:11000]
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Metne dayalı {question_count} test sorusu ve cevap anahtarı hazırla:\n\n{safe_text_test}"}],
                        model=MODEL_NAME
                    )
                    st.write(res.choices[0].message.content)
                except Exception as e:
                    if "413" in str(e) or "rate_limit" in str(e):
                        st.error("📂 **Metin Çok Uzun!**")
                        st.warning("Bu kadar uzun bir metinden tek seferde test hazırlayamıyorum kanka. Lütfen metni kısaltıp tekrar dene.")
                    else:
                        st.error(f"Hata: {e}")
