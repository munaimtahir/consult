# Hospital Consult System - Demo Script

## Pre-Demo Setup

Before the demo, ensure the system is running:
```bash
# Using Docker (recommended for demo)
docker-compose up -d

# Or locally:
cd backend && python manage.py runserver &
cd frontend && npm run dev &
```

## Demo Credentials

| Role | Email | Password | Permissions |
|------|-------|----------|-------------|
| **Superuser** | admin@pmc.edu.pk | adminpassword123 | Full system access |
| **System Admin** | sysadmin@pmc.edu.pk | password123 | All admin permissions |
| **Cardiology HOD** | cardio.hod@pmc.edu.pk | password123 | Department head, can assign consults |
| **Cardiology Doctor** | cardio.doc@pmc.edu.pk | password123 | Can view and respond to consults |
| **ER Doctor** | er.doc@pmc.edu.pk | password123 | Can create consults |
| **Neurology HOD** | neuro.hod@pmc.edu.pk | password123 | Department head |
| **Neurology Doctor** | neuro.doc@pmc.edu.pk | password123 | Doctor role |
| **Orthopedics HOD** | ortho.hod@pmc.edu.pk | password123 | Department head |
| **Medicine HOD** | med.hod@pmc.edu.pk | password123 | Department head |

## Introduction (1 minute)
*   **Presenter:** "Good morning/afternoon, everyone. Today, I'm excited to present the Hospital Consult System, a powerful tool designed to streamline and modernize the inter-departmental consultation process in a hospital setting."
*   **Key Message:** The current system of phone calls and pagers is inefficient and prone to errors. Our solution provides a centralized, real-time platform for managing consults, improving communication, and ultimately, enhancing patient care.

## Login & Dashboard (1 minute)
*   **Action:** Login as `cardio.hod@pmc.edu.pk` with password `password123`
*   **Presenter:** "The application uses a standard email and password for secure authentication. Once logged in, clinicians are taken directly to the consults list, their central hub for managing all their consultation requests."
*   **Show:** The dashboard with pending, in-progress, and overdue consults

## Admin Panel Demo (2 minutes)
*   **Action:** Login as `admin@pmc.edu.pk` with password `adminpassword123`
*   **Navigate:** Admin Panel → Users
*   **Presenter:** "Administrators can manage users, departments, and view global analytics."
*   **Show:**
    - User management (create, edit, activate/deactivate)
    - Department management with SLA configuration
    - Global dashboard with analytics across all departments

## Creating a New Consult (2 minutes)
*   **Action:** Login as `er.doc@pmc.edu.pk` with password `password123`
*   **Action:** Click the "+ New Consult" button
*   **Presenter:** "Let's create a new consult. The form is designed to be intuitive and easy to use, guiding the clinician through the process of providing all the necessary information."
*   **Fill out:**
    - Search for patient "MRN015" (Usman Raza)
    - Select target department: Orthopedics
    - Urgency: URGENT
    - Reason: "Pre-operative clearance needed for ACL repair surgery"
*   **Submit** and show the consult is now pending

## Managing a Consult (3 minutes)
*   **Action:** Login as `ortho.hod@pmc.edu.pk` to show HOD perspective
*   **Show:** The pending consult in their department
*   **Demonstrate:**
    - **Acknowledge:** Click acknowledge to confirm receipt
    - **Assign:** Assign to `ortho.doc@pmc.edu.pk`
*   **Action:** Login as `ortho.doc@pmc.edu.pk` 
*   **Demonstrate:**
    - **View assigned consult**
    - **Add Note:** Progress note with initial assessment
    - **Complete:** Add final note with recommendations

## Workflow Demonstration (2 minutes)
*   **Show existing consults:**
    - PENDING consults (show SLA countdown)
    - IN_PROGRESS consults (assigned to doctors)
    - COMPLETED consults (with final notes)
    - OVERDUE consults (highlight urgency)
*   **Filtering:** Demonstrate filtering by status, urgency, department

## Filtering & Searching (1 minute)
*   **Action:** Return to consults list
*   **Presenter:** "The consults list is designed to be highly interactive. Clinicians can easily filter the list by status, urgency, or department, allowing them to focus on the consults that require their immediate attention."
*   **Demonstrate:**
    - Filter by EMERGENCY urgency
    - Filter by PENDING status
    - Clear filters

## Analytics Dashboard (1 minute)
*   **Action:** Login as admin, navigate to Global Dashboard
*   **Show:**
    - Consults by department
    - SLA compliance rates
    - Average response times
    - Trend analysis

## Conclusion (1 minute)
*   **Presenter:** "The Hospital Consult System is a powerful tool that has the potential to revolutionize the way hospitals manage inter-departmental consultations. By providing a centralized, real-time platform for communication and collaboration, we can improve efficiency, reduce errors, and ultimately, enhance patient care."
*   **Call to Action:** "Thank you for your time. I'd be happy to answer any questions you may have."

## Quick Reference - Sample Data

### Patients Available
| MRN | Name | Ward | Diagnosis |
|-----|------|------|-----------|
| MRN001 | Muhammad Ali Khan | CCU | Acute MI |
| MRN005 | Imran Qureshi | Ortho Ward | Compound Fracture |
| MRN009 | Bilal Sheikh | Emergency | Chest Pain |
| MRN010 | Nadia Iqbal | Emergency | Severe Headache |
| MRN015 | Usman Raza | Ortho Ward | ACL Tear |

### Pre-loaded Consults
- **3 Pending** - Including emergency cases from ER
- **2 Acknowledged** - Awaiting assignment
- **3 In Progress** - Assigned to doctors
- **4 Completed** - With final notes and recommendations
