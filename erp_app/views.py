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
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db.models import Q,Sum, Count
from datetime import datetime
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from django.utils.timezone import make_aware


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



# API to fetch the member latest milk pour and ther amount 

class MppCollectionAggregationListView(generics.ListAPIView):
    serializer_class = MppCollectionAggregationSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = MppCollectionAggregation.objects.all()
        member_code = self.request.query_params.get('member_code')
        year = self.request.query_params.get('year')

        if not member_code:
            return Response({
                "status": 200,
                "message": "success",
            }, status=status.HTTP_400_BAD_REQUEST)

        queryset = queryset.filter(member_code=member_code)

        if year:
            try:
                year = int(year)
                queryset = queryset.filter(
                    Q(from_date__year=year) | Q(to_date__year=year)
                )
            except ValueError:
                return Response({
                "status": 200,
                "message": "success",
            }, status=status.HTTP_400_BAD_REQUEST)


        return queryset

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                "status": 200,
                "message": "success",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({
                "status": 400,
                "message": str(e),
                "data": []
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": 500,
                "message": "An unexpected error occurred",
                "data": []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#  API to fetch member current date pouring detail and financial year detail

class MppCollectionDetailView(generics.GenericAPIView):
    serializer_class = MppCollectionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        today = timezone.now().date()
        member_code = request.query_params.get('member_code')
        financial_year = request.query_params.get('financial_year')
        
        if not member_code:
            return Response({
                "status": 400,
                "message": "member_code is required",
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        current_year = today.year
        current_month = today.month

        if financial_year:
            try:
                start_year = int(financial_year)
            except ValueError:
                return Response({
                    "status": 400,
                    "message": "financial_year must be a valid integer",
                    "data": {}
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            if current_month < 4:
                start_year = current_year - 1
            else:
                start_year = current_year

        start_date = make_aware(timezone.datetime(start_year, 4, 1))
        end_date = make_aware(timezone.datetime(start_year + 1, 3, 31, 23, 59, 59))

        # Filter for current date
        today_queryset = MppCollection.objects.filter(
            collection_date__date=today,
            member_code=member_code
        )
        # Aggregated data for financial year
        fy_queryset = MppCollection.objects.filter(
            collection_date__range=(start_date, end_date),
            member_code=member_code
        )
        fy_aggregated_data = fy_queryset.aggregate(
            total_days=Count('collection_date', distinct=True),
            total_qty=Sum('qty'),
            total_payment=Sum('amount')
        )

        today_serializer = self.get_serializer(today_queryset, many=True)

        response_data = {
            "status": 200,
            "message": "success",
            "data": {
                "current_date_data": today_serializer.data,
                "fy_data": fy_aggregated_data
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)
