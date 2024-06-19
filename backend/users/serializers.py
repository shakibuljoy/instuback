from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

UserModel = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):

    

    class Meta:
        model = UserModel
        fields = ( "id", "username", "password", "email", "user_type", "first_name", "last_name", "institute", "profile_pic")

        password = serializers.CharField(write_only=True)

    def create(self, validated_data):

        user = UserModel.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            user_type=validated_data['user_type'],
            institute=validated_data.get('institute'),
            profile_pic=validated_data.get('profile_pic')
        )

        return user
    
    def validate(self, data):
    # Existing validation logic
        user_type = data.get('user_type')
        institute = data.get('institute')
        if user_type != "developer" and not institute:
            raise ValidationError("Non-developer User must saved under a institute")
        return data