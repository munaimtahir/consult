# Email Notification Service - Setup Guide

## Overview

The email notification service has been implemented to send emails for all major consult events. The system is designed to support email reply handling, allowing users to perform actions (like acknowledging a consult) by simply replying to the email.

## Features Implemented

### 1. Email Notifications for All Events

- ✅ **Consult Generation**: Sent when a new consult is created
- ✅ **Consult Acknowledgement**: Sent when a consult is acknowledged
- ✅ **Note Addition**: Sent when a note is added to a consult
- ✅ **Consult Closure**: Sent when a consult is closed
- ✅ **SLA Time Breach**: Sent when a consult exceeds its expected response time
- ✅ **Reassignment**: Sent when a consult is reassigned
- ✅ **Analytics**: Support for sending analytics reports (method ready, needs integration)

### 2. Email Reply Handling

The system includes infrastructure for email reply handling:
- Unique reply tokens for each email
- Reply email addresses (e.g., `reply+{token}@pmc.edu.pk`)
- Command parsing (acknowledged, complete, close)
- API endpoint for processing replies

## Setup Instructions

### 1. Database Migration

Create and run the migration for the new `EmailNotification` model:

```bash
cd backend
python manage.py makemigrations notifications
python manage.py migrate
```

### 2. Environment Variables

Add the following to your `.env` file:

```bash
# Email Configuration (already in settings, but ensure these are set)
EMAIL_HOST_USER=consult@pmc.edu.pk
EMAIL_HOST_PASSWORD=your-app-password-here
EMAIL_DOMAIN=pmc.edu.pk

# Frontend URL (for email links)
FRONTEND_URL=https://your-domain.com
```

### 3. Google Workspace Setup

#### Create App Password

1. Go to Google Account settings
2. Enable 2-Step Verification
3. Generate an App Password for "Mail"
4. Use this password in `EMAIL_HOST_PASSWORD`

#### Configure Email Domain

The system uses `EMAIL_DOMAIN` to generate reply email addresses. Ensure this matches your Google Workspace domain.

### 4. Email Reply Integration (Optional - For Future)

To enable email reply handling, you'll need to set up one of the following:

#### Option A: Google Apps Script (Recommended)

1. Create a Google Apps Script that monitors Gmail
2. When a reply is received to `reply+{token}@pmc.edu.pk`, extract the token
3. Call the API endpoint: `POST /api/email-reply/` with:
   ```json
   {
     "reply_token": "uuid-here",
     "sender_email": "user@pmc.edu.pk",
     "reply_body": "acknowledged"
   }
   ```

#### Option B: Email Webhook Service

Use a service like SendGrid, Mailgun, or similar that can forward emails to your API endpoint.

## Email Templates

All email templates are located in `backend/templates/emails/`:

- `base.html` - Base template with reply instructions
- `new_consult.html` - New consult notification
- `consult_acknowledged.html` - Acknowledgement notification
- `consult_assigned.html` - Assignment notification
- `note_added.html` - Note addition notification
- `consult_completed.html` - Completion notification
- `consult_closed.html` - Closure notification
- `sla_breach.html` - SLA breach alert
- `reassignment.html` - Reassignment notification
- `analytics_report.html` - Analytics report

## API Endpoints

### Email Reply Processing

**Endpoint**: `POST /api/email-reply/`

**Request Body**:
```json
{
  "reply_token": "uuid-string",
  "sender_email": "user@pmc.edu.pk",
  "reply_body": "acknowledged"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Consult #123 has been acknowledged",
  "action_taken": "acknowledge"
}
```

**Note**: In production, add authentication (API key, secret token) to this endpoint.

## Supported Reply Commands

Users can reply to emails with these commands:

- `acknowledged` / `acknowledge` / `ack` - Acknowledge a consult
- `complete` / `completed` - Complete a consult
- `close` / `closed` - Close a consult

## Testing

### Test Email Sending

1. Create a test consult
2. Check that emails are sent to appropriate recipients
3. Verify email templates render correctly

### Test Email Reply (Manual)

1. Send a test email notification
2. Note the reply token from the `EmailNotification` record
3. Call the API endpoint manually:
   ```bash
   curl -X POST http://localhost:8000/api/email-reply/ \
     -H "Content-Type: application/json" \
     -d '{
       "reply_token": "token-here",
       "sender_email": "user@pmc.edu.pk",
       "reply_body": "acknowledged"
     }'
   ```

## Monitoring

### Email Notification Records

All sent emails are tracked in the `EmailNotification` model:

```python
from apps.notifications.models import EmailNotification

# View all notifications
notifications = EmailNotification.objects.all()

# View notifications for a consult
consult_notifications = EmailNotification.objects.filter(consult_id=123)

# View notifications with replies
replied_notifications = EmailNotification.objects.filter(reply_received=True)
```

### Failed Emails

Failed emails are tracked with `sent_successfully=False` and include error messages.

## Scheduled Tasks

The system includes a Celery task that checks for SLA breaches:

- **Task**: `apps.consults.tasks.check_sla_breaches`
- **Schedule**: Every 15 minutes
- **Action**: Sends email notifications for consults that have breached their SLA

Ensure Celery Beat is running to process these tasks.

## Future Enhancements

1. **Google Apps Script Integration**: Set up automatic email reply processing
2. **Email Preferences**: Allow users to configure which emails they receive
3. **Email Digest**: Option to receive daily/weekly summaries instead of individual emails
4. **Rich Email Templates**: Enhanced HTML templates with better styling
5. **Email Analytics**: Track open rates, click rates, etc.

## Troubleshooting

### Emails Not Sending

1. Check `EMAIL_HOST_PASSWORD` is correct (use App Password, not regular password)
2. Verify SMTP settings in `settings/base.py`
3. Check Django logs for email errors
4. Verify `EmailNotification` records are being created

### Reply Handling Not Working

1. Ensure the API endpoint is accessible
2. Verify reply tokens are being generated correctly
3. Check that sender email matches recipient email
4. Review logs for command parsing errors

### Email Templates Not Rendering

1. Verify templates are in `backend/templates/emails/`
2. Check template syntax (Django template language)
3. Ensure context variables are being passed correctly

## Security Considerations

1. **Email Reply Endpoint**: Currently allows any request. In production:
   - Add API key authentication
   - Verify sender email matches token recipient
   - Rate limit the endpoint
   - Add IP whitelist if using webhook service

2. **Reply Tokens**: Tokens are UUIDs, which are hard to guess but:
   - Consider adding expiration
   - Implement token rotation
   - Add rate limiting per token

3. **Email Content**: Ensure no sensitive patient data is exposed in emails (already handled, but review templates)

## Support

For issues or questions, check:
- Django logs: `backend/logs/django.log`
- Email notification records in database
- Celery task logs

