from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.services import predictor

app = FastAPI(
    title="EstateIQ AI",
    version="0.2.0",
    description="AI-powered real estate intelligence platform."
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class PredictIn(BaseModel):
    city: str
    location: str | None = None
    area: float = Field(gt=0, le=100000)
    unit: str = "Marla"
    bedrooms: int = Field(ge=1, le=10)
    baths: int = Field(default=2, ge=1, le=10)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "EstateIQ AI"}


@app.get("/api/options")
async def options():
    return predictor.options()


@app.post("/api/predict")
async def predict(body: PredictIn):
    if body.unit not in predictor.SQFT:
        raise HTTPException(422, f"unit must be one of {list(predictor.SQFT)}")
    sqft = body.area * predictor.SQFT[body.unit]
    if not 450 <= sqft <= 25000:
        raise HTTPException(422, "Area must be between about 450 and 25,000 sq ft; the model has not seen sizes outside that range.")
    return predictor.predict(body.city, body.location, body.area, body.unit, body.bedrooms, body.baths)
