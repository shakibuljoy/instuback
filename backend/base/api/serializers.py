from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    instu_id = serializers.CharField(max_length=150)
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['name'] = user.first_name+' '+user.last_name
        token['type'] = user.user_type
        # ...
        print(user.user_type)
        return token