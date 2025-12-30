# Migration to add ForeignKey to students.Student
# Run this migration after students app is created

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('intake', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentintakesubmission',
            name='created_student',
            field=models.ForeignKey(
                blank=True,
                help_text='Student record created from this submission (if approved)',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='intake_submission',
                to='students.Student',
            ),
        ),
    ]
