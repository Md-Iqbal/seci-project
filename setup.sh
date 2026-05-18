#!/bin/bash

echo "Setting up Sonali Bank Account Opening System..."

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create MySQL database
echo "Creating MySQL database..."
mysql -u root -p << EOF
CREATE DATABASE IF NOT EXISTS sonali_bank_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'sonali_user'@'localhost' IDENTIFIED BY 'sonali_pass123';
GRANT ALL PRIVILEGES ON sonali_bank_db.* TO 'sonali_user'@'localhost';
FLUSH PRIVILEGES;
EOF

# Create necessary directories
echo "Creating directories..."
mkdir -p media/applicant_photos
mkdir -p media/nid_copies
mkdir -p media/signatures
mkdir -p static
mkdir -p staticfiles

# Run migrations
echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser
echo "Creating superuser..."
python manage.py createsuperuser

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Setup complete!"
echo ""
echo "To start the development server: python manage.py runserver"
echo "To start Celery worker: celery -A sonali_bank worker -l info"
echo "To start Celery beat: celery -A sonali_bank beat -l info"