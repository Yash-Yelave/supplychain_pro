# ConstructProcure AI Deployment Guide

This guide covers how to deploy the FastAPI backend and the React+Vite frontend on separate platforms (e.g., Render for backend, Vercel/Netlify for frontend) and how to ensure they communicate properly via CORS and Environment Variables.

## Architecture
- **Backend:** FastAPI application running via Uvicorn. Exposes REST endpoints (`/procurement/*`) and a `/health` endpoint.
- **Frontend:** React application built with Vite. Consumes the backend APIs.

## 1. Backend Deployment (Render / Railway / VPS)

### Prerequisites
1. Ensure your `.env` variables are ready for the production environment.
2. A PostgreSQL database (e.g., Supabase) is required.

### Environment Variables
Configure the following in your deployment platform's environment settings:
```env
# Essential config
APP_ENV=production
DATABASE_URL=postgresql+psycopg://user:password@host:5432/dbname
FRONTEND_CORS_ORIGINS=https://your-production-frontend.com

# DeepSeek config
DEEPSEEK_API_KEY=your_api_key
```

*Note:* `FRONTEND_CORS_ORIGINS` is a comma-separated list of allowed origins. It **must** match your frontend's deployed URL exactly (no trailing slash).

### Startup Command
Depending on your platform, the startup command is:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
If deploying via Docker, use the equivalent `CMD` in your `Dockerfile`.

## 2. Frontend Deployment (Vercel / Netlify)

The frontend is a static Single Page Application (SPA).

### Prerequisites
1. Ensure the backend is deployed and you have its public URL (e.g., `https://api.yourdomain.com`).

### Environment Variables
Set the following environment variable in your frontend deployment platform (Vercel/Netlify):
```env
VITE_API_BASE_URL=https://api.yourdomain.com
```

### Build Settings
- **Framework Preset:** Vite (or React)
- **Build Command:** `npm run build`
- **Output Directory:** `dist`
- **Install Command:** `npm install`

## 3. Local Development Integration

When developing locally, you want the local frontend to talk to the local backend.

1. **Backend:**
   Ensure your `.env` has:
   ```env
   FRONTEND_CORS_ORIGINS=http://localhost:5173
   ```
   Run: `python -m uvicorn app.main:app --reload` (Runs on port 8000)

2. **Frontend:**
   Ensure `frontend/.env.development` has:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```
   Run: `npm run dev` (Runs on port 5173)

## Troubleshooting

### CORS Errors
If the frontend shows a CORS error in the browser console:
- Verify that the `FRONTEND_CORS_ORIGINS` on the backend matches the frontend's origin **exactly** (e.g., `https://my-app.vercel.app` - no trailing slash).
- Verify the backend has been redeployed after changing the environment variable.

### API Connection Refused / 404
- Ensure `VITE_API_BASE_URL` is set correctly in the frontend deployment.
- Verify the backend `/health` endpoint is reachable from your browser.
