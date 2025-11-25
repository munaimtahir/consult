# Hospital Consult System - System Architecture

## 1. High-Level Overview
The system will be a web-based application with a responsive frontend for doctors (accessible via desktop and mobile browsers) and a robust backend API managing data consistency, real-time updates, and business logic.

## 2. Technology Stack

### Frontend (Client-Side)
*   **Framework**: React.js (using Vite for fast build times).
*   **Language**: TypeScript (for type safety and maintainability).
*   **Styling**: Tailwind CSS (for rapid, responsive, and modern UI development).
*   **State Management**: React Query (server state) + Context API (local state).
*   **Real-time**: Socket.io Client (for instant notifications).

### Backend (Server-Side)
*   **Runtime**: Node.js.
*   **Framework**: Express.js (lightweight and flexible) or NestJS (structured and scalable). *Recommendation: Express.js for speed of development.*
*   **Language**: TypeScript.
*   **Real-time**: Socket.io Server (handling events like `NEW_CONSULT`, `STATUS_UPDATE`).
*   **Authentication**: JWT (JSON Web Tokens) for secure stateless authentication.

### Database
*   **Primary DB**: PostgreSQL.
    *   *Reason*: Relational data integrity is crucial for patient records, department hierarchies, and audit logs.
*   **ORM**: Prisma (for type-safe database access and easy migrations).

## 3. System Components

### A. API Gateway / Load Balancer
*   Entry point for all client requests.
*   Handles SSL termination and basic rate limiting.

### B. Application Server
*   **Auth Service**: Handles Login, Registration, Password Reset.
*   **Consult Service**: Manages creation, assignment, and status updates of consults.
*   **Notification Service**: Listens to events and pushes updates via WebSockets.
*   **Master Data Service**: Manages Departments, Users, and Configurations.

### C. Data Layer
*   **Users Table**: Stores credentials and roles.
*   **Patients Table**: Stores manual patient entries.
*   **Consults Table**: Stores request details, timestamps, and urgency.
*   **Notes Table**: Stores clinical responses.
*   **AuditLog Table**: Tracks every action for accountability.

## 4. Data Flow Example: New Consult
1.  **Client**: User submits "New Consult" form.
2.  **API**: Validates data (required fields, valid department).
3.  **DB**: Saves new `ConsultRequest` record with status `PENDING`.
4.  **Event**: Backend emits `CONSULT_CREATED` event to the specific `DepartmentRoom`.
5.  **Socket**: Connected clients in that department receive the alert instantly.
6.  **Client**: UI updates to show the new request in the "Incoming" list.

## 5. Security Considerations
*   **Data Encryption**: TLS for data in transit.
*   **Access Control**: Role-Based Access Control (RBAC) middleware to ensure only authorized users can view/edit specific consults.
*   **Audit Trails**: Immutable logs of who accessed what patient data and when.
