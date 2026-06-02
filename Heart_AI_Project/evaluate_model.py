"""
Measure how good the model is and save charts for your presentation.

Needs: data/heart.csv (same format as train_model.py)
Creates: reports/model_metrics.json and reports/confusion_matrix.png
"""

import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    roc_auc_score,
    roc_curve,
)

from data_pipeline import save_heart_csv

DATA_PATH = Path(__file__).parent / "data" / "heart.csv"
MODEL_PATH = Path(__file__).parent / "cardio_rf_model.pkl"
SCALER_PATH = Path(__file__).parent / "cardio_scaler.pkl"
REPORTS_DIR = Path(__file__).parent / "reports"

FEATURES = [
    "Age",
    "Sex",
    "ChestPain",
    "SystolicBP",
    "Cholesterol",
    "FastingBS",
    "RestingECG",
    "MaxHR",
    "ExerciseAngina",
    "Oldpeak",
    "Slope",
    "NumVessels",
    "Thal",
]


def main():
    if not DATA_PATH.exists():
        print("[*] Building merged dataset from UCI sources...")
        save_heart_csv()
    if not DATA_PATH.exists():
        print(f"[!] No data at {DATA_PATH}.")
        return
    if not MODEL_PATH.exists():
        print("[!] Run train_model.py first or keep your existing .pkl files.")
        return

    df = pd.read_csv(DATA_PATH)
    label_col = "HeartDisease" if "HeartDisease" in df.columns else "target"
    X = df[FEATURES]
    y = df[label_col]

    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    X_scaled = scaler.transform(X)

    preds = model.predict(X_scaled)
    proba = model.predict_proba(X_scaled)[:, 1]

    acc = accuracy_score(y, preds)
    auc = roc_auc_score(y, proba)
    report = classification_report(y, preds, output_dict=True)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    metrics = {
        "accuracy_percent": round(acc * 100, 2),
        "roc_auc": round(auc, 3),
        "classification_report": report,
        "note": "Use these numbers on your science fair poster.",
    }
    metrics_path = REPORTS_DIR / "model_metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"[*] Wrote {metrics_path}")
    print(f"[*] Accuracy: {acc:.2%}  |  ROC AUC: {auc:.3f}")

    ConfusionMatrixDisplay.from_predictions(y, preds)
    plt.title("Confusion Matrix — Heart Risk Model")
    cm_path = REPORTS_DIR / "confusion_matrix.png"
    plt.savefig(cm_path, dpi=120, bbox_inches="tight")
    plt.close()
    print(f"[*] Wrote {cm_path}")

    fpr, tpr, _ = roc_curve(y, proba)
    plt.figure()
    plt.plot(fpr, tpr, label=f"AUC = {auc:.3f}")
    plt.plot([0, 1], [0, 1], "k--")
    plt.xlabel("False positive rate")
    plt.ylabel("True positive rate")
    plt.title("ROC Curve")
    plt.legend()
    roc_path = REPORTS_DIR / "roc_curve.png"
    plt.savefig(roc_path, dpi=120, bbox_inches="tight")
    plt.close()
    print(f"[*] Wrote {roc_path}")


if __name__ == "__main__":
    main()
