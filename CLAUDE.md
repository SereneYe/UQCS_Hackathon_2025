# Claude Code Configuration

This file configures Claude Code to help with PR reviews and code assistance for this React + FastAPI project.

## Project Structure
- **Frontend**: React with TypeScript, Vite, TailwindCSS, and shadcn/ui components
- **Backend**: FastAPI with SQLAlchemy, Google Cloud TTS integration

## Build and Test Commands

### Frontend (React/TypeScript)
```bash
cd frontend
npm install
npm run build
npm run lint
```

### Backend (FastAPI/Python)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Code Quality Rules

### General
- Follow existing code patterns and conventions
- Maintain TypeScript strict mode compliance
- Ensure all imports are properly organized
- No hardcoded secrets or credentials in code
- Keep components focused and reusable

### Frontend Specific
- Use shadcn/ui components consistently
- Follow React best practices (hooks, functional components)
- Maintain proper TypeScript typing
- Use TailwindCSS for styling
- Implement proper error handling and loading states

### Backend Specific
- Follow FastAPI conventions for route definitions
- Use Pydantic models for request/response validation
- Implement proper error handling with HTTP status codes
- Maintain database models with SQLAlchemy
- Secure API endpoints appropriately

## PR Review Focus Areas
- Security vulnerabilities and credential exposure
- Performance optimizations
- Code maintainability and readability
- Proper error handling
- Type safety (TypeScript/Pydantic)
- Component reusability (React)
- API design consistency (FastAPI)
- Database query efficiency
- Test coverage and quality

## Dependencies
- Keep dependencies up to date
- Avoid unnecessary dependencies
- Use peer dependencies appropriately for React components
- Maintain Python package compatibility