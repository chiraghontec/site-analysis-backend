#!/usr/bin/env python
"""
Quick test script to verify Django backend setup without database connectivity.
Run this to check if all imports and basic structure work correctly.
"""

import os
import sys
import django
from django.conf import settings

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_analysis_backend.settings')

# Test imports and basic setup
def test_backend_setup():
    print("🧪 Testing Django Backend Setup...\n")
    
    try:
        # Test Django configuration
        django.setup()
        print("✅ Django setup successful")
        
        # Test model imports
        from environmental_analysis.models import SiteAnalysis, EnvironmentalFeature, ClimateData
        print("✅ Models imported successfully")
        
        # Test service imports
        from environmental_analysis.services import EnvironmentalAnalysisService
        print("✅ Services imported successfully")
        
        # Test API imports
        from environmental_analysis.api import router
        print("✅ API router imported successfully")
        
        # Test admin imports
        from environmental_analysis import admin
        print("✅ Admin configuration imported successfully")
        
        # Test OSMnx import
        import osmnx as ox
        print("✅ OSMnx imported successfully")
        
        # Test GeoPandas import
        import geopandas as gpd
        print("✅ GeoPandas imported successfully")
        
        # Test spatial libraries
        from django.contrib.gis.geos import Point
        point = Point(-122.4194, 37.7749)  # San Francisco coordinates
        print(f"✅ Spatial operations working: {point}")
        
        print("\n🎉 All backend components are properly configured!")
        print("\n📌 Next steps:")
        print("1. Set up PostgreSQL with PostGIS")
        print("2. Update database password in settings.py")
        print("3. Run: python manage.py migrate")
        print("4. Run: python manage.py runserver")
        print("5. Visit: http://localhost:8000/api/docs")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_backend_setup()
