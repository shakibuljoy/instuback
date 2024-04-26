from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from .views import (
    verify_user
)

app_name = 'base'

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(),name='token_obtain'),
    path('token/refresh/', TokenRefreshView.as_view(),name='token_refresh'),
    path('verify-user/', verify_user, name="verify-user")
]
