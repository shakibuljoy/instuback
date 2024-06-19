from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView
)
from .views import (
    verify_user
)
from base.api.views import MyTokenObtainPairView
from users.views import user_registration

app_name = 'base'

urlpatterns = [
    path('token/', MyTokenObtainPairView.as_view(),name='token_obtain'),
    path('token/refresh/', TokenRefreshView.as_view(),name='token_refresh'),
    path('verify-user/', verify_user, name="verify-user"),
    path('register/', user_registration, name='user_register')
]
