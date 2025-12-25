import streamlit as st

# Sayfa Ayarları
st.set_page_config(page_title="Benim Müziğim", page_icon="🎵")

# Uygulama Başlığı
st.title("🎵 Özel Müzik Çalarım")

# Şarkı Listesi (Buraya kendi şarkılarının linklerini ekleyeceksin)
# Örnek olarak bir demo şarkı ekledim
sarkilar = {
    "Şarkı 1 (Örnek)": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    "Şarkı 2 (Örnek)": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"
}

secilen_sarki = st.selectbox("Bir şarkı seç ve dinle:", list(sarkilar.keys()))

# Müzik Çalar
st.audio(sarkilar[secilen_sarki])

st.write(f"Şu an oynatılıyor: **{secilen_sarki}**")