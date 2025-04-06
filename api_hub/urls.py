from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from message_receiver.views import webhook_receiver

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    
    # Custom admin UI
    path('', include('admin_ui.urls')),
    
    # API endpoints
    path('api/', include('api_hub.api_urls')),
    
    # Webhook endpoints
    path('webhook/<str:path>/', webhook_receiver, name='webhook_receiver'),
    
    # Django Browser Reload
    path('__reload__/', include('django_browser_reload.urls')),
]

# Add static and media URLs in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
