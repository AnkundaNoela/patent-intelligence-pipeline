import sqlalchemy
from dotenv import load_dotenv
import os
import pandas as pd

# ============================================
# CONNECT TO MYSQL
# ============================================
load_dotenv()

engine = sqlalchemy.create_engine(
    f"mysql+pymysql://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PASSWORD', '')}@{os.getenv('DB_HOST', 'localhost')}/{os.getenv('DB_NAME', 'patent_db')}?charset=utf8mb4"
)

def run_query(sql):
    with engine.connect() as conn:
        return pd.read_sql(sqlalchemy.text(sql), conn)

# ============================================
# Q1: TOP INVENTORS
# Who has the most patents?
# ============================================
def q1_top_inventors(limit=20):
    sql = """
        SELECT 
            i.inventor_id,
            i.full_name,
            i.country,
            COUNT(pi.patent_id) AS patent_count
        FROM inventors i
        JOIN patent_inventors pi ON i.inventor_id = pi.inventor_id
        GROUP BY i.inventor_id, i.full_name, i.country
        ORDER BY patent_count DESC
        LIMIT :limit
    """.replace(":limit", str(limit))
    return run_query(sql)

# ============================================
# Q2: TOP COMPANIES
# Which companies own the most patents?
# ============================================
def q2_top_companies(limit=20):
    sql = """
        SELECT
            c.company_id,
            c.name,
            c.country,
            COUNT(pc.patent_id) AS patent_count
        FROM companies c
        JOIN patent_companies pc ON c.company_id = pc.company_id
        GROUP BY c.company_id, c.name, c.country
        ORDER BY patent_count DESC
        LIMIT :limit
    """.replace(":limit", str(limit))
    return run_query(sql)

# ============================================
# Q3: TOP COUNTRIES
# Which countries produce the most patents?
# ============================================
def q3_top_countries(limit=20):
    sql = """
        SELECT
            i.country,
            COUNT(DISTINCT pi.patent_id) AS patent_count,
            ROUND(COUNT(DISTINCT pi.patent_id) * 100.0 / 
                (SELECT COUNT(*) FROM patents), 2) AS share_pct
        FROM inventors i
        JOIN patent_inventors pi ON i.inventor_id = pi.inventor_id
        WHERE i.country IS NOT NULL AND i.country != ''
        GROUP BY i.country
        ORDER BY patent_count DESC
        LIMIT :limit
    """.replace(":limit", str(limit))
    return run_query(sql)

# ============================================
# Q4: TRENDS OVER TIME
# How many patents per year?
# ============================================
def q4_trends_over_time():
    sql = """
        SELECT
            year,
            COUNT(*) AS patent_count,
            COUNT(DISTINCT patent_type) AS patent_types
        FROM patents
        WHERE year BETWEEN 2000 AND 2025
        GROUP BY year
        ORDER BY year ASC
    """
    return run_query(sql)

# ============================================
# Q5: JOIN QUERY
# Combine patents with inventors and companies
# ============================================
def q5_patents_with_inventors_companies(limit=20):
    sql = """
        SELECT
            p.patent_id,
            p.title,
            p.year,
            i.full_name AS inventor_name,
            i.country AS inventor_country,
            c.name AS company_name,
            c.country AS company_country
        FROM patents p
        LEFT JOIN patent_inventors pi ON p.patent_id = pi.patent_id
        LEFT JOIN inventors i ON pi.inventor_id = i.inventor_id
        LEFT JOIN patent_companies pc ON p.patent_id = pc.patent_id
        LEFT JOIN companies c ON pc.company_id = c.company_id
        WHERE pi.inventor_sequence = 0
        AND pc.assignee_sequence = 0
        LIMIT :limit
    """.replace(":limit", str(limit))
    return run_query(sql)

# ============================================
# Q6: CTE QUERY
# Top technology sectors by patent count
# ============================================
def q6_cte_tech_sectors():
    sql = """
        WITH sector_counts AS (
            SELECT
                pc.wipo_sector,
                COUNT(*) AS patent_count
            FROM patent_classifications pc
            WHERE pc.wipo_sector IS NOT NULL
            GROUP BY pc.wipo_sector
        ),
        ranked_sectors AS (
            SELECT
                wipo_sector,
                patent_count,
                RANK() OVER (ORDER BY patent_count DESC) AS sector_rank
            FROM sector_counts
        )
        SELECT *
        FROM ranked_sectors
        ORDER BY sector_rank
    """
    return run_query(sql)

# ============================================
# Q7: RANKING QUERY
# Rank inventors using window functions
# ============================================
def q7_ranked_inventors():
    sql = """
        WITH inventor_patents AS (
            SELECT
                i.inventor_id,
                i.full_name,
                i.country,
                COUNT(pi.patent_id) AS patent_count
            FROM inventors i
            JOIN patent_inventors pi ON i.inventor_id = pi.inventor_id
            GROUP BY i.inventor_id, i.full_name, i.country
        )
        SELECT
            full_name,
            country,
            patent_count,
            RANK() OVER (ORDER BY patent_count DESC) AS global_rank,
            DENSE_RANK() OVER (ORDER BY patent_count DESC) AS dense_rank_position,
            RANK() OVER (PARTITION BY country ORDER BY patent_count DESC) AS country_rank
        FROM inventor_patents
        WHERE patent_count > 5
        ORDER BY global_rank
        LIMIT 50
    """
    return run_query(sql)

# ============================================
# MAIN - run and preview all queries
# ============================================
if __name__ == "__main__":
    print("=" * 60)
    print("  RUNNING ALL PATENT QUERIES")
    print("=" * 60)

    print("\nQ1: Top Inventors")
    print(q1_top_inventors(10).to_string(index=False))

    print("\nQ2: Top Companies")
    print(q2_top_companies(10).to_string(index=False))

    print("\nQ3: Top Countries")
    print(q3_top_countries(10).to_string(index=False))

    print("\nQ4: Trends Over Time")
    print(q4_trends_over_time().to_string(index=False))

    print("\nQ5: Patents with Inventors & Companies")
    print(q5_patents_with_inventors_companies(5).to_string(index=False))

    print("\nQ6: CTE - Tech Sectors")
    print(q6_cte_tech_sectors().to_string(index=False))

    print("\nQ7: Ranked Inventors")
    print(q7_ranked_inventors().to_string(index=False))

    print("\n" + "=" * 60)
    print("  ALL QUERIES COMPLETE")
    print("=" * 60)