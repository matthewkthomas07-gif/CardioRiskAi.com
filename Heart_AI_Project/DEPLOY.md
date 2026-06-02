# Deploy CardioRiskAi.com

This project serves **both** the website and the AI API from one server after you build the frontend.

## Option A — One server (recommended)

Good for: Railway, Render, Fly.io, a VPS, or Docker.

### 1. Build the website

```powershell
cd website
npm install
npm run build
cd ..
```

### 2. Run everything

```powershell
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000` — you should see CardioRisk AI and the chat bot.

### 3. Docker (production)

```bash
docker compose up --build -d
```

### 4. Point your domain

At your DNS provider (where you bought **cardioriskai.com**):

| Type | Name | Value |
|------|------|--------|
| A | `@` | Your server IP |
| CNAME | `www` | `cardioriskai.com` or your host URL |

On your host (Railway, Render, etc.), add custom domains:

- `cardioriskai.com`
- `www.cardioriskai.com`

Enable HTTPS (Let's Encrypt) in the hosting dashboard.

---

## Option B — Split hosting

| Part | Host | Notes |
|------|------|--------|
| Website | Vercel / Netlify | Deploy `website/` folder |
| API | Railway / Render | Deploy repo root (Python) |

Set environment variable on Vercel:

```
VITE_API_URL=https://api.cardioriskai.com
```

Deploy API separately and set `CORS_ORIGINS` to your Vercel URL.

---

## Local development (two terminals)

**Terminal 1 — API**

```powershell
python -m uvicorn app:app --reload --port 8000
```

**Terminal 2 — Website (hot reload)**

```powershell
cd website
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) — Vite proxies `/api` to port 8000.

---

## Verify production

1. `https://cardioriskai.com` loads the landing page  
2. Chat shows “Model online”  
3. Type **start** and complete the questions  
4. `https://cardioriskai.com/api/health` returns `"model_loaded": true`
