
from django.contrib import admin
from django.urls import path, include

admin.site.site_header = "Instuzilla Admin"
admin.site.site_title = "School Management System"
admin.site.index_title = "School Management System"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('base.urls'), name='base_urls'),
    path('finance/', include('finance.urls'), name='finance_urls')
]
