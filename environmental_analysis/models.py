from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.core.validators import MinValueValidator, MaxValueValidator

class SiteAnalysis(models.Model):
    """Main model for storing site analysis requests and results"""
    name = models.CharField(max_length=200, help_text="Site name or identifier")
    location = models.PointField(srid=4326, help_text="Site coordinates (WGS84)")
    analysis_radius = models.IntegerField(
        default=500,
        validators=[MinValueValidator(100), MaxValueValidator(2000)],
        help_text="Analysis radius in meters"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.location}"
    
    class Meta:
        verbose_name = "Site Analysis"
        verbose_name_plural = "Site Analyses"

class EnvironmentalFeature(models.Model):
    """Model for storing environmental features from OSM"""
    FEATURE_TYPES = [
        ('landuse', 'Land Use'),
        ('natural', 'Natural Feature'),
        ('leisure', 'Leisure Area'),
        ('highway', 'Transportation'),
        ('building', 'Building'),
        ('amenity', 'Amenity'),
    ]
    
    site_analysis = models.ForeignKey(
        SiteAnalysis, 
        on_delete=models.CASCADE, 
        related_name='features'
    )
    feature_type = models.CharField(max_length=20, choices=FEATURE_TYPES)
    osm_id = models.BigIntegerField(help_text="OpenStreetMap ID")
    geometry = models.GeometryField(srid=4326, help_text="Feature geometry")
    properties = models.JSONField(default=dict, help_text="OSM tags and properties")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.feature_type} - OSM ID: {self.osm_id}"
    
    class Meta:
        unique_together = ['site_analysis', 'osm_id']
        indexes = [
            models.Index(fields=['feature_type']),
            models.Index(fields=['osm_id']),
        ]

class ClimateData(models.Model):
    """Model for storing EPW climate data"""
    site_analysis = models.OneToOneField(
        SiteAnalysis,
        on_delete=models.CASCADE,
        related_name='climate_data'
    )
    epw_file_path = models.CharField(max_length=500, blank=True, null=True)
    temperature_data = models.JSONField(default=dict, help_text="Temperature statistics")
    precipitation_data = models.JSONField(default=dict, help_text="Precipitation data")
    wind_data = models.JSONField(default=dict, help_text="Wind patterns")
    solar_data = models.JSONField(default=dict, help_text="Solar radiation data")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Climate data for {self.site_analysis.name}"
    
    class Meta:
        verbose_name = "Climate Data"
        verbose_name_plural = "Climate Data"
