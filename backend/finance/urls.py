from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import FeeView

router = DefaultRouter()
router.register(r'fees', FeeView)


app_name='billing'

