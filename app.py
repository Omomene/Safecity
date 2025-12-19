import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely import wkb
import plotly.express as px
from pipeline.transformer import ai_analysis
from pipeline.config import OUTPUT_FILE

st.set_page_config(page_title="🏛️ SafeCity Dashboard", layout="wide")

# -----------------------------
# CSS
# -----------------------------
st.markdown("""
<style>
.metric-card {
    background-color: #f8f9fa;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
}
.section-header {
    background-color: #e9ecef;
    padding: 8px 15px;
    border-radius: 5px;
    margin-top: 20px;
    font-weight: bold;
    font-size: 18px;
}
.header-container {
    background-color: #2C3E50;
    padding: 20px;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Load data
# -----------------------------
df = pd.read_parquet(OUTPUT_FILE)

# -----------------------------
# Department code → name mapping
# -----------------------------
DEPT_NAMES = {
    "01": "Ain", "02": "Aisne", "03": "Allier", "04": "Alpes-de-Haute-Provence",
    "05": "Hautes-Alpes", "06": "Alpes-Maritimes", "07": "Ardèche",
    "08": "Ardennes", "09": "Ariège", "10": "Aube", "11": "Aude",
    "12": "Aveyron", "13": "Bouches-du-Rhône", "14": "Calvados",
    "15": "Cantal", "16": "Charente", "17": "Charente-Maritime",
    "18": "Cher", "19": "Corrèze", "2A": "Corse-du-Sud",
    "2B": "Haute-Corse", "21": "Côte-d'Or", "22": "Côtes-d'Armor",
    "23": "Creuse", "24": "Dordogne", "25": "Doubs", "26": "Drôme",
    "27": "Eure", "28": "Eure-et-Loir", "29": "Finistère",
    "30": "Gard", "31": "Haute-Garonne", "32": "Gers", "33": "Gironde",
    "34": "Hérault", "35": "Ille-et-Vilaine", "36": "Indre",
    "37": "Indre-et-Loire", "38": "Isère", "39": "Jura",
    "40": "Landes", "41": "Loir-et-Cher", "42": "Loire",
    "43": "Haute-Loire", "44": "Loire-Atlantique", "45": "Loiret",
    "46": "Lot", "47": "Lot-et-Garonne", "48": "Lozère",
    "49": "Maine-et-Loire", "50": "Manche", "51": "Marne",
    "52": "Haute-Marne", "53": "Mayenne", "54": "Meurthe-et-Moselle",
    "55": "Meuse", "56": "Morbihan", "57": "Moselle",
    "58": "Nièvre", "59": "Nord", "60": "Oise",
    "61": "Orne", "62": "Pas-de-Calais", "63": "Puy-de-Dôme",
    "64": "Pyrénées-Atlantiques", "65": "Hautes-Pyrénées",
    "66": "Pyrénées-Orientales", "67": "Bas-Rhin",
    "68": "Haut-Rhin", "69": "Rhône", "70": "Haute-Saône",
    "71": "Saône-et-Loire", "72": "Sarthe", "73": "Savoie",
    "74": "Haute-Savoie", "75": "Paris", "76": "Seine-Maritime",
    "77": "Seine-et-Marne", "78": "Yvelines",
    "79": "Deux-Sèvres", "80": "Somme", "81": "Tarn",
    "82": "Tarn-et-Garonne", "83": "Var", "84": "Vaucluse",
    "85": "Vendée", "86": "Vienne", "87": "Haute-Vienne",
    "88": "Vosges", "89": "Yonne", "90": "Territoire de Belfort",
    "91": "Essonne", "92": "Hauts-de-Seine",
    "93": "Seine-Saint-Denis", "94": "Val-de-Marne",
    "95": "Val-d'Oise"
}

df["department_name"] = df["code_insee"].map(DEPT_NAMES)

# -----------------------------
# Fix geometry
# -----------------------------
geom_type = type(df["geometry"].iloc[0])
if geom_type == bytes:
    df["geometry"] = df["geometry"].apply(wkb.loads)
elif geom_type == str:
    from shapely import wkt
    df["geometry"] = df["geometry"].apply(wkt.loads)

gdf_full = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")

# -----------------------------
# Header
# -----------------------------
st.markdown("""
<div class="header-container">
    <h1 style="margin:0;font-size:48px;">🏛️ SafeCity Dashboard</h1>
    <p style="margin-top:5px;font-size:20px;">
        Analyse de la criminalité en France par département
    </p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Layout
# -----------------------------
filters_col, content_col = st.columns([1, 4])

# -----------------------------
# Filters
# -----------------------------
with filters_col:
    st.markdown("<div class='section-header'>Filtres</div>", unsafe_allow_html=True)

    years = ["Toutes les années"] + sorted(df["year"].unique().tolist())
    selected_year = st.selectbox("Année", years)

    departments = sorted(df["department_name"].dropna().unique())
    selected_department = st.selectbox(
        "Département",
        ["Tous"] + departments
    )

    top_n = st.slider("Top N départements", 5, 20, 10)

# -----------------------------
# Apply filters
# -----------------------------
filtered_df = df.copy()

if selected_year != "Toutes les années":
    filtered_df = filtered_df[filtered_df["year"] == selected_year]

if selected_department != "Tous":
    filtered_df = filtered_df[filtered_df["department_name"] == selected_department]

gdf = gdf_full.loc[filtered_df.index]

# -----------------------------
# Content
# -----------------------------
with content_col:

    total_crimes = int(filtered_df["crime_count"].sum())
    avg_rate = filtered_df["crime_rate"].mean()
    top_crime = filtered_df.groupby("crime_type")["crime_count"].sum().idxmax() \
        if "crime_type" in filtered_df.columns else "Vols"

    col1, col2, col3 = st.columns(3)
    col1.markdown(f"<div class='metric-card'><h4>Total délits</h4><h2>{total_crimes}</h2></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='metric-card'><h4>Taux moyen</h4><h2>{avg_rate:.2f}</h2></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='metric-card'><h4>Crime le plus fréquent</h4><h2>{top_crime}</h2></div>", unsafe_allow_html=True)

    # -----------------------------
    # Map
    # -----------------------------
    st.markdown("<div class='section-header'>Carte de la criminalité</div>", unsafe_allow_html=True)

    gdf_map = gdf_full if selected_year == "Toutes les années" else gdf_full[gdf_full["year"] == selected_year]

    fig_map = px.choropleth_mapbox(
        gdf_map,
        geojson=gdf_map.geometry.__geo_interface__,
        locations=gdf_map.index,
        color="crime_rate",
        hover_name="department_name",
        hover_data={"crime_count": True, "population": True},
        color_continuous_scale="Reds",
        mapbox_style="carto-positron",
        zoom=4,
        center={"lat": 46.5, "lon": 2.5}
    )

    st.plotly_chart(fig_map, use_container_width=True)

    # -----------------------------
    # Top departments table
    # -----------------------------
    st.markdown("<div class='section-header'>Top départements</div>", unsafe_allow_html=True)
    top_departments = filtered_df.groupby("department_name")["crime_rate"].mean().nlargest(top_n).reset_index()
    st.dataframe(top_departments, use_container_width=True)

    # -----------------------------
    # AI
    # -----------------------------
    st.markdown("<div class='section-header'>🤖 Analyse IA</div>", unsafe_allow_html=True)
    with st.expander("Afficher l'analyse IA"):
        st.markdown(ai_analysis(filtered_df))

    st.markdown("<div class='section-header'>💬 Question IA</div>", unsafe_allow_html=True)
    q = st.text_input("Posez votre question")
    if q:
        st.text_area("Réponse", ai_analysis(filtered_df, user_prompt=q), height=180)
