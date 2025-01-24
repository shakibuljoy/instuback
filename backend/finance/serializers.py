from rest_framework import serializers
from .models import Fee, Bill, Payment, Epayment
from rest_framework.exceptions import ValidationError

class FeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fee
        fields = '__all__'

class BillSerializer(serializers.ModelSerializer):
    fee_title = serializers.CharField(source='fee.fee.title', read_only=True)
    fee_amount = serializers.DecimalField(source='fee.amount', max_digits=12, decimal_places=2, read_only=True)
    trx = serializers.SerializerMethodField()

    class Meta:
        model = Bill
        fields = ['id', 'student', 'fee', 'fee_title', 'fee_amount', 'paid', 'due_date', 'discount', 'get_payable_amount', 'trx']

    def get_trx(self, value):
        return
    
    def to_representation(self, instance):
        represents =  super().to_representation(instance)
        try:
            payment = Payment.objects.get(bills=instance)
            represents['trx'] = payment.trx_id
        except Payment.DoesNotExist:
            instance.paid = False
            instance.save()
            represents['trx'] = ''
        return represents


class PaymentSerializer(serializers.ModelSerializer):
    bill_ids= serializers.PrimaryKeyRelatedField(many=True,queryset=Bill.objects.all(), source='bills')
    

    class Meta:
        model = Payment
        fields = ['id', 'trx_id','bill_ids', 'status','paid_amount', 'get_total_amount', 'mode', 'created_at','created_by', 'updated_by']


class EPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Epayment
        fields = '__all__'