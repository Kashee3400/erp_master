from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
import logging, calendar, datetime, decimal
from django.utils.functional import Promise
from django.utils.encoding import force_str
from django.contrib.auth import get_user_model

from notifications.model import Notification, NotificationStatus, NotificationTemplate
from member.models import SahayakIncentives
from notifications.tasks import process_collections_batch

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Create sahayak incentive notifications for a specific or current month if not already created."

    def add_arguments(self, parser):
        parser.add_argument(
            "--month",
            type=str,
            help="Optional: Month name (e.g., January, February). Defaults to current month.",
        )
        parser.add_argument(
            "--year",
            type=str,
            help="Optional: Year (e.g., 2025). Defaults to current year.",
        )

    def handle(self, *args, **options):
        now = timezone.now()
        today = now.date()

        month_arg = options.get("month")
        year_arg = options.get("year")

        if month_arg:
            # normalize input (e.g., "feb" → "February")
            try:
                current_month_name = next(
                    m
                    for m in calendar.month_name
                    if m.lower().startswith(month_arg.lower())
                )
            except StopIteration:
                self.stderr.write(
                    self.style.ERROR(
                        f"❌ Invalid month name '{month_arg}'. Use full name like 'January'."
                    )
                )
                return
        else:
            current_month_name = calendar.month_name[today.month]

        current_year = year_arg or str(today.year)

        self.stdout.write(
            self.style.NOTICE(
                f"📅 Processing Sahayak incentives for {current_month_name} {current_year}..."
            )
        )

        # --- Load template ---
        try:
            template = NotificationTemplate.objects.get(
                name="sahayak_incentive_update_hi"
            )
        except NotificationTemplate.DoesNotExist:
            self.stderr.write(self.style.ERROR("❌ Notification template not found."))
            return

        # --- Fetch incentives ---
        incentives = SahayakIncentives.objects.filter(
            month=current_month_name, year=current_year
        ).select_related("user")
        if not incentives.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️ No sahayak incentives found for {current_month_name} {current_year}."
                )
            )
            return

        # --- Idempotency: Skip already-notified incentives ---
        incentive_ct = ContentType.objects.get_for_model(SahayakIncentives)
        incentive_ids = list(incentives.values_list("id", flat=True))

        existing_notified_ids = set(
            Notification.objects.filter(
                template=template,
                content_type=incentive_ct,
                object_id__in=incentive_ids,
            ).values_list("object_id", flat=True)
        )

        new_incentives = [
            inc for inc in incentives if inc.id not in existing_notified_ids
        ]

        if not new_incentives:
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ All incentives for {current_month_name} {current_year} already notified."
                )
            )
            return

        notifications_to_create = []

        # --- Build notifications ---
        for record in new_incentives:
            try:
                render_context = {
                    "recipient": record.user,
                    "incentive": record,
                    "site_name": "Kashee E-Dairy",
                }
                rendered = template.render_content(render_context)
                context_data = self._serialize_context(render_context)

                notifications_to_create.append(
                    Notification(
                        template=template,
                        recipient_id=record.user.pk,
                        delivery_status={"status": NotificationStatus.PENDING},
                        channels=["push"],
                        app_route="/",
                        title=rendered.get("title", ""),
                        body=rendered.get("body", ""),
                        email_subject=rendered.get("email_subject", ""),
                        email_body=rendered.get("email_body", ""),
                        context_data=context_data,
                        content_type=incentive_ct,
                        object_id=record.id,
                    )
                )
            except Exception as e:
                logger.warning(
                    "⚠️ Skipping incentive ID %s due to error: %s", record.pk, e
                )

        if not notifications_to_create:
            self.stdout.write(self.style.WARNING("⚠️ No new notifications to create."))
            return

        # --- Create notifications in one atomic block ---
        with transaction.atomic():
            created_notifications = Notification.objects.bulk_create(
                notifications_to_create, batch_size=500
            )
            # all_ids = [n.pk for n in created_notifications]
            # transaction.on_commit(lambda: process_collections_batch.delay(all_ids))

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Created {len(created_notifications)} new notifications for {current_month_name} {current_year}."
            )
        )

    # --- Safe serialization helper ---
    def _serialize_context(self, context: dict) -> dict:
        def safe_value(value):
            if isinstance(value, Promise):
                return force_str(value)
            if hasattr(value, "_meta"):
                return {
                    "id": value.pk,
                    "model": value._meta.label_lower,
                    "str": str(value),
                }
            if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
                return value.isoformat()
            if isinstance(value, decimal.Decimal):
                return float(value)
            if isinstance(value, (list, tuple)):
                return [safe_value(v) for v in value]
            if isinstance(value, dict):
                return {k: safe_value(v) for k, v in value.items()}
            return value

        return {k: safe_value(v) for k, v in (context or {}).items()}
