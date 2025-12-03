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
- **Admin Panel**: User management, department configuration, SLA setup
- **Email Notifications**: Configurable SMTP for alerts

## 🔐 Demo Credentials

The system includes pre-seeded demo data. Use these credentials to explore:

| Role | Email | Password |
|------|-------|----------|
| **Superuser** | admin@pmc.edu.pk | adminpassword123 |
| **System Admin** | sysadmin@pmc.edu.pk | password123 |
| **Cardiology HOD** | cardio.hod@pmc.edu.pk | password123 |
| **Cardiology Doctor** | cardio.doc@pmc.edu.pk | password123 |
| **Neurology HOD** | neuro.hod@pmc.edu.pk | password123 |
| **Neurology Doctor** | neuro.doc@pmc.edu.pk | password123 |
| **Orthopedics HOD** | ortho.hod@pmc.edu.pk | password123 |
| **ER Doctor** | er.doc@pmc.edu.pk | password123 |
| **Medicine HOD** | med.hod@pmc.edu.pk | password123 |

> **Note:** All department users follow the pattern `{dept}.{role}@pmc.edu.pk` with password `password123`

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
- **Styling**: Tailwind CSS

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

The database will be automatically seeded with demo data on first run.

### Local Development Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

# Run migrations
python manage.py migrate

# Seed demo data
python manage.py seed_data

# Run development server
python manage.py runserver
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
echo "VITE_API_URL=http://localhost:8000/api/v1" > .env
echo "VITE_WS_URL=ws://localhost:8000/ws" >> .env

# Run development server
npm run dev
```

### Access Points

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000/api/v1 |
| Django Admin | http://localhost:8000/admin |

## 📚 Documentation

The codebase is thoroughly documented with docstrings (Python) and JSDoc comments (JavaScript).

### Key Documents

All detailed documentation has been organized in the [docs/](docs/) directory:

- **[DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md)**: Step-by-step demo presentation guide
- **[PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md)**: High-level project overview
- **[CURRENT_STATUS.md](docs/CURRENT_STATUS.md)**: Latest development progress
- **[ADMIN_PANEL.md](docs/ADMIN_PANEL.md)**: Admin panel features and usage
- **[VISION.md](docs/VISION.md)**: Project vision and goals
- **[WORKFLOW.md](docs/WORKFLOW.md)**: Consult workflow documentation
- **[DATA_MODEL.md](docs/DATA_MODEL.md)**: Database schema
- **[TECHNICAL_PLAN.md](docs/TECHNICAL_PLAN.md)**: Complete technical architecture
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)**: System architecture overview
- **[DEPLOYMENT.md](docs/DEPLOYMENT.md)**: Deployment instructions and guidelines
- **[GOOGLE_WORKSPACE_SETUP.md](docs/GOOGLE_WORKSPACE_SETUP.md)**: Google SSO integration setup

## 🧪 Testing

### Backend Tests
```bash
cd backend
python manage.py test
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

## 🚢 Deployment

### Docker Deployment (Recommended)

```bash
# Production deployment
docker-compose up -d

# View logs
docker-compose logs -f backend

# Restart services
docker-compose restart
```

### Environment Variables

#### Backend (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | (required in production) |
| `DEBUG` | Enable debug mode | `True` |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1` |
| `DATABASE` | Database type | `postgres` |
| `DB_NAME` | Database name | `consult_db` |
| `DB_USER` | Database user | `consult_user` |
| `DB_PASSWORD` | Database password | (required) |
| `DB_HOST` | Database host | `localhost` |
| `REDIS_URL` | Redis URL for channels | `redis://localhost:6379/0` |
| `CORS_ALLOWED_ORIGINS` | CORS origins | `http://localhost:3000` |

#### Frontend (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000/api/v1` |
| `VITE_WS_URL` | WebSocket URL | `ws://localhost:8000/ws` |

## 📝 Development Status

### Completed (MVP)
- ✅ User authentication (JWT)
- ✅ Department management with SLA configuration
- ✅ Patient creation and search
- ✅ Consult creation and workflow
- ✅ Status transitions (Pending → Acknowledged → In Progress → Completed)
- ✅ Notes and final note completion
- ✅ Permission controls
- ✅ Dashboard with statistics
- ✅ Admin Panel (user management, department management)
- ✅ Real-time WebSocket notifications
- ✅ CI/CD pipelines (GitHub Actions)
- ✅ Docker deployment
- ✅ Comprehensive demo data

### Future Enhancements
- Google Workspace SSO integration
- SLA monitoring and escalation
- Analytics dashboard
- CSV user import
- Email notifications (templates ready)

## 📄 License

Proprietary - Pakistan Medical Commission

---

**Built with ❤️ for Pakistan Medical Commission**
