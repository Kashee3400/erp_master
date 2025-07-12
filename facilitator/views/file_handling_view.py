from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from ..authentication import ApiKeyAuthentication2
from ..serializers.file_serializers import (
    UploadedFile,
    UploadedFileSerializer,
    serializers,
)
from ..models.file_models import FileActionLog
from rest_framework.response import Response
from ..utils.file_utils import generate_image_thumbnail, get_client_ip, get_geo_location
from notifications.tasks import scan_file_virus
from rest_framework.pagination import PageNumberPagination
from math import ceil
from error_formatter import format_exception, simplify_errors
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action


def custom_response(
    status_text, data=None, message=None, status_code=200, errors=None, headers=None
):
    return Response(
        {
            "status": status_text,
            "message": message or "Success",
            "data": data,
            "errors": errors,
            "headers": headers,
        },
        status=status_code,
    )


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    # Optional: Attach extra data externally before calling pagination
    extra_data = {}

    def get_paginated_response(self, data):
        total_items = self.page.paginator.count
        current_page = self.page.number
        per_page = self.page.paginator.per_page
        total_pages = ceil(total_items / int(per_page))

        base_response = {
            "count": total_items,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "current_page": current_page,
            "total_pages": total_pages,
            "page_size": int(per_page),
            "has_next": self.page.has_next(),
            "has_previous": self.page.has_previous(),
            "results": data,
        }

        # Merge extra dynamic data if any
        base_response.update(self.extra_data)

        return custom_response(
            status_text="success",
            message="Success",
            data=base_response,
            status_code=status.HTTP_200_OK,
        )


class UploadedFileViewSet(viewsets.ModelViewSet):
    queryset = UploadedFile.objects.all().order_by("-uploaded_at")
    serializer_class = UploadedFileSerializer
    parser_classes = [MultiPartParser, FormParser]
    authentication_classes = [ApiKeyAuthentication2]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filter_fields = ["media_type"]

    @action(
        detail=False,
        methods=["post"],
        url_path="bulk-upload",
        parser_classes=[MultiPartParser, FormParser],
    )
    def bulk_upload(self, request):
        files = request.FILES.getlist("files")
        if not files:
            return custom_response(
                status_text="error",
                message="No files provided.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        responses = []
        errors = []

        for index, file in enumerate(files):
            file_data = {
                "file": file,
                "tags": request.data.get("tags"),
                "notes": request.data.get("notes"),
            }

            serializer = self.get_serializer(data=file_data)
            if serializer.is_valid():
                try:
                    instance = serializer.save(
                        uploaded_by=(
                            request.user if request.user.is_authenticated else None
                        ),
                        ip_address=get_client_ip(request),
                        geo_location=get_geo_location(get_client_ip(request)),
                    )

                    if instance.media_type == "image":
                        generate_image_thumbnail(instance)

                    scan_file_virus.delay(instance.file.path)

                    responses.append(serializer.data)
                except serializers.ValidationError as exc:
                    errors.append({"filename": file.name, "error": simplify_errors(error_dict=exc.default_detail)})
                except Exception as e:
                    errors.append({"filename": file.name, "error": format_exception(e)})
            else:
                errors.append(
                    {"filename": file.name, "error": simplify_errors(serializer.errors)}
                )

        return custom_response(
            status_text="partial_success" if errors else "success",
            message="Bulk upload processed.",
            data={"uploaded": responses, "errors": errors},
            status_code=(
                status.HTTP_207_MULTI_STATUS if errors else status.HTTP_201_CREATED
            ),
        )

    def perform_create(self, serializer):
        request = self.request
        instance = serializer.save(
            uploaded_by=request.user if request.user.is_authenticated else None,
            ip_address=get_client_ip(request),
            geo_location=get_geo_location(get_client_ip(request)),
        )
        # Generate thumbnail for images
        if instance.media_type == "image":
            generate_image_thumbnail(instance)
        # Run virus scan in background
        scan_file_virus.delay(instance.file.path)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            self.perform_create(serializer)

            headers = self.get_success_headers(serializer.data)
            return custom_response(
                status_text="success",
                message="File uploaded successfully.",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED,
                headers=headers,
            )
        except serializers.ValidationError as e:
            return custom_response(
                status_text="error",
                message="Validation failed.",
                errors=simplify_errors(error_dict=e.detail),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return custom_response(
                status_text="error",
                message="Unexpected server error.",
                errors=format_exception(exc=e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def list(self, request, *args, **kwargs):
        print(self.request.user)
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page or queryset, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return custom_response(
                status_text="success",
                message="File details retrieved.",
                data=serializer.data,
            )
        except Exception as e:
            return custom_response(
                status_text="error",
                message="File not found.",
                errors=format_exception(exc=e),
                status_code=status.HTTP_404_NOT_FOUND,
            )

    def update(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
            return custom_response(
                status_text="success", message="File updated.", data=response.data
            )
        except serializers.ValidationError as e:
            return custom_response(
                status_text="error",
                message="Validation error.",
                errors=simplify_errors(error_dict=e.detail),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return custom_response(
                status_text="error",
                message="Update failed.",
                errors=format_exception(exc=e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()
            return custom_response(
                status_text="success",
                message="File deleted successfully.",
                data=None,
                status_code=status.HTTP_204_NO_CONTENT,
            )
        except Exception as e:
            return custom_response(
                status_text="error",
                message="Deletion failed.",
                errors=format_exception(exc=e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
