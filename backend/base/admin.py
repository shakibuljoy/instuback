from django.contrib import admin
from .models import Klass, Student,StudentDocument

class StudentDocumentInline(admin.TabularInline):
    model = StudentDocument
    extra = 1

class StudentAdmin(admin.ModelAdmin):
    inlines = [StudentDocumentInline]

admin.site.register(Student, StudentAdmin)    
admin.site.register(Klass)
