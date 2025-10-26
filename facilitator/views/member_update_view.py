from util.response import StandardResultsSetPagination, custom_response

from rest_framework import viewsets, status, generics
from ..serializers.member_update_serializers import *
from rest_framework.permissions import IsAuthenticated, AllowAny
from facilitator.authentication import ApiKeyAuthentication
from erp_app.models import Bank, Branch
from erp_app.serializers import BankListSerializer, BranchListSerializer

# views.py
from django.utils.translation import gettext_lazy as _
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import transaction
from django.utils import timezone
from ..choices import (
    RoleType,
    RequestStatus,
    DocumentTypeChoice,
    RequestTypeChoices,
)
from error_formatter import format_exception, simplify_errors


class UpdateRequestViewSet(viewsets.ModelViewSet):
    """
    A viewset for handling CRUD operations on UpdateRequest model.

    Provides:
    - List with pagination and filtering
    - Create new requests
    - Retrieve individual requests
    - Update requests
    - Delete requests
    - Custom actions for approval/rejection
    """

    queryset = UpdateRequest.objects.all()
    serializer_class = UpdateRequestSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    # Enable filtering, searching, and ordering
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        "status",
        "request_type",
        "role_type",
        "created_by",
        "is_deleted",
        "updated_by",
        "mcc_code",
        "mpp_ex_code",
    ]

    search_fields = [
        "request_id",
        "member_name",
        "member_ex_code",
        "mobile_number",
        "mpp_name",
    ]
    ordering_fields = ["created_at", "updated_at", "reviewed_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == "list":
            return UpdateRequestListSerializer
        return UpdateRequestSerializer

    def get_queryset(self):
        """Filter queryset based on user permissions"""
        user = self.request.user
        queryset = UpdateRequest.objects.select_related("created_by", "reviewed_by")

        # If user is not staff, only show their own requests
        if not user.is_staff:
            queryset = queryset.filter(created_by=user)

        return queryset.filter(is_deleted=False)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def create(self, request, *args, **kwargs):
        """Create a new update request"""
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                instance = serializer.save()
                response_data = UpdateRequestSerializer(instance).data
                return custom_response(
                    status_text="success",
                    message=_("Update request created successfully"),
                    data=response_data,
                    status_code=status.HTTP_201_CREATED,
                )
            else:
                return custom_response(
                    status_text="error",
                    message=_("Validation failed"),
                    errors=serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
        except serializers.ValidationError as e:
            return custom_response(
                status_text="error",
                message=_("An error occurred while creating the request"),
                errors=simplify_errors(error_dict=e.detail),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return custom_response(
                status_text="error",
                message=_("An error occurred while creating the request"),
                errors=format_exception(exc=e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific update request"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)

            return custom_response(
                status_text="success",
                message=_("Request retrieved successfully"),
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )
        except UpdateRequest.DoesNotExist:
            return custom_response(
                status_text="error",
                message=_("Request not found"),
                status_code=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return custom_response(
                status_text="error",
                message=_("An error occurred while retrieving the request"),
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def update(self, request, *args, **kwargs):
        """Update an existing update request"""
        try:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()

            # Check if user can update this request
            if not request.user.is_staff and instance.created_by != request.user:
                return custom_response(
                    status_text="error",
                    message=_("You don't have permission to update this request"),
                    status_code=status.HTTP_403_FORBIDDEN,
                )

            # Check if request is in a state that allows updates
            if instance.status in [RequestStatus.APPROVED, RequestStatus.REJECTED]:
                return custom_response(
                    status_text="error",
                    message=_(
                        "Cannot update a request that has already been processed"
                    ),
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            if serializer.is_valid():
                serializer.save()
                return custom_response(
                    status_text="success",
                    message=_("Request updated successfully"),
                    data=serializer.data,
                    status_code=status.HTTP_200_OK,
                )
            else:
                return custom_response(
                    status_text="error",
                    message=_("Validation failed"),
                    errors=serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
        except UpdateRequest.DoesNotExist:
            return custom_response(
                status_text="error",
                message=_("Request not found"),
                status_code=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return custom_response(
                status_text="error",
                message=_("An error occurred while updating the request"),
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def destroy(self, request, *args, **kwargs):
        """Delete an update request"""
        try:
            instance = self.get_object()

            # Check if user can delete this request
            if not request.user.is_staff and instance.created_by != request.user:
                return custom_response(
                    status_text="error",
                    message=_("You don't have permission to delete this request"),
                    status_code=status.HTTP_403_FORBIDDEN,
                )

            # Check if request is in a state that allows deletion
            if instance.status in [RequestStatus.UPDATED, RequestStatus.REJECTED]:
                return custom_response(
                    status_text="error",
                    message=_(
                        "Cannot delete a request that has already been processed"
                    ),
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            instance.delete()

            return custom_response(
                status_text="success",
                message=_("Request deleted successfully"),
                status_code=status.HTTP_204_NO_CONTENT,
            )
        except UpdateRequest.DoesNotExist:
            return custom_response(
                status_text="error",
                message=_("Request not found"),
                status_code=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return custom_response(
                status_text="error",
                message=_("An error occurred while deleting the request"),
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def approve(self, request, pk=None):
        """Approve a pending update request"""
        try:
            instance = self.get_object()

            # Check if user has permission to approve
            if not request.user.is_staff:
                return custom_response(
                    status_text="error",
                    message=_("You don't have permission to approve requests"),
                    status_code=status.HTTP_403_FORBIDDEN,
                )

            # Check if request is in pending state
            if instance.status != RequestStatus.PENDING:
                return custom_response(
                    status_text="error",
                    message=_("Only pending requests can be approved"),
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            with transaction.atomic():
                instance.status = RequestStatus.APPROVED
                instance.reviewed_by = request.user
                instance.reviewed_at = timezone.now()
                instance.ho_comments = request.data.get("ho_comments", "")
                instance.save()

            serializer = self.get_serializer(instance)
            return custom_response(
                status_text="success",
                message=_("Request approved successfully"),
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            return custom_response(
                status_text="error",
                message=_("An error occurred while approving the request"),
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def reject(self, request, pk=None):
        """Reject a pending update request"""
        try:
            instance = self.get_object()

            # Check if user has permission to reject
            if not request.user.is_staff:
                return custom_response(
                    status_text="error",
                    message=_("You don't have permission to reject requests"),
                    status_code=status.HTTP_403_FORBIDDEN,
                )

            # Check if request is in pending state
            if instance.status != RequestStatus.PENDING:
                return custom_response(
                    status_text="error",
                    message=_("Only pending requests can be rejected"),
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            # Validate rejection reason
            rejection_reason = request.data.get("rejection_reason", "").strip()
            if not rejection_reason:
                return custom_response(
                    status_text="error",
                    message=_("Rejection reason is required"),
                    errors={"rejection_reason": [_("This field is required")]},
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            with transaction.atomic():
                instance.status = RequestStatus.REJECTED
                instance.reviewed_by = request.user
                instance.reviewed_at = timezone.now()
                instance.rejection_reason = rejection_reason
                instance.ho_comments = request.data.get("ho_comments", "")
                instance.save()

            serializer = self.get_serializer(instance)
            return custom_response(
                status_text="success",
                message=_("Request rejected successfully"),
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            return custom_response(
                status_text="error",
                message=_("An error occurred while rejecting the request"),
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"], url_name="stats")
    def stats(self, request):
        """Get statistics for update requests"""
        try:
            queryset = self.get_queryset()

            stats = {
                "total_requests": queryset.count(),
                "pending_requests": queryset.filter(
                    status=RequestStatus.PENDING
                ).count(),
                "approved_requests": queryset.filter(
                    status=RequestStatus.UPDATED
                ).count(),
                "rejected_requests": queryset.filter(
                    status=RequestStatus.REJECTED
                ).count(),
                "by_request_type": {
                    choice[0]: queryset.filter(request_type=choice[0]).count()
                    for choice in RequestTypeChoices.choices
                },
                "by_role_type": {
                    choice[0]: queryset.filter(role_type=choice[0]).count()
                    for choice in RoleType.choices
                },
            }

            return custom_response(
                status_text="success",
                message=_("Statistics retrieved successfully"),
                data=stats,
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            return custom_response(
                status_text="error",
                message=_("An error occurred while retrieving statistics"),
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


from rest_framework.parsers import MultiPartParser, FormParser


class UpdateRequestDocumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for uploading and managing update request documents.
    """

    # Enable filtering, searching, and ordering
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["request__id"]

    queryset = UpdateRequestDocument.objects.all().select_related("request")
    serializer_class = UpdateRequestDocumentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return custom_response("success", data=serializer.data)
        except Exception as e:
            return custom_response(
                "error",
                message="Failed to fetch documents.",
                errors=str(e),
                status_code=500,
            )

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return custom_response("success", data=serializer.data)
        except Exception as e:
            return custom_response(
                "error",
                message="Failed to fetch document.",
                errors=str(e),
                status_code=500,
            )

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return custom_response(
                status_text="success",
                message="Document uploaded successfully.",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED,
            )
        except serializers.ValidationError as e:
            return custom_response(
                "error", message="Validation failed.", errors=e.detail, status_code=400
            )
        except Exception as e:
            return custom_response(
                "error",
                message="Failed to upload document.",
                errors=str(e),
                status_code=500,
            )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()
            return custom_response("success", message="Document deleted successfully.")
        except Exception as e:
            return custom_response(
                "error",
                message="Failed to delete document.",
                errors=str(e),
                status_code=500,
            )


class BankListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    authentication_classes = [ApiKeyAuthentication]
    serializer_class = BankListSerializer

    def get_queryset(self):
        return Bank.objects.filter(is_active=True).order_by("bank_name")

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return custom_response(
                status_text="success",
                message="Banks fetched successfully.",
                data=serializer.data,
            )
        except Exception as e:
            return custom_response(
                "error", message="Error fetching banks.", errors=str(e), status_code=500
            )


class BranchListView(generics.ListAPIView):
    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [AllowAny]

    serializer_class = BranchListSerializer

    def get_queryset(self):
        bank_code = self.request.query_params.get("bank_code")
        qs = Branch.objects.filter(is_active=True).order_by("branch_name")
        if bank_code:
            qs = qs.filter(bank_code=bank_code)
        return qs

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return custom_response(
                status_text="success",
                message="Branches fetched successfully.",
                data=serializer.data,
            )
        except Exception as e:
            return custom_response(
                "error",
                message="Error fetching branches.",
                errors=str(e),
                status_code=500,
            )


from rest_framework.views import APIView
from django.utils import translation


def get_choices_enum(enum_cls):
    return [{"value": choice.value, "label": choice.label} for choice in enum_cls]


from django.utils import translation


class EnumChoicesView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [ApiKeyAuthentication]

    def get(self, request, *args, **kwargs):
        # Force language from Accept-Language header
        lang = request.headers.get("Accept-Language")
        if lang:
            translation.activate(lang)

        data = {
            "request_types": get_choices_enum(RequestTypeChoices),
            "role_types": get_choices_enum(RoleType),
            "request_statuses": get_choices_enum(RequestStatus),
            "document_types": get_choices_enum(DocumentTypeChoice),
        }

        translation.deactivate()

        return custom_response(
            status_text="success",
            message="Choices loaded successfully.",
            data=data,
            status_code=status.HTTP_200_OK,
        )
