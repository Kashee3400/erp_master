from django.db.models.signals import pre_save
from django.dispatch import receiver
import uuid
from .models import SahayakFeedback

@receiver(pre_save, sender=SahayakFeedback)
def generate_feedback_id(sender, instance, **kwargs):
    if not instance.feedback_id:
        instance.feedback_id = str(uuid.uuid4())
