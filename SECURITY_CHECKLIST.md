# Security Checklist for Sonali Bank

## Before Deployment

- [ ] Change SECRET_KEY to a new random value
- [ ] Set DEBUG=False in production
- [ ] Update ALLOWED_HOSTS with your domain
- [ ] Generate strong database passwords
- [ ] Configure HTTPS/SSL certificates
- [ ] Set up firewall rules
- [ ] Configure secure session settings
- [ ] Enable CSRF protection
- [ ] Set up rate limiting
- [ ] Configure proper file permissions
- [ ] Set up database backups
- [ ] Configure logging
- [ ] Set up monitoring

## File Permissions

```bash
# .env file
chmod 600 .env

# Media directory
chmod 755 media/
chmod 644 media/*/*/*

# Logs directory
chmod 755 logs/
chmod 640 logs/*

# Static files
chmod 755 staticfiles/
chmod 644 staticfiles/*/*/*