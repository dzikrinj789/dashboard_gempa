import pandas as pd
import streamlit as st

# Konfigurasi untuk halaman utama/beranda
st.set_page_config(
    page_title="Beranda - SiagaGempa",
    page_icon="🌏",
    layout="wide"
)

# Konten Halaman Beranda
st.title("Selamat Datang di SiagaGempa 🌏")
st.header("Platform Analisis Kejadian Gempa Bumi di Indonesia")

# Menambahkan gambar latar belakang (opsional, ganti URL dengan gambar Anda)
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1590484042996-3687053a8c8a?q=80&w=2070&auto=format&fit=crop");
        background-size: cover;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("""
Aplikasi ini dirancang untuk memberikan tiga layanan utama:

- **Analisis Historis**: Menganalisis tingkat risiko fisik suatu lokasi terhadap dampak gempa bumi berdasarkan data historis dan geografis. Ini adalah dasbor interaktif yang bisa Anda filter.
- **Informasi General Gempa**: Menyajikan laporan analisis statis mengenai karakteristik umum gempa bumi di Indonesia berdasarkan keseluruhan data historis.
- **Panduan Gempa**: Memberikan informasi penting tentang apa yang harus dilakukan sebelum, saat, dan setelah gempa bumi untuk meningkatkan kesiapsiagaan masyarakat.

Silakan pilih halaman yang ingin Anda tuju dari menu di sebelah kiri.
""")

st.info("👈 Untuk memulai, pilih halaman **Analisis Interaktif** atau **Analisis Pareto dan General** pada menu di samping.", icon="ℹ️")

st.success("Dibuat dengan ❤️ untuk Indonesia yang lebih tangguh.")

st.caption(f"Update Terakhir: {pd.to_datetime('today').strftime('%d %B %Y')}")