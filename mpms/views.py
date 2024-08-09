from rest_framework import serializers, viewsets
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum, Avg, Count, Min, Max, Case, When, Value, CharField
from .models import Tblfarmer, Tblfarmercollection
from .serializers import TblfarmercollectionSerializer
from datetime import datetime,date
from django.db.models.functions import TruncDay
from erp_app.models import MppCollectionAggregation

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50

class TblfarmercollectionViewSet(viewsets.ModelViewSet):
    serializer_class = TblfarmercollectionSerializer
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        mpms_member = Tblfarmer.objects.filter(phonenumber = self.request.user.username).first()
        queryset = Tblfarmercollection.objects.all()
        year = self.request.query_params.get('year')
        if year:
            year = int(year)
            start_date = f"{year}-04-01"    
            end_date = f"{year + 1}-03-31"
            
        mpp_aggregations = MppCollectionAggregation.objects.filter(member_tr_code=mpms_member.farmercode).first()
        if datetime.now().year == 2024:
            day = 1
            end_day = 1
            month = 4
            if int(mpp_aggregations.mcc_tr_code) == 4:  # Sonbahdra
                end_day = 10
                month = 6
                
            elif int(mpp_aggregations.mcc_tr_code) == 2: # Chunar
                end_day = 10
                
            elif int(mpp_aggregations.mcc_tr_code) in [1,3,5]: #
                end_day = 20
            start_date = date(year=datetime.now().year, month=month, day=day)
            end_date = date(year= datetime.now().year, month=month, day=end_day)


        if mpms_member.farmercode:
            queryset = queryset.filter(member_other_code=mpms_member.farmercode)
        
        if start_date and end_date:
            try:
                queryset = queryset.filter(dumpdate__range=(start_date, end_date))
            except ValueError:
                raise serializers.ValidationError("Invalid date format. Use 'YYYY-MM-DD'.")

        # Create a case statement to group days into the appropriate period
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
            unique_dates=Count(TruncDay('dumpdate'), distinct=True),
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

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            return self.get_paginated_response(page)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
