"""
URL configuration for jhdkz_portal project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('issues/', include('issues.urls')),
    path('articles/', include('articles.urls')),
    path('users/', include('users.urls')),
    path('accounts/', include('django.contrib.auth.urls')), # Basic auth URLs
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
