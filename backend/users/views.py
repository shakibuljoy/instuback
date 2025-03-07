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
from django.dispatch import receiver
from django.db.models.signals import post_save
from base.mailsender import mail_sender

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
        
            student = Student.objects.get(student_id=student_id)
            if CustomUser.objects.filter(student=student).exists():
                return Response({"detail": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)
            if student.active == False:
                return Response({"detail":"Student is not active"}, status=status.HTTP_400_BAD_REQUEST)
            if student.email == '':
                return Response({"detial":"Email not found"}, status=status.HTTP_400_BAD_REQUEST)
            email_associated = CustomUser.objects.filter(email=student.email).exists()
            if email_associated:
                return Response({"detail": "Email already associated with another user"}, status=status.HTTP_400_BAD_REQUEST)
            user_creation = CustomUser.objects.create_user(username=student.email, password=student.student_id, user_type='student', email=student.email, institute=student.institute, student=student)
            user_creation.save()
            return Response(data=user_creation.username, status=status.HTTP_201_CREATED)
        
        except Student.DoesNotExist:
            return Response({"detail":"Student not found"}, status=status.HTTP_404_NOT_FOUND)
        

@receiver(post_save, sender=CustomUser)
def create_student_user(sender, instance, created, **kwargs):
    if created and instance.is_student():
        student = instance.student
        mail_sender('Account Created', f'Your account has been created. Your username is {instance.username} and password is {student.student_id}', student.email)
        student.save()
        
