import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely import wkb
import plotly.express as px
from pipeline.transformer import ai_analysis
from pipeline.config import OUTPUT_FILE, REPORTS_DIR

st.set_page_config(page_title="🏛️ SafeCity Dashboard", layout="wide")

# -----------------------------
# Custom CSS for UI
# -----------------------------
st.markdown("""
<style>
/* Card style for metrics */
.metric-card {
    background-color: #f8f9fa;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
    margin-bottom: 10px;
}

/* Section headers with gray background */
.section-header {
    background-color: #e9ecef;
    padding: 8px 15px;
    border-radius: 5px;
    margin-top: 20px;
    margin-bottom: 10px;
    font-weight: bold;
    font-size: 18px;
}

/* Table styling */
.stTable {
    border-radius: 10px;
    overflow: hidden;
}

/* Chatbox area */
.chatbox {
    background-color: #f8f9fa;
    padding: 10px;
    border-radius: 8px;
}

/* Full width header */
.header-container {
    background-color: #2C3E50; 
    padding: 20px; 
    border-radius: 10px; 
    color: white; 
    text-align: center;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Load processed data
# -----------------------------
df = pd.read_parquet(OUTPUT_FILE)

# -----------------------------
# Fix geometry column
# -----------------------------
geom_type = type(df['geometry'].iloc[0])
if geom_type == bytes:
    df['geometry'] = df['geometry'].apply(wkb.loads)
elif geom_type == str:
    from shapely import wkt
    df['geometry'] = df['geometry'].apply(wkt.loads)

# Create GeoDataFrame
gdf_full = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")

# -----------------------------
# Header
# -----------------------------
st.markdown(f"""
<div class="header-container">
    <h1 style="margin:0; font-size:48px;">🏛️ SafeCity Dashboard</h1>
    <p style="margin:5px 0 0 0; font-size:20px;">Analyse de la criminalité en France</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Layout: Filters under header
# -----------------------------
filters_col, content_col = st.columns([1, 4])  # 1:4 ratio

with filters_col:
    st.markdown("<div class='section-header'>Filtres</div>", unsafe_allow_html=True)
    years = df['year'].unique()
    selected_year = st.selectbox("Période", sorted(years))
    top_n = st.slider("Afficher les N zones les plus criminelles", min_value=5, max_value=20, value=10)

# Filter the data for selected year
df_year = df[df['year'] == selected_year].copy()
gdf = gdf_full[gdf_full['year'] == selected_year]

with content_col:
    # -----------------------------
    # Key statistics in styled cards
    # -----------------------------
    total_crimes = df_year['crime_count'].sum()
    evolution = (df_year['crime_rate'].mean() - df['crime_rate'].mean()) / df['crime_rate'].mean() * 100
    top_crime_type = "Vols"

    col1, col2, col3 = st.columns(3)
    col1.markdown(f"<div class='metric-card'><h4>Total de délits</h4><h2>{int(total_crimes)}</h2></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='metric-card'><h4>Évolution moyenne</h4><h2>{evolution:.2f}%</h2></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='metric-card'><h4>Crime le plus fréquent</h4><h2>{top_crime_type}</h2></div>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # -----------------------------
    # Map and top zones side by side
    # -----------------------------
    st.markdown("<div class='section-header'>Carte & Top Zones</div>", unsafe_allow_html=True)
    map_col, top_col = st.columns([3, 1])

    with map_col:
        fig_map = px.choropleth_mapbox(
            gdf,
            geojson=gdf.geometry.__geo_interface__,
            locations=gdf.index,
            color="crime_rate",
            hover_name="name",
            hover_data={"crime_count": True, "population": True, "crime_rate": True},
            color_continuous_scale="Reds",
            mapbox_style="carto-positron",
            zoom=4,
            center={"lat": 46.5, "lon": 2.5},
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with top_col:
        st.markdown(f"<div class='section-header'>Top {top_n} zones à risque</div>", unsafe_allow_html=True)
        top_zones = df_year.nlargest(top_n, "crime_rate")[["name", "crime_rate"]]
        st.table(top_zones.set_index("name"))

    st.markdown("<hr>", unsafe_allow_html=True)

    # -----------------------------
    # Evolution over time
    # -----------------------------
    st.markdown("<div class='section-header'>📈 Évolution du taux de criminalité</div>", unsafe_allow_html=True)
    # Only sum numeric columns excluding 'year' to avoid errors
    numeric_cols = df.select_dtypes(include='number').columns.drop('year')
    df_numeric = df.groupby("year")[numeric_cols].sum().reset_index()
    fig_line = px.line(
        df_numeric,
        x="year",
        y="crime_rate",
        markers=True
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # -----------------------------
    # AI Analysis (collapsible)
    # -----------------------------
    st.markdown("<div class='section-header'>🤖 Rapport IA</div>", unsafe_allow_html=True)
    with st.expander("Afficher le rapport IA"):
        initial_report = ai_analysis(df_year)
        st.markdown(initial_report)

    st.markdown("<hr>", unsafe_allow_html=True)

    # -----------------------------
    # Chatbox
    # -----------------------------
    st.markdown("<div class='section-header'>💬 Posez une question à l'IA</div>", unsafe_allow_html=True)
    user_question = st.text_input("Votre question ici", key="chat_input")

    if user_question:
        response = ai_analysis(df_year, user_prompt=user_question)
        st.text_area("Réponse IA", response, height=200, key="chat_response")
