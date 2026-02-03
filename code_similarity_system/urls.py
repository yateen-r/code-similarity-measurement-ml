from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/users/dashboard/', permanent=False)),
    path('users/', include('users.urls', namespace='users')),
    path('accounts/', include('users.urls', namespace='accounts')),  # Same URLs, different namespace
    path('admins/', include('admins.urls', namespace='admins')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
