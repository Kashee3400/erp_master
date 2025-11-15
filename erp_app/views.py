from util.response import StandardResultsSetPagination
from .serializers import *
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Sum, Avg, Count
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models.functions import TruncDate, Cast
from django.utils.dateparse import parse_datetime


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

class MppCollectionListView(generics.ListAPIView):
    """
    Returns paginated aggregation list,
    but totals are calculated from RAW MppCollection (correct ERP logic).
    """

    serializer_class = MppCollectionAggregationSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    # ----------------------------------------------------
    # FETCH AGGREGATION LIST
    # ----------------------------------------------------
    def get_queryset(self):
        mobile_no = "7518705924"

        member = MemberMaster.objects.filter(
            mobile_no=mobile_no, is_active=True
        ).first()

        if not member:
            return MppCollectionAggregation.objects.none()

        queryset = MppCollectionAggregation.objects.filter(
            member_code=member.member_code
        ).order_by("-created_at")

        # FINANCIAL YEAR FILTER
        year = self.request.GET.get("year")
        if year:
            try:
                year = int(year)
                start_date = f"{year}-04-01"
                end_date = f"{year + 1}-03-31"

                queryset = queryset.filter(
                    from_date__lte=end_date,
                    to_date__gte=start_date,
                )
            except ValueError:
                return MppCollectionAggregation.objects.none()

        return queryset

    # ----------------------------------------------------
    # RAW MPPCollection → ERP TOTALS
    # ----------------------------------------------------
    def calculate_raw_totals(self, member_code, start_date=None, end_date=None):
        """
        Calculates totals from RAW MppCollection:
        - unique days
        - unique shift days
        - weighted fat & snf
        - total qty & amount
        """

        from django.db.models import F, Sum
        from decimal import Decimal

        raw_qs = MppCollection.objects.filter(member_code=member_code)

        # Apply FY filter
        if start_date and end_date:
            raw_qs = raw_qs.filter(
                collection_date__date__gte=start_date,
                collection_date__date__lte=end_date,
            )

        # ---------------------------------------
        # UNIQUE DAYS & UNIQUE SHIFT-DAYS
        # ---------------------------------------
        unique_days = raw_qs.values("collection_date__date").distinct().count()
        unique_shift_days = (
            raw_qs.values("collection_date__date", "shift_code").distinct().count()
        )

        # ---------------------------------------
        # TOTAL QTY & AMOUNT
        # ---------------------------------------
        totals = raw_qs.aggregate(
            total_qty=Sum("qty"),
            total_amount=Sum("amount"),
            qty_fat_sum=Sum(F("qty") * F("fat")),
            qty_snf_sum=Sum(F("qty") * F("snf")),
        )

        total_qty = totals["total_qty"] or Decimal("0")
        total_amount = totals["total_amount"] or Decimal("0")
        qty_fat_sum = totals["qty_fat_sum"] or Decimal("0")
        qty_snf_sum = totals["qty_snf_sum"] or Decimal("0")

        epsilon = Decimal("0.00001")

        weighted_fat = qty_fat_sum / (total_qty + epsilon)
        weighted_snf = qty_snf_sum / (total_qty + epsilon)

        return {
            "total_qty": float(total_qty),
            "total_amount": float(total_amount),
            "weighted_fat": float(round(weighted_fat, 3)),
            "weighted_snf": float(round(weighted_snf, 3)),
            "total_days": unique_days,
            "total_shift": unique_shift_days,
        }

    # ----------------------------------------------------
    # MAIN LIST
    # ----------------------------------------------------
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Paginate the aggregation (as before)
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        # FETCH MEMBER
        mobile_no = "7518705924"
        member = MemberMaster.objects.filter(
            mobile_no=mobile_no, is_active=True
        ).first()

        # FINANCIAL YEAR DETAILS
        year = request.GET.get("year")
        if year:
            year = int(year)
            start_date = f"{year}-04-01"
            end_date = f"{year + 1}-03-31"
        else:
            start_date = None
            end_date = None

        # GET RAW TOTALS (ERP-CORRECT)
        raw_totals = self.calculate_raw_totals(
            member.member_code, start_date=start_date, end_date=end_date
        )

        # Attach totals
        serializer = self.get_serializer(paginated_queryset, many=True)
        paginator.extra_data = {"totals": raw_totals}

        return paginator.get_paginated_response(serializer.data)


from django.core.cache import cache


class MppCollectionDetailView(generics.GenericAPIView):
    """
    API endpoint for fetching other dashboard data.
    """

    serializer_class = MppCollectionSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        today = timezone.now().date()

        # Fetch date parameter and validate format
        date_str = request.query_params.get("date", None)
        provided_date = self.validate_date(date_str, today)
        if isinstance(provided_date, Response):
            return provided_date

        username = self.request.user.username
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
                {
                    "status": 400,
                    "message": "No member found on this mobile number",
                    "data": {},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        member_code = member["member_code"]
        start_date, end_date = self.get_fiscal_year_range(provided_date)

        # Cache key for collections on provided date
        cache_key_date = f"mpp_collection_{member_code}_{provided_date}"
        date_queryset = cache.get(cache_key_date)
        if date_queryset is None:
            date_queryset = list(
                MppCollection.objects.filter(
                    collection_date__date=provided_date, member_code=member_code
                )
            )
            cache.set(cache_key_date, date_queryset, timeout=3600)
        cache_key_fy = f"mpp_collection_fy_{member_code}_{start_date}_{end_date}"
        fiscal_data = cache.get(cache_key_fy)
        if fiscal_data is None:
            aggregated_data = MppCollection.objects.filter(
                collection_date__range=(start_date, end_date), member_code=member_code
            ).annotate(date_only=TruncDate("collection_date"))

            fiscal_data = aggregated_data.aggregate(
                total_days=Count("date_only", distinct=True),
                total_qty=Sum("qty", default=0),
                total_payment=Sum("amount", default=0),
            )
            cache.set(cache_key_fy, fiscal_data, timeout=3600)

        date_serializer = self.get_serializer(date_queryset, many=True)

        response_data = {
            "status": status.HTTP_200_OK,
            "message": "success",
            "data": {
                "dashboard_data": date_serializer.data,
                "dashboard_fy_data": fiscal_data,
            },
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def get_fiscal_year_range(self, provided_date):
        current_year = provided_date.year
        start_year = current_year - 1 if provided_date.month < 4 else current_year
        start_date = timezone.make_aware(timezone.datetime(start_year, 4, 1))
        end_date = timezone.make_aware(
            timezone.datetime(start_year + 1, 3, 31, 23, 59, 59)
        )
        return start_date, end_date

    def validate_date(self, date_str, default_date):
        if not date_str:
            return default_date
        try:
            return timezone.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {
                    "status": 400,
                    "message": "Date must be in YYYY-MM-DD format",
                    "data": {},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


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
