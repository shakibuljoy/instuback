from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from base.permissions import IsAdministrator
from .models import Bill, Payment, Fee
from base.models import Student
from .serializers import FeeSerializer, BillSerializer, PaymentSerializer, EPaymentSerializer
from .aamarpay import aamarPay

class FeeView(viewsets.ModelViewSet):
    permission_classes =[IsAdministrator]
    serializer_class = FeeSerializer
    
    def get_queryset(self):
        queryset = Fee.objects.filter(institute=self.request.user.institute)
        return queryset
    
    def perform_create(self, serializer):
        return serializer.save(institute=self.request.user.institute)
    

    
    

class BillViewSet(viewsets.ModelViewSet):
    permission_classes =[IsAdministrator]
    serializer_class = BillSerializer

    def get_queryset(self):
        queryset = Bill.objects.filter(fee__fee__institute=self.request.user.institute)
        return queryset
    

    
    def perform_create(self, serializer):
        student_id = serializer['student']
        try:
            student = Student.objects.get(student_id) 
            if student.institute == self.request.user.institute:
                return super().perform_create(serializer)
            else:
                return Response({'detail':'Unauthorized action!'}, status=status.HTTP_401_UNAUTHORIZED)

        except Student.DoesNotExist:
            return Response({'detail':'Student Not Found!'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAdministrator])
def student_bills(request, pk):
    student = get_object_or_404(Student, pk=pk)
    bills = Bill.objects.filter(student=student)
    serializer = BillSerializer(bills, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes =[IsAdministrator]
    serializer_class = PaymentSerializer

    def get_queryset(self):
        queryset = Payment.objects.filter(bills__fee__fee__institute=self.request.user.institute)
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        # Get the payment by primary key
        payment = get_object_or_404(Payment, pk=kwargs['pk'])
        
        if payment.bills.filter(fee__fee__institute=self.request.user.institute).exists():
            serializer = self.get_serializer(payment)
            return Response(serializer.data)
        else:
            return Response({'detail': 'Payment not found or unauthorized'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.validated_data['created_by'] = request.user
            # Custom validation and logic before saving
            bills = serializer.validated_data['bills']
            is_paid_amount = serializer.validated_data.get('paid_amount')
            total_amount = 0

            for bill in bills:
                total_amount += bill.get_payable_amount()
                
                if bill.student.institute != self.request.user.institute:
                    return Response({'detail': 'Unauthorized action!'}, status=status.HTTP_401_UNAUTHORIZED)
                
                if bill.paid:
                    return Response({'detail': "Paid bill is not payable"}, status=status.HTTP_406_NOT_ACCEPTABLE)

            if is_paid_amount:
                paid_amount = serializer.validated_data['paid_amount']
                if paid_amount > 0 and paid_amount < total_amount:
                    serializer.validated_data['status'] = 'hold'
            else:
                serializer.validated_data['status'] = 'failed'
            # If everything is fine, proceed with the object creation
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)



@api_view(['GET'])
@permission_classes([IsAdministrator])
def payment_created_by_user(request):
    payment_list = Payment.objects.filter(created_by=request.user)

    serializer = PaymentSerializer(payment_list, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# @api_view(['POST'])
def online_payment(trx_id):
    # trx_id = request.data.get('trx_id')
    if trx_id:
        try:
            payment = Payment.objects.get(trx_id=trx_id)
            if payment.status == 'hold' and payment.mode == 'online':
                student = payment.bills.first().student
                initiate_payment = aamarPay(
                    transactionID=payment.trx_id, 
                    transactionAmount=payment.get_total_amount(),
                    description=', '.join([bill.fee.fee.title for bill in payment.bills.all()]),

                    customerName=student.full_name(), 
                    customerEmail=student.email, 
                    customerMobile=student.mobile, customerAddress1=student.address
                )
                payment_url = initiate_payment.payment()
                if str(payment_url).startswith('https://'):
                    return Response({'payment_url': payment_url}, status=status.HTTP_200_OK)
                else:
                    return Response({'detail': payment_url}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': 'Payment status not valid for Procced online payment'}, status=status.HTTP_400_BAD_REQUEST)
        except Payment.DoesNotExist:
            return Response({'detail': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'detail': 'trx_id is required'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def inititate_payment(request):
    data = request.data
    if not data:
        return Response({'detail': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)
    data['created_by'] = request.user.id
    data['mode'] = 'online'
    data['status'] = 'hold'
    data['paid_amount'] = 0
    serializer = PaymentSerializer(data=data)
    
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        bills = serializer.validated_data['bills']

        for bill in bills:
            if bill.paid:
                return Response({'detail': "Paid bill is not payable"}, status=status.HTTP_406_NOT_ACCEPTABLE)

        return online_payment(serializer.data.get('trx_id'))
    else:
        return Response({'detail': 'Invalid data', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

from  . import  _constants as constants

@api_view(['POST'])
def success_url(request):
    data = request.data
    if not data:
        frontend_success_url = f"{constants.frontUrl}/?detail=Something went wrong"
        return HttpResponseRedirect(frontend_success_url)

    # Validate and save payment data
    serializer = EPaymentSerializer(data=data)
    if serializer.is_valid():
        instance = serializer.save()
    else:
        frontend_success_url = f"{constants.frontUrl}/?detail=Something went wrong"
        return HttpResponseRedirect(frontend_success_url)
        # return Response({'detail': 'Invalid data', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    # Process the payment if status is Successful
    if data.get('pay_status') == "Successful":
        try:
            # Fetch payment by transaction ID
            payment = Payment.objects.get(trx_id=data.get('mer_txnid'))
            
            # Validate payment amount
            if payment.get_total_amount() <= float(data.get('amount', 0)):
                # Verify transaction with aamarPay
                initiate_verification = aamarPay()
                response = initiate_verification.check_transaction(data.get('mer_txnid'))
                
                # Ensure response is a valid dictionary
                if isinstance(response, dict):
                    charge_amount = float(response.get('processing_charge', 0))
                    received_amount = float(response.get('rec_amount', 0))
                    total_amount_paid = charge_amount + received_amount
                    actual_amount = total_amount_paid == float(data.get('amount', 0))
                    if response.get('status_code') == '2' and actual_amount:
                        # Mark payment as successful
                        payment.status = 'success'
                        payment.mode = 'online'
                        payment.paid_amount = total_amount_paid
                        payment.epayment = instance
                        payment.save()
                        frontend_success_url = f"{constants.frontUrl}/?trx_id={payment.trx_id}&amount={total_amount_paid}&status=success&detail=Successfully paid {total_amount_paid}"
                        return HttpResponseRedirect(frontend_success_url)
                        # return Response({'detail': f"Successfully paid {response['rec_amount']}"}, status=status.HTTP_200_OK)
                    elif response.get('status_code') == '2':
                        payment.status = 'pending'
                        payment.mode = 'online'
                        payment.paid_amount = total_amount_paid
                        payment.epayment = instance
                        payment.save()
                        frontend_success_url = f"{constants.frontUrl}/?trx_id={payment.trx_id}&amount={total_amount_paid}&status=pending&detail=Payment verification pending"
                        return HttpResponseRedirect(frontend_success_url)
                        # return Response({'detail': 'Payment verification pending'}, status=status.HTTP_200_OK)
                    else:
                        payment.status = 'failed'
                        payment.mode = 'online'
                        payment.paid_amount = total_amount_paid
                        payment.epayment = instance
                        payment.save()
                        frontend_success_url = f"{constants.frontUrl}/?trx_id={payment.trx_id}&amount={payment.get_total_amount()}&status=failed&detail=Payment verification failed"
                        return HttpResponseRedirect(frontend_success_url)
                        # return Response({'detail': 'Payment verification failed'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    frontend_success_url = f"{constants.frontUrl}/?trx_id={payment.trx_id}&amount={payment.get_total_amount()}&status=failed&detail=Invalid verification response"
                    return HttpResponseRedirect(frontend_success_url)
                    # return Response({'detail': 'Invalid verification response'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                frontend_success_url = f"{constants.frontUrl}/?trx_id={payment.trx_id}&amount={payment.get_total_amount()}&status=failed&detail=Invalid amount"
                return HttpResponseRedirect(frontend_success_url)
                # return Response({'detail': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)
        except Payment.DoesNotExist:
            frontend_success_url = f"{constants.frontUrl}/?detail=Payment not found"
            return HttpResponseRedirect(frontend_success_url)
            # return Response({'detail': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            frontend_success_url = f"{constants.frontUrl}/?detail=Something went wrong"
            return HttpResponseRedirect(frontend_success_url)
            # return Response({'detail': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Default response for non-successful payments
    frontend_success_url = f"{constants.frontUrl}/?trx_id={data.get('mer_txnid')}&amount={data.get('amount')}&status=failed&detail=Invalid Payement"
    return HttpResponseRedirect(frontend_success_url)


@api_view(['POST', 'GET'])
def cancel_url(request):
    if request.method == 'GET':
        frontend_success_url = f"{constants.frontUrl}/?detail=Payment Cencelled"
        return HttpResponseRedirect(frontend_success_url)
    data = request.data
    
    if not data:
        frontend_success_url = f"{constants.frontUrl}/?detail=Something went wrong"
        return HttpResponseRedirect(frontend_success_url)
    serializer = EPaymentSerializer(data=data)
    if serializer.is_valid():
        instance = serializer.save()
        if data.get('pay_status') == "Failed":
            try:
                payment = Payment.objects.get(trx_id=data.get('mer_txnid'))
                payment.status = 'failed'
                payment.mode = 'online'
                payment.paid_amount = 0
                payment.epayment = instance
                payment.save()
                frontend_success_url = f"{constants.frontUrl}/?detail=Payment Failed"
                return HttpResponseRedirect(frontend_success_url)
            except Payment.DoesNotExist:
                frontend_success_url = f"{constants.frontUrl}/?detail=Payment Failed"
                return HttpResponseRedirect(frontend_success_url)
        frontend_success_url = f"{constants.frontUrl}/?detail=Payment Cencelled"
        return HttpResponseRedirect(frontend_success_url)




