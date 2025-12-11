# Acknowledge & Assign API Documentation

## Overview

This document describes the new combined "Acknowledge & Assign" workflow for the consult system. This workflow ensures that consults are both received/acknowledged AND assigned to a doctor in a single atomic operation, preventing intermediate states and ensuring a clear audit trail.

## New Endpoint

### POST `/api/v1/consults/requests/{id}/acknowledge-assign/`

Acknowledges receipt of a consult and assigns it to a doctor in one combined action.

#### Permissions

Only the following users can use this endpoint:
- **HOD (Head of Department)** of the target department
- **Delegated Receiver** - A senior doctor designated by the HOD via the `Department.delegated_receiver` field
- Users with `can_manage_consults_in_department` permission set to `True`

#### Request Body

```json
{
  "assigned_to_user_id": 123
}
```

**Parameters:**
- `assigned_to_user_id` (required): ID of the user to assign the consult to. Must be a member of the target department.

#### Response

Returns the updated consult with all fields populated:

```json
{
  "id": 1,
  "status": "IN_PROGRESS",
  "received_by": {
    "id": 456,
    "email": "hod@pmc.edu.pk",
    "full_name": "Dr. John HOD"
  },
  "received_at": "2025-12-10T21:45:00Z",
  "assigned_to": {
    "id": 123,
    "email": "doctor@pmc.edu.pk",
    "full_name": "Dr. Jane Doctor"
  },
  "assigned_by": {
    "id": 456,
    "email": "hod@pmc.edu.pk",
    "full_name": "Dr. John HOD"
  },
  "assigned_at": "2025-12-10T21:45:00Z",
  "assignment_type": "manual",
  ...other consult fields...
}
```

#### Error Responses

**403 Forbidden** - User lacks permission
```json
{
  "error": "You do not have permission to acknowledge and assign consults. Only HOD or delegated receivers can perform this action."
}
```

**400 Bad Request** - Invalid consult status
```json
{
  "error": "Only SUBMITTED or ACKNOWLEDGED consults can be acknowledged and assigned. Current status: IN_PROGRESS"
}
```

**400 Bad Request** - Assigned user not in department
```json
{
  "error": "Assigned user must be in the target department"
}
```

**404 Not Found** - Assigned user doesn't exist
```json
{
  "error": "User not found"
}
```

## New Model Fields

### ConsultRequest Model

The following fields have been added to track receipt and assignment:

- `received_by` (FK to User): User who acknowledged receipt of the consult
- `received_at` (DateTime): Timestamp when consult was received
- `assigned_to` (FK to User): User assigned to handle the consult (existing field)
- `assigned_by` (FK to User): User who performed the assignment
- `assigned_at` (DateTime): Timestamp when assignment occurred
- `assignment_type` (CharField): Either "manual" or "auto" (for auto-assigned consults)

**Note:** The deprecated `acknowledged_by` and `acknowledged_at` fields are still populated for backward compatibility, but new code should use `received_by` and `received_at`.

### Department Model

- `delegated_receiver` (FK to User, nullable): Senior doctor delegated by HOD to receive and assign consults

## HOD Delegation Feature

HODs can delegate the responsibility of receiving and assigning consults to a trusted senior doctor:

### Setting a Delegated Receiver

Update the department via the admin API:

```json
PATCH /api/v1/admin/departments/{id}/
{
  "delegated_receiver": 789
}
```

### Checking Permissions

The User model now has a `can_manage_consults` property that returns `True` if:
1. User is an HOD, OR
2. User has `can_manage_consults_in_department` flag set to `True`, OR
3. User is set as `delegated_receiver` for their department

## Workflow Example

### Scenario: HOD Receives New Consult

1. **Consult Created** - A doctor in Emergency creates a consult for Cardiology
   - Status: `SUBMITTED`
   - All receipt/assignment fields: `null`

2. **HOD Views Pending Consults**
   ```
   GET /api/v1/consults/requests/?view=my_department&status=SUBMITTED
   ```

3. **HOD Acknowledges and Assigns**
   ```
   POST /api/v1/consults/requests/1/acknowledge-assign/
   {
     "assigned_to_user_id": 123
   }
   ```

4. **Consult Updated** - System atomically updates:
   - Status: `IN_PROGRESS`
   - `received_by`: HOD
   - `received_at`: Current timestamp
   - `assigned_to`: Selected doctor
   - `assigned_by`: HOD
   - `assigned_at`: Current timestamp (same as received_at)
   - `assignment_type`: "manual"

5. **Doctor Notified** - Assigned doctor receives notification

### Scenario: Delegated Receiver Handles Consult

1. HOD sets delegated receiver:
   ```
   PATCH /api/v1/admin/departments/2/
   {
     "delegated_receiver": 789  // Senior Registrar ID
   }
   ```

2. Senior Registrar acknowledges and assigns:
   ```
   POST /api/v1/consults/requests/2/acknowledge-assign/
   {
     "assigned_to_user_id": 456
   }
   ```

3. Consult updated with Senior Registrar as both `received_by` and `assigned_by`

## Business Rules

1. **Atomic Operation**: Acknowledgement and assignment MUST happen together in one transaction
2. **No Intermediate States**: A consult cannot be in a "received but unassigned" state
3. **Permission Check**: Only HOD or delegated receivers can acknowledge & assign
4. **Department Validation**: Assigned user must belong to the target department
5. **Status Validation**: Only `SUBMITTED` or `ACKNOWLEDGED` consults can be acknowledged & assigned
6. **Audit Trail**: All changes are logged with who performed them and when

## Migration from Old Workflow

The system maintains backward compatibility:

- Old `acknowledged_by` and `acknowledged_at` fields are still populated
- Existing `/acknowledge/` and `/assign/` endpoints still work
- Auto-assignment logic (on-call, hierarchy-based) populates all new fields
- Old consults without new fields will continue to work

However, new frontend code should use the new `/acknowledge-assign/` endpoint for the best experience.

## Testing

See `backend/apps/consults/tests/test_acknowledge_assign.py` for comprehensive test cases covering:
- HOD permissions
- Delegated receiver permissions
- Regular doctor restrictions
- Department validation
- Status validation
- Atomic transaction verification
