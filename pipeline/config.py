# from pathlib import Path

# # =========================
# # PATHS
# # =========================
# BASE_DIR = Path(__file__).resolve().parent.parent

# DATA_DIR = BASE_DIR / "data"
# RAW_DIR = DATA_DIR / "raw"
# PROCESSED_DIR = DATA_DIR / "processed"
# REPORTS_DIR = BASE_DIR / "reports" / "ai_reports"

# # Create folders if they don't exist
# RAW_DIR.mkdir(parents=True, exist_ok=True)
# PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
# REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# # =========================
# # DATA SOURCES (OFFICIAL / SECURE)
# # =========================

# # Crimes & délits (XLSX)
# CRIME_DATA_URL = (
#     "https://www.data.gouv.fr/api/1/datasets/r/d792092f-b1f7-4180-a367-d043200c1520"
# )

# # Population INSEE (XLS)
# POPULATION_DATA_URL = (
#     "https://www.insee.fr/fr/statistiques/fichier/1893198/estim-pop-dep-sexe-gca-1975-2023.xls"
# )

# # Geographic boundaries (OpenStreetMap ZIP)
# DEPARTMENTS_ZIP_URL = (
#     "https://www.data.gouv.fr/api/1/datasets/r/d308e7be-1529-4dfe-b733-2ba2ccdf0d62"
# )

# # =========================
# # FILE NAMES
# # =========================
# CRIME_RAW_FILE = RAW_DIR / "crimes.xlsx"          
# POPULATION_RAW_FILE = RAW_DIR / "population.xls"
# DEPARTMENTS_ZIP_FILE = RAW_DIR / "departments.zip"
# GEO_RAW_FILE = RAW_DIR / "departments.geojson"   # we will convert shapefile to geojson

from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
REPORTS_DIR = BASE_DIR / "reports" / "ai_reports"

CRIMES_FILE = RAW_DIR / "crimes.xlsx"
POPULATION_FILE = RAW_DIR / "population.xls"
GEO_FILE = RAW_DIR / "departments.geojson"

OUTPUT_FILE = PROCESSED_DIR / "safecity.parquet"

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "mistralai/mistral-7b-instruct"
