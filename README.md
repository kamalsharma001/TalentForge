# TalentForge — Interview Management & Preparation

> End-to-end technical interview management & preparation platform — from scheduling and live interviews to AI-powered mock interviews, personalized preparation, candidate workflows, and evidence-based interview evaluation.

**[🚀 Live Demo](https://talentforge-platform.vercel.app/)** &nbsp;·&nbsp; **[GitHub](https://github.com/kamalsharma001/TalentForge)**

---

## What is TalentForge?

TalentForge connects recruiters, interviewers, and candidates on a single platform. Recruiters request and manage interviews, interviewers submit scored reports, and candidates track their progress — with AI-driven interview preparation, structured time-aware mock interviews with Alex (the AI technical interviewer), resume intelligence extraction, and a personalized practice question studio.

---

## Features

| | Feature | Description |
|---|---|---|
| 🔐 | Role-based access | Four roles — `admin`, `recruiter`, `interviewer`, `candidate` — each with a dedicated dashboard |
| 📋 | Interview management | Create, assign, schedule, and track interviews through a full status lifecycle |
| 📅 | Smart scheduling | Interviewers publish availability slots; recruiters use smart-match to find the right fit |
| 📝 | Scored reports | Multi-dimension scoring and written reports, published to candidates by recruiters |
| 🤖 | AI feedback | Generates summaries, strengths, and weaknesses from interview scores |
| 🔔 | Notifications | In-app notification system with unread counts and mark-all-read |
| 🎯 | AI Mock Interviews | Multi-turn adaptive technical interviews powered by Gemini with time-tracking, competency blueprints, topic rotation, and verbatim transcript evidence scorecards |
| 📄 | Resume Intelligence | In-memory text extraction (PDF, DOCX) and Gemini claim analysis with automatic local fallback |
| 📚 | Practice Questions | Question studio with personalized recommendations filterable by role, difficulty, and tech stack |

---

## Tech stack

**Backend** — FastAPI · PostgreSQL · SQLAlchemy ORM · Alembic · PyJWT · Google Gemini GenAI SDK · Pydantic v2 · Uvicorn / Gunicorn

**Frontend** — React 18 · Vite 5 · React Router 6 · Axios · Tailwind CSS 3 · Supabase Auth (Google OAuth)

---

## Project structure

```
TalentForge/
├── backend/
│   ├── app/
│   │   ├── routers/           # FastAPI APIRouter endpoints
│   │   ├── models/            # SQLAlchemy declarative models
│   │   ├── schemas/           # Pydantic v2 validation models
│   │   ├── services/          # Decoupled business logic (AiPrepService, LLMService, etc.)
│   │   ├── utils/             # Errors, pagination, security, validators
│   │   ├── main.py            # FastAPI app factory and router registration
│   │   ├── config.py          # App settings mapping environment variables
│   │   ├── database.py        # SQLAlchemy engine and SessionLocal dependency
│   │   └── dependencies.py    # Common Depends() helpers (JWT extraction, RoleChecker)
│   ├── migrations/            # Alembic database migrations
│   ├── alembic.ini            # Alembic configuration
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example           # Backend environment template
│   └── run.py                 # Backend launch helper
│
└── frontend/
    ├── src/
    │   ├── components/        # Layout, auth guards, shared UI
    │   ├── context/           # AuthContext (JWT & Supabase OAuth state)
    │   ├── hooks/             # Custom React hooks
    │   ├── pages/             # Route-level page components (candidate, recruiter, interviewer)
    │   ├── services/          # Axios API modules (api.js, aiPrepService.js, etc.)
    │   └── utils/             # Shared formatting and error parsing helpers
    ├── .env.example           # Frontend environment template
    ├── vite.config.js         # Vite configuration and dev proxy
    └── package.json           # Frontend dependencies
```

---

## Getting started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL database (local or [Supabase](https://supabase.com))
- Google Gemini API key ([Google AI Studio](https://aistudio.google.com/))
- *(Optional)* Supabase project for Google OAuth
- *(Optional)* Cloudinary account for CDN media hosting

### Backend Setup

```bash
cd TalentForge/backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env              # Fill in your database and Gemini API key

# Run database migrations
alembic upgrade head

# Start FastAPI server
uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --reload
```

Backend API runs at `http://localhost:8000` (API documentation at `http://localhost:8000/docs`).

### Frontend Setup

```bash
cd TalentForge/frontend

# Install dependencies
npm install

# Configure environment (optional in dev, proxy defaults to http://localhost:8000)
cp .env.example .env

# Start Vite development server
npm run dev
```

Frontend runs at `http://localhost:5173`.

---

## Environment Variables

### Local Development

#### Backend (`backend/.env`)

| Variable | Required? | Default / Example | Purpose |
|---|---|---|---|
| `FLASK_ENV` | Optional | `development` | Environment mode (`development`, `production`). |
| `FRONTEND_URL` | Optional | `http://localhost:5173` | Allowed origin for CORS and client redirection. |
| `DATABASE_URL` | **Required** | `postgresql://user:pass@host:5432/db` | PostgreSQL database connection string. |
| `JWT_SECRET_KEY` | **Required** | `your-jwt-secret-key-change-in-production` | Secret for signing backend access and refresh JWTs. |
| `GEMINI_API_KEY` | **Required** | `AIzaSy...` | Google Gemini API key for AI Prep & Mock Interviews. |
| `GEMINI_MODEL` | Optional | `gemini-3.5-flash-lite` | Gemini model pinned for inference. |
| `SUPABASE_URL` | Cond. Required | `https://your-project.supabase.co` | Required only if testing "Continue with Google" OAuth. |
| `SUPABASE_JWT_AUDIENCE` | Optional | `authenticated` | Expected audience claim for Supabase Google tokens. |

#### Frontend (`frontend/.env`)

| Variable | Required? | Default / Example | Purpose |
|---|---|---|---|
| `VITE_API_URL` | Optional in dev | *(leave blank in dev)* | Empty in dev to use Vite proxy (`/api` → `http://localhost:8000`). |
| `VITE_SUPABASE_URL` | Cond. Required | `https://your-project.supabase.co` | Supabase endpoint for Google OAuth handshake. |
| `VITE_SUPABASE_ANON_KEY` | Cond. Required | `eyJhbGci...` | Public client anon key for browser OAuth. |

---

### Production Deployment

#### Backend — Render / Railway

The following variables **MUST** be configured in your hosting environment dashboard (e.g. Render Web Service Environment Settings):

```env
# Application
FLASK_ENV=production
FRONTEND_URL=https://your-production-frontend.vercel.app

# Database
DATABASE_URL=postgresql://user:password@your-pooler-host.supabase.com:6543/postgres

# Authentication
JWT_SECRET_KEY=generate_a_secure_64_character_hex_key

# Google Gemini AI Engine
GEMINI_API_KEY=your_production_gemini_api_key
GEMINI_MODEL=gemini-3.5-flash-lite

# Supabase Auth (Required if "Continue with Google" is enabled)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_JWT_AUDIENCE=authenticated
```

#### Frontend — Vercel

The following variables **MUST** be configured in Vercel Project Settings → Environment Variables:

```env
# Backend API Base URL (DO NOT add trailing slash, DO NOT append /api)
# api.js automatically appends '/api' to VITE_API_URL
VITE_API_URL=https://your-backend-api.onrender.com

# Supabase Client Handshake (Required if "Continue with Google" is enabled)
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_supabase_public_anon_key
```

---

### Optional Services

#### Cloudinary CDN Storage
* **Status:** **OPTIONAL** for the current Candidate AI Mock Interview workflow.
* **Why it is optional:** When Cloudinary is not configured or offline, `AiPrepService.upload_and_analyze_resume` catches the error, assigns a local database fallback identifier, and extracts text and Gemini intelligence with 100% success in memory.
* **When to configure:** Only if you wish to store raw PDF files or video recordings on Cloudinary's remote CDN.
```env
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

#### SMTP Email Dispatch
* **Status:** **OPTIONAL**.
* **Why it is optional:** When SMTP variables are not set, `NotificationService` skips email dispatch and creates in-app notification records without errors.
* **When to configure:** If you wish to send transactional emails when human interviews are scheduled or reports published.
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=notifications@yourdomain.com
MAIL_PASSWORD=your_app_specific_password
MAIL_DEFAULT_SENDER=noreply@yourdomain.com
```

---

### Removed / Deprecated Variables

The following variables were audited and confirmed **unused** by runtime application code:

1. **`HF_API_TOKEN`**: Deprecated. Legacy HuggingFace integration was fully replaced by Google Gemini (`gemini-3.5-flash-lite`).
2. **`SUPABASE_JWT_SECRET`**: Deprecated. Backend token verification validates Supabase tokens using RS256/ES256 via the public JWKS endpoint (`SUPABASE_URL/auth/v1/.well-known/jwks.json`), eliminating the need for a symmetric JWT secret.
3. **`SECRET_KEY`**: Deprecated. Inherited from legacy Flask boilerplate. All session, authentication, and token handling in FastAPI strictly uses `JWT_SECRET_KEY`.

---

### Security Rules

> [!CAUTION]
> **Strict Secret Isolation Policy**
> * **Never expose `GEMINI_API_KEY` to the frontend.** All AI generation happens server-side via `LLMService`.
> * **Never expose `JWT_SECRET_KEY` to the frontend.** Token creation and verification are strictly backend operations.
> * **Never expose `DATABASE_URL` to the frontend.**
> * **Never expose `CLOUDINARY_API_SECRET` or `MAIL_PASSWORD` to the frontend.**
> * **Never prefix backend secrets with `VITE_`.** Any variable prefixed with `VITE_` is baked directly into client-side JavaScript bundles by Vite during `npm run build` and is publicly readable by anyone inspecting browser network traffic.
> * `VITE_*` variables must contain **only public browser-safe configuration** (`VITE_API_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`).

---

### Production Deployment Checklist

Before launching to production, verify:

- [ ] `DATABASE_URL` is configured on Render/Railway with a valid PostgreSQL pooler connection.
- [ ] A cryptographically strong `JWT_SECRET_KEY` is generated (`openssl rand -hex 32`).
- [ ] `GEMINI_API_KEY` is configured and active.
- [ ] `GEMINI_MODEL=gemini-3.5-flash-lite` is configured.
- [ ] `FLASK_ENV=production` is set on the backend.
- [ ] `FRONTEND_URL` on Render points to your production Vercel domain.
- [ ] `VITE_API_URL` on Vercel points to your live Render backend URL **without** a trailing slash or `/api`.
- [ ] `SUPABASE_URL` and `VITE_SUPABASE_URL` match your Supabase project (if Google OAuth is enabled).
- [ ] `VITE_SUPABASE_ANON_KEY` is set on Vercel (if Google OAuth is enabled).
- [ ] Zero backend secrets (`GEMINI_API_KEY`, `JWT_SECRET_KEY`, `DATABASE_URL`) are present in Vercel or prefixed with `VITE_`.
- [ ] CORS configuration in `backend/app/main.py` permits your production Vercel domain.
- [ ] Frontend production build succeeds cleanly (`npm run build`).
- [ ] Backend starts cleanly and passes health check (`GET /health` → HTTP 200).

---

## API overview

Base URL: `https://<your-app>.onrender.com/api`

All authenticated endpoints require `Authorization: Bearer <access_token>`.

| Module | Base path | Key actions |
|---|---|---|
| Auth | `/api/auth` | register, login, refresh, Google OAuth, change-password |
| Users | `/api/users` | profile, admin user management, recruiter verification |
| Interviews | `/api/interviews` | create, assign, complete, cancel |
| Scheduling | `/api/scheduling` | availability slots, smart-match interviewers |
| Reports | `/api/reports` | submit, edit, publish |
| Notifications | `/api/notifications` | list, mark read, unread count |
| AI Prep & Mock | `/api/ai-prep` | prep plan, questions studio, structured mock interview, resume analysis |
| Mock Interviews | `/api/mock-interviews` | legacy solo mock sessions |
| Practice Questions | `/api/practice` | browse question bank by role, difficulty, category |

---

## Author

**Kamal Sharma**

[![GitHub](https://img.shields.io/badge/GitHub-kamalsharma001-181717?style=flat&logo=github)](https://github.com/kamalsharma001/TalentForge)

---

*Built with FastAPI · React · PostgreSQL*
