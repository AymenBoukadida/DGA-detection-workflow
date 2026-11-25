from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.domains import normalize_domain
from app.model import MODEL_VERSION, THRESHOLD, model_info, train_model

model = train_model()

app = FastAPI(title="DGA Classifier", version=MODEL_VERSION)


class PredictRequest(BaseModel):
    domain: str


class BatchPredictRequest(BaseModel):
    domains: list[str] = Field(min_length=1, max_length=1000)


def _severity(probability: float) -> int:
    if probability < 0.6:
        return 0
    if probability < 0.7:
        return 1
    if probability < 0.8:
        return 2
    return 3


def _predict(domain: str) -> dict:
    host = normalize_domain(domain)
    probability = round(float(model.predict_proba([host])[0]), 4)
    return {
        "domain": host,
        "probability_DGA": probability,
        "label": "dga" if probability >= THRESHOLD else "benign",
        "threshold": THRESHOLD,
        "severity": _severity(probability),
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model_loaded": model is not None}


@app.get("/model-info")
def get_model_info() -> dict:
    return model_info(model)


@app.post("/predict")
def predict(payload: PredictRequest) -> dict:
    try:
        return _predict(payload.domain)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/predict/batch")
def predict_batch(payload: BatchPredictRequest) -> dict:
    results = []
    for index, domain in enumerate(payload.domains):
        try:
            results.append(_predict(domain))
        except ValueError as exc:
            raise HTTPException(
                status_code=422,
                detail=f"invalid domain at index {index}: {exc}",
            ) from exc
    return {"results": results}
