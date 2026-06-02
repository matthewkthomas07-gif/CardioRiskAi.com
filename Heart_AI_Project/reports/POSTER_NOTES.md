# Science fair poster — what to say

Copy these ideas onto your board after you run `python evaluate_model.py` (with `data/heart.csv`).

## What I built

- A computer program that learns patterns from heart health data.
- It gives a **risk percentage** — not a yes/no doctor diagnosis.

## How it works (3 steps)

1. **Collect** patient numbers (age, blood pressure, etc.).
2. **Scale** them with `cardio_scaler.pkl` so they match training.
3. **Predict** with `cardio_rf_model.pkl` (Random Forest).

## Numbers to show (from `reports/model_metrics.json`)

- **Accuracy** — how often the model is right on test data.
- **ROC AUC** — how well it separates sick vs healthy (closer to 1.0 is better).
- **Confusion matrix picture** — `reports/confusion_matrix.png`.

## Always include

> “This project is for learning only. Talk to a doctor for real medical advice.”
