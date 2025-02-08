from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError


def institute_photo_upload_path(instance, filename):
    return f'public/institute/{instance.instu_id}/{filename}'

# Model creation started  
class Institute(models.Model):
    INSTITUTE_TYPE = (
        ('school', 'School'),
        ('college', 'College'),
        ('training_center','Training Center'),
        ('university', 'University'),
        ('polytechnic', 'Polytechnic'),
        ('madrashah', 'Madrashah'),
        ('coaching', 'Coaching')
    )
    instu_id = models.CharField(
        max_length=150,
        unique=True,
        help_text='Required. 150 characters of fewer. Letters, digits only',
        validators=[UnicodeUsernameValidator],
        error_messages={
            'unique': "A institute with this ID already exists."
        }
        )
    
    name = models.CharField(max_length=150)
    eiin = models.CharField(max_length=150, verbose_name='EIIN', blank=True, null=True)
    address = models.CharField(max_length=240)
    instititute_photo = models.ImageField(upload_to=institute_photo_upload_path, null=True, blank=True)
    institute_type = models.CharField(max_length=50, choices=INSTITUTE_TYPE),
    residential = models.BooleanField()


    def __str__(self):
        return self.instu_id



class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username.strip(), email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(username, email, password, **extra_fields)
        

# Validators
# Validating if user is a developer no need Institution.
def validate_institute_for_user_type(self):
    if self.user_type != 'developer' and not self.institute:
        raise ValidationError('Institute is required for non-developer users.')
    if self.user_type == 'student' and (not self.student):
        raise ValidationError('An student data must be associated with a student account')
         
class CustomUser(AbstractUser):
    
        
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('administrator','Administrator'),
        ('developer', 'Developer')
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey('base.Student', on_delete=models.CASCADE, null=True, blank=True)

    profile_pic = models.ImageField(upload_to=f"profile/", verbose_name='Profile Picture', null=True, blank=True)

    def is_student(self):
        return self.user_type == 'student'
    
    def is_teacher(self):
        return self.user_type == 'teacher'
    
    def is_administrator(self):
        return self.user_type == 'administrator'
    
    def is_developer(self):
        return self.user_type == 'developer'
    
    def clean(self):
        validate_institute_for_user_type(self)
        super().clean()
    
    objects = CustomUserManager()


