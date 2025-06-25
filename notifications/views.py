from .permissions import IsNotificationOwner
from math import ceil
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.core.exceptions import ObjectDoesNotExist
from .models import AppNotification
from .serializers import AppNotificationSerializer
from error_formatter import simplify_errors, format_exception
from rest_framework.views import APIView
from django.utils.translation import gettext_lazy as _

def custom_response(status_text, data=None, message=None, errors=None, status_code=200):
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


class AppNotificationViewSet(viewsets.ModelViewSet):
    serializer_class = AppNotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsNotificationOwner]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter]
    ordering = ["-created_at"]

    def get_queryset(self):
        return AppNotification.objects.filter(recipient=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(
            queryset, many=True, context={"request": request}
        )
        return custom_response(
            status_text="success",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
            message="Sucess",
        )

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, context={"request": request})
            return custom_response(
                status_text="success",
                message="Notification retrieved successfully",
                data=serializer.data,
            )
        except ObjectDoesNotExist:
            return custom_response(
                status_text="error",
                message="Notification not found.",
                errors={"detail": "Invalid ID"},
                status_code=status.HTTP_404_NOT_FOUND,
            )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save(recipient=request.user)
            return custom_response(
                status_text="success",
                message="Notification created successfully.",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED,
            )
        except ValidationError as exc:
            return custom_response(
                status_text="error",
                message="Validation failed.",
                errors=simplify_errors(error_dict=exc.detail),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial, context={"request": request}
        )
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return custom_response(
                status_text="success",
                message="Notification updated successfully.",
                data=serializer.data,
            )
        except ValidationError as exc:
            return custom_response(
                status_text="error",
                message="Validation failed.",
                errors=simplify_errors(error_dict=exc.detail),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return custom_response(
            status_text="success",
            message="Notification deleted successfully.",
            data=None,
            status_code=status.HTTP_204_NO_CONTENT,
        )


class UnreadNotificationCountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargsl̥):
        user = request.user
        count = AppNotification.objects.filter(recipient=user, is_read=False).count()
        return custom_response(
            status_text="success",
            data={"unread_count": count},
            message=_("Unread notification count retrieved successfully."),
        )
