"""Loads the trained model and turns user input into a price estimate."""
from functools import lru_cache
from pathlib import Path
import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SQFT = {"Marla": 272.25, "Kanal": 5445.0, "Sq. Yd.": 9.0, "Square Feet": 1.0}


@lru_cache
def _bundle():
    return joblib.load(ROOT / "ml/model.joblib")


@lru_cache
def _data() -> pd.DataFrame:
    return pd.read_csv(ROOT / "data/properties_clean.csv", usecols=["city", "location", "latitude", "longitude", "price", "bedrooms", "baths", "area_sqft", "price_per_sqft"])


def options() -> dict:
    d = _data()
    known = set(_bundle()["known_locations"])
    out = {}
    for city, g in d.groupby("city"):
        locs = g["location"].value_counts()
        out[city] = [l for l in locs[locs >= 20].index if l in known][:60]
    feat = d.sample(6, random_state=7)[["city", "location", "price", "bedrooms", "baths", "area_sqft"]]
    return {
        "cities": out, "units": list(SQFT),
        "stats": {"listings": int(len(d)), "median_price": float(d.price.median())},
        "ppsf": {c: float(v) for c, v in d.groupby("city").price_per_sqft.median().sort_values(ascending=False).items()},
        "featured": feat.to_dict("records"),
    }


def predict(city: str, location: str | None, area: float, unit: str, bedrooms: int, baths: int) -> dict:
    b, d = _bundle(), _data()
    sqft = area * SQFT[unit]
    loc = location if location in b["known_locations"] else "Other"
    near = d[(d.city == city) & (d.location == location)]
    ref = near if len(near) else d[d.city == city]
    row = pd.DataFrame([{"area_sqft": sqft, "bedrooms": bedrooms, "baths": baths,
                         "latitude": ref.latitude.median(), "longitude": ref.longitude.median(),
                         "city": city, "location": loc}])[b["features"]]
    pipe = b["pipeline"]
    mid = float(np.expm1(pipe.predict(row)[0]))
    out = {"price": mid, "area_sqft": sqft, "model": b["model_name"], "low": mid * 0.8, "high": mid * 1.2}
    forest = pipe.named_steps["model"]
    if hasattr(forest, "estimators_"):          # spread across the forest's trees gives a data-based range
        X = pipe.named_steps["pre"].transform(row)
        p = np.expm1([t.predict(X)[0] for t in forest.estimators_])
        out["low"], out["high"] = float(np.percentile(p, 10)), float(np.percentile(p, 90))
    return out
