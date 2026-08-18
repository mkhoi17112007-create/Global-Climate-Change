from pathlib import Path
import os
import json
import re
import joblib
import numpy as np
import pandas as pd

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text

BASE_DIR = Path(__file__).resolve().parents[1]
ARTIFACTS = BASE_DIR / "artifacts"

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is required")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

metadata = json.loads(
    (ARTIFACTS / "model_metadata.json").read_text(encoding="utf-8")
)
model = joblib.load(ARTIFACTS / "climate_ridge_20y.joblib")

FEATURES = metadata["features"]
CITY_TREND_FEATURES = metadata["city_trend_features"]
HISTORICAL_END = pd.Timestamp(metadata["historical_end"])
FORECAST_END = HISTORICAL_END + pd.DateOffset(years=20)

app = FastAPI(
    title="Global Climate Change Forecast API",
    version="2.0",
    description="Monthly statistical temperature forecast for five major cities."
)

class PredictionInput(BaseModel):
    city: str
    year: int = Field(ge=1800, le=2100)
    month: int = Field(ge=1, le=12)

class PredictionResponse(BaseModel):
    city: str
    date: str
    predicted_temperature_c: float
    model: str
    warning: str

def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")

def get_lookup(city: str, month: int) -> dict:
    query = text("""
        SELECT *
        FROM climate_feature_lookup
        WHERE country = :city
          AND month = :month
        LIMIT 1
    """)

    with engine.connect() as conn:
        row = conn.execute(
            query,
            {"country": country, "month": month}
        ).mappings().first()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail=f"No feature lookup for city={city}, month={month}"
        )
    return dict(row)

def build_feature_row(city: str, year: int, month: int) -> pd.DataFrame:
    target_date = pd.Timestamp(year=year, month=month, day=1)

    if target_date <= HISTORICAL_END:
        raise HTTPException(
            status_code=400,
            detail=f"Prediction date must be after {HISTORICAL_END.date()}"
        )

    if target_date > FORECAST_END:
        raise HTTPException(
            status_code=400,
            detail=f"Project horizon is limited to 20 years: max date {FORECAST_END.date()}"
        )

    row = get_lookup(city, month)
    row["year"] = year
    row["month"] = month
    row["quarter"] = (month - 1) // 3 + 1
    row["time_idx"] = (year - 1850) * 12 + (month - 1)
    row["month_sin"] = np.sin(2 * np.pi * month / 12)
    row["month_cos"] = np.cos(2 * np.pi * month / 12)

    current_city_slug = slug(city)
    for feature in CITY_TREND_FEATURES:
        target_city_slug = feature.replace("time_idx_city_", "")
        row[feature] = row["time_idx"] if current_city_slug == target_city_slug else 0

    frame = pd.DataFrame([row])
    return frame[["country"] + FEATURES]

def predict_one(city: str, year: int, month: int) -> float:
    X = build_feature_row(city, year, month)
    return float(model.predict(X)[0])

@app.get("/")
def root():
    return {
        "service": "Global Climate Change Forecast API",
        "model": metadata["model_name"],
        "historical_end": metadata["historical_end"],
        "forecast_horizon_months": metadata["forecast_horizon_months"],
        "warning": metadata["warning"]
    }

@app.get("/countries")
def cities():
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT DISTINCT country FROM climate_feature_lookup ORDER BY country")
        ).fetchall()
    return [row[0] for row in rows]

@app.get("/model-info")
def model_info():
    return metadata

@app.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionInput):
    yhat = predict_one(payload.city, payload.year, payload.month)
    return PredictionResponse(
        city=payload.city,
        date=f"{payload.year:04d}-{payload.month:02d}",
        predicted_temperature_c=round(yhat, 3),
        model=metadata["model_name"],
        warning=metadata["warning"]
    )

@app.get("/forecast")
def forecast(
    city: str = Query(...),
    years: int = Query(20, ge=1, le=20)
):
    start = HISTORICAL_END + pd.offsets.MonthBegin(1)
    end = HISTORICAL_END + pd.DateOffset(years=years)
    dates = pd.date_range(start, end, freq="MS")

    output = []
    for date in dates:
        yhat = predict_one(city, int(date.year), int(date.month))
        output.append({
            "date": date.strftime("%Y-%m"),
            "predicted_temperature_c": round(yhat, 3)
        })
    return output