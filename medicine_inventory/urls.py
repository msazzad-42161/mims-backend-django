# medicine_inventory/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from inventory import views as inventory_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('inventory.urls')),
        # JWT Auth Endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # User Registration Endpoint
    path('api/register/', inventory_views.RegisterView.as_view(), name='register'),
]
