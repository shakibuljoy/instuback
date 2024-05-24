from django.contrib import admin
from .models import CustomUser, Institute


admin.site.register(CustomUser)

admin.site.register(Institute)