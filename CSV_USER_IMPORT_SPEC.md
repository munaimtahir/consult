# CSV User Import Specification

## Overview

This document specifies the CSV user import functionality for the Hospital Consult System. Admins can upload a CSV file containing user information, and the system will automatically create user accounts with proper hierarchy levels.

---

## CSV Format

### Required Columns

| Column Name | Description | Example | Required |
|-------------|-------------|---------|----------|
| `email` | User's PMC email address | `john.doe@pmc.edu.pk` | Yes |
| `first_name` | User's first name | `John` | Yes |
| `last_name` | User's last name | `Doe` | Yes |
| `department` | Department code or name | `CARDIO` or `Cardiology` | Yes |
| `designation` | User's designation | `Resident 1` | Yes |
| `phone_number` | Contact number | `+92-300-1234567` | No |

### Sample CSV

```csv
email,first_name,last_name,department,designation,phone_number
john.doe@pmc.edu.pk,John,Doe,Cardiology,Resident 1,+92-300-1234567
jane.smith@pmc.edu.pk,Jane,Smith,Cardiology,Senior Registrar,+92-300-7654321
dr.ahmed@pmc.edu.pk,Ahmed,Khan,Cardiology,Assistant Professor,+92-300-1111111
dr.fatima@pmc.edu.pk,Fatima,Ali,Cardiology,Professor,+92-300-2222222
dr.hassan@pmc.edu.pk,Hassan,Malik,Cardiology,HOD,+92-300-3333333
```

---

## Designation to Seniority Level Mapping

The system automatically maps designations to seniority levels for escalation hierarchy:

| Designation | Seniority Level | Role | Description |
|-------------|-----------------|------|-------------|
| `Resident 1` | 1 | DOCTOR | First-year resident |
| `Resident 2` | 2 | DOCTOR | Second-year resident |
| `Resident 3` | 3 | DOCTOR | Third-year resident |
| `Resident 4` | 4 | DOCTOR | Fourth-year resident |
| `Resident 5` | 5 | DOCTOR | Fifth-year resident |
| `Senior Registrar` | 6 | DOCTOR | Senior registrar |
| `Assistant Professor` | 7 | DEPARTMENT_USER | Assistant professor |
| `Professor` | 8 | DEPARTMENT_USER | Professor |
| `HOD` | 9 | HOD | Head of Department |

**Escalation Logic**: When a consult is overdue, it escalates to the next higher seniority level in the same department.

---

## User Model Updates

### New Fields

```python
# apps/accounts/models.py
class User(AbstractUser):
    # ... existing fields ...
    
    designation = models.CharField(
        max_length=50,
        choices=[
            ('RESIDENT_1', 'Resident 1'),
            ('RESIDENT_2', 'Resident 2'),
            ('RESIDENT_3', 'Resident 3'),
            ('RESIDENT_4', 'Resident 4'),
            ('RESIDENT_5', 'Resident 5'),
            ('SENIOR_REGISTRAR', 'Senior Registrar'),
            ('ASSISTANT_PROFESSOR', 'Assistant Professor'),
            ('PROFESSOR', 'Professor'),
            ('HOD', 'Head of Department'),
        ],
        blank=True
    )
    
    # Auto-calculated from designation
    seniority_level = models.IntegerField(default=1)
    
    def save(self, *args, **kwargs):
        # Auto-set seniority level based on designation
        designation_map = {
            'RESIDENT_1': 1,
            'RESIDENT_2': 2,
            'RESIDENT_3': 3,
            'RESIDENT_4': 4,
            'RESIDENT_5': 5,
            'SENIOR_REGISTRAR': 6,
            'ASSISTANT_PROFESSOR': 7,
            'PROFESSOR': 8,
            'HOD': 9,
        }
        if self.designation:
            self.seniority_level = designation_map.get(self.designation, 1)
        
        # Auto-set role based on designation
        if self.designation == 'HOD':
            self.role = 'HOD'
        elif self.designation in ['ASSISTANT_PROFESSOR', 'PROFESSOR']:
            self.role = 'DEPARTMENT_USER'
        else:
            self.role = 'DOCTOR'
        
        super().save(*args, **kwargs)
```

---

## Django Admin Implementation

### CSV Import in Department Admin

```python
# apps/departments/admin.py
from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
from .models import Department
from apps.accounts.models import User
import csv
import io

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'head', 'user_count', 'is_active']
    search_fields = ['name', 'code']
    
    def user_count(self, obj):
        return obj.users.count()
    user_count.short_description = 'Users'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:department_id>/import-users/',
                self.admin_site.admin_view(self.import_users_view),
                name='department_import_users',
            ),
        ]
        return custom_urls + urls
    
    def import_users_view(self, request, department_id):
        """Handle CSV upload for user import"""
        department = Department.objects.get(pk=department_id)
        
        if request.method == 'POST':
            csv_file = request.FILES.get('csv_file')
            
            if not csv_file:
                messages.error(request, 'Please upload a CSV file.')
                return redirect('..')
            
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'File must be a CSV.')
                return redirect('..')
            
            # Parse CSV
            try:
                decoded_file = csv_file.read().decode('utf-8')
                io_string = io.StringIO(decoded_file)
                reader = csv.DictReader(io_string)
                
                created_count = 0
                updated_count = 0
                errors = []
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        email = row.get('email', '').strip()
                        first_name = row.get('first_name', '').strip()
                        last_name = row.get('last_name', '').strip()
                        designation = row.get('designation', '').strip()
                        phone_number = row.get('phone_number', '').strip()
                        
                        # Validation
                        if not email or not email.endswith('@pmc.edu.pk'):
                            errors.append(f'Row {row_num}: Invalid email {email}')
                            continue
                        
                        if not first_name or not last_name:
                            errors.append(f'Row {row_num}: Missing name')
                            continue
                        
                        # Map designation
                        designation_map = {
                            'Resident 1': 'RESIDENT_1',
                            'Resident 2': 'RESIDENT_2',
                            'Resident 3': 'RESIDENT_3',
                            'Resident 4': 'RESIDENT_4',
                            'Resident 5': 'RESIDENT_5',
                            'Senior Registrar': 'SENIOR_REGISTRAR',
                            'Assistant Professor': 'ASSISTANT_PROFESSOR',
                            'Professor': 'PROFESSOR',
                            'HOD': 'HOD',
                        }
                        
                        designation_code = designation_map.get(designation)
                        if not designation_code:
                            errors.append(f'Row {row_num}: Invalid designation {designation}')
                            continue
                        
                        # Create or update user
                        user, created = User.objects.update_or_create(
                            email=email,
                            defaults={
                                'username': email.split('@')[0],
                                'first_name': first_name,
                                'last_name': last_name,
                                'department': department,
                                'designation': designation_code,
                                'phone_number': phone_number,
                            }
                        )
                        
                        if created:
                            created_count += 1
                        else:
                            updated_count += 1
                    
                    except Exception as e:
                        errors.append(f'Row {row_num}: {str(e)}')
                
                # Show results
                if created_count > 0:
                    messages.success(request, f'Created {created_count} users.')
                if updated_count > 0:
                    messages.info(request, f'Updated {updated_count} users.')
                if errors:
                    for error in errors[:10]:  # Show first 10 errors
                        messages.warning(request, error)
                    if len(errors) > 10:
                        messages.warning(request, f'... and {len(errors) - 10} more errors.')
                
                return redirect('..')
            
            except Exception as e:
                messages.error(request, f'Error processing CSV: {str(e)}')
                return redirect('..')
        
        # GET request - show upload form
        context = {
            'department': department,
            'title': f'Import Users for {department.name}',
        }
        return render(request, 'admin/department_import_users.html', context)
```

### Admin Template

```html
<!-- templates/admin/department_import_users.html -->
{% extends "admin/base_site.html" %}

{% block content %}
<h1>{{ title }}</h1>

<div class="module">
    <h2>Upload CSV File</h2>
    
    <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        
        <div class="form-row">
            <label for="csv_file">CSV File:</label>
            <input type="file" name="csv_file" id="csv_file" accept=".csv" required>
        </div>
        
        <div class="submit-row">
            <input type="submit" value="Import Users" class="default">
            <a href="{% url 'admin:departments_department_changelist' %}" class="button cancel-link">Cancel</a>
        </div>
    </form>
</div>

<div class="module">
    <h2>CSV Format</h2>
    <p>The CSV file must have the following columns:</p>
    <ul>
        <li><strong>email</strong> - User's PMC email (must end with @pmc.edu.pk)</li>
        <li><strong>first_name</strong> - User's first name</li>
        <li><strong>last_name</strong> - User's last name</li>
        <li><strong>department</strong> - Department name (will use current department)</li>
        <li><strong>designation</strong> - One of: Resident 1, Resident 2, Resident 3, Resident 4, Resident 5, Senior Registrar, Assistant Professor, Professor, HOD</li>
        <li><strong>phone_number</strong> - Contact number (optional)</li>
    </ul>
    
    <h3>Sample CSV:</h3>
    <pre>email,first_name,last_name,department,designation,phone_number
john.doe@pmc.edu.pk,John,Doe,Cardiology,Resident 1,+92-300-1234567
jane.smith@pmc.edu.pk,Jane,Smith,Cardiology,Senior Registrar,+92-300-7654321
dr.ahmed@pmc.edu.pk,Ahmed,Khan,Cardiology,Professor,+92-300-1111111</pre>
</div>
{% endblock %}
```

---

## Management Command

For bulk imports from command line:

```python
# apps/accounts/management/commands/import_users.py
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.accounts.models import User
from apps.departments.models import Department
import csv

class Command(BaseCommand):
    help = 'Import users from CSV file'
    
    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')
    
    def handle(self, *args, **options):
        csv_file = options['csv_file']
        
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            
            created_count = 0
            updated_count = 0
            
            for row in reader:
                email = row['email'].strip()
                department_name = row['department'].strip()
                
                # Get or create department
                department, _ = Department.objects.get_or_create(
                    name=department_name,
                    defaults={'code': department_name[:10].upper()}
                )
                
                # Map designation
                designation_map = {
                    'Resident 1': 'RESIDENT_1',
                    'Resident 2': 'RESIDENT_2',
                    'Resident 3': 'RESIDENT_3',
                    'Resident 4': 'RESIDENT_4',
                    'Resident 5': 'RESIDENT_5',
                    'Senior Registrar': 'SENIOR_REGISTRAR',
                    'Assistant Professor': 'ASSISTANT_PROFESSOR',
                    'Professor': 'PROFESSOR',
                    'HOD': 'HOD',
                }
                
                designation_code = designation_map.get(row['designation'].strip())
                
                # Create or update user
                user, created = User.objects.update_or_create(
                    email=email,
                    defaults={
                        'username': email.split('@')[0],
                        'first_name': row['first_name'].strip(),
                        'last_name': row['last_name'].strip(),
                        'department': department,
                        'designation': designation_code,
                        'phone_number': row.get('phone_number', '').strip(),
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'Created: {email}'))
                else:
                    updated_count += 1
                    self.stdout.write(self.style.WARNING(f'Updated: {email}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nTotal: {created_count} created, {updated_count} updated'))
```

**Usage**:
```bash
python manage.py import_users users.csv
```

---

## Validation Rules

1. **Email Validation**:
   - Must end with `@pmc.edu.pk`
   - Must be unique
   - Must be valid email format

2. **Designation Validation**:
   - Must be one of the allowed designations
   - Case-sensitive matching

3. **Department Validation**:
   - Department must exist in the system
   - If importing via Department Admin, uses current department

4. **Name Validation**:
   - First name and last name are required
   - Cannot be empty

---

## User Login Flow

1. **First-time Login**:
   - User clicks "Sign in with Google Workspace"
   - Google OAuth validates `@pmc.edu.pk` email
   - Backend checks if user exists in database
   - If user was imported via CSV, account is already created with proper role/department
   - User is logged in and redirected to dashboard

2. **Subsequent Logins**:
   - User clicks "Sign in with Google Workspace"
   - Google OAuth validates
   - User is logged in immediately

3. **User Not in CSV**:
   - If user's email is not in the imported CSV
   - System can either:
     - **Option A**: Reject login (strict mode)
     - **Option B**: Create account with default role (DOCTOR) and no department (requires admin assignment)

---

## Admin Interface Features

### Department Admin

- **List View**: Shows department name, code, head, and user count
- **Detail View**: Shows all users in department
- **Import Users Button**: Opens CSV upload form
- **Bulk Actions**: Activate/deactivate users

### User Admin

- **List View**: Shows email, name, department, designation, seniority level
- **Filters**: Filter by department, role, designation
- **Search**: Search by email, name
- **Inline Editing**: Edit user details directly

---

## CSV Template Download

Provide a downloadable CSV template in the admin interface:

```python
# apps/departments/admin.py (add to DepartmentAdmin)
def download_csv_template(self, request):
    """Download CSV template"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="user_import_template.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['email', 'first_name', 'last_name', 'department', 'designation', 'phone_number'])
    writer.writerow(['john.doe@pmc.edu.pk', 'John', 'Doe', 'Cardiology', 'Resident 1', '+92-300-1234567'])
    writer.writerow(['jane.smith@pmc.edu.pk', 'Jane', 'Smith', 'Cardiology', 'Senior Registrar', '+92-300-7654321'])
    
    return response
```

---

## Testing

### Test Cases

1. **Valid CSV Import**:
   - Upload CSV with valid data
   - Verify all users are created
   - Verify seniority levels are correct
   - Verify roles are assigned correctly

2. **Invalid Email**:
   - Upload CSV with non-PMC email
   - Verify error message is shown
   - Verify user is not created

3. **Duplicate Email**:
   - Upload CSV with duplicate email
   - Verify existing user is updated
   - Verify no duplicate users are created

4. **Invalid Designation**:
   - Upload CSV with invalid designation
   - Verify error message is shown
   - Verify user is not created

5. **HOD Assignment**:
   - Upload CSV with HOD designation
   - Verify user role is set to HOD
   - Verify seniority level is 9
   - Verify department head is updated

---

## Future Enhancements

1. **Excel Support**: Support `.xlsx` files in addition to CSV
2. **Bulk Update**: Allow updating existing users via CSV
3. **Export Users**: Export department users to CSV
4. **Validation Preview**: Show preview before importing
5. **Undo Import**: Ability to rollback an import
6. **Import History**: Track all imports with timestamps and user

---

## Summary

The CSV user import feature allows admins to:
- ✅ Bulk import users with hierarchy levels
- ✅ Automatically map designations to seniority levels
- ✅ Assign users to departments
- ✅ Enable Google SSO login for all imported users
- ✅ Maintain escalation hierarchy for consult system

Users can login via Google Workspace SSO without manual account creation, and the system automatically assigns them the correct role and department based on the imported data.
