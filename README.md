# TalentForge — Interview Management & Preparation Platform

> End-to-end platform for managing technical interviews and helping candidates prepare through structured practice, AI-assisted mock interviews, resume intelligence, and personalized preparation.

**[🚀 Live Demo](https://talentforge-platform.vercel.app/)** · **[GitHub](https://github.com/kamalsharma001/TalentForge)**

---

## Overview

TalentForge is a full-stack technical interview platform that combines **interview management for hiring teams** with **interview preparation for candidates**.

The platform supports the complete interview workflow:

```text
Recruiter Request ➔ Interviewer Matching ➔ Scheduling ➔ Technical Interview ➔ Evaluation ➔ Recruiter Review ➔ Candidate Feedback
```

Alongside the hiring workflow, candidates get a dedicated preparation environment to build interview readiness through personalized practice, resume-aware preparation, and adaptive AI mock interviews.

---

## Two Core Pillars

### Interview Management

TalentForge provides a structured workflow for recruiters and interviewers to coordinate and evaluate technical assessments:

* **Recruiter interview requests** — Create and manage interview requests across candidate pipelines.
* **Interviewer assignment & matching** — Smart-match interviewers based on skills and availability.
* **Availability & scheduling** — Timezone-aware slot management for seamless interview booking.
* **Lifecycle tracking** — Monitor interview stages from initial request to published report.
* **Structured evaluations** — Multi-dimensional scoring with written feedback and hiring recommendations.
* **Recruiter review & publishing** — Approval gates before releasing reports and feedback to candidates.
* **Role-based access control** — Granular permissions across Admin, Recruiter, Interviewer, and Candidate roles.

### Candidate Interview Preparation

Candidates have a dedicated preparation workspace designed around their target role, technology stack, and background:

* **Adaptive AI Mock Interviews** — Practice technical interviews with **Alex**, an AI interviewer that builds competency-focused blueprints, asks adaptive follow-ups, rotates topics, and tracks session duration.
* **Evidence-Based Evaluation** — Generates post-interview scorecards with competency scores, supporting transcript evidence, strengths, weaknesses, and improvement areas.
* **Resume Intelligence** — Upload PDF or DOCX resumes to extract key technical experience and anchor mock interview questions to verified claims.
* **Practice Question Studio** — Curated technical question practice filtered by target role, tech stack, difficulty, and topic.

---

## Key Features

| Capability | Description | Pillar |
|---|---|---|
| **Interview Pipeline** | Request creation, interviewer assignment, and status lifecycle tracking | Management |
| **Smart Scheduling** | Interviewer availability management and timezone-aware slot booking | Management |
| **Structured Evaluations** | Multi-dimensional rubrics, written notes, and hiring recommendations | Management |
| **Report Publishing** | Recruiter review workflows and candidate feedback distribution | Management |
| **AI Mock Interviews** | Multi-turn, adaptive technical sessions with server-side duration tracking | Preparation |
| **Resume Intelligence** | Resume parsing (PDF/DOCX) and claim-aware question personalization | Preparation |
| **Evidence Scorecards** | Transcript-backed competency evaluation with concrete recommendations | Preparation |
| **Question Studio** | Targeted technical practice across roles, stacks, and difficulty levels | Preparation |
| **Auth & Security** | JWT authentication, Supabase Google OAuth, and strict RBAC isolation | Platform |

---

## Application Roles

| Role | Responsibilities |
|---|---|
| **Admin** | User management and platform oversight |
| **Recruiter** | Create interviews, assign interviewers, manage candidates, and publish reports |
| **Interviewer** | Manage availability, conduct interviews, and submit evaluations |
| **Candidate** | Track interviews, view feedback, prepare, practice, and run AI mock interviews |

---

## System Architecture

```text
┌──────────────────────┐
│    React Frontend    │
│   Vite + Tailwind    │
└──────────┬───────────┘
           │ REST / HTTPS
           ▼
┌──────────────────────┐
│   FastAPI Backend    │
│                      │
│    Authentication    │
│ Interview Management │
│      Scheduling      │
│     Evaluations      │
│Candidate Preparation │
│  AI Mock Interviews  │
└───────┬───────┬──────┘
        │       │
┌───────┘       └────────┐
▼                        ▼
┌──────────────────┐  ┌──────────────────┐
│    PostgreSQL    │  │  Google Gemini   │
│  SQLAlchemy ORM  │  │    AI Engine     │
└──────────────────┘  └──────────────────┘
```

---

## Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, Vite, React Router, Tailwind CSS, Axios |
| **Backend** | Python, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic, PyJWT, bcrypt |
| **Database** | PostgreSQL (Supabase) |
| **AI & Processing** | Google Gemini (Google GenAI SDK), pypdf, python-docx |
| **Authentication** | Native JWT, Supabase Google OAuth, Role-Based Access Control |
| **Deployment** | Vercel (Frontend), Render (Backend), Supabase (Database) |

---

## Project Structure

```text
TalentForge/
├── backend/
│   ├── app/
│   │   ├── routers/          # Authentication, interviews, scheduling, reports, AI preparation
│   │   ├── models/           # Users, interviews, candidates, evaluations, resumes, AI sessions
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   ├── services/         # Business logic, scheduling, evaluation & AI services
│   │   ├── templates/        # AI interview and evaluation prompt templates
│   │   ├── utils/            # Security, validation, errors & shared utilities
│   │   ├── config.py         # Environment configuration
│   │   ├── database.py       # SQLAlchemy database setup
│   │   ├── dependencies.py   # Authentication, authorization & database dependencies
│   │   └── main.py           # FastAPI application entrypoint
│   ├── migrations/           # Alembic database migrations
│   ├── requirements.txt      # Backend dependencies
│   ├── run.py                # Development server entrypoint
│   └── alembic.ini           # Alembic configuration
│
└── frontend/
    ├── src/
    │   ├── components/       # Reusable UI, layouts & interview components
    │   ├── context/          # Authentication & application state
    │   ├── pages/
    │   │   ├── auth/         # Authentication flows
    │   │   ├── recruiter/    # Interview management workflows
    │   │   ├── interviewer/  # Scheduling & evaluation workflows
    │   │   ├── candidate/    # Interview tracking & preparation
    │   │   ├── admin/        # Platform administration
    │   │   └── shared/       # Shared interview, report & notification views
    │   ├── services/         # API clients and service integrations
    │   ├── App.jsx           # Application routing
    │   └── main.jsx          # React entrypoint
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── tailwind.config.js
```

---

## Getting Started

### Prerequisites

* Python 3.11+
* Node.js 18+
* PostgreSQL
* Google Gemini API key

### Backend

```bash
cd backend
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:create_app --factory --reload
```

* **Backend API:** `http://localhost:8000`
* **API Documentation:** `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

* **Frontend:** `http://localhost:5173`

---

## Environment Variables

### Backend (`backend/.env`)

```env
DATABASE_URL=
JWT_SECRET_KEY=
GEMINI_API_KEY=
GEMINI_MODEL=
FRONTEND_URL=

# Optional — Google OAuth
SUPABASE_URL=
SUPABASE_JWT_AUDIENCE=
```

### Frontend (`frontend/.env`)

```env
VITE_API_URL=
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
```

> **Note:** Backend secrets (`GEMINI_API_KEY`, `JWT_SECRET_KEY`, `DATABASE_URL`) are never exposed to the client.

---

## API Modules

| Module | Purpose |
|---|---|
| `/api/auth` | Authentication and session management |
| `/api/users` | User profiles and role administration |
| `/api/interviews` | Interview requests, assignment, and status lifecycle |
| `/api/scheduling` | Interviewer availability and slot matching |
| `/api/reports` | Multi-dimensional evaluations and report publishing |
| `/api/notifications` | In-app alerts for scheduling and report updates |
| `/api/ai-prep` | Resume analysis, practice studio, and AI mock interviews |

---

## Deployment

| Component | Platform | Configuration |
|---|---|---|
| **Frontend** | [Vercel](https://vercel.com/) | Single-page application build (`npm run build`) |
| **Backend** | [Render](https://render.com/) | FastAPI web service with Uvicorn |
| **Database** | [Supabase](https://supabase.com/) | Managed PostgreSQL with Alembic migrations |
| **AI Inference** | [Google Gemini](https://ai.google.dev/) | Flash-Lite model via official Google GenAI SDK |

**[🚀 Live Application](https://talentforge-platform.vercel.app/)**

---

## Author

**Kamal Sharma**  
[GitHub Profile](https://github.com/kamalsharma001)

---

*TalentForge — Interview Management & Preparation Platform*
