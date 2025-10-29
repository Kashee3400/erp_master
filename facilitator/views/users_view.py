from all_imports import *
from django.contrib.auth.models import Group, Permission
from math import ceil
from rest_framework.decorators import action
from django.core.exceptions import ValidationError as DjangoValidationError
from ..serializers.users_serializers import (
    UserSerializer,
    GroupSerializer,
    PermissionSerializer,
    VerifyOTPSerializer,
    SendOTPSerializer,
)

from rest_framework.pagination import PageNumberPagination
from util.response import StandardResultsSetPagination, custom_response

from ..serializers.profile_serializer import (
    UserProfile,
    UserProfileSerializer,
    UserUpdateProfileSerializer,
    UserUpdateSerializer,
)
from error_formatter import *
from rest_framework.parsers import MultiPartParser, FormParser


class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = "page_size"
    max_page_size = 100


class UserViewSet(viewsets.ModelViewSet):
    from rest_framework.filters import SearchFilter, OrderingFilter

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filterset_fields = ["is_active", "is_staff", "groups", "is_superuser"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering_fields = ["username", "email", "date_joined", "last_login"]
    lookup_field = "pk"
    filter_backends = [
        SearchFilter,
        OrderingFilter,
        DjangoFilterBackend,
    ]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page or queryset, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=["post"], url_path="bulk-delete")
    def bulk_delete(self, request):
        ids = request.data.get("ids", [])
        user = self.request.user
        if not (
            (user.is_superuser or user.is_staff) and user.has_perm("auth.delete_user")
        ):
            return custom_response(
                status_text="error",
                message="You do not have permission to perform bulk deletion.",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        if not isinstance(ids, list) or not ids:
            return custom_response(
                status_text="error",
                message="Please provide a list of user IDs to delete.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Filter users by provided IDs and delete them
        users_to_delete = self.queryset.filter(id__in=ids)

        count = users_to_delete.count()
        if count == 0:
            return custom_response(
                status_text="error",
                message="No matching users found to delete.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        users_to_delete.delete()

        return custom_response(
            status_text="success",
            message=f"Successfully deleted {count} user(s).",
            status_code=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return custom_response("success", serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return custom_response(
                "success",
                serializer.data,
                message="User created",
                status_code=status.HTTP_201_CREATED,
            )

        except DjangoValidationError as e:
            flat_message = (
                "; ".join(
                    f"{field}: {', '.join(map(str, errors))}"
                    for field, errors in e.detail.items()
                )
                if isinstance(e.detail, dict)
                else str(e.detail)
            )

            return custom_response(
                "error",
                data=e.detail,
                message=flat_message,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        except (IntegrityError, DjangoValidationError) as e:
            return custom_response(
                "error",
                message=f"Validation error: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            return custom_response(
                "error",
                message=f"Unexpected error: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return custom_response("success", serializer.data, message="User updated")

        except ValidationError as e:
            flat_message = (
                "; ".join(
                    f"{field}: {', '.join(map(str, errors))}"
                    for field, errors in e.detail.items()
                )
                if isinstance(e.detail, dict)
                else str(e.detail)
            )

            return custom_response(
                "error",
                data=e.detail,
                message=flat_message,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        except (IntegrityError, DjangoValidationError) as e:
            return custom_response(
                "error",
                message=f"Validation error: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            return custom_response(
                "error",
                message=f"Unexpected error: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        self.perform_destroy(user)
        return custom_response("success", message="User deleted", data=None)

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """
        Get comprehensive user statistics
        """
        total_users = self.get_queryset().count()
        active_users = self.get_queryset().filter(is_active=True).count()
        inactive_users = self.get_queryset().filter(is_active=False).count()
        staff_users = self.get_queryset().filter(is_staff=True).count()
        superusers = self.get_queryset().filter(is_superuser=True).count()

        # Users with groups
        users_with_groups = (
            self.get_queryset().filter(groups__isnull=False).distinct().count()
        )
        users_without_groups = total_users - users_with_groups

        return custom_response(
            status_text="success",
            data={
                "total_users": total_users,
                "active_users": active_users,
                "inactive_users": inactive_users,
                "staff_users": staff_users,
                "superusers": superusers,
                "users_with_groups": users_with_groups,
                "users_without_groups": users_without_groups,
                "activity_rate": (
                    round((active_users / total_users * 100), 2)
                    if total_users > 0
                    else 0
                ),
            },
            message="Stats fetched",
            status_code=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def registration_stats(self, request):
        """
        Get user registration statistics by time periods
        """
        now = timezone.now()
        today = now.date()

        # Registration counts
        today_registrations = (
            self.get_queryset().filter(date_joined__date=today).count()
        )

        week_ago = now - timedelta(days=7)
        week_registrations = (
            self.get_queryset().filter(date_joined__gte=week_ago).count()
        )

        month_ago = now - timedelta(days=30)
        month_registrations = (
            self.get_queryset().filter(date_joined__gte=month_ago).count()
        )

        year_ago = now - timedelta(days=365)
        year_registrations = (
            self.get_queryset().filter(date_joined__gte=year_ago).count()
        )

        return custom_response(
            status_text="success",
            status_code=status.HTTP_200_OK,
            message="User registration stats fetched",
            data={
                "today": today_registrations,
                "last_7_days": week_registrations,
                "last_30_days": month_registrations,
                "last_365_days": year_registrations,
            },
        )

    @action(detail=False, methods=["get"])
    def login_stats(self, request):
        """
        Get user login activity statistics
        """
        now = timezone.now()

        # Users who logged in recently
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        logged_in_today = self.get_queryset().filter(last_login__gte=day_ago).count()

        logged_in_week = self.get_queryset().filter(last_login__gte=week_ago).count()

        logged_in_month = self.get_queryset().filter(last_login__gte=month_ago).count()

        never_logged_in = self.get_queryset().filter(last_login__isnull=True).count()

        return custom_response(
            status_text="success",
            status_code=status.HTTP_200_OK,
            message="User login activity stats fetched",
            data={
                "logged_in_last_24h": logged_in_today,
                "logged_in_last_7_days": logged_in_week,
                "logged_in_last_30_days": logged_in_month,
                "never_logged_in": never_logged_in,
            },
        )

    @action(detail=False, methods=["get"])
    def group_stats(self, request):
        """
        Get statistics about user groups
        """
        # Group distribution
        group_stats = (
            self.get_queryset()
            .values("groups__name")
            .annotate(user_count=Count("id"))
            .filter(groups__name__isnull=False)
            .order_by("-user_count")
        )

        # Users per group count
        users_by_group_count = (
            self.get_queryset()
            .annotate(group_count=Count("groups"))
            .values("group_count")
            .annotate(user_count=Count("id"))
            .order_by("group_count")
        )

        group_data = {
            "groups_distribution": list(group_stats),
            "users_by_group_count": list(users_by_group_count),
        }

        return custom_response(
            status_text="success",
            data=group_data,
            message="Group statistics retrieved successfully",
        )

    @action(detail=False, methods=["get"])
    def monthly_registration_trend(self, request):
        """
        Get monthly registration trend for the last 12 months
        """

        now = timezone.now()
        year_ago = now - timedelta(days=365)

        monthly_stats = (
            self.get_queryset()
            .filter(date_joined__gte=year_ago)
            .extra(
                select={
                    "month": "EXTRACT(month FROM date_joined)",
                    "year": "EXTRACT(year FROM date_joined)",
                }
            )
            .values("month", "year")
            .annotate(count=Count("id"))
            .order_by("year", "month")
        )

        return custom_response(
            status_text="success",
            data=list(monthly_stats),
            message="Registration trend retrieved successfully",
        )

    @action(detail=False, methods=["get"])
    def user_type_breakdown(self, request):
        """
        Get breakdown of different user types
        """
        breakdown = {
            "regular_users": self.get_queryset()
            .filter(is_staff=False, is_superuser=False)
            .count(),
            "staff_only": self.get_queryset()
            .filter(is_staff=True, is_superuser=False)
            .count(),
            "superusers": self.get_queryset().filter(is_superuser=True).count(),
            "active_regular": self.get_queryset()
            .filter(is_active=True, is_staff=False, is_superuser=False)
            .count(),
            "inactive_regular": self.get_queryset()
            .filter(is_active=False, is_staff=False, is_superuser=False)
            .count(),
        }
        return custom_response(
            status_text="success",
            data=breakdown,
            message="Breakdown retrieved successfully",
            status_code=status.HTTP_200_OK,
        )


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    authentication_classes = [JWTAuthentication]
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAuthenticated, IsAdminUser]

    lookup_field = "pk"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return custom_response(
                status_text="success",
                data=serializer.data,
                message="Group created",
                status_code=status.HTTP_201_CREATED,
            )

        except ValidationError as e:
            # Generate human-readable error summary
            try:
                flat_message = "; ".join(
                    f"{field}: {', '.join(map(str, errors))}"
                    for field, errors in e.detail.items()
                )
            except Exception:
                flat_message = str(e.detail)

            return custom_response(
                status_text="error",
                data=e.detail,  # Full field-level errors
                message=flat_message,  # Human-readable message
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        except DjangoValidationError as e:
            return custom_response(
                status_text="error",
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        except IntegrityError as e:
            return custom_response(
                status_text="error",
                message="Database integrity error: " + str(e),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:

            return custom_response(
                status_text="error",
                message="An unexpected error occurred: " + str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"], url_path="bulk-delete")
    def bulk_delete(self, request):
        ids = request.data.get("ids", [])
        user = self.request.user
        if not (
            (user.is_superuser or user.is_staff) and user.has_perm("auth.delete_user")
        ):
            return custom_response(
                status_text="error",
                message="You do not have permission to perform bulk deletion.",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        if not isinstance(ids, list) or not ids:
            return custom_response(
                status_text="error",
                message="Please provide a list of user IDs to delete.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Filter users by provided IDs and delete them
        groups_to_delete = self.queryset.filter(id__in=ids)

        count = groups_to_delete.count()
        if count == 0:
            return custom_response(
                status_text="error",
                message="No matching users found to delete.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        groups_to_delete.delete()

        return custom_response(
            status_text="success",
            message=f"Successfully deleted {count} group(s).",
            status_code=status.HTTP_200_OK,
        )

    def update(self, request, *args, **kwargs):
        group = self.get_object()
        serializer = self.get_serializer(group, data=request.data, partial=True)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return custom_response("success", serializer.data, "Group updated")

        except ValidationError as e:
            # Flatten error message
            try:
                flat_message = "; ".join(
                    f"{field}: {', '.join(map(str, errors))}"
                    for field, errors in e.detail.items()
                )
            except Exception:
                flat_message = str(e.detail)

            return custom_response(
                status_text="error",
                data=e.detail,  # For frontend form-level field errors
                message=flat_message,  # For display/snackbar
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        except DjangoValidationError as e:
            return custom_response(
                status_text="error",
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        except IntegrityError as e:
            return custom_response(
                status_text="error",
                message="Database integrity error: " + str(e),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            return custom_response(
                status_text="error",
                message="An unexpected error occurred: " + str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page or queryset, many=True)
        return self.get_paginated_response(serializer.data)

    def get_paginated_response(self, data):
        page = self.paginator.page
        page_size = self.request.GET.get("page_size", self.paginator.page_size)
        total_items = page.paginator.count
        current_page = page.number
        total_pages = ceil(total_items / int(page_size))

        return custom_response(
            status_text="success",
            message="Users fetched",
            data={
                "count": total_items,
                "next": self.paginator.get_next_link(),
                "previous": self.paginator.get_previous_link(),
                "current_page": current_page,
                "total_pages": total_pages,
                "page_size": int(page_size),
                "has_next": page.has_next(),
                "has_previous": page.has_previous(),
                "results": data,
            },
            status_code=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        group = self.get_object()
        serializer = self.get_serializer(group)
        return custom_response("success", serializer.data)

    def destroy(self, request, *args, **kwargs):
        group = self.get_object()
        self.perform_destroy(group)
        return custom_response("success", message="Group deleted")


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    from rest_framework.filters import SearchFilter

    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    authentication_classes = [JWTAuthentication]
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAuthenticated, IsAdminUser]
    lookup_field = "pk"

    filter_backends = [SearchFilter]

    search_fields = [
        "codename",
        "name",
        "content_type__app_label",
        "content_type__model",
    ]

    def retrieve(self, request, *args, **kwargs):
        permission = self.get_object()
        serializer = self.get_serializer(permission)
        return custom_response("success", serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return custom_response(
            status_text="success",
            message="Permissions fetched",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


class UserProfileViewSet(viewsets.ModelViewSet):
    from rest_framework.filters import SearchFilter, OrderingFilter

    pagination_class = StandardResultsSetPagination
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = "user_id"  # this will appear in URL: /user-profiles/<user_id>/
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["department", "user", "is_verified", "designation"]
    search_fields = [
        "phone_number",
        "user__username",
        "user__first_name",
        "user__email",
    ]

    def get_object(self):
        queryset = self.get_queryset()
        user_id = self.kwargs.get(self.lookup_field)
        return get_object_or_404(queryset, user__id=user_id)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return custom_response(
                status_text="success",
                status_code=status.HTTP_200_OK,
                message="User profile retrieved successfully.",
                data=serializer.data,
            )

        except serializers.ValidationError as exc:
            return custom_response(
                status_text="error",
                status_code=status.HTTP_400_BAD_REQUEST,
                message=simplify_errors(exc.detail),
            )
        except Exception as exc:
            return custom_response(
                status_text="error",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=format_exception(str(exc)),
            )

    def get_queryset(self):
        queryset = UserProfile.objects.select_related("user").all()
        if self.action == "list":
            queryset = queryset.exclude(user=self.request.user)
        return queryset

    @action(detail=False, methods=["get"], url_path="me")
    def get_authenticated_profile(self, request):
        try:
            profile = get_object_or_404(UserProfile, user=request.user)
            serializer = self.get_serializer(profile)
            return Response(
                {
                    "status": "success",
                    "message": "Authenticated user profile fetched successfully.",
                    "data": serializer.data,
                    "errors": {},
                },
                status=status.HTTP_200_OK,
            )

        except Exception as exc:
            return Response(
                {
                    "status": "error",
                    "message": "Failed to retrieve authenticated user profile.",
                    "data": {},
                    "errors": {"non_field_errors": [str(exc)]},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page or queryset, many=True)
        return self.get_paginated_response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return custom_response(
                status_code=status.HTTP_201_CREATED,
                status_text="success",
                message="User profile created successfully.",
                data=serializer.data,
            )
        except (IntegrityError, DatabaseError) as db_err:
            return custom_response(
                status_text="error",
                status_code=status.HTTP_400_BAD_REQUEST,
                message=format_exception(str(db_err)),
            )
        except serializers.ValidationError as exc:
            return custom_response(
                status_text="error",
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Failed to create user profile",
                errors=simplify_errors(exc.detail),
            )

        except Exception as exc:
            return custom_response(
                status_text="error",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Something error occurred",
                errors=format_exception(str(exc)),
            )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        try:
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return custom_response(
                status_text="success",
                status_code=status.HTTP_200_OK,
                message="User profile updated successfully.",
                data=serializer.data,
            )
        except serializers.ValidationError as exc:
            return custom_response(
                status_text="error",
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Failed update",
                errors=simplify_errors(exc.detail),
            )

        except (IntegrityError, DatabaseError) as db_err:
            return custom_response(
                status_text="error",
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Error Occurred",
                errors=format_exception(str(db_err)),
            )
        except Exception as exc:
            return custom_response(
                status_text="error",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Error Occurred",
                errors=format_exception(str(exc)),
            )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return custom_response(
                status_text="success",
                status_code=status.HTTP_200_OK,
                message="User profile deleted successfully.",
            )
        except serializers.ValidationError as exc:
            return custom_response(
                status_text="error",
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Failed to delete the object",
                errors=simplify_errors(exc.detail),
            )

        except Exception as exc:
            return custom_response(
                status_text="error",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Something error occurred",
                errors=format_exception(str(exc)),
            )


from django.core.cache import cache
from rest_framework.views import APIView
from django.core.mail import send_mail

import random


class SendOTPView(APIView):
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            otp = f"{random.randint(100000, 999999)}"
            cache_key = f"otp:{email}"
            cache.set(cache_key, otp, timeout=300)

            try:
                send_mail(
                    subject="Your Email Verification OTP",
                    message=f"Your OTP is: {otp}",
                    from_email=settings.HRMS_DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
            except serializers.ValidationError as err_dict:
                return custom_response(
                    status_text="error",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message=f"Failed to send email:",
                    errors=simplify_errors(error_dict=err_dict.detail),
                )
            except Exception as e:
                return custom_response(
                    status_text="error",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message=f"Failed to send email",
                    errors=str(e),
                )

            return custom_response(
                status_text="success",
                status_code=status.HTTP_200_OK,
                message="OTP sent successfully.",
            )

        return custom_response(
            status_text="error",
            status_code=status.HTTP_400_BAD_REQUEST,
            message="OTP request failed",
            errors=serializer.errors,
        )


class VerifyOTPView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data["user_id"]
            email = serializer.validated_data["email"]
            otp = serializer.validated_data["otp"]

            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return custom_response(
                    status_text="error",
                    status_code=status.HTTP_404_NOT_FOUND,
                    message="User not found.",
                )

            if user.profile.is_email_verified and user.email == email:
                return custom_response(
                    status_text="success",
                    status_code=status.HTTP_200_OK,
                    message="This email is already verified.",
                )

            cache_key = f"otp:{email}"
            cached_otp = cache.get(cache_key)

            if cached_otp is None:
                return custom_response(
                    status_text="error",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="OTP has expired or was not requested.",
                )

            if str(cached_otp) != str(otp):
                return custom_response(
                    status_text="error",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Invalid OTP provided.",
                )
            user.email = email
            try:
                profile = user.profile
            except UserProfile.DoesNotExist:
                profile = UserProfile.objects.create(user=user)
            profile.is_email_verified = True
            profile.save()
            user.save()
            cache.delete(cache_key)
            return custom_response(
                status_text="success",
                status_code=status.HTTP_200_OK,
                message="Email verified and updated successfully.",
            )

        return custom_response(
            status_text="error",
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Invalid request data",
            errors=serializer.errors,
        )


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction


@api_view(["POST", "PUT", "PATCH"])
@permission_classes([IsAuthenticated])
@transaction.atomic
def create_update_user_profile(request):
    """
    Create or update User and UserProfile in a single API call.

    POST: Create new user and profile
    PUT/PATCH: Update existing user and profile

    Expected payload:
    {
        "user": {
            "username": "john_doe",
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe"
        },
        "profile": {
            "salutation": "Mr.",
            "department": "engineering",
            "phone_number": "1234567890",
            "address": "123 Main St",
            "designation": "Senior Engineer",
            "reports_to": 1,
            "mpp_code": "MPP001"
        }
    }
    """
    try:
        user_data = request.data.get("user", {})
        profile_data = request.data.get("profile", {})
        user_id = request.data.get("user_id")
        is_update = user_id is not None

        if is_update:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return custom_response(
                    status_text="error",
                    message="User not found.",
                    errors={"user_id": ["User with this ID does not exist."]},
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            try:
                profile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist:
                return custom_response(
                    status_text="error",
                    message="User profile not found.",
                    errors={"profile": ["Profile does not exist for this user."]},
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            # Serialize and validate user data
            user_serializer = UserUpdateSerializer(user, data=user_data, partial=True)
            if not user_serializer.is_valid():
                return custom_response(
                    status_text="error",
                    message="User validation failed.",
                    errors=user_serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            # Serialize and validate profile data
            profile_serializer = UserUpdateProfileSerializer(
                profile, data=profile_data, partial=True
            )
            if not profile_serializer.is_valid():
                return custom_response(
                    status_text="error",
                    message="Profile validation failed.",
                    errors=profile_serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            # Save updated data
            user_serializer.save()
            profile_serializer.save()

            return custom_response(
                status_text="success",
                data={
                    "user_id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "profile": UserUpdateProfileSerializer(profile).data,
                },
                message="User and profile updated successfully.",
                status_code=status.HTTP_200_OK,
            )

        else:
            # Create new user and profile
            if not user_data.get("username"):
                return custom_response(
                    status_text="error",
                    message="Username is required for new user creation.",
                    errors={"user": {"username": ["This field is required."]}},
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            if not user_data.get("email"):
                return custom_response(
                    status_text="error",
                    message="Email is required for new user creation.",
                    errors={"user": {"email": ["This field is required."]}},
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            # Serialize and validate user data
            user_serializer = UserSerializer(data=user_data)
            if not user_serializer.is_valid():
                return custom_response(
                    status_text="error",
                    message="User validation failed.",
                    errors=user_serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            # Create user
            user = user_serializer.save()

            # Create profile with user foreign key
            profile_data["user"] = user.id
            profile_serializer = UserUpdateProfileSerializer(data=profile_data)

            if not profile_serializer.is_valid():
                # Delete user if profile creation fails
                user.delete()
                return custom_response(
                    status_text="error",
                    message="Profile validation failed.",
                    errors=profile_serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            profile = profile_serializer.save(user=user)

            return custom_response(
                status_text="success",
                data={
                    "user_id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "profile": UserUpdateProfileSerializer(profile).data,
                },
                message="User and profile created successfully.",
                status_code=status.HTTP_201_CREATED,
            )

    except ValidationError as e:
        return custom_response(
            status_text="error",
            message="Validation error occurred.",
            errors={"detail": str(e)},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return custom_response(
            status_text="error",
            message="An unexpected error occurred.",
            errors={"detail": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


"""
1. CREATE NEW USER AND PROFILE (POST):
POST /api/user-profile/
{
    "user": {
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe"
    },
    "profile": {
        "salutation": "Mr.",
        "department": "engineering",
        "phone_number": "9876543210",
        "address": "123 Main Street, City",
        "designation": "Senior Engineer",
        "mpp_code": "MPP001"
    }
}

2. UPDATE EXISTING USER AND PROFILE (PUT/PATCH):
PUT /api/user-profile/
{
    "user_id": 1,
    "user": {
        "first_name": "Jonathan",
        "last_name": "Doe"
    },
    "profile": {
        "designation": "Lead Engineer",
        "phone_number": "9876543211"
    }
}

3. RESPONSE EXAMPLE (SUCCESS):
{
    "status": "success",
    "message": "User and profile created successfully.",
    "data": {
        "user_id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "profile": {
            "id": 1,
            "salutation": "Mr.",
            "department": "engineering",
            "phone_number": "9876543210",
            ...
        }
    },
    "errors": null
}

4. RESPONSE EXAMPLE (ERROR):
{
    "status": "error",
    "message": "User validation failed.",
    "data": null,
    "errors": {
        "email": ["This email is already in use."]
    }
}
"""
