<div align="center">

# 🏠 EstateIQ AI

**An AI real estate platform for Pakistan: estimate house prices, explore the market, and (soon) get recommendations and answers from an AI assistant.**

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?logo=scikitlearn&logoColor=white)
![Status](https://img.shields.io/badge/status-in%20development-F2B134)

![EstateIQ dashboard](<img width="1346" height="636" alt="house" src="https://github.com/user-attachments/assets/8d68f551-f031-4f83-b78e-33f0ed91167b" />
)

</div>

## What it does

Buying property in Pakistan means comparing listings across cities, areas and units (marla, kanal, square yards) with no clear sense of what is a fair price. EstateIQ AI turns about 25,000 real listings into something you can use:

- **Price estimate.** Pick a city, area name, size, bedrooms and bathrooms. You get a price in lakh and crore plus a likely range.
- **Market view.** Median asking rate per square foot for each city, from the cleaned data.
- **Properties.** Example listings from the dataset, filterable by city.
- **Assistant.** A chat interface. Right now it gives canned answers; the live AI assistant and document search are the next steps.

## Current status

| Module | Status |
|---|---|
| Data cleaning and analysis (Pandas, NumPy, Matplotlib, Seaborn) | ✅ Done |
| ML price prediction (Random Forest, saved model) | ✅ Done |
| FastAPI backend and web dashboard | ✅ Done for prediction; other pages in progress |
| Property recommendations with explanations | 🔜 Next |
| Generative AI assistant (Gemini) | 🔜 Planned |
| RAG knowledge assistant (ChromaDB) | 🔜 Planned |

## Model results

Trained and tested on a 80/20 split of the cleaned data (`ml/metrics.json`).

| Model | MAE (PKR) | R² on log price |
|---|---|---|
| Linear Regression | 12.7 million | 0.859 |
| Decision Tree | 6.9 million | 0.926 |
| **Random Forest** (saved) | **6.2 million** | **0.942** |

The model predicts log price, which handles the huge spread between small and large houses. The median asking price in the data is PKR 25 million, so a typical estimate is off by roughly a quarter. The price range shown in the app comes from how much the forest's 120 trees disagree.

## Quick start

```bash
git clone https://github.com/YOUR-USERNAME/EstateIQ-AI.git
cd EstateIQ-AI

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000. Interactive API docs are at http://127.0.0.1:8000/docs.

The cleaned data and trained model are already in the repo. To rebuild them from the raw file:

```bash
python -m analysis.real_estate_analysis   # cleans data, saves charts to reports/figures/
python -m ml.train                        # trains 3 models, saves ml/model.joblib
```

## API

```bash
curl -X POST http://127.0.0.1:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"city":"Lahore","location":"DHA Defence","area":10,"unit":"Marla","bedrooms":4,"baths":4}'
```

```json
{ "price": 50358625, "low": 44347689, "high": 58661128, "area_sqft": 2722, "model": "Random Forest" }
```

| Endpoint | Purpose |
|---|---|
| `GET /` | Web dashboard |
| `GET /api/options` | Cities, areas, units, city rates and example listings |
| `POST /api/predict` | Price estimate and range |
| `GET /health` | Health check |

Supported units are Marla, Kanal, Sq. Yd. and Square Feet. Sizes outside about 450 to 25,000 sq ft are rejected because the model has not seen them.

## Data

About 29,000 house listings from Zameen.com (September 2022) covering Lahore, Karachi, Islamabad and Peshawar. After cleaning, 24,918 for-sale listings remain.

Cleaning steps: keep for-sale listings only, convert marla, kanal and square yards to square feet, remove missing or implausible bedroom, bathroom and area values, and drop the top and bottom 1% of price per square foot.

Six charts (price distribution, city comparison, top areas, area vs price, correlations, price trend) are in `reports/figures/`.

Details and the licence note are in [`data/README.md`](data/README.md).

## Project structure

```
EstateIQ-AI/
├── app/                  FastAPI app, routes and services (predictor)
├── analysis/             Data cleaning and EDA
├── ml/                   Training script, saved model, metrics
├── data/                 Raw and cleaned data, RAG documents folder
├── reports/figures/      Generated charts
├── static/               CSS and JavaScript
├── templates/            HTML dashboard
└── docs/screenshots/     Screenshots
```

## Limitations

- Prices are **2022 asking prices**, not sale prices, and are not adjusted for inflation.
- The data covers **houses only**. Flats and plots are not supported.
- **Lahore makes up most of the data**, and Peshawar has fewer than 100 listings, so estimates for smaller markets are less reliable.
- The estimate is a guide, not a professional valuation.
- The dataset was scraped from a public website and has no stated licence. It is used for learning, not commercial use.

## Roadmap

- [x] Dataset selection, cleaning and analysis
- [x] Price prediction model and `/api/predict`
- [x] Dashboard UI connected to the model
- [ ] Recommendation engine that explains each match
- [ ] Gemini assistant with a real-estate system prompt
- [ ] RAG over buying guides and legal checklists (ChromaDB)
- [ ] Tests and deployment

## Tech stack

Python, FastAPI, Pandas, NumPy, scikit-learn, Matplotlib, Seaborn, joblib, Jinja2, vanilla HTML, CSS and JavaScript. Planned: Gemini API, ChromaDB, sentence-transformers.

## Credits

Listing data from [Zameen.com](https://www.zameen.com), via the public repository [huzefakhan/Zameen.com-2022-latest-Raw-Data-Set-Realstate](https://github.com/huzefakhan/Zameen.com-2022-latest-Raw-Data-Set-Realstate).
