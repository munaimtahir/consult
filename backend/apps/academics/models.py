"""
Academic models for SIMS - Program and Term.
"""

from django.db import models
from django.core.exceptions import ValidationError


class Program(models.Model):
    """Represents an academic program (e.g., MBBS, BDS, etc.)."""
    
    code = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration_years = models.IntegerField(default=5)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'programs'
        ordering = ['code']
        verbose_name = 'Program'
        verbose_name_plural = 'Programs'
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Term(models.Model):
    """Represents an academic term/semester."""
    
    code = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    academic_year = models.CharField(max_length=20, help_text='e.g., 2024-2025')
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'terms'
        ordering = ['-start_date', 'code']
        verbose_name = 'Term'
        verbose_name_plural = 'Terms'
    
    def __str__(self):
        return f"{self.code} - {self.academic_year}"
    
    def clean(self):
        """Validate that end_date is after start_date."""
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValidationError({'end_date': 'End date must be after start date.'})
