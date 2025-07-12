import streamlit as st
import pandas as pd

st.set_page_config(page_title="Informasi Gempa", page_icon="📚", layout="wide")

st.title("📚 Panduan Kesiapsiagaan Gempa Bumi")
st.markdown("Mengetahui apa yang harus dilakukan dapat menyelamatkan nyawa. Berikut adalah panduan praktis untuk menghadapi gempa bumi.")

st.markdown("---")

# --- KONTEN INFORMASI ---

with st.expander("❓ **Mengenal Skala Magnitudo**", expanded=True):
    st.write("""
    Ukuran kekuatan gempa bumi yang menggambarkan besarnya energi seismik yang dipancarkan oleh sumber gempa dan merupakan hasil pengamatan seismograf.
    """)
    skala_data = {
        "Magnitudo": ["< 2.5", "2.5 - 5.4", "5.5 - 6.0", "6.1 - 6.9", "7.0 - 7.9", "8.0 >"],
        "Efek yang Dirasakan": [
            "Biasanya tidak terasa, tetapi dapat direkam dengan seismograf.",
            "Sering dirasakan, tetapi hanya menyebabkan kerusakan kecil.",
            "Dapat menyebabakan kerusakan ringan pada bangunan dan struktur lainnya.",
            "Dapat menyebabkan kerusakan di daerah berpenduduk padat.",
            "Gempa bumi besar dengan kerusakan serius.",
            "Gempa hebat dan dapat menghancurkan komunitas di dekat pusat gempa."
        ]
    }
    st.table(pd.DataFrame(skala_data))

with st.expander("💡 **Apa yang Harus Dilakukan SEBELUM Gempa?**"):
    st.markdown("""
    - **Kenali Lingkungan Anda**: Ketahui di mana letak pintu keluar, tangga darurat, dan tempat aman di dalam dan di luar gedung/rumah.
    - **Amankan Benda Berat**: Letakkan benda besar dan berat di rak bawah. Gantung bingkai foto atau cermin jauh dari tempat tidur atau sofa.
    - **Siapkan Tas Siaga Bencana (TSB)**: Isi tas dengan persediaan darurat seperti air minum, makanan ringan, P3K, senter, peluit, dan obat-obatan pribadi.
    - **Lakukan Latihan**: Lakukan latihan evakuasi secara rutin bersama keluarga atau rekan kerja. Praktikkan teknik "Berlindung, Lindungi Kepala, Bertahan" (Drop, Cover, Hold On).
    """)

with st.expander("🚨 **Apa yang Harus Dilakukan SAAT Gempa?**"):
    st.markdown("""
    - **Jika di Dalam Ruangan**:
        - **JANGAN KELUAR!** Tetap di dalam.
        - Segera berlindung di bawah meja yang kokoh. Lindungi kepala dan leher dengan lengan Anda.
        - Jauhi jendela, kaca, dan benda-benda yang mungkin jatuh.
        - **Jangan gunakan lift.**
    - **Jika di Luar Ruangan**:
        - Cari tempat terbuka yang jauh dari gedung, pohon, tiang listrik, dan papan reklame.
        - Merunduk dan lindungi kepala Anda.
    - **Jika di Dalam Kendaraan**:
        - Menepi dan hentikan kendaraan di tempat yang aman (jauhi jembatan, terowongan, atau rambu besar).
        - Tetap di dalam mobil sampai guncangan berhenti.
    """)

with st.expander("🩹 **Apa yang Harus Dilakukan SETELAH Gempa?**"):
    st.markdown("""
    - **Periksa Diri dan Sekitar**: Pastikan Anda dan orang di sekitar tidak ada yang terluka. Berikan pertolongan pertama jika mampu.
    - **Waspada Gempa Susulan**: Gempa susulan bisa terjadi kapan saja. Tetap waspada.
    - **Periksa Potensi Bahaya**: Periksa kebocoran gas (jika tercium bau gas, segera keluar), kerusakan listrik, dan kerusakan struktur bangunan.
    - **Ikuti Informasi Resmi**: Dengarkan informasi dari sumber yang terpercaya seperti BMKG atau BPBD. Jangan mudah percaya pada hoaks.
    - **Evakuasi jika Diperlukan**: Jika bangunan rusak parah atau berada di area rawan tsunami (jika gempa terjadi di laut), segera evakuasi ke tempat yang lebih tinggi dan aman.
    """)

with st.expander("🗺️ **Sesar Aktif Utama di Indonesia**"):
    st.write(
        "Indonesia, sebagai negara yang terletak di Cincin Api Pasifik, "
        "memiliki banyak sekali sesar (patahan) aktif yang menjadi sumber gempa bumi. "
        "Mengenali sesar-sesar utama ini dapat meningkatkan kewaspadaan nasional."
    )

    # Data sesar aktif utama di seluruh Indonesia
    data_sesar = {
        'Pulau/Wilayah': [
            'Sumatra', 'Jawa', 'Jawa', 'Jawa', 'Jawa', 'Nusa Tenggara', 
            'Sulawesi', 'Sulawesi', 'Papua', 'Papua'
        ],
        'Sesar': [
            'Sesar Semangko (Great Sumatran Fault)', 'Sesar Lembang', 'Sesar Cimandiri',
            'Sesar Baribis', 'Sesar Opak', 'Sesar Naik Flores (Flores Thrust)',
            'Sesar Palu-Koro', 'Sesar Matano', 'Sesar Sorong', 'Sesar Yapen'
        ],
        'Perkiraan Panjang': [
            '~1900 km', '~30 km', '~100 km', '~100 km', '~45 km', '~300 km',
            '~500 km', '~120 km', '~2000 km', '~400 km'
        ],
        'Lokasi Terdampak': [
            'Membentang dari Aceh hingga Lampung', 'Bandung Utara, Lembang', 'Sukabumi, Cianjur',
            'Subang, Purwakarta, Karawang', 'Yogyakarta, Bantul', 'Lepas pantai utara Flores',
            'Donggala, Palu (Sulawesi Tengah)', 'Sekitar Danau Matano (Sulawesi Tengah)', 
            'Kepala Burung Papua Barat', 'Pulau Yapen, Papua'
        ],
        'Potensi Magnitudo': [
            'Bisa mencapai M 7.5+', '6.5 - 7.0 M', '7.0 M', '6.5 - 7.0 M', '6.5 - 6.8 M', 'Bisa mencapai M 8.0',
            '7.5 M', '7.0 - 7.3 M', 'Bisa mencapai M 7.5+', '7.0 - 7.5 M'
        ]
    }
    
    # Membuat DataFrame dan menampilkannya sebagai tabel
    df_sesar = pd.DataFrame(data_sesar)
    st.table(df_sesar)

    st.info(
        "**Catatan:** Daftar ini hanya mencakup beberapa sesar utama yang paling dikenal. "
        "Masih banyak sesar aktif lainnya di seluruh Indonesia."
    )
    st.warning(
        "Data di atas adalah perkiraan untuk tujuan edukasi. "
        "Selalu merujuk pada data resmi dari lembaga geologi dan BMKG untuk informasi yang akurat dan terkini."
    )


st.markdown("---")
st.info("Informasi di halaman ini bersifat umum. Selalu ikuti arahan dari otoritas lokal di wilayah Anda.")