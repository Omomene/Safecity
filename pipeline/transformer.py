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
    """
    Returns AI analysis text for the given dataframe or a user question.
    Works safely with OpenRouter/Mistral response format.
    """
    # Build prompt
    if user_prompt is None:
        prompt = (
            "Fais un rapport synthétique sur les données de criminalité suivantes :\n\n"
            f"{df[['name','crime_count','population']].to_string(index=False)}"
        )
    else:
        prompt = user_prompt

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 500
    }

    try:
        resp = requests.post(OPENROUTER_URL, headers=headers, json=payload)
        resp_json = resp.json()

        # OpenRouter sometimes returns 'choices' as a list of dicts
        choices = resp_json.get("choices", [])
        if not choices:
            return "L'IA n'a pas renvoyé de réponse. Essayez de poser une question plus détaillée."

        choice = choices[0]

        # Some versions: choice has 'message' -> 'content'
        if "message" in choice and "content" in choice["message"]:
            return choice["message"]["content"].strip()
        # Some versions: choice has 'text' directly
        elif "text" in choice:
            return choice["text"].strip()
        # Otherwise
        return "L'IA n'a pas renvoyé de réponse. Essayez de poser une question plus détaillée."

    except Exception as e:
        return f"L'IA n'a pas pu générer de réponse: {e}"
