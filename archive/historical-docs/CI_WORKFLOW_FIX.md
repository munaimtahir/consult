# Docker CI Workflow Fix

## Issue Summary

The Docker CI workflow (job 57780218275) was failing with the following error:

```
decouple.UndefinedValueError: DB_NAME not found. Declare it as envvar or define a default value.
```

## Root Cause Analysis

### Problem Identification

1. **Backend Dockerfile Configuration**
   - The Dockerfile sets `ENV DJANGO_SETTINGS_MODULE config.settings.production` (line 6)
   - This forces the container to use production settings

2. **Production Settings Requirements**
   - File: `backend/config/settings/production.py`
   - Lines 15-19 require these environment variables:
     - `DB_NAME` (required, no default)
     - `DB_USER` (required, no default)
     - `DB_PASSWORD` (required, no default)
     - `DB_HOST` (defaults to 'localhost')
     - `DB_PORT` (defaults to '5432')

3. **CI Workflow Issue**
   - The "Test Backend Image" step runs: `docker run --rm consult-backend:test python manage.py --help`
   - Django loads settings on startup, even for `--help` command
   - Production settings try to access `DB_NAME` via `config('DB_NAME')`
   - No environment variables provided → `UndefinedValueError`

### Why This Happens

The `python-decouple` library's `config()` function:
- Looks for environment variables first
- Falls back to `.env` file
- If not found and no default provided → raises `UndefinedValueError`

## Solution Implemented

### Changes Made to `.github/workflows/docker-ci.yml`

#### 1. Test Backend Image Step (Lines 50-61)

**Before:**
```yaml
- name: Test Backend Image
  run: |
    docker run --rm consult-backend:test python manage.py --help > /dev/null
    echo "✓ Backend image is functional"
```

**After:**
```yaml
- name: Test Backend Image
  run: |
    # Test that the image can run help command with required env vars
    docker run --rm \
      -e DB_NAME=test_db \
      -e DB_USER=test_user \
      -e DB_PASSWORD=test_pass \
      -e DB_HOST=localhost \
      -e DB_PORT=5432 \
      -e SECRET_KEY=test-secret-key-for-ci \
      consult-backend:test python manage.py --help > /dev/null
    echo "✓ Backend image is functional"
```

**Reasoning:**
- Provides minimal test values for all required database environment variables
- Allows Django to load production settings without errors
- Uses harmless test values that don't connect to any real database

#### 2. Docker Compose Build Step (Lines 85-102)

**Before:**
```yaml
- name: Build with docker-compose (smoke test)
  run: |
    docker compose build
    echo "✓ All services build successfully via docker-compose"
  env:
    VITE_API_URL: http://localhost:8000/api/v1
    VITE_WS_URL: ws://localhost:8000/ws
```

**After:**
```yaml
- name: Build with docker-compose (smoke test)
  run: |
    # Create minimal .env file for docker-compose build
    cat > .env << EOF
    DB_NAME=test_db
    DB_USER=test_user
    DB_PASSWORD=test_pass
    DB_HOST=localhost
    DB_PORT=5432
    SECRET_KEY=test-secret-key-for-ci
    VITE_API_URL=http://localhost:8000/api/v1
    VITE_WS_URL=ws://localhost:8000/ws
    EOF
    
    docker compose build
    echo "✓ All services build successfully via docker-compose"
```

**Reasoning:**
- Docker Compose reads `.env` file automatically
- Creates a temporary `.env` file with test values
- Provides environment variables for both backend and frontend builds
- File is temporary and only exists during CI run

## Validation

### YAML Syntax Check
```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/docker-ci.yml'))"
✓ YAML syntax is valid
```

### Expected Behavior

With these changes, the workflow should now:

1. ✅ **Validate docker-compose configuration**
   - Checks YAML syntax
   - No database connection needed

2. ✅ **Build Backend Docker Image**
   - Installs dependencies
   - No database connection needed

3. ✅ **Test Backend Image**
   - Runs `python manage.py --help`
   - Django loads production settings
   - Environment variables provided → No error
   - Command completes successfully

4. ✅ **Build Frontend Docker Image**
   - Builds with Vite
   - No database connection needed

5. ✅ **Test Frontend Image**
   - Starts nginx container
   - Serves static files
   - No database connection needed

6. ✅ **Build with docker-compose**
   - Creates .env file with test values
   - Builds all services
   - No services started (no postgres/redis needed)

7. ✅ **Show image sizes**
   - Informational output
   - No errors expected

## Alternative Solutions Considered

### Option 1: Use Development Settings (Not Chosen)
**Approach:** Change Dockerfile to use `config.settings.development`

**Pros:**
- Development settings use SQLite (no DB env vars needed)

**Cons:**
- Dockerfile would not match production configuration
- CI wouldn't test actual production setup
- Defeats purpose of Docker CI validation

### Option 2: Add Defaults to Production Settings (Not Chosen)
**Approach:** Add defaults like `config('DB_NAME', default='default_db')`

**Pros:**
- Would prevent errors without env vars

**Cons:**
- Violates security best practices
- Production settings should require explicit configuration
- Could hide misconfiguration in actual deployments

### Option 3: Provide Environment Variables (✅ Chosen)
**Approach:** Add env vars to CI workflow

**Pros:**
- Maintains production settings integrity
- Tests actual production configuration
- Clear and explicit
- No code changes to application

**Cons:**
- Requires CI workflow updates (minimal effort)

## Testing in CI Environment

The changes have been pushed to the branch. To verify the fix:

1. **Monitor Workflow Run**
   - Check GitHub Actions tab
   - Look for "Docker CI" workflow
   - Should see all steps passing with ✓

2. **Expected Output**
   ```
   ✓ docker-compose.yml is valid
   ✓ Backend image built successfully
   ✓ Backend image is functional
   ✓ Frontend image built successfully
   ✓ Frontend image is functional
   ✓ All services build successfully via docker-compose
   ```

3. **Failure Indicators (Should Not Occur)**
   - ❌ `decouple.UndefinedValueError: DB_NAME not found`
   - ❌ Exit code 1 from backend test
   - ❌ Build failures

## Additional Notes

### Security Considerations

**Test Values Used:**
- `DB_NAME=test_db` - Harmless test database name
- `DB_USER=test_user` - Non-privileged test user
- `DB_PASSWORD=test_pass` - Test password (no real database to access)
- `SECRET_KEY=test-secret-key-for-ci` - Only used during build/validation

**Why This Is Safe:**
- No actual database connection is made
- No services are started in CI
- Values are only used for Django settings validation
- No data is persisted or exposed

### Environment Variables in Production

In actual production deployment:
- Use secure, unique values
- Store in environment variables or secrets manager
- Never commit to version control
- Use strong passwords
- Rotate credentials regularly

### docker-compose.yml Configuration

The `docker-compose.yml` already has good defaults:
```yaml
environment:
  - DB_NAME=${DB_NAME:-consult_db}
  - DB_USER=${DB_USER:-consult_user}
  - DB_PASSWORD=${DB_PASSWORD:-consult_password}
```

The `${VAR:-default}` syntax means:
- Use `$VAR` if set
- Otherwise use `default` value

This works well for local development but CI needs explicit values during build phase.

## Summary

**Problem:** Docker CI failing due to missing database environment variables

**Solution:** Added environment variables to CI workflow steps

**Result:** Workflow can now validate Docker images without database connection errors

**Commit:** b041fa6 - "Fix Docker CI workflow by adding required database environment variables"

**Status:** ✅ Ready for CI validation
