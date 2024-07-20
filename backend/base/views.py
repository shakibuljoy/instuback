
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .permissions import IsNotAStudent
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status
from .models import Student, Klass, Attendence
from .serializers import StudentSerializer, KlassSerializer, AttendenceSerializer
import mimetypes
from django.http import FileResponse
from django.shortcuts import get_object_or_404
import jwt
from backend import settings
from users.models import CustomUser, Institute
from copy import deepcopy
from rest_framework.parsers import MultiPartParser, FormParser

import datetime


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_user(request):
    return Response({'name': request.user.username, 'user_type': request.user.user_type})

class StudentView(viewsets.ModelViewSet):
    
    permission_classes =[IsNotAStudent]
    serializer_class = StudentSerializer
    parser_classes = [MultiPartParser, FormParser]
    def get_queryset(self):
        user = self.request.user
        klass_id = self.request.GET.get('klass')
        if klass_id:
            try:
                klass_filter = Klass.objects.get(pk=klass_id)
                user_institute = user.institute
                if(user.user_type=='administrator'):
                    return Student.objects.filter(institute=user_institute, klass=klass_filter)
                return Student.objects.filter(institute=user_institute, klass=klass_filter).filter(klass__teachers=user)
            except Klass.DoesNotExist:
                return Response({'detail':'Class not found'}, status=status.HTTP_404_NOT_FOUND)
        elif not klass_id:
            user_institute = user.institute
            if(user.user_type=='administrator'):
                return Student.objects.filter(institute=user_institute)
            return Student.objects.filter(institute=user_institute, klass__teachers=user)
    
    def create(self, request, *args, **kwargs):
        data = deepcopy(request.data)
        user_type = request.user.user_type

        if 'institute' in data and user_type == 'developer':
            try:
                institute = Institute.objects.get(instu_id=data['institute'])
                pass
            except Institute.DoesNotExist:
                return Response({'detail': 'Institute not found'}, status=status.HTTP_404_NOT_FOUND)
        elif user_type != 'developer':
            data['institute'] = request.user.institute.instu_id

        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=False):
            print(serializer.errors)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response({'detail':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
def student_image_view(request, pk):
    auth_header = request.headers.get('Authorization')
    
    if auth_header:
        try:
            # Extract the token from the header
            token = auth_header.split(' ')[1]
            # Decode the token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            # Authenticate the user based on the token payload
            user_id = payload.get('user_id')
            user = get_object_or_404(CustomUser, pk=user_id)
            
            # Check if the user is authenticated
            if user.is_authenticated:
                student = get_object_or_404(Student, pk=pk)
                image_path = student.image.path  # Full path to the image file
                mime_type, _ = mimetypes.guess_type(image_path)  # Guess the mime type
                if not mime_type:
                    mime_type = 'application/octet-stream'  # Default to binary stream if mime type cannot be guessed
                image = open(image_path, 'rb')
                response = FileResponse(image, content_type=mime_type)
                response['Content-Disposition'] = f'inline; filename="{student.image.name}"'
                return response
            else:
                return Response({"detail": "Unauthorized user could not be allowed"}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.ExpiredSignatureError:
            return Response({"detail": "Token has expired"}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({"detail": "Authorization header missing"}, status=status.HTTP_401_UNAUTHORIZED)
    

@api_view(['GET', 'POST'])
@permission_classes([IsNotAStudent])
def klass_view(request):
    if request.method == 'GET':
        user = request.user
        if user.user_type != "teacher":
            klasses = Klass.objects.filter(institute=user.institute)
        elif user.user_type == 'teacher':
            klasses = Klass.objects.filter(teachers=user)
        elif user.user_type == 'developer':
            klasses = Klass.objects.all()
        serializers = KlassSerializer(klasses, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)
    
    if request.method == 'POST':
        pass

    return Response({'detail': 'Something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST', 'GET'])
@permission_classes([IsNotAStudent])
def attendence(request, pk):
    try:
        klass = Klass.objects.get(pk=pk)
        if request.user in klass.teachers.all() or (request.user.user_type == 'administrator' and klass.institute==request.user.institute):
            if request.method == 'POST':
                data = deepcopy(request.data)
                data['teacher'] = request.user.pk
                # try:
                #     data['student'] = Student.objects.get(pk=data['student'])
                # except Student.DoesNotExist:
                #     return Response({'detail':'Student Not Found'}, status=status.HTTP_404_NOT_FOUND)
                
                serializer = AttendenceSerializer(data=data)

                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    today = datetime.date.today()
                    all_attendence_today = Attendence.objects.filter(date=today, klass=klass)
                    all_serializer = AttendenceSerializer(all_attendence_today, many=True)
                    return Response(all_serializer.data, status=status.HTTP_201_CREATED)
            if request.method == 'GET':
                today = datetime.date.today()
                all_attendence_today = Attendence.objects.filter(date=today, klass=klass)
                all_serializer = AttendenceSerializer(all_attendence_today, many=True)
                return Response(all_serializer.data, status=status.HTTP_200_OK)
        else:
            
            return Response({'detail': 'User not allowed to this class'}, status=status.HTTP_401_UNAUTHORIZED)
    except Klass.DoesNotExist:
        return Response({'detail': "Class not Found!"}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'detail': "Data not valid"}, status=status.HTTP_400_BAD_REQUEST)