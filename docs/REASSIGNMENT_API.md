# Reassignment API Documentation

## Overview

This document describes the reassignment functionality for the consult system. HODs and authorized users can reassign consults to different doctors within their department, including reassigning to themselves.

## New Endpoint

### POST `/api/v1/consults/requests/{id}/reassign/`

Reassigns an already-assigned consult to a different doctor.

#### Permissions

Only the following users can use this endpoint:
- **HOD (Head of Department)** of the target department
- Users with `can_manage_consults_in_department` permission set to `True`
- **Delegated Receiver** - A senior doctor designated by the HOD via the `Department.delegated_receiver` field

#### Prerequisites

- Consult must already be assigned (have an `assigned_to` value)
- For unassigned consults, use the `/acknowledge-assign/` endpoint instead

#### Request Body

```json
{
  "assigned_to_user_id": 123
}
```

**Parameters:**
- `assigned_to_user_id` (required): ID of the user to reassign the consult to. Must be a member of the target department. Can be the same as the current user (self-assignment).

#### Response

Returns the updated consult with new assignment details:

```json
{
  "id": 1,
  "status": "IN_PROGRESS",
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
  "assigned_at": "2025-12-11T17:30:00Z",
  "assignment_type": "manual",
  "last_action_summary": "Reassigned from Dr. Old Doctor to Dr. Jane Doctor by Dr. John HOD",
  ...other consult fields...
}
```

#### Error Responses

**403 Forbidden** - User lacks permission
```json
{
  "error": "You do not have permission to reassign consults. Only HOD or authorized users can perform this action."
}
```

**400 Bad Request** - Consult not yet assigned
```json
{
  "error": "This consult is not yet assigned. Use acknowledge-assign endpoint instead."
}
```

**400 Bad Request** - New assigned user not in department
```json
{
  "error": "New assigned user must be in the target department"
}
```

**404 Not Found** - New assigned user doesn't exist
```json
{
  "error": "User not found"
}
```

## Use Cases

### 1. HOD Reassigning to Another Doctor

**Scenario:** HOD realizes a consult is better suited for a different specialist.

```bash
POST /api/v1/consults/requests/123/reassign/
Authorization: Bearer <hod_token>
Content-Type: application/json

{
  "assigned_to_user_id": 789
}
```

**Result:**
- Consult reassigned to doctor 789
- `assigned_by` set to HOD
- `assigned_at` updated to current time
- `last_action_summary` updated with details
- Notification sent to new assignee

### 2. HOD Taking Over a Consult

**Scenario:** HOD wants to handle a complex consult personally.

```bash
POST /api/v1/consults/requests/123/reassign/
Authorization: Bearer <hod_token>
Content-Type: application/json

{
  "assigned_to_user_id": 456  # HOD's own user ID
}
```

**Result:**
- Consult reassigned to HOD
- HOD becomes both `assigned_by` and `assigned_to`
- Complete audit trail maintained

### 3. Delegated Receiver Reassigning

**Scenario:** Senior doctor (delegated receiver) redistributes workload.

```bash
POST /api/v1/consults/requests/123/reassign/
Authorization: Bearer <senior_doctor_token>
Content-Type: application/json

{
  "assigned_to_user_id": 234
}
```

**Result:**
- Consult reassigned by delegated receiver
- Same validation and audit trail as HOD reassignment

## Permission Management

### Default Permissions
By default, only HODs can reassign consults in their department.

### Delegating Reassignment Authority

HOD can grant reassignment authority to other users:

```bash
PATCH /api/v1/admin/users/789/update_permissions/
Authorization: Bearer <hod_token>
Content-Type: application/json

{
  "can_manage_consults_in_department": true
}
```

This grants user 789 the ability to:
- Acknowledge and assign new consults
- Reassign existing consults
- Assign consults to themselves

### Checking User Permissions

The `User.can_manage_consults` property returns `True` if the user has reassignment authority:

```python
if user.can_manage_consults:
    # User can reassign consults
    pass
```

## Audit Trail

Every reassignment is fully tracked:

### Fields Updated
- `assigned_to` - New assignee
- `assigned_by` - Person who performed reassignment
- `assigned_at` - Timestamp of reassignment
- `assignment_type` - Set to "manual"
- `last_action_summary` - Human-readable description

### Example Audit Trail
```
Consult #123 Timeline:
1. Created by Dr. ER at 2025-12-11 10:00
2. Auto-assigned to Dr. Junior by System at 2025-12-11 10:01
3. Reassigned to Dr. Senior by Dr. HOD at 2025-12-11 14:30
4. Reassigned to Dr. HOD by Dr. HOD at 2025-12-11 15:15
5. Completed by Dr. HOD at 2025-12-11 16:00
```

## Business Rules

### Rule 1: Already Assigned
Consult must already have an `assigned_to` value. For new consults, use `/acknowledge-assign/` instead.

### Rule 2: Department Membership
New assignee must belong to the target department. Cross-department reassignments are not allowed.

### Rule 3: Self-Assignment Allowed
HOD and authorized users can reassign consults to themselves.

### Rule 4: Status Preservation
Reassignment does not change the consult status. If it was `IN_PROGRESS`, it stays `IN_PROGRESS`.

### Rule 5: Atomic Operation
Reassignment is wrapped in `@transaction.atomic` to ensure all changes succeed or fail together.

### Rule 6: Notification
New assignee receives a notification when consult is reassigned to them.

## Integration with Acknowledge & Assign

The reassignment endpoint works alongside the acknowledge & assign workflow:

```
Workflow 1: New Consult → Acknowledge & Assign
├─ Status: SUBMITTED → IN_PROGRESS
├─ Endpoint: POST /acknowledge-assign/
└─ Sets: received_by, assigned_to, assigned_by (all at once)

Workflow 2: Reassign Existing Consult
├─ Status: Unchanged (stays IN_PROGRESS, etc.)
├─ Endpoint: POST /reassign/
└─ Updates: assigned_to, assigned_by, assigned_at
```

## Testing

See `backend/apps/consults/tests/test_reassign.py` for comprehensive test cases:

1. **test_hod_can_reassign_consult** - HOD reassigns to different doctor
2. **test_hod_can_reassign_to_themselves** - HOD self-assignment
3. **test_regular_doctor_cannot_reassign** - Permission denial
4. **test_cannot_reassign_unassigned_consult** - Validation check
5. **test_reassigned_user_must_be_in_target_department** - Department validation

All tests passing ✅

## Comparison: Acknowledge-Assign vs Reassign

| Feature | Acknowledge-Assign | Reassign |
|---------|-------------------|----------|
| **Use Case** | New consult arrives | Change existing assignment |
| **Required State** | SUBMITTED or ACKNOWLEDGED | Already assigned |
| **Sets received_by** | Yes | No (preserves original) |
| **Sets assigned_to** | Yes | Yes (updates) |
| **Changes status** | Yes (→ IN_PROGRESS) | No (preserves) |
| **Permissions** | HOD or delegated receiver | HOD or authorized users |
| **Atomic** | Yes | Yes |

## Error Handling

### Common Errors

1. **"This consult is not yet assigned"**
   - **Cause:** Trying to reassign an unassigned consult
   - **Solution:** Use `/acknowledge-assign/` instead

2. **"You do not have permission to reassign"**
   - **Cause:** User is not HOD and lacks `can_manage_consults_in_department`
   - **Solution:** Have HOD grant permission or have HOD perform reassignment

3. **"New assigned user must be in the target department"**
   - **Cause:** Trying to reassign to doctor from different department
   - **Solution:** Select a doctor from the same department

4. **"You can only reassign consults in your department"**
   - **Cause:** User trying to reassign consult from different department
   - **Solution:** Can only reassign consults in own department

## Future Enhancements

Potential future features (not currently implemented):

- [ ] Bulk reassignment of multiple consults
- [ ] Reassignment history view
- [ ] Automatic reassignment based on workload
- [ ] Reassignment notifications to previous assignee
- [ ] Reassignment analytics and reporting

## Related Documentation

- [ACKNOWLEDGE_ASSIGN_API.md](./ACKNOWLEDGE_ASSIGN_API.md) - Acknowledge & Assign workflow
- [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) - Technical implementation details
