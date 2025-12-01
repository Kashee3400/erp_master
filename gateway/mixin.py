import logging
from decouple import config


from phonepe.sdk.pg.payments.v2.standard_checkout_client import (
    StandardCheckoutClient,
)

logger = logging.getLogger(__name__)


class PhonePeClientMixin:
    """Mixin to initialize PhonePe client"""

    @staticmethod
    def get_phonepe_client():
        """Initialize and return PhonePe client"""
        try:
            client = StandardCheckoutClient.get_instance(
                client_id=config("PHONEPE_CLIENT_ID"),
                client_secret=config("PHONEPE_CLIENT_SECRET"),
                client_version=config("PHONEPE_CLIENT_VERSION"),
                env=config("PHONEPE_ENV"),
                should_publish_events=False,
            )
            return client
        except Exception as e:
            logger.error(f"Failed to initialize PhonePe client: {str(e)}")
            raise
