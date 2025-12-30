"""
Views for Student Intake submissions.
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from .forms import StudentIntakeForm
from .models import StudentIntakeSubmission


@require_http_methods(["GET", "POST"])
def student_intake_form(request):
    """Public form view for student intake submissions."""
    
    # Check cooldown (anti-spam)
    last_submission_time = request.session.get('last_intake_submission_time')
    if last_submission_time:
        time_diff = (timezone.now().timestamp() - last_submission_time)
        if time_diff < 60:  # 60 seconds cooldown
            remaining = int(60 - time_diff)
            messages.error(
                request,
                f'Please wait {remaining} seconds before submitting again.'
            )
            return render(request, 'intake/student_intake_form.html', {
                'form': StudentIntakeForm(),
                'cooldown_remaining': remaining,
            })
    
    if request.method == 'POST':
        form = StudentIntakeForm(request.POST, request.FILES)
        if form.is_valid():
            # Create submission with PENDING status
            submission = form.save(commit=False)
            submission.status = 'PENDING'
            submission.save()
            
            # Update session cooldown
            request.session['last_intake_submission_time'] = timezone.now().timestamp()
            
            # Redirect to success page
            return redirect('intake:success', submission_id=submission.submission_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StudentIntakeForm()
    
    return render(request, 'intake/student_intake_form.html', {
        'form': form,
    })


def student_intake_success(request, submission_id):
    """Success page after form submission."""
    try:
        submission = StudentIntakeSubmission.objects.get(submission_id=submission_id)
    except StudentIntakeSubmission.DoesNotExist:
        messages.error(request, 'Invalid submission ID.')
        return redirect('intake:form')
    
    return render(request, 'intake/student_intake_success.html', {
        'submission': submission,
    })
