"""
Tests for Timetable services.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from apps.timetable.models import WeekPlan, WeekSlotRow, WeekCell
from apps.timetable.services import TimetableService, get_monday
from apps.timetable.exceptions import TimetableValidationError
from apps.departments.models import Department

User = get_user_model()


class TimetableServiceTestCase(TestCase):
    """Test cases for TimetableService."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@pmc.edu.pk',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='HOD'
        )
        self.department = Department.objects.create(
            name='Test Department',
            code='TEST'
        )
    
    def test_get_monday(self):
        """Test get_monday helper function."""
        # Test with a Monday
        monday = date(2024, 1, 1)  # This is a Monday
        self.assertEqual(get_monday(monday), monday)
        
        # Test with a Wednesday
        wednesday = date(2024, 1, 3)
        expected_monday = date(2024, 1, 1)
        self.assertEqual(get_monday(wednesday), expected_monday)
        
        # Test with a Sunday
        sunday = date(2024, 1, 7)
        expected_monday = date(2024, 1, 1)
        self.assertEqual(get_monday(sunday), expected_monday)
    
    def test_create_week(self):
        """Test creating a single week."""
        week_start = date(2024, 1, 1)  # Monday
        
        week_plan = TimetableService.create_week(week_start, self.user)
        
        self.assertIsNotNone(week_plan)
        self.assertEqual(week_plan.week_start_date, week_start)
        self.assertEqual(week_plan.status, 'DRAFT')
        self.assertEqual(week_plan.created_by, self.user)
        
        # Check slot rows were created (default 8)
        slot_rows = week_plan.slot_rows.all()
        self.assertEqual(slot_rows.count(), 8)
        self.assertEqual(slot_rows[0].row_index, 1)
        self.assertEqual(slot_rows[7].row_index, 8)
        
        # Check cells were created (7 days × 8 slots = 56)
        cells = week_plan.cells.all()
        self.assertEqual(cells.count(), 56)
        
        # Check cells are organized correctly
        for day in range(7):
            day_cells = cells.filter(day_of_week=day)
            self.assertEqual(day_cells.count(), 8)
    
    def test_create_week_duplicate(self):
        """Test that creating duplicate week raises error."""
        week_start = date(2024, 1, 1)
        TimetableService.create_week(week_start, self.user)
        
        with self.assertRaises(TimetableValidationError):
            TimetableService.create_week(week_start, self.user)
    
    def test_create_next_4_weeks(self):
        """Test creating next 4 weeks."""
        week_plans = TimetableService.create_next_4_weeks(created_by=self.user)
        
        self.assertEqual(len(week_plans), 4)
        
        # Check they are consecutive weeks
        for i in range(3):
            next_week = week_plans[i].week_start_date + timedelta(weeks=1)
            self.assertEqual(week_plans[i + 1].week_start_date, next_week)
        
        # Check all are DRAFT
        for week_plan in week_plans:
            self.assertEqual(week_plan.status, 'DRAFT')
    
    def test_verify_week(self):
        """Test verifying a week."""
        week_start = date(2024, 1, 1)
        week_plan = TimetableService.create_week(week_start, self.user)
        
        verified_week = TimetableService.verify_week(week_plan.id, self.user)
        
        self.assertEqual(verified_week.status, 'VERIFIED')
        self.assertEqual(verified_week.verified_by, self.user)
        self.assertIsNotNone(verified_week.verified_at)
    
    def test_verify_week_wrong_status(self):
        """Test that verifying non-draft week raises error."""
        week_start = date(2024, 1, 1)
        week_plan = TimetableService.create_week(week_start, self.user)
        week_plan.status = 'VERIFIED'
        week_plan.save()
        
        with self.assertRaises(TimetableValidationError):
            TimetableService.verify_week(week_plan.id, self.user)
    
    def test_publish_week(self):
        """Test publishing a week."""
        week_start = date(2024, 1, 1)
        week_plan = TimetableService.create_week(week_start, self.user)
        
        # Set times for rows
        for row in week_plan.slot_rows.all():
            row.start_time = '09:00:00'
            row.end_time = '10:00:00'
            row.save()
        
        # Set department for some cells
        for cell in week_plan.cells.filter(day_of_week=0)[:3]:  # First 3 Monday cells
            cell.department = self.department
            cell.save()
        
        # Verify first
        TimetableService.verify_week(week_plan.id, self.user)
        
        # Publish
        published_week = TimetableService.publish_week(week_plan.id, self.user)
        
        self.assertEqual(published_week.status, 'PUBLISHED')
        self.assertEqual(published_week.published_by, self.user)
        self.assertIsNotNone(published_week.published_at)
        
        # Check session occurrences were created
        from apps.timetable.models import SessionOccurrence
        sessions = SessionOccurrence.objects.filter(week_plan=week_plan)
        self.assertEqual(sessions.count(), 3)  # 3 scheduled cells with departments
    
    def test_publish_week_validation_fails(self):
        """Test that publishing without valid data fails."""
        week_start = date(2024, 1, 1)
        week_plan = TimetableService.create_week(week_start, self.user)
        
        # Don't set times or departments
        
        TimetableService.verify_week(week_plan.id, self.user)
        
        with self.assertRaises(TimetableValidationError):
            TimetableService.publish_week(week_plan.id, self.user)
    
    def test_bulk_save_grid(self):
        """Test bulk saving grid data."""
        week_start = date(2024, 1, 1)
        week_plan = TimetableService.create_week(week_start, self.user)
        
        # Prepare update data
        rows_data = []
        for row in week_plan.slot_rows.all():
            rows_data.append({
                'id': row.id,
                'start_time': '09:00:00',
                'end_time': '10:00:00',
            })
        
        cells_data = []
        for cell in week_plan.cells.filter(day_of_week=0)[:2]:  # First 2 Monday cells
            cells_data.append({
                'id': cell.id,
                'department_id': self.department.id,
                'topic': 'Test Topic',
                'faculty_name': 'Test Faculty',
                'status': 'SCHEDULED',
            })
        
        updated_week = TimetableService.bulk_save_grid(
            week_plan.id,
            rows_data,
            cells_data,
            self.user
        )
        
        # Check rows were updated
        for row in updated_week.slot_rows.all():
            self.assertEqual(str(row.start_time), '09:00:00')
            self.assertEqual(str(row.end_time), '10:00:00')
        
        # Check cells were updated
        updated_cells = updated_week.cells.filter(day_of_week=0, department=self.department)
        self.assertEqual(updated_cells.count(), 2)
        self.assertEqual(updated_cells[0].topic, 'Test Topic')
        self.assertEqual(updated_cells[0].faculty_name, 'Test Faculty')
