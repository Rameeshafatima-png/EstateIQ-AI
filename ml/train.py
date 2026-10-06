"""EstateIQ AI - price prediction training.

Run:  python -m ml.train
Compares three models on log(price), prints MAE / RMSE / R2 in rupees, saves the best to ml/model.joblib.
"""
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeRegressor
from analysis.real_estate_analysis import load_clean

OUT = Path(__file__).parent
NUM = ["area_sqft", "bedrooms", "baths", "latitude", "longitude"]
CAT = ["city", "location"]


def prepare(df: pd.DataFrame):
    df = df.copy()
    keep = df["location"].value_counts()
    df["location"] = df["location"].where(df["location"].isin(keep[keep >= 20].index), "Other")
    return df[NUM + CAT], np.log1p(df["price"])


def build(model) -> Pipeline:
    pre = ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore"), CAT)], remainder="passthrough")
    return Pipeline([("pre", pre), ("model", model)])


if __name__ == "__main__":
    X, y = prepare(load_clean())
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
    models = {
        "Linear Regression": LinearRegression(),
        "Decision Tree": DecisionTreeRegressor(max_depth=14, min_samples_leaf=5, random_state=42),
        "Random Forest": RandomForestRegressor(n_estimators=120, min_samples_leaf=3, n_jobs=-1, random_state=42),
    }
    results, fitted = {}, {}
    for name, m in models.items():
        p = build(m).fit(Xtr, ytr); fitted[name] = p
        pred = np.expm1(p.predict(Xte)); true = np.expm1(yte)
        results[name] = {"MAE": round(mean_absolute_error(true, pred)), "RMSE": round(float(np.sqrt(mean_squared_error(true, pred)))),
                         "R2_price": round(r2_score(true, pred), 3), "R2_log_price": round(r2_score(yte, p.predict(Xte)), 3)}
        print(f"{name:18s}", results[name])
    best = max(results, key=lambda k: results[k]["R2_log_price"])
    joblib.dump({"pipeline": fitted[best], "features": NUM + CAT, "model_name": best, "known_locations": sorted(set(X["location"]))}, OUT / "model.joblib", compress=3)
    (OUT / "metrics.json").write_text(json.dumps({"best": best, "test_rows": len(Xte), "results": results}, indent=2))
    print("Saved best model:", best)
