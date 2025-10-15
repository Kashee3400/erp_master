from django.utils.translation import gettext_lazy as _

from .managers.case_entry_manager import CaseEntryManager
from ..choices.choices import *
from django.db import models
from django.conf import settings
import random
from .common_models import BaseModel, User, CattleCaseType, PaymentMethod, TreatmentCostConfiguration
from .models import Cattle, CattleStatusType, NonMemberCattle
from django.utils import timezone
from .stock_models import Symptoms, Disease, Medicine
from django.core.validators import MinLengthValidator
from django.db import transaction


class DiagnosisRoute(models.Model):
    route = models.CharField(
        max_length=20,
        verbose_name=_("Diagnosis Route Name"),
        help_text=_(
            "Short name or label of the diagnosis route, e.g., Oral, Injection, etc."
        ),
    )
    locale = models.CharField(
        max_length=10,
        choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE,
        verbose_name=_("Locale"),
        help_text=_("Locale used for this entry (e.g. en, hi, te)"),
    )

    created_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Last Updated At"),
        help_text=_("Timestamp of the last update. Automatically set on update."),
    )
    sync = models.BooleanField(
        default=False,
        verbose_name=_("Is Synced"),
        help_text=_(
            "Flag to track if the record has been synced with external systems."
        ),
    )

    def __str__(self):
        return f"{self.route}"

    class Meta:
        db_table = "tbl_diagnosis_route"
        verbose_name = _("Diagnosis Route")
        verbose_name_plural = _("Diagnosis Routes")
        ordering = ["route"]
        indexes = [
            models.Index(fields=["route"], name="idx_diagnosisroute_route"),
            models.Index(fields=["sync"], name="idx_diagnosisroute_sync"),
        ]

class CaseEntry(BaseModel):
    # Existing cattle field (for members)
    cattle = models.ForeignKey(
        Cattle,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cattle_cases",
        help_text=_("The member cattle associated with this case entry."),
        verbose_name=_("Member Cattle"),
    )

    # New field for non-member cattle
    non_member_cattle = models.ForeignKey(
        NonMemberCattle,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="non_member_cattle_cases",
        help_text=_("The non-member cattle associated with this case entry."),
        verbose_name=_("Non-Member Cattle"),
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="case_entries",
        help_text=_("User who applied or recorded this case."),
        verbose_name=_("Applied By"),
    )

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
        help_text=_("Current status of the case."),
        verbose_name=_("Case Status"),
    )

    address = models.CharField(
        max_length=255,
        default="",
        help_text=_("Address where the case occurred or was reported."),
        verbose_name=_("Address"),
    )

    remark = models.TextField(
        blank=True,
        null=True,
        help_text=_("Additional notes or remarks about the case."),
        verbose_name=_("Remarks"),
    )

    case_no = models.CharField(
        max_length=250,
        primary_key=True,
        validators=[MinLengthValidator(3)],
        help_text=_("Unique identifier for the case."),
        verbose_name=_("Case Number"),
    )

    disease_name = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Disease name in Hindi or English")
    )

    visit_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Scheduled visit date and time")
    )

    is_tagged_animal = models.BooleanField(
        default=True,
        help_text=_("Whether the animal is tagged or non-tagged for cost calculation")
    )

    is_emergency = models.BooleanField(
        default=False,
        help_text=_("Whether this is an emergency treatment")
    )

    calculated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Calculated treatment cost")
    )

    sync = models.BooleanField(
        default=False,
        help_text=_("Indicates whether the entry is synced with the server."),
        verbose_name=_("Sync Status"),
    )
    objects = CaseEntryManager()

    class Meta:
        db_table = "tbl_case_entries"
        verbose_name = _("Case Entry")
        verbose_name_plural = _("Case Entries")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["case_no"], name="idx_caseentry_case_no"),
            models.Index(fields=["cattle"], name="idx_caseentry_cattle"),
            models.Index(fields=["status"], name="idx_caseentry_status"),
        ]

    def clean(self):
        """Validation to ensure either cattle or non_member_cattle is provided"""
        from django.core.exceptions import ValidationError

        if not self.cattle and not self.non_member_cattle:
            raise ValidationError(_("Either member cattle or non-member cattle must be specified."))

        if self.cattle and self.non_member_cattle:
            raise ValidationError(_("Cannot specify both member cattle and non-member cattle."))

    @property
    def is_member_case(self):
        """Check if this is a member case"""
        return self.cattle is not None

    @property
    def is_non_member_case(self):
        """Check if this is a non-member case"""
        return self.non_member_cattle is not None

    @property
    def owner_name(self):
        """Get owner name regardless of member type"""
        if self.cattle and getattr(self.cattle, "owner", None):
            return self.cattle.owner.member_name
        elif self.non_member_cattle and getattr(self.non_member_cattle, "non_member", None):
            return self.non_member_cattle.non_member.name
        return "N/A"

    @property
    def owner_mobile(self):
        """Get owner mobile regardless of member type"""
        if self.cattle:
            return self.cattle.owner.mobile_no if hasattr(self.cattle, 'owner') else "N/A"
        elif self.non_member_cattle:
            return self.non_member_cattle.non_member.mobile_no
        return "N/A"

    @property
    def animal_tag(self):
        """Get animal tag regardless of member type"""
        if self.cattle and hasattr(self.cattle, 'tag_detail') and self.cattle.tag_detail:
            return getattr(self.cattle.tag_detail, 'tag_number', 'N/A')
        elif self.non_member_cattle:
            return self.non_member_cattle.tag_number
        return "N/A"

    # Updated method for CaseEntry model

    def calculate_treatment_cost(self):
        """Calculate treatment cost based on configuration table"""
        from datetime import time

        if not self.visit_date:
            return 0

        # Determine parameters
        visit_time = self.visit_date.time()
        is_member = self.is_member_case

        # Map to configuration choices
        membership_type = MembershipTypeChoices.MEMBER if is_member else MembershipTypeChoices.NON_MEMBER
        time_slot = TimeSlotChoices.BEFORE_10AM if visit_time < time(10, 0) else TimeSlotChoices.AFTER_10AM
        animal_tag_type = AnimalTagChoices.TAGGED if self.is_tagged_animal else AnimalTagChoices.NON_TAGGED
        treatment_type = TreatmentTypeChoices.EMERGENCY if self.is_emergency else TreatmentTypeChoices.NORMAL

        # Get cost from configuration table
        cost_amount = TreatmentCostConfiguration.get_cost(
            membership_type=membership_type,
            time_slot=time_slot,
            animal_tag_type=animal_tag_type,
            treatment_type=treatment_type,
            visit_date=self.visit_date.date()
        )

        return float(cost_amount)

    @classmethod
    def assign_to(cls, case_no, to_user, remarks=None):
        """
        Assign a case to a user and log the transfer.
        (Your existing method - unchanged)
        """
        from django.core.exceptions import ObjectDoesNotExist

        if not case_no or not to_user:
            raise ValueError(_("Both 'case_no' and 'to_user' are required."))

        try:
            case = cls.objects.select_for_update().get(case_no=case_no)
        except ObjectDoesNotExist:
            raise ValueError(
                _("Case with number '{case_no}' does not exist.").format(
                    case_no=case_no
                )
            )

        with transaction.atomic():
            previous_user = case.created_by

            if previous_user == to_user:
                raise ValueError(_("The case is already assigned to this user."))

            # Update assignment
            case.created_by = to_user
            case.save(update_fields=["created_by", "updated_at"])

            # Create transfer log (assuming you have CaseReceiverLog model)
            CaseReceiverLog.objects.create(
                case_entry=case,
                from_user=previous_user,
                to_user=to_user,
                remarks=remarks or _("Assigned via system action."),
            )

        return case

    def __str__(self):
        created_by = self.created_by.get_full_name() if self.created_by else _("N/A")
        owner = self.owner_name
        return f"{self.case_no} - {owner} - {created_by}"

    def save(self, *args, **kwargs):
        # Auto-calculate cost before saving
        if self.visit_date:
            self.calculated_cost = self.calculate_treatment_cost()

        if not self.case_no:
            farmer_code = "UNKNOWN"
            tag_number = "NA"
            timestamp = timezone.now().strftime("%Y%m%d-%H%M%S")

            # Handle member cattle
            if self.cattle and hasattr(self.cattle, "owner") and self.cattle.owner:
                if hasattr(self.cattle.owner, 'member_code'):
                    farmer_code = self.cattle.owner.member_code[-6:]

                if hasattr(self.cattle, 'tag_detail') and self.cattle.tag_detail:
                    tag_number = getattr(self.cattle.tag_detail, 'tag_number', 'NA')
                elif hasattr(self.cattle, 'tag_number'):
                    tag_number = self.cattle.tag_number

            # Handle non-member cattle
            elif self.non_member_cattle:
                farmer_code = self.non_member_cattle.non_member.non_member_id[-6:]
                tag_number = self.non_member_cattle.tag_number

            if tag_number != "NA":
                self.case_no = f"{farmer_code}-{tag_number}-{timestamp}"
            else:
                rand_suffix = random.randint(100, 999)
                self.case_no = f"{farmer_code}-{tag_number}-{timestamp}-{rand_suffix}"

        super().save(*args, **kwargs)

        # Update visit count for non-members
        if self.non_member_cattle:
            non_member = self.non_member_cattle.non_member
            non_member.visit_count = CaseEntry.objects.filter(
                non_member_cattle__non_member=non_member
            ).count()
            non_member.save(update_fields=['visit_count'])


class CaseReceiverLog(BaseModel):
    case_entry = models.ForeignKey(
        CaseEntry,
        on_delete=models.CASCADE,
        related_name="receiver_logs",
        blank=True,
        null=True,
        verbose_name=_("Case Entry"),
        help_text=_("Reference to the case entry being transferred."),
    )

    assigned_from = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="case_transferred_from",
        verbose_name=_("Transferred From"),
        help_text=_("User who previously handled the case."),
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="case_transferred_to",
        verbose_name=_("Transferred To"),
        help_text=_("User who is receiving the case."),
    )

    remarks = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Remarks"),
        help_text=_("Optional remarks for the transfer."),
    )

    transferred_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Transferred At"),
        help_text=_("Timestamp of when the case was transferred."),
    )

    def __str__(self):
        return _("Case: {case_no} | {from_user} ➝ {to_user} @ {timestamp}").format(
            case_no=self.case_entry.case_no if self.case_entry else _("N/A"),
            from_user=self.assigned_from or _("System"),
            to_user=self.assigned_to,
            timestamp=self.transferred_at.strftime("%Y-%m-%d %H:%M"),
        )

    class Meta:
        db_table = "tbl_case_receiver_logs"
        verbose_name = _("Case Receiver Log")
        verbose_name_plural = _("Case Receiver Logs")
        ordering = ["-transferred_at"]
        indexes = [
            models.Index(fields=["case_entry"], name="idx_receiverlog_case"),
            models.Index(fields=["assigned_to"], name="idx_receiverlog_to_user"),
            models.Index(
                fields=["transferred_at"], name="idx_receiverlog_transferred_at"
            ),
        ]


class AnimalDiagnosis(BaseModel):
    case_entry = models.ForeignKey(
        CaseEntry,
        on_delete=models.CASCADE,
        related_name="diagnoses",
        verbose_name=_("Case Entry"),
        help_text=_("The case entry associated with this diagnosis."),
    )

    disease = models.ForeignKey(
        Disease,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Disease"),
        help_text=_("Identified disease during the diagnosis."),
    )

    status = models.ForeignKey(
        CattleStatusType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Cattle Status"),
        help_text=_("Current physiological or production status of the animal."),
    )

    milk_production = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Milk Production"),
        help_text=_("Optional note on milk production (e.g., '2.5L/day')."),
    )

    case_type = models.ForeignKey(
        CattleCaseType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Case Type"),
        help_text=_(
            "Type of the veterinary case (e.g., Normal, Special, Operational)."
        ),
    )

    def __str__(self):
        tag = (
            getattr(self.case_entry.cattle.tag_detail, "tag_number", _("Unknown"))
            if self.case_entry and hasattr(self.case_entry, "cattle")
            else _("N/A")
        )
        disease_name = self.disease.disease if self.disease else _("Unknown Disease")
        return _("{tag} - {disease} @ {date}").format(
            tag=tag,
            disease=disease_name,
            date=self.created_at.strftime("%Y-%m-%d"),
        )

    class Meta:
        db_table = "tbl_animal_diagnosis"
        verbose_name = _("Animal Diagnosis")
        verbose_name_plural = _("Animal Diagnoses")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["case_entry"], name="idx_diagnosis_case_entry"),
            models.Index(fields=["disease"], name="idx_diagnosis_disease"),
            models.Index(fields=["status"], name="idx_diagnosis_status"),
        ]


class DiagnosedSymptomHistory(BaseModel):
    symptom = models.ForeignKey(
        Symptoms,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Symptom"),
        help_text=_("Symptom associated with this diagnosis."),
    )

    diagnosis = models.ForeignKey(
        AnimalDiagnosis,
        on_delete=models.CASCADE,
        related_name="diagnosis_symptoms",
        verbose_name=_("Animal Diagnosis"),
        help_text=_("Diagnosis entry this symptom is related to."),
    )

    remark = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Remark"),
        help_text=_("Additional notes or observations about the symptom."),
    )

    def __str__(self):
        diagnosis_str = (
            self.diagnosis.disease.disease
            if self.diagnosis and self.diagnosis.disease
            else _("Unknown Diagnosis")
        )
        symptom_str = self.symptom.symptom if self.symptom else _("Unknown Symptom")
        return _("{diagnosis} - {symptom} @ {date}").format(
            diagnosis=diagnosis_str,
            symptom=symptom_str,
            date=self.created_at.strftime("%Y-%m-%d"),
        )

    class Meta:
        db_table = "tbl_animal_diagnosed_symptom"
        verbose_name = _("Diagnosed Symptom")
        verbose_name_plural = _("Diagnosed Symptoms")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["diagnosis"], name="idx_symptom_diagnosis"),
            models.Index(fields=["symptom"], name="idx_symptom_symptom"),
        ]


class AnimalTreatment(BaseModel):
    case_treatment = models.ForeignKey(
        CaseEntry,
        on_delete=models.CASCADE,
        related_name="animal_treatments",
        blank=True,
        null=True,
        verbose_name=_("Case Entry"),
        help_text=_("The case entry to which this treatment belongs."),
    )

    treatment_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="treatments_done",
        verbose_name=_("Treatment Provider"),
        help_text=_("User (doctor or vet) who performed the treatment."),
    )

    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Medicine"),
        help_text=_("Medicine used in the treatment, if any."),
    )

    route = models.ForeignKey(
        DiagnosisRoute,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Administration Route"),
        help_text=_("Route of administration for the medicine."),
    )

    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Notes"),
        help_text=_("Additional notes or instructions for the treatment."),
    )

    otp_verified = models.BooleanField(
        default=False,
        verbose_name=_("OTP Verified"),
        help_text=_("Indicates whether the treatment has been verified via OTP."),
    )

    def __str__(self):
        case_no = self.case_treatment.case_no if self.case_treatment else _("No Case")
        medicine_name = self.medicine.name if self.medicine else _("No Medicine")
        return _("Treatment for Case: {case} | Medicine: {med} | By: {user}").format(
            case=case_no,
            med=medicine_name,
            user=self.treatment_by.username,
        )

    class Meta:
        db_table = "tbl_animal_treatments"
        verbose_name = _("Animal Treatment")
        verbose_name_plural = _("Animal Treatments")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["case_treatment"], name="idx_treatment_case"),
            models.Index(fields=["treatment_by"], name="idx_treatment_by"),
            models.Index(fields=["medicine"], name="idx_treatment_medicine"),
        ]


class CasePayment(models.Model):
    case_entry = models.ForeignKey(
        CaseEntry,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name=_("Case Entry"),
        help_text=_("Case associated with this payment."),
    )

    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.CASCADE,
        verbose_name=_("Payment Method"),
        help_text=_("Method used for payment."),
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Amount"),
        help_text=_("Amount paid."),
    )

    payment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Payment Date"),
        help_text=_("Date and time when the payment was made."),
    )

    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Transaction ID"),
        help_text=_("Payment gateway reference or manual receipt ID."),
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatusChoices.choices,
        default=PaymentStatusChoices.PENDING,
        verbose_name=_("Payment Status"),
        help_text=_("Current status of the payment."),
    )

    gateway_response = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_("Gateway Response"),
        help_text=_("Raw payment gateway response data (online payments only)."),
    )

    is_reconciled = models.BooleanField(
        default=False,
        verbose_name=_("Is Reconciled"),
        help_text=_("Whether this payment is reconciled in accounting."),
    )

    is_collected = models.BooleanField(
        default=False,
        verbose_name=_("Is Cash Collected"),
        help_text=_("Indicates if cash has been collected for offline payments."),
    )

    collected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="collected_payments",
        verbose_name=_("Collected By"),
        help_text=_("User who collected the payment (for COD)."),
    )

    collected_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Collected Date"),
        help_text=_("Date and time when cash was collected."),
    )

    def __str__(self):
        method_name = getattr(
            getattr(self.payment_method, "online_payment", None), "gateway_name", None
        ) or getattr(self.payment_method, "method", _("Unknown Method"))
        return _("Payment: ₹{amount} for Case: {case} via {method} [{status}]").format(
            amount=self.amount,
            case=self.case_entry.case_no if self.case_entry else _("N/A"),
            method=method_name,
            status=self.get_payment_status_display(),
        )

    class Meta:
        db_table = "tbl_case_payments"
        verbose_name = _("Case Payment")
        verbose_name_plural = _("Case Payments")
        ordering = ["-payment_date"]
        indexes = [
            models.Index(fields=["case_entry"], name="idx_payment_case_entry"),
            models.Index(fields=["payment_method"], name="idx_payment_method"),
            models.Index(fields=["payment_status"], name="idx_payment_status"),
            models.Index(fields=["transaction_id"], name="idx_payment_txnid"),
        ]


from math import radians, sin, cos, sqrt, atan2


class TravelRecord(models.Model):
    case_entry = models.OneToOneField(
        "CaseEntry",
        on_delete=models.CASCADE,
        related_name="travel_record",
        verbose_name=_("Case Entry"),
        help_text=_("Case related to this travel record."),
    )

    from_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name=_("From Latitude"),
        help_text=_("Starting point latitude."),
    )
    from_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name=_("From Longitude"),
        help_text=_("Starting point longitude."),
    )
    to_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name=_("To Latitude"),
        help_text=_("Destination latitude."),
    )
    to_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name=_("To Longitude"),
        help_text=_("Destination longitude."),
    )

    distance_travelled = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Distance Travelled (km)"),
        help_text=_("Calculated distance in kilometers."),
    )

    date = models.DateField(
        verbose_name=_("Travel Date"),
        help_text=_("Date of the travel."),
    )

    def __str__(self):
        return _(
            "Case Entry: {case_no} | Distance: {distance} km | Date: {date}"
        ).format(
            case_no=self.case_entry.case_no if self.case_entry else _("N/A"),
            distance=self.distance_travelled,
            date=self.date.strftime("%Y-%m-%d"),
        )

    def save(self, *args, **kwargs):
        # Automatically calculate distance before saving
        if all(
                [
                    self.from_latitude,
                    self.from_longitude,
                    self.to_latitude,
                    self.to_longitude,
                ]
        ):
            self.distance_travelled = self.calculate_distance()
        super().save(*args, **kwargs)

    def add_image(self, image_file, description=""):
        """
        Helper to attach image to this travel record.
        """
        return self.images.create(image=image_file, description=description)

    def calculate_distance(self) -> float:
        """
        Haversine formula to calculate distance in km.
        """
        from_lat = radians(float(self.from_latitude))
        from_lon = radians(float(self.from_longitude))
        to_lat = radians(float(self.to_latitude))
        to_lon = radians(float(self.to_longitude))

        dlat = to_lat - from_lat
        dlon = to_lon - from_lon

        a = sin(dlat / 2) ** 2 + cos(from_lat) * cos(to_lat) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        R = 6371.0  # Earth radius in km

        return round(R * c, 2)

    class Meta:
        db_table = "tbl_travel_records"
        verbose_name = _("Travel Record")
        verbose_name_plural = _("Travel Records")
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["case_entry"], name="idx_travel_case_entry"),
            models.Index(fields=["date"], name="idx_travel_date"),
        ]


class TravelRecordImage(models.Model):
    travel_record = models.ForeignKey(
        TravelRecord,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("Travel Record"),
        help_text=_("Travel record associated with this image."),
    )

    image = models.ImageField(
        upload_to="travel_records/%Y/%m/%d/",
        verbose_name=_("Image"),
        help_text=_("Upload image related to the travel, such as vehicle dashboard, odometer, or scene."),
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Uploaded At"),
        help_text=_("Time when image was uploaded."),
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Description"),
        help_text=_("Optional notes about this image."),
    )

    def __str__(self):
        return _("Image for Travel Record ID: {id}").format(id=self.travel_record.id)

    class Meta:
        db_table = "tbl_travel_record_images"
        verbose_name = _("Travel Record Image")
        verbose_name_plural = _("Travel Record Images")
        ordering = ["-uploaded_at"]
        indexes = [
            models.Index(fields=["travel_record"], name="idx_travel_image_record"),
        ]
