"""
Patient model for Hospital Consult System.
"""

from django.db import models


class Patient(models.Model):
    """
    Patient information (manually entered).
    """
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    mrn = models.CharField(
        max_length=50,
        unique=True,
        help_text='Medical Record Number'
    )
    name = models.CharField(max_length=200)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    ward = models.CharField(max_length=100)
    bed_number = models.CharField(max_length=20)
    primary_department = models.ForeignKey(
        'departments.Department',
        on_delete=models.PROTECT,
        related_name='patients'
    )
    primary_diagnosis = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'patients'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['mrn']),
            models.Index(fields=['primary_department', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} (MRN: {self.mrn})"
    
    @property
    def location(self):
        """Get patient location as formatted string"""
        return f"{self.ward}, Bed {self.bed_number}"
    
    @property
    def consults_count(self):
        """Get number of consults for this patient"""
        return self.consults.count()
