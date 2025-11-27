# Hospital Consult System

A comprehensive digital system for managing inter-departmental patient consultations at Pakistan Medical Commission (PMC).

## 🏥 Overview

The Hospital Consult System is a paperless, digital application that streamlines communication between primary treating teams and specialty departments, ensuring timely patient reviews and reducing medical errors. This repository contains the complete codebase for the project, with a Django backend and a React frontend.

## 🎯 MVP Features

- **Authentication**: JWT-based authentication with email login
- **Real-time Notifications**: WebSocket-based live updates for consult requests
- **Role-Based Access**: Doctor, Department User, HOD, and Admin roles
- **Patient Management**: Create and search patients
- **Consult Workflow**: Full lifecycle from creation to completion
- **Dashboard**: Statistics and quick actions for consult management
- **Email Notifications**: Configurable SMTP for alerts

## 🛠️ Technology Stack

### Backend
- **Framework**: Django 5.x
- **API**: Django REST Framework
- **Database**: PostgreSQL (Production), SQLite (Development)
- **Authentication**: JWT via djangorestframework-simplejwt
- **Real-time**: Django Channels (WebSockets)
- **Email**: SMTP (configurable)

### Frontend
- **Framework**: React 19 (Vite)
- **State Management**: TanStack Query (React Query)
- **Routing**: React Router v7
- **HTTP Client**: Axios
- **Real-time**: WebSocket client

## 📁 Project Structure

```
consult/
├── backend/              # Django project
│   ├── apps/             # Django apps (accounts, consults, patients, etc.)
│   ├── config/           # Django settings and configuration
│   └── templates/        # Email templates
├── frontend/             # React project
│   ├── src/
│   │   ├── api/          # API client and services
│   │   ├── components/   # Reusable React components
│   │   ├── context/      # React context providers
│   │   ├── hooks/        # Custom React hooks
│   │   ├── pages/        # Page components
│   │   └── router/       # Route configuration
├── nginx/                # Nginx configuration for Docker
├── docker-compose.yml    # Docker Compose configuration
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+ (for production)
- Redis (for WebSockets)

### Quick Start with Docker

The easiest way to run the full stack:

```bash
# Clone the repository
git clone <repository-url>
cd consult

# Start all services
docker compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/api/v1
# Admin: http://localhost:8000/admin
```

### Local Development Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install django-filter requests daphne

# Create logs directory
mkdir -p logs

# Run migrations
DJANGO_SETTINGS_MODULE=config.settings.development python manage.py migrate

# Create sample data (optional)
python setup_data.py

# Run development server
DJANGO_SETTINGS_MODULE=config.settings.development python manage.py runserver
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env

# Run development server
npm run dev
```

### Access Points

| Service | Development | Docker |
|---------|-------------|--------|
| Frontend | http://localhost:5173 | http://localhost:3000 |
| Backend API | http://localhost:8000/api/v1 | http://localhost:8000/api/v1 |
| Admin | http://localhost:8000/admin | http://localhost:8000/admin |

## 🧪 Testing

### Backend Tests
```bash
cd backend
source venv/bin/activate
DJANGO_SETTINGS_MODULE=config.settings.development python manage.py test
```

### Frontend Linting
```bash
cd frontend
npm run lint
```

### Frontend Build
```bash
cd frontend
npm run build
```

## 🔧 Environment Variables

### Backend (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | (required in production) |
| `DEBUG` | Enable debug mode | `True` |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1` |
| `DB_NAME` | Database name | `consult_db` |
| `DB_USER` | Database user | `consult_user` |
| `DB_PASSWORD` | Database password | (required) |
| `DB_HOST` | Database host | `localhost` |
| `REDIS_URL` | Redis URL for channels | `redis://localhost:6379/0` |
| `CORS_ALLOWED_ORIGINS` | CORS origins | `http://localhost:3000` |

### Frontend (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000/api/v1` |
| `VITE_WS_URL` | WebSocket URL | `ws://localhost:8000/ws` |

## 📝 Development Status

### Completed (MVP)
- ✅ User authentication (JWT)
- ✅ Department management
- ✅ Patient creation and search
- ✅ Consult creation and workflow
- ✅ Status transitions (Pending → Acknowledged → In Progress → Completed)
- ✅ Notes and final note completion
- ✅ Permission controls
- ✅ Dashboard with statistics
- ✅ Real-time WebSocket notifications
- ✅ CI/CD pipelines (GitHub Actions)
- ✅ Docker deployment

### Future Enhancements
- Google Workspace SSO integration
- SLA monitoring and escalation
- Analytics dashboard
- CSV user import
- Email notifications (templates ready)

## 📖 Additional Documentation

- [Technical Plan](./TECHNICAL_PLAN.md) - Complete technical architecture
- [Data Model](./DATA_MODEL.md) - Database schema
- [Workflow](./WORKFLOW.md) - Consult workflow documentation
- [Implementation Plan](./IMPLEMENTATION_PLAN.md) - Detailed implementation guide

## 📄 License

Proprietary - Pakistan Medical Commission

---

**Built with ❤️ for Pakistan Medical Commission**
