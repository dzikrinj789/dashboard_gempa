import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Konfigurasi halaman ini
st.set_page_config(layout="wide", page_title="Dasbor Interaktif", page_icon="🌋")

@st.cache_data
def load_data():
    df = pd.read_csv('data_gempa_darat.csv')
    df['time'] = pd.to_datetime(df['time'], format='ISO8601')
    def klasifikasi_bmkg(mag):
        if mag < 2.5: return 'Mikro (Tidak Terasa, < 2.5)'
        elif mag <= 5.4: return 'Ringan (Dirasakan, 2.5 - 5.4)'
        elif mag <= 6.0: return 'Sedang (5.5 - 6.0)'
        elif mag <= 6.9: return 'Kuat (6.1 - 6.9)'
        elif mag <= 7.9: return 'Besar (7.0 - 7.9)'
        else: return 'Dahsyat (>= 8.0)'
    df['klasifikasi'] = df['mag'].apply(klasifikasi_bmkg)
    geojson = gpd.read_file('Batas Provinsi 50m.geojson')
    return df, geojson

df_darat, gdf_provinsi = load_data()

st.title("🌋 Dasbor Interaktif Kejadian Gempa di Indonesia")
st.sidebar.header("Filter Dasbor")
min_date = df_darat['time'].min().date()
max_date = df_darat['time'].max().date()
start_date, end_date = st.sidebar.date_input("Pilih Rentang Tanggal:", value=[min_date, max_date], min_value=min_date, max_value=max_date)
list_provinsi = ['Semua Provinsi'] + sorted(df_darat['provinsi'].unique().tolist())
provinsi_terpilih = st.sidebar.selectbox("Pilih Provinsi:", list_provinsi)

df_filtered = df_darat[(df_darat['time'].dt.date >= start_date) & (df_darat['time'].dt.date <= end_date)]
if provinsi_terpilih != 'Semua Provinsi':
    df_main_filtered = df_filtered[df_filtered['provinsi'] == provinsi_terpilih]
else:
    df_main_filtered = df_filtered

st.header("Ringkasan Data Sesuai Filter")
total_gempa = len(df_main_filtered)
mag_tertinggi = df_main_filtered['mag'].max() if total_gempa > 0 else 0
prov_paling_sering = df_main_filtered['provinsi'].mode()[0] if total_gempa > 0 and provinsi_terpilih == 'Semua Provinsi' else provinsi_terpilih
col1, col2, col3 = st.columns(3)
col1.metric("Total Kejadian Gempa", f"{total_gempa:,}")
col2.metric("Magnitudo Tertinggi", f"{mag_tertinggi:.2f}")
col3.metric("Provinsi Terdampak Terbanyak", prov_paling_sering)
st.divider()

tab1, tab2, tab3 = st.tabs(["Peta Risiko Interaktif", "Analisis Tren & Komposisi", "Profil Risiko per Provinsi"])

with tab1:
    st.header("Peta Sebaran dan Risiko Gempa Darat")
    if df_main_filtered.empty:
        st.warning("Tidak ada data untuk filter yang dipilih.")
    else:
        WARNA_KATEGORI = {'Mikro (Tidak Terasa, < 2.5)': '#8FBC8F', 'Ringan (Dirasakan, 2.5 - 5.4)': '#87CEEB', 'Sedang (5.5 - 6.0)': '#FFD700', 'Kuat (6.1 - 6.9)': '#FFA500', 'Besar (7.0 - 7.9)': '#DC143C', 'Dahsyat (>= 8.0)': '#8B0000'}
        KATEGORI_URUTAN = list(WARNA_KATEGORI.keys())
        profil_kerusakan = pd.crosstab(df_main_filtered['provinsi'], df_main_filtered['klasifikasi'])
        for kat in KATEGORI_URUTAN:
            if kat not in profil_kerusakan.columns: profil_kerusakan[kat] = 0
        profil_kerusakan['total'] = profil_kerusakan.sum(axis=1)
        def style_marker(jumlah_gempa):
            if jumlah_gempa < 100: return {'radius': 6, 'color': 'green'}
            elif jumlah_gempa < 500: return {'radius': 9, 'color': 'orange'}
            else: return {'radius': 12, 'color': 'red'}
        m = folium.Map(location=[-2.5, 118], zoom_start=5, tiles='CartoDB positron')
        for index, row in profil_kerusakan.iterrows():
            nama_prov = index
            prov_geom = gdf_provinsi[gdf_provinsi['PROVINSI'] == nama_prov]
            if prov_geom.empty: prov_geom = gdf_provinsi[gdf_provinsi['NAMOBJ'] == nama_prov]
            if not prov_geom.empty:
                gdf_planar = prov_geom.to_crs("EPSG:3857")
                centroid_planar = gdf_planar.geometry.centroid.iloc[0]
                centroid_latlon = gpd.GeoSeries([centroid_planar], crs="EPSG:3857").to_crs("EPSG:4326").iloc[0]
                data_chart = row.drop('total').reset_index(); data_chart.columns = ['klasifikasi', 'jumlah']
                fig_popup = px.bar(data_chart, x='klasifikasi', y='jumlah', color='klasifikasi', color_discrete_map=WARNA_KATEGORI, category_orders={'klasifikasi': KATEGORI_URUTAN}, title=f"Detail Gempa di {nama_prov}")
                fig_popup.update_layout(height=400, width=600, showlegend=False, yaxis=dict(tickmode='linear', tick0=0, dtick=50), margin=dict(b=150))
                html_chart = fig_popup.to_html(full_html=False, include_plotlyjs='cdn')
                iframe = folium.IFrame(html_chart, width=630, height=430)
                popup = folium.Popup(iframe, max_width=650)
                marker_style = style_marker(row['total'])
                folium.CircleMarker(location=[centroid_latlon.y, centroid_latlon.x], radius=marker_style['radius'], color=marker_style['color'], fill=True, fill_color=marker_style['color'], fill_opacity=0.7, popup=popup, tooltip=f"<b>{nama_prov}</b><br>Total Gempa: {row['total']}<br>Klik untuk detail").add_to(m)
        st_folium(m, use_container_width=True, height=600, key="map_risiko")
        st.subheader("Legenda Jumlah Total Gempa per Provinsi")
        leg_col1, leg_col2, leg_col3 = st.columns(3)
        with leg_col1: st.markdown("<div style='display:flex; align-items:center;'><div style='background-color:green; width:20px; height:20px; border-radius:50%; margin-right:10px;'></div> < 100 Kejadian</div>", unsafe_allow_html=True)
        with leg_col2: st.markdown("<div style='display:flex; align-items:center;'><div style='background-color:orange; width:20px; height:20px; border-radius:50%; margin-right:10px;'></div> 100 - 500 Kejadian</div>", unsafe_allow_html=True)
        with leg_col3: st.markdown("<div style='display:flex; align-items:center;'><div style='background-color:red; width:20px; height:20px; border-radius:50%; margin-right:10px;'></div> > 500 Kejadian</div>", unsafe_allow_html=True)
with tab2:
    st.header("Analisis Tren dan Komposisi")
    if df_main_filtered.empty:
        st.warning("Tidak ada data untuk filter yang dipilih.")
    else:
        st.subheader("Tren Kejadian Gempa per Bulan")
        df_ts = df_main_filtered.set_index('time')
        tren_bulanan = df_ts['mag'].resample('ME').agg(['size', 'max'])
        tren_bulanan.rename(columns={'size': 'Jumlah Gempa', 'max': 'Magnitudo Maks'}, inplace=True)
        tren_bulanan['Magnitudo Maks'] = tren_bulanan['Magnitudo Maks'].fillna(0)
        fig_ts = make_subplots(specs=[[{"secondary_y": True}]])
        fig_ts.add_trace(go.Bar(x=tren_bulanan.index, y=tren_bulanan['Jumlah Gempa'], name='Jumlah Gempa'), secondary_y=False)
        fig_ts.add_trace(go.Scatter(x=tren_bulanan.index, y=tren_bulanan['Magnitudo Maks'], name='Magnitudo Maks', marker_color='red'), secondary_y=True)
        st.plotly_chart(fig_ts, use_container_width=True)
        st.subheader("Komposisi Kekuatan Gempa")
        kategori_counts = df_main_filtered['klasifikasi'].value_counts()
        fig_pie = px.pie(values=kategori_counts.values, names=kategori_counts.index, title='Proporsi Gempa Berdasarkan Kekuatan')
        st.plotly_chart(fig_pie, use_container_width=True)
with tab3:
    st.header("Perbandingan Profil Risiko antar Provinsi")
    st.write("Grafik ini membandingkan komposisi kekuatan gempa (berdasarkan filter).")
    
    if df_main_filtered.empty:
        st.warning("Tidak ada data untuk filter yang dipilih.")
    else:
        # PERBAIKAN: Logika diubah untuk menampilkan semua provinsi atau satu provinsi
        
        if provinsi_terpilih == 'Semua Provinsi':
            # Langsung gunakan data yang sudah difilter tanpa batasan top 15
            df_to_plot = df_main_filtered
            title = "Profil Risiko di Semua Provinsi"
        else:
            # Jika satu provinsi dipilih, gunakan data provinsi tersebut
            df_to_plot = df_main_filtered
            title = f"Profil Risiko di {provinsi_terpilih}"
        
        if not df_to_plot.empty:
            profil_risiko = pd.crosstab(df_to_plot['provinsi'], df_to_plot['klasifikasi'])
            
            # Mengurutkan provinsi berdasarkan total gempa agar lebih rapi
            profil_risiko['total'] = profil_risiko.sum(axis=1)
            profil_risiko = profil_risiko.sort_values('total', ascending=False).drop(columns='total')

            # Reorder columns to ensure logical stacking
            # Pastikan variabel KATEGORI_URUTAN dan WARNA_KATEGORI sudah didefinisikan di atas
            # Jika belum, Anda bisa definisikan di sini
            WARNA_KATEGORI = {'Mikro (Tidak Terasa, < 2.5)': '#8FBC8F', 'Ringan (Dirasakan, 2.5 - 5.4)': '#87CEEB', 'Sedang (5.5 - 6.0)': '#FFD700', 'Kuat (6.1 - 6.9)': '#FFA500', 'Besar (7.0 - 7.9)': '#DC143C', 'Dahsyat (>= 8.0)': '#8B0000'}
            KATEGORI_URUTAN = list(WARNA_KATEGORI.keys())
            profil_risiko = profil_risiko.reindex(columns=KATEGORI_URUTAN, fill_value=0)
            
            fig_bar = px.bar(profil_risiko, barmode='stack', title=title,
                           color_discrete_map=WARNA_KATEGORI)
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Tidak ada data untuk ditampilkan pada provinsi yang dipilih.")
