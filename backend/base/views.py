
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .permissions import IsNotAStudent
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.views import APIView
from .models import Student
from .serializers import StudentSerializer
import mimetypes
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
import jwt
from backend import settings
from users.models import CustomUser
import os
from PIL import Image
from io import BytesIO


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_user(request):
    return Response({'name': request.user.username, 'user_type': request.user.user_type})

class StudentView(viewsets.ModelViewSet):
    permission_classes =[IsNotAStudent]
    serializer_class = StudentSerializer
    def get_queryset(self):
        user_institute = self.request.user.institute
        return Student.objects.filter(institute=user_institute)


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
                return Response({"detail": "Unauthorized user could not be allowed"}, status=401)
        except jwt.ExpiredSignatureError:
            return Response({"detail": "Token has expired"}, status=401)
        except jwt.InvalidTokenError:
            return Response({"detail": "Invalid token"}, status=401)
    else:
        return Response({"detail": "Authorization header missing"}, status=401)
    
class StudentImageView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self, request, pk, format=None):
        student = get_object_or_404(Student,pk=pk)

        if not student.image:
            return Response({'detail': 'Image not found for this Student'}, status=404)
        
        try:
            image_path = student.image.path
            with open(image_path, 'rb') as f:
                image_data = f.read()
            with Image.open(BytesIO(image_data)) as img:
                # Optional: Perform image manipulation (resize, etc.)
                img_data = img.getvalue('RGB')  # Get image data in desired format
        except (IOError, OSError):
            return Response({"detail":"Invalid image data"}, status=404)
         # Get content type based on file extension
        extension = os.path.splitext(student.image.path)[1].lower()
        content_type = 'image/' + extension.lstrip('.')  # Remove leading dot

        return Response(img_data, content_type=content_type)
