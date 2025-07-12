import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import seaborn as sns

# --- 1. Konfigurasi Halaman ---
st.set_page_config(
    page_title="Dasbor & Analisis Gempa",
    page_icon="⚠️",
    layout="wide"
)

# --- 2. Fungsi Pemuatan Data dengan Cache ---
@st.cache_data
def load_data():
    """Memuat dan memproses data awal sekali saja untuk efisiensi."""
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

# --- 3. Sidebar ---
st.sidebar.title("Menu Navigasi")
pilihan_tampilan = st.sidebar.radio(
    "Pilih Tampilan:",
    ('Dasbor Interaktif', 'Laporan Analisis Statis')
)
st.sidebar.divider()


# --- Logika Utama Berdasarkan Pilihan Menu ---

if pilihan_tampilan == 'Dasbor Interaktif':
    # --- Kode untuk Dasbor Utama Interaktif ---
    st.title("⚠️ Dasbor Interaktif Gempa Darat di Indonesia")
    
    st.sidebar.header("Filter Dasbor")
    st.sidebar.info("Filter di bawah ini hanya berlaku untuk Dasbor Interaktif.")
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
        if df_main_filtered.empty:
            st.warning("Tidak ada data untuk filter yang dipilih.")
        else:
            if provinsi_terpilih == 'Semua Provinsi':
                df_to_plot = df_main_filtered
                top_provinsi = df_to_plot['provinsi'].value_counts().nlargest(15).index
                df_top = df_to_plot[df_to_plot['provinsi'].isin(top_provinsi)]
                title = "Profil Risiko di 15 Provinsi Teratas"
            else:
                df_top = df_main_filtered
                title = f"Profil Risiko di {provinsi_terpilih}"
            
            if not df_top.empty:
                profil_risiko = pd.crosstab(df_top['provinsi'], df_top['klasifikasi'])
                KATEGORI_URUTAN = list(WARNA_KATEGORI.keys())
                profil_risiko = profil_risiko.reindex(columns=KATEGORI_URUTAN, fill_value=0)
                profil_risiko['total'] = profil_risiko.sum(axis=1)
                profil_risiko = profil_risiko.sort_values('total', ascending=False).drop(columns='total')
                fig_bar = px.bar(profil_risiko, barmode='stack', title=title, color_discrete_map=WARNA_KATEGORI)
                st.plotly_chart(fig_bar, use_container_width=True)


elif pilihan_tampilan == 'Laporan Analisis Statis':
    # --- Kode untuk Laporan Statis ---
    st.title("Laporan Analisis Statis Gempa Darat (2004-2024)")
    st.info("Halaman ini menampilkan analisis dari keseluruhan data mentah untuk memberikan gambaran umum.")
    
    st.header("1. Analisis Pareto: Konsentrasi Gempa per Provinsi")
    provinsi_counts = df_darat['provinsi'].value_counts()
    df_pareto = pd.DataFrame({'jumlah': provinsi_counts})
    df_pareto = df_pareto.sort_values(by='jumlah', ascending=False)
    df_pareto['persen_kumulatif'] = (df_pareto['jumlah'].cumsum() / df_pareto['jumlah'].sum()) * 100
    fig_pareto, ax_pareto = plt.subplots(figsize=(12, 7))
    ax_pareto.bar(df_pareto.index[:15], df_pareto['jumlah'][:15], color="C0")
    ax_pareto.set_ylabel("Jumlah Total Gempa Darat")
    plt.setp(ax_pareto.get_xticklabels(), rotation=75, ha="right")
    ax2_pareto = ax_pareto.twinx()
    ax2_pareto.plot(df_pareto.index[:15], df_pareto['persen_kumulatif'][:15], color="C1", marker="o", ms=5)
    ax2_pareto.yaxis.set_major_formatter(PercentFormatter())
    ax2_pareto.set_ylabel("Persentase Kumulatif")
    fig_pareto.tight_layout()
    st.pyplot(fig_pareto)

    st.header("2. Analisis Distribusi Karakteristik Gempa")
    fig_dist, axes_dist = plt.subplots(1, 3, figsize=(18, 5))
    sns.set_style("whitegrid")
    df_darat['year'] = df_darat['time'].dt.year
    sns.countplot(ax=axes_dist[0], y=df_darat['year'], hue=df_darat['year'], palette="viridis", order=df_darat['year'].value_counts().index, legend=False)
    axes_dist[0].set_title('Jumlah Gempa per Tahun')
    sns.histplot(ax=axes_dist[1], data=df_darat, x='mag', kde=True, bins=20, color='royalblue')
    axes_dist[1].set_title('Distribusi Magnitudo')
    sns.histplot(ax=axes_dist[2], data=df_darat[df_darat['depth'] <= 300], x='depth', kde=True, bins=25, color='darkorange')
    axes_dist[2].set_title('Distribusi Kedalaman (km)')
    fig_dist.tight_layout()
    st.pyplot(fig_dist)

    st.header("3. Peta Choropleth dengan Detail per Provinsi")
    provinsi_counts = df_darat.groupby('provinsi').size().reset_index(name='jumlah_gempa')
    idx_max_mag = df_darat.groupby('provinsi')['mag'].idxmax()
    max_mag_events = df_darat.loc[idx_max_mag, ['provinsi', 'mag', 'time']].copy()
    max_mag_events['tahun_mag_maks'] = max_mag_events['time'].dt.year
    max_mag_events.rename(columns={'mag': 'magnitudo_maks'}, inplace=True)
    provinsi_stats = pd.merge(provinsi_counts, max_mag_events[['provinsi', 'magnitudo_maks', 'tahun_mag_maks']], on='provinsi', how='left')
    prov_col_name = next((col for col in ['PROVINSI', 'NAMOBJ'] if col in gdf_provinsi.columns), None)
    peta_data = gdf_provinsi.merge(provinsi_stats, left_on=prov_col_name, right_on='provinsi', how='left')
    peta_data['jumlah_gempa'] = peta_data['jumlah_gempa'].fillna(0).astype(int)
    peta_data['magnitudo_maks'] = peta_data['magnitudo_maks'].fillna(0)
    peta_data['tahun_mag_maks'] = peta_data['tahun_mag_maks'].fillna('N/A')

    m_static = folium.Map(location=[-2.5, 118], zoom_start=5, tiles='CartoDB positron')
    folium.Choropleth(
        geo_data=peta_data, name='choropleth', data=peta_data,
        columns=['provinsi', 'jumlah_gempa'], key_on=f'feature.properties.{prov_col_name}',
        fill_color='YlOrRd', fill_opacity=0.7, line_opacity=0.2,
        legend_name='Jumlah Total Gempa Darat'
    ).add_to(m_static)
    style_function = lambda x: {'fillColor': 'transparent', 'color': 'transparent', 'weight': 0}
    tooltip = folium.features.GeoJsonTooltip(
        fields=['provinsi', 'jumlah_gempa', 'magnitudo_maks', 'tahun_mag_maks'],
        aliases=['Provinsi:', 'Jumlah Gempa:', 'Magnitudo Tertinggi:', 'Tahun Magnitudo Tertinggi:'],
        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;"),
        localize=True
    )
    folium.GeoJson(peta_data, style_function=style_function, tooltip=tooltip).add_to(m_static)
    folium.LayerControl().add_to(m_static)
    st_folium(m_static, use_container_width=True, height=500, key="map_static_detail")