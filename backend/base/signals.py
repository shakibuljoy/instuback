from users.models import CustomUser
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Student, Attendence
from .mailsender import mail_sender




'''
Signal for updating banned_account in Student
'''
@receiver(post_save, sender=Student)
def banned_account(sender, instance, created, **kwargs):
    print("Banned Account inititated")
    if not created:
        
        try:
            account = CustomUser.objects.get(student = instance)
            if instance.banned_account:
                account.is_active = False
                account.save()
            else:
                account.is_active = True
                account.save()
        except Exception as e:
            pass



'''
Attendance signal fo mailing the parents
'''

@receiver(post_save, sender=Attendence)
def mail_parents(sender, instance, created, **kwargs):
    if created:
        student = instance.student
        subject = f"Attendance of {student.full_name()} on {instance.date}"
        message = f"Dear Parents, Your child {student.full_name()} was { 'present' if instance.presents else 'absent'} on {instance.date}."
        mail_sender(subject, message, student.email)
    else:
        student = instance.student
        subject = f"Updated Attendance of {student.full_name()} on {instance.date}"
        message = f"Dear Parents, Your child {student.full_name()} was { 'present' if instance.presents else 'absent'} on {instance.date}{ "cause: "+ instance.cause if instance.cause else ""}."
        mail_sender(subject, message, student.email)
        
