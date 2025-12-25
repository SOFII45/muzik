import streamlit as st
import requests
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
import io
from PIL import Image

# --- AYARLAR ---
API_KEY = "AIzaSyAfXdRpKAV9pxZKRGYx5Cj_Btw1lIdCVaw"
FOLDER_ID = "11gcrukvEObg-9Vwu4l_vFW4vRS5Oc2Wz"

st.set_page_config(page_title="Melis'in Müzik Dünyası", page_icon="🎵", layout="centered")

# Spotify Tarzı Karanlık Tema
st.markdown("""
<style>
    .main { background-color: #121212; }
    .stButton>button { 
        width: 100%; border-radius: 8px; text-align: left; 
        background-color: #181818; color: white; border: 1px solid #282828;
        padding: 10px; margin-bottom: 5px;
    }
    .stButton>button:hover { border-color: #1DB954; }
    .cover-art { border-radius: 10px; margin-bottom: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
</style>
""", unsafe_allow_headers=True)

st.title("🎵 Melis'in Kütüphanesi")

@st.cache_data(ttl=600)
def get_music_list(api_key, folder_id):
    url = f"https://www.googleapis.com/drive/v3/files?q='{folder_id}'+in+parents+and+mimeType='audio/mpeg'&fields=files(id, name)&key={api_key}"
    return requests.get(url).json().get('files', [])

def get_album_art(file_id, api_key):
    # Bu fonksiyon şarkıyı indirip içindeki resmi bulmaya çalışır
    # Not: Çok fazla şarkıda yavaşlama yapabilir, bu yüzden dikkatli kullanıyoruz
    try:
        r = requests.get(f"https://drive.google.com/uc?export=download&id={file_id}", stream=True)
        audio = MP3(io.BytesIO(r.content), ID3=ID3)
        for tag in audio.tags.values():
            if isinstance(tag, APIC):
                return Image.open(io.BytesIO(tag.data))
    except:
        return None
    return None

files = get_music_list(API_KEY, FOLDER_ID)
search = st.text_input("Şarkı veya Sanatçı Ara...", "").lower()

if files:
    filtered = [f for f in files if search in f['name'].lower()]
    for f in sorted(filtered, key=lambda x: x['name']):
        col1, col2 = st.columns([1, 4])
        with col1:
            st.write("🎵") # Küçük ikon
        with col2:
            if st.button(f"{f['name'].replace('.mp3','')}", key=f['id']):
                st.session_state.current_id = f['id']
                st.session_state.current_name = f['name']

    # --- OYNATICI VE KAPAK ---
    if 'current_id' in st.session_state:
        st.markdown("---")
        # Kapak Resmini Çek (Dene)
        art = get_album_art(st.session_state.current_id, API_KEY)
        if art:
            st.image(art, width=250, use_container_width=False, output_format="PNG")
        
        st.subheader(st.session_state.current_name.replace(".mp3",""))
        audio_url = f"https://drive.google.com/uc?export=download&id={st.session_state.current_id}"
        st.audio(audio_url)