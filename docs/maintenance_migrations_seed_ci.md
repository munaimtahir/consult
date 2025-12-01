# Maintenance: Migrations, Seed Command & CI Fixes

This document summarizes the maintenance work performed to fix migrations, seed command, and CI workflows.

## Migration Files Changed

### `backend/apps/accounts/migrations/0004_remove_user_users_email_4b85f2_idx_and_more.py`

**Problem:** Migration was attempting to remove indexes that were never created in the migration chain.

**Cause:** Migration 0004 contained `RemoveIndex` operations for:
- `users_email_4b85f2_idx`
- `users_departm_6a50ab_idx`
- `users_designa_2a55ef_idx`

These indexes were never created in migrations 0001 or 0002, likely due to a previous migration squash or model refactoring that wasn't properly reconciled.

**Solution:** Emptied the operations list in migration 0004 while preserving the migration file to maintain the migration chain integrity.

```python
# Fixed: Removed invalid RemoveIndex operations for indexes that were never created
operations = []
```

## Seed Command (`seed_data`)

The seed command at `backend/apps/core/management/commands/seed_data.py` was already working correctly and required no changes. It creates:

- **5 Departments:** Cardiology, Neurology, Orthopedics, General Medicine, Emergency
- **17 Users:** Including superuser, admin, and department staff (HODs, Professors, Doctors)
- **15 Patients:** Sample patients with various conditions
- **12 Consults:** Sample consults at various workflow stages

### Running the Seed Command

```bash
# Using Docker
docker-compose exec backend sh -c "python manage.py seed_data"

# Local development
cd backend
python manage.py seed_data
```

## CI Workflow Changes

### Backend CI (`backend.yml`)

No changes required to the workflow file. Fixed issues in the code:

1. **Renamed utility script:** `test_me_endpoint.py` → `check_me_endpoint.py`
   - The old filename was being picked up by Django's test discovery
   - The script was a development utility for testing authentication, not an actual test

### Frontend CI (`frontend.yml`)

No changes required to the workflow file. Fixed issues in the code:

1. **Fixed ESLint error in `playwright.config.js`**
   - Removed redundant `/* global process */` comment
   - The ESLint config already included Node.js globals for this file

## Verification Commands

### Backend

```bash
# Run migrations (fresh database)
cd backend
python manage.py migrate --noinput

# Check for pending migrations
python manage.py makemigrations --check --dry-run

# Run tests
python manage.py test

# Seed demo data
python manage.py seed_data
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run linter
npm run lint

# Build for production
npm run build
```

### Docker

```bash
# Build and run all services
docker-compose up --build

# Run migrations in container
docker-compose exec backend sh -c "python manage.py migrate"

# Run seed command in container
docker-compose exec backend sh -c "python manage.py seed_data"

# Run backend tests in container
docker-compose exec backend sh -c "python manage.py test"
```

## Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| **Superuser** | admin@pmc.edu.pk | adminpassword123 |
| **System Admin** | sysadmin@pmc.edu.pk | password123 |
| **Cardiology HOD** | cardio.hod@pmc.edu.pk | password123 |
| **Cardiology Doctor** | cardio.doc@pmc.edu.pk | password123 |
| **Neurology HOD** | neuro.hod@pmc.edu.pk | password123 |
| **ER Doctor** | er.doc@pmc.edu.pk | password123 |

> All department users follow the pattern `{dept}.{role}@pmc.edu.pk` with password `password123`

## CI/CD Pipelines

### Backend CI (`backend.yml`)

- **Trigger:** Push/PR to `main` or `develop` branches affecting `backend/**`
- **Python Version:** 3.11
- **Steps:**
  1. Install dependencies
  2. Create logs directory
  3. Run `makemigrations --check --dry-run` to verify migrations are up to date
  4. Run `python manage.py test`

### Frontend CI (`frontend.yml`)

- **Trigger:** Push/PR to `main` or `develop` branches affecting `frontend/**`
- **Node Version:** 20.x
- **Steps:**
  1. Install dependencies (`npm ci` with fallback to `npm install`)
  2. Run ESLint (`npm run lint`)
  3. Build (`npm run build`)

## Environment Variables

### Backend (Required for CI)

| Variable | Default | Description |
|----------|---------|-------------|
| `DJANGO_SETTINGS_MODULE` | `config.settings.development` | Django settings module |

### Frontend

No environment variables required for CI (build uses defaults).
