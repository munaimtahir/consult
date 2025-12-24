# Keystone Compatibility Test Plan

## Purpose

This document provides a comprehensive test plan to verify that the Hospital Consult System works correctly under Keystone's path-based routing (e.g., `http://VPS_IP/{APP_SLUG}/`) while maintaining compatibility with standard root-path deployment (e.g., `http://localhost/`).

## Prerequisites

- Docker and Docker Compose installed
- Basic knowledge of browser developer tools
- Access to terminal/command line

## Test Environment Setup

### Option 1: Local Traefik Simulation (Recommended)

This simulates Keystone's Traefik setup locally.

1. **Create test configuration** (`docker-compose.keystone-test.yml`):

```yaml
version: '3.8'

services:
  traefik:
    image: traefik:v2.10
    container_name: consult_traefik_test
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
    ports:
      - "8080:80"      # App access
      - "8081:8080"    # Traefik dashboard
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      - test_network

  db:
    image: postgres:13-alpine
    environment:
      - POSTGRES_DB=consult_db
      - POSTGRES_USER=consult_user
      - POSTGRES_PASSWORD=consult_password
    networks:
      - test_network

  redis:
    image: redis:7-alpine
    networks:
      - test_network

  backend:
    build: ./backend
    command: uvicorn config.asgi:application --host 0.0.0.0 --port 8000
    environment:
      - APP_SLUG=consult
      - DEBUG=True
      - SECRET_KEY=test-secret-key-change-in-prod
      - ALLOWED_HOSTS=localhost,127.0.0.1
      - DB_NAME=consult_db
      - DB_USER=consult_user
      - DB_PASSWORD=consult_password
      - DB_HOST=db
      - REDIS_URL=redis://redis:6379/0
      - REDIS_HOST=redis
      - CORS_ALLOWED_ORIGINS=http://localhost:8080
      - CSRF_TRUSTED_ORIGINS=http://localhost:8080
      - USE_X_FORWARDED_HOST=True
    depends_on:
      - db
      - redis
    networks:
      - test_network
    labels:
      - "traefik.enable=true"
      # API routes
      - "traefik.http.routers.consult-api.rule=PathPrefix(`/consult/api`)"
      - "traefik.http.middlewares.consult-api-stripprefix.stripprefix.prefixes=/consult"
      - "traefik.http.routers.consult-api.middlewares=consult-api-stripprefix"
      - "traefik.http.services.consult-api.loadbalancer.server.port=8000"
      # WebSocket routes
      - "traefik.http.routers.consult-ws.rule=PathPrefix(`/consult/ws`)"
      - "traefik.http.middlewares.consult-ws-stripprefix.stripprefix.prefixes=/consult"
      - "traefik.http.routers.consult-ws.middlewares=consult-ws-stripprefix"
      # Admin routes
      - "traefik.http.routers.consult-admin.rule=PathPrefix(`/consult/admin`)"
      - "traefik.http.middlewares.consult-admin-stripprefix.stripprefix.prefixes=/consult"
      - "traefik.http.routers.consult-admin.middlewares=consult-admin-stripprefix"
      # Static files
      - "traefik.http.routers.consult-static.rule=PathPrefix(`/consult/static`)"
      - "traefik.http.middlewares.consult-static-stripprefix.stripprefix.prefixes=/consult"
      - "traefik.http.routers.consult-static.middlewares=consult-static-stripprefix"

  frontend:
    build:
      context: ./frontend
      args:
        - VITE_APP_SLUG=consult
        - VITE_API_URL=http://localhost:8080/consult/api/v1
        - VITE_WS_URL=ws://localhost:8080/consult/ws
    networks:
      - test_network
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.consult-frontend.rule=PathPrefix(`/consult`)"
      - "traefik.http.routers.consult-frontend.priority=1"
      - "traefik.http.services.consult-frontend.loadbalancer.server.port=80"

networks:
  test_network:
    driver: bridge
```

2. **Start test environment**:
```bash
docker-compose -f docker-compose.keystone-test.yml up --build
```

3. **Run database migrations**:
```bash
docker-compose -f docker-compose.keystone-test.yml exec backend python manage.py migrate
docker-compose -f docker-compose.keystone-test.yml exec backend python manage.py seed_data
```

### Option 2: Environment Variable Testing

Test with different `APP_SLUG` values using the main docker-compose:

```bash
# Create .env file
cat > .env << EOF
APP_SLUG=consult
VITE_APP_SLUG=consult
VITE_API_URL=http://localhost/consult/api/v1
VITE_WS_URL=ws://localhost/consult/ws
EOF

# Build and start
docker-compose up --build
```

## Test Cases

### Test 1: Root Path Deployment (Local Dev Mode)

**Purpose**: Verify app still works at root path `/` for local development.

**Setup**:
- Ensure `APP_SLUG` is empty or unset
- Use standard URLs (no path prefix)

**Steps**:
1. Start app: `docker-compose up`
2. Open browser: `http://localhost:3000`
3. Login with demo credentials: `admin@pmc.edu.pk` / `adminpassword123`
4. Navigate to Dashboard
5. Navigate to Consults page
6. Create a new consult
7. Open browser DevTools → Network tab
8. Logout

**Expected Results**:
- ✅ All pages load correctly
- ✅ CSS and JavaScript files load (no 404 errors)
- ✅ API calls go to `http://localhost:8000/api/v1/*`
- ✅ Login redirects to `/dashboard`
- ✅ Logout redirects to `/login`
- ✅ No console errors
- ✅ WebSocket connects to `ws://localhost:8000/ws/notifications/`

**Status**: ⬜ Not Started | 🔄 In Progress | ✅ Passed | ❌ Failed

---

### Test 2: Subpath Deployment (Keystone Simulation)

**Purpose**: Verify app works under `/consult/` path with Traefik stripping prefix.

**Setup**:
- Use Option 1 test configuration (Traefik)
- `APP_SLUG=consult`
- `VITE_APP_SLUG=consult`

**Steps**:
1. Start test environment: `docker-compose -f docker-compose.keystone-test.yml up --build`
2. Wait for services to be healthy
3. Open browser: `http://localhost:8080/consult/`
4. Verify login page loads
5. Login with: `admin@pmc.edu.pk` / `adminpassword123`
6. Verify redirect to: `http://localhost:8080/consult/dashboard`
7. Open browser DevTools → Network tab
8. Navigate to Consults: `http://localhost:8080/consult/consults`
9. Click "New Consult" button
10. Verify URL: `http://localhost:8080/consult/consults/new`
11. Navigate to Admin Panel (if admin user)
12. Check static file requests in Network tab
13. Check API requests in Network tab
14. Check WebSocket connection in Network tab (WS filter)
15. Logout

**Expected Results**:
- ✅ Login page loads at `/consult/` with correct styling
- ✅ All CSS/JS files load from `/consult/assets/*` (no 404)
- ✅ Login redirects to `/consult/dashboard`
- ✅ All navigation stays within `/consult/*` paths
- ✅ API calls go to `/consult/api/v1/*` and succeed (200 responses)
- ✅ Static files load from `/consult/static/*`
- ✅ WebSocket connects to `ws://localhost:8080/consult/ws/notifications/`
- ✅ Browser address bar always shows `/consult/*` paths
- ✅ Logout redirects to `/consult/login`
- ✅ Direct URL access works: `http://localhost:8080/consult/dashboard`
- ✅ Browser refresh on any route works correctly
- ✅ No console errors

**Status**: ⬜ Not Started | 🔄 In Progress | ✅ Passed | ❌ Failed

---

### Test 3: Static Files Under Subpath

**Purpose**: Verify Django static files are served correctly under subpath.

**Steps**:
1. Use Keystone test setup
2. Open: `http://localhost:8080/consult/admin/`
3. Inspect Django admin page styling
4. Open DevTools → Network tab
5. Check for requests to `/consult/static/admin/*`

**Expected Results**:
- ✅ Django admin loads with correct styling
- ✅ Static files load from `/consult/static/admin/*`
- ✅ No 404 errors for static files
- ✅ Admin functionality works (can login, navigate)

**Status**: ⬜ Not Started | 🔄 In Progress | ✅ Passed | ❌ Failed

---

### Test 4: API Endpoints Under Subpath

**Purpose**: Verify all API endpoints work correctly under subpath.

**Steps**:
1. Use Keystone test setup
2. Login to app at `/consult/`
3. Open DevTools → Network tab
4. Navigate through these pages:
   - Dashboard
   - Consults list
   - Consult detail (click any consult)
   - New consult form
   - Admin panel (if accessible)
5. Check all API requests

**Expected Results**:
- ✅ All API requests go to `/consult/api/v1/*`
- ✅ All API requests return 200 (or appropriate status)
- ✅ Authentication headers are present
- ✅ CORS headers are correct
- ✅ Data loads correctly on all pages

**Status**: ⬜ Not Started | 🔄 In Progress | ✅ Passed | ❌ Failed

---

### Test 5: WebSocket Under Subpath

**Purpose**: Verify WebSocket connections work under subpath.

**Steps**:
1. Use Keystone test setup
2. Login to app at `/consult/`
3. Open DevTools → Network tab → WS filter
4. Wait for WebSocket connection
5. In another browser/incognito window:
   - Login as different user
   - Create a new consult
6. Check for notification in first window

**Expected Results**:
- ✅ WebSocket connects to `ws://localhost:8080/consult/ws/notifications/`
- ✅ Connection status shows "Connected" (green indicator)
- ✅ WebSocket remains connected (not disconnecting/reconnecting)
- ✅ Real-time notifications appear
- ✅ No WebSocket errors in console

**Status**: ⬜ Not Started | 🔄 In Progress | ✅ Passed | ❌ Failed

---

### Test 6: Authentication Flow Under Subpath

**Purpose**: Verify login/logout flow maintains correct paths.

**Steps**:
1. Use Keystone test setup
2. Open: `http://localhost:8080/consult/dashboard` (while logged out)
3. Verify redirect to login
4. Login with credentials
5. Verify redirect back to dashboard
6. Logout
7. Verify redirect to login

**Expected Results**:
- ✅ Accessing protected route redirects to `/consult/login`
- ✅ After login, redirects to `/consult/dashboard`
- ✅ After logout, redirects to `/consult/login`
- ✅ All redirects maintain `/consult/` prefix
- ✅ Session cookies are set with correct path

**Status**: ⬜ Not Started | 🔄 In Progress | ✅ Passed | ❌ Failed

---

### Test 7: Direct URL Access & Browser Refresh

**Purpose**: Verify SPA routing works correctly with direct URLs and refresh.

**Steps**:
1. Use Keystone test setup
2. Login first
3. Manually enter in address bar:
   - `http://localhost:8080/consult/dashboard`
   - `http://localhost:8080/consult/consults`
   - `http://localhost:8080/consult/consults/new`
   - `http://localhost:8080/consult/adminpanel` (if admin)
4. On each page, press F5 to refresh

**Expected Results**:
- ✅ All direct URLs load correctly
- ✅ Page refresh works on all routes
- ✅ No 404 errors
- ✅ Content loads correctly after refresh
- ✅ User remains authenticated

**Status**: ⬜ Not Started | 🔄 In Progress | ✅ Passed | ❌ Failed

---

### Test 8: Form Submissions Under Subpath

**Purpose**: Verify form submissions (POST requests) work correctly.

**Steps**:
1. Use Keystone test setup
2. Login
3. Go to: `http://localhost:8080/consult/consults/new`
4. Fill out new consult form
5. Submit form
6. Open DevTools → Network tab
7. Check POST request

**Expected Results**:
- ✅ Form submission sends POST to `/consult/api/v1/consults/`
- ✅ Request succeeds (201 Created)
- ✅ Redirect to new consult detail page
- ✅ URL maintains `/consult/` prefix
- ✅ CSRF token is valid

**Status**: ⬜ Not Started | 🔄 In Progress | ✅ Passed | ❌ Failed

---

### Test 9: Search for Hardcoded Paths

**Purpose**: Verify no remaining hardcoded root paths in code.

**Steps**:
1. Run these grep commands:
```bash
# Search for hardcoded absolute paths in frontend
cd frontend/src
grep -r 'href="/' --include="*.jsx" --include="*.js"
grep -r 'src="/' --include="*.jsx" --include="*.js"
grep -r "window.location.href = '/" --include="*.jsx" --include="*.js"
grep -r 'fetch("/' --include="*.jsx" --include="*.js"
grep -r 'axios.get("/' --include="*.jsx" --include="*.js"
grep -r 'navigate("/' --include="*.jsx" --include="*.js" | grep -v 'navigate("/[a-z]'  # Exclude relative routes
```

**Expected Results**:
- ✅ `href="/"` only appears in React Router paths (which use basename)
- ✅ No `window.location.href = '/'` (should use helper function)
- ✅ No `fetch("/")` or `axios.get("/")` (should use apiClient)
- ✅ All `navigate()` calls use relative paths

**Status**: ⬜ Not Started | 🔄 In Progress | ✅ Passed | ❌ Failed

---

### Test 10: Cookie Path Scope

**Purpose**: Verify session/CSRF cookies are scoped correctly.

**Steps**:
1. Use Keystone test setup
2. Login at `/consult/`
3. Open DevTools → Application → Cookies
4. Inspect cookie properties

**Expected Results**:
- ✅ `sessionid` cookie has `Path=/consult`
- ✅ `csrftoken` cookie has `Path=/consult`
- ✅ Cookies are sent with API requests
- ✅ Authentication persists across page navigation

**Status**: ⬜ Not Started | 🔄 In Progress | ✅ Passed | ❌ Failed

---

## Automated Tests

Create a minimal test file: `backend/apps/core/tests/test_keystone.py`

```python
from django.test import TestCase, override_settings
from django.urls import reverse

class KeystoneCompatibilityTestCase(TestCase):
    @override_settings(FORCE_SCRIPT_NAME='/consult')
    def test_static_url_with_app_slug(self):
        """Verify STATIC_URL includes app slug when FORCE_SCRIPT_NAME is set"""
        from django.conf import settings
        self.assertEqual(settings.STATIC_URL, '/consult/static/')
    
    @override_settings(FORCE_SCRIPT_NAME='/consult')
    def test_media_url_with_app_slug(self):
        """Verify MEDIA_URL includes app slug when FORCE_SCRIPT_NAME is set"""
        from django.conf import settings
        self.assertEqual(settings.MEDIA_URL, '/consult/media/')
    
    def test_static_url_without_app_slug(self):
        """Verify STATIC_URL works without app slug (root path)"""
        from django.conf import settings
        # Default should be /static/
        self.assertTrue(settings.STATIC_URL.endswith('/static/'))
    
    @override_settings(FORCE_SCRIPT_NAME='/consult')
    def test_api_urls_with_script_name(self):
        """Verify API URLs resolve correctly with script name"""
        url = reverse('health-check')  # Assuming you have this URL name
        self.assertTrue(url.startswith('/consult/'))
```

Run tests:
```bash
docker-compose exec backend python manage.py test apps.core.tests.test_keystone
```

---

## Negative Tests

### Test 11: Verify Root Path Access Fails (When Deployed for Keystone)

**Purpose**: Ensure that accessing root path doesn't work when app is configured for subpath.

**Steps**:
1. Use Keystone test setup (`APP_SLUG=consult`)
2. Try accessing: `http://localhost:8080/` (root path)

**Expected Results**:
- ✅ Root path returns 404 or Traefik default page
- ✅ App only responds at `/consult/` path

**Status**: ⬜ Not Started | 🔄 In Progress | ✅ Passed | ❌ Failed

---

## Test Summary Template

After completing all tests, fill out this summary:

```
KEYSTONE COMPATIBILITY TEST RESULTS
Date: [YYYY-MM-DD]
Tester: [Name]

Root Path Deployment (Local Dev):
- Test 1: [Status]

Subpath Deployment (Keystone):
- Test 2: [Status]
- Test 3: [Status]
- Test 4: [Status]
- Test 5: [Status]
- Test 6: [Status]
- Test 7: [Status]
- Test 8: [Status]
- Test 9: [Status]
- Test 10: [Status]
- Test 11: [Status]

Automated Tests:
- [X passed / Y total]

Overall Status: ✅ READY FOR KEYSTONE / ❌ ISSUES FOUND

Issues Found:
1. [Description]
2. [Description]

Notes:
[Any additional observations]
```

## Troubleshooting Guide

### Issue: Static files return 404
- Check `APP_SLUG` is set in backend environment
- Verify Traefik stripPrefix middleware is configured
- Run `collectstatic` command

### Issue: API calls fail
- Check `VITE_API_URL` includes the app slug
- Verify CORS_ALLOWED_ORIGINS includes the full origin (without path)
- Check Traefik labels for API router

### Issue: WebSocket won't connect
- Check `VITE_WS_URL` includes the app slug
- Verify Traefik labels for WebSocket router with stripPrefix
- Check browser console for WebSocket errors

### Issue: Login redirect goes to wrong path
- Check `VITE_APP_SLUG` is set during frontend build
- Verify `basename` is used in BrowserRouter
- Check API client helper function for redirects

## Success Criteria

All tests must pass before the application is considered Keystone-ready:
- ✅ All manual tests pass
- ✅ All automated tests pass  
- ✅ No hardcoded absolute paths remain
- ✅ Works both at root path (dev) and subpath (production)
- ✅ No console errors or warnings
- ✅ All features functional under subpath
