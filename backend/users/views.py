from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import CustomUser
from .serializers import CustomUserSerializer
from rest_framework.exceptions import ValidationError
from copy import deepcopy

@api_view(['POST'])
@permission_classes([IsAuthenticated])
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
        
