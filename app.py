import streamlit as st
import requests
import io
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from PIL import Image

# --- AYARLAR ---
API_KEY = "AIzaSyAfXdRpKAV9pxZKRGYx5Cj_Btw1lIdCVaw"
FOLDER_ID = "11gcrukvEObg-9Vwu4l_vFW4vRS5Oc2Wz"

st.set_page_config(page_title="Melis'in Müzik Dünyası", page_icon="🎵")

# TASARIM
st.markdown("""
<style>
    .main { background-color: #0d1117; }
    .stButton>button { 
        width: 100%; border-radius: 12px; text-align: left; 
        background-color: #238636; color: white; font-weight: bold;
        padding: 12px; margin-bottom: 8px; border: none;
    }
    .stButton>button:hover { background-color: #2ea043; }
    .stTextInput>div>div>input { background-color: #161b22; color: white; border: 1px solid #30363d; }
</style>
""", unsafe_allow_html=True)

st.title("🎵 Melis'in Kütüphanesi")

@st.cache_data(ttl=300)
def get_music_list(api_key, folder_id):
    url = f"https://www.googleapis.com/drive/v3/files?q='{folder_id}'+in+parents+and+mimeType='audio/mpeg'&fields=files(id, name)&key={api_key}"
    return requests.get(url).json().get('files', [])

def get_album_art(file_id):
    try:
        # Kapak resmini çekmek için stream linki
        r = requests.get(f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media&key={API_KEY}", stream=True)
        audio = MP3(io.BytesIO(r.content), ID3=ID3)
        for tag in audio.tags.values():
            if isinstance(tag, APIC):
                return Image.open(io.BytesIO(tag.data))
    except: return None

files = get_music_list(API_KEY, FOLDER_ID)
search = st.text_input("🔍 Şarkı Ara...", "").lower()

if files:
    filtered = [f for f in files if search in f['name'].lower()]
    for f in sorted(filtered, key=lambda x: x['name']):
        if st.button(f"▶️ {f['name'].replace('.mp3','')}", key=f['id']):
            st.session_state.current_id = f['id']
            st.session_state.current_name = f['name']

    if 'current_id' in st.session_state:
        st.markdown("---")
        # Kapak Gösterimi
        art = get_album_art(st.session_state.current_id)
        if art:
            st.image(art, width=250)
        else:
            st.caption("🎨 Bu şarkıda gömülü kapak resmi bulunamadı.")
        
        st.subheader(st.session_state.current_name.replace(".mp3",""))
        
        # YENİLENEN ÇALMA LİNKİ (API Üzerinden Doğrudan Akış)
        stream_url = f"https://www.googleapis.com/drive/v3/files/{st.session_state.current_id}?alt=media&key={API_KEY}"
        st.audio(stream_url, format="audio/mp3")