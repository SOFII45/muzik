import streamlit as st
import requests
import random
import time
import io

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="VIBE X-TREME PRO", page_icon="🦅", layout="wide")

API_KEY = "AIzaSyAfXdRpKAV9pxZKRGYx5Cj_Btw1lIdCVaw"
MUZIK_FOLDER_ID = "11gcrukvEObg-9Vwu4l_vFW4vRS5Oc2Wz"
FOTO_FOLDER_ID = "1-wlcQSKbhyKPXBB3T0_hvk-rgCTNVICT"
LOGO_URL = "https://p7.hiclipart.com/preview/256/896/4/vodafone-park-be%C5%9Fikta%C5%9F-j-k-football-team-super-lig-bjk-akatlar-arena-football.jpg"
UYGULAMA_SIFRESI = "1234"

# --- 2. HIZLANDIRICI (CACHE) SİSTEMİ ---
@st.cache_data(ttl=3600)
def get_drive_list(folder_id):
    """Dosya listesini bir kez çeker ve hafızaya alır."""
    try:
        url = f"https://www.googleapis.com/drive/v3/files?q='{folder_id}'+in+parents&fields=files(id, name)&key={API_KEY}"
        return requests.get(url).json().get('files', [])
    except: return []

@st.cache_resource(show_spinner=False)
def load_media(file_id):
    """Medya dosyasını indirir ve RAM'de tutar (Anında oynatma için)."""
    try:
        url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media&key={API_KEY}"
        return requests.get(url).content
    except: return None

# --- 3. PREMIUM UI (CSS) ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;600&display=swap');
    
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
                    url("https://images.unsplash.com/photo-1514525253361-bee8718a340b?q=80&w=1964&auto=format&fit=crop");
        background-size: cover;
        font-family: 'Inter', sans-serif;
    }}
    
    /* Neon Glassmorphism Kartlar */
    .main-card {{
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 30px;
        padding: 30px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.5);
    }}

    .song-row {{
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 10px 20px;
        margin-bottom: 10px;
        transition: 0.4s;
        border: 1px solid transparent;
    }}
    .song-row:hover {{
        background: rgba(255, 255, 255, 0.15);
        border: 1px solid #fff;
        transform: scale(1.02) translateX(10px);
    }}

    /* Eagle Glow Logo */
    .logo-glow {{
        width: 120px;
        filter: drop-shadow(0 0 10px #fff);
        margin-bottom: 20px;
    }}

    h1, h2 {{ font-family: 'Orbitron', sans-serif; color: white; text-transform: uppercase; letter-spacing: 3px; }}
    
    /* Kaydırma Çubuğu */
    ::-webkit-scrollbar {{ width: 5px; }}
    ::-webkit-scrollbar-thumb {{ background: #fff; border-radius: 10px; }}
</style>
""", unsafe_allow_html=True)

# --- 4. SESSION & AUTH ---
if "auth" not in st.session_state: st.session_state.auth = False
if "idx" not in st.session_state: st.session_state.idx = 0
if "auto" not in st.session_state: st.session_state.auto = False

if not st.session_state.auth:
    st.markdown(f'<div style="text-align:center;"><img src="{LOGO_URL}" class="logo-glow"></div>', unsafe_allow_html=True)
    with st.container():
        _, mid, _ = st.columns([1,2,1])
        with mid:
            st.markdown("<h2 style='text-align:center;'>PASSWORD</h2>", unsafe_allow_html=True)
            pw = st.text_input("", type="password", placeholder="Enter Code...")
            if st.button("UNLOCK SYSTEM"):
                if pw == UYGULAMA_SIFRESI:
                    st.session_state.auth = True
                    st.rerun()
                else: st.error("Access Denied!")
    st.stop()

# --- 5. DATA LOADING ---
songs = sorted([f for f in get_drive_list(MUZIK_FOLDER_ID) if f['name'].lower().endswith('.mp3')], key=lambda x: x['name'])
photos = get_drive_list(FOTO_FOLDER_ID)

# --- 6. MAIN INTERFACE ---
st.markdown(f'<div style="text-align:left;"><img src="{LOGO_URL}" width="60"></div>', unsafe_allow_html=True)
st.title("VIBE X-TREME PRO")

col_lib, col_play = st.columns([1.2, 1], gap="large")

with col_lib:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📁 LIBRARY")
    search = st.text_input("🔍 Search tracks...", label_visibility="collapsed", placeholder="Search for a vibe...")
    
    # Kaydırılabilir Liste Alanı
    list_area = st.container(height=500)
    with list_area:
        for i, s in enumerate(songs):
            if search.lower() in s['name'].lower():
                c1, c2 = st.columns([5, 1])
                c1.markdown(f'<div class="song-row"><b>{s["name"][:-4]}</b></div>', unsafe_allow_html=True)
                if c2.button("▶️", key=f"play_{s['id']}"):
                    st.session_state.idx = i
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col_player:
    st.markdown('<div class="main-card" style="text-align:center;">', unsafe_allow_html=True)
    if songs:
        current = songs[st.session_state.idx]
        title = current['name'][:-4]
        
        # Kapak Fotoğrafı Mantığı (Eşleşen veya Rastgele)
        match = next((p for p in photos if title.lower()[:4] in p['name'].lower()), None)
        p_id = match['id'] if match else (random.choice(photos)['id'] if photos else None)
        
        if p_id:
            img_bytes = load_media(p_id)
            if img_bytes:
                st.image(img_bytes, use_container_width=True)
        
        st.markdown(f"<h2>{title}</h2>", unsafe_allow_html=True)
        
        # Audio Player (Anında Yükleme)
        audio_bytes = load_media(current['id'])
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3")
        
        # Kontroller
        b1, b2, b3 = st.columns([1,2,1])
        if b1.button("⏮️ BACK"):
            st.session_state.idx = (st.session_state.idx - 1) % len(songs)
            st.rerun()
        if b3.button("NEXT ⏭️"):
            st.session_state.idx = (st.session_state.idx + 1) % len(songs)
            st.rerun()
            
        st.divider()
        st.session_state.auto = st.toggle("AUTO-ADVANCE (Sequential Play)", value=st.session_state.auto)
        
        if st.session_state.auto:
            st.caption("Auto-next is active. Ready for the next track.")
            
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<p style='text-align:center; margin-top:50px; opacity:0.3;'>Eagle Edition | Powered by Gemini 3 Flash</p>", unsafe_allow_html=True)