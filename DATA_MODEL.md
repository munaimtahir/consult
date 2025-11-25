# Hospital Consult System - Data Model

This document defines the core entities and their properties in plain English.

## 1. Patient
Represents the person receiving care.
-   **Name**: Full name of the patient.
-   **MRN**: Medical Record Number (Unique Identifier).
-   **Age**: Patient's age.
-   **Gender**: Patient's gender.
-   **Location**: Current Ward and Bed Number.
-   **Primary Department**: The department currently treating the patient.

## 2. Department
Represents a medical specialty unit (e.g., Cardiology, Orthopedics).
-   **Name**: Name of the department.
-   **Head of Department**: User ID of the department head (for escalation).
-   **Contact Number**: Central contact for the department.

## 3. User
Represents any staff member using the system (Doctors, Admins).
-   **Name**: Full name.
-   **Role**: Job title (e.g., Resident, Consultant, Head of Dept, Admin).
-   **Department**: The department this user belongs to.
-   **Login Credentials**: Username/Email and Password hash.
-   **Seniority Level**: Used for hierarchy/escalation logic (e.g., Level 1 = Resident, Level 3 = HOD).

## 4. ConsultRequest
Represents the core transaction—a request for a review.
-   **ID**: Unique reference number.
-   **Patient**: Link to the Patient entity.
-   **Requester**: Link to the User who created the request.
-   **Target Department**: Link to the Department being requested.
-   **Assigned Doctor**: Link to the User currently responsible for the review (can be null initially).
-   **Urgency**: Level of urgency (Emergency, Urgent, Routine).
-   **Status**: Current state (Pending, Assigned, In Progress, Completed, Escalated, Follow-up).
-   **Clinical Details**: Text description of the problem/reason for consult.
-   **Created At**: Timestamp of creation.
-   **Due By**: Calculated timestamp based on urgency (e.g., Created At + 4 hours).
-   **First Response At**: Timestamp when the first note was added (for analytics).
-   **Completed At**: Timestamp when marked as completed (for analytics).
-   **Follow-up Type**: If in follow-up, specifies Regular or Conditional.

## 5. ConsultNote
Represents the outcome/response to a request.
-   **ID**: Unique reference number.
-   **ConsultRequest**: Link to the parent ConsultRequest.
-   **Author**: Link to the User writing the note.
-   **Content**: The medical advice, findings, and plan.
-   **Created At**: Timestamp when the note was submitted.
