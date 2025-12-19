import pandas as pd
from pipeline.fetcher import load_crimes, load_population, load_geo
from pipeline.transformer import transform_population, transform_crimes, ai_analysis
from pipeline.storage import save_parquet, save_report
from pipeline.config import *

def run():
    # -----------------------------
    # Load and transform crimes for all PN and GN years
    # -----------------------------
    print("Loading and transforming crimes...")
    all_crimes = []
    sheets = [f"Services PN {y}" for y in range(2012, 2022)] + [f"Services GN {y}" for y in range(2012, 2022)]
    for sheet in sheets:
        year = int(sheet.split()[-1])
        crimes_raw = load_crimes(CRIMES_FILE, sheet)
        crimes_year = transform_crimes(crimes_raw, year)
        all_crimes.append(crimes_year)
    crimes = pd.concat(all_crimes, ignore_index=True)
    print("Crimes data ready")

    # -----------------------------
    # Load and transform population
    # -----------------------------
    print("Loading and transforming population...")
    population_raw = load_population(POPULATION_FILE)
    population = transform_population(population_raw)
    print("Population data ready")

    # -----------------------------
    # Load geo data
    # -----------------------------
    print("Loading geo data...")
    geo = load_geo(GEO_FILE)
    geo["code_insee"] = geo["code_insee"].astype(str).str.zfill(2)
    print("Geo data ready")

    # -----------------------------
    # Merge all data
    # -----------------------------
    print("Merging data...")
    df = geo.merge(population, on="code_insee", how="left")
    df = df.merge(crimes, on="code_insee", how="left")
    print(f"Data merged. Shape: {df.shape}")

    if "nom" in df.columns:
        df.rename(columns={"nom": "name"}, inplace=True)
    elif "name" not in df.columns:
        df["name"] = df["code_insee"]

    if "population_total" in df.columns:
        df.rename(columns={"population_total": "population"}, inplace=True)
    elif "population" not in df.columns:
        df["population"] = 0

    df["crime_count"] = df["crime_count"].fillna(0)
    df["population"] = df["population"].fillna(0)

    df["crime_rate"] = df.apply(
        lambda row: row["crime_count"] / row["population"] * 100000 if row["population"] > 0 else 0,
        axis=1
    )

    save_parquet(df, OUTPUT_FILE)
    print(f"Processed data saved to {OUTPUT_FILE}")

    # -----------------------------
    # Generate AI report
    # -----------------------------
    print("Generating AI report...")
    try:
        report = ai_analysis(df)
        save_report(report, REPORTS_DIR / "latest_report.txt")
        print("AI report saved")
    except KeyError as e:
        print(f"AI report generation failed: {e}")

    print("SafeCity pipeline completed")


if __name__ == "__main__":
    run()
