from import_export.widgets import ForeignKeyWidget, ManyToManyWidget, DateWidget, BooleanWidget, Widget
from import_export.results import RowResult
from django.db import IntegrityError
from datetime import timezone
from ..models.models import (
    Cattle,
    CattleTagging,
    CattleStatusLog,
    MembersMasterCopy,
    SpeciesBreed,
    CattleStatusType,
    GenderChoices,
    TagMethodChoices,
    TagLocationChoices,
    TagActionChoices,
    MonthChoices
)
import logging
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from import_export import resources, fields
from decimal import Decimal, InvalidOperation

logger = logging.getLogger(__name__)


class SmartBooleanWidget(BooleanWidget):
    """Enhanced boolean widget that handles various input formats"""

    def clean(self, value, row=None, **kwargs):
        if value is None or value == '':
            return False

        if isinstance(value, bool):
            return value

        if isinstance(value, (int, float)):
            return bool(value)

        if isinstance(value, str):
            value = value.lower().strip()
            true_values = {'yes', 'y', '1', 'true', 't', 'on', 'active'}
            false_values = {'no', 'n', '0', 'false', 'f', 'off', 'inactive', ''}

            if value in true_values:
                return True
            elif value in false_values:
                return False

        # Default to False for unrecognized values
        logger.warning(f"Unrecognized boolean value: {value}, defaulting to False")
        return False


class SafeDateWidget(DateWidget):
    """Date widget with enhanced error handling"""

    def clean(self, value, row=None, **kwargs):
        if not value or value == '':
            return None

        try:
            return super().clean(value, row, **kwargs)
        except (ValueError, TypeError) as e:
            logger.warning(f"Date parsing error for value '{value}': {e}")
            return None


class CustomForeignKeyWidget(ForeignKeyWidget):
    """Enhanced ForeignKey widget with better error handling"""

    def clean(self, value, row=None, **kwargs):
        if not value or value == '':
            return None

        try:
            return super().clean(value, row, **kwargs)
        except Exception as e:
            logger.error(f"ForeignKey lookup failed for {self.model.__name__} with value '{value}': {e}")
            raise ValidationError(f"Invalid {self.model.__name__}: {value}")


class DecimalWidget(Widget):
    """Widget for handling decimal values safely"""

    def clean(self, value, row=None, **kwargs):
        if not value or value == '':
            return None

        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            logger.warning(f"Invalid decimal value: {value}, defaulting to 0")
            return Decimal('0')


class SmartDateWidget(DateWidget):
    """Enhanced date widget that handles multiple date formats"""

    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return None

        # Handle various date formats
        date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S']

        for fmt in date_formats:
            try:
                from datetime import datetime
                return datetime.strptime(str(value), fmt).date()
            except (ValueError, TypeError):
                continue

        return super().clean(value, row, **kwargs)


class CattleResource(resources.ModelResource):
    """Resource class for Cattle model with Excel import/export"""

    # Define fields with custom widgets
    owner = fields.Field(
        column_name='owner_name',
        attribute='owner',
        widget=CustomForeignKeyWidget(MembersMasterCopy, 'name')
    )

    breed = fields.Field(
        column_name='breed_name',
        attribute='breed',
        widget=CustomForeignKeyWidget(SpeciesBreed, 'breed_name')
    )

    mother = fields.Field(
        column_name='mother_tag',
        attribute='mother',
        widget=CustomForeignKeyWidget(Cattle, 'cattle_tagged__tag_number')
    )

    father = fields.Field(
        column_name='father_tag',
        attribute='father',
        widget=CustomForeignKeyWidget(Cattle, 'cattle_tagged__tag_number')
    )

    current_status = fields.Field(
        column_name='current_status_code',
        attribute='current_status',
        widget=CustomForeignKeyWidget(CattleStatusType, 'code')
    )

    date_of_birth = fields.Field(
        column_name='date_of_birth',
        attribute='date_of_birth',
        widget=SafeDateWidget('%Y-%m-%d')
    )

    # Read-only computed fields for export
    tag_number = fields.Field(
        column_name='tag_number',
        attribute='tag_detail__tag_number',
        readonly=True
    )

    children_count = fields.Field(
        column_name='children_count',
        readonly=True
    )

    class Meta:
        model = Cattle
        fields = (
            'id', 'name', 'owner', 'breed', 'gender', 'age', 'age_year',
            'no_of_calving', 'mother', 'father', 'date_of_birth', 'is_alive',
            'current_status', 'tag_number', 'children_count', 'created_at'
        )
        export_order = fields
        import_id_fields = ('name', 'owner', 'breed')
        skip_unchanged = True
        report_skipped = True
        use_bulk = True
        batch_size = 1000

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        """Pre-process dataset before import"""
        logger.info(f"Starting cattle import: {len(dataset)} rows")

        # Validate required columns
        required_columns = ['name', 'owner_name', 'breed_name', 'gender', 'age']
        missing_columns = [col for col in required_columns if col not in dataset.headers]

        if missing_columns:
            raise ValidationError(f"Missing required columns: {', '.join(missing_columns)}")

        # Clean and validate data
        for i, row in enumerate(dataset.dict):
            try:
                # Validate gender
                if row.get('gender') and row['gender'].upper() not in [choice[0] for choice in GenderChoices.choices]:
                    logger.warning(f"Row {i + 1}: Invalid gender '{row['gender']}', defaulting to MALE")
                    row['gender'] = GenderChoices.MALE

                # Validate age
                if row.get('age'):
                    try:
                        age = int(float(row['age']))
                        if age < 0:
                            raise ValueError("Age cannot be negative")
                        row['age'] = age
                    except (ValueError, TypeError):
                        logger.warning(f"Row {i + 1}: Invalid age '{row['age']}', setting to 0")
                        row['age'] = 0

                # Clean name
                if row.get('name'):
                    row['name'] = str(row['name']).strip()[:100]

            except Exception as e:
                logger.error(f"Row {i + 1} preprocessing error: {e}")

    def before_import_row(self, row, row_number=None, **kwargs):
        """Process each row before import"""
        try:
            # Additional row-level validation
            if not row.get('name') or not str(row['name']).strip():
                row['name'] = f"Cattle_{row_number}_{timezone.now().strftime('%Y%m%d_%H%M%S')}"

            # Set default values
            if not row.get('is_alive'):
                row['is_alive'] = True

            if not row.get('gender'):
                row['gender'] = GenderChoices.MALE

        except Exception as e:
            logger.error(f"Row {row_number} before_import_row error: {e}")

    def import_row(self, row, instance_loader, using_transactions=True, dry_run=False, **kwargs):
        """Import a single row with error handling"""
        row_result = RowResult()

        try:
            with transaction.atomic():
                result = super().import_row(row, instance_loader, using_transactions, dry_run, **kwargs)

                # Additional business logic after successful import
                if not dry_run and result.object_id:
                    cattle = Cattle.objects.get(pk=result.object_id)

                    # Auto-calculate age_year if not provided
                    if not cattle.age_year and cattle.age:
                        cattle.age_year = cattle.age // 12
                        cattle.save(update_fields=['age_year'])

                return result

        except ValidationError as e:
            row_result.errors.append(f"Validation Error: {e}")
            logger.warning(f"Validation error in row import: {e}")

        except IntegrityError as e:
            row_result.errors.append(f"Database Error: Duplicate or invalid data")
            logger.error(f"Integrity error in row import: {e}")

        except Exception as e:
            row_result.errors.append(f"Import Error: {str(e)}")
            logger.error(f"Unexpected error in row import: {e}")

        return row_result

    def after_import(self, dataset, result, using_transactions, dry_run, **kwargs):
        """Post-process after import completion"""
        if not dry_run:
            logger.info(f"Import completed: {result.totals}")

            # Update related data if needed
            try:
                # Refresh cattle relationships
                imported_ids = [row.object_id for row in result.rows if row.object_id]
                if imported_ids:
                    Cattle.objects.filter(id__in=imported_ids).update(
                        updated_at=timezone.now()
                    )
            except Exception as e:
                logger.error(f"Post-import processing error: {e}")

    def dehydrate_children_count(self, cattle):
        """Export children count"""
        try:
            return cattle.children.count()
        except:
            return 0

    def export(self, queryset=None, *args, **kwargs):
        """Custom export with optimized queries"""
        if queryset is None:
            queryset = self.get_queryset()

        # Optimize queryset for export
        queryset = queryset.select_related(
            'owner', 'breed', 'mother', 'father', 'current_status'
        ).prefetch_related(
            'offspring_from_mother', 'cattle_tagged'
        )

        return super().export(queryset, *args, **kwargs)


class CattleTaggingResource(resources.ModelResource):
    """Resource class for Cattle Tagging"""

    cattle = fields.Field(
        column_name='cattle_name',
        attribute='cattle',
        widget=CustomForeignKeyWidget(Cattle, 'name')
    )

    cattle_tag = fields.Field(
        column_name='cattle_existing_tag',
        attribute='cattle',
        widget=CustomForeignKeyWidget(Cattle, 'cattle_tagged__tag_number')
    )

    class Meta:
        model = CattleTagging
        fields = (
            'id', 'cattle', 'cattle_tag', 'tag_number', 'tag_method',
            'tag_location', 'tag_action', 'replaced_on', 'remarks', 'created_at'
        )
        import_id_fields = ('tag_number',)

    def before_import_row(self, row, row_number=None, **kwargs):
        """Validate tag data before import"""
        try:
            # Ensure tag_number is unique
            if row.get('tag_number'):
                row['tag_number'] = str(row['tag_number']).strip().upper()

            # Set defaults
            if not row.get('tag_method'):
                row['tag_method'] = TagMethodChoices.MANUAL

            if not row.get('tag_location'):
                row['tag_location'] = TagLocationChoices.LEFT_EAR

            if not row.get('tag_action'):
                row['tag_action'] = TagActionChoices.CREATED

        except Exception as e:
            logger.error(f"Tag row {row_number} preprocessing error: {e}")


class CattleStatusLogResource(resources.ModelResource):
    """Resource class for Cattle Status Log"""

    cattle = fields.Field(
        column_name='cattle_tag',
        attribute='cattle',
        widget=CustomForeignKeyWidget(Cattle, 'cattle_tagged__tag_number')
    )

    statuses = fields.Field(
        column_name='status_codes',
        attribute='statuses',
        widget=ManyToManyWidget(CattleStatusType, field='code', separator='|')
    )

    from_date = fields.Field(
        column_name='from_date',
        attribute='from_date',
        widget=SafeDateWidget('%Y-%m-%d')
    )

    to_date = fields.Field(
        column_name='to_date',
        attribute='to_date',
        widget=SafeDateWidget('%Y-%m-%d')
    )

    class Meta:
        model = CattleStatusLog
        fields = (
            'id', 'cattle', 'last_calving_month', 'statuses',
            'from_date', 'to_date', 'notes', 'pregnancy_status', 'created_at'
        )

    def before_import_row(self, row, row_number=None, **kwargs):
        """Validate status log data"""
        try:
            # Set default from_date if not provided
            if not row.get('from_date'):
                row['from_date'] = timezone.now().date()

            # Validate last_calving_month
            if row.get('last_calving_month'):
                valid_months = [choice[0] for choice in MonthChoices.choices]
                if row['last_calving_month'].upper() not in valid_months:
                    logger.warning(f"Row {row_number}: Invalid month '{row['last_calving_month']}'")
                    row['last_calving_month'] = None

        except Exception as e:
            logger.error(f"Status log row {row_number} preprocessing error: {e}")


class CombinedCattleResource(resources.ModelResource):
    """Simple but effective resource for importing/exporting cattle"""

    # ---------------- Cattle Fields ----------------
    cattle_code = fields.Field(column_name="Cattle Code", attribute="cattle_code")
    name = fields.Field(column_name="Cattle Name", attribute="name")
    owner = fields.Field(
        column_name='Member Code',
        attribute='owner',
        widget=CustomForeignKeyWidget(MembersMasterCopy, 'member_tr_code')
    )
    breed = fields.Field(
        column_name='Breed',
        attribute='breed',
        widget=CustomForeignKeyWidget(SpeciesBreed, 'breed')
    )
    gender = fields.Field(column_name="Gender", attribute="gender")
    age = fields.Field(column_name="Age (Month)", attribute="age")
    age_year = fields.Field(column_name="Age (Year)", attribute="age_year")
    current_status = fields.Field(
        column_name='Animal Status',
        attribute='current_status',
        widget=CustomForeignKeyWidget(CattleStatusType, 'code')
    )
    no_of_calving = fields.Field(column_name="Lactation Count", attribute="no_of_calving")
    is_active = fields.Field(column_name="Is Active", attribute="is_active", widget=SmartBooleanWidget())
    is_alive = fields.Field(column_name="Is Alive", attribute="is_alive", widget=SmartBooleanWidget())

    # ---------------- Tag Fields (not direct attributes) ----------------
    tag_number = fields.Field(column_name='Animal Tag No')
    virtual_tag_number = fields.Field(column_name='Virtual Tag No')
    tag_method = fields.Field(column_name='TAG Method')
    tag_location = fields.Field(column_name='TAG Location')

    # ---------------- Status Fields (not direct attributes) ----------------
    pregnancy_status = fields.Field(column_name='Pregnant', widget=SmartBooleanWidget())
    milk_production_lpd = fields.Field(column_name='Milk Production (LPD)')

    class Meta:
        model = Cattle
        fields = (
            'cattle_code', 'name', 'owner', 'breed', 'gender', 'age', 'age_year',
            'no_of_calving', 'is_active', 'is_alive', 'current_status',
        )
        import_id_fields = ['cattle_code']
        skip_unchanged = True
        report_skipped = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._import_errors = []

    def before_import_row(self, row, **kwargs):
        """Simple validation before importing each row"""
        self._current_row = row
        row_number = kwargs.get('row_number', 'Unknown')

        # Basic validation
        if not row.get('Member Code', '').strip():
            raise ValidationError(f"Row {row_number}: Member Code is required")

        if not row.get('Age (Month)', '').strip():
            raise ValidationError(f"Row {row_number}: Age is required")

        # Validate age is numeric and positive
        try:
            age = float(row.get('Age (Month)', 0))
            if age < 0:
                raise ValidationError(f"Row {row_number}: Age cannot be negative")
        except (ValueError, TypeError):
            raise ValidationError(f"Row {row_number}: Invalid age value")

        return super().before_import_row(row, **kwargs)

    def after_save_instance(self, instance, row, **kwargs):
        """Create related objects after cattle save"""
        if kwargs.get('dry_run', False):
            return

        row_number = kwargs.get('row_number', 'Unknown')

        try:
            with transaction.atomic():
                # Handle tagging
                self._handle_tagging(instance, row)

                # Handle status
                self._handle_status(instance, row)

                logger.info(f"Row {row_number}: Successfully created related objects for {instance}")

        except Exception as e:
            error_msg = f"Row {row_number}: Error creating related objects: {str(e)}"
            logger.error(error_msg)
            self._import_errors.append(error_msg)
            # Continue processing other rows instead of failing completely

    def _handle_tagging(self, instance, row):
        """Handle cattle tagging"""
        tag_number = row.get('Animal Tag No', '').strip()
        virtual_tag_no = row.get('Virtual Tag No', '').strip()
        tag_method = row.get('TAG Method', TagMethodChoices.MANUAL).strip()
        tag_location = row.get('TAG Location', TagLocationChoices.LEFT_EAR).strip()

        if not tag_number and not virtual_tag_no:
            return  # No tag info to process

        # Check for existing active tag
        existing_tag = CattleTagging.objects.filter(
            cattle=instance,
            is_active=True
        ).first()

        if existing_tag:
            # Update existing tag if needed
            updated = False
            if tag_number and existing_tag.tag_number != tag_number:
                existing_tag.tag_number = tag_number
                updated = True
            if virtual_tag_no and existing_tag.virtual_tag_no != virtual_tag_no:
                existing_tag.virtual_tag_no = virtual_tag_no
                updated = True
            if tag_method and existing_tag.tag_method != tag_method:
                existing_tag.tag_method = tag_method
                updated = True
            if tag_location and existing_tag.tag_location != tag_location:
                existing_tag.tag_location = tag_location
                updated = True

            if updated:
                existing_tag.save()
        else:
            # Create new tag
            CattleTagging.objects.create(
                cattle=instance,
                tag_number=tag_number or f"AUTO-{instance.cattle_code}",
                virtual_tag_no=virtual_tag_no,
                tag_method=tag_method,
                tag_location=tag_location,
                tag_action=TagActionChoices.CREATED,
                is_active=True
            )

    def _handle_status(self, instance, row):
        """Handle cattle status"""
        pregnancy_status = row.get('Pregnant', '').strip()
        milk_production_lpd = row.get('Milk Production (LPD)', '').strip()
        status_codes = row.get('Animal Status', '').strip()

        # Convert pregnancy status to boolean
        pregnancy_bool = False
        if pregnancy_status:
            pregnancy_bool = pregnancy_status.lower() in ('yes', 'y', '1', 'true', 't', 'on')

        # Convert milk production to decimal
        milk_lpd = 0
        if milk_production_lpd:
            try:
                milk_lpd = float(milk_production_lpd)
            except (ValueError, TypeError):
                milk_lpd = 0

        # Get or create current status
        today = timezone.now().date()
        current_status, created = CattleStatusLog.objects.get_or_create(
            cattle=instance,
            is_current=True,
            defaults={
                'from_date': today,
                'pregnancy_status': pregnancy_bool,
                'milk_production_lpd': milk_lpd,
                'notes': f"Imported on {today}"
            }
        )

        if not created:
            # Update existing status
            current_status.pregnancy_status = pregnancy_bool
            current_status.milk_production_lpd = milk_lpd
            current_status.save()

        # Handle status codes if provided
        if status_codes:
            status_list = [code.strip() for code in status_codes.split("|") if code.strip()]
            if status_list:
                try:
                    # Get valid status types
                    valid_statuses = CattleStatusType.objects.filter(code__in=status_list)
                    current_status.statuses.set(valid_statuses)
                except Exception as e:
                    logger.warning(f"Error setting status codes for {instance}: {e}")

    def skip_row(self, instance, original, row, import_validation_errors=None):
        """Skip logic for business rules"""
        if import_validation_errors:
            return True

        # Skip if cattle is sold or dead
        if instance and instance.pk:
            if getattr(instance, 'is_sold', False):
                return True
            if not getattr(instance, 'is_alive', True):
                return True

        return super().skip_row(instance, original, row, import_validation_errors)

    # Export methods for related data
    def dehydrate_tag_number(self, obj):
        try:
            active_tag = CattleTagging.objects.filter(cattle=obj, is_active=True).first()
            return active_tag.tag_number if active_tag else None
        except:
            return None

    def dehydrate_virtual_tag_number(self, obj):
        try:
            active_tag = CattleTagging.objects.filter(cattle=obj, is_active=True).first()
            return active_tag.virtual_tag_no if active_tag else None
        except:
            return None

    def dehydrate_tag_method(self, obj):
        try:
            active_tag = CattleTagging.objects.filter(cattle=obj, is_active=True).first()
            return active_tag.tag_method if active_tag else None
        except:
            return None

    def dehydrate_tag_location(self, obj):
        try:
            active_tag = CattleTagging.objects.filter(cattle=obj, is_active=True).first()
            return active_tag.tag_location if active_tag else None
        except:
            return None

    def dehydrate_pregnancy_status(self, obj):
        try:
            current_status = CattleStatusLog.objects.filter(cattle=obj, is_current=True).first()
            return current_status.pregnancy_status if current_status else False
        except:
            return False

    def dehydrate_milk_production_lpd(self, obj):
        try:
            current_status = CattleStatusLog.objects.filter(cattle=obj, is_current=True).first()
            return float(
                current_status.milk_production_lpd) if current_status and current_status.milk_production_lpd else 0
        except:
            return 0

    def get_import_errors(self):
        """Get accumulated import errors"""
        return self._import_errors

    def clear_import_errors(self):
        """Clear accumulated import errors"""
        self._import_errors = []
