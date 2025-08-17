# Full-Stack App (React + FastAPI)

This repository contains:
- Frontend: React + Vite
- Backend: FastAPI (Python), running on Uvicorn

Follow this guide to run both services locally.

## AI-Powered Development

This project was developed using cutting-edge AI tools for brainstorming, design, and implementation:

### AI Models Used
- **Claude Sonnet 4** - Advanced reasoning and code generation
- **ChatGPT-4** - Problem solving and architectural decisions

### AI Development Tools
- **Claude Code** - Interactive CLI for real-time code assistance and debugging
- **ChatGPT** - Ideation, brainstorming, and technical consultation  
- **Lovable** - AI-powered frontend development and UI/UX design

These AI tools significantly accelerated development by providing intelligent code suggestions, architectural guidance, and rapid prototyping capabilities.

## Tech Stack

### Frontend
- **React** - Modern UI library for building interactive user interfaces
- **TypeScript** - Type-safe JavaScript for better development experience
- **Vite** - Fast build tool and development server
- **TailwindCSS** - Utility-first CSS framework for rapid styling
- **shadcn/ui** - High-quality accessible UI components

### Backend
- **FastAPI** - High-performance Python web framework with automatic API documentation
- **SQLAlchemy** - Python SQL toolkit and Object-Relational Mapping (ORM)
- **Uvicorn** - Lightning-fast ASGI server implementation
- **Pydantic** - Data validation using Python type annotations

### Cloud Services & APIs
- **Google Cloud Storage (GCS)** - Scalable object storage for file uploads and management
- **Google Cloud Text-to-Speech** - AI-powered speech synthesis
- **VEO3** - Advanced AI video generation service for creating high-quality videos from text prompts

### Database
- **SQLite** - Lightweight, serverless database for development

### Development Tools
- **Python 3.11+** - Modern Python runtime
- **Node.js & npm** - JavaScript runtime and package management
- **Git** - Version control system

## Running Image

<img width="2994" height="2510" alt="homepage" src="https://github.com/user-attachments/assets/ad939745-07ac-4dd0-ba86-b7eba1ea471e" />

<img width="2994" height="2606" alt="upload" src="https://github.com/user-attachments/assets/6610afb8-9686-40be-a688-33a4a5bd2131" />

<img width="2994" height="2428" alt="upload2" src="https://github.com/user-attachments/assets/a67a2ad4-4cd4-48be-ba54-ee87e8629c99" />

<img width="2994" height="3514" alt="video_collection" src="https://github.com/user-attachments/assets/cb90aed2-6298-4fed-b943-fdf1a68d086f" />

## Sample Generation Videos

https://github.com/user-attachments/assets/39e8cb4b-948d-446d-9099-d123e9c093a5

https://github.com/user-attachments/assets/df342521-01f1-454a-9c8e-c11fc024dab7

https://github.com/user-attachments/assets/7abf5bf8-7bc7-40e3-b8c0-e3ceae049757

https://github.com/user-attachments/assets/fc982a8b-b7f5-4292-9cec-337f5f7b0db8

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

⚠️ **IMPORTANT: Google Cloud TTS Setup Required**

The backend includes Text-to-Speech functionality that requires Google Cloud credentials:

1. **Create Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable the "Cloud Text-to-Speech API"

2. **Create Service Account:**
   - Go to "IAM & Admin" > "Service Accounts"
   - Create service account with "Cloud Text-to-Speech User" role
   - Download the JSON key file

3. **Setup Credentials:**
   ```bash
   # Create credentials directory
   mkdir backend/credentials
   
   # Place your JSON key file in credentials directory
   # Example: backend/credentials/tts-credential.json
   
   # Copy environment template
   cp backend/.env.example backend/.env
   
   # Edit .env file to point to your credential file:
   # GOOGLE_APPLICATION_CREDENTIALS=credentials/tts-credential.json
   ```

**Without proper credentials, TTS endpoints will return 500 errors.**

### Backend Setup:

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

## API Endpoints

The backend provides the following API categories:

- **Users** (`/users/`) - User management
- **Videos** (`/videos/`) - Video processing 
- **Audio** (`/audio/`) - Text-to-Speech functionality ⚠️ *Requires Google Cloud credentials*

Visit `http://localhost:8000/docs` for interactive API documentation.

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
