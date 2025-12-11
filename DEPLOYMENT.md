# Deployment Guide

This guide provides simple steps to deploy the Hospital Consult System on a Linux VPS using Docker Compose.

## Multi-App Deployment

This deployment is configured for **multi-app support**, allowing multiple applications to run on the same server. See [MULTI_APP_DEPLOYMENT_PLAN.md](../MULTI_APP_DEPLOYMENT_PLAN.md) for details.

**Key Features:**
- Path-based routing through Nginx
- Health checks for all services
- Resource limits and isolation
- Easy app management scripts

**Quick Management:**
```bash
# List all apps
bash scripts/manage-apps.sh list

# Check health
bash scripts/manage-apps.sh health

# Manage specific app
bash scripts/manage-apps.sh start backend
bash scripts/manage-apps.sh stop frontend
bash scripts/manage-apps.sh logs backend
```

**Adding New Apps:**
See [docs/ADD_NEW_APP_GUIDE.md](../docs/ADD_NEW_APP_GUIDE.md) for instructions.

## Prerequisites

- A Linux VPS with Docker and Docker Compose installed.
- The repository code cloned onto the VPS.

## Deployment Steps

1.  **Navigate to the project directory:**
    ```bash
    cd /path/to/your/project
    ```

2.  **Validate configuration (optional but recommended):**
    ```bash
    # Validate environment variables
    bash scripts/validate-env.sh
    
    # Validate docker-compose configuration
    docker compose config
    ```

3.  **Deploy using the deployment script (recommended):**
    ```bash
    ./scripts/deploy.sh
    ```
    Or manually:
    ```bash
    # Build and run the Docker containers
    docker compose up --build -d
    ```

4.  **Verify the deployment:**
    ```bash
    # Check service status
    docker compose ps
    
    # Check health of all apps
    bash scripts/manage-apps.sh health
    
    # View logs
    docker compose logs -f
    ```
    You should see all services running and health checks passing.

## Accessing the Application

-   **Frontend:** Open your web browser and navigate to `http://34.93.19.177`.
-   **Backend API:** The API is accessible at `http://34.93.19.177/api/v1/`.

## Default Login Credentials

Here are the default credentials from the seed data for demonstration purposes:

| Role             | Email                    | Password        |
| ---------------- | ------------------------ | --------------- |
| **Superuser**    | `admin@pmc.edu.pk`       | `adminpassword123` |
| **System Admin** | `sysadmin@pmc.edu.pk`    | `password123`   |
| **HOD (Cardiology)**|`cardio.hod@pmc.edu.pk` | `password123`   |
| **Doctor (Cardiology)** | `cardio.doc@pmc.edu.pk`  | `password123`   |

For a complete list of users, please refer to the `backend/setup_data.py` file.

---

## Non-Docker Deployment Guide (Backup)

This guide provides instructions for deploying the application on a Linux VPS without using Docker.

### 1. Backend Setup

**a. Prerequisites:**
- Python 3.10+ and Pip
- PostgreSQL
- Redis
- Nginx (or another web server)

**b. Installation:**
1.  **Clone the repository and navigate to the `backend` directory.**
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    pip install gunicorn  # For running the Django app
    ```
4.  **Configure environment variables:**
    Create a `.env` file in the `backend` directory by copying `.env.example` and filling in the values for your database, secret key, etc.
5.  **Run database migrations and seed data:**
    ```bash
    python manage.py migrate
    python manage.py seed_data
    ```
6.  **Collect static files:**
    ```bash
    python manage.py collectstatic
    ```
7.  **Run the backend server with Gunicorn:**
    ```bash
    gunicorn --workers 3 config.wsgi:application
    ```

### 2. Frontend Setup

**a. Prerequisites:**
- Node.js and npm

**b. Installation:**
1.  **Navigate to the `frontend` directory.**
2.  **Install dependencies:**
    ```bash
    npm install
    ```
3.  **Create a production build:**
    ```bash
    VITE_API_URL=http://34.93.19.177/api/v1 VITE_WS_URL=ws://34.93.19.177/ws npm run build
    ```
4.  The static files will be generated in the `frontend/dist` directory.

### 3. Nginx Configuration (Reverse Proxy)

Configure Nginx to serve the frontend and proxy API requests to the backend. A sample configuration can be found in `nginx/default.conf`. You will need to adapt it to serve the static files from `frontend/dist` and proxy to the Gunicorn server.
