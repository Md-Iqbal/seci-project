#!/bin/bash

echo "=========================================="
echo "Sonali Bank Production Deployment"
echo "=========================================="

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root${NC}" 
   exit 1
fi

# Backup existing database
echo -e "${GREEN}Backing up database...${NC}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mysqldump -u root -p sonali_bank_db > backup_$TIMESTAMP.sql

# Pull latest code
echo -e "${GREEN}Pulling latest code...${NC}"
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo -e "${GREEN}Installing dependencies...${NC}"
pip install -r requirements.txt

# Run migrations
echo -e "${GREEN}Running migrations...${NC}"
python manage.py migrate

# Collect static files
echo -e "${GREEN}Collecting static files...${NC}"
python manage.py collectstatic --noinput

# Set proper permissions
echo -e "${GREEN}Setting permissions...${NC}"
chown -R www-data:www-data media/
chown -R www-data:www-data staticfiles/
chown -R www-data:www-data logs/
chmod 600 .env

# Restart services
echo -e "${GREEN}Restarting services...${NC}"
systemctl restart gunicorn
systemctl restart nginx
systemctl restart celery
systemctl restart celerybeat

# Check service status
echo -e "${GREEN}Checking service status...${NC}"
systemctl status gunicorn --no-pager
systemctl status celery --no-pager

echo ""
echo "=========================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "=========================================="