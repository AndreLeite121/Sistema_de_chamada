from django.contrib import admin
from django.urls import path, include

from core.views import presenca_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('presenca', presenca_view, name='presenca'),
    path('core/', include('core.urls')),
    path('', include('home.urls'))
]
