# Full-Stack App (React + FastAPI)

This repository contains:
- Frontend: React + Vite
- Backend: FastAPI (Python), running on Uvicorn

Follow this guide to run both services locally.

---

## Prerequisites

- Node.js LTS and npm
- Python 3.10+ (3.11 recommended)
- Git
- macOS/Linux shell or Windows PowerShell

---

## Project Structure

- `frontend/` — Vite React app (dev server defaults to http://localhost:8080)
- `backend/` — FastAPI app (`app/main.py`, dev server at http://127.0.0.1:8000)
- `.env.example` — Sample environment variables (copy to `.env` if needed)
---

## Environment Variables (optional)

If your app needs environment variables:
1. Copy `.env.example` to `.env` in the project root (or into `frontend/` and/or `backend/` if you scope them per app).
2. Fill in any required values.
---

## Backend: Setup and Run (FastAPI)

From the repo root:

macOS/Linux:
The dev server will print a local URL (typically http://localhost:5173).

---

## Run Frontend and Backend Together

1. Terminal 1 (backend):
   - macOS/Linux:
     ```bash
     cd backend
     source .venv/bin/activate
     fastapi dev app/main.py
     ```
   - Windows PowerShell:
     ```powershell
     cd backend
     .venv\Scripts\Activate.ps1
     fastapi dev app/main.py
     ```
2. Terminal 2 (frontend):
   ```bash
   cd frontend
   npm run dev
   ```

## Common Tasks
- Update Python dependencies and lock them:
  ```bash
  # inside backend virtual environment
  pip install <new-package>
  pip freeze > requirements.txt
  ```
  Commit the updated `backend/requirements.txt`.

- Clean install (backend):
  ```bash
  rm -rf backend/.venv
  cd backend
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```

- Clean install (frontend):
  ```bash
  cd frontend
  rm -rf node_modules
  npm install
  ```

## What to Commit

- Commit `backend/requirements.txt` so others can install the exact same Python packages.
- Do not commit virtual environments (`backend/.venv/`) or `frontend/node_modules/`.

---

## Quick Start (Copy-Paste)
macOS/Linux:
```
bash
# Backend
cd backend python3 -m venv .venv source .venv/bin/activate pip install --upgrade pip pip install -r requirements.txt fastapi dev app/main.py
``` 

In another terminal:
```
bash
# Frontend
cd frontend npm install npm run dev
``` 

Windows PowerShell:
```
powershell
# Backend
cd backend python -m venv .venv .venv\Scripts\Activate.ps1 python -m pip install --upgrade pip pip install -r requirements.txt fastapi dev app/main.py
``` 

In another terminal:
```
powershell
# Frontend
cd frontend npm install npm run dev
