# UAMS/urls.py
from django.contrib import admin
from django.urls import path, include
from UAMS_App import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),  # Make login the root page
    path('accounts/', include('UAMS_App.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)