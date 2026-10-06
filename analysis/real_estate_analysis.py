"""EstateIQ AI - data cleaning and exploratory analysis.

Run:  python -m analysis.real_estate_analysis
Reads data/properties_raw.csv, writes data/properties_clean.csv and charts in reports/figures/.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
RAW, CLEAN, FIG = ROOT / "data/properties_raw.csv", ROOT / "data/properties_clean.csv", ROOT / "reports/figures"
SQFT = {"Marla": 272.25, "Kanal": 5445.0, "Sq. Yd.": 9.0}  # 1 kanal = 20 marla


def clean(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.drop_duplicates("property_id").copy()
    df = df[df["purpose"] == "For Sale"]                       # rent prices are on a different scale
    num = df["area"].str.extract(r"^([\d\.,]+)\s*(.+)$")
    df["area_value"] = pd.to_numeric(num[0].str.replace(",", ""), errors="coerce")
    df["area_unit"] = num[1].str.strip()
    df["area_sqft"] = df["area_value"] * df["area_unit"].map(SQFT)
    df = df.dropna(subset=["area_sqft"])
    df = df[df["bedrooms"].between(1, 10) & df["baths"].between(1, 10)]   # 0 means missing or plot
    df = df[df["area_sqft"].between(450, 25000)]
    df["price_per_sqft"] = df["price"] / df["area_sqft"]
    lo, hi = df["price_per_sqft"].quantile([0.01, 0.99])       # drop extreme price-per-sqft outliers
    df = df[df["price_per_sqft"].between(lo, hi)]
    df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")
    df["month"] = df["date_added"].dt.to_period("M").astype(str)
    return df.reset_index(drop=True)


def load_clean() -> pd.DataFrame:
    return pd.read_csv(CLEAN, parse_dates=["date_added"]) if CLEAN.exists() else clean(pd.read_csv(RAW))


def make_charts(df: pd.DataFrame) -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", palette="viridis")
    def save(name):
        plt.tight_layout(); plt.savefig(FIG / name, dpi=140); plt.close()

    plt.figure(figsize=(8, 4.5)); sns.histplot(df["price"] / 1e6, bins=60, log_scale=True)
    plt.xlabel("Price (PKR million, log scale)"); plt.title("Price distribution"); save("01_price_distribution.png")

    order = df.groupby("city")["price_per_sqft"].median().sort_values(ascending=False).index
    plt.figure(figsize=(8, 4.5)); sns.barplot(df, x="city", y="price_per_sqft", order=order, estimator="median", errorbar=None)
    plt.ylabel("Median price per sq ft (PKR)"); plt.title("City comparison"); save("02_city_price_per_sqft.png")

    top = df["location"].value_counts().head(12).index
    t = df[df["location"].isin(top)]; o = t.groupby("location")["price_per_sqft"].median().sort_values().index
    plt.figure(figsize=(9, 5.5)); sns.boxplot(t, y="location", x="price_per_sqft", order=o, showfliers=False)
    plt.xlabel("Price per sq ft (PKR)"); plt.title("Most listed areas"); save("03_top_locations.png")

    s = df.sample(min(len(df), 6000), random_state=1)
    plt.figure(figsize=(8, 5)); sns.scatterplot(s, x="area_sqft", y=s["price"] / 1e6, hue="city", alpha=.5, s=14)
    plt.yscale("log"); plt.xscale("log"); plt.ylabel("Price (PKR million)"); plt.xlabel("Area (sq ft)")
    plt.title("Area vs price"); save("04_area_vs_price.png")

    plt.figure(figsize=(7, 5)); sns.heatmap(df[["price", "area_sqft", "bedrooms", "baths", "latitude", "longitude"]].corr(), annot=True, fmt=".2f", cmap="viridis")
    plt.title("Correlations"); save("05_correlation.png")

    m = df.groupby(["month", "city"])["price_per_sqft"].median().reset_index()
    m = m[m["month"] < "2022-10"]
    plt.figure(figsize=(9, 4.5)); sns.lineplot(m, x="month", y="price_per_sqft", hue="city", marker="o")
    plt.xticks(rotation=45); plt.ylabel("Median price per sq ft (PKR)"); plt.title("Asking price trend by listing month"); save("06_price_trend.png")


if __name__ == "__main__":
    raw = pd.read_csv(RAW)
    df = clean(raw)
    df.to_csv(CLEAN, index=False)
    make_charts(df)
    print(f"Raw rows: {len(raw):,} -> clean rows: {len(df):,}")
    print(df.groupby("city").agg(listings=("price", "size"), median_price=("price", "median"), median_ppsf=("price_per_sqft", "median")).round(0))
    print("Charts saved to", FIG)
