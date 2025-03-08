import base64
from django.core.files.base import ContentFile
import random
from rest_framework import viewsets
from rest_framework import status
from ..serializers.vcg_serializers import *
from ..filters.api_filters import VCGMeetingFilter,MonthAssignmentFilter
from django.db.models import Count
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from ..authentication import ApiKeyAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class VCGMemberAttendanceViewSet(viewsets.ModelViewSet):
    queryset = VCGMemberAttendance.objects.all()
    serializer_class = VCGMemberAttendanceSerializer

    @action(detail=False, methods=['post'])
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
            return Response(
                {"error": "Invalid data format. Provide 'meeting' (int) and 'members' (list of ints)."},
                status=status.HTTP_400_BAD_REQUEST
            )
        meeting = get_object_or_404(VCGMeeting, id=meeting_id)
        responses = []
        errors = []
        for member_id in member_ids:
            try:
                member = get_object_or_404(VCGroup, id=member_id)
                attendance, created = VCGMemberAttendance.objects.update_or_create(
                    meeting=meeting,
                    member=member,
                    defaults={"status": VCGMemberAttendance.PRESENT}
                )
                responses.append({
                    "member_id": member_id,
                    "status": "Present",
                    "created": created
                })
            except Exception as e:
                errors.append({"member_id": member_id, "error": str(e)})
        response_data = {"marked": responses}
        if errors:
            response_data["errors"] = errors
        return Response(response_data, status=status.HTTP_207_MULTI_STATUS if errors else status.HTTP_200_OK)

class ZeroDaysPouringReportViewSet(viewsets.ModelViewSet):
    queryset = ZeroDaysPouringReport.objects.all()
    serializer_class = ZeroDaysPouringReportSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    @action(detail=False, methods=['post'])
    def mark_zero_days(self, request):
        """
        Bulk marks Zero Days Pouring Report for the given meeting and members.
        Expected request format:
        {
            "meeting": <meeting_id>,
            "members": [
                {"member_code": "M001", "member_ex_code": "EX001", "member_name": "John Doe"},
                {"member_code": "M002", "member_ex_code": "EX002", "member_name": "Jane Doe"}
            ],
            "reason": <reason_id>
        }
        """
        meeting_id = request.data.get("meeting")
        members = request.data.get("members", [])
        reason_id = request.data.get("reason")

        if not meeting_id or not isinstance(members, list) or not reason_id:
            return Response(
                {"error": "Invalid data format. Provide 'meeting' (int), 'members' (list of dicts), and 'reason' (int)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        meeting = get_object_or_404(VCGMeeting, id=meeting_id)
        reason = get_object_or_404(ZeroDaysPourerReason, id=reason_id)

        responses = []
        errors = []

        for member in members:
            try:
                member_code = member.get("member_code")
                member_ex_code = member.get("member_ex_code")
                member_name = member.get("member_name")

                if not member_code or not member_ex_code or not member_name:
                    raise ValueError("Missing required member fields: 'member_code', 'member_ex_code', 'member_name'.")

                report, created = ZeroDaysPouringReport.objects.update_or_create(
                    meeting=meeting,
                    reason=reason,
                    member_code=member_code,
                    member_ex_code=member_ex_code,
                    member_name=member_name
                )

                responses.append({
                    "member_code": member_code,
                    "status": "Report Created" if created else "Already Exists",
                    "created": created
                })
            except Exception as e:
                errors.append({"member": member, "error": str(e)})

        response_data = {"marked": responses}
        if errors:
            response_data["errors"] = errors

        return Response(response_data, status=status.HTTP_207_MULTI_STATUS if errors else status.HTTP_200_OK)

class MonthAssignmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API to fetch Month Assignment data. This is read-only.
    """
    queryset = MonthAssignment.objects.all()
    serializer_class = MonthAssignmentSerializer
    permission_classes = [AllowAny]
    authentication_classes = [ApiKeyAuthentication]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MonthAssignmentFilter

    search_fields = ["mpp_code"]
    ordering_fields = ["month"]
    ordering = ["-month"]

class MemberComplaintReportViewSet(viewsets.ModelViewSet):
    queryset = MemberComplaintReport.objects.all()
    serializer_class = MemberComplaintReportSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @action(detail=False, methods=['post'])
    def mark_complaint(self, request):
        """
        Bulk marks Member Complaint Reports for the given meeting and members.
        Expected request format:
        {
            "meeting": <meeting_id>,
            "members": [
                {"member_code": "M101", "member_ex_code": "EX101", "member_name": "John Doe"},
                {"member_code": "M102", "member_ex_code": "EX102", "member_name": "Jane Doe"}
            ],
            "reason": <reason_id>
        }
        """
        meeting_id = request.data.get("meeting")
        members = request.data.get("members", [])
        reason_id = request.data.get("reason")

        if not meeting_id or not isinstance(members, list) or not reason_id:
            return Response(
                {"error": "Invalid data format. Provide 'meeting' (int), 'members' (list of dicts), and 'reason' (int)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        meeting = get_object_or_404(VCGMeeting, id=meeting_id)
        reason = get_object_or_404(MemberComplaintReason, id=reason_id)

        responses = []
        errors = []

        for member_data in members:
            try:
                member_code = member_data.get("member_code")
                member_ex_code = member_data.get("member_ex_code")
                member_name = member_data.get("member_name")

                if not member_code or not member_name:
                    errors.append({
                        "member_data": member_data,
                        "error": "Missing required fields: 'member_code', 'member_name'."
                    })
                    continue

                report, created = MemberComplaintReport.objects.update_or_create(
                    meeting=meeting,
                    member_code=member_code,
                    defaults={
                        "member_ex_code": member_ex_code,
                        "member_name": member_name,
                        "reason": reason
                    }
                )

                responses.append({
                    "member_code": member_code,
                    "member_name": member_name,
                    "meeting": meeting.id,
                    "status": "Report Created" if created else "Updated"
                })

            except Exception as e:
                errors.append({"member_data": member_data, "error": str(e)})

        response_data = {"reports": responses}
        if errors:
            response_data["errors"] = errors

        return Response(response_data, status=status.HTTP_207_MULTI_STATUS if errors else status.HTTP_200_OK)

class ZeroDaysReasonViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    authentication_classes = [ApiKeyAuthentication]
    queryset = ZeroDaysPourerReason.objects.all()
    serializer_class = ZeroDaysReasonSerializer

class MemberComplaintReasonViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    authentication_classes = [ApiKeyAuthentication]
    queryset = MemberComplaintReason.objects.all()
    serializer_class = MemberComplaintReasonSerializer

class VCGMeetingImagesViewSet(viewsets.ModelViewSet):
    queryset = VCGMeetingImages.objects.all()
    serializer_class = VCGMeetingImagesSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @action(detail=False, methods=["post"])
    def upload_images(self, request):
        """
        Uploads images for a specific meeting.
        Expected request format:
        {
            "meeting_id": <meeting_id>,
            "images": [<base64_string1>, <base64_string2>, ...],
            "date_time": "YYYY-MM-DD HH:MM:SS"
        }
        """
        meeting_id = request.data.get("meeting_id")
        base64_images = request.data.get("images", [])
        selected_datetime = request.data.get("date_time")

        if not meeting_id or not isinstance(base64_images, list) or not selected_datetime:
            return Response(
                {"error": "Invalid data format. Provide 'meeting_id' (int), 'images' (list of base64 strings), and 'date_time' (str)."},
                status=status.HTTP_400_BAD_REQUEST
            )
        meeting = get_object_or_404(VCGMeeting, meeting_id=meeting_id)
        uploaded_images = []
        errors = []
        for base64_image in base64_images:
            try:
                image_data = base64.b64decode(base64_image)
                image_file = ContentFile(
                    image_data,
                    name=f"{random.randint(100, 999)}_{meeting_id}_{selected_datetime}.jpg"
                )
                meeting_image = VCGMeetingImages.objects.create(
                    meeting=meeting,
                    image=image_file
                )
                uploaded_images.append({
                    "id": meeting_image.id,
                    "image_url": meeting_image.image.url
                })
            except Exception as e:
                errors.append({"image": base64_image[:30], "error": str(e)})
        # Update meeting status
        meeting.end_datetime = selected_datetime
        meeting.status = VCGMeeting.COMPLETED
        meeting.save()
        response_data = {
            "message": "Images uploaded successfully",
            "meeting_id": meeting.meeting_id,
            "uploaded_images": uploaded_images
        }
        if errors:
            response_data["errors"] = errors
        return Response(response_data, status=status.HTTP_207_MULTI_STATUS if errors else status.HTTP_200_OK)

class VCGMeetingViewSet(viewsets.ModelViewSet):
    queryset = VCGMeeting.objects.all()
    serializer_class = VCGMeetingSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = VCGMeetingFilter
    search_fields = ['mpp_name', 'mpp_code']
    ordering_fields = ['started_at', 'completed_at']
    ordering = ['-started_at']

    def get_queryset(self):
        user = self.request.user
        queryset = VCGMeeting.objects.annotate(num_images=Count("meeting_images"))
        
        if user.is_staff or user.is_superuser:
            return queryset
        return queryset.filter(user=user, num_images=0)
    
    def create(self, request, *args, **kwargs):
        """
        Create a new meeting record.
        Expected request format:
        {
            "user": <user_id>,
            "mpp_name": "MPP Name",
            "mpp_ex_code": "MPP_EX_001",
            "mpp_code": "MPP_001",
            "lat": 23.456,
            "lon": 78.123,
            "started_at": "YYYY-MM-DD HH:MM:SS"
        }
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            meeting = serializer.save(status=VCGMeeting.STARTED, synced=False)
            return Response(
                {
                    "message": "Meeting created successfully",
                    "meeting_id": meeting.meeting_id,
                    "status": meeting.status
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        Update meeting details including marking it as completed.
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
            meeting = serializer.save()
            response_data = {
                "message": "Meeting updated successfully",
                "meeting_id": meeting.meeting_id,
                "status": meeting.status
            }
            return Response(response_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def mark_completed(self, request, pk=None):
        """
        Marks a meeting as completed.
        Expected request format:
        {
            "completed_at": "YYYY-MM-DD HH:MM:SS"
        }
        """
        meeting = get_object_or_404(VCGMeeting, pk=pk)
        if meeting.status == VCGMeeting.COMPLETED:
            return Response({"message": "Meeting is already completed."}, status=status.HTTP_400_BAD_REQUEST)
        completed_at = request.data.get("completed_at", timezone.now())
        meeting.completed_at = completed_at
        meeting.status = VCGMeeting.COMPLETED
        meeting.synced = True
        meeting.save()

        return Response(
            {
                "message": "Meeting marked as completed",
                "meeting_id": meeting.meeting_id,
                "completed_at": meeting.completed_at
            },
            status=status.HTTP_200_OK
        )
