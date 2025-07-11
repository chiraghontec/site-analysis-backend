from ninja import Router
from ninja.schema import Schema
from typing import List, Dict, Any, Optional
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import json
import logging
from datetime import datetime

from .models import SiteAnalysis, EnvironmentalFeature, ClimateData
from .services import EnvironmentalAnalysisService

logger = logging.getLogger(__name__)
router = Router()

class CoordinateSchema(Schema):
    latitude: float
    longitude: float
    radius: Optional[int] = 500
    name: Optional[str] = None

class EnvironmentalFeatureSchema(Schema):
    id: int
    feature_type: str
    osm_id: int
    properties: Dict[str, Any]

class AnalysisResponseSchema(Schema):
    id: int
    name: str
    coordinates: Dict[str, float]
    radius: int
    features_count: int
    summary: Dict[str, Any]
    created_at: str

@router.get("/test")
def test_endpoint(request):
    """Test endpoint to verify API is working"""
    return {"message": "Environmental Analysis API is working with PostGIS!"}

@router.post("/analyze", response=AnalysisResponseSchema)
def analyze_site(request, coordinates: CoordinateSchema):
    """
    Analyze environmental features around given coordinates using OSMnx
    """
    try:
        # Initialize the analysis service
        service = EnvironmentalAnalysisService()
        
        # Perform the analysis
        site_analysis = service.analyze_site(
            latitude=coordinates.latitude,
            longitude=coordinates.longitude,
            radius=coordinates.radius,
            site_name=coordinates.name
        )
        
        # Get summary statistics
        summary = service.get_analysis_summary(site_analysis)
        
        return {
            "id": site_analysis.id,
            "name": site_analysis.name,
            "coordinates": {
                "latitude": site_analysis.location.y,
                "longitude": site_analysis.location.x,
            },
            "radius": site_analysis.analysis_radius,
            "features_count": site_analysis.features.count(),
            "summary": summary,
            "created_at": site_analysis.created_at.isoformat(),
        }
        
    except Exception as e:
        logger.error(f"Error in analyze_site: {str(e)}")
        return JsonResponse(
            {"error": f"Analysis failed: {str(e)}"}, 
            status=500
        )

@router.get("/analysis/{analysis_id}")
def get_analysis(request, analysis_id: int):
    """Get details of a specific analysis"""
    site_analysis = get_object_or_404(SiteAnalysis, id=analysis_id)
    service = EnvironmentalAnalysisService()
    summary = service.get_analysis_summary(site_analysis)
    
    return {
        "id": site_analysis.id,
        "name": site_analysis.name,
        "coordinates": {
            "latitude": site_analysis.location.y,
            "longitude": site_analysis.location.x,
        },
        "radius": site_analysis.analysis_radius,
        "summary": summary,
        "created_at": site_analysis.created_at.isoformat(),
    }

@router.get("/analysis/{analysis_id}/features")
def get_analysis_features(request, analysis_id: int, feature_type: str = None):
    """Get environmental features for a specific analysis"""
    site_analysis = get_object_or_404(SiteAnalysis, id=analysis_id)
    features = site_analysis.features.all()
    
    if feature_type:
        features = features.filter(feature_type=feature_type)
    
    features_data = []
    for feature in features:
        features_data.append({
            "id": feature.id,
            "feature_type": feature.feature_type,
            "osm_id": feature.osm_id,
            "properties": feature.properties,
            "geometry": json.loads(feature.geometry.geojson),
        })
    
    return {
        "analysis_id": analysis_id,
        "feature_type": feature_type,
        "features": features_data,
        "count": len(features_data),
    }

@router.get("/analysis/{analysis_id}/export")
def export_analysis(request, analysis_id: int, format: str = "geojson"):
    """Export analysis results in various formats"""
    site_analysis = get_object_or_404(SiteAnalysis, id=analysis_id)
    features = site_analysis.features.all()
    
    if format.lower() == "geojson":
        geojson = {
            "type": "FeatureCollection",
            "features": []
        }
        
        for feature in features:
            geojson["features"].append({
                "type": "Feature",
                "id": feature.osm_id,
                "properties": {
                    **feature.properties,
                    "feature_type": feature.feature_type,
                    "analysis_id": analysis_id,
                },
                "geometry": json.loads(feature.geometry.geojson),
            })
        
        return geojson
    
    return {"error": f"Format '{format}' not supported. Available: geojson"}

@router.get("/features/types")
def get_feature_types(request):
    """Get available feature types"""
    return {
        "feature_types": [choice[0] for choice in EnvironmentalFeature.FEATURE_TYPES],
        "descriptions": dict(EnvironmentalFeature.FEATURE_TYPES),
    }

@router.get("/analysis/{analysis_id}/climate")
def get_climate_data(request, analysis_id: int):
    """Get climate data for a specific analysis"""
    site_analysis = get_object_or_404(SiteAnalysis, id=analysis_id)
    
    try:
        climate_data = site_analysis.climate_data
        
        return {
            "analysis_id": analysis_id,
            "site_name": site_analysis.name,
            "coordinates": {
                "latitude": site_analysis.location.y,
                "longitude": site_analysis.location.x,
            },
            "climate_zone": climate_data.temperature_data.get("monthly_averages", {}).get("zone", "unknown"),
            "temperature_data": climate_data.temperature_data,
            "precipitation_data": climate_data.precipitation_data,
            "wind_data": climate_data.wind_data,
            "solar_data": climate_data.solar_data,
            "last_updated": climate_data.updated_at.isoformat(),
            "created_at": climate_data.created_at.isoformat(),
        }
        
    except ClimateData.DoesNotExist:
        return {"error": "Climate data not available for this analysis", "analysis_id": analysis_id}

@router.post("/analysis/{analysis_id}/climate/refresh")
def refresh_climate_data(request, analysis_id: int):
    """Refresh climate data for a specific analysis"""
    site_analysis = get_object_or_404(SiteAnalysis, id=analysis_id)
    
    from .services import ClimateDataService
    
    climate_service = ClimateDataService()
    climate_data = climate_service.get_climate_data(
        site_analysis.location.y,  # latitude
        site_analysis.location.x,  # longitude
        site_analysis
    )
    
    return {
        "message": "Climate data refreshed successfully",
        "analysis_id": analysis_id,
        "updated_at": climate_data.updated_at.isoformat(),
        "climate_zone": climate_data.temperature_data.get("monthly_averages", {}).get("zone", "unknown"),
    }

@router.get("/climate/summary")
def get_climate_summary(request, latitude: float, longitude: float):
    """Get climate summary for any coordinates without creating an analysis"""
    from .services import ClimateDataService
    
    climate_service = ClimateDataService()
    
    # Get climate summary data
    current_weather = climate_service._get_current_weather(latitude, longitude)
    climate_summary = climate_service._get_climate_summary(latitude, longitude)
    
    return {
        "coordinates": {
            "latitude": latitude,
            "longitude": longitude,
        },
        "climate_zone": climate_summary.get("zone", "unknown"),
        "current_weather": current_weather,
        "climate_patterns": climate_summary,
        "timestamp": datetime.now().isoformat(),
    }
