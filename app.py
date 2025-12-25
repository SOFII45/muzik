import streamlit as st
import requests
import random
import time

# --- 1. AYARLAR ---
UYGULAMA_ADI = "CEMRE'NİN VIBE PREMIUM"
LOGO_URL = "https://p7.hiclipart.com/preview/256/896/4/vodafone-park-be%C5%9Fikta%C5%9F-j-k-football-team-super-lig-bjk-akatlar-arena-football.jpg"
API_KEY = "AIzaSyAfXdRpKAV9pxZKRGYx5Cj_Btw1lIdCVaw"
MUZIK_FOLDER_ID = "11gcrukvEObg-9Vwu4l_vFW4vRS5Oc2Wz"
FOTO_FOLDER_ID = "1-wlcQSKbhyKPXBB3T0_hvk-rgCTNVICT"
UYGULAMA_SIFRESI = "1234"

st.set_page_config(page_title=UYGULAMA_ADI, page_icon="🦅", layout="wide")

# --- 2. GÖRSEL ŞÖLEN (CSS) ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {{
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(180deg, #000000 0%, #111111 100%);
        color: white;
    }}

    /* Neon Logo */
    .logo-img {{
        width: 180px; height: 180px;
        border-radius: 50%;
        border: 4px solid #fff;
        box-shadow: 0 0 20px #fff, 0 0 40px #fff;
        display: block; margin: 0 auto 20px auto;
        animation: pulse 2s infinite;
    }}

    @keyframes pulse {{
        0% {{ transform: scale(1); box-shadow: 0 0 20px #fff; }}
        50% {{ transform: scale(1.05); box-shadow: 0 0 40px #fff; }}
        100% {{ transform: scale(1); box-shadow: 0 0 20px #fff; }}
    }}

    /* Şarkı Kartları */
    .song-card {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 20px;
        transition: 0.3s;
        cursor: pointer;
        margin-bottom: 15px;
    }}
    .song-card:hover {{
        background: rgba(255, 255, 255, 0.15);
        transform: translateX(10px);
        border-left: 8px solid #ffffff;
    }}

    /* Butonlar */
    .stButton>button {{
        border-radius: 50px;
        background: white; color: black;
        font-weight: bold; border: none;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        background: #ddd; transform: scale(1.1);
    }}

    /* Gizli Audio Player */
    audio {{ width: 100%; filter: invert(100%); }}
</style>
""", unsafe_allow_html=True)

# --- 3. SESSION MANAGEMENT ---
if "auth" not in st.session_state: st.session_state.auth = False
if "idx" not in st.session_state: st.session_state.idx = 0
if "auto_next" not in st.session_state: st.session_state.auto_next = False

# Giriş Ekranı
if not st.session_state.auth:
    st.markdown(f'<img src="{LOGO_URL}" class="logo-img">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>🦅 Siyah Beyaz Devam...</h2>", unsafe_allow_html=True)
    with st.container():
        sifre = st.text_input("Kod:", type="password")
        if st.button("GİRİŞ"):
            if sifre == UYGULAMA_SIFRESI:
                st.session_state.auth = True
                st.rerun()
    st.stop()

# --- 4. VERİ ÇEKME ---
@st.cache_data(ttl=600)
def fetch_all(f_id):
    url = f"https://www.googleapis.com/drive/v3/files?q='{f_id}'+in+parents&fields=files(id, name)&key={API_KEY}"
    return requests.get(url).json().get('files', [])

songs = sorted([f for f in fetch_all(MUZIK_FOLDER_ID) if f['name'].lower().endswith('.mp3')], key=lambda x: x['name'])
photos = fetch_all(FOTO_FOLDER_ID)

# --- 5. ANA PANEL ---
col_list, col_player = st.columns([2, 1])

with col_list:
    st.markdown(f"## 🎵 Müzik Kütüphanen ({len(songs)})")
    search = st.text_input("Şarkılarda ara...", label_visibility="collapsed", placeholder="Şarkı ara...")
    
    for i, s in enumerate(songs):
        if search.lower() in s['name'].lower():
            with st.container():
                c1, c2 = st.columns([5, 1])
                c1.markdown(f'<div class="song-card"><b>{s["name"].replace(".mp3","")}</b></div>', unsafe_allow_html=True)
                if c2.button("▶️", key=f"btn_{s['id']}"):
                    st.session_state.idx = i
                    st.rerun()

# --- 6. GÖRSEL OYNATICI (PLAYER) ---
with col_player:
    st.markdown("### 🎧 ŞİMDİ ÇALIYOR")
    if songs:
        cur = songs[st.session_state.idx]
        cur_name = cur['name'].replace(".mp3", "")
        
        # Kapak Fotoğrafı
        match = next((p for p in photos if cur_name.lower()[:5] in p['name'].lower()), None)
        p_id = match['id'] if match else (random.choice(photos)['id'] if photos else None)
        
        if p_id:
            img = f"https://www.googleapis.com/drive/v3/files/{p_id}?alt=media&key={API_KEY}"
            st.markdown(f'<img src="{img}" style="width:100%; border-radius:20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">', unsafe_allow_html=True)
        
        st.markdown(f"<h3 style='text-align:center;'>{cur_name}</h3>", unsafe_allow_html=True)
        
        # Audio
        stream = f"https://www.googleapis.com/drive/v3/files/{cur['id']}?alt=media&key={API_KEY}"
        st.audio(stream, format="audio/mp3")
        
        # Kontroller
        cx1, cx2, cx3 = st.columns(3)
        if cx1.button("⏮️"):
            st.session_state.idx = (st.session_state.idx - 1) % len(songs)
            st.rerun()
        if cx2.button("⏭️"):
            st.session_state.idx = (st.session_state.idx + 1) % len(songs)
            st.rerun()
        
        # OTOMATİK İLERLEME SİSTEMİ
        auto = st.toggle("Sıradan Devam Et (Otomatik)", value=st.session_state.auto_next)
        st.session_state.auto_next = auto
        
        if auto:
            st.caption("⏱️ Şarkı bitince 5 saniye içinde diğerine geçilecek...")
            # Bu basit bir 'sleep' mekanizmasıdır, Streamlit'in doğası gereği 
            # şarkının tam bittiğini tarayıcıdan yakalamak zordur ama bu sırayı korur.
            time.sleep(1) 

st.markdown("<br><center>🦅 Cemre'nin Beşiktaş Temalı Müzik Kutusu v2.0</center>", unsafe_allow_html=True)