# Admin Panel Documentation

## Overview

The Admin Panel provides authorized users with capabilities to manage users, departments, and view system-wide dashboards. Access is controlled through a granular permission system.

## Features

### 1. Users Management (`/admin/users`)
- List all users with filters (department, role, active status, search)
- Create new users with email, department, and role assignment
- Edit user profiles and department assignments
- Activate/deactivate user accounts
- Set user passwords

### 2. Departments Management (`/admin/departments`)
- List all departments with flat or hierarchical view
- Create and edit departments with SLA configurations
- Create sub-departments (parent/child hierarchy)
- Assign Head of Department (HOD)
- Activate/deactivate departments
- Delete departments (if no users or consults attached)

### 3. Department Dashboard (`/admin/dashboards/department`)
- View consult statistics for a specific department
- Summary cards: Active, Pending, Acknowledged, In Progress, Completed Today, Overdue
- Received consults table (consults TO this department)
- Sent consults table (consults FROM this department)
- Filter by status, urgency, overdue, date range

### 4. Global Dashboard (`/admin/dashboards/global`)
- System-wide KPIs across all departments
- All consults table with comprehensive filters
- Department summary view with:
  - Open received/sent counts
  - Overdue counts
  - Average acknowledgement time
  - Average completion time
- Consult reassignment (for authorized users)
- Force close/cancel consults with reason

## Permission System

### Permission Flags

| Permission | Description |
|------------|-------------|
| `can_manage_users` | Create, edit, and manage users |
| `can_manage_departments` | Create, edit, and manage departments |
| `can_view_department_dashboard` | Access department-level dashboards |
| `can_view_global_dashboard` | Access system-wide dashboards |
| `can_manage_consults_globally` | Reassign and force-close consults across all departments |
| `can_manage_permissions` | Modify permission flags for other users (SuperAdmin only) |

### Typical Role Configurations

#### SuperAdmin (Full Access)
- All permissions enabled
- Can modify any user's permissions
- Full access to all dashboards and management features

```json
{
  "is_superuser": true
  // All permissions automatically granted
}
```

#### Medical Director / IT Admin
- Manage users and departments
- View global dashboard
- Manage consults globally if needed

```json
{
  "can_manage_users": true,
  "can_manage_departments": true,
  "can_view_department_dashboard": true,
  "can_view_global_dashboard": true,
  "can_manage_consults_globally": true
}
```

#### Head of Department (HOD)
- View own department dashboard only
- Cannot manage users or departments

```json
{
  "can_view_department_dashboard": true
}
```

#### Quality Assurance
- View all dashboards for reporting
- No management capabilities

```json
{
  "can_view_department_dashboard": true,
  "can_view_global_dashboard": true
}
```

## API Endpoints

### Users Admin API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/users/` | List users with filters |
| POST | `/api/v1/admin/users/` | Create new user |
| GET | `/api/v1/admin/users/{id}/` | Get user details |
| PATCH | `/api/v1/admin/users/{id}/` | Update user |
| POST | `/api/v1/admin/users/{id}/activate/` | Activate user |
| POST | `/api/v1/admin/users/{id}/deactivate/` | Deactivate user |
| PATCH | `/api/v1/admin/users/{id}/update_permissions/` | Update permissions |
| POST | `/api/v1/admin/users/{id}/set_password/` | Set password |

### Departments Admin API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/departments/` | List departments |
| POST | `/api/v1/admin/departments/` | Create department |
| GET | `/api/v1/admin/departments/{id}/` | Get department details |
| PATCH | `/api/v1/admin/departments/{id}/` | Update department |
| DELETE | `/api/v1/admin/departments/{id}/` | Delete department |
| POST | `/api/v1/admin/departments/{id}/activate/` | Activate department |
| POST | `/api/v1/admin/departments/{id}/deactivate/` | Deactivate department |
| GET | `/api/v1/admin/departments/{id}/users/` | Get department users |
| GET | `/api/v1/admin/departments/hierarchy/` | Get hierarchy view |

### Dashboard API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/dashboards/department/` | Department dashboard |
| GET | `/api/v1/admin/dashboards/global/` | Global dashboard |
| POST | `/api/v1/admin/consults/{id}/reassign/` | Reassign consult |
| POST | `/api/v1/admin/consults/{id}/force-close/` | Force close consult |

## Granting Admin Access

### From the Admin Panel (if you have `can_manage_permissions`)

1. Go to Admin Panel → Users Management
2. Click "Edit" on the user
3. Go to "Admin Permissions" tab
4. Enable the desired permissions
5. Click "Save Permissions"

### From Django Admin (for initial setup)

1. Access Django admin at `/admin/`
2. Navigate to Users
3. Edit the user
4. Under "Admin Panel Permissions", check the desired boxes
5. Save

### Via Django Shell (for initial SuperAdmin)

```python
from apps.accounts.models import User

# Create superuser with all permissions
user = User.objects.get(email='admin@pmc.edu.pk')
user.is_superuser = True
user.is_staff = True
user.save()

# Or grant specific permissions
user.can_manage_users = True
user.can_manage_departments = True
user.can_view_department_dashboard = True
user.can_view_global_dashboard = True
user.can_manage_consults_globally = True
user.can_manage_permissions = True
user.save()
```

## Security Notes

1. **Backend Enforcement**: All permissions are enforced on the backend. Even if a user manipulates the frontend, unauthorized API calls will be rejected with 403 Forbidden.

2. **Self-Protection**: Users cannot deactivate their own accounts.

3. **SuperUser Protection**: Only superusers can modify another superuser's permissions.

4. **Audit Trail**: All admin actions (creating users, modifying permissions, force-closing consults) are logged with timestamps and the actor's identity.

## Frontend Routes

| Route | Component | Required Permission |
|-------|-----------|---------------------|
| `/admin` | AdminHomePage | Any admin access |
| `/admin/users` | AdminUsersPage | `can_manage_users` |
| `/admin/departments` | AdminDepartmentsPage | `can_manage_departments` |
| `/admin/dashboards/department` | DepartmentDashboardPage | `can_view_department_dashboard` |
| `/admin/dashboards/global` | GlobalDashboardPage | `can_view_global_dashboard` |

## Troubleshooting

### "Access Denied" when accessing Admin Panel
- Ensure the user has at least one admin permission flag enabled
- Check that the user is active

### Cannot see "Admin Panel" link in navigation
- Only visible to users with `has_admin_panel_access`
- This includes users with any admin permission or admin role

### Cannot update another user's permissions
- You need `can_manage_permissions` permission or be a superuser
- You cannot modify a superuser's permissions unless you are also a superuser

### Department dashboard shows no data
- Ensure you have `can_view_department_dashboard` permission
- If viewing another department (as SuperAdmin), specify `department_id` in the request
