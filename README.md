#  Global Patent Intelligence Pipeline

> **"The Geography of Innovation: How patent leadership has shifted across countries, companies, and technology sectors from 2000–2025"**

A full ETL data pipeline built on real USPTO patent data, analyzing 7.2 million patents across 25 years.

---

## Project Structure
patent-intelligence-pipeline/
├── data/
│   ├── raw/          ← USPTO PatentsView zip files
│   └── clean/        ← Cleaned CSV files
├── scripts/
│   ├── ingest.py     ← Extract & Transform (ETL)
│   ├── load_db.py    ← Load into MySQL
│   ├── queries.py    ← SQL analytical queries
│   └── reports.py    ← CSV, JSON & visualizations
├── sql/
│   └── schema.sql    ← Database schema
├── dashboard/
│   └── app.py        ← Streamlit dashboard
├── reports/          ← Generated reports & charts
└── README.md
---

##  Engineering Considerations

### Large-Scale Data Handling

Due to the size of the dataset (tens of millions of rows across tables), data processing was optimized using:

- **Chunked loading** in Python (pandas) to avoid memory overflow
- Incremental inserts into MySQL instead of single bulk loads
- Efficient indexing during database loading

This approach prevented system crashes and ensured stable execution on a local machine with limited resources.
## Data Source

**USPTO PatentsView Granted Patent Disambiguated Data**
- URL: https://data.uspto.gov/bulkdata/datasets/pvgpatdis
- Files used: `g_patent`, `g_patent_abstract`, `g_application`, `g_inventor_disambiguated`, `g_assignee_disambiguated`, `g_location_disambiguated`, `g_cpc_current`, `g_wipo_technology`

---

## Database Schema

6 tables in MySQL:

| Table | Records |
|---|---|
| patents | 7,194,096 |
| inventors | 3,433,752 |
| companies | 389,214 |
| patent_inventors | 19,577,655 |
| patent_companies | 6,806,806 |
| patent_classifications | 6,445,731 |

---

## ⚙️Setup & Installation

### 1. Clone the repo
```bash
git clone https://github.com/AnkundaNoela/patent-intelligence-pipeline.git
cd patent-intelligence-pipeline
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
Create a `.env` file:
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=patent_db
### 4. Create the database
```bash
mysql -u root -p < sql/schema.sql
```

### 5. Download raw data
Download these 8 files from USPTO PatentsView into `data/raw/`:
- g_patent.tsv.zip
- g_patent_abstract.tsv.zip
- g_application.tsv.zip
- g_inventor_disambiguated.tsv.zip
- g_assignee_disambiguated.tsv.zip
- g_location_disambiguated.tsv.zip
- g_cpc_current.tsv.zip
- g_wipo_technology.tsv.zip

---

##  Running the Pipeline

```bash
# Step 1 - Extract & Transform
python scripts/ingest.py

# Step 2 - Load into MySQL
python scripts/load_db.py

# Step 3 - Run SQL queries
python scripts/queries.py

# Step 4 - Generate reports
python scripts/reports.py

# Step 5 - Launch dashboard
streamlit run dashboard/app.py
```

---

##  SQL Queries

| Query | Description |
|---|---|
| Q1 | Top inventors by patent count |
| Q2 | Top companies by patent count |
| Q3 | Top countries by patent share |
| Q4 | Patent trends over time (2000-2025) |
| Q5 | JOIN — patents with inventors & companies |
| Q6 | CTE — technology sector analysis |
| Q7 | Window functions — inventor rankings |

---

## Key Findings

- **7,194,096** patents analyzed (2000–2025)
- **USA dominates** with 52.97% of all patents
- **Samsung Display** leads with 168,757 patents
- **Shunpei Yamazaki** is top inventor with 6,178 patents
- **Electrical engineering** is the largest tech sector
- Patents grew from **176,192** in 2000 to **378,741** in 2025

---
##  Deployment Notes

### Local Deployment
The Streamlit dashboard is currently deployed and tested on **localhost**, ensuring:
- Fast query execution
- Full control over the database
- No cloud-related latency or cost constraints

### Cloud Deployment Considerations

Deploying this pipeline to free-tier cloud databases (e.g., PlanetScale, Firebase, etc.) presents challenges:

- The dataset exceeds **tens of millions of rows**
- Free tiers typically impose:
  - Storage limits
  - Query performance restrictions
  - Connection limits

As a result, uploading and querying this dataset in such environments would be **slow and impractical**.


## Tech Stack

- **Python** — pandas, sqlalchemy, matplotlib, seaborn
- **MySQL** — relational database via WAMP
- **Streamlit** — interactive dashboard
- **GitHub** — version control

---
##   Key considerations
#  Data Validation

- Verified dataset integrity against USPTO totals
- Confirmed full dataset size (~9.4M patents)
- Ensured consistency after filtering (2000–2025 subset)
##  Author

Ankunda Noela 23/U/06264/PS
