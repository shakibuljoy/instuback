from rest_framework import serializers
from .models import Fee, Bill, Payment

class FeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fee
        fields = '__all__'

class BillSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.first_name', read_only=True)
    fee_title = serializers.CharField(source='fee.fee.title', read_only=True)
    fee_amount = serializers.DecimalField(source='fee.amount', max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Bill
        fields = ['id', 'student', 'student_name', 'fee', 'fee_title', 'fee_amount', 'paid', 'due_date', 'discount', 'get_payable_amount']

class PaymentSerializer(serializers.ModelSerializer):
    bill_ids = serializers.PrimaryKeyRelatedField(many=True, queryset=Bill.objects.all(), source='bills')
    

    class Meta:
        model = Payment
        fields = ['id', 'trx_id', 'bill_ids', 'status','paid_amount', 'get_total_amount']