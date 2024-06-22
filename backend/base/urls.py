from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView
)
from .views import (
    verify_user,
    StudentView,
    student_image_view,
    StudentImageView
)
from base.api.views import MyTokenObtainPairView
from users.views import user_registration
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'students', StudentView, basename='student')

app_name = 'base'

urlpatterns = [
    path('token/', MyTokenObtainPairView.as_view(),name='token_obtain'),
    path('token/refresh/', TokenRefreshView.as_view(),name='token_refresh'),
    path('verify-user/', verify_user, name="verify-user"),
    path('register/', user_registration, name='user_register'),
    path('',include(router.urls), name='student'),
    path('retrieve_student_image/<pk>/',student_image_view, name="retrieve_student_image")
]
