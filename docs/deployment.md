# CertiNexus AI — Deployment & Operations Guide

**Course**: 20MSSL12 Machine Learning Lab  
**Target Environment**: Production Linux / Windows / Docker Containerized  

---

## 1. System Requirements & Prerequisites

- **Python**: Version 3.10, 3.11, or 3.12 (64-bit)
- **Node.js**: Version 18.0+ or 20.0+ LTS
- **Package Managers**: `pip` (v23+), `npm` (v9+)
- **System Memory**: 4 GB RAM minimum (8 GB recommended for OCR image processing)
- **Disk Space**: ~1.5 GB for dependencies, ML models, and storage

---

## 2. Local Development Quickstart

### 2.1 Backend Setup
```bash
# 1. Create and activate Python virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy environment configuration
cp .env.example .env

# 4. Start FastAPI server with live reloading
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
The interactive OpenAPI/Swagger documentation will be available at: `http://localhost:8000/docs`.

### 2.2 Frontend Setup
```bash
# 1. Navigate to web directory
cd web

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev
```
The React frontend will be accessible at: `http://localhost:5173`.

---

## 3. Environment Configuration (`.env`)

```ini
# Application
APP_NAME=CertiNexus AI
APP_ENV=production
SECRET_KEY=change-this-to-a-secure-random-64-character-hex-string
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Database
# Local SQLite default:
DATABASE_URL=sqlite:///./storage/certinexus.db
# Or PostgreSQL for production:
# DATABASE_URL=postgresql://user:password@localhost:5432/certinexus

# Storage
STORAGE_PATH=./storage/uploads
MAX_UPLOAD_SIZE_MB=10

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,https://certinexus.ai

# ML Model Paths
ML_MODEL_DIR=./ml/models/production
```

---

## 4. Production Build & Static Serving

To build the optimized client bundle:
```bash
cd web
npm run build
```
This produces optimized production assets inside `web/dist/`. In production, these static files can be served directly by Nginx, Caddy, Cloudflare Pages, or mounted to FastAPI:

```python
# In backend/app/main.py:
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="web/dist", html=True), name="static")
```

---

## 5. Docker Deployment

### 5.1 Dockerfile (Backend & ML Engine)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY ml/ ./ml/
COPY dataset/ ./dataset/

ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 5.2 Docker Compose Orchestration (`docker-compose.yml`)
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./storage/certinexus.db
      - SECRET_KEY=prod-secret-key-replace-me
      - STORAGE_PATH=/app/storage/uploads
    volumes:
      - certinexus-storage:/app/storage

  frontend:
    build:
      context: ./web
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - backend

volumes:
  certinexus-storage:
```

---

## 6. Verification & Health Monitoring

- **Health Check Endpoint**: `GET /api/health` returns `{"status": "healthy", "service": "CertiNexus AI"}`.
- **Admin Research Endpoint**: `GET /api/admin/model-performance` returns live production classification accuracy and confusion matrix from the loaded model.
