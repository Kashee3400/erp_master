import json
import logging
from uuid import uuid4
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from phonepe.sdk.pg.payments.v2.models.request.standard_checkout_pay_request import (
    StandardCheckoutPayRequest,
)

from phonepe.sdk.pg.common.models.request.meta_info import MetaInfo

from ..models.transaction_model import PaymentTransaction, PaymentTransactionTypeChoices
from ..mixin import PhonePeClientMixin
from django.utils import timezone

from decouple import config

logger = logging.getLogger(__name__)

MAX_LEN = 63


@method_decorator(csrf_exempt, name="dispatch")
class InitiatePaymentView(View, PhonePeClientMixin):
    """
    Initiate a new payment transaction

    POST /api/payments/initiate/
    Body: {
        "amount": 100.00,
        "redirect_url": "https://yourapp.com/payment/callback",
        "user_identifier": "user_123",  # REQUIRED
        "transaction_type": "PRODUCT_PURCHASE",  # REQUIRED
        "payment_method_type": "UPI",  # Optional: UPI, CARD, NETBANKING, WALLET
        "related_object_id": "product_id_or_uuid",  # Optional for generic relations
        "related_model": "Product",  # Optional: Product, CaseEntry, Subscription, etc.
        "udf1": "optional_data_1",
        "udf2": "optional_data_2",
        "udf3": "optional_data_3",
        "metadata": {"custom_key": "custom_value"}  # Optional: additional data
    }
    """

    def post(self, request):
        try:
            # Parse request body
            data = json.loads(request.body)

            # Extract and validate required fields
            amount = data.get("amount")
            redirect_url = data.get("redirect_url")
            user_identifier = data.get("user_identifier")
            transaction_type = data.get("transaction_type")

            # Validation
            errors = self._validate_request(
                amount, redirect_url, user_identifier, transaction_type
            )
            if errors:
                return JsonResponse({"status": "error", "message": errors}, status=400)

            # Generate unique merchant order ID
            merchant_order_id = self._generate_merchant_order_id(data)

            # Get content type and object ID if provided (for generic relations)
            content_type = None
            object_id = None
            if data.get("related_object_id") and data.get("related_model"):
                try:
                    related_model = data.get("related_model")
                    content_type = ContentType.objects.get(model=related_model.lower())
                    object_id = data.get("related_object_id")
                except ContentType.DoesNotExist:
                    logger.warning(f"Invalid model: {data.get('related_model')}")
                    return JsonResponse(
                        {
                            "status": "error",
                            "message": f"Invalid model type: {data.get('related_model')}",
                        },
                        status=400,
                    )

            # Build redirect URL
            app_return_url = data.get("redirect_url")
            brand = data.get("brand", "default")

            # Final hosted payment result page
            hosted_result_url = config("HOSTED_RESULT_URL")

            # The final URL PhonePe will redirect to
            final_redirect_url = (
                f"{hosted_result_url}"
                f"?order_id={merchant_order_id}"
                f"&return_url={app_return_url}"
                f"&brand={brand}"
            )

            # Prepare metadata
            meta_info = MetaInfo(
                udf1=data.get("udf1", ""),
                udf2=data.get("udf2", ""),
                udf3=data.get("udf3", ""),
            )

            # Initialize PhonePe client
            client = self.get_phonepe_client()

            # Create PhonePe payment request
            pay_request = StandardCheckoutPayRequest.build_request(
                merchant_order_id=merchant_order_id,
                amount=int(float(amount) * 100),
                redirect_url=final_redirect_url,
                meta_info=meta_info,
            )

            # Initiate payment with PhonePe
            pay_response = client.pay(pay_request)

            # Prepare transaction data
            transaction_data = {
                "merchant_order_id": merchant_order_id,
                "amount": amount,
                "status": "INITIATED",
                "user_identifier": user_identifier,
                "transaction_type": transaction_type,
                "redirect_url": redirect_url,
                "udf1": data.get("udf1", ""),
                "udf2": data.get("udf2", ""),
                "udf3": data.get("udf3", ""),
                "payment_method_type": data.get("payment_method_type"),
                "metadata": data.get("metadata", {}),
                "ip_address": self._get_client_ip(request),
                "user_agent": request.META.get("HTTP_USER_AGENT", ""),
            }

            # Add PhonePe transaction ID if available
            if hasattr(pay_response, "transaction_id") and pay_response.transaction_id:
                transaction_data["phonepe_transaction_id"] = pay_response.transaction_id

            # Create transaction with or without generic relation
            if content_type and object_id:
                transaction = PaymentTransaction.objects.create(
                    content_type=content_type, object_id=object_id, **transaction_data
                )
            else:
                transaction = PaymentTransaction.objects.create(**transaction_data)

            logger.info(
                f"Payment initiated: Order ID - {merchant_order_id}, "
                f"Amount - ₹{amount}, User - {user_identifier}"
            )
            
            return JsonResponse(
                {
                    "status": "success",
                    "message":"Payment initiated",
                    "data": {
                        "transaction_id": str(transaction.id),
                        "merchant_order_id": merchant_order_id,
                        "checkout_url": pay_response.redirect_url,
                        "amount": str(amount),
                        "currency": "INR",
                        "redirect_url": final_redirect_url,
                        "status": "INITIATED",
                    },
                },
                status=200,
            )

        except json.JSONDecodeError:
            logger.error("Invalid JSON in request")
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
        except Exception as e:
            logger.error(f"Payment initiation failed: {str(e)}", exc_info=True)
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Payment initiation failed",
                    "errors": str(e),
                },
                status=500,
            )

    @staticmethod
    def _validate_request(amount, redirect_url, user_identifier, transaction_type):
        """Validate required fields"""
        errors = {}

        if not amount:
            errors["amount"] = "Amount is required"
        elif isinstance(amount, (int, float)):
            if amount <= 0:
                errors["amount"] = "Amount must be greater than 0"
            elif amount > 100000:
                errors["amount"] = "Amount exceeds maximum limit (₹100,000)"
        else:
            errors["amount"] = "Amount must be a number"

        if not redirect_url:
            errors["redirect_url"] = "Redirect URL is required"
        elif not redirect_url.startswith(("http://", "https://")):
            errors["redirect_url"] = "Invalid redirect URL"

        if not user_identifier:
            errors["user_identifier"] = "User identifier is required"
        elif len(str(user_identifier)) > 255:
            errors["user_identifier"] = "User identifier too long"

        if not transaction_type:
            errors["transaction_type"] = "Transaction type is required"
        elif transaction_type not in dict(PaymentTransactionTypeChoices.choices):
            valid_types = [t[0] for t in PaymentTransactionTypeChoices.choices]
            errors["transaction_type"] = (
                f"Invalid type. Valid types: {', '.join(valid_types)}"
            )

        return errors

    @staticmethod
    def _generate_merchant_order_id(data):
        related_model = (data.get("related_model", "GEN")).upper()[:8]
        related_id = str(data.get("related_object_id", ""))[:12]
        timestamp = str(int(timezone.now().timestamp() * 1000))
        rand = uuid4().hex[:8]

        order_id = f"ORD_{related_model}_{related_id}_{timestamp}_{rand}"

        return order_id[:MAX_LEN]

    @staticmethod
    def _get_client_ip(request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")


# "transaction_type": "Invalid type. Valid types: PRODUCT_PURCHASE, CASE_ENTRY_FEE, SUBSCRIPTION, SERVICE_FEE, BOOKING, CONSULTATION, OTHER"
