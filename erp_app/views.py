from util.response import StandardResultsSetPagination, custom_response
from .serializers import *
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.dateparse import parse_datetime
from django.core.cache import cache
from .mixins import FastTotalsMixin
from django.db import connections


class MemberByPhoneNumberView(generics.RetrieveAPIView):
    serializer_class = MemberMasterSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_object(self):
        phone_number = self.request.user.username
        try:
            return (
                MemberMaster.objects.using("sarthak_kashee")
                .filter(mobile_no=phone_number, is_active=True)
                .last()
            )
        except MemberMaster.DoesNotExist:
            return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return Response(
                {"status": status.HTTP_404_NOT_FOUND, "message": "No Data Found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        # Serialize MemberMaster data
        member_serializer = self.get_serializer(instance)
        # Fetch and serialize related MppCollectionAggregation data
        mpp_aggregations = MppCollectionAggregation.objects.filter(
            member_code=instance.member_code
        ).first()
        response_data = {}
        if mpp_aggregations:
            mpp = Mpp.objects.filter(mpp_code=mpp_aggregations.mpp_code).first()
            mcc = Mcc.objects.filter(mcc_code=mpp_aggregations.mcc_code).first()
            response_data = member_serializer.data
            response_data["mcc_code"] = mcc.mcc_ex_code
            response_data["mcc_name"] = mcc.mcc_name
            response_data["mcc_tr_code"] = mcc.mcc_code

            response_data["mpp_name"] = mpp.mpp_name
            response_data["mpp_code"] = mpp.mpp_ex_code
            response_data["mpp_tr_code"] = mpp_aggregations.mpp_tr_code
            response_data["company_code"] = mpp_aggregations.company_code
            response_data["company_name"] = mpp_aggregations.company_name
            response_data["member_tr_code"] = mpp_aggregations.member_tr_code
        billing_member_detail = BillingMemberDetail.objects.filter(
            member_code=instance.member_code
        ).first()
        response_data["bank"] = billing_member_detail.bank_code.bank_name
        response_data["bank_branch"] = ""
        response_data["account_no"] = billing_member_detail.acc_no
        response_data["ifsc"] = billing_member_detail.ifsc
        response = {
            "status": status.HTTP_200_OK,
            "message": "Success",
            "data": response_data,
        }
        return Response(response)


class MemberProfileView(generics.RetrieveAPIView):
    serializer_class = MemberProfileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        phone_number = user.username
        return MemberHierarchyView.objects.filter(
            mobile_no=phone_number, is_default=True
        ).last()

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if not instance:
                return Response(
                    {
                        "status": "error",
                        "message": "No member profile found for this user.",
                        "data": {},
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            member_serializer = self.get_serializer(instance)
            bank_data = MemberSahayakBankDetail.objects.filter(
                module_code=instance.member_code
            ).last()
            bank_detail = MemberBankSerializer(bank_data).data if bank_data else {}
            return Response(
                {
                    "status": "success",
                    "message": "Member profile retrieved successfully.",
                    "data": {
                        "member_detail": member_serializer.data,
                        "bank_detail": bank_detail,
                    },
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": "An unexpected error occurred while retrieving the profile.",
                    "data": {},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


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
        if not MemberMaster.objects.filter(
            mobile_no=self.request.user.username, is_active=True
        ).exists():
            return Response(
                {
                    "status": 400,
                    "message": _(
                        f"No member found on this mobile no {self.request.user.username}"
                    ),
                    "data": {},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        member = MemberMaster.objects.get(
            mobile_no=self.request.user.username, is_active=True
        )
        from_date_str = self.request.GET.get("from_date")
        to_date_str = self.request.GET.get("to_date")

        from_date = parse_datetime(from_date_str)
        to_date = parse_datetime(to_date_str)

        # Filter the BillingMemberMaster objects
        billing_member_master_qs = BillingMemberMaster.objects.filter(
            from_date__lte=to_date, to_date__gte=from_date
        )

        # Get the related BillingMemberDetail objects
        billing_member_details = BillingMemberDetail.objects.using(
            "sarthak_kashee"
        ).filter(
            member_code=member.member_code,
            billing_member_master_code__in=billing_member_master_qs,
        )
        return billing_member_details

    def retrieve(self, request, *args, **kwargs):
        instances = self.get_objects()
        if not instances:
            response = {
                "status": status.HTTP_404_NOT_FOUND,
                "message": _("No Data Found"),
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        detailed_data = []
        for instance in instances:
            serializer = self.get_serializer(instance)
            local_sale_txns = []
            if (
                BillingMemberMaster.objects.using("sarthak_kashee")
                .filter(
                    billing_member_master_code=instance.billing_member_master_code.billing_member_master_code
                )
                .exists()
            ):
                billing_master_instance = BillingMemberMaster.objects.using(
                    "sarthak_kashee"
                ).get(
                    billing_member_master_code=instance.billing_member_master_code.billing_member_master_code
                )
                from_date = billing_master_instance.from_date
                to_date = billing_master_instance.to_date

                local_sales_queryset = LocalSale.objects.using("sarthak_kashee").filter(
                    module_code=instance.member_code,
                    status__in=["Pending", "Approved"],
                    installment_start_date__range=[from_date, to_date],
                )
                for local_sale in local_sales_queryset:
                    local_sale_txns_queryset = local_sale.local_sale_txn.all()
                    local_sale_txns.extend(
                        LocalSaleTxnSerializer(local_sale_txns_queryset, many=True).data
                    )

            detailed_data.append(
                {
                    "details": serializer.data,
                    "local_sale_txns": local_sale_txns,
                }
            )

        response = {
            "status": status.HTTP_200_OK,
            "message": "Success",
            "data": detailed_data,
        }
        return Response(response)


class MppCollectionDetailView(FastTotalsMixin, generics.GenericAPIView):
    """
    API endpoint for dashboard data (daily + fiscal year totals).
    """

    serializer_class = MppCollectionSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        today = timezone.now().date()
        date_str = request.query_params.get("date")
        provided_date = self.validate_date(date_str, today)
        if isinstance(provided_date, Response):
            return provided_date

        username = request.user.username
        cache_key_member = f"member_{username}"
        member = cache.get(cache_key_member)
        if member is None:
            member = (
                MemberMaster.objects.filter(mobile_no=username, is_active=True)
                .values("member_code")
                .last()
            )
            cache.set(cache_key_member, member, timeout=3600)

        if not member:
            return Response(
                {"status": 400, "message": "No member found", "data": {}}, status=400
            )

        member_code = member["member_code"]

        # ---------------------------
        # Daily dashboard data (only required fields)
        # ---------------------------
        cache_key_date = f"mpp_collection_{member_code}_{provided_date}"
        date_queryset = cache.get(cache_key_date)
        if date_queryset is None:
            date_queryset = list(
                MppCollection.objects.filter(
                    member_code=member_code,
                    collection_date__date=provided_date,
                ).values("collection_date", "shift_code", "qty", "fat", "snf", "amount")
            )
            cache.set(cache_key_date, date_queryset, timeout=3600)

        # ---------------------------
        # Fiscal year totals (reuse calculate_fast_totals)
        # ---------------------------
        start_date, end_date = self.get_fiscal_year_range(provided_date)
        cache_key_fy = f"mpp_collection_fy_{member_code}_{start_date}_{end_date}"
        fiscal_data = cache.get(cache_key_fy)

        if fiscal_data is None:
            fiscal_data = self.calculate_fast_totals(member_code, start_date, end_date)
            cache.set(cache_key_fy, fiscal_data, timeout=3600)
        response_data = {
            "status": status.HTTP_200_OK,
            "message": "success",
            "data": {
                "dashboard_data": date_queryset,
                "dashboard_fy_data": fiscal_data,
            },
        }
        return Response(response_data, status=status.HTTP_200_OK)

    # ---------------------------
    # Date validation
    # ---------------------------
    def validate_date(self, date_str, default_date):
        if not date_str:
            return default_date
        try:
            return timezone.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"status": 400, "message": "Date must be YYYY-MM-DD", "data": {}},
                status=400,
            )

    # ---------------------------
    # Fiscal year range
    # ---------------------------
    def get_fiscal_year_range(self, provided_date):
        year = provided_date.year
        start_year = year - 1 if provided_date.month < 4 else year
        start_date = timezone.make_aware(timezone.datetime(start_year, 4, 1))
        end_date = timezone.make_aware(
            timezone.datetime(start_year + 1, 3, 31, 23, 59, 59)
        )
        return start_date, end_date


class MppCollectionListView(FastTotalsMixin, generics.ListAPIView):
    """
    Returns paginated aggregation list, but totals are calculated from RAW MppCollection using optimized SQL.
    """

    serializer_class = MppCollectionAggregationSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    # ---------------------------
    # AGGREGATION LIST (same as before)
    # ---------------------------
    def get_queryset(self):
        mobile_no = (
            self.request.user.username
        )

        member = MemberMaster.objects.filter(
            mobile_no=mobile_no, is_active=True
        ).first()

        if not member:
            return MppCollectionAggregation.objects.none()

        qs = MppCollectionAggregation.objects.filter(
            member_code=member.member_code
        ).order_by("-created_at")

        year = self.request.GET.get("year")
        if year:
            try:
                year = int(year)
                start_date = f"{year}-04-01"
                end_date = f"{year + 1}-03-31"
                qs = qs.filter(from_date__lte=end_date, to_date__gte=start_date)
            except ValueError:
                return MppCollectionAggregation.objects.none()

        return qs

    # ---------------------------
    # MAIN LIST — return paginated data + totals
    # ---------------------------
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        # Fetch member
        mobile_no = self.request.user.username
        member = MemberMaster.objects.filter(
            mobile_no=mobile_no, is_active=True
        ).first()
        if not member:
            return paginator.get_paginated_response([])

        # FY filter for totals
        year = request.GET.get("year")
        if year:
            year = int(year)
            start_date = f"{year}-04-01"
            end_date = f"{year + 1}-03-31"
        else:
            start_date = None
            end_date = None

        # ---------------------------
        # FAST TOTALS from raw table
        # ---------------------------
        totals = self.calculate_fast_totals(member.member_code, start_date, end_date)

        # ---------------------------
        # Paginated serializer
        # ---------------------------
        serializer = self.get_serializer(paginated_queryset, many=True)

        # Attach totals in extra_data
        paginator.extra_data = {"totals": totals}

        return paginator.get_paginated_response(serializer.data)

# TODO: Remove after succefull implementation of new apis
# class MppCollectionListView(generics.ListAPIView):
#     serializer_class = MppCollectionAggregationSerializer
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]
#     pagination_class = StandardResultsSetPagination

#     # ---------------------------------------
#     # AGGREGATED LIST (same as before)
#     # ---------------------------------------
#     def get_queryset(self):
#         mobile_no = "7518705924"

#         member = MemberMaster.objects.filter(
#             mobile_no=mobile_no, is_active=True
#         ).first()

#         if not member:
#             return MppCollectionAggregation.objects.none()

#         qs = MppCollectionAggregation.objects.filter(
#             member_code=member.member_code
#         ).order_by("-created_at")

#         year = self.request.GET.get("year")
#         if year:
#             try:
#                 year = int(year)
#                 start_date = f"{year}-04-01"
#                 end_date = f"{year + 1}-03-31"

#                 qs = qs.filter(
#                     from_date__lte=end_date,
#                     to_date__gte=start_date,
#                 )
#             except:
#                 return MppCollectionAggregation.objects.none()

#         return qs

#     # ---------------------------------------
#     # SUPER FAST TOTALS (raw SQL)
#     # ---------------------------------------
#     def calculate_fast_totals(
#         self, member_code, start_date=None, end_date=None, using="sarthak_kashee"
#     ):
#         """
#         Calculate ERP-correct totals directly from MppCollection table using raw SQL.
#         Optimized for MSSQL with proper indexes.

#         Returns:
#             dict: total_qty, total_amount, weighted_fat, weighted_snf, total_days, total_shift
#         """
#         from django.db import connections
#         from decimal import Decimal

#         params = [member_code]
#         date_filter = ""

#         if start_date and end_date:
#             date_filter = "AND collection_date BETWEEN %s AND %s"
#             params.extend([start_date, end_date])

#         sql = f"""
#             SELECT
#                 SUM(qty) AS total_qty,
#                 SUM(amount) AS total_amount,
#                 SUM(qty * fat) AS qty_fat_sum,
#                 SUM(qty * snf) AS qty_snf_sum,
#                 COUNT(DISTINCT CAST(collection_date AS DATE)) AS total_days,
#                 COUNT(DISTINCT CONCAT(
#                     CAST(collection_date AS DATE), '_', CAST(shift_code AS VARCHAR(10))
#                 )) AS total_shift
#             FROM mpp_collection
#             WHERE member_code = %s
#             {date_filter};
#         """

#         # Use specified database connection
#         with connections[using].cursor() as cursor:
#             cursor.execute(sql, params)
#             row = cursor.fetchone()

#         total_qty = Decimal(row[0] or 0)
#         total_amount = Decimal(row[1] or 0)
#         qty_fat_sum = Decimal(row[2] or 0)
#         qty_snf_sum = Decimal(row[3] or 0)
#         total_days = row[4] or 0
#         total_shift = row[5] or 0

#         # Avoid division by zero
#         epsilon = Decimal("0.00001")

#         weighted_fat = (
#             float(round(qty_fat_sum / (total_qty + epsilon), 3)) if total_qty else 0
#         )
#         weighted_snf = (
#             float(round(qty_snf_sum / (total_qty + epsilon), 3)) if total_qty else 0
#         )

#         return {
#             "total_qty": float(total_qty),
#             "total_amount": float(total_amount),
#             "weighted_fat": weighted_fat,
#             "weighted_snf": weighted_snf,
#             "total_days": total_days,
#             "total_shift": total_shift,
#         }

#     # ---------------------------------------
#     # MAIN LIST — return paginated list + totals
#     # ---------------------------------------
#     def list(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         paginator = self.pagination_class()
#         paginated_queryset = paginator.paginate_queryset(queryset, request)

#         # fetch member
#         mobile_no = "7518705924"
#         member = MemberMaster.objects.filter(
#             mobile_no=mobile_no, is_active=True
#         ).first()

#         # FY filter
#         year = request.GET.get("year")
#         if year:
#             year = int(year)
#             start_date = f"{year}-04-01"
#             end_date = f"{year + 1}-03-31"
#         else:
#             start_date = None
#             end_date = None

#         # SUPER FAST TOTALS
#         totals = self.calculate_fast_totals(member.member_code, start_date, end_date)

#         # normal paginated serializer
#         serializer = self.get_serializer(paginated_queryset, many=True)

#         # attach totals
#         paginator.extra_data = {"totals": totals}

#         return paginator.get_paginated_response(serializer.data)


# class MppCollectionDetailView(generics.GenericAPIView):
#     """
#     API endpoint for fetching other dashboard data.
#     """

#     serializer_class = MppCollectionSerializer
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         today = timezone.now().date()

#         # Fetch date parameter and validate format
#         date_str = request.query_params.get("date", None)
#         provided_date = self.validate_date(date_str, today)
#         if isinstance(provided_date, Response):
#             return provided_date

#         username = self.request.user.username
#         cache_key_member = f"member_{username}"
#         member = cache.get(cache_key_member)
#         if member is None:
#             member = (
#                 MemberMaster.objects.filter(mobile_no=username, is_active=True)
#                 .values("member_code")
#                 .last()
#             )
#             cache.set(cache_key_member, member, timeout=3600)

#         if not member:
#             return Response(
#                 {
#                     "status": 400,
#                     "message": "No member found on this mobile number",
#                     "data": {},
#                 },
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         member_code = member["member_code"]
#         start_date, end_date = self.get_fiscal_year_range(provided_date)

#         # Cache key for collections on provided date
#         cache_key_date = f"mpp_collection_{member_code}_{provided_date}"
#         date_queryset = cache.get(cache_key_date)
#         if date_queryset is None:
#             date_queryset = list(
#                 MppCollection.objects.filter(
#                     collection_date__date=provided_date, member_code=member_code
#                 )
#             )
#             cache.set(cache_key_date, date_queryset, timeout=3600)
#         cache_key_fy = f"mpp_collection_fy_{member_code}_{start_date}_{end_date}"
#         fiscal_data = cache.get(cache_key_fy)
#         if fiscal_data is None:
#             aggregated_data = MppCollection.objects.filter(
#                 collection_date__range=(start_date, end_date), member_code=member_code
#             ).annotate(date_only=TruncDate("collection_date"))

#             fiscal_data = aggregated_data.aggregate(
#                 total_days=Count("date_only", distinct=True),
#                 total_qty=Sum("qty", default=0),
#                 total_payment=Sum("amount", default=0),
#             )
#             cache.set(cache_key_fy, fiscal_data, timeout=3600)

#         date_serializer = self.get_serializer(date_queryset, many=True)

#         response_data = {
#             "status": status.HTTP_200_OK,
#             "message": "success",
#             "data": {
#                 "dashboard_data": date_serializer.data,
#                 "dashboard_fy_data": fiscal_data,
#             },
#         }

#         return Response(response_data, status=status.HTTP_200_OK)

#     def get_fiscal_year_range(self, provided_date):
#         current_year = provided_date.year
#         start_year = current_year - 1 if provided_date.month < 4 else current_year
#         start_date = timezone.make_aware(timezone.datetime(start_year, 4, 1))
#         end_date = timezone.make_aware(
#             timezone.datetime(start_year + 1, 3, 31, 23, 59, 59)
#         )
#         return start_date, end_date

#     def validate_date(self, date_str, default_date):
#         if not date_str:
#             return default_date
#         try:
#             return timezone.datetime.strptime(date_str, "%Y-%m-%d").date()
#         except ValueError:
#             return Response(
#                 {
#                     "status": 400,
#                     "message": "Date must be in YYYY-MM-DD format",
#                     "data": {},
#                 },
#                 status=status.HTTP_400_BAD_REQUEST,
#             )


class MemberShareFinalInfoView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        member = MemberMaster.objects.filter(
            mobile_no=self.request.user.username, is_active=True
        )
        if not member.exists():
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Member does not exists",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        first_member = member.first()
        records = MemberShareFinalInfo.objects.filter(to_code=first_member.member_code)
        total_sum = (
            records.aggregate(total_no_of_share=Sum("no_of_share"))["total_no_of_share"]
            or 0
        )
        serializer = MemberShareFinalInfoSerializer(records, many=True)
        response_data = {
            "status": status.HTTP_200_OK,
            "message": "Success",
            "data": {"total_no_of_share": total_sum, "records": serializer.data},
        }
        return Response(response_data, status=status.HTTP_200_OK)


class TodayCollectionView(generics.GenericAPIView):
    """
    API to fetch total milk collection for today,
    with breakdown by shift and overall total.
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, *args, **kwargs):
        member_code = request.query_params.get("member_code")
        if not member_code:
            return Response(
                {"status": 400, "message": "member_code is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        today = timezone.now().date()
        result = self.get_today_collection(member_code, today)
        return Response({"status": 200, "message": "success", "data": result})

    @staticmethod
    def get_today_collection(member_code, collection_date, using="sarthak_kashee"):
        """
        Returns:
            {
                "total_qty": 123.45,
                "morning_shift_qty": 70.12,
                "evening_shift_qty": 53.33
            }
        """
        # Assuming: shift_code 1 = morning, 2 = evening
        sql = """
            SELECT
                SUM(qty) AS total_qty,
                SUM(CASE WHEN shift_code = 1 THEN qty ELSE 0 END) AS morning_shift_qty,
                SUM(CASE WHEN shift_code = 2 THEN qty ELSE 0 END) AS evening_shift_qty
            FROM mpp_collection
            WHERE member_code = %s
            AND CAST(collection_date AS DATE) = %s;
        """

        with connections[using].cursor() as cursor:
            cursor.execute(sql, [member_code, collection_date])
            row = cursor.fetchone()

        total_qty = float(row[0] or 0)
        morning_qty = float(row[1] or 0)
        evening_qty = float(row[2] or 0)

        data = {
            "total_qty": round(total_qty, 2),
            "morning_shift_qty": round(morning_qty, 2),
            "evening_shift_qty": round(evening_qty, 2),
        }
        return custom_response(
            status_text="success",
            data=data,
            message="Today Collection Fetched",
            status_code=status.HTTP_200_OK,
            errors={},
        )


from datetime import timedelta


class Last5DaysCollectionView(generics.GenericAPIView):
    """
    API to fetch total milk collection for last 5 days
    for a member, with breakdown by shift and total per day.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        member_code = request.query_params.get("member_code")
        if not member_code:
            return Response(
                {"status": 400, "message": "member_code is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        today = timezone.now().date()
        last_5_days = [today - timedelta(days=i) for i in range(5)]
        last_5_days.sort()

        results = []
        for day in last_5_days:
            totals = self.get_day_collection(member_code, day)
            results.append({"date": str(day), **totals})

        return Response({"status": 200, "message": "success", "data": results})

    @staticmethod
    def get_day_collection(member_code, collection_date, using="sarthak_kashee"):
        """
        Returns totals for a single date:
        {
            "total_qty": 123.45,
            "morning_shift_qty": 70.12,
            "evening_shift_qty": 53.33
        }
        """
        sql = """
            SELECT
                SUM(qty) AS total_qty,
                SUM(CASE WHEN shift_code = 1 THEN qty ELSE 0 END) AS morning_shift_qty,
                SUM(CASE WHEN shift_code = 2 THEN qty ELSE 0 END) AS evening_shift_qty
            FROM mpp_collection
            WHERE member_code = %s
            AND CAST(collection_date AS DATE) = %s;
        """

        with connections[using].cursor() as cursor:
            cursor.execute(sql, [member_code, collection_date])
            row = cursor.fetchone()

        total_qty = float(row[0] or 0)
        morning_qty = float(row[1] or 0)
        evening_qty = float(row[2] or 0)

        data = {
            "total_qty": round(total_qty, 2),
            "morning_shift_qty": round(morning_qty, 2),
            "evening_shift_qty": round(evening_qty, 2),
        }

        return custom_response(
            status_text="success",
            data=data,
            message="Last 5 Days Collection Fetched...",
            status_code=status.HTTP_200_OK,
            errors={},
        )
