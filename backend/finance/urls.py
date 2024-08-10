from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FeeView, BillViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r'fees', FeeView, basename='fees')
router.register(r'bill', BillViewSet, basename='bill')
router.register(r'payment', PaymentViewSet, basename='payment')


app_name='finance'

urlpatterns = [
    path('', include(router.urls), name='finance')
]


