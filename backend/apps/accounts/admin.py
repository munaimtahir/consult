"""
Django admin configuration for User model with CSV import functionality.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
from .models import User
import csv
import io


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User admin with CSV import functionality.
    """
    
    list_display = ['email', 'get_full_name', 'department', 'designation', 'role', 'seniority_level', 'is_active']
    list_filter = ['role', 'designation', 'department', 'is_active', 'is_staff']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['department', '-seniority_level']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number', 'profile_photo')}),
        ('Hospital Info', {'fields': ('department', 'designation', 'role', 'seniority_level', 'is_on_call')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'department', 'designation'),
        }),
    )
    
    readonly_fields = ['seniority_level', 'role']
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'import-csv/',
                self.admin_site.admin_view(self.import_csv_view),
                name='accounts_user_import_csv',
            ),
        ]
        return custom_urls + urls
    
    def import_csv_view(self, request):
        """Handle CSV upload for bulk user import"""
        if request.method == 'POST':
            csv_file = request.FILES.get('csv_file')
            
            if not csv_file:
                messages.error(request, 'Please upload a CSV file.')
                return redirect('..')
            
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'File must be a CSV.')
                return redirect('..')
            
            try:
                from apps.departments.models import Department
                
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
                        department_name = row.get('department', '').strip()
                        designation = row.get('designation', '').strip()
                        phone_number = row.get('phone_number', '').strip()
                        
                        # Validation
                        if not email or not email.endswith('@pmc.edu.pk'):
                            errors.append(f'Row {row_num}: Invalid email {email}')
                            continue
                        
                        if not first_name or not last_name:
                            errors.append(f'Row {row_num}: Missing name')
                            continue
                        
                        # Get or create department
                        department = None
                        if department_name:
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
                        
                        designation_code = designation_map.get(designation, '')
                        
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
                    for error in errors[:10]:
                        messages.warning(request, error)
                    if len(errors) > 10:
                        messages.warning(request, f'... and {len(errors) - 10} more errors.')
                
                return redirect('..')
            
            except Exception as e:
                messages.error(request, f'Error processing CSV: {str(e)}')
                return redirect('..')
        
        # GET request - show upload form
        context = {
            'title': 'Import Users from CSV',
            'opts': self.model._meta,
        }
        return render(request, 'admin/accounts/user_import_csv.html', context)
