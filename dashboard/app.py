import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.queries import (
    q1_top_inventors,
    q2_top_companies,
    q3_top_countries,
    q4_trends_over_time,
    q6_cte_tech_sectors,
    q7_ranked_inventors
)

st.set_page_config(
    page_title="Global Patent Intelligence",
    page_icon="💡",
    layout="wide"
)

st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1a237e;
        text-align: center;
        margin-bottom: 0;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">💡 Global Patent Intelligence Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Geography of Innovation: 2000–2025 | USPTO PatentsView Data</p>', unsafe_allow_html=True)
st.divider()

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Total Patents", "7,194,096")
with col2:
    st.metric("Total Inventors", "3,433,752")
with col3:
    st.metric("Total Companies", "389,214")
with col4:
    st.metric("Years Covered", "2000–2025")
with col5:
    st.metric("Top Country", "🇺🇸 USA (52.97%)")

st.divider()

@st.cache_data(show_spinner="Loading trends...")
def load_trends(): return q4_trends_over_time()

@st.cache_data(show_spinner="Loading inventors...")
def load_inventors(): return q1_top_inventors(20)

@st.cache_data(show_spinner="Loading companies...")
def load_companies(): return q2_top_companies(20)

@st.cache_data(show_spinner="Loading countries...")
def load_countries(): return q3_top_countries(20)

@st.cache_data(show_spinner="Loading sectors...")
def load_sectors(): return q6_cte_tech_sectors()

@st.cache_data(show_spinner="Loading rankings...")
def load_ranked(): return q7_ranked_inventors()

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Trends",
    "👤 Inventors",
    "🏢 Companies",
    "🌍 Countries",
    "🔬 Technology",
    "🏆 Rankings"
])

sns.set_theme(style="whitegrid")

with tab1:
    st.subheader("Patent Activity Over Time (2000–2025)")
    trends = load_trends()

    fig, ax = plt.subplots(figsize=(13, 5))
    ax.plot(trends["year"], trends["patent_count"],
            color="#1a237e", linewidth=2.5, marker="o", markersize=4)
    ax.fill_between(trends["year"], trends["patent_count"],
                    alpha=0.1, color="#1a237e")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
    ax.set_xlabel("Year")
    ax.set_ylabel("Patents Granted")
    ax.set_title("Global Patent Grants Per Year", fontweight="bold")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.subheader("Decade Comparison")
    trends["decade"] = (trends["year"] // 10) * 10
    decade = trends.groupby("decade")["patent_count"].sum().reset_index()
    decade["label"] = decade["decade"].astype(str) + "s"

    fig2, ax2 = plt.subplots(figsize=(8, 4))
    colors = sns.color_palette("Blues_d", len(decade))
    bars = ax2.bar(decade["label"], decade["patent_count"], color=colors)
    ax2.bar_label(bars, fmt="%,.0f", padding=3)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax2.set_title("Total Patents by Decade", fontweight="bold")
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()

    st.dataframe(trends[["year", "patent_count"]], use_container_width=True)

with tab2:
    st.subheader("Top Patent Inventors (2000–2025)")
    inventors = load_inventors()

    top_n = st.slider("Show top N inventors", 5, 20, 10)
    inv_data = inventors.head(top_n).sort_values("patent_count")

    fig, ax = plt.subplots(figsize=(11, max(5, top_n * 0.5)))
    colors = sns.color_palette("Blues_d", len(inv_data))
    bars = ax.barh(inv_data["full_name"], inv_data["patent_count"], color=colors)
    ax.bar_label(bars, fmt="%,.0f", padding=4)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.set_title(f"Top {top_n} Inventors by Patent Count", fontweight="bold")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.dataframe(inventors.head(top_n), use_container_width=True)

with tab3:
    st.subheader("Top Patent-Owning Companies (2000–2025)")
    companies = load_companies()

    top_n = st.slider("Show top N companies", 5, 20, 10)
    comp_data = companies.head(top_n).sort_values("patent_count")

    fig, ax = plt.subplots(figsize=(12, max(5, top_n * 0.6)))
    colors = sns.color_palette("Oranges_d", len(comp_data))
    bars = ax.barh(comp_data["name"], comp_data["patent_count"], color=colors)
    ax.bar_label(bars, fmt="%,.0f", padding=4)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.set_title(f"Top {top_n} Companies by Patent Count", fontweight="bold")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.dataframe(companies.head(top_n), use_container_width=True)

with tab4:
    st.subheader("Patent Activity by Country (2000–2025)")
    countries = load_countries()

    col1, col2 = st.columns(2)
    with col1:
        top5 = countries.head(5).copy()
        other_count = countries.iloc[5:]["patent_count"].sum()
        pie_data = pd.concat([
            top5[["country", "patent_count"]],
            pd.DataFrame([{"country": "Others", "patent_count": other_count}])
        ], ignore_index=True)

        fig, ax = plt.subplots(figsize=(7, 7))
        colors = sns.color_palette("Set2", len(pie_data))
        ax.pie(pie_data["patent_count"], labels=pie_data["country"],
               autopct="%1.1f%%", colors=colors, startangle=140)
        ax.set_title("Patent Share by Country", fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        fig2, ax2 = plt.subplots(figsize=(7, 7))
        data_sorted = countries.sort_values("patent_count")
        colors2 = sns.color_palette("coolwarm", len(data_sorted))
        bars = ax2.barh(data_sorted["country"], data_sorted["patent_count"], color=colors2)
        ax2.bar_label(bars, fmt="%,.0f", padding=3)
        ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
        ax2.set_title("Patents by Country", fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close()

    st.dataframe(countries, use_container_width=True)

with tab5:
    st.subheader("Patent Activity by Technology Sector")
    sectors = load_sectors()

    fig, ax = plt.subplots(figsize=(11, 5))
    colors = sns.color_palette("viridis", len(sectors))
    bars = ax.bar(sectors["wipo_sector"], sectors["patent_count"],
                  color=colors, edgecolor="white")
    ax.bar_label(bars, fmt="%,.0f", padding=4)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.set_title("Patents by WIPO Technology Sector (2000–2025)", fontweight="bold")
    ax.set_xlabel("Sector")
    ax.set_ylabel("Patents")
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.dataframe(sectors, use_container_width=True)

with tab6:
    st.subheader("Inventor Rankings with Window Functions")
    st.caption("Global rank, dense rank, and country-level rank for top inventors")
    ranked = load_ranked()

    country_filter = st.selectbox(
        "Filter by country",
        ["All"] + sorted(ranked["country"].dropna().unique().tolist())
    )

    if country_filter != "All":
        ranked = ranked[ranked["country"] == country_filter]

    st.dataframe(ranked, use_container_width=True)

st.divider()
st.caption("Data source: USPTO PatentsView Granted Patent Disambiguated Data | Built with Python, MySQL, and Streamlit")