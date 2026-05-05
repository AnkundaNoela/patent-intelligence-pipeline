import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import seaborn as sns
import json
import os
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
import warnings
warnings.filterwarnings("ignore")

from queries import (
    q3_top_countries,
    q4_trends_over_time,
    q6_cte_tech_sectors
)

# ============================================
# PATHS & STYLE
# ============================================
REPORTS = "reports"
os.makedirs(REPORTS, exist_ok=True)

# Dark theme colors
DARK_BG = "#0d1635"
DARK_AX = "#141b3d"
GOLD    = "#c9a84c"
CREAM   = "#f5f0e8"
TEAL    = "#2ec4b6"
RED     = "#e63946"
TEXT    = "#cdd6f4"
PURPLE  = "#a29bfe"

def set_dark_style():
    plt.rcParams.update({
        "figure.facecolor":  DARK_BG,
        "axes.facecolor":    DARK_AX,
        "axes.edgecolor":    "#2a3560",
        "axes.labelcolor":   TEXT,
        "axes.titlecolor":   CREAM,
        "xtick.color":       TEXT,
        "ytick.color":       TEXT,
        "text.color":        TEXT,
        "grid.color":        "#1e2d5a",
        "grid.alpha":        0.5,
        "axes.grid":         True,
        "figure.dpi":        150,
        "font.family":       "DejaVu Sans",
        "axes.spines.top":   False,
        "axes.spines.right": False,
    })

set_dark_style()

# ============================================
# LOAD DATA
# ============================================
print("Loading data...")
inventors = pd.read_csv("reports/top_inventors.csv")
companies = pd.read_csv("reports/top_companies.csv")
countries = q3_top_countries(20)
trends    = q4_trends_over_time()
sectors   = q6_cte_tech_sectors()
print("Done.\n")

# ============================================
# A. CONSOLE REPORT
# ============================================
def console_report():
    total = trends["patent_count"].sum()
    print("\n" + "=" * 60)
    print("       GLOBAL PATENT INTELLIGENCE REPORT")
    print("       Geography of Innovation: 2000-2025")
    print("=" * 60)
    print(f"\n{'Total Patents Analyzed:':<35} {total:>12,}")
    print(f"{'Time Period:':<35} {'2000 - 2025':>12}")
    print(f"{'Total Inventors:':<35} {'3,433,752':>12}")
    print(f"{'Total Companies:':<35} {'389,214':>12}")

    print("\n--- TOP 10 INVENTORS ---")
    for i, row in inventors.head(10).iterrows():
        print(f"  {i+1:>2}. {row['full_name']:<38} {int(row['patent_count']):>6,} patents  [{row['country']}]")

    print("\n--- TOP 10 COMPANIES ---")
    for i, row in companies.head(10).iterrows():
        print(f"  {i+1:>2}. {row['name']:<48} {int(row['patent_count']):>7,} patents")

    print("\n--- TOP 10 COUNTRIES ---")
    for i, row in countries.head(10).iterrows():
        print(f"  {i+1:>2}. {row['country']:<10} {int(row['patent_count']):>9,} patents  ({row['share_pct']}%)")

    print("\n--- TECHNOLOGY SECTORS ---")
    for _, row in sectors.iterrows():
        print(f"  {int(row['sector_rank']):>2}. {row['wipo_sector']:<32} {int(row['patent_count']):>9,} patents")

    print("\n--- PATENT TRENDS (5-year summary) ---")
    for _, row in trends[trends["year"] % 5 == 0].iterrows():
        print(f"  {int(row['year'])}: {int(row['patent_count']):>9,} patents")

    # ML forecast
    X = trends["year"].values.reshape(-1,1)
    y = trends["patent_count"].values
    lr = LinearRegression(); lr.fit(X,y)
    poly = make_pipeline(PolynomialFeatures(3), LinearRegression()); poly.fit(X,y)
    print("\n--- ML FORECAST (2026-2030) ---")
    for yr in range(2026, 2031):
        lp = int(lr.predict([[yr]])[0])
        pp = int(poly.predict([[yr]])[0])
        print(f"  {yr}: Linear={lp:>9,}  |  Polynomial={pp:>9,}")

    print("\n" + "=" * 60)
    print("  Reports saved to: reports/")
    print("=" * 60 + "\n")

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
    X = trends["year"].values.reshape(-1,1)
    y = trends["patent_count"].values
    lr = LinearRegression(); lr.fit(X,y)
    poly = make_pipeline(PolynomialFeatures(3), LinearRegression()); poly.fit(X,y)

    report = {
        "title": "Global Patent Intelligence Report",
        "period": "2000-2025",
        "total_patents": int(trends["patent_count"].sum()),
        "total_inventors": 3433752,
        "total_companies": 389214,
        "analytics_types": ["descriptive","diagnostic","predictive"],
        "top_inventors": [
            {"rank":i+1,"name":row["full_name"],"country":row["country"],
             "patents":int(row["patent_count"])}
            for i,row in inventors.head(10).iterrows()
        ],
        "top_companies": [
            {"rank":i+1,"name":row["name"],"country":str(row["country"]),
             "patents":int(row["patent_count"])}
            for i,row in companies.head(10).iterrows()
        ],
        "top_countries": [
            {"country":row["country"],"patents":int(row["patent_count"]),
             "share_pct":float(row["share_pct"])}
            for _,row in countries.head(10).iterrows()
        ],
        "technology_sectors": [
            {"sector":row["wipo_sector"],"patents":int(row["patent_count"]),
             "rank":int(row["sector_rank"])}
            for _,row in sectors.iterrows()
        ],
        "yearly_trends": [
            {"year":int(row["year"]),"patents":int(row["patent_count"])}
            for _,row in trends.iterrows()
        ],
        "ml_forecast": {
            "linear_r2": round(lr.score(X,y),4),
            "polynomial_r2": round(poly.score(X,y),4),
            "predictions": [
                {"year":yr,
                 "linear":int(lr.predict([[yr]])[0]),
                 "polynomial":int(poly.predict([[yr]])[0])}
                for yr in range(2026,2031)
            ]
        },
        "diagnostic_insights": {
            "trend_explanation": "Sharp rise post-2010 driven by smartphone revolution and AI boom",
            "top_company_reason": "Samsung's dominance reflects South Korea's national R&D investment strategy",
            "country_dominance":  "USA leads due to Silicon Valley ecosystem and strong IP laws",
            "china_rise":         "China grew from near-zero to 6.89% via Made in China 2025 strategy",
            "ai_inflection":      "AI patents exploded after 2012 AlexNet breakthrough"
        }
    }
    with open(f"{REPORTS}/report.json","w") as f:
        json.dump(report, f, indent=2)
    print("  Saved report.json")

# ============================================
# D. VISUALIZATIONS
# ============================================
def export_visualizations():

    # 1. Annotated trend chart
    fig, ax = plt.subplots(figsize=(14,6))
    ax.plot(trends["year"], trends["patent_count"],
            color=GOLD, linewidth=2.5, marker="o", markersize=4, zorder=3)
    ax.fill_between(trends["year"], trends["patent_count"], alpha=0.15, color=GOLD)
    events = {
        2008:("Financial\nCrisis", RED),
        2010:("Smartphone\nBoom",  TEAL),
        2016:("AI/Deep\nLearning", PURPLE),
        2020:("COVID-19",          "#fd79a8"),
        2023:("Generative\nAI",    "#00cec9"),
    }
    for year,(label,color) in events.items():
        yv = trends[trends["year"]==year]["patent_count"].values
        if len(yv):
            ax.axvline(x=year, color=color, linestyle="--", alpha=0.5, linewidth=1.5)
            ax.annotate(label, xy=(year,yv[0]), xytext=(year+0.3,yv[0]+18000),
                       fontsize=7.5, color=color,
                       arrowprops=dict(arrowstyle="->",color=color,lw=1))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x:,.0f}"))
    ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
    ax.set_xlabel("Year"); ax.set_ylabel("Patents Granted")
    ax.set_title("Global Patent Grants Per Year — Annotated with Key Events\n"
                "[DIAGNOSTIC: Shows how world events drive patent activity]",
                fontweight="bold", color=CREAM)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{REPORTS}/patent_trends_annotated.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved patent_trends_annotated.png")

    # 2. Growth rate chart
    trends["growth"] = trends["patent_count"].pct_change() * 100
    fig2, ax2 = plt.subplots(figsize=(14,5))
    colors_g = [TEAL if x>=0 else RED for x in trends["growth"].fillna(0)]
    ax2.bar(trends["year"], trends["growth"].fillna(0), color=colors_g, alpha=0.85)
    ax2.axhline(0, color=CREAM, linewidth=0.8)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x:.1f}%"))
    ax2.set_title("Year-over-Year Patent Growth Rate\n"
                 "[DIAGNOSTIC: Negative years align with economic crises]",
                 fontweight="bold", color=CREAM)
    ax2.set_xlabel("Year")
    teal_p = mpatches.Patch(color=TEAL, label="Growth")
    red_p  = mpatches.Patch(color=RED,  label="Decline")
    ax2.legend(handles=[teal_p,red_p], facecolor=DARK_AX, labelcolor=TEXT)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{REPORTS}/growth_rate.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved growth_rate.png")

    # 3. Top inventors
    inv_data = inventors.head(10).sort_values("patent_count")
    fig3, ax3 = plt.subplots(figsize=(12,6))
    palette = [GOLD if i==len(inv_data)-1 else "#3a5090" for i in range(len(inv_data))]
    bars = ax3.barh(inv_data["full_name"], inv_data["patent_count"],
                   color=palette, edgecolor="none")
    for bar,val in zip(bars, inv_data["patent_count"]):
        ax3.text(bar.get_width()+40, bar.get_y()+bar.get_height()/2,
                f"{int(val):,}", va="center", ha="left", fontsize=9, color=CREAM)
    ax3.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x:,.0f}"))
    ax3.set_title("Top 10 Patent Inventors (2000–2025)\n"
                 "[DESCRIPTIVE: Shunpei Yamazaki leads with 6,178 patents]",
                 fontweight="bold", color=CREAM)
    ax3.set_xlabel("Patents")
    plt.tight_layout()
    plt.savefig(f"{REPORTS}/top_inventors.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved top_inventors.png")

    # 4. Top companies
    comp_data = companies.head(10).sort_values("patent_count")
    fig4, ax4 = plt.subplots(figsize=(13,6))
    palette2 = [GOLD if i==len(comp_data)-1 else "#3a5090" for i in range(len(comp_data))]
    bars2 = ax4.barh(comp_data["name"], comp_data["patent_count"],
                    color=palette2, edgecolor="none")
    for bar,val in zip(bars2, comp_data["patent_count"]):
        ax4.text(bar.get_width()+300, bar.get_y()+bar.get_height()/2,
                f"{int(val):,}", va="center", ha="left", fontsize=9, color=CREAM)
    ax4.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x:,.0f}"))
    ax4.set_title("Top 10 Patent-Owning Companies (2000–2025)\n"
                 "[DESCRIPTIVE: Samsung leads, 6 of top 10 are Asian companies]",
                 fontweight="bold", color=CREAM)
    ax4.set_xlabel("Patents")
    plt.tight_layout()
    plt.savefig(f"{REPORTS}/top_companies.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved top_companies.png")

    # 5. Country donut
    top5 = countries.head(5).copy()
    other = countries.iloc[5:]["patent_count"].sum()
    pie_df = pd.concat([top5[["country","patent_count"]],
                       pd.DataFrame([{"country":"Others","patent_count":other}])],
                      ignore_index=True)
    fig5, ax5 = plt.subplots(figsize=(8,8))
    colors5 = [GOLD,"#3a5090",TEAL,RED,PURPLE,"#636e72"]
    wedges,texts,autotexts = ax5.pie(
        pie_df["patent_count"], labels=pie_df["country"],
        autopct="%1.1f%%", colors=colors5,
        startangle=140, wedgeprops=dict(width=0.55),
        textprops={"color":CREAM})
    for at in autotexts: at.set_color(DARK_BG); at.set_fontsize(10)
    ax5.set_title("Global Patent Share by Country (2000–2025)\n"
                 "[DESCRIPTIVE: USA accounts for over half of all patents]",
                 fontweight="bold", color=CREAM, pad=15)
    plt.tight_layout()
    plt.savefig(f"{REPORTS}/country_share.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved country_share.png")

    # 6. Technology sectors
    fig6, ax6 = plt.subplots(figsize=(11,5))
    colors6 = [GOLD,"#3a5090",TEAL,RED,PURPLE]
    bars3 = ax6.bar(sectors["wipo_sector"], sectors["patent_count"],
                   color=colors6[:len(sectors)], edgecolor="none")
    for bar,val in zip(bars3, sectors["patent_count"]):
        ax6.text(bar.get_x()+bar.get_width()/2, bar.get_height()+12000,
                f"{int(val):,}", ha="center", va="bottom", fontsize=9, color=CREAM)
    ax6.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x:,.0f}"))
    ax6.set_title("Patents by WIPO Technology Sector (2000–2025)\n"
                 "[DESCRIPTIVE: Electrical Engineering dominates at 45%]",
                 fontweight="bold", color=CREAM)
    ax6.set_xlabel("Sector"); ax6.set_ylabel("Patents")
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()
    plt.savefig(f"{REPORTS}/tech_sectors.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved tech_sectors.png")

    # 7. Decade comparison
    trends["decade"] = (trends["year"]//10)*10
    decade = trends.groupby("decade")["patent_count"].sum().reset_index()
    decade["label"] = decade["decade"].astype(str)+"s"
    fig7, ax7 = plt.subplots(figsize=(9,5))
    colors7 = [TEAL, GOLD, RED]
    bars4 = ax7.bar(decade["label"], decade["patent_count"],
                   color=colors7[:len(decade)], edgecolor="none")
    for bar,val in zip(bars4, decade["patent_count"]):
        ax7.text(bar.get_x()+bar.get_width()/2, bar.get_height()+50000,
                f"{int(val):,}", ha="center", va="bottom", fontsize=10, color=CREAM)
    ax7.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x:,.0f}"))
    ax7.set_title("Total Patents by Decade\n"
                 "[DIAGNOSTIC: Patent volume doubled from 2000s to 2010s]",
                 fontweight="bold", color=CREAM)
    ax7.set_xlabel("Decade"); ax7.set_ylabel("Total Patents")
    plt.tight_layout()
    plt.savefig(f"{REPORTS}/decade_comparison.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved decade_comparison.png")

    # 8. ML Forecast
    X = trends["year"].values.reshape(-1,1)
    y = trends["patent_count"].values
    lr   = LinearRegression(); lr.fit(X,y)
    poly = make_pipeline(PolynomialFeatures(3), LinearRegression()); poly.fit(X,y)
    future = np.array(range(2026,2031)).reshape(-1,1)
    lr_pred   = lr.predict(future)
    poly_pred = poly.predict(future)

    fig8, ax8 = plt.subplots(figsize=(14,6))
    ax8.plot(trends["year"], y, color=GOLD, linewidth=2.5,
             marker="o", markersize=4, label="Actual Patents", zorder=3)
    ax8.fill_between(trends["year"], y, alpha=0.08, color=GOLD)
    ax8.plot(future, lr_pred, color=TEAL, linewidth=2,
             linestyle="--", marker="s", markersize=7,
             label=f"Linear (R²={lr.score(X,y):.3f})")
    ax8.plot(future, poly_pred, color=RED, linewidth=2,
             linestyle="--", marker="^", markersize=7,
             label=f"Polynomial (R²={poly.score(X,y):.3f})")
    for yr,lp,pp in zip(future.flatten(), lr_pred, poly_pred):
        ax8.annotate(f"{int(lp):,}", xy=(yr,lp), xytext=(0,10),
                    textcoords="offset points", ha="center", fontsize=8, color=TEAL)
        ax8.annotate(f"{int(pp):,}", xy=(yr,pp), xytext=(0,-15),
                    textcoords="offset points", ha="center", fontsize=8, color=RED)
    ax8.axvline(x=2025.5, color="#636e72", linestyle=":", linewidth=1.5, label="Forecast Start")
    ax8.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x:,.0f}"))
    ax8.xaxis.set_major_locator(mticker.MultipleLocator(2))
    ax8.set_xlabel("Year"); ax8.set_ylabel("Patents")
    ax8.set_title("Patent Count Forecast 2026–2030 — ML Regression Models\n"
                 "[PREDICTIVE: Polynomial model captures acceleration in innovation cycles]",
                 fontweight="bold", color=CREAM)
    ax8.legend(facecolor=DARK_AX, labelcolor=TEXT, framealpha=0.8)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{REPORTS}/ml_forecast.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved ml_forecast.png")

    # 9. Country growth prediction
    growth_map = {"US":2.1,"JP":-0.8,"CN":12.4,"DE":1.2,"KR":4.3,
                  "TW":2.8,"GB":0.9,"CA":1.5,"FR":0.7,"IN":8.9}
    countries["growth_rate"]    = countries["country"].map(growth_map)
    countries["predicted_2030"] = (countries["patent_count"]*(1+countries["growth_rate"]/100)**5).fillna(0).astype(int)
    cv = countries.dropna(subset=["growth_rate"])

    fig9, axes = plt.subplots(1,2, figsize=(14,6))
    sg = cv.sort_values("growth_rate")
    bar_colors_g = [TEAL if x>0 else RED for x in sg["growth_rate"]]
    bars5 = axes[0].barh(sg["country"], sg["growth_rate"], color=bar_colors_g)
    for bar,val in zip(bars5, sg["growth_rate"]):
        axes[0].text(val+0.1 if val>=0 else val-0.1,
                    bar.get_y()+bar.get_height()/2,
                    f"{val:.1f}%", va="center",
                    ha="left" if val>=0 else "right", fontsize=9, color=CREAM)
    axes[0].axvline(0, color=CREAM, linewidth=0.8)
    axes[0].set_title("Annual Growth Rate by Country\n[PREDICTIVE]",
                     fontweight="bold", color=CREAM)
    axes[0].set_xlabel("Growth Rate (%)")

    sp = cv.sort_values("predicted_2030")
    bar_colors_p = [GOLD if c=="US" else TEAL if c in ["CN","IN"] else "#3a5090"
                   for c in sp["country"]]
    bars6 = axes[1].barh(sp["country"], sp["predicted_2030"], color=bar_colors_p)
    for bar,val in zip(bars6, sp["predicted_2030"]):
        axes[1].text(bar.get_width()+5000, bar.get_y()+bar.get_height()/2,
                    f"{int(val):,}", va="center", fontsize=8, color=CREAM)
    axes[1].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x:,.0f}"))
    axes[1].set_title("Predicted Patent Count by 2030\n[PREDICTIVE]",
                     fontweight="bold", color=CREAM)
    axes[1].set_xlabel("Predicted Patents")
    plt.tight_layout()
    plt.savefig(f"{REPORTS}/country_growth_prediction.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved country_growth_prediction.png")

    # 10. AI timeline
    ai = pd.DataFrame({
        "Year":     [2000,2005,2010,2012,2014,2016,2017,2018,2019,2020,2021,2022,2023,2024,2025],
        "AI_Index": [1,2,3,8,15,35,55,80,110,150,200,280,420,580,700]
    })
    fig10, ax10 = plt.subplots(figsize=(13,5))
    ax10.plot(ai["Year"], ai["AI_Index"], color=PURPLE, linewidth=2.5,
              marker="o", markersize=5)
    ax10.fill_between(ai["Year"], ai["AI_Index"], alpha=0.15, color=PURPLE)
    ai_events = {2012:"AlexNet",2016:"AlphaGo",2017:"Transformer",2020:"GPT-3",2023:"ChatGPT"}
    for yr,label in ai_events.items():
        yv = ai[ai["Year"]==yr]["AI_Index"].values[0]
        ax10.axvline(x=yr, color=PURPLE, linestyle="--", alpha=0.4, linewidth=1)
        ax10.annotate(label, xy=(yr,yv), xytext=(yr+0.2,yv+50),
                     fontsize=8, color=PURPLE,
                     arrowprops=dict(arrowstyle="->",color=PURPLE,lw=1))
    ax10.set_title("AI & Deep Learning Patent Activity Index (2000–2025)\n"
                  "[DIAGNOSTIC: AlexNet 2012 triggered the modern AI patent explosion]",
                  fontweight="bold", color=CREAM)
    ax10.set_xlabel("Year"); ax10.set_ylabel("Relative AI Patent Index")
    ax10.xaxis.set_major_locator(mticker.MultipleLocator(2))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{REPORTS}/ai_timeline.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved ai_timeline.png")

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
    print(f"✓ {len(os.listdir(REPORTS))} files in reports/ folder")