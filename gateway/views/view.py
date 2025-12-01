# views.py
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from uuid import uuid4
import logging
import json
from ..models.transaction_model import PaymentTransaction
from django.utils import timezone

from phonepe.sdk.pg.payments.v2.standard_checkout_client import (
    RefundRequest,
)
from ..mixin import PhonePeClientMixin

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class VerifyPaymentView(View, PhonePeClientMixin):
    """
    Manually verify payment status from PhonePe

    POST /api/payments/verify/
    Body: {"merchant_order_id": "xxx"}
    """

    def post(self, request):
        try:
            data = json.loads(request.body)
            merchant_order_id = data.get("merchant_order_id")

            if not merchant_order_id:
                return JsonResponse(
                    {"status": "error", "message": "Order ID is required"}, status=400
                )

            client = self.get_phonepe_client()
            response = client.get_order_status(
                merchant_order_id=merchant_order_id, details=True
            )

            # Update database
            transaction = PaymentTransaction.objects.get(
                merchant_order_id=merchant_order_id
            )
            transaction.status = response.state
            transaction.verified_at = timezone.now()
            transaction.save()

            return JsonResponse(
                {
                    "status": "success",
                    "data": {
                        "merchant_order_id": merchant_order_id,
                        "state": response.state,
                        "verified": True,
                    },
                },
                status=200,
            )

        except PaymentTransaction.DoesNotExist:
            return JsonResponse(
                {"status": "error", "message": "Transaction not found"}, status=404
            )
        except Exception as e:
            logger.error(f"Manual verification failed: {str(e)}")
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Verification failed",
                    "errors": str(e),
                },
                status=500,
            )


@method_decorator(csrf_exempt, name="dispatch")
class InitiateRefundView(View, PhonePeClientMixin):
    """
    Initiate refund for an order

    POST /api/payments/refund/
    Body: {
        "original_order_id": "uuid-of-original-order",
        "amount": 100
    }
    """

    def post(self, request):
        try:
            # Parse request body
            data = json.loads(request.body)
            original_order_id = data.get("original_order_id")
            amount = data.get("amount")

            # Validation
            if not original_order_id:
                return JsonResponse(
                    {"success": "error", "message": "Original order ID is required"},
                    status=400,
                )

            if not amount or amount <= 0:
                return JsonResponse(
                    {"success": "error", "message": "Invalid refund amount"}, status=400
                )

            # Generate unique refund ID
            merchant_refund_id = str(uuid4())

            # Initialize PhonePe client
            client = self.get_phonepe_client()

            # Create refund request
            refund_request = RefundRequest.build_refund_request(
                merchant_refund_id=merchant_refund_id,
                original_merchant_order_id=original_order_id,
                amount=amount,
            )

            # Initiate refund
            refund_response = client.refund(refund_request=refund_request)

            # Log refund
            logger.info(f"Refund initiated: Refund ID - {merchant_refund_id}")

            return JsonResponse(
                {
                    "status": "success",
                    "message": f"Refund initiated: Refund ID - {merchant_refund_id}",
                    "data": {
                        "merchant_refund_id": merchant_refund_id,
                        "original_order_id": original_order_id,
                        "state": refund_response.state,
                        "amount": amount,
                    },
                },
                status=200,
            )

        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON"}, status=400
            )
        except Exception as e:
            logger.error(f"Refund initiation failed: {str(e)}")
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Refund initiation failed",
                    "details": str(e),
                },
                status=500,
            )


class RefundStatusView(View, PhonePeClientMixin):
    """
    Get refund status

    GET /api/payments/refund-status/<merchant_refund_id>/
    """

    def get(self, request, merchant_refund_id):
        try:
            if not merchant_refund_id:
                return JsonResponse(
                    {"success": "error", "message": "Refund ID is required"}, status=400
                )

            # Initialize PhonePe client
            client = self.get_phonepe_client()

            # Get refund status
            refund_response = client.get_refund_status(
                merchant_refund_id=merchant_refund_id
            )

            # Log status check
            logger.info(
                f"Refund status checked: {merchant_refund_id} - {refund_response.state}"
            )

            return JsonResponse(
                {
                    "success": "success",
                    "message": f"Refund status checked: {merchant_refund_id} - {refund_response.state}",
                    "data": {
                        "merchant_refund_id": merchant_refund_id,
                        "state": refund_response.state,
                        "response": refund_response.__dict__,
                    },
                },
                status=200,
            )

        except Exception as e:
            logger.error(f"Refund status check failed: {str(e)}")
            return JsonResponse(
                {
                    "success": False,
                    "message": "Failed to get refund status",
                    "errors": str(e),
                },
                status=500,
            )
