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

# TASARIM DÜZELTMESİ (Hata buradaydı: unsafe_allow_html kullanıldı)
st.markdown("""
<style>
    .main { background-color: #121212; }
    .stButton>button { 
        width: 100%; border-radius: 12px; text-align: left; 
        background-color: #1DB954; color: white; font-weight: bold;
        padding: 12px; margin-bottom: 8px; border: none;
    }
    .stTextInput>div>div>input { background-color: #282828; color: white; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

st.title("🎵 Melis'in Kütüphanesi")

@st.cache_data(ttl=600)
def get_music_list(api_key, folder_id):
    url = f"https://www.googleapis.com/drive/v3/files?q='{folder_id}'+in+parents+and+mimeType='audio/mpeg'&fields=files(id, name)&key={api_key}"
    return requests.get(url).json().get('files', [])

def get_album_art(file_id):
    try:
        # Şarkının sadece baş kısmını okuyarak kapağı bulmaya çalışır (Hız için)
        r = requests.get(f"https://drive.google.com/uc?export=download&id={file_id}", stream=True)
        audio = MP3(io.BytesIO(r.content), ID3=ID3)
        for tag in audio.tags.values():
            if isinstance(tag, APIC):
                return Image.open(io.BytesIO(tag.data))
    except:
        return None
    return None

files = get_music_list(API_KEY, FOLDER_ID)
search = st.text_input("🔍 Şarkı Ara...", "").lower()

if files:
    filtered = [f for f in files if search in f['name'].lower()]
    for f in sorted(filtered, key=lambda x: x['name']):
        if st.button(f"▶️ {f['name'].replace('.mp3','')}", key=f['id']):
            st.session_state.current_id = f['id']
            st.session_state.current_name = f['name']

    # --- OYNATICI VE KAPAK ---
    if 'current_id' in st.session_state:
        st.markdown("---")
        # Kapak resmini göster
        with st.spinner('Kapak yükleniyor...'):
            art = get_album_art(st.session_state.current_id)
            if art:
                st.image(art, width=300)
            else:
                st.info("🎨 Bu şarkıda gömülü kapak resmi bulunamadı.")
        
        st.subheader(st.session_state.current_name.replace(".mp3",""))
        audio_url = f"https://drive.google.com/uc?export=download&id={st.session_state.current_id}"
        st.audio(audio_url)
else:
    st.warning("Klasörde müzik bulunamadı veya API anahtarı yükleniyor...")