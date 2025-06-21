from all_imports import *
from django.contrib.auth.models import Group, Permission
from math import ceil
from rest_framework.decorators import action
from django.core.exceptions import ValidationError as DjangoValidationError
from ..serializers.users_serializers import (
    UserSerializer,
    GroupSerializer,
    PermissionSerializer,
)

from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError


class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = "page_size"
    max_page_size = 100


def custom_response(status_text, data=None, message=None, status_code=200, errors=None):
    return Response(
        {
            "status": status_text,
            "message": message or "Success",
            "data": data,
            "errors": errors,
        },
        status=status_code,
    )

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        total_items = self.page.paginator.count
        current_page = self.page.number
        per_page = self.page.paginator.per_page
        total_pages = ceil(total_items / int(per_page))

        return custom_response(
            status_text="success",
            message="Success",
            data={
                "count": total_items,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "current_page": current_page,
                "total_pages": total_pages,
                "page_size": int(per_page),
                "has_next": self.page.has_next(),
                "has_previous": self.page.has_previous(),
                "results": data,
            },
            status_code=status.HTTP_200_OK,
        )


class UserViewSet(viewsets.ModelViewSet):
    from rest_framework.filters import SearchFilter, OrderingFilter

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
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


from ..serializers.profile_serializer import UserProfile, UserProfileSerializer
from error_formatter import *


class UserProfileViewSet(viewsets.ModelViewSet):
    from rest_framework.filters import SearchFilter, OrderingFilter
    pagination_class = StandardResultsSetPagination
    queryset = UserProfile.objects.select_related("user").all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]
    filterset_fields = ["department", "user__id", "is_verified", "designation"]
    search_fields = [
        "phone_number",
        "user__username",
        "user__first_name",
        "user__email",
    ]
    @action(detail=False, methods=["get"], url_path="me")
    def get_authenticated_profile(self, request):
        try:
            profile = get_object_or_404(UserProfile, user=request.user)
            serializer = self.get_serializer(profile)
            return Response({
                "status": "success",
                "message": "Authenticated user profile fetched successfully.",
                "data": serializer.data,
                "errors": {},
            }, status=status.HTTP_200_OK)

        except Exception as exc:
            return Response({
                "status": "error",
                "message": "Failed to retrieve authenticated user profile.",
                "data": {},
                "errors": {"non_field_errors": [str(exc)]},
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page or queryset, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        try:
            instance = get_object_or_404(self.get_queryset(), pk=pk)
            serializer = self.get_serializer(instance)
            return custom_response(
                status_text="success",
                status_code=status.HTTP_200_OK,
                message="User profile retrieved successfully.",
                data=serializer.data,
            )
        except ValidationError as exc:
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
        except ValidationError as exc:
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
        except ValidationError as exc:
            return custom_response(
                status_text="error",
                status_code=status.HTTP_400_BAD_REQUEST,
                message=simplify_errors(exc.detail),
            )

        except (IntegrityError, DatabaseError) as db_err:
            return custom_response(
                status_text="error",
                status_code=status.HTTP_400_BAD_REQUEST,
                message=format_exception(str(db_err)),
            )
        except Exception as exc:
            return custom_response(
                status_text="error",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=format_exception(str(exc)),
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
        except ValidationError as exc:
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
