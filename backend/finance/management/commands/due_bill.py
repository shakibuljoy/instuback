# management/commands/create_new_bills.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from finance.models import Bill

class Command(BaseCommand):
    help = 'Creates new bills for expired due dates'

    def bill_creator(self, bill):
        if bill.fee.fee.due_type == 'monthly':
            new_due_date = bill.due_date + timedelta(days=30)
        elif bill.fee.fee.due_type == 'quarterly':
            new_due_date = bill.due_date + timedelta(days=90)
        elif bill.fee.fee.due_type == 'yearly':
            new_due_date = bill.due_date + timedelta(days=365)
        else:
            new_due_date = bill.due_date

        Bill.objects.create(
            student=bill.student,
            fee=bill.fee,
            due_date=new_due_date,
            discount=bill.discount,
        )
        self.stdout.write(self.style.SUCCESS(f'Created new bill for {bill.student.first_name}'))

    def handle(self, *args, **kwargs):
        expired_bills = Bill.objects.filter(due_date__lt=timezone.now().date())
        for bill in expired_bills:
            self.bill_creator(bill)

            
            