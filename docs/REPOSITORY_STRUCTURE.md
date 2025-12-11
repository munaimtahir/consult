# Repository Structure

This document describes the organization and structure of the Hospital Consult System repository.

## Overview

This is a monorepo containing three main applications:
- **Backend**: Django REST API with WebSocket support
- **Frontend**: React web application
- **Mobile**: React Native Android/iOS application

## Directory Structure

```
/
├── archive/                        # Historical and legacy content (preserved, not deleted)
│   ├── deployment-templates/       # Multi-app deployment templates (archived)
│   ├── historical-docs/            # Historical status reports, plans, and summaries (36 files)
│   ├── env.example.duplicate       # Old duplicate env file
│   └── README.md                   # Explains archive purpose
│
├── backend/                        # Django Backend Application
│   ├── apps/                       # Django apps (accounts, consults, departments, etc.)
│   ├── config/                     # Django settings and configuration
│   ├── templates/                  # Email templates
│   ├── manage.py                   # Django management script
│   ├── requirements.txt            # Python dependencies
│   ├── Dockerfile                  # Backend Docker configuration
│   └── entrypoint.sh              # Docker entrypoint script
│
├── frontend/                       # React Frontend Application
│   ├── src/                        # React source code
│   │   ├── components/            # Reusable React components
│   │   ├── pages/                 # Page components
│   │   ├── services/              # API service layer
│   │   └── hooks/                 # Custom React hooks
│   ├── tests/                     # Playwright E2E tests
│   ├── public/                    # Static assets
│   ├── package.json               # NPM dependencies
│   ├── vite.config.js            # Vite build configuration
│   ├── Dockerfile                 # Frontend Docker configuration
│   └── nginx.conf                 # Nginx configuration for frontend
│
├── mobile/                         # React Native Mobile Application
│   ├── src/                        # React Native source code
│   │   ├── components/            # Mobile UI components
│   │   ├── screens/               # Screen components
│   │   ├── navigation/            # Navigation configuration
│   │   └── services/              # API service layer
│   ├── android/                   # Android-specific code
│   ├── ios/                       # iOS-specific code (if present)
│   ├── package.json               # NPM dependencies
│   ├── app.json                   # Expo/React Native config
│   └── [Build scripts]            # Various build automation scripts
│
├── nginx/                          # Nginx Configuration
│   ├── default.conf               # Main Nginx configuration
│   └── error-pages/               # Custom error pages
│
├── scripts/                        # Utility Scripts
│   ├── deploy.sh                  # Main deployment script
│   ├── setup-java.sh              # Java setup helper
│   ├── update-server-ip.sh        # IP configuration updater
│   ├── add-app.sh                 # Add new app to deployment
│   ├── remove-app.sh              # Remove app from deployment
│   ├── manage-apps.sh             # Manage deployed apps
│   ├── validate-deployment.sh     # Validate deployment configuration
│   └── validate-env.sh            # Validate environment variables
│
├── docs/                           # Active Technical Documentation
│   ├── ACKNOWLEDGE_ASSIGN_API.md  # Acknowledge & Assign API spec
│   ├── REASSIGNMENT_API.md        # Reassignment API spec
│   ├── ADMIN_PANEL.md             # Admin panel documentation
│   ├── ANALYTICS_DASHBOARD.md     # Analytics dashboard documentation
│   ├── CSV_USER_IMPORT_SPEC.md    # CSV import feature spec
│   ├── MULTI_APP_DEPLOYMENT_GUIDE.md  # Multi-app deployment guide
│   ├── ADD_NEW_APP_GUIDE.md       # Guide for adding new apps
│   ├── maintenance_migrations_seed_ci.md  # Maintenance guide
│   ├── app_config_template.yml    # App configuration template
│   └── REPOSITORY_STRUCTURE.md    # This file
│
├── .github/                        # GitHub Configuration
│   └── workflows/                 # GitHub Actions CI/CD
│       ├── backend.yml            # Backend CI pipeline
│       ├── frontend.yml           # Frontend CI pipeline
│       └── docker-ci.yml          # Docker build CI pipeline
│
├── .vscode/                        # VS Code Configuration
│   ├── settings.json              # Editor settings
│   └── extensions.json            # Recommended extensions
│
├── docker-compose.yml              # Docker Compose configuration
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
├── README.md                       # Main project documentation
│
└── [Essential Docs at Root]        # Core documentation files
    ├── ARCHITECTURE.md             # System architecture overview
    ├── CI-CD.md                    # CI/CD documentation
    ├── DATA_MODEL.md               # Database schema
    ├── DEPLOYMENT.md               # Deployment instructions
    ├── VISION.md                   # Project vision and goals
    └── WORKFLOW.md                 # Consult workflow documentation
```

## File Organization Principles

### Active vs Archived

**Active Files** (in main directories):
- Currently used in the application
- Referenced by code, CI/CD, or deployment scripts
- Actively maintained and updated

**Archived Files** (in `/archive`):
- Historical documentation and status reports
- Completed milestone reports
- Legacy templates no longer in active use
- Preserved for reference but not actively maintained

### Documentation Organization

1. **Root Level Docs**: Core project documentation (README, ARCHITECTURE, VISION, etc.)
2. **`/docs` Directory**: Technical specifications, API docs, and feature documentation
3. **Component READMEs**: Each major component (backend, frontend, mobile) has its own README
4. **Archive**: Historical documentation preserved for reference

### Scripts Organization

All utility scripts are consolidated in the `/scripts` directory for easy discovery and maintenance. This includes:
- Deployment scripts
- Setup and configuration scripts
- Validation and management scripts

## Configuration Files

### Environment Configuration
- **`.env.example`**: Template for environment variables (use this)
- **`backend/.env.example`**: Backend-specific template
- **`frontend/.env.example`**: Frontend-specific template

### Docker Configuration
- **`docker-compose.yml`**: Multi-service orchestration
- **`backend/Dockerfile`**: Backend container definition
- **`frontend/Dockerfile`**: Frontend container definition
- **`nginx/default.conf`**: Reverse proxy configuration

### Build Configuration
- **Backend**: `requirements.txt`, Django settings
- **Frontend**: `package.json`, `vite.config.js`, `tailwind.config.js`
- **Mobile**: `package.json`, `metro.config.js`, `babel.config.js`

## Technology Stack

### Backend
- **Framework**: Django 5.x
- **API**: Django REST Framework
- **Database**: PostgreSQL (Production), SQLite (Development)
- **Real-time**: Django Channels (WebSockets)
- **Authentication**: JWT via djangorestframework-simplejwt

### Frontend
- **Framework**: React 19
- **Build Tool**: Vite
- **State Management**: TanStack Query (React Query)
- **Styling**: Tailwind CSS
- **Testing**: Playwright

### Mobile
- **Framework**: React Native
- **Language**: TypeScript
- **Navigation**: React Navigation

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Reverse Proxy**: Nginx
- **Database**: PostgreSQL
- **Cache/Queue**: Redis
- **CI/CD**: GitHub Actions

## Key Locations

### Application Entry Points
- **Backend**: `backend/manage.py`, `backend/config/asgi.py`
- **Frontend**: `frontend/src/main.jsx`, `frontend/index.html`
- **Mobile**: `mobile/index.js`, `mobile/App.tsx`

### Configuration Files
- **Backend Settings**: `backend/config/settings/`
- **Frontend Config**: `frontend/vite.config.js`, `frontend/.env.example`
- **Mobile Config**: `mobile/app.json`, `mobile/android/app/build.gradle`

### Test Files
- **Backend Tests**: `backend/apps/*/tests/`
- **Frontend Tests**: `frontend/tests/`

### Static Assets
- **Frontend**: `frontend/public/`
- **Backend Static**: Served via Django's static files

## Getting Started

1. **Clone the repository**
2. **Read the main README.md** for setup instructions
3. **Review ARCHITECTURE.md** for system overview
4. **Check DEPLOYMENT.md** for deployment instructions
5. **Refer to component-specific READMEs** for detailed setup

## Recent Changes (December 2024)

The repository was recently reorganized to improve maintainability:

1. **Archived 36 historical documents** - Moved status reports, progress updates, and completion summaries to `archive/historical-docs/`
2. **Organized API documentation** - Moved feature and API specs to `docs/` directory
3. **Consolidated scripts** - Moved all utility scripts to `scripts/` directory
4. **Removed duplicates** - Archived duplicate env files and templates
5. **Updated .gitignore** - Added patterns to ignore test artifacts and build outputs

All historical files were preserved (not deleted) for future reference.

## Maintenance

### Adding New Documentation
- **API/Feature docs**: Add to `docs/`
- **Core project docs**: Consider if it belongs at root level
- **Historical/milestone docs**: Add to `archive/historical-docs/` if not actively maintained

### Adding New Scripts
- Place in `scripts/` directory
- Make executable: `chmod +x scripts/your-script.sh`
- Document purpose in script header comments

### Updating Structure
When making structural changes:
1. Update this document
2. Update references in other documentation
3. Update CI/CD workflows if needed
4. Test that builds and deployments still work

---

**Last Updated**: December 2024  
**Maintained By**: Development Team
