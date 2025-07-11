# PostgreSQL + PostGIS Setup Guide

## Prerequisites

1. **Install PostgreSQL and PostGIS** (if not already installed):

### macOS (using Homebrew):
```bash
brew install postgresql postgis
```

### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib postgis postgresql-15-postgis-3
```

## Database Setup

1. **Start PostgreSQL service**:
```bash
# macOS
brew services start postgresql

# Ubuntu/Linux
sudo systemctl start postgresql
```

2. **Create database and user**:
```bash
# Connect to PostgreSQL as superuser
psql -U postgres

# Create database
CREATE DATABASE site_analysis_db;

# Create user (replace 'your_password' with a secure password)
CREATE USER site_analysis_user WITH PASSWORD 'your_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE site_analysis_db TO site_analysis_user;

# Connect to the new database
\c site_analysis_db

# Enable PostGIS extension
CREATE EXTENSION postgis;

# Verify PostGIS installation
SELECT PostGIS_Version();

# Exit psql
\q
```

## Django Configuration

1. **Update settings.py** with your database credentials:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'site_analysis_db',
        'USER': 'site_analysis_user',  # or your username
        'PASSWORD': 'your_password',   # replace with your actual password
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

2. **Run migrations**:
```bash
python manage.py makemigrations
python manage.py migrate
```

3. **Create superuser**:
```bash
python manage.py createsuperuser
```

## Test the Setup

1. **Run the development server**:
```bash
python manage.py runserver
```

2. **Test the API endpoints**:
- Visit: http://127.0.0.1:8000/api/docs (Django Ninja auto-generated docs)
- Test endpoint: http://127.0.0.1:8000/api/hello
- Environmental API: http://127.0.0.1:8000/api/environmental/test

3. **Access Django Admin**:
- Visit: http://127.0.0.1:8000/admin
- Login with your superuser credentials
- You should see the Environmental Analysis models with map widgets

## Troubleshooting

### Common Issues:

1. **"Could not connect to server"**:
   - Make sure PostgreSQL is running
   - Check if the service is started: `brew services list | grep postgresql`

2. **"database does not exist"**:
   - Create the database as shown in step 2 above

3. **"PostGIS extension not found"**:
   - Make sure PostGIS is installed: `brew install postgis`
   - Enable the extension in your database: `CREATE EXTENSION postgis;`

4. **Permission denied**:
   - Make sure your user has the correct privileges
   - Try connecting as the postgres superuser first

### Verify PostGIS Installation:
```sql
-- Connect to your database
psql -U site_analysis_user -d site_analysis_db

-- Check PostGIS version
SELECT PostGIS_Version();

-- List available spatial reference systems
SELECT COUNT(*) FROM spatial_ref_sys;
```

## Next Steps

1. **Integrate OSMnx**: Update the API to use actual OSMnx queries
2. **Add EPW parsing**: Implement climate data parsing functionality
3. **Create visualization**: Add map rendering and export features
4. **Add authentication**: Implement user authentication for the API
