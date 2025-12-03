# Hospital Consult System - Technical Plan (Django + React)

## Executive Summary

This document defines the complete technical architecture for the Hospital Consult System using a **Django REST Framework backend** and **React frontend**. This stack is specifically chosen for healthcare/university management systems due to its security, stability, auditability, and rapid development capabilities.

---

## 1. Why Django + React for Hospital Systems?

### Backend: Django + Django REST Framework

**Security & Compliance**
- **Built-in Security**: Django provides CSRF protection, SQL injection prevention, XSS protection, and clickjacking protection out of the box
- **Auditable**: Django Admin provides automatic audit trails for all model changes
- **HIPAA-Ready**: Django's security features align with healthcare compliance requirements
- **Mature Authentication**: Django's auth system is battle-tested with role-based permissions built-in

**Stability & Maintainability**
- **Batteries Included**: Admin interface, ORM, migrations, and authentication come standard
- **Long-term Support**: Django LTS releases ensure stability for critical healthcare systems
- **Python Ecosystem**: Access to medical libraries (HL7, FHIR parsers) and data science tools
- **Clear Architecture**: Django's MVT pattern enforces clean separation of concerns

**Development Speed**
- **Rapid Prototyping**: Django Admin allows immediate CRUD operations without building admin UIs
- **ORM Power**: Complex medical queries are easier with Django's ORM vs raw SQL
- **Migration System**: Schema changes are tracked, versioned, and reversible
- **DRF (Django REST Framework)**: Industry-standard API framework with serialization, validation, and documentation

### Frontend: React

**Modern & Flexible**
- **Component Reusability**: Medical forms, patient cards, and consult lists can be modular components
- **Real-time Updates**: Easy integration with WebSockets for live notifications
- **Rich Ecosystem**: Access to medical UI libraries, charting tools, and form validators
- **Mobile-Ready**: React can be extended to React Native for native mobile apps in the future

### Why This Stack Beats Node.js for Hospitals

| Aspect | Django + React | Node.js + React |
|--------|----------------|-----------------|
| **Security** | Built-in, opinionated security | Requires manual configuration |
| **Admin Interface** | Automatic, production-ready | Must build from scratch |
| **ORM** | Mature, supports complex medical queries | Prisma/Sequelize less mature |
| **Audit Trails** | Built-in with Django Admin | Requires custom implementation |
| **Data Integrity** | Strong typing via Django models | Weaker guarantees |
| **Medical Integrations** | Python has HL7/FHIR libraries | Limited medical libraries |
| **University Adoption** | Python is standard in medical research | Less common in healthcare |

---

## 2. System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                            │
│                    (React Application)                      │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Doctor     │  │  Department  │  │    Admin     │    │
│  │  Dashboard   │  │  Dashboard   │  │   Dashboard  │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
│  Components: ConsultForm, ConsultList, PatientCard,        │
│              NotificationCenter, AnalyticsDashboard         │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ REST API (JSON)
                            │ WebSocket (Real-time)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                         BACKEND                             │
│              (Django + Django REST Framework)               │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    API Layer                         │  │
│  │  ViewSets: ConsultViewSet, UserViewSet,             │  │
│  │            DepartmentViewSet, AnalyticsViewSet       │  │
│  │  Serializers: Input validation & output formatting  │  │
│  │  Permissions: IsDoctor, IsDepartmentUser, IsAdmin   │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  Service Layer                       │  │
│  │  ConsultService: Business logic for consult workflow│  │
│  │  NotificationService: Real-time notifications       │  │
│  │  EscalationService: SLA monitoring & escalation     │  │
│  │  AnalyticsService: Metrics calculation              │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   Model Layer                        │  │
│  │  Models: User, Department, Patient,                 │  │
│  │          ConsultRequest, ConsultNote                │  │
│  │  Django ORM: Query optimization, transactions       │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Background Tasks (Celery)               │  │
│  │  - SLA monitoring (check overdue consults)          │  │
│  │  - Email notifications                              │  │
│  │  - Analytics aggregation                            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATABASE LAYER                         │
│                                                             │
│  Production: PostgreSQL 14+                                │
│  Development: SQLite (local testing only)                  │
│                                                             │
│  Tables: auth_user, departments, patients,                 │
│          consult_requests, consult_notes                   │
└─────────────────────────────────────────────────────────────┘
```

### API-First Design Principles

1. **Stateless REST API**: All client-server communication via JSON REST endpoints
2. **JWT Authentication**: Token-based auth for mobile and web clients
3. **Versioned APIs**: `/api/v1/` namespace for future compatibility
4. **Consistent Response Format**: Standardized success/error responses
5. **Comprehensive Documentation**: Auto-generated API docs via DRF's Spectacular/Swagger

---

## 3. Backend Architecture (Django)

### Project Structure

```
backend/
├── manage.py
├── requirements.txt
├── .env.example
├── config/                      # Django project settings
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py             # Common settings
│   │   ├── development.py      # SQLite, DEBUG=True
│   │   ├── production.py       # PostgreSQL, DEBUG=False
│   │   └── test.py             # Test configuration
│   ├── urls.py                 # Root URL configuration
│   ├── wsgi.py
│   └── asgi.py                 # For WebSocket support
│
├── apps/
│   ├── accounts/               # User & Authentication
│   │   ├── models.py           # Custom User model
│   │   ├── serializers.py      # User serializers
│   │   ├── views.py            # Auth endpoints
│   │   ├── permissions.py      # Custom permissions
│   │   └── admin.py            # User admin interface
│   │
│   ├── departments/            # Department Management
│   │   ├── models.py           # Department model
│   │   ├── serializers.py
│   │   ├── views.py            # CRUD endpoints
│   │   └── admin.py
│   │
│   ├── patients/               # Patient Management
│   │   ├── models.py           # Patient model
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── admin.py
│   │
│   ├── consults/               # Core Consult System
│   │   ├── models.py           # ConsultRequest, ConsultNote
│   │   ├── serializers.py
│   │   ├── views.py            # Consult CRUD + workflow
│   │   ├── services.py         # Business logic
│   │   ├── signals.py          # Post-save hooks for notifications
│   │   ├── filters.py          # Query filters
│   │   ├── permissions.py      # Consult-specific permissions
│   │   └── admin.py
│   │
│   ├── notifications/          # Real-time Notifications
│   │   ├── models.py           # Notification model
│   │   ├── consumers.py        # WebSocket consumers
│   │   ├── services.py         # Notification logic
│   │   └── routing.py          # WebSocket routing
│   │
│   ├── analytics/              # Analytics & Reporting
│   │   ├── views.py            # Analytics endpoints
│   │   ├── services.py         # Metrics calculation
│   │   └── serializers.py
│   │
│   └── core/                   # Shared utilities
│       ├── models.py           # Abstract base models
│       ├── permissions.py      # Base permissions
│       ├── pagination.py       # Custom pagination
│       └── exceptions.py       # Custom exceptions
│
└── tasks/                      # Celery background tasks
    ├── __init__.py
    ├── celery.py               # Celery configuration
    ├── escalation.py           # SLA monitoring tasks
    └── notifications.py        # Email notification tasks
```

### Django Models (ORM)

#### User Model (Custom)
```python
# apps/accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Custom user model with hospital-specific fields"""
    ROLE_CHOICES = [
        ('RESIDENT', 'Resident'),
        ('CONSULTANT', 'Consultant'),
        ('HOD', 'Head of Department'),
        ('ADMIN', 'Administrator'),
    ]
    
    department = models.ForeignKey('departments.Department', on_delete=models.SET_NULL, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    seniority_level = models.IntegerField(default=1)  # For escalation hierarchy
    phone_number = models.CharField(max_length=20, blank=True)
    is_on_call = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'users'
        ordering = ['department', '-seniority_level']
```

#### Department Model
```python
# apps/departments/models.py
from django.db import models

class Department(models.Model):
    """Medical department/specialty"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)  # e.g., "CARDIO"
    head = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='headed_departments')
    contact_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    
    # SLA Configuration (in minutes)
    emergency_sla = models.IntegerField(default=60)      # 1 hour
    urgent_sla = models.IntegerField(default=240)        # 4 hours
    routine_sla = models.IntegerField(default=1380)      # 23 hours
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'departments'
        ordering = ['name']
```

#### Patient Model
```python
# apps/patients/models.py
from django.db import models

class Patient(models.Model):
    """Patient information (manually entered)"""
    mrn = models.CharField(max_length=50, unique=True)  # Medical Record Number
    name = models.CharField(max_length=200)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    ward = models.CharField(max_length=100)
    bed_number = models.CharField(max_length=20)
    primary_department = models.ForeignKey('departments.Department', on_delete=models.PROTECT)
    primary_diagnosis = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'patients'
        ordering = ['-created_at']
```

#### ConsultRequest Model
```python
# apps/consults/models.py
from django.db import models
from django.utils import timezone
from datetime import timedelta

class ConsultRequest(models.Model):
    """Core consult request entity"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ASSIGNED', 'Assigned'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('ESCALATED', 'Escalated'),
        ('FOLLOW_UP', 'Follow-up'),
    ]
    
    URGENCY_CHOICES = [
        ('EMERGENCY', 'Emergency'),
        ('URGENT', 'Urgent'),
        ('ROUTINE', 'Routine'),
    ]
    
    FOLLOW_UP_CHOICES = [
        ('NONE', 'None'),
        ('REGULAR', 'Regular Daily'),
        ('CONDITIONAL', 'Conditional'),
    ]
    
    # Relationships
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='consults')
    requester = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='requested_consults')
    target_department = models.ForeignKey('departments.Department', on_delete=models.PROTECT, related_name='incoming_consults')
    assigned_doctor = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_consults')
    
    # Request Details
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    clinical_details = models.TextField()
    reason_for_consult = models.TextField()
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    due_by = models.DateTimeField()  # Calculated based on urgency
    first_response_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Follow-up
    follow_up_type = models.CharField(max_length=20, choices=FOLLOW_UP_CHOICES, default='NONE')
    follow_up_instructions = models.TextField(blank=True)
    
    class Meta:
        db_table = 'consult_requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'target_department']),
            models.Index(fields=['assigned_doctor', 'status']),
            models.Index(fields=['urgency', 'created_at']),
        ]
    
    def save(self, *args, **kwargs):
        # Auto-calculate due_by if not set
        if not self.due_by:
            sla_minutes = {
                'EMERGENCY': self.target_department.emergency_sla,
                'URGENT': self.target_department.urgent_sla,
                'ROUTINE': self.target_department.routine_sla,
            }
            self.due_by = timezone.now() + timedelta(minutes=sla_minutes[self.urgency])
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        return timezone.now() > self.due_by and self.status not in ['COMPLETED']
    
    @property
    def response_time_minutes(self):
        if self.first_response_at:
            return (self.first_response_at - self.created_at).total_seconds() / 60
        return None
```

#### ConsultNote Model
```python
# apps/consults/models.py
class ConsultNote(models.Model):
    """Medical notes/responses to consults"""
    consult_request = models.ForeignKey(ConsultRequest, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey('accounts.User', on_delete=models.PROTECT)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'consult_notes'
        ordering = ['created_at']
```

### Service Layer Pattern

```python
# apps/consults/services.py
from django.utils import timezone
from .models import ConsultRequest, ConsultNote
from apps.notifications.services import NotificationService

class ConsultService:
    """Business logic for consult workflow"""
    
    @staticmethod
    def create_consult(requester, patient, target_department, urgency, clinical_details, reason):
        """Create a new consult request"""
        consult = ConsultRequest.objects.create(
            patient=patient,
            requester=requester,
            target_department=target_department,
            urgency=urgency,
            clinical_details=clinical_details,
            reason_for_consult=reason,
        )
        
        # Send real-time notification to target department
        NotificationService.notify_new_consult(consult)
        
        return consult
    
    @staticmethod
    def assign_consult(consult, doctor):
        """Assign consult to a specific doctor"""
        consult.assigned_doctor = doctor
        consult.status = 'ASSIGNED'
        consult.save()
        
        NotificationService.notify_consult_assigned(consult, doctor)
        
        return consult
    
    @staticmethod
    def add_note(consult, author, content):
        """Add a consult note and update timestamps"""
        note = ConsultNote.objects.create(
            consult_request=consult,
            author=author,
            content=content
        )
        
        # Update first_response_at if this is the first note
        if not consult.first_response_at:
            consult.first_response_at = timezone.now()
            consult.status = 'IN_PROGRESS'
            consult.save()
        
        NotificationService.notify_note_added(consult, note)
        
        return note
    
    @staticmethod
    def complete_consult(consult, follow_up_type='NONE', follow_up_instructions=''):
        """Mark consult as completed or move to follow-up"""
        if follow_up_type == 'NONE':
            consult.status = 'COMPLETED'
            consult.completed_at = timezone.now()
        else:
            consult.status = 'FOLLOW_UP'
            consult.follow_up_type = follow_up_type
            consult.follow_up_instructions = follow_up_instructions
        
        consult.save()
        NotificationService.notify_consult_completed(consult)
        
        return consult
```

### API Endpoints (Django REST Framework)

#### Authentication Endpoints
```
POST   /api/v1/auth/login/              # Login (returns JWT token)
POST   /api/v1/auth/logout/             # Logout
POST   /api/v1/auth/refresh/            # Refresh JWT token
GET    /api/v1/auth/me/                 # Get current user profile
PUT    /api/v1/auth/me/                 # Update current user profile
POST   /api/v1/auth/change-password/    # Change password
```

#### User Management (Admin only)
```
GET    /api/v1/users/                   # List all users
POST   /api/v1/users/                   # Create user
GET    /api/v1/users/{id}/              # Get user details
PUT    /api/v1/users/{id}/              # Update user
DELETE /api/v1/users/{id}/              # Deactivate user
GET    /api/v1/users/on-call/           # List on-call doctors
```

#### Department Management
```
GET    /api/v1/departments/             # List departments
POST   /api/v1/departments/             # Create department (Admin)
GET    /api/v1/departments/{id}/        # Get department details
PUT    /api/v1/departments/{id}/        # Update department (Admin)
DELETE /api/v1/departments/{id}/        # Deactivate department (Admin)
GET    /api/v1/departments/{id}/staff/  # List department staff
```

#### Patient Management
```
GET    /api/v1/patients/                # List patients (paginated)
POST   /api/v1/patients/                # Create patient (manual entry)
GET    /api/v1/patients/{id}/           # Get patient details
PUT    /api/v1/patients/{id}/           # Update patient
GET    /api/v1/patients/{id}/consults/  # Get patient's consult history
GET    /api/v1/patients/search/?q=      # Search patients by MRN/name
```

#### Consult Management (Core)
```
GET    /api/v1/consults/                # List consults (filtered by role)
POST   /api/v1/consults/                # Create new consult request
GET    /api/v1/consults/{id}/           # Get consult details
PUT    /api/v1/consults/{id}/           # Update consult
DELETE /api/v1/consults/{id}/           # Cancel consult (requester only)

# Workflow Actions
POST   /api/v1/consults/{id}/assign/    # Assign to doctor
POST   /api/v1/consults/{id}/notes/     # Add consult note
POST   /api/v1/consults/{id}/complete/  # Mark as completed
POST   /api/v1/consults/{id}/escalate/  # Manual escalation

# Filtering & Views
GET    /api/v1/consults/my-requests/    # Consults I requested
GET    /api/v1/consults/assigned-to-me/ # Consults assigned to me
GET    /api/v1/consults/incoming/       # Incoming to my department
GET    /api/v1/consults/overdue/        # Overdue consults
GET    /api/v1/consults/follow-up/      # Follow-up consults
```

#### Notifications
```
GET    /api/v1/notifications/           # List my notifications
PUT    /api/v1/notifications/{id}/read/ # Mark as read
PUT    /api/v1/notifications/read-all/  # Mark all as read
WS     /ws/notifications/               # WebSocket for real-time updates
```

#### Analytics & Reporting
```
GET    /api/v1/analytics/dashboard/                    # Overview metrics
GET    /api/v1/analytics/department/{id}/              # Department-specific metrics
GET    /api/v1/analytics/consult-volume/               # Volume over time
GET    /api/v1/analytics/response-times/               # Average response times
GET    /api/v1/analytics/sla-compliance/               # SLA compliance rate
GET    /api/v1/analytics/export/?format=csv|pdf        # Export reports
```

### Role-Based Permissions

```python
# apps/core/permissions.py
from rest_framework import permissions

class IsDoctor(permissions.BasePermission):
    """Allow access only to doctors"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['RESIDENT', 'CONSULTANT', 'HOD']

class IsDepartmentUser(permissions.BasePermission):
    """Allow access to users in the target department"""
    def has_object_permission(self, request, view, obj):
        return obj.target_department == request.user.department

class IsConsultRequester(permissions.BasePermission):
    """Allow access to the user who created the consult"""
    def has_object_permission(self, request, view, obj):
        return obj.requester == request.user

class IsAssignedDoctor(permissions.BasePermission):
    """Allow access to the assigned doctor"""
    def has_object_permission(self, request, view, obj):
        return obj.assigned_doctor == request.user

class IsAdminUser(permissions.BasePermission):
    """Allow access only to admins"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADMIN'
```

### Background Tasks (Celery)

```python
# tasks/escalation.py
from celery import shared_task
from django.utils import timezone
from apps.consults.models import ConsultRequest
from apps.notifications.services import NotificationService

@shared_task
def check_overdue_consults():
    """Run every 15 minutes to check for overdue consults"""
    overdue_consults = ConsultRequest.objects.filter(
        status__in=['PENDING', 'ASSIGNED', 'IN_PROGRESS'],
        due_by__lt=timezone.now()
    )
    
    for consult in overdue_consults:
        if consult.status != 'ESCALATED':
            consult.status = 'ESCALATED'
            consult.save()
            
            # Notify HOD
            NotificationService.escalate_to_hod(consult)

@shared_task
def send_daily_follow_up_reminders():
    """Run daily at 8 AM to remind about follow-up consults"""
    follow_up_consults = ConsultRequest.objects.filter(
        status='FOLLOW_UP',
        follow_up_type='REGULAR'
    )
    
    for consult in follow_up_consults:
        NotificationService.send_follow_up_reminder(consult)
```

---

## 4. Frontend Architecture (React)

### Project Structure

```
frontend/
├── package.json
├── .env.example
├── vite.config.js              # Vite configuration
├── index.html
├── public/
│   └── assets/
│
└── src/
    ├── main.jsx                # Entry point
    ├── App.jsx                 # Root component
    │
    ├── api/                    # API client layer
    │   ├── client.js           # Axios instance with JWT interceptor
    │   ├── auth.js             # Auth API calls
    │   ├── consults.js         # Consult API calls
    │   ├── patients.js         # Patient API calls
    │   ├── departments.js      # Department API calls
    │   └── analytics.js        # Analytics API calls
    │
    ├── components/             # Reusable UI components
    │   ├── common/
    │   │   ├── Button.jsx
    │   │   ├── Input.jsx
    │   │   ├── Modal.jsx
    │   │   ├── Card.jsx
    │   │   ├── Badge.jsx
    │   │   ├── Spinner.jsx
    │   │   └── ErrorBoundary.jsx
    │   │
    │   ├── layout/
    │   │   ├── Navbar.jsx
    │   │   ├── Sidebar.jsx
    │   │   ├── Footer.jsx
    │   │   └── Layout.jsx
    │   │
    │   ├── consults/
    │   │   ├── ConsultCard.jsx         # Single consult display
    │   │   ├── ConsultList.jsx         # List of consults
    │   │   ├── ConsultForm.jsx         # Create/edit consult
    │   │   ├── ConsultDetail.jsx       # Full consult view
    │   │   ├── ConsultNoteForm.jsx     # Add note form
    │   │   ├── UrgencyBadge.jsx        # Visual urgency indicator
    │   │   └── StatusBadge.jsx         # Visual status indicator
    │   │
    │   ├── patients/
    │   │   ├── PatientCard.jsx
    │   │   ├── PatientForm.jsx
    │   │   └── PatientSearch.jsx
    │   │
    │   ├── notifications/
    │   │   ├── NotificationBell.jsx
    │   │   ├── NotificationList.jsx
    │   │   └── NotificationItem.jsx
    │   │
    │   └── analytics/
    │       ├── MetricCard.jsx
    │       ├── ConsultVolumeChart.jsx
    │       ├── ResponseTimeChart.jsx
    │       └── SLAComplianceChart.jsx
    │
    ├── pages/                  # Page-level components
    │   ├── auth/
    │   │   ├── LoginPage.jsx
    │   │   └── ProfilePage.jsx
    │   │
    │   ├── doctor/
    │   │   ├── DoctorDashboard.jsx     # My requests + assigned consults
    │   │   ├── NewConsultPage.jsx      # Create new consult
    │   │   └── ConsultDetailPage.jsx   # View/respond to consult
    │   │
    │   ├── department/
    │   │   ├── DepartmentDashboard.jsx # Incoming consults
    │   │   ├── IncomingConsults.jsx    # Triage view
    │   │   └── FollowUpConsults.jsx    # Follow-up pool
    │   │
    │   ├── admin/
    │   │   ├── AdminDashboard.jsx
    │   │   ├── UserManagement.jsx
    │   │   ├── DepartmentManagement.jsx
    │   │   └── SystemSettings.jsx
    │   │
    │   └── analytics/
    │       └── AnalyticsDashboard.jsx
    │
    ├── hooks/                  # Custom React hooks
    │   ├── useAuth.js          # Authentication state
    │   ├── useConsults.js      # Consult data fetching
    │   ├── useNotifications.js # Real-time notifications
    │   ├── useWebSocket.js     # WebSocket connection
    │   └── useAnalytics.js     # Analytics data
    │
    ├── context/                # React Context providers
    │   ├── AuthContext.jsx     # User authentication state
    │   ├── NotificationContext.jsx # Notification state
    │   └── ThemeContext.jsx    # UI theme (light/dark)
    │
    ├── utils/                  # Utility functions
    │   ├── formatters.js       # Date/time formatting
    │   ├── validators.js       # Form validation
    │   ├── constants.js        # App constants
    │   └── helpers.js          # General helpers
    │
    ├── styles/                 # Global styles
    │   ├── index.css           # Global CSS
    │   ├── variables.css       # CSS variables
    │   └── themes.css          # Theme definitions
    │
    └── router/                 # Routing configuration
        └── index.jsx           # React Router setup
```

### Key Frontend Features

#### 1. Authentication Flow
```jsx
// src/hooks/useAuth.js
import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../api/auth';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in on mount
    const token = localStorage.getItem('token');
    if (token) {
      authAPI.getMe().then(setUser).catch(() => logout());
    }
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    const { token, user } = await authAPI.login(username, password);
    localStorage.setItem('token', token);
    setUser(user);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
```

#### 2. Real-time Notifications (WebSocket)
```jsx
// src/hooks/useWebSocket.js
import { useEffect, useState } from 'react';
import { useAuth } from './useAuth';

export const useWebSocket = () => {
  const { user } = useAuth();
  const [socket, setSocket] = useState(null);
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    if (!user) return;

    const ws = new WebSocket(`ws://localhost:8000/ws/notifications/`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setNotifications(prev => [data, ...prev]);
      
      // Show browser notification
      if (Notification.permission === 'granted') {
        new Notification(data.title, { body: data.message });
      }
    };

    setSocket(ws);
    return () => ws.close();
  }, [user]);

  return { socket, notifications };
};
```

#### 3. Consult List Component
```jsx
// src/components/consults/ConsultList.jsx
import { useState, useEffect } from 'react';
import { consultsAPI } from '../../api/consults';
import ConsultCard from './ConsultCard';
import Spinner from '../common/Spinner';

const ConsultList = ({ filter = 'all' }) => {
  const [consults, setConsults] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchConsults = async () => {
      setLoading(true);
      const data = await consultsAPI.list({ filter });
      setConsults(data);
      setLoading(false);
    };
    
    fetchConsults();
  }, [filter]);

  if (loading) return <Spinner />;

  return (
    <div className="consult-list">
      {consults.map(consult => (
        <ConsultCard key={consult.id} consult={consult} />
      ))}
    </div>
  );
};

export default ConsultList;
```

### Component Hierarchy

```
App
├── AuthProvider
│   └── Router
│       ├── LoginPage
│       └── Layout (Protected)
│           ├── Navbar
│           │   └── NotificationBell
│           ├── Sidebar
│           └── Outlet
│               ├── DoctorDashboard
│               │   ├── ConsultList (My Requests)
│               │   └── ConsultList (Assigned to Me)
│               │
│               ├── DepartmentDashboard
│               │   ├── ConsultList (Incoming)
│               │   └── ConsultList (Follow-up)
│               │
│               ├── NewConsultPage
│               │   ├── PatientSearch
│               │   └── ConsultForm
│               │
│               ├── ConsultDetailPage
│               │   ├── ConsultDetail
│               │   └── ConsultNoteForm
│               │
│               └── AnalyticsDashboard
│                   ├── MetricCard (x4)
│                   ├── ConsultVolumeChart
│                   └── ResponseTimeChart
```

---

## 5. Data Flow & State Management

### Request Flow Example: Creating a Consult

```
┌──────────────┐
│   Doctor     │
│  Dashboard   │
└──────┬───────┘
       │ 1. Click "New Consult"
       ▼
┌──────────────┐
│ ConsultForm  │
│  Component   │
└──────┬───────┘
       │ 2. Fill form & submit
       ▼
┌──────────────┐
│  consultsAPI │
│   .create()  │
└──────┬───────┘
       │ 3. POST /api/v1/consults/
       ▼
┌──────────────────────────┐
│  Django REST Framework   │
│   ConsultViewSet         │
└──────┬───────────────────┘
       │ 4. Validate data
       ▼
┌──────────────────────────┐
│   ConsultService         │
│   .create_consult()      │
└──────┬───────────────────┘
       │ 5. Create ConsultRequest in DB
       │ 6. Trigger NotificationService
       ▼
┌──────────────────────────┐
│  NotificationService     │
│  .notify_new_consult()   │
└──────┬───────────────────┘
       │ 7. Send WebSocket message
       ▼
┌──────────────────────────┐
│  Target Department Users │
│  (WebSocket clients)     │
└──────┬───────────────────┘
       │ 8. Receive real-time notification
       ▼
┌──────────────────────────┐
│  NotificationBell        │
│  (Updates badge count)   │
└──────────────────────────┘
```

### State Management Strategy

**Local State (useState)**
- Form inputs
- UI toggles (modals, dropdowns)
- Component-specific loading states

**Context API**
- User authentication state
- Global notifications
- Theme preferences

**React Query / SWR (Recommended)**
- Server state caching
- Automatic refetching
- Optimistic updates
- Background synchronization

```jsx
// Example using React Query
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { consultsAPI } from '../api/consults';

export const useConsults = (filter) => {
  return useQuery({
    queryKey: ['consults', filter],
    queryFn: () => consultsAPI.list({ filter }),
    refetchInterval: 30000, // Refetch every 30 seconds
  });
};

export const useCreateConsult = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: consultsAPI.create,
    onSuccess: () => {
      // Invalidate and refetch consults
      queryClient.invalidateQueries({ queryKey: ['consults'] });
    },
  });
};
```

---

## 6. Security & Compliance

### Authentication & Authorization

1. **JWT Token Authentication**
   - Access token (15 min expiry)
   - Refresh token (7 days expiry)
   - Stored in httpOnly cookies (production) or localStorage (development)

2. **Role-Based Access Control (RBAC)**
   - Doctor: Can create consults, view assigned consults
   - Department User: Can view incoming consults, assign to doctors
   - HOD: All department permissions + analytics
   - Admin: Full system access

3. **Permission Checks**
   - Backend: Django REST Framework permissions on every endpoint
   - Frontend: Conditional rendering based on user role

### Data Security

1. **Encryption**
   - HTTPS/TLS for all API communication
   - Database encryption at rest (PostgreSQL native encryption)
   - Encrypted backups

2. **Input Validation**
   - Django REST Framework serializers validate all inputs
   - Frontend validation for UX (not security)
   - SQL injection prevention via Django ORM

3. **Audit Logging**
   - Django Admin logs all model changes
   - Custom audit trail for consult status changes
   - Timestamp all actions with user attribution

4. **HIPAA Compliance Considerations**
   - Auto-logout after 15 minutes of inactivity
   - Password complexity requirements
   - Access logs for patient data
   - Data retention policies

---

## 7. Database Design

### PostgreSQL Schema

```sql
-- Users (extends Django's auth_user)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254),
    password VARCHAR(128) NOT NULL,
    department_id INTEGER REFERENCES departments(id),
    role VARCHAR(20) NOT NULL,
    seniority_level INTEGER DEFAULT 1,
    phone_number VARCHAR(20),
    is_on_call BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    date_joined TIMESTAMP DEFAULT NOW()
);

-- Departments
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL,
    head_id INTEGER REFERENCES users(id),
    contact_number VARCHAR(20),
    emergency_sla INTEGER DEFAULT 60,
    urgent_sla INTEGER DEFAULT 240,
    routine_sla INTEGER DEFAULT 1380,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Patients
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    mrn VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    age INTEGER NOT NULL,
    gender VARCHAR(10) NOT NULL,
    ward VARCHAR(100),
    bed_number VARCHAR(20),
    primary_department_id INTEGER REFERENCES departments(id),
    primary_diagnosis TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Consult Requests
CREATE TABLE consult_requests (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    requester_id INTEGER REFERENCES users(id),
    target_department_id INTEGER REFERENCES departments(id),
    assigned_doctor_id INTEGER REFERENCES users(id),
    urgency VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING',
    clinical_details TEXT NOT NULL,
    reason_for_consult TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    due_by TIMESTAMP NOT NULL,
    first_response_at TIMESTAMP,
    completed_at TIMESTAMP,
    follow_up_type VARCHAR(20) DEFAULT 'NONE',
    follow_up_instructions TEXT
);

-- Indexes for performance
CREATE INDEX idx_consult_status_dept ON consult_requests(status, target_department_id);
CREATE INDEX idx_consult_assigned ON consult_requests(assigned_doctor_id, status);
CREATE INDEX idx_consult_urgency ON consult_requests(urgency, created_at);

-- Consult Notes
CREATE TABLE consult_notes (
    id SERIAL PRIMARY KEY,
    consult_request_id INTEGER REFERENCES consult_requests(id) ON DELETE CASCADE,
    author_id INTEGER REFERENCES users(id),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Database Optimization

1. **Indexing Strategy**
   - Index on `status` + `target_department_id` (most common query)
   - Index on `assigned_doctor_id` + `status`
   - Index on `urgency` + `created_at` (for SLA monitoring)

2. **Query Optimization**
   - Use `select_related()` for foreign keys to avoid N+1 queries
   - Use `prefetch_related()` for reverse foreign keys
   - Implement pagination (50 items per page)

3. **Connection Pooling**
   - Use PgBouncer for connection pooling in production
   - Configure Django's `CONN_MAX_AGE` for persistent connections

---

## 8. Deployment Architecture

### Development Environment
```
Backend:  Django dev server (SQLite)
Frontend: Vite dev server
Database: SQLite (local file)
```

### Production Environment
```
┌─────────────────────────────────────────────────────────┐
│                    Load Balancer (Nginx)                │
└─────────────────┬───────────────────────┬───────────────┘
                  │                       │
        ┌─────────▼─────────┐   ┌─────────▼─────────┐
        │  Frontend (React) │   │  Backend (Django) │
        │  Static Files     │   │  Gunicorn/uWSGI   │
        │  (Nginx/CDN)      │   │  + Celery Workers │
        └───────────────────┘   └─────────┬─────────┘
                                          │
                                ┌─────────▼─────────┐
                                │  PostgreSQL 14+   │
                                │  (Primary DB)     │
                                └───────────────────┘
                                          │
                                ┌─────────▼─────────┐
                                │  Redis            │
                                │  (Celery Broker)  │
                                │  (WebSocket)      │
                                └───────────────────┘
```

### Recommended Hosting

**Option 1: Single VPS (Small Hospital)**
- DigitalOcean/Linode Droplet (4GB RAM, 2 vCPUs)
- Docker Compose setup
- Cost: ~$20-40/month

**Option 2: Managed Services (Scalable)**
- Backend: Railway/Render (Django + Celery)
- Frontend: Vercel/Netlify (React)
- Database: Managed PostgreSQL (DigitalOcean/AWS RDS)
- Cost: ~$50-100/month

**Option 3: On-Premise (University Hospital)**
- Self-hosted on hospital servers
- Full data control
- Requires IT infrastructure

---

## 9. Development Workflow

### Phase 1: Foundation (Week 1-2)
- [ ] Setup Django project with PostgreSQL
- [ ] Configure Django REST Framework
- [ ] Implement User model and authentication
- [ ] Setup React project with Vite
- [ ] Create login page and protected routes
- [ ] Setup JWT authentication flow

### Phase 2: Core Models (Week 3)
- [ ] Implement Department model and API
- [ ] Implement Patient model and API
- [ ] Implement ConsultRequest model
- [ ] Implement ConsultNote model
- [ ] Create Django Admin interfaces
- [ ] Write model tests

### Phase 3: Consult Workflow (Week 4-5)
- [ ] Build consult creation API
- [ ] Build consult listing/filtering API
- [ ] Build consult assignment API
- [ ] Build note creation API
- [ ] Implement frontend consult forms
- [ ] Implement consult list views
- [ ] Implement consult detail view

### Phase 4: Real-time Features (Week 6)
- [ ] Setup Django Channels for WebSockets
- [ ] Implement notification system
- [ ] Build real-time notification UI
- [ ] Add browser push notifications
- [ ] Test real-time updates

### Phase 5: Advanced Features (Week 7-8)
- [ ] Implement SLA monitoring (Celery tasks)
- [ ] Implement escalation logic
- [ ] Build follow-up workflow
- [ ] Add analytics endpoints
- [ ] Build analytics dashboard
- [ ] Implement export functionality

### Phase 6: Polish & Testing (Week 9-10)
- [ ] Write comprehensive tests (80%+ coverage)
- [ ] Implement error handling
- [ ] Add loading states
- [ ] Mobile responsiveness
- [ ] Security audit
- [ ] Performance optimization

### Phase 7: Deployment (Week 11-12)
- [ ] Setup production environment
- [ ] Configure CI/CD pipeline
- [ ] Database migration strategy
- [ ] Backup and recovery plan
- [ ] User training documentation
- [ ] Go-live checklist

---

## 10. Testing Strategy

### Backend Testing (Django)
```python
# tests/test_consults.py
from django.test import TestCase
from apps.consults.models import ConsultRequest
from apps.consults.services import ConsultService

class ConsultServiceTest(TestCase):
    def setUp(self):
        # Create test users, departments, patients
        pass
    
    def test_create_consult_calculates_due_by(self):
        consult = ConsultService.create_consult(...)
        self.assertIsNotNone(consult.due_by)
    
    def test_emergency_consult_has_1_hour_sla(self):
        consult = ConsultService.create_consult(urgency='EMERGENCY', ...)
        expected_due = consult.created_at + timedelta(hours=1)
        self.assertEqual(consult.due_by, expected_due)
```

### Frontend Testing (React)
```jsx
// __tests__/ConsultForm.test.jsx
import { render, screen, fireEvent } from '@testing-library/react';
import ConsultForm from '../components/consults/ConsultForm';

test('submits consult form with valid data', async () => {
  render(<ConsultForm />);
  
  fireEvent.change(screen.getByLabelText('Patient Name'), {
    target: { value: 'John Doe' }
  });
  
  fireEvent.click(screen.getByText('Submit'));
  
  // Assert API was called
  expect(mockAPI.create).toHaveBeenCalledWith({
    patient_name: 'John Doe',
    ...
  });
});
```

### API Testing
- Use Django REST Framework's `APITestCase`
- Test all endpoints with different user roles
- Test permission checks
- Test validation errors

### End-to-End Testing
- Use Playwright or Cypress
- Test complete workflows (create consult → assign → respond → complete)
- Test real-time notifications

---

## 11. Monitoring & Maintenance

### Application Monitoring
- **Sentry**: Error tracking and performance monitoring
- **Django Debug Toolbar**: Development debugging
- **Prometheus + Grafana**: Metrics and dashboards

### Database Monitoring
- **pg_stat_statements**: Query performance analysis
- **pgAdmin**: Database administration
- **Automated backups**: Daily full backups, hourly incrementals

### Logging Strategy
```python
# config/settings/base.py
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
        },
    },
    'loggers': {
        'apps.consults': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

---

## 12. Future Enhancements

### Phase 2 Features (Post-Launch)
1. **Mobile Apps**: React Native apps for iOS/Android
2. **HL7/FHIR Integration**: Connect to hospital EMR systems
3. **Voice Notes**: Audio recording for consult notes
4. **Image Attachments**: Upload X-rays, ECGs, lab reports
5. **Telemedicine**: Video consultation integration
6. **AI Triage**: ML-based urgency classification
7. **Multi-language Support**: i18n for international hospitals
8. **Offline Mode**: PWA with offline capabilities

### Scalability Roadmap
- **Microservices**: Split into separate services (Auth, Consults, Analytics)
- **Caching**: Redis caching for frequently accessed data
- **CDN**: CloudFront/Cloudflare for static assets
- **Database Sharding**: Horizontal scaling for large hospitals

---

## 13. Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Data Loss** | Critical | Automated daily backups, transaction logging, point-in-time recovery |
| **Downtime** | High | Load balancing, health checks, auto-restart, 99.9% SLA monitoring |
| **Security Breach** | Critical | Penetration testing, security audits, encrypted data, access logs |
| **Slow Performance** | Medium | Database indexing, query optimization, caching, load testing |
| **User Adoption** | High | Comprehensive training, intuitive UI, gradual rollout, feedback loops |
| **Regulatory Compliance** | Critical | HIPAA compliance checklist, data retention policies, audit trails |

---

## 14. Success Metrics

### Technical KPIs
- **API Response Time**: < 200ms for 95% of requests
- **Database Query Time**: < 50ms average
- **Uptime**: 99.9% availability
- **Test Coverage**: > 80%
- **Security Vulnerabilities**: Zero critical/high

### Business KPIs
- **Consult Response Time**: 50% reduction vs paper-based
- **SLA Compliance**: > 90% consults responded within SLA
- **User Adoption**: > 80% of doctors using the system daily
- **Error Rate**: < 1% of consults have data errors
- **User Satisfaction**: > 4.5/5 rating

---

## 15. Conclusion

This Django + React architecture provides:

✅ **Security**: Built-in Django security features + RBAC  
✅ **Stability**: Battle-tested frameworks with LTS support  
✅ **Auditability**: Django Admin + comprehensive logging  
✅ **Scalability**: Proven architecture for hospital-scale systems  
✅ **Maintainability**: Clean separation of concerns, well-documented  
✅ **Compliance**: HIPAA-ready with encryption and access controls  
✅ **Developer Experience**: Rapid development with Django's batteries-included approach  

The system is designed to be:
- **Secure** from day one
- **Easy to audit** for compliance
- **Simple to maintain** with clear architecture
- **Ready to scale** as the hospital grows
- **Extensible** for future integrations (HL7, FHIR, EMR)

---

## Next Steps

**Before proceeding to implementation, please review and approve:**

1. ✅ Backend technology stack (Django + DRF + PostgreSQL)
2. ✅ Frontend technology stack (React + Vite)
3. ✅ Database schema and models
4. ✅ API endpoint design
5. ✅ Folder structure for both backend and frontend
6. ✅ Security and permission model
7. ✅ Deployment architecture
8. ✅ Development phases and timeline

**Questions for you:**

1. Do you prefer **React** or **Next.js** for the frontend? (Next.js adds SSR and better SEO)
2. Should we use **React Query** or **Redux** for state management?
3. Do you want a **monorepo** (single repo for backend + frontend) or **separate repos**?
4. What is your preferred deployment environment? (VPS, Cloud, On-Premise)
5. Do you need **email notifications** in addition to in-app notifications?

Once approved, I will begin implementing the backend and frontend code following this architecture.
