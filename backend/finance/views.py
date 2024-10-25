from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework import viewsets
from base.permissions import IsAdministrator
from .models import Bill, Payment, Fee
from base.models import Student
from .serializers import FeeSerializer, BillSerializer, PaymentSerializer

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