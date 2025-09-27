"""
URL configuration for config project.

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
# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

def health_check(request):
    return JsonResponse({"status": "healthy", "service": "espritverse"})

urlpatterns = [
    path("", health_check, name="health_check"),  # Health check endpoint
    path("admin/", admin.site.urls),
    path("api/", include("accounts.urls")),   # auth, users, profiles, friends
    path("api/", include("social.urls")),     # posts, comments
    path("api/", include("notifications.urls")),
    path("api/dm/", include("dm.urls")),      # direct messages
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),  # raw OpenAPI JSON
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

]

# serve media files in dev
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
