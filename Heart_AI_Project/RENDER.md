# Deploy on Render.com

Use these values in **New Web Service** (or use the included `render.yaml` Blueprint).

## Render form settings

| Field | Value |
|-------|--------|
| **Language** | Python 3 |
| **Branch** | `main` |
| **Root Directory** | *(leave blank)* or `./` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app:app --host 0.0.0.0 --port $PORT` |

Alternative start command (Gunicorn + Uvicorn workers):

```bash
gunicorn app:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

## Environment variables

| Key | Value |
|-----|--------|
| `PYTHON_VERSION` | `3.12.0` |
| `CORS_ORIGINS` | `https://cardioriskai.com,https://www.cardioriskai.com,https://YOUR-SERVICE.onrender.com` |

Replace `YOUR-SERVICE` with your actual Render URL (e.g. `cardioriskai-com`).

## Files that must be in GitHub

Push these to your repo or the deploy will fail:

- `app.py`, `chat_bot.py`, `data_pipeline.py`
- `requirements.txt`
- `cardio_rf_model.pkl`, `cardio_scaler.pkl`
- `model_metrics.json`, `medical_glossary.json`
- `website/dist/` (entire folder — the built website)

## Custom domain (cardioriskai.com)

1. In Render → your service → **Settings** → **Custom Domains** → add `cardioriskai.com` and `www.cardioriskai.com`
2. At your domain registrar, add the DNS records Render shows you (usually CNAME to `*.onrender.com`)
3. Wait for SSL (automatic)

## After deploy — test

- `https://YOUR-SERVICE.onrender.com/` — homepage
- `https://YOUR-SERVICE.onrender.com/api/health` — should show `"model_loaded": true`
- Chat → type `start`

## Free tier note

Render free instances **sleep after ~15 minutes** of no traffic. The first visit may take 30–60 seconds to wake up.
