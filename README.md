# Environmental Site Analysis Backend

A comprehensive Django backend for environmental site analysis with geospatial feature extraction and climate data integration. This system combines OpenStreetMap data via OSMnx with climate data from multiple APIs to provide complete environmental assessments for any global location.

## 🌍 Features

- **Geospatial Analysis**: Extract environmental features (buildings, roads, parks, water bodies) using OSMnx
- **Climate Data Integration**: Real-time weather and historical climate patterns from NASA POWER and OpenWeatherMap
- **PostgreSQL + PostGIS**: Spatial database for storing geospatial and climate data
- **RESTful API**: Django Ninja-powered API with automatic documentation
- **Global Coverage**: Works for any coordinates worldwide
- **Scalable Architecture**: Service layer separation with comprehensive error handling

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.12+**
- **Homebrew** (for macOS dependencies)
- **Git**

## 🚀 Quick Start

### 1. Clone and Setup Project

```bash
# Clone the repository (or create the project structure)
cd "/Volumes/LocalDrive/Site Analysis"

# Navigate to the backend directory
cd site_analysis_backend

# Create and activate Python virtual environment
python3 -m venv site_env
source site_env/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 2. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt
```

The `requirements.txt` includes:
- Django 5.2.3 with GeoDjango
- Django Ninja for API development
- OSMnx for geospatial analysis
- GeoPandas, Shapely for spatial processing
- psycopg2-binary for PostgreSQL
- Climate data packages (python-dotenv, aiohttp)

### 3. Install System Dependencies (macOS)

```bash
# Install PostgreSQL with PostGIS extension
brew install postgresql@14 postgis

# Install GDAL and spatial libraries
brew install gdal geos spatialite-tools

# Start PostgreSQL service
brew services start postgresql@14
```

### 4. Database Setup

```bash
# Create database
/opt/homebrew/opt/postgresql@14/bin/createdb site_analysis_db

# Enable PostGIS extensions
/opt/homebrew/opt/postgresql@14/bin/psql site_analysis_db -c "CREATE EXTENSION postgis;"
/opt/homebrew/opt/postgresql@14/bin/psql site_analysis_db -c "CREATE EXTENSION postgis_topology;"
```

### 5. Django Configuration

```bash
# Run database migrations
python manage.py migrate

# Create Django superuser
python manage.py createsuperuser --username admin --email admin@example.com
# When prompted for password, enter your desired password
```

### 6. Environment Configuration (Optional)

```bash
# Copy environment template
cp .env.example .env

# Edit .env file to add API keys (optional)
# For enhanced climate data, add your OpenWeatherMap API key:
# OPENWEATHER_API_KEY=your_api_key_here
```

**Getting API Keys:**
- **OpenWeatherMap**: Free API key at [https://openweathermap.org/api](https://openweathermap.org/api)
- **NASA POWER**: No API key required (free access)

### 7. Start the Server

```bash
# Start Django development server
python manage.py runserver 8001
```

The server will start at `http://127.0.0.1:8001/`

## 📖 API Usage

### Interactive Documentation
Visit `http://127.0.0.1:8001/api/docs` for interactive API documentation.

### Admin Interface
Visit `http://127.0.0.1:8001/admin/` and login with your superuser credentials.

### Core API Endpoints

#### 1. Create Site Analysis
```bash
curl -X POST "http://127.0.0.1:8001/api/environmental/analyze" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Test Site",
       "latitude": 37.7749,
       "longitude": -122.4194,
       "analysis_radius": 800
     }'
```

#### 2. Get Environmental Features
```bash
curl "http://127.0.0.1:8001/api/environmental/analysis/{analysis_id}/features"
```

#### 3. Get Climate Data
```bash
curl "http://127.0.0.1:8001/api/environmental/analysis/{analysis_id}/climate"
```

#### 4. Get Climate Summary (No Analysis Required)
```bash
curl "http://127.0.0.1:8001/api/environmental/climate/summary?latitude=37.7749&longitude=-122.4194"
```

### Complete API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/environmental/analyze` | POST | Create site analysis with environmental and climate data |
| `/api/environmental/analysis/{id}` | GET | Get analysis details and summary |
| `/api/environmental/analysis/{id}/features` | GET | Export environmental features as GeoJSON |
| `/api/environmental/analysis/{id}/climate` | GET | Get comprehensive climate data |
| `/api/environmental/analysis/{id}/climate/refresh` | POST | Refresh climate data from APIs |
| `/api/environmental/climate/summary` | GET | Get climate summary for coordinates |
| `/api/environmental/features/types` | GET | Get available feature types |

## 🧪 Testing

### Run API Tests

```bash
# Test basic functionality
python test_api.py

# Test climate data functionality
python test_climate_api.py
```

### Manual Testing

```bash
# Quick test with Python
python -c "
import requests
response = requests.post('http://127.0.0.1:8001/api/environmental/analyze', json={
    'name': 'Test Site',
    'latitude': 37.7749,
    'longitude': -122.4194,
    'analysis_radius': 500
})
print(f'Status: {response.status_code}')
print(f'Features found: {response.json().get(\"features_count\", 0)}')
"
```

## 🗄️ Database Models

### SiteAnalysis
- **location**: Point geometry (WGS84)
- **analysis_radius**: Search radius in meters
- **name**: Site identifier
- **timestamps**: Created/updated times

### EnvironmentalFeature
- **geometry**: Any geometry type (Point, LineString, Polygon)
- **feature_type**: Category (natural, leisure, highway, landuse, amenity)
- **osm_id**: OpenStreetMap feature ID
- **properties**: JSON field with OSM tags

### ClimateData
- **temperature_data**: Current conditions and historical patterns
- **precipitation_data**: Weather and seasonal patterns
- **wind_data**: Speed, direction, seasonal variations
- **solar_data**: Radiation and availability patterns

## 🔧 Troubleshooting

### Common Issues

#### 1. GDAL Library Not Found
```bash
# Ensure GDAL is installed and path is correct in settings.py
brew install gdal

# Check GDAL installation
find /opt/homebrew -name "*gdal*" -type f | grep -E "\.(dylib|so)$"
```

#### 2. PostgreSQL Connection Error
```bash
# Check PostgreSQL is running
brew services list | grep postgresql

# Start PostgreSQL if not running
brew services start postgresql@14

# Verify database exists
/opt/homebrew/opt/postgresql@14/bin/psql -l | grep site_analysis_db
```

#### 3. OSMnx Network Error
```bash
# OSMnx requires internet connection for OpenStreetMap data
# Check internet connectivity and try again
# OSMnx includes automatic retry mechanisms
```

#### 4. Climate API Issues
```bash
# Climate data works with mock fallback if APIs are unavailable
# Check API keys in .env file for enhanced data
# NASA POWER API is free and doesn't require keys
```

### Performance Optimization

#### 1. Large Radius Analysis
```python
# For analysis radius > 1000m, consider chunking requests
# OSMnx automatically handles large datasets but may take longer
```

#### 2. Database Performance
```bash
# Create indexes for frequent queries
python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute('CREATE INDEX IF NOT EXISTS idx_feature_type ON environmental_analysis_environmentalfeature(feature_type);')
"
```

## 🌍 Global Usage Examples

### Different Climate Zones

```bash
# Tropical (Singapore)
curl "http://127.0.0.1:8001/api/environmental/climate/summary?latitude=1.3521&longitude=103.8198"

# Temperate (London)
curl "http://127.0.0.1:8001/api/environmental/climate/summary?latitude=51.5074&longitude=-0.1278"

# Arctic (Reykjavik)
curl "http://127.0.0.1:8001/api/environmental/climate/summary?latitude=64.1466&longitude=-21.9426"
```

### Urban vs Rural Analysis

```bash
# Dense urban area (Manhattan, NYC)
curl -X POST "http://127.0.0.1:8001/api/environmental/analyze" \
     -H "Content-Type: application/json" \
     -d '{"name": "Manhattan", "latitude": 40.7589, "longitude": -73.9851, "analysis_radius": 500}'

# Rural area (Yellowstone)
curl -X POST "http://127.0.0.1:8001/api/environmental/analyze" \
     -H "Content-Type: application/json" \
     -d '{"name": "Yellowstone", "latitude": 44.4280, "longitude": -110.5885, "analysis_radius": 1000}'
```

## 🚀 Production Deployment

### Environment Variables
```bash
# Production .env file
DEBUG=False
SECRET_KEY=your_secure_secret_key
DATABASE_URL=postgresql://user:password@host:port/dbname
OPENWEATHER_API_KEY=your_production_api_key
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

### WSGI Configuration
```python
# Use production WSGI server like Gunicorn
pip install gunicorn
gunicorn site_analysis_backend.wsgi:application --bind 0.0.0.0:8000
```

### Database Optimization
```sql
-- Production PostgreSQL optimizations
-- Increase shared_buffers, effective_cache_size
-- Enable PostGIS optimizations
-- Create spatial indexes
```

## 📁 Project Structure

```
site_analysis_backend/
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── test_api.py                  # API test script
├── test_climate_api.py          # Climate API test script
├── PROJECT_STATUS.md            # Project status and results
├── SETUP_POSTGRESQL.md          # Detailed PostgreSQL setup
├── site_env/                    # Python virtual environment
├── site_analysis_backend/       # Main Django project
│   ├── settings.py              # Django configuration
│   ├── urls.py                  # URL routing
│   └── wsgi.py                  # WSGI application
└── environmental_analysis/      # Django app
    ├── models.py                # Database models
    ├── api.py                   # API endpoints
    ├── services.py              # Business logic
    ├── admin.py                 # Admin interface
    └── migrations/              # Database migrations
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the Django and PostGIS documentation
3. Check OSMnx documentation for geospatial issues
4. Verify API endpoints with interactive docs at `/api/docs`

## 🎯 Next Steps

After successful setup, you can:
1. Integrate with frontend applications (React, Vue, etc.)
2. Export data to GIS applications (QGIS, ArcGIS)
3. Build mobile applications using the REST API
4. Scale for production with proper caching and load balancing
5. Add additional climate data sources or analysis features

---

**Successfully tested with:**
- ✅ macOS Sequoia (Apple Silicon)
- ✅ Python 3.12
- ✅ PostgreSQL 14 + PostGIS 3.5
- ✅ Global coordinates (tested across 5 continents)
- ✅ Large datasets (4000+ features per analysis)
- ✅ Multiple climate zones and weather conditions
