import os
import pandas as pd
import sqlalchemy
from dotenv import load_dotenv
load_dotenv()

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS = os.path.join(BASE, "reports")

# Force CSV mode — only use MySQL if explicitly configured
DB_HOST = os.getenv("DB_HOST", "")
USE_CSV = DB_HOST == "" or DB_HOST == "localhost"

engine = None
if not USE_CSV:
    try:
        engine = sqlalchemy.create_engine(
            f"mysql+pymysql://{os.getenv('DB_USER','root')}:{os.getenv('DB_PASSWORD','')}@{DB_HOST}:{os.getenv('DB_PORT','3306')}/{os.getenv('DB_NAME','patent_db')}?charset=utf8mb4"
        )
    except Exception:
        USE_CSV = True

def run_query(sql):
    if USE_CSV or engine is None:
        raise RuntimeError("Database not available — use CSV mode")
    with engine.connect() as conn:
        return pd.read_sql(sqlalchemy.text(sql), conn)

def q1_top_inventors(limit=20):
    if USE_CSV:
        return pd.read_csv(f"{REPORTS}/top_inventors.csv").head(limit)
    sql = f"""
        SELECT i.inventor_id, i.full_name, i.country,
               COUNT(pi.patent_id) AS patent_count
        FROM patent_inventors pi
        JOIN inventors i ON i.inventor_id = pi.inventor_id
        GROUP BY i.inventor_id, i.full_name, i.country
        ORDER BY patent_count DESC LIMIT {limit}"""
    return run_query(sql)

def q2_top_companies(limit=20):
    if USE_CSV:
        return pd.read_csv(f"{REPORTS}/top_companies.csv").head(limit)
    sql = f"""
        SELECT c.company_id, c.name, c.country,
               COUNT(pc.patent_id) AS patent_count
        FROM patent_companies pc
        JOIN companies c ON c.company_id = pc.company_id
        GROUP BY c.company_id, c.name, c.country
        ORDER BY patent_count DESC LIMIT {limit}"""
    return run_query(sql)

def q3_top_countries(limit=20):
    if USE_CSV:
        return pd.read_csv(f"{REPORTS}/country_trends.csv").head(limit)
    sql = f"""
        SELECT i.country,
               COUNT(DISTINCT pi.patent_id) AS patent_count,
               ROUND(COUNT(DISTINCT pi.patent_id)*100.0/
               (SELECT COUNT(*) FROM patents),2) AS share_pct
        FROM inventors i
        JOIN patent_inventors pi ON i.inventor_id = pi.inventor_id
        WHERE i.country IS NOT NULL AND i.country != ''
        GROUP BY i.country
        ORDER BY patent_count DESC LIMIT {limit}"""
    return run_query(sql)

def q4_trends_over_time():
    if USE_CSV:
        return pd.read_csv(f"{REPORTS}/patent_trends.csv")
    sql = """
        SELECT year, COUNT(*) AS patent_count,
               COUNT(DISTINCT patent_type) AS patent_types
        FROM patents WHERE year BETWEEN 2000 AND 2025
        GROUP BY year ORDER BY year ASC"""
    return run_query(sql)

def q5_patents_with_inventors_companies(limit=20):
    sql = f"""
        SELECT p.patent_id, p.title, p.year,
               i.full_name AS inventor_name, i.country AS inventor_country,
               c.name AS company_name, c.country AS company_country
        FROM patents p
        LEFT JOIN patent_inventors pi ON p.patent_id = pi.patent_id AND pi.inventor_sequence=0
        LEFT JOIN inventors i ON pi.inventor_id = i.inventor_id
        LEFT JOIN patent_companies pc ON p.patent_id = pc.patent_id AND pc.assignee_sequence=0
        LEFT JOIN companies c ON pc.company_id = c.company_id
        LIMIT {limit}"""
    if USE_CSV:
        return pd.DataFrame({"patent_id":["N/A"],"title":["Run locally to see JOIN results"],
                            "year":[2024],"inventor_name":["N/A"],"inventor_country":["N/A"],
                            "company_name":["N/A"],"company_country":["N/A"]})
    return run_query(sql)

def q6_cte_tech_sectors():
    if USE_CSV:
        return pd.read_csv(f"{REPORTS}/tech_sectors.csv")
    sql = """
        WITH sector_counts AS (
            SELECT wipo_sector, COUNT(*) AS patent_count
            FROM patent_classifications WHERE wipo_sector IS NOT NULL
            GROUP BY wipo_sector),
        ranked_sectors AS (
            SELECT wipo_sector, patent_count,
                   RANK() OVER (ORDER BY patent_count DESC) AS sector_rank
            FROM sector_counts)
        SELECT * FROM ranked_sectors ORDER BY sector_rank"""
    return run_query(sql)

def q7_ranked_inventors():
    if USE_CSV:
        try:
            return pd.read_csv(f"{REPORTS}/top_inventors.csv").assign(
                global_rank=lambda x: x["patent_count"].rank(ascending=False).astype(int),
                dense_rank_position=lambda x: x["patent_count"].rank(method="dense", ascending=False).astype(int),
                country_rank=lambda x: x.groupby("country")["patent_count"].rank(ascending=False).astype(int)
            )
        except:
            return pd.read_csv(f"{REPORTS}/top_inventors.csv")
    sql = """
        WITH inventor_patents AS (
            SELECT pi.inventor_id, COUNT(pi.patent_id) AS patent_count
            FROM patent_inventors pi GROUP BY pi.inventor_id)
        SELECT i.full_name, i.country, ip.patent_count,
               RANK() OVER (ORDER BY ip.patent_count DESC) AS global_rank,
               DENSE_RANK() OVER (ORDER BY ip.patent_count DESC) AS dense_rank_position,
               RANK() OVER (PARTITION BY i.country ORDER BY ip.patent_count DESC) AS country_rank
        FROM inventor_patents ip
        JOIN inventors i ON i.inventor_id = ip.inventor_id
        WHERE ip.patent_count > 5
        ORDER BY global_rank LIMIT 50"""
    return run_query(sql)