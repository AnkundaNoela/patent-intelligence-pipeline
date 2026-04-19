import pandas as pd
import zipfile
import os

# ============================================
# PATHS
# ============================================
RAW = "data/raw"
CLEAN = "data/clean"
os.makedirs(CLEAN, exist_ok=True)

# ============================================
# HELPER: read tsv from zip in chunks
# ============================================
def read_zip_chunked(filename, usecols=None, dtype=str, chunksize=500_000,
                     filter_ids=None, filter_col=None):
    path = os.path.join(RAW, filename)
    print(f"  Reading {filename} in chunks...")
    chunks = []
    with zipfile.ZipFile(path) as z:
        tsv_name = z.namelist()[0]
        with z.open(tsv_name) as f:
            for chunk in pd.read_csv(
                f,
                sep="\t",
                usecols=usecols,
                dtype=dtype,
                on_bad_lines="skip",
                chunksize=chunksize
            ):
                if filter_ids is not None and filter_col is not None:
                    chunk = chunk[chunk[filter_col].isin(filter_ids)]
                chunks.append(chunk)
    df = pd.concat(chunks, ignore_index=True)
    print(f"  Loaded {len(df):,} rows")
    return df

# ============================================
# 1. PATENTS
# ============================================
def clean_patents():
    print("\n[1/6] Cleaning patents...")

    # core patent info
    patents = read_zip_chunked("g_patent.tsv.zip", usecols=[
        "patent_id", "patent_type", "patent_date",
        "patent_title", "num_claims", "withdrawn"
    ])
    patents.rename(columns={
        "patent_date": "grant_date",
        "patent_title": "title"
    }, inplace=True)

    patent_id_set = set(patents["patent_id"])

    # abstracts
    abstracts = read_zip_chunked(
        "g_patent_abstract.tsv.zip",
        usecols=["patent_id", "patent_abstract"],
        filter_ids=patent_id_set,
        filter_col="patent_id"
    )
    abstracts.rename(columns={"patent_abstract": "abstract"}, inplace=True)

    # filing dates
    applications = read_zip_chunked(
        "g_application.tsv.zip",
        usecols=["patent_id", "filing_date"],
        filter_ids=patent_id_set,
        filter_col="patent_id"
    )

    # merge all three
    df = patents.merge(abstracts, on="patent_id", how="left")
    df = df.merge(applications, on="patent_id", how="left")

    # clean dates
    df["grant_date"] = pd.to_datetime(df["grant_date"], errors="coerce")
    df["filing_date"] = pd.to_datetime(df["filing_date"], errors="coerce")
    df["year"] = df["grant_date"].dt.year

    # filter 2000-2025
    df = df[df["year"].between(2000, 2025)]

    # drop duplicates and nulls
    df.drop_duplicates(subset="patent_id", inplace=True)
    df.dropna(subset=["patent_id", "title"], inplace=True)

    # reorder columns
    df = df[[
        "patent_id", "title", "abstract", "filing_date",
        "grant_date", "year", "patent_type", "num_claims", "withdrawn"
    ]]

    df.to_csv(f"{CLEAN}/clean_patents.csv", index=False)
    print(f"  Saved {len(df):,} patents to clean_patents.csv")
    return set(df["patent_id"].tolist())

# ============================================
# 2. LOCATIONS
# ============================================
def clean_locations():
    print("\n[2/6] Cleaning locations...")
    df = read_zip_chunked("g_location_disambiguated.tsv.zip", usecols=[
        "location_id", "disambig_city", "disambig_state",
        "disambig_country", "latitude", "longitude"
    ])
    df.rename(columns={
        "disambig_city": "city",
        "disambig_state": "state",
        "disambig_country": "country"
    }, inplace=True)
    df.drop_duplicates(subset="location_id", inplace=True)
    print(f"  Loaded {len(df):,} locations")
    return df

# ============================================
# 3. INVENTORS
# ============================================
def clean_inventors(patent_ids, locations):
    print("\n[3/6] Cleaning inventors...")
    df = read_zip_chunked(
        "g_inventor_disambiguated.tsv.zip",
        usecols=[
            "patent_id", "inventor_id", "disambig_inventor_name_first",
            "disambig_inventor_name_last", "location_id", "inventor_sequence"
        ],
        filter_ids=patent_ids,
        filter_col="patent_id"
    )
    df.rename(columns={
        "disambig_inventor_name_first": "first_name",
        "disambig_inventor_name_last": "last_name"
    }, inplace=True)

    # join location info
    df = df.merge(locations, on="location_id", how="left")

    # full name
    df["full_name"] = (
        df["first_name"].fillna("") + " " + df["last_name"].fillna("")
    ).str.strip()

    # relationship table
    patent_inventors = df[["patent_id", "inventor_id", "inventor_sequence"]].copy()
    patent_inventors.drop_duplicates(inplace=True)

    # inventors table (unique inventors only)
    inventors = df[[
        "inventor_id", "first_name", "last_name",
        "full_name", "country", "city", "state",
        "latitude", "longitude"
    ]].drop_duplicates(subset="inventor_id")

    inventors.to_csv(f"{CLEAN}/clean_inventors.csv", index=False)
    patent_inventors.to_csv(f"{CLEAN}/clean_patent_inventors.csv", index=False)
    print(f"  Saved {len(inventors):,} inventors")
    print(f"  Saved {len(patent_inventors):,} patent-inventor relationships")

# ============================================
# 4. COMPANIES (assignees)
# ============================================
def clean_companies(patent_ids, locations):
    print("\n[4/6] Cleaning companies...")
    df = read_zip_chunked(
        "g_assignee_disambiguated.tsv.zip",
        usecols=[
            "patent_id", "assignee_id", "disambig_assignee_organization",
            "assignee_type", "location_id", "assignee_sequence"
        ],
        filter_ids=patent_ids,
        filter_col="patent_id"
    )
    df.rename(columns={
        "assignee_id": "company_id",
        "disambig_assignee_organization": "name"
    }, inplace=True)

    # drop rows with no company name
    df.dropna(subset=["name"], inplace=True)

    # join location
    df = df.merge(locations, on="location_id", how="left")

    # relationship table
    patent_companies = df[["patent_id", "company_id", "assignee_sequence"]].copy()
    patent_companies.drop_duplicates(inplace=True)

    # companies table
    companies = df[[
        "company_id", "name", "assignee_type", "country", "city"
    ]].drop_duplicates(subset="company_id")

    companies.to_csv(f"{CLEAN}/clean_companies.csv", index=False)
    patent_companies.to_csv(f"{CLEAN}/clean_patent_companies.csv", index=False)
    print(f"  Saved {len(companies):,} companies")
    print(f"  Saved {len(patent_companies):,} patent-company relationships")

# ============================================
# 5. CLASSIFICATIONS
# ============================================
def clean_classifications(patent_ids):
    print("\n[5/6] Cleaning CPC classifications...")
    
    # force all patent_ids to string for consistent matching
    patent_id_set = set(str(pid) for pid in patent_ids)
    print(f"  Matching against {len(patent_id_set):,} patent IDs")
    
    path = os.path.join(RAW, "g_cpc_current.tsv.zip")
    chunks = []
    with zipfile.ZipFile(path) as z:
        tsv_name = z.namelist()[0]
        with z.open(tsv_name) as f:
            for chunk in pd.read_csv(
                f, sep="\t",
                usecols=["patent_id", "cpc_section", "cpc_class",
                         "cpc_subclass", "cpc_group", "cpc_type"],
                dtype={"patent_id": str},
                low_memory=False, on_bad_lines="skip",
                chunksize=1000000
            ):
                chunk["patent_id"] = chunk["patent_id"].astype(str).str.strip()
                chunk = chunk[chunk["patent_id"].isin(patent_id_set)]
                chunk = chunk[chunk["cpc_type"] == "inventional"]
                chunks.append(chunk)
                print(f"    CPC chunks processed: {len(chunks)}, records so far: {sum(len(c) for c in chunks):,}", end="\r")

    cpc = pd.concat(chunks, ignore_index=True)
    cpc.drop_duplicates(subset=["patent_id"], keep="first", inplace=True)
    print(f"\n  Kept {len(cpc):,} CPC records after filtering")

    print("\n[6/6] Cleaning WIPO technology...")
    wipo_chunks = []
    path = os.path.join(RAW, "g_wipo_technology.tsv.zip")
    with zipfile.ZipFile(path) as z:
        tsv_name = z.namelist()[0]
        with z.open(tsv_name) as f:
            for chunk in pd.read_csv(
                f, sep="\t",
                usecols=["patent_id", "wipo_field_id",
                         "wipo_sector_title", "wipo_field_title"],
                dtype={"patent_id": str},
                low_memory=False, on_bad_lines="skip",
                chunksize=1000000
            ):
                chunk["patent_id"] = chunk["patent_id"].astype(str).str.strip()
                chunk = chunk[chunk["patent_id"].isin(patent_id_set)]
                wipo_chunks.append(chunk)

    wipo = pd.concat(wipo_chunks, ignore_index=True)
    wipo.rename(columns={
        "wipo_sector_title": "wipo_sector",
        "wipo_field_title": "wipo_field"
    }, inplace=True)
    wipo.drop_duplicates(subset="patent_id", inplace=True)
    print(f"  Kept {len(wipo):,} WIPO records")

    df = cpc.merge(wipo, on="patent_id", how="left")
    df.to_csv(f"{CLEAN}/clean_classifications.csv", index=False)
    print(f"  Saved {len(df):,} classification records")

# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    print("=" * 50)
    print("  PATENT DATA INGESTION PIPELINE")
    print("=" * 50)

    patent_ids = clean_patents()
    locations = clean_locations()
    clean_inventors(patent_ids, locations)
    clean_companies(patent_ids, locations)
    clean_classifications(patent_ids)

    print("\n" + "=" * 50)
    print("  INGESTION COMPLETE!")
    print("=" * 50)