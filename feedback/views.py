from all_imports import *
from math import ceil
from rest_framework.filters import SearchFilter, OrderingFilter
from error_formatter import format_exception, simplify_errors
from .serializers.feedback_serializer import (
    FeedbackSerializer,
    Feedback,
    FeedbackFile,
    FeedbackFileSerializer,
)


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


# Create your views here.


from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg, DurationField, ExpressionWrapper, F
from django.utils.timezone import now
from datetime import timedelta


class FeedbackViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Feedback operations with custom responses and pagination.
    Integrates status transitions, base64 file upload, comment creation, and locale-based translations.
    """

    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "priority","assigned_to"]
    search_fields = [
        "mpp_code",
        "mcc_code",
        "member_code",
        "member_tr_code",
        "name",
        "mobile_no",
    ]

    def get_queryset(self):
        """
        Restrict to feedbacks created by the authenticated user unless superuser.
        """
        if not self.request.user.is_superuser:
            return self.queryset.filter(sender=self.request.user)
        return self.queryset

    def perform_create(self, serializer):
        """
        Automatically set the authenticated user as the sender during feedback creation.
        """
        serializer.save(sender=self.request.user)

    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        """
        Return feedback statistics: total count, by status, priority, and avg response time.
        """
        user_filter = {} if request.user.is_superuser else {"sender": request.user}

        # Aggregate counts
        total = Feedback.objects.filter(**user_filter).count()
        by_status = (
            Feedback.objects.filter(**user_filter)
            .values("status")
            .annotate(count=Count("id"))
        )
        by_priority = (
            Feedback.objects.filter(**user_filter)
            .values("priority")
            .annotate(count=Count("id"))
        )

        # Optional: average response time (if you track resolution/updated timestamp)
        avg_response_time = None
        if hasattr(Feedback, "resolved_at") and hasattr(Feedback, "created_at"):
            resolved_feedbacks = Feedback.objects.filter(
                resolved_at__isnull=False, **user_filter
            ).annotate(
                response_time=ExpressionWrapper(
                    F("resolved_at") - F("created_at"), output_field=DurationField()
                )
            )
            avg_response_time = resolved_feedbacks.aggregate(avg=Avg("response_time"))[
                "avg"
            ]
            response_data = {
                "total": total,
                "by_status": list(by_status),
                "by_priority": list(by_priority),
                "average_response_time": (
                    avg_response_time.total_seconds() if avg_response_time else None
                ),
            }
        return custom_response(
            status_text="success",
            message="Stats loaded",
            data=response_data,
            status_code=status.HTTP_200_OK,
        )

    def list(self, request, *args, **kwargs):
        """
        Override the list response to include a custom format with locale support.
        """
        locale = request.query_params.get("locale", "en")
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(
            page if page is not None else queryset,
            many=True,
            context={"request": request, "locale": locale},
        )

        response_data = {
            "status": "success",
            "status_code": status.HTTP_200_OK,
            "message": "Feedbacks retrieved successfully.",
            "results": serializer.data,
        }

        return (
            self.get_paginated_response(serializer.data)
            if page is not None
            else Response(response_data)
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {
                    "status": "success",
                    "status_code": status.HTTP_201_CREATED,
                    "message": "Feedback created successfully.",
                    "results": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except ValidationError:
            friendly = simplify_errors(exc.detail)
            return custom_response(
                status_text="error",
                status_code=status.HTTP_400_BAD_REQUEST,
                message=f"{friendly}",
                data={},
            )

        except Exception as e:
            return custom_response(
                status_text="error",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"{format_exception(e)}",
                data={},
            )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial, context={"request": request}
        )
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(
                {
                    "status": "success",
                    "status_code": status.HTTP_200_OK,
                    "message": "Feedback updated successfully.",
                    "results": serializer.data,
                }
            )
        except ValidationError:
            friendly = simplify_errors(exc.detail)
            return custom_response(
                status_text="error",
                status_code=status.HTTP_400_BAD_REQUEST,
                message=f"{friendly}",
                data={},
            )

        except Exception as e:
            return custom_response(
                status_text="error",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"{format_exception(e)}",
                data={},
            )

    def destroy(self, request, *args, **kwargs):
        """
        Override the delete response to include a soft delete with custom format.
        """
        instance = self.get_object()
        instance.deleted = True
        instance.save()
        return custom_response(
            status_text="success",
            status_code=status.HTTP_204_NO_CONTENT,
            message="Feedback deleted successfully.",
        )


class FeedbackFileViewsets(viewsets.ModelViewSet):
    queryset = FeedbackFile.objects.all()
    pagination_class = StandardResultsSetPagination
    serializer_class = FeedbackFileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]
    filterset_fields = ["feedback__id"]

    def list(self, request, *args, **kwargs):
        """
        Override the list response to include a custom format with locale support.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(
            page if page is not None else queryset,
            many=True,
            context={"request": request},
        )

        response_data = {
            "status": "success",
            "status_code": status.HTTP_200_OK,
            "message": "Feedbacks retrieved successfully.",
            "results": serializer.data,
        }

        return (
            self.get_paginated_response(serializer.data)
            if page is not None
            else Response(response_data)
        )
