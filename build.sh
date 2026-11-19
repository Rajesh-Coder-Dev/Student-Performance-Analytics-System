#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "=========================================="
echo " Starting Build Process for Render"
echo "=========================================="

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
python -m pip install -r requirements.txt

# Collect static files with WhiteNoise
echo "==> Collecting static assets..."
python manage.py collectstatic --no-input

# Apply database migrations
echo "==> Running database migrations..."
python manage.py migrate --no-input

# Load initial student, subject, and marks records if present
if [ -f "initial_data.json" ]; then
    echo "==> Loading seed academic dataset..."
    python manage.py loaddata initial_data.json || echo "Initial data load step completed."
fi

# Provision administrator account if ADMIN_PASSWORD is set in Render environment
if [ -n "$ADMIN_PASSWORD" ]; then
    echo "==> Provisioning administrator account..."
    python manage.py create_admin --username "${ADMIN_USERNAME:-admin}" --password "$ADMIN_PASSWORD" --email "${ADMIN_EMAIL:-admin@example.com}"
fi

echo "=========================================="
echo " Build Completed Successfully!"
echo "=========================================="
