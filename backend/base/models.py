import uuid
from django.db import models
from users.models import CustomUser, Institute

class Klass(models.Model):
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    group = models.CharField(max_length=50, null=True, blank=True)
    branch = models.CharField(max_length=50, null=True, blank=True)
    teachers = models.ManyToManyField(CustomUser, related_name='teachers',blank=True)
    result_published = models.BooleanField(default=False)
    admission_open = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}{'-' + self.group if self.group else ''}{'-' + self.branch if self.branch else ''}"

class AdditionalStudentField(models.Model):
    FIELD_CHOICES =(
        ('number', 'Number'),
        ('text', 'Text'),
        ('file', 'File')
    
    )
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    field_type = models.CharField(max_length=50, choices=FIELD_CHOICES)
    required = models.BooleanField(default=False)

    class Meta:
        unique_together = ['institute', 'title']

    def __str__(self):
        return f"{self.institute.instu_id}-{self.title}"


GENDER_CHOICES = (
    ('Male', 'male'),
    ('Female', 'female'),
    ('Third-Gender', 'third-gender')
)

class Student(models.Model):
    def folder_convention(instance, filename):
        return f"profile/student/{instance.student_id}/{filename}"
    

    student_id = models.CharField(max_length=8, unique=True, blank=True, default='', editable=False)
    admission_date = models.DateField(auto_now_add=True)
    email = models.EmailField()
    klass = models.ForeignKey(Klass, on_delete=models.PROTECT, verbose_name="Class", blank=True, null=True)
    position = models.IntegerField(blank=True, null=True)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120, null=True, blank=True)
    gender = models.CharField(max_length=50,choices=GENDER_CHOICES, default='male')
    mobile = models.CharField(max_length=50)
    mothers_name = models.CharField(max_length=120)
    fathers_name = models.CharField(max_length=120)
    address = models.CharField(max_length=220)
    birth_date = models.DateField()
    birth_certificate_no = models.CharField(max_length=220)
    nid_no = models.CharField(max_length=220, null=True, blank=True)
    image = models.ImageField(upload_to=folder_convention, null=False, blank=False)
    active = models.BooleanField(default=False)
    admitted = models.BooleanField(default=False)
    account_created = models.BooleanField(default=False)
    banned_account = models.BooleanField(default=False)


    def _generate_unique_student_id(self):
        while True:
            student_id = uuid.uuid4().hex[:8].upper()
            if not Student.objects.filter(student_id=student_id).exists():
                return student_id
            
    def full_name(self):
        return f"{self.first_name} {self.last_name if self.last_name else ''}"
            
    def save(self,*args, **kwargs ):
        if not self.student_id:
            self.student_id=self._generate_unique_student_id()
        super(Student, self).save(*args, **kwargs)


    def __str__(self):
        return f"{self.first_name} {self.last_name if self.last_name else ''} ({self.student_id})"
    



class AdditionalStudentInfo(models.Model):
    def folder_convention(instance, filename):
        return f"document/student/{instance.student.id}/{filename}"


    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    field = models.ForeignKey(AdditionalStudentField, on_delete=models.CASCADE)
    value = models.CharField(max_length=512, blank=True, null=True)
    file = models.ImageField(upload_to=folder_convention, blank=True, null=True)

    def __str__(self):
        return f"{self.student.student_id}-{self.field.title}"
    
    def save(self, *args, **kwargs):
        if self.field.field_type == 'file' and not self.file:
            raise ValueError('Please Upload a File')
        elif self.field.field_type != 'file' and not self.value:
            raise ValueError('Please filled up the field')

        return super(AdditionalStudentInfo, self).save(*args, **kwargs)

    
    
    class Meta:
        unique_together = ['student', 'field']




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
    



    

class Subject(models.Model):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=50)
    klass = models.ForeignKey(Klass, on_delete=models.CASCADE)
    credit = models.FloatField()

    class Meta:
        unique_together = ['name', 'klass']

    def __str__(self):
        return f"{self.name} ({self.klass})"
    

class Mark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    mark = models.FloatField(blank=True, null=True)
    
    class Meta:
        unique_together = ['student', 'subject']


    def __str__(self):
        return f"{self.student.student_id}-{self.subject.name}"










