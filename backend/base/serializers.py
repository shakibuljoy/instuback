from rest_framework import serializers
from .models import Student,Institute, Klass
from users.models import CustomUser
from django.urls import reverse
from rest_framework.exceptions import ValidationError


class StudentSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    institute = serializers.SlugRelatedField(slug_field='instu_id', queryset=Institute.objects.all(), allow_null=True)
    class Meta:
        model = Student
        fields = ['id','student_id','klass', 'first_name', 'last_name', 'mobile', 'institute',
                  'fathers_name', 'mothers_name', 'address','birth_date', 'birth_certificate_no',
                  'nid_no', 'image', 'image_url'
                  ]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(reverse('base:retrieve_student_image', kwargs={'pk': obj.pk}))
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if instance.image and request:
            representation['image_url'] = request.build_absolute_uri(reverse('base:retrieve_student_image', kwargs={'pk': instance.pk}))
            representation['image'] = 'uploaded'
            representation['klass'] = str(instance.klass)
        return representation
    
    def validate_image(self, value):
        MAX_IMAGE_SIZE = 2 * 1024 * 1024 # 2MB
        print(value.size)
        if value.size > MAX_IMAGE_SIZE:
            raise ValidationError(f"Image size should not exceed {MAX_IMAGE_SIZE / (1024 * 1024)} MB.")
        return value


class KlassSerializer(serializers.ModelSerializer):
    institute = serializers.SlugRelatedField(slug_field='instu_id', queryset=Institute.objects.all(), allow_null=True)
    class Meta:
        model = Klass
        fields = '__all__'