"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include
from api.views.auth_views import welcome_view  # ✅ Import welcome view
import sys


urlpatterns = [
    path("", welcome_view, name="home"),
    path("admin/", admin.site.urls),
    path("api/v1", include("api.urls")),  # ✅ Include API routes
    path('api/v1/auth/', include('api.urls.auth_urls')),  # or similar

]

if "runserver" in sys.argv:
    from django.urls import get_resolver
    print("\n📌 Registered URLs in Django:")
    for url_pattern in get_resolver().url_patterns:
        print(f"➡️ {url_pattern}")