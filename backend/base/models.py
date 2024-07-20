from django.db import models
from users.models import CustomUser, Institute

class Klass(models.Model):
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    group = models.CharField(max_length=50, null=True, blank=True)
    branch = models.CharField(max_length=50, null=True, blank=True)
    teachers = models.ManyToManyField(CustomUser, related_name='teachers',blank=True)

    def __str__(self):
        return f"{self.name}{"-"+ self.group if self.group else ""}{"-"+self.branch if self.branch else ""}"



class Student(models.Model):
    def folder_convention(instance, filename):
        return f"profile/student/{instance.student_id}/{filename}"
    

    student_id = models.CharField(max_length=120)
    admission_date = models.DateField(auto_now_add=True)
    klass = models.ForeignKey(Klass, on_delete=models.PROTECT, verbose_name="Class")
    position = models.IntegerField(blank=True, null=True)
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
    image = models.ImageField(upload_to=folder_convention, null=False, blank=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name if self.last_name else ""} ({self.student_id})"

class StudentDocument(models.Model):
    def folder_convention(instance, filename):
        return f"document/student/{instance.student.id}/{filename}"
    

    document_title = models.CharField(max_length=120)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=folder_convention)



class Attendence(models.Model):
    date = models.DateField(auto_now_add=True, editable=False)
    teacher = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    klass = models.ForeignKey(Klass, on_delete=models.CASCADE)
    presents = models.BooleanField()
    cause = models.CharField(max_length=220, null=True, blank=True)

    class Meta:
        unique_together = ['date', 'student', 'klass']

    def __str__(self):
        return f"{self.klass}-{self.student.student_id} ({self.date})"

