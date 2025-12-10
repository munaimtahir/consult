#!/bin/sh

# Create necessary directories
mkdir -p /app/logs /app/staticfiles /app/media

echo "========================================="
echo "Backend Container Startup"
echo "========================================="

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    # Wait up to 60 seconds for postgres to be ready
    max_attempts=600
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
      if nc -z $DB_HOST $DB_PORT 2>/dev/null; then
        echo "✓ PostgreSQL started at $DB_HOST:$DB_PORT"
        break
      fi
      attempt=$((attempt + 1))
      sleep 0.1
    done
    
    if [ $attempt -eq $max_attempts ]; then
      echo "⚠ Warning: PostgreSQL may not be ready, but continuing..."
    fi
fi

# Apply database migrations
echo ""
echo "========================================="
echo "Applying database migrations..."
echo "========================================="
if python manage.py migrate --noinput; then
    echo "✓ Migrations applied successfully"
else
    echo "✗ Migration failed!"
    exit 1
fi

# Seed the database with initial data
echo ""
echo "========================================="
echo "Seeding the database with demo data..."
echo "========================================="
if python manage.py seed_data; then
    echo ""
    echo "✓ Database seeding completed successfully!"
    echo "========================================="
else
    echo "✗ Seeding failed!"
    exit 1
fi

# Collect static files
echo ""
echo "========================================="
echo "Collecting static files..."
echo "========================================="
if python manage.py collectstatic --noinput; then
    echo "✓ Static files collected successfully"
else
    echo "⚠ Warning: Static file collection had issues (may continue anyway)"
fi

# Start server
echo ""
echo "========================================="
echo "Starting server..."
echo "========================================="
exec "$@"
