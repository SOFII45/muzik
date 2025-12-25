import streamlit as st
import requests
import io
import random
from PIL import Image

# --- 1. KİŞİSELLEŞTİRME VE AYARLAR ---
UYGULAMA_ADI = "CEMRENİN MÜZİK KUTUSU"
LOGO_DATA = "data:image/png;base64,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"
API_KEY = "AIzaSyAfXdRpKAV9pxZKRGYx5Cj_Btw1lIdCVaw"
MUZIK_FOLDER_ID = "11gcrukvEObg-9Vwu4l_vFW4vRS5Oc2Wz"
FOTO_FOLDER_ID = "1-wlcQSKbhyKPXBB3T0_hvk-rgCTNVICT"
UYGULAMA_SIFRESI = "1234"

st.set_page_config(page_title=UYGULAMA_ADI, page_icon="🎵", layout="centered")

# --- 2. GELİŞMİŞ UI/UX TASARIMI (CSS) ---
st.markdown(f"""
<style>
    .stApp {{
        background: linear-gradient(135deg, #000000, #1a1a1a, #050505);
        color: white;
    }}
    .logo-container {{ text-align: center; padding: 20px; }}
    .logo-img {{ border-radius: 50%; border: 2px solid #1DB954; width: 100px; height: 100px; object-fit: cover; box-shadow: 0 0 15px #1DB954; }}
    
    .stButton>button {{
        width: 100%; border-radius: 25px; border: none;
        background: #1DB954; color: black; font-weight: bold;
        padding: 12px; transition: 0.3s ease;
    }}
    .stButton>button:hover {{ transform: scale(1.03); background: #1ed760; }}
    
    .song-card {{
        background: rgba(255, 255, 255, 0.05); border-radius: 15px;
        padding: 10px 20px; margin-bottom: 8px; border: 1px solid rgba(255, 255, 255, 0.1);
    }}
    .song-title {{ color: #1DB954; font-weight: bold; font-size: 1.1em; }}
    
    /* Yan Panel (Sidebar) Tasarımı */
    section[data-testid="stSidebar"] {{
        background-color: #080808 !important; border-right: 1px solid #222;
    }}
</style>
""", unsafe_allow_html=True)

# --- 3. ŞİFRELEME VE OTURUM KONTROLÜ ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "current_index" not in st.session_state: st.session_state.current_index = 0

if not st.session_state.authenticated:
    st.markdown(f'<div class="logo-container"><img class="logo-img" src="{LOGO_DATA}"></div>', unsafe_allow_html=True)
    st.title(f"🔐 {UYGULAMA_ADI}")
    sifre = st.text_input("Giriş Kodunu Yazın", type="password")
    if st.button("Sisteme Gir"):
        if sifre == UYGULAMA_SIFRESI:
            st.session_state.authenticated = True
            st.rerun()
        else: st.error("Hatalı Kod!")
    st.stop()

# --- 4. VERİ ÇEKME FONKSİYONLARI ---
@st.cache_data(ttl=300)
def get_drive_files(folder_id):
    try:
        url = f"https://www.googleapis.com/drive/v3/files?q='{folder_id}'+in+parents&fields=files(id, name)&key={API_KEY}"
        res = requests.get(url).json()
        return res.get('files', [])
    except: return []

# Dosyaları al
all_songs = sorted([f for f in get_drive_files(MUZIK_FOLDER_ID) if f['name'].endswith('.mp3')], key=lambda x: x['name'])
all_photos = get_drive_files(FOTO_FOLDER_ID)

# --- 5. ANA EKRAN ARAYÜZÜ ---
st.markdown(f'<div class="logo-container"><img class="logo-img" src="{LOGO_DATA}"></div>', unsafe_allow_html=True)
st.title(UYGULAMA_ADI)

search = st.text_input("🔍 Kitaplığında ara...", placeholder="Şarkı veya sanatçı adı...")
filtered_songs = [s for s in all_songs if search.lower() in s['name'].lower()]

# Şarkı Listesi Döngüsü
for song in filtered_songs:
    with st.container():
        col_info, col_play = st.columns([4, 1])
        with col_info:
            name_clean = song['name'].replace(".mp3", "")
            st.markdown(f'<div class="song-card"><span class="song-title">{name_clean}</span></div>', unsafe_allow_html=True)
        with col_play:
            if st.button("▶️", key=song['id']):
                st.session_state.current_index = all_songs.index(song)
                st.rerun()

# --- 6. SABİT YAN PANEL OYNATICI (SIDEBAR) ---
if all_songs:
    current_song = all_songs[st.session_state.current_index]
    current_name = current_song['name'].replace(".mp3", "")
    
    with st.sidebar:
        st.markdown(f"### 🎧 Şimdi Çalıyor")
        st.markdown(f"**{current_name}**")
        
        # Kapak Fotoğrafı Mantığı: Eşleşen varsa al, yoksa rastgele göster
        photo_match = next((p for p in all_photos if current_name.lower() in p['name'].lower()), None)
        final_photo = photo_match if photo_match else (random.choice(all_photos) if all_photos else None)
        
        if final_photo:
            photo_url = f"https://www.googleapis.com/drive/v3/files/{final_photo['id']}?alt=media&key={API_KEY}"
            st.image(photo_url, use_container_width=True)
        
        # Ses Oynatıcı
        stream_url = f"https://www.googleapis.com/drive/v3/files/{current_song['id']}?alt=media&key={API_KEY}"
        st.audio(stream_url, format="audio/mp3")
        
        # Kontrol Butonları
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⏮️ Geri"):
                st.session_state.current_index = (st.session_state.current_index - 1) % len(all_songs)
                st.rerun()
        with c2:
            if st.button("İleri ⏭️"):
                st.session_state.current_index = (st.session_state.current_index + 1) % len(all_songs)
                st.rerun()
        
        st.divider()
        st.caption(f"Liste Sırası: {st.session_state.current_index + 1} / {len(all_songs)}")

# --- 7. OTOMATİK GEÇİŞ VE PERSONEL DOKUNUŞLAR ---
st.markdown("<br><br><br>", unsafe_allow_html=True)
if st.session_state.authenticated:
    st.info("💡 iPhone'da dinlerken yan paneli (Sidebar) kapatıp kütüphanede gezinebilirsin.")