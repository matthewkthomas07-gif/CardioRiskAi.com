# CardioRisk AI (Heart Risk Project)

**CardioRiskAi.com** — A machine-learning cardiovascular risk demo with a guided **AI chat assistant**, FastAPI backend, and production-ready website.

Built for school / science fair demos and portfolio hosting.

**Important:** This is **not** a medical device. It does not diagnose disease. Always talk to a real doctor about health.

---

## What’s in this folder?

| File | What it does |
|------|----------------|
| `cardio_rf_model.pkl` | The trained “brain” (Random Forest model) |
| `cardio_scaler.pkl` | Scales numbers so the brain understands them |
| `app.py` | API server other programs can call |
| `ui.py` | Friendly web page to try the AI |
| `RUN_WEBSITE.bat` | **Full site** — builds CardioRiskAi.com UI + API (recommended) |
| `RUN_ME.bat` | Streamlit checker (simple local demo) |
| `RUN_API.bat` | API only (no website build) |
| `website/` | React site for **cardioriskai.com** |
| `chat_bot.py` | Conversational AI that feeds the model |
| `DEPLOY.md` | How to put the site on the real domain |
| `train_model.py` | Retrain if you add `data/heart.csv` |
| `evaluate_model.py` | Makes accuracy charts for your poster |

---

## CardioRiskAi.com website (recommended)

1. Install [Node.js](https://nodejs.org) (for building the site).
2. **Double-click `RUN_WEBSITE.bat`.**
3. Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.
4. Chat with the assistant — type **start** and answer the questions.

See **`DEPLOY.md`** to connect the real domain **cardioriskai.com**.

---

## Streamlit demo (simpler, no website build)

1. Open this folder in File Explorer.
2. **Double-click `RUN_ME.bat`.**
3. Wait for “Installing packages” (first time only).
4. Your browser opens the **Heart Risk Checker**.
5. Fill in the boxes → click **Check risk**.

To stop: close the black window or press `Ctrl+C` in it.

---

## If you want the API too (optional)

1. Double-click **`RUN_API.bat`** (leave that window open).
2. Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in a browser.
3. Try **POST /predict** or visit [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) to see if the model loaded.

If port 8000 is busy, edit `RUN_API.bat` and change `8000` to `8001`.

---

## Manual commands (PowerShell)

```powershell
cd "c:\Users\matth\OneDrive - Fort Bend Independent School District\Desktop\Heart_AI_Project"
python -m pip install -r requirements.txt
python -m streamlit run ui.py
```

API:

```powershell
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

---

## Retrain or evaluate (when you have data)

1. Put your CSV at **`data/heart.csv`** with columns: `Age`, `Sex`, `ChestPain`, … `Thal`, and label `HeartDisease` (0/1) or `target`.
2. Train: `python train_model.py`
3. Evaluate (poster charts): `python evaluate_model.py`
4. Open **`reports/confusion_matrix.png`** and **`reports/model_metrics.json`** for your presentation.

---

## Input cheat sheet (for the form)

| Field | Meaning (simple) |
|-------|------------------|
| Age | How old the patient is |
| Sex | 0 = female, 1 = male (dataset coding) |
| ChestPain | Chest pain category 0–3 |
| SystolicBP | Top blood pressure number |
| Cholesterol | Cholesterol level |
| FastingBS | High blood sugar when fasting? 0/1 |
| RestingECG | ECG result category 0–2 |
| MaxHR | Highest heart rate in test |
| ExerciseAngina | Chest pain during exercise? 0/1 |
| Oldpeak | ST depression measure |
| Slope | ST segment slope 0–2 |
| NumVessels | Vessels seen on scan 0–3 |
| Thal | Blood disorder test 1–3 |

Use the same coding as the dataset you trained on.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| “Python is not installed” | Install from [python.org](https://www.python.org/downloads/) — check “Add Python to PATH” |
| Model won’t load | Make sure `cardio_rf_model.pkl` and `cardio_scaler.pkl` are in this folder |
| Port already in use | Close other servers or use port 8001 in `RUN_API.bat` |
| sklearn version warning | Usually safe to ignore; your model still runs. Re-save `.pkl` files after retraining if you upgrade sklearn. |

---

## License / ethics

For educational use. Do not present this as a real clinical tool.
