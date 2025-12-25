import streamlit as st
import requests
import io
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from PIL import Image

# --- AYARLAR ---
API_KEY = "AIzaSyAfXdRpKAV9pxZKRGYx5Cj_Btw1lIdCVaw"
FOLDER_ID = "11gcrukvEObg-9Vwu4l_vFW4vRS5Oc2Wz"
UYGULAMA_SIFRESI = "1234" # Burayı istediğin şifre ile değiştirebilirsin

st.set_page_config(page_title="VIBE Premium", page_icon="🔊", layout="centered")

# --- UI/UX TASARIMI (CSS) ---
st.markdown(f"""
<style>
    /* Arka Plan ve Genel Font */
    .stApp {{
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: white;
    }}
    
    /* Cam Efekti Kartlar */
    .song-card {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}

    /* Buton Tasarımı */
    .stButton>button {{
        width: 100%;
        border-radius: 12px;
        border: none;
        background: linear-gradient(90deg, #1DB954, #191414);
        color: white;
        font-weight: 600;
        padding: 10px;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(29, 185, 84, 0.4);
    }}

    /* Şifre Ekranı */
    .login-box {{
        padding: 40px;
        text-align: center;
        background: rgba(0,0,0,0.4);
        border-radius: 20px;
    }}
</style>
""", unsafe_allow_html=True)

# --- ŞİFRE KONTROLÜ ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.title("🔒 VIBE Access")
    sifre_girisi = st.text_input("Giriş şifresini yazın:", type="password")
    if st.button("Giriş Yap"):
        if sifre_girisi == UYGULAMA_SIFRESI:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Hatalı şifre!")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- ANA UYGULAMA (Giriş Başarılıysa) ---

@st.cache_data(ttl=600)
def get_music_data(api_key, folder_id):
    url = f"https://www.googleapis.com/drive/v3/files?q='{folder_id}'+in+parents+and+mimeType='audio/mpeg'&fields=files(id, name)&key={api_key}"
    return requests.get(url).json().get('files', [])

def get_cover(file_id):
    try:
        r = requests.get(f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media&key={API_KEY}", stream=True)
        audio = MP3(io.BytesIO(r.content), ID3=ID3)
        for tag in audio.tags.values():
            if isinstance(tag, APIC):
                return Image.open(io.BytesIO(tag.data))
    except: return None

# Üst Bar
st.title("🔊 VIBE Premium")
search = st.text_input("🔍 Kitaplığında ara...", placeholder="Şarkı adı yazın")

files = get_music_data(API_KEY, FOLDER_ID)

if files:
    filtered = [f for f in files if search.lower() in f['name'].lower()]
    
    # Şarkı Listesi
    for f in sorted(filtered, key=lambda x: x['name']):
        col_txt, col_btn = st.columns([4, 1])
        with col_txt:
            st.markdown(f"🎵 **{f['name'].replace('.mp3','')}**")
        with col_btn:
            if st.button("Çal", key=f['id']):
                st.session_state.current_id = f['id']
                st.session_state.current_name = f['name']

    # --- SABİT ALT OYNATICI (FLOATING PLAYER) ---
    if 'current_id' in st.session_state:
        st.markdown("<br><br><br>", unsafe_allow_html=True) # Boşluk bırak
        with st.container():
            st.sidebar.markdown("---")
            st.sidebar.subheader("🎧 Şimdi Oynatılıyor")
            
            # Kapak resmi
            art = get_cover(st.session_state.current_id)
            if art:
                st.sidebar.image(art, use_container_width=True)
            
            st.sidebar.write(f"**{st.session_state.current_name.replace('.mp3','')}**")
            
            url = f"https://www.googleapis.com/drive/v3/files/{st.session_state.current_id}?alt=media&key={API_KEY}"
            st.sidebar.audio(url, format="audio/mp3")