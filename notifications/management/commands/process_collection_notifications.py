from django.core.management.base import BaseCommand
from django.utils import timezone
from erp_app.models import MppCollection
from notifications.model import (
    Notification,
    NotificationStatus,
    NotificationTemplate,
    NotificationTrackMppCollection,
)
from django.contrib.auth import get_user_model
from django.db import transaction
import logging
from django.contrib.contenttypes.models import ContentType
from erp_app.models import MemberHierarchyView

User = get_user_model()

logger = logging.getLogger(__name__)


def make_json_safe(data):
    import decimal
    import datetime

    if isinstance(data, dict):
        return {k: make_json_safe(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [make_json_safe(v) for v in data]
    elif isinstance(data, decimal.Decimal):
        return float(data)
    elif isinstance(data, (datetime.date, datetime.datetime)):
        return data.isoformat()
    else:
        return data


class Command(BaseCommand):
    help = "Pull new MppCollection records, create notifications, and retry failed/pending ones."


    def handle(self, *args, **options):
        now = timezone.now()
        today = now.date()

        # 1. Fetch notification template
        template = NotificationTemplate.objects.filter(
            name="mpp_collection_created_hi"
        ).first()
        if not template:
            self.stdout.write(
                self.style.ERROR(
                    "❌ Notification template 'mpp_collection_created_hi' not found."
                )
            )
            return

        # 2. Get already tracked collection codes to prevent duplicates
        tracked_codes = set(
            NotificationTrackMppCollection.objects.filter(is_sent=True).values_list(
                "collection_code", flat=True
            )
        )

        # 3. Fetch today's collections with shift info, excluding already tracked ones
        collections = (
            MppCollection.objects.filter(collection_date__date=today)
            .exclude(mpp_collection_code__in=tracked_codes)
            .select_related("shift_code")
            .order_by("collection_date")
            .values(
                "member_code",
                "mpp_collection_code",
                "qty",
                "fat",
                "uuid",
                "snf",
                "amount",
                "collection_date",
                "shift_code__shift_short_name",
            )
        )

        if not collections.exists():
            self.stdout.write(
                self.style.WARNING("⚠️ No new MppCollection records found for today.")
            )
            return

        member_codes = [c["member_code"] for c in collections]

        # 4. Map members to mobile numbers
        members_map = {
            m.member_code: m.mobile_no
            for m in MemberHierarchyView.objects.filter(member_code__in=member_codes)
        }

        # 5. Map users by mobile number
        user_map = {
            u.username: u.id
            for u in User.objects.filter(username__in=members_map.values())
        }

        # 6. ContentType for linking notification to collection
        collection_ct = ContentType.objects.get_for_model(MppCollection)

        notifications_to_create = []
        tracking_records_to_create = []

        # 7. Process new collections
        for record in collections:
            collection_code = record["mpp_collection_code"]
            shift = record.get("shift_code__shift_short_name", "")

            member_code = record["member_code"]
            mobile = members_map.get(member_code)
            user_id = user_map.get(mobile)
            if not user_id:
                continue

            render_context = {
                "recipient": User.objects.get(id=user_id),
                "collection": record,
                "site_name": "Kashee E-Dairy",
            }

            # Render content using the template model
            rendered = template.render_content(render_context)

            context_data = make_json_safe(
                {
                    "mpp_collection": {
                        "collection_code": collection_code,
                        "uuid": str(record["uuid"]),
                        "member_code": member_code,
                        "qty": record["qty"],
                        "fat": record["fat"],
                        "snf": record["snf"],
                        "amount": record["amount"],
                        "collection_date": record["collection_date"],
                        "shift": shift,
                    }
                }
            )

            notifications_to_create.append(
                Notification(
                    template=template,
                    recipient_id=user_id,
                    delivery_status={"status": NotificationStatus.PENDING},
                    channels=["push"],
                    app_route="/",
                    title=rendered.get("title", ""),
                    body=rendered.get("body", ""),
                    email_subject=rendered.get("email_subject", ""),
                    email_body=rendered.get("email_body"),
                    context_data=context_data,
                    content_type=collection_ct,
                )
            )

            # Create tracking record for this collection
            tracking_records_to_create.append(
                NotificationTrackMppCollection(
                    collection_code=collection_code, is_sent=True
                )
            )

        # 8. Retry failed/pending notifications (only for untracked collections)
        retry_notifications = Notification.objects.filter(
            template=template,
            created_at__date=today,
            status__in=[NotificationStatus.PENDING, NotificationStatus.FAILED],
        ).exclude(context_data__mpp_collection__collection_code__in=tracked_codes)

        if not notifications_to_create and not retry_notifications.exists():
            self.stdout.write(
                self.style.SUCCESS("✅ No new or retry notifications to process.")
            )
            return

        with transaction.atomic():
            # Bulk create new notifications
            created_notifications = Notification.objects.bulk_create(
                notifications_to_create, batch_size=500
            )

            # Bulk create tracking records
            NotificationTrackMppCollection.objects.bulk_create(
                tracking_records_to_create, batch_size=500, ignore_conflicts=True
            )

        # Combine new and retry for processing
        all_notification_ids = [obj.pk for obj in created_notifications] + list(
            retry_notifications.values_list("id", flat=True)
        )

        from notifications.tasks import process_collections_batch

        process_collections_batch.delay(all_notification_ids)

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Created {len(created_notifications)} new notifications, "
                f"retried {retry_notifications.count()} notifications, "
                f"and tracked {len(tracking_records_to_create)} collections."
            )
        )
