import pandas as pd
import sqlalchemy
from dotenv import load_dotenv
import os

# ============================================
# CONNECT TO MYSQL
# ============================================
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "patent_db")

engine = sqlalchemy.create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?charset=utf8mb4"
)

CLEAN = "data/clean"

# ============================================
# HELPER: load csv into mysql table
# ============================================
def load_table(filename, table_name, chunksize=50000):
    path = os.path.join(CLEAN, filename)
    print(f"\n  Loading {filename} → {table_name}...")
    total = 0
    for chunk in pd.read_csv(path, chunksize=chunksize, low_memory=False):
        chunk.drop_duplicates(inplace=True)
        try:
            chunk.to_sql(
                table_name,
                con=engine,
                if_exists="append",
                index=False,
                method="multi"
            )
        except Exception:
            # insert row by row skipping duplicates
            with engine.connect() as conn:
                for _, row in chunk.iterrows():
                    try:
                        row.to_frame().T.to_sql(
                            table_name,
                            con=conn,
                            if_exists="append",
                            index=False
                        )
                    except Exception:
                        pass
        total += len(chunk)
        print(f"    {total:,} rows loaded...", end="\r")
    print(f"  ✓ {total:,} rows loaded into {table_name}")

# ============================================
# MAIN
# ============================================
def table_is_loaded(table_name):
    with engine.connect() as conn:
        result = conn.execute(sqlalchemy.text(f"SELECT COUNT(*) FROM {table_name}"))
        count = result.scalar()
        return count > 0

if __name__ == "__main__":
    print("=" * 50)
    print("  LOADING DATA INTO MYSQL")
    print("=" * 50)

    tables = [
        ("clean_patents.csv",          "patents"),
        ("clean_inventors.csv",        "inventors"),
        ("clean_companies.csv",        "companies"),
        ("clean_patent_inventors.csv", "patent_inventors"),
        ("clean_patent_companies.csv", "patent_companies"),
        ("clean_classifications.csv",  "patent_classifications"),
    ]

    for filename, table_name in tables:
        if table_is_loaded(table_name):
            print(f"\n  ⏭ Skipping {table_name} — already loaded")
        else:
            load_table(filename, table_name)

    print("\n" + "=" * 50)
    print("  DATABASE LOADING COMPLETE!")
    print("=" * 50)