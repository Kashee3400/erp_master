from datetime import timedelta
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import *
from .serializers import *
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
import requests


class MemberByPhoneNumberView(generics.RetrieveAPIView):
    serializer_class = MemberMasterSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        phone_number = self.kwargs['phone_number']
        try:
            return MemberMaster.objects.using('sarthak_kashee').get(mobile_no=phone_number)
        except MemberMaster.DoesNotExist:
            return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return Response({'error': 'No member found with this phone number'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        response = {
            'status':status.HTTP_200_OK,
            'messafe':'Success',
            'data':serializer.data
        }
        return Response(response)
    
    
class BillingMemberDetailHistoryView(generics.RetrieveAPIView):
    serializer_class = BillingMemberDetailHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        member_code = self.kwargs['member_code']
        try:
            return BillingMemberDetailHistory.objects.using('sarthak_kashee').get(member_code=member_code)
        except BillingMemberDetailHistory.DoesNotExist:
            
            return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            response = {
            'status':status.HTTP_400_BAD_REQUEST,
            'messafe':'No member found with this member code',
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        response = {
            'status':status.HTTP_200_OK,
            'messafe':'Success',
            'data':serializer.data
        }
        return Response(response)

