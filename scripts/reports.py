import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import json
import os
from queries import (
    q1_top_inventors,
    q2_top_companies,
    q3_top_countries,
    q4_trends_over_time,
    q6_cte_tech_sectors
)

# ============================================
# PATHS
# ============================================
REPORTS = "reports"
os.makedirs(REPORTS, exist_ok=True)

# style
sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)
plt.rcParams["font.size"] = 11

# ============================================
# FETCH ALL DATA
# ============================================
print("Fetching data from database...")
inventors   = q1_top_inventors(20)
companies   = q2_top_companies(20)
countries   = q3_top_countries(20)
trends      = q4_trends_over_time()
sectors     = q6_cte_tech_sectors()
print("Done.\n")

# ============================================
# A. CONSOLE REPORT
# ============================================
def console_report():
    total = trends["patent_count"].sum()

    print("\n" + "=" * 55)
    print("       GLOBAL PATENT INTELLIGENCE REPORT")
    print("       Geography of Innovation: 2000-2025")
    print("=" * 55)

    print(f"\n{'Total Patents Analyzed:':<30} {total:>12,}")
    print(f"{'Time Period:':<30} {'2000 - 2025':>12}")
    print(f"{'Total Inventors:':<30} {'3,433,752':>12}")
    print(f"{'Total Companies:':<30} {'389,214':>12}")

    print("\n--- TOP 10 INVENTORS ---")
    for i, row in inventors.head(10).iterrows():
        print(f"  {i+1:>2}. {row['full_name']:<35} {row['patent_count']:>6,} patents  [{row['country']}]")

    print("\n--- TOP 10 COMPANIES ---")
    for i, row in companies.head(10).iterrows():
        
        print(f"  {i+1:>2}. {row['name']:<45} {row['patent_count']:>7,} patents")

    print("\n--- TOP 10 COUNTRIES ---")
    for i, row in countries.head(10).iterrows():
        print(f"  {i+1:>2}. {row['country']:<10} {row['patent_count']:>8,} patents  ({row['share_pct']}%)")

    print("\n--- TECHNOLOGY SECTORS ---")
    for i, row in sectors.iterrows():
        print(f"  {row['sector_rank']:>2}. {row['wipo_sector']:<30} {row['patent_count']:>8,} patents")

    print("\n--- PATENT TRENDS (5-year summary) ---")
    for _, row in trends[trends["year"] % 5 == 0].iterrows():
        print(f"  {row['year']}: {row['patent_count']:>8,} patents")

    print("\n" + "=" * 55)
    print("  Reports saved to: reports/")
    print("=" * 55 + "\n")

# ============================================
# B. CSV EXPORTS
# ============================================
def export_csvs():
    inventors.to_csv(f"{REPORTS}/top_inventors.csv", index=False)
    print("  Saved top_inventors.csv")

    companies.to_csv(f"{REPORTS}/top_companies.csv", index=False)
    print("  Saved top_companies.csv")

    countries.to_csv(f"{REPORTS}/country_trends.csv", index=False)
    print("  Saved country_trends.csv")

    trends.to_csv(f"{REPORTS}/patent_trends.csv", index=False)
    print("  Saved patent_trends.csv")

    sectors.to_csv(f"{REPORTS}/tech_sectors.csv", index=False)
    print("  Saved tech_sectors.csv")

# ============================================
# C. JSON REPORT
# ============================================
def export_json():
    report = {
        "title": "Global Patent Intelligence Report",
        "period": "2000-2025",
        "total_patents": int(trends["patent_count"].sum()),
        "total_inventors": 3433752,
        "total_companies": 389214,
        "top_inventors": [
            {
                "rank": i + 1,
                "name": row["full_name"],
                "country": row["country"],
                "patents": int(row["patent_count"])
            }
            for i, row in inventors.head(10).iterrows()
        ],
        "top_companies": [
            {
                "rank": i + 1,
                "name": row["name"],
                "country": str(row["country"]),
                "patents": int(row["patent_count"])
            }
            for i, row in companies.head(10).iterrows()
        ],
        "top_countries": [
            {
                "country": row["country"],
                "patents": int(row["patent_count"]),
                "share_pct": float(row["share_pct"])
            }
            for _, row in countries.head(10).iterrows()
        ],
        "technology_sectors": [
            {
                "sector": row["wipo_sector"],
                "patents": int(row["patent_count"]),
                "rank": int(row["sector_rank"])
            }
            for _, row in sectors.iterrows()
        ],
        "yearly_trends": [
            {
                "year": int(row["year"]),
                "patents": int(row["patent_count"])
            }
            for _, row in trends.iterrows()
        ]
    }

    with open(f"{REPORTS}/report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("  Saved report.json")

# ============================================
# D. VISUALIZATIONS
# ============================================
def export_visualizations():

    # 1. Top 10 Inventors bar chart
    fig, ax = plt.subplots(figsize=(12, 7))
    data = inventors.head(10).sort_values("patent_count")
    colors = sns.color_palette("Blues_d", len(data))
    bars = ax.barh(data["full_name"], data["patent_count"], color=colors)
    ax.bar_label(bars, fmt="%,.0f", padding=5)
    ax.set_xlabel("Number of Patents")
    ax.set_title("Top 10 Patent Inventors (2000-2025)", fontsize=14, fontweight="bold")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    plt.tight_layout()
    plt.savefig(f"{REPORTS}/top_inventors.png", dpi=150)
    plt.close()
    print("  Saved top_inventors.png")

    # 2. Top 10 Companies bar chart
    fig, ax = plt.subplots(figsize=(13, 7))
    data = companies.head(10).sort_values("patent_count")
    colors = sns.color_palette("Oranges_d", len(data))
    bars = ax.barh(data["name"], data["patent_count"], color=colors)
    ax.bar_label(bars, fmt="%,.0f", padding=5)
    ax.set_xlabel("Number of Patents")
    ax.set_title("Top 10 Patent-Owning Companies (2000-2025)", fontsize=14, fontweight="bold")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    plt.tight_layout()
    plt.savefig(f"{REPORTS}/top_companies.png", dpi=150)
    plt.close()
    print("  Saved top_companies.png")

    # 3. Top Countries pie chart
    fig, ax = plt.subplots(figsize=(10, 8))
    top5 = countries.head(5).copy()
    other = pd.DataFrame([{
        "country": "Others",
        "patent_count": countries.iloc[5:]["patent_count"].sum()
    }])
    data = pd.concat([top5[["country", "patent_count"]], other], ignore_index=True)
    colors = sns.color_palette("Set2", len(data))
    wedges, texts, autotexts = ax.pie(
        data["patent_count"],
        labels=data["country"],
        autopct="%1.1f%%",
        colors=colors,
        startangle=140,
        pctdistance=0.85
    )
    ax.set_title("Patent Share by Country (2000-2025)", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(f"{REPORTS}/country_share.png", dpi=150)
    plt.close()
    print("  Saved country_share.png")

    # 4. Patent trends line chart
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.plot(trends["year"], trends["patent_count"],
            color="#2196F3", linewidth=2.5, marker="o", markersize=4)
    ax.fill_between(trends["year"], trends["patent_count"],
                    alpha=0.15, color="#2196F3")
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of Patents")
    ax.set_title("Global Patent Activity Trends (2000-2025)", fontsize=14, fontweight="bold")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{REPORTS}/patent_trends.png", dpi=150)
    plt.close()
    print("  Saved patent_trends.png")

    # 5. Technology sectors bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = sns.color_palette("viridis", len(sectors))
    bars = ax.bar(sectors["wipo_sector"], sectors["patent_count"],
                  color=colors, edgecolor="white", linewidth=0.5)
    ax.bar_label(bars, fmt="%,.0f", padding=5)
    ax.set_xlabel("Technology Sector")
    ax.set_ylabel("Number of Patents")
    ax.set_title("Patents by WIPO Technology Sector (2000-2025)",
                 fontsize=14, fontweight="bold")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()
    plt.savefig(f"{REPORTS}/tech_sectors.png", dpi=150)
    plt.close()
    print("  Saved tech_sectors.png")

    # 6. Decade comparison bar chart (BONUS - shift analysis)
    fig, ax = plt.subplots(figsize=(10, 6))
    trends["decade"] = (trends["year"] // 10) * 10
    decade_data = trends.groupby("decade")["patent_count"].sum().reset_index()
    decade_data["decade_label"] = decade_data["decade"].astype(str) + "s"
    colors = sns.color_palette("coolwarm", len(decade_data))
    bars = ax.bar(decade_data["decade_label"], decade_data["patent_count"],
                  color=colors, edgecolor="white")
    ax.bar_label(bars, fmt="%,.0f", padding=5)
    ax.set_xlabel("Decade")
    ax.set_ylabel("Total Patents")
    ax.set_title("Patent Activity by Decade (2000-2025)",
                 fontsize=14, fontweight="bold")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    plt.tight_layout()
    plt.savefig(f"{REPORTS}/decade_comparison.png", dpi=150)
    plt.close()
    print("  Saved decade_comparison.png")

# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    console_report()

    print("\nExporting CSV files...")
    export_csvs()

    print("\nExporting JSON report...")
    export_json()

    print("\nGenerating visualizations...")
    export_visualizations()

    print("\n✓ All reports generated successfully!")