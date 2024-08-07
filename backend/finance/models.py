from django.db import models
from base.models import Student, Institute
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta, datetime
from django.utils import timezone

DUE_TYPE_CHOICES = (
    ('daily', 'Daily'),
    ('weekly', 'Weekly'),
    ('monthly', 'Monthly'),
    ('quarterly', 'Quarterly'),
    ('half-yearly', 'Half-Yearly'),
    ('yearly', 'Yearly')
)

class Fee(models.Model):
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    description = models.CharField(max_length=550, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_type = models.CharField(max_length=120, choices=DUE_TYPE_CHOICES)
    active = models.BooleanField(default=True)
    required_for_all = models.BooleanField()

    def __str__(self):
        return f"{self.institute.instu_id}-{self.title}-{self.amount}"

class FeeVersion(models.Model):
    fee = models.ForeignKey(Fee, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.fee.title}-{self.amount}-{self.created_at}"

class Bill(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    fee = models.ForeignKey(FeeVersion, on_delete=models.PROTECT)
    paid = models.BooleanField(default=False)
    due_date = models.DateField()

    def __str__(self):
        return f"{self.student.first_name}-{self.fee.fee.title}-{self.fee.amount}"

PAYMENT_CHOICES = (
    ('pending', 'Pending'),
    ('success', 'Success'),
    ('fail', 'Fail'),
    ('hold', 'Hold')
)

class Payment(models.Model):
    trx_id = models.CharField(max_length=32, unique=True, verbose_name='Transaction ID', blank=True, default='')
    bills = models.ManyToManyField(Bill, related_name='bill')
    status = models.CharField(max_length=30, choices=PAYMENT_CHOICES)

    def save(self, *args, **kwargs):
        if not self.trx_id:
            self.trx_id = self._generate_unique_trx_id()
        super(Payment, self).save(*args, **kwargs)

    def _generate_unique_trx_id(self):
        while True:
            trx_id = uuid.uuid4().hex[:32].upper()
            if not Payment.objects.filter(trx_id=trx_id).exists():
                return trx_id

    def __str__(self):
        return f"Payment {self.trx_id} - {self.status}"

@receiver(post_save, sender=Fee)
def create_bills_for_fee(sender, instance, created, **kwargs):
    if created:
        # Firstly Create a initial version of a new Fee
        fee_version = FeeVersion.objects.create(fee=instance,amount=instance.amount)
        if instance.required_for_all:
            institute = fee_version.fee.institute
            due_type = fee_version.fee.due_type
            today = timezone.now().date()
            
            students = Student.objects.filter(institute=institute)

            for student in students:
                if due_type == 'daily':
                    due_date = today + timedelta(days=1)
                elif due_type == 'weekly':
                    due_date = today + timedelta(weeks=1)
                elif due_type == 'monthly':
                    due_date = today + timedelta(days=30)
                elif due_type == 'quarterly':
                    due_date = today + timedelta(weeks=13)
                elif due_type == 'half-yearly':
                    due_date = today + timedelta(weeks=26)
                elif due_type == 'yearly':
                    due_date = today + timedelta(weeks=52)
                else:
                    due_date = today

                Bill.objects.create(student=student, fee=fee_version, due_date=due_date)
    else: 
        prev_versions = FeeVersion.objects.filter(fee=instance)
        for fee_version in prev_versions:
            if fee_version.amount == instance.amount:
                return
            fee_version.active = False
            fee_version.save()

        FeeVersion.objects.create(fee=instance,amount=instance.amount)

        

@receiver(post_save, sender=Student)
def create_bills_for_new_student(sender, instance, created, **kwargs):
    if created:
        institute = instance.institute
        today = timezone.now().date()
        fees = FeeVersion.objects.filter(fee__institute=institute, fee__required_for_all=True, active=True)

        for fee in fees:
            if fee.fee.due_type == 'daily':
                due_date = today + timedelta(days=1)
            elif fee.fee.due_type == 'weekly':
                due_date = today + timedelta(weeks=1)
            elif fee.fee.due_type == 'monthly':
                due_date = today + timedelta(weeks=4)
            elif fee.fee.due_type == 'quarterly':
                due_date = today + timedelta(weeks=13)
            elif fee.fee.due_type == 'half-yearly':
                due_date = today + timedelta(weeks=26)
            elif fee.fee.due_type == 'yearly':
                due_date = today + timedelta(weeks=52)
            else:
                due_date = today

            Bill.objects.create(student=instance, fee=fee, due_date=due_date)


