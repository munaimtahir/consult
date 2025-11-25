# Google Workspace Setup Guide

This guide will walk you through setting up Google Workspace SSO and SMTP for the Hospital Consult System.

---

## Prerequisites

- Google Workspace account with admin access
- Your hospital domain configured in Google Workspace (e.g., `yourhospital.com`)

---

## Part 1: OAuth 2.0 Setup (for SSO Login)

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** → **"New Project"**
3. Enter project details:
   - **Project name**: `Hospital Consult System`
   - **Organization**: Select your hospital organization
4. Click **"Create"**

### Step 2: Enable Google+ API

1. In the Google Cloud Console, go to **"APIs & Services"** → **"Library"**
2. Search for **"Google+ API"**
3. Click on it and press **"Enable"**

### Step 3: Configure OAuth Consent Screen

1. Go to **"APIs & Services"** → **"OAuth consent screen"**
2. Select **"Internal"** (only users in your organization can sign in)
3. Click **"Create"**
4. Fill in the application information:
   - **App name**: `Hospital Consult System`
   - **User support email**: Your admin email
   - **App logo**: (Optional) Upload hospital logo
   - **Authorized domains**: `yourhospital.com`
   - **Developer contact**: Your admin email
5. Click **"Save and Continue"**
6. **Scopes**: Click **"Add or Remove Scopes"**
   - Select: `email`, `profile`, `openid`
7. Click **"Save and Continue"**
8. Review and click **"Back to Dashboard"**

### Step 4: Create OAuth 2.0 Credentials

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"Create Credentials"** → **"OAuth client ID"**
3. Select **"Web application"**
4. Enter details:
   - **Name**: `Hospital Consult System - Web Client`
   - **Authorized JavaScript origins**:
     ```
     http://localhost:3000
     https://consult.yourhospital.com
     ```
   - **Authorized redirect URIs**:
     ```
     http://localhost:3000/api/auth/callback/google
     https://consult.yourhospital.com/api/auth/callback/google
     http://localhost:8000/accounts/google/login/callback/
     https://api.consult.yourhospital.com/accounts/google/login/callback/
     ```
5. Click **"Create"**
6. **Save the credentials**:
   - **Client ID**: `123456789-abcdefg.apps.googleusercontent.com`
   - **Client Secret**: `GOCSPX-xxxxxxxxxxxxxxxx`

### Step 5: Add Credentials to Your Project

**Backend (.env)**
```bash
# backend/.env
GOOGLE_OAUTH_CLIENT_ID=123456789-abcdefg.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxxxxx
```

**Frontend (.env.local)**
```bash
# frontend/.env.local
GOOGLE_CLIENT_ID=123456789-abcdefg.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxxxxx
```

---

## Part 2: SMTP Setup (for Email Notifications)

### Step 1: Create Service Account Email

1. Go to [Google Admin Console](https://admin.google.com/)
2. Navigate to **"Users"**
3. Click **"Add new user"**
4. Create user:
   - **First name**: `No Reply`
   - **Last name**: `Consult System`
   - **Primary email**: `noreply@yourhospital.com`
   - **Password**: Generate strong password
5. Click **"Add new user"**

### Step 2: Generate App Password

> **Note**: App Passwords are required if you have 2-Step Verification enabled (recommended).

1. Sign in to the service account: `noreply@yourhospital.com`
2. Go to [Google Account Security](https://myaccount.google.com/security)
3. Under **"Signing in to Google"**, click **"2-Step Verification"**
4. Enable 2-Step Verification if not already enabled
5. Scroll down to **"App passwords"**
6. Click **"App passwords"**
7. Select:
   - **App**: `Mail`
   - **Device**: `Other (Custom name)`
   - **Name**: `Hospital Consult System`
8. Click **"Generate"**
9. **Copy the 16-character app password** (e.g., `abcd efgh ijkl mnop`)

### Step 3: Add SMTP Credentials to Backend

```bash
# backend/.env
EMAIL_HOST_USER=noreply@yourhospital.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop  # Remove spaces from app password
```

### Step 4: Test Email Sending

**Django Shell Test**
```bash
cd backend
python manage.py shell
```

```python
from django.core.mail import send_mail

send_mail(
    subject='Test Email from Hospital Consult System',
    message='This is a test email.',
    from_email='noreply@yourhospital.com',
    recipient_list=['your-email@yourhospital.com'],
    fail_silently=False,
)
```

If successful, you should receive the test email.

---

## Part 3: Domain Verification (Production Only)

### Step 1: Verify Domain Ownership

1. Go to [Google Search Console](https://search.google.com/search-console)
2. Click **"Add property"**
3. Enter your domain: `consult.yourhospital.com`
4. Follow verification instructions (DNS TXT record or HTML file upload)

### Step 2: Configure DNS Records

Add these DNS records to your domain:

**SPF Record** (Prevents email spoofing)
```
Type: TXT
Name: @
Value: v=spf1 include:_spf.google.com ~all
```

**DKIM Record** (Email authentication)
1. Go to [Google Admin Console](https://admin.google.com/)
2. Navigate to **"Apps"** → **"Google Workspace"** → **"Gmail"** → **"Authenticate email"**
3. Click **"Generate new record"**
4. Copy the DKIM record and add it to your DNS

**DMARC Record** (Email reporting)
```
Type: TXT
Name: _dmarc
Value: v=DMARC1; p=none; rua=mailto:dmarc-reports@yourhospital.com
```

---

## Part 4: Security Configuration

### Step 1: Restrict OAuth to Your Domain

In your Django settings:

```python
# config/settings/base.py
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'AUTH_PARAMS': {
            'hd': 'yourhospital.com',  # Only allow your domain
        },
    }
}
```

In your NextAuth configuration:

```typescript
// app/api/auth/[...nextauth]/route.ts
GoogleProvider({
  authorization: {
    params: {
      hd: 'yourhospital.com', // Only allow your domain
    },
  },
})
```

### Step 2: Email Domain Validation

```python
# apps/accounts/signals.py
ALLOWED_EMAIL_DOMAIN = 'yourhospital.com'

@receiver(pre_save, sender=User)
def validate_email_domain(sender, instance, **kwargs):
    if instance.email and not instance.email.endswith(f'@{ALLOWED_EMAIL_DOMAIN}'):
        raise ValidationError(
            f'Only {ALLOWED_EMAIL_DOMAIN} email addresses are allowed.'
        )
```

---

## Part 5: Testing the Integration

### Test 1: SSO Login

1. Start your development servers:
   ```bash
   # Backend
   cd backend
   python manage.py runserver
   
   # Frontend
   cd frontend
   npm run dev
   ```

2. Navigate to `http://localhost:3000/login`
3. Click **"Sign in with Google Workspace"**
4. Sign in with your `@yourhospital.com` account
5. Verify you're redirected to the dashboard

### Test 2: Email Sending

1. Create a test consult request
2. Check that email is sent to the target department
3. Verify email content and formatting

---

## Troubleshooting

### Issue: "Access blocked: This app's request is invalid"

**Solution**: Make sure you've added the correct redirect URIs in Google Cloud Console.

### Issue: "Error 400: redirect_uri_mismatch"

**Solution**: The redirect URI in your code doesn't match the one in Google Cloud Console. Double-check both.

### Issue: Emails not sending

**Solutions**:
- Verify SMTP credentials are correct
- Check that 2-Step Verification is enabled
- Ensure App Password is generated correctly
- Check firewall allows outbound connections on port 587

### Issue: "Only users in your organization can sign in"

**Solution**: This is expected if you selected "Internal" for OAuth consent screen. External users cannot sign in.

---

## Production Checklist

Before deploying to production:

- [ ] OAuth consent screen is configured as "Internal"
- [ ] Redirect URIs include production domain
- [ ] SMTP credentials are stored securely (environment variables)
- [ ] Email domain is verified in Google Search Console
- [ ] SPF, DKIM, and DMARC records are configured
- [ ] Email domain restriction is enforced in code
- [ ] Test SSO login with multiple user roles
- [ ] Test email sending for all notification types
- [ ] Monitor email delivery rates
- [ ] Setup email bounce handling

---

## Summary

You now have:

✅ Google Workspace SSO configured for secure authentication  
✅ SMTP configured for email notifications  
✅ Domain restrictions to ensure only hospital staff can access  
✅ Email authentication (SPF, DKIM, DMARC) for deliverability  

**Next Steps**: Proceed with Phase 1 implementation in [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md)
