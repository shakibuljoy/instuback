from rest_framework import serializers
from .models import Student
from django.urls import reverse


class StudentSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = Student
        fields = '__all__'

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(reverse('base:retrieve_student_image', kwargs={'pk': obj.pk}))
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if instance.image and request:
            representation['image'] = request.build_absolute_uri(reverse('base:retrieve_student_image', kwargs={'pk': instance.pk}))
        return representation
