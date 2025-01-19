from django.contrib import admin
from .models import (Klass, Student,
                    Attendence, AdditionalStudentInfo, Subject, Mark)

class AdStInfoInline(admin.TabularInline):
    model = AdditionalStudentInfo
    extra =1 



class AttendenceInline(admin.TabularInline):
    readonly_fields = ['date']
    model = Attendence
    extra = 1

class SubjectInline(admin.TabularInline):
    model = Subject
    extra = 1





class StudentAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        return qs.filter(klass__institute=request.user.institute)
    inlines = [AdStInfoInline, AttendenceInline]

class KlassAdmin(admin.ModelAdmin):
    inlines = [SubjectInline]
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        return qs.filter(institute=request.user.institute)



admin.site.register(Student, StudentAdmin)
admin.site.register(Klass, KlassAdmin)
admin.site.register(Attendence)
admin.site.register(Mark)



