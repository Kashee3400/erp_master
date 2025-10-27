from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.cache import cache
import tempfile, uuid, os, logging, pandas as pd
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from util.response import custom_response
from .choices_view import BaseModelViewSet
from ..models.excel_model import ExcelUploadSession
from django.http import JsonResponse, HttpResponse
from ..serializers.excel_serializers import (
    ExcelUploadSessionListSerializer,
    ExcelUploadSessionDetailSerializer,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from tablib import Dataset
from datetime import datetime

from ..tasks import process_excel_import
from ..utils.exce_util import RESOURCE_REGISTRY

logger = logging.getLogger(__name__)


class ImportableModelsView(APIView):
    """Return list of models available for Excel import."""

    def get(self, request):
        models_info = []
        for model_label, resource_class in RESOURCE_REGISTRY.items():
            models_info.append(
                {
                    "label": model_label,  # e.g. "cattle.Cattle"
                    "name": model_label.split(".")[-1],  # e.g. "Cattle"
                    "app": model_label.split(".")[0],  # e.g. "cattle"
                    "resource": resource_class.__name__,  # e.g. "CattleResource"
                }
            )
        return JsonResponse({"models": models_info})


def _store_temp_file(uploaded_file):
    """Store uploaded file temporarily"""
    temp_dir = tempfile.gettempdir()
    temp_filename = f"excel_{uuid.uuid4().hex}_{uploaded_file.name}"
    temp_path = os.path.join(temp_dir, temp_filename)

    with open(temp_path, "wb+") as temp_file:
        for chunk in uploaded_file.chunks():
            temp_file.write(chunk)

    return temp_path


class ExcelExportView(APIView):
    """Handle Excel export with multiple sheets"""

    def post(self, request):
        try:
            export_config = request.data.get("config", {})
            sheets_config = export_config.get("sheets", [])
            filename = export_config.get("filename", "export")

            # Create workbook
            from openpyxl import Workbook

            wb = Workbook()
            wb.remove(wb.active)  # Remove default sheet

            for sheet_config in sheets_config:
                model_name = sheet_config.get("model")
                sheet_name = sheet_config.get("name", model_name)
                queryset = sheet_config.get("queryset")  # You'd pass this or build it

                # Create worksheet
                ws = wb.create_sheet(title=sheet_name)

                # Add headers and data
                # This would use your django-import-export resources
                # Mock implementation here
                ws.append(["Column 1", "Column 2", "Column 3"])
                ws.append(["Data 1", "Data 2", "Data 3"])

            # Prepare response
            response = HttpResponse(
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}.xlsx"'

            wb.save(response)
            return response

        except Exception as e:
            return JsonResponse({"error": f"Export failed: {str(e)}"}, status=500)


class ExcelSessionViewSet(BaseModelViewSet):
    queryset = ExcelUploadSession.objects.all()
    authentication_classes = [JWTAuthentication]
    filterset_fields = ["status"]
    ordering_fields = ("uploaded_at",)
    ordering = ("-uploaded_at",)
    permission_classes = [IsAuthenticated]

    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.request.method in ["List"]:
            return ExcelUploadSessionListSerializer
        else:
            return ExcelUploadSessionDetailSerializer

    def create(self, request, *args, **kwargs):
        excel_file = request.FILES.get("file")

        if not excel_file:
            return Response(
                {"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not excel_file.name.endswith((".xlsx", ".xls")):
            return Response(
                {"error": "Invalid file type"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Create a new session entry
        session = ExcelUploadSession.objects.create(
            filename=excel_file.name,
            uploaded_by=self.request.user if request.user.is_authenticated else None,
        )

        try:
            xl_file = pd.ExcelFile(excel_file)
            sheets_data = {}
            total_all_rows = 0

            for sheet_name in xl_file.sheet_names:
                # Preview up to 100 rows
                df = pd.read_excel(xl_file, sheet_name=sheet_name, nrows=100)
                df_full = pd.read_excel(xl_file, sheet_name=sheet_name)

                df = df.fillna("")
                headers = df.columns.tolist()
                data = df.values.tolist()

                # Format preview rows for JSON safety
                formatted_data = []
                for row in data:
                    formatted_row = []
                    for cell in row:
                        if pd.isna(cell):
                            formatted_row.append(None)
                        elif isinstance(cell, (pd.Timestamp, datetime)):
                            formatted_row.append(cell.isoformat())
                        else:
                            formatted_row.append(str(cell) if cell != "" else None)
                    formatted_data.append(formatted_row)

                total_rows = len(df_full)
                total_all_rows += total_rows

                sheets_data[sheet_name] = {
                    "headers": headers,
                    "data": formatted_data,
                    "total_rows": total_rows,
                    "preview_rows": min(100, total_rows),
                    "columns": len(headers),
                }

            # Update session
            session.sheets_data = sheets_data
            session.total_rows = total_all_rows
            session.save()

            # Store file temporarily for later confirm
            temp_file_path = _store_temp_file(excel_file)
            cache.set(f"excel_file_{session.id}", temp_file_path, timeout=3600)
            return JsonResponse(
                {
                    "success": True,
                    "session_id": str(session.id),
                    "sheets": sheets_data,
                    "filename": excel_file.name,
                    "total_sheets": len(sheets_data),
                    "total_rows": total_all_rows,
                }
            )
        except Exception as e:
            session.status = ExcelUploadSession.Status.FAILED
            session.error_message = str(e)
            session.save(update_fields=["status", "error_message"])
            return Response(
                {"error": f"Failed to read Excel file: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return custom_response(
            status_text="success",
            message="Record deleted successfully.",
            status_code=status.HTTP_200_OK,
        )


def download_sample_excel(request, target_model: str):
    """
    Generate and download a sample Excel template for a given model.
    """
    if target_model not in RESOURCE_REGISTRY:
        return HttpResponse("Invalid model", status=400)

    resource_class = RESOURCE_REGISTRY[target_model]
    resource = resource_class()

    # Get headers from resource
    dataset = Dataset()
    dataset.headers = [f.column_name for f in resource.get_fields()]

    # Export to Excel (xlsx)
    excel_data = dataset.export("xlsx")

    # Return as downloadable response
    response = HttpResponse(
        excel_data,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = (
        f'attachment; filename="sample_{target_model.replace(".", "_")}.xlsx"'
    )
    return response


class ExcelImportConfirmView(APIView):
    """Async Excel import with background processing"""

    def post(self, request):
        session_id = request.data.get("session_id")
        selected_sheets = request.data.get("selected_sheets", [])
        target_model = request.data.get("target_model")

        # Validation
        if not session_id or not target_model:
            return JsonResponse(
                {"error": "Session ID and target model required"}, status=400
            )

        try:
            session = ExcelUploadSession.objects.get(id=session_id)
        except ExcelUploadSession.DoesNotExist:
            return JsonResponse({"error": "Invalid session"}, status=400)

        if session.processed:
            return JsonResponse({"error": "Session already processed"}, status=400)

        # Get temporary file
        temp_file_path = cache.get(f"excel_file_{session_id}")
        if not temp_file_path or not os.path.exists(temp_file_path):
            return JsonResponse({"error": "File not found or expired"}, status=400)

        # Dispatch task to custom queue
        task = process_excel_import.delay(
            session.id,
            temp_file_path,
            selected_sheets,
            target_model,
        )

        # Store task_id for tracking
        session.status = ExcelUploadSession.Status.QUEUED
        session.task_id = task.id
        session.save(update_fields=["status", "task_id"])

        return JsonResponse(
            {
                "success": True,
                "message": "Import started in background",
                "session_id": str(session_id),
                "task_id": task.id,
                "status": "queued",
            }
        )


class ExcelImportStatusView(APIView):
    def get(self, request, session_id):
        session = get_object_or_404(
            ExcelUploadSession, id=session_id, user=self.request.user
        )
        return JsonResponse(
            {
                "status": session.status,
                "processed": session.processed,
                "results": getattr(session, "results", None),
                "error": getattr(session, "error_message", None),
            }
        )
