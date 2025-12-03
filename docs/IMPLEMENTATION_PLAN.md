# Hospital Consult System - Implementation Plan

## Overview

This document outlines the complete implementation plan for the Hospital Consult System using:
- **Backend**: Django 5.x + Django REST Framework + PostgreSQL
- **Frontend**: Next.js 14+ with App Router + React Query
- **Authentication**: Google Workspace SSO (OAuth 2.0)
- **Email**: Google Workspace SMTP
- **Deployment**: VPS (local testing first)
- **Repository**: Monorepo structure

---

## Phase 1: Foundation & Authentication (Week 1-2)

### 1.1 Monorepo Setup

**Folder Structure**
```
consult/
├── README.md
├── .gitignore
├── docker-compose.yml (optional)
├── backend/
└── frontend/
```

**Tasks**
- Create root directory structure
- Initialize Git repository
- Create comprehensive `.gitignore`
- Write project README

### 1.2 Backend: Django Project Setup

**Installation**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install django djangorestframework django-cors-headers
pip install psycopg2-binary python-decouple djangorestframework-simplejwt
pip install django-allauth dj-rest-auth
pip install celery redis django-channels channels-redis
```

**Django Project Structure**
```
backend/
├── manage.py
├── requirements.txt
├── .env.example
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── apps/
    └── (will be created in Phase 2)
```

**Database Configuration**
```python
# config/settings/development.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# config/settings/production.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}
```

**CORS Configuration**
```python
# config/settings/base.py
INSTALLED_APPS = [
    # ...
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'dj_rest_auth',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    # ... other middleware
]

# Development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]

# Production (will be updated)
CORS_ALLOWED_ORIGINS = [
    "https://consult.yourhospital.com",
]
```

### 1.3 Backend: Google Workspace SSO Configuration

**Install Dependencies**
```bash
pip install django-allauth[socialaccount]
```

**Django Settings**
```python
# config/settings/base.py

INSTALLED_APPS = [
    # ...
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'dj_rest_auth',
    'dj_rest_auth.registration',
]

SITE_ID = 1

# Allauth Configuration
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_USERNAME_REQUIRED = False

# Social Account Configuration
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
            'hd': 'yourhospital.com',  # Restrict to your domain
        },
        'APP': {
            'client_id': config('GOOGLE_OAUTH_CLIENT_ID'),
            'secret': config('GOOGLE_OAUTH_CLIENT_SECRET'),
            'key': ''
        }
    }
}

# JWT Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}
```

**Custom User Model**
```python
# apps/accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('DOCTOR', 'Doctor'),
        ('DEPARTMENT_USER', 'Department User'),
        ('HOD', 'Head of Department'),
        ('ADMIN', 'Administrator'),
    ]
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='DOCTOR')
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    seniority_level = models.IntegerField(default=1)
    phone_number = models.CharField(max_length=20, blank=True)
    profile_photo = models.URLField(blank=True)  # From Google
    is_on_call = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        ordering = ['department', '-seniority_level']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
```

**Email Domain Validation**
```python
# apps/accounts/signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import User

@receiver(pre_save, sender=User)
def validate_email_domain(sender, instance, **kwargs):
    """Ensure only hospital domain emails are allowed"""
    allowed_domain = 'yourhospital.com'
    if instance.email and not instance.email.endswith(f'@{allowed_domain}'):
        raise ValidationError(
            f'Only {allowed_domain} email addresses are allowed.'
        )
```

### 1.4 Backend: Google Workspace SMTP Configuration

**Email Settings**
```python
# config/settings/base.py

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')  # e.g., noreply@yourhospital.com
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')  # App password
DEFAULT_FROM_EMAIL = f'Hospital Consult System <{EMAIL_HOST_USER}>'
SERVER_EMAIL = EMAIL_HOST_USER

# Email Templates Directory
EMAIL_TEMPLATES_DIR = BASE_DIR / 'templates' / 'emails'
```

**Email Service**
```python
# apps/core/services/email_service.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

class EmailService:
    @staticmethod
    def send_new_consult_notification(consult):
        """Send email when new consult is created"""
        subject = f'New {consult.urgency} Consult Request'
        message = render_to_string('emails/new_consult.html', {
            'consult': consult,
            'patient': consult.patient,
            'requester': consult.requester,
        })
        
        recipient_list = [consult.target_department.head.email]
        
        send_mail(
            subject=subject,
            message='',  # Plain text fallback
            html_message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
    
    @staticmethod
    def send_overdue_escalation(consult):
        """Send escalation email for overdue consults"""
        subject = f'URGENT: Overdue Consult #{consult.id}'
        message = render_to_string('emails/overdue_escalation.html', {
            'consult': consult,
        })
        
        # Send to HOD
        recipient_list = [consult.target_department.head.email]
        
        send_mail(
            subject=subject,
            message='',
            html_message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
```

### 1.5 Frontend: Next.js Setup

**Installation**
```bash
npx create-next-app@latest frontend --typescript --app --tailwind
cd frontend
npm install @tanstack/react-query axios next-auth
npm install @heroicons/react date-fns
```

**Project Structure**
```
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── login/
│   │   └── page.tsx
│   ├── dashboard/
│   │   └── page.tsx
│   ├── api/
│   │   └── auth/
│   │       └── [...nextauth]/
│   │           └── route.ts
│   └── providers.tsx
├── components/
├── lib/
│   ├── api/
│   ├── hooks/
│   └── utils/
├── public/
├── .env.local.example
└── next.config.js
```

**Environment Variables**
```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key-here
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### 1.6 Frontend: NextAuth.js Configuration

**NextAuth Configuration**
```typescript
// app/api/auth/[...nextauth]/route.ts
import NextAuth from 'next-auth';
import GoogleProvider from 'next-auth/providers/google';

const handler = NextAuth({
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      authorization: {
        params: {
          hd: 'yourhospital.com', // Restrict to your domain
          prompt: 'consent',
          access_type: 'offline',
          response_type: 'code',
        },
      },
    }),
  ],
  callbacks: {
    async signIn({ user, account, profile }) {
      // Validate email domain
      if (!user.email?.endsWith('@yourhospital.com')) {
        return false;
      }
      
      // Send user data to Django backend
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/google/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: user.email,
          name: user.name,
          image: user.image,
          google_id: account?.providerAccountId,
        }),
      });
      
      const data = await response.json();
      
      // Store JWT token
      if (data.access_token) {
        user.accessToken = data.access_token;
        user.role = data.user.role;
        user.department = data.user.department;
      }
      
      return true;
    },
    async jwt({ token, user }) {
      if (user) {
        token.accessToken = user.accessToken;
        token.role = user.role;
        token.department = user.department;
      }
      return token;
    },
    async session({ session, token }) {
      session.accessToken = token.accessToken;
      session.user.role = token.role;
      session.user.department = token.department;
      return session;
    },
  },
  pages: {
    signIn: '/login',
  },
});

export { handler as GET, handler as POST };
```

**Login Page**
```typescript
// app/login/page.tsx
'use client';

import { signIn } from 'next-auth/react';

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow">
        <div>
          <h2 className="text-center text-3xl font-bold">
            Hospital Consult System
          </h2>
          <p className="mt-2 text-center text-gray-600">
            Sign in with your hospital Google account
          </p>
        </div>
        
        <button
          onClick={() => signIn('google', { callbackUrl: '/dashboard' })}
          className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-md shadow-sm bg-white text-gray-700 hover:bg-gray-50"
        >
          <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
            {/* Google icon SVG */}
          </svg>
          Sign in with Google Workspace
        </button>
      </div>
    </div>
  );
}
```

**Protected Route Middleware**
```typescript
// middleware.ts
import { withAuth } from 'next-auth/middleware';

export default withAuth({
  callbacks: {
    authorized({ token }) {
      return !!token;
    },
  },
});

export const config = {
  matcher: ['/dashboard/:path*', '/admin/:path*', '/department/:path*'],
};
```

---

## Phase 2: Core Models & API (Week 3)

### 2.1 Django Apps Structure

**Create Apps**
```bash
cd backend
python manage.py startapp accounts
python manage.py startapp departments
python manage.py startapp patients
python manage.py startapp consults
python manage.py startapp notifications
python manage.py startapp analytics
python manage.py startapp core
```

### 2.2 Department Model & API

**Model** (already shown in TECHNICAL_PLAN.md)

**Serializers**
```python
# apps/departments/serializers.py
from rest_framework import serializers
from .models import Department

class DepartmentSerializer(serializers.ModelSerializer):
    head_name = serializers.CharField(source='head.get_full_name', read_only=True)
    user_count = serializers.IntegerField(source='users.count', read_only=True)
    
    class Meta:
        model = Department
        fields = '__all__'
```

**ViewSet**
```python
# apps/departments/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Department
from .serializers import DepartmentSerializer

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == 'ADMIN':
            return Department.objects.all()
        return Department.objects.filter(is_active=True)
```

### 2.3 Patient Model & API

(Similar structure to Department)

### 2.4 ConsultRequest Model & API

(Already detailed in TECHNICAL_PLAN.md)

---

## Phase 3: Consult Workflow (Week 4-5)

### 3.1 Service Layer Implementation

(Already detailed in TECHNICAL_PLAN.md)

### 3.2 Email Notifications

**Email Templates**
```html
<!-- templates/emails/new_consult.html -->
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; }
        .header { background: #2563eb; color: white; padding: 20px; }
        .content { padding: 20px; }
        .urgency-emergency { color: #dc2626; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h2>New Consult Request</h2>
    </div>
    <div class="content">
        <p><strong>Urgency:</strong> <span class="urgency-{{ consult.urgency|lower }}">{{ consult.urgency }}</span></p>
        <p><strong>Patient:</strong> {{ patient.name }} (MRN: {{ patient.mrn }})</p>
        <p><strong>Location:</strong> {{ patient.ward }}, Bed {{ patient.bed_number }}</p>
        <p><strong>Requested by:</strong> {{ requester.get_full_name }}</p>
        <p><strong>Reason:</strong> {{ consult.reason_for_consult }}</p>
        
        <p><a href="https://consult.yourhospital.com/consults/{{ consult.id }}">View Consult</a></p>
    </div>
</body>
</html>
```

### 3.3 Frontend Components

**React Query Setup**
```typescript
// app/providers.tsx
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { SessionProvider } from 'next-auth/react';
import { useState } from 'react';

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient());
  
  return (
    <SessionProvider>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </SessionProvider>
  );
}
```

**API Client**
```typescript
// lib/api/client.ts
import axios from 'axios';
import { getSession } from 'next-auth/react';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
});

// Add JWT token to requests
apiClient.interceptors.request.use(async (config) => {
  const session = await getSession();
  if (session?.accessToken) {
    config.headers.Authorization = `Bearer ${session.accessToken}`;
  }
  return config;
});

export default apiClient;
```

**Consult Hooks**
```typescript
// lib/hooks/useConsults.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../api/client';

export function useConsults(filter?: string) {
  return useQuery({
    queryKey: ['consults', filter],
    queryFn: async () => {
      const { data } = await apiClient.get('/consults/', {
        params: { filter },
      });
      return data;
    },
  });
}

export function useCreateConsult() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (consultData) => {
      const { data } = await apiClient.post('/consults/', consultData);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['consults'] });
    },
  });
}
```

---

## Phase 4: Real-time Features (Week 6)

### 4.1 Django Channels Setup

**Installation**
```bash
pip install channels channels-redis
```

**Configuration**
```python
# config/settings/base.py
INSTALLED_APPS = [
    # ...
    'channels',
]

ASGI_APPLICATION = 'config.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}
```

**WebSocket Consumer**
```python
# apps/notifications/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.group_name = f'user_{self.user.id}'
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    
    async def notification(self, event):
        await self.send(text_data=json.dumps(event['data']))
```

### 4.2 Frontend WebSocket

```typescript
// lib/hooks/useWebSocket.ts
import { useEffect, useState } from 'react';
import { useSession } from 'next-auth/react';

export function useWebSocket() {
  const { data: session } = useSession();
  const [notifications, setNotifications] = useState([]);
  
  useEffect(() => {
    if (!session?.accessToken) return;
    
    const ws = new WebSocket(
      `ws://localhost:8000/ws/notifications/?token=${session.accessToken}`
    );
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setNotifications(prev => [data, ...prev]);
      
      // Show browser notification
      if (Notification.permission === 'granted') {
        new Notification(data.title, { body: data.message });
      }
    };
    
    return () => ws.close();
  }, [session]);
  
  return { notifications };
}
```

---

## Phase 5-7: Advanced Features, Testing, Deployment

(Detailed in TECHNICAL_PLAN.md)

---

## Google Workspace Setup Requirements

### What You Need to Provide

1. **Google Workspace Domain**
   - Your hospital domain (e.g., `yourhospital.com`)

2. **Google Cloud Console Setup**
   - Create OAuth 2.0 credentials
   - Get Client ID and Client Secret
   - Configure authorized redirect URIs

3. **SMTP Configuration**
   - Email address for sending (e.g., `noreply@yourhospital.com`)
   - Generate App Password for SMTP

See [GOOGLE_WORKSPACE_SETUP.md](./GOOGLE_WORKSPACE_SETUP.md) for detailed instructions.

---

## Next Steps

1. Review this implementation plan
2. Provide Google Workspace configuration details
3. Begin Phase 1 implementation
4. Test authentication flow
5. Proceed to Phase 2

**Ready to start building! 🚀**
