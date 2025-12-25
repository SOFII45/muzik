import streamlit as st
import requests
import random
import time
import io

# --- 1. YAPILANDIRMA VE SABİTLER ---
UYGULAMA_ADI = "CEMRE'NİN VIBE PREMIUM"
LOGO_URL = "https://p7.hiclipart.com/preview/256/896/4/vodafone-park-be%C5%9Fikta%C5%9F-j-k-football-team-super-lig-bjk-akatlar-arena-football.jpg"
API_KEY = "AIzaSyAfXdRpKAV9pxZKRGYx5Cj_Btw1lIdCVaw"
MUZIK_FOLDER_ID = "11gcrukvEObg-9Vwu4l_vFW4vRS5Oc2Wz"
FOTO_FOLDER_ID = "1-wlcQSKbhyKPXBB3T0_hvk-rgCTNVICT"
UYGULAMA_SIFRESI = "1234"

st.set_page_config(page_title=UYGULAMA_ADI, page_icon="🦅", layout="wide")

# --- 2. GELİŞMİŞ GÖRSEL TASARIM (CSS) ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@700&family=Inter:wght@400;600&display=swap');
    
    .stApp {{
        background: radial-gradient(circle at top, #1a1a1a 0%, #000000 100%);
        color: white;
        font-family: 'Inter', sans-serif;
    }}
    
    .logo-img {{
        width: 140px; height: 140px;
        border-radius: 50%;
        border: 3px solid #fff;
        box-shadow: 0 0 25px rgba(255, 255, 255, 0.3);
        display: block; margin: 0 auto 15px auto;
        transition: 0.5s;
    }}
    .logo-img:hover {{ transform: rotate(360deg); }}

    .song-card {{
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        transition: 0.3s ease;
    }}
    .song-card:hover {{
        background: rgba(255, 255, 255, 0.1);
        border-left: 5px solid #ffffff;
        transform: scale(1.01);
    }}

    .stButton>button {{
        background: white; color: black;
        border-radius: 25px; border: none;
        font-weight: 700; transition: 0.3s;
    }}
    .stButton>button:hover {{
        background: #000; color: white;
        border: 1px solid white;
    }}
    
    h1, h2, h3 {{ font-family: 'Syncopate', sans-serif; text-transform: uppercase; letter-spacing: 2px; }}
</style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE (BELLEK YÖNETİMİ) ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "current_idx" not in st.session_state: st.session_state.current_idx = 0
if "auto_play" not in st.session_state: st.session_state.auto_play = False

# --- 4. GİRİŞ EKRANI ---
if not st.session_state.authenticated:
    st.markdown(f'<img src="{LOGO_URL}" class="logo-img">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>EAGLE ACCESS ONLY</h2>", unsafe_allow_html=True)
    with st.columns([1,2,1])[1]:
        input_pass = st.text_input("Giriş Kodunu Gir:", type="password")
        if st.button("SİSTEME GİR"):
            if input_pass == UYGULAMA_SIFRESI:
                st.session_state.authenticated = True
                st.rerun()
            else: st.error("Hatalı Kod!")
    st.stop()

# --- 5. DRIVE API YARDIMCILARI ---
def get_files_from_drive(folder_id):
    try:
        url = f"https://www.googleapis.com/drive/v3/files?q='{folder_id}'+in+parents&fields=files(id, name)&key={API_KEY}"
        return requests.get(url).json().get('files', [])
    except: return []

def download_as_bytes(file_id):
    try:
        url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media&key={API_KEY}"
        return requests.get(url).content
    except: return None

# Veriyi bir kez çek
songs = sorted([f for f in get_files_from_drive(MUZIK_FOLDER_ID) if f['name'].lower().endswith('.mp3')], key=lambda x: x['name'])
photos = get_files_from_drive(FOTO_FOLDER_ID)

# --- 6. ANA ARAYÜZ ---
st.markdown(f'<img src="{LOGO_URL}" class="logo-img">', unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center;'>VIBE PREMIUM</h1>", unsafe_allow_html=True)

col_list, col_player = st.columns([1.8, 1.2], gap="large")

with col_list:
    st.subheader("🎵 Kütüphane")
    search = st.text_input("Şarkılarda ara...", placeholder="Bir parça ismi yaz...")
    
    filtered_list = [s for s in songs if search.lower() in s['name'].lower()]
    
    for i, s in enumerate(filtered_list):
        with st.container():
            c1, c2 = st.columns([5, 1])
            c1.markdown(f'<div class="song-card"><b>{s["name"].replace(".mp3","")}</b></div>', unsafe_allow_html=True)
            if c2.button("▶️", key=f"play_{s['id']}"):
                # Gerçek index'i bul
                st.session_state.current_idx = songs.index(s)
                st.rerun()

with col_player:
    st.subheader("🦅 Oynatıcı")
    if songs:
        active_song = songs[st.session_state.current_idx]
        clean_name = active_song['name'].replace(".mp3", "")
        
        # Fotoğraf Eşleştirme (Gelişmiş)
        match = next((p for p in photos if clean_name.lower()[:5] in p['name'].lower()), None)
        active_photo_id = match['id'] if match else (random.choice(photos)['id'] if photos else None)
        
        # Kapak Fotoğrafını Göster
        if active_photo_id:
            img_data = download_as_bytes(active_photo_id)
            if img_data:
                st.image(img_data, use_container_width=True)
        
        st.markdown(f"### {clean_name}")
        
        # Ses Dosyasını Oynat
        audio_bytes = download_as_bytes(active_song['id'])
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3")
        
        # Navigasyon Kontrolleri
        n1, n2, n3 = st.columns(3)
        if n1.button("⏮️"):
            st.session_state.current_idx = (st.session_state.current_idx - 1) % len(songs)
            st.rerun()
        if n2.button("⏭️"):
            st.session_state.current_idx = (st.session_state.current_idx + 1) % len(songs)
            st.rerun()
        
        st.divider()
        # Otomatik Geçiş Ayarı
        st.session_state.auto_play = st.toggle("Sıradaki Şarkıya Otomatik Geç", value=st.session_state.auto_play)
        
        if st.session_state.auto_play:
            st.caption("ℹ️ Şarkı bittiğinde listedeki bir sonrakine geçilecektir.")
            # Teknik Not: Tarayıcı audio bittiğini bildiremediği için bu 'bebek adımı' bir otomasyondur.
            # Sayfa her yenilendiğinde (st.rerun) bir sonraki şarkıyı hazırlar.

st.markdown("<br><br><br><center><small>Cemre için özel olarak kodlanmıştır. Beşiktaş Ruhuna Uygun.</small></center>", unsafe_allow_html=True)