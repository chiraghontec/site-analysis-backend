#!/usr/bin/env python
"""
API Test Script for Site Analysis Backend
Tests the environmental analysis API endpoints.
"""

import requests
import json
import time

# API Base URL
BASE_URL = "http://127.0.0.1:8001/api"

def test_api_endpoints():
    print("🧪 Testing Site Analysis API Endpoints\n")
    
    # Test data - San Francisco coordinates
    test_site_data = {
        "name": "Golden Gate Park Test Site",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "analysis_radius": 800
    }
    
    print("📍 Testing site analysis creation...")
    print(f"Location: {test_site_data['name']}")
    print(f"Coordinates: ({test_site_data['latitude']}, {test_site_data['longitude']})")
    print(f"Radius: {test_site_data['analysis_radius']} meters\n")
    
    try:
        # 1. Create Site Analysis
        print("1️⃣ Creating site analysis...")
        response = requests.post(f"{BASE_URL}/environmental/analyze", json=test_site_data)
        
        if response.status_code == 200:
            result = response.json()
            site_id = result['id']  # The API returns 'id' not 'site_id'
            print(f"✅ Site analysis created successfully!")
            print(f"   Site ID: {site_id}")
            print(f"   Features found: {result['features_count']}")
            print(f"   Analysis completed at: {result['created_at']}")
            
            # Show immediate summary from creation response
            summary = result.get('summary', {})
            if summary:
                print(f"   Total features: {summary.get('total_features', 0)}")
                print("   Feature breakdown:")
                for f_type, count in summary.get('feature_counts', {}).items():
                    print(f"     - {f_type}: {count}")
            
            # 2. Get Features
            print("\n2️⃣ Fetching extracted features...")
            features_response = requests.get(f"{BASE_URL}/environmental/analysis/{site_id}/features")
            
            if features_response.status_code == 200:
                features = features_response.json()
                print(f"✅ Features retrieved successfully!")
                print(f"   GeoJSON feature count: {len(features.get('features', []))}")
                
                # Show first few features as examples
                sample_features = features.get('features', [])[:3]
                if sample_features:
                    print("   Sample features:")
                    for i, feature in enumerate(sample_features, 1):
                        props = feature.get('properties', {})
                        geom_type = feature.get('geometry', {}).get('type', 'Unknown')
                        print(f"     {i}. {props.get('feature_type', 'Unknown')} ({geom_type})")
                    
            else:
                print(f"❌ Failed to retrieve features: {features_response.status_code}")
                print(f"   Response: {features_response.text[:200]}...")
            
            # 3. Get Analysis Summary
            print("\n3️⃣ Getting analysis details...")
            summary_response = requests.get(f"{BASE_URL}/environmental/analysis/{site_id}")
            
            if summary_response.status_code == 200:
                details = summary_response.json()
                print(f"✅ Analysis details retrieved successfully!")
                print(f"   Site: {details.get('name', 'Unknown')}")
                print(f"   Analysis radius: {details.get('radius', 'Unknown')}m")
                print(f"   Total features: {details.get('features_count', 0)}")
                print(f"   Created: {details.get('created_at', 'Unknown')}")
                    
            else:
                print(f"❌ Failed to retrieve analysis details: {summary_response.status_code}")
                print(f"   Response: {summary_response.text[:200]}...")
                
        else:
            print(f"❌ Failed to create site analysis: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Django server is running on port 8001")
        print("   Run: python manage.py runserver 8001")
    except Exception as e:
        print(f"❌ Error: {e}")

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
    print("🌍 Site Analysis Backend API Test\n")
    
    if test_server_health():
        print()
        test_api_endpoints()
    else:
        print("\n💡 Make sure to start the Django server:")
        print("   cd site_analysis_backend")
        print("   source site_env/bin/activate")
        print("   python manage.py runserver 8001")
        
    print("\n🔗 Useful URLs:")
    print("   API Documentation: http://127.0.0.1:8001/api/docs")
    print("   Django Admin: http://127.0.0.1:8001/admin/")
    print("   (Login: admin / [password you set])")
