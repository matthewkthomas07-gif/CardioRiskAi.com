import json
import os
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from chat_bot import GREETING, handle_message, sessions

ROOT = Path(__file__).parent
MODEL_PATH = ROOT / "cardio_rf_model.pkl"
SCALER_PATH = ROOT / "cardio_scaler.pkl"
WEB_DIST = ROOT / "website" / "dist"
METRICS_PATH = ROOT / "model_metrics.json"
GLOSSARY_PATH = ROOT / "medical_glossary.json"

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://cardioriskai.com",
    "https://www.cardioriskai.com",
    "https://cardioriskai.vercel.app",
]
extra_origins = os.getenv("CORS_ORIGINS", "")
if extra_origins:
    ALLOWED_ORIGINS.extend(o.strip() for o in extra_origins.split(",") if o.strip())

app = FastAPI(title="CardioRisk AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = None
scaler = None
load_error: str | None = None

print("[*] Loading AI Model and Scaler...")
try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    print("[*] Successfully loaded AI brains!")
except Exception as e:
    load_error = str(e)
    print(f"[!] Error loading files: {e}")


class PatientData(BaseModel):
    Age: int
    Sex: int
    ChestPain: int
    SystolicBP: int
    Cholesterol: int
    FastingBS: int
    RestingECG: int
    MaxHR: int
    ExerciseAngina: int
    Oldpeak: float
    Slope: int
    NumVessels: int
    Thal: int


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    stage: str
    collected: dict
    prediction: dict | None = None
    done: bool = False


def _require_model():
    if model is None or scaler is None:
        raise HTTPException(
            status_code=503,
            detail=f"Model not loaded. {load_error or 'Missing .pkl files.'}",
        )


def _run_prediction(data: dict) -> dict:
    _require_model()
    patient_df = pd.DataFrame([data])
    scaled_features = scaler.transform(patient_df)
    risk_probability = model.predict_proba(scaled_features)[0][1]
    return {
        "status": "success",
        "risk_percentage": round(risk_probability * 100, 2),
        "message": "Prediction complete.",
    }


@app.get("/api/health")
@app.get("/health")
def health():
    return {
        "status": "ok" if model is not None else "error",
        "model_loaded": model is not None,
        "scaler_loaded": scaler is not None,
        "error": load_error,
        "brand": "CardioRisk AI",
    }


@app.post("/api/predict")
@app.post("/predict")
def predict_risk(patient: PatientData):
    return _run_prediction(patient.model_dump())


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if req.message.strip().lower() in ("ping",):
        return ChatResponse(
            reply="pong",
            session_id=req.session_id or "",
            stage="idle",
            collected={},
        )

    def predict_fn(data: dict) -> dict:
        return _run_prediction(data)

    if not req.message.strip() and not req.session_id:
        session = sessions.get_or_create(None)
        return ChatResponse(
            reply=GREETING,
            session_id=session.session_id,
            stage=session.stage,
            collected=session.data,
        )

    result = handle_message(req.message, req.session_id, predict_fn)
    return ChatResponse(
        reply=result.reply,
        session_id=result.session_id,
        stage=result.stage,
        collected=result.collected,
        prediction=result.prediction,
        done=result.done,
    )


@app.get("/api/metrics")
def get_metrics():
    if METRICS_PATH.is_file():
        return json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    return {
        "accuracy_percent": None,
        "note": "Run python train_model.py to generate metrics.",
    }


@app.get("/api/glossary")
def get_glossary():
    if GLOSSARY_PATH.is_file():
        return json.loads(GLOSSARY_PATH.read_text(encoding="utf-8"))
    return []


@app.get("/api/chat/welcome", response_model=ChatResponse)
def chat_welcome():
    session = sessions.get_or_create(None)
    return ChatResponse(
        reply=GREETING,
        session_id=session.session_id,
        stage=session.stage,
        collected=session.data,
    )


if WEB_DIST.is_dir():
    app.mount("/", StaticFiles(directory=WEB_DIST, html=True), name="website")
