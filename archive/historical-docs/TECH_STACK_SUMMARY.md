# Hospital Consult System - Technology Stack Summary

## 🎯 Approved Technology Stack

### Backend
- **Framework**: Django 5.x
- **API**: Django REST Framework (DRF)
- **Database**: PostgreSQL 14+ (Production), SQLite (Development only)
- **Authentication**: Google Workspace SSO (OAuth 2.0) + Django Allauth
- **Email**: Google Workspace SMTP
- **Real-time**: Django Channels (WebSockets)
- **Background Tasks**: Celery + Redis
- **Admin**: Django Admin (built-in)

### Frontend
- **Framework**: Next.js 14+ (App Router)
- **State Management**: React Query (TanStack Query)
- **Routing**: Next.js App Router
- **HTTP Client**: Axios
- **UI Components**: Custom components (clean, simple)
- **Real-time**: WebSocket client
- **Authentication**: NextAuth.js with Google Provider

### Database
- **Production**: PostgreSQL 14+
- **Development**: SQLite (local testing ONLY)
- **ORM**: Django ORM (all models)

### Infrastructure
- **Repository**: Monorepo (single repo with /backend and /frontend)
- **Deployment**: VPS (local testing first)
- **Web Server**: Nginx (reverse proxy)
- **App Server**: Gunicorn/uWSGI
- **Task Queue**: Celery
- **Message Broker**: Redis
- **Caching**: Redis (optional)

---

## 📁 Project Structure (Monorepo)

```
consult/
├── README.md
├── .gitignore
├── docker-compose.yml         # Optional: Docker setup
│
├── backend/                   # Django project
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── config/               # Django settings
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── apps/                 # Django apps
│   │   ├── accounts/         # Users & Google SSO Auth
│   │   ├── departments/      # Departments
│   │   ├── patients/         # Patients
│   │   ├── consults/         # Core consult logic
│   │   ├── notifications/    # Real-time notifications
│   │   ├── analytics/        # Analytics & reporting
│   │   └── core/             # Shared utilities
│   └── tasks/                # Celery tasks
│
└── frontend/                 # Next.js project
    ├── package.json
    ├── next.config.js
    ├── .env.local.example
    ├── app/                  # Next.js App Router
    │   ├── layout.tsx        # Root layout
    │   ├── page.tsx          # Home page
    │   ├── login/            # Login page
    │   ├── dashboard/        # Doctor dashboard
    │   ├── department/       # Department dashboard
    │   ├── admin/            # Admin pages
    │   └── api/              # API routes (NextAuth)
    │       └── auth/
    ├── components/           # Reusable components
    │   ├── common/
    │   ├── layout/
    │   ├── consults/
    │   ├── patients/
    │   ├── notifications/
    │   └── analytics/
    ├── lib/                  # Utilities
    │   ├── api/              # API client layer
    │   ├── hooks/            # Custom hooks
    │   └── utils/            # Helper functions
    └── public/               # Static assets
```

---

## 🔐 Authentication Flow (Google Workspace SSO)

### Backend (Django)
- **django-allauth**: Social authentication
- **Google OAuth 2.0**: Workspace SSO integration
- **JWT Tokens**: API authentication after SSO login
- **Email Domain Restriction**: Only allow @yourhospital.com emails

### Frontend (Next.js)
- **NextAuth.js**: Authentication library
- **Google Provider**: Google Workspace OAuth
- **Session Management**: Secure session cookies
- **Protected Routes**: Middleware-based route protection

### Authentication Flow
```
1. User clicks "Sign in with Google"
2. NextAuth redirects to Google OAuth
3. User authenticates with Google Workspace
4. Google returns user info (email, name, photo)
5. Backend validates email domain (@hospital.com)
6. Backend creates/updates user in Django
7. Backend returns JWT token
8. Frontend stores token in httpOnly cookie
9. All API requests include JWT token
```

---

## 📧 Email Configuration (Google Workspace)

### SMTP Settings
```python
# Django settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'noreply@yourhospital.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'Hospital Consult System <noreply@yourhospital.com>'
```

### Email Notifications
- **New Consult**: Notify target department
- **Consult Assigned**: Notify assigned doctor
- **Consult Overdue**: Escalation email to HOD
- **Password Reset**: Password reset link
- **Daily Summary**: Daily consult summary for HODs

---

## 🔐 Security Features

✅ **Google Workspace SSO**
- Single Sign-On (no password management)
- Email domain restriction
- Automatic user provisioning
- Centralized access control

✅ **Built-in Django Security**
- CSRF protection
- SQL injection prevention
- XSS protection
- Clickjacking protection

✅ **Authentication & Authorization**
- JWT token-based auth
- Role-based access control (RBAC)
- Permission checks on every endpoint

✅ **Data Protection**
- HTTPS/TLS encryption
- Database encryption at rest
- Encrypted backups
- Auto-logout after inactivity

✅ **Audit & Compliance**
- Django Admin audit trails
- Timestamped actions
- User attribution
- HIPAA-ready architecture

---

## 🚀 Key Features

### API-First Design
- RESTful API endpoints
- JSON request/response
- Versioned APIs (`/api/v1/`)
- Auto-generated documentation (Swagger/OpenAPI)

### Role-Based Access
- **Doctor**: Create consults, view assigned consults
- **Department User**: View incoming, assign to doctors
- **HOD**: Department analytics + all department permissions
- **Admin**: Full system access

### Real-time Updates
- WebSocket notifications
- Live consult status updates
- Browser push notifications
- Auto-refresh lists

### Analytics Dashboard
- Consult volume metrics
- Response time tracking
- SLA compliance monitoring
- Export to CSV/PDF

### Email Notifications
- New consult alerts
- Assignment notifications
- Overdue escalations
- Daily summaries

---

## 📊 Core Models

1. **User** (extends Django's AbstractUser)
   - Google Workspace email (unique)
   - Role, Department, Seniority Level
   - Profile photo from Google
   - Built-in permissions

2. **Department**
   - Name, Code, Head, Contact
   - SLA configuration per urgency
   - Email notification settings

3. **Patient**
   - MRN, Demographics, Location
   - Primary Department

4. **ConsultRequest**
   - Patient, Requester, Target Department
   - Urgency, Status, Clinical Details
   - Timestamps for SLA tracking

5. **ConsultNote**
   - Author, Content, Timestamp
   - Linked to ConsultRequest

---

## 🔄 Development Workflow

### Phase 1: Foundation & Authentication (Week 1-2)
- ✅ Setup monorepo structure
- ✅ Setup Django + PostgreSQL
- ✅ Setup Next.js + React Query
- ✅ Configure Google Workspace SSO (Backend)
- ✅ Configure NextAuth.js (Frontend)
- ✅ Configure Google Workspace SMTP
- ✅ Test email sending

### Phase 2: Core Models (Week 3)
- ✅ Department, Patient, Consult models
- ✅ Django Admin interfaces
- ✅ API endpoints for CRUD operations

### Phase 3: Consult Workflow (Week 4-5)
- ✅ Create, list, assign, respond
- ✅ Frontend forms and views
- ✅ Email notifications for key events

### Phase 4: Real-time (Week 6)
- ✅ WebSocket notifications
- ✅ Live updates

### Phase 5: Advanced (Week 7-8)
- ✅ SLA monitoring (Celery)
- ✅ Email escalations
- ✅ Analytics dashboard
- ✅ Follow-up workflow

### Phase 6: Testing (Week 9-10)
- ✅ Unit tests, integration tests
- ✅ Security audit
- ✅ Performance optimization

### Phase 7: VPS Deployment (Week 11-12)
- ✅ VPS setup (Ubuntu/Debian)
- ✅ Nginx configuration
- ✅ SSL certificate (Let's Encrypt)
- ✅ PostgreSQL setup
- ✅ Redis setup
- ✅ Celery worker setup
- ✅ CI/CD pipeline
- ✅ User training

---

## 🌐 VPS Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Domain (HTTPS)                       │
│              consult.yourhospital.com                   │
└─────────────────┬───────────────────────────────────────┘
                  │
        ┌─────────▼─────────┐
        │  Nginx (Port 80/443)                            │
        │  - SSL Termination                              │
        │  - Reverse Proxy                                │
        └─────────┬─────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
┌───────▼────────┐  ┌───────▼────────┐
│  Next.js       │  │  Django        │
│  (Port 3000)   │  │  Gunicorn      │
│  Static Files  │  │  (Port 8000)   │
└────────────────┘  └───────┬────────┘
                            │
                  ┌─────────┴─────────┐
                  │                   │
        ┌─────────▼────────┐  ┌───────▼────────┐
        │  PostgreSQL      │  │  Redis         │
        │  (Port 5432)     │  │  (Port 6379)   │
        └──────────────────┘  └───────┬────────┘
                                      │
                            ┌─────────▼────────┐
                            │  Celery Worker   │
                            │  (Background)    │
                            └──────────────────┘
```

---

## ✅ Why This Stack?

| Benefit | Django + Next.js | Node.js + React |
|---------|------------------|-----------------|
| **Security** | ✅ Built-in | ⚠️ Manual config |
| **Admin Interface** | ✅ Automatic | ❌ Build from scratch |
| **ORM Maturity** | ✅ Excellent | ⚠️ Good |
| **Audit Trails** | ✅ Built-in | ❌ Custom |
| **Medical Libraries** | ✅ HL7/FHIR | ⚠️ Limited |
| **University Adoption** | ✅ Standard | ⚠️ Less common |
| **SSR/SEO** | ✅ Next.js | ⚠️ Manual setup |
| **Development Speed** | ✅ Very Fast | ⚠️ Fast |

---

## 📋 Approved Configuration

✅ **Backend**: Django 5.x + DRF + PostgreSQL  
✅ **Frontend**: Next.js 14+ with App Router  
✅ **State Management**: React Query (TanStack Query)  
✅ **Repository**: Monorepo (single repo)  
✅ **Deployment**: VPS (local testing first)  
✅ **Authentication**: Google Workspace SSO  
✅ **Email**: Google Workspace SMTP  

---

## 🚀 Next Steps

**I will now proceed to:**

1. ✅ Create monorepo structure (`/backend` and `/frontend`)
2. ✅ Initialize Django project with PostgreSQL configuration
3. ✅ Configure Google Workspace SSO (django-allauth)
4. ✅ Configure Google Workspace SMTP
5. ✅ Initialize Next.js project with App Router
6. ✅ Configure NextAuth.js with Google Provider
7. ✅ Implement authentication flow (SSO + JWT)
8. ✅ Create core Django models
9. ✅ Build API endpoints
10. ✅ Build Next.js dashboard pages

**Ready to start building! 🚀**

---

## 📞 Google Workspace Configuration Needed

Before I start, please provide:

1. **Google Workspace Domain**: Your hospital domain (e.g., `yourhospital.com`)
2. **OAuth Client ID & Secret**: From Google Cloud Console (I can guide you through creating this)
3. **SMTP Email Address**: The email to send from (e.g., `noreply@yourhospital.com`)
4. **SMTP App Password**: Google Workspace app password for SMTP

*Don't worry if you don't have these yet - I'll create placeholder configurations and provide step-by-step instructions to set them up.*
