from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from base.permissions import IsAdministrator
from rest_framework import status
from base.models import Student
from .models import CustomUser  
from .serializers import CustomUserSerializer
from rest_framework.exceptions import ValidationError
from copy import deepcopy

@api_view(['POST'])
@permission_classes([IsAdministrator])
def user_registration(request):
    if request.method == 'POST':
        data = deepcopy(request.data)
        
        # A developer user can create Administrator, Teacher and Student
        if  request.user.is_developer():
            serializers = CustomUserSerializer(data=data)
            if serializers.is_valid(raise_exception=True):
                if serializers.validated_data['user_type'] != 'developer':
                    serializers.save()
                    return Response(data=serializers.validated_data['username'],status=status.HTTP_201_CREATED)
        # But A non-developer user can only create Teacher and Student
        elif request.user.is_administrator():
            institute = request.user.institute
            
            data['institute'] = institute.pk
            data['username'] = institute.instu_id+"_"+data['username']
            serializers = CustomUserSerializer(data=data)
            try:
                serializers.is_valid(raise_exception=True)
            except ValidationError as e:
                return Response(data=e.detail, status=status.HTTP_400_BAD_REQUEST)
            user_type = serializers.validated_data.get('user_type')
            if user_type in ['teacher', 'student']:
                serializers.save(institute=institute)
                return Response(data=serializers.validated_data['username'],status=status.HTTP_201_CREATED)
            else:
                return Response(data="Please contact with Instuzilla to create an adminstrator", status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(data="Only administrator can create any user", status=status.HTTP_401_UNAUTHORIZED) 
        return Response(data="Something went wrong",status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
@permission_classes([IsAdministrator])
def student_user(request):
    if request.method == 'POST':
        student_id = request.data.get('student_id')
        try:
            prev_user = CustomUser.objects.filter(username=student_id).exists()
            if prev_user:
                return Response(data="User already exists", status=status.HTTP_400_BAD_REQUEST)
        
            student = Student.objects.get(student_id=student_id)
            user_creation = CustomUser.objects.create_user(username=student.student_id, password=student.student_id, user_type='student', email=student.email, institute=student.institute)
            user_creation.save()
            return Response(data=user_creation.username, status=status.HTTP_201_CREATED)
        
        except Student.DoesNotExist:
            return Response(data="Student not found", status=status.HTTP_404_NOT_FOUND)
        
