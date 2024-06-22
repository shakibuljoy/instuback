from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer
from users.models import Institute, CustomUser
from rest_framework import status
from rest_framework.response import Response

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        try:
            user = CustomUser.objects.get(username=username)
            if user.user_type == 'developer':
                return super().post(request, *args, **kwargs)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        instu_id = request.data.get('instu_id')
        
        

        if not instu_id or not username:
            return Response({"detail": "Institute ID and username are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            institute = Institute.objects.get(instu_id=instu_id)
        except Institute.DoesNotExist:
            return Response({"detail": "Institute not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if user.institute != institute:
            return Response({"detail": "User not found for this institute."}, status=status.HTTP_400_BAD_REQUEST)

        return super().post(request, *args, **kwargs)
