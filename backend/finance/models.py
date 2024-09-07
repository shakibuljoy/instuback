from django.db import models
from base.models import Student, Institute
import uuid
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .utils import due_date_calucalator

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
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    due_date = models.DateField()

    def __str__(self):
        return f"{self.student.first_name}-{self.fee.fee.title}-{self.fee.amount}"
    
    def get_payable_amount(self):
        bill_amount = self.fee.amount - self.discount
        return bill_amount
    

PAYMENT_CHOICES = (
    ('pending', 'Pending'),
    ('success', 'Success'),
    ('failed', 'Failed'),
    ('hold', 'Hold')
)

class Payment(models.Model):
    trx_id = models.CharField(max_length=32, unique=True, verbose_name='Transaction ID', blank=True, default='', editable=False)
    bills = models.ManyToManyField(Bill, related_name='payments')
    mode = models.CharField(max_length=50, choices=(('cash', 'Cash'),('online', 'Online')))
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=30, choices=PAYMENT_CHOICES)

    def get_total_amount(self):
        total_amount = 0
        for bill in self.bills.all():
           total_amount += bill.get_payable_amount()
        return total_amount

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
        return f"{self.trx_id} - {self.status}"

@receiver(post_save, sender=Fee)
def create_bills_for_fee(sender, instance, created, **kwargs):
    if created:
        # Firstly Create a initial version of a new Fee
        fee_version = FeeVersion.objects.create(fee=instance,amount=instance.amount)
        if instance.required_for_all:
            institute = fee_version.fee.institute
            due_type = fee_version.fee.due_type
            
            students = Student.objects.filter(institute=institute)

            for student in students:
                Bill.objects.create(student=student, fee=fee_version, due_date=due_date_calucalator(due_type))
    else: 
        prev_versions = FeeVersion.objects.filter(fee=instance)
        for fee_version in prev_versions:
            if fee_version.amount == instance.amount:
                # If save() initiated without changing amount then return
                return
            fee_version.active = False
            fee_version.save()

        FeeVersion.objects.create(fee=instance,amount=instance.amount)

        

@receiver(post_save, sender=Student)
def create_bills_for_new_student(sender, instance, created, **kwargs):
    if created:
        institute = instance.institute
        fees = FeeVersion.objects.filter(fee__institute=institute, fee__required_for_all=True, active=True)

        for fee in fees:
            Bill.objects.create(student=instance, fee=fee, due_date=due_date_calucalator(fee.fee.due_type))


@receiver(m2m_changed, sender=Payment.bills.through)
def check_is_bill_paid(sender, instance, action,**kwargs):
    if action == 'post_add':
        print(" M@M Signal is triggered")
        if instance.status == 'success':
            print("Signal is triggered in Success", instance)
            
            for bill in instance.bills.all():
                print("Signal is triggered in Success in For loop", instance)
                
                bill.paid = True
                print("from signal",bill.paid)
                bill.save()


@receiver(post_save, sender=Payment)
def check_is_bill_paid(sender, instance, created,**kwargs):
    if not created:
        print(" Post Signal is triggered")
        if instance.status == 'success':
            print("Signal is triggered in Success", instance)
            payment_instance = Payment.objects.get(pk=instance.id)
            print(payment_instance)
            for bill in payment_instance.bills.all():
                print("Signal is triggered in Success in For loop", payment_instance)
                
                bill.paid = True
                print("from signal",bill.paid)
                bill.save()
        


