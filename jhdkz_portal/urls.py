"""
URL configuration for jhdkz_portal project.
"""
from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Совместимость: после логина некоторые сборки редиректят на /accounts/profile/
    path('accounts/profile/', RedirectView.as_view(url=reverse_lazy('users:dashboard'), permanent=False)),
    path('issues/', include('issues.urls')),
    path('articles/', include('articles.urls')),
    path('users/', include('users.urls')),
    path('submissions/', include('submissions.urls')),  # OJS submission system
    path('reviews/', include('reviews.urls')),  # OJS review system
    path('accounts/', include('django.contrib.auth.urls')), # Basic auth URLs
    # ВНИМАНИЕ: корневые маршруты core в самом конце, чтобы не перехватывать /issues/ и прочие
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
