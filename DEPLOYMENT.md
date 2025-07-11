# Deployment Guide

This guide covers deploying the Site Analysis Backend to various production environments.

## Quick Deployment Options

### 1. Heroku Deployment

1. **Install Heroku CLI**
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku
   
   # Or download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Prepare for Heroku**
   ```bash
   # Create Procfile
   echo "web: gunicorn site_analysis_backend.wsgi" > Procfile
   
   # Install additional requirements
   pip install gunicorn whitenoise dj-database-url
   ```

3. **Create and Configure Heroku App**
   ```bash
   heroku create your-app-name
   heroku addons:create heroku-postgresql:hobby-dev
   heroku config:set DJANGO_SETTINGS_MODULE=site_analysis_backend.settings
   heroku config:set DJANGO_SECRET_KEY="your-secret-key"
   heroku config:set DEBUG=False
   heroku config:set OPENWEATHER_API_KEY="your-api-key"
   ```

4. **Deploy**
   ```bash
   git push heroku main
   heroku run python manage.py migrate
   heroku run python manage.py createsuperuser
   ```

### 2. DigitalOcean App Platform

1. **Create app.yaml**
   ```yaml
   name: site-analysis-backend
   services:
   - name: web
     source_dir: /
     github:
       repo: your-username/site-analysis-backend
       branch: main
     run_command: gunicorn site_analysis_backend.wsgi
     environment_slug: python
     instance_count: 1
     instance_size_slug: basic-xxs
     env:
     - key: DJANGO_SETTINGS_MODULE
       value: site_analysis_backend.settings
     - key: DEBUG
       value: "False"
     - key: DJANGO_SECRET_KEY
       value: ${DJANGO_SECRET_KEY}
     - key: OPENWEATHER_API_KEY
       value: ${OPENWEATHER_API_KEY}
   databases:
   - name: site-analysis-db
     engine: PG
     version: "14"
   ```

2. **Deploy via CLI**
   ```bash
   doctl apps create --spec app.yaml
   ```

### 3. AWS Elastic Beanstalk

1. **Install EB CLI**
   ```bash
   pip install awsebcli
   ```

2. **Initialize and Deploy**
   ```bash
   eb init
   eb create production
   eb deploy
   ```

## Production Configuration

### Environment Variables

Create production environment variables:

```bash
# Required
export DJANGO_SECRET_KEY="your-very-secure-secret-key"
export DEBUG=False
export DATABASE_URL="postgis://user:pass@host:port/db"

# Optional but recommended
export OPENWEATHER_API_KEY="your-openweather-api-key"
export NASA_POWER_API_KEY="your-nasa-power-api-key"

# Security
export ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com"
export CSRF_TRUSTED_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"

# Email (if using email features)
export EMAIL_HOST="smtp.gmail.com"
export EMAIL_PORT=587
export EMAIL_HOST_USER="your-email@gmail.com"
export EMAIL_HOST_PASSWORD="your-app-password"
```

### Production Settings

Update `settings.py` for production:

```python
# Add to settings.py
import os
from pathlib import Path

# Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# HTTPS
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Database Setup

#### PostgreSQL with PostGIS on Ubuntu/Debian

```bash
# Install PostgreSQL and PostGIS
sudo apt update
sudo apt install postgresql postgresql-contrib postgis

# Create database and user
sudo -u postgres createuser -P siteanalysis
sudo -u postgres createdb -O siteanalysis site_analysis
sudo -u postgres psql -d site_analysis -c "CREATE EXTENSION postgis;"

# Configure PostgreSQL
sudo nano /etc/postgresql/14/main/postgresql.conf
# Set: shared_preload_libraries = 'postgis'

sudo systemctl restart postgresql
```

#### Database Optimization

```sql
-- Performance tuning for spatial queries
CREATE INDEX CONCURRENTLY idx_siteanalysis_location ON environmental_analysis_siteanalysis USING GIST (location);
CREATE INDEX CONCURRENTLY idx_envfeature_geometry ON environmental_analysis_environmentalfeature USING GIST (geometry);
CREATE INDEX CONCURRENTLY idx_climatedata_location ON environmental_analysis_climatedata USING GIST (location);

-- Additional indexes for common queries
CREATE INDEX CONCURRENTLY idx_siteanalysis_created_at ON environmental_analysis_siteanalysis (created_at);
CREATE INDEX CONCURRENTLY idx_climatedata_date ON environmental_analysis_climatedata (date);
```

## Monitoring and Logging

### Application Monitoring

1. **Sentry for Error Tracking**
   ```bash
   pip install sentry-sdk[django]
   ```
   
   Add to settings.py:
   ```python
   import sentry_sdk
   from sentry_sdk.integrations.django import DjangoIntegration
   
   sentry_sdk.init(
       dsn="your-sentry-dsn",
       integrations=[DjangoIntegration()],
       traces_sample_rate=1.0,
       send_default_pii=True
   )
   ```

2. **Database Monitoring**
   ```python
   # Add to settings.py
   LOGGING = {
       'version': 1,
       'disable_existing_loggers': False,
       'handlers': {
           'file': {
               'level': 'INFO',
               'class': 'logging.FileHandler',
               'filename': '/var/log/django/site_analysis.log',
           },
       },
       'loggers': {
           'django.db.backends': {
               'level': 'DEBUG',
               'handlers': ['file'],
           },
       },
   }
   ```

### Health Checks

Create `health_check.py`:

```python
from django.http import JsonResponse
from django.db import connection
from django.contrib.gis.geos import Point

def health_check(request):
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Test PostGIS
        point = Point(0, 0)
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected',
            'postgis': 'available'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=500)
```

## Performance Optimization

### Caching

1. **Redis Setup**
   ```bash
   # Install Redis
   sudo apt install redis-server
   pip install redis django-redis
   ```

2. **Cache Configuration**
   ```python
   # Add to settings.py
   CACHES = {
       'default': {
           'BACKEND': 'django_redis.cache.RedisCache',
           'LOCATION': 'redis://127.0.0.1:6379/1',
           'OPTIONS': {
               'CLIENT_CLASS': 'django_redis.client.DefaultClient',
           }
       }
   }
   
   # Cache expensive spatial queries
   CACHE_MIDDLEWARE_ALIAS = 'default'
   CACHE_MIDDLEWARE_SECONDS = 600
   CACHE_MIDDLEWARE_KEY_PREFIX = 'site_analysis'
   ```

### Static Files and CDN

1. **AWS S3 for Static Files**
   ```bash
   pip install boto3 django-storages
   ```

2. **Storage Configuration**
   ```python
   # Add to settings.py
   if not DEBUG:
       DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
       STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
       
       AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
       AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
       AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
       AWS_S3_REGION_NAME = 'us-east-1'
   ```

## Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Enable HTTPS
- [ ] Set secure cookie flags
- [ ] Configure CORS if needed
- [ ] Update dependencies regularly
- [ ] Set up database backups
- [ ] Configure firewall rules
- [ ] Enable database SSL
- [ ] Set up log monitoring
- [ ] Configure rate limiting

## Backup Strategy

### Database Backups

```bash
#!/bin/bash
# backup_db.sh
BACKUP_DIR="/backups/site_analysis"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_NAME="site_analysis"

mkdir -p $BACKUP_DIR

# Create backup
pg_dump -h localhost -U siteanalysis -d $DB_NAME | gzip > "$BACKUP_DIR/backup_$TIMESTAMP.sql.gz"

# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: backup_$TIMESTAMP.sql.gz"
```

### Automated Backups

Add to crontab:
```bash
# Daily backup at 2 AM
0 2 * * * /path/to/backup_db.sh
```

## Troubleshooting

### Common Issues

1. **PostGIS Extension Error**
   ```bash
   sudo -u postgres psql -d site_analysis -c "CREATE EXTENSION IF NOT EXISTS postgis;"
   ```

2. **GDAL/GEOS Issues**
   ```bash
   # Find GDAL library
   gdal-config --libs
   
   # Set in environment
   export GDAL_LIBRARY_PATH=/usr/lib/libgdal.so
   export GEOS_LIBRARY_PATH=/usr/lib/libgeos_c.so
   ```

3. **Memory Issues with Large Datasets**
   ```python
   # Use iterator for large querysets
   for obj in Model.objects.iterator():
       process(obj)
   ```

### Performance Monitoring

```bash
# Monitor database connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

# Monitor spatial queries
sudo -u postgres psql -d site_analysis -c "SELECT query, calls, total_time FROM pg_stat_statements WHERE query LIKE '%geometry%' ORDER BY total_time DESC LIMIT 10;"
```

## Scaling Considerations

### Horizontal Scaling

1. **Load Balancer Setup**
2. **Database Read Replicas**
3. **Celery for Background Tasks**
4. **Redis for Session Storage**

### Vertical Scaling

1. **Database Tuning**
2. **Connection Pooling**
3. **Query Optimization**
4. **Caching Strategy**

For more detailed deployment instructions for specific platforms, refer to their respective documentation.
