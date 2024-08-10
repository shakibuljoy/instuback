from django.contrib import admin
from .models import CustomUser, Institute
from base.models import AdditionalStudentField


class AdStFieldInline(admin.TabularInline):
    model = AdditionalStudentField
    extra =1 

class InstituteAdmin(admin.ModelAdmin):
    inlines = [ AdStFieldInline]


admin.site.register(CustomUser)

admin.site.register(Institute, InstituteAdmin)