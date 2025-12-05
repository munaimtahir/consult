#!/bin/sh

# Create necessary directories
mkdir -p /app/logs /app/staticfiles /app/media

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    # Wait up to 60 seconds for postgres to be ready
    max_attempts=600
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
      if nc -z $DB_HOST $DB_PORT 2>/dev/null; then
        echo "PostgreSQL started at $DB_HOST:$DB_PORT"
        break
      fi
      attempt=$((attempt + 1))
      sleep 0.1
    done
    
    if [ $attempt -eq $max_attempts ]; then
      echo "Warning: PostgreSQL may not be ready, but continuing..."
    fi
fi

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Seed the database with initial data
echo "Seeding the database..."
python manage.py seed_data

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start server
echo "Starting server..."
exec "$@"
