# TalentForge

> End-to-end technical interview management platform — from scheduling and live interviews to AI-generated feedback and candidate practice.

**[🚀 Live Demo](https://talentforge-platform.vercel.app/)** &nbsp;·&nbsp; **[GitHub](https://github.com/kamalsharma001/TalentForge)**

---

## What is TalentForge?

TalentForge connects recruiters, interviewers, and candidates on a single platform. Recruiters request and manage interviews, interviewers submit scored reports, and candidates track their progress — with AI feedback summaries, mock interview sessions, and a role-based practice question bank built in.

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
| 🎥 | Recording upload | Interview recordings stored and linked via Cloudinary |
| 🎯 | Mock interviews | Candidate-initiated solo practice sessions with AI evaluation |
| 📚 | Practice questions | Question bank filterable by job role, difficulty, and category |

---

## Tech stack

**Backend** — Flask 3 · PostgreSQL · SQLAlchemy · Alembic · Flask-JWT-Extended · Marshmallow · Gunicorn

**Frontend** — React 18 · Vite 5 · React Router 6 · Axios · Tailwind CSS 3 · date-fns

---
## Project structure

```
TalentForge/
├── backend/
│   ├── app/
│   │   ├── auth/              # JWT routes + decorators
│   │   ├── users/             # User profile management
│   │   ├── interviews/        # Interview CRUD + lifecycle
│   │   ├── scheduling/        # Availability slots + smart match
│   │   ├── reports/           # Scored reports
│   │   ├── notifications/     # In-app notifications
│   │   ├── ai_feedback/       # AI summary generation
│   │   ├── mock_interviews/   # Mock interview sessions
│   │   ├── practice/          # Practice question bank
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Marshmallow schemas
│   │   ├── services/          # Business logic layer
│   │   └── utils/             # Errors, pagination, validators
│   ├── migrations/            # Alembic versions
│   └── requirements.txt
│
└── frontend/
    └── src/
        ├── components/        # Layout, auth guards, shared UI
        ├── context/           # AuthContext
        ├── hooks/             # Custom React hooks
        ├── pages/             # Route-level page components
        ├── services/          # Axios API modules
        └── utils/             # Shared helpers
```
---
## Getting started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL database (local or [Supabase](https://supabase.com))
- [Cloudinary](https://cloudinary.com) account
- OpenAI API key *(optional — a rule-based fallback is included)*

### Backend

```bash
cd TalentForge/backend

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env              # fill in your values

flask db upgrade
python run.py
```

API runs at `http://localhost:5000`.

### Frontend

```bash
cd TalentForge/frontend

npm install
echo "VITE_API_URL=http://localhost:5000/api" > .env.local
npm run dev
```

App runs at `http://localhost:5173`.

---

## Environment variables

Copy `backend/.env.example` to `backend/.env` and fill in the following:

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key

DATABASE_URL=postgresql://user:password@host:5432/talentforge

CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

OPENAI_API_KEY=your-openai-api-key       # optional

MAIL_SERVER=smtp.gmail.com               # optional
MAIL_PORT=587
MAIL_USERNAME=your@email.com
MAIL_PASSWORD=your-app-password

FRONTEND_URL=http://localhost:5173
```

> In production set `FLASK_ENV=production` and rotate all secret keys.

---

## API overview

Base URL: `https://<your-app>.onrender.com/api`

All authenticated endpoints require `Authorization: Bearer <access_token>`.

| Module | Base path | Key actions |
|---|---|---|
| Auth | `/api/auth` | register, login, refresh, change-password |
| Users | `/api/users` | profile, admin user management, interviewer approval |
| Interviews | `/api/interviews` | create, assign, complete, cancel |
| Scheduling | `/api/scheduling` | availability slots, smart-match interviewers |
| Reports | `/api/reports` | submit, edit, publish, AI generate |
| Notifications | `/api/notifications` | list, mark read, unread count |
| AI Feedback | `/api/feedback` | generate summary, preview |
| Mock Interviews | `/api/mock-interviews` | start session, submit answers, get AI feedback |
| Practice Questions | `/api/practice` | browse by role, difficulty, category |

### Interview status lifecycle

```
pending ──► scheduled ──► completed ──► report_pending ──► published
   │             │              │               │
   └─────────────┴──────────────┴───────────────┘
                         cancelled
```

### Role permission matrix

| Action | admin | recruiter | interviewer | candidate |
|---|:---:|:---:|:---:|:---:|
| Create / assign interview | ✓ | ✓ | ✗ | ✗ |
| Complete interview + scores | ✓ | ✗ | ✓ | ✗ |
| Submit / publish report | ✓ | publish only | submit only | ✗ |
| View report | ✓ | ✓ | ✓ | published only |
| Generate AI feedback | ✓ | ✓ | ✓ | ✗ |
| Manage availability slots | ✓ | view only | ✓ | ✗ |
| Mock interviews | ✗ | ✗ | ✗ | ✓ |
| Practice questions | ✗ | ✗ | ✗ | ✓ |
| Approve interviewers | ✓ | ✗ | ✗ | ✗ |

---

## Deployment

**Backend → [Render](https://render.com)**
1. Create a Web Service pointing to `backend/`
2. Build command: `pip install -r requirements.txt && flask db upgrade`
3. Start command: `gunicorn run:app`
4. Add all env variables from `.env.example`

**Frontend → [Vercel](https://vercel.com)**
1. Import repo and set root directory to `frontend/`
2. Add env variable: `VITE_API_URL=https://<your-render-app>.onrender.com/api`
3. Deploy — Vercel auto-detects Vite and runs `npm run build`

---

## Author

**Kamal Sharma**

[![GitHub](https://img.shields.io/badge/GitHub-kamalsharma001-181717?style=flat&logo=github)](https://github.com/kamalsharma001/TalentForge)

---

*Built with Flask · React · PostgreSQL*
