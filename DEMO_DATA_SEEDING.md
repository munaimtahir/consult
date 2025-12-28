# Demo Data Seeding Configuration

## ✅ Demo Data Seeding is Already Configured

The demo data seeding is **automatically configured** and will run when the backend container starts.

## How It Works

### 1. Entrypoint Script
The `backend/entrypoint.sh` script automatically:
1. ✅ Waits for PostgreSQL to be ready
2. ✅ Runs database migrations (`python manage.py migrate --noinput`)
3. ✅ **Seeds demo data** (`python manage.py seed_data`)
4. ✅ Collects static files (`python manage.py collectstatic --noinput`)
5. ✅ Starts the server (uvicorn)

### 2. Dockerfile Configuration
The `backend/Dockerfile` uses `entrypoint.sh` as the ENTRYPOINT:
```dockerfile
ENTRYPOINT ["sh", "/app/entrypoint.sh"]
```

### 3. Docker Compose
The `docker-compose.coolify.yml` passes the uvicorn command to the entrypoint:
```yaml
command: uvicorn config.asgi:application --host 0.0.0.0 --port 8000
```

The entrypoint script will execute this command after running migrations and seeding.

## What Demo Data is Created

The `seed_data` management command creates:

- **5 Departments:**
  - Cardiology
  - Neurology
  - Orthopedics
  - General Medicine
  - Emergency

- **17 Users:**
  - Superuser: `admin@pmc.edu.pk`
  - System Admin: `sysadmin@pmc.edu.pk`
  - Department HODs (Heads of Department)
  - Department Doctors
  - Department Professors

- **15 Patients:**
  - Sample patients with various medical conditions

- **12 Consults:**
  - Sample consults at various workflow stages (pending, in-progress, completed)

## Demo Login Credentials

After deployment, you can use these credentials to test:

| Role | Email | Password |
|------|-------|----------|
| **Superuser** | admin@pmc.edu.pk | adminpassword123 |
| **System Admin** | sysadmin@pmc.edu.pk | password123 |
| **Cardiology HOD** | cardio.hod@pmc.edu.pk | password123 |
| **Cardiology Doctor** | cardio.doc@pmc.edu.pk | password123 |
| **Neurology HOD** | neuro.hod@pmc.edu.pk | password123 |
| **Neurology Doctor** | neuro.doc@pmc.edu.pk | password123 |
| **Orthopedics HOD** | ortho.hod@pmc.edu.pk | password123 |
| **ER Doctor** | er.doc@pmc.edu.pk | password123 |

> **Pattern**: All department users follow `{dept}.{role}@pmc.edu.pk` with password `password123`

## Verification

### Check if Demo Data is Loaded

After deployment, verify demo data by:

1. **Login to Django Admin:**
   ```
   https://consult.alshifalab.pk/admin/
   ```
   - Username: `admin@pmc.edu.pk`
   - Password: `adminpassword123`

2. **Check Users:**
   - Go to Admin → Users
   - Should see 17 users

3. **Check Departments:**
   - Go to Admin → Departments
   - Should see 5 departments

4. **Check Patients:**
   - Go to Admin → Patients
   - Should see 15 patients

5. **Check Consults:**
   - Go to Admin → Consults
   - Should see 12 consults

## Manual Seeding (If Needed)

If you need to re-seed the data manually:

### Via Coolify Dashboard
1. Access the backend container shell in Coolify
2. Run:
   ```bash
   python manage.py seed_data
   ```

### Via Docker Compose (Local)
```bash
docker compose exec backend python manage.py seed_data
```

## Important Notes

⚠️ **Warning**: The seed command will:
- Create new users if they don't exist
- Create new departments if they don't exist
- Create new patients and consults
- **Will NOT delete existing data** (it's idempotent)

✅ **Safe to Run**: The seed command is safe to run multiple times - it checks for existing data before creating.

## Troubleshooting

### Demo Data Not Appearing

1. **Check Container Logs:**
   - In Coolify dashboard, check backend container logs
   - Look for "Seeding the database with demo data..." message
   - Check for any errors during seeding

2. **Verify Database Connection:**
   - Ensure database is healthy and accessible
   - Check environment variables: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`

3. **Check Migrations:**
   - Ensure migrations ran successfully before seeding
   - Check logs for "Migrations applied successfully"

4. **Manual Verification:**
   - Access backend container shell
   - Run: `python manage.py seed_data --verbosity=2` for detailed output

### Re-seeding Data

If you need to reset and re-seed:
```bash
# Access backend container
# Flush database (WARNING: Deletes all data)
python manage.py flush --noinput

# Run migrations
python manage.py migrate --noinput

# Seed data
python manage.py seed_data
```

---

**Status**: ✅ Demo data seeding is automatically configured
**Location**: `backend/apps/core/management/commands/seed_data.py`
**Entrypoint**: `backend/entrypoint.sh` (runs automatically on container start)

