from rest_framework.permissions import BasePermission


class IsNotAStudent(BasePermission):
    # Checking the user not a student
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.user_type != 'student')
    
class IsAdministrator(BasePermission):
    # Checking the user is an administrator
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.user_type == 'administrator')