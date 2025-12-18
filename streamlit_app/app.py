import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely import wkb
import plotly.express as px
from pipeline.transformer import ai_analysis
from pipeline.config import OUTPUT_FILE, REPORTS_DIR

st.set_page_config(page_title="🏛️ SafeCity Dashboard", layout="wide")

# Title
st.title("🏛️ SafeCity Dashboard")

# Load processed data
df = pd.read_parquet(OUTPUT_FILE)

# Sidebar: Period selection
years = df['year'].unique()
selected_year = st.sidebar.selectbox("Période", sorted(years))

df_year = df[df['year'] == selected_year].copy()

# -----------------------------
# Fix geometry column
# -----------------------------
# Check type of first element
geom_type = type(df_year['geometry'].iloc[0])
if geom_type == bytes:
    # If bytes, convert from WKB
    df_year['geometry'] = df_year['geometry'].apply(wkb.loads)
elif geom_type == str:
    # If WKT string
    from shapely import wkt
    df_year['geometry'] = df_year['geometry'].apply(wkt.loads)
# else assume already proper shapely objects

# Create GeoDataFrame
gdf = gpd.GeoDataFrame(df_year, geometry='geometry', crs="EPSG:4326")

# -----------------------------
# Map of France with crime rates
# -----------------------------
st.subheader("Carte de France - Taux de criminalité")

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

# -----------------------------
# Key statistics
# -----------------------------
st.subheader("📊 Statistiques clés")
total_crimes = df_year['crime_count'].sum()
evolution = (df_year['crime_rate'].mean() - df['crime_rate'].mean()) / df['crime_rate'].mean() * 100
top_crime_type = "Vols"  # placeholder

st.markdown(f"""
- **Total :** {int(total_crimes)} délits  
- **Évolution :** {evolution:.2f}%  
- **Top :** {top_crime_type} (45%)  
""")

# -----------------------------
# AI Analysis
# -----------------------------
st.subheader("🤖 Analyse IA")
report_text = ai_analysis(df_year)
st.text_area("Analyse IA", report_text, height=200)

# -----------------------------
# Graph: evolution over time
# -----------------------------
st.subheader("📈 Évolution du taux de criminalité")
fig_line = px.line(
    df.groupby("year").sum().reset_index(),
    x="year",
    y="crime_rate",
    markers=True
)
st.plotly_chart(fig_line, use_container_width=True)

# -----------------------------
# User question
# -----------------------------
# -----------------------------
# User question
# -----------------------------
st.subheader("💬 Question")
question = st.text_input("Quel département a le plus progressé ?")

if question:
    try:
        report_for_question = ai_analysis(df_year, user_prompt=question)
        if not report_for_question:
            report_for_question = "L'IA n'a pas renvoyé de réponse. Essayez de poser une question plus détaillée."
    except Exception as e:
        report_for_question = f"Erreur lors de l'analyse IA: {e}"

    st.text_area("Résultat", report_for_question, height=150)
