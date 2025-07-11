"""
Environmental Analysis Services

This module contains the business logic for extracting and processing
environmental data from OpenStreetMap using OSMnx and climate data from various APIs.
"""
import osmnx as ox
import geopandas as gpd
from django.contrib.gis.geos import Point, GEOSGeometry
from django.contrib.gis.geos import fromstr
from typing import Dict, List, Tuple, Any, Optional
import json
import logging
import requests
import asyncio
import aiohttp
from datetime import datetime, timedelta
from django.conf import settings
import os

from .models import SiteAnalysis, EnvironmentalFeature, ClimateData

logger = logging.getLogger(__name__)

class EnvironmentalAnalysisService:
    """Service class for performing environmental analysis using OSMnx"""
    
    # OSM tag filters based on the requirements
    OSM_FILTERS = {
        'landuse': ['forest', 'grass', 'cemetery'],
        'natural': ['water', 'tree', 'scrub'],
        'leisure': ['park', 'playground'],
    }
    
    def __init__(self):
        # Configure OSMnx settings for better performance
        ox.settings.log_console = False
        ox.settings.use_cache = True
    
    def analyze_site(self, latitude: float, longitude: float, 
                    radius: int = 500, site_name: str = None) -> SiteAnalysis:
        """
        Perform complete environmental analysis for a site
        
        Args:
            latitude: Site latitude
            longitude: Site longitude
            radius: Analysis radius in meters
            site_name: Optional name for the site
            
        Returns:
            SiteAnalysis object with all extracted features and climate data
        """
        # Create or get site analysis record
        location = Point(longitude, latitude, srid=4326)
        site_analysis = SiteAnalysis.objects.create(
            name=site_name or f"Site at {latitude:.4f}, {longitude:.4f}",
            location=location,
            analysis_radius=radius
        )
        
        try:
            # Extract features from OSM
            features_data = self.extract_osm_features(latitude, longitude, radius)
            
            # Save features to database
            self.save_features_to_db(site_analysis, features_data)
            
            # Initialize climate data service and fetch climate data
            climate_service = ClimateDataService()
            climate_data = climate_service.get_climate_data(latitude, longitude, site_analysis)
            
            logger.info(f"Successfully analyzed site {site_analysis.id} with {len(features_data)} features and climate data")
            
        except Exception as e:
            logger.error(f"Error analyzing site: {str(e)}")
            raise
        
        return site_analysis
    
    def extract_osm_features(self, latitude: float, longitude: float, 
                           radius: int) -> List[Dict[str, Any]]:
        """
        Extract environmental features from OpenStreetMap
        
        Args:
            latitude: Center point latitude
            longitude: Center point longitude
            radius: Search radius in meters
            
        Returns:
            List of feature dictionaries
        """
        point = (latitude, longitude)
        all_features = []
        
        # Define comprehensive tag filters
        tag_filters = {
            'landuse': True,
            'natural': True,
            'leisure': True,
            'amenity': ['park', 'playground', 'garden'],
            'highway': ['footway', 'path', 'cycleway'],
        }
        
        try:
            logger.info(f"Extracting features from OSM for point {point} with radius {radius}m")
            
            # Query OSM data
            gdf = ox.features_from_point(point, tags=tag_filters, dist=radius)
            
            if gdf.empty:
                logger.warning("No features found in the specified area")
                return []
            
            # Process each feature
            for idx, row in gdf.iterrows():
                try:
                    feature_data = self.process_osm_feature(row, idx)
                    if feature_data:
                        all_features.append(feature_data)
                except Exception as e:
                    logger.warning(f"Error processing feature {idx}: {str(e)}")
                    continue
                    
            logger.info(f"Successfully extracted {len(all_features)} features")
            
        except Exception as e:
            logger.error(f"Error extracting OSM features: {str(e)}")
            raise
        
        return all_features
    
    def process_osm_feature(self, row: gpd.GeoSeries, osm_id: Any) -> Dict[str, Any]:
        """
        Process a single OSM feature from GeoDataFrame row
        
        Args:
            row: GeoDataFrame row containing feature data
            osm_id: OSM feature ID
            
        Returns:
            Processed feature dictionary or None if feature should be skipped
        """
        try:
            # Extract geometry
            geometry = row['geometry']
            if geometry is None or geometry.is_empty:
                return None
            
            # Convert geometry to WKT for Django
            geometry_wkt = geometry.wkt
            
            # Determine feature type
            feature_type = self.determine_feature_type(row)
            if not feature_type:
                return None
            
            # Extract properties (OSM tags)
            properties = {}
            for col in row.index:
                if col != 'geometry' and pd.notna(row[col]):
                    # Convert numpy types to Python types for JSON serialization
                    value = row[col]
                    if hasattr(value, 'item'):  # numpy scalar
                        value = value.item()
                    properties[col] = value
            
            return {
                'osm_id': int(osm_id) if isinstance(osm_id, (int, float)) else hash(str(osm_id)),
                'feature_type': feature_type,
                'geometry_wkt': geometry_wkt,
                'properties': properties,
            }
            
        except Exception as e:
            logger.warning(f"Error processing feature {osm_id}: {str(e)}")
            return None
    
    def determine_feature_type(self, row: gpd.GeoSeries) -> str:
        """
        Determine the primary feature type based on OSM tags
        
        Args:
            row: GeoDataFrame row containing feature data
            
        Returns:
            Feature type string or None
        """
        # Priority order for feature type determination
        type_priorities = ['landuse', 'natural', 'leisure', 'amenity', 'highway']
        
        for feature_type in type_priorities:
            if feature_type in row.index and pd.notna(row[feature_type]):
                return feature_type
        
        return 'other'
    
    def save_features_to_db(self, site_analysis: SiteAnalysis, 
                           features_data: List[Dict[str, Any]]) -> None:
        """
        Save extracted features to the database
        
        Args:
            site_analysis: SiteAnalysis instance
            features_data: List of feature dictionaries
        """
        features_to_create = []
        
        for feature_data in features_data:
            try:
                # Convert WKT to Django geometry
                geometry = GEOSGeometry(feature_data['geometry_wkt'])
                
                feature = EnvironmentalFeature(
                    site_analysis=site_analysis,
                    feature_type=feature_data['feature_type'],
                    osm_id=feature_data['osm_id'],
                    geometry=geometry,
                    properties=feature_data['properties']
                )
                features_to_create.append(feature)
                
            except Exception as e:
                logger.warning(f"Error creating feature {feature_data['osm_id']}: {str(e)}")
                continue
        
        # Bulk create features
        if features_to_create:
            EnvironmentalFeature.objects.bulk_create(
                features_to_create, 
                ignore_conflicts=True  # Skip duplicates
            )
            logger.info(f"Saved {len(features_to_create)} features to database")
    
    def get_analysis_summary(self, site_analysis: SiteAnalysis) -> Dict[str, Any]:
        """
        Generate summary statistics for a site analysis
        
        Args:
            site_analysis: SiteAnalysis instance
            
        Returns:
            Summary dictionary
        """
        features = site_analysis.features.all()
        
        # Count features by type
        feature_counts = {}
        for feature in features:
            feature_type = feature.feature_type
            feature_counts[feature_type] = feature_counts.get(feature_type, 0) + 1
        
        # Calculate total area for polygon features
        total_area = 0
        for feature in features:
            if hasattr(feature.geometry, 'area'):
                # Convert to approximate square meters (rough calculation)
                total_area += feature.geometry.area * 111000 * 111000
        
        return {
            'total_features': len(features),
            'feature_counts': feature_counts,
            'approximate_total_area_sqm': round(total_area, 2),
            'analysis_radius': site_analysis.analysis_radius,
            'center_coordinates': {
                'latitude': site_analysis.location.y,
                'longitude': site_analysis.location.x,
            }
        }

class ClimateDataService:
    """Service class for fetching climate data from various APIs"""
    
    def __init__(self):
        # API endpoints
        self.openweather_base = "https://api.openweathermap.org/data/2.5"
        self.nasa_power_base = "https://power.larc.nasa.gov/api/temporal/daily/point"
        self.world_bank_base = "https://climateknowledgeportal.worldbank.org/api"
        
        # Get API keys from environment or settings
        self.openweather_key = getattr(settings, 'OPENWEATHER_API_KEY', os.getenv('OPENWEATHER_API_KEY'))
    
    def get_climate_data(self, latitude: float, longitude: float, site_analysis: SiteAnalysis) -> ClimateData:
        """
        Fetch comprehensive climate data for a location
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            site_analysis: Associated site analysis object
            
        Returns:
            ClimateData object with aggregated climate information
        """
        climate_data, created = ClimateData.objects.get_or_create(
            site_analysis=site_analysis,
            defaults={
                'temperature_data': {},
                'precipitation_data': {},
                'wind_data': {},
                'solar_data': {}
            }
        )
        
        try:
            # Fetch from multiple sources
            current_weather = self._get_current_weather(latitude, longitude)
            nasa_data = self._get_nasa_power_data(latitude, longitude)
            climate_summary = self._get_climate_summary(latitude, longitude)
            
            # Aggregate all data
            climate_data.temperature_data = {
                'current': current_weather.get('temperature', {}),
                'historical_avg': nasa_data.get('temperature', {}),
                'monthly_averages': climate_summary.get('temperature', {})
            }
            
            climate_data.precipitation_data = {
                'current': current_weather.get('precipitation', {}),
                'historical': nasa_data.get('precipitation', {}),
                'annual_patterns': climate_summary.get('precipitation', {})
            }
            
            climate_data.wind_data = {
                'current': current_weather.get('wind', {}),
                'patterns': nasa_data.get('wind', {}),
                'seasonal': climate_summary.get('wind', {})
            }
            
            climate_data.solar_data = {
                'current': current_weather.get('solar', {}),
                'radiation': nasa_data.get('solar', {}),
                'yearly_patterns': climate_summary.get('solar', {})
            }
            
            climate_data.save()
            logger.info(f"Climate data updated for site: {site_analysis.name}")
            
        except Exception as e:
            logger.error(f"Error fetching climate data: {e}")
            
        return climate_data
    
    def _get_current_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get current weather data from OpenWeatherMap"""
        if not self.openweather_key:
            logger.warning("OpenWeatherMap API key not configured")
            return self._get_mock_current_weather(lat, lon)
        
        try:
            # Current weather
            current_url = f"{self.openweather_base}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.openweather_key,
                'units': 'metric'
            }
            
            response = requests.get(current_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'temperature': {
                        'current': data['main']['temp'],
                        'feels_like': data['main']['feels_like'],
                        'min': data['main']['temp_min'],
                        'max': data['main']['temp_max'],
                        'humidity': data['main']['humidity'],
                        'pressure': data['main']['pressure']
                    },
                    'precipitation': {
                        'description': data['weather'][0]['description'],
                        'clouds': data['clouds']['all'],
                        'rain': data.get('rain', {}).get('1h', 0),
                        'snow': data.get('snow', {}).get('1h', 0)
                    },
                    'wind': {
                        'speed': data['wind']['speed'],
                        'direction': data['wind'].get('deg', 0),
                        'gust': data['wind'].get('gust', 0)
                    },
                    'solar': {
                        'visibility': data['visibility'],
                        'uv_index': None  # Requires separate API call
                    }
                }
            else:
                logger.warning(f"OpenWeatherMap API error: {response.status_code}")
                return self._get_mock_current_weather(lat, lon)
                
        except Exception as e:
            logger.error(f"Error fetching current weather: {e}")
            return self._get_mock_current_weather(lat, lon)
    
    def _get_nasa_power_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get NASA POWER meteorological data"""
        try:
            # Get last year's data for historical context
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            params = {
                'start': start_date.strftime('%Y%m%d'),
                'end': end_date.strftime('%Y%m%d'),
                'latitude': lat,
                'longitude': lon,
                'community': 'RE',
                'parameters': 'T2M,PRECTOT,WS2M,ALLSKY_SFC_SW_DWN',
                'format': 'JSON'
            }
            
            response = requests.get(self.nasa_power_base, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                properties = data['properties']['parameter']
                
                # Calculate averages
                temp_data = list(properties.get('T2M', {}).values())
                precip_data = list(properties.get('PRECTOT', {}).values())
                wind_data = list(properties.get('WS2M', {}).values())
                solar_data = list(properties.get('ALLSKY_SFC_SW_DWN', {}).values())
                
                return {
                    'temperature': {
                        'annual_avg': sum(temp_data) / len(temp_data) if temp_data else 0,
                        'annual_max': max(temp_data) if temp_data else 0,
                        'annual_min': min(temp_data) if temp_data else 0
                    },
                    'precipitation': {
                        'annual_total': sum(precip_data) if precip_data else 0,
                        'avg_daily': sum(precip_data) / len(precip_data) if precip_data else 0
                    },
                    'wind': {
                        'avg_speed': sum(wind_data) / len(wind_data) if wind_data else 0,
                        'max_speed': max(wind_data) if wind_data else 0
                    },
                    'solar': {
                        'avg_radiation': sum(solar_data) / len(solar_data) if solar_data else 0,
                        'peak_radiation': max(solar_data) if solar_data else 0
                    }
                }
            else:
                logger.warning(f"NASA POWER API error: {response.status_code}")
                return self._get_mock_nasa_data(lat, lon)
                
        except Exception as e:
            logger.error(f"Error fetching NASA POWER data: {e}")
            return self._get_mock_nasa_data(lat, lon)
    
    def _get_climate_summary(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get climate zone and summary information"""
        # This is a simplified climate classification based on coordinates
        # In production, you might use Köppen climate classification or other systems
        
        climate_zone = self._classify_climate_zone(lat, lon)
        
        return {
            'zone': climate_zone,
            'temperature': {
                'seasonal_variation': 'high' if abs(lat) > 40 else 'moderate',
                'frost_risk': 'high' if abs(lat) > 50 else 'low'
            },
            'precipitation': {
                'pattern': self._get_precipitation_pattern(lat, lon),
                'seasonality': 'distinct' if abs(lat) > 23.5 else 'minimal'
            },
            'wind': {
                'patterns': self._get_wind_patterns(lat, lon)
            },
            'solar': {
                'availability': 'high' if abs(lat) < 35 else 'moderate',
                'seasonal_variation': 'high' if abs(lat) > 40 else 'low'
            }
        }
    
    def _classify_climate_zone(self, lat: float, lon: float) -> str:
        """Simple climate zone classification"""
        abs_lat = abs(lat)
        
        if abs_lat > 66.5:
            return "polar"
        elif abs_lat > 50:
            return "subarctic"
        elif abs_lat > 40:
            return "temperate"
        elif abs_lat > 23.5:
            return "subtropical"
        else:
            return "tropical"
    
    def _get_precipitation_pattern(self, lat: float, lon: float) -> str:
        """Determine precipitation patterns"""
        if abs(lat) < 10:
            return "equatorial_wet"
        elif abs(lat) < 23.5:
            return "tropical_seasonal"
        elif abs(lat) < 40:
            return "mediterranean" if 30 < abs(lat) < 45 else "temperate"
        else:
            return "continental"
    
    def _get_wind_patterns(self, lat: float, lon: float) -> Dict[str, str]:
        """Determine wind patterns"""
        abs_lat = abs(lat)
        
        if abs_lat < 5:
            return {"dominant": "trade_winds", "seasonal": "monsoon"}
        elif abs_lat < 30:
            return {"dominant": "trade_winds", "seasonal": "variable"}
        elif abs_lat < 60:
            return {"dominant": "westerlies", "seasonal": "strong_variation"}
        else:
            return {"dominant": "polar_easterlies", "seasonal": "extreme_variation"}
    
    def _get_mock_current_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """Provide mock weather data when API is unavailable"""
        # Generate reasonable mock data based on location
        base_temp = 20 - (abs(lat) - 23.5) * 0.5  # Rough temperature estimation
        
        return {
            'temperature': {
                'current': base_temp + 5,
                'feels_like': base_temp + 3,
                'min': base_temp,
                'max': base_temp + 10,
                'humidity': 65,
                'pressure': 1013
            },
            'precipitation': {
                'description': 'partly cloudy',
                'clouds': 30,
                'rain': 0,
                'snow': 0
            },
            'wind': {
                'speed': 5.5,
                'direction': 225,
                'gust': 8.2
            },
            'solar': {
                'visibility': 10000,
                'uv_index': 6
            }
        }
    
    def _get_mock_nasa_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Provide mock NASA POWER data when API is unavailable"""
        base_temp = 20 - (abs(lat) - 23.5) * 0.5
        
        return {
            'temperature': {
                'annual_avg': base_temp,
                'annual_max': base_temp + 15,
                'annual_min': base_temp - 10
            },
            'precipitation': {
                'annual_total': 800 + (60 - abs(lat)) * 10,
                'avg_daily': 2.2
            },
            'wind': {
                'avg_speed': 4.5 + abs(lat) * 0.1,
                'max_speed': 12.3
            },
            'solar': {
                'avg_radiation': 5.5 - abs(lat) * 0.05,
                'peak_radiation': 8.2
            }
        }

# Import pandas for data processing
import pandas as pd
