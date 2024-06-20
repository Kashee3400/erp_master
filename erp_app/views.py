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
from django.utils.translation import gettext_lazy as _


# class MemberByPhoneNumberView(generics.RetrieveAPIView):
#     serializer_class = MemberMasterSerializer
#     permission_classes = [IsAuthenticated]

#     def get_object(self):
#         phone_number = self.request.user.username
#         try:
#             return MemberMaster.objects.using('sarthak_kashee').get(mobile_no=phone_number)
#         except MemberMaster.DoesNotExist:
#             return None

#     def retrieve(self, request, *args, **kwargs):
#         instance = self.get_object()
#         if instance is None:
#             return Response(
#                 {
#                     'status':status.HTTP_404_NOT_FOUND,
#                     'message':'No Data Found'
#                 },
#                 status=status.HTTP_404_NOT_FOUND
#             )
#         serializer = self.get_serializer(instance)
        
#         response = {
#             'status':status.HTTP_200_OK,
#             'messafe':'Success',
#             'data':serializer.data
#         }
#         return Response(response)


class MemberByPhoneNumberView(generics.RetrieveAPIView):
    serializer_class = MemberMasterSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        phone_number = self.request.user.username
        try:
            return MemberMaster.objects.using('sarthak_kashee').get(mobile_no=phone_number)
        except MemberMaster.DoesNotExist:
            return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return Response(
                {
                    'status': status.HTTP_404_NOT_FOUND,
                    'message': 'No Data Found'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # Serialize MemberMaster data
        member_serializer = self.get_serializer(instance)

        # Fetch and serialize related MppCollectionAggregation data
        mpp_aggregations = MppCollectionAggregation.objects.filter(member_code=instance.member_code).first()
        mpp = Mpp.objects.filter(mpp_code=mpp_aggregations.mpp_code).first()
        mcc = Mcc.objects.filter(mcc_code=mpp_aggregations.mcc_code).first()

        # Prepare response
        response_data = member_serializer.data
        response_data['mcc_code'] = mcc.mcc_ex_code
        response_data['mcc_name'] = mcc.mcc_name
        response_data['mcc_tr_code'] = mcc.mcc_code

        response_data['mpp_name'] = mpp.mpp_name
        response_data['mpp_code'] = mpp.mpp_ex_code
        response_data['mpp_tr_code'] = mpp.mpp_code.mpp_tr_code

        response_data['company_code'] = mpp_aggregations.company_code
        response_data['company_name'] = mpp_aggregations.company_name
        response_data['member_tr_code'] = mpp_aggregations.member_tr_code
        
        member_fee_info = MemberFeeInfo.objects.filter(member_code=instance.member_code).first()

        response_data['bank'] = member_fee_info.bank_ref_no
        response_data['bank_branch'] = member_fee_info.branch_code
        response_data['account_no'] = member_fee_info.payment_mode
        response_data['ifsc'] = member_fee_info.ifsc

        response = {
            'status': status.HTTP_200_OK,
            'message': 'Success',
            'data': response_data
        }
        return Response(response)


from django.utils.dateparse import parse_datetime

class BillingMemberDetailView(generics.RetrieveAPIView):
    """
    Retrieve view for billing member details.

    This view retrieves the billing member details, including master and local sales information, 
    based on the provided member code. It ensures the member exists and fetches associated 
    billing master and local sale transactions.
    """
    serializer_class = BillingMemberDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_objects(self):
        """
        Retrieves billing member details using the member code from the URL.

        Returns:
            QuerySet: A queryset of BillingMemberDetail objects filtered by the member code.
        """
        if not MemberMaster.objects.filter(mobile_no=self.request.user.username).exists():
            return Response({
                "status": 400,
                "message": _(f"No member found on this mobile no {self.request.user.username}"),
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)
        member = MemberMaster.objects.get(mobile_no=self.request.user.username)
        from_date_str = self.request.query_params.get('from_date')
        to_date_str = self.request.query_params.get('to_date')
        
        from_date = parse_datetime(from_date_str)
        to_date = parse_datetime(to_date_str)
        
         # Filter the BillingMemberMaster objects
        billing_member_master_qs = BillingMemberMaster.objects.filter(from_date__lte=to_date, to_date__gte=from_date)
        
        # Get the related BillingMemberDetail objects
        billing_member_details = BillingMemberDetail.objects.using('sarthak_kashee').filter( member_code=member.member_code,billing_member_master_code__in=billing_member_master_qs)
        return billing_member_details

    def retrieve(self, request, *args, **kwargs):

        instances = self.get_objects()
        if not instances:
            response = {
                'status': status.HTTP_404_NOT_FOUND,
                'message': _('No Data Found'),
                
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        
        detailed_data = []

        for instance in instances:
            serializer = self.get_serializer(instance)
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
from rest_framework.pagination import PageNumberPagination

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 20  # Default page size
    page_size_query_param = 'page_size'  # Query parameter to dynamically set page size
    max_page_size = 100  # Maximum page size


class MppCollectionAggregationListView(generics.ListAPIView):
    '''
    This class provides the latest payments of cycle
    '''
    serializer_class = MppCollectionAggregationSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        queryset = MppCollectionAggregation.objects.all()
        
        if not MemberMaster.objects.filter(mobile_no=self.request.user.username).exists():
            return MppCollectionAggregation.objects.none()

        member = MemberMaster.objects.get(mobile_no=self.request.user.username)
        year = self.request.query_params.get('year')
        queryset = queryset.filter(member_code=member.member_code).order_by('-created_at')
        
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
                return MppCollectionAggregation.objects.none()

        return queryset

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            
            # Perform pagination
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(queryset, request)
            
            # Calculate totals
            duplicate_count = queryset.values('from_date', 'to_date').annotate(count=Count('id')).filter(count__gt=1).count()
            total_pouring_days = Sum('no_of_pouring_days') - duplicate_count
            totals = queryset.aggregate(
                total_qty=Sum('qty'),
                avg_fat=Cast(Avg('fat'), output_field=models.DecimalField(decimal_places=3, max_digits=18)),
                avg_snf=Cast(Avg('snf'), output_field=models.DecimalField(decimal_places=3, max_digits=18)),
                total_amount=Sum('amount'),
                total_days=total_pouring_days,
                total_shift=total_pouring_days * 2,
            )

            # Serialize data for the current page
            serializer = self.get_serializer(paginated_queryset, many=True)
            
            # Prepare paginated response
            paginated_response = paginator.get_paginated_response(serializer.data)
            paginated_response.data['totals'] = totals
            paginated_response.data['status'] = status.HTTP_200_OK
            paginated_response.data['message'] = "success"

            return paginated_response

        except ValidationError as e:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": str(e),
                "data": []
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": f"An unexpected error occurred: {str(e)}",
                "data": []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MppCollectionDetailView(generics.GenericAPIView):
    """
    This class provides the data for dashboard
    """
    serializer_class = MppCollectionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        today = timezone.now().date()
        
        if not MemberMaster.objects.filter(mobile_no=request.user.username).exists():
            return Response({
                "status": 400,
                "message": "No member found on this mobile no",
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        member = MemberMaster.objects.get(mobile_no=request.user.username)
        
        date_str = request.query_params.get('date')
        # Parse the date parameter if provided
        if date_str:
            try:
                provided_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response({
                    "status": 400,
                    "message": "date must be in YYYY-MM-DD format",
                    "data": {}
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            provided_date = today

        current_year = provided_date.year
        current_month = provided_date.month

        # Determine the start year of the financial year based on the provided date
        if current_month < 4:
            start_year = current_year - 1
        else:
            start_year = current_year

        start_date = make_aware(timezone.datetime(start_year, 4, 1))
        end_date = make_aware(timezone.datetime(start_year + 1, 3, 31, 23, 59, 59))

        # Filter for the provided date
        date_queryset = MppCollection.objects.filter(
            collection_date__date=provided_date,
            member_code=member.member_code
        )
        
        mpp_agg_queryset = MppCollectionAggregation.objects.filter(
            member_code=member.member_code
        )
        fy_queryset = mpp_agg_queryset.filter(
                    Q(from_date__gte=start_date, from_date__lte=end_date) |
                    Q(to_date__gte=start_date, to_date__lte=end_date) |
                    Q(from_date__lte=start_date, to_date__gte=end_date)
                )
        
        fy_aggregated_data = fy_queryset.aggregate(
            total_days=Count('no_of_pouring_days', distinct=True),
            total_qty=Sum('qty'),
            total_payment=Sum('amount')
        )

        date_serializer = self.get_serializer(date_queryset, many=True)

        response_data = {
            "status": 200,
            "message": "success",
            "data": {
                "dashboard_data": date_serializer.data,
                "dashboard_fy_data": fy_aggregated_data
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)
