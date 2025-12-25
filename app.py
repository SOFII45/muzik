import streamlit as st
import requests
import random
import base64

# --- 1. AYARLAR VE KİŞİSELLEŞTİRME ---
UYGULAMA_ADI = "CEMRENİN MÜZİK KUTUSU"
# Yeni Beşiktaş Logo Linki
LOGO_URL = "https://p7.hiclipart.com/preview/256/896/4/vodafone-park-be%C5%9Fikta%C5%9F-j-k-football-team-super-lig-bjk-akatlar-arena-football.jpg"
API_KEY = "AIzaSyAfXdRpKAV9pxZKRGYx5Cj_Btw1lIdCVaw"
MUZIK_FOLDER_ID = "11gcrukvEObg-9Vwu4l_vFW4vRS5Oc2Wz"
FOTO_FOLDER_ID = "1-wlcQSKbhyKPXBB3T0_hvk-rgCTNVICT"
UYGULAMA_SIFRESI = "1234"

st.set_page_config(page_title=UYGULAMA_ADI, page_icon="🦅", layout="centered")

# --- 2. GELİŞMİŞ CSS TASARIMI ---
st.markdown(f"""
<style>
    /* Arka Plan ve Genel Tema */
    .stApp {{
        background: linear-gradient(135deg, #000000, #1a1a1a, #050505);
        color: white;
    }}
    
    /* Logo Tasarımı */
    .logo-container {{ text-align: center; padding: 20px; }}
    .logo-img {{ 
        border-radius: 50%; 
        border: 3px solid #ffffff; 
        width: 150px; 
        height: 150px; 
        object-fit: cover; 
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.2); 
    }}
    
    /* Buton Tasarımı */
    .stButton>button {{
        width: 100%; border-radius: 30px; border: none;
        background: linear-gradient(90deg, #000000, #444444); 
        color: white; font-weight: bold;
        padding: 10px; transition: 0.4s ease;
        border: 1px solid #555;
    }}
    .stButton>button:hover {{ 
        transform: translateY(-3px); 
        box-shadow: 0 5px 15px rgba(255, 255, 255, 0.2);
        background: #ffffff; color: black;
    }}
    
    /* Şarkı Kartları */
    .song-card {{
        background: rgba(255, 255, 255, 0.03); 
        border-radius: 15px;
        padding: 15px; 
        margin-bottom: 10px; 
        border-left: 5px solid #ffffff;
    }}
    .song-title {{ color: #eee; font-weight: 600; font-size: 1.1em; }}

    /* Sidebar Oynatıcı */
    section[data-testid="stSidebar"] {{
        background-color: #050505 !important;
        border-right: 1px solid #333;
    }}
</style>
""", unsafe_allow_html=True)

# --- 3. ŞİFRELEME VE SESSION STATE ---
if "auth" not in st.session_state: st.session_state.auth = False
if "idx" not in st.session_state: st.session_state.idx = 0

if not st.session_state.auth:
    st.markdown(f'<div class="logo-container"><img class="logo-img" src="{LOGO_URL}"></div>', unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>Giriş Yap</h1>", unsafe_allow_html=True)
    sifre = st.text_input("Uygulama Şifresi", type="password")
    if st.button("Sistemi Başlat"):
        if sifre == UYGULAMA_SIFRESI:
            st.session_state.auth = True
            st.rerun()
        else: st.error("Hatalı Şifre!")
    st.stop()

# --- 4. DATA FONKSİYONLARI ---
@st.cache_data(ttl=600)
def get_files(f_id):
    try:
        url = f"https://www.googleapis.com/drive/v3/files?q='{f_id}'+in+parents&fields=files(id, name)&key={API_KEY}"
        return requests.get(url).json().get('files', [])
    except: return []

songs = sorted([f for f in get_files(MUZIK_FOLDER_ID) if f['name'].lower().endswith('.mp3')], key=lambda x: x['name'])
photos = get_files(FOTO_FOLDER_ID)

# --- 5. ANA EKRAN ---
st.markdown(f'<div class="logo-container"><img class="logo-img" src="{LOGO_URL}"></div>', unsafe_allow_html=True)
st.title(UYGULAMA_ADI)

search = st.text_input("🔍 Kütüphanede Ara...", placeholder="Şarkı ismi...")
filtered = [s for s in songs if search.lower() in s['name'].lower()]

# Şarkı Listeleme
for s in filtered:
    with st.container():
        col_txt, col_btn = st.columns([5, 1])
        with col_txt:
            st.markdown(f'<div class="song-card"><span class="song-title">{s["name"].replace(".mp3","")}</span></div>', unsafe_allow_html=True)
        with col_btn:
            if st.button("▶️", key=s['id']):
                st.session_state.idx = songs.index(s)
                st.rerun()

# --- 6. GÜÇLÜ SIDEBAR OYNATICI ---
if songs:
    cur = songs[st.session_state.idx]
    cur_clean = cur['name'].replace(".mp3", "")
    
    with st.sidebar:
        st.markdown("### 🦅 Şimdi Çalıyor")
        st.info(f"**{cur_clean}**")
        
        # Kapak Fotoğrafı Mantığı
        match = next((p for p in photos if cur_clean.lower() in p['name'].lower()), None)
        p_id = match['id'] if match else (random.choice(photos)['id'] if photos else None)
        
        if p_id:
            # Görsel çekme linki
            img = f"https://drive.google.com/uc?export=view&id={p_id}"
            # HATA DÜZELTMESİ: use_container_width yerine width='stretch' kullanıldı
            st.image(img, width='stretch')
        
        # SES OYNATICI DÜZELTMESİ
        # Google Drive doğrudan stream'e izin vermediği için 'uc' (user content) linkini kullanıyoruz
        stream_url = f"https://drive.google.com/uc?export=download&id={cur['id']}"
        
        # st.audio bazen cache nedeniyle takılabilir, bu yüzden doğrudan audio_tag kullanabiliriz
        st.audio(stream_url, format="audio/mp3")
        
        # Navigasyon
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⏮️ Geri"):
                st.session_state.idx = (st.session_state.idx - 1) % len(songs)
                st.rerun()
        with c2:
            if st.button("İleri ⏭️"):
                st.session_state.idx = (st.session_state.idx + 1) % len(songs)
                st.rerun()
        
        st.divider()
        st.caption(f"Toplam {len(songs)} şarkı arasından {st.session_state.idx + 1}. çalınıyor.")

# --- 7. BİLGİLENDİRME ---
st.markdown("<br><hr><center><small>Cemre için özel olarak Beşiktaş temasıyla tasarlanmıştır.</small></center>", unsafe_allow_html=True)