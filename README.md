# Hospital Consult System

A comprehensive digital system for managing inter-departmental patient consultations at Pakistan Medical Commission (PMC).

## 🏥 Overview

The Hospital Consult System is a paperless, digital application that streamlines communication between primary treating teams and specialty departments, ensuring timely patient reviews and reducing medical errors. This repository contains the complete codebase for the project, with a Django backend and a React frontend.

## 🎯 Key Features

- **Google Workspace SSO**: Secure authentication using `@pmc.edu.pk` accounts
- **Real-time Notifications**: WebSocket-based live updates for consult requests
- **Role-Based Access**: Doctor, Department User, HOD, and Admin roles
- **SLA Monitoring**: Automatic escalation for overdue consults
- **Analytics Dashboard**: Live insights for department performance
- **Email Notifications**: Google Workspace SMTP for alerts and escalations
- **CSV User Import**: Bulk import users with hierarchy levels

## 🛠️ Technology Stack

### Backend
- **Framework**: Django 5.x
- **API**: Django REST Framework
- **Database**: PostgreSQL (Production), SQLite (Development)
- **Authentication**: Google Workspace SSO via django-allauth
- **Real-time**: Django Channels (WebSockets)
- **Background Tasks**: Celery + Redis
- **Email**: Google Workspace SMTP

### Frontend
- **Framework**: React (Vite)
- **State Management**: React Query (TanStack Query)
- **Authentication**: Context API
- **HTTP Client**: Axios
- **Real-time**: WebSocket client

## 📁 Project Structure

```
consult/
├── backend/          # Django project
├── frontend/         # React project
└── README.md         # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+ (for production)
- Redis (for Celery and WebSockets)
- Google Workspace account with `@pmc.edu.pk` domain

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your configuration

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env
# Edit .env with your configuration

# Run development server
npm run dev
```

### Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/api/v1
- **Django Admin**: http://localhost:8000/admin

## 🔐 Google Workspace Configuration

See [GOOGLE_WORKSPACE_SETUP.md](./GOOGLE_WORKSPACE_SETUP.md) for detailed instructions on:
- Setting up OAuth 2.0 credentials
- Configuring SMTP for email notifications
- Domain verification and DNS configuration

## 📊 User Management

### CSV User Import

Admins can bulk import users via CSV with the following format:

```csv
email,first_name,last_name,department,designation,phone_number
john.doe@pmc.edu.pk,John,Doe,Cardiology,Resident 1,+92-300-1234567
```

**Supported Designations**:
- Resident 1-5
- Senior Registrar
- Assistant Professor
- Professor
- HOD (Head of Department)

See [CSV_USER_IMPORT_SPEC.md](./CSV_USER_IMPORT_SPEC.md) for detailed specifications.

## 📖 Documentation

The codebase is thoroughly documented with docstrings (Python) and JSDoc comments (JavaScript). You can generate a full documentation set using the following tools:

- **Backend (Python)**: [Sphinx](https://www.sphinx-doc.org/en/master/) or [pdoc](https://pdoc.dev/)
- **Frontend (JavaScript)**: [JSDoc](https://jsdoc.app/)

In addition to the in-code documentation, the following documents provide further details on the project:

- [Technical Plan](./TECHNICAL_PLAN.md) - Complete technical architecture
- [Implementation Plan](./IMPLEMENTATION_PLAN.md) - Detailed implementation guide
- [Google Workspace Setup](./GOOGLE_WORKSPACE_SETUP.md) - OAuth and SMTP configuration
- [CSV User Import](./CSV_USER_IMPORT_SPEC.md) - User import specifications
- [Vision Document](./VISION.md) - Project vision and goals
- [Workflow](./WORKFLOW.md) - Consult workflow documentation
- [Data Model](./DATA_MODEL.md) - Database schema

## 🧪 Testing

### Backend Tests
```bash
cd backend
python manage.py test
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🚢 Deployment

See [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) for VPS deployment instructions.

## 📝 Development Phases

The project is currently in the initial development phase. The core models and APIs have been implemented, and the frontend has been set up with basic functionality.

- ✅ **Phase 1**: Foundation & Authentication
- ⏳ **Phase 2**: Core Models & API
- ⏳ **Phase 3**: Consult Workflow
- ⏳ **Phase 4**: Real-time Features
- ⏳ **Phase 5**: Advanced Features
- ⏳ **Phase 6**: Testing & Polish
- ⏳ **Phase 7**: VPS Deployment

## 🤝 Contributing

This is an internal PMC project. For questions or issues, contact the development team.

## 📄 License

Proprietary - Pakistan Medical Commission

## 🆘 Support

For technical support or questions:
- Email: consult@pmc.edu.pk
- Internal Documentation: See the other documents in the root directory.

---

**Built with ❤️ for Pakistan Medical Commission**
