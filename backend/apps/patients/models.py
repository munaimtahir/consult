"""
Patient model for Hospital Consult System.
"""

from django.db import models


class Patient(models.Model):
    """Represents a patient in the hospital.

    This model stores essential demographic and clinical information about a
    patient, such as their medical record number (MRN), name, age, and
    primary diagnosis.

    Attributes:
        mrn: The patient's unique Medical Record Number.
        name: The full name of the patient.
        age: The age of the patient.
        gender: The gender of the patient.
        ward: The ward where the patient is currently located.
        bed_number: The patient's bed number in the ward.
        primary_department: The department primarily responsible for the
                            patient's care.
        primary_diagnosis: The patient's primary diagnosis.
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
        """Returns the patient's location as a formatted string.

        Returns:
            A string in the format "Ward, Bed Bed Number".
        """
        return f"{self.ward}, Bed {self.bed_number}"
    
    @property
    def consults_count(self):
        """Returns the number of consults associated with this patient.

        Returns:
            An integer representing the total number of consults.
        """
        return self.consults.count()
