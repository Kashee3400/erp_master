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
from django.db.models import Q,Sum, Count,Avg,Max
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


class BillingMemberDetailView(generics.RetrieveAPIView):
    """
    Retrieve view for billing member details.

    This view retrieves the billing member details, including master and local sales information, 
    based on the provided member code. It ensures the member exists and fetches associated 
    billing master and local sale transactions.
    """
    serializer_class = BillingMemberDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_fy_dates(self, fy=None):
        """
        Calculates the start and end dates of the financial year.

        Args:
            fy (str): The financial year in 'YYYY-YYYY' format.

        Returns:
            tuple: A tuple containing the start and end dates of the financial year.
        """
        if fy:
            start_year = int(fy.split('-')[0])
        else:
            today = datetime.today()
            if today.month >= 4:
                start_year = today.year
            else:
                start_year = today.year - 1

        start_date = datetime(start_year, 4, 1)
        end_date = datetime(start_year + 1, 3, 31)
        return start_date, end_date

    def get_objects(self):
        """
        Retrieves billing member details using the member code from the URL.

        Returns:
            QuerySet: A queryset of BillingMemberDetail objects filtered by the member code.
        """
        member_code = self.kwargs['member_code']
        # fy = self.kwargs['fy']
        fy = self.request.query_params.get('fy')
        start_date, end_date = self.get_fy_dates(fy)
        return BillingMemberDetail.objects.using('sarthak_kashee').filter(
            member_code=member_code,
          transaction_date__range=[start_date, end_date]
        )

    def retrieve(self, request, *args, **kwargs):
        """
        Handles GET requests to retrieve detailed billing member information.

        If the member exists, it gathers the billing master, local sales, and local sale transactions 
        within the specified date range. If the member does not exist, it returns a 404 response.

        Args:
            request (Request): The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A response containing the billing member details and related information.
        """
        instances = self.get_objects()
        if not instances.exists():
            response = {
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'No member found with this member code',
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        
        detailed_data = []

        for instance in instances:
            serializer = self.get_serializer(instance)
            billing_master = None
            local_sale_txns = []

            if BillingMemberMaster.objects.using('sarthak_kashee').filter(billing_member_master_code=instance.billing_member_master_code.billing_member_master_code).exists():
                billing_master_instance = BillingMemberMaster.objects.using('sarthak_kashee').get(billing_member_master_code=instance.billing_member_master_code.billing_member_master_code)
                from_date = billing_master_instance.from_date
                to_date = billing_master_instance.to_date

                local_sales_queryset = LocalSale.objects.using('sarthak_kashee').filter(
                    module_code=instance.member_code,
                   installment_start_date__range=[from_date, to_date]
                )
                for local_sale in local_sales_queryset:
                    local_sale_txns_queryset = local_sale.local_sale_txn.all()
                    local_sale_txns.extend(LocalSaleTxnSerializer(local_sale_txns_queryset, many=True).data)

            detailed_data.append({
                'details': serializer.data,
                'local_sale_txns': local_sale_txns,
            })

        response = {
            'status': status.HTTP_200_OK,
            'message': 'Success',
            'data': detailed_data,
        }
        return Response(response)


# API to fetch the member latest milk pour and ther amount 
from django.db.models.functions import Cast
from django.db.models import Subquery, OuterRef

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
                start_date = f"{year}-04-01"    
                end_date = f"{year + 1}-03-31"
                queryset = queryset.filter(
                    Q(from_date__gte=start_date, from_date__lte=end_date) |
                    Q(to_date__gte=start_date, to_date__lte=end_date) |
                    Q(from_date__lte=start_date, to_date__gte=end_date)
                )
            except ValueError:
                return Response({
                    "status": 400,
                    "message": "Invalid year provided.",
                }, status=status.HTTP_400_BAD_REQUEST)

        return queryset

    def list(self, request, *args, **kwargs):
        try:
           
            queryset = self.get_queryset()
            duplicate_count = queryset.values('from_date', 'to_date').annotate(count=Count('id')).filter(count__gt=1).count()
            total_pouring_days = (Sum('no_of_pouring_days')-duplicate_count)
            totals = queryset.aggregate(
                total_qty=Sum('qty'),
                avg_fat=Cast(Avg('fat'), output_field=models.DecimalField(decimal_places=3, max_digits=18)),
                avg_snf=Cast(Avg('snf'), output_field=models.DecimalField(decimal_places=3, max_digits=18)),
                total_amount=Sum('amount'),
                total_days=total_pouring_days,
                total_shift=total_pouring_days*2,
            )
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                "status": 200,
                "message": "success",
                'totals':totals,
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
                "message": f"An unexpected error occurred,{str(e)}",
                "data": []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#  API for Dashboard to fetch member current date pouring detail and financial year detail

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

