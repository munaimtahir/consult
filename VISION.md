# Hospital Consult System - Vision Document

## 1. Introduction
The Hospital Consult System is a digital solution designed to replace the traditional paper-based workflow for inter-departmental patient consultations. It aims to streamline communication between primary treating teams and specialty departments, ensuring timely patient reviews and reducing medical errors associated with lost or delayed requests.

## 2. Problem Statement
Currently, when a patient requires a review by another department:
- **Inefficiency**: Paper requests are physically handed to attendants who must locate the correct ward and doctor.
- **Data Loss**: Paper forms can be lost or misplaced.
- **Delays**: Finding the on-call doctor takes time, and there is no automated tracking of response times.
- **Lack of Accountability**: It is difficult to track when a request was made and if it was seen within the medically required timeframe.

## 3. The Solution
A paperless, digital application that allows doctors to:
- Instantly send consult requests with full patient context.
- Track the status of requests in real-time.
- Ensure accountability through automated time-tracking and escalation.

## 4. Key Users
- **Referring Doctor (Requester)**: The primary doctor treating the patient who identifies the need for a specialist opinion.
- **Receiving Department (Responder)**: The specialty department (e.g., Cardiology, Neurology) receiving the request. This includes:
    - **Department Admin/Senior**: Triages requests and assigns them to available doctors.
    - **Consultant/Resident**: The doctor who performs the review and writes the note.
- **Head of Department (HOD)**: Reviews department performance and consult metrics.
- **Administrator**: Manages user accounts, department hierarchies, and system settings.

## 5. Core Value Proposition
- **Speed**: Instant transmission of requests eliminates physical travel time.
- **Tracking**: Real-time status updates (Sent, Received, In Progress, Completed).
- **Safety**: Automated alerts for urgent consults and hierarchy escalation if delays occur.
- **Record Keeping**: All consult notes and history are permanently stored and easily retrievable.
- **Analytics**: Live dashboards for HODs and Admins to monitor department performance, response times, and consult volumes.

## 6. Urgency Levels & SLAs
The system enforces Service Level Agreements (SLAs) based on clinical urgency:
1.  **Emergency**: Review required within **< 1 hour**.
2.  **Urgent**: Review required within **4 hours**.
3.  **Routine**: Review required within **23 hours**.

*Failure to meet these timelines triggers an automatic notification to the next senior level in the department hierarchy.*
