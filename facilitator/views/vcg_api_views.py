import base64
from django.core.files.base import ContentFile
import random
from rest_framework import viewsets
from rest_framework import status
from ..serializers.vcg_serializers import *
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
)
from error_formatter import format_exception, simplify_errors
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action
from ..authentication import ApiKeyAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter, api_settings
from rest_framework import status, viewsets, exceptions
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError


from math import ceil


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


class VCGMemberAttendanceViewSet(viewsets.ModelViewSet):
    queryset = VCGMemberAttendance.objects.all()
    serializer_class = VCGMemberAttendanceSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    authentication_classes = [JWTAuthentication]
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]
    filterset_fields = ["meeting__meeting_id"]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().order_by("id"))

        # 👇 This sets self.page and returns paginated queryset
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Fallback: if pagination is not applied
        serializer = self.get_serializer(queryset, many=True)
        return custom_response(
            status_text="success",
            message="Member attendance loaded...",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"])
    def mark_attendance(self, request):
        """
        Marks all given members as PRESENT for the specified meeting.
        Expected request format:
        {
            "meeting": <meeting_id>,
            "members": [<member_id1>, <member_id2>, ...]
        }
        """
        meeting_id = request.data.get("meeting")
        member_ids = request.data.get("members", [])
        if not meeting_id or not isinstance(member_ids, list):
            return custom_response(
                status_text="error",
                message="Invalid data format. Provide 'meeting' (str) and 'members' (list of member_code).",
                data={},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        meeting = get_object_or_404(VCGMeeting, meeting_id=meeting_id)
        responses = []
        errors = []
        for member_id in member_ids:
            try:
                member = get_object_or_404(
                    VCGroup, Q(member_code=member_id) | Q(member_ex_code=member_id)
                )
                attendance, created = VCGMemberAttendance.objects.update_or_create(
                    meeting=meeting,
                    group_member=member,
                    defaults={"status": VCGMemberAttendance.PRESENT},
                )
                responses.append(VCGMemberAttendanceSerializer(attendance).data)
            except ValidationError as exc:
                friendly = simplify_errors(exc.detail)
                errors.append(friendly)
            except Exception as e:
                errors.append(format_exception(e))

        return custom_response(
            status_text="success",
            message=(
                "Some records failed to save."
                if errors
                else "All records saved successfully."
            ),
            data=responses,
            errors=errors,
            status_code=(
                status.HTTP_207_MULTI_STATUS if errors else status.HTTP_200_OK
            ),
        )

    def delete(self, request, *args, **kwargs):

        ids = request.data.get("ids", [])

        if not isinstance(ids, list):
            return Response(
                {"error": "Invalid data format. Provide 'attendances' (list of int)."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        attendances_obj = VCGMemberAttendance.objects.filter(pk__in=ids)
        if attendances_obj:
            attendances_obj.delete()
            return custom_response(
                status_text="success",
                message=f"Successfully deleted {len(ids)} attendance(s)...",
                data={},
                status_code=status.HTTP_200_OK,
            )
        return custom_response(
            status_text="error",
            message="Attendances not found",
            data={},
            status_code=status.HTTP_200_OK,
        )


class ZeroDaysPouringReportViewSet(viewsets.ModelViewSet):
    queryset = ZeroDaysPouringReport.objects.all()
    serializer_class = ZeroDaysPouringReportSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    authentication_classes = [JWTAuthentication]
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]
    filterset_fields = ["meeting__meeting_id"]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().order_by("id"))

        # 👇 This sets self.page and returns paginated queryset
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Fallback: if pagination is not applied
        serializer = self.get_serializer(queryset, many=True)
        return custom_response(
            status_text="success",
            message="Zero days report loaded...",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        meeting_id = request.data.get("meeting")
        members = request.data.get("members", [])
        reason_id = request.data.get("reason")

        if not meeting_id or not isinstance(members, list) or not reason_id:
            return Response(
                {
                    "error": "Invalid data format. Provide 'meeting' (int), 'members' (list of dicts), and 'reason' (int)."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        meeting = get_object_or_404(VCGMeeting, meeting_id=meeting_id)

        responses = []
        errors = []

        for member_data in members:
            data = {**member_data, "meeting": meeting.pk, "reason": reason_id}

            serializer = ZeroDaysPouringReportSerializer(data=data)
            try:
                serializer.is_valid(raise_exception=True)

                report, created = serializer.create_or_update(serializer.validated_data)
                serializer.instance = report
                serializer.save()
                responses.append(
                    {
                        **serializer.data,
                        "status": "Report Created" if created else "Updated",
                        "created": created,
                    }
                )
            except ValidationError as exc:
                friendly = simplify_errors(exc.detail)
                errors.append(friendly)
            except Exception as e:
                errors.append(format_exception(e))

        return custom_response(
            status_text="success",
            message=(
                "Some records failed to save."
                if errors
                else "All records saved successfully."
            ),
            data=responses,
            errors=errors,
            status_code=(
                status.HTTP_207_MULTI_STATUS if errors else status.HTTP_201_CREATED
            ),
        )

    def delete(self, request, *args, **kwargs):
        """
        Bulk delete member complaint reports for a given meeting.

        **Method**: DELETE
        **Endpoint**: `/member-complaint-reports/`

        **Request Body**:
        ```json
        {
        "meeting": 1,
        "members": [
            {"member_code": "M001"},
            {"member_code": "M002"}
        ]
        }
        ```

        **Response (200/207)**:
        ```json
        {
        "status": "success",
        "message": "Successfully deleted 2 member(s)",
        "data": {
            "deleted": [
            {"member_code": "M001", "status": "Deleted"}
            ],
            "not_found": [
            {"member_code": "M002", "error": "Not found"}
            ]
        }
        }
        ```

        - Returns 207 if some deletions fail (e.g., member not found).
        """

        meeting_id = request.data.get("meeting")
        members = request.data.get("members", [])

        if not meeting_id or not isinstance(members, list):
            return Response(
                {
                    "error": "Invalid data format. Provide 'meeting' (int) and 'members' (list of dicts with 'member_code')."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        meeting = get_object_or_404(VCGMeeting, meeting_id=meeting_id)

        deleted = []
        not_found = []
        count = 0
        delete_count = 0
        for member_data in members:
            member_code = member_data.get("member_code")
            if not member_code:
                not_found.append(
                    {"member_data": member_data, "error": "Missing 'member_code'."}
                )
                continue

            try:
                obj = ZeroDaysPouringReport.objects.get(
                    meeting=meeting, member_code=member_code
                )
                obj.delete()
                deleted.append({"member_code": member_code, "status": "Deleted"})
                count += 1
            except ZeroDaysPouringReport.DoesNotExist:
                not_found.append({"member_code": member_code, "error": "Not found"})
                delete_count -= 1

        response_data = {"deleted": deleted}
        status_text = "success"
        message_text = f"Successfully deleted {count} member(s)"
        if not_found:
            response_data["not_found"] = not_found
            status_text = "error"
            message_text = f"failed to delete {delete_count} member(s)"

        return custom_response(
            status_text=status_text,
            message=message_text,
            data=response_data,
            errors=not_found,
            status_code=(
                status.HTTP_207_MULTI_STATUS if not_found else status.HTTP_200_OK
            ),
        )


class MemberComplaintReportViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing member complaint reports linked to a meeting.

    **Available Methods:**
    - `POST /member-complaint-reports/`: Bulk create or update complaint reports.
    - `GET /member-complaint-reports/`: List complaint reports with filtering and pagination.
    - `DELETE /member-complaint-reports/`: Bulk delete complaint reports by meeting and member codes.

    **Authentication**: JWT required.
    """

    queryset = MemberComplaintReport.objects.all()
    serializer_class = MemberComplaintReportSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]
    filterset_fields = ["meeting__meeting_id"]

    def create(self, request, *args, **kwargs):
        """
        Bulk create or update member complaint reports for a specific meeting.

        **Method**: POST
        **Endpoint**: `/member-complaint-reports/`

        **Request Body**:
        ```json
        {
        "meeting": 1,
        "reason": 2,
        "members": [
            {"member_code": "M001", "member_ex_code": "EX001", "member_name": "John Doe"},
            {"member_code": "M002", "member_ex_code": "EX002", "member_name": "Jane Doe"}
        ]
        }
        ```

        **Response (200/207)**:
        ```json
        {
        "status": "success",
        "message": "Report created successfully...",
        "data": [
            {
            "member_code": "M001",
            "status": "Report Created",
            "created": true
            }
        ],
        "errors": [
            {
            "member_data": { ... },
            "error": "Duplicate entry"
            }
        ]
        }
        ```

        - Returns HTTP 200 on success, or 207 if partial failures occurred.
        """

        meeting_id = request.data.get("meeting")
        members = request.data.get("members", [])
        reason_id = request.data.get("reason")

        if not meeting_id or not isinstance(members, list) or not reason_id:
            return Response(
                {
                    "error": "Invalid data format. Provide 'meeting' (int), 'members' (list of dicts), and 'reason' (int)."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        meeting = get_object_or_404(VCGMeeting, meeting_id=meeting_id)
        reason = get_object_or_404(MemberComplaintReason, id=reason_id)

        responses = []
        errors = []

        for member_data in members:
            data = {**member_data, "meeting": meeting.pk, "reason": reason.pk}

            serializer = MemberComplaintReportSerializer(data=data)
            try:
                serializer.is_valid(raise_exception=True)

                report, created = serializer.create_or_update(serializer.validated_data)
                serializer.instance = report  # needed for serializer.data to work
                serializer.save()
                responses.append(
                    {
                        **serializer.data,
                        "status": "Report Created" if created else "Updated",
                        "created": created,
                    }
                )
            except ValidationError as exc:
                friendly = simplify_errors(exc.detail)
                errors.append(friendly)
            except Exception as e:
                errors.append(format_exception(e))

        return custom_response(
            status_text="success",
            message=(
                "Some records failed to save."
                if errors
                else "All records saved successfully."
            ),
            data=responses,
            errors=errors,
            status_code=(
                status.HTTP_207_MULTI_STATUS if errors else status.HTTP_201_CREATED
            ),
        )

    def list(self, request, *args, **kwargs):
        """
        List all complaint reports with optional filtering, search, ordering, and pagination.

        **Method**: GET
        **Endpoint**: `/member-complaint-reports/`

        ---
        ### 🔍 Query Parameters:
        - `meeting__meeting_id`: *(uud)* Filter reports by related meeting ID.
        - `search`: *(string)* Search by default fields (configure in `SearchFilter`).
        - `ordering`: *(string)* Order results by fields. E.g., `ordering=created_at` or `ordering=-id`.
        - `page_size`: *(int)* Number of results per page (pagination).
        - `page`: *(int)* Start index for pagination.

        ---
        ### ✅ Example:
        ```
        GET /member-complaint-reports/?meeting__meeting_id=12&ordering=-id&limit=20&offset=0
        ```

        ---
        ### 🔁 Response (200):
        ```json
        {
        "count": 1,
        "next": null,
        "previous": null,
        "results": [
            {
            "id": 1,
            "member_code": "M001",
            "meeting": 12,
            "reason": 3,
            ...
            }
        ]
        }
        ```
        """
        queryset = self.filter_queryset(self.get_queryset().order_by("id"))

        # 👇 This sets self.page and returns paginated queryset
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Fallback: if pagination is not applied
        serializer = self.get_serializer(queryset, many=True)
        return custom_response(
            status_text="success",
            message="Zero days report loaded...",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    def delete(self, request, *args, **kwargs):
        """
        Bulk delete member complaint reports for a given meeting.

        **Method**: DELETE
        **Endpoint**: `/member-complaint-reports/`

        **Request Body**:
        ```json
        {
        "meeting": 1,
        "members": [
            {"member_code": "M001"},
            {"member_code": "M002"}
        ]
        }
        ```

        **Response (200/207)**:
        ```json
        {
        "status": "success",
        "message": "Successfully deleted 2 member(s)",
        "data": {
            "deleted": [
            {"member_code": "M001", "status": "Deleted"}
            ],
            "not_found": [
            {"member_code": "M002", "error": "Not found"}
            ]
        }
        }
        ```

        - Returns 207 if some deletions fail (e.g., member not found).
        """

        meeting_id = request.data.get("meeting")
        members = request.data.get("members", [])

        if not meeting_id or not isinstance(members, list):
            return Response(
                {
                    "error": "Invalid data format. Provide 'meeting' (int) and 'members' (list of dicts with 'member_code')."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        meeting = get_object_or_404(VCGMeeting, meeting_id=meeting_id)

        deleted = []
        not_found = []
        count = 0
        delete_count = 0
        for member_data in members:
            member_code = member_data.get("member_code")
            if not member_code:
                not_found.append(
                    {"member_data": member_data, "error": "Missing 'member_code'."}
                )
                continue

            try:
                obj = MemberComplaintReport.objects.get(
                    meeting=meeting, member_code=member_code
                )
                obj.delete()
                deleted.append({"member_code": member_code, "status": "Deleted"})
                count += 1
            except MemberComplaintReport.DoesNotExist:
                delete_count += 1
                not_found.append({"member_code": member_code, "error": "Not found"})

        response_data = {"deleted": deleted}
        status_text = "success"
        message_text = f"Successfully deleted {count} member(s)"
        if not_found:
            response_data["not_found"] = not_found
            status_text = "error"
            message_text = f"failed to delete {delete_count} member(s)"

        return custom_response(
            status_text=status_text,
            message=message_text,
            data=response_data,
            status_code=(
                status.HTTP_207_MULTI_STATUS if not_found else status.HTTP_200_OK
            ),
        )


class ZeroDaysReasonViewSet(viewsets.ModelViewSet):
    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [AllowAny]
    queryset = ZeroDaysPourerReason.objects.all()
    serializer_class = ZeroDaysReasonSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {
                    "status": "success",
                    "message": "Resource created successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {"status": "error", "message": str(e), "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
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
                    "message": "Resource updated successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"status": "error", "message": str(e), "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(
                {
                    "status": "success",
                    "message": "Resource retrieved successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"status": "error", "message": str(e), "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset().order_by("id"))
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "status": "success",
                    "message": "Resource list retrieved successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"status": "error", "message": str(e), "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )


class MemberComplaintReasonViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    authentication_classes = [ApiKeyAuthentication]
    queryset = MemberComplaintReason.objects.all()
    serializer_class = MemberComplaintReasonSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {
                    "status": "success",
                    "message": "Member complaint reason created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {"status": "error", "message": str(e), "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
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
                    "message": "Member complaint reason updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"status": "error", "message": str(e), "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(
                {
                    "status": "success",
                    "message": "Member complaint reason retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"status": "error", "message": str(e), "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset().order_by("id"))

            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "status": "success",
                    "message": "Member complaint reasons retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"status": "error", "message": str(e), "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {
                    "status": "success",
                    "message": "Member complaint reason deleted successfully.",
                    "data": None,
                },
                status=status.HTTP_204_NO_CONTENT,
            )
        except Exception as e:
            return Response(
                {"status": "error", "message": str(e), "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )


class VCGMeetingImagesViewSet(viewsets.ModelViewSet):
    queryset = VCGMeetingImages.objects.all()
    serializer_class = VCGMeetingImagesSerializer
    pagination_class =  StandardResultsSetPagination
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["meeting__meeting_id"]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().order_by("id"))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return custom_response(
            status_text="success",
            message="VCG meetings images loaded...",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    @action(detail=False, methods=['post'], url_path='bulk-delete')
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        if not isinstance(ids, list) or not all(isinstance(i, int) for i in ids):
            return custom_response(
                status_text="error",
                message="Invalid IDs list",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        instances = self.queryset.filter(id__in=ids)
        count = instances.count()
        instances.delete()
        return custom_response(status_text="success",message= f'{count} items deleted.', status_code=status.HTTP_200_OK)


    @action(detail=False, methods=["post"])
    def upload_images(self, request):
        """
        Upload base64-encoded images for a specific meeting.

        Request Body:
        - `meeting_id` (int): ID of the meeting.
        - `images` (List[str]): List of base64-encoded image strings.

        Returns:
        - HTTP 200 OK if all images are saved.
        - HTTP 207 Multi-Status if some images fail.
        - Includes uploaded image URLs and any errors encountered.
        """
        from django.utils.timezone import now

        meeting_id = request.data.get("meeting_id")
        base64_images = request.data.get("images", [])

        if not meeting_id or not isinstance(base64_images, list):
            return Response(
                {
                    "error": "Invalid data format. Provide 'meeting_id' (int), 'images' (list of base64 strings)"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        meeting = get_object_or_404(VCGMeeting, meeting_id=meeting_id)
        uploaded_images = []
        errors = []

        for base64_image in base64_images:
            try:
                image_data = base64.b64decode(base64_image)
                image_file = ContentFile(
                    image_data,
                    name=f"{random.randint(100, 999)}_{meeting_id}.jpg",
                )
                meeting_image = VCGMeetingImages.objects.create(
                    meeting=meeting, image=image_file
                )
                uploaded_images.append(
                    {"id": meeting_image.id, "image_url": meeting_image.image.url}
                )
            except Exception as e:
                errors.append(
                    {
                        "image": base64_image[:30],
                        "error": format_exception(exc=e),
                    }
                )

        # Update meeting status
        meeting.completed_at = now()
        meeting.status = VCGMeeting.COMPLETED
        meeting.save()

        response_data = {
            "meeting_id": meeting.meeting_id,
            "uploaded_images": uploaded_images,
        }

        return custom_response(
            status_text="success",
            message=(
                "Some images failed to save."
                if errors
                else "All images saved successfully."
            ),
            data=response_data,
            errors=errors,
            status_code=(
                status.HTTP_207_MULTI_STATUS if errors else status.HTTP_200_OK
            ),
        )


class VCGMeetingViewSet(viewsets.ModelViewSet):
    serializer_class = VCGMeetingSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "is_deleted"]
    search_fields = ["mpp_name", "mpp_code"]
    ordering_fields = ["started_at", "completed_at"]
    ordering = ["-started_at"]
    lookup_field = "meeting_id"

    def get_queryset(self):
        user = self.request.user
        queryset = VCGMeeting.objects.all()
        if user.is_staff or user.is_superuser:
            return queryset
        return queryset.filter(user=user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().order_by("id"))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return custom_response(
            status_text="success",
            message="VCG meetings loaded...",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.status = VCGMeeting.DELETED
        instance.save(update_fields=["is_deleted", "status"])
        return custom_response(
            status_text="success",
            message="VCG meeting deleted...",
            data=None,
            status_code=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        """
        Create a new meeting record if it doesn't exist.
        If a meeting with the same `mpp_name`, `mpp_ex_code`, and `mpp_code` exists, return that instead.
        """
        mpp_code = request.data.get("mpp_code")
        started_at = request.data.get("started_at")
        dt_obj = datetime.fromisoformat(started_at)
        exists, meeting = VCGMeeting.get_ongoing_meeting(mpp_code=mpp_code, date=dt_obj)
        if exists:
            return Response(
                {
                    "status": "success",
                    "message": _("A meeting with the same details already exists."),
                    "result": VCGMeetingSerializer(meeting).data,
                },
                status=status.HTTP_200_OK,
            )
        # If no existing meeting, create a new one
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            meeting = serializer.save(status=VCGMeeting.STARTED, synced=False)
            return Response(
                {
                    "status": "success",
                    "message": _("Your meeting has started"),
                    "result": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "status": "error",
                "message": _("Invalid data"),
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def update(self, request, *args, **kwargs):
        """
        Update meeting details, including marking it as completed.
        Expected request format:
        {
            "completed_at": "YYYY-MM-DD HH:MM:SS",
            "status": "completed"
        }
        """
        partial = kwargs.pop("partial", True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": _("Meeting updated successfully"),
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "status": "error",
                "message": _("Invalid data"),
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class VCGroupViewSet(viewsets.ModelViewSet):
    queryset = VCGroup.objects.all()
    serializer_class = VCGroupSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = super().get_queryset()
        mpp_code = self.request.GET.get("mpp_code")
        if not mpp_code:
            return Response(
                {"status": "error", "message": "mpp_code is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        queryset = queryset.filter(mpp__mpp_code=mpp_code)
        serializer = self.serializer_class(queryset, many=True)
        return Response(
            {
                "status": "success",
                "message": "vcg group fetched",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": _("VCG Member created successfully"),
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"error": _("Invalid data"), "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": _("VCG Member updated successfully"),
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"error": _("Invalid data"), "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(
            {"message": _("VCG Member deleted successfully")},
            status=status.HTTP_204_NO_CONTENT,
        )
