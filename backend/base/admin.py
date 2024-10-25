from django.contrib import admin
from .models import (Klass, Student,
                    Attendence, AdditionalStudentInfo)

class AdStInfoInline(admin.TabularInline):
    model = AdditionalStudentInfo
    extra =1 



class AttendenceInline(admin.TabularInline):
    readonly_fields = ['date']
    model = Attendence
    extra = 1


class StudentAdmin(admin.ModelAdmin):
    inlines = [AdStInfoInline, AttendenceInline]



admin.site.register(Student, StudentAdmin)
admin.site.register(Klass)
admin.site.register(Attendence)


