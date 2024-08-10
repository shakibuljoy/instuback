
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('base.urls'), name='base_urls'),
    path('finance/', include('finance.urls'), name='finance_urls')
]
