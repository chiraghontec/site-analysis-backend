#!/usr/bin/env python
"""
Climate Data API Test Script
Tests the enhanced site analysis API with climate data functionality.
"""

import requests
import json
import time

# API Base URL
BASE_URL = "http://127.0.0.1:8001/api"

def test_climate_data_api():
    print("🌤️ Testing Climate Data API Endpoints\n")
    
    # Test data - San Francisco coordinates (different location from previous tests)
    test_site_data = {
        "name": "Climate Test Site - Downtown SF",
        "latitude": 37.7849,
        "longitude": -122.4094,
        "analysis_radius": 500
    }
    
    print("📍 Testing site analysis with climate data...")
    print(f"Location: {test_site_data['name']}")
    print(f"Coordinates: ({test_site_data['latitude']}, {test_site_data['longitude']})")
    print(f"Radius: {test_site_data['analysis_radius']} meters\n")
    
    try:
        # 1. Create Site Analysis (should now include climate data)
        print("1️⃣ Creating site analysis with climate data...")
        response = requests.post(f"{BASE_URL}/environmental/analyze", json=test_site_data)
        
        if response.status_code == 200:
            result = response.json()
            site_id = result['id']
            print(f"✅ Site analysis created successfully!")
            print(f"   Site ID: {site_id}")
            print(f"   Features found: {result['features_count']}")
            
            # 2. Test Climate Data Endpoint
            print("\n2️⃣ Fetching climate data...")
            climate_response = requests.get(f"{BASE_URL}/environmental/analysis/{site_id}/climate")
            
            if climate_response.status_code == 200:
                climate_data = climate_response.json()
                print(f"✅ Climate data retrieved successfully!")
                print(f"   Climate zone: {climate_data.get('climate_zone', 'Unknown')}")
                
                # Show temperature data
                temp_data = climate_data.get('temperature_data', {})
                current_temp = temp_data.get('current', {})
                if current_temp:
                    print(f"   Current temperature: {current_temp.get('current', 'N/A')}°C")
                    print(f"   Humidity: {current_temp.get('humidity', 'N/A')}%")
                
                # Show precipitation data
                precip_data = climate_data.get('precipitation_data', {})
                current_precip = precip_data.get('current', {})
                if current_precip:
                    print(f"   Weather: {current_precip.get('description', 'N/A')}")
                    print(f"   Cloud cover: {current_precip.get('clouds', 'N/A')}%")
                
                # Show wind data
                wind_data = climate_data.get('wind_data', {})
                current_wind = wind_data.get('current', {})
                if current_wind:
                    print(f"   Wind speed: {current_wind.get('speed', 'N/A')} m/s")
                    print(f"   Wind direction: {current_wind.get('direction', 'N/A')}°")
                    
            else:
                print(f"❌ Failed to retrieve climate data: {climate_response.status_code}")
                print(f"   Response: {climate_response.text[:200]}...")
            
            # 3. Test Climate Summary Endpoint (no analysis required)
            print("\n3️⃣ Testing standalone climate summary...")
            summary_response = requests.get(f"{BASE_URL}/environmental/climate/summary", params={
                'latitude': test_site_data['latitude'],
                'longitude': test_site_data['longitude']
            })
            
            if summary_response.status_code == 200:
                summary_data = summary_response.json()
                print(f"✅ Climate summary retrieved successfully!")
                print(f"   Climate zone: {summary_data.get('climate_zone', 'Unknown')}")
                
                current_weather = summary_data.get('current_weather', {})
                if current_weather:
                    temp = current_weather.get('temperature', {})
                    print(f"   Current conditions: {temp.get('current', 'N/A')}°C")
                    
                climate_patterns = summary_data.get('climate_patterns', {})
                if climate_patterns:
                    temp_patterns = climate_patterns.get('temperature', {})
                    print(f"   Seasonal variation: {temp_patterns.get('seasonal_variation', 'N/A')}")
                    precip_patterns = climate_patterns.get('precipitation', {})
                    print(f"   Precipitation pattern: {precip_patterns.get('pattern', 'N/A')}")
                    
            else:
                print(f"❌ Failed to retrieve climate summary: {summary_response.status_code}")
                print(f"   Response: {summary_response.text[:200]}...")
            
            # 4. Test Climate Data Refresh
            print("\n4️⃣ Testing climate data refresh...")
            refresh_response = requests.post(f"{BASE_URL}/environmental/analysis/{site_id}/climate/refresh")
            
            if refresh_response.status_code == 200:
                refresh_data = refresh_response.json()
                print(f"✅ Climate data refreshed successfully!")
                print(f"   Updated at: {refresh_data.get('updated_at', 'N/A')}")
                print(f"   Climate zone: {refresh_data.get('climate_zone', 'N/A')}")
                    
            else:
                print(f"❌ Failed to refresh climate data: {refresh_response.status_code}")
                print(f"   Response: {refresh_response.text[:200]}...")
                
        else:
            print(f"❌ Failed to create site analysis: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Django server is running on port 8001")
        print("   Run: python manage.py runserver 8001")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_multiple_locations():
    """Test climate data for different global locations"""
    print("\n🌍 Testing climate data for multiple locations...")
    
    locations = [
        {"name": "London, UK", "lat": 51.5074, "lon": -0.1278},
        {"name": "Tokyo, Japan", "lat": 35.6762, "lon": 139.6503},
        {"name": "Sydney, Australia", "lat": -33.8688, "lon": 151.2093},
        {"name": "São Paulo, Brazil", "lat": -23.5505, "lon": -46.6333},
    ]
    
    for location in locations:
        print(f"\n📍 {location['name']}:")
        try:
            response = requests.get(f"{BASE_URL}/environmental/climate/summary", params={
                'latitude': location['lat'],
                'longitude': location['lon']
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Climate zone: {data.get('climate_zone', 'Unknown')}")
                
                current = data.get('current_weather', {}).get('temperature', {})
                if current:
                    print(f"   Current temp: {current.get('current', 'N/A')}°C")
                    
                patterns = data.get('climate_patterns', {})
                if patterns:
                    temp_var = patterns.get('temperature', {}).get('seasonal_variation', 'N/A')
                    precip_pattern = patterns.get('precipitation', {}).get('pattern', 'N/A')
                    print(f"   Seasonal variation: {temp_var}")
                    print(f"   Precipitation: {precip_pattern}")
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_server_health():
    """Test if the server is responding"""
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ Server is running and responding")
            return True
    except:
        pass
    
    print("❌ Server is not responding")
    return False

if __name__ == "__main__":
    print("🌤️ Climate Data API Test Suite\n")
    
    if test_server_health():
        print()
        test_climate_data_api()
        test_multiple_locations()
    else:
        print("\n💡 Make sure to start the Django server:")
        print("   cd site_analysis_backend")
        print("   source site_env/bin/activate")
        print("   python manage.py runserver 8001")
        
    print("\n🔗 Enhanced API URLs:")
    print("   API Documentation: http://127.0.0.1:8001/api/docs")
    print("   Django Admin: http://127.0.0.1:8001/admin/")
    print("\n🌤️ New Climate Endpoints:")
    print("   GET /api/environmental/analysis/{id}/climate")
    print("   POST /api/environmental/analysis/{id}/climate/refresh")
    print("   GET /api/environmental/climate/summary?latitude=LAT&longitude=LON")
