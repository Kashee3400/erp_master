import json
import logging
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction as db_transaction
from ..models.transaction_model import PaymentTransaction, PaymentStatusChoices
from ..mixin import PhonePeClientMixin
from django.utils import timezone
from decouple import config
from phonepe.sdk.pg.common.exceptions import PhonePeException
from phonepe.sdk.pg.payments.v2.models.callback_response import CallbackResponse
from phonepe.sdk.pg.payments.v2.models.response.callback_data import CallbackData
from decimal import Decimal


logger = logging.getLogger(__name__)


from django.db import transaction as db_transaction


@method_decorator(csrf_exempt, name="dispatch")
class PaymentWebhookView(View, PhonePeClientMixin):

    def post(self, request):

        raw_body = ""
        try:
            client = self.get_phonepe_client()

            # -----------------------------------------------------
            # 1️⃣ Extract Authorization header
            # -----------------------------------------------------
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return JsonResponse({"error": "Unauthorized"}, status=401)

            # -----------------------------------------------------
            # 2️⃣ Extract raw request body
            # -----------------------------------------------------
            raw_body = request.body.decode("utf-8") if request.body else ""
            if not raw_body.strip():
                return JsonResponse({"error": "Empty Body"}, status=400)

            logger.info(f"[PHONEPE WEBHOOK RAW]: {raw_body}")

            # -----------------------------------------------------
            # 3️⃣ Validate callback signature + parse json
            # -----------------------------------------------------
            try:
                callback: CallbackResponse = client.validate_callback(
                    username=config("PHONEPE_WEBHOOK_USERNAME"),
                    password=config("PHONEPE_WEBHOOK_PASSWORD"),
                    callback_header_data=auth_header,
                    callback_response_data=raw_body,
                )
            except PhonePeException as pe:
                logger.error(f"[PHONEPE EXCEPTION] {pe.message} — data={pe.data}")
                return JsonResponse(
                    {"error": pe.message, "data": pe.data},
                    status=pe.http_status_code or 500,
                )
            except Exception as e:
                logger.error(f"[WEBHOOK PARSE ERROR] {e}")
                return JsonResponse({"error": "Invalid Callback Body"}, status=400)

            # -----------------------------------------------------
            # 4️⃣ Extract PhonePe callback structure
            # -----------------------------------------------------
            callback_type = callback.type
            event = callback.event
            payload: CallbackData = callback.payload

            merchant_order_id = payload.merchant_order_id
            order_id = payload.order_id
            state = payload.state  # COMPLETED / FAILED / PENDING
            amount = payload.amount
            error_code = payload.error_code
            detailed_error_code = payload.detailed_error_code

            logger.info(
                f"[PHONEPE] Callback Received → type={callback_type}, event={event}, "
                f"merchant_order_id={merchant_order_id}, state={state}"
            )

            # -----------------------------------------------------
            # 5️⃣ Extract Payment Rails + Instruments
            # -----------------------------------------------------
            payment_method_data = {}
            payment_details = payload.payment_details or []

            if payment_details:
                detail = payment_details[
                    0
                ]  # Only one payment details block in checkout

                split = detail.split_instruments or []
                if split:
                    part = split[0]  # Always one split instrument for checkout flow

                    rail = part.rail
                    instrument = part.instrument

                    # ---- RAIL INFO ----
                    if rail:
                        if rail.type == "UPI":
                            payment_method_data["rail"] = {
                                "type": "UPI",
                                "utr": rail.utr,
                                "upi_transaction_id": rail.upi_transaction_id,
                                "vpa": rail.vpa,
                            }
                        elif rail.type == "PG":
                            payment_method_data["rail"] = {
                                "type": "PG",
                                "transaction_id": rail.transaction_id,
                                "authorization_code": rail.authorization_code,
                                "service_transaction_id": rail.service_transaction_id,
                            }

                    # ---- INSTRUMENT ----
                    if instrument:
                        pm = {"type": instrument.type}

                        # NET BANKING / CC / DC share same fields
                        if instrument.type in (
                            "NET_BANKING",
                            "CREDIT_CARD",
                            "DEBIT_CARD",
                        ):
                            pm.update(
                                {
                                    "bank_transaction_id": instrument.bank_transaction_id,
                                    "bank_id": instrument.bank_id,
                                    "arn": instrument.arn,
                                    "brn": instrument.brn,
                                }
                            )

                        # ACCOUNT instrument
                        if instrument.type == "ACCOUNT":
                            pm.update(
                                {
                                    "ifsc": instrument.ifsc,
                                    "account_type": instrument.account_type,
                                    "masked_account_number": instrument.masked_account_number,
                                    "account_holder_name": instrument.account_holder_name,
                                }
                            )

                        payment_method_data["instrument"] = pm

            # -----------------------------------------------------
            # 6️⃣ Atomic DB update
            # -----------------------------------------------------
            with db_transaction.atomic():

                txn = (
                    PaymentTransaction.objects.select_for_update()
                    .filter(merchant_order_id=merchant_order_id)
                    .first()
                )

                if not txn:
                    logger.error(
                        f"[PHONEPE] Unknown merchant_order_id: {merchant_order_id}"
                    )
                    return JsonResponse({"error": "Transaction Not Found"}, status=404)

                # Always save full webhook JSON
                txn.webhook_response = json.loads(raw_body)

                # Save payment_method block (rail + instrument)
                txn.payment_method = payment_method_data

                # Save amount update (if differs)
                if amount and amount != int(txn.amount * 100):
                    txn.amount = Decimal(amount) / Decimal("100.00")

                # ---- SUCCESS CASE ----
                if state in ("COMPLETED", "SUCCESS"):
                    txn.status = PaymentStatusChoices.COMPLETED
                    txn.phonepe_transaction_id = order_id
                    txn.status_message = "Payment Successful"
                    txn.gateway_response_code = "SUCCESS"
                    txn.gateway_response_message = "Payment Completed"
                    txn.verified_at = timezone.now()
                    txn.completed_at = timezone.now()

                    # mark related object
                    if txn.content_object and hasattr(
                        txn.content_object, "mark_as_paid"
                    ):
                        txn.content_object.mark_as_paid()

                # ---- FAILED CASE ----
                elif state == "FAILED":
                    reason = detailed_error_code or error_code or "Payment Failed"

                    txn.status = PaymentStatusChoices.FAILED
                    txn.failure_reason = reason
                    txn.status_message = reason
                    txn.gateway_response_code = error_code or "FAILED"
                    txn.gateway_response_message = (
                        detailed_error_code or "Payment Failed"
                    )

                    if txn.content_object and hasattr(
                        txn.content_object, "mark_as_failed"
                    ):
                        txn.content_object.mark_as_failed(reason=reason)

                # ---- PENDING / UNKNOWN / PROCESSING ----
                else:
                    txn.status = PaymentStatusChoices.PENDING
                    txn.status_message = "Payment Pending"
                    txn.gateway_response_code = "PENDING"

                txn.save()

            return JsonResponse({"success": True}, status=200)

        except Exception as e:
            logger.error(f"[WEBHOOK ERROR] {str(e)} | BODY={raw_body}", exc_info=True)
            return JsonResponse(
                {"error": "Server Error", "details": str(e)}, status=500
            )


@method_decorator(csrf_exempt, name="dispatch")
class CheckPaymentStatusView(View, PhonePeClientMixin):
    """
    Check payment status for a specific transaction

    GET /api/payments/order-status/<merchant_order_id>/
    or
    POST /api/payments/status/
    Body: {"merchant_order_id": "ORD_..."}
    """

    def get(self, request, merchant_order_id=None):
        """GET method to check status"""
        return self._check_status(merchant_order_id)

    def post(self, request):
        """POST method to check status"""
        try:
            data = json.loads(request.body)
            merchant_order_id = data.get("merchant_order_id")

            if not merchant_order_id:
                return JsonResponse(
                    {"status": "error", "message": "merchant_order_id is required"},
                    status=400,
                )

            return self._check_status(merchant_order_id)
        except json.JSONDecodeError:
            return JsonResponse(
                {"success": "error", "message": "Invalid JSON"}, status=400
            )

    @staticmethod
    def _check_status(merchant_order_id):
        """Check transaction status"""
        try:
            transaction = PaymentTransaction.objects.get(
                merchant_order_id=merchant_order_id
            )

            return JsonResponse(
                {
                    "status": "success",
                    "message": "Status checked successfully",
                    "data": {
                        "transaction_id": str(transaction.id),
                        "merchant_order_id": transaction.merchant_order_id,
                        "status": transaction.status,
                        "status_display": transaction.get_status_display(),
                        "amount": str(transaction.amount),
                        "currency": transaction.currency,
                        "created_at": transaction.created_at.isoformat(),
                        "completed_at": (
                            transaction.completed_at.isoformat()
                            if transaction.completed_at
                            else None
                        ),
                        "is_successful": transaction.is_successful,
                        "failure_reason": transaction.failure_reason,
                    },
                },
                status=200,
            )

        except PaymentTransaction.DoesNotExist:
            logger.warning(f"Transaction not found: {merchant_order_id}")
            return JsonResponse(
                {"status": "error", "message": "Transaction not found"}, status=404
            )
        except Exception as e:
            logger.error(f"Status check error: {str(e)}", exc_info=True)
            return JsonResponse(
                {"status": "error", "message": "Internal server error"}, status=500
            )
