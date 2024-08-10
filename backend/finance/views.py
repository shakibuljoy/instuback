from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
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

        

class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes =[IsAdministrator]
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_queryset(self):
        queryset = Payment.objects.filter(bills__fee__fee__institute=self.request.user.institute)
        return queryset

    def perform_create(self, serializer):
        bills = serializer.validated_data['bills']
        for bill in bills:
            if bill.student.institute != self.request.user.institute:
                return Response({'detail':'Unauthorized action!'}, status=status.HTTP_401_UNAUTHORIZED)
        super().perform_create(serializer)