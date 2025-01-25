from rest_framework import serializers
from .models import Student,Institute, Klass, Attendence, AdditionalStudentField, AdditionalStudentInfo, Subject, Mark
from django.db import IntegrityError
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
        
class AdditionalStFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalStudentField
        fields = '__all__'


    
class AdditionalStInfoSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(slug_field='title',read_only=True, source='field')
    field_id = serializers.PrimaryKeyRelatedField(many=False, queryset=AdditionalStudentField.objects.all(), source='field')
    student_id = serializers.PrimaryKeyRelatedField(many=False, queryset=Student.objects.all(), source='student')
    class Meta:
        model = AdditionalStudentInfo
        fields = ['id', 'title', 'field_id', 'value', 'student_id', 'file']

    def validate(self, data):
        student = data.get('student')
        field = data.get('field')

        if AdditionalStudentInfo.objects.filter(student=student, field=field).exists():
            raise serializers.ValidationError(
                f"An entry for the student {student.student_id} with the field '{field.title}' already exists."
            )
        return data
    

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class MarkSerializer(serializers.ModelSerializer):
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    subject_title = serializers.CharField(source='subject.name', read_only=True)
    subject_credit = serializers.CharField(source='subject.credit', read_only=True)
    print("Serializer")

    class Meta:
        model = Mark
        fields = '__all__'

        
    def validate(self, data):
        student = data.get('student')
        subject = data.get('subject')
        if Mark.objects.filter(student=student, subject=subject).exists():
            raise serializers.ValidationError(
                f"An entry for the student {student.student_id} with the subject '{subject.name}' already exists."
            )
        return data