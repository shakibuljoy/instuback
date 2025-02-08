from django.db import models
from base.models import Student, Institute
import uuid
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .utils import due_date_calucalator
from django.conf import settings

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
    trx_id = models.CharField(max_length=8, unique=True, verbose_name='Transaction ID', blank=True, default='', editable=False)
    bills = models.ManyToManyField(Bill, related_name='payments')
    mode = models.CharField(max_length=50, choices=(('cash', 'Cash'),('online', 'Online')))
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=30, choices=PAYMENT_CHOICES)
    epayment = models.OneToOneField('Epayment', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='payments_created', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='payments_updated', on_delete=models.SET_NULL, null=True, blank=True)

    def get_total_amount(self):
        total_amount = 0
        for bill in self.bills.all():
           total_amount += bill.get_payable_amount()
        return total_amount

    def save(self, *args, **kwargs):
        if not self.trx_id:
            self.trx_id = self._generate_unique_trx_id()

        # if not self.pk:
        #     self.created_by = kwargs.pop('user', None)
        # self.updated_by = kwargs.pop('user', None)
        super(Payment, self).save(*args, **kwargs)

    def _generate_unique_trx_id(self):
        while True:
            trx_id = uuid.uuid4().hex[:8].upper()
            if not Payment.objects.filter(trx_id=trx_id).exists():
                return trx_id
            

    def __str__(self):
        return f"{self.trx_id} - {self.status}"
    

class Epayment(models.Model):
    pg_service_charge_bdt = models.CharField(max_length=255, null=True, blank=True)
    amount_original = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    gateway_fee = models.CharField(max_length=255, null=True, blank=True)
    pg_service_charge_usd = models.CharField(max_length=255, null=True, blank=True)
    pg_card_bank_name = models.CharField(max_length=255, null=True, blank=True)
    pg_card_bank_country = models.CharField(max_length=255, null=True, blank=True)
    card_number = models.CharField(max_length=255, null=True, blank=True)
    card_holder = models.CharField(max_length=255, null=True, blank=True)
    status_code = models.IntegerField()
    pay_status = models.CharField(max_length=50)
    success_url = models.URLField(null=True, blank=True)
    fail_url = models.URLField(null=True, blank=True)
    cus_name = models.CharField(max_length=255, null=True, blank=True)
    cus_email = models.EmailField(null=True, blank=True)
    cus_phone = models.CharField(max_length=255, null=True, blank=True)
    currency_merchant = models.CharField(max_length=10, null=True, blank=True)
    convertion_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    other_currency = models.CharField(max_length=255, null=True, blank=True)
    pg_txnid = models.CharField(max_length=255, null=True, blank=True)
    epw_txnid = models.CharField(max_length=255, null=True, blank=True)
    mer_txnid = models.CharField(max_length=255, null=True, blank=True)
    store_id = models.CharField(max_length=255, null=True, blank=True)
    merchant_id = models.CharField(max_length=255, null=True, blank=True)
    currency = models.CharField(max_length=10, null=True, blank=True)
    store_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    pay_time = models.DateTimeField(null=True, blank=True)
    amount = models.CharField(max_length=255, null=True, blank=True)
    bank_txn = models.CharField(max_length=255, null=True, blank=True)
    card_type = models.CharField(max_length=255, null=True, blank=True)
    reason = models.CharField(max_length=255, null=True, blank=True)
    pg_card_risklevel = models.CharField(max_length=2, null=True, blank=True)
    pg_error_code_details = models.CharField(max_length=255, null=True, blank=True)
    opt_a = models.CharField(max_length=255, null=True, blank=True)
    opt_b = models.CharField(max_length=255, null=True, blank=True)
    opt_c = models.CharField(max_length=255, null=True, blank=True)
    opt_d = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Payment {self.pg_txnid} - {self.pay_status}"

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


def check_is_bill_paid(instance):
        if instance.status == 'success':
            for bill in instance.bills.all():
                bill.paid = True
                bill.save()
                

@receiver(m2m_changed, sender=Payment.bills.through)
def bill_marker_m2m_change(sender, instance, action,**kwargs):
    if action == 'post_add':
        check_is_bill_paid(instance)


@receiver(post_save, sender=Payment)
def bill_marker_post_save(sender, instance, created,**kwargs):
    if not created:
        check_is_bill_paid(instance)
        



