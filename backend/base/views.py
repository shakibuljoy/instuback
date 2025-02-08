
from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .permissions import IsNotAStudent
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status
from .models import Student, Klass, Attendence, AdditionalStudentField, AdditionalStudentInfo, Mark
from .serializers import (StudentSerializer, KlassSerializer, AttendenceSerializer,
                           AdditionalStFieldSerializer,AdditionalStInfoSerializer,
                           MarkSerializer, SubjectSerializer)
import mimetypes
from django.http import FileResponse
from django.shortcuts import get_object_or_404
import jwt
from backend import settings
from users.models import CustomUser
from copy import deepcopy
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Sum
from users.utils import validate_institute
import datetime
from .storages import generate_presigned_url


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_user(request):
    return Response({'name': request.user.username, 'user_type': request.user.user_type})


@api_view(['POST'])
def student_create(request):
    institute = validate_institute(request)
    if institute:
        data = deepcopy(request.data)
        data['institute'] = institute.instu_id
    
        seralizer = StudentSerializer(data=data)
        if seralizer.is_valid(raise_exception=True):
            seralizer.save()
            return Response(seralizer.data, status=status.HTTP_201_CREATED)
    else:
        return Response({'detail':'Provide valid institute id'}, status=status.HTTP_404_NOT_FOUND)
    


class StudentView(viewsets.ModelViewSet):
    
    # permission_classes =[IsNotAStudent]
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
        institute = validate_institute(request)
        if institute:


            data['institute'] = institute.instu_id
            
            serializer = self.get_serializer(data=data)
            
            if serializer.is_valid(raise_exception=False):
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            else:
                print(serializer.errors)
                return Response({'detail':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail':'Provide valid institute id'}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_image_view(request, pk):
        try:
            student = get_object_or_404(Student, pk=pk)
            image_url = generate_presigned_url(student.image.name)  # ✅ Return URL
            return Response({"image_url": image_url}, status=status.HTTP_200_OK)  # ✅ Send URL to frontend
        except jwt.ExpiredSignatureError:
            return Response({"detail": "Token expired"}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

class AdditionalStudentFieldView(viewsets.ModelViewSet):
    serializer_class = AdditionalStFieldSerializer
    def get_queryset(self):
        institute = validate_institute(self.request)
        if institute:
            return AdditionalStudentField.objects.filter(institute=institute)
        else:
            return []
    
    def create(self, request, *args, **kwargs):
        if request.user.is_authenticated:

            data = deepcopy(request.data)
            user_institute = request.user.institute
            data['institute'] = user_institute.id
            serializer = self.get_serializer(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'detial':'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)

from django.core.files.uploadedfile import InMemoryUploadedFile

class AdditionalStInfoView(viewsets.ModelViewSet):
    serializer_class = AdditionalStInfoSerializer 
    def get_queryset(self):
        if self.request.user.is_authenticated:
            user = self.request.user
            return AdditionalStudentInfo.objects.filter(field__institute=user.institute)
    
    def create(self, request, *args, **kwargs):
        data = request.data
        tem_data = []
        for i in data:
            keyNote = str(i).split('_')
            student_id = keyNote[0]
            field_id = keyNote[1]
            value = data[i]
            if type(value) == str:
                tem_data.append({
                    'field_id':field_id,
                    'student_id': student_id,
                    'value':value
                })
            elif type(value) == InMemoryUploadedFile:
                tem_data.append({
                    'field_id':field_id,
                    'student_id': student_id,
                    'file':value
                })
        # Check if the request contains multiple items (bulk)
        if isinstance(tem_data, list):
            serializer = self.get_serializer(data=tem_data, many=True)
        else:
            serializer = self.get_serializer(data=tem_data)

        # Validate and save the data
        if serializer.is_valid(raise_exception=True):
            return self.perform_create(serializer)

            

    def perform_create(self, serializer):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

@api_view(['GET', 'POST'])
def klass_view(request):
    if request.method == 'GET':
        klasses = []
        institute = validate_institute(request)
        if institute:
            klasses = Klass.objects.filter(institute=institute)
        elif(request.user.is_authenticated):
            user = request.user
            if user.user_type == 'developer':
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
                today = datetime.date.today()
                dataList = request.data
                present_mail_list = []
                abscent_mail_list = []
                for data in dataList:
                    data['teacher'] = request.user.pk
                    data['klass'] = klass.pk
                    try:
                        student = Student.objects.get(pk=data['student'])
                        past_attendence = Attendence.objects.filter(student=student, date=today, klass=klass).exists()
                        
                        if past_attendence:
                            return Response({'detail': 'Attendence already submitted'}, status=status.HTTP_400_BAD_REQUEST)
                            
                        if data['presents']:
                            present_mail_list.append(student.email)
                        else:
                            abscent_mail_list.append(student.email)
                    except Student.DoesNotExist:
                        return Response({'detail': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
           
                if isinstance(dataList, list):
                    serializer = AttendenceSerializer(data=dataList, many=True)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        
                        # mass_mail_sender("Attendence",f"You have been marked as present at {str(today)}", present_mail_list)
                        # mass_mail_sender("Attendence",f"You have been marked as abscent at {str(today)}", abscent_mail_list)
                        return Response({'detail':'Submited attendence successfully'}, status=status.HTTP_201_CREATED)
                     
                    return Response({'detail':'Submited attendence successfully'}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'detail': 'Data not valid'}, status=status.HTTP_400_BAD_REQUEST)
            elif request.method == 'GET':
                today = datetime.date.today()
                if request.GET.get('date'):
                    today = request.GET.get('date')
                all_attendence_today = Attendence.objects.filter(date=today, klass=klass)
                all_serializer = AttendenceSerializer(all_attendence_today, many=True)
                return Response(all_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            return Response({'detail': 'User not allowed to this class'}, status=status.HTTP_401_UNAUTHORIZED)
    except Klass.DoesNotExist:
        return Response({'detail': "Class not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(str(e))
        return Response({'detail': "Something went wrong", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['PATCH','GET'])
@permission_classes([IsNotAStudent])
def editAttendece(request, pk):
    try:
        attendence = Attendence.objects.get(pk=pk)
        if request.method == 'PATCH':
            if attendence.teacher == request.user or request.user.user_type == 'administrator':
                attendence.presents = True if request.data.get('presents') == 'true' else False
                attendence.cause = request.data['cause'] if request.data.get('cause') else ""
                attendence.save()
                serializer = AttendenceSerializer(attendence)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        elif  request.method == 'GET':
            serializer = AttendenceSerializer(attendence)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Attendence.DoesNotExist:
            return Response({'detail': 'Data no found'}, status=status.HTTP_404_NOT_FOUND)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_attendence(request, pk):
    month = request.GET.get('month')
    year = request.GET.get('year')
    if month and year:
        try:
            user = request.user
            if user.is_student():

                student = user.student
                access_conditon = True
                
            else:
                student = Student.objects.get(pk=pk)
                access_conditon = user in student.klass.teachers.all() or (user.user_type == 'administrator'  and student.institute==user.institute)
            
            if access_conditon:
                all_attendence = Attendence.objects.filter(
                    student=student,
                    date__month=month,
                    date__year=year
                )
                serializer = AttendenceSerializer(all_attendence, many=True)
                print(serializer.data)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)

        except Student.DoesNotExist:
            return Response({'detail': 'Student not found!'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'detail': 'Specify month & year'}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET'])
def get_subjects(request):
    klass_id = request.GET.get('klass_id')
    student_id = request.GET.get('student_id')
    if klass_id:

        try:
            klass = Klass.objects.get(pk=klass_id)
        
            subjects = klass.subject_set.all()
            serializer = SubjectSerializer(subjects, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Klass.DoesNotExist:
            return Response({'detail': 'Class not found!'}, status=status.HTTP_404_NOT_FOUND)
    elif student_id:
        try:
            student = Student.objects.get(pk=student_id)
            subjects = student.klass.subject_set.all()
            serializer = SubjectSerializer(subjects, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Student.DoesNotExist:
            return Response({'detail': 'Student not found!'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'detail': 'Provide class id or student id'}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
@permission_classes([IsNotAStudent])
def submit_marks(request):
    data = request.data
    tem_data = []
    for i in data:
        keyNote = str(i).split('_')
        student_id = keyNote[0]
        field_id = keyNote[1]
        value = data[i]

        tem_data.append({
            'subject': field_id,
            'student': student_id,
            'mark': float(value)
        })

    try:
        student = Student.objects.get(pk=tem_data[0]['student'])

        if not student.active:
            return Response({'detail': 'Student not active'}, status=status.HTTP_400_BAD_REQUEST)
        
        if isinstance(tem_data, list):
            serializer = MarkSerializer(data=tem_data, many=True)
        else:
            serializer = MarkSerializer(data=tem_data)
        
        if not serializer.is_valid():
            # Collect errors for each item in the list
            error = serializer.errors[0]['non_field_errors'][0].code
            if error == "unique":
                return Response({'detail': 'Marks already submitted'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': "Data is not valid"}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
    except Student.DoesNotExist:
        return Response({'detail': 'Student not found!'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        print(f"Unexpected error: {e}")  # Debug print
        return Response({'detail': "Something went wrong", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def get_marks(request):
    student_id = request.GET.get('student_id')
    instu_id = request.GET.get('instu_id')
    klass_id = request.GET.get('klass_id')
    if student_id and instu_id and klass_id:
        try:
            student = Student.objects.get(student_id=student_id, klass__institute__instu_id=instu_id)
            klass = Klass.objects.get(pk=klass_id)
            if klass.result_published:
                marks = Mark.objects.filter(student=student, subject__klass=klass)
                if marks.count() == 0:
                    return Response({'detail': 'No marks found'}, status=status.HTTP_404_NOT_FOUND)
                serializer = MarkSerializer(marks, many=True)
                
                student_data = {
                    'name': student.first_name+' '+student.last_name,
                    'student_id': student.student_id,
                    'class': student.klass.name,
                    'total_marks': marks.aggregate(Sum('mark'))['mark__sum'] or 0
                }
                response_data = {
                    'student': student_data,
                    'marks': serializer.data
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Result not published yet'}, status=status.HTTP_400_BAD_REQUEST)
        except Student.DoesNotExist:
            return Response({'detail': 'Student not found!'}, status=status.HTTP_404_NOT_FOUND)
        except Klass.DoesNotExist:
            return Response({'detail': 'Class not found!'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    return Response({'detail': 'Data not provided properly'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsNotAStudent])
def migrate_student(request):
    data = request.data
    student_id = data.get('student_id')
    klass_id = data.get('klass_id')
    if student_id is None or klass_id is None:
        return Response({'detail': 'Provide Student ID and Class ID'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        student = Student.objects.get(student_id=student_id)
        klass = Klass.objects.get(pk=klass_id)
        student.klass = klass
        student.save()
        return Response({'detail': f"Student ID: {student_id} migrated to class {str(klass)}"}, status=status.HTTP_200_OK)
    except Student.DoesNotExist:
        return Response({'detail': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        