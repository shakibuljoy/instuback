from rest_framework import serializers
from .models import Student,Institute, Klass, Attendence
from django.db import IntegrityError
from users.models import CustomUser
from django.urls import reverse
from rest_framework.exceptions import ValidationError


class StudentSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    full_klass = serializers.SerializerMethodField()
    institute = serializers.SlugRelatedField(slug_field='instu_id', queryset=Institute.objects.all(), allow_null=True)
    class Meta:
        model = Student
        fields = '__all__'

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image != None and request:
            return request.build_absolute_uri(reverse('base:retrieve_student_image', kwargs={'pk': obj.pk}))
        return None
    
    def get_full_klass(self, obj):
        return f"{obj.klass.name}{'-' + obj.klass.group if obj.klass.group else ''}{'-' + obj.klass.branch if obj.klass.branch else ''}"
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if instance.image and request:
            # representation['image_url'] = request.build_absolute_uri(reverse('base:retrieve_student_image', kwargs={'pk': instance.pk}))
            representation['image_url'] = self.get_image_url(instance)
            representation['image'] = 'uploaded'
            representation['full_klass'] = self.get_full_klass(instance)
        return representation
    
    def validate_image(self, value):
        MAX_IMAGE_SIZE = 2 * 1024 * 1024 # 2MB
        print(value.size)
        if value.size > MAX_IMAGE_SIZE:
            raise ValidationError(f"Image size should not exceed {MAX_IMAGE_SIZE / (1024 * 1024)} MB.")
        return value


class KlassSerializer(serializers.ModelSerializer):
    full_klass = serializers.SerializerMethodField()
    institute = serializers.SlugRelatedField(slug_field='instu_id', queryset=Institute.objects.all(), allow_null=True)
    
    class Meta:
        model = Klass
        fields = '__all__'

    def get_full_klass(self, obj):
        return f"{obj.name}{'-' + obj.group if obj.group else ''}{'-' + obj.branch if obj.branch else ''}"
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['full_klass'] = self.get_full_klass(instance)
        return representation


class AttendenceSerializer(serializers.ModelSerializer):
    # student = StudentSerializer() 
    class Meta:
        model = Attendence
        fields = '__all__'
        read_only_fields = ['date']

    
    def to_representation(self, instance):
        represents =  super().to_representation(instance)
        represents['student'] = StudentSerializer(instance.student).data
        return represents
     

    def validate(self,data):
        klass = data.get('klass')
        teacher = data.get('teacher')
        if(teacher not in klass.teachers.all()):
            if teacher.user_type != 'administrator':
                raise ValidationError({"detail": "Unauthorized class access"})
        
        return data
    
    def create(self, validated_data):
        try:
            return Attendence.objects.create(**validated_data)
        except IntegrityError:
            raise serializers.ValidationError(
                {"detail": "An attendance record with the same date, student, and class already exists."}
            )