from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from base.permissions import IsAdministrator
from .serializers import FeeSerializer

class FeeView(ModelViewSet):
    permission_classes =[IsAdministrator]
    serializer_class = FeeSerializer
