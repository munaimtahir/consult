# Hospital Consult System - Workflow

This document outlines the step-by-step process for a patient consultation within the system.

## 1. Consult Creation (Referring Doctor)
1.  **Log In**: Doctor logs into the application.
2.  **Initiate Consult**: Click "New Consult Request".
3.  **Enter Patient Details**: Manually enter **Patient Name, Age, Ward, Bed No, and Primary Diagnosis** (as no central digital patient database exists).
4.  **Fill Consult Details**:
    -   Enter clinical summary and reason for referral.
    -   Select **Target Department** (e.g., Cardiology).
    -   Select **Urgency Level** (Emergency, Urgent, or Routine).
    -   (Optional) Attach relevant lab reports or images.
    -   **Assignment Preference**: Select a specific doctor (if known) or send to Department Pool (assignment logic depends on Department Policy).
5.  **Submit**: The request is sent instantly. Timer starts based on urgency level.

## 2. Triage & Assignment (Receiving Department)
1.  **Notification**: The Target Department receives a notification.
2.  **Triage**: A Senior Doctor or Department Admin views the incoming request list.
3.  **Assignment**: The request is assigned based on **Department Policy** for the specific urgency level (Emergency, Urgent, Routine).
    -   *Note*: Each department defines its own logic for who receives which type of consult.
4.  **Status Update**: Request status changes to **"Assigned"** or **"In Progress"**.

## 3. Patient Review (Consultant/Resident)
1.  **Review Data**: The assigned doctor reviews the patient's data and the request details on their device.
2.  **Physical Assessment**: The doctor visits the patient (if required).
3.  **Draft Note**: The doctor opens the request and drafts a **Consult Note** with their findings and recommendations.

## 4. Consultant Action (Response)
1.  **Submit Note**: The consulting doctor submits their findings.
2.  **Decision**: The consultant chooses an outcome:
    -   **Mark as Completed**: Issue resolved.
    -   **Add to Follow-up Pool**:
        -   *Regular Follow-up*: Daily review required.
        -   *Conditional Follow-up*: Review after specific labs or time duration.

## 5. Completion & Feedback (Referring Doctor)
1.  **Notification**: The Referring Doctor receives the consult note.
2.  **Action**: The Referring Doctor reviews the note and can:
    -   **Mark as Closed**: Accepts the advice.
    -   **Request Details**: Asks for clarification (re-opens communication).

## 6. Escalation Flow (Automated)
If a consult is not managed within the desired time:
-   **Logic**: Escalation rules and time limits are defined **per Department Policy**.
-   **Action**: Notification sent to the next senior level in the hierarchy.

## 6. Audit & History
-   All actions are timestamped.
-   Completed consults are archived in the patient's digital history.
