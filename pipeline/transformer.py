import pandas as pd
import requests
from pipeline.config import OPENROUTER_API_KEY, OPENROUTER_URL, MODEL

def transform_population(df):
    df = df.dropna(how="all").reset_index(drop=True)
    
    # Find the first row with department codes
    for i, row in df.iterrows():
        if str(row[0]).isdigit():
            df_data = df.iloc[i:].copy()
            break
    else:
        raise ValueError("No department data found")
    
    df_data = df_data.reset_index(drop=True)
    df_data = df_data.iloc[:, [0, 1, -1]]
    
    # Rename to standard 'population' column
    df_data.columns = ["code_insee", "nom", "population"]
    df_data["code_insee"] = df_data["code_insee"].astype(str).str.zfill(2)
    df_data["population"] = pd.to_numeric(df_data["population"], errors="coerce")
    df_data = df_data.dropna(subset=["population"])
    
    return df_data

def transform_crimes(df, year):
    df = df.iloc[2:].reset_index(drop=True)
    df = df.drop(columns=df.columns[:2])
    sums = df.sum(axis=0)
    records = []
    for col, val in sums.items():
        dept = col.split(".")[0]
        if dept.isdigit() or dept in ["2A", "2B"]:
            records.append({
                "code_insee": dept.zfill(2) if dept.isdigit() else dept,
                "year": year,
                "crime_count": int(val)
            })
    return pd.DataFrame(records).groupby(["code_insee", "year"], as_index=False).sum()

def ai_analysis(df, user_prompt=None):
    summary = df[["name", "crime_count", "population"]].dropna().to_string(index=False)
    if user_prompt:
        prompt = f"{summary}\n\nQuestion de l'utilisateur : {user_prompt}"
    else:
        prompt = f"Analyse les données suivantes et produis un rapport synthétique.\n{summary}"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }
    r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
    return r.json()["choices"][0]["message"]["content"]
