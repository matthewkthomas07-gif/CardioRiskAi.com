# Build frontend
FROM node:22-alpine AS web
WORKDIR /web
COPY website/package.json website/package-lock.json* ./
RUN npm install
COPY website/ ./
RUN npm run build

# Python API + static site
FROM python:3.12-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py chat_bot.py ./
COPY cardio_rf_model.pkl cardio_scaler.pkl ./
COPY --from=web /web/dist ./website/dist

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
