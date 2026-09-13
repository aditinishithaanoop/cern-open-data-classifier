"""
Minimal API serving the trained classifier.

Deliberately small: one endpoint, clear input schema, no unnecessary
complexity. The goal for the AWS deployment stage is a working demo, not a
production-grade service.

Run locally with:
    uvicorn app.main:app --reload

Once deployed, a request looks like:
    POST /predict
    {"pt1": 30.0, "eta1": 0.5, "phi1": 0.1, "pt2": 25.0, "eta2": -0.3, "phi2": 2.0}
"""

import os
import sys

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.train import build_features

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "outputs", "model.joblib")

app = FastAPI(title="CERN Open Data Classifier Demo")

_model_bundle = None  # lazy-loaded so the app can still start without a model for /health


class EventFeatures(BaseModel):
    pt1: float
    eta1: float
    phi1: float
    pt2: float
    eta2: float
    phi2: float


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": _model_bundle is not None}


@app.on_event("startup")
def load_model():
    global _model_bundle
    if os.path.exists(MODEL_PATH):
        _model_bundle = joblib.load(MODEL_PATH)
    else:
        _model_bundle = None  # /predict will return a clear error until a model is trained


@app.post("/predict")
def predict(event: EventFeatures):
    if _model_bundle is None:
        raise HTTPException(
            status_code=503,
            detail="No trained model found. Run src/train.py first to produce outputs/model.joblib.",
        )

    df = pd.DataFrame([event.dict()])
    X = build_features(df)[_model_bundle["feature_columns"]]
    proba = _model_bundle["model"].predict_proba(X)[0, 1]

    return {
        "signal_probability": float(proba),
        "prediction": "signal" if proba > 0.5 else "background",
    }
