from django.db import models
from users.models import CustomUser, Institute

class Student(models.Model):
    def folder_convention(instance, filename):
        return f"profile/student/{instance.student_id}/{filename}"
    

    student_id = models.CharField(max_length=120)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120, null=True, blank=True)
    mobile = models.CharField(max_length=50)
    mothers_name = models.CharField(max_length=120)
    fathers_name = models.CharField(max_length=120)
    address = models.CharField(max_length=220)
    birth_date = models.DateField()
    birth_certificate_no = models.CharField(max_length=220)
    nid_no = models.CharField(max_length=220, null=True, blank=True)
    image = models.ImageField(upload_to=folder_convention)

class StudentDocument(models.Model):
    def folder_convention(instance, filename):
        return f"document/student/{instance.student.id}/{filename}"
    

    document_title = models.CharField(max_length=120)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=folder_convention)

class Klass(models.Model):
    name = models.CharField(max_length=50)
    group = models.CharField(max_length=50, null=True, blank=True)
    branch = models.CharField(max_length=50, null=True, blank=True)
    teachers = models.ManyToManyField(CustomUser, related_name='teacher')
    students = models.ManyToManyField(Student, related_name='student')

