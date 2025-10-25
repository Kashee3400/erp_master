from django.core.management.base import BaseCommand
from django.utils import timezone
from erp_app.models import MppCollection
from notifications.model import Notification, NotificationStatus, NotificationTemplate
from django.contrib.auth import get_user_model
from django.db import transaction
import logging
from django.contrib.contenttypes.models import ContentType
from erp_app.models import MemberHierarchyView

import redis

r = redis.Redis(host="localhost", port=6379, db=0)

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

    REDIS_KEY_PREFIX = "collection_notification"

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

        # 2. Fetch today's collections with shift info
        collections = (
            MppCollection.objects.filter(collection_date__date=today)
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
                self.style.WARNING("⚠️ No MppCollection records found for today.")
            )

        member_codes = [c["member_code"] for c in collections]

        # 3. Map members to mobile numbers
        members_map = {
            m.member_code: m.mobile_no
            for m in MemberHierarchyView.objects.filter(member_code__in=member_codes)
        }

        # 4. Map users by mobile number
        user_map = {
            u.username: u.id
            for u in User.objects.filter(username__in=members_map.values())
        }

        # 5. ContentType for linking notification to collection
        collection_ct = ContentType.objects.get_for_model(MppCollection)

        notifications_to_create = []

        # 6. Process new collections
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

        # 7. Retry failed/pending notifications
        retry_notifications = Notification.objects.filter(
            template=template,
            recipient_id = user_id,
            created_at=today,
            status__in=[NotificationStatus.PENDING, NotificationStatus.FAILED],
        )

        # Combine new and retry
        notifications_to_create += list(retry_notifications)

        if not notifications_to_create:
            self.stdout.write(
                self.style.SUCCESS("✅ No new or retry notifications to process.")
            )
            return

        with transaction.atomic():
            # Bulk create only the new notifications (retry already exists)
            created_notifications = Notification.objects.bulk_create(
                [n for n in notifications_to_create if not n.id], batch_size=500
            )
        from notifications.tasks import process_collections_batch

        # process_collections_batch.delay([obj.pk for obj in created_notifications])

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Created {len(created_notifications)} new notifications and retried {retry_notifications.count()} notifications."
            )
        )
