import os
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS = os.path.join(BASE, "reports")

def q1_top_inventors(limit=20):
    return pd.read_csv(os.path.join(REPORTS, "top_inventors.csv")).head(limit)

def q2_top_companies(limit=20):
    return pd.read_csv(os.path.join(REPORTS, "top_companies.csv")).head(limit)

def q3_top_countries(limit=20):
    return pd.read_csv(os.path.join(REPORTS, "country_trends.csv")).head(limit)

def q4_trends_over_time():
    return pd.read_csv(os.path.join(REPORTS, "patent_trends.csv"))

def q5_patents_with_inventors_companies(limit=20):
    return pd.DataFrame({
        "patent_id":        ["See local dashboard"],
        "title":            ["Run locally for full JOIN results"],
        "year":             [2024],
        "inventor_name":    ["N/A"],
        "inventor_country": ["N/A"],
        "company_name":     ["N/A"],
        "company_country":  ["N/A"]
    })

def q6_cte_tech_sectors():
    return pd.read_csv(os.path.join(REPORTS, "tech_sectors.csv"))

def q7_ranked_inventors():
    df = pd.read_csv(os.path.join(REPORTS, "top_inventors.csv"))
    df["global_rank"] = df["patent_count"].rank(ascending=False, method="min").astype(int)
    df["dense_rank_position"] = df["patent_count"].rank(ascending=False, method="dense").astype(int)
    df["country_rank"] = df.groupby("country")["patent_count"].rank(ascending=False, method="min").astype(int)
    return df