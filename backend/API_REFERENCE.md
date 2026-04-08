# TalentForge — Backend API Reference

Base URL (production): `https://<your-render-app>.onrender.com/api`

All authenticated endpoints require:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

---

## Authentication  `/api/auth`

| Method | Path | Auth | Roles | Description |
|--------|------|------|-------|-------------|
| POST | `/register` | ✗ | — | Register a new user |
| POST | `/login` | ✗ | — | Login, receive JWT tokens |
| POST | `/refresh` | Refresh JWT | — | Get a new access token |
| GET | `/me` | ✓ | Any | Return authenticated user profile |
| POST | `/logout` | ✓ | Any | Client-side token discard |
| POST | `/change-password` | ✓ | Any | Change own password |

### POST /auth/register
```json
{
  "email": "jane@acme.com",
  "password": "Secure@123",
  "role": "recruiter",
  "first_name": "Jane",
  "last_name": "Doe",
  "phone": "+1-555-0100"
}
```
Roles allowed: `recruiter`, `interviewer`, `candidate`

### POST /auth/login
```json
{ "email": "jane@acme.com", "password": "Secure@123" }
```
Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "user": { "id": "...", "email": "...", "role": "recruiter", ... }
}
```

---

## Users  `/api/users`

| Method | Path | Roles | Description |
|--------|------|-------|-------------|
| GET | `/me` | Any | Own profile |
| PATCH | `/me` | Any | Update own profile |
| GET | `/` | admin | List all users |
| GET | `/<id>` | admin | Get user by ID |
| PATCH | `/<id>/deactivate` | admin | Deactivate user |
| PATCH | `/<id>/activate` | admin | Reactivate user |
| GET | `/interviewers` | admin, recruiter | List approved interviewers |
| PATCH | `/interviewers/<id>/approve` | admin | Approve interviewer |

---

## Interviews  `/api/interviews`

| Method | Path | Roles | Description |
|--------|------|-------|-------------|
| POST | `/` | admin, recruiter | Create interview request |
| GET | `/` | Any | List interviews (scoped by role) |
| GET | `/<id>` | Any | Get interview detail |
| PATCH | `/<id>` | admin, recruiter | Update interview |
| POST | `/<id>/assign` | admin, recruiter | Assign interviewer + slot |
| POST | `/<id>/complete` | interviewer | Mark complete + submit scores |
| POST | `/<id>/cancel` | Any | Cancel interview |

### POST /interviews/
```json
{
  "title": "Senior Backend Engineer Interview",
  "job_role": "Backend Engineer",
  "candidate_id": "<uuid>",
  "organization_id": "<uuid>",
  "tech_stack": ["Python", "PostgreSQL", "AWS"],
  "difficulty": "hard",
  "duration_mins": 60,
  "instructions": "Focus on system design and SQL optimisation.",
  "scheduled_at": "2025-09-01T10:00:00Z",
  "timezone": "America/New_York"
}
```

### POST /interviews/<id>/assign
```json
{ "interviewer_id": "<uuid>", "slot_id": "<uuid>" }
```

### POST /interviews/<id>/complete
```json
{
  "recording_url": "https://res.cloudinary.com/...",
  "recording_cloudinary_id": "talentforge/recordings/...",
  "recording_duration_s": 3540,
  "scores": [
    { "dimension": "Problem Solving", "score": 8, "notes": "Clean approach" },
    { "dimension": "Communication",   "score": 7 },
    { "dimension": "System Design",   "score": 9, "notes": "Excellent depth" }
  ]
}
```

---

## Scheduling  `/api/scheduling`

| Method | Path | Roles | Description |
|--------|------|-------|-------------|
| POST | `/slots` | interviewer | Add availability slot |
| DELETE | `/slots/<id>` | interviewer | Remove slot |
| GET | `/slots` | admin, recruiter, interviewer | List slots |
| GET | `/match` | admin, recruiter | Find available interviewers |

### POST /scheduling/slots
```json
{
  "start_time": "2025-09-01T09:00:00Z",
  "end_time":   "2025-09-01T12:00:00Z",
  "timezone":   "America/New_York",
  "is_recurring": false
}
```

### GET /scheduling/match
Query params:
- `tech_stack=Python,AWS`
- `requested_at=2025-09-01T10:00:00Z`
- `duration_mins=60`

---

## Reports  `/api/reports`

| Method | Path | Roles | Description |
|--------|------|-------|-------------|
| POST | `/<interview_id>` | interviewer | Submit report |
| GET | `/<interview_id>` | Any | Get report (candidate sees stripped view) |
| PATCH | `/<report_id>/edit` | interviewer, admin | Update report |
| POST | `/<report_id>/publish` | admin, recruiter | Publish report to candidate |
| POST | `/<interview_id>/generate-ai` | admin, recruiter, interviewer | Trigger AI summary |

### POST /reports/<interview_id>
```json
{
  "summary":        "The candidate demonstrated strong fundamentals...",
  "strengths":      "Excellent problem decomposition, clean code style.",
  "weaknesses":     "Could improve on distributed systems knowledge.",
  "recommendation": "Recommend proceeding to final round.",
  "private_notes":  "Seemed nervous initially but recovered well.",
  "decision":       "hire"
}
```
Decisions: `hire` | `hold` | `no_hire`

---

## Notifications  `/api/notifications`

| Method | Path | Roles | Description |
|--------|------|-------|-------------|
| GET | `/` | Any | List own notifications |
| GET | `/unread-count` | Any | Count of unread notifications |
| PATCH | `/<id>/read` | Any | Mark single notification read |
| POST | `/mark-all-read` | Any | Mark all notifications read |

Query params for GET `/`:
- `page=1`
- `per_page=20`
- `unread_only=true`

---

## AI Feedback  `/api/feedback`

| Method | Path | Roles | Description |
|--------|------|-------|-------------|
| POST | `/<interview_id>/generate` | admin, recruiter, interviewer | Generate AI summary |
| GET | `/<interview_id>/preview` | admin, recruiter, interviewer | Preview stored AI output |

---

## Common Response Formats

### Pagination envelope
```json
{
  "items":    [...],
  "total":    42,
  "page":     1,
  "pages":    3,
  "per_page": 20,
  "has_next": true,
  "has_prev": false
}
```

### Error envelope
```json
{
  "error": "Human-readable message",
  "code":  "machine_readable_code"
}
```

### Validation error (422)
```json
{
  "error": "Validation failed",
  "code":  "validation_error",
  "details": { "email": ["Not a valid email address."] }
}
```

---

## Interview Status Lifecycle

```
pending → scheduled → completed → report_pending
   ↓          ↓           ↓             ↓
cancelled  cancelled  cancelled    (report created)
```

---

## Role Permission Matrix

| Endpoint Group | admin | recruiter | interviewer | candidate |
|----------------|-------|-----------|-------------|-----------|
| Create interview | ✓ | ✓ | ✗ | ✗ |
| Assign interviewer | ✓ | ✓ | ✗ | ✗ |
| Complete interview | ✓ | ✗ | ✓ | ✗ |
| Submit report | ✓ | ✗ | ✓ | ✗ |
| Publish report | ✓ | ✓ | ✗ | ✗ |
| View report | ✓ | ✓ | ✓ | published only |
| Manage slots | ✓ | view | ✓ own | ✗ |
| Match interviewers | ✓ | ✓ | ✗ | ✗ |
| Generate AI feedback | ✓ | ✓ | ✓ | ✗ |
| Approve interviewer | ✓ | ✗ | ✗ | ✗ |
