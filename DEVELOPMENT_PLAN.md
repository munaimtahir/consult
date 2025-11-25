# Hospital Consult System - Development Plan

This document outlines the staged approach to building the application.

## Phase 1: Foundation & Authentication
**Goal**: Set up the project structure and enable secure user access.
1.  **Repo Setup**: Initialize Monorepo (or separate folders) for Client and Server.
2.  **Database**: Setup PostgreSQL and Prisma Schema (Users, Departments).
3.  **API**: Implement Auth Routes (Login, Register, Me).
4.  **Frontend**: Create Login Page and Basic Layout (Sidebar, Navbar).

## Phase 2: Master Data Management
**Goal**: Allow Admins to configure the hospital structure.
1.  **API**: CRUD endpoints for `Departments` and `Users`.
2.  **Frontend**: Admin Dashboard to:
    *   Create Departments (e.g., "Cardiology").
    *   Create Users and assign them to Departments/Roles.

## Phase 3: Core Consult Workflow (The "Happy Path")
**Goal**: Enable the basic flow: Request -> Receive -> Reply.
1.  **API**:
    *   `POST /consults`: Create request.
    *   `GET /consults`: List requests (filtered by Dept/User).
    *   `POST /consults/:id/note`: Add a consult note.
2.  **Frontend**:
    *   "New Consult" Form (Manual Patient Entry).
    *   "Incoming Consults" List (for Departments).
    *   "My Requests" List (for Referrers).
    *   Consult Detail View (View info + Write Note).

## Phase 4: Real-time & Notifications
**Goal**: Make the system "Live".
1.  **Backend**: Integrate Socket.io. Emit events on creation and updates.
2.  **Frontend**:
    *   Toast notifications ("New Consult from ER!").
    *   Live update of the list without refreshing the page.
    *   Visual indicators for Urgency (Red for Emergency).

## Phase 5: Advanced Workflow & Polish
**Goal**: Implement the specific user feedback features.
1.  **Workflow**:
    *   Implement "Assign to Doctor" vs "Department Pool".
    *   Implement "Follow-up" vs "Complete" logic.
    *   Implement "Escalation" background jobs (Cron jobs to check overdue consults).
2.  **UI/UX**:
    *   Mobile responsiveness check.
    *   Loading states and Error handling.

## Phase 6: Analytics Dashboard
**Goal**: Provide live insights for HODs and Admins.
1.  **API**:
    *   `GET /analytics/department/:id`: Department-specific metrics.
    *   `GET /analytics/system`: System-wide metrics (Admin only).
    *   Aggregate queries for consult volume, response times, SLA compliance.
2.  **Frontend**:
    *   Dashboard page with charts (using Chart.js or Recharts).
    *   Metrics: Volume, Response Time, Status Distribution, SLA Compliance.
    *   Real-time updates via Socket.io.
    *   Export to CSV/PDF functionality.

## Phase 7: Testing & Deployment
1.  **QA**: End-to-end testing of the flow.
2.  **Deployment**:
    *   Deploy Backend (e.g., Railway/Render/VPS).
    *   Deploy Frontend (e.g., Vercel/Netlify).
    *   Seed initial data (Admin user, common departments).
