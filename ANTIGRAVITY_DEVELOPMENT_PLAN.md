# ANTIGRAVITY_DEVELOPMENT_PLAN.md  
## 🚨 AGENT NOTES (IMPORTANT — READ FIRST)

These instructions are written specifically for **Google Antigravity Agents**.  
Agents must follow these rules **strictly**:

1. **NEVER create a new Django project**. Always use the existing `backend/` and `config/` folders.
2. **NEVER change the tech stack** (Django + DRF + PostgreSQL + React + Vite).
3. **ALWAYS follow phases in order**.  
   - Do **NOT** jump to later phases.  
   - Do **NOT** mix backend and frontend tasks in the same mission.
4. **ALL missions must be atomic**.  
   A mission must be small enough to be completed safely without modifying unrelated files.
5. **Before making changes**, the agent must:
   - Analyze existing files  
   - Preserve structure  
   - Avoid overwriting files unless explicitly instructed
6. **Ask for confirmation ONLY when required by Antigravity safety**, not for every small action.
7. **NEVER delete or rename files** unless explicitly stated.
8. **ALWAYS produce an Artifact** at the end of each mission:
   - Summary of changes  
   - Tree structure of modified folders  
   - Any code that was added  
   - Any questions or assumptions  
   - Warnings about potential issues  
9. **If a conflict arises**, choose the safest option and explain it in the Artifact.

---

# 📘 FULL DEVELOPMENT PLAN (STRICT VERSION)

## Phase 0 — Baseline Verification

### Objectives
- Confirm that required directories exist.
- Confirm Python version, Django version, DRF version.
- Confirm `INSTALLED_APPS` alignment.
- Confirm `config/settings` structure.
- Confirm that `backend/apps/{accounts, departments, patients}` are valid Django apps.

### Agent Tasks
1. Scan entire repo and generate a folder tree.
2. Verify required files:
   - `backend/config/settings/base.py`
   - `backend/config/settings/development.py`
   - `backend/config/settings/production.py`
   - `backend/apps/*/apps.py`
3. Generate a “Readiness Report” Artifact.
4. Ask ONLY IF a blocking issue is found.

---

# Phase 1 — Create Full Backend Skeleton (Very Strict)

### Purpose
Create missing Django apps with **complete empty structure** (no logic).

### Required Apps
- `apps.consults`
- `apps.notifications`
- `apps.analytics`
- `apps.core`

### Required Files in Each App
```
__init__.py
apps.py                  # MUST include proper AppConfig
models.py                # MUST include TODO header
serializers.py           # MUST include TODO header
views.py                 # MUST import DRF and include TODO header
urls.py                  # MUST define an empty urlpatterns list
admin.py                 # MUST include admin.site.register TODO
migrations/__init__.py
```

### Strict Rules
- DO NOT create duplicate files.
- DO NOT modify existing apps in this phase.
- DO NOT implement business logic.
- DO NOT create database fields yet.

### Additional Requirements
- Update `INSTALLED_APPS` only if missing.
- Validate imports by running `python manage.py check`.
- Output full Artifact with:
  - Tree of `backend/apps`
  - Contents of all created files
  - Output of `manage.py check`

---

# Phase 2 — Core Models (Very Strict)

### Purpose
Implement actual database models, deferring advanced behaviors until later phases.

### Models to Implement
#### accounts
- Use existing model if already implemented
- Add TODOs for additional role fields

#### departments
Fields:
- name (str)
- code (str)
- head (FK account)
- contact (str or null)

#### patients
Fields:
- mrn
- name
- age
- gender
- location
- primary_department (FK)

#### consults
Models:
- ConsultRequest
- ConsultNote

Each must include:
- created_at
- updated_at
- status (choice)
- urgency

### Strict Rules
- NO API implementation.
- NO business methods.
- NO serializer logic.
- Only model definitions + migrations.

---

# Phase 3 — Backend API Layer (DRF ViewSets)

### Required Steps
1. Create serializers for all models.
2. Create ViewSets for CRUD.
3. Add routers in each app.
4. Include routers under `/api/v1/`.

### Restriction
- DO NOT implement WebSockets.
- DO NOT implement JWT.
- DO NOT implement permissions.
- Minimum viable CRUD only.

---

# Phase 4 — Authentication (JWT)

### Requirements
1. Install SimpleJWT
2. Configure:
   - `/auth/login/`
   - `/auth/refresh/`
   - `/auth/me/`
3. Implement role-based permission classes.
4. Enforce authorization on all endpoints.

### Strict Rule
- DO NOT modify unrelated endpoints.

---

# Phase 5 — Frontend Skeleton (React + Vite)

### Required Folders
```
src/
  api/
  components/
  context/
  hooks/
  pages/
  router/
  utils/
```

### Required Pages
- LoginPage.jsx
- Dashboard.jsx
- ConsultListPage.jsx
- ConsultDetailsPage.jsx

Each should contain:
- A heading
- TODO comments

---

# Phase 6 — Connect Frontend to Backend

### Implement:
- Login flow
- JWT storage
- Protected routes
- Consult list retrieval
- Consult detail + notes

### Strict Rule
- No UI beautification
- No analytics yet

---

# Phase 7 — Real-time Notifications

### Required Components
- Django Channels
- WebSocket routing
- Notification consumer
- React WebSocket client

---

# Phase 8 — Background Tasks (Celery)

Implement:
- Celery configuration
- Redis broker
- Automated overdue consult reminders

---

# Phase 9 — Analytics (Backend + Frontend)

Implement:
- Consult volume endpoint
- SLA compliance
- Average response time
- Frontend charts

---

# Phase 10 — Testing + Deployment

### Requirements
- Backend test suite
- Frontend tests
- Docker configuration
- Nginx reverse proxy
- VPS deployment checklist

---

# ✔ End of Document
This file should remain in the **root directory** of the repository.  
Antigravity must refer to this plan before every mission.
