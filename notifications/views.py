from .permissions import IsNotificationOwner
from django.db import models
from rest_framework import viewsets, permissions, status, filters, generics
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.core.exceptions import ObjectDoesNotExist
from error_formatter import simplify_errors, format_exception
from rest_framework.views import APIView
from django.utils.translation import gettext_lazy as _
from rest_framework.decorators import api_view, permission_classes, action
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from .model import Notification, NotificationPreferences
from .serializers import (
    NotificationSerializer,
    NotificationPreferencesSerializer,
)
from .notification_service import NotificationServices
from util.response import (
    custom_response,
    StandardResultsSetPagination,
    handle_custom_exceptions,
    ExceptionHandlerMixin,
    transaction,
    IntegrityError,
)

class UnreadNotificationCountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        count = Notification.objects.filter(recipient=user, is_read=False).count()
        return custom_response(
            status_text="success",
            data={"unread_count": count},
            message=_("Unread notification count retrieved successfully."),
        )


# app_name/views.py
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters import rest_framework as df_filters


class NotificationFilter(df_filters.FilterSet):
    # expose 'category' as template__category
    category = df_filters.CharFilter(
        field_name="template__category", lookup_expr="iexact"
    )

    # boolean filter; also support a flexible 'read' alias (accepts true/false strings)
    is_read = df_filters.BooleanFilter(field_name="is_read")
    read = df_filters.CharFilter(method="filter_read", label="read (alias for is_read)")

    notification_type = df_filters.CharFilter(
        field_name="notification_type", lookup_expr="iexact"
    )
    priority = df_filters.CharFilter(field_name="priority", lookup_expr="iexact")

    def filter_read(self, queryset, name, value):
        if value is None:
            return queryset
        v = str(value).lower()
        if v in ("true", "1", "t", "yes", "y"):
            return queryset.filter(is_read=True)
        if v in ("false", "0", "f", "no", "n"):
            return queryset.filter(is_read=False)
        # if ambiguous, return unfiltered queryset (or you can choose to return none)
        return queryset

    class Meta:
        model = Notification
        fields = ["category", "is_read", "notification_type", "priority", "read"]


# ---- List view ----
class NotificationListView(ExceptionHandlerMixin, generics.ListAPIView):
    """
    List user's notifications with explicit filtering fields:
    - ?category=...          -> template__category (case-insensitive exact)
    - ?is_read=true|false    -> boolean
    - ?read=true|false       -> alias for is_read (more lenient parsing)
    - ?notification_type=...
    - ?priority=...
    - ?search=...            -> searches title & body (icontains)
    - ordering via ?ordering=created_at or ?ordering=-created_at
    """

    serializer_class = NotificationSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [df_filters.DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = NotificationFilter
    search_fields = ["title", "body"]
    ordering_fields = ["created_at", "priority", "notification_type"]
    ordering = ["-created_at"]

    def get_queryset(self):
        # keep queryset minimal and performant; select_related where appropriate
        return Notification.objects.filter(recipient=self.request.user).select_related(
            "template", "sender"
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(
                page, many=True, context={"request": request}
            )
            # convert DRF pagination response to your custom_response format
            paginated = self.get_paginated_response(
                serializer.data
            )  # returns DRF Response
            return custom_response(
                status_text="success",
                message="Notifications retrieved successfully.",
                data=paginated.data,
                status_code=status.HTTP_200_OK,
            )

        serializer = self.get_serializer(
            queryset, many=True, context={"request": request}
        )
        return custom_response(
            status_text="success",
            message="Notifications retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


# ---- Detail view ----
class NotificationDetailView(ExceptionHandlerMixin, generics.RetrieveAPIView):
    """
    Retrieve single notification (by uuid) and auto-mark as read.
    """

    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "uuid"

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).select_related(
            "template", "sender"
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()  # exceptions handled by mixin.handle_exception
        # Auto-mark as read
        if not instance.is_read:
            # mark_as_read may raise DB errors; mixin will format those
            instance.mark_as_read()

        serializer = self.get_serializer(instance, context={"request": request})
        return custom_response(
            status_text="success",
            message="Notification retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
@handle_custom_exceptions()
def mark_notification_read(request, uuid):
    """Mark a specific notification as read"""
    notification = get_object_or_404(Notification, uuid=uuid, recipient=request.user)
    notification.mark_as_read()

    return custom_response(
        status_text="success",
        message="Notification marked as read.",
        data={},
        status_code=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
@handle_custom_exceptions()
def mark_all_read(request):
    """Mark all notifications as read"""
    category = request.data.get("category")
    service = NotificationServices()
    count = service.mark_all_read(request.user, category)

    return custom_response(
        status_text="success",
        message=f"Marked {count} notifications as read.",
        data={"count": count},
        status_code=status.HTTP_200_OK,
    )


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
@handle_custom_exceptions()
def archive_notification(request, uuid):
    """Archive a notification"""
    notification = get_object_or_404(Notification, uuid=uuid, recipient=request.user)
    notification.is_archived = True
    notification.save(update_fields=["is_archived"])

    return custom_response(
        status_text="success",
        message="Notification archived.",
        data={},
        status_code=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
@handle_custom_exceptions()
def notification_stats(request):
    """Get notification statistics for the user"""
    user = request.user
    total = Notification.objects.filter(recipient=user).count()
    unread = Notification.objects.filter(recipient=user, is_read=False).count()

    categories = (
        Notification.objects.filter(recipient=user)
        .values("template__category")
        .annotate(
            total=models.Count("id"),
            unread=models.Count("id", filter=models.Q(is_read=False)),
        )
        .order_by("template__category")
    )

    return custom_response(
        status_text="success",
        message="Retrieved notification stats.",
        data={
            "total": total,
            "unread": unread,
            "read": total - unread,
            "categories": list(categories),
        },
        status_code=status.HTTP_200_OK,
    )


class NotificationPreferencesView(ExceptionHandlerMixin, generics.ListCreateAPIView):
    """
    List and create notification preferences
    """

    pagination_class = StandardResultsSetPagination
    serializer_class = NotificationPreferencesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return NotificationPreferences.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page or queryset, many=True)

        response_data = {
            "success": True,
            "message": "Notification preferences retrieved successfully.",
            "data": serializer.data,
        }
        return (
            self.get_paginated_response(response_data)
            if page
            else self.success_response(response_data)
        )

    def perform_create(self, serializer):
        try:
            with transaction.atomic():
                serializer.save(user=self.request.user)
        except IntegrityError:
            raise IntegrityError("A preference with these details already exists.")


class NotificationPreferencesUpdateView(ExceptionHandlerMixin, generics.UpdateAPIView):
    """
    Update notification preferences
    """

    serializer_class = NotificationPreferencesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return NotificationPreferences.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except ObjectDoesNotExist:
            return self.error_response(
                message="Notification preference not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                self.perform_update(serializer)
        except IntegrityError:
            return self.error_response(
                message="Database integrity error while updating preference.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return self.success_response(
            message="Notification preference updated successfully.",
            data=serializer.data,
        )
