from django.conf import settings
from .models import DeliveryStatus
from notifications.fcm import _send_device_specific_notification
from .tasks import send_feedback_email


class NotificationService:
    
    @staticmethod
    def send_email_notification(subject, message, recipients):
        send_feedback_email.delay(
            subject=subject, message=message, recipient_list=recipients
        )

    @staticmethod
    def send_push_notification(user, instance=None):
        if hasattr(user, "device") and user.device:
            sent,info = _send_device_specific_notification(user.device.device, data_payload=instance.to_payload())
            status = DeliveryStatus.SENT if sent else DeliveryStatus.FAILED
            instance.mark_delivery_result(status=status,response=info)

    @staticmethod
    def notify_instance_created(notification_instance):
        user = notification_instance.recipient
        if notification_instance.allowed_email:
            NotificationService.send_email_notification(
                subject=notification_instance.title,
                message=notification_instance.message,
                recipients=[settings.SUPPORT_TEAM_EMAIL],
            )

        NotificationService.send_push_notification(
            user=user,
            instance=notification_instance,
        )
