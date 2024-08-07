# management/commands/generate_bills.py
from django.core.management.base import BaseCommand
from base.models import Bill
from datetime import timedelta, datetime
from django.utils import timezone

class Command(BaseCommand):
    help = 'Generate new bills based on due dates'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        bills = Bill.objects.filter(due_date=today)

        for bill in bills:
            fee = bill.fee
            student = bill.student

            if fee.due_type == 'daily':
                new_due_date = today + timedelta(days=1)
            elif fee.due_type == 'weekly':
                new_due_date = today + timedelta(weeks=1)
            elif fee.due_type == 'monthly':
                new_due_date = today + timedelta(days=30)
            elif fee.due_type == 'quarterly':
                new_due_date = today + timedelta(weeks=13)
            elif fee.due_type == 'half-yearly':
                new_due_date = today + timedelta(weeks=26)
            elif fee.due_type == 'yearly':
                new_due_date = today + timedelta(weeks=52)
            else:
                new_due_date = today

            Bill.objects.create(student=student, fee=fee, due_date=new_due_date)
            self.stdout.write(self.style.SUCCESS(f'Created new bill for {student} with due date {new_due_date}'))

