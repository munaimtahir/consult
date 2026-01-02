"""
Timetable Service
Business logic for timetable workflow.
"""

from django.db import transaction
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from .models import WeekPlan, WeekSlotRow, WeekCell, WeekChangeLog, SessionOccurrence
from .exceptions import TimetableValidationError


def get_monday(date):
    """Get the Monday of the week for a given date."""
    days_since_monday = date.weekday()
    return date - timedelta(days=days_since_monday)


class TimetableService:
    """Encapsulates business logic for timetable management."""
    
    @staticmethod
    @transaction.atomic
    def create_week(week_start_date, created_by=None):
        """Creates a new week plan with slot rows and cells.
        
        Args:
            week_start_date: Monday date of the week
            created_by: User creating the week (optional)
            
        Returns:
            WeekPlan instance
        """
        # Ensure it's a Monday
        monday = get_monday(week_start_date)
        
        # Check if week already exists
        if WeekPlan.objects.filter(week_start_date=monday).exists():
            raise TimetableValidationError(f"Week starting {monday} already exists")
        
        # Create week plan
        week_plan = WeekPlan.objects.create(
            week_start_date=monday,
            status='DRAFT',
            created_by=created_by
        )
        
        # Get slot count from settings
        slot_count = getattr(settings, 'TIMETABLE_SLOT_COUNT', 8)
        
        # Create slot rows
        slot_rows = []
        for i in range(1, slot_count + 1):
            slot_row = WeekSlotRow.objects.create(
                week_plan=week_plan,
                row_index=i
            )
            slot_rows.append(slot_row)
        
        # Create cells (7 days × N slots)
        for day in range(7):  # Monday to Sunday
            for slot_row in slot_rows:
                WeekCell.objects.create(
                    week_plan=week_plan,
                    slot_row=slot_row,
                    day_of_week=day,
                    status='SCHEDULED'
                )
        
        return week_plan
    
    @staticmethod
    @transaction.atomic
    def create_next_4_weeks(from_week_start=None, created_by=None):
        """Creates the next 4 consecutive weeks starting from a given date.
        
        Args:
            from_week_start: Starting Monday date (defaults to next Monday)
            created_by: User creating the weeks (optional)
            
        Returns:
            List of WeekPlan instances
        """
        if from_week_start is None:
            # Start from next Monday
            today = timezone.now().date()
            next_monday = get_monday(today) + timedelta(days=7)
        else:
            next_monday = get_monday(from_week_start)
        
        week_plans = []
        for i in range(4):
            week_date = next_monday + timedelta(weeks=i)
            # Only create if it doesn't exist
            week_plan, created = WeekPlan.objects.get_or_create(
                week_start_date=week_date,
                defaults={
                    'status': 'DRAFT',
                    'created_by': created_by
                }
            )
            if created:
                # Create slot rows and cells
                slot_count = getattr(settings, 'TIMETABLE_SLOT_COUNT', 8)
                slot_rows = []
                for j in range(1, slot_count + 1):
                    slot_row = WeekSlotRow.objects.create(
                        week_plan=week_plan,
                        row_index=j
                    )
                    slot_rows.append(slot_row)
                
                # Create cells
                for day in range(7):
                    for slot_row in slot_rows:
                        WeekCell.objects.create(
                            week_plan=week_plan,
                            slot_row=slot_row,
                            day_of_week=day,
                            status='SCHEDULED'
                        )
            week_plans.append(week_plan)
        
        return week_plans
    
    @staticmethod
    def _create_snapshot(week_plan):
        """Creates a JSON snapshot of week plan state."""
        rows = []
        for row in week_plan.slot_rows.all():
            rows.append({
                'id': row.id,
                'row_index': row.row_index,
                'start_time': str(row.start_time) if row.start_time else None,
                'end_time': str(row.end_time) if row.end_time else None,
            })
        
        cells = []
        for cell in week_plan.cells.all():
            cells.append({
                'id': cell.id,
                'slot_row_id': cell.slot_row.id,
                'day_of_week': cell.day_of_week,
                'department_id': cell.department.id if cell.department else None,
                'topic': cell.topic,
                'faculty_name': cell.faculty_name,
                'status': cell.status,
            })
        
        return {'rows': rows, 'cells': cells}
    
    @staticmethod
    @transaction.atomic
    def bulk_save_grid(week_id, rows_data, cells_data, actor):
        """Bulk save grid data (rows and cells) with permission checks.
        
        Args:
            week_id: WeekPlan ID
            rows_data: List of dicts with {id, start_time, end_time}
            cells_data: List of dicts with {id, department_id, topic, faculty_name, status}
            actor: User performing the action
            
        Returns:
            Updated WeekPlan instance
        """
        week_plan = WeekPlan.objects.get(id=week_id)
        
        # Check permissions
        if week_plan.status == 'PUBLISHED':
            if not (actor.is_admin_user or actor.is_hod):
                raise TimetableValidationError(
                    "Only HOD/Admin can edit published weeks"
                )
        elif week_plan.status == 'VERIFIED':
            if not (actor.is_admin_user or actor.is_hod):
                raise TimetableValidationError(
                    "Only HOD/Admin can edit verified weeks"
                )
        
        # Create snapshot for change log if published
        before_snapshot = None
        if week_plan.status == 'PUBLISHED':
            before_snapshot = TimetableService._create_snapshot(week_plan)
        
        # Update rows
        changed_row_ids = []
        for row_data in rows_data:
            row = WeekSlotRow.objects.get(id=row_data['id'], week_plan=week_plan)
            if row.start_time != row_data.get('start_time') or row.end_time != row_data.get('end_time'):
                changed_row_ids.append(row.id)
            row.start_time = row_data.get('start_time')
            row.end_time = row_data.get('end_time')
            row.save()
        
        # Update cells
        changed_cell_ids = []
        for cell_data in cells_data:
            cell = WeekCell.objects.get(id=cell_data['id'], week_plan=week_plan)
            changed = False
            
            if cell.department_id != cell_data.get('department_id'):
                changed = True
                cell.department_id = cell_data.get('department_id')
            if cell.topic != cell_data.get('topic', ''):
                changed = True
                cell.topic = cell_data.get('topic', '')
            if cell.faculty_name != cell_data.get('faculty_name', ''):
                changed = True
                cell.faculty_name = cell_data.get('faculty_name', '')
            if cell.status != cell_data.get('status', 'SCHEDULED'):
                changed = True
                cell.status = cell_data.get('status', 'SCHEDULED')
            
            if changed:
                changed_cell_ids.append(cell.id)
            cell.save()
        
        # Create change log if published and changes were made
        if week_plan.status == 'PUBLISHED' and (changed_row_ids or changed_cell_ids):
            after_snapshot = TimetableService._create_snapshot(week_plan)
            WeekChangeLog.objects.create(
                week_plan=week_plan,
                changed_by=actor,
                change_reason=f"Grid updated by {actor.get_full_name()}",
                before_snapshot=before_snapshot,
                after_snapshot=after_snapshot,
                changed_rows=changed_row_ids,
                changed_cells=changed_cell_ids
            )
        
        week_plan.refresh_from_db()
        return week_plan
    
    @staticmethod
    def validate_publish(week_plan):
        """Validates that a week plan is ready to be published.
        
        Args:
            week_plan: WeekPlan instance
            
        Raises:
            TimetableValidationError if validation fails
        """
        errors = []
        
        # Check all rows have valid timings
        for row in week_plan.slot_rows.all():
            if not row.start_time or not row.end_time:
                errors.append(f"Slot {row.row_index} is missing start or end time")
            elif row.end_time <= row.start_time:
                errors.append(f"Slot {row.row_index} has invalid time range")
        
        # Check scheduled cells have department
        scheduled_cells = week_plan.cells.filter(status='SCHEDULED')
        for cell in scheduled_cells:
            if not cell.department:
                day_name = dict(WeekCell.DAY_CHOICES).get(cell.day_of_week, 'Unknown')
                errors.append(
                    f"{day_name} Slot {cell.slot_row.row_index} is scheduled but has no department"
                )
        
        if errors:
            raise TimetableValidationError("Validation failed: " + "; ".join(errors))
    
    @staticmethod
    @transaction.atomic
    def verify_week(week_id, verifier):
        """Moves a week from DRAFT to VERIFIED.
        
        Args:
            week_id: WeekPlan ID
            verifier: User verifying the week
            
        Returns:
            Updated WeekPlan instance
        """
        week_plan = WeekPlan.objects.get(id=week_id)
        
        if week_plan.status != 'DRAFT':
            raise TimetableValidationError(
                f"Cannot verify week in {week_plan.status} status"
            )
        
        week_plan.status = 'VERIFIED'
        week_plan.verified_by = verifier
        week_plan.verified_at = timezone.now()
        week_plan.save()
        
        return week_plan
    
    @staticmethod
    @transaction.atomic
    def publish_week(week_id, publisher):
        """Moves a week from VERIFIED to PUBLISHED and generates SessionOccurrences.
        
        Args:
            week_id: WeekPlan ID
            publisher: User publishing the week
            
        Returns:
            Updated WeekPlan instance
        """
        week_plan = WeekPlan.objects.get(id=week_id)
        
        if week_plan.status != 'VERIFIED':
            raise TimetableValidationError(
                f"Cannot publish week in {week_plan.status} status"
            )
        
        # Validate before publishing
        TimetableService.validate_publish(week_plan)
        
        # Update status
        week_plan.status = 'PUBLISHED'
        week_plan.published_by = publisher
        week_plan.published_at = timezone.now()
        week_plan.save()
        
        # Generate SessionOccurrences (idempotent - delete existing first)
        SessionOccurrence.objects.filter(week_plan=week_plan).delete()
        
        for cell in week_plan.cells.filter(status='SCHEDULED', department__isnull=False):
            # Calculate actual date
            day_offset = cell.day_of_week
            session_date = week_plan.week_start_date + timedelta(days=day_offset)
            
            # Only create if row has valid times
            if cell.slot_row.start_time and cell.slot_row.end_time:
                SessionOccurrence.objects.create(
                    week_plan=week_plan,
                    week_cell=cell,
                    date=session_date,
                    start_time=cell.slot_row.start_time,
                    end_time=cell.slot_row.end_time,
                    department=cell.department,
                    topic=cell.topic,
                    faculty_name=cell.faculty_name,
                    status='SCHEDULED'
                )
        
        return week_plan
    
    @staticmethod
    @transaction.atomic
    def revert_to_draft(week_id, actor, reason):
        """Reverts a VERIFIED or PUBLISHED week back to DRAFT.
        
        Args:
            week_id: WeekPlan ID
            actor: User performing the revert (must be Admin/HOD)
            reason: Reason for reverting
            
        Returns:
            Updated WeekPlan instance
        """
        week_plan = WeekPlan.objects.get(id=week_id)
        
        if week_plan.status not in ['VERIFIED', 'PUBLISHED']:
            raise TimetableValidationError(
                f"Cannot revert week in {week_plan.status} status"
            )
        
        if not (actor.is_admin_user or actor.is_hod):
            raise TimetableValidationError(
                "Only HOD/Admin can revert weeks"
            )
        
        # Create change log if published
        if week_plan.status == 'PUBLISHED':
            before_snapshot = TimetableService._create_snapshot(week_plan)
            week_plan.status = 'DRAFT'
            week_plan.save()
            after_snapshot = TimetableService._create_snapshot(week_plan)
            
            WeekChangeLog.objects.create(
                week_plan=week_plan,
                changed_by=actor,
                change_reason=f"Reverted to draft: {reason}",
                before_snapshot=before_snapshot,
                after_snapshot=after_snapshot,
                changed_rows=[],
                changed_cells=[]
            )
        else:
            week_plan.status = 'DRAFT'
            week_plan.save()
        
        return week_plan
