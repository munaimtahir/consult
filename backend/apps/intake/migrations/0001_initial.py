# Generated migration for Student Intake Submission model

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentIntakeSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submission_id', models.CharField(db_index=True, help_text='Unique submission reference (STU-YYYYMMDD-XXXX)', max_length=50, unique=True)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('NEEDS_REVIEW', 'Needs Review'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], db_index=True, default='PENDING', help_text='Current verification status', max_length=20)),
                ('staff_notes', models.TextField(blank=True, help_text='Internal notes for staff review')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('force_approve', models.BooleanField(default=False, help_text='Admin-only override to bypass duplicate checks')),
                ('full_name', models.CharField(max_length=200)),
                ('father_name', models.CharField(max_length=200)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], max_length=10)),
                ('date_of_birth', models.DateField()),
                ('cnic_or_bform', models.CharField(db_index=True, help_text='CNIC or B-Form number (normalized)', max_length=20)),
                ('mobile', models.CharField(db_index=True, help_text='Mobile phone number (required)', max_length=20)),
                ('email', models.EmailField(db_index=True, help_text='Email address (required)', max_length=254)),
                ('address', models.TextField()),
                ('guardian_name', models.CharField(max_length=200)),
                ('guardian_relation', models.CharField(choices=[('FATHER', 'Father'), ('MOTHER', 'Mother'), ('GUARDIAN', 'Guardian'), ('OTHER', 'Other')], max_length=20)),
                ('guardian_phone_whatsapp', models.CharField(help_text='Guardian WhatsApp number (required)', max_length=20)),
                ('mdcat_roll_number', models.CharField(db_index=True, help_text='MDCAT Roll Number (required, checked for duplicates)', max_length=50)),
                ('merit_number', models.IntegerField(help_text='Merit number (must be > 0)', validators=[django.core.validators.MinValueValidator(1)])),
                ('merit_percentage', models.DecimalField(decimal_places=2, help_text='Merit percentage (0.00-100.00)', max_digits=5, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)])),
                ('last_qualification', models.CharField(choices=[('MATRIC', 'Matric'), ('FSC', 'FSc'), ('A_LEVELS', 'A-Levels'), ('OTHER', 'Other')], max_length=20)),
                ('institute_name', models.CharField(max_length=200)),
                ('board_or_university', models.CharField(max_length=200)),
                ('passing_year', models.IntegerField(validators=[django.core.validators.MinValueValidator(1900), django.core.validators.MaxValueValidator(2100)])),
                ('total_marks_or_grade', models.CharField(max_length=50)),
                ('obtained_marks_or_grade', models.CharField(max_length=50)),
                ('subjects', models.CharField(help_text='Subjects studied (short text)', max_length=500)),
                ('passport_size_photo', models.ImageField(help_text='Passport-size photograph (jpg/png only, max 1MB, REQUIRED)', upload_to='intake/')),
                ('cnic_front', models.FileField(blank=True, help_text='CNIC front (pdf/jpg/png, max 3MB)', null=True, upload_to='intake/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])])),
                ('cnic_back', models.FileField(blank=True, help_text='CNIC back (pdf/jpg/png, max 3MB)', null=True, upload_to='intake/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])])),
                ('domicile', models.FileField(blank=True, help_text='Domicile certificate (pdf/jpg/png, max 3MB)', null=True, upload_to='intake/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])])),
                ('matric_certificate', models.FileField(blank=True, help_text='Matric certificate (pdf/jpg/png, max 3MB)', null=True, upload_to='intake/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])])),
                ('fsc_certificate', models.FileField(blank=True, help_text='FSc certificate (pdf/jpg/png, max 3MB)', null=True, upload_to='intake/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])])),
                ('migration_certificate', models.FileField(blank=True, help_text='Migration certificate (pdf/jpg/png, max 3MB)', null=True, upload_to='intake/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])])),
                ('other_document_1', models.FileField(blank=True, help_text='Other document 1 (pdf/jpg/png, max 3MB)', null=True, upload_to='intake/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])])),
                ('other_document_2', models.FileField(blank=True, help_text='Other document 2 (pdf/jpg/png, max 3MB)', null=True, upload_to='intake/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])])),
                ('approved_by', models.ForeignKey(blank=True, help_text='Staff member who approved this submission', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_intake_submissions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Student Intake Submission',
                'verbose_name_plural': 'Student Intake Submissions',
                'db_table': 'student_intake_submissions',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='studentintakesubmission',
            index=models.Index(fields=['cnic_or_bform'], name='student_int_cnic_or_12345_idx'),
        ),
        migrations.AddIndex(
            model_name='studentintakesubmission',
            index=models.Index(fields=['mobile'], name='student_int_mobile_12345_idx'),
        ),
        migrations.AddIndex(
            model_name='studentintakesubmission',
            index=models.Index(fields=['email'], name='student_int_email_12345_idx'),
        ),
        migrations.AddIndex(
            model_name='studentintakesubmission',
            index=models.Index(fields=['mdcat_roll_number'], name='student_int_mdcat_r_12345_idx'),
        ),
        migrations.AddIndex(
            model_name='studentintakesubmission',
            index=models.Index(fields=['status'], name='student_int_status_12345_idx'),
        ),
        migrations.AddIndex(
            model_name='studentintakesubmission',
            index=models.Index(fields=['submission_id'], name='student_int_submiss_12345_idx'),
        ),
    ]
