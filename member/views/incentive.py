from all_imports import *
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from ..models import SahayakIncentives
from ..forms import SahayakIncentivesForm
from ..filters import SahayakIncentivesFilter
from ..resources import SahayakIncentivesResource


class SahayakIncentivesAllInOneView(LoginRequiredMixin, View, ImportExportModelAdmin):
    template_name = "member/pages/dashboards/sahayak_incentives_all.html"
    form_class = SahayakIncentivesForm
    excel_form = ImportForm
    resource_class = SahayakIncentivesResource
    import_template_name = "member/form/confirm_excel_import.html"
    success_url = reverse_lazy("sahayak_incentives_list")
    model = SahayakIncentives

    export_template_name = "member/form/export.html"

    def get(self, request, *args, **kwargs):
        query = request.GET.get("q", "")
        filter_class = SahayakIncentivesFilter(
            request.GET, queryset=SahayakIncentives.objects.all().order_by("-id")
        )
        incentives = self.get_filtered_incentives(query, filter_class)
        # Pagination setup
        page_number = request.GET.get("page", 1)
        per_page = (
            settings.PAGINATION_SIZE if hasattr(settings, "PAGINATION_SIZE") else 100
        )
        paginator = Paginator(incentives, per_page)
        paginated_incentives = paginator.get_page(page_number)
        actions = [
            {"value": "bulk_delete", "label": "Delete Selected"},
            {"value": "export_csv", "label": "Export Selected"},
        ]
        import_form = self.create_import_form(request=request)
        total_rows = incentives.count()
        context = {
            "objects": paginated_incentives,
            "form": self.form_class(),
            "filter": filter_class,
            "import_form": import_form,
            "actions": actions,
            "total_rows": total_rows,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        import_excel = request.POST.get("excel_import")
        process_import = request.POST.get("process_import")
        if action:
            handler = getattr(self, f"handle_{action}", None)
            if handler:
                return handler(request)
        elif import_excel and import_excel == "excel_import":
            handler = getattr(self, f"import_action", None)
            return handler(request)
        elif process_import and process_import == "process_import":
            handler = getattr(self, f"process_import", None)
            return handler(request)
        return self.get(request)

    def get_filtered_incentives(self, query, filter_class):
        if query:
            return SahayakIncentives.objects.filter(
                Q(mcc_name__icontains=query)
                | Q(mpp_name__icontains=query)
                | Q(user__username__icontains=query)
            )
        return filter_class.qs

    def import_action(self, request, **kwargs):
        """
        Perform a dry_run of the import to make sure the import will not
        result in errors.  If there are no errors, save the user
        uploaded file to a local temp file that will be used by
        'process_import' for the actual import.
        """
        if not self.has_import_permission(request):
            raise PermissionDenied

        context = self.get_import_context_data()

        import_formats = self.get_import_formats()
        import_form = self.create_import_form(request)
        if request.POST and import_form.is_valid():
            input_format = import_formats[int(import_form.cleaned_data["format"])]()
            if not input_format.is_binary():
                input_format.encoding = self.from_encoding
            import_file = import_form.cleaned_data["import_file"]
            if self.is_skip_import_confirm_enabled():
                data = b""
                for chunk in import_file.chunks():
                    data += chunk
                try:
                    dataset = input_format.create_dataset(data)
                except Exception as e:
                    self.add_data_read_fail_error_to_form(import_form, e)
                if not import_form.errors:
                    result = self.process_dataset(
                        dataset,
                        import_form,
                        request,
                        raise_errors=False,
                        rollback_on_validation_errors=True,
                        **kwargs,
                    )
                    if not result.has_errors() and not result.has_validation_errors():
                        return self.process_result(result, request)
                    else:
                        context["result"] = result
            else:
                tmp_storage = self.write_to_tmp_storage(import_file, input_format)
                import_file.tmp_storage_name = tmp_storage.name
                try:
                    data = tmp_storage.read()
                    dataset = input_format.create_dataset(data)
                except Exception as e:
                    self.add_data_read_fail_error_to_form(import_form, e)
                else:
                    if len(dataset) == 0:
                        import_form.add_error(
                            "import_file",
                            _(
                                "No valid data to import. Ensure your file "
                                "has the correct headers or data for import."
                            ),
                        )
                if not import_form.errors:
                    # prepare kwargs for import data, if needed
                    res_kwargs = self.get_import_resource_kwargs(
                        request, form=import_form, **kwargs
                    )
                    resource = self.choose_import_resource_class(import_form, request)(
                        **res_kwargs
                    )
                    # prepare additional kwargs for import_data, if needed
                    imp_kwargs = self.get_import_data_kwargs(
                        request=request, form=import_form, **kwargs
                    )
                    result = resource.import_data(
                        dataset,
                        dry_run=True,
                        raise_errors=False,
                        file_name=import_file.name,
                        user=request.user,
                        **imp_kwargs,
                    )
                    context["result"] = result

                    if not result.has_errors() and not result.has_validation_errors():
                        context["confirm_form"] = self.create_confirm_form(
                            request, import_form=import_form
                        )
        else:
            res_kwargs = self.get_import_resource_kwargs(
                request=request, form=import_form, **kwargs
            )
        context.update(self.get_context_data())
        context["title"] = _("Import Sahayak Incentive Preview")
        context["form"] = import_form
        context["media"] = self.media + import_form.media
        context["import_error_display"] = self.import_error_display
        request.current_app = "Kashee ERP"
        return TemplateResponse(request, [self.import_template_name], context)

    def process_import(self, request, **kwargs):
        """
        Perform the actual import action (after the user has confirmed the import)
        """
        if not self.has_import_permission(request):
            raise PermissionDenied

        confirm_form = self.create_confirm_form(request)
        if confirm_form.is_valid():
            import_formats = self.get_import_formats()
            input_format = import_formats[int(confirm_form.cleaned_data["format"])](
                encoding=self.from_encoding
            )
            encoding = None if input_format.is_binary() else self.from_encoding
            tmp_storage_cls = self.get_tmp_storage_class()
            tmp_storage = tmp_storage_cls(
                name=confirm_form.cleaned_data["import_file_name"],
                encoding=encoding,
                read_mode=input_format.get_read_mode(),
                **self.get_tmp_storage_class_kwargs(),
            )

            data = tmp_storage.read()
            dataset = input_format.create_dataset(data)
            result = self.process_dataset(dataset, confirm_form, request, **kwargs)

            tmp_storage.remove()

            return self.process_result(result, request)
        else:
            context = self.get_context_data()
            context.update(
                {
                    "title": _("Import"),
                    "confirm_form": confirm_form,
                    "opts": self.model._meta,
                    "errors": confirm_form.errors,
                }
            )
            return TemplateResponse(request, [self.import_template_name], context)

    def process_result(self, result, request):
        self.generate_log_entries(result, request)
        self.add_success_message(result, request)
        # post_import.send(sender=None, model=self.model)

        return redirect(self.success_url)

    def handle_bulk_delete(self, request):
        ids = self.request.POST.getlist("selected_rows")
        if ids:
            SahayakIncentives.objects.filter(id__in=ids).delete()
            messages.success(request, "Selected incentives deleted successfully!")
        else:
            messages.warning(request, "No incentives were selected for deletion.")
        return redirect(self.success_url)

    def handle_export_csv(self, request):
        return self.export_to_csv()

    def save_form(self, form, action):
        if form.is_valid():
            form.save()
            messages.success(self.request, f"Sahayak incentive {action} successfully!")
        else:
            messages.error(self.request, f"Error {action} incentive.")
        return redirect(self.success_url)

    def export_to_csv(self):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            'attachment; filename="sahayak_incentives.csv"'
        )
        writer = csv.writer(response)
        writer.writerow(
            [
                "User",
                "MCC Code",
                "MCC Name",
                "MPP Code",
                "MPP Name",
                "Month",
                "Opening",
                "Milk Incentive",
                "Other Incentive",
                "Payable",
                "Closing",
            ]
        )

        for incentive in SahayakIncentives.objects.all():
            writer.writerow(
                [
                    incentive.user.username,
                    incentive.mcc_code,
                    incentive.mcc_name,
                    incentive.mpp_code,
                    incentive.mpp_name,
                    incentive.month,
                    incentive.opening,
                    incentive.milk_incentive,
                    incentive.other_incentive,
                    incentive.payable,
                    incentive.closing,
                ]
            )
        return response


class SahayakIncentivesCreateView(CreateView):
    model = SahayakIncentives
    form_class = SahayakIncentivesForm
    template_name = "member/form/creation_form.html"
    success_url = reverse_lazy("sahayak_incentives_list")

    def form_valid(self, form):
        messages.success(self.request, "Sahayak incentive created successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Error creating Sahayak incentive. Please correct the errors below.",
        )
        return super().form_invalid(form)


class SahayakIncentivesUpdateView(UpdateView):
    model = SahayakIncentives
    form_class = SahayakIncentivesForm
    template_name = "member/form/creation_form.html"
    success_url = reverse_lazy("sahayak_incentives_list")

    def get_object(self, queryset=None):
        # Get the object to be updated
        return get_object_or_404(SahayakIncentives, id=self.kwargs["pk"])

    def form_valid(self, form):
        # Custom processing before saving
        return super().form_valid(form)


class SahayakIncentivesViewSet(viewsets.ModelViewSet):
    queryset = SahayakIncentives.objects.all()
    serializer_class = SahayakIncentivesSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "user",
        "mcc_code",
        "mcc_name",
        "mpp_code",
        "mpp_name",
        "month",
        "year",
    ]
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SahayakIncentives.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(
                    {
                        "status": "success",
                        "message": "Incentives retrieved successfully",
                        "result": serializer.data,
                    }
                )
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "status": "success",
                    "message": "Incentives retrieved successfully",
                    "result": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": "Error retrieving incentives",
                    "result": {},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
