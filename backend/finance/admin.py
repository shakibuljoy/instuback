from django.contrib import admin
from .models import Bill, Fee, Payment, FeeVersion, Epayment

class BillAdmin(admin.ModelAdmin):
    list_display = ('student','fee','paid', 'due_date', 'get_payable_amount')

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('trx_id', 'mode', 'paid_amount', 'status', 'created_by', 'updated_by')

    def save_model(self, request, obj, form, change):
        """
        This method is called when an object is saved in the admin panel.
        """
        if not change:  # if the object is being created for the first time
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Bill,BillAdmin)
admin.site.register(Fee)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(FeeVersion)
admin.site.register(Epayment)