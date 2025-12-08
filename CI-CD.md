# CI/CD Documentation

This document describes the Continuous Integration and Continuous Deployment (CI/CD) setup for the Consult application.

## Overview

The project has **three GitHub Actions workflows** that ensure code quality and build integrity:

1. **Backend CI** (`.github/workflows/backend.yml`) - Tests the Django/Python backend
2. **Frontend CI** (`.github/workflows/frontend.yml`) - Lints and builds the React/Vite frontend
3. **Docker CI** (`.github/workflows/docker-ci.yml`) - Validates Docker images and compose configuration

## Workflows

### 1. Backend CI

**File:** `.github/workflows/backend.yml`

**Triggers:**
- Push to `main` or `develop` branches (when backend code changes)
- Pull requests to `main` or `develop` branches (when backend code changes)

**What it does:**
1. Sets up Python 3.11
2. Installs dependencies from `requirements.txt`
3. Installs additional packages: `django-filter`, `requests`, `daphne`
4. Creates required logs directory
5. Checks for unapplied migrations (`makemigrations --check`)
6. Runs the Django test suite

**Running tests locally:**
```bash
cd backend
pip install -r requirements.txt
pip install django-filter requests daphne
mkdir -p logs
export DJANGO_SETTINGS_MODULE=config.settings.development
python manage.py test
```

### 2. Frontend CI

**File:** `.github/workflows/frontend.yml`

**Triggers:**
- Push to `main` or `develop` branches (when frontend code changes)
- Pull requests to `main` or `develop` branches (when frontend code changes)

**What it does:**
1. Sets up Node.js 20.x
2. Installs dependencies with `npm ci` (falls back to `npm install` if needed)
3. Runs ESLint to check code quality
4. Builds the Vite production bundle

**Running locally:**
```bash
cd frontend
npm install --legacy-peer-deps
npm run lint
npm run build
```

**Development mode:**
```bash
cd frontend
npm run dev
```

### 3. Docker CI

**File:** `.github/workflows/docker-ci.yml`

**Triggers:**
- Push to `main` or `develop` branches (when Docker-related files change)
- Pull requests to `main` or `develop` branches (when Docker-related files change)

**What it does:**
1. Validates `docker-compose.yml` configuration
2. Builds the backend Docker image
3. Tests the backend image (runs `python manage.py --help`)
4. Builds the frontend Docker image
5. Tests the frontend image (checks nginx serves content)
6. Performs a full `docker-compose build` smoke test
7. Reports image sizes

**Running locally:**

**Build individual images:**
```bash
# Backend
docker build -t consult-backend:local backend/

# Frontend
docker build \
  --build-arg VITE_API_URL=http://localhost:8000/api/v1 \
  --build-arg VITE_WS_URL=ws://localhost:8000/ws \
  -t consult-frontend:local \
  frontend/
```

**Build with docker-compose:**
```bash
docker compose build
```

**Run the full stack:**
```bash
docker compose up -d
```

## Tech Stack

### Backend
- **Language:** Python 3.11
- **Framework:** Django 5.0
- **Database:** PostgreSQL (production), SQLite (CI)
- **Cache/Queue:** Redis
- **ASGI Server:** Uvicorn/Daphne
- **Task Queue:** Celery

### Frontend
- **Language:** JavaScript/JSX
- **Framework:** React 19
- **Build Tool:** Vite 7
- **Bundler:** ESBuild
- **Linter:** ESLint 9

### Docker
- **Backend Base:** `python:3.11-slim`
- **Frontend Base:** `node:22-alpine` (build) + `nginx:alpine` (production)
- **Orchestration:** Docker Compose 3.8

## Environment Variables

### Backend (Docker)
- `DEBUG` - Debug mode (0 for production)
- `SECRET_KEY` - Django secret key
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts
- `DATABASE` - Database type (postgres/sqlite)
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` - Database credentials
- `REDIS_URL` - Redis connection URL
- `CORS_ALLOWED_ORIGINS` - CORS allowed origins
- `CSRF_TRUSTED_ORIGINS` - CSRF trusted origins

### Frontend (Docker Build)
- `VITE_API_URL` - Backend API URL (e.g., `http://localhost:8000/api/v1`)
- `VITE_WS_URL` - WebSocket URL (e.g., `ws://localhost:8000/ws`)

## CI Status Badges

Add these to your `README.md`:

```markdown
![Backend CI](https://github.com/munaimtahir/consult/workflows/Backend%20CI/badge.svg)
![Frontend CI](https://github.com/munaimtahir/consult/workflows/Frontend%20CI/badge.svg)
![Docker CI](https://github.com/munaimtahir/consult/workflows/Docker%20CI/badge.svg)
```

## Troubleshooting

### Backend Tests Fail

**Issue:** Tests fail with database errors
```bash
# Ensure you're using the development settings
export DJANGO_SETTINGS_MODULE=config.settings.development
python manage.py test
```

**Issue:** Missing migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Frontend Build Fails

**Issue:** Dependency conflicts
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

**Issue:** ESLint errors
```bash
# Run linter to see specific issues
npm run lint

# Auto-fix where possible (use with caution)
npm run lint -- --fix
```

### Docker Build Fails

**Issue:** Build context errors
```bash
# Make sure you're building from the correct directory
cd backend  # or frontend
docker build -t test-image .
```

**Issue:** Layer caching issues
```bash
# Build without cache
docker build --no-cache -t test-image .
```

**Issue:** Docker compose fails
```bash
# Validate configuration
docker compose config

# Rebuild from scratch
docker compose down -v
docker compose build --no-cache
docker compose up
```

## Best Practices

1. **Always run tests locally** before pushing
2. **Check CI status** before merging PRs
3. **Keep dependencies updated** but test thoroughly
4. **Use feature branches** for development
5. **Write meaningful commit messages**
6. **Update this documentation** when CI changes

## Deployment

This CI/CD setup validates code quality and build integrity but does not automatically deploy to production. For deployment:

1. All three CI workflows must pass ✅
2. Manual deployment via `docker-compose.yml` on target server
3. See `DEPLOYMENT.md` for detailed deployment instructions

## Maintenance

### Updating Python Version
1. Update `python-version` in `.github/workflows/backend.yml`
2. Update `FROM python:X.Y-slim` in `backend/Dockerfile`
3. Test locally before committing

### Updating Node Version
1. Update `node-version` in `.github/workflows/frontend.yml`
2. Update `FROM node:X-alpine` in `frontend/Dockerfile`
3. Test locally before committing

### Updating Dependencies
- **Backend:** Update `requirements.txt`, test, commit
- **Frontend:** Update `package.json`, run `npm install`, test, commit

## Support

For issues or questions about CI/CD:
1. Check workflow logs on GitHub Actions tab
2. Review this documentation
3. Contact the development team
