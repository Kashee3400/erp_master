from rest_framework import serializers, viewsets
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum, Avg, Count, Min, Max, Case, When, Value, CharField
from .serializers import TblfarmercollectionSerializer
from datetime import datetime,date
from django.db.models.functions import TruncDay
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Sum
from .models import Tblfarmer, Tblfarmercollection

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50


class TblfarmercollectionViewSet(viewsets.ModelViewSet):
    serializer_class = TblfarmercollectionSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [AllowAny]

    def get_queryset(self):
        mpms_member = Tblfarmer.objects.filter(phonenumber=self.request.user.username).first()
        queryset = Tblfarmercollection.objects.all()
        year = self.request.query_params.get('year')
        start_date, end_date = None, None

        if year:
            year = int(year)
            start_date = f"{year}-04-01"
            end_date = f"{year + 1}-03-31"

        # Financial Year 2024 check
        fy_start_date = date(2024, 4, 1)
        fy_end_date = date(2025, 3, 31)
        current_date = timezone.now().date()

        if fy_start_date <= current_date <= fy_end_date:
            if year:
                year = int(year)
                start_date = f"{year}-04-01"
                end_date = f"{year + 1}-03-31"
            month = 4
            if int(mpms_member.mccid.mccid) == 4:
                end_day = 10
                month = 6
            elif int(mpms_member.mccid.mccid) == 2:
                end_day = 10
            elif int(mpms_member.mccid.mccid) in [1, 3, 5]:
                end_day = 20
            else:
                end_day = 1
            
            start_date = date(year=timezone.now().year, month=month, day=1)
            end_date = date(year=timezone.now().year, month=month, day=end_day)

            if mpms_member.farmercode:
                queryset = queryset.filter(member_other_code=mpms_member.farmercode)
            
            if start_date and end_date:
                try:
                    queryset = queryset.filter(dumpdate__range=(start_date, end_date))
                except ValueError:
                    raise serializers.ValidationError("Invalid date format. Use 'YYYY-MM-DD'.")
        else:
            # Return empty queryset if outside the FY 2024 range
            queryset = Tblfarmercollection.objects.none()

        # Annotate period
        queryset = queryset.annotate(
            period=Case(
                When(dumpdate__day__lte=10, then=Value('1-10')),
                When(dumpdate__day__lte=20, then=Value('11-20')),
                default=Value('21-end'),
                output_field=CharField()
            )
        )

        # Aggregate data by month and period
        aggregated_data = queryset.values(
            'dumpdate__year', 'dumpdate__month', 'period'
        ).annotate(
            sum_weight=Sum('weight'),
            avg_fat=Avg('fat'),
            avg_snf=Avg('snf'),
            sum_totalamount=Sum('totalamount'),
            unique_dates=Count('dumpdate', distinct=True),
            total_count=Count('rowid'),
            from_dumpdate=Min('dumpdate'),
            to_dumpdate=Max('dumpdate')
        ).order_by('dumpdate__year', 'dumpdate__month', 'period')

        # Format numerical fields to two decimal places
        for item in aggregated_data:
            item['sum_weight'] = format(float(item['sum_weight']), '.2f')
            item['avg_fat'] = format(float(item['avg_fat']), '.2f')
            item['avg_snf'] = format(float(item['avg_snf']), '.2f')
            item['sum_totalamount'] = format(float(item['sum_totalamount']), '.2f')

        return aggregated_data

    def get_totals(self, queryset):
        totals = queryset.aggregate(
            total_qty=Sum('weight'),
            avg_fat=Avg('fat'),
            avg_snf=Avg('snf'),
            total_amount=Sum('totalamount'),
            total_days=Count('dumpdate', distinct=True),
            total_shift=Count('rowid')
        )
        # Format numerical fields to two decimal places
        totals['total_qty'] = format(float(totals['total_qty'] or 0), '.2f')
        totals['avg_fat'] = format(float(totals['avg_fat'] or 0), '.3f')
        totals['avg_snf'] = format(float(totals['avg_snf'] or 0), '.3f')
        totals['total_amount'] = format(float(totals['total_amount'] or 0), '.2f')
        return totals

    def list(self, request, *args, **kwargs):
        fy_start_date = date(2024, 4, 1)
        fy_end_date = date(2025, 3, 31)
        current_date = timezone.now().date()

        if not (fy_start_date <= current_date <= fy_end_date):
            response = {
                'status': status.HTTP_200_OK,
                'message': 'FY is not 2024',
                'data': {
                    'results': [],
                    'totals': {
                        'sum_weight': '0.00',
                        'avg_fat': '0.00',
                        'avg_snf': '0.00',
                        'sum_totalamount': '0.00'
                    }
                }
            }
            return Response(response, status=status.HTTP_200_OK)

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            paginated_data = self.get_paginated_response(page).data['results']
        else:
            paginated_data = queryset

        totals = self.get_totals(queryset)

        response = {
            'status': status.HTTP_200_OK,
            'message': 'Success',
            'data': {
                'results': paginated_data,
                'totals': totals
            }
        }
        return Response(response, status=status.HTTP_200_OK)

class OldDataCollectionView(generics.GenericAPIView):
    """
    API endpoint for fetching old data.
    """
    serializer_class = TblfarmercollectionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        phonenumber = "8810778378"  # Hardcoded; should be `self.request.user.username`
        mpms_member = Tblfarmer.objects.filter(phonenumber=phonenumber).first()
        if not mpms_member:
            return Response({"status": 400, "message": "No member found on this mobile number", "data": {}}, 
                            status=status.HTTP_400_BAD_REQUEST)
        provided_date = self.get_requested_date(request)
        start_date, end_date = self.get_date_range(mpms_member, provided_date.year)

        # Filter once and reuse the queryset
        mpms_farmer_collection = Tblfarmercollection.objects.filter(
            dumpdate__range=[start_date, end_date],  
            isapproved=True,
            isdelete=False,
            member_other_code=mpms_member.farmercode,
        )
        mpms_farmer_collection_data = mpms_farmer_collection.filter(dumpdate=provided_date)
        aggregates = mpms_farmer_collection.aggregate(
            total_lr=Sum('weightliter') or 0,
            total_amount=Sum('totalamount') or 0
        )
        response_data = {
            "status": status.HTTP_200_OK,
            "message": "success",
            "data": {
                "old_dashboard_data": TblfarmercollectionSerializer(mpms_farmer_collection_data, many=True).data,
                "old_dashboard_fy_data": {
                    "total_days": mpms_farmer_collection.values('dumpdate').distinct().count(),
                    "total_qty": aggregates['total_lr'],
                    "total_payment": aggregates['total_amount']
                },
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def get_requested_date(self, request):
        """Extract and validate requested date from query params."""
        date_str = request.query_params.get('date')
        if date_str:
            try:
                return timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response({"status": 400, "message": "Date must be in YYYY-MM-DD format", "data": {}},
                                status=status.HTTP_400_BAD_REQUEST)
        return timezone.now().date()

    def get_date_range(self, mpms_member, year):
        """Determine start and end date based on `mccid` rules."""
        day, end_day, month = 1, 1, 4
        mccid_mapping = {4: (6, 10), 2: (4, 10), 1: (4, 20), 3: (4, 20), 5: (4, 20)}
        month, end_day = mccid_mapping.get(int(mpms_member.mccid.mccid), (4, 1))

        return date(year, month, day), date(year, month, end_day)
