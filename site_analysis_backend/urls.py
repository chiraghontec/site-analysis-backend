"""
URL configuration for site_analysis_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from environmental_analysis.api import router as environmental_router

api = NinjaAPI(
    title="Site Analysis API",
    description="Environmental & Climate Site Report Generator API",
    version="1.0.0"
)

# Add the environmental analysis router
api.add_router("/environmental/", environmental_router)

@api.get("/hello")
def hello(request):
    return {"message": "Hello from Django Ninja API!"}

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", api.urls),
]
