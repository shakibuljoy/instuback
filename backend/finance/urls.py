from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (FeeView, BillViewSet, PaymentViewSet,
                     student_bills, payment_created_by_user, online_payment, success_url
)

router = DefaultRouter()
router.register(r'fees', FeeView, basename='fees')
router.register(r'bill', BillViewSet, basename='bill')
router.register(r'payment', PaymentViewSet, basename='payment')


app_name='finance'

urlpatterns = [
    path('', include(router.urls), name='finance'),
    path('student-bills/<pk>/', student_bills, name='student-bills'),
    path('user-created-payment/', payment_created_by_user, name='user-created-payment'),
    path('online-payment/', online_payment, name='online-payment'),
    path('success-payment/', success_url, name='success-url')
]


