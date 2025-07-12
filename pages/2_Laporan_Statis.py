import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import seaborn as sns

st.set_page_config(layout="wide", page_title="Informasi Gempa", page_icon="ℹ️")

@st.cache_data
def load_data():
    df = pd.read_csv('data_gempa_darat.csv')
    df['time'] = pd.to_datetime(df['time'], format='ISO8601')
    geojson = gpd.read_file('Batas Provinsi 50m.geojson')
    return df, geojson

df_darat, gdf_provinsi = load_data()

st.title("ℹ️ Laporan Analisis Statis Gempa Darat (2004-2024)")
st.info("Halaman ini menampilkan analisis dari keseluruhan data untuk memberikan gambaran umum tanpa filter.")

# --- Analisis 1: Pareto ---
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

# --- Analisis 2: Distribusi ---
st.header("2. Analisis Distribusi Karakteristik Gempa")
fig_dist, axes_dist = plt.subplots(1, 3, figsize=(18, 5))
sns.set_style("whitegrid")
df_darat['year'] = df_darat['time'].dt.year
sns.countplot(ax=axes_dist[0], y=df_darat['year'], hue=df_darat['year'], palette="viridis", order=df_darat['year'].value_counts().index, legend=False)
axes_dist[0].set_title('Jumlah Gempa per Tahun')
axes_dist[0].set_xlabel('Jumlah Kejadian')
axes_dist[0].set_ylabel('Tahun')
sns.histplot(ax=axes_dist[1], data=df_darat, x='mag', kde=True, bins=20, color='royalblue')
axes_dist[1].set_title('Distribusi Magnitudo')
axes_dist[1].set_xlabel('Magnitudo')
sns.histplot(ax=axes_dist[2], data=df_darat[df_darat['depth'] <= 300], x='depth', kde=True, bins=25, color='darkorange')
axes_dist[2].set_title('Distribusi Kedalaman (km)')
axes_dist[2].set_xlabel('Kedalaman (km)')
fig_dist.tight_layout()
st.pyplot(fig_dist)

# --- Analisis 3: Peta Choropleth ---
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

# ================== BAGIAN BARU ==================
st.divider()
st.header("4. Analisis Korelasi Magnitudo dan Kedalaman")

col1, col2 = st.columns([2, 1]) # Buat 2 kolom dengan rasio 2:1

with col1:
    st.subheader("Scatter Plot Magnitudo vs Kedalaman")
    # Menggunakan regplot untuk melihat garis tren
    fig_corr, ax_corr = plt.subplots(figsize=(10, 6))
    sns.regplot(
        data=df_darat[df_darat['depth'] <= 300], # Fokus pada kedalaman < 300km agar lebih jelas
        x='depth', 
        y='mag',
        scatter_kws={'alpha':0.2}, # Buat titik transparan untuk melihat kepadatan
        line_kws={'color':'red'},
        ax=ax_corr
    )
    ax_corr.set_xlabel("Kedalaman (km)")
    ax_corr.set_ylabel("Magnitudo")
    ax_corr.set_title("Hubungan Sebaran Magnitudo dan Kedalaman")
    st.pyplot(fig_corr)

with col2:
    st.subheader("Matriks Korelasi")
    # Pilih hanya kolom numerik yang relevan
    numeric_data = df_darat[['mag', 'depth']]
    correlation_matrix = numeric_data.corr(method='pearson')
    
    fig_heatmap, ax_heatmap = plt.subplots(figsize=(6, 5))
    sns.heatmap(
        correlation_matrix, 
        annot=True, # Tampilkan angka korelasi
        cmap='coolwarm', 
        fmt=".2f",
        ax=ax_heatmap
    )
    ax_heatmap.set_title("Korelasi Pearson")
    st.pyplot(fig_heatmap)

st.markdown("""
**Interpretasi:**
- **Scatter Plot**: Menunjukkan bahwa gempa darat terkonsentrasi pada kedalaman dangkal (< 100 km) di semua rentang magnitudo. Garis tren merah yang sedikit menurun mengindikasikan adanya hubungan negatif yang sangat lemah.
- **Heatmap Korelasi**: Nilai korelasi antara `mag` dan `depth` adalah **negatif dan mendekati nol**. Ini mengonfirmasi secara statistik bahwa tidak ada hubungan linear yang kuat antara kedalaman dan kekuatan gempa darat. Namun, nilai negatif yang kecil tersebut sejalan dengan kecenderungan bahwa gempa yang lebih merusak (magnitudo besar) lebih sering terjadi pada kedalaman yang lebih dangkal.
""")
