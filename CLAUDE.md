# Project Overview

This is a full-stack application with React frontend and FastAPI backend.

## Tech Stack
- **Frontend**: React, TypeScript, Vite, TailwindCSS, shadcn/ui
- **Backend**: FastAPI, SQLAlchemy, Python, Google Cloud TTS

## Build Commands

Frontend:
```bash
cd frontend && npm run build && npm run lint
```

Backend:
```bash
cd backend && python -m uvicorn app.main:app --reload
```

## Testing Commands

Frontend:
```bash
cd frontend && npm run lint
```

Backend:
```bash
cd backend && python -m pytest
```

## Code Standards

- Follow existing patterns and conventions
- Use TypeScript for type safety
- Implement proper error handling
- No hardcoded credentials
- Use shadcn/ui components for UI
- Follow FastAPI best practices
- Maintain SQLAlchemy model consistency