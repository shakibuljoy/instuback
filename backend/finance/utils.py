from django.utils import timezone
from datetime import timedelta

def due_date_calucalator(due_type):
    today = timezone.now().date()
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
    return due_date
