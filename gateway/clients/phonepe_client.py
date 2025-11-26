import base64
import hashlib
import json
import logging
import requests
from dataclasses import dataclass

from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class PhonePeConfig:
    merchant_id: str = settings.PHONEPE_MERCHANT_ID
    salt_key: str = settings.PHONEPE_SALT_KEY
    salt_index: str = str(settings.PHONEPE_SALT_INDEX)
    base_url: str = settings.PHONEPE_BASE_URL
    redirect_url: str = settings.PHONEPE_REDIRECT_URL
    callback_url: str = settings.PHONEPE_CALLBACK_URL


class PhonePeClient:
    def __init__(self, config: PhonePeConfig | None = None):
        self.config = config or PhonePeConfig()

    def _build_x_verify(self, payload_base64: str, api_path: str) -> str:
        """
        For pay API: SHA256(base64Payload + apiPath + saltKey) + ### + saltIndex
        For status API: often SHA256(apiPath + saltKey) + ### + saltIndex
        (check your PhonePe docs – this helper handles the first case.
         For status we use a different helper below.)
        """
        to_hash = f"{payload_base64}{api_path}{self.config.salt_key}"
        sha256 = hashlib.sha256(to_hash.encode("utf-8")).hexdigest()
        return f"{sha256}###{self.config.salt_index}"

    def _build_x_verify_for_status(self, api_path: str) -> str:
        # Status APIs often require SHA256(apiPath + saltKey)
        to_hash = f"{api_path}{self.config.salt_key}"
        sha256 = hashlib.sha256(to_hash.encode("utf-8")).hexdigest()
        return f"{sha256}###{self.config.salt_index}"

    def initiate_payment(
        self,
        merchant_transaction_id: str,
        merchant_user_id: str,
        amount_paise: int,
        mobile: str | None = None,
        instrument_type: str = "PAY_PAGE",
    ) -> dict:
        api_path = "/pg/v1/pay"

        payload = {
            "merchantId": self.config.merchant_id,
            "merchantTransactionId": merchant_transaction_id,
            "merchantUserId": merchant_user_id,
            "amount": amount_paise,
            "redirectUrl": self.config.redirect_url,
            "redirectMode": "POST",
            "callbackUrl": self.config.callback_url,
            "paymentInstrument": {
                "type": instrument_type,
            },
        }

        if mobile:
            payload["mobileNumber"] = mobile

        payload_json = json.dumps(payload, separators=(",", ":"))
        payload_base64 = base64.b64encode(payload_json.encode()).decode()

        headers = {
            "Content-Type": "application/json",
            "X-VERIFY": self._build_x_verify(payload_base64, api_path),
        }

        data = {"request": payload_base64}

        url = f"{self.config.base_url}{api_path}"
        logger.info("PhonePe pay request %s", payload)

        resp = requests.post(url, headers=headers, json=data, timeout=15)
        resp.raise_for_status()
        body = resp.json()
        logger.info("PhonePe pay response %s", body)
        return body

    def check_status(self, merchant_transaction_id: str) -> dict:
        api_path = f"/pg/v1/status/{self.config.merchant_id}/{merchant_transaction_id}"

        url = f"{self.config.base_url}{api_path}"
        headers = {
            "Content-Type": "application/json",
            "X-VERIFY": self._build_x_verify_for_status(api_path),
            "X-MERCHANT-ID": self.config.merchant_id,
        }

        logger.info("PhonePe status request %s", api_path)
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        body = resp.json()
        logger.info("PhonePe status response %s", body)
        return body
