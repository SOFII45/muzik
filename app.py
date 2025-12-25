import streamlit as st
import requests
import random
from streamlit.components.v1 import html

# --- SABİTLER ---
UYGULAMA_ADI = "CEMOŞUN MÜZİK KUTUSU"
LOGO_URL = "https://p7.hiclipart.com/preview/256/896/4/vodafone-park-be%C5%9Fikta%C5%9F-j-k-football-team-super-lig-bjk-akatlar-arena-football.jpg"
API_KEY = "AIzaSyAfXdRpKAV9pxZKRGYx5Cj_Btw1lIdCVaw"
MUZIK_FOLDER_ID = "11gcrukvEObg-9Vwu4l_vFW4vRS5Oc2Wz"
FOTO_FOLDER_ID = "1-wlcQSKbhyKPXBB3T0_hvk-rgCTNVICT"
UYGULAMA_SIFRESI = "1234"

st.set_page_config(page_title=UYGULAMA_ADI, page_icon="🦅", layout="wide")

# --- CSS / PROFESYONEL TASARIM ---
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #0f0f0f 0%, #000000 100%);
    color: white;
    font-family: 'Inter', sans-serif;
}
.logo-img { width: 140px; height: 140px; border-radius:50%; display:block; margin:0 auto; border:3px solid #fff; box-shadow: 0 0 25px rgba(255,255,255,0.3);}
.logo-img:hover { transform: rotate(360deg); transition:0.5s;}
.song-card { 
    background: rgba(255,255,255,0.05); border-radius:15px; padding:15px; margin-bottom:10px;
    transition:0.3s; display:flex; justify-content:space-between; align-items:center;
}
.song-card:hover { background: rgba(255,255,255,0.15); transform: scale(1.02); }
.audio-player { width:100%; border-radius:15px; margin-top:10px;}
h1,h2,h3 { font-family:'Syncopate', sans-serif; text-transform:uppercase; letter-spacing:1.5px; text-align:center;}
</style>
""", unsafe_allow_html=True)

# --- SESSION ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "current_idx" not in st.session_state: st.session_state.current_idx = 0
if "songs" not in st.session_state: st.session_state.songs = []
if "photos" not in st.session_state: st.session_state.photos = []

# --- GİRİŞ ---
if not st.session_state.authenticated:
    st.markdown(f'<img src="{LOGO_URL}" class="logo-img">', unsafe_allow_html=True)
    st.markdown("<h2>EAGLE ACCESS ONLY</h2>", unsafe_allow_html=True)
    with st.columns([1,2,1])[1]:
        input_pass = st.text_input("Giriş Kodunu Gir:", type="password")
        if st.button("SİSTEME GİR"):
            if input_pass == UYGULAMA_SIFRESI:
                st.session_state.authenticated = True
                st.rerun()
            else: st.error("Hatalı Kod!")
    st.stop()

# --- DRIVE ---
@st.cache_data
def get_files(folder_id):
    files, page_token = [], None
    while True:
        url = f"https://www.googleapis.com/drive/v3/files?q='{folder_id}'+in+parents&fields=nextPageToken,files(id,name)&key={API_KEY}"
        if page_token: url += f"&pageToken={page_token}"
        res = requests.get(url).json()
        files.extend(res.get("files",[]))
        page_token = res.get("nextPageToken")
        if not page_token: break
    return files

if not st.session_state.songs:
    st.session_state.songs = sorted([f for f in get_files(MUZIK_FOLDER_ID) if f['name'].lower().endswith(".mp3")], key=lambda x:x['name'])
if not st.session_state.photos:
    st.session_state.photos = get_files(FOTO_FOLDER_ID)

# --- ANA ARAYÜZ ---
st.markdown(f'<img src="{LOGO_URL}" class="logo-img">', unsafe_allow_html=True)
st.markdown("<h1>VIBE PREMIUM</h1>", unsafe_allow_html=True)

col_list, col_player = st.columns([1.8,1.2], gap="large")

# --- KÜTÜPHANE ---
with col_list:
    search = st.text_input("Şarkılarda ara...", placeholder="Parça ismi...")
    filtered = [s for s in st.session_state.songs if search.lower() in s['name'].lower()]
    for i,s in enumerate(filtered):
        c1,c2 = st.columns([5,1])
        c1.markdown(f'<div class="song-card">{s["name"].replace(".mp3","")}</div>', unsafe_allow_html=True)
        if c2.button("▶️", key=f"play_{s['id']}"):
            st.session_state.current_idx = st.session_state.songs.index(s)
            st.experimental_rerun()

# --- OYNATICI VE JS AUTO-PLAY ---
with col_player:
    if st.session_state.songs:
        active = st.session_state.songs[st.session_state.current_idx]
        name_clean = active["name"].replace(".mp3","")
        photo_match = next((p for p in st.session_state.photos if name_clean.lower() == p['name'].lower().replace(".jpg","").replace(".png","")), None)
        img_id = photo_match['id'] if photo_match else (random.choice(st.session_state.photos)['id'] if st.session_state.photos else None)
        if img_id:
            img_bytes = requests.get(f"https://www.googleapis.com/drive/v3/files/{img_id}?alt=media&key={API_KEY}").content
            st.image(img_bytes, use_container_width=True)
        st.markdown(f"### {name_clean}")
        audio_url = f"https://www.googleapis.com/drive/v3/files/{active['id']}?alt=media&key={API_KEY}"
        
        # HTML audio + JS auto-play
        html(f"""
        <audio id="player" class="audio-player" src="{audio_url}" controls autoplay></audio>
        <script>
        const player = document.getElementById("player");
        player.onended = function() {{
            fetch("{st.experimental_get_query_params().get('rerun_url',[''])[0]}").then(()=>location.reload());
        }};
        </script>
        """, height=80)
