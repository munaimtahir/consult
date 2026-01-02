"""
Serializers for Timetable app.
"""

from rest_framework import serializers
from .models import WeekPlan, WeekSlotRow, WeekCell, WeekChangeLog, SessionOccurrence
from apps.departments.serializers import DepartmentSerializer
from apps.accounts.serializers import UserSerializer


class WeekSlotRowSerializer(serializers.ModelSerializer):
    """Serializer for WeekSlotRow."""
    
    class Meta:
        model = WeekSlotRow
        fields = ['id', 'row_index', 'start_time', 'end_time']
        read_only_fields = ['id', 'row_index']


class WeekCellSerializer(serializers.ModelSerializer):
    """Serializer for WeekCell."""
    
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    slot_row_id = serializers.IntegerField(source='slot_row.id', read_only=True)
    
    class Meta:
        model = WeekCell
        fields = [
            'id',
            'slot_row',
            'slot_row_id',
            'day_of_week',
            'department',
            'department_id',
            'topic',
            'faculty_name',
            'status'
        ]
        read_only_fields = ['id', 'slot_row']


class WeekPlanListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing week plans."""
    
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.get_full_name', read_only=True)
    published_by_name = serializers.CharField(source='published_by.get_full_name', read_only=True)
    week_end_date = serializers.DateField(read_only=True)
    
    class Meta:
        model = WeekPlan
        fields = [
            'id',
            'week_start_date',
            'week_end_date',
            'status',
            'created_by',
            'created_by_name',
            'verified_by',
            'verified_by_name',
            'verified_at',
            'published_by',
            'published_by_name',
            'published_at',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class WeekPlanDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for week plan with rows and cells."""
    
    slot_rows = WeekSlotRowSerializer(many=True, read_only=True)
    cells = WeekCellSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.get_full_name', read_only=True)
    published_by_name = serializers.CharField(source='published_by.get_full_name', read_only=True)
    week_end_date = serializers.DateField(read_only=True)
    
    class Meta:
        model = WeekPlan
        fields = [
            'id',
            'week_start_date',
            'week_end_date',
            'status',
            'created_by',
            'created_by_name',
            'verified_by',
            'verified_by_name',
            'verified_at',
            'published_by',
            'published_by_name',
            'published_at',
            'slot_rows',
            'cells',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class WeekGridSaveSerializer(serializers.Serializer):
    """Serializer for bulk saving grid data."""
    
    rows = serializers.ListField(
        child=serializers.DictField(),
        help_text='List of row updates: {id, start_time, end_time}'
    )
    cells = serializers.ListField(
        child=serializers.DictField(),
        help_text='List of cell updates: {id, department_id, topic, faculty_name, status}'
    )
    
    def validate_rows(self, value):
        """Validate row data."""
        for row in value:
            if 'id' not in row:
                raise serializers.ValidationError("Each row must have an 'id'")
        return value
    
    def validate_cells(self, value):
        """Validate cell data."""
        for cell in value:
            if 'id' not in cell:
                raise serializers.ValidationError("Each cell must have an 'id'")
        return value


class WeekChangeLogSerializer(serializers.ModelSerializer):
    """Serializer for WeekChangeLog."""
    
    changed_by_name = serializers.CharField(source='changed_by.get_full_name', read_only=True)
    
    class Meta:
        model = WeekChangeLog
        fields = [
            'id',
            'week_plan',
            'changed_by',
            'changed_by_name',
            'change_reason',
            'before_snapshot',
            'after_snapshot',
            'changed_rows',
            'changed_cells',
            'created_at'
        ]
        read_only_fields = ['created_at']


class SessionOccurrenceSerializer(serializers.ModelSerializer):
    """Serializer for SessionOccurrence."""
    
    department = DepartmentSerializer(read_only=True)
    
    class Meta:
        model = SessionOccurrence
        fields = [
            'id',
            'week_plan',
            'week_cell',
            'date',
            'start_time',
            'end_time',
            'department',
            'topic',
            'faculty_name',
            'status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
