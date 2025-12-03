from all_imports import *
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from erp_app.models import Mpp
from facilitator.authentication import ApiKeyAuthentication
from facilitator.models.user_profile_model import UserProfile
from ..throttle import OTPThrottle
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.views import View


from decouple import config

logger = logging.getLogger(__name__)


def custom_response(status, data=None, message=None, status_code=200):
    response_data = {"status": status, "message": message or "Success", "data": data}
    return JsonResponse(
        response_data, status=status_code, json_dumps_params={"ensure_ascii": False}
    )


class MyHomePage(LoginRequiredMixin, View):
    template_name = "member/pages/dashboards/default.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class GenerateOTPView(APIView):
    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [AllowAny]
    throttle_classes = [OTPThrottle]

    def post(self, request, *args, **kwargs):
        try:
            phone_number = request.data.get("phone_number", "").strip()

            if not phone_number.isdigit() or len(phone_number) != 10:
                return Response(
                    {"status": "error", "message": "Invalid phone number format."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            members = MemberHierarchyView.objects.using("sarthak_kashee").filter(
                mobile_no=phone_number, is_default=True, is_active=True
            )
            if not members.exists():
                return Response(
                    {
                        "status": "error",
                        "message": "Mobile number does not exist in member data",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            if members.count() > 1:
                return Response(
                    {
                        "status": "error",
                        "message": f"{members.count()} member found with this number",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Delete any existing OTP
            OTP.objects.filter(phone_number=phone_number).delete()
            # Create new OTP entry
            new_otp = OTP.objects.create(phone_number=phone_number)
            # Send OTP
            sent, info = send_sms_api(mobile=phone_number, otp=new_otp)
            if not sent:
                return Response(
                    {
                        "status": "error",
                        "message": "Failed to send OTP. Please try again later.",
                        "details": info,
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(
                {"status": "success", "message": "OTP sent successfully."},
                status=status.HTTP_200_OK,
            )

        except DatabaseError as db_err:
            logger.error(f"Database error: {db_err}")
            return Response(
                {"status": "error", "message": "Database error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except serializers.ValidationError as val_err:
            return Response(
                {"status": "error", "message": str(val_err)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.exception("Unexpected error while generating OTP")
            return Response(
                {"status": "error", "message": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            phone_number = serializer.validated_data["phone_number"]
            otp_value = serializer.validated_data["otp"]
            device_id = request.data.get("device_id")
            module = request.data.get("module", "member")

            if not device_id or not otp_value:
                return Response(
                    {"status": "error", "message": "OTP and device ID are required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            otp = OTP.objects.filter(phone_number=phone_number, otp=otp_value).last()
            if not otp:
                return Response(
                    {"status": "error", "message": "Invalid OTP"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not otp.is_valid():
                otp.delete()
                return Response(
                    {"status": "error", "message": "OTP expired"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user, _ = User.objects.get_or_create(username=phone_number)
            # ⚙️ Check if user is already logged into another module
            existing_device = UserDevice.objects.filter(user=user).first()
            if existing_device:
                existing_module = (existing_device.module or "").strip().lower()
                current_module = (module or "").strip().lower()

                # Compare only if existing_module has a valid value
                if existing_module and existing_module != current_module:
                    return Response(
                        {
                            "status": "error",
                            "message": f"You are already logged into {existing_module} module. Contact Admin.",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # 🔐 Blacklist all outstanding tokens for this user
            try:
                for token in OutstandingToken.objects.filter(user=user):
                    BlacklistedToken.objects.get_or_create(token=token)
            except Exception as e:
                logger.warning(f"Token blacklisting failed for {user}: {e}")

            # 🧹 Remove old device entries
            UserDevice.objects.filter(Q(user=user) | Q(device=device_id)).delete()

            # 🆕 Register new device
            device = UserDevice.objects.create(
                user=user, device=device_id, module=module
            )

            # 🔁 Generate new token pair
            refresh = RefreshToken.for_user(user)
            update_last_login(None, user)

            otp.delete()

            return Response(
                {
                    "status": "success",
                    "message": "Authentication successful",
                    "phone_number": user.username,
                    "user_id": user.pk,
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "device_id": device.device,
                },
                status=status.HTTP_200_OK,
            )

        except (DatabaseError, IntegrityError) as db_err:
            logger.error(f"Database error during OTP verification: {db_err}")
            return Response(
                {"status": "error", "message": "Database error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            logger.exception(f"Unexpected error during OTP verification: {e}")
            return Response(
                {"status": "error", "message": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GenerateSahayakOTPView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [OTPThrottle]

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get("phone_number")

        if not phone_number:
            return Response(
                {"status": "error", "message": "Phone number is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not User.objects.filter(username=phone_number).exists():
            return Response(
                {
                    "status": "error",
                    "message": "User does not exist. Please contact support.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Delete previous OTPs for this number
        OTP.objects.filter(phone_number=phone_number).delete()

        # Create new OTP
        new_otp = OTP.objects.create(phone_number=phone_number)

        sent, info = send_sms_api(mobile=phone_number, otp=new_otp.otp)
        if not sent:
            return Response(
                {
                    "status": "error",
                    "message": "Failed to send OTP. Please try again later.",
                    "details": info,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"status": "success", "message": "OTP sent successfully."},
            status=status.HTTP_200_OK,
        )


class VerifySahayakOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]
        otp_value = serializer.validated_data["otp"]
        device_id = request.data.get("device_id")
        module = request.data.get("module", "sahayak")

        # --- 1️⃣ Validate OTP
        otp = OTP.objects.filter(phone_number=phone_number, otp=otp_value).first()
        if not otp:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid OTP. Try again.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not otp.is_valid():
            otp.delete()
            return Response(
                {"status": status.HTTP_400_BAD_REQUEST, "message": "OTP expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --- 2️⃣ Get or create user
        user, _ = User.objects.get_or_create(username=phone_number)

        # --- 3️⃣ Get or create user profile
        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                "department": UserProfile.Department.SAHAYAK,
                "phone_number": user.username,
                "designation": "Sahayak",
                "is_verified": True,
                "avatar": "",
                "address": "",
                "mpp_code": "",
                "is_email_verified": False,
                "salutation": "",
            },
        )

        # --- 4️⃣ Ensure MPP Code exists
        if not profile.mpp_code:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "MPP code not assigned. Contact support.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        existing_device = UserDevice.objects.filter(user=user).first()

        if existing_device:
            existing_module = (existing_device.module or "").strip().lower()
            current_module = (module or "").strip().lower()

            if existing_module != current_module:
                return Response(
                    {
                        "status": "error",
                        "message": f"You are already logged into {existing_module} module. Contact Admin.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # --- 5️⃣ Clean up conflicting devices (same user or same device_id)
        UserDevice.objects.filter(Q(user=user) | Q(device=device_id)).delete()

        # --- 6️⃣ Register new device (MPP code now comes from profile)
        device = UserDevice.objects.create(
            user=user,
            device=device_id,
            module=module,
            mpp_code=profile.mpp_code,
        )

        # --- 7️⃣ Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        update_last_login(None, user)

        # --- 8️⃣ Respond
        return Response(
            {
                "status": status.HTTP_200_OK,
                "phone_number": user.username,
                "message": "Authentication successful",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "device_id": device.device,
                "mpp_code": profile.mpp_code,
            },
            status=status.HTTP_200_OK,
        )


def send_sms_api(mobile, otp):
    url = config("SMS_API_URL")
    params = {
        "userid": config("SMS_USERID"),
        "output": "json",
        "password": config("SMS_PASSWORD"),
        "sendMethod": "quick",
        "mobile": mobile,
        "msg": f"आपका काशी ई-डेयरी लॉगिन ओटीपी कोड {otp} है। किसी के साथ साझा न करें- काशी डेरी",
        "senderid": config("SMS_SENDERID"),
        "msgType": "unicode",
        "dltEntityId": config("SMS_DLT_ENTITY_ID"),
        "dltTemplateId": config("SMS_DLT_TEMPLATE_ID"),
        "duplicatecheck": "true",
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if response.status_code == 200:
            return True, data
        return False, data
    except requests.RequestException as e:
        return False, str(e)


class VerifySession(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        device_id = request.data.get("device_id")
        if UserDevice.objects.filter(user=user, device=device_id).exists():
            return Response({"is_valid": True}, status=status.HTTP_200_OK)
        else:
            return Response({"is_valid": False}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        user = self.request.user

        if not serializer.is_valid():
            logger.warning(
                "Logout validation failed for user %s: %s",
                request.user,
                serializer.errors,
            )
            return custom_response(
                status="error",
                status_code=status.HTTP_400_BAD_REQUEST,
                message=serializer.errors.get("refresh_token", ["Invalid data"])[0],
            )

        try:
            serializer.save()
            # UserDevice.objects.filter(user=user).delete()
        except serializers.ValidationError as e:
            logger.warning(
                "Logout blacklist failed for user %s: %s", request.user, str(e)
            )
            return custom_response(
                status="error",
                status_code=status.HTTP_400_BAD_REQUEST,
                message=str(e.detail[0]),
            )
        except Exception as e:
            logger.error(
                "Unexpected logout error for user %s: %s",
                request.user,
                str(e),
                exc_info=True,
            )
            return custom_response(
                status="error",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="An unexpected error occurred during logout.",
            )

        logger.info("User %s logged out successfully.", request.user)
        return custom_response(
            status="success",
            status_code=status.HTTP_200_OK,
            message="Logout successful.",
        )


class ProductRateListView(generics.ListAPIView):
    pagination_class = StandardResultsSetPagination
    permission_classes = [AllowAny]
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("locale",)

    def get_queryset(self):
        locale = self.request.GET.get("locale", "en")
        return ProductRate.objects.filter(locale=locale)

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            if queryset.exists():
                return custom_response(status="success", data=serializer.data)
            else:
                return custom_response(
                    status="error",
                    message="No products found",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
        except Exception as e:
            return custom_response(
                status="error",
                message=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class MonthListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        months = [
            _("January"),
            _("February"),
            _("March"),
            _("April"),
            _("May"),
            _("June"),
            _("July"),
            _("August"),
            _("September"),
            _("October"),
            _("November"),
            _("December"),
        ]

        return Response(
            {
                "status": "success",
                "message": _("Months retrieved successfully"),
                "result": months,
            },
            status=status.HTTP_200_OK,
        )


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_saleable", "is_purchase"]
    serializer_class = ERProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        Fetch products based on the latest PriceBook and its PriceBookDetail efficiently.
        """
        latest_price_book = PriceBook.objects.order_by("-created_at").first()
        self.latest_price_book = latest_price_book  # Store it for reuse

        if latest_price_book:
            # Fetch PriceBookDetails efficiently & store for later use
            self.price_book_details = {
                detail.product_code.product_code: detail
                for detail in PriceBookDetail.objects.filter(
                    price_book_code=latest_price_book.price_book_code
                ).select_related("product_code")
            }

            # Get only the filtered products
            product_codes = self.price_book_details.keys()
            return Product.objects.filter(product_code__in=product_codes)

        self.price_book_details = {}  # Empty dictionary if no price book
        return Product.objects.none()

    def list(self, request, *args, **kwargs):
        """
        Custom response format with `status`, `message`, and `results`.
        Pass `price_book` and `price_book_details` to the serializer.
        """
        queryset = self.get_queryset()  # Calls optimized get_queryset()
        serializer = self.get_serializer(
            queryset,
            many=True,
            context={
                "latest_price_book": self.latest_price_book,
                "price_book_details": self.price_book_details,
            },
        )
        response_data = {
            "status": "success",
            "message": "Data fetched successfully",
            "results": serializer.data,
            "latest_price_book": self.latest_price_book.price_book_code,
        }
        return Response(response_data)


class LocalSaleViewSet(viewsets.ModelViewSet):
    queryset = LocalSaleTxn.objects.all()
    serializer_class = LocalSaleTxnSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_serializer_context(self):
        return {"request": self.request}

    def get_queryset(self):
        queryset = super().get_queryset()
        device = self.request.user.device
        mpp = Mpp.objects.filter(mpp_ex_code=device.mpp_code).last()
        return queryset.filter(
            local_sale_code__mpp_code=mpp.mpp_code,
            local_sale_code__status__in=["Pending", "Approved"],
        )

    def list(self, request, *args, **kwargs):
        product_id = request.query_params.get("product_id", None)
        start_date = request.query_params.get("start_date", None)
        end_date = request.query_params.get("end_date", None)
        queryset = self.get_queryset()
        if product_id:
            queryset = queryset.filter(product_code__product_code=product_id)
        if not start_date == "null" and not end_date == "null":
            queryset = queryset.filter(
                local_sale_code__transaction_date__range=[start_date, end_date]
            )
        aggregated_data = queryset.aggregate(
            total_qty=Sum("qty"),
            total_amount=Sum("amount"),
            avg_rate=Avg("rate"),
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(
                {
                    "status": "success",
                    "message": "Data fetched successfully",
                    "aggregated_data": aggregated_data,
                    "results": serializer.data,
                }
            )

        # Serialize and return response
        serializer = self.get_serializer(queryset, many=True)
        response_data = {
            "status": "success",
            "message": "Data fetched successfully",
            "aggregated_data": aggregated_data,
            "results": serializer.data,
        }
        return Response(response_data)


class CustomPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"

    def get_paginated_response(self, data):
        return Response(
            {
                "status": "success",
                "status_code": 200,
                "message": "Data fetched successfully",
                "pagination": {
                    "count": self.page.paginator.count,
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                    "page_size": self.page_size,
                },
                "results": data,
            }
        )


class MemberHierarchyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A ViewSet for viewing MemberHierarchy data with additional last 15 days data.
    """

    queryset = MemberHierarchyView.objects.all()
    serializer_class = MemberHierarchyViewSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]
    filterset_class = MemberHeirarchyFilter
    filter_backends = [DjangoFilterBackend]
    search_fields = ["member_name", "member_code", "member_tr_code"]
    ordering_fields = ["member_name"]

    def get_queryset(self):
        queryset = super().get_queryset()
        device = self.request.user.device
        mpp = Mpp.objects.filter(mpp_ex_code=device.mpp_code).last()
        # mpp = Mpp.objects.filter(mpp_ex_code="1008").last()
        if not mpp:
            return MemberHierarchyView.objects.none()
        return queryset.filter(mpp_code=mpp.mpp_code).order_by("member_name")

    def list(self, request, *args, **kwargs):
        from datetime import timedelta, datetime

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            main_data = self.get_serializer(page, many=True).data
            paginated_response = self.get_paginated_response(main_data)
        else:
            main_data = self.get_serializer(queryset, many=True).data
            paginated_response = {"results": main_data}

        # Calculate the last 15 days
        # fixed_date = datetime(2024, 3, 28, 0, 0, 0)
        # last_15_days_date = fixed_date - timedelta(days=15)
        last_15_days_date = timezone.now() - timedelta(days=15)
        last_15_days_data = queryset.filter(created_at__gte=last_15_days_date)
        last_15_days_serializer = self.get_serializer(last_15_days_data, many=True)

        # Add last 15 days data to the response
        paginated_response.data["last_15_days"] = last_15_days_serializer.data
        return Response(paginated_response.data)


class NewsViewSet(viewsets.ModelViewSet):
    from rest_framework.filters import OrderingFilter

    queryset = News.objects.all()
    serializer_class = NewsSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["is_published", "is_read", "module"]
    ordering_fields = ["published_date", "updated_date"]
    pagination_class = CustomPagination
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    def get_queryset(self):
        """
        Optionally filter queryset by date range, search term,
        and default module='member'
        """
        queryset = super().get_queryset()
        request = self.request

        # --- default module filtering ---
        module = request.GET.get("module", "member")
        queryset = queryset.filter(module=module)

        # --- optional date filtering ---
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        if start_date and end_date:
            try:
                queryset = queryset.filter(
                    published_date__date__range=[start_date, end_date]
                )
            except Exception as e:
                raise exceptions.ValidationError(
                    {"error": f"Invalid date range provided: {str(e)}"}
                )

        # --- optional search filtering ---
        search = request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(summary__icontains=search)
                | Q(content__icontains=search)
            )

        return queryset

    def list(self, request, *args, **kwargs):
        """
        Customize the response for list API.
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(data=serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "status": "success",
                    "status_code": 200,
                    "results": len(serializer.data),
                    "message": "News articles retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except exceptions.ValidationError as e:
            return Response(
                {
                    "status": "error",
                    "status_code": 400,
                    "message": "Validation error.",
                    "errors": e.detail,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "status_code": 500,
                    "message": "An unexpected error occurred.",
                    "errors": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def retrieve(self, request, *args, **kwargs):
        """
        Customize the response for retrieve API.
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(
                {
                    "status": "success",
                    "status_code": 200,
                    "message": "News article retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "status_code": 404,
                    "message": "News article not found.",
                    "errors": str(e),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    def create(self, request, *args, **kwargs):
        """
        Customize the response for create API.
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {
                    "status": "success",
                    "status_code": 201,
                    "message": "News article created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except exceptions.ValidationError as e:
            return Response(
                {
                    "status": "error",
                    "status_code": 400,
                    "message": "Validation error.",
                    "errors": e.detail,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "status_code": 500,
                    "message": "An unexpected error occurred.",
                    "errors": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def update(self, request, *args, **kwargs):
        """
        Customize the response for update API.
        """
        try:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(
                {
                    "status": "success",
                    "status_code": 200,
                    "message": "News article updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except exceptions.ValidationError as e:
            return Response(
                {
                    "status": "error",
                    "status_code": 400,
                    "message": "Validation error.",
                    "errors": e.detail,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "status_code": 500,
                    "message": "An unexpected error occurred.",
                    "errors": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def destroy(self, request, *args, **kwargs):
        """
        Customize the response for delete API.
        """
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {
                    "status": "success",
                    "status_code": 204,
                    "message": "News article deleted successfully.",
                },
                status=status.HTTP_204_NO_CONTENT,
            )
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "status_code": 500,
                    "message": "An unexpected error occurred.",
                    "errors": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class NewsNotReadCountAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        not_read_count = News.objects.filter(is_read=False).count()
        return Response({"not_read_count": not_read_count})


from erp_app.models import BillingMemberMaster


class BillingMemberMasterRowFilter(FilterSet):
    from_date = DateTimeFromToRangeFilter()
    to_date = DateTimeFromToRangeFilter()

    class Meta:
        model = BillingMemberMaster
        fields = ["from_date", "to_date", "mpp_code"]


class MemberMasterViewSet(viewsets.ModelViewSet):
    queryset = MemberMaster.objects.all()
    serializer_class = MemberMasterSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["member_code", "member_name", "is_active"]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Member Masters retrieved successfully",
                "results": serializer.data,
            }
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Member Master retrieved successfully",
                "results": serializer.data,
            }
        )


class BankViewSet(viewsets.ModelViewSet):
    queryset = Bank.objects.all()
    serializer_class = BankSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["bank_name", "is_active", "nationalized_bank"]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Banks retrieved successfully",
                "results": serializer.data,
            }
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Bank retrieved successfully",
                "results": serializer.data,
            }
        )


class BillingMemberMasterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BillingMemberMaster.objects.all()
    serializer_class = BillingMemberMasterSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = BillingMemberMasterRowFilter
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Billing Member Master Rows retrieved successfully",
                "results": serializer.data,
            }
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Billing Member Master Row retrieved successfully",
                "results": serializer.data,
            }
        )


class BillingMemberDetailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BillingMemberDetail.objects.all()
    serializer_class = BillingMemberDetailSerializer
    # pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["member_code", "billing_member_master_code"]
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return BillingMemberDetail.objects.all()
        billing_master_code = self.request.GET.get("billing_member_master_code")
        return BillingMemberDetail.objects.filter(
            billing_member_master_code=billing_master_code
        )

    def get_serializer_context(self):
        return {"request": self.request}

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(
            queryset, many=True, context={"request": request}
        )
        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Billing Member Details retrieved successfully",
                "results": serializer.data,
            }
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Billing Member Detail retrieved successfully",
                "results": serializer.data,
            }
        )


class MppViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Mpp.objects.all()
    serializer_class = MppSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["mpp_ex_code"]
    search_fields = ["mpp_name", "mpp_ex_code"]
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Mpp list retrieved successfully",
                "results": serializer.data,
            }
        )


    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Mpp retrieved successfully",
                "results": serializer.data,
            }
        )


class LocalSaleTxnFilter(FilterSet):
    installment_start_date = DateFromToRangeFilter(
        field_name="local_sale_code__installment_start_date"
    )

    class Meta:
        model = LocalSaleTxn
        fields = ["installment_start_date", "local_sale_code__module_code"]


class LocalSaleTxnViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LocalSaleTxn.objects.all()
    serializer_class = DeductionTxnSerializer
    filter_backends = [DjangoFilterBackend]
    pagination_class = StandardResultsSetPagination
    filterset_class = LocalSaleTxnFilter
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(local_sale_code__status__in=["Pending", "Approved"])
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Local sale transactions retrieved successfully",
                "results": serializer.data,
            }
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Local sale transaction retrieved successfully",
                "results": serializer.data,
            }
        )


class NewSahayakDashboardAPI(APIView):
    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        created_date = request.GET.get("date", timezone.now().date())
        mpp_code = request.GET.get("mpp_code")
        shift_code = request.GET.get("shift_code")

        if not mpp_code:
            return Response(
                {"status": "error", "message": "Please provide the MPP code"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Caching: Store and retrieve results from cache
        cache_key = f"sahayak_dashboard_{mpp_code}_{shift_code}_{created_date}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        dispatches = self.get_aggregates(
            MppDispatchTxn,
            "dispatch_qty",
            "fat",
            "snf",
            mpp_dispatch_code__mpp_code=mpp_code,
            mpp_dispatch_code__from_date__date=created_date,
            mpp_dispatch_code__from_shift=shift_code,
        )

        # Construct response data
        response_data = {
            "status": 200,
            "message": _("Data Retrieved"),
            "data": {
                "dispatch": self.format_aggregates(dispatches),
            },
        }

        # Store in cache for 5 minutes
        cache.set(cache_key, response_data, timeout=300)
        return Response(response_data, status=status.HTTP_200_OK)

    def get_aggregates(self, model, qty_field, fat_field, snf_field, **filters):
        """
        Optimized function to compute aggregations efficiently.
        """
        aggregation = model.objects.filter(**filters).aggregate(
            qty=Sum(qty_field),
            fat=Coalesce(
                Cast(
                    Sum(F(qty_field) * F(fat_field), output_field=FloatField()),
                    FloatField(),
                )
                / Cast(Sum(qty_field), FloatField()),
                0.0,
            ),
            snf=Coalesce(
                Cast(
                    Sum(F(qty_field) * F(snf_field), output_field=FloatField()),
                    FloatField(),
                )
                / Cast(Sum(qty_field), FloatField()),
                0.0,
            ),
        )
        return aggregation

    def format_aggregates(self, aggregates):
        """
        Rounds float values for better readability.
        """
        return {
            key: round(value, 2) if value is not None else 0.0
            for key, value in aggregates.items()
        }


class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = get_object_or_404(self.queryset, pk=kwargs["pk"])
        serializer = self.get_serializer(instance)
        return JsonResponse(serializer.data)


class MppIncentiveSummaryAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request):
        mpp_code = request.GET.get("mpp_code")
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        if not mpp_code:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Please select MPP code.",
                    "results": [],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate start_date and end_date
        if not start_date or not end_date:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Start date and end date are required.",
                    "results": [],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Parse dates
        start_date_parsed = parse_date(start_date)
        end_date_parsed = parse_date(end_date)

        if not start_date_parsed or not end_date_parsed:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Invalid date format. Use YYYY-MM-DD.",
                    "results": [],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Filter records in date range
        collections = RmrdMilkCollection.objects.filter(
            module_code=mpp_code,
            collection_date__date__range=(
                start_date_parsed,
                end_date_parsed,
            ),
        )

        # Weighted aggregation
        aggregation = collections.aggregate(
            qty=Sum("qty"),
            fat=Coalesce(
                Cast(Sum(F("qty") * F("fat"), output_field=FloatField()), FloatField())
                / Cast(Sum("qty"), FloatField()),
                0.0,
            ),
            snf=Coalesce(
                Cast(Sum(F("qty") * F("snf"), output_field=FloatField()), FloatField())
                / Cast(Sum("qty"), FloatField()),
                0.0,
            ),
        )

        qty = aggregation["qty"] or 0
        fat = round(aggregation["fat"], 2) or 0
        snf = round(aggregation["snf"], 2) or 0

        # Calculate incentive
        efu = fat + (snf * 2 / 3)
        rupee_per_ltr = efu * 0.096
        incentive = rupee_per_ltr * float(qty)

        # Build response
        data = {
            "status": "success",
            "message": "Incentive calculated successfully.",
            "results": {
                "fat": round(fat, 2),
                "snf": round(snf, 2),
                "qty": round(qty, 2),
                "incentive": round(incentive, 2),
            },
        }

        return Response(data)
