from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView
)
from .views import (
    verify_user,
    StudentView,
    student_image_view,
    klass_view,
    attendence,
    editAttendece,
    get_student_attendence,
    AdditionalStudentFieldView,
    AdditionalStInfoView,
    student_create,
    get_subjects,
    submit_marks,
    get_marks,
    migrate_student,
)
from base.api.views import MyTokenObtainPairView
from users.views import user_registration
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'students', StudentView, basename='student')
router.register(r'add_st_field', AdditionalStudentFieldView, basename='add_st_field')
router.register(r'add_st_info', AdditionalStInfoView, basename='add_st_info')

app_name = 'base'

urlpatterns = [
    path('token/', MyTokenObtainPairView.as_view(),name='token_obtain'),
    path('token/refresh/', TokenRefreshView.as_view(),name='token_refresh'),
    path('verify-user/', verify_user, name="verify-user"),
    path('register/', user_registration, name='user_register'),
    path('',include(router.urls), name='student'),
    path('retrieve_student_image/<pk>/',student_image_view, name="retrieve_student_image"),
    path('klasses', klass_view, name="klass_view"),
    path('attendence/<pk>/', attendence, name='attendence'),
    path('edit-attendence/<pk>/', editAttendece, name='edit-attendence'),
    path('student-attendance/<pk>/', get_student_attendence, name='student-attendance'),
    path('student-create/', student_create, name='student-create'),

    path('get-subjects/', get_subjects, name='get-subjects'),
    path('submit-marks/', submit_marks, name='submit-marks'),
    path('get-marks/', get_marks, name='get-marks'),
    path('migrate-student/', migrate_student, name='migrate-student'),
]
