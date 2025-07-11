from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from .models import SiteAnalysis, EnvironmentalFeature, ClimateData

@admin.register(SiteAnalysis)
class SiteAnalysisAdmin(GISModelAdmin):
    list_display = ['name', 'location', 'analysis_radius', 'created_at']
    list_filter = ['analysis_radius', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Site Information', {
            'fields': ('name', 'location', 'analysis_radius')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(EnvironmentalFeature)
class EnvironmentalFeatureAdmin(GISModelAdmin):
    list_display = ['feature_type', 'osm_id', 'site_analysis', 'created_at']
    list_filter = ['feature_type', 'created_at']
    search_fields = ['osm_id', 'site_analysis__name']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Feature Information', {
            'fields': ('site_analysis', 'feature_type', 'osm_id')
        }),
        ('Geometry & Properties', {
            'fields': ('geometry', 'properties')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(ClimateData)
class ClimateDataAdmin(admin.ModelAdmin):
    list_display = ['site_analysis', 'epw_file_path', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['site_analysis__name', 'epw_file_path']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Site Reference', {
            'fields': ('site_analysis', 'epw_file_path')
        }),
        ('Climate Data', {
            'fields': ('temperature_data', 'precipitation_data', 'wind_data', 'solar_data')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
