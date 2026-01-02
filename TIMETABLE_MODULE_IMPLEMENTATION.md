# Timetable Module MVP Implementation

## Overview

This document summarizes the implementation of the Timetable Module MVP, which provides a weekly timetable editor with draft/verify/publish workflow.

## Features Implemented

### Backend (Django)

1. **Models** (`backend/apps/timetable/models.py`):
   - `WeekPlan`: Represents a weekly timetable plan with status (DRAFT → VERIFIED → PUBLISHED)
   - `WeekSlotRow`: Defines time slots (rows) for each week with start/end times
   - `WeekCell`: Grid cells (WeekPlan × DayOfWeek × SlotRow) with department, topic, faculty
   - `WeekChangeLog`: Audit log for changes to published weeks
   - `SessionOccurrence`: Real dated sessions generated when a week is published

2. **Services** (`backend/apps/timetable/services.py`):
   - `create_week()`: Creates a week plan with N slot rows and 7×N cells
   - `create_next_4_weeks()`: Creates 4 consecutive weeks in one operation
   - `bulk_save_grid()`: Bulk save rows and cells with permission checks
   - `verify_week()`: Moves week from DRAFT to VERIFIED
   - `publish_week()`: Moves week from VERIFIED to PUBLISHED and generates SessionOccurrences
   - `revert_to_draft()`: Reverts VERIFIED/PUBLISHED weeks back to DRAFT
   - `validate_publish()`: Validates week is ready for publishing

3. **API Endpoints** (`backend/apps/timetable/views.py`):
   - `GET /api/v1/timetable/weeks/`: List weeks (with filters)
   - `GET /api/v1/timetable/weeks/{id}/`: Get week details with grid
   - `POST /api/v1/timetable/weeks/create_week/`: Create single week
   - `POST /api/v1/timetable/weeks/create_next_4_weeks/`: Create next 4 weeks
   - `POST /api/v1/timetable/weeks/{id}/save_grid/`: Bulk save grid
   - `POST /api/v1/timetable/weeks/{id}/verify/`: Verify week
   - `POST /api/v1/timetable/weeks/{id}/publish/`: Publish week
   - `POST /api/v1/timetable/weeks/{id}/revert_to_draft/`: Revert to draft
   - `GET /api/v1/timetable/weeks/{id}/change_logs/`: Get change logs
   - `GET /api/v1/timetable/sessions/`: List session occurrences

4. **Permissions** (`backend/apps/timetable/permissions.py`):
   - `CanEditTimetable`: Edit based on status and role
   - `CanVerifyTimetable`: Verify draft weeks (HOD/Admin)
   - `CanPublishTimetable`: Publish verified weeks (HOD/Admin)
   - `CanRevertTimetable`: Revert weeks (HOD/Admin)

5. **Configuration**:
   - Added `apps.timetable` to `INSTALLED_APPS` in `settings.py`
   - Added `TIMETABLE_SLOT_COUNT = 8` setting (configurable)
   - Added timetable routes to main URL config

### Frontend (React)

1. **API Client** (`frontend/src/api/index.js`):
   - `timetableAPI`: Complete API client for all timetable operations

2. **Pages**:
   - `TimetableWeekEditor` (`frontend/src/pages/TimetableWeekEditor.jsx`):
     - Week selector dropdown
     - Status display and action buttons (Verify, Publish, Revert)
     - "Create Next 4 Weeks" button
     - Error/success message display
     - Integrates with WeekGrid component

3. **Components**:
   - `WeekGrid` (`frontend/src/components/timetable/WeekGrid.jsx`):
     - Landscape grid layout (rows × days)
     - Time inputs for each slot row
     - Department dropdown, topic, and faculty inputs per cell
     - Save button with unsaved changes indicator
     - Read-only mode for verified/published weeks

4. **Routing**:
   - Added `/timetable` route to `App.jsx`
   - Added "Timetable" link to main navigation

### Tests

- Basic unit tests in `backend/apps/timetable/tests/test_services.py`:
  - Week creation
  - Next 4 weeks creation
  - Verification workflow
  - Publishing workflow
  - Bulk save operations
  - Validation tests

## Workflow

1. **Create Weeks**: User clicks "Create Next 4 Weeks" → System creates 4 DRAFT weeks
2. **Edit Draft**: User selects week → Edits slot times and cell content → Saves
3. **Verify**: Verifier (HOD/Admin) verifies week → Status becomes VERIFIED
4. **Publish**: Publisher (HOD/Admin) publishes week → Status becomes PUBLISHED, SessionOccurrences generated
5. **Post-Publish Changes**: HOD/Admin can edit published weeks with reason → Change log created

## Database Schema

- `week_plans`: One record per week (Monday start date)
- `week_slot_rows`: N rows per week (default 8)
- `week_cells`: 7×N cells per week (7 days × N slots)
- `week_change_logs`: Audit trail for published week changes
- `session_occurrences`: Real sessions generated on publish

## Configuration

Set `TIMETABLE_SLOT_COUNT` in `backend/config/settings.py` to change the number of slots per day (default: 8).

## Next Steps (Optional Enhancements)

1. Add attendance tracking linked to SessionOccurrence
2. Add monthly reporting based on SessionOccurrence
3. Add bulk operations (copy week, template weeks)
4. Add export functionality (PDF, Excel)
5. Add notifications for week status changes
6. Add department-specific views/filters

## Files Created/Modified

### Backend
- `backend/apps/timetable/` (new app)
  - `models.py`
  - `services.py`
  - `serializers.py`
  - `views.py`
  - `urls.py`
  - `permissions.py`
  - `admin.py`
  - `exceptions.py`
  - `tests/test_services.py`
- `backend/config/settings.py` (modified)
- `backend/apps/core/urls.py` (modified)

### Frontend
- `frontend/src/api/index.js` (modified)
- `frontend/src/pages/TimetableWeekEditor.jsx` (new)
- `frontend/src/components/timetable/WeekGrid.jsx` (new)
- `frontend/src/App.jsx` (modified)
- `frontend/src/components/Layout.jsx` (modified)

## Usage

1. Run migrations: `python manage.py makemigrations timetable && python manage.py migrate`
2. Access timetable editor at `/timetable` route
3. Create weeks, edit, verify, and publish as needed
