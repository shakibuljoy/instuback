from django.contrib import admin
from .models import Bill, Fee, Payment, FeeVersion

admin.site.register(Bill)
admin.site.register(Fee)
admin.site.register(Payment)
admin.site.register(FeeVersion)